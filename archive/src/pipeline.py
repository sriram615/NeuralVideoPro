"""
VideoSearchPipeline — End-to-end Orchestrator for Semantic Video Retrieval.

Integrates keyframe extraction (VideoProcessor), audio transcription (AudioTranscriber),
CLIP vision encoding (CLIPVisionEncoder), text query encoding (TextQueryEncoder),
and hybrid late-fusion vector search (QdrantVectorStore).

Usage:
    pipeline = VideoSearchPipeline(db_path="./data/qdrant_db")
    num_points = pipeline.ingest_video("news_report.mp4", domain="news")

    results = pipeline.search(
        query="press conference speech",
        domain_filter="news",
        alpha=0.6,
        top_k=5,
    )
    pipeline.close()
"""

from __future__ import annotations

# ── CPU thread limits (must precede torch / numpy / cv2 imports) ─────────
import os

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from qdrant_client.models import FieldCondition, Filter, MatchValue

from src.db.qdrant_db import QdrantVectorStore
from src.ingestion.audio_processor import AudioTranscriber
from src.ingestion.video_processor import VideoProcessor
from src.models.text_encoder import TextQueryEncoder
from src.models.vision_encoder import CLIPVisionEncoder

logger = logging.getLogger(__name__)


VISUAL_KEYWORDS = {
    "visual", "scene", "showing", "look", "looking", "whiteboard", "diagram",
    "podium", "suit", "red tie", "flag", "banner", "crowd", "stage", "camera",
    "background", "wearing", "standing", "sitting", "walking", "gesturing",
}
AUDIO_KEYWORDS = {
    "said", "speech", "transcript", "audio", "talking", "spoken", "words",
    "statement", "quote", "announced", "declared", "mentioned", "retaliate",
    "economy", "inflation", "interview", "podcast",
}


def predict_alpha_intent(query: str) -> float:
    """Classify query intent using keyword matching to determine optimal alpha."""
    q_lower = query.lower()
    has_visual = any(kw in q_lower for kw in VISUAL_KEYWORDS)
    has_audio = any(kw in q_lower for kw in AUDIO_KEYWORDS)

    if has_visual and not has_audio:
        return 0.8
    elif has_audio and not has_visual:
        return 0.2
    else:
        return 0.5


