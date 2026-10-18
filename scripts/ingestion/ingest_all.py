"""
Batch Ingestion — Ingest every video in data/raw/raw_videos/ into Qdrant.

Reuses VideoSearchPipeline.ingest_video() for each source file so the
end-to-end pipeline (keyframe extraction → Whisper transcription → CLIP
encoding → Qdrant upsert) is exercised exactly once per video.

Usage:
    python scripts/ingestion/ingest_all.py
    python scripts/ingestion/ingest_all.py --dir data/raw/raw_videos --domain news
    python scripts/ingestion/ingest_all.py --db-path ./data/vectors/qdrant_db

Notes:
    - Supported extensions: .mp4 .mov .mkv .avi .webm
    - .zip archives and other non-video files are skipped.
    - One video failure does not abort the whole batch.
"""

from __future__ import annotations

import argparse
import gc
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# ── CPU thread limits (must precede torch / numpy imports) ──────────────
import os

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from src.db.qdrant_db import COLLECTION_NAME  # noqa: E402
from src.pipeline import VideoSearchPipeline  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ingest_all")

SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}


def find_video_files(input_dir: Path) -> List[Path]:
    """Return sorted list of supported video files in *input_dir*."""
    if not input_dir.exists() or not input_dir.is_dir():
        return []
    return sorted(
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def ingest_all(
    input_dir: Union[str, Path] = "./data/raw/raw_videos",
    domain: str = "news",
    db_path: Union[str, Path] = "./data/vectors/qdrant_db",
    frames_dir: Union[str, Path] = "./data/processed/extracted_frames_v2",
) -> Dict[str, Any]:
    """Ingest every supported video in *input_dir* into Qdrant.

    Returns a summary dict with per-file reports and aggregate stats.
    """
    in_path = Path(input_dir).resolve()
    video_files = find_video_files(in_path)

    print("=" * 72)
    print("  NEURALVIDEO v5.0 — BATCH VIDEO INGESTION")
    print("=" * 72)
    print(f"  Source directory : {in_path}")
    print(f"  Video files found: {len(video_files)}")
    print(f"  Target domain    : {domain}")
    print(f"  Qdrant DB path   : {db_path}")
    print(f"  Frames directory : {frames_dir}")
    print("-" * 72)

    if not video_files:
        print(f"[BATCH] No supported video files found in {in_path}")
        print("  Place .mp4 / .mov / .mkv / .avi / .webm files in the source directory.")
        print("=" * 72 + "\n")
        return {
            "processed": 0,
            "skipped": 0,
            "total_points": 0,
            "total_time_sec": 0.0,
            "files": [],
        }

    # Instantiate pipeline once — models loaded once, reused across videos.
    pipeline = VideoSearchPipeline(db_path=db_path, frames_dir=frames_dir)

    processed = 0
    skipped = 0
    total_points = 0
    file_reports: List[Dict[str, Any]] = []
    t_start = time.perf_counter()

    for idx, vfile in enumerate(video_files, 1):
        v_start = time.perf_counter()

        try:
            num_points = pipeline.ingest_video(str(vfile), domain=domain)
            v_elapsed = time.perf_counter() - v_start

            processed += 1
            total_points += num_points
            file_reports.append({
                "file": vfile.name,
                "status": "SUCCESS",
                "points": num_points,
                "time_sec": round(v_elapsed, 2),
            })
            print(
                f"  [{idx}/{len(video_files)}] ✅ {vfile.name} "
                f"→ {num_points} points in {v_elapsed:.2f}s"
            )

        except Exception as err:  # noqa: BLE001 — one failure must not abort the batch
            v_elapsed = time.perf_counter() - v_start
            skipped += 1
            logger.error("Failed to ingest %s: %s", vfile.name, err, exc_info=True)
            file_reports.append({
                "file": vfile.name,
                "status": f"FAILED ({err.__class__.__name__})",
                "points": 0,
                "time_sec": round(v_elapsed, 2),
            })
            print(f"  [{idx}/{len(video_files)}] ❌ {vfile.name}: skipped ({err})")

        finally:
            gc.collect()

    total_time = time.perf_counter() - t_start

    # Verify total point count in the collection
    try:
        collection_count = pipeline.vector_store.client.count(
            collection_name=COLLECTION_NAME
        ).count
    except Exception:  # noqa: BLE001
        collection_count = None

    pipeline.close()

    # Summary table
    print("\n" + "=" * 72)
    print("  BATCH INGESTION SUMMARY")
    print("=" * 72)
    print(f"  {'Filename':<40}{'Status':<20}{'Points':<10}{'Time (s)'}")
    print("-" * 72)
    for r in file_reports:
        print(f"  {r['file']:<40}{r['status']:<20}{r['points']:<10}{r['time_sec']:.2f}")
    print("-" * 72)
    print(f"  Total Videos Processed : {processed}")
    print(f"  Total Videos Skipped   : {skipped}")
    print(f"  Total Points Indexed   : {total_points}")
    if collection_count is not None:
        print(f"  Qdrant Collection Count: {collection_count}")
    print(f"  Total Ingestion Time   : {total_time:.2f} s")
    print("=" * 72 + "\n")

    return {
        "processed": processed,
        "skipped": skipped,
        "total_points": total_points,
        "total_time_sec": round(total_time, 2),
        "collection_count": collection_count,
        "files": file_reports,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest every video in data/raw/raw_videos/ into Qdrant."
    )
    parser.add_argument(
        "--dir", type=str, default="./data/raw/raw_videos",
        help="Input directory containing source videos (default: ./data/raw/raw_videos)",
    )
    parser.add_argument(
        "--domain", type=str, default="news",
        help="Domain tag applied to every ingested video (default: news)",
    )
    parser.add_argument(
        "--db-path", type=str, default="./data/vectors/qdrant_db",
        help="Qdrant DB directory (default: ./data/vectors/qdrant_db)",
    )
    parser.add_argument(
        "--frames-dir", type=str, default="./data/processed/extracted_frames_v2",
        help="Keyframe output directory (default: ./data/processed/extracted_frames_v2)",
    )
    args = parser.parse_args()

    ingest_all(
        input_dir=args.dir,
        domain=args.domain,
        db_path=args.db_path,
        frames_dir=args.frames_dir,
    )


if __name__ == "__main__":
    main()
