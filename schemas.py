"""
Pydantic Schemas — Request/Response contracts for the NeuralVideo v5.0 API.

Defines typed models for search requests, XAI attribution responses,
intent telemetry, health checks, and corpus statistics.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------
class SearchRequest(BaseModel):
    """POST /api/v1/search request body."""

    query: str = Field(..., min_length=1, description="Natural language search query.")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to return.")
    override_alpha: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Manual alpha override (0.0–1.0). If None, auto-intent is used.",
    )
    domain_filter: Optional[str] = Field(
        default="news",
        description="Domain metadata filter. Set to None or 'all' to disable filtering.",
    )


class AskVideoRequest(BaseModel):
    """POST /api/v1/ask-video request body for Grounded Video-RAG."""

    question: str = Field(..., min_length=1, description="User question about the video corpus.")
    top_k_snippets: int = Field(default=5, ge=1, le=20, description="Top context snippets to retrieve.")
    use_mmr: bool = Field(default=True, description="Enable Maximal Marginal Relevance reranking to eliminate redundancy.")


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------
class IntentTelemetry(BaseModel):
    """Zero-Shot Query Intent classification telemetry."""

    alpha: float = Field(..., description="Effective late-fusion alpha weight.")
    intent_label: str = Field(..., description="Human-readable intent label.")
    visual_weight_pct: int = Field(..., description="Visual modality weight as integer percentage.")
    audio_weight_pct: int = Field(..., description="Audio modality weight as integer percentage.")
    auto_detected: bool = Field(..., description="Whether alpha was auto-detected or manually overridden.")
    masked_modality: Optional[str] = Field(default=None, description="Masked modality if speech is absent.")


class XAIAttribution(BaseModel):
    """Explainable AI breakdown for a single search result."""

    primary_driver: str = Field(..., description="Primary modality driver label.")
    primary_driver_emoji: str = Field(..., description="Emoji icon for the driver badge.")
    visual_similarity_pct: float = Field(..., description="Raw visual cosine similarity as percentage.")
    audio_similarity_pct: float = Field(..., description="Raw audio cosine similarity as percentage.")
    fused_score_pct: float = Field(..., description="Late-fusion fused score as percentage.")
    rrf_score: Optional[float] = Field(default=None, description="Reciprocal Rank Fusion score.")
    fusion_formula: str = Field(..., description="Human-readable LaTeX-free fusion formula string.")
    confidence_tier: str = Field(..., description="Confidence tier: 'high', 'moderate', or 'low'.")


class EventSegment(BaseModel):
    """Temporal event segment spanning adjacent keyframe windows."""

    video_id: str = Field(..., description="Unique video identifier.")
    event_start: float = Field(..., description="Event window start time in seconds.")
    event_end: float = Field(..., description="Event window end time in seconds.")
    hero_keyframe_timestamp: float = Field(..., description="Representative hero keyframe timestamp.")
    hero_keyframe_path: str = Field(..., description="Hero keyframe file path.")
    full_transcript_segment: str = Field(..., description="Full spoken dialogue transcript across event window.")
    visual_scene_description: str = Field(default="", description="Visual scene description for multimodal context.")


class SearchResultItem(BaseModel):
    """Single search result with payload, scores, event segment, and XAI attribution."""

    rank: int = Field(..., description="1-indexed rank position.")
    id: Any = Field(..., description="Qdrant point ID.")
    fused_score: float = Field(..., description="Raw fused similarity score (0–1).")
    visual_score: float = Field(..., description="Raw visual cosine similarity (0–1).")
    audio_score: float = Field(..., description="Raw audio cosine similarity (0–1).")
    rrf_score: Optional[float] = Field(default=None, description="Reciprocal Rank Fusion score.")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Qdrant point payload metadata.")
    event_segment: Optional[EventSegment] = Field(default=None, description="Unified temporal event segment payload.")
    xai: XAIAttribution = Field(..., description="Explainable AI attribution breakdown.")
    confidence_band: Optional[str] = Field(default=None, description="Bounded confidence band: HIGH, MEDIUM, or LOW.")
    match_rationale: Optional[List[str]] = Field(default=None, description="Human-readable match rationale strings.")


class SearchResponse(BaseModel):
    """POST /api/v1/search response body."""

    status: str = Field(default="SUCCESS", description="Response status ('SUCCESS' or 'NO_CONFIDENT_MATCH_FOUND').")
    query: str = Field(..., description="Original search query.")
    total_results: int = Field(..., description="Number of results returned.")
    latency_ms: float = Field(..., description="End-to-end search latency in milliseconds.")
    intent: IntentTelemetry = Field(..., description="Intent telemetry for the query.")
    results: List[SearchResultItem] = Field(default_factory=list, description="Ranked search results.")


class AskVideoResponse(BaseModel):
    """POST /api/v1/ask-video response body."""

    question: str = Field(..., description="Original user question.")
    answer: str = Field(..., description="Grounded LLM answer strictly derived from transcript context.")
    citations: List[Dict[str, Any]] = Field(default_factory=list, description="Source video and timestamp citations.")
    context_snippets: List[str] = Field(default_factory=list, description="Retrieved transcript context snippets.")
    retrieval_latency_ms: float = Field(..., description="Vector search retrieval latency in ms (SLA: <200ms).")
    llm_latency_ms: float = Field(default=0.0, description="LLM text generation latency in ms.")
    latency_ms: float = Field(..., description="Total processing latency in ms.")


class HealthResponse(BaseModel):
    """GET /api/v1/health response body."""

    status: str = Field(..., description="System status ('ok' or 'degraded').")
    models_loaded: Dict[str, bool] = Field(
        default_factory=dict,
        description="Loaded model states (clip_encoder, whisper_transcriber, text_encoder).",
    )
    qdrant_connected: bool = Field(..., description="Whether Qdrant vector store is accessible.")
    total_vectors: int = Field(..., description="Total indexed dual-vector point count.")
    collection_name: str = Field(..., description="Active Qdrant collection name.")


class CorpusStatsResponse(BaseModel):
    """GET /api/v1/corpus/stats response body."""

    collection_name: str = Field(..., description="Qdrant collection name.")
    total_points: int = Field(..., description="Total points in collection.")
    vector_dim: int = Field(default=512, description="Embedding dimensionality.")
    named_vectors: List[str] = Field(
        default_factory=lambda: ["visual_vector", "audio_vector"],
        description="Named vector fields.",
    )
    domains: List[str] = Field(default_factory=list, description="Unique domain tags found in corpus.")
    video_catalog: List[Dict[str, Any]] = Field(default_factory=list, description="List of available videos in catalog.")
