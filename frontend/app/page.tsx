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
import Skeleton from "@/components/Skeleton";
import {
  fetchCorpusStats,
  fetchHealth,
  fetchSearch,
  type CorpusStats,
  type HealthResponse,
  type SearchResponse,
} from "@/lib/api";

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
  return text.replace(pattern, '<mark class="bg-accent-cyan/30 text-accent-cyan/90 border-b border-accent-cyan/50 px-1 py-0.5 rounded font-mono font-bold">$1</mark>');
}

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
      <div className="flex-1 relative flex flex-col justify-center items-center p-4 md:p-8 text-center overflow-hidden pt-16 md:pt-24">
        <WireframeArcs variant="manifesto" aria-hidden="true" />
        <div className="z-10 max-w-5xl mx-auto flex flex-col items-center justify-center my-auto px-3 md:px-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-black/60 backdrop-blur-md rounded-full border border-accent-emerald/40 mb-6 shadow-[0_0_20px_rgba(16,185,129,0.2)]">
            <span className="w-2 h-2 rounded-full bg-accent-emerald" aria-hidden="true" />
            <span className="font-mono font-bold text-[10px] text-accent-emerald tracking-[0.25em] uppercase">
              HACKATHON JUDGE DEMO MODE &bull; &lt; 300 MS CPU LATENCY
            </span>
          </div>
          <h1 className="font-mono font-black text-4xl sm:text-6xl lg:text-8xl uppercase tracking-[0.1em] text-white leading-none mb-6 drop-shadow-[0_10px_30px_rgba(0,0,0,0.8)]">
            NEURALVIDEO <span className="text-accent-cyan">PRO</span>
          </h1>
          <p className="font-sans font-normal text-sm sm:text-base md:text-lg text-bone max-w-3xl leading-relaxed mb-8 text-center">
            Sub-second cross-modal video search fusing{" "}
            <span className="text-accent-cyan/90 font-semibold border-b border-accent-cyan/50">
              CLIP ViT-B/32 keyframes
            </span>{" "}
            and{" "}
            <span className="text-accent-emerald/90 font-semibold border-b border-accent-emerald/50">
              Whisper Base dialogue transcripts
            </span>{" "}
            with Reciprocal Rank Fusion & XAI attribution.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 w-full max-w-4xl mb-8 font-mono">
            <div className="p-3 bg-black/70 rounded-xl border border-white/10 text-center">
              <span className="text-[9px] text-gray-400 uppercase tracking-widest block mb-1">SEARCH SLA</span>
              <span className="text-xl font-black text-accent-emerald">&lt; 300ms</span>
            </div>
            <div className="p-3 bg-black/70 rounded-xl border border-white/10 text-center">
              <span className="text-[9px] text-gray-400 uppercase tracking-widest block mb-1">VECTOR STORE</span>
              <span className="text-xl font-black text-accent-cyan">Qdrant Dual 512-D</span>
            </div>
            <div className="p-3 bg-black/70 rounded-xl border border-white/10 text-center">
              <span className="text-[9px] text-gray-400 uppercase tracking-widest block mb-1">INDEX POINTS</span>
              <span className="text-xl font-black text-white">{corpusStats?.total_points || 2086}</span>
            </div>
            <div className="p-3 bg-black/70 rounded-xl border border-white/10 text-center">
              <span className="text-[9px] text-gray-400 uppercase tracking-widest block mb-1">EXPLAINABILITY</span>
              <span className="text-xl font-black text-accent-cyan">RRF + XAI</span>
            </div>
          </div>
          <button
            onClick={() => onNavigate(1)}
            className="font-mono font-bold text-base sm:text-lg tracking-[0.2em] uppercase px-8 py-4 bg-accent-cyan hover:bg-accent-emerald text-black rounded-2xl transition-all duration-300 shadow-[0_0_35px_rgba(6,182,212,0.4)] hover:scale-105 group cursor-pointer flex items-center gap-3 focus-visible:ring-2 focus-visible:ring-accent-cyan"
          >
            ENTER SEARCH CONSOLE
            <span className="text-2xl group-hover:translate-x-1 transition-transform" aria-hidden="true">
              &rarr;
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}

