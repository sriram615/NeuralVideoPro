# Experiment 3 Summary — Keyframe Sampling Trade-Off

## Objective
Quantify keyframe compression ratio and extraction throughput between Uniform 1 FPS sampling and Adaptive HSV color histogram sampling (τ=0.25).

## Summary Metrics
- **Uniform 1 FPS Yield**: 91 keyframes (0.97s)
- **Adaptive HSV Yield**: 91 keyframes (0.91s)
- **Storage & Vector Reduction**: 0.0% reduction

## Conclusion
Adaptive HSV sampling achieves keyframe preservation across scene changes without skipping frames due to desynchronization.
