"""
Script to test and download public domain speech, news broadcasts, and interview MP4 clips with active audio.
"""

import shutil
import sys
from pathlib import Path

import cv2
import requests

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_VIDEOS_DIR = PROJECT_ROOT / "data" / "raw_videos"
EXTRACTED_FRAMES_DIR = PROJECT_ROOT / "data" / "extracted_frames"
QDRANT_DB_DIR = PROJECT_ROOT / "data" / "qdrant_db"


def clean_environment():
    """Remove old surveillance/CCTV videos, extracted frames, and vector database."""
    print("=" * 70)
    print("  CLEANING SURVEILLANCE / OLD VIDEO DATA")
    print("=" * 70)

    if RAW_VIDEOS_DIR.exists():
        shutil.rmtree(RAW_VIDEOS_DIR)
        print(f"  [CLEANED] Removed {RAW_VIDEOS_DIR}")
    RAW_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

    if EXTRACTED_FRAMES_DIR.exists():
        shutil.rmtree(EXTRACTED_FRAMES_DIR)
        print(f"  [CLEANED] Removed {EXTRACTED_FRAMES_DIR}")
    EXTRACTED_FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    if QDRANT_DB_DIR.exists():
        shutil.rmtree(QDRANT_DB_DIR)
        print(f"  [CLEANED] Reset {QDRANT_DB_DIR}")
    QDRANT_DB_DIR.mkdir(parents=True, exist_ok=True)


# Candidate speech / news broadcast / interview MP4 URLs
CANDIDATE_URLS = [
    {
        "name": "obama_weekly_address_2009.mp4",
        "url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/0/02/Barack_Obama_weekly_address_2009-01-24.ogv/Barack_Obama_weekly_address_2009-01-24.ogv.360p.vp9.webm",
        "alt_urls": [
            "https://archive.org/download/BarackObamaWeeklyAddressJan242009/BarackObamaWeeklyAddressJan242009_512kb.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
        ]
    },
    {
        "name": "nasa_press_briefing_news.mp4",
        "url": "https://archive.org/download/gov.archives.arc.1155021/gov.archives.arc.1155021_512kb.mp4",
    },
    {
        "name": "presidential_news_address.mp4",
        "url": "https://archive.org/download/reagan_address_1986/reagan_address_1986_512kb.mp4",
    },
    {
        "name": "public_event_speech_news.mp4",
        "url": "https://archive.org/download/MartinLutherKingJrIHaveADreamSpeech/MartinLutherKingJrIHaveADreamSpeech_512kb.mp4",
    },
]

if __name__ == "__main__":
    clean_environment()
