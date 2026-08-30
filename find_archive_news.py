"""
Find and verify working MP4 news, speech, and interview clips from Archive.org API.
"""

from pathlib import Path
import requests

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

def find_news_clips():
    search_url = (
        "https://archive.org/advancedsearch.php?"
        "q=mediatype%3Amovies+AND+%28subject%3Anews+OR+subject%3Aspeech+OR+subject%3Ainterview+OR+subject%3Apress%29"
        "&fl%5B%5D=identifier%2Ctitle&sort%5B%5D=downloads+desc&rows=30&output=json"
    )
    res = requests.get(search_url, headers=headers).json()
    docs = res.get("response", {}).get("docs", [])
    print(f"Found {len(docs)} candidate Archive.org items.")

    valid_mp4s = []

    for d in docs:
        if len(valid_mp4s) >= 8:
            break
        identifier = d["identifier"]
        title = d.get("title", identifier)

        # Get item metadata to list files
        meta_url = f"https://archive.org/metadata/{identifier}"
        try:
            meta = requests.get(meta_url, headers=headers, timeout=10).json()
            files = meta.get("files", [])
            # Find smaller MP4 files (< 50MB) with format containing 'MP4' or 512Kb/h.264
            for f in files:
                fname = f.get("name", "")
                format_type = f.get("format", "")
                size = int(f.get("size", 0))

                if fname.endswith(".mp4") and 500_000 <= size <= 50_000_000:
                    file_url = f"https://archive.org/download/{identifier}/{fname}"
                    # Verify HEAD request
                    try:
                        h = requests.head(file_url, headers=headers, allow_redirects=True, timeout=5)
                        if h.status_code == 200:
                            print(f"  ✅ [VALID MP4] Item: '{title}' ({identifier})")
                            print(f"     URL: {file_url} ({size / 1024 / 1024:.2f} MB)")
                            valid_mp4s.append({
                                "identifier": identifier,
                                "title": title,
                                "fname": fname,
                                "url": file_url,
                                "size_mb": round(size / 1024 / 1024, 2)
                            })
                            break
                    except Exception:
                        pass
        except Exception as e:
            pass

    print(f"\nDiscovered {len(valid_mp4s)} direct working MP4 URLs for news/speeches.")
    return valid_mp4s

if __name__ == "__main__":
    find_news_clips()
