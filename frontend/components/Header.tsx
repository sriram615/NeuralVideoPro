"use client";

import { useState } from "react";
import type { CorpusStats, HealthResponse } from "@/lib/api";

interface HeaderProps {
  tickerText: string;
  pageIndex: number;
  onNavigate: (index: number) => void;
  corpusStats: CorpusStats | null;
  selectedVideo: string;
  onSelectVideo: (video: string) => void;
  health: HealthResponse | null;
}

export default function Header({
  tickerText,
  pageIndex,
  onNavigate,
  corpusStats,
  selectedVideo,
  onSelectVideo,
  health,
}: HeaderProps) {
  const [catalogOpen, setCatalogOpen] = useState(false);

  return (
    <header
      className="fixed top-0 left-0 right-0 z-40 bg-[#08080a]/90 backdrop-blur-2xl border-b border-white/10"
      aria-label="Main navigation"
    >
      <div className="flex flex-wrap items-center justify-between gap-4 px-6 py-4">
        {/* Brand & Logo */}
        <div
          className="flex items-center gap-4 cursor-pointer group"
          onClick={() => onNavigate(0)}
          aria-label="NeuralVideo home"
          role="link"
          tabIndex={0}
        >
          <div className="w-9 h-9 rounded-xl bg-[#06B6D4]/80 border border-[#06B6D4]/50 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.3)]">
            <svg width="22" height="22" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
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
              <span className="font-mono text-xs font-bold text-[#06B6D4] bg-[#06B6D4]/60 px-2 py-0.5 rounded border border-[#06B6D4]/30">
                v5.0 TIER 2
              </span>
            </div>
            <span className="font-mono text-[10px] text-[#E6E1D5]/80 tracking-widest uppercase">
              MULTIMODAL VIDEO RAG & SEARCH CONSOLE
            </span>
          </div>
        </div>

        {/* Catalog Dropdown */}
        <div className="hidden lg:flex items-center gap-3 bg-black/60 border border-white/15 px-3 py-1.5 rounded-xl">
          <label htmlFor="catalog-select" className="font-mono text-xs font-bold text-[#06B6D4] uppercase tracking-wider sr-only">
            Catalog
          </label>
          <select
            id="catalog-select"
            value={selectedVideo}
            onChange={(e) => onSelectVideo(e.target.value)}
            className="bg-transparent text-white font-mono text-xs outline-none cursor-pointer pr-2 focus:ring-2 focus:ring-[#06B6D4] rounded"
            aria-label="Select video from catalog"
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
              <option disabled className="bg-[#08080a] text-gray-500">
                No videos indexed
              </option>
            )}
          </select>
        </div>

        {/* Ticker Text */}
        <div className="hidden md:block font-mono text-xs text-gray-300 tracking-wider truncate max-w-md" aria-live="polite">
          {tickerText}
        </div>

        {/* Navigation Links */}
        <nav aria-label="Section navigation" className="flex items-center gap-2 font-mono text-xs">
          {[
            { idx: 0, label: "DEMO" },
            { idx: 1, label: "CONSOLE" },
            { idx: 2, label: "XAI PROVENANCE" },
          ].map((item) => (
            <button
              key={item.idx}
              onClick={() => onNavigate(item.idx)}
              aria-current={pageIndex === item.idx ? "page" : undefined}
              aria-label={`Navigate to ${item.label}`}
              className={`px-3 py-1.5 rounded-lg transition-all font-bold focus-visible:ring-2 focus-visible:ring-[#06B6D4] ${
                pageIndex === item.idx
                  ? "bg-[#06B6D4] text-black shadow-[0_0_12px_rgba(6,182,212,0.4)]"
                  : "text-gray-400 hover:text-white hover:bg-white/10"
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </div>

      {/* System Status Bar */}
      <div className="border-t border-white/10 pt-4 flex justify-between items-center text-xs font-mono text-gray-400 bg-[#08080a] px-6">
        <div className="flex items-center gap-2">
          <span>SYSTEM STATUS: </span>
          <span
            className={health?.status === "ok" ? "text-[#10B981]" : "text-[#F59E0B]"}
            role="status"
            aria-live="polite"
          >
            {health?.status === "ok" ? "READY (ONLINE)" : "INITIALIZING..."}
          </span>
        </div>
        <button
          onClick={() => onNavigate(1)}
          className="text-xs font-mono text-[#06B6D4] hover:text-[#10B981] focus-visible:ring-2 focus-visible:ring-[#06B6D4] cursor-pointer"
        >
          LAUNCH INTERACTIVE DEMO &rarr;
        </button>
      </div>
    </header>
  );
}
