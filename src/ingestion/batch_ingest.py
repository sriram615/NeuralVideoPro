"""
Batch Video Ingestion Module for Semantic Video Retrieval.

Scans a directory for video files (.mp4, .mkv, .avi), ingests them into Qdrant
via VideoSearchPipeline, and applies RAM garbage collection after each video.

Usage CLI:
    python -m src.ingestion.batch_ingest --dir data/raw_videos --domain news

Usage Python:
    from src.ingestion.batch_ingest import batch_ingest_directory
    summary = batch_ingest_directory("data/raw_videos", domain="news")
"""

from __future__ import annotations

# ── CPU thread limits (must precede torch / numpy imports) ──────────────
import os

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import argparse
import gc
import logging
import time
from pathlib import Path
from typing import Dict, List, Union

from src.pipeline import VideoSearchPipeline

logger = logging.getLogger(__name__)

# Supported video extensions
SUPPORTED_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm"}


def batch_ingest_directory(
    input_dir: Union[str, Path] = "data/raw_videos",
    domain: str = "news",
    db_path: Union[str, Path] = "./data/qdrant_db",
) -> Dict[str, Any]:
    """Ingest all raw video files from a directory into Qdrant.

    Parameters
    ----------
    input_dir : str | Path
        Path to input directory containing video files.
    domain : str
        Domain metadata tag (default ``"news"``).
    db_path : str | Path
        Path to Qdrant database directory.

    Returns
    -------
    dict
        Summary dictionary containing:
            - ``processed``     : int (number of videos successfully ingested)
            - ``skipped``       : int (number of videos skipped due to errors)
            - ``total_points``  : int (total Qdrant points indexed)
            - ``total_time_sec``: float (total elapsed seconds)
    """
    in_path = Path(input_dir).resolve()
    if not in_path.exists() or not in_path.is_dir():
        logger.warning("Input directory does not exist or is not a directory: %s", in_path)
        return {"processed": 0, "skipped": 0, "total_points": 0, "total_time_sec": 0.0}

    # Find all supported video files
    video_files: List[Path] = [
        p for p in in_path.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    video_files.sort()

    logger.info("Found %d video files in %s", len(video_files), in_path)
    if not video_files:
        print(f"[BATCH] No supported video files ({', '.join(SUPPORTED_EXTENSIONS)}) found in {in_path}")
        return {"processed": 0, "skipped": 0, "total_points": 0, "total_time_sec": 0.0}

    # Instantiate pipeline
    pipeline = VideoSearchPipeline(db_path=db_path)

    processed_count = 0
    skipped_count = 0
    total_points = 0
    file_reports: List[Dict[str, Any]] = []

    start_time = time.perf_counter()

    for idx, vfile in enumerate(video_files, 1):
        v_start = time.perf_counter()
        logger.info("[%d/%d] Ingesting %s …", idx, len(video_files), vfile.name)

        try:
            pts = pipeline.ingest_video(str(vfile), domain=domain)
            v_elapsed = time.perf_counter() - v_start

            processed_count += 1
            total_points += pts
            file_reports.append({
                "file": vfile.name,
                "status": "SUCCESS",
                "points": pts,
                "time_sec": round(v_elapsed, 2),
            })
            print(f"  [{idx}/{len(video_files)}] ✅ {vfile.name}: {pts} points in {v_elapsed:.2f}s")

        except Exception as err:
            v_elapsed = time.perf_counter() - v_start
            skipped_count += 1
            logger.error("Error processing %s: %s", vfile.name, err, exc_info=True)
            file_reports.append({
                "file": vfile.name,
                "status": f"FAILED ({err.__class__.__name__})",
                "points": 0,
                "time_sec": round(v_elapsed, 2),
            })
            print(f"  [{idx}/{len(video_files)}] ❌ {vfile.name}: Skipped due to error ({err})")

        finally:
            # Force garbage collection to free memory between videos
            gc.collect()

    total_time = time.perf_counter() - start_time
    pipeline.close()

    # Print summary table
    print("\n" + "=" * 70)
    print("  BATCH INGESTION SUMMARY REPORT")
    print("=" * 70)
    print(f"  {'Filename':<35}{'Status':<18}{'Points':<10}{'Time (s)'}")
    print("-" * 70)
    for r in file_reports:
        print(f"  {r['file']:<35}{r['status']:<18}{r['points']:<10}{r['time_sec']:.2f}")
    print("-" * 70)
    print(f"  Total Videos Processed : {processed_count}")
    print(f"  Total Videos Skipped   : {skipped_count}")
    print(f"  Total Points Indexed   : {total_points}")
    print(f"  Total Ingestion Time   : {total_time:.2f} s")
    print("=" * 70 + "\n")

    return {
        "processed": processed_count,
        "skipped": skipped_count,
        "total_points": total_points,
        "total_time_sec": round(total_time, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch video ingestion for Semantic Video Retrieval.")
    parser.add_argument(
        "--dir",
        type=str,
        default="data/raw_videos",
        help="Target directory containing video files (default: data/raw_videos)",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default="news",
        help="Domain metadata tag for payload (default: news)",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="./data/qdrant_db",
        help="Qdrant database directory (default: ./data/qdrant_db)",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    batch_ingest_directory(
        input_dir=args.dir,
        domain=args.domain,
        db_path=args.db_path,
    )


if __name__ == "__main__":
    main()
