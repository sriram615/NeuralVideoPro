# download_seed_videos.py — Helper to fetch additional CC-licensed seed videos.
#
# Tries yt-dlp with a Creative Commons license filter on YouTube first.
# If yt-dlp isn't available or no CC results are found, it prints a
# manual-download checklist with exact search terms for Pexels/Pixabay/Wikimedia.
#
# Usage:
#     python scripts/ingestion/download_seed_videos.py --out data/raw/raw_videos
#
# Notes:
#     - Keep clips under 3 minutes so ingestion stays fast.
#     - Prefer videos with clear speech (Whisper works better).
#     - Do not download copyrighted music videos or movie clips.

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Candidate YouTube search queries filtered to Creative Commons.
# These are starting points — review each result before downloading.
YT_CC_QUERIES = [
    "university lecture whiteboard mathematics creativecommons",
    "cooking tutorial chopping vegetables kitchen creativecommons",
    "daily vlog apartment morning routine creativecommons",
    "nature documentary forest wildlife narration creativecommons",
    "tech conference slide presentation stage creativecommons",
]

# Manual fallback: exact search terms for Pexels / Pixabay / Wikimedia Commons.
MANUAL_SOURCES = [
    {
        "domain": "education / lecture",
        "search_terms": ["university lecture whiteboard", "mathematics classroom demo", "science lecture experiment"],
        "platforms": ["Pexels Videos", "Pixabay Videos", "Wikimedia Commons"],
        "tip": "Look for clips with a speaker at a whiteboard or chalkboard.",
    },
    {
        "domain": "cooking / tutorial",
        "search_terms": ["cooking tutorial chopping vegetables", "kitchen recipe close up", "food preparation hands"],
        "platforms": ["Pexels Videos", "Pixabay Videos"],
        "tip": "Close-up hands and objects give the visual encoder a distinct texture.",
    },
    {
        "domain": "vlog / personal",
        "search_terms": ["apartment morning routine vlog", "daily life indoor handheld", "room tour casual"],
        "platforms": ["Pexels Videos", "Pixabay Videos"],
        "tip": "Handheld camera + casual indoor speech contrasts with studio news footage.",
    },
    {
        "domain": "nature / documentary",
        "search_terms": ["nature documentary forest wildlife", "ocean waves scenery", "national park narrator"],
        "platforms": ["Pexels Videos", "Pixabay Videos", "Wikimedia Commons"],
        "tip": "Narrator-only audio tests the audio-only retrieval path.",
    },
    {
        "domain": "conference / presentation",
        "search_terms": ["tech conference slide presentation", "TEDx talk stage", "academic symposium lecture"],
        "platforms": ["Wikimedia Commons", "Internet Archive", "Pexels Videos"],
        "tip": "Slides + stage lighting differ from podium speech footage.",
    },
]


def _check_yt_dlp() -> bool:
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        return True
    except Exception:
        return False


def download_with_yt_dlp(query: str, out_dir: Path) -> bool:
    """Download one CC-licensed YouTube video matching `query`."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_tmpl = str(out_dir / "%(title)s.%(ext)s")
    cmd = [
        "yt-dlp",
        "--format", "mp4/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "--max-filesize", "100M",
        "--write-info-json",
        "--output", out_tmpl,
        f"ytsearch5:{query}",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr[-2000:])
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("yt-dlp timed out for:", query)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Download additional seed videos.")
    parser.add_argument("--out", default="data/raw/raw_videos", help="Output directory")
    parser.add_argument("--yt", action="store_true", help="Attempt yt-dlp YouTube CC download")
    args = parser.parse_args()

    out_dir = Path(args.out)

    if args.yt:
        if not _check_yt_dlp():
            print("yt-dlp not installed. Install with: pip install yt-dlp  (or brew install yt-dlp)")
            sys.exit(1)
        for q in YT_CC_QUERIES:
            print(f"\n=== Searching YouTube CC: {q} ===")
            download_with_yt_dlp(q, out_dir)
    else:
        print("\n=== Manual download checklist ===\n")
        for item in MANUAL_SOURCES:
            print(f"Domain: {item['domain']}")
            print(f"  Search: {' | '.join(item['search_terms'])}")
            print(f"  Platforms: {', '.join(item['platforms'])}")
            print(f"  Tip: {item['tip']}")
            print()

        print("After downloading, place MP4 files into:", out_dir.resolve())
        print("Then ingest them:\n")
        print("  source .venv/bin/activate")
        print("  cd backend")
        print("  python -m scripts.ingestion.ingest_all  # or ingest individual videos")


if __name__ == "__main__":
    main()
