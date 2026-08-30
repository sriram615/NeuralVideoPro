"""
Integration test for batch video ingestion (batch_ingest.py).

1. Creates synthetic raw videos in a temporary directory.
2. Runs batch_ingest_directory().
3. Asserts processing stats and total point count.
4. Performs a search query to confirm points from all ingested videos are retrieved.
5. Cleans up temporary test directories.
"""

from __future__ import annotations

# ── CPU thread limits (must precede torch / numpy / cv2 imports) ─────────
import os

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import shutil
import sys
import time
from pathlib import Path

import cv2
import numpy as np

# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.batch_ingest import batch_ingest_directory  # noqa: E402
from src.pipeline import VideoSearchPipeline  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_TEST_TMP = PROJECT_ROOT / "data" / "_test_batch_tmp"
_TEST_RAW_DIR = _TEST_TMP / "raw_videos"
_TEST_DB_PATH = _TEST_TMP / "qdrant_db"

_SYNTH_DURATION = 5  # seconds
_SYNTH_FPS = 24
_SYNTH_WIDTH = 640
_SYNTH_HEIGHT = 480


def _generate_test_video(filename: str, label: str, hue_start: int) -> str:
    """Generate a short synthetic MP4 video file."""
    _TEST_RAW_DIR.mkdir(parents=True, exist_ok=True)
    video_path = _TEST_RAW_DIR / filename

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(video_path), fourcc, _SYNTH_FPS, (_SYNTH_WIDTH, _SYNTH_HEIGHT))

    if not writer.isOpened():
        raise RuntimeError(f"Failed to create VideoWriter for {video_path}")

    total_frames = _SYNTH_DURATION * _SYNTH_FPS
    for i in range(total_frames):
        hue = (hue_start + int((i / total_frames) * 60)) % 180
        hsv = np.full((_SYNTH_HEIGHT, _SYNTH_WIDTH, 3), (hue, 180, 200), dtype=np.uint8)
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        cv2.putText(
            bgr,
            f"{label} - Frame {i:03d}",
            (30, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2,
        )
        writer.write(bgr)

    writer.release()
    print(f"[SYNTH] Generated {video_path.name}")
    return str(video_path)


def main() -> None:
    print("=" * 70)
    print("  Batch Ingestion — Integration & Verification Test")
    print("=" * 70)

    # 1. Cleanup old test directory
    if _TEST_TMP.exists():
        shutil.rmtree(_TEST_TMP)

    _TEST_TMP.mkdir(parents=True, exist_ok=True)

    try:
        # 2. Generate 2 synthetic videos
        print("\n[STEP 1] Generating 2 synthetic test videos …")
        _generate_test_video("batch_test_alpha.mp4", "Alpha Press Briefing", hue_start=10)
        _generate_test_video("batch_test_beta.mp4", "Beta Public Rally", hue_start=90)

        # 3. Execute batch ingestion
        print("\n[STEP 2] Running batch_ingest_directory() …")
        t0 = time.perf_counter()
        summary = batch_ingest_directory(
            input_dir=_TEST_RAW_DIR,
            domain="news",
            db_path=_TEST_DB_PATH,
        )
        elapsed = time.perf_counter() - t0

        print(f"\n[SUMMARY RETURNED] {summary}")

        # 4. Assertions on batch ingestion summary
        assert summary["processed"] == 2, f"Expected 2 processed videos, got {summary['processed']}"
        assert summary["skipped"] == 0, f"Expected 0 skipped videos, got {summary['skipped']}"
        assert summary["total_points"] >= 8, f"Expected >= 8 points (5s @ 1fps x 2 videos), got {summary['total_points']}"
        print("\n[ASSERT] Batch ingestion summary checks passed ✓")

        # 5. Search verification
        print("\n[STEP 3] Verifying search accessibility across ingested batch …")
        pipeline = VideoSearchPipeline(db_path=_TEST_DB_PATH)

        search_out = pipeline.search(
            query="public news event briefing",
            domain_filter="news",
            alpha=0.5,
            top_k=10,
        )
        results = search_out.get("results", [])

        print(f"\n[SEARCH RESULTS] Query returned {len(results)} points:")
        retrieved_vids = set()
        for r in results:
            vid = r["payload"]["video_id"]
            retrieved_vids.add(vid)
            print(f"  ID: {r['id']} | Fused Score: {r['score']:.4f} | Video ID: {vid} | TS: {r['payload']['timestamp']}s")

        assert len(results) > 0, "Search returned 0 points!"
        assert len(retrieved_vids) >= 2, f"Expected points from both videos, got video IDs: {retrieved_vids}"

        print("\n[ASSERT] Search verified: points from both videos are searchable ✓")

        pipeline.close()

        print("\n" + "=" * 70)
        print("  BATCH INGESTION INTEGRATION TEST PASSED ✓")
        print("=" * 70)

    finally:
        if _TEST_TMP.exists():
            shutil.rmtree(_TEST_TMP)
            print(f"\n[CLEANUP] Removed temporary directory: {_TEST_TMP}")


def test_batch_ingest() -> None:
    main()


if __name__ == "__main__":
    main()
