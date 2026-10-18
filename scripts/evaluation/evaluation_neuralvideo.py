#!/usr/bin/env python3
"""NeuralVideoPro Evaluation — 26 search queries + 4 grounded Q&A."""

import json
import sys
import time
import requests

API = "http://localhost:8000"

def search(query: str, top_k: int = 5) -> dict:
    r = requests.post(f"{API}/api/v1/search", json={"query": query, "top_k": top_k})
    r.raise_for_status()
    return r.json()

def ask_video(question: str, top_k_snippets: int = 5) -> dict:
    r = requests.post(f"{API}/api/v1/ask-video", json={
        "question": question,
        "top_k_snippets": top_k_snippets,
        "use_mmr": True,
    })
    r.raise_for_status()
    return r.json()

def fmt_result(res: dict, rank_limit: int = 5) -> str:
    lines = []
    for r in res.get("results", [])[:rank_limit]:
        p = r.get("payload", {})
        fname = p.get("file_name", p.get("video_id", "?"))
        ts = p.get("timestamp", 0)
        txt = (p.get("transcribed_text", "") or "")[:80]
        xai = r.get("xai", {})
        lines.append(
            f"  #{r['rank']}: {fname}  fused={r['fused_score']:.4f}  "
            f"vis={r['visual_score']:.4f}  aud={r['audio_score']:.4f}  "
            f"rrf={r.get('rrf_score','n/a')}  ts={ts:.1f}s  "
            f"driver={xai.get('primary_driver','?')}  tier={xai.get('confidence_tier','?')}"
        )
        if txt:
            lines.append(f"     transcript: \"{txt}\"")
    return "\n".join(lines)

# ============================================================
# Section A — One clean query per video (10)
# ============================================================
section_a_queries = [
    ("a 1981 interview with a personal computer industry pioneer", "Steve Jobs Interview Feb 18 1981.mp4"),
    ("an explanation of how AI agents are designed using large language models", "my_llm_talk"),
    ("a crowd gathering around a physical altercation caught on camera", "Abuse001_x264.mp4"),
    ("a president's farewell address about democracy", "obama_farewell_speech.mp4"),
    ("news coverage of conflict and diplomacy in the Middle East", "middle_east_news_report.mp4"),
    ("a rocket launch and space exploration", "nasa_space_flight_news.mp4"),
    ("sports commentary and game highlights", "sports_news_breakdown.mp4"),
    ("a keynote on global trade and financial policy", "ecns_opening_speech.mp4"),
    ("a debate between an atheist and a religious believer", "atheist_discussion_interview.mp4"),
    ("an interview about identity politics and social policy", "identity_politics_interview.mp4"),
]

# Section B — Cross-video ambiguity (3)
section_b_queries = [
    ("computing and artificial intelligence transforming society", ["Steve Jobs", "my_llm_talk"]),
    ("a broadcast interview touching on politics and society", ["atheist_discussion", "identity_politics", "ecns_opening", "middle_east"]),
    ("a formal address given from behind a podium", ["obama_farewell", "ecns_opening"]),
]

# Section C — Visual/CLIP-path tests (2)
section_c_queries = [
    ("grainy black-and-white security camera footage of two people fighting", "Abuse001_x264.mp4"),
    ("a bright rocket exhaust plume against the sky during liftoff", "nasa_space_flight_news.mp4"),
]

# Section D — Speech/Whisper-path tests (2)
section_d_queries = [
    ("an explanation of how the attention mechanism lets a model weigh different words", "my_llm_talk"),
    ("remarks about currency exchange rates and global markets", "ecns_opening_speech.mp4"),
]

# Section E — Precision / near-miss pairs (3)
section_e_queries = [
    ("an interview exploring religious belief versus atheism", "atheist_discussion_interview.mp4", "identity_politics_interview.mp4"),
    ("a discussion of race, gender, or social identity in politics", "identity_politics_interview.mp4", "atheist_discussion_interview.mp4"),
    ("an economic keynote address", "ecns_opening_speech.mp4", "obama_farewell_speech.mp4"),
]

# Section F — Keyframe-density / multi-timestamp (2)
section_f_queries = [
    ("a highlight reel narrator describing a game-winning play", "sports_news_breakdown.mp4"),
    ("analysts breaking down team strategy after a match", "sports_news_breakdown.mp4"),
]

