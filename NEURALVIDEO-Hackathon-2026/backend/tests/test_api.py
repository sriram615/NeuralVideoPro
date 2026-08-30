"""
API Endpoint Tests — NeuralVideo v5.0 FastAPI Backend.

Verifies:
    1. Module imports and schema validation.
    2. GET /api/v1/health returns 200 with expected structure.
    3. POST /api/v1/search returns 200 with intent telemetry and XAI attribution.
    4. GET /api/v1/corpus/stats returns 200 with corpus metadata.
    5. Search validation rejects empty queries (422).
    6. Alpha override mode disables auto-intent.

Usage:
    HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python -m pytest tests/test_api.py -v
"""

from __future__ import annotations

import os

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path for both api and src imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="module")
def client():
    """Create a TestClient with the FastAPI app (loads pipeline once per module)."""
    import shutil
    from fastapi.testclient import TestClient

    src_db = PROJECT_ROOT.parent / "data" / "vectors" / "qdrant_db"
    test_db = PROJECT_ROOT.parent / "data" / "vectors" / "_test_api_qdrant_db"

    if test_db.exists():
        shutil.rmtree(test_db, ignore_errors=True)

    if src_db.exists():
        shutil.copytree(src_db, test_db)
    else:
        test_db.mkdir(parents=True, exist_ok=True)

    old_env = os.environ.get("QDRANT_DB_PATH")
    os.environ["QDRANT_DB_PATH"] = str(test_db)

    from api import app

    try:
        with TestClient(app) as c:
            yield c
    finally:
        if old_env is not None:
            os.environ["QDRANT_DB_PATH"] = old_env
        else:
            os.environ.pop("QDRANT_DB_PATH", None)

        if test_db.exists():
            shutil.rmtree(test_db, ignore_errors=True)


# ---------------------------------------------------------------------------
# Import & Schema Tests
# ---------------------------------------------------------------------------
class TestImportsAndSchemas:
    """Verify that all modules import and schemas instantiate correctly."""

    def test_api_module_imports(self):
        import api

        assert hasattr(api, "app"), "api.py missing FastAPI app instance"
        assert hasattr(api, "predict_alpha"), "api.py missing predict_alpha function"

    def test_schema_imports(self):
        from schemas import (
            CorpusStatsResponse,
            HealthResponse,
            IntentTelemetry,
            SearchRequest,
            SearchResponse,
            SearchResultItem,
            XAIAttribution,
        )

        # Validate SearchRequest instantiation
        req = SearchRequest(query="test query", top_k=3)
        assert req.query == "test query"
        assert req.top_k == 3
        assert req.override_alpha is None

    def test_predict_alpha_visual(self):
        from api import predict_alpha

        alpha, label = predict_alpha("person in suit standing at podium")
        assert alpha == 0.8
        assert label == "High Visual Bias"

    def test_predict_alpha_audio(self):
        from api import predict_alpha

        alpha, label = predict_alpha("speech transcript quote retaliate")
        assert alpha == 0.2
        assert label == "High Audio/Speech Bias"

    def test_predict_alpha_balanced(self):
        from api import predict_alpha

        alpha, label = predict_alpha("Obama farewell speech White House podium")
        assert alpha == 0.5
        assert label == "Balanced Hybrid"


