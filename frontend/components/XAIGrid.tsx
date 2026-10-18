"use client";

import type { SearchResultItem } from "@/lib/api";

interface XAIGridProps {
  item: SearchResultItem;
}

export default function XAIGrid({ item }: XAIGridProps) {
  return (
    <div className="p-6 bg-black/90 backdrop-blur-2xl border border-[#10B981]/40 rounded-2xl space-y-4 font-mono">
      <span className="text-xs font-bold text-[#10B981] uppercase tracking-wider block">
        TECHNICAL ML SCORE CALCULATIONS
      </span>
      <div className="grid grid-cols-3 gap-4 text-center">
        <div className="p-4 bg-white/5 rounded-xl border border-white/10">
          <span className="text-[10px] text-gray-400 uppercase block">FUSED SCORE</span>
          <span className="text-2xl font-black text-white">{item.xai.fused_score_pct.toFixed(1)}%</span>
        </div>
        <div className="p-4 bg-[#06B6D4]/60 rounded-xl border border-[#06B6D4]/40">
          <span className="text-[10px] text-[#06B6D4] uppercase block">VISUAL (CLIP)</span>
          <span className="text-2xl font-black text-[#06B6D4]/90">{item.xai.visual_similarity_pct.toFixed(1)}%</span>
        </div>
        <div className="p-4 bg-[#10B981]/60 rounded-xl border border-[#10B981]/40">
          <span className="text-[10px] text-[#10B981] uppercase block">AUDIO (WHISPER)</span>
          <span className="text-2xl font-black text-[#10B981]/90">{item.xai.audio_similarity_pct.toFixed(1)}%</span>
        </div>
      </div>

      {/* XAI Attribution Details */}
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-white/5 rounded-xl border border-white/10">
          <span className="text-[10px] text-gray-400 uppercase block">PRIMARY DRIVER</span>
          <div className="flex items-center gap-2 mt-2">
            <span aria-hidden="true">{item.xai.primary_driver_emoji}</span>
            <span className="text-xs font-mono font-bold text-[#06B6D4]">
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
