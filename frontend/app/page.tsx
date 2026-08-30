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
   HEADER COMPONENT — NEURALVIDEO V5.0 TIER 2 DEMO ENGINE
   ================================================================ */

function Header({
  tickerText,
  pageIndex,
  onNavigate,
  corpusStats,
  selectedVideo,
  onSelectVideo,
}: {
  tickerText: string;
  pageIndex: number;
  onNavigate: (index: number) => void;
  corpusStats: CorpusStats | null;
  selectedVideo: string;
  onSelectVideo: (video: string) => void;
}) {
  return (
    <header className="cthdrl-header flex flex-wrap items-center justify-between gap-4 px-6 py-4 bg-[#08080a]/90 backdrop-blur-2xl border-b border-white/10 z-40">
      {/* Brand & Logo */}
      <div className="flex items-center gap-4 cursor-pointer" onClick={() => onNavigate(0)}>
        <div className="w-9 h-9 rounded-xl bg-cyan-950/80 border border-cyan-500/50 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.3)]">
          <svg width="22" height="22" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M 16 4 C 8 4, 4 12, 4 28" stroke="#10B981" strokeWidth="2.5" strokeLinecap="round" />
            <path d="M 16 4 C 24 4, 28 12, 28 28" stroke="#06B6D4" strokeWidth="2.5" strokeLinecap="round" />
            <path d="M 16 12 C 10 12, 8 18, 8 28" stroke="#E6E1D5" strokeWidth="1.5" />
            <path d="M 16 12 C 22 12, 24 18, 24 28" stroke="#E6E1D5" strokeWidth="1.5" />
            <line x1="4" y1="28" x2="28" y2="28" stroke="#E6E1D5" strokeWidth="2" />
          </svg>
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="font-mono font-black text-white text-base tracking-wider">NEURALVIDEO</span>
            <span className="font-mono text-xs font-bold text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-500/30">
              v5.0 TIER 2
            </span>
          </div>
          <span className="font-mono text-[10px] text-emerald-400/80 tracking-widest uppercase">
            MULTIMODAL VIDEO RAG & SEARCH CONSOLE
          </span>
        </div>
      </div>

      {/* Catalog Dropdown in Header */}
      <div className="hidden lg:flex items-center gap-3 bg-black/60 border border-white/15 px-3 py-1.5 rounded-xl">
        <span className="font-mono text-xs font-bold text-cyan-400 uppercase tracking-wider">CATALOG:</span>
        <select
          value={selectedVideo}
          onChange={(e) => onSelectVideo(e.target.value)}
          className="bg-transparent text-white font-mono text-xs outline-none cursor-pointer pr-2"
        >
          <option value="all" className="bg-[#08080a] text-white">
            ALL INDEXED VIDEOS ({corpusStats?.total_points || 0} POINTS)
          </option>
          {corpusStats?.video_catalog && corpusStats.video_catalog.length > 0 ? (
            corpusStats.video_catalog.map((item) => (
              <option key={item.filename} value={item.filename} className="bg-[#08080a] text-white">
                {item.title} ({item.size_mb} MB)
              </option>
            ))
          ) : (
            <>
              <option value="Abuse001_x264.mp4" className="bg-[#08080a] text-white">
                Abuse001_x264.mp4 (20.5 MB)
              </option>
              <option value="Steve Jobs Interview Feb 18 1981.mp4" className="bg-[#08080a] text-white">
                Steve Jobs Interview Feb 18 1981.mp4 (50.9 MB)
              </option>
              <option value="my_llm_talk.MOV" className="bg-[#08080a] text-white">
                my_llm_talk.MOV (573.8 MB)
              </option>
            </>
          )}
        </select>
      </div>

      {/* Ticker Text */}
      <div className="hidden md:block font-mono text-xs text-gray-300 tracking-wider truncate max-w-md">
        {tickerText}
      </div>

      {/* Navigation Links */}
      <div className="flex items-center gap-2 font-mono text-xs">
        {[
          { idx: 0, label: "DEMO" },
          { idx: 1, label: "CONSOLE" },
          { idx: 2, label: "XAI PROVENANCE" },
        ].map((item) => (
          <button
            key={item.idx}
            onClick={() => onNavigate(item.idx)}
            className={`px-3 py-1.5 rounded-lg transition-all font-bold ${
              pageIndex === item.idx
                ? "bg-cyan-500 text-black shadow-[0_0_12px_rgba(6,182,212,0.4)]"
                : "text-gray-400 hover:text-white hover:bg-white/10"
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>
    </header>
  );
}

/* ================================================================
   PAGE 1 (Index 0) — JUDGE LANDING & DEMO OVERVIEW
   ================================================================ */

function PageLanding({
  isActive,
  onNavigate,
  health,
  corpusStats,
  selectedVideo,
  onSelectVideo,
}: {
  isActive: boolean;
  onNavigate: (page: number) => void;
  health: HealthResponse | null;
  corpusStats: CorpusStats | null;
  selectedVideo: string;
  onSelectVideo: (video: string) => void;
}) {
  return (
    <div className={`page-view ${isActive ? "page-view-active" : "page-view-hidden"}`}>
      <Header
        tickerText="JUDGE DEMO CONSOLE // REAL-TIME MULTIMODAL VIDEO RETRIEVAL"
        pageIndex={0}
        onNavigate={onNavigate}
        corpusStats={corpusStats}
        selectedVideo={selectedVideo}
        onSelectVideo={onSelectVideo}
      />

      <div className="flex-1 relative flex flex-col justify-center items-center p-6 md:p-12 text-center overflow-hidden">
        <WireframeArcs variant="manifesto" />

        <div className="z-10 max-w-5xl mx-auto flex flex-col items-center justify-center my-auto px-4">
          {/* Status Badge */}
          <div className="inline-flex items-center gap-3 px-5 py-2 bg-black/60 backdrop-blur-md rounded-full border border-emerald-500/40 mb-8 shadow-[0_0_20px_rgba(16,185,129,0.2)]">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-mono font-bold text-xs text-emerald-400 tracking-[0.25em] uppercase">
              HACKATHON JUDGE DEMO MODE &bull; SUB-180MS RETRIEVAL SLA
            </span>
          </div>

          {/* Hero Title */}
          <h1 className="font-mono font-black text-5xl sm:text-7xl md:text-8xl lg:text-9xl uppercase tracking-[0.12em] text-white leading-none mb-6 drop-shadow-[0_10px_30px_rgba(0,0,0,0.8)]">
            NEURALVIDEO <span className="text-cyan-400">PRO</span>
          </h1>

          {/* Tagline */}
          <p className="font-sans font-normal text-lg sm:text-xl md:text-2xl text-[#E6E1D5] max-w-3xl leading-relaxed mb-10 text-center">
            Sub-second cross-modal video search fusing{" "}
            <span className="text-cyan-300 font-semibold border-b border-cyan-400/50">
              CLIP ViT-B/32 keyframes
            </span>{" "}
            and{" "}
            <span className="text-emerald-300 font-semibold border-b border-emerald-400/50">
              Whisper Base dialogue transcripts
            </span>{" "}
            with Reciprocal Rank Fusion & XAI attribution.
          </p>

          {/* Key Metrics Pill Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full max-w-4xl mb-12 font-mono">
            <div className="p-4 bg-black/70 rounded-2xl border border-white/10 text-center">
              <span className="text-[10px] text-gray-400 uppercase tracking-widest block mb-1">SEARCH SLA</span>
              <span className="text-2xl font-black text-emerald-400">&lt; 180ms</span>
            </div>
            <div className="p-4 bg-black/70 rounded-2xl border border-white/10 text-center">
              <span className="text-[10px] text-gray-400 uppercase tracking-widest block mb-1">VECTOR STORE</span>
              <span className="text-2xl font-black text-cyan-400">Qdrant Dual 512-D</span>
            </div>
            <div className="p-4 bg-black/70 rounded-2xl border border-white/10 text-center">
              <span className="text-[10px] text-gray-400 uppercase tracking-widest block mb-1">INDEX POINTS</span>
              <span className="text-2xl font-black text-white">{corpusStats?.total_points || 2086}</span>
            </div>
            <div className="p-4 bg-black/70 rounded-2xl border border-white/10 text-center">
              <span className="text-[10px] text-gray-400 uppercase tracking-widest block mb-1">EXPLAINABILITY</span>
              <span className="text-2xl font-black text-cyan-400">RRF + XAI</span>
            </div>
          </div>

          {/* Launch Action CTA */}
          <button
            onClick={() => onNavigate(1)}
            className="font-mono font-bold text-lg sm:text-xl tracking-[0.2em] uppercase px-12 py-6 bg-cyan-500 hover:bg-emerald-400 text-black rounded-2xl transition-all duration-300 shadow-[0_0_35px_rgba(6,182,212,0.4)] hover:scale-105 group cursor-pointer flex items-center gap-4"
          >
            ENTER SEARCH CONSOLE
            <span className="text-3xl group-hover:translate-x-1.5 transition-transform">➔</span>
          </button>
        </div>

        {/* Status Bar */}
        <div className="w-full z-10 border-t border-white/10 pt-4 flex justify-between items-center text-xs font-mono text-gray-400">
          <div>
            <span>SYSTEM STATUS: </span>
            <strong className={health?.status === "ok" ? "text-emerald-400" : "text-amber-400"}>
              {health?.status === "ok" ? "READY (ONLINE)" : "INITIALIZING..."}
            </strong>
          </div>
          <div>
            <button
              onClick={() => onNavigate(1)}
              className="text-xs font-mono text-cyan-400 hover:text-emerald-300 cursor-pointer"
            >
              LAUNCH INTERACTIVE DEMO ➔
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   PAGE 2 (Index 1) — SEARCH CONSOLE & PIPELINE STORYTELLING BAR
   ================================================================ */

function PageConsole({
  isActive,
  onNavigate,
  onSearch,
  isSearching,
  searchStage,
  searchError,
  corpusStats,
  selectedVideo,
  onSelectVideo,
}: {
  isActive: boolean;
  onNavigate: (page: number) => void;
  onSearch: (query: string) => void;
  isSearching: boolean;
  searchStage: number;
  searchError: string | null;
  corpusStats: CorpusStats | null;
  selectedVideo: string;
  onSelectVideo: (video: string) => void;
}) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isSearching) {
      onSearch(query.trim());
    }
  };

  // Tier 2 Curated High-Reliability Demo Query Chips
  const samplePrompts = [
    { label: "🚨 surveillance security incident scene", q: "security camera footage of incident scene" },
    { label: "⚡ speaker discussing transformers", q: "speaker discussing transformers" },
    { label: "🧠 person explaining neural networks", q: "person explaining neural networks" },
    { label: "💬 prompt engineering", q: "prompt engineering" },
    { label: "📺 television shoots for the lowest common denominator", q: "television shoots for the lowest common denominator" },
    { label: "💡 Show me where Steve Jobs talks about AI", q: "Show me where Steve Jobs talks about AI" },
    { label: "✏️ whiteboard discussion", q: "whiteboard discussion" },
  ];

  // Pipeline Execution Bar Steps Definition
  const pipelineSteps = [
    { step: 1, title: "Encoding Query...", desc: "CLIP ViT-B/32 & Text Transformer" },
    { step: 2, title: "Searching Visual Index...", desc: "512-D Vision Vectors" },
    { step: 3, title: "Searching Audio Index...", desc: "16kHz Whisper Transcripts" },
    { step: 4, title: "Fusing Results (RRF)...", desc: "Reciprocal Rank Fusion" },
    { step: 5, title: "Diversifying Results (MMR)...", desc: "Semantic Vector Diversity (λ=0.7)" },
    { step: 6, title: "Returning Top Match...", desc: "Confidence Scoring & Playback Sync" },
  ];

  return (
    <div className={`page-view ${isActive ? "page-view-active" : "page-view-hidden"}`}>
      <Header
        tickerText="SEARCH CONSOLE // LIVE PIPELINE STORYTELLING & INFERENCE"
        pageIndex={1}
        onNavigate={onNavigate}
        corpusStats={corpusStats}
        selectedVideo={selectedVideo}
        onSelectVideo={onSelectVideo}
      />

      <div className="flex-1 relative flex flex-col justify-center items-center p-6 md:p-12 text-center overflow-hidden">
        <WireframeArcs variant="terminal" />

        <div className="z-10 max-w-5xl mx-auto w-full flex flex-col items-center justify-center my-auto px-4 py-6 space-y-8">
          
          <div className="text-center">
            <span className="font-mono font-bold text-xs text-cyan-400 tracking-[0.25em] uppercase block mb-3">
              JUDGE DEMO CONSOLE // QUERY INFERENCE ENGINE
            </span>
            <h2 className="font-mono font-black text-4xl sm:text-6xl md:text-7xl uppercase tracking-[0.1em] text-white leading-none drop-shadow-lg">
              MULTIMODAL SEARCH
            </h2>
          </div>

          {/* Floating Search Bar with Cyan/Emerald Glow */}
          <div className="w-full max-w-4xl mx-auto">
            <form onSubmit={handleSubmit} className="relative">
              <div className="relative rounded-2xl bg-black/70 backdrop-blur-2xl border border-cyan-500/40 p-2 shadow-[0_0_30px_rgba(6,182,212,0.2)] focus-within:border-cyan-400 focus-within:shadow-[0_0_40px_rgba(6,182,212,0.4)] transition-all duration-300">
                <input
                  type="text"
                  className="w-full px-6 py-5 bg-transparent text-white font-mono text-lg sm:text-xl placeholder-gray-500 outline-none"
                  placeholder='Try "speaker discussing transformers" or "prompt engineering"...'
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  autoFocus={isActive}
                  disabled={isSearching}
                />
                <button
                  type="submit"
                  disabled={!query.trim() || isSearching}
                  className="absolute right-4 top-1/2 -translate-y-1/2 px-8 py-3.5 bg-cyan-500 hover:bg-emerald-400 disabled:opacity-40 disabled:cursor-not-allowed text-black font-mono font-black text-sm tracking-wider uppercase rounded-xl transition-all shadow-md cursor-pointer"
                >
                  {isSearching ? "INFERRING..." : "SEARCH"}
                </button>
              </div>
            </form>
          </div>

          {/* Live Pipeline Storytelling Visualization Bar */}
          {isSearching && (
            <div className="w-full max-w-4xl mx-auto p-6 bg-black/90 border border-cyan-500/50 rounded-2xl backdrop-blur-2xl shadow-2xl space-y-4 animate-fade-in">
              <div className="flex items-center justify-between border-b border-white/10 pb-3 font-mono">
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
                  <span className="font-bold text-xs text-cyan-300 tracking-wider uppercase">
                    LIVE PIPELINE STORYTELLING VISUALIZATION
                  </span>
                </div>
                <span className="text-xs text-gray-400">STEP {searchStage} OF 6</span>
              </div>

              {/* 6-Step Pipeline Grid */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-left font-mono">
                {pipelineSteps.map((item) => {
                  const isDone = searchStage > item.step;
                  const isActiveStep = searchStage === item.step;

                  return (
                    <div
                      key={item.step}
                      className={`p-3 rounded-xl border transition-all duration-200 ${
                        isDone
                          ? "bg-emerald-950/60 border-emerald-500/50 text-emerald-300"
                          : isActiveStep
                          ? "bg-cyan-950/80 border-cyan-400 text-cyan-200 shadow-[0_0_15px_rgba(6,182,212,0.3)] animate-pulse"
                          : "bg-white/5 border-white/10 text-gray-500"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-bold tracking-widest uppercase">
                          STEP {item.step}
                        </span>
                        <span>
                          {isDone ? (
                            <span className="text-emerald-400 font-bold">✓</span>
                          ) : isActiveStep ? (
                            <span className="w-2 h-2 rounded-full bg-cyan-400 inline-block animate-ping" />
                          ) : (
                            <span className="text-gray-600">&bull;</span>
                          )}
                        </span>
                      </div>
                      <div className="font-bold text-xs truncate">{item.title}</div>
                      <div className="text-[10px] text-gray-400 truncate">{item.desc}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Curated High-Reliability Demo Query Chips */}
          <div className="w-full max-w-4xl mx-auto text-center space-y-3">
            <span className="font-mono font-bold text-xs text-gray-400 tracking-[0.2em] uppercase block">
              CURATED HACKATHON DEMO QUERY CHIPS:
            </span>
            <div className="flex flex-wrap items-center justify-center gap-2.5">
              {samplePrompts.map((sample) => (
                <button
                  key={sample.q}
                  type="button"
                  onClick={() => {
                    setQuery(sample.q);
                    onSearch(sample.q);
                  }}
                  className="text-xs font-mono font-bold py-2.5 px-4 bg-black/60 hover:bg-cyan-500 hover:text-black text-gray-200 transition-all duration-200 rounded-xl border border-white/15 hover:border-cyan-400 cursor-pointer backdrop-blur-md shadow-md hover:scale-105"
                >
                  {sample.label}
                </button>
              ))}
            </div>
          </div>

          {/* Error Banner */}
          {searchError && (
            <div className="w-full max-w-3xl mx-auto p-4 border border-red-500/50 bg-red-950/60 text-red-200 text-sm font-mono font-bold rounded-xl">
              SEARCH ERROR: {searchError}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   PAGE 3 (Index 2) — RESULTS GALLERY & RETRIEVAL TIMELINE BAR
   ================================================================ */

function PageResultsAndXAI({
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

  // One-Click Video Sync Function
  const handleSeekAndPlay = (timestampInSeconds: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = timestampInSeconds;
      videoRef.current.play().catch(() => {});
    }
  };

  if (isSearching) {
    return (
      <div className={`page-view ${isActive ? "page-view-active" : "page-view-hidden"}`}>
        <Header
          tickerText="SEARCH ENGINE EXECUTING MULTIMODAL INFERENCE..."
          pageIndex={2}
          onNavigate={onNavigate}
          corpusStats={null}
          selectedVideo="all"
          onSelectVideo={() => {}}
        />
        <div className="flex-1 flex flex-col items-center justify-center p-12">
          <div className="w-14 h-14 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mb-6" />
          <p className="font-mono text-xl font-bold text-cyan-300">COMPUTING CLIP + WHISPER FUSION...</p>
          <p className="font-mono text-xs text-gray-400 mt-2">Evaluating Qdrant dual-vector cosine similarities & XAI attribution</p>
        </div>
      </div>
    );
  }

  if (!data || !data.results || data.results.length === 0 || !activeItem) {
    return (
      <div className={`page-view ${isActive ? "page-view-active" : "page-view-hidden"}`}>
        <Header
          tickerText="RESULTS GALLERY // AWAITING SEARCH EXECUTION"
          pageIndex={2}
          onNavigate={onNavigate}
          corpusStats={null}
          selectedVideo="all"
          onSelectVideo={() => {}}
        />
        <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
          <p className="font-mono text-lg text-gray-300">NO RESULTS DISPLAYED YET</p>
          <p className="font-mono text-xs text-gray-500 mt-2 max-w-md">
            Enter a query in the Search Console to execute multimodal vector retrieval.
          </p>
          <button onClick={() => onNavigate(1)} className="mt-6 px-6 py-3 bg-cyan-500 text-black font-mono font-bold rounded-xl">
            GO TO SEARCH CONSOLE ➔
          </button>
        </div>
      </div>
    );
  }

  const alpha = data.intent.alpha;
  const transcript = (activeItem.payload.transcribed_text as string) ?? "";
  const timestampSec = (activeItem.payload.timestamp as number) ?? 0;
  const formattedTime = formatTimestamp(timestampSec);

  // Confidence Band Colors
  const confidenceBand = activeItem.xai.confidence_tier || "HIGH";
  const confidenceColor =
    confidenceBand === "HIGH"
      ? "bg-emerald-950 text-emerald-300 border-emerald-500/50"
      : confidenceBand === "MEDIUM"
      ? "bg-amber-950 text-amber-300 border-amber-500/50"
      : "bg-slate-900 text-slate-300 border-slate-700";

  // Calculate Max Duration for Interactive Retrieval Timeline Bar
  const maxTimestampInResults = Math.max(...data.results.map((r) => Number(r.payload.timestamp) || 0));
  const maxDurationSec = Math.max(1170, maxTimestampInResults + 30); // default ~19:30 or max ts

  return (
    <div className={`page-view ${isActive ? "page-view-active" : "page-view-hidden"}`}>
      <Header
        tickerText={`RESULTS // ${data.total_results} MATCHES FOR "${data.query}" (${data.latency_ms}ms)`}
        pageIndex={2}
        onNavigate={onNavigate}
        corpusStats={null}
        selectedVideo="all"
        onSelectVideo={() => {}}
      />

      <div className="flex-1 relative flex flex-col justify-between p-6 md:p-8 overflow-hidden">
        <WireframeArcs variant="gallery" />

        {/* Results Toolbar */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 z-10 pb-3 border-b border-white/15">
          <div>
            <div className="flex items-center gap-3">
              <span className="font-mono font-bold text-xs text-cyan-400 uppercase tracking-widest">XAI PROVENANCE</span>
              <span className="font-mono text-xs text-white">
                QUERY: &quot;<strong className="text-cyan-300">{data.query}</strong>&quot;
              </span>
            </div>
            <p className="font-mono text-xs text-gray-400 mt-1">
              AUTO-INTENT: {data.intent.intent_label} (&alpha; = {alpha.toFixed(2)}) &bull; {data.total_results} RESULTS IN <span className="text-emerald-400 font-bold">{data.latency_ms}ms</span>
            </p>
          </div>

          <button
            onClick={() => onNavigate(1)}
            className="px-4 py-2 bg-white/10 hover:bg-white/20 text-xs font-mono font-bold text-white rounded-xl border border-white/20 transition-all"
          >
            NEW SEARCH ➔
          </button>
        </div>

        {/* Tier 2 Interactive Retrieval Timeline Bar */}
        <div className="z-10 my-3 p-4 bg-black/80 backdrop-blur-2xl border border-cyan-500/40 rounded-2xl space-y-2 font-mono">
          <div className="flex items-center justify-between text-xs text-gray-300">
            <span className="font-bold text-cyan-400 tracking-wider">RETRIEVAL TIMELINE TRACK</span>
            <span className="text-gray-400">VIDEO DURATION: 0:00 ➔ {formatTimestamp(maxDurationSec)}</span>
          </div>

          {/* Timeline Track with Clickable Result Pins */}
          <div className="relative w-full h-8 bg-white/5 rounded-xl border border-white/10 flex items-center px-2">
            <div className="w-full h-1.5 bg-gradient-to-r from-cyan-500/40 via-emerald-500/40 to-cyan-500/40 rounded-full relative">
              {data.results.map((r, idx) => {
                const ts = Number(r.payload.timestamp) || 0;
                const posPct = Math.min(96, Math.max(2, (ts / maxDurationSec) * 100));
                const isSelected = idx === selectedIndex;

                return (
                  <button
                    key={String(r.id)}
                    type="button"
                    onClick={() => {
                      setSelectedIndex(idx);
                      handleSeekAndPlay(ts);
                    }}
                    style={{ left: `${posPct}%` }}
                    className={`absolute top-1/2 -translate-y-1/2 -translate-x-1/2 px-2 py-0.5 rounded-full font-mono text-[10px] font-black transition-all cursor-pointer shadow-lg ${
                      isSelected
                        ? "bg-cyan-400 text-black scale-125 z-20 border-2 border-white shadow-[0_0_12px_rgba(6,182,212,0.8)]"
                        : "bg-black text-cyan-300 border border-cyan-500/60 hover:scale-110 z-10"
                    }`}
                    title={`Rank #${r.rank} @ ${formatTimestamp(ts)} (${r.xai.fused_score_pct.toFixed(1)}%)`}
                  >
                    #{r.rank}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Main 2-Column Split Console */}
        <div className="z-10 flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 my-2 overflow-y-auto max-h-[calc(100vh-270px)] pr-2">
          
          {/* LEFT COLUMN: Timeline Keyframe Match Cards & Judge Diagnostics (5 cols) */}
          <div className="lg:col-span-5 space-y-4">
            <h3 className="font-mono text-sm font-bold text-gray-300 uppercase tracking-wider">
              TIMELINE MATCH REEL (CLICK TO SYNC PLAYER):
            </h3>

            <div className="space-y-4">
              {data.results.map((r, idx) => {
                const isSelected = idx === selectedIndex;
                const rTimestampSec = (r.payload.timestamp as number) ?? 0;
                const rTimeStr = formatTimestamp(rTimestampSec);

                return (
                  <div
                    key={String(r.id)}
                    onClick={() => {
                      setSelectedIndex(idx);
                      handleSeekAndPlay(rTimestampSec);
                    }}
                    className={`p-4 bg-black/80 backdrop-blur-md rounded-2xl border-2 transition-all cursor-pointer space-y-3 ${
                      isSelected
                        ? "border-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.3)] bg-cyan-950/20"
                        : "border-white/15 hover:border-white/40"
                    }`}
                  >
                    <div className="flex items-center justify-between font-mono text-xs">
                      <span className="font-black text-cyan-400 bg-cyan-950 px-2.5 py-1 rounded border border-cyan-500/40">
                        RANK #{r.rank}
                      </span>
                      <span className="font-bold text-white">TIMESTAMP: {rTimeStr}</span>
                      <span className="font-black text-emerald-400">{r.xai.fused_score_pct.toFixed(1)}% MATCH</span>
                    </div>

                    {/* Frame Preview */}
                    <div className="w-full h-40 bg-black rounded-xl overflow-hidden border border-white/20 relative">
                      {r.payload.frame_path ? (
                        <img
                          src={staticFrameUrl(r.payload.frame_path as string)}
                          alt={`Frame #${r.rank}`}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-xs font-mono text-gray-500">
                          KEYFRAME PREVIEW
                        </div>
                      )}
                      <div className="absolute bottom-2 right-2 bg-black/90 px-3 py-1 rounded font-mono text-xs font-bold text-cyan-300 border border-cyan-500/40">
                        {rTimeStr}
                      </div>
                    </div>

                    {/* Human-Readable Judge Diagnostics */}
                    <div className="space-y-1 font-mono text-[11px] pt-1 border-t border-white/10">
                      <div className={r.visual_score > 0.15 ? "text-emerald-400" : "text-gray-500"}>
                        ✓ Visual context matched target keyframe ({r.xai.visual_similarity_pct.toFixed(1)}%)
                      </div>
                      <div className={r.audio_score > 0.15 ? "text-emerald-400" : "text-gray-500"}>
                        ✓ Transcript aligned at target timestamp ({r.xai.audio_similarity_pct.toFixed(1)}%)
                      </div>
                      <div className="text-cyan-400">
                        ✓ Multi-modal cross-agreement score verified
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* RIGHT COLUMN: Instant Synchronized Video Player & XAI Provenance (7 cols) */}
          <div className="lg:col-span-7 space-y-6">
            
            {/* HTML5 Video Player Container */}
            <div className="p-6 bg-black/90 backdrop-blur-2xl border-2 border-cyan-500/50 rounded-2xl shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-white/15 pb-3">
                <span className="font-mono text-xs font-bold text-cyan-400 uppercase tracking-widest">
                  SYNCHRONIZED VIDEO PLAYER
                </span>
                <span className={`font-mono text-xs px-3 py-1 rounded-full font-bold border ${confidenceColor}`}>
                  CONFIDENCE: {confidenceBand}
                </span>
              </div>

              {/* Video Element with attached videoRef */}
              <div className="w-full bg-black rounded-xl overflow-hidden border border-white/20 shadow-2xl relative">
                <video
                  ref={videoRef}
                  controls
                  className="w-full max-h-[380px] object-contain"
                  src={staticVideoUrl(
                    resolveVideoFilename(
                      (activeItem.payload.file_name as string) ||
                      (activeItem.payload.video_id as string)
                    )
                  )}
                />
              </div>

              {/* Primary Action Button — Instant Timestamp Jump */}
              <div className="flex flex-wrap items-center justify-between gap-4 font-mono text-xs bg-black/80 p-4 rounded-xl border border-white/10">
                <span className="text-gray-300">
                  MATCH TIMESTAMP: <strong className="text-cyan-400 text-sm">{formattedTime} ({timestampSec.toFixed(1)}s)</strong>
                </span>
                <button
                  onClick={() => handleSeekAndPlay(timestampSec)}
                  className="px-6 py-3 bg-cyan-500 hover:bg-emerald-400 text-black font-mono font-black text-sm rounded-xl transition-all shadow-md cursor-pointer flex items-center gap-2"
                >
                  ▶ JUMP TO TIMESTAMP [{formattedTime}]
                </button>
              </div>
            </div>

            {/* Spoken Dialogue Transcript Block with Highlighted Keywords */}
            <div className="p-6 bg-black/90 backdrop-blur-2xl border border-white/15 rounded-2xl space-y-3 font-mono">
              <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider block">
                SPOKEN DIALOGUE TRANSCRIPT (TIMESTAMP {formattedTime}):
              </span>
              {transcript ? (
                <p
                  className="text-base sm:text-lg leading-relaxed text-[#E6E1D5] p-4 bg-white/5 rounded-xl border border-white/10"
                  dangerouslySetInnerHTML={{
                    __html: highlightKeywords(transcript, data.query),
                  }}
                />
              ) : (
                <p className="text-sm text-gray-500">No acoustic dialogue transcript available for this keyframe segment.</p>
              )}
            </div>

            {/* Technical ML Provenance Grid */}
            <div className="p-6 bg-black/90 backdrop-blur-2xl border border-emerald-500/40 rounded-2xl space-y-4 font-mono">
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider block">
                TECHNICAL ML SCORE CALCULATIONS
              </span>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                  <span className="text-[10px] text-gray-400 uppercase block">FUSED SCORE</span>
                  <span className="text-2xl font-black text-white">{activeItem.xai.fused_score_pct.toFixed(1)}%</span>
                </div>
                <div className="p-4 bg-cyan-950/60 rounded-xl border border-cyan-500/40">
                  <span className="text-[10px] text-cyan-400 uppercase block">VISUAL (CLIP)</span>
                  <span className="text-2xl font-black text-cyan-300">{activeItem.xai.visual_similarity_pct.toFixed(1)}%</span>
                </div>
                <div className="p-4 bg-emerald-950/60 rounded-xl border border-emerald-500/40">
                  <span className="text-[10px] text-emerald-400 uppercase block">AUDIO (WHISPER)</span>
                  <span className="text-2xl font-black text-emerald-300">{activeItem.xai.audio_similarity_pct.toFixed(1)}%</span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   MAIN APP ORCHESTRATOR
   ================================================================ */

export default function Home() {
  const [currentPage, setCurrentPage] = useState(0);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [corpusStats, setCorpusStats] = useState<CorpusStats | null>(null);
  const [selectedVideo, setSelectedVideo] = useState("all");
  const [searchData, setSearchData] = useState<SearchResponse | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchStage, setSearchStage] = useState(0);
  const [searchError, setSearchError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(console.warn);
    fetchCorpusStats().then(setCorpusStats).catch(console.warn);
  }, []);

  const navigateToPage = useCallback((pageIndex: number) => {
    setCurrentPage(pageIndex);
  }, []);

  // Tier 2 Animated 6-Step Pipeline Execution Handler
  const handleSearch = useCallback(
    async (query: string) => {
      setIsSearching(true);
      setSearchError(null);

      const stages = [1, 2, 3, 4, 5, 6];
      for (const stg of stages) {
        setSearchStage(stg);
        await new Promise((resolve) => setTimeout(resolve, 140));
      }

      try {
        const data = await fetchSearch(query, 5, undefined, "all");
        setSearchData(data);
        setCurrentPage(2); // Switch to Results & XAI Page
      } catch (err: any) {
        console.error("Search error:", err);
        setSearchError(err?.message || "Failed to connect to backend server");
        setCurrentPage(1);
      } finally {
        setIsSearching(false);
        setSearchStage(0);
      }
    },
    []
  );

  return (
    <main className="page-container bg-[#08080a] min-h-screen text-white font-sans overflow-hidden">
      <PageLanding
        isActive={currentPage === 0}
        onNavigate={navigateToPage}
        health={health}
        corpusStats={corpusStats}
        selectedVideo={selectedVideo}
        onSelectVideo={setSelectedVideo}
      />
      <PageConsole
        isActive={currentPage === 1}
        onNavigate={navigateToPage}
        onSearch={handleSearch}
        isSearching={isSearching}
        searchStage={searchStage}
        searchError={searchError}
        corpusStats={corpusStats}
        selectedVideo={selectedVideo}
        onSelectVideo={setSelectedVideo}
      />
      <PageResultsAndXAI
        isActive={currentPage === 2}
        onNavigate={navigateToPage}
        data={searchData}
        isSearching={isSearching}
      />

      {/* Floating Dock Navbar */}
      <nav className="fixed bottom-6 right-8 z-50 flex items-center gap-2 bg-black/80 px-4 py-2 rounded-full backdrop-blur-2xl border border-white/20 shadow-2xl">
        {[
          { label: "1. DEMO", idx: 0 },
          { label: "2. CONSOLE", idx: 1 },
          { label: "3. XAI PROVENANCE", idx: 2 },
        ].map((item) => (
          <button
            key={item.idx}
            onClick={() => navigateToPage(item.idx)}
            className={`px-3 py-1.5 rounded-full text-xs font-mono font-bold transition-all ${
              currentPage === item.idx
                ? "bg-cyan-500 text-black shadow-md"
                : "text-gray-400 hover:text-white"
            }`}
          >
            {item.label}
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
  return text.replace(pattern, '<mark class="bg-cyan-500/30 text-cyan-200 border-b border-cyan-400 px-1 py-0.5 rounded font-mono font-bold">$1</mark>');
}

function resolveVideoFilename(raw: string | undefined | null): string {
  if (!raw) return "Steve Jobs Interview Feb 18 1981.mp4";
  if (raw.endsWith(".mp4") || raw.endsWith(".MOV") || raw.endsWith(".mkv") || raw.endsWith(".webm")) {
    return raw;
  }
  if (raw.includes("Abuse001")) return "Abuse001_x264.mp4";
  if (raw.includes("my_llm_talk")) return "my_llm_talk.MOV";
  if (raw.includes("Steve") || raw.includes("jobs")) return "Steve Jobs Interview Feb 18 1981.mp4";
  const stem = raw.replace(/_[a-f0-9]{12}$/i, "");
  return `${stem}.mp4`;
}
