"""
Standalone integration test for QdrantVectorStore.

Exercises:
    1. Collection creation (idempotent)
    2. Upsert of 10 dummy points with normalised 512-d visual + audio vectors
    3. Cosine similarity search on visual_vector, printing top-3 results
    4. Clean shutdown releasing all embedded SQLite locks
"""

import sys
import shutil
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so `src.db` resolves.
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.db.qdrant_db import QdrantVectorStore  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
TEST_DB_PATH = PROJECT_ROOT.parent / "data" / "vectors" / "_test_qdrant_db"

def _normalised_random_vectors(n: int, dim: int = 512, seed: int = 42) -> np.ndarray:
    """Return *n* L2-normalised random vectors of given dimension."""
    rng = np.random.default_rng(seed)
    vecs = rng.standard_normal((n, dim)).astype(np.float32)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / norms


def main() -> None:
    print("=" * 70)
    print("  QdrantVectorStore — Integration Test")
    print("=" * 70)

    # 1. Clean slate for reproducible tests
    if TEST_DB_PATH.exists():
        shutil.rmtree(TEST_DB_PATH)
        print(f"\n[CLEANUP] Removed previous database at {TEST_DB_PATH}")

    # 2. Instantiate store
    store = QdrantVectorStore(db_path=str(TEST_DB_PATH))
    print(f"\n[INIT] QdrantVectorStore opened at {TEST_DB_PATH}")

    # 3. Create collection (should be idempotent)
    store.init_collection()
    store.init_collection()  # second call must be a no-op
    print("[INIT] Collection 'video_intelligence' ready (idempotent check passed).")

    # 4. Generate dummy data
    num_points = 10
    visual_vecs = _normalised_random_vectors(num_points, seed=42)
    audio_vecs = _normalised_random_vectors(num_points, seed=99)

    points = []
    for i in range(num_points):
        points.append({
            "id": i,  # deterministic integer IDs for easy debugging
            "visual_vector": visual_vecs[i].tolist(),
            "audio_vector": audio_vecs[i].tolist(),
            "video_id": f"vid_{i:04d}",
            "timestamp": round(i * 1.5, 2),       # 0.0, 1.5, 3.0, …
            "frame_idx": i * 30,                   # 0, 30, 60, …
            "transcribed_text": f"Sample transcription for frame {i}.",
        })

    # 5. Upsert
    store.upsert_points(points)
    print(f"[UPSERT] Inserted {num_points} points.\n")

    # 6. Search — use the first visual vector as the query
    query_vec = visual_vecs[0].tolist()
    top_k = 3
    results = store.search_vectors(
        query_vector=query_vec,
        vector_name="visual_vector",
        top_k=top_k,
    )

    print(f"[SEARCH] Top-{top_k} results for visual_vector query (point 0):")
    print("-" * 60)
    print(f"  {'Rank':<6}{'ID':<8}{'Score':<12}{'Timestamp':<12}{'Video ID'}")
    print("-" * 60)
    for rank, r in enumerate(results, 1):
        ts = r["payload"]["timestamp"]
        vid = r["payload"]["video_id"]
        print(f"  {rank:<6}{r['id']:<8}{r['score']:<12.6f}{ts:<12}{vid}")
    print("-" * 60)

    # 7. Sanity checks
    assert len(results) == top_k, f"Expected {top_k} results, got {len(results)}"
    assert results[0]["id"] == 0, "Top result should be the query vector itself (id=0)"
    assert abs(results[0]["score"] - 1.0) < 1e-4, "Self-similarity score should be ≈1.0"
    print("\n[ASSERT] All sanity checks passed ✓")

    # 8. Graceful shutdown
    store.close()
    print("[CLOSE] Embedded Qdrant connection closed — lock files released.")

    print("\n" + "=" * 70)
    print("  TEST PASSED ✓")
    print("=" * 70)


def test_qdrant() -> None:
    main()


if __name__ == "__main__":
    main()
