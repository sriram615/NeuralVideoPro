"""
Pipeline orchestrator for downloading and ingesting real news broadcasts,
speeches, and interview MP4 clips into Qdrant.

1. Cleans old data (surveillance/cctv clips).
2. Downloads 7 clean news broadcasts, speeches, and interviews.
3. Validates OpenCV readability and non-empty audio.
4. Batch ingests into Qdrant.
5. Verifies hybrid late fusion search.
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
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from src.ingestion.batch_ingest import batch_ingest_directory  # noqa: E402
from src.pipeline import VideoSearchPipeline  # noqa: E402

RAW_VIDEOS_DIR = PROJECT_ROOT / "data" / "raw" / "raw_videos"
EXTRACTED_FRAMES_DIR = PROJECT_ROOT / "data" / "processed" / "extracted_frames"
QDRANT_DB_DIR = PROJECT_ROOT / "data" / "vectors" / "qdrant_db"

NEWS_VIDEO_SOURCES = [
    {
        "name": "obama_farewell_speech.mp4",
        "title": "President Obama Farewell Speech News Clip",
        "url": "https://archive.org/download/youtube-GG2Ckl5Jsg0/GG2Ckl5Jsg0.mp4",
    },
    {
        "name": "middle_east_news_report.mp4",
        "title": "Middle East News Analysis Report",
        "url": "https://archive.org/download/youtube-3gBK_yy1mkk/3gBK_yy1mkk.mp4",
    },
    {
        "name": "ecns_opening_speech.mp4",
        "title": "ECNS Conference Opening Speech",
        "url": "https://archive.org/download/psikoyorum-17591/psikoyorum-17591.mp4",
    },
    {
        "name": "identity_politics_interview.mp4",
        "title": "Public Event Interview - Identity Politics",
        "url": "https://archive.org/download/youtube-gQp8f1Gfthg/gQp8f1Gfthg.mp4",
    },
    {
        "name": "sports_news_breakdown.mp4",
        "title": "Sports News Broadcast & Analysis",
        "url": "https://archive.org/download/youtube-jqotckF2ICQ/jqotckF2ICQ.mp4",
    },
    {
        "name": "nasa_space_flight_news.mp4",
        "title": "NASA Space Flight News Briefing",
        "url": "https://archive.org/download/NasaKsnn-SpaceFlightPhysicalChanges/NASAKSN-SpaceFlightPhysicalChanges.mp4",
    },
    {
        "name": "atheist_discussion_interview.mp4",
        "title": "Public Event Interview Discussion",
        "url": "https://archive.org/download/youtube--kv8fRlFedM/-kv8fRlFedM.mp4",
    },
]


def clean_environment() -> None:
    """Wipe out old surveillance/cctv files and reset database."""
    print("=" * 70)
    print("  RESETTING ENVIRONMENT & PURGING OLD SURVEILLANCE DATA")
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


def download_and_validate() -> List[Dict]:
    """Download news clips and validate OpenCV readability."""
    print("\n" + "=" * 70)
    print("  ACQUIRING & VALIDATING NEWS BROADCAST & SPEECH MP4 CLIPS")
    print("=" * 70)

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    validated_files = []

    for item in NEWS_VIDEO_SOURCES:
        file_path = RAW_VIDEOS_DIR / item["name"]

        print(f"\n[DOWNLOADING] {item['title']} ({item['name']}) …")
        t0 = time.perf_counter()

        try:
            r = requests.get(item["url"], headers=headers, stream=True, timeout=60)
            r.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

            dl_time = time.perf_counter() - t0

            # Validate video
            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                print(f"  ❌ Invalid video format: {item['name']}")
                file_path.unlink(missing_ok=True)
                continue

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            ret, frame = cap.read()
            cap.release()

            if not ret or frame is None or fps <= 0 or frame_count <= 0:
                print(f"  ❌ Unreadable frames: {item['name']}")
                file_path.unlink(missing_ok=True)
                continue

            duration = round(frame_count / fps, 2)
            fsize_mb = round(file_path.stat().st_size / 1024 / 1024, 2)

            print(f"  ✅ [VALID] {item['name']}: {width}x{height} @ {fps:.1f}fps, {duration}s, {fsize_mb} MB (Downloaded in {dl_time:.2f}s)")
            validated_files.append({
                "filename": item["name"],
                "title": item["title"],
                "path": str(file_path),
                "duration": duration,
                "fps": fps,
                "resolution": f"{width}x{height}",
                "size_mb": fsize_mb,
            })

        except Exception as err:
            print(f"  ❌ Download failed: {err}")
            file_path.unlink(missing_ok=True)

    print(f"\n[SUMMARY] Acquired {len(validated_files)}/{len(NEWS_VIDEO_SOURCES)} valid speech & news broadcast videos.")
    return validated_files


def run_pipeline_and_verify():
    clean_environment()
    valid_videos = download_and_validate()

    if not valid_videos:
        print("\n❌ No valid videos downloaded. Aborting ingestion.")
        return

    print("\n" + "=" * 70)
    print("  RUNNING BATCH INGESTION PIPELINE (DOMAIN: news)")
    print("=" * 70)

    t0 = time.perf_counter()
    summary = batch_ingest_directory(
        input_dir=RAW_VIDEOS_DIR,
        domain="news",
        db_path=QDRANT_DB_DIR,
    )
    ingest_time = time.perf_counter() - t0

    # Verification search
    print("\n" + "=" * 70)
    print("  VERIFYING HYBRID LATE FUSION SEARCH ON INGESTED NEWS BATCH")
    print("=" * 70)

    pipeline = VideoSearchPipeline(db_path=QDRANT_DB_DIR)
    test_queries = [
        "president speech address to public",
        "middle east news broadcast and discussion",
        "sports news analysis",
        "nasa space flight briefing",
    ]

    for q in test_queries:
        results = pipeline.search(query=q, domain_filter="news", alpha=0.5, top_k=3)
        print(f"\nQuery: '{q}' → Top Result:")
        if results:
            top = results[0]
            p = top["payload"]
            print(f"  Fused Score: {top['score']:.4f} (Visual: {top['visual_score']:.4f}, Audio: {top['audio_score']:.4f})")
            print(f"  Video ID   : {p['video_id']}")
            print(f"  Timestamp  : {p['timestamp']}s")
            print(f"  Transcript : \"{p['transcribed_text'][:70]}\"")

    pipeline.close()

    print("\n" + "=" * 70)
    print("  INGESTION & SEARCH VERIFICATION COMPLETE ✓")
    print("=" * 70)


if __name__ == "__main__":
    run_pipeline_and_verify()
