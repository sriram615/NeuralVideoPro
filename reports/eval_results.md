# System Pilot Evaluation & Benchmark Report

**Project:** Semantic Video Retrieval Engine
**Evaluation Date:** July 27, 2026 (systems metrics) / pending (retrieval-quality metrics — see below)
**Database:** Local Embedded Qdrant (`video_intelligence` — 1,903 vector points)
**Hardware Execution:** Mac CPU Bounded (`OMP_NUM_THREADS=2`, `MKL_NUM_THREADS=2`)

---

## What this report covers, and what it doesn't

This report measures **system health**: does the pipeline run without crashing, are vectors correctly normalized, is latency acceptable. All of that is genuinely verified below.

It does **not** measure **retrieval quality** — whether a search actually returns the right video for a given query. That requires precision/recall/MRR against a ground-truth set, which this project has (`tests/ground_truth_benchmark.json`, 30 labeled queries, plus `eval_suite.py`/`scripts/evaluation/eval_suite.py` which computes Precision@5, Recall@5, and MRR@5 against it). That evaluation script has been run, but its numeric output was never captured into a report. Until it is, treat retrieval quality as unverified — the metrics below are not a substitute for it, and the "production ready" framing this report previously carried was not supported by them.

**Known issue:** spot-checking ground-truth entry `v_01` ("whiteboard architecture diagram explanation" → `sports_news_breakdown_372460f80e66`) against the actual extracted frames around the labeled timestamp shows a show title card and a laughing host in a leather jacket — no whiteboard or diagram anywhere in frame. That label does not hold up on inspection. The ground-truth set needs a manual re-verification pass (watch or spot-check each of the 30 labeled clips against its query) before the precision/recall numbers it produces can be trusted.

---

## Systems Metrics (verified, July 27 2026 run)

- **Total Test Configurations:** 14 evaluation runs across Mode A, Mode B, and Mode C.
- **Average Query Latency:** 165.8 ms
- **Maximum Query Latency:** 271.6 ms
- **Score Integrity:** 100% of scores within bounds [0.0, 1.0], zero `NaN`, `Inf`, or `KeyError` exceptions across the 14 runs.
- **L2 Vector Normalization:** Verified (‖v‖₂ = 1.000000 for all text/visual query vectors).

## Benchmark Precision & Similarity Matrix

