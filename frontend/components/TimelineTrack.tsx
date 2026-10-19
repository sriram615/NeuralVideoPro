"use client";

import type { SearchResultItem } from "@/lib/api";

function formatTimestamp(seconds: number): string {
  const total = Math.round(seconds);
  const mins = Math.floor(total / 60);
  const secs = total % 60;
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

interface TimelineTrackProps {
  results: SearchResultItem[];
  selectedIndex: number;
  /** Real duration of the source video in seconds, when the player reports it. */
  durationSec?: number;
  onSelect: (index: number, timestamp: number) => void;
}

export default function TimelineTrack({
  results,
  selectedIndex,
  durationSec = 0,
  onSelect,
}: TimelineTrackProps) {
  const maxTimestampInResults =
    results.length > 0
      ? Math.max(...results.map((r) => Number(r.payload.timestamp) || 0))
      : 0;

  // Prefer the duration reported by the <video> element; otherwise derive the
  // track span from the retrieved hits. Fall back to 1s only so the marker
  // math never divides by zero before the player has loaded metadata.
  const maxDurationSec =
    durationSec > 0
      ? durationSec
      : maxTimestampInResults > 0
      ? maxTimestampInResults + 30
      : 1;
  const hasDuration = durationSec > 0 || maxTimestampInResults > 0;

  return (
    <div className="z-10 my-3 p-4 bg-black/80 backdrop-blur-2xl border border-accent-cyan/50 rounded-2xl space-y-2 font-mono">
      <div className="flex items-center justify-between text-xs text-gray-300">
        <span className="font-bold text-accent-cyan tracking-wider">RETRIEVAL TIMELINE TRACK</span>
        <span className="text-gray-400">
          VIDEO DURATION: 0:00 &rarr; {hasDuration ? formatTimestamp(maxDurationSec) : "--:--"}
        </span>
      </div>

      <div className="relative w-full h-8 bg-white/5 rounded-xl border border-white/10 flex items-center px-2">
        <div className="w-full h-1.5 bg-gradient-to-r from-accent-cyan/40 via-accent-emerald/40 to-accent-cyan/40 rounded-full relative">
          {results.map((r, idx) => {
            const ts = Number(r.payload.timestamp) || 0;
            const posPct = Math.min(96, Math.max(2, (ts / maxDurationSec) * 100));
            const isSelected = idx === selectedIndex;
            const tsStr = `${Math.floor(ts / 60)
              .toString()
              .padStart(2, "0")}:${Math.floor(ts % 60)
              .toString()
              .padStart(2, "0")}`;

            return (
              <button
                key={String(r.id)}
                type="button"
                onClick={() => onSelect(idx, ts)}
                aria-label={`Result ${idx + 1} at ${tsStr}, ${r.xai.fused_score_pct.toFixed(1)}% match`}
                style={{ left: `${posPct}%` }}
                className={`absolute top-1/2 -translate-y-1/2 -translate-x-1/2 px-2 py-0.5 rounded-full font-mono text-micro font-black transition-all cursor-pointer shadow-lg focus-visible:ring-2 focus-visible:ring-accent-cyan ${
                  isSelected
                    ? "bg-accent-cyan text-black scale-125 z-20 border-2 border-white shadow-[0_0_12px_rgba(6,182,212,0.8)]"
                    : "bg-black text-accent-cyan/80 border border-accent-cyan/60 hover:scale-110 z-10"
                }`}
              >
                #{r.rank}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
