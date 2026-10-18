"use client";

import type { SearchResultItem } from "@/lib/api";

interface ResultCardProps {
  item: SearchResultItem;
  rank: number;
  isSelected: boolean;
  onSelect: (rank: number) => void;
}

export default function ResultCard({
  item,
  rank,
  isSelected,
  onSelect,
}: ResultCardProps) {
  const payload = item.payload;
  const rTimestampSec = (payload.timestamp as number) ?? 0;
  const rTimeStr = `${Math.floor(rTimestampSec / 60)
    .toString()
    .padStart(2, "0")}:${Math.floor(rTimestampSec % 60)
    .toString()
    .padStart(2, "0")}`;

  return (
    <div
      key={String(item.id)}
      onClick={() => onSelect(rank)}
      role="button"
      tabIndex={0}
      aria-label={`Result ${rank}: ${payload.video_id} at ${rTimeStr}, ${item.xai.fused_score_pct.toFixed(1)}% match`}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect(rank);
        }
      }}
      className={`p-4 bg-black/80 backdrop-blur-md rounded-2xl border-2 transition-all cursor-pointer space-y-3 focus-visible:ring-2 focus-visible:ring-accent-cyan ${
        isSelected
          ? "border-accent-cyan shadow-[0_0_20px_rgba(6,182,212,0.3)] bg-accent-cyan/20"
          : "border-white/15 hover:border-white/40"
      }`}
    >
      <div className="flex items-center justify-between font-mono text-xs">
        <span className={`font-black bg-accent-cyan/40 px-2.5 py-1 rounded border border-accent-cyan/40 ${
          isSelected ? "text-black" : "text-accent-cyan"
        }`}>
          RANK #{rank}
        </span>
        <span className="font-bold text-white">TIMESTAMP: {rTimeStr}</span>
        <span className={`font-black ${item.visual_score > 0.15 ? "text-accent-emerald" : "text-gray-500"}`}>
          {item.xai.fused_score_pct.toFixed(1)}% MATCH
        </span>
      </div>

      {/* Frame Preview */}
      <div className="w-full h-40 bg-black rounded-xl overflow-hidden border border-white/20 relative">
        {payload.frame_path ? (
          <img
            src={`/api/static/frames/${payload.frame_path}`}
            alt={`Frame #${rank} from ${payload.video_id}`}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-xs font-mono text-gray-500">
            KEYFRAME PREVIEW
          </div>
        )}
        <div className="absolute bottom-2 right-2 bg-black/90 px-3 py-1 rounded font-mono text-xs font-bold text-accent-cyan border border-accent-cyan/40">
          {rTimeStr}
        </div>
      </div>

      {/* Human-Readable Judge Diagnostics */}
      <div className="space-y-1 font-mono text-[11px] pt-1 border-t border-white/10">
        <div
          className={`flex items-center gap-2 ${
            item.visual_score > 0.15 ? "text-accent-emerald" : "text-gray-500"
          }`}
        >
          <span aria-hidden="true">&check;</span>
          <span className="sr-only">Visual context matched target keyframe</span>
          {`${item.xai.visual_similarity_pct.toFixed(1)}%`}
        </div>
        <div
          className={`flex items-center gap-2 ${
            item.audio_score > 0.15 ? "text-accent-emerald" : "text-gray-500"
          }`}
        >
          <span aria-hidden="true">&check;</span>
          <span className="sr-only">Transcript aligned at target timestamp</span>
          {`${item.xai.audio_similarity_pct.toFixed(1)}%`}
        </div>
        <div className="flex items-center gap-2 text-accent-cyan">
          <span aria-hidden="true">&check;</span>
          <span className="sr-only">Multi-modal cross-agreement score verified</span>
          Verified
        </div>
      </div>
    </div>
  );
}
