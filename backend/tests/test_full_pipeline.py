"""
Integration test for VideoSearchPipeline and CLIPVisionEncoder.

1. Generates a synthetic 10-second MP4 test video.
2. Ingests the video via VideoSearchPipeline.ingest_video().
3. Performs search("press conference news report") with late fusion.
4. Asserts output counts, score ranges, payload integrity, and cleanup.
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

from src.models.vision_encoder import CLIPVisionEncoder  # noqa: E402
from src.pipeline import VideoSearchPipeline  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_TEST_TMP = PROJECT_ROOT / "data" / "_test_pipeline_tmp"
_TEST_DB = _TEST_TMP / "qdrant_db"
_TEST_FRAMES = _TEST_TMP / "frames"
_TEST_VIDEO = _TEST_TMP / "news_sample.mp4"

_SYNTH_DURATION = 10  # seconds
_SYNTH_FPS = 24
_SYNTH_WIDTH = 1280
_SYNTH_HEIGHT = 720


def _generate_synthetic_video() -> str:
    """Create a 10-second MP4 video file for pipeline testing."""
    _TEST_TMP.mkdir(parents=True, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(_TEST_VIDEO), fourcc, _SYNTH_FPS, (_SYNTH_WIDTH, _SYNTH_HEIGHT))

    if not writer.isOpened():
        raise RuntimeError("cv2.VideoWriter failed to open.")

    total_frames = _SYNTH_DURATION * _SYNTH_FPS
    for i in range(total_frames):
        hue = int((i / total_frames) * 180)
        hsv = np.full((_SYNTH_HEIGHT, _SYNTH_WIDTH, 3), (hue, 180, 200), dtype=np.uint8)
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        cv2.putText(
            bgr,
            f"Breaking News Event Frame {i:04d}",
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (255, 255, 255),
            3,
        )
        writer.write(bgr)

    writer.release()
    print(f"[SYNTH] Generated test video: {_TEST_VIDEO}")
    return str(_TEST_VIDEO)


def main() -> None:
    print("=" * 70)
    print("  VideoSearchPipeline — Integration & Search Verification Test")
    print("=" * 70)

    # 1. Clean previous temp database
    if _TEST_TMP.exists():
        shutil.rmtree(_TEST_TMP)

    _TEST_TMP.mkdir(parents=True, exist_ok=True)

    try:
        # 2. Test CLIPVisionEncoder standalone first
        print("\n[STEP 1] Testing CLIPVisionEncoder standalone …")
        encoder = CLIPVisionEncoder()

        # Dummy PIL image test
        from PIL import Image
        dummy_img = Image.fromarray(np.uint8(np.random.randint(0, 255, (224, 224, 3))))
        single_vec = encoder.encode_image(dummy_img)

        assert single_vec.shape == (512,), f"Expected shape (512,), got {single_vec.shape}"
        assert single_vec.dtype == np.float32, f"Expected float32, got {single_vec.dtype}"
        norm = float(np.linalg.norm(single_vec))
        assert abs(norm - 1.0) < 1e-4, f"L2 norm = {norm}, expected ≈1.0"
        print(f"         CLIPVisionEncoder output shape: {single_vec.shape}, L2 norm: {norm:.6f} ✓")

        # 3. Generate test video
        print("\n[STEP 2] Generating synthetic news video …")
        video_path = _generate_synthetic_video()

        # 4. Instantiate pipeline
        print("\n[STEP 3] Instantiating VideoSearchPipeline …")
        t0 = time.perf_counter()
        pipeline = VideoSearchPipeline(db_path=_TEST_DB, frames_dir=_TEST_FRAMES)
        init_time = (time.perf_counter() - t0) * 1000
        print(f"         Pipeline initialized in {init_time:.1f} ms ✓")

        # 5. Ingest video
        print("\n[STEP 4] Ingesting video into vector store …")
        t0 = time.perf_counter()
        num_points = pipeline.ingest_video(video_path, domain="news")
        ingest_time = (time.perf_counter() - t0) * 1000

        print(f"         Ingested {num_points} points in {ingest_time:.1f} ms ({ingest_time/num_points:.1f} ms/frame)")
        assert num_points >= 9, f"Expected at least 9 keyframe points, got {num_points}"

        # 6. Execute Late Fusion search query
        print("\n[STEP 5] Executing hybrid late fusion search …")
        query_text = "press conference news report"

        t0 = time.perf_counter()
        search_out = pipeline.search(
            query=query_text,
            domain_filter="news",
            alpha=0.5,
            top_k=5,
        )
        results = search_out.get("results", [])
        search_time = (time.perf_counter() - t0) * 1000

        print(f"\n[SEARCH RESULTS] Query: '{query_text}' (Latency: {search_time:.2f} ms)")
        print("-" * 65)
        print(f"  {'Rank':<6}{'Fused Score':<14}{'Visual':<10}{'Audio':<10}{'Timestamp':<10}{'Domain'}")
        print("-" * 65)

        for rank, r in enumerate(results, 1):
            p = r["payload"]
            print(f"  {rank:<6}{r['score']:<14.6f}{r['visual_score']:<10.4f}{r['audio_score']:<10.4f}{p['timestamp']:<10.1f}{p.get('domain', 'N/A')}")
        print("-" * 65)

        # 7. Assertions
        assert len(results) > 0, "Search returned 0 results!"
        assert len(results) <= 5, f"Expected max 5 results, got {len(results)}"
        assert results[0]["score"] > 0.0, f"Expected non-zero score, got {results[0]['score']}"
        assert "domain" in results[0]["payload"], "Domain tag missing from payload"
        assert results[0]["payload"]["domain"] == "news", f"Expected domain 'news', got {results[0]['payload']['domain']}"

        print("\n[ASSERT] All search integrity & payload assertions passed ✓")

        # 8. Close pipeline connection
        pipeline.close()
        print("\n[CLOSE] Pipeline connection closed clean ✓")

        print("\n" + "=" * 70)
        print("  ALL INTEGRATION TESTS PASSED ✓")
        print("=" * 70)

    finally:
        # Cleanup temp directory
        if _TEST_TMP.exists():
            shutil.rmtree(_TEST_TMP)
            print(f"\n[CLEANUP] Removed temporary directory: {_TEST_TMP}")


def test_full_pipeline() -> None:
    main()


if __name__ == "__main__":
    main()
