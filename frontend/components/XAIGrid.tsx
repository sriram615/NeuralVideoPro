"use client";

import type { SearchResultItem } from "@/lib/api";

interface XAIGridProps {
  item: SearchResultItem;
}

export default function XAIGrid({ item }: XAIGridProps) {
  return (
    <div className="p-6 bg-black/90 backdrop-blur-2xl border border-accent-emerald/40 rounded-2xl space-y-4 font-mono">
      <span className="text-xs font-bold text-accent-emerald uppercase tracking-wider block">
        TECHNICAL ML SCORE CALCULATIONS
      </span>
      <div className="grid grid-cols-3 gap-4 text-center">
        <div className="p-4 bg-white/5 rounded-xl border border-white/10">
          <span className="text-[10px] text-gray-400 uppercase block">FUSED SCORE</span>
          <span className="text-2xl font-black text-white">{item.xai.fused_score_pct.toFixed(1)}%</span>
        </div>
        <div className="p-4 bg-accent-cyan/60 rounded-xl border border-accent-cyan/40">
          <span className="text-[10px] text-accent-cyan uppercase block">VISUAL (CLIP)</span>
          <span className="text-2xl font-black text-accent-cyan/90">{item.xai.visual_similarity_pct.toFixed(1)}%</span>
        </div>
        <div className="p-4 bg-accent-emerald/60 rounded-xl border border-accent-emerald/40">
          <span className="text-[10px] text-accent-emerald uppercase block">AUDIO (WHISPER)</span>
          <span className="text-2xl font-black text-accent-emerald/90">{item.xai.audio_similarity_pct.toFixed(1)}%</span>
        </div>
      </div>

      {/* XAI Attribution Details */}
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-white/5 rounded-xl border border-white/10">
          <span className="text-[10px] text-gray-400 uppercase block">PRIMARY DRIVER</span>
          <div className="flex items-center gap-2 mt-2">
            <span aria-hidden="true">{item.xai.primary_driver_emoji}</span>
            <span className="text-xs font-mono font-bold text-accent-cyan">
              {item.xai.primary_driver}
            </span>
          </div>
          <p className="text-[10px] text-gray-500 mt-2">{item.xai.fusion_formula}</p>
        </div>
        <div className="p-4 bg-white/5 rounded-xl border border-white/10">
          <span className="text-[10px] text-gray-400 uppercase block">RRF SCORE</span>
          <span className="text-2xl font-mono font-bold text-white">
            {item.xai.rrf_score?.toFixed(6) ?? "N/A"}
          </span>
          <p className="text-[10px] text-gray-500 mt-2">
            Confidence: <span className="font-bold capitalize">{item.xai.confidence_tier}</span>
          </p>
        </div>
      </div>
    </div>
  );
}
