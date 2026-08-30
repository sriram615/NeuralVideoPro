"""
Ranker & XAI Module — NEURALVIDEO v5.0

Implements:
    1. Temporal Window Merging & De-duplication (merge_temporal_windows)
    2. Calibrated Qualitative Confidence Scoring (get_calibrated_confidence_band)
    3. XAI Attribution & Rationale Generation (calculate_xai_attribution)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def merge_temporal_windows(
    candidates: List[Dict[str, Any]],
    max_delta_sec: float = 5.0,
) -> List[Dict[str, Any]]:
    """Merge contiguous timestamp search hits from the same video into unified clip segments.

    Consolidation Rules:
        - Candidates within max_delta_sec (default 5.0s) sharing video_id are merged.
        - Fused scores, visual_score, audio_score, rrf_score are aggregated via max-pooling.
        - Hero keyframe path & timestamp are selected from the highest-scoring frame.
        - Unique spoken dialogue transcript chunks are concatenated across the window.

    Parameters
    ----------
    candidates : list[dict]
        Ranked search candidate dictionaries.
    max_delta_sec : float
        Maximum allowable gap between contiguous keyframe timestamps for merging.

    Returns
    -------
    list[dict]
        Consolidated, de-duplicated list of search results.
    """
    if not candidates:
        return []

    # Group candidates by video_id
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for cand in candidates:
        payload = cand.get("payload", {})
        vid = payload.get("video_id", "unknown")
        groups.setdefault(vid, []).append(cand)

    merged_results: List[Dict[str, Any]] = []

    for vid, group in groups.items():
        # Sort candidate hits by timestamp ascending
        group.sort(key=lambda x: float(x.get("payload", {}).get("timestamp", 0.0)))

        clusters: List[List[Dict[str, Any]]] = []
        current_cluster: List[Dict[str, Any]] = []

        for cand in group:
            if not current_cluster:
                current_cluster.append(cand)
            else:
                prev_ts = float(current_cluster[-1].get("payload", {}).get("timestamp", 0.0))
                curr_ts = float(cand.get("payload", {}).get("timestamp", 0.0))

                if abs(curr_ts - prev_ts) <= max_delta_sec:
                    current_cluster.append(cand)
                else:
                    clusters.append(current_cluster)
                    current_cluster = [cand]

        if current_cluster:
            clusters.append(current_cluster)

        # Merge each cluster into a single representative event segment
        for cluster in clusters:
            # Hero candidate = max-pooled by rrf_score or fused score
            hero = max(cluster, key=lambda x: float(x.get("rrf_score", x.get("score", 0.0))))

            max_fused = max(float(x.get("score", 0.0)) for x in cluster)
            max_visual = max(float(x.get("visual_score", 0.0)) for x in cluster)
            max_audio = max(float(x.get("audio_score", 0.0)) for x in cluster)
            max_rrf = max(float(x.get("rrf_score", 0.0)) for x in cluster)

            timestamps = [float(x.get("payload", {}).get("timestamp", 0.0)) for x in cluster]
            t_start = round(min(timestamps), 2)
            t_end = round(max(timestamps) + 2.0, 2)

            # Concatenate unique transcript text chunks
            transcripts: List[str] = []
            for item in cluster:
                txt = item.get("payload", {}).get("transcribed_text", "").strip()
                if txt and txt.lower() != "news video footage scene" and txt not in transcripts:
                    transcripts.append(txt)

            full_transcript = " ".join(transcripts) if transcripts else "Visual scene footage"

            hero_ts = float(hero.get("payload", {}).get("timestamp", 0.0))
            hero_frame_path = hero.get("payload", {}).get("frame_path", "")

            # Consolidated Event Segment Payload
            consolidated_event = {
                "video_id": vid,
                "event_start": t_start,
                "event_end": t_end,
                "hero_keyframe_timestamp": hero_ts,
                "hero_keyframe_path": hero_frame_path,
                "full_transcript_segment": full_transcript,
                "visual_scene_description": f"Keyframe visual scene in window {t_start:.1f}s–{t_end:.1f}s",
            }

            merged_item = dict(hero)
            merged_item["score"] = round(max_fused, 6)
            merged_item["visual_score"] = round(max_visual, 6)
            merged_item["audio_score"] = round(max_audio, 6)
            merged_item["rrf_score"] = round(max_rrf, 6)
            merged_item["event_segment"] = consolidated_event
            merged_item["payload"] = dict(hero.get("payload", {}))
            merged_item["payload"]["transcribed_text"] = full_transcript

            merged_results.append(merged_item)

    # Sort final consolidated list by rrf_score / score descending
    merged_results.sort(key=lambda x: float(x.get("rrf_score", x.get("score", 0.0))), reverse=True)
    return merged_results


def get_calibrated_confidence_band(
    score: float,
    rrf_score: float = 0.0,
    visual_score: float = 0.0,
    audio_score: float = 0.0,
) -> str:
    """Map empirical similarity & RRF scores to calibrated qualitative confidence bands.

    Threshold Tiers:
        - "HIGH"   : Strong audio match (>= 0.85) OR strong visual match (>= 0.28) OR Top-1 RRF match with score >= 0.25
        - "MEDIUM" : Moderate audio match (>= 0.65) OR moderate visual match (>= 0.21) OR RRF >= 0.008
        - "LOW"    : Distant / Weak similarity score (< 0.21 visual & < 0.65 audio)

    Returns
    -------
    str
        Qualitative tier label ("HIGH", "MEDIUM", or "LOW").
    """
    if audio_score >= 0.85 or visual_score >= 0.28 or (score >= 0.25 and rrf_score >= 0.016):
        return "HIGH"
    elif audio_score >= 0.65 or visual_score >= 0.21 or score >= 0.15 or rrf_score >= 0.008:
        return "MEDIUM"
    else:
        return "LOW"


def calculate_xai_attribution(
    visual_score: float,
    audio_score: float,
    fused_score: float,
    rrf_score: Optional[float] = None,
    alpha: float = 0.5,
) -> Dict[str, Any]:
    """Calculate Explainable AI (XAI) attribution metrics and non-hallucinated confidence tiers."""
    v_pct = round(min(100.0, max(0.0, visual_score * 100.0)), 1)
    a_pct = round(min(100.0, max(0.0, audio_score * 100.0)), 1)
    f_pct = round(min(100.0, max(0.0, fused_score * 100.0)), 1)

    if visual_score >= audio_score:
        driver = "CLIP Visual Scene"
        emoji = "👁️"
    else:
        driver = "Whisper Audio Transcript"
        emoji = "🎧"

    formula = f"({alpha:.2f} × Visual) + ({(1.0 - alpha):.2f} × Audio)"
    confidence = get_calibrated_confidence_band(fused_score, rrf_score or 0.0, visual_score, audio_score)

    return {
        "primary_driver": driver,
        "primary_driver_emoji": emoji,
        "visual_similarity_pct": v_pct,
        "audio_similarity_pct": a_pct,
        "fused_score_pct": f_pct,
        "rrf_score": rrf_score,
        "fusion_formula": formula,
        "confidence_tier": confidence,
    }