| Operational Mode | Query String | Alpha (α) | Latency (ms) | Fused Score | Visual Score | Audio Score | Matched Video & Timestamp | Matched Speech Excerpt |
|---|---|---|---|---|---|---|---|---|
| MODE A (Visual) | `blue planet earth from space` | 1.00 | 271.6 ms | 0.2518 | 0.2518 | 0.7415 | `nasa_space_flight_news_a485d4f58b49` @ 00:10 | "Did you know astronauts' bodies change in space when my body" |
| MODE A (Visual) | `blue planet earth from space` | 0.80 | 169.4 ms | 0.3497 | 0.2518 | 0.7415 | `nasa_space_flight_news_a485d4f58b49` @ 00:10 | "Did you know astronauts' bodies change in space when my body" |
| MODE A (Visual) | `blue planet earth from space` | 0.50 | 161.2 ms | 0.4967 | 0.2518 | 0.7415 | `nasa_space_flight_news_a485d4f58b49` @ 00:10 | "Did you know astronauts' bodies change in space when my body" |
| MODE A (Visual) | `person in dark suit standing at podium` | 1.00 | 160.6 ms | 0.2914 | 0.2914 | 0.0000 | `obama_farewell_speech_353ca4868dfb` @ 00:03 | "news video footage scene" |
| MODE A (Visual) | `person in dark suit standing at podium` | 0.80 | 145.7 ms | 0.2331 | 0.2914 | 0.0000 | `obama_farewell_speech_353ca4868dfb` @ 00:03 | "news video footage scene" |
| MODE A (Visual) | `person in dark suit standing at podium` | 0.50 | 158.1 ms | 0.3367 | 0.0000 | 0.6735 | `ecns_opening_speech_665f4791a4e8` @ 02:58 | "news video footage scene" |
| MODE B (Speech/Audio) | `astronauts bodies change in space` | 0.00 | 159.4 ms | 0.9399 | 0.2985 | 0.9399 | `nasa_space_flight_news_a485d4f58b49` @ 00:11 | "Did you know astronauts' bodies change in space when my body" |
| MODE B (Speech/Audio) | `astronauts bodies change in space` | 0.20 | 164.4 ms | 0.8116 | 0.2985 | 0.9399 | `nasa_space_flight_news_a485d4f58b49` @ 00:11 | "Did you know astronauts' bodies change in space when my body" |
| MODE B (Speech/Audio) | `astronauts bodies change in space` | 0.50 | 160.2 ms | 0.6192 | 0.2985 | 0.9399 | `nasa_space_flight_news_a485d4f58b49` @ 00:11 | "Did you know astronauts' bodies change in space when my body" |
| MODE B (Speech/Audio) | `retaliate against Israel` | 0.00 | 168.5 ms | 0.9538 | 0.2442 | 0.9538 | `middle_east_news_report_0a56c7e5359d` @ 00:06 | "I don't really see too many possibilities of retaliation aga" |
| MODE B (Speech/Audio) | `retaliate against Israel` | 0.20 | 154.2 ms | 0.8119 | 0.2442 | 0.9538 | `middle_east_news_report_0a56c7e5359d` @ 00:06 | "I don't really see too many possibilities of retaliation aga" |
| MODE B (Speech/Audio) | `retaliate against Israel` | 0.50 | 148.0 ms | 0.5990 | 0.2442 | 0.9538 | `middle_east_news_report_0a56c7e5359d` @ 00:06 | "I don't really see too many possibilities of retaliation aga" |
| MODE C (Hybrid) | `Obama farewell address White House` | 0.50 | 156.2 ms | 0.5268 | 0.3041 | 0.7495 | `obama_farewell_speech_353ca4868dfb` @ 01:29 | "You made the White House a place that belongs to everybody," |
| MODE C (Hybrid) | `sports news and player discussion` | 0.50 | 143.5 ms | 0.4447 | 0.0000 | 0.8894 | `sports_news_breakdown_372460f80e66` @ 08:57 | "What kind of game do you expect to see from the off?" |

*Note: these top-matches were not checked against independent ground truth — they show the system returns a plausible-looking result for each query, not that it's the correct or best result among the corpus.*

---

## Failure Mode & Edge-Case Analysis

**Zero-Weight Modality Behavior (α = 1.0 vs α = 0.0):**
- Visual Only (α = 1.0): Fused score strictly matches visual_score. Audio vector weighting reduces to 0.0000.
- Audio Only (α = 0.0): Fused score strictly matches audio_score. Visual vector weighting reduces to 0.0000.
- Balanced (α = 0.5): Fused score computes exact arithmetic mean of visual and audio.

**Payload Key & Silent Frame Hardening:**
- Frames lacking speech transcription fall back to a placeholder `"news video footage scene"` string, avoiding empty-embedding exceptions. Worth noting: several of the matches above (rows with that exact placeholder transcript) are matching on visual signal only — that's expected behavior, not a bug, but it means those rows say nothing about audio retrieval quality.
- Keyframe records contain all mandatory metadata fields (`video_id`, `timestamp`, `frame_idx`, `transcribed_text`, `domain`, `frame_path`).

**Latency:** Mac CPU execution capped at 2 threads achieved an average retrieval latency of 165.8 ms, comfortably under a 1,500 ms budget.

---

## Systems Health Summary

| Check | Requirement | Observed | Status |
|---|---|---|---|
| Vector Space Normalization | ‖v‖₂ = 1.0 | 1.000000 | Passed |
| Qdrant Point Count | ~1,900 points | 1,903 points | Passed |
| Query Latency | < 1,500 ms | 165.8 ms avg | Passed |
| Late Fusion Consistency | Exact linear combination | α·V + (1−α)·A | Passed |
| Payload Integrity | Zero KeyErrors / NaNs | 0 exceptions | Passed |

These confirm the system is stable and fast. They do not confirm it retrieves the right results — see "What this report covers" above for the retrieval-quality evaluation that's still outstanding.
