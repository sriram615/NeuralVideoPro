"use client";

import { useRef } from "react";
import type { SearchResultItem, VideoCatalogItem } from "@/lib/api";
import { resolveVideoFilename, staticVideoUrl } from "@/lib/api";

interface VideoPlayerProps {
  item: SearchResultItem;
  formattedTime: string;
  timestampSec: number;
  confidenceBand: string;
  /** Corpus catalog used to map a result's hashed video_id to a real file. */
  catalog?: VideoCatalogItem[] | null;
  /** Reports the real duration of the loaded source so the timeline can scale. */
  onDurationChange?: (durationSec: number) => void;
}

export default function VideoPlayer({
  item,
  formattedTime,
  timestampSec,
  confidenceBand,
  catalog = null,
  onDurationChange,
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  const confidenceColor =
    confidenceBand === "HIGH"
      ? "bg-accent-emerald/10 text-accent-emerald border-accent-emerald/50"
      : confidenceBand === "MEDIUM"
      ? "bg-accent-amber/10 text-accent-amber border-accent-amber/50"
      : "bg-slate-900 text-slate-300 border-slate-700";

  const filename = resolveVideoFilename(
    (item.payload.file_name as string) || (item.payload.video_path as string) || "",
    item.payload.video_id as string,
    catalog,
  );

  const jumpToTimestamp = () => {
    const el = videoRef.current;
    if (!el) return;
    el.currentTime = timestampSec;
    el.play().catch(() => {});
  };

  return (
    <div className="p-6 bg-black/90 backdrop-blur-2xl border-2 border-accent-cyan/50 rounded-2xl shadow-2xl space-y-4">
      <div className="flex items-center justify-between border-b border-white/15 pb-3">
        <span className="font-mono text-xs font-bold text-accent-cyan uppercase tracking-widest">
          SYNCHRONIZED VIDEO PLAYER
        </span>
        <span className={`font-mono text-xs px-3 py-1 rounded-full font-bold border ${confidenceColor}`}>
          CONFIDENCE: {confidenceBand}
        </span>
      </div>

      <div className="w-full bg-black rounded-xl overflow-hidden border border-white/20 shadow-2xl relative">
        {filename ? (
          <video
            ref={videoRef}
            controls
            className="w-full max-h-[380px] object-contain"
            src={staticVideoUrl(filename)}
            onLoadedMetadata={(e) => onDurationChange?.(e.currentTarget.duration)}
          />
        ) : (
          <div className="flex flex-col items-center justify-center gap-2 h-[220px] px-6 text-center">
            <span className="font-mono text-xs text-gray-400 uppercase tracking-widest">
              VIDEO SOURCE UNAVAILABLE
            </span>
            <span className="font-mono text-[11px] text-gray-500">
              This match has no catalogued file on the server. Results and XAI attribution are still valid.
            </span>
          </div>
        )}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-4 font-mono text-xs bg-black/80 p-4 rounded-xl border border-white/10">
        <span className="text-gray-300">
          MATCH TIMESTAMP: <strong className="text-accent-cyan text-sm">{formattedTime} ({timestampSec.toFixed(1)}s)</strong>
        </span>
        <button
          type="button"
          onClick={jumpToTimestamp}
          disabled={!filename}
          className="px-6 py-3 bg-accent-cyan hover:bg-accent-emerald disabled:opacity-40 disabled:cursor-not-allowed text-black font-mono font-black text-sm rounded-xl transition-all shadow-md cursor-pointer flex items-center gap-2 focus-visible:ring-2 focus-visible:ring-accent-cyan"
        >
          &nbsp;JUMP TO TIMESTAMP [{formattedTime}]
        </button>
      </div>
    </div>
  );
}
