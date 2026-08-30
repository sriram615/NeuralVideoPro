"""
VideoProcessor — CPU-optimised keyframe extraction using OpenCV.

Extracts frames at a configurable fps (default 1 fps) from an MP4 video,
auto-downscaling to 720p if the source resolution exceeds it.  Returns
structured dicts ready for Qdrant payload insertion and CLIP vision encoding.

Usage:
    vp = VideoProcessor()
    frames = vp.extract_keyframes("input.mp4", "./frames_out", target_fps=1.0)
"""

from __future__ import annotations

# ── CPU thread limits (must precede numpy / cv2 imports) ──────────────
import os

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import hashlib
import logging
from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_MAX_HEIGHT = 720  # 720p ceiling


class VideoProcessor:
    """Extract keyframes from video files on CPU.

    All heavy OpenCV work is kept single-threaded via the environment
    variables set at module load time.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def extract_keyframes(
        self,
        video_path: str,
        output_dir: str,
        target_fps: float = 1.0,
    ) -> List[Dict]:
        """Sample keyframes at *target_fps* and save as JPEG.

        Parameters
        ----------
        video_path : str
            Path to the source MP4 / video file.
        output_dir : str
            Directory to write extracted JPEG frames into.
        target_fps : float
            Desired sampling rate in frames-per-second (default ``1.0``).

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

        # How many source frames to skip between samples.
        frame_interval = max(1, int(round(src_fps / target_fps)))

        logger.info(
            "Video: %s  |  %dx%d @ %.2f fps  |  %d total frames  |  sampling every %d frames",
            video_path, src_w, src_h, src_fps, total_frames, frame_interval,
        )

        results: List[Dict] = []
        frame_count = 0      # source frame ordinal
        extracted_idx = 0    # extracted frame ordinal
        last_hist: Optional[np.ndarray] = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                # Downscale if above 720p
                frame = self._maybe_downscale(frame)

                # Compute normalized RGB histogram for perceptual deduplication
                hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                cv2.normalize(hist, hist)
                hist = hist.flatten()

                # Deduplication check: drop frame if visual similarity > 0.92
                if last_hist is not None:
                    sim = float(np.dot(hist, last_hist) / (np.linalg.norm(hist) * np.linalg.norm(last_hist) + 1e-9))
                    if sim > 0.92:
                        frame_count += 1
                        continue

                last_hist = hist
                timestamp = round(frame_count / src_fps, 4)
                start_ts = round(max(0.0, timestamp - 0.5), 4)
                end_ts = round(timestamp + 0.5, 4)

                fname = f"frame_{extracted_idx:06d}.jpg"
                save_path = str(out_dir / fname)

                cv2.imwrite(save_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])

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
        logger.info("Extracted %d keyframes (deduplicated) → %s", extracted_idx, out_dir)
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
