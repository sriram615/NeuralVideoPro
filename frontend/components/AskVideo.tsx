"use client";

import { useCallback, useState } from "react";
import type { AskVideoResponse, CorpusStats, HealthResponse } from "@/lib/api";
import { fetchAskVideo } from "@/lib/api";
import WireframeArcs from "@/components/WireframeArcs";
import Header from "@/components/Header";
import PipelineSteps from "@/components/PipelineSteps";

function formatTimestamp(seconds: number | null | undefined): string {
  if (seconds === null || seconds === undefined) return "--:--";
  const total = Math.round(seconds);
  const mins = Math.floor(total / 60);
  const secs = total % 60;
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

interface AskVideoProps {
  onNavigate: (page: number) => void;
  health: HealthResponse | null;
  corpusStats: CorpusStats | null;
}

interface CitationCardProps {
  citation: NonNullable<AskVideoResponse["citations"]>[number];
  index: number;
}

function CitationCard({ citation, index }: CitationCardProps) {
  const { video_id, event_window, hero_timestamp, transcript_snippet, visual_description } = citation;

  return (
    <div
      className="p-4 bg-black/80 backdrop-blur-md rounded-xl border border-white/15 space-y-3 font-mono"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="font-black px-2 py-1 rounded border border-accent-cyan/40 bg-accent-cyan/10 text-accent-cyan">
          SOURCE {index + 1}
        </span>
        <span className={`text-micro font-bold ${video_id ? "text-accent-emerald" : "text-gray-500"}`}>
          {video_id ?? "UNKNOWN"}
        </span>
      </div>

      <div className="space-y-1 text-xs text-gray-400">
        <div className="flex items-center gap-1">
          <span className="text-accent-cyan">WINDOW:</span>
          <span className="text-bone">{event_window}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-accent-cyan">TIMESTAMP:</span>
          <span className="text-bone">{formatTimestamp(hero_timestamp)}</span>
        </div>
      </div>

      {transcript_snippet && (
        <div className="p-3 bg-white/5 rounded-xl border border-white/10 text-sm text-bone leading-relaxed">
          <span className="text-micro text-accent-emerald uppercase block mb-1">TRANSCRIPT EVIDENCE</span>
          <p className="italic">{transcript_snippet}</p>
        </div>
      )}

      {visual_description && (
        <div className="p-3 bg-accent-cyan/5 rounded-xl border border-accent-cyan/20 text-sm text-bone leading-relaxed">
          <span className="text-micro text-accent-cyan uppercase block mb-1">VISUAL SCENE</span>
          <p className="italic">{visual_description}</p>
        </div>
      )}
    </div>
  );
}

export default function AskVideo({
  onNavigate,
  health,
  corpusStats,
}: AskVideoProps) {
  const [question, setQuestion] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [questionStage, setQuestionStage] = useState(0);
  const [ragData, setRagData] = useState<AskVideoResponse | null>(null);
  const [ragError, setRagError] = useState<string | null>(null);

  const sampleQuestions = [
    { label: "What is the quadratic equation formula?", q: "What is the quadratic equation formula?" },
    { label: "What did Steve Jobs say about calculators?", q: "What did Steve Jobs say about calculators?" },
    { label: "Who is Michelle in Obama's farewell?", q: "Who is Michelle in Obama's farewell?" },
    { label: "What is stage design identity?", q: "What is stage design identity?" },
    { label: "What are the downsides of living alone?", q: "What are the downsides of living alone?" },
    { label: "How do you make an omelette?", q: "How do you make an omelette?" },
  ];

  const ragPipelineSteps = [
    { step: 1, title: "Encoding Question...", desc: "CLIP ViT-B/32 text embedding" },
    { step: 2, title: "Retrieving Context...", desc: "Dual-vector Qdrant search (RRF)" },
    { step: 3, title: "Diversifying Snippets...", desc: "MMR redundancy elimination" },
    { step: 4, title: "Generating Answer...", desc: "Groq grounded synthesis with citations" },
    { step: 5, title: "Grounding Verification...", desc: "Source citation attribution" },
  ];

  const handleAsk = useCallback(
    async (q: string) => {
      setIsAsking(true);
      setRagError(null);
      setRagData(null);
      setQuestionStage(1);

      const stageTimer = setInterval(() => {
        setQuestionStage((s) => (s < 4 ? s + 1 : s));
      }, 200);

      try {
        const data = await fetchAskVideo(q, 5, true);
        setQuestionStage(5);
        setRagData(data);
      } catch (err: unknown) {
        console.error("Video-RAG error:", err);
        setRagError(err instanceof Error ? err.message : "Failed to connect to Video RAG API");
      } finally {
        clearInterval(stageTimer);
        setIsAsking(false);
        setQuestionStage(0);
      }
    },
    []
  );

  return (
    <div className="page-shell pt-16 md:pt-20">
      <Header
        tickerText="VIDEO-RAG // GROUNDED QUESTION ANSWERING WITH SOURCE CITATIONS"
        pageIndex={3}
        onNavigate={onNavigate}
        corpusStats={corpusStats}
        selectedVideo="all"
        onSelectVideo={() => {}}
        health={health}
      />
      <div className="flex-1 relative flex flex-col justify-center items-center p-4 md:p-8 text-center overflow-hidden">
        <WireframeArcs variant="xai" aria-hidden="true" />
        <div className="z-10 max-w-5xl mx-auto w-full flex flex-col items-center justify-center my-auto px-3 md:px-6 py-4 md:py-6 space-y-6">
          <div className="text-center">
            <span className="font-mono font-bold text-xs text-accent-emerald tracking-[0.25em] uppercase block mb-2">
              JUDGE DEMO CONSOLE // VIDEO-RAG Q&A ENGINE
            </span>
            <h2 className="font-mono font-black text-3xl sm:text-5xl md:text-6xl uppercase tracking-[0.1em] text-white leading-none drop-shadow-lg">
              GROUNDED Q&A
            </h2>
          </div>

          {/* Question Input */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (question.trim() && !isAsking) {
                handleAsk(question.trim());
              }
            }}
            className="relative w-full max-w-4xl mx-auto"
            aria-label="Video-RAG question input"
          >
            <div className="relative rounded-2xl bg-black/70 backdrop-blur-2xl border border-accent-emerald/40 p-2 shadow-[0_0_30px_rgba(16,185,129,0.2)] focus-within:border-accent-emerald focus-within:shadow-[0_0_40px_rgba(16,185,129,0.4)] transition-all duration-300">
              <label htmlFor="rag-question-input" className="sr-only">
                Video-RAG question
              </label>
              <input
                id="rag-question-input"
                type="text"
                className="w-full px-6 py-5 bg-transparent text-white font-mono text-lg sm:text-xl placeholder-bone/60 outline-none focus-visible:ring-2 focus-visible:ring-accent-emerald"
                placeholder='Try "What is the quadratic equation formula?" or "What did Steve Jobs say about calculators?"...'
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                autoFocus
                disabled={isAsking}
                aria-label="Video-RAG question"
                aria-disabled={isAsking}
              />
              <button
                type="submit"
                disabled={!question.trim() || isAsking}
                className="absolute right-4 top-1/2 -translate-y-1/2 px-8 py-3.5 bg-accent-emerald hover:bg-accent-cyan disabled:opacity-40 disabled:cursor-not-allowed text-black font-mono font-black text-sm tracking-wider uppercase rounded-xl transition-all shadow-md cursor-pointer focus-visible:ring-2 focus-visible:ring-accent-emerald"
                aria-label={isAsking ? "Generating answer..." : "Ask"}
              >
                {isAsking ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-black" viewBox="0 0 24 24" aria-hidden="true">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="4" fill="none"></path>
                    </svg>
                    GENERATING...
                  </>
                ) : (
                  "ASK"
                )}
              </button>
            </div>
          </form>

          {isAsking && (
            <PipelineSteps steps={ragPipelineSteps} activeStep={questionStage} />
          )}

          <div className="w-full max-w-4xl mx-auto text-center space-y-3">
            <span className="font-mono font-bold text-xs text-gray-400 tracking-[0.2em] uppercase block">
              CURATED VIDEO-RAG QUESTION CHIPS:
            </span>
            <div className="flex flex-wrap items-center justify-center gap-2">
              {sampleQuestions.map((sample) => (
                <button
                  key={sample.q}
                  type="button"
                  onClick={() => {
                    setQuestion(sample.q);
                    handleAsk(sample.q);
                  }}
                  disabled={isAsking}
                  className={`text-xs sm:text-sm font-mono font-bold py-2 px-3 bg-black/60 hover:bg-accent-emerald hover:text-black text-gray-200 transition-all duration-200 rounded-xl border border-white/15 hover:border-accent-emerald cursor-pointer backdrop-blur-md shadow-md hover:scale-105 focus-visible:ring-2 focus-visible:ring-accent-emerald ${
                    isAsking ? "opacity-40 cursor-not-allowed" : ""
                  }`}
                  aria-label={`Ask: ${sample.label}`}
                >
                  {sample.label}
                </button>
              ))}
            </div>
          </div>

          {ragError && (
            <div className="w-full max-w-3xl mx-auto p-4 border border-accent-amber/50 bg-accent-amber/60 text-accent-amber text-sm font-mono font-bold rounded-xl" role="alert">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-accent-amber/80">VIDEO-RAG ERROR:</span>
                <span className="text-bone/90">{ragError}</span>
              </div>
              <button
                onClick={() => {
                  setRagError(null);
                  if (question.trim()) {
                    handleAsk(question.trim());
                  }
                }}
                className="text-xs font-mono text-accent-cyan hover:text-accent-emerald focus-visible:ring-2 focus-visible:ring-accent-cyan mt-2"
              >
                Try again
              </button>
            </div>
          )}

          {/* Answer Display */}
          {ragData && (
            <div className="w-full max-w-5xl mx-auto space-y-6">
              <div className="flex items-center justify-between border-b border-white/15 pb-4">
                <div>
                  <span className="font-mono font-bold text-xs text-accent-emerald uppercase tracking-wider block mb-1">
                    GROUNDED ANSWER
                  </span>
                  <p className="font-mono text-xs text-gray-400">
                    QUESTION: "{ragData.question}" &bull; {ragData.latency_ms}ms TOTAL
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-micro font-bold text-bone">
                    LLM: {Math.round(ragData.llm_latency_ms)}ms
                  </span>
                  <span className="text-micro font-bold text-bone">
                    RETRIEVAL: {Math.round(ragData.retrieval_latency_ms)}ms
                  </span>
                </div>
              </div>

              <div className="p-6 bg-black/90 backdrop-blur-2xl border border-accent-emerald/40 rounded-2xl shadow-2xl">
                <div className="text-bone text-lg sm:text-xl leading-relaxed font-sans whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: ragData.answer }} />
              </div>

              {ragData.citations && ragData.citations.length > 0 && (
                <div className="space-y-3">
                  <h3 className="font-mono text-xs font-bold text-accent-cyan uppercase tracking-wider block mb-3">
                    SOURCE CITATIONS ({ragData.citations.length})
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {ragData.citations.map((citation, idx) => (
                      <CitationCard key={idx} citation={citation} index={idx} />
                    ))}
                  </div>
                </div>
              )}

              <button
                onClick={() => onNavigate(1)}
                className="px-6 py-3 bg-accent-emerald hover:bg-accent-cyan text-black font-mono font-bold text-sm rounded-xl transition-all shadow-md focus-visible:ring-2 focus-visible:ring-accent-emerald"
              >
                NEW QUESTION &rarr;
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
