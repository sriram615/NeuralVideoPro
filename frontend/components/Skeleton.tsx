"use client";

interface SkeletonProps {
  className?: string;
  height?: string | number;
  width?: string | number;
}

export default function Skeleton({
  className,
  height = "1rem",
  width = "100%",
}: SkeletonProps) {
  return (
    <div
      className={`skeleton ${className}`}
      style={{ height: typeof height === "number" ? `${height}px` : height, width: typeof width === "number" ? `${width}px` : width }}
      aria-hidden="true"
    />
  );
}

interface SkeletonTextProps {
  count?: number;
  className?: string;
}

export function SkeletonText({ count = 3, className }: SkeletonTextProps) {
  return (
    <div className={className}>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="skeleton mb-2"
          style={{ height: "0.75rem", width: i === count - 1 ? "60%" : "100%" }}
          aria-hidden="true"
        />
      ))}
    </div>
  );
}
