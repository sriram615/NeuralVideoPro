"""
Test exact Archive.org public domain news broadcasts and historical speech MP4s.
"""

from pathlib import Path
import requests

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

ITEMS = [
    "gov.archives.arc.1155021",
    "NasaKsnn-SpaceFlightPhysicalChanges",
    "gov.archives.arc.36067",
    "1944-12-18_News_Digest",
    "1941-12-09_FDR_Report_on_Japan",
    "1952-11-04_Election_Night_News",
    "1969-07-20_Moon_Landing_Broadcast",
    "1960_presidential_debate",
    "1963_march_on_washington",
    "1969_apollo_11_moonwalk",
]

def check_items():
    print("Checking Archive.org news & speech items...")
    valid_links = []
    for item in ITEMS:
        meta_url = f"https://archive.org/metadata/{item}"
        try:
            r = requests.get(meta_url, headers=headers, timeout=5)
            if r.status_code == 200:
                files = r.json().get("files", [])
                for f in files:
                    fname = f.get("name", "")
                    if fname.endswith(".mp4") or fname.endswith("512kb.mp4") or fname.endswith("_512kb.mp4"):
                        url = f"https://archive.org/download/{item}/{fname}"
                        h = requests.head(url, headers=headers, allow_redirects=True, timeout=5)
                        if h.status_code == 200:
                            size_mb = int(h.headers.get("content-length", 0)) / 1024 / 1024
                            print(f"  ✅ [VALID] {item} -> {fname} ({size_mb:.2f} MB)")
                            print(f"     {url}")
                            valid_links.append((item, fname, url, size_mb))
                            break
        except Exception as e:
            pass
    print(f"\nFound {len(valid_links)} valid MP4 video links.")
    return valid_links

if __name__ == "__main__":
    check_items()
