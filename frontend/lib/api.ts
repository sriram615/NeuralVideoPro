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
  masked_modality?: string;
}

export interface XAIAttribution {
  primary_driver: string;
  primary_driver_emoji: string;
  visual_similarity_pct: number;
  audio_similarity_pct: number;
  fused_score_pct: number;
  rrf_score?: number;
  fusion_formula: string;
  confidence_tier: string;
}

export interface EventSegment {
  video_id: string;
  event_start: number;
  event_end: number;
  hero_keyframe_timestamp: number;
  hero_keyframe_path: string;
  full_transcript_segment: string;
  visual_scene_description?: string;
}

export interface SearchResultItem {
  rank: number;
  id: string | number;
  fused_score: number;
  visual_score: number;
  audio_score: number;
  rrf_score?: number;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  payload: Record<string, any>;
  event_segment?: EventSegment;
  xai: XAIAttribution;
  confidence_band?: string;
  match_rationale?: string[];
}

export interface SearchResponse {
  status: string;
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
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    });
  } catch (err) {
    if (API_BASE.includes("localhost")) {
      const fallbackUrl = API_BASE.replace("localhost", "127.0.0.1");
      res = await fetch(`${fallbackUrl}${path}`, {
        ...init,
        headers: {
          "Content-Type": "application/json",
          ...(init?.headers ?? {}),
        },
      });
    } else {
      throw err;
    }
  }
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
  domainFilter = "all",
  enableMmr = true,
  enableReranker = false,
): Promise<SearchResponse> {
  return apiFetch<SearchResponse>("/api/v1/search", {
    method: "POST",
    body: JSON.stringify({
      query,
      top_k: topK,
      override_alpha: overrideAlpha ?? null,
      domain_filter: domainFilter,
      enable_mmr: enableMmr,
      enable_reranker: enableReranker,
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

/**
 * Resolve the on-disk video filename for a search result.
 *
 * Search payloads carry a hashed ``video_id`` (e.g.
 * ``atheist_discussion_interview_0b781ddebb17``) that is *not* a filename, so
 * the authoritative name is taken from the corpus catalog when available.
 * Callers should treat an empty string as "no playable source" and render a
 * placeholder rather than guessing an extension.
 */
export function resolveVideoFilename(
  rawFilename: string | undefined | null,
  videoId?: string | null,
  catalog?: VideoCatalogItem[] | null,
): string {
  const explicit = (rawFilename ?? "").trim();
  if (explicit) {
    return explicit;
  }
  const id = (videoId ?? "").trim();
  if (!id) {
    return "";
  }
  const match = catalog?.find((item) => item.video_id === id);
  return match?.filename ?? "";
}

/** Construct full URL for static keyframe assets served by FastAPI. */
export function staticFrameUrl(framePath: string): string {
  if (!framePath) return "";
  const match = framePath.match(/extracted_frames[^/]*\/(.+)$/);
  if (match && match[1]) {
    return `${API_BASE}/static/frames/${match[1]}`;
  }
  const basename = framePath.split("/").pop() || "";
  return `${API_BASE}/static/frames/${basename}`;
}
