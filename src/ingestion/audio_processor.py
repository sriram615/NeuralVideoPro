"""
AudioTranscriber — CPU-only Whisper speech transcription for video files.

Extracts the audio track from an MP4 via ffmpeg, converts to 16 kHz mono
WAV, then runs ``whisper-base`` on CPU to produce timestamped transcript
segments ready for Qdrant payload insertion.

Usage:
    at = AudioTranscriber()
    segments = at.transcribe("input.mp4")
"""

from __future__ import annotations

# ── CPU thread limits (must precede torch / whisper imports) ──────────
import os

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import hashlib
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DEFAULT_MODEL = "base"
_SAMPLE_RATE = 16_000  # Whisper expects 16 kHz


class AudioTranscriber:
    """Whisper-based audio transcriber for video files.

    Parameters
    ----------
    model_name : str
        Whisper model size (``tiny``, ``base``, ``small``, …).
        Default ``base`` balances accuracy and CPU latency.
    """

    def __init__(self, model_name: str = _DEFAULT_MODEL) -> None:
        self.model_name = model_name
        self._model = None  # lazy-loaded

    # ------------------------------------------------------------------
    # Lazy model loading
    # ------------------------------------------------------------------
    def _load_model(self):
        """Load Whisper model on first call (CPU only)."""
        if self._model is not None:
            return

        import whisper  # deferred so module import stays fast

        logger.info("Loading Whisper '%s' model on CPU …", self.model_name)
        self._model = whisper.load_model(self.model_name, device="cpu")
        logger.info("Whisper model loaded.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def transcribe(self, video_path: str) -> List[Dict]:
        """Extract audio from *video_path* and return transcript segments.

        Parameters
        ----------
        video_path : str
            Path to the source MP4 / video file.

        Returns
        -------
        list[dict]
            Each dict contains:
                - ``start``    : float – segment start (seconds)
                - ``end``      : float – segment end   (seconds)
                - ``text``     : str   – transcribed text
                - ``video_id`` : str   – deterministic hash-based ID
        """
        video_path = str(Path(video_path).resolve())
        video_id = self._make_video_id(video_path)

        # 1. Extract audio to a temporary WAV
        wav_path = self._extract_audio(video_path)
        if wav_path is None:
            logger.warning("No audio track found in %s — returning empty transcript.", video_path)
            return []

        try:
            # 2. Run Whisper
            self._load_model()

            import whisper  # already cached after _load_model

            logger.info("Transcribing %s …", wav_path)
            result = self._model.transcribe(
                str(wav_path),
                language="en",
                fp16=False,  # CPU — fp16 not supported
            )

            segments: List[Dict] = []
            for seg in result.get("segments", []):
                segments.append({
                    "start": round(seg["start"], 3),
                    "end": round(seg["end"], 3),
                    "text": seg["text"].strip(),
                    "video_id": video_id,
                })

            logger.info("Transcription complete — %d segments.", len(segments))
            return segments

        finally:
            # 3. Clean up temporary WAV
            if wav_path and Path(wav_path).exists():
                Path(wav_path).unlink()
                logger.debug("Removed temporary WAV: %s", wav_path)

    # ------------------------------------------------------------------
    # Audio extraction via ffmpeg
    # ------------------------------------------------------------------
    @staticmethod
    def _extract_audio(video_path: str) -> Optional[str]:
        """Demux audio to a 16 kHz mono WAV via ffmpeg.

        Returns
        -------
        str | None
            Path to the temporary WAV file, or ``None`` if the video
            contains no audio stream.
        """
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        wav_path = tmp.name

        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn",                       # drop video
            "-acodec", "pcm_s16le",      # 16-bit PCM
            "-ar", str(_SAMPLE_RATE),    # 16 kHz
            "-ac", "1",                  # mono
            wav_path,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            # ffmpeg returns non-zero if there is no audio stream
            if result.returncode != 0:
                Path(wav_path).unlink(missing_ok=True)
                if "does not contain any stream" in result.stderr or \
                   "Output file is empty" in result.stderr:
                    return None
                logger.debug("ffmpeg stderr: %s", result.stderr[-500:])
                return None

            # Check the file has some content
            if Path(wav_path).stat().st_size < 100:
                Path(wav_path).unlink(missing_ok=True)
                return None

            return wav_path

        except subprocess.TimeoutExpired:
            Path(wav_path).unlink(missing_ok=True)
            raise RuntimeError(f"ffmpeg timed out processing {video_path}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _make_video_id(video_path: str) -> str:
        """Deterministic short hash from the absolute path."""
        digest = hashlib.sha256(video_path.encode()).hexdigest()[:12]
        stem = Path(video_path).stem
        return f"{stem}_{digest}"
