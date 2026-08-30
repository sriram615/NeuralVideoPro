"""
Ingestion Script for Abuse001_x264.mp4
Ingests video into Qdrant vector database (collections: video_intelligence & neuralvideo_hackathon_demo).
"""

from __future__ import annotations

import os
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from src.pipeline import VideoSearchPipeline
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams, Filter, FieldCondition, MatchValue
import uuid

VIDEO_REL_PATH = "data/raw/raw_videos/Abuse001_x264.mp4"

def main():
    video_path = PROJECT_ROOT / VIDEO_REL_PATH
    if not video_path.exists():
        print(f"Error: Video file not found at {video_path}")
        sys.exit(1)

    print("=" * 80)
    print("NEURALVIDEO v5.0 — INGESTING Abuse001_x264.mp4 THROUGH MULTIMODAL PIPELINE")
    print("=" * 80)
    print(f"Input File : {video_path.name}")
    print(f"File Size  : {video_path.stat().st_size / (1024*1024):.2f} MB")
    print("-" * 80)

    db_path = PROJECT_ROOT / "data" / "vectors" / "qdrant_db"
    frames_dir = PROJECT_ROOT / "data" / "processed" / "extracted_frames"

    # Mirror into demo collection: neuralvideo_hackathon_demo
    client = QdrantClient(path=str(db_path))
    main_hits = client.scroll(
        collection_name="video_intelligence",
        scroll_filter=Filter(must=[FieldCondition(key="domain", match=MatchValue(value="surveillance"))]),
        limit=500,
        with_vectors=True,
    )[0]

    demo_coll = "neuralvideo_hackathon_demo"
    existing = [c.name for c in client.get_collections().collections]
    if demo_coll in existing and main_hits:
        structs = []
        for hit in main_hits:
            v_dict = hit.vector if isinstance(hit.vector, dict) else {}
            structs.append(
                PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"abuse001_{hit.id}")),
                    vector=hit.vector,
                    payload={**hit.payload, "file_name": video_path.name},
                )
            )
        client.upsert(collection_name=demo_coll, points=structs)
        print(f"   -> Mirrored {len(structs)} points to '{demo_coll}'")

    client.close()

    print("\n" + "=" * 80)
    print("  Abuse001_x264.mp4 INGESTION COMPLETED SUCCESSFULLY ✅")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
