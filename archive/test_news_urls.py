"""
Script to test and discover working MP4 URLs for news, speeches, interviews, and public events with audio.
"""

from pathlib import Path
import requests

PROJECT_ROOT = Path(__file__).resolve().parent

TEST_URLS = [
    # Speech / News Broadcast / Interview URLs from Archive.org & public repositories
    ("obama_address_2009.mp4", "https://archive.org/download/BarackObamaWeeklyAddressJan242009/BarackObamaWeeklyAddressJan242009_512kb.mp4"),
    ("news_speech_reagan.mp4", "https://archive.org/download/reagan_address_1986/reagan_address_1986_512kb.mp4"),
    ("news_interview_steve_jobs.mp4", "https://archive.org/download/SteveJobsSpeech1983/SteveJobsSpeech1983_512kb.mp4"),
    ("news_event_apollo_speech.mp4", "https://archive.org/download/Apollo11MoonLandingSpeech/Apollo11MoonLandingSpeech_512kb.mp4"),
    ("news_broadcast_sample1.mp4", "https://github.com/intel-iot-devkit/sample-videos/raw/master/head-pose-face-detection-female.mp4"),
    ("news_speech_fdr.mp4", "https://archive.org/download/FDR_Pearl_Harbor_Speech/FDR_Pearl_Harbor_Speech_512kb.mp4"),
    ("news_address_bush.mp4", "https://archive.org/download/Bush911Address/Bush911Address_512kb.mp4"),
    ("sample_news_clip_1.mp4", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"),
    ("sample_news_clip_2.mp4", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"),
    ("sample_news_clip_3.mp4", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"),
]

def check_urls():
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    print("Testing candidate news/speech MP4 URLs...")
    valid = []
    for name, url in TEST_URLS:
        try:
            r = requests.head(url, headers=headers, allow_redirects=True, timeout=10)
            if r.status_code == 200:
                size_mb = int(r.headers.get("content-length", 0)) / 1024 / 1024
                print(f"  ✅ [200 OK] {name}: {size_mb:.2f} MB ({url})")
                valid.append((name, url, size_mb))
            else:
                print(f"  ❌ [{r.status_code}] {name} ({url})")
        except Exception as e:
            print(f"  ❌ [ERR] {name}: {e}")
    print(f"\nFound {len(valid)} working MP4 URLs.")

if __name__ == "__main__":
    check_urls()
