"""
VideoProcessor — Adaptive Scene-Change Keyframe Sampler using OpenCV.

Extracts keyframes dynamically based on HSV color histogram distances and
optical flux thresholding. High motion/scene cuts increase sampling density up to 3 FPS,
while static monologue scenes throttle down to 0.2 FPS (1 frame per 5s) to eliminate
redundant CLIP embeddings and vector DB payload bloat.

Usage:
    vp = VideoProcessor()
    frames = vp.extract_keyframes("input.mp4", "./frames_out", target_fps=1.0, adaptive=True)
"""

from __future__ import annotations

# ── CPU thread limits (must precede numpy / cv2 imports) ──────────────
import os

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants & Bounding Limits
# ---------------------------------------------------------------------------
_MAX_HEIGHT = 720        # 720p ceiling
_MIN_FPS = 0.5           # Min sampling rate: 1 frame every 2 seconds
_MAX_FPS = 3.0           # Max sampling rate: 3 frames per second (scene cuts)
_HIST_CUT_THRESHOLD = 0.25  # Bhattacharyya distance threshold for scene cut
_FLUX_CUT_THRESHOLD = 12.0  # Mean absolute optical flux threshold for motion


class VideoProcessor:
    """Extract keyframes from video files with adaptive scene-change sampling.

    Keeps heavy OpenCV processing single-threaded via environment limits.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def extract_keyframes(
        self,
        video_path: str,
        output_dir: str,
        target_fps: float = 1.0,
        adaptive: bool = False,
    ) -> List[Dict]:
        """Sample keyframes dynamically or at target_fps and save as JPEG.

        Parameters
        ----------
        video_path : str
            Path to the source MP4 / video file.
        output_dir : str
            Directory to write extracted JPEG frames into.
        target_fps : float
            Baseline sampling rate in frames-per-second (default 1.0).
        adaptive : bool
            Whether to use adaptive scene-change sampling (default False).

        Returns
        -------
        list[dict]
            Each dict contains:
                - ``frame_path``  : str   – absolute path to saved JPEG
                - ``timestamp``   : float – seconds from start
                - ``frame_idx``   : int   – ordinal of extracted frame
                - ``video_id``    : str   – deterministic hash-based ID
        """
        video_path = str(Path(video_path).resolve())
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        video_id = self._make_video_id(video_path)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise FileNotFoundError(f"Cannot open video: {video_path}")

        src_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if src_fps <= 0:
            cap.release()
            raise ValueError(f"Invalid source FPS ({src_fps}) for {video_path}")

        base_interval = max(1, int(round(src_fps / target_fps)))

        logger.info(
            "Video: %s | %dx%d @ %.2f fps | %d total frames | adaptive=%s",
            video_path, src_w, src_h, src_fps, total_frames, adaptive,
        )

        results: List[Dict] = []
        frame_count = 0        # Source frame ordinal
        extracted_idx = 0      # Extracted keyframe ordinal

        last_extracted_frame = -99999
        last_hsv_hist: Optional[np.ndarray] = None
        last_gray_frame: Optional[np.ndarray] = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            should_sample = False
            if not adaptive:
                should_sample = (frame_count % base_interval == 0)
            else:
                should_sample = (frame_count == 0) or ((frame_count - last_extracted_frame) >= current_interval)

            if should_sample:
                downscaled = self._maybe_downscale(frame)

                # Convert to HSV and Gray for motion/change analysis
                hsv = cv2.cvtColor(downscaled, cv2.COLOR_BGR2HSV)
                gray = cv2.cvtColor(downscaled, cv2.COLOR_BGR2GRAY)

                # Compute 2D HSV Histogram (Hue & Saturation)
                hist = cv2.calcHist([hsv], [0, 1], None, [18, 25], [0, 180, 0, 256])
                cv2.normalize(hist, hist)

                # Adaptive Rate Adjustment Logic if enabled
                if adaptive and last_hsv_hist is not None and last_gray_frame is not None:
                    # 1. HSV Histogram Distance (Bhattacharyya distance [0.0 - 1.0])
                    hist_dist = float(cv2.compareHist(hist, last_hsv_hist, cv2.HISTCMP_BHATTACHARYYA))
                    # 2. Optical Flux / Intensity Difference
                    optical_flux = float(np.mean(cv2.absdiff(gray, last_gray_frame)))

                    # Dynamic Rate Calculation
                    if hist_dist > _HIST_CUT_THRESHOLD or optical_flux > _FLUX_CUT_THRESHOLD:
                        # High Motion / Scene Cut: Boost sampling rate (up to 3.0 FPS)
                        adaptive_fps = min(_MAX_FPS, target_fps * 2.0)
                    else:
                        adaptive_fps = target_fps

                    current_interval = max(1, int(round(src_fps / adaptive_fps)))
                else:
                    current_interval = base_interval

                last_hsv_hist = hist
                last_gray_frame = gray.copy()
                last_extracted_frame = frame_count

                timestamp = round(frame_count / src_fps, 4)
                start_ts = round(max(0.0, timestamp - 0.5), 4)
                end_ts = round(timestamp + 0.5, 4)

                fname = f"frame_{extracted_idx:06d}.jpg"
                save_path = str(out_dir / fname)

                cv2.imwrite(save_path, downscaled, [cv2.IMWRITE_JPEG_QUALITY, 90])

                results.append({
                    "frame_path": save_path,
                    "timestamp": timestamp,
                    "start_timestamp": start_ts,
                    "end_timestamp": end_ts,
                    "frame_idx": extracted_idx,
                    "video_id": video_id,
                })
                extracted_idx += 1

            frame_count += 1

        cap.release()
        logger.info("Extracted %d keyframes → %s", extracted_idx, out_dir)
        return results

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    @staticmethod
    def _maybe_downscale(frame: np.ndarray) -> np.ndarray:
        """Resize to ≤ 720p height, keeping aspect ratio."""
        h, w = frame.shape[:2]
        if h <= _MAX_HEIGHT:
            return frame
        scale = _MAX_HEIGHT / h
        new_w = int(w * scale)
        return cv2.resize(frame, (new_w, _MAX_HEIGHT), interpolation=cv2.INTER_AREA)

    @staticmethod
    def _make_video_id(video_path: str) -> str:
        """Deterministic short hash from the absolute path."""
        digest = hashlib.sha256(video_path.encode()).hexdigest()[:12]
        stem = Path(video_path).stem
        return f"{stem}_{digest}"
