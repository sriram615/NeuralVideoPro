# download_from_links.py — Download YouTube videos by URL with audio.
#
# Usage:
#     python scripts/ingestion/download_from_links.py \
#         --urls "https://youtube.com/watch?v=XXXX" "https://youtu.be/YYYY"
#
#     python scripts/ingestion/download_from_links.py --urls-file links.txt
#
# Each line in links.txt should be a single YouTube URL.
#
# Downloads best MP4 (video + audio merged) capped at ~150 MB per file.
# Requires: yt-dlp + ffmpeg

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_OUT = Path("data/raw/raw_videos")
YTDLP_BIN = shutil.which("yt-dlp") or str(Path(__file__).resolve().parent.parent.parent / ".venv" / "bin" / "yt-dlp")
FFMPEG_BIN = shutil.which("ffmpeg") or "ffmpeg"


def _check_tools() -> list[str]:
    missing: list[str] = []
    if not shutil.which("yt-dlp") and not Path(YTDLP_BIN).exists():
        missing.append("yt-dlp")
    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg")
    return missing


def download_url(url: str, out_dir: Path) -> str | None:
    """Download one URL. Returns the final filename or None on failure."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_tmpl = str(out_dir / "%(title)s.%(ext)s")

    cmd = [
        YTDLP_BIN,
        "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "--max-filesize", "150M",
        "--write-info-json",
        "--output", out_tmpl,
        url,
    ]
    if FFMPEG_BIN != "ffmpeg":
        cmd.extend(["--ffmpeg-location", FFMPEG_BIN])

    print(f"\n=== Downloading: {url} ===")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr[-2000:])
            return None
        return "ok"
    except subprocess.TimeoutExpired:
        print("yt-dlp timed out for:", url)
        return None


def read_urls_from_file(path: Path) -> list[str]:
    urls: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def main() -> None:
    missing = _check_tools()
    if missing:
        print("Missing required tools:", ", ".join(missing))
        print("Install with: brew install yt-dlp ffmpeg   (or pip install yt-dlp)")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Download YouTube videos with audio.")
    parser.add_argument(
        "--urls",
        nargs="*",
        help="One or more YouTube URLs",
    )
    parser.add_argument(
        "--urls-file",
        type=Path,
        help="Text file with one YouTube URL per line",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output directory (default: data/raw/raw_videos)",
    )
    args = parser.parse_args()

    urls: list[str] = []
    if args.urls_file:
        urls.extend(read_urls_from_file(args.urls_file))
    if args.urls:
        urls.extend(args.urls)

    if not urls:
        print("No URLs provided. Use --urls or --urls-file.")
        sys.exit(1)

    out_dir: Path = args.out
    print(f"Output directory: {out_dir.resolve()}")
    print(f"{len(urls)} URL(s) to download.\n")

    successes = 0
    for url in urls:
        result = download_url(url, out_dir)
        if result:
            successes += 1

    print(f"\nDone: {successes}/{len(urls)} downloaded.")
    print(f"Files saved to: {out_dir.resolve()}")
    print("\nNext step — ingest them into the search index:")
    print("  source .venv/bin/activate")
    print("  cd backend")
    print("  python -m scripts.ingestion.ingest_all")


if __name__ == "__main__":
    main()
