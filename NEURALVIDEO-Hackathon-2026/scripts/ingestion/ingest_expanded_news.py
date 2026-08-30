"""
Large News Corpus Ingestion Script — Parallel Qdrant Collection.

Ingests MP4 files from ``./data/news_corpus_large/`` into a NEW Qdrant
collection ``video_intelligence_v2``, completely isolated from the
primary ``video_intelligence`` collection.

Reuses the existing VideoProcessor, AudioTranscriber, CLIPVisionEncoder,
and TextQueryEncoder components but targets the v2 collection directly.

Usage:
    python ingest_expanded_news.py
    python ingest_expanded_news.py --dir data/news_corpus_large --domain news
"""

from __future__ import annotations

# ── CPU thread limits (must precede torch / numpy imports) ──────────────
import os

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import argparse
import gc
import logging
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

import torch
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from src.ingestion.audio_processor import AudioTranscriber
from src.ingestion.video_processor import VideoProcessor
from src.models.text_encoder import TextQueryEncoder
from src.models.vision_encoder import CLIPVisionEncoder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
V2_COLLECTION_NAME = "video_intelligence_v2"
VISUAL_VECTOR_NAME = "visual_vector"
AUDIO_VECTOR_NAME = "audio_vector"
VECTOR_DIM = 512
SUPPORTED_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm"}


def init_v2_collection(client: QdrantClient) -> None:
    """Create the v2 collection if it does not already exist."""
    existing = [c.name for c in client.get_collections().collections]
    if V2_COLLECTION_NAME in existing:
        logger.info("Collection '%s' already exists — skipping creation.", V2_COLLECTION_NAME)
        return

    client.create_collection(
        collection_name=V2_COLLECTION_NAME,
        vectors_config={
            VISUAL_VECTOR_NAME: VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
            AUDIO_VECTOR_NAME: VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
        },
    )
    logger.info("Created collection '%s'.", V2_COLLECTION_NAME)


def upsert_points_v2(
    client: QdrantClient,
    points: List[Dict[str, Any]],
    batch_size: int = 64,
) -> None:
    """Upsert points into the v2 collection."""
    structs: List[PointStruct] = []
    for pt in points:
        point_id = pt.get("id", str(uuid.uuid4()))
        structs.append(
            PointStruct(
                id=point_id,
                vector={
                    VISUAL_VECTOR_NAME: pt["visual_vector"],
                    AUDIO_VECTOR_NAME: pt["audio_vector"],
                },
                payload={
                    "video_id": pt["video_id"],
                    "timestamp": pt["timestamp"],
                    "frame_idx": pt["frame_idx"],
                    "transcribed_text": pt["transcribed_text"],
                    "domain": pt.get("domain", "news"),
                    "frame_path": pt.get("frame_path", ""),
                },
            )
        )

    for i in range(0, len(structs), batch_size):
        batch = structs[i : i + batch_size]
        client.upsert(collection_name=V2_COLLECTION_NAME, points=batch)

    logger.info("Upserted %d points into '%s'.", len(structs), V2_COLLECTION_NAME)


def ingest_single_video(
    video_path: Path,
    domain: str,
    frames_dir: Path,
    video_processor: VideoProcessor,
    audio_transcriber: AudioTranscriber,
    vision_encoder: CLIPVisionEncoder,
    text_encoder: TextQueryEncoder,
) -> List[Dict[str, Any]]:
    """Process a single video and return Qdrant-ready point dicts."""
    video_id = video_processor._make_video_id(str(video_path))
    target_dir = frames_dir / video_id
    target_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Extract keyframes at 1 fps
    keyframes = video_processor.extract_keyframes(
        video_path=str(video_path),
        output_dir=str(target_dir),
        target_fps=1.0,
    )
    if not keyframes:
        logger.warning("No keyframes extracted from %s", video_path.name)
        return []

    # Step 2: Transcribe audio via Whisper
    segments = audio_transcriber.transcribe(str(video_path))

    # Step 3: Encode visual keyframes via CLIP (micro-batch size 8)
    frame_paths = [f["frame_path"] for f in keyframes]
    visual_vecs = vision_encoder.encode_batch_images(frame_paths, batch_size=8)

    # Step 4: Match transcripts to frames and encode audio text
    audio_texts: List[str] = []
    for f in keyframes:
        ts = f["timestamp"]
        matched_text = ""
        for seg in segments:
            if seg["start"] <= ts <= seg["end"] or abs(ts - seg["start"]) <= 1.5:
                matched_text = seg["text"]
                break
        audio_texts.append(matched_text if matched_text else "news video footage scene")

    audio_vecs = text_encoder.encode_batch_queries(audio_texts)

    # Build point dicts
    points: List[Dict[str, Any]] = []
    for idx, f in enumerate(keyframes):
        points.append({
            "visual_vector": visual_vecs[idx].tolist(),
            "audio_vector": audio_vecs[idx].tolist(),
            "video_id": f["video_id"],
            "timestamp": f["timestamp"],
            "frame_idx": f["frame_idx"],
            "transcribed_text": audio_texts[idx],
            "domain": domain,
            "frame_path": f["frame_path"],
        })

    return points


