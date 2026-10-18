"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import WireframeArcs from "@/components/WireframeArcs";
import Header from "@/components/Header";
import SearchBar from "@/components/SearchBar";
import PipelineSteps from "@/components/PipelineSteps";
import ResultCard from "@/components/ResultCard";
import TimelineTrack from "@/components/TimelineTrack";
import VideoPlayer from "@/components/VideoPlayer";
import XAIGrid from "@/components/XAIGrid";
import {
  fetchCorpusStats,
  fetchHealth,
  fetchSearch,
  staticVideoUrl,
  type CorpusStats,
  type HealthResponse,
  type SearchResponse,
} from "@/lib/api";

/* ================================================================
   PAGE 1 (Index 0) — JUDGE LANDING & DEMO OVERVIEW
   ================================================================ */

function PageLanding({
  onNavigate,
  health,
  corpusStats,
  selectedVideo,
  onSelectVideo,
}: {
  onNavigate: (page: number) => void;
  health: HealthResponse | null;
  corpusStats: CorpusStats | null;
  selectedVideo: string;
  onSelectVideo: (video: string) => void;
}) {
  return (
    <div className="page-view page-view-active">
      <Header
        tickerText="JUDGE DEMO CONSOLE // REAL-TIME MULTIMODAL VIDEO RETRIEVAL"
        pageIndex={0}
        onNavigate={onNavigate}
        corpusStats={corpusStats}
        selectedVideo={selectedVideo}
        onSelectVideo={onSelectVideo}
        health={health}
      />

      <div className="flex-1 relative flex flex-col justify-center items-center p-6 md:p-12 text-center overflow-hidden pt-20">
        <WireframeArcs variant="manifesto" aria-hidden="true" />

        <div className="z-10 max-w-5xl mx-auto flex flex-col items-center justify-center my-auto px-4">
          {/* Status Badge */}
          <div className="inline-flex items-center gap-3 px-5 py-2 bg-black/60 backdrop-blur-md rounded-full border border-[#10B981]/40 mb-8 shadow-[0_0_20px_rgba(16,185,129,0.2)]">
            <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" aria-hidden="true" />
            <span className="font-mono font-bold text-xs text-[#10B981] tracking-[0.25em] uppercase">
              HACKATHON JUDGE DEMO MODE &bull; &lt; 300 MS CPU LATENCY
            </span>
          </div>

          {/* Hero Title */}
          <h1 className="font-mono font-black text-5xl sm:text-7xl md:text-8xl lg:text-9xl uppercase tracking-[0.12em] text-white leading-none mb-6 drop-shadow-[0_10px_30px_rgba(0,0,0,0.8)]">
            NEURALVIDEO <span className="text-[#06B6D4]">PRO</span>
          </h1>

          {/* Tagline */}
          <p className="font-[var(--font-inter)] font-normal text-lg sm:text-xl md:text-2xl text-[var(--text-bone)] max-w-3xl leading-relaxed mb-10 text-center">
            Sub-second cross-modal video search fusing{" "}
            <span className="text-[#06B6D4]/90 font-semibold border-b border-[#06B6D4]/50">
              CLIP ViT-B/32 keyframes
            </span>{" "}
            and{" "}
            <span className="text-[#10B981]/90 font-semibold border-b border-[#10B981]/50">
              Whisper Base dialogue transcripts
            </span>{" "}
            with Reciprocal Rank Fusion & XAI attribution.
          </p>

          {/* Key Metrics Pill Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full max-w-4xl mb-12 font-mono">
            <div className="p-4 bg-black/70 rounded-2xl border border-white/10 text-center">
              <span className="text-[10px] text-gray-400 uppercase tracking-widest block mb-1">SEARCH SLA</span>
              <span className="text-2xl font-black text-[#10B981]">&lt; 300ms</span>
            </div>
            <div className="p-4 bg-black/70 rounded-2xl border border-white/10 text-center">
              <span className="text-[10px] text-gray-400 uppercase tracking-widest block mb-1">VECTOR STORE</span>
              <span className="text-2xl font-black text-[#06B6D4]">Qdrant Dual 512-D</span>
            </div>
            <div className="p-4 bg-black/70 rounded-2xl border border-white/10 text-center">
              <span className="text-[10px] text-gray-400 uppercase tracking-widest block mb-1">INDEX POINTS</span>
              <span className="text-2xl font-black text-white">{corpusStats?.total_points || 2086}</span>
            </div>
            <div className="p-4 bg-black/70 rounded-2xl border border-white/10 text-center">
              <span className="text-[10px] text-gray-400 uppercase tracking-widest block mb-1">EXPLAINABILITY</span>
              <span className="text-2xl font-black text-[#06B6D4]">RRF + XAI</span>
            </div>
          </div>

          {/* Launch Action CTA */}
          <button
            onClick={() => onNavigate(1)}
            className="font-mono font-bold text-lg sm:text-xl tracking-[0.2em] uppercase px-12 py-6 bg-[#06B6D4] hover:bg-[#10B981] text-black rounded-2xl transition-all duration-300 shadow-[0_0_35px_rgba(6,182,212,0.4)] hover:scale-105 group cursor-pointer flex items-center gap-4 focus-visible:ring-2 focus-visible:ring-[#06B6D4]"
          >
            ENTER SEARCH CONSOLE
            <span className="text-3xl group-hover:translate-x-1.5 transition-transform" aria-hidden="true">
              &rarr;
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   PAGE 2 (Index 1) — SEARCH CONSOLE & PIPELINE STORYTELLING BAR
   ================================================================ */

function PageConsole({
  onNavigate,
  onSearch,
  isSearching,
  searchStage,
  searchError,
  corpusStats,
  selectedVideo,
  onSelectVideo,
}: {
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

  const samplePrompts = [
    { label: "security camera footage of incident scene", q: "security camera footage of incident scene" },
    { label: "speaker discussing transformers", q: "speaker discussing transformers" },
    { label: "person explaining neural networks", q: "person explaining neural networks" },
    { label: "prompt engineering", q: "prompt engineering" },
    { label: "television shoots for the lowest common denominator", q: "television shoots for the lowest common denominator" },
    { label: "Show me where Steve Jobs talks about AI", q: "Show me where Steve Jobs talks about AI" },
    { label: "whiteboard discussion", q: "whiteboard discussion" },
  ];

  const pipelineSteps = [
    { step: 1, title: "Encoding Query...", desc: "CLIP ViT-B/32 & Text Transformer" },
    { step: 2, title: "Searching Visual Index...", desc: "512-D Vision Vectors" },
    { step: 3, title: "Searching Audio Index...", desc: "16kHz Whisper Transcripts" },
    { step: 4, title: "Fusing Results (RRF)...", desc: "Reciprocal Rank Fusion" },
    { step: 5, title: "Diversifying Results (MMR)...", desc: "Semantic Vector Diversity (λ=0.7)" },
    { step: 6, title: "Returning Top Match...", desc: "Confidence Scoring & Playback Sync" },
  ];

  return (
    <div className="page-view page-view-active pt-20">
      <Header
        tickerText="SEARCH CONSOLE // LIVE PIPELINE STORYTELLING & INFERENCE"
        pageIndex={1}
        onNavigate={onNavigate}
        corpusStats={corpusStats}
        selectedVideo={selectedVideo}
        onSelectVideo={onSelectVideo}
        health={null}
      />

      <div className="flex-1 relative flex flex-col justify-center items-center p-6 md:p-12 text-center overflow-hidden">
        <WireframeArcs variant="terminal" aria-hidden="true" />

        <div className="z-10 max-w-5xl mx-auto w-full flex flex-col items-center justify-center my-auto px-4 py-6 space-y-8">
          <div className="text-center">
            <span className="font-mono font-bold text-xs text-[#06B6D4] tracking-[0.25em] uppercase block mb-3">
              JUDGE DEMO CONSOLE // QUERY INFERENCE ENGINE
            </span>
            <h2 className="font-mono font-black text-4xl sm:text-6xl md:text-7xl uppercase tracking-[0.1em] text-white leading-none drop-shadow-lg">
              MULTIMODAL SEARCH
            </h2>
          </div>

          <SearchBar
            query={query}
            setQuery={setQuery}
            onSearch={onSearch}
            isSearching={isSearching}
          />

          {isSearching && (
            <PipelineSteps steps={pipelineSteps} activeStep={searchStage} />
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
                  className="text-xs font-mono font-bold py-2.5 px-4 bg-black/60 hover:bg-[#06B6D4] hover:text-black text-gray-200 transition-all duration-200 rounded-xl border border-white/15 hover:border-[#06B6D4] cursor-pointer backdrop-blur-md shadow-md hover:scale-105 focus-visible:ring-2 focus-visible:ring-[#06B6D4]"
                  aria-label={`Search: ${sample.label}`}
                >
                  {sample.label}
                </button>
              ))}
            </div>
          </div>

          {/* Error Banner */}
          {searchError && (
            <div className="w-full max-w-3xl mx-auto p-4 border border-[#F59E0B]/50 bg-[#F59E0B]/60 text-[#F59E0B]/200 text-sm font-mono font-bold rounded-xl" role="alert">
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
  onNavigate,
  data,
  isSearching,
}: {
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

  const handleSeekAndPlay = (timestampInSeconds: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = timestampInSeconds;
      videoRef.current.play().catch(() => {});
    }
  };

  if (isSearching) {
    return (
      <div className="page-view page-view-active pt-20">
        <Header
          tickerText="SEARCH ENGINE EXECUTING MULTIMODAL INFERENCE..."
          pageIndex={2}
          onNavigate={onNavigate}
          corpusStats={null}
          selectedVideo="all"
          onSelectVideo={() => {}}
          health={null}
        />
        <div className="flex-1 flex flex-col p-6 md:p-8 overflow-hidden">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 z-10 pb-3 border-b border-white/15">
            <div>
              <span className="font-mono font-bold text-xs text-[#06B6D4] uppercase tracking-widest">XAI PROVENANCE</span>
              <span className="font-mono text-xs text-white">QUERY: "&quot;...&quot;</span>
            </div>
            <p className="font-mono text-xs text-gray-400 mt-1">AUTO-INTENT: ... (&alpha; = ...) &bull; ... RESULTS</p>
          </div>

          <PipelineSteps
            steps={[
              { step: 1, title: "Encoding Query...", desc: "CLIP ViT-B/32 & Text Transformer" },
              { step: 2, title: "Searching Visual Index...", desc: "512-D Vision Vectors" },
              { step: 3, title: "Searching Audio Index...", desc: "16kHz Whisper Transcripts" },
              { step: 4, title: "Fusing Results (RRF)...", desc: "Reciprocal Rank Fusion" },
              { step: 5, title: "Diversifying Results (MMR)...", desc: "Semantic Vector Diversity (λ=0.7)" },
              { step: 6, title: "Returning Top Match...", desc: "Confidence Scoring & Playback Sync" },
            ]}
            activeStep={4}
          />
        </div>
      </div>
  );
}

  if (!data || !data.results || data.results.length === 0 || !activeItem) {
    return (
      <div className="page-view page-view-active pt-20">
        <Header
          tickerText="RESULTS GALLERY // AWAITING SEARCH EXECUTION"
          pageIndex={2}
          onNavigate={onNavigate}
          corpusStats={null}
          selectedVideo="all"
          onSelectVideo={() => {}}
          health={null}
        />
        <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
          <p className="font-mono text-lg text-gray-300">NO RESULTS DISPLAYED YET</p>
          <p className="font-mono text-xs text-gray-500 mt-2 max-w-md">
            Enter a query in the Search Console to execute multimodal vector retrieval.
          </p>
          <button
            onClick={() => onNavigate(1)}
            className="mt-6 px-6 py-3 bg-[#06B6D4] text-black font-mono font-bold rounded-xl transition-all focus-visible:ring-2 focus-visible:ring-[#06B6D4]"
          >
            GO TO SEARCH CONSOLE &rarr;
          </button>
        </div>
      </div>
    );
  }

  const alpha = data.intent.alpha;
  const transcript = (activeItem.payload.transcribed_text as string) ?? "";
  const timestampSec = (activeItem.payload.timestamp as number) ?? 0;
  const formattedTime = `${Math.floor(timestampSec / 60)
    .toString()
    .padStart(2, "0")}:${Math.floor(timestampSec % 60)
    .toString()
    .padStart(2, "0")}`;

  const confidenceBand = activeItem.xai.confidence_tier || "HIGH";

  const maxTimestampInResults =
    resultsLength(data.results) > 0
      ? Math.max(...data.results.map((r) => Number(r.payload.timestamp) || 0))
      : 0;
  const maxDurationSec = maxTimestampInResults > 0 ? maxTimestampInResults + 30 : 300;

  return (
    <div className="page-view page-view-active pt-20">
      <Header
        tickerText={`RESULTS // ${data.total_results} MATCHES FOR "${data.query}" (${data.latency_ms}ms)`}
        pageIndex={2}
        onNavigate={onNavigate}
        corpusStats={null}
        selectedVideo="all"
        onSelectVideo={() => {}}
        health={null}
      />

      <div className="flex-1 relative flex flex-col justify-between p-6 md:p-8 overflow-hidden">
        <WireframeArcs variant="gallery" aria-hidden="true" />

        {/* Results Toolbar */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 z-10 pb-3 border-b border-white/15">
          <div>
            <div className="flex items-center gap-3">
              <span className="font-mono font-bold text-xs text-[#06B6D4] uppercase tracking-widest">XAI PROVENANCE</span>
              <span className="font-mono text-xs text-white">
                QUERY: &quot;<strong className="text-[#06B6D4]/90">{data.query}</strong>&quot;
              </span>
            </div>
            <p className="font-mono text-xs text-gray-400 mt-1">
              AUTO-INTENT: {data.intent.intent_label} (&alpha; = {alpha.toFixed(2)}) &bull; {data.total_results} RESULTS IN <span className="text-[#10B981] font-bold">{data.latency_ms}ms</span>
            </p>
          </div>

          <button
            onClick={() => onNavigate(1)}
            className="px-4 py-2 bg-white/10 hover:bg-white/20 text-xs font-mono font-bold text-white rounded-xl border border-white/20 transition-all focus-visible:ring-2 focus-visible:ring-[#06B6D4]"
          >
            NEW SEARCH &rarr;
          </button>
        </div>

        <TimelineTrack
          results={data.results}
          selectedIndex={selectedIndex}
          onSelect={(idx, ts) => {
            setSelectedIndex(idx);
            handleSeekAndPlay(ts);
          }}
        />

        {/* Main 2-Column Split Console */}
        <div className="z-10 flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 my-2 overflow-y-auto max-h-[calc(100vh-270px)] pr-2">
          {/* LEFT COLUMN: Timeline Keyframe Match Cards */}
          <div className="lg:col-span-5 space-y-4">
            <h3 className="font-mono text-sm font-bold text-gray-300 uppercase tracking-wider">
              TIMELINE MATCH REEL (CLICK TO SYNC PLAYER):
            </h3>

            <div className="space-y-4">
              {data.results.map((r, idx) => (
                <ResultCard
                  key={String(r.id)}
                  item={r}
                  rank={idx + 1}
                  isSelected={idx === selectedIndex}
                  onSelect={(rankIdx) => {
                    setSelectedIndex(rankIdx - 1);
                    handleSeekAndPlay(Number(r.payload.timestamp) || 0);
                  }}
                />
              ))}
            </div>
          </div>

          {/* RIGHT COLUMN: Video Player & XAI */}
          <div className="lg:col-span-7 space-y-6">
            <VideoPlayer
              item={activeItem}
              formattedTime={formattedTime}
              timestampSec={timestampSec}
              confidenceBand={confidenceBand}
            />

            {/* Spoken Dialogue Transcript Block */}
            <div className="p-6 bg-black/90 backdrop-blur-2xl border border-white/15 rounded-2xl space-y-3 font-mono">
              <span className="text-xs font-bold text-[#06B6D4] uppercase tracking-wider block">
                SPOKEN DIALOGUE TRANSCRIPT (TIMESTAMP {formattedTime}):
              </span>
              {transcript ? (
                <p
                  className="text-base sm:text-lg leading-relaxed text-[var(--text-bone)] p-4 bg-white/5 rounded-xl border border-white/10"
                  dangerouslySetInnerHTML={{
                    __html: highlightKeywords(transcript, data.query),
                  }}
                />
              ) : (
                <p className="text-sm text-gray-500">No acoustic dialogue transcript available for this keyframe segment.</p>
              )}
            </div>

            <XAIGrid item={activeItem} />
          </div>
        </div>
      </div>
    </div>
  );
}

function resultsLength(results: SearchResponse["results"]): number {
  return results.length;
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
        setCurrentPage(2);
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
    <main className="page-container bg-[#08080a] min-h-screen text-white font-[var(--font-inter)] overflow-hidden">
      {currentPage === 0 && (
        <PageLanding
          onNavigate={navigateToPage}
          health={health}
          corpusStats={corpusStats}
          selectedVideo={selectedVideo}
          onSelectVideo={setSelectedVideo}
        />
      )}
      {currentPage === 1 && (
        <PageConsole
          onNavigate={navigateToPage}
          onSearch={handleSearch}
          isSearching={isSearching}
          searchStage={searchStage}
          searchError={searchError}
          corpusStats={corpusStats}
          selectedVideo={selectedVideo}
          onSelectVideo={setSelectedVideo}
        />
      )}
      {currentPage === 2 && (
        <PageResultsAndXAI
          onNavigate={navigateToPage}
          data={searchData}
          isSearching={isSearching}
        />
      )}

      {/* Floating Dock Navbar */}
      <nav className="fixed bottom-6 right-8 z-50 flex items-center gap-2 bg-black/80 px-4 py-2 rounded-full backdrop-blur-2xl border border-white/20 shadow-2xl" aria-label="Section navigation">
        {[
          { label: "1. DEMO", idx: 0 },
          { label: "2. CONSOLE", idx: 1 },
          { label: "3. XAI PROVENANCE", idx: 2 },
        ].map((item) => (
          <button
            key={item.idx}
            onClick={() => navigateToPage(item.idx)}
            aria-current={currentPage === item.idx ? "page" : undefined}
            className={`px-3 py-1.5 rounded-full text-xs font-mono font-bold transition-all focus-visible:ring-2 focus-visible:ring-[#06B6D4] ${
              currentPage === item.idx
                ? "bg-[#06B6D4] text-black shadow-md"
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
  return text.replace(pattern, '<mark class="bg-[#06B6D4]/30 text-[#06B6D4]/90 border-b border-[#06B6D4]/50 px-1 py-0.5 rounded font-mono font-bold">$1</mark>');
}

function resolveVideoFilename(raw: string | undefined | null): string {
  if (!raw) return "";
  if (raw.endsWith(".mp4") || raw.endsWith(".MOV") || raw.endsWith(".mkv") || raw.endsWith(".webm")) {
    return raw;
  }
  return `${raw}.mp4`;
}
