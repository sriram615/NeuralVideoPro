import sys
from pathlib import Path

sys.path.insert(0, "./backend")
from qdrant_client import QdrantClient

client = QdrantClient(path="data/vectors/qdrant_db")
points, _ = client.scroll(collection_name="video_intelligence", limit=3000, with_payload=True, with_vectors=False)

videos = {}
for p in points:
    payload = p.payload or {}
    vid = payload.get("video_id", "unknown")
    domain = payload.get("domain", "all")
    text = payload.get("transcribed_text", "")
    frame_path = payload.get("frame_path", "")
    if vid not in videos:
        videos[vid] = {"domain": domain, "count": 0, "transcripts": [], "frame_sample": frame_path}
    videos[vid]["count"] += 1
    if text and text not in videos[vid]["transcripts"] and text != "Visual scene footage":
        videos[vid]["transcripts"].append(text)

print(f"Total Vectors Indexed: {len(points)}")
print(f"Total Unique Videos: {len(videos)}\n")

for vid, info in videos.items():
    print(f"🎥 Video ID : {vid}")
    print(f"   Domain   : {info['domain']}")
    print(f"   Keyframes: {info['count']}")
    print(f"   Transcripts Snippets ({len(info['transcripts'])} found):")
    for t in info["transcripts"][:5]:
        print(f"     • \"{t[:100]}\"")
    print("=" * 70)