# ---------------------------------------------------------------------------
# Health Endpoint
# ---------------------------------------------------------------------------
class TestHealthEndpoint:
    """Verify GET /api/v1/health."""

    def test_health_returns_200(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200

    def test_health_has_required_fields(self, client):
        data = client.get("/api/v1/health").json()
        assert "status" in data
        assert "models_loaded" in data
        assert "qdrant_connected" in data
        assert "total_vectors" in data
        assert "collection_name" in data

    def test_health_status_ok(self, client):
        data = client.get("/api/v1/health").json()
        assert data["status"] == "ok"
        assert data["qdrant_connected"] is True
        assert data["total_vectors"] > 0

    def test_health_models_loaded(self, client):
        data = client.get("/api/v1/health").json()
        models = data["models_loaded"]
        assert models.get("clip_encoder") is True
        assert models.get("whisper_transcriber") is True
        assert models.get("text_encoder") is True


# ---------------------------------------------------------------------------
# Search Endpoint
# ---------------------------------------------------------------------------
class TestSearchEndpoint:
    """Verify POST /api/v1/search."""

    def test_search_returns_200(self, client):
        resp = client.post(
            "/api/v1/search",
            json={"query": "person in suit at podium", "top_k": 3},
        )
        assert resp.status_code == 200

    def test_search_response_structure(self, client):
        data = client.post(
            "/api/v1/search",
            json={"query": "person in suit at podium", "top_k": 3},
        ).json()

        assert "query" in data
        assert "total_results" in data
        assert "latency_ms" in data
        assert "intent" in data
        assert "results" in data

    def test_search_intent_telemetry(self, client):
        data = client.post(
            "/api/v1/search",
            json={"query": "person in suit at podium", "top_k": 3},
        ).json()

        intent = data["intent"]
        assert intent["auto_detected"] is True
        assert intent["alpha"] == 0.8
        assert intent["intent_label"] == "High Visual Bias"
        assert intent["visual_weight_pct"] == 80
        assert intent["audio_weight_pct"] == 20

    def test_search_results_have_xai(self, client):
        data = client.post(
            "/api/v1/search",
            json={"query": "person in suit at podium", "top_k": 3},
        ).json()

        if data["total_results"] > 0:
            result = data["results"][0]
            assert "xai" in result
            xai = result["xai"]
            assert "primary_driver" in xai
            assert "confidence_tier" in xai
            assert "fusion_formula" in xai
            assert "visual_similarity_pct" in xai
            assert "audio_similarity_pct" in xai
            assert "fused_score_pct" in xai

    def test_search_with_alpha_override(self, client):
        data = client.post(
            "/api/v1/search",
            json={
                "query": "person in suit at podium",
                "top_k": 2,
                "override_alpha": 0.3,
            },
        ).json()

        intent = data["intent"]
        assert intent["auto_detected"] is False
        assert intent["alpha"] == 0.3
        assert intent["intent_label"] == "Manual Override"

    def test_search_server_timing_header(self, client):
        resp = client.post(
            "/api/v1/search",
            json={"query": "person in suit at podium", "top_k": 3},
        )
        assert "server-timing" in resp.headers or "Server-Timing" in resp.headers
        timing_val = resp.headers.get("server-timing") or resp.headers.get("Server-Timing")
        assert "encoder" in timing_val
        assert "qdrant" in timing_val
        assert "rrf_fusion" in timing_val

    def test_search_rrf_score_presence(self, client):
        data = client.post(
            "/api/v1/search",
            json={"query": "person in suit at podium", "top_k": 3},
        ).json()
        assert "status" in data
        if data["total_results"] > 0:
            res = data["results"][0]
            assert "rrf_score" in res

    def test_ask_video_decoupled_latency(self, client):
        resp = client.post(
            "/api/v1/ask-video",
            json={"question": "What speeches were given?", "top_k_snippets": 3},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "retrieval_latency_ms" in data
        assert "llm_latency_ms" in data
        assert "latency_ms" in data
        assert data["retrieval_latency_ms"] >= 0.0
        assert data["latency_ms"] >= data["retrieval_latency_ms"]


# ---------------------------------------------------------------------------
# Corpus Stats Endpoint
# ---------------------------------------------------------------------------
class TestCorpusStatsEndpoint:
    """Verify GET /api/v1/corpus/stats."""

    def test_corpus_stats_returns_200(self, client):
        resp = client.get("/api/v1/corpus/stats")
        assert resp.status_code == 200

    def test_corpus_stats_structure(self, client):
        data = client.get("/api/v1/corpus/stats").json()
        assert "collection_name" in data
        assert "total_points" in data
        assert "vector_dim" in data
        assert "named_vectors" in data
        assert "domains" in data

    def test_corpus_stats_values(self, client):
        data = client.get("/api/v1/corpus/stats").json()
        assert data["collection_name"] == "video_intelligence"
        assert data["vector_dim"] == 512
        assert data["total_points"] > 0
        assert "visual_vector" in data["named_vectors"]
        assert "audio_vector" in data["named_vectors"]


# ---------------------------------------------------------------------------
# Evaluation Suite & Ground Truth Tests
# ---------------------------------------------------------------------------
class TestEvalSuite:
    """Verify eval_suite.py execution, ground truth dataset, math bounds, and ablation engine."""

    def test_ground_truth_dataset_loading(self):
        from scripts.evaluation.eval_suite import load_ground_truth_benchmark
        dataset = load_ground_truth_benchmark()
        assert len(dataset) == 30, f"Expected 30 queries in ground truth benchmark, found {len(dataset)}"
        for item in dataset:
            assert "query_id" in item
            assert "query" in item
            assert "category" in item
            assert "ground_truth_video_ids" in item
            assert len(item["ground_truth_video_ids"]) > 0

    def test_eval_suite_strict_math_bounds(self, client):
        from scripts.evaluation.eval_suite import evaluate_pipeline
        from api import get_pipeline
        pipeline = get_pipeline()
        metrics = evaluate_pipeline(pipeline=pipeline)
        assert "mrr_5" in metrics
        assert "precision_5" in metrics
        assert "recall_5" in metrics
        assert "mean_vector_latency_ms" in metrics

        # Strict Mathematical Bounds Assertions
        assert 0.0 <= metrics["recall_5"] <= 1.0, f"Recall@5 out of bounds [0, 1]: {metrics['recall_5']}"
        assert 0.0 <= metrics["precision_5"] <= 1.0, f"Precision@5 out of bounds [0, 1]: {metrics['precision_5']}"
        assert 0.0 <= metrics["mrr_5"] <= 1.0, f"MRR@5 out of bounds [0, 1]: {metrics['mrr_5']}"
        assert metrics["total_queries_tested"] == 30

    def test_ablation_study_execution(self, client):
        from scripts.evaluation.eval_suite import run_ablation_study
        from api import get_pipeline
        pipeline = get_pipeline()
        results = run_ablation_study(pipeline=pipeline)
        assert isinstance(results, dict)
        assert "Auto-Intent RRF + Agreement + MMR" in results

    def test_semantic_vector_mmr_cosine(self):
        from src.pipeline import VideoSearchPipeline
        v1 = [1.0] * 512
        v2 = [1.0] * 512
        v3 = [-1.0] * 512
        sim_identical = VideoSearchPipeline._cosine_sim(v1, v2)
        sim_opposite = VideoSearchPipeline._cosine_sim(v1, v3)
        assert abs(sim_identical - 1.0) < 1e-4
        assert abs(sim_opposite - (-1.0)) < 1e-4

        candidates = [
            {"id": "1", "rrf_score": 0.03, "visual_vector": v1, "payload": {"video_id": "v1", "timestamp": 10.0}},
            {"id": "2", "rrf_score": 0.029, "visual_vector": v2, "payload": {"video_id": "v1", "timestamp": 12.0}},
            {"id": "3", "rrf_score": 0.025, "visual_vector": v3, "payload": {"video_id": "v2", "timestamp": 50.0}},
        ]
        selected = VideoSearchPipeline._apply_mmr_diversification(candidates, top_k=2, lambda_param=0.7)
        assert len(selected) == 2
        assert selected[0]["id"] == "1"
        assert selected[1]["id"] == "3"

    def test_cross_modal_agreement_score_boost(self):
        from src.pipeline import VideoSearchPipeline
        cands = [
            {"id": "a", "rrf_score": 0.02, "visual_score": 0.3, "audio_score": 0.1},
            {"id": "b", "rrf_score": 0.019, "visual_score": 0.8, "audio_score": 0.8},
        ]
        reranked = VideoSearchPipeline._apply_cross_modal_agreement_score(cands)
        assert len(reranked) == 2
        assert reranked[0]["id"] == "b"

    def test_confidence_band_mapping(self):
        from src.pipeline import VideoSearchPipeline
        assert VideoSearchPipeline._get_confidence_band({"score": 0.75, "rrf_score": 0.025}) == "HIGH"
        assert VideoSearchPipeline._get_confidence_band({"score": 0.50, "rrf_score": 0.015}) == "MEDIUM"
        assert VideoSearchPipeline._get_confidence_band({"score": 0.10, "rrf_score": 0.005}) == "LOW"

    def test_match_rationale_structure(self):
        from src.pipeline import VideoSearchPipeline
        result = {"visual_score": 0.6, "audio_score": 0.4, "rrf_score": 0.018}
        rationale = VideoSearchPipeline._get_match_rationale(result, True, True, None)
        assert isinstance(rationale, list)
        assert len(rationale) >= 5  # visual + audio + rrf + agreement + mmr
        assert any("Cross-Modal Agreement" in r for r in rationale)
        assert any("MMR" in r for r in rationale)

    def test_match_rationale_with_masked_modality(self):
        from src.pipeline import VideoSearchPipeline
        result = {"visual_score": 0.6, "audio_score": 0.0, "rrf_score": 0.010}
        rationale = VideoSearchPipeline._get_match_rationale(result, False, True, "audio (silent)")
        assert any("masked" in r.lower() for r in rationale)
        assert not any("Cross-Modal Agreement" in r for r in rationale)

    def test_qualitative_case_studies_generation(self, client):
        from scripts.evaluation.eval_suite import generate_qualitative_case_studies
        from api import get_pipeline
        pipeline = get_pipeline()
        case_studies = generate_qualitative_case_studies(pipeline=pipeline)
        assert len(case_studies) == 3
        for cs in case_studies:
            assert "category" in cs
            assert "query" in cs
            assert "top_5_retrieved_events" in cs
            assert len(cs["top_5_retrieved_events"]) > 0





