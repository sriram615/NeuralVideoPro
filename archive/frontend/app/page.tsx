"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import WireframeArcs from "@/components/WireframeArcs";
import {
  fetchCorpusStats,
  fetchHealth,
  fetchSearch,
  staticFrameUrl,
  staticVideoUrl,
  type CorpusStats,
  type HealthResponse,
  type SearchResponse,
} from "@/lib/api";

/* ================================================================
   HEADER COMPONENT — NEURALVIDEO V2.0 PRO
   ================================================================ */

function Header({
  tickerText,
  pageIndex,
  onNavigate,
}: {
  tickerText: string;
  pageIndex: number;
  onNavigate: (index: number) => void;
}) {
  return (
    <header className="cthdrl-header">
      {/* Logo Icon Box */}
      <div
        className="cthdrl-logo-box cursor-pointer"
        onClick={() => onNavigate(0)}
        title="Go to Front Page"
      >
        <svg
          width="26"
          height="26"
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M 16 4 C 8 4, 4 12, 4 28"
            stroke="#00FF66"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
          <path
            d="M 16 4 C 24 4, 28 12, 28 28"
            stroke="#00FF66"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
          <path
            d="M 16 12 C 10 12, 8 18, 8 28"
            stroke="#E6E1D5"
            strokeWidth="1.5"
          />
          <path
            d="M 16 12 C 22 12, 24 18, 24 28"
            stroke="#E6E1D5"
            strokeWidth="1.5"
          />
          <line x1="4" y1="28" x2="28" y2="28" stroke="#E6E1D5" strokeWidth="2" />
        </svg>
      </div>

      {/* NEURALVIDEO / V2.0 PRO */}
      <div className="cthdrl-nav-block cursor-pointer" onClick={() => onNavigate(0)}>
        <span className="font-bold text-[#E6E1D5] tracking-wider">NEURALVIDEO</span>
        <span style={{ color: "var(--accent-cyan)" }}>/V2.0 PRO</span>
      </div>

      {/* MULTIMODAL / SEARCH ENGINE */}
      <div className="cthdrl-nav-block hidden sm:flex">
        <span>MULTIMODAL</span>
        <span style={{ color: "rgba(230, 225, 213, 0.6)" }}>SEARCH ENGINE</span>
      </div>

      {/* Middle Header Ticker */}
      <div className="cthdrl-header-ticker">{tickerText}</div>

      {/* Right Page Counter */}
      <div className="cthdrl-page-counter">{pageIndex + 1}/03</div>
    </header>
  );
}

/* ================================================================
   PAGE 1 (Index 0) — FRONT PAGE / LANDING PAGE
   ================================================================ */

