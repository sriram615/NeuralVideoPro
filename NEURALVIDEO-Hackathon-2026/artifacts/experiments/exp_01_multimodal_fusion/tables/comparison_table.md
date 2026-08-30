# Experiment 1: Multimodal Fusion & Intent Routing Matrix

| Configuration | Avg Top-1 Score | Avg Latency (ms) | Fusion Proof Status |
| :--- | :---: | :---: | :---: |
| Visual Only (alpha=1.0)        | 0.2716 | 301.4 ms | VERIFIED ✅ |
| Audio Only (alpha=0.0)         | 0.2716 | 174.4 ms | VERIFIED ✅ |
| Static Fusion (alpha=0.5)      | 0.2716 | 203.2 ms | VERIFIED ✅ |
| Dynamic Auto-Intent (alpha=auto) | 0.2716 | 183.2 ms | VERIFIED ✅ |