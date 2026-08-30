# NEURALVIDEO — Multimodal Video Search & Intelligence Engine

> **Hackathon Release 2026** | Real-Time Cross-Modal Deep Retrieval with CLIP (512-D), OpenAI Whisper Speech Transcription, Reciprocal Rank Fusion (RRF), Cross-Modal Agreement Scoring, and Maximal Marginal Relevance (MMR) Diversification.

---

## 1. Project Overview

**NEURALVIDEO** is a multimodal video search engine designed to perform semantic search over unstructured video archives. The engine breaks down video streams into synchronized visual keyframe embeddings (via OpenAI CLIP) and speech transcript embeddings (via OpenAI Whisper), fusing them in an embedded **Qdrant Vector Database** using Auto-Intent Late Fusion.

### Core Capabilities
- **Dual-Modality Vector Search:** 512-D Cosine similarity matching across both visual keyframes and acoustic speech text.
- **Auto-Intent Classification:** Dynamic query intent detection balancing visual bias ($\alpha = 0.8$) vs. acoustic speech bias ($\alpha = 0.2$) or hybrid fusion ($\alpha = 0.5$).
- **Explainable AI (XAI) Attribution:** Full score breakdowns (`visual_score`, `audio_score`, `rrf_score`, `confidence_band`, `match_rationale`) for every retrieved snippet.
- **RAG & Video QA:** Decoupled LLM video question answering (`/api/v1/ask-video`) with sub-200ms vector search SLA.

---

## 2. Workspace Folder Structure

```
NEURALVIDEO-Hackathon-2026/
├── backend/                  # FastAPI Application & ML Pipeline
│   ├── api.py                # REST API Endpoints (/health, /search, /ask-video, /corpus/stats)
│   ├── schemas.py            # Pydantic Schemas & XAI Telemetry Models
│   ├── legacy/               # Streamlit App (Legacy UI)
│   ├── src/                  # Core Python Package
│   │   ├── db/               # Qdrant Vector Store Wrapper
│   │   ├── ingestion/        # Keyframe Sampler & Audio Transcriber
│   │   └── models/           # CLIP Vision & Text Encoder Pipelines
│   └── tests/                # Comprehensive Test Suite & Benchmark Data
├── frontend/                 # Modern Next.js 14 Web Application
├── data/                     # Vector DB, Raw Media & Benchmarks
│   ├── raw/                  # Source MP4 Videos
│   ├── processed/            # Extracted 1fps Keyframes
│   ├── vectors/              # Embedded Qdrant Storage (qdrant_db)
│   └── benchmarks/           # Experiment Result Caches
├── docs/                     # Architectural Documentation
├── reports/                  # Evaluation Reports & Ablation Matrix
├── scripts/                  # Automated Workflows
│   ├── ingestion/            # Video Ingestion Scripts
│   ├── evaluation/           # Evaluation & Ablation Matrix Suites
│   └── utilities/            # Pipeline Verification Tools
├── setup.sh                  # macOS / Linux Setup Script
├── setup.bat                 # Windows Setup Script
├── verify_install.py         # Environment Verification Script
├── pytest.ini                # Pytest Configuration
└── requirements.txt          # Python Package Dependencies
```

---

## 3. Prerequisites

Ensure your host machine has the following tools installed:

1. **Python 3.10+** (Python 3.11 recommended)
2. **Node.js 18+** & `npm`
3. **ffmpeg** system binary (required for video/audio demuxing):
   - **macOS:** `brew install ffmpeg`
   - **Linux (Ubuntu/Debian):** `sudo apt update && sudo apt install -y ffmpeg`
   - **Windows:** Download from `ffmpeg.org` or via `winget install ffmpeg`

---

## 4. Installation

Run the automated one-command setup script for your platform:

### macOS / Linux
```bash
./setup.sh
```

### Windows
```cmd
setup.bat
```

The script automatically:
1. Provisions a `.venv` Python virtual environment.
2. Installs required Python dependencies from `requirements.txt`.
3. Installs frontend Node.js packages in `frontend/`.
4. Copies `.env.example` to `.env`.
5. Executes `verify_install.py` to confirm environment readiness.

---

## 5. Backend Startup

To start the FastAPI REST server:

```bash
# 1. Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate.bat  # Windows

# 2. Start Uvicorn ASGI Server
cd backend
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The REST API will be available at `http://localhost:8000`. Interactive OpenAPI documentation is accessible at `http://localhost:8000/docs`.

---

## 6. Frontend Startup

To start the Next.js web application:

```bash
cd frontend
npm run dev
```

Open `http://localhost:3000` in your web browser to interact with the search UI.

---

## 7. Dataset Setup

Place raw `.mp4` video files into:
```
data/raw/raw_videos/
```

Example included dataset:
- `data/raw/raw_videos/Steve Jobs Interview Feb 18 1981.mp4`

---

## 8. Video Ingestion

To ingest video files into the local Qdrant vector database:

```bash
# Activate virtual environment from project root
source .venv/bin/activate

# Ingest real news broadcasts & clips
python -m scripts.ingestion.ingest_real_news

# Or ingest the Steve Jobs stress-test video
python -m scripts.ingestion.ingest_and_test_steve_jobs
```

---

## 9. Running Tests

Execute the complete 36-test suite:

```bash
# Run pytest from project root
pytest -v
```

All 36 unit and integration tests run in ~2 minutes on standard CPU hardware.

---

## 10. Benchmark Commands

Run the empirical Information Retrieval (IR) ablation matrix and system benchmark:

```bash
# 1. Evaluation & Ablation Suite (30 Annotated Queries)
python -m scripts.evaluation.eval_suite

# 2. Mode A/B/C Latency & SLA Benchmark
python -m scripts.evaluation.eval_benchmark

# 3. Pipeline Verification Verification Script
python -m scripts.utilities.verify_pipeline_test
```

Reports are automatically generated and saved in `reports/eval_results.md`.

---

## 11. End-to-End Demo Workflow

1. **Clone & Setup:**
   ```bash
   git clone <repo-url> NEURALVIDEO-Hackathon-2026
   cd NEURALVIDEO-Hackathon-2026
   ./setup.sh
   ```
2. **Start Backend:**
   ```bash
   source .venv/bin/activate
   cd backend && uvicorn api:app --reload
   ```
3. **Start Frontend:**
   ```bash
   cd frontend && npm run dev
   ```
4. **Demo Query Execution:**
   - Open `http://localhost:3000`.
   - Type `"Steve Jobs discussing computers"` or `"whiteboard architecture diagram"`.
   - Inspect sub-200ms latency, keyframe matches, transcript alignment, and XAI confidence bands.

---

## 12. Troubleshooting & Common Issues

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `ffmpeg missing` error | `ffmpeg` binary not on system PATH | Install `ffmpeg` via `brew install ffmpeg` or `sudo apt install ffmpeg`. |
| Qdrant file lock error | Concurrent Qdrant instances | Ensure only one backend or script process accesses `./data/vectors/qdrant_db` at a time. |
| CORS issue in Frontend | API URL mismatch | Verify `.env` has `NEXT_PUBLIC_API_URL=http://localhost:8000`. |
| Pytest `ModuleNotFoundError` | PYTHONPATH not configured | Run `pytest` directly from the project root (`NEURALVIDEO-Hackathon-2026`). `pytest.ini` automatically sets the pythonpath. |
