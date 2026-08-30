"""
Find clean, appropriate public domain news broadcasts, NASA reports, and speech MP4s.
"""

from pathlib import Path
import requests

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

CLEAN_QUERIES = [
    "collection:nasa",
    "subject:speech AND mediatype:movies",
    "subject:newsbroadcast AND mediatype:movies",
    "subject:pressconference AND mediatype:movies",
]

def find_clean_videos():
    valid = []
    seen_urls = set()

    for q in CLEAN_QUERIES:
        if len(valid) >= 7:
            break
        url = f"https://archive.org/advancedsearch.php?q={requests.utils.quote(q)}&fl[]=identifier,title&rows=25&output=json"
        try:
            res = requests.get(url, headers=headers, timeout=10).json()
            docs = res.get("response", {}).get("docs", [])
            for d in docs:
                if len(valid) >= 7:
                    break
                identifier = d["identifier"]
                title = d.get("title", identifier)

                # Skip any questionable titles
                title_lower = title.lower()
                if any(bad in title_lower for bad in ["suicide", "massacre", "sex", "nsfw", "nude", "explicit"]):
                    continue

                meta_url = f"https://archive.org/metadata/{identifier}"
                try:
                    meta = requests.get(meta_url, headers=headers, timeout=10).json()
                    files = meta.get("files", [])
                    for f in files:
                        fname = f.get("name", "")
                        size = int(f.get("size", 0))

                        if fname.endswith(".mp4") and 1_000_000 <= size <= 40_000_000:
                            file_url = f"https://archive.org/download/{identifier}/{requests.utils.quote(fname)}"
                            if file_url in seen_urls:
                                continue

                            try:
                                h = requests.head(file_url, headers=headers, allow_redirects=True, timeout=5)
                                if h.status_code == 200:
                                    print(f"  ✅ [CLEAN MP4] Title: '{title}'")
                                    print(f"     URL: {file_url} ({size / 1024 / 1024:.2f} MB)")
                                    valid.append({
                                        "identifier": identifier,
                                        "title": title,
                                        "fname": fname,
                                        "url": file_url,
                                        "size_mb": round(size / 1024 / 1024, 2)
                                    })
                                    seen_urls.add(file_url)
                                    break
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception as e:
            print(f"Query error: {e}")

    print(f"\nDiscovered {len(valid)} clean working MP4 news/speech URLs.")
    return valid

if __name__ == "__main__":
    find_clean_videos()
