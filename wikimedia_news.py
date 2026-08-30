"""
Fetch and download clean public domain news, speech, and interview clips from Wikimedia Commons API.
Supports MP4, WebM, and OGV files.
"""

from pathlib import Path
import requests

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_VIDEOS_DIR = PROJECT_ROOT / "data" / "raw_videos"
RAW_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

SEARCH_TERMS = ["weekly address", "press conference", "news broadcast", "interview speech"]

def search_wikimedia():
    print("Searching Wikimedia Commons for news/speech clips...")
    found_videos = []

    for term in SEARCH_TERMS:
        if len(found_videos) >= 7:
            break
        api_url = (
            "https://commons.wikimedia.org/w/api.php?"
            "action=query&list=search&srsearch=" + requests.utils.quote(term + " filetype:video") +
            "&srnamespace=6&format=json"
        )
        try:
            res = requests.get(api_url, headers=headers, timeout=10).json()
            search_results = res.get("query", {}).get("search", [])

            for item in search_results:
                if len(found_videos) >= 7:
                    break
                title = item["title"]

                # Get file info & url
                info_url = (
                    "https://commons.wikimedia.org/w/api.php?"
                    "action=query&titles=" + requests.utils.quote(title) +
                    "&prop=imageinfo&iiprop=url|size|mime&format=json"
                )
                info_res = requests.get(info_url, headers=headers, timeout=10).json()
                pages = info_res.get("query", {}).get("pages", {})

                for pid, pdata in pages.items():
                    imageinfo = pdata.get("imageinfo", [])
                    if imageinfo:
                        file_url = imageinfo[0].get("url", "")
                        mime = imageinfo[0].get("mime", "")
                        size = imageinfo[0].get("size", 0)

                        # Filter for video mime types and reasonable size (1MB to 50MB)
                        if any(ext in mime for ext in ["video/mp4", "video/webm", "video/ogg"]) and 1_000_000 <= size <= 50_000_000:
                            clean_name = title.replace("File:", "").replace(" ", "_")
                            # Convert to clean filename
                            if not any(clean_name.endswith(ext) for ext in [".mp4", ".webm", ".ogv"]):
                                clean_name += ".webm" if "webm" in mime else ".mp4"

                            print(f"  ✅ Found Wikimedia Video: {clean_name} ({size / 1024 / 1024:.2f} MB)")
                            print(f"     URL: {file_url}")
                            found_videos.append({
                                "name": clean_name,
                                "url": file_url,
                                "size_mb": round(size / 1024 / 1024, 2)
                            })
                            break
        except Exception as e:
            print(f"Error searching {term}: {e}")

    print(f"\nDiscovered {len(found_videos)} Wikimedia video clips.")
    return found_videos

if __name__ == "__main__":
    search_wikimedia()