function PageFrontPage({
  isActive,
  onNavigate,
  health,
  corpusStats,
}: {
  isActive: boolean;
  onNavigate: (page: number) => void;
  health: HealthResponse | null;
  corpusStats: CorpusStats | null;
}) {
  return (
    <div className={`page-view ${isActive ? "page-view-active" : "page-view-hidden"}`}>
      <Header
        tickerText="NEURALVIDEO X QDRANT DUAL-VECTOR RETRIEVAL ENGINE"
        pageIndex={0}
        onNavigate={onNavigate}
      />

      <div className="flex-1 relative flex flex-col justify-center items-center p-6 md:p-12 text-center overflow-hidden">
        <WireframeArcs variant="manifesto" />

        {/* CENTERED HERO CONTAINER (TECH WIREFRAME MONOSPACE THIN) */}
        <div className="z-10 max-w-5xl mx-auto flex flex-col items-center justify-center my-auto px-4">
          {/* Badge */}
          <div className="inline-flex items-center gap-3 px-5 py-2 bg-white/5 wire-all mb-8 rounded-full border border-emerald-500/30">
            <span className="w-2 h-2 rounded-full bg-[var(--accent-cyan)] animate-pulse" />
            <span className="font-mono font-light text-xs text-[var(--accent-cyan)] tracking-[0.25em] uppercase">
              ZERO-SHOT MULTIMODAL VIDEO INTELLIGENCE
            </span>
          </div>

          {/* Centered Main Title — Thin Monospaced Wireframe Style */}
          <h1 className="font-mono font-extralight text-5xl sm:text-7xl md:text-8xl lg:text-9xl uppercase tracking-[0.15em] text-white leading-none mb-8 drop-shadow-lg">
            NEURALVIDEO PRO
          </h1>

          {/* Centered Tagline — Thin Monospaced High-Contrast */}
          <p className="font-mono font-light text-lg sm:text-xl md:text-2xl text-[#E6E1D5] max-w-4xl leading-relaxed mb-12 text-center tracking-wide">
            Real-time multimodal search engine combining{" "}
            <span className="text-[var(--accent-cyan)] font-normal border-b border-emerald-400/50 pb-0.5">
              CLIP ViT-B/32 visual keyframes
            </span>{" "}
            and{" "}
            <span className="text-white font-normal border-b border-white/50 pb-0.5">
              Whisper Base acoustic dialogue transcripts
            </span>
          </p>

          {/* Centered Launch CTA Button — Thin Monospaced Tech Styling */}
          <button
            onClick={() => onNavigate(1)}
            className="font-mono font-light text-lg sm:text-xl tracking-[0.2em] uppercase px-10 py-5 bg-emerald-950/30 hover:bg-[var(--accent-cyan)] text-[var(--accent-cyan)] hover:text-black border border-[var(--accent-cyan)]/70 hover:border-[var(--accent-cyan)] rounded-xl transition-all duration-300 shadow-xl shadow-emerald-950/50 hover:scale-105 group cursor-pointer flex items-center gap-4"
          >
            LAUNCH SEARCH ENGINE
            <span className="text-2xl group-hover:translate-x-1 transition-transform">↴</span>
          </button>
        </div>

        {/* Minimal Bottom Bar */}
        <div className="w-full z-10 border-t border-[rgba(230,225,213,0.2)] pt-4 flex justify-between items-center text-xs font-mono text-[rgba(230,225,213,0.7)]">
          <div>
            <span>● SYSTEM: {health?.status === "ok" ? "ONLINE" : "CONNECTING…"}</span>
          </div>
          <div>
            <button
              onClick={() => onNavigate(1)}
              className="cthdrl-link-btn text-xs font-mono font-light tracking-widest text-[#E6E1D5] hover:text-[var(--accent-cyan)]"
            >
              ENTER SEARCH CONSOLE ↳
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   PAGE 2 (Index 1) — SEARCH CONSOLE / QUERY INPUT
   ================================================================ */

function PageTerminal({
  isActive,
  onNavigate,
  onSearch,
  isSearching,
  searchError,
  corpusStats,
}: {
  isActive: boolean;
  onNavigate: (page: number) => void;
  onSearch: (query: string) => void;
  isSearching: boolean;
  searchError: string | null;
  corpusStats: CorpusStats | null;
}) {
  const [query, setQuery] = useState("");
  const [selectedCatalogVideo, setSelectedCatalogVideo] = useState("all");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isSearching) {
      onSearch(query.trim());
    }
  };

  return (
    <div className={`page-view ${isActive ? "page-view-active" : "page-view-hidden"}`}>
      <Header
        tickerText="SEARCH CONSOLE // MULTIMODAL QUERY INPUT"
        pageIndex={1}
        onNavigate={onNavigate}
      />

      <div className="flex-1 relative flex flex-col justify-center items-center p-6 md:p-12 text-center overflow-hidden">
        <WireframeArcs variant="terminal" />

        <div className="z-10 max-w-5xl mx-auto w-full flex flex-col items-center justify-center my-auto px-4 py-8 space-y-8 sm:space-y-12">
          
          <div className="text-center">
            <span className="font-mono font-light text-xs sm:text-sm text-[var(--accent-cyan)] tracking-[0.25em] uppercase block mb-4">
              PAGE 2 OF 3 // MULTIMODAL SEARCH CONSOLE
            </span>
            <h2 className="font-mono font-extralight text-5xl sm:text-7xl md:text-8xl lg:text-9xl uppercase tracking-[0.15em] text-white leading-none drop-shadow-lg">
              SEARCH CONSOLE
            </h2>
          </div>

          {/* Video Catalog Selector Dropdown */}
          <div className="w-full max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-md">
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <span className="font-mono font-bold text-xs text-[var(--accent-cyan)] tracking-wider uppercase">
                VIDEO CATALOG SELECTOR:
              </span>
              <select
                value={selectedCatalogVideo}
                onChange={(e) => setSelectedCatalogVideo(e.target.value)}
                className="px-4 py-2 bg-black/90 text-white font-mono text-xs rounded-xl border border-white/20 focus:border-[var(--accent-cyan)] outline-none cursor-pointer flex-1 sm:w-80"
              >
                <option value="all">ALL VIDEOS IN CORPUS ({corpusStats?.total_points || 0} Points)</option>
                {corpusStats?.video_catalog && corpusStats.video_catalog.length > 0 ? (
                  corpusStats.video_catalog.map((item) => (
                    <option key={item.filename} value={item.filename}>
                      {item.title} ({item.size_mb} MB)
                    </option>
                  ))
                ) : (
                  <option value="Steve Jobs Interview Feb 18 1981.mp4">
                    Steve Jobs Interview Feb 18 1981.mp4 (50.9 MB)
                  </option>
                )}
              </select>
            </div>
            <div className="text-xs font-mono text-gray-400">
              ACTIVE DOMAIN: <strong className="text-white">NEWS / HISTORICAL SPEECH</strong>
            </div>
          </div>

          {/* Floating Giant Search Bar Container */}
          <div className="w-full max-w-4xl mx-auto">
            <form onSubmit={handleSubmit} className="relative">
              <input
                type="text"
                className="cthdrl-input"
                placeholder='e.g. "young man sitting in office with glasses" or "television shoots for lowest common denominator"'
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                autoFocus={isActive}
              />
            </form>
          </div>

          {/* Benchmark Sample Prompts */}
          <div className="w-full max-w-4xl mx-auto text-center space-y-4">
            <span className="font-mono font-bold text-xs sm:text-sm text-gray-300 tracking-[0.25em] uppercase block">
              STEVE JOBS 20-MIN INTERVIEW BENCHMARK PROMPTS:
            </span>
            <div className="flex flex-wrap items-center justify-center gap-3">
              {[
                { label: "👁️ Visual: Young man sitting in office with glasses", q: "young man sitting in office in front of Apple computer with glasses" },
                { label: "🎧 Audio: Television shoots for lowest common denominator", q: "television shoots for the lowest common denominator" },
                { label: "⚖️ Hybrid: Steve Jobs discussing computers near Apple logo", q: "Steve Jobs discussing computers while sitting near Apple logo" },
              ].map((sample) => (
                <button
                  key={sample.q}
                  type="button"
                  onClick={() => {
                    setQuery(sample.q);
                    onSearch(sample.q);
                  }}
                  className="text-xs font-mono font-bold py-3 px-5 bg-white/5 hover:bg-[var(--accent-cyan)] hover:text-black text-white transition-all duration-300 rounded-xl border border-white/20 hover:border-[var(--accent-cyan)] cursor-pointer shadow-lg backdrop-blur-md hover:scale-105"
                >
                  {sample.label}
                </button>
              ))}
            </div>
          </div>

          {/* Error Banner */}
          {searchError && (
            <div className="w-full max-w-3xl mx-auto p-5 border border-red-500/50 bg-red-950/40 text-red-200 text-sm font-mono font-bold rounded-2xl">
              SEARCH ERROR: {searchError}
            </div>
          )}

          {/* Action Row — Floating Launch CTA Button */}
          <div className="text-center pt-4">
            <button
              onClick={() => query.trim() && !isSearching && onSearch(query.trim())}
              disabled={!query.trim() || isSearching}
              className="px-14 py-6 bg-[var(--accent-cyan)] hover:bg-emerald-300 disabled:opacity-30 disabled:cursor-not-allowed text-black font-black text-xl md:text-2xl tracking-widest uppercase flex items-center gap-4 transition-all duration-300 rounded-2xl cursor-pointer border-none shadow-2xl shadow-emerald-950/80 hover:scale-105 mx-auto"
            >
              {isSearching ? "SEARCHING…" : "EXECUTE ENGINE"} <span className="text-3xl">↴</span>
            </button>
          </div>
        </div>

        {/* Minimal Bottom Bar */}
        <div className="w-full z-10 border-t border-[rgba(230,225,213,0.2)] pt-4 flex justify-end items-center text-xs font-mono text-[rgba(230,225,213,0.7)]">
          <div>
            <button
              onClick={() => onNavigate(2)}
              className="cthdrl-link-btn text-xs font-bold text-[#E6E1D5] hover:text-[var(--accent-cyan)]"
            >
              VIEW RESULTS & XAI ↳
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   PAGE 3 (Index 2) — RESULTS GALLERY & XAI PROVENANCE MATRIX
   ================================================================ */

function PageGalleryAndXAI({
  isActive,
  onNavigate,
  data,
  isSearching,
}: {
  isActive: boolean;
  onNavigate: (page: number) => void;
  data: SearchResponse | null;
  isSearching: boolean;
}) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    setSelectedIndex(0);
  }, [data]);

  const activeItem = data?.results?.[selectedIndex] || data?.results?.[0];

  useEffect(() => {
    if (activeItem?.payload?.timestamp !== undefined && videoRef.current) {
      videoRef.current.currentTime = (activeItem.payload.timestamp as number) || 0;
    }
  }, [activeItem]);

  const handleSeekToTimestamp = (sec: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = sec;
      videoRef.current.play().catch(() => {});
    }
  };

  if (isSearching) {
    return (
      <div className={`page-view ${isActive ? "page-view-active" : "page-view-hidden"}`}>
        <Header
          tickerText="SEARCH ENGINE EXECUTING VECTOR SEARCH…"
          pageIndex={2}
          onNavigate={onNavigate}
        />
        <div className="flex-1 flex flex-col items-center justify-center p-12">
          <div className="w-12 h-12 border-2 border-[var(--accent-cyan)] border-t-transparent rounded-full animate-spin mb-6" />
          <p className="cthdrl-mono text-lg text-[var(--accent-cyan)]">SEARCHING QDRANT VECTOR SPACE…</p>
          <p className="text-xs font-mono text-[#E6E1D5] mt-2">Computing CLIP visual + Whisper audio Late Fusion scores</p>
        </div>
      </div>
    );
  }

  if (!data || !data.results || data.results.length === 0 || !activeItem) {
    return (
      <div className={`page-view ${isActive ? "page-view-active" : "page-view-hidden"}`}>
        <Header
          tickerText="RESULTS REEL // AWAITING SEARCH EXECUTION"
          pageIndex={2}
          onNavigate={onNavigate}
        />
        <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
          <p className="cthdrl-mono text-lg text-[#E6E1D5]">NO RESULTS DISPLAYED YET</p>
          <p className="text-xs font-mono text-[rgba(230,225,213,0.7)] mt-2 max-w-md">
            Enter a query in the Search Console to execute multimodal retrieval and view score provenance.
          </p>
          <button onClick={() => onNavigate(1)} className="cthdrl-link-btn mt-6">
            GO TO SEARCH CONSOLE ⮡
          </button>
        </div>
      </div>
    );
  }

  const alpha = data.intent.alpha;
  const transcript = (activeItem.payload.transcribed_text as string) ?? "";
  const videoId = (activeItem.payload.video_id as string) ?? "N/A";
  const timestamp = formatTimestamp((activeItem.payload.timestamp as number) ?? 0);

  return (
    <div className={`page-view ${isActive ? "page-view-active" : "page-view-hidden"}`}>
      <Header
        tickerText={`SEARCH RESULTS // ${data.total_results} MATCHES FOR "${data.query}" (${data.latency_ms}ms)`}
        pageIndex={2}
        onNavigate={onNavigate}
      />

      <div className="flex-1 relative flex flex-col justify-between p-6 md:p-10 overflow-hidden">
        <WireframeArcs variant="gallery" />

        {/* Summary Bar */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 z-10 pb-3 border-b border-[rgba(230,225,213,0.2)]">
          <div>
            <div className="flex items-center gap-3">
              <span className="cthdrl-mono text-xs text-[var(--accent-cyan)]">RESULTS REEL</span>
              <span className="text-xs font-mono text-[#E6E1D5]">
                QUERY: &quot;<strong>{data.query}</strong>&quot;
              </span>
            </div>
            <p className="cthdrl-mono text-[11px] mt-1 text-[#E6E1D5]">
              INTENT: {data.intent.intent_label} (α = {alpha.toFixed(2)}) • {data.total_results} RESULTS IN {data.latency_ms}ms
            </p>
          </div>

          <div className="flex items-center gap-4">
            <span className="cthdrl-mono text-sm font-mono text-[var(--accent-cyan)]">PAGE 3 OF 3</span>
            <button
              onClick={() => onNavigate(1)}
              className="px-3 py-1.5 bg-white/10 hover:bg-white/20 wire-all text-xs font-mono text-[#E6E1D5] transition-colors"
            >
              NEW SEARCH ⮡
            </button>
          </div>
        </div>

        {/* SOTA LINEAR STORYTELLING CONTAINER (PAGE 3) */}
        <div className="z-10 flex-1 overflow-y-auto max-h-[calc(100vh-210px)] pr-2 space-y-10 my-3">
          
          {/* ============================================================
             SECTION 1: TOP NON-TECHNICAL XAI SUMMARY (HIGH-IMPACT HEADER)
             ============================================================ */}
          <div className="w-full bg-[#121212]/95 border-2 border-[var(--accent-cyan)]/50 backdrop-blur-xl p-8 md:p-10 rounded-2xl shadow-2xl space-y-4">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-white/15 pb-4 gap-2">
              <span className="font-mono text-xs md:text-sm font-extrabold text-[var(--accent-cyan)] tracking-widest uppercase">
                NON-TECHNICAL SUMMARY // WHY THIS MATCHED
              </span>
              <span className="text-xs font-mono px-3 py-1.5 bg-emerald-950 text-[var(--accent-cyan)] rounded-lg font-bold border border-emerald-500/40">
                SOTA MULTIMODAL EXPLANATION
              </span>
            </div>

            <p className="text-lg sm:text-xl md:text-2xl font-sans font-semibold leading-relaxed text-[#E6E1D5]">
              {activeItem.visual_score > activeItem.audio_score ? (
                <>
                  This video matched your search for &quot;<strong className="text-white underline decoration-white/50">{data.query}</strong>&quot; primarily because of the <strong className="text-[var(--accent-cyan)] font-extrabold">visual scene contents</strong> shown at timestamp <strong>{timestamp}</strong>. The AI visual recognition model identified keyframe elements matching your query with a <strong className="text-[var(--accent-cyan)] font-extrabold">{activeItem.xai.visual_similarity_pct.toFixed(1)}% visual similarity</strong> score.
                </>
              ) : activeItem.audio_score > activeItem.visual_score ? (
                <>
                  This video matched your search for &quot;<strong className="text-white underline decoration-white/50">{data.query}</strong>&quot; primarily because of the <strong className="text-white font-extrabold">spoken audio transcript</strong> spoken at timestamp <strong>{timestamp}</strong>. The speech recognition model detected spoken words matching your query with a <strong className="text-white font-extrabold">{activeItem.xai.audio_similarity_pct.toFixed(1)}% audio similarity</strong> score.
                </>
              ) : (
                <>
                  This video matched your search for &quot;<strong className="text-white underline decoration-white/50">{data.query}</strong>&quot; through a balanced combination of <strong className="text-[var(--accent-cyan)] font-extrabold">visual keyframe scene matching ({activeItem.xai.visual_similarity_pct.toFixed(1)}%)</strong> and <strong className="text-white font-extrabold">spoken dialogue audio matching ({activeItem.xai.audio_similarity_pct.toFixed(1)}%)</strong> at timestamp <strong>{timestamp}</strong>.
                </>
              )}
            </p>
          </div>

          {/* ============================================================
             SECTION 2: "HERE ARE THE TOP 5 FRAMES" (SPACIOUS SCROLLABLE REEL)
             ============================================================ */}
          <div className="space-y-6">
            <div className="flex justify-between items-center border-b border-white/15 pb-3">
              <h3 className="font-mono text-xl sm:text-2xl md:text-3xl font-black text-white uppercase tracking-wider flex items-center gap-3">
                <span className="text-[var(--accent-cyan)]">✦</span> HERE ARE THE TOP 5 FRAMES
              </h3>
              <span className="text-xs font-mono text-gray-400 font-bold">
                SCROLL DOWN TO INSPECT EACH KEYFRAME
              </span>
            </div>

            <div className="space-y-8">
              {data.results.slice(0, 5).map((r, idx) => {
                const isSelected = idx === selectedIndex;
                const isVisualDriver = r.visual_score >= r.audio_score;
                return (
                  <div
                    key={String(r.id)}
                    onClick={() => setSelectedIndex(idx)}
                    className={`w-full bg-[#0c0c0c]/90 p-6 sm:p-8 wire-all cursor-pointer transition-all duration-300 rounded-2xl border-2 space-y-4 group ${
                      isSelected
                        ? "border-[var(--accent-cyan)] shadow-2xl shadow-emerald-950/80 bg-[#161616]"
                        : "border-white/15 hover:border-white/40"
                    }`}
                  >
                    {/* Header */}
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-white/10 pb-3">
                      <div className="flex items-center gap-3">
                        <span className="font-mono text-lg font-black text-[var(--accent-cyan)] px-3 py-1 bg-emerald-950/80 rounded-lg border border-emerald-500/40">
                          FRAME #{r.rank}
                        </span>
                        <span className="font-mono text-sm font-bold text-white">
                          VIDEO: {(r.payload.video_id as string)}
                        </span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="font-mono text-xs text-gray-300">
                          DRIVER: <strong className="text-[var(--accent-cyan)] font-extrabold">[{isVisualDriver ? "VISUAL SCENE" : "AUDIO TRANSCRIPT"}]</strong>
                        </span>
                        <span className="font-mono text-lg font-black text-[var(--accent-cyan)]">
                          {r.xai.fused_score_pct.toFixed(1)}% MATCH
                        </span>
                      </div>
                    </div>

                    {/* BIG SOTA KEYFRAME IMAGE */}
                    <div className="w-full h-64 sm:h-96 md:h-[480px] bg-black overflow-hidden relative rounded-xl border border-white/20 shadow-2xl group-hover:border-[var(--accent-cyan)]/70 transition-all">
                      {r.payload.frame_path ? (
                        <img
                          src={staticFrameUrl(r.payload.frame_path as string)}
                          alt={`Top Frame #${r.rank}`}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-sm font-mono text-[#E6E1D5]">
                          NO FRAME PREVIEW AVAILABLE
                        </div>
                      )}

                      {/* Overlay Badges */}
                      <div className="absolute top-4 left-4 px-4 py-2 bg-black/85 backdrop-blur-md border border-white/20 rounded-lg font-mono text-xs font-bold text-white shadow">
                        RANK #{r.rank} KEYFRAME
                      </div>
                      <div className="absolute bottom-4 right-4 px-4 py-2 bg-black/85 backdrop-blur-md border border-[var(--accent-cyan)]/50 rounded-lg font-mono text-sm font-extrabold text-[var(--accent-cyan)] shadow">
                        TIMESTAMP: {formatTimestamp((r.payload.timestamp as number) ?? 0)}
                      </div>
                    </div>

                    {/* Footer Score Breakdown */}
                    <div className="flex justify-between items-center pt-2 font-mono text-xs sm:text-sm font-bold">
                      <span className="text-[var(--accent-cyan)]">VISUAL CLIP SIMILARITY: {r.xai.visual_similarity_pct.toFixed(1)}%</span>
                      <span className="text-white">AUDIO WHISPER SIMILARITY: {r.xai.audio_similarity_pct.toFixed(1)}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* ============================================================
             SECTION 3: THE VIDEO CLIP FOUND & SYNCED VIDEO PLAYER CONTROLS
             ============================================================ */}
          <div className="w-full bg-[#0c0c0c]/95 border-2 border-white/20 p-8 md:p-10 rounded-2xl shadow-2xl space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-white/15 pb-4 gap-2">
              <div>
                <span className="font-mono text-xs text-[var(--accent-cyan)] font-bold tracking-widest uppercase block mb-1">
                  ACOUSTIC SPEECH RETRIEVAL & VIDEO PLAYER SYNC
                </span>
                <h3 className="font-mono text-xl sm:text-2xl font-black text-white uppercase tracking-tight">
                  FOUND VIDEO CLIP // PLAYBACK CONTROL SYNC ({timestamp})
                </h3>
              </div>
            </div>

            {/* Embedded Synced HTML5 Video Player */}
            <div className="space-y-4">
              <div className="w-full bg-black rounded-xl overflow-hidden border border-white/20 shadow-2xl relative">
                <video
                  ref={videoRef}
                  controls
                  className="w-full max-h-[420px] object-contain"
                  src={staticVideoUrl(
                    (activeItem.payload.file_name as string) ||
                    "Steve Jobs Interview Feb 18 1981.mp4"
                  )}
                />
              </div>
              <div className="flex flex-wrap items-center justify-between gap-4 font-mono text-xs bg-black/80 p-4 rounded-xl border border-white/10">
                <span className="text-gray-300">
                  CURRENT MATCH TIMESTAMP: <strong className="text-[var(--accent-cyan)]">{timestamp} ({activeItem.payload.timestamp ? Number(activeItem.payload.timestamp).toFixed(1) : "0.0"}s)</strong>
                </span>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => handleSeekToTimestamp(Number(activeItem.payload.timestamp) || 0)}
                    className="px-4 py-2 bg-[var(--accent-cyan)] text-black font-extrabold rounded-lg hover:bg-emerald-300 transition-all cursor-pointer"
                  >
                    ▶ JUMP TO TIMESTAMP {timestamp}
                  </button>
                  {activeItem.payload.video_path && (
                    <a
                      href={staticVideoUrl(activeItem.payload.video_path as string)}
                      target="_blank"
                      rel="noreferrer"
                      className="px-4 py-2 bg-white/10 text-white font-bold rounded-lg hover:bg-white/20 transition-all border border-white/20"
                    >
                      OPEN MP4 ↗
                    </a>
                  )}
                </div>
              </div>
            </div>

            {transcript ? (
              <div className="p-6 bg-black/90 border border-white/15 rounded-xl space-y-3 font-mono">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block">
                  SPOKEN DIALOGUE TRANSCRIPT AT TIMESTAMP {timestamp}:
                </span>
                <p
                  className="text-base sm:text-lg leading-relaxed text-[#E6E1D5]"
                  dangerouslySetInnerHTML={{
                    __html: highlightKeywords(transcript, data.query),
                  }}
                />
              </div>
            ) : (
              <p className="text-sm font-mono text-gray-400">No acoustic dialogue transcript available for this keyframe segment.</p>
            )}
          </div>

          {/* ============================================================
             SECTION 4: TECHNICAL SUMMARY AND CALCULATIONS (TECH XAI)
             ============================================================ */}
          <div className="w-full bg-[#0c0c0c]/95 border-2 border-emerald-500/40 p-8 md:p-10 rounded-2xl shadow-2xl space-y-8 font-mono">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-white/15 pb-4 gap-2">
              <div>
                <span className="font-mono text-xs text-[var(--accent-cyan)] font-bold tracking-widest uppercase block mb-1">
                  MACHINE LEARNING PROVENANCE
                </span>
                <h3 className="font-mono text-xl sm:text-2xl font-black text-white uppercase tracking-tight">
                  TECHNICAL SUMMARY & CALCULATIONS // MATHEMATICAL LATE FUSION
                </h3>
              </div>
              <span className="text-xs font-mono px-3.5 py-1.5 bg-emerald-950 text-[var(--accent-cyan)] rounded-lg font-bold border border-emerald-500/50">
                ML TECH SPECS
              </span>
            </div>

            {/* Score Grid */}
            <div className="grid grid-cols-3 gap-6 text-center">
              <div className="p-5 bg-black/70 rounded-2xl border border-white/15">
                <p className="text-xs font-mono mb-1 text-gray-300 font-bold uppercase">FUSED SCORE</p>
                <p className="text-3xl sm:text-4xl font-black text-white">
                  {activeItem.xai.fused_score_pct.toFixed(1)}%
                </p>
                <p className="text-xs font-mono text-gray-400 mt-2">({activeItem.fused_score.toFixed(4)})</p>
              </div>
              <div className="p-5 bg-black/70 rounded-2xl border-2 border-emerald-500/40">
                <p className="text-xs font-mono mb-1 text-[var(--accent-cyan)] font-bold uppercase">VISUAL (CLIP)</p>
                <p className="text-3xl sm:text-4xl font-black text-[var(--accent-cyan)]">
                  {activeItem.xai.visual_similarity_pct.toFixed(1)}%
                </p>
                <p className="text-xs font-mono text-gray-400 mt-2">({activeItem.visual_score.toFixed(4)})</p>
              </div>
              <div className="p-5 bg-black/70 rounded-2xl border border-white/15">
                <p className="text-xs font-mono mb-1 text-gray-300 font-bold uppercase">AUDIO (WHISPER)</p>
                <p className="text-3xl sm:text-4xl font-black text-white">
                  {activeItem.xai.audio_similarity_pct.toFixed(1)}%
                </p>
                <p className="text-xs font-mono text-gray-400 mt-2">({activeItem.audio_score.toFixed(4)})</p>
              </div>
            </div>

            {/* Late Fusion Formula & Calculation */}
            <div className="p-6 bg-white/5 border border-white/10 rounded-2xl space-y-4">
              <p className="text-base font-bold text-gray-300">
                FORMULA: <span className="text-white">Fused_Score = (α · S_visual) + ((1 - α) · S_audio)</span>
              </p>
              <div className="p-4 bg-black/80 rounded-xl space-y-2 text-base text-[#E6E1D5]">
                <div>
                  <span className="text-gray-400">EXACT CALCULATION: </span>
                  <span className="text-[var(--accent-cyan)] font-extrabold">
                    ({alpha.toFixed(2)} × {activeItem.visual_score.toFixed(4)}) + ({(1 - alpha).toFixed(2)} × {activeItem.audio_score.toFixed(4)})
                  </span>
                </div>
                <div className="text-lg sm:text-xl font-black text-white pt-2 border-t border-white/10 flex justify-between items-center">
                  <span>RESULTING FUSED SCORE:</span>
                  <span className="text-[var(--accent-cyan)]">{activeItem.fused_score.toFixed(6)} → {activeItem.xai.fused_score_pct.toFixed(1)}%</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs sm:text-sm text-gray-300 pt-3 border-t border-white/10">
              <div>
                <span className="text-[var(--accent-cyan)] font-bold">VISUAL EMBEDDING ARCHITECTURE:</span> CLIP ViT-B/32 (512-dim cosine similarity)
              </div>
              <div>
                <span className="text-white font-bold">AUDIO EMBEDDING ARCHITECTURE:</span> Whisper Base (512-dim cosine similarity)
              </div>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="grid grid-cols-12 gap-6 z-10 border-t border-[rgba(230,225,213,0.25)] pt-3">
          <div className="col-span-6">
            <p className="cthdrl-mono text-xs text-[#E6E1D5]">
              CLICK ANY CARD ON THE REEL TO EXAMINE EXACT LATE FUSION MATH
            </p>
          </div>
          <div className="col-span-6 text-right">
            <p className="cthdrl-mono text-xs text-[var(--accent-cyan)]">PAGE 3 OF 3</p>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   MAIN APP ORCHESTRATOR — ISOLATED 3-PAGE CONTROLLER
   ================================================================ */

export default function Home() {
  const [currentPage, setCurrentPage] = useState(0);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [corpusStats, setCorpusStats] = useState<CorpusStats | null>(null);
  const [searchData, setSearchData] = useState<SearchResponse | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch((err) => {
      console.warn("Health check error:", err);
    });
    fetchCorpusStats().then(setCorpusStats).catch((err) => {
      console.warn("Corpus stats error:", err);
    });
  }, []);

  const navigateToPage = useCallback((pageIndex: number) => {
    setCurrentPage(pageIndex);
  }, []);

  const handleSearch = useCallback(
    async (query: string) => {
      setIsSearching(true);
      setSearchError(null);
      setCurrentPage(2); // Switch to Results Page immediately

      try {
        const data = await fetchSearch(query, 5);
        setSearchData(data);
      } catch (err: any) {
        console.error("Search error:", err);
        setSearchError(err?.message || "Failed to connect to backend server");
        setCurrentPage(1); // Return to terminal on error
      } finally {
        setIsSearching(false);
      }
    },
    []
  );

  // Keyboard Arrow Navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.key === "ArrowRight" && currentPage < 2) {
        setCurrentPage((prev) => Math.min(2, prev + 1));
      } else if (e.key === "ArrowLeft" && currentPage > 0) {
        setCurrentPage((prev) => Math.max(0, prev - 1));
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [currentPage]);

  return (
    <main className="page-container">
      <PageFrontPage
        isActive={currentPage === 0}
        onNavigate={navigateToPage}
        health={health}
        corpusStats={corpusStats}
      />
      <PageTerminal
        isActive={currentPage === 1}
        onNavigate={navigateToPage}
        onSearch={handleSearch}
        isSearching={isSearching}
        searchError={searchError}
        corpusStats={corpusStats}
      />
      <PageGalleryAndXAI
        isActive={currentPage === 2}
        onNavigate={navigateToPage}
        data={searchData}
        isSearching={isSearching}
      />

      {/* Floating Bottom Navigation Bar */}
      <nav className="fixed bottom-6 right-10 z-50 flex items-center gap-3 bg-black/80 px-4 py-2 wire-all rounded-full backdrop-blur-md shadow-xl border border-[rgba(230,225,213,0.3)]">
        {["1. FRONT PAGE", "2. SEARCH CONSOLE", "3. RESULTS & XAI"].map((label, i) => (
          <button
            key={i}
            title={label}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full transition-all ${
              currentPage === i
                ? "bg-[var(--accent-cyan)] text-black font-bold text-xs shadow-md shadow-emerald-950"
                : "text-[rgba(230,225,213,0.6)] hover:text-[#E6E1D5] text-[11px] font-mono"
            }`}
            onClick={() => navigateToPage(i)}
          >
            <span
              className={`w-2.5 h-2.5 rounded-full transition-all ${
                currentPage === i ? "bg-black" : "bg-[rgba(230,225,213,0.4)]"
              }`}
            />
            <span>{label}</span>
          </button>
        ))}
      </nav>
    </main>
  );
}

/* ================================================================
   HELPERS
   ================================================================ */

function formatTimestamp(seconds: number): string {
  const total = Math.round(seconds);
  const mins = Math.floor(total / 60);
  const secs = total % 60;
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

const STOP_WORDS = new Set([
  "the", "and", "a", "an", "in", "on", "at", "to", "for", "of", "with",
  "by", "from", "up", "about", "into", "over", "after", "is", "are", "was",
  "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
  "but", "or", "so", "if", "out", "no", "not", "only", "own", "same", "that",
  "this", "these", "those", "then", "there", "when", "where", "why", "how",
]);

function highlightKeywords(text: string, query: string): string {
  const tokens = query
    .toLowerCase()
    .split(/\W+/)
    .filter((w) => w.length >= 3 && !STOP_WORDS.has(w))
    .map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));

  if (!tokens.length) return text;

  const pattern = new RegExp(`\\b(${tokens.join("|")})\\b`, "gi");
  return text.replace(pattern, '<mark class="transcript-mark">$1</mark>');
}