def clear_memory() -> None:
    """Aggressive memory cleanup after each video."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def ingest_expanded_corpus(
    input_dir: Union[str, Path] = "./data/raw/news_corpus_large",
    domain: str = "news",
    db_path: Union[str, Path] = "./data/vectors/qdrant_db",
) -> Dict[str, Any]:
    """Ingest all videos from input_dir into video_intelligence_v2."""
    in_path = Path(input_dir).resolve()
    if not in_path.exists() or not in_path.is_dir():
        print(f"[ERROR] Input directory does not exist: {in_path}")
        print(f"[INFO]  Create '{input_dir}/' and place MP4 files inside before running.")
        return {"processed": 0, "skipped": 0, "total_points": 0, "total_time_sec": 0.0}

    video_files = sorted(
        p for p in in_path.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not video_files:
        print(f"[BATCH] No supported video files found in {in_path}")
        return {"processed": 0, "skipped": 0, "total_points": 0, "total_time_sec": 0.0}

    print("=" * 72)
    print("  EXPANDED NEWS CORPUS INGESTION — video_intelligence_v2")
    print("=" * 72)
    print(f"  Source directory : {in_path}")
    print(f"  Video files found: {len(video_files)}")
    print(f"  Target collection: {V2_COLLECTION_NAME}")
    print(f"  Domain tag       : {domain}")
    print("-" * 72)

    # Initialize Qdrant v2 collection
    db_full_path = Path(db_path)
    db_full_path.mkdir(parents=True, exist_ok=True)
    client = QdrantClient(path=str(db_full_path))
    init_v2_collection(client)

    # Initialize processing components
    frames_dir = Path("./data/processed/extracted_frames_v2")
    frames_dir.mkdir(parents=True, exist_ok=True)

    video_processor = VideoProcessor()
    audio_transcriber = AudioTranscriber()
    vision_encoder = CLIPVisionEncoder()
    text_encoder = TextQueryEncoder()

    processed = 0
    skipped = 0
    total_points = 0
    file_reports: List[Dict[str, Any]] = []
    t_start = time.perf_counter()

    for idx, vfile in enumerate(video_files, 1):
        v_start = time.perf_counter()

        try:
            points = ingest_single_video(
                video_path=vfile,
                domain=domain,
                frames_dir=frames_dir,
                video_processor=video_processor,
                audio_transcriber=audio_transcriber,
                vision_encoder=vision_encoder,
                text_encoder=text_encoder,
            )

            if points:
                upsert_points_v2(client, points)

            v_elapsed = time.perf_counter() - v_start
            processed += 1
            total_points += len(points)
            file_reports.append({
                "file": vfile.name, "status": "SUCCESS",
                "points": len(points), "time_sec": round(v_elapsed, 2),
            })
            print(f"  [{idx}/{len(video_files)}] ✅ Processed {vfile.name} -> Added {len(points)} points. Memory clear.")

        except Exception as err:
            v_elapsed = time.perf_counter() - v_start
            skipped += 1
            logger.error("Error processing %s: %s", vfile.name, err, exc_info=True)
            file_reports.append({
                "file": vfile.name, "status": f"FAILED ({err.__class__.__name__})",
                "points": 0, "time_sec": round(v_elapsed, 2),
            })
            print(f"  [{idx}/{len(video_files)}] ❌ {vfile.name}: Skipped ({err})")

        finally:
            clear_memory()

    total_time = time.perf_counter() - t_start

    # Verify v2 collection point count
    v2_count = client.count(collection_name=V2_COLLECTION_NAME).count
    client.close()

    # Summary table
    print("\n" + "=" * 72)
    print("  EXPANDED CORPUS INGESTION SUMMARY")
    print("=" * 72)
    print(f"  {'Filename':<38}{'Status':<18}{'Points':<10}{'Time (s)'}")
    print("-" * 72)
    for r in file_reports:
        print(f"  {r['file']:<38}{r['status']:<18}{r['points']:<10}{r['time_sec']:.2f}")
    print("-" * 72)
    print(f"  Total Videos Processed : {processed}")
    print(f"  Total Videos Skipped   : {skipped}")
    print(f"  Total Points Indexed   : {total_points}")
    print(f"  Collection v2 Count    : {v2_count}")
    print(f"  Total Ingestion Time   : {total_time:.2f} s")
    print("=" * 72 + "\n")

    return {
        "processed": processed,
        "skipped": skipped,
        "total_points": total_points,
        "total_time_sec": round(total_time, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest expanded news corpus into video_intelligence_v2."
    )
    parser.add_argument("--dir", type=str, default="./data/news_corpus_large",
                        help="Input directory (default: ./data/news_corpus_large)")
    parser.add_argument("--domain", type=str, default="news",
                        help="Domain tag (default: news)")
    parser.add_argument("--db-path", type=str, default="./data/qdrant_db",
                        help="Qdrant DB path (default: ./data/qdrant_db)")
    args = parser.parse_args()

    ingest_expanded_corpus(
        input_dir=args.dir, domain=args.domain, db_path=args.db_path,
    )


if __name__ == "__main__":
    main()
