"""
Benchmark: video_intelligence (v1 baseline) vs video_intelligence_v2 (expanded).

Compares vector point counts, search latency, and score consistency across
visual-heavy and audio-heavy queries for both collections.
"""

from __future__ import annotations

import os

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import sys
import time
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from qdrant_client import QdrantClient
from qdrant_client.models import SearchParams

from src.models.text_encoder import TextQueryEncoder

DB_PATH = PROJECT_ROOT / "data" / "qdrant_db"
V1_COLLECTION = "video_intelligence"
V2_COLLECTION = "video_intelligence_v2"

BENCHMARK_QUERIES = [
    {"query": "person in dark suit standing at podium", "type": "Visual-Heavy"},
    {"query": "blue planet earth from space",           "type": "Visual-Heavy"},
    {"query": "astronauts bodies change in space",      "type": "Audio-Heavy"},
    {"query": "retaliate against Israel",               "type": "Audio-Heavy"},
    {"query": "Obama farewell address White House",     "type": "Hybrid"},
    {"query": "sports news and player discussion",      "type": "Hybrid"},
]


def search_collection(
    client: QdrantClient,
    collection_name: str,
    query_vec: List[float],
    vector_name: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    response = client.query_points(
        collection_name=collection_name,
        query=query_vec,
        using=vector_name,
        limit=top_k,
        search_params=SearchParams(exact=False, hnsw_ef=128),
    )
    return [
        {"id": hit.id, "score": hit.score, "payload": hit.payload}
        for hit in response.points
    ]


def run_benchmark() -> None:
    print("=" * 80)
    print("  BENCHMARK: video_intelligence (v1) vs video_intelligence_v2 (v2)")
    print("=" * 80)

    client = QdrantClient(path=str(DB_PATH))
    encoder = TextQueryEncoder()

    # Point counts
    v1_count = client.count(collection_name=V1_COLLECTION).count
    v2_count = client.count(collection_name=V2_COLLECTION).count
    print(f"\n  Collection Point Counts:")
    print(f"    v1 ({V1_COLLECTION}): {v1_count} points")
    print(f"    v2 ({V2_COLLECTION}): {v2_count} points")

    # Run queries against both collections
    header = f"  {'Query':<40}{'Type':<14}{'Vec':<10}{'v1 Lat(ms)':<12}{'v1 Score':<12}{'v2 Lat(ms)':<12}{'v2 Score'}"
    print(f"\n{'-' * 80}")
    print(header)
    print("-" * 80)

    v1_latencies = []
    v2_latencies = []

    for item in BENCHMARK_QUERIES:
        query = item["query"]
        qtype = item["type"]
        qvec = encoder.encode_query(query).tolist()

        for vec_name, vec_label in [("visual_vector", "Visual"), ("audio_vector", "Audio")]:
            # v1 search
            t0 = time.perf_counter()
            v1_hits = search_collection(client, V1_COLLECTION, qvec, vec_name, top_k=5)
            v1_lat = (time.perf_counter() - t0) * 1000
            v1_top = v1_hits[0]["score"] if v1_hits else 0.0
            v1_latencies.append(v1_lat)

            # v2 search
            t0 = time.perf_counter()
            v2_hits = search_collection(client, V2_COLLECTION, qvec, vec_name, top_k=5)
            v2_lat = (time.perf_counter() - t0) * 1000
            v2_top = v2_hits[0]["score"] if v2_hits else 0.0
            v2_latencies.append(v2_lat)

            print(
                f"  {query[:38]:<40}{qtype:<14}{vec_label:<10}"
                f"{v1_lat:<12.1f}{v1_top:<12.4f}{v2_lat:<12.1f}{v2_top:.4f}"
            )

    print("-" * 80)

    v1_avg = sum(v1_latencies) / len(v1_latencies)
    v2_avg = sum(v2_latencies) / len(v2_latencies)
    v1_max = max(v1_latencies)
    v2_max = max(v2_latencies)

    print(f"\n  Latency Summary:")
    print(f"    v1 — Avg: {v1_avg:.1f} ms  |  Max: {v1_max:.1f} ms  |  Points: {v1_count}")
    print(f"    v2 — Avg: {v2_avg:.1f} ms  |  Max: {v2_max:.1f} ms  |  Points: {v2_count}")

    # SLA check
    sla_pass = v1_max < 200 and v2_max < 200
    print(f"\n  Sub-200ms SLA: {'PASSED ✅' if sla_pass else 'FAILED ❌'}")

    client.close()

    # Write report
    report_path = PROJECT_ROOT / "reports" / "v1_v2_benchmark.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        f.write("# v1 vs v2 Collection Benchmark Report\n\n")
        f.write(f"**Date:** July 28, 2026  \n")
        f.write(f"**Hardware:** Mac CPU (`OMP_NUM_THREADS=2`)  \n\n")
        f.write("## Collection Summary\n\n")
        f.write(f"| Collection | Points |\n|---|---|\n")
        f.write(f"| `{V1_COLLECTION}` (v1 Baseline) | **{v1_count}** |\n")
        f.write(f"| `{V2_COLLECTION}` (v2 Expanded) | **{v2_count}** |\n\n")
        f.write("## Latency & Score Matrix\n\n")
        f.write(f"| Query | Type | Vector | v1 Latency | v1 Top Score | v2 Latency | v2 Top Score |\n")
        f.write(f"|---|---|---|---|---|---|---|\n")
        # Re-encode for report (use cached values — just format)
        f.write(f"\n*(See terminal output for full row data)*\n\n")
        f.write("## Latency Summary\n\n")
        f.write(f"| Metric | v1 | v2 |\n|---|---|---|\n")
        f.write(f"| Avg Latency | **{v1_avg:.1f} ms** | **{v2_avg:.1f} ms** |\n")
        f.write(f"| Max Latency | **{v1_max:.1f} ms** | **{v2_max:.1f} ms** |\n")
        f.write(f"| Point Count | **{v1_count}** | **{v2_count}** |\n")
        f.write(f"| Sub-200ms SLA | **{'PASSED ✅' if v1_max < 200 else 'FAILED ❌'}** | **{'PASSED ✅' if v2_max < 200 else 'FAILED ❌'}** |\n")

    print(f"\n  Report saved to: {report_path}")
    print("=" * 80)
    print("  BENCHMARK COMPLETE ✓")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
