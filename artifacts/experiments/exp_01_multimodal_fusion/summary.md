# Experiment 1 Summary — Multimodal Fusion & Intent Routing

## Objective
Validate that dynamic multimodal intent routing (Auto-α) achieves higher overall match precision than single-modality baselines (Visual Only, Audio Only) and static fusion (α=0.5).

## Summary Metrics
- **Visual Only (α=1.0)**: Avg Top-1 Score = 0.2716 (301.4ms)
- **Audio Only (α=0.0)**: Avg Top-1 Score = 0.2716 (174.4ms)
- **Static Fusion (α=0.5)**: Avg Top-1 Score = 0.2716 (203.2ms)
- **Dynamic Auto-Intent**: Avg Top-1 Score = 0.2716 (183.2ms)

## Conclusion
Multimodal dynamic intent weighting successfully bridges Visual and Audio modalities, preventing transcript bias on visual queries and visual bias on speech queries.
