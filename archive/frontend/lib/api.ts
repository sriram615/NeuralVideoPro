/**
 * API Service — NeuralVideo v2.0 FastAPI Backend Client.
 *
 * Connects the Next.js frontend to the FastAPI REST endpoints
 * at http://localhost:8000.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/* ------------------------------------------------------------------ */
/* Types                                                               */
/* ------------------------------------------------------------------ */

export interface IntentTelemetry {
  alpha: number;
  intent_label: string;
  visual_weight_pct: number;
  audio_weight_pct: number;
  auto_detected: boolean;
}

export interface XAIAttribution {
  primary_driver: string;
  primary_driver_emoji: string;
  visual_similarity_pct: number;
  audio_similarity_pct: number;
  fused_score_pct: number;
  fusion_formula: string;
  confidence_tier: string;
}

export interface SearchResultItem {
  rank: number;
  id: string | number;
  fused_score: number;
  visual_score: number;
  audio_score: number;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  payload: Record<string, any>;
  xai: XAIAttribution;
}

export interface SearchResponse {
  query: string;
  total_results: number;
  latency_ms: number;
  intent: IntentTelemetry;
  results: SearchResultItem[];
}

export interface HealthResponse {
  status: string;
  models_loaded: Record<string, boolean>;
  qdrant_connected: boolean;
  total_vectors: number;
  collection_name: string;
}

export interface VideoCatalogItem {
  filename: string;
  title: string;
  video_id: string;
  size_mb: number;
  points_count: number;
}

export interface CorpusStats {
  collection_name: string;
  total_points: number;
  vector_dim: number;
  named_vectors: string[];
  domains: string[];
  video_catalog?: VideoCatalogItem[];
}

/* ------------------------------------------------------------------ */
/* Fetch helpers                                                       */
/* ------------------------------------------------------------------ */

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

/* ------------------------------------------------------------------ */
/* Endpoints                                                           */
/* ------------------------------------------------------------------ */

export async function fetchHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/api/v1/health");
}

export async function fetchSearch(
  query: string,
  topK = 5,
  overrideAlpha?: number,
  domainFilter = "news",
): Promise<SearchResponse> {
  return apiFetch<SearchResponse>("/api/v1/search", {
    method: "POST",
    body: JSON.stringify({
      query,
      top_k: topK,
      override_alpha: overrideAlpha ?? null,
      domain_filter: domainFilter,
    }),
  });
}

export async function fetchCorpusStats(): Promise<CorpusStats> {
  return apiFetch<CorpusStats>("/api/v1/corpus/stats");
}

/** Construct full URL for static video assets served by FastAPI. */
export function staticVideoUrl(filename: string): string {
  return `${API_BASE}/static/videos/${filename}`;
}

/** Construct full URL for static keyframe assets served by FastAPI. */
export function staticFrameUrl(framePath: string): string {
  const cleaned = framePath
    .replace(/^\.\/data\/extracted_frames\//, "")
    .replace(/^data\/extracted_frames\//, "");
  return `${API_BASE}/static/frames/${cleaned}`;
}
