"use client";

import { useState } from "react";
import type { SearchResultItem } from "@/lib/api";
import { staticFrameUrl } from "@/lib/api";
import Skeleton from "@/components/Skeleton";

interface ResultCardProps {
  item: SearchResultItem;
  rank: number;
  isSelected: boolean;
  onSelect: (rank: number) => void;
}

/** Mirrors the backend's `min_confidence_threshold` (pipeline.search). */
const MATCH_THRESHOLD = 0.15;

function tierColor(tier: string | undefined): string {
  if (tier === "HIGH") return "text-accent-emerald";
  if (tier === "MEDIUM") return "text-accent-amber";
  return "text-gray-500";
}

export default function ResultCard({
  item,
  rank,
  isSelected,
  onSelect,
}: ResultCardProps) {
  const payload = item.payload;
  const [frameLoaded, setFrameLoaded] = useState(false);
  const [frameFailed, setFrameFailed] = useState(false);

  const rTimestampSec = (payload.timestamp as number) ?? 0;
  const rTimeStr = `${Math.floor(rTimestampSec / 60)
    .toString()
    .padStart(2, "0")}:${Math.floor(rTimestampSec % 60)
    .toString()
    .padStart(2, "0")}`;

  const frameUrl = payload.frame_path ? staticFrameUrl(String(payload.frame_path)) : "";
  const tier = item.xai.confidence_tier;

  const modalityRows = [
    { label: "Visual keyframe match", score: item.visual_score, pct: item.xai.visual_similarity_pct, sr: "Visual context matched target keyframe" },
    { label: "Transcript alignment", score: item.audio_score, pct: item.xai.audio_similarity_pct, sr: "Transcript aligned at target timestamp" },
  ];

  return (
    <div
      onClick={() => onSelect(rank)}
      role="button"
      tabIndex={0}
      aria-pressed={isSelected}
      aria-label={`Result ${rank}: ${payload.video_id} at ${rTimeStr}, ${item.xai.fused_score_pct.toFixed(1)}% fused match, ${tier} confidence`}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect(rank);
        }
      }}
      className={`p-4 bg-black/80 backdrop-blur-md rounded-2xl border-2 transition-all cursor-pointer space-y-3 focus-visible:ring-2 focus-visible:ring-accent-cyan ${
        isSelected
          ? "border-accent-cyan shadow-[0_0_20px_rgba(6,182,212,0.3)] bg-accent-cyan/10"
          : "border-white/15 hover:border-white/40"
      }`}
    >
      <div className="flex items-center justify-between gap-2 font-mono text-xs">
        <span
          className={`font-black px-2.5 py-1 rounded border border-accent-cyan/40 ${
            isSelected ? "bg-accent-cyan text-black" : "bg-accent-cyan/10 text-accent-cyan"
          }`}
        >
          RANK #{rank}
        </span>
        <span className="font-bold text-white">TIMESTAMP: {rTimeStr}</span>
        <span className={`font-black ${tierColor(tier)}`}>
          {item.xai.fused_score_pct.toFixed(1)}% MATCH
        </span>
      </div>

      {/* Frame Preview */}
      <div className="w-full h-40 bg-black rounded-xl overflow-hidden border border-white/20 relative">
        {frameUrl && !frameFailed ? (
          <>
            {!frameLoaded && (
              <Skeleton className="absolute inset-0" height="100%" width="100%" />
            )}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={frameUrl}
              alt={`Keyframe at ${rTimeStr} from ${payload.video_id}`}
              loading="lazy"
              onLoad={() => setFrameLoaded(true)}
              onError={() => setFrameFailed(true)}
              className="w-full h-full object-cover"
            />
          </>
        ) : (
          <div className="w-full h-full flex items-center justify-center text-xs font-mono text-gray-500">
            KEYFRAME PREVIEW UNAVAILABLE
          </div>
        )}
        <div className="absolute bottom-2 right-2 bg-black/90 px-3 py-1 rounded font-mono text-xs font-bold text-accent-cyan border border-accent-cyan/40">
          {rTimeStr}
        </div>
      </div>

      {/* Judge diagnostics — only claim a match when the score clears threshold */}
      <div className="space-y-1 font-mono text-[11px] pt-1 border-t border-white/10">
        {modalityRows.map((row) => {
          const matched = row.score > MATCH_THRESHOLD;
          return (
            <div key={row.label} className={`flex items-center gap-2 ${matched ? "text-accent-emerald" : "text-gray-500"}`}>
              <span aria-hidden="true">{matched ? "\u2713" : "\u2013"}</span>
              <span className="sr-only">{matched ? row.sr : `No ${row.label.toLowerCase()}`}</span>
              <span>{row.pct.toFixed(1)}%</span>
              <span className="text-gray-400">{row.label}</span>
            </div>
          );
        })}
        <div className="flex items-center gap-2">
          <span className={tierColor(tier)} aria-hidden="true">&#9679;</span>
          <span className="text-gray-400">Confidence</span>
          <span className={`font-bold ${tierColor(tier)}`}>{tier ?? "N/A"}</span>
        </div>
      </div>
    </div>
  );
}