# Section G — Negative controls (3)
section_g_queries = [
    "a tutorial on how to bake sourdough bread",
    "a fictional movie trailer with special effects and an on-screen villain",
    "a children's cartoon show",
]

# Section H — Duplicate-file probe (1)
# re-run query 2

# Grounded Q&A (4)
qa_queries = [
    ("Steve Jobs Interview Feb 18 1981.mp4", "What does Steve Jobs say will happen to computing in the future?"),
    ("obama_farewell_speech.mp4", "What does Obama say democracy requires of its citizens?"),
    ("my_llm_talk.mp4", "How does the speaker describe the role of prompt engineering when building an AI agent?"),
    ("atheist_discussion_interview.mp4", 'What specific Bible verse does the guest cite to support their argument?'),
]


def run_all():
    output = []
    output.append("=" * 80)
    output.append("NEURALVIDEOPRO EVALUATION — 26 Search + 4 Q&A")
    output.append("=" * 80)

    # ── Section A ──
    output.append("\n### SECTION A: One clean query per video (10)")
    output.append("-" * 60)
    a_correct = 0
    for i, (query, expected) in enumerate(section_a_queries, 1):
        res = search(query, top_k=5)
        top1 = res["results"][0] if res["results"] else {}
        top1_file = top1.get("payload", {}).get("file_name", top1.get("payload", {}).get("video_id", "?"))
        correct = expected.replace(".mp4", "").replace(".MOV", "") in str(top1_file)
        if correct:
            a_correct += 1
        output.append(f"\nA{i}: \"{query}\"")
        output.append(f"  Expected: {expected}")
        output.append(f"  Correct: {'YES' if correct else 'NO'}")
        output.append(f"  Latency: {res['latency_ms']:.1f}ms")
        output.append(f"  Intent: alpha={res['intent']['alpha']} label={res['intent']['intent_label']}")
        output.append(fmt_result(res, rank_limit=3))
        # For query 2, check if both .MOV and .mp4 appear
        if i == 2:
            llm_hits = [r for r in res["results"] if "my_llm_talk" in str(r.get("payload", {}).get("file_name", r.get("payload", {}).get("video_id", "")))]
            output.append(f"  [DEDUP CHECK] my_llm_talk hits in top-5: {len(llm_hits)}")
            for h in llm_hits:
                output.append(f"    -> {h['payload'].get('file_name', h['payload'].get('video_id', '?'))}")
        time.sleep(0.3)
    output.append(f"\n  Section A Score: {a_correct}/10")

    # ── Section B ──
    output.append("\n### SECTION B: Cross-video ambiguity / MMR diversification (3)")
    output.append("-" * 60)
    for i, (query, plausible) in enumerate(section_b_queries, 11):
        res = search(query, top_k=5)
        output.append(f"\nB{i}: \"{query}\"")
        output.append(f"  Plausible: {plausible}")
        output.append(f"  Latency: {res['latency_ms']:.1f}ms")
        output.append(fmt_result(res, rank_limit=5))
        # Check which plausible hits appear in top 3
        top3_files = [r.get("payload", {}).get("file_name", r.get("payload", {}).get("video_id", "")) for r in res["results"][:3]]
        matched = [p for p in plausible if any(p.lower().replace(" ","_") in str(f).lower() or p.lower().replace("_"," ") in str(f).lower() for f in top3_files)]
        output.append(f"  Plausible in top-3: {matched}")
        time.sleep(0.3)

    # ── Section C ──
    output.append("\n### SECTION C: Visual/CLIP-path tests (2)")
    output.append("-" * 60)
    c_correct = 0
    for i, (query, expected) in enumerate(section_c_queries, 14):
        res = search(query, top_k=5)
        top1 = res["results"][0] if res["results"] else {}
        top1_file = top1.get("payload", {}).get("file_name", top1.get("payload", {}).get("video_id", "?"))
        correct = expected.replace(".mp4", "") in str(top1_file)
        if correct:
            c_correct += 1
        output.append(f"\nC{i}: \"{query}\"")
        output.append(f"  Expected: {expected}")
        output.append(f"  Correct: {'YES' if correct else 'NO'}")
        output.append(f"  Latency: {res['latency_ms']:.1f}ms")
        output.append(fmt_result(res, rank_limit=3))
        time.sleep(0.3)
    output.append(f"\n  Section C Score: {c_correct}/2")

    # ── Section D ──
    output.append("\n### SECTION D: Speech/Whisper-path tests (2)")
    output.append("-" * 60)
    d_correct = 0
    for i, (query, expected) in enumerate(section_d_queries, 16):
        res = search(query, top_k=5)
        top1 = res["results"][0] if res["results"] else {}
        top1_file = top1.get("payload", {}).get("file_name", top1.get("payload", {}).get("video_id", "?"))
        correct = expected.replace(".mp4", "") in str(top1_file)
        if correct:
            d_correct += 1
        output.append(f"\nD{i}: \"{query}\"")
        output.append(f"  Expected: {expected}")
        output.append(f"  Correct: {'YES' if correct else 'NO'}")
        output.append(f"  Latency: {res['latency_ms']:.1f}ms")
        output.append(fmt_result(res, rank_limit=3))
        time.sleep(0.3)
    output.append(f"\n  Section D Score: {d_correct}/2")

    # ── Section E ──
    output.append("\n### SECTION E: Precision / near-miss pairs (3)")
    output.append("-" * 60)
    e_correct = 0
    for i, (query, expected, should_not) in enumerate(section_e_queries, 18):
        res = search(query, top_k=5)
        top1 = res["results"][0] if res["results"] else {}
        top1_file = top1.get("payload", {}).get("file_name", top1.get("payload", {}).get("video_id", "?"))
        correct = expected.replace(".mp4", "") in str(top1_file)
        wrong_won = should_not.replace(".mp4", "") in str(top1_file)
        if correct:
            e_correct += 1
        output.append(f"\nE{i}: \"{query}\"")
        output.append(f"  Expected: {expected}")
        output.append(f"  Should NOT win: {should_not}")
        output.append(f"  Correct: {'YES' if correct else 'NO'}  Wrong-won: {'YES (BAD)' if wrong_won else 'no'}")
        output.append(f"  Latency: {res['latency_ms']:.1f}ms")
        output.append(fmt_result(res, rank_limit=3))
        time.sleep(0.3)
    output.append(f"\n  Section E Score: {e_correct}/3")

    # ── Section F ──
    output.append("\n### SECTION F: Keyframe-density / multi-timestamp test (2)")
    output.append("-" * 60)
    f_correct = 0
    f_timestamps = []
    for i, (query, expected) in enumerate(section_f_queries, 21):
        res = search(query, top_k=5)
        top1 = res["results"][0] if res["results"] else {}
        top1_file = top1.get("payload", {}).get("file_name", top1.get("payload", {}).get("video_id", "?"))
        ts = top1.get("payload", {}).get("timestamp", 0)
        correct = expected.replace(".mp4", "") in str(top1_file)
        if correct:
            f_correct += 1
        f_timestamps.append(ts)
        output.append(f"\nF{i}: \"{query}\"")
        output.append(f"  Expected: {expected}")
        output.append(f"  Correct: {'YES' if correct else 'NO'}")
        output.append(f"  Top-1 timestamp: {ts:.1f}s")
        output.append(f"  Latency: {res['latency_ms']:.1f}ms")
        output.append(fmt_result(res, rank_limit=3))
        time.sleep(0.3)
    distinct = abs(f_timestamps[0] - f_timestamps[1]) > 5.0 if len(f_timestamps) == 2 else False
    output.append(f"\n  Section F Score: {f_correct}/2")
    output.append(f"  Timestamps distinct (>5s apart): {'YES' if distinct else 'NO'} ({f_timestamps[0]:.1f}s vs {f_timestamps[1]:.1f}s)")

    # ── Section G ──
    output.append("\n### SECTION G: Negative controls — out-of-domain (3)")
    output.append("-" * 60)
    g_correct = 0
    for i, query in enumerate(section_g_queries, 23):
        res = search(query, top_k=5)
        top1 = res["results"][0] if res["results"] else {}
        top_score = top1.get("fused_score", 0)
        all_scores = [r.get("fused_score", 0) for r in res["results"]]
        low_confidence = top_score < 0.45
        if low_confidence:
            g_correct += 1
        output.append(f"\nG{i}: \"{query}\"")
        output.append(f"  Expected: No good match / low scores")
        output.append(f"  Top-1 score: {top_score:.4f}  Low-confidence (<0.45): {'YES (GOOD)' if low_confidence else 'NO (false positive)'}")
        output.append(f"  All top-5 scores: {[f'{s:.4f}' for s in all_scores]}")
        output.append(fmt_result(res, rank_limit=3))
        time.sleep(0.3)
    output.append(f"\n  Section G Score: {g_correct}/3")

    # ── Section H ──
    output.append("\n### SECTION H: Duplicate-file probe (1)")
    output.append("-" * 60)
    query_h = "an explanation of how AI agents are designed using large language models"
    res = search(query_h, top_k=10)
    llm_hits = []
    for r in res["results"]:
        fn = r.get("payload", {}).get("file_name", r.get("payload", {}).get("video_id", ""))
        if "my_llm_talk" in str(fn).lower():
            llm_hits.append((fn, r["fused_score"], r.get("payload", {}).get("timestamp", 0)))
    output.append(f"\nH26: Re-running query 2 with top_k=10")
    output.append(f"  my_llm_talk hits found: {len(llm_hits)}")
    for fn, sc, ts in llm_hits:
        output.append(f"    -> {fn}  score={sc:.4f}  ts={ts:.1f}s")
    distinct_files = set(fn for fn, _, _ in llm_hits)
    output.append(f"  Distinct file names: {distinct_files}")
    if len(distinct_files) > 1:
        output.append("  [FLAG] DEDUP ISSUE: .MOV and .mp4 appear as separate indexed items")
    else:
        output.append("  [OK] Only one file variant indexed")

    # ── Grounded Q&A ──
    output.append("\n### GROUNDED VIDEO Q&A (ask-video) — 4 queries")
    output.append("-" * 60)
    for i, (video, question) in enumerate(qa_queries, 1):
        output.append(f"\nQ{i}: [{video}] \"{question}\"")
        try:
            res = ask_video(question, top_k_snippets=5)
            output.append(f"  Answer: {res.get('answer', 'N/A')}")
            output.append(f"  Latency: retrieval={res.get('retrieval_latency_ms', 0):.1f}ms  llm={res.get('llm_latency_ms', 0):.1f}ms  total={res.get('latency_ms', 0):.1f}ms")
            # Show citations
            cits = res.get("citations", [])
            output.append(f"  Citations ({len(cits)}):")
            for c in cits[:5]:
                output.append(f"    video={c.get('video_id','?')}  window={c.get('event_window','?')}  transcript=\"{c.get('transcript_snippet','')[:80]}\"")
            # Show context snippets
            snippets = res.get("context_snippets", [])
            if snippets:
                output.append(f"  Context snippet #1:")
                output.append(f"    {snippets[0][:200]}")
            # Check grounding — does the answer reference a specific video_id?
            cited_videos = set(c.get("video_id", "") for c in cits)
            target_stem = video.replace(".mp4", "").replace(".MOV", "")
            grounded = any(target_stem.lower().replace(" ", "_") in v.lower() or target_stem.lower() in v.lower() for v in cited_videos)
            output.append(f"  Grounded to target video: {'YES' if grounded else 'NO'}")
            output.append(f"  Timestamp given: {'YES' if cits and cits[0].get('event_window') else 'NO'}")
        except Exception as e:
            output.append(f"  ERROR: {e}")
        time.sleep(0.3)

    # ── Summary ──
    output.append("\n" + "=" * 80)
    output.append("SUMMARY")
    output.append("=" * 80)
    total_search = a_correct + c_correct + d_correct + e_correct + f_correct
    output.append(f"Section A (clean per-video):   {a_correct}/10")
    output.append(f"Section C (visual/CLIP-path):  {c_correct}/2")
    output.append(f"Section D (speech/Whisper):     {d_correct}/2")
    output.append(f"Section E (precision pairs):    {e_correct}/3")
    output.append(f"Section F (keyframe-density):   {f_correct}/2")
    output.append(f"Section G (negative controls):  {g_correct}/3")
    output.append(f"Scored search total:            {total_search + g_correct}/22")
    output.append(f"(Sections B, H are qualitative, not scored)")

    result = "\n".join(output)
    print(result)
    return result


if __name__ == "__main__":
    result = run_all()
    with open("/Users/apple/Desktop/CV-Hackathon/evaluation_results_neuralvideo.txt", "w") as f:
        f.write(result)
    print("\n\nResults saved to evaluation_results_neuralvideo.txt")
