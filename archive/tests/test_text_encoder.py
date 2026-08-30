"""
Standalone integration & performance test for TextQueryEncoder.

Validates:
    1. Single-query encoding  → shape (512,), L2 norm ≈ 1.0
    2. Batch encoding (5 queries) → shape (5, 512), all rows normalised
    3. CPU inference latency   → prints ms/query (target < 50 ms)
"""

import sys
import time
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.models.text_encoder import TextQueryEncoder  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
NORM_TOLERANCE = 1e-5
LATENCY_TARGET_MS = 50.0  # per single query on CPU

SINGLE_QUERY = "a red sports car driving down the street"

BATCH_QUERIES = [
    "soccer player scoring a goal from a free kick",
    "a cat sitting on a sunny windowsill",
    "time lapse of a city skyline at sunset",
    "underwater coral reef with tropical fish",
    "chef preparing sushi in a Japanese restaurant",
]


def _check_norm(vec: np.ndarray, label: str) -> None:
    """Assert that a vector (or each row of a matrix) has unit L2 norm."""
    if vec.ndim == 1:
        norm = float(np.linalg.norm(vec))
        assert abs(norm - 1.0) < NORM_TOLERANCE, (
            f"{label}: L2 norm = {norm:.8f}, expected ≈1.0"
        )
    else:
        norms = np.linalg.norm(vec, axis=1)
        for i, n in enumerate(norms):
            assert abs(n - 1.0) < NORM_TOLERANCE, (
                f"{label}[{i}]: L2 norm = {n:.8f}, expected ≈1.0"
            )


def main() -> None:
    print("=" * 70)
    print("  TextQueryEncoder — Integration & Performance Test")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Load model
    # ------------------------------------------------------------------
    t0 = time.perf_counter()
    encoder = TextQueryEncoder()
    load_ms = (time.perf_counter() - t0) * 1000
    print(f"\n[LOAD] Model loaded in {load_ms:,.1f} ms")
    print(f"       {encoder!r}")

    # ------------------------------------------------------------------
    # 2. Single-query encoding
    # ------------------------------------------------------------------
    t0 = time.perf_counter()
    single_vec = encoder.encode_query(SINGLE_QUERY)
    single_ms = (time.perf_counter() - t0) * 1000

    assert isinstance(single_vec, np.ndarray), "Expected np.ndarray"
    assert single_vec.dtype == np.float32, f"Expected float32, got {single_vec.dtype}"
    assert single_vec.shape == (512,), f"Expected (512,), got {single_vec.shape}"
    _check_norm(single_vec, "single_query")

    single_norm = float(np.linalg.norm(single_vec))
    print(f"\n[SINGLE] Query: \"{SINGLE_QUERY}\"")
    print(f"         Shape: {single_vec.shape}  |  dtype: {single_vec.dtype}")
    print(f"         L2 norm: {single_norm:.8f}")
    print(f"         Latency: {single_ms:.2f} ms")
    print(f"         First 8 dims: {single_vec[:8].tolist()}")

    # ------------------------------------------------------------------
    # 3. Batch encoding
    # ------------------------------------------------------------------
    n = len(BATCH_QUERIES)
    t0 = time.perf_counter()
    batch_vecs = encoder.encode_batch_queries(BATCH_QUERIES)
    batch_ms = (time.perf_counter() - t0) * 1000
    per_query_ms = batch_ms / n

    assert isinstance(batch_vecs, np.ndarray), "Expected np.ndarray"
    assert batch_vecs.dtype == np.float32, f"Expected float32, got {batch_vecs.dtype}"
    assert batch_vecs.shape == (n, 512), f"Expected ({n}, 512), got {batch_vecs.shape}"
    _check_norm(batch_vecs, "batch_query")

    norms = np.linalg.norm(batch_vecs, axis=1)
    print(f"\n[BATCH]  {n} queries encoded")
    print(f"         Shape: {batch_vecs.shape}  |  dtype: {batch_vecs.dtype}")
    print(f"         L2 norms: {norms.tolist()}")
    print(f"         Total latency: {batch_ms:.2f} ms")
    print(f"         Per-query: {per_query_ms:.2f} ms")

    # ------------------------------------------------------------------
    # 4. Cosine similarity sanity check
    # ------------------------------------------------------------------
    # Since vectors are L2-normalised, dot product == cosine similarity.
    cos_sims = batch_vecs @ single_vec
    print(f"\n[COSINE] Similarity of batch queries to \"{SINGLE_QUERY[:40]}…\":")
    print("-" * 60)
    for i, (q, s) in enumerate(zip(BATCH_QUERIES, cos_sims)):
        print(f"  {i+1}. {s:+.6f}  \"{q}\"")
    print("-" * 60)

    # ------------------------------------------------------------------
    # 5. Latency target check
    # ------------------------------------------------------------------
    print(f"\n[PERF]  Single-query latency: {single_ms:.2f} ms  "
          f"(target: < {LATENCY_TARGET_MS:.0f} ms) ", end="")
    if single_ms < LATENCY_TARGET_MS:
        print("✅ PASS")
    else:
        # Not a hard failure — first call can include JIT warm-up
        print("⚠️  ABOVE TARGET (first-call warm-up expected)")

    # Warm run (second call) for fair measurement
    t0 = time.perf_counter()
    _ = encoder.encode_query(SINGLE_QUERY)
    warm_ms = (time.perf_counter() - t0) * 1000
    print(f"[PERF]  Warm-run latency:     {warm_ms:.2f} ms  "
          f"(target: < {LATENCY_TARGET_MS:.0f} ms) ", end="")
    if warm_ms < LATENCY_TARGET_MS:
        print("✅ PASS")
    else:
        print("⚠️  ABOVE TARGET")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n[ASSERT] All shape, dtype, and normalization checks passed ✓")

    print("\n" + "=" * 70)
    print("  TEST PASSED ✓")
    print("=" * 70)


def test_text_encoder() -> None:
    main()


if __name__ == "__main__":
    main()
