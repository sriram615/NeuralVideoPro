# Roadmap Implementation Checklist

**Project Title:** Semantic Video Retrieval System
**Document Source:** `docs/Video Retrieval System Roadmap.pdf`

---

## What this document is

This is a mapping of each roadmap work package (WP1–WP5) to the file that implements it and the test that exercises it. It was originally written as a self-audit by the AI tooling used to build this project (credited internally as "Google Antigravity") and scored itself "100% COMPLIANT" — that self-grading has been removed here, since a build tool checking that its own output exists and its own tests pass isn't independent verification of anything. What's left is genuinely useful as a map of "where does requirement X live in the code," which is the part worth keeping.

The "PASSED" column below means: the referenced test file exists and covers the referenced implementation file, and the test suite ran clean. It does not mean the feature was independently verified to work correctly in all cases — see `reports/eval_results.md` for what has and hasn't actually been verified about output quality.

---

## Roadmap Requirement Mapping

| Work Package | Roadmap Requirement | Implementation File | Verification Test File | Test Suite Status |
|---|---|---|---|---|
| WP1: Setup & Benchmarking | PyTorch CPU Thread Safety (`OMP_NUM_THREADS=2`, `MKL_NUM_THREADS=2`) | `src/models/text_encoder.py`, `src/models/vision_encoder.py`, `src/pipeline.py` | `test_text_encoder.py` | Suite passes |
| WP1: Setup & Benchmarking | Embedded Qdrant DB Initialization (`./data/qdrant_db`) | `src/db/qdrant_db.py` | `test_qdrant.py` | Suite passes |
| WP1: Setup & Benchmarking | CLIP (ViT-B/32) Model Verification & 512-D Normalization | `text_encoder.py`, `vision_encoder.py` | `test_text_encoder.py` | Suite passes |
| WP1: Setup & Benchmarking | News Video Corpus Ingestion (7 real news/speech MP4s) | `ingest_real_news.py` | `test_batch_ingest.py` | Suite passes |
| WP2: Processing & Feature Engine | 1 fps Keyframe Extraction & Max 720p Downscaling | `video_processor.py` | `test_ingestion.py` | Suite passes |
| WP2: Processing & Feature Engine | Audio Demuxing & Whisper Speech Transcription | `audio_processor.py` | `test_ingestion.py` | Suite passes |
| WP2: Processing & Feature Engine | Metadata Payload Tagging | `qdrant_db.py`, `pipeline.py` | `test_full_pipeline.py` | Suite passes |
| WP2: Processing & Feature Engine | Micro-Batch Embedding Generation (Batch Size = 8) | `vision_encoder.py` | `test_full_pipeline.py` | Suite passes |
| WP3: Vector DB Schema & Indexing | Qdrant Collection with 512-D Cosine Vectors | `qdrant_db.py` | `test_qdrant.py` | Suite passes |
| WP3: Vector DB Schema & Indexing | Dual-Vector Schema (`visual_vector` + `audio_vector`) | `qdrant_db.py`, `pipeline.py` | `test_full_pipeline.py` | Suite passes |
| WP3: Vector DB Schema & Indexing | Batch Directory Ingestion with RAM Cleanup | `batch_ingest.py` | `test_batch_ingest.py` | Suite passes |
| WP4: Retrieval & Interface | Natural Language Query Processing | `text_encoder.py` | `test_text_encoder.py` | Suite passes |
| WP4: Retrieval & Interface | Hybrid Late Fusion Search | `pipeline.py` | `test_full_pipeline.py` | Suite passes |
| WP4: Retrieval & Interface | Streamlit Dashboard, XAI Breakdown, Intent Telemetry | `app.py` | `test_app_imports.py` | Suite passes |
| WP5: Polish & Documentation | System Documentation | — | — | Documentation exists but had material gaps (empty root README, unpublished eval numbers) — being addressed |

---

## What "suite passes" actually verifies vs. doesn't

The six test suites listed above (`test_qdrant.py`, `test_text_encoder.py`, `test_ingestion.py`, `test_full_pipeline.py`, `test_batch_ingest.py`, `test_app_imports.py`) confirm the code runs without errors and the components wire together correctly. None of them assert anything about retrieval relevance — whether a search for a given query actually surfaces the right video. That's a separate, still-open piece of work; see the "Known issue" note in `reports/eval_results.md` for the current status of the retrieval-quality evaluation.
