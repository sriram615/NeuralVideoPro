"use client";

/**
 * WireframeArcs — Precise SVG geometric circular arch wireframes replicating cthdrl.co.
 * Features sweeping concentric arcs, intersecting vaults, and framing curves.
 */
export default function WireframeArcs({
  variant = "manifesto",
  className = "",
}: {
  variant?: "manifesto" | "terminal" | "gallery" | "xai";
  className?: string;
}) {
  if (variant === "manifesto") {
    return (
      <svg
        className={`pointer-events-none absolute inset-0 w-full h-full ${className}`}
        viewBox="0 0 1440 900"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        preserveAspectRatio="none"
      >
        {/* Main sweeping arch from bottom right to top left */}
        <path
          d="M 1440 900 C 1440 300, 900 50, 0 120"
          stroke="rgba(229, 224, 216, 0.22)"
          strokeWidth="1.2"
        />
        {/* Inner concentric arch */}
        <path
          d="M 1440 900 C 1440 450, 1050 200, 100 200"
          stroke="rgba(229, 224, 216, 0.12)"
          strokeWidth="0.8"
        />
        {/* Giant vault arch sweeping from bottom right center up */}
        <path
          d="M 720 900 C 720 500, 1100 450, 1440 500"
          stroke="rgba(229, 224, 216, 0.18)"
          strokeWidth="1"
        />
        <path
          d="M 720 900 C 720 580, 1020 520, 1440 600"
          stroke="rgba(229, 224, 216, 0.12)"
          strokeWidth="0.8"
        />
        {/* Bottom left vault arch sweeping up */}
        <path
          d="M -100 900 C 200 400, 400 900, 400 900"
          stroke="rgba(229, 224, 216, 0.15)"
          strokeWidth="1"
        />
      </svg>
    );
  }

  if (variant === "terminal") {
    return (
      <svg
        className={`pointer-events-none absolute inset-0 w-full h-full ${className}`}
        viewBox="0 0 1440 900"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        preserveAspectRatio="none"
      >
        {/* Massive framing dome arch over center terminal */}
        <path
          d="M 200 900 C 200 200, 1240 200, 1240 900"
          stroke="rgba(229, 224, 216, 0.28)"
          strokeWidth="1.5"
        />
        <path
          d="M 250 900 C 250 260, 1190 260, 1190 900"
          stroke="rgba(229, 224, 216, 0.12)"
          strokeWidth="0.8"
        />
        {/* Bottom left intersecting fan lines */}
        <path
          d="M 0 900 C 0 700, 150 500, 150 900"
          stroke="rgba(229, 224, 216, 0.18)"
          strokeWidth="1"
        />
        <path
          d="M 0 900 C 0 600, 250 400, 250 900"
          stroke="rgba(229, 224, 216, 0.12)"
          strokeWidth="0.8"
        />
      </svg>
    );
  }

  if (variant === "gallery") {
    return (
      <svg
        className={`pointer-events-none absolute inset-0 w-full h-full ${className}`}
        viewBox="0 0 1440 900"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        preserveAspectRatio="none"
      >
        <path
          d="M 0 900 C 400 300, 1040 300, 1440 900"
          stroke="rgba(229, 224, 216, 0.2)"
          strokeWidth="1.2"
        />
        <path
          d="M 0 450 C 720 100, 1440 450, 1440 450"
          stroke="rgba(229, 224, 216, 0.1)"
          strokeWidth="0.8"
        />
      </svg>
    );
  }

  // xai matrix
  return (
    <svg
      className={`pointer-events-none absolute inset-0 w-full h-full ${className}`}
      viewBox="0 0 1440 900"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      preserveAspectRatio="none"
    >
      <circle
        cx="720"
        cy="450"
        r="400"
        stroke="rgba(229, 224, 216, 0.12)"
        strokeWidth="1"
      />
      <circle
        cx="720"
        cy="450"
        r="250"
        stroke="rgba(229, 224, 216, 0.08)"
        strokeWidth="0.8"
      />
    </svg>
  );
}
