"use client";

import type { SearchResultItem } from "@/lib/api";
import { staticVideoUrl } from "@/lib/api";

function resolveVideoFilename(raw: string | undefined | null): string {
  if (!raw) return "";
  if (raw.endsWith(".mp4") || raw.endsWith(".MOV") || raw.endsWith(".mkv") || raw.endsWith(".webm")) {
    return raw;
  }
  return `${raw}.mp4`;
}

interface VideoPlayerProps {
  item: SearchResultItem;
  formattedTime: string;
  timestampSec: number;
  confidenceBand: string;
}

export default function VideoPlayer({
  item,
  formattedTime,
  timestampSec,
  confidenceBand,
}: VideoPlayerProps) {
  const confidenceColor =
    confidenceBand === "HIGH"
      ? "bg-[#10B981]/60 text-[#10B981] border-[#10B981]/50"
      : confidenceBand === "MEDIUM"
      ? "bg-[#F59E0B]/60 text-[#F59E0B] border-[#F59E0B]/50"
      : "bg-slate-900 text-slate-300 border-slate-700";

  const filename =
    (item.payload.file_name as string) ||
    (item.payload.video_id as string) ||
    "";

  return (
    <div className="p-6 bg-black/90 backdrop-blur-2xl border-2 border-[#06B6D4]/50 rounded-2xl shadow-2xl space-y-4">
      <div className="flex items-center justify-between border-b border-white/15 pb-3">
        <span className="font-mono text-xs font-bold text-[#06B6D4] uppercase tracking-widest">
          SYNCHRONIZED VIDEO PLAYER
        </span>
        <span className={`font-mono text-xs px-3 py-1 rounded-full font-bold border ${confidenceColor}`}>
          CONFIDENCE: {confidenceBand}
        </span>
      </div>

      <div className="w-full bg-black rounded-xl overflow-hidden border border-white/20 shadow-2xl relative">
        <video
          controls
          className="w-full max-h-[380px] object-contain"
          src={staticVideoUrl(resolveVideoFilename(filename))}
        />
      </div>

      <div className="flex flex-wrap items-center justify-between gap-4 font-mono text-xs bg-black/80 p-4 rounded-xl border border-white/10">
        <span className="text-gray-300">
          MATCH TIMESTAMP: <strong className="text-[#06B6D4] text-sm">{formattedTime} ({timestampSec.toFixed(1)}s)</strong>
        </span>
        <button
          className="px-6 py-3 bg-[#06B6D4] hover:bg-[#10B981] text-black font-mono font-black text-sm rounded-xl transition-all shadow-md cursor-pointer flex items-center gap-2 focus-visible:ring-2 focus-visible:ring-[#06B6D4]"
        >
          &nbsp;JUMP TO TIMESTAMP [{formattedTime}]
        </button>
      </div>
    </div>
  );
}
