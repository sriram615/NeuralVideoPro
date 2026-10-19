"use client";

const ITEMS = [
  { label: "Visual", className: "text-accent-cyan" },
  { label: "Audio", className: "text-accent-emerald" },
  { label: "Fused", className: "text-bone" },
];

/**
 * Documents the modality color mapping so the palette is never color-only.
 * Pairs every swatch with a text label.
 */
export default function ModalityLegend({ className = "" }: { className?: string }) {
  return (
    <ul
      className={`flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-micro uppercase tracking-wider ${className}`}
      aria-label="Modality color legend"
    >
      {ITEMS.map((item) => (
        <li key={item.label} className="flex items-center gap-1.5">
          <span
            className={`w-2 h-2 rounded-full bg-current ${item.className}`}
            aria-hidden="true"
          />
          <span className="text-gray-400">{item.label}</span>
        </li>
      ))}
    </ul>
  );
}