class VideoSearchPipeline:
    """End-to-end multimodal video ingestion and retrieval pipeline.

    Parameters
    ----------
    db_path : str | Path
        Path to local Qdrant database directory.
    frames_dir : str | Path
        Directory for storing extracted keyframe JPEGs.
    """


    def __init__(
        self,
        db_path: Union[str, Path] = "./data/qdrant_db",
        frames_dir: Union[str, Path] = "./data/extracted_frames",
    ) -> None:
        self.db_path = Path(db_path)
        self.frames_dir = Path(frames_dir)
        self.frames_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Initializing VideoSearchPipeline with database at %s", self.db_path)
        self.vector_store = QdrantVectorStore(db_path=self.db_path)
        self.vector_store.init_collection()

        self.video_processor = VideoProcessor()
        self.audio_transcriber = AudioTranscriber()
        self.vision_encoder = CLIPVisionEncoder()
        self.text_encoder = TextQueryEncoder()

        logger.info("VideoSearchPipeline initialization complete.")

    # ------------------------------------------------------------------
    # Video Ingestion
    # ------------------------------------------------------------------
    def ingest_video(self, video_path: str, domain: str = "news") -> int:
        """Ingest a video file into the search engine.

        1. Extracts keyframes at 1 fps.
        2. Transcribes audio via Whisper.
        3. Encodes visual keyframes via CLIPVisionEncoder.
        4. Matches transcript segments to keyframes and encodes audio text via TextQueryEncoder.
        5. Upserts points into Qdrant vector store.

        Parameters
        ----------
        video_path : str
            Path to input MP4 video file.
        domain : str
            Domain tag for payload metadata (e.g., ``"news"``, ``"sports"``).

        Returns
        -------
        int
            Number of points ingested into the database.
        """
        vpath = Path(video_path).resolve()
        if not vpath.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        video_id = self.video_processor._make_video_id(str(vpath))
        target_frames_dir = self.frames_dir / video_id
        target_frames_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Step 1/4: Extracting keyframes for %s …", vpath.name)
        keyframes = self.video_processor.extract_keyframes(
            video_path=str(vpath),
            output_dir=str(target_frames_dir),
            target_fps=1.0,
        )

        if not keyframes:
            logger.warning("No keyframes extracted from %s", vpath.name)
            return 0

        logger.info("Step 2/4: Transcribing audio for %s …", vpath.name)
        segments = self.audio_transcriber.transcribe(str(vpath))

        logger.info("Step 3/4: Encoding %d visual keyframes …", len(keyframes))
        frame_paths = [f["frame_path"] for f in keyframes]
        visual_vecs = self.vision_encoder.encode_batch_images(frame_paths, batch_size=8)

        logger.info("Step 4/4: Matching transcripts and encoding audio text …")
        audio_texts: List[str] = []
        for f in keyframes:
            ts = f["timestamp"]
            # Find matching transcript segment covering this timestamp
            matched_text = ""
            for seg in segments:
                if seg["start"] <= ts <= seg["end"] or abs(ts - seg["start"]) <= 1.5:
                    matched_text = seg["text"]
                    break
            # Fallback text if silent frame to ensure non-zero audio vector representation
            fallback_text = matched_text if matched_text else "news video footage scene"
            audio_texts.append(fallback_text)

        audio_vecs = self.text_encoder.encode_batch_queries(audio_texts)

        # Build Qdrant points
        points: List[Dict[str, Any]] = []
        for idx, f in enumerate(keyframes):
            pt = {
                "visual_vector": visual_vecs[idx].tolist(),
                "audio_vector": audio_vecs[idx].tolist(),
                "video_id": f["video_id"],
                "timestamp": f["timestamp"],
                "frame_idx": f["frame_idx"],
                "transcribed_text": audio_texts[idx],
                "domain": domain,
                "frame_path": f["frame_path"],
            }
            points.append(pt)

        self.vector_store.upsert_points(points)
        logger.info("Successfully ingested %d points for video %s", len(points), vpath.name)
        return len(points)

    # ------------------------------------------------------------------
    # Hybrid Search with Reciprocal Rank Fusion (RRF) & Dynamic Masking
    # ------------------------------------------------------------------
    def search(
        self,
        query: str,
        domain_filter: Optional[str] = "news",
        alpha: Optional[float] = 0.5,
        top_k: int = 5,
        rrf_k: int = 60,
        min_confidence_threshold: float = 0.15,
        enable_reranker: bool = False,
        enable_mmr: bool = True,
    ) -> Dict[str, Any]:
        """Search videos using Reciprocal Rank Fusion (RRF), Dynamic Modality Masking, Agreement Scoring, and MMR.

        Parameters
        ----------
        query : str
            Natural language search query.
        domain_filter : str | None
            Optional domain tag to filter results by.
        alpha : float | None
            Visual vector weight in fusion. If None, auto-intent prediction is used.
        top_k : int
            Number of top results to return.
        rrf_k : int
            RRF smoothing constant (default 60).
        min_confidence_threshold : float
            Minimum raw similarity threshold.
        enable_reranker : bool
            Whether to apply Top-20 Cross-Modal Agreement Scoring (default False).
        enable_mmr : bool
            Whether to apply Semantic Vector MMR diversification (default True).
        """
        effective_alpha = alpha
        if effective_alpha is None:
            effective_alpha = predict_alpha_intent(query)

        logger.info("Encoding query: '%s' (effective_alpha=%.2f)", query, effective_alpha)
        query_vec = self.text_encoder.encode_query(query).tolist()

        filter_cond = None
        if domain_filter and domain_filter.lower() != "all":
            filter_cond = Filter(
                must=[
                    FieldCondition(
                        key="domain",
                        match=MatchValue(value=domain_filter),
                    )
                ]
            )

        fetch_limit = max(top_k * 4, 30)

        # Retrieve visual and audio nearest neighbours
        visual_hits = self.vector_store.search_vectors(
            query_vector=query_vec,
            vector_name="visual_vector",
            top_k=fetch_limit,
            filter_conditions=filter_cond,
        )

        audio_hits = self.vector_store.search_vectors(
            query_vector=query_vec,
            vector_name="audio_vector",
            top_k=fetch_limit,
            filter_conditions=filter_cond,
        )

        # Build rank lookups (1-indexed)
        visual_ranks: Dict[Any, int] = {hit["id"]: i + 1 for i, hit in enumerate(visual_hits)}
        audio_ranks: Dict[Any, int] = {hit["id"]: i + 1 for i, hit in enumerate(audio_hits)}

        visual_scores: Dict[Any, float] = {hit["id"]: hit["score"] for hit in visual_hits}
        audio_scores: Dict[Any, float] = {hit["id"]: hit["score"] for hit in audio_hits}
        payload_map: Dict[Any, Dict[str, Any]] = {hit["id"]: hit["payload"] for hit in visual_hits + audio_hits}
        vector_map: Dict[Any, Any] = {hit["id"]: hit.get("visual_vector") for hit in visual_hits if hit.get("visual_vector") is not None}

        all_ids = set(visual_ranks.keys()).union(audio_ranks.keys())

        if not all_ids:
            return {"status": "NO_CONFIDENT_MATCH_FOUND", "results": [], "masked_modality": None}

        # Check maximum raw confidence across hits
        max_raw_v = max(visual_scores.values()) if visual_scores else 0.0
        max_raw_a = max(audio_scores.values()) if audio_scores else 0.0
        max_raw = max(max_raw_v, max_raw_a)

        if max_raw < min_confidence_threshold:
            logger.warning("Query '%s' failed confidence threshold (max_raw=%.4f < %.4f)", query, max_raw, min_confidence_threshold)
            return {"status": "NO_CONFIDENT_MATCH_FOUND", "results": [], "masked_modality": None}

        # Check audio score variance across candidate hits
        audio_scores_list = list(audio_scores.values())
        audio_var = 0.0
        if len(audio_scores_list) > 1:
            mean_a = sum(audio_scores_list) / len(audio_scores_list)
            audio_var = sum((s - mean_a) ** 2 for s in audio_scores_list) / len(audio_scores_list)

        low_audio_variance = audio_var < 0.005

        results: List[Dict[str, Any]] = []
        global_masked_modality = None

        if low_audio_variance:
            global_masked_modality = "audio (low variance)"

        for cid in all_ids:
            payload = payload_map[cid]
            v_score = visual_scores.get(cid, 0.0)
            a_score = audio_scores.get(cid, 0.0)

            r_v = visual_ranks.get(cid, 1000)
            r_a = audio_ranks.get(cid, 1000)

            # Dynamic Modality Masking: If audio transcript is empty or audio score variance is low
            transcript = payload.get("transcribed_text", "").strip()
            is_silent = not transcript or transcript.lower() == "news video footage scene"

            if is_silent or low_audio_variance:
                w_v, w_a = 1.0, 0.0
                if is_silent:
                    global_masked_modality = "audio (silent)"
            else:
                w_v, w_a = effective_alpha, (1.0 - effective_alpha)

            # Reciprocal Rank Fusion Calculation
            rrf_score = (w_v / (rrf_k + r_v)) + (w_a / (rrf_k + r_a))
            # Normalized linear fused score for backwards compatibility and UI display
            fused_linear = (w_v * v_score) + (w_a * a_score)

            ts = float(payload.get("timestamp", 0.0))
            event_start = max(0.0, round(ts - 10.0, 1))
            event_end = round(ts + 10.0, 1)
            mins, secs = int(ts // 60), int(ts % 60)

            event_segment = {
                "video_id": payload.get("video_id", ""),
                "event_start": event_start,
                "event_end": event_end,
                "hero_keyframe_timestamp": ts,
                "hero_keyframe_path": payload.get("frame_path", ""),
                "full_transcript_segment": transcript if transcript else "Visual footage scene (silent)",
                "visual_scene_description": f"Keyframe visual elements matching '{query}' at timestamp {mins:02d}:{secs:02d}",
            }

            results.append({
                "id": cid,
                "score": round(float(fused_linear), 6),
                "rrf_score": round(float(rrf_score), 6),
                "visual_score": round(float(v_score), 6),
                "audio_score": round(float(a_score), 6),
                "visual_vector": vector_map.get(cid),
                "payload": payload,
                "event_segment": event_segment,
                "modality_weights": {"visual": w_v, "audio": w_a},
            })

        # Sort candidate pool by RRF score descending
        results.sort(key=lambda x: x["rrf_score"], reverse=True)

        # Stage 1: Optional Top-20 Cross-Modal Agreement Scoring
        if enable_reranker:
            candidate_pool = self._apply_cross_modal_agreement_score(results[:20])
        else:
            candidate_pool = results

        # Stage 2: Optional Semantic Vector MMR Diversification
        if enable_mmr:
            top_results = self._apply_mmr_diversification(candidate_pool, top_k=top_k, lambda_param=0.7)
        else:
            top_results = candidate_pool[:top_k]

        # Stage 3: Attach confidence_band and match_rationale to each result
        for res in top_results:
            res["confidence_band"] = self._get_confidence_band(res)
            res["match_rationale"] = self._get_match_rationale(res, enable_reranker, enable_mmr, global_masked_modality)

        logger.info("Search complete (agreement_score=%s, mmr=%s) — returned top-%d candidates.", enable_reranker, enable_mmr, len(top_results))
        return {
            "status": "SUCCESS",
            "results": top_results,
            "masked_modality": global_masked_modality,
        }

    # ------------------------------------------------------------------
    # Cross-Modal Agreement Scoring Helper
    # ------------------------------------------------------------------
    @staticmethod
    def _apply_cross_modal_agreement_score(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Top-20 Cross-Modal Agreement Scoring: agreement multiplier 1.0 + 0.5 * (visual_score * audio_score)."""
        reranked: List[Dict[str, Any]] = []
        for cand in candidates:
            rrf_sc = cand.get("rrf_score", 0.0)
            v_sc = cand.get("visual_score", 0.0)
            a_sc = cand.get("audio_score", 0.0)

            # Cross-modal agreement multiplier: 1.0 + 0.5 * (visual_score * audio_score)
            cross_agreement = float(v_sc * a_sc)
            rerank_score = rrf_sc * (1.0 + 0.5 * cross_agreement)

            cand_copy = dict(cand)
            cand_copy["rerank_score"] = round(rerank_score, 6)
            reranked.append(cand_copy)

        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        return reranked

    # ------------------------------------------------------------------
    # Confidence Band & Match Rationale Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _get_confidence_band(result: Dict[str, Any]) -> str:
        """Map a result's fused score to a bounded confidence band (HIGH / MEDIUM / LOW)."""
        score = result.get("score", 0.0)
        rrf = result.get("rrf_score", 0.0)
        if score >= 0.70 or rrf >= 0.020:
            return "HIGH"
        elif score >= 0.35 or rrf >= 0.010:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _get_match_rationale(
        result: Dict[str, Any],
        agreement_applied: bool,
        mmr_applied: bool,
        masked_modality: Optional[str],
    ) -> List[str]:
        """Build a human-readable list of match rationale strings for a search result."""
        rationale: List[str] = []

        v = result.get("visual_score", 0.0)
        a = result.get("audio_score", 0.0)

        rationale.append(f"✓ Visual similarity: {v:.4f}")
        rationale.append(f"✓ Audio similarity: {a:.4f}")
        rationale.append(f"✓ RRF fusion score: {result.get('rrf_score', 0.0):.6f}")

        if masked_modality:
            rationale.append(f"⚠ Modality masked: {masked_modality}")

        if agreement_applied:
            rationale.append("✓ Cross-Modal Agreement Scoring applied")

        if mmr_applied:
            rationale.append("✓ MMR diversification applied")

        return rationale

    # ------------------------------------------------------------------
    # Semantic Vector MMR Diversification Helper
    # ------------------------------------------------------------------
    @staticmethod
    def _cosine_sim(v1: Optional[List[float]], v2: Optional[List[float]]) -> float:
        """Compute cosine similarity between two 512-D visual vectors."""
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        import numpy as np
        a1 = np.array(v1, dtype=np.float32)
        a2 = np.array(v2, dtype=np.float32)
        n1, n2 = np.linalg.norm(a1), np.linalg.norm(a2)
        if n1 == 0 or n2 == 0:
            return 0.0
        return float(np.dot(a1, a2) / (n1 * n2))

    @classmethod
    def _apply_mmr_diversification(
        cls,
        candidates: List[Dict[str, Any]],
        top_k: int = 5,
        lambda_param: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Apply Maximal Marginal Relevance (MMR) using pairwise Cosine Similarity over candidate 512-D visual vectors."""
        if not candidates:
            return []

        selected: List[Dict[str, Any]] = [candidates[0]]
        remaining: List[Dict[str, Any]] = candidates[1:]

        while len(selected) < top_k and remaining:
            best_candidate = None
            best_mmr_score = -float("inf")
            best_idx = -1

            for idx, cand in enumerate(remaining):
                rrf_sc = cand.get("rrf_score", 0.0)
                cand_v = cand.get("visual_vector")

                max_sim = 0.0
                for sel in selected:
                    sel_v = sel.get("visual_vector")
                    if cand_v and sel_v:
                        sim = cls._cosine_sim(cand_v, sel_v)
                    else:
                        # Fallback for candidates without vector embeddings
                        if cand["payload"].get("video_id") == sel["payload"].get("video_id"):
                            ts_diff = abs(cand["payload"].get("timestamp", 0.0) - sel["payload"].get("timestamp", 0.0))
                            sim = 1.0 if ts_diff <= 15.0 else 0.4
                        else:
                            sim = 0.0

                    if sim > max_sim:
                        max_sim = sim

                mmr_score = (lambda_param * rrf_sc) - ((1.0 - lambda_param) * max_sim)
                if mmr_score > best_mmr_score:
                    best_mmr_score = mmr_score
                    best_candidate = cand
                    best_idx = idx

            if best_candidate is not None:
                selected.append(best_candidate)
                remaining.pop(best_idx)
            else:
                break

        return selected

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def close(self) -> None:
        """Close vector store connection."""
        if hasattr(self, "vector_store") and self.vector_store is not None:
            self.vector_store.close()
            logger.info("VideoSearchPipeline connection closed.")

    def __enter__(self) -> "VideoSearchPipeline":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        self.close()
