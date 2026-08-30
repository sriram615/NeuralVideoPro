# CV-Hackathon

This folder is the development workspace for **NEURALVIDEO**, a multimodal (visual + speech) semantic video search engine built with CLIP, Whisper, and Qdrant.

**The canonical, submission-ready project lives in [`NEURALVIDEO-Hackathon-2026/`](./NEURALVIDEO-Hackathon-2026/README.md).** Start there — it has the real setup instructions, the FastAPI backend, the Next.js frontend, and the test/eval suite.

## What's in this outer folder

Everything at this top level (`api.py`, `app.py`, `src/`, the various `ingest_*.py` / `fetch_news.py` / `find_*.py` scripts, `venv/`, `.venv/`) is the original dev history: early experiments, one-off data-collection scripts used to build the video corpus, and the first version of the pipeline before it was restructured into `NEURALVIDEO-Hackathon-2026/`. It's kept here for reference but isn't the version to run or review.

If you're cleaning this repo up for good, the end state should be: promote the contents of `NEURALVIDEO-Hackathon-2026/` to the repo root, and move everything else here into an `archive/` (or `legacy/`) folder, or drop it. A script to do that mechanically is at [`promote_and_archive.sh`](./promote_and_archive.sh) — see the comments at the top before running it.

## Known issue being worked on

One entry in the evaluation ground-truth set (`tests/ground_truth_benchmark.json`, query `v_01`, "whiteboard architecture diagram explanation") does not match its labeled video on inspection of the actual frames — see the note in `reports/eval_results.md`. The evaluation numbers in `reports/` predate a full re-verification of the ground-truth labels against real footage and should be treated as provisional until that's done.
