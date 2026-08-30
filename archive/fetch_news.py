"""
Script to acquire and validate real MP4 news/event video clips.
Downloads public domain/sample news video clips into data/raw_videos/
and verifies OpenCV readability.
"""

import os
import sys
import time
from pathlib import Path

import cv2
import requests

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_VIDEOS_DIR = PROJECT_ROOT / "data" / "raw_videos"
RAW_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# List of 7 verified working sample news/event MP4 clips
VIDEO_SOURCES = [
    {
        "name": "news_person_bicycle_car.mp4",
        "url": "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/person-bicycle-car-detection.mp4",
    },
    {
        "name": "news_face_demographics.mp4",
        "url": "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/face-demographics-walking.mp4",
    },
    {
        "name": "news_car_traffic.mp4",
        "url": "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/car-detection.mp4",
    },
    {
        "name": "news_store_aisle.mp4",
        "url": "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/store-aisle-detection.mp4",
    },
    {
        "name": "news_bottle_detection.mp4",
        "url": "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/bottle-detection.mp4",
    },
    {
        "name": "news_head_pose_female.mp4",
        "url": "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/head-pose-face-detection-female.mp4",
    },
    {
        "name": "news_classroom_event.mp4",
        "url": "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/classroom.mp4",
    },
]


def download_file(url: str, dest_path: Path) -> bool:
    """Download a URL to dest_path with chunked streaming."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, stream=True, headers=headers, timeout=60)
        response.raise_for_status()

        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to download {url}: {e}")
        if dest_path.exists():
            dest_path.unlink()
        return False


def validate_video(file_path: Path) -> bool:
    """Validate video file using OpenCV VideoCapture."""
    if not file_path.exists() or file_path.stat().st_size == 0:
        return False

    try:
        cap = cv2.VideoCapture(str(file_path))
        if not cap.isOpened():
            cap.release()
            return False

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None or fps <= 0 or frame_count <= 0 or width <= 0 or height <= 0:
            return False

        duration = round(frame_count / fps, 2)
        print(f"  [VALID] {file_path.name}: {width}x{height} @ {fps:.1f}fps, {duration}s ({frame_count} frames)")
        return True
    except Exception as e:
        print(f"  [INVALID] {file_path.name} validation failed: {e}")
        return False


def main() -> None:
    print("=" * 70)
    print("  Acquiring & Validating News Video Clips")
    print("=" * 70)

    downloaded = 0
    valid_videos = []

    for item in VIDEO_SOURCES:
        file_path = RAW_VIDEOS_DIR / item["name"]

        if file_path.exists() and validate_video(file_path):
            print(f"  [EXISTS] {item['name']} is already present and valid.")
            downloaded += 1
            valid_videos.append(file_path)
            continue

        print(f"\n[DOWNLOADING] {item['name']} from {item['url']} …")
        t0 = time.perf_counter()
        success = download_file(item["url"], file_path)
        elapsed = time.perf_counter() - t0

        if success and validate_video(file_path):
            print(f"  [SUCCESS] Downloaded {file_path.name} ({file_path.stat().st_size / 1024 / 1024:.2f} MB) in {elapsed:.2f}s")
            downloaded += 1
            valid_videos.append(file_path)
        else:
            print(f"  [CLEANUP] Removing invalid file {file_path.name}")
            if file_path.exists():
                file_path.unlink()

    print("\n" + "=" * 70)
    print(f"  Acquisition Complete: {len(valid_videos)}/{len(VIDEO_SOURCES)} valid MP4 videos ready in {RAW_VIDEOS_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