function PageConsole({
  onNavigate,
  onSearch,
  isSearching,
  searchStage,
  searchError,
  setSearchError,
  corpusStats,
  selectedVideo,
  onSelectVideo,
}: {
  onNavigate: (page: number) => void;
  onSearch: (query: string) => void;
  isSearching: boolean;
  searchStage: number;
  searchError: string | null;
  setSearchError: (err: string | null) => void;
  corpusStats: CorpusStats | null;
  selectedVideo: string;
  onSelectVideo: (video: string) => void;
}) {
  const [query, setQuery] = useState("");

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
    <div className="page-view page-view-active pt-16 md:pt-20">
      <Header
        tickerText="SEARCH CONSOLE // LIVE PIPELINE STORYTELLING & INFERENCE"
        pageIndex={1}
        onNavigate={onNavigate}
        corpusStats={corpusStats}
        selectedVideo={selectedVideo}
        onSelectVideo={onSelectVideo}
        health={null}
      />
      <div className="flex-1 relative flex flex-col justify-center items-center p-4 md:p-8 text-center overflow-hidden">
        <WireframeArcs variant="terminal" aria-hidden="true" />
        <div className="z-10 max-w-5xl mx-auto w-full flex flex-col items-center justify-center my-auto px-3 md:px-6 py-4 md:py-6 space-y-6">
          <div className="text-center">
            <span className="font-mono font-bold text-xs text-accent-cyan tracking-[0.25em] uppercase block mb-2">
              JUDGE DEMO CONSOLE // QUERY INFERENCE ENGINE
            </span>
            <h2 className="font-mono font-black text-3xl sm:text-5xl md:text-6xl uppercase tracking-[0.1em] text-white leading-none drop-shadow-lg">
              MULTIMODAL SEARCH
            </h2>
          </div>
          <SearchBar query={query} setQuery={setQuery} onSearch={onSearch} isSearching={isSearching} />
          {isSearching && (
            <PipelineSteps steps={pipelineSteps} activeStep={searchStage} />
          )}
          <div className="w-full max-w-4xl mx-auto text-center space-y-3">
            <span className="font-mono font-bold text-xs text-gray-400 tracking-[0.2em] uppercase block">
              CURATED HACKATHON DEMO QUERY CHIPS:
            </span>
            <div className="flex flex-wrap items-center justify-center gap-2">
              {samplePrompts.map((sample) => (
                <button
                  key={sample.q}
                  type="button"
                  onClick={() => {
                    setQuery(sample.q);
                    onSearch(sample.q);
                  }}
                  className="text-xs sm:text-sm font-mono font-bold py-2 px-3 bg-black/60 hover:bg-accent-cyan hover:text-black text-gray-200 transition-all duration-200 rounded-xl border border-white/15 hover:border-accent-cyan cursor-pointer backdrop-blur-md shadow-md hover:scale-105 focus-visible:ring-2 focus-visible:ring-accent-cyan"
                  aria-label={`Search: ${sample.label}`}
                >
                  {sample.label}
                </button>
              ))}
            </div>
          </div>
          {searchError && (
            <div className="w-full max-w-3xl mx-auto p-4 border border-accent-amber/50 bg-accent-amber/60 text-accent-amber text-sm font-mono font-bold rounded-xl" role="alert">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-accent-amber/80">SEARCH ERROR:</span>
                <span className="text-bone/90">{searchError}</span>
              </div>
              <button
                onClick={() => {
                  setSearchError(null);
                  if (query.trim()) {
                    onSearch(query.trim());
                  }
                }}
                className="text-xs font-mono text-accent-cyan hover:text-accent-emerald focus-visible:ring-2 focus-visible:ring-accent-cyan mt-2"
              >
                Try again
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function PageResultsAndXAI({
  onNavigate,
  data,
  isSearching,
  corpusStats,
}: {
  onNavigate: (page: number) => void;
  data: SearchResponse | null;
  isSearching: boolean;
  corpusStats: CorpusStats | null;
}) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [videoDurationSec, setVideoDurationSec] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);

  const activeItem = data?.results[selectedIndex];

  const handleSeekAndPlay = (timestampInSeconds: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = timestampInSeconds;
      videoRef.current.play().catch(() => {});
    }
  };

  if (isSearching) {
    return (
      <div className="page-view page-view-active pt-16 md:pt-20">
        <Header
          tickerText="SEARCH ENGINE EXECUTING MULTIMODAL INFERENCE..."
          pageIndex={2}
          onNavigate={onNavigate}
          corpusStats={null}
          selectedVideo="all"
          onSelectVideo={() => {}}
          health={null}
        />
        <div className="flex-1 flex flex-col p-4 md:p-6 overflow-hidden">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 z-10 pb-3 border-b border-white/15">
            <div>
              <span className="font-mono font-bold text-xs text-accent-cyan uppercase tracking-widest">XAI PROVENANCE</span>
              <span className="font-mono text-xs text-white">QUERY: &quot;&hellip;&quot;</span>
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
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3" aria-hidden="true">
            {[0, 1, 2, 3].map((i) => (
              <div key={i} className="p-4 bg-black/70 rounded-xl border border-white/10 space-y-3">
                <Skeleton height="0.75rem" width="45%" />
                <Skeleton height="0.75rem" width="85%" />
                <Skeleton height="2.5rem" width="100%" />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!data || !data.results || data.results.length === 0 || !activeItem) {
    return (
      <div className="page-view page-view-active pt-16 md:pt-20">
        <Header
          tickerText="RESULTS GALLERY // AWAITING SEARCH EXECUTION"
          pageIndex={2}
          onNavigate={onNavigate}
          corpusStats={null}
          selectedVideo="all"
          onSelectVideo={() => {}}
          health={null}
        />
        <div className="flex-1 flex flex-col items-center justify-center p-6 md:p-12 text-center">
          <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <p className="font-mono text-lg text-gray-300">No results found</p>
          <p className="font-mono text-xs text-gray-500 max-w-md">
            Try adjusting your query or browse the video catalog to see indexed content.
          </p>
          <button
            onClick={() => onNavigate(1)}
            className="mt-6 px-6 py-3 bg-accent-cyan text-black font-mono font-bold rounded-xl transition-all focus-visible:ring-2 focus-visible:ring-accent-cyan"
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
  const formattedTime = formatTimestamp(timestampSec);

  const confidenceBand = activeItem.xai.confidence_tier || "HIGH";

  return (
    <div className="page-view page-view-active pt-16 md:pt-20">
      <Header
        tickerText={`RESULTS // ${data.total_results} MATCHES FOR "${data.query}" (${data.latency_ms}ms)`}
        pageIndex={2}
        onNavigate={onNavigate}
        corpusStats={corpusStats}
        selectedVideo="all"
        onSelectVideo={() => {}}
        health={null}
      />
      <div className="flex-1 relative flex flex-col justify-between p-4 md:p-6 overflow-hidden">
        <WireframeArcs variant="gallery" aria-hidden="true" />
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 z-10 pb-3 border-b border-white/15">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-xs text-accent-cyan uppercase tracking-widest">XAI PROVENANCE</span>
              <span className="font-mono text-xs text-white">
                QUERY: &quot;<strong className="text-accent-cyan/90">{data.query}</strong>&quot;
              </span>
            </div>
            <p className="font-mono text-xs text-gray-400 mt-1">
              AUTO-INTENT: {data.intent.intent_label} (&alpha; = {alpha.toFixed(2)}) &bull; {data.total_results} RESULTS IN <span className="text-accent-emerald font-bold">{data.latency_ms}ms</span>
            </p>
          </div>
          <button
            onClick={() => onNavigate(1)}
            className="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-xs font-mono font-bold text-white rounded-xl border border-white/20 transition-all focus-visible:ring-2 focus-visible:ring-accent-cyan"
          >
            NEW SEARCH &rarr;
          </button>
        </div>
        <TimelineTrack results={data.results} selectedIndex={selectedIndex} durationSec={videoDurationSec} onSelect={(idx, ts) => { setSelectedIndex(idx); handleSeekAndPlay(ts); }} />
        <div className="z-10 flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 my-2 overflow-y-auto max-h-[calc(100vh-260px)] pr-2">
          <div className="lg:col-span-5 space-y-3">
            <h3 className="font-mono text-xs font-bold text-gray-300 uppercase tracking-widest">
              TIMELINE MATCH REEL (CLICK TO SYNC PLAYER):
            </h3>
            <div className="space-y-3">
              {data.results.map((r, idx) => (
                <ResultCard key={String(r.id)} item={r} rank={idx + 1} isSelected={idx === selectedIndex} onSelect={(rankIdx) => { setSelectedIndex(rankIdx - 1); handleSeekAndPlay(Number(r.payload.timestamp) || 0); }} />
              ))}
            </div>
          </div>
          <div className="lg:col-span-7 space-y-4">
            <VideoPlayer item={activeItem} formattedTime={formattedTime} timestampSec={timestampSec} confidenceBand={confidenceBand} catalog={corpusStats?.video_catalog ?? null} onDurationChange={setVideoDurationSec} />
            <div className="p-5 bg-black/90 backdrop-blur-2xl border border-white/15 rounded-xl space-y-3 font-mono">
              <span className="text-xs font-bold text-accent-cyan uppercase tracking-wider block">
                SPOKEN DIALOGUE TRANSCRIPT (TIMESTAMP {formattedTime}):
              </span>
              {transcript ? (
                <p className="text-base sm:text-lg leading-relaxed text-bone p-4 bg-white/5 rounded-xl border border-white/10" dangerouslySetInnerHTML={{ __html: highlightKeywords(transcript, data.query) }} />
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
      } catch (err: unknown) {
        console.error("Search error:", err);
        setSearchError(err instanceof Error ? err.message : "Failed to connect to backend server");
        setCurrentPage(1);
      } finally {
        setIsSearching(false);
        setSearchStage(0);
      }
    },
    []
  );

  return (
    <main className="page-container bg-void min-h-screen text-white font-sans overflow-hidden">
      {currentPage === 0 && (
        <PageLanding onNavigate={navigateToPage} health={health} corpusStats={corpusStats} selectedVideo={selectedVideo} onSelectVideo={setSelectedVideo} />
      )}
      {currentPage === 1 && (
        <PageConsole
          onNavigate={navigateToPage}
          onSearch={handleSearch}
          isSearching={isSearching}
          searchStage={searchStage}
          searchError={searchError}
          setSearchError={setSearchError}
          corpusStats={corpusStats}
          selectedVideo={selectedVideo}
          onSelectVideo={setSelectedVideo}
        />
      )}
      {currentPage === 2 && (
        <PageResultsAndXAI
          key={searchData?.query ?? "no-results"}
          onNavigate={navigateToPage}
          data={searchData}
          isSearching={isSearching}
          corpusStats={corpusStats}
        />
      )}

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
            className={`px-3 py-1.5 rounded-full text-xs font-mono font-bold transition-all focus-visible:ring-2 focus-visible:ring-accent-cyan ${currentPage === item.idx ? "bg-accent-cyan text-black shadow-md" : "text-gray-400 hover:text-white"}`}
          >
            {item.label}
          </button>
        ))}
      </nav>
    </main>
  );
}
