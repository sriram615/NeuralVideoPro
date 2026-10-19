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

  const goHome = () => onNavigate(0);

  return (
    <header
      className="fixed top-0 left-0 right-0 z-40 bg-void/90 backdrop-blur-2xl border-b border-white/10"
      aria-label="Main navigation"
    >
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
        {/* Brand & Logo */}
        <div
          className="flex items-center gap-3 cursor-pointer group"
          onClick={goHome}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              goHome();
            }
          }}
          aria-label="NeuralVideo home"
          role="link"
          tabIndex={0}
        >
          <div className="w-8 h-8 rounded-xl bg-accent-cyan/80 border border-accent-cyan/50 flex items-center justify-center shadow-[0_0_12px_rgba(6,182,212,0.3)]">
            <svg width="20" height="20" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <path d="M 16 4 C 8 4, 4 12, 4 28" stroke="var(--color-accent-emerald)" strokeWidth="2.5" strokeLinecap="round" />
              <path d="M 16 4 C 24 4, 28 12, 28 28" stroke="var(--color-accent-cyan)" strokeWidth="2.5" strokeLinecap="round" />
              <path d="M 16 12 C 10 12, 8 18, 8 28" stroke="var(--color-bone)" strokeWidth="1.5" />
              <path d="M 16 12 C 22 12, 24 18, 24 28" stroke="var(--color-bone)" strokeWidth="1.5" />
              <line x1="4" y1="28" x2="28" y2="28" stroke="var(--color-bone)" strokeWidth="2" />
            </svg>
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-mono font-black text-white text-sm tracking-wider">NEURALVIDEO</span>
              <span className="font-mono text-micro font-bold text-black bg-accent-cyan px-1.5 py-0.5 rounded border border-accent-cyan/30">
                v5.0
              </span>
            </div>
            <span className="font-mono text-micro text-bone/80 tracking-widest uppercase">
              MULTIMODAL VIDEO RAG & SEARCH
            </span>
          </div>
        </div>

        {/* Ticker Text */}
        <div className="hidden md:block font-mono text-micro text-gray-300 tracking-wider truncate max-w-md" aria-live="polite">
          {tickerText}
        </div>

        {/* Catalog Dropdown */}
        <div className="hidden md:flex items-center gap-2 bg-black/60 border border-white/15 px-2.5 py-1.5 rounded-xl">
          <label htmlFor="catalog-select" className="font-mono text-micro font-bold text-accent-cyan uppercase tracking-wider sr-only">
            Catalog
          </label>
          <select
            id="catalog-select"
            value={selectedVideo}
            onChange={(e) => onSelectVideo(e.target.value)}
            className="bg-transparent text-white font-mono text-micro outline-none cursor-pointer pr-2 focus:ring-2 focus:ring-accent-cyan rounded"
            aria-label="Select video from catalog"
          >
            <option value="all" className="bg-void text-white">
              ALL INDEXED VIDEOS ({corpusStats?.total_points || 0} POINTS)
            </option>
            {corpusStats?.video_catalog && corpusStats.video_catalog.length > 0 ? (
              corpusStats.video_catalog.map((item) => (
                <option key={item.filename} value={item.filename} className="bg-void text-white">
                  {item.title} ({item.size_mb} MB)
                </option>
              ))
            ) : (
              <option disabled className="bg-void text-gray-500">
                No videos indexed
              </option>
            )}
          </select>
        </div>

        {/* Navigation Links */}
        <nav aria-label="Section navigation" className="hidden md:flex items-center gap-1.5 font-mono text-micro">
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
              className={`px-2 py-1 rounded-lg transition-all font-bold focus-visible:ring-2 focus-visible:ring-accent-cyan ${
                pageIndex === item.idx
                  ? "bg-accent-cyan text-black shadow-[0_0_12px_rgba(6,182,212,0.4)]"
                  : "text-gray-400 hover:text-white hover:bg-white/10"
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>

        {/* Mobile menu button */}
        <button
          onClick={() => setCatalogOpen(!catalogOpen)}
          className="md:hidden p-2 rounded-lg bg-black/60 border border-white/15 hover:bg-white/10 focus-visible:ring-2 focus-visible:ring-accent-cyan"
          aria-label="Open catalog menu"
          aria-expanded={catalogOpen}
        >
          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        {/* Mobile Catalog Dropdown */}
        {catalogOpen && (
          <div className="md:hidden w-full bg-black/90 border border-white/15 rounded-xl p-3 mt-2">
            <label htmlFor="mobile-catalog-select" className="font-mono text-micro font-bold text-accent-cyan uppercase tracking-wider block mb-1">
              Catalog
            </label>
            <select
              id="mobile-catalog-select"
              value={selectedVideo}
              onChange={(e) => {
                onSelectVideo(e.target.value);
                setCatalogOpen(false);
              }}
              className="w-full bg-transparent text-white font-mono text-micro outline-none focus:ring-2 focus:ring-accent-cyan rounded"
              aria-label="Select video from catalog"
            >
              <option value="all" className="bg-void text-white">
                ALL INDEXED VIDEOS ({corpusStats?.total_points || 0} POINTS)
              </option>
              {corpusStats?.video_catalog && corpusStats.video_catalog.length > 0 ? (
                corpusStats.video_catalog.map((item) => (
                  <option key={item.filename} value={item.filename} className="bg-void text-white">
                    {item.title} ({item.size_mb} MB)
                  </option>
                ))
              ) : (
                <option disabled className="bg-void text-gray-500">
                  No videos indexed
                </option>
              )}
            </select>
          </div>
        )}
      </div>

      {/* System Status Bar */}
      <div className="border-t border-white/10 pt-3 flex justify-between items-center text-xs font-mono text-gray-400 bg-void px-4">
        <div className="flex items-center gap-1.5">
          <span>SYSTEM STATUS: </span>
          <span
            className={health?.status === "ok" ? "text-accent-emerald" : "text-accent-amber"}
            role="status"
            aria-live="polite"
          >
            {health?.status === "ok" ? "READY (ONLINE)" : "INITIALIZING..."}
          </span>
        </div>
        <button
          onClick={() => onNavigate(1)}
          className="text-xs font-mono text-accent-cyan hover:text-accent-emerald focus-visible:ring-2 focus-visible:ring-accent-cyan"
        >
          LAUNCH INTERACTIVE DEMO &rarr;
        </button>
      </div>
    </header>
  );
}
