# generate_llm_questions.py — LLM-generated easy/medium/hard questions per video.
#
# Extracts transcripts from Qdrant for each video, asks Groq to generate 3
# questions (easy / medium / hard) grounded in that video's content, and saves
# them to a JSON file for final evaluation/testing.
#
# Usage:
#     source .venv/bin/activate
#     export GROQ_API_KEY="gsk_..."
#     PYTHONPATH=backend python scripts/evaluation/generate_llm_questions.py
#
# Output: backend/tests/data/llm_generated_questions.json

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

os.environ.setdefault("QDRANT_DB_PATH", "/Users/apple/Desktop/CV-Hackathon/data/vectors/qdrant_db")
sys.path.insert(0, "/Users/apple/Desktop/CV-Hackathon/backend")

from src.db.qdrant_db import QdrantVectorStore
from src.rag.generator import get_rag_generator


# ---------------------------------------------------------------------------
# Videos to include — the 15 real content videos (exclude test artifacts)
# ---------------------------------------------------------------------------
TARGET_VIDEOS = [
    "'Wait ... be careful ... quiet!' Trump snaps at reporters during White House press conference_9acd664fd096",
    "How To Make an Omelette_3f9a7f590a70",
    "How to TEDx： Design a stage_b56eece8f029",
    "Quadratic Equation Demo class_dd11e5ce2493",
    "what they dont tell you about living alone._cfdf48ba368c",
    "Steve Jobs Interview Feb 18 1981_936669ae85ba",
    "atheist_discussion_interview_a3bb4396b531",
    "ecns_opening_speech_665f4791a4e8",
    "identity_politics_interview_d8c8047ee6b7",
    "middle_east_news_report_0a56c7e5359d",
    "my_llm_talk",
    "nasa_space_flight_news_a485d4f58b49",
    "obama_farewell_speech_353ca4868dfb",
    "sports_news_breakdown_372460f80e66",
    "Abuse001_x264_b05204644f3f",
]


def extract_transcripts(db_path: str) -> Dict[str, str]:
    """Return {video_id: combined_transcript_text} for target videos."""
    store = QdrantVectorStore(db_path=db_path)
    result = store.client.scroll(
        collection_name="video_intelligence",
        limit=10000,
        with_payload=True,
        with_vectors=False,
    )

    transcripts: Dict[str, List[str]] = {}
    for point in result[0]:
        if not point.payload:
            continue
        vid = point.payload.get("video_id", "unknown")
        if vid not in TARGET_VIDEOS:
            continue
        tr = point.payload.get("transcribed_text", "")
        if tr.strip() and tr.lower() not in ["news video footage scene", "visual scene footage"]:
            transcripts.setdefault(vid, []).append(tr)

    store.close()
    return {vid: " ".join(segs) for vid, segs in transcripts.items()}


def generate_questions_for_video(
    generator,
    video_id: str,
    transcript: str,
    max_chars: int = 3000,
) -> List[Dict[str, Any]]:
    """Ask Groq to generate easy/medium/hard questions for one video."""
    trimmed = transcript[:max_chars]

    prompt = (
        "You are a question-generation assistant for evaluating a video search engine.\n"
        "Given the transcript of a video below, generate exactly 3 questions:\n"
        "  1. EASY — a factual question answerable from a single sentence (who/what/where/when).\n"
        "  2. MEDIUM — a comprehension question requiring 2-3 sentences of context.\n"
        "  3. HARD — an inference or synthesis question requiring understanding of the whole video.\n\n"
        "For each question, also provide:\n"
        "  - 'answer': a short ground-truth answer drawn from the transcript.\n"
        "  - 'timestamp': an approximate second in the video where the answer appears (or 0 if unknown).\n\n"
        "Respond with valid JSON only, no markdown, no explanation:\n"
        '{"questions": [{"difficulty": "easy", "question": "...", "answer": "...", "timestamp": 0}, ...]}\n\n'
        f"VIDEO TRANSCRIPT:\n{trimmed}"
    )

    try:
        response = generator.client.chat.completions.create(
            model=generator.model,
            messages=[
                {"role": "system", "content": "You generate evaluation questions for video search. Output valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=800,
        )
        content = response.choices[0].message.content or ""
        # Strip any markdown fencing
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        questions = data.get("questions", [])
        for q in questions:
            q["video_id"] = video_id
        return questions
    except Exception as exc:
        print(f"  [!] Groq failed for {video_id[:40]}: {exc}")
        return []


def main() -> None:
    db_path = os.getenv("QDRANT_DB_PATH", "/Users/apple/Desktop/CV-Hackathon/data/vectors/qdrant_db")
    generator = get_rag_generator()

    if not generator.is_available():
        print("ERROR: GROQ_API_KEY not set. Add it to .env and try again.")
        sys.exit(1)

    print(f"Using model: {generator.model}")
    print("Extracting transcripts from Qdrant...")
    transcripts = extract_transcripts(db_path)

    # Filter to videos that actually have transcript content
    available = {vid: txt for vid, txt in transcripts.items() if len(txt) > 100}
    missing = [vid for vid in TARGET_VIDEOS if vid not in available]
    if missing:
        print(f"Warning: {len(missing)} target videos have no usable transcript:")
        for vid in missing:
            print(f"  - {vid[:60]}")

    print(f"\nGenerating questions for {len(available)} videos...\n")

    all_questions: List[Dict[str, Any]] = []
    for idx, (vid, transcript) in enumerate(sorted(available.items()), 1):
        short_vid = vid[:50]
        print(f"[{idx:2d}/{len(available)}] {short_vid}... ({len(transcript)} chars)")
        questions = generate_questions_for_video(generator, vid, transcript)
        all_questions.extend(questions)
        for q in questions:
            print(f"      [{q['difficulty']:6s}] {q['question'][:80]}")

    out_path = Path("/Users/apple/Desktop/CV-Hackathon/backend/tests/data/llm_generated_questions.json")
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(all_questions, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(all_questions)} questions to {out_path}")
    print(f"Videos covered: {len(set(q['video_id'] for q in all_questions))}")


if __name__ == "__main__":
    main()
