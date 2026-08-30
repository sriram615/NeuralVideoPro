"""
Integration tests for the ingestion pipeline.

1. Generates a 10-second synthetic video (coloured frames, no audio).
2. Verifies VideoProcessor.extract_keyframes — frame count, timestamps,
   file existence, and 720p downscale.
3. Verifies AudioTranscriber — graceful fallback when no audio track.
4. Cleans up all temporary artefacts on exit.
"""

from __future__ import annotations

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
# Ensure project root is on sys.path
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.video_processor import VideoProcessor   # noqa: E402
from src.ingestion.audio_processor import AudioTranscriber  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_SYNTH_DURATION = 10      # seconds
_SYNTH_FPS = 24           # source fps for synthetic video
_SYNTH_WIDTH = 1280       # 720p width
_SYNTH_HEIGHT = 960       # above 720p to exercise downscale
_TMP_DIR = PROJECT_ROOT / "data" / "_test_ingestion_tmp"
_SYNTH_VIDEO = str(_TMP_DIR / "synthetic_test.mp4")
_FRAMES_DIR = str(_TMP_DIR / "frames")


# ---------------------------------------------------------------------------
# Synthetic video generator
# ---------------------------------------------------------------------------
def _generate_synthetic_video() -> str:
    """Create a 10-second MP4 with colour-shifting frames (no audio)."""
    _TMP_DIR.mkdir(parents=True, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(_SYNTH_VIDEO, fourcc, _SYNTH_FPS, (_SYNTH_WIDTH, _SYNTH_HEIGHT))

    if not writer.isOpened():
        raise RuntimeError("cv2.VideoWriter failed — check codec support.")

    total_frames = _SYNTH_DURATION * _SYNTH_FPS
    for i in range(total_frames):
        # Smooth colour cycle: hue rotates over 10 s
        hue = int((i / total_frames) * 180)
        hsv = np.full((_SYNTH_HEIGHT, _SYNTH_WIDTH, 3), (hue, 200, 220), dtype=np.uint8)
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # Burn a frame counter into the image for visual debugging
        cv2.putText(
            bgr,
            f"Frame {i:04d}  t={i / _SYNTH_FPS:.2f}s",
            (40, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.8,
            (255, 255, 255),
            3,
        )
        writer.write(bgr)

    writer.release()
    fsize = Path(_SYNTH_VIDEO).stat().st_size
    print(f"[SYNTH] Generated {_SYNTH_VIDEO}  ({fsize / 1024:.1f} KB, "
          f"{_SYNTH_DURATION}s @ {_SYNTH_FPS} fps, {_SYNTH_WIDTH}×{_SYNTH_HEIGHT})")
    return _SYNTH_VIDEO


import pytest


@pytest.fixture(scope="module")
def video_path() -> str:
    path = _generate_synthetic_video()
    yield path
    if _TMP_DIR.exists():
        shutil.rmtree(_TMP_DIR)



# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_video_processor(video_path: str) -> None:
    """Test keyframe extraction at 1 fps from the synthetic video."""
    print("\n" + "-" * 60)
    print("  TEST: VideoProcessor.extract_keyframes")
    print("-" * 60)

    vp = VideoProcessor()

    t0 = time.perf_counter()
    frames = vp.extract_keyframes(video_path, _FRAMES_DIR, target_fps=1.0)
    elapsed = time.perf_counter() - t0

    # ── Assertions ──
    # 10-second video at 1 fps → expect ~10 frames (±1 due to rounding)
    expected_min, expected_max = 9, 11
    assert expected_min <= len(frames) <= expected_max, (
        f"Expected {expected_min}–{expected_max} frames, got {len(frames)}"
    )

    # Timestamps should be monotonically increasing
    timestamps = [f["timestamp"] for f in frames]
    for i in range(1, len(timestamps)):
        assert timestamps[i] > timestamps[i - 1], (
            f"Timestamps not monotonic at index {i}: {timestamps[i - 1]} >= {timestamps[i]}"
        )

    # First timestamp should be 0.0
    assert timestamps[0] == 0.0, f"First timestamp should be 0.0, got {timestamps[0]}"

    # All frame files should exist
    for f in frames:
        fp = Path(f["frame_path"])
        assert fp.exists(), f"Frame file missing: {fp}"
        assert fp.suffix == ".jpg", f"Expected .jpg, got {fp.suffix}"

    # Downscale check: read back a frame and verify height ≤ 720
    sample = cv2.imread(frames[0]["frame_path"])
    h, w = sample.shape[:2]
    assert h <= 720, f"Frame height {h} exceeds 720p"

    # video_id should be consistent
    ids = {f["video_id"] for f in frames}
    assert len(ids) == 1, f"Inconsistent video IDs: {ids}"

    # ── Report ──
    print(f"\n  Frames extracted : {len(frames)}")
    print(f"  Time elapsed     : {elapsed * 1000:.1f} ms")
    print(f"  Timestamps       : {timestamps}")
    print(f"  Output resolution: {w}×{h}")
    print(f"  Video ID         : {frames[0]['video_id']}")
    print(f"  Output directory : {_FRAMES_DIR}")

    print("\n  [PASS] ✅  All VideoProcessor assertions passed.")


def test_audio_transcriber(video_path: str) -> None:
    """Test AudioTranscriber — expect graceful empty return (no audio track)."""
    print("\n" + "-" * 60)
    print("  TEST: AudioTranscriber.transcribe (no-audio fallback)")
    print("-" * 60)

    at = AudioTranscriber()

    t0 = time.perf_counter()
    segments = at.transcribe(video_path)
    elapsed = time.perf_counter() - t0

    # Synthetic video has no audio → expect empty list
    assert isinstance(segments, list), f"Expected list, got {type(segments)}"
    assert len(segments) == 0, (
        f"Expected 0 segments (no audio track), got {len(segments)}"
    )

    print(f"\n  Segments returned : {len(segments)} (correct — no audio track)")
    print(f"  Time elapsed      : {elapsed * 1000:.1f} ms")
    print("\n  [PASS] ✅  AudioTranscriber graceful fallback verified.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("  Ingestion Pipeline — Integration Tests")
    print("=" * 60)

    try:
        video_path = _generate_synthetic_video()
        test_video_processor(video_path)
        test_audio_transcriber(video_path)

        print("\n" + "=" * 60)
        print("  ALL TESTS PASSED ✓")
        print("=" * 60)

    finally:
        # Cleanup
        if _TMP_DIR.exists():
            shutil.rmtree(_TMP_DIR)
            print(f"\n[CLEANUP] Removed {_TMP_DIR}")


if __name__ == "__main__":
    main()
