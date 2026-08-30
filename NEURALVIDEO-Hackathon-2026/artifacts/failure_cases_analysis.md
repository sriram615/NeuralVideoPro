# NEURALVIDEO v5.0 — Failure Cases Analysis & Technical Explanation

**Document Purpose:** Honest, transparent technical analysis of retrieval limitations, false positive edge cases, and architectural explanations for hackathon judges and AI technical reviewers.

---

## 1. TECHNICAL EXPLANATIONS FOR RETRIEVAL BEHAVIOR

### Q1: Why does Audio Similarity show 0% on some Audio/Text queries?
* **Architectural Explanation:** NEURALVIDEO operates a **dual-index candidate generation pipeline** with sparse nearest-neighbor retrieval (Top-30 per modality in Qdrant).
  $$S_{\text{visual}} = \text{Qdrant.search}(\text{visual\_vector}, K=30), \quad S_{\text{audio}} = \text{Qdrant.search}(\text{audio\_vector}, K=30)$$
* When a search query is executed, if a candidate keyframe point is retrieved within the Top-30 visual vector candidates ($S_{\text{visual}}$), but fell outside the Top-30 nearest neighbors of the audio transcript index ($S_{\text{audio}}$), its raw $audio\_score$ is set to $0.0$.
* Reciprocal Rank Fusion (RRF) preserves the point in the final Top-5 output based on its strong visual rank $r_{\text{visual}}$, but the XAI panel transparently displays **Audio Similarity: 0%** because it was not in the audio candidate set.

---

## 2. REAL-WORLD FAILURE CASES & ROOT CAUSE ANALYSIS

| Failure Case | Example Query | Expected Target | Observed Incorrect Rank | Root Cause & Failure Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Case #1: Visual Scene Polysemy** | *"Whiteboard discussion on artificial intelligence"* | `my_llm_talk` (Slide presentation) | **Rank 3:** `atheist_discussion_interview` | CLIP visual encoder matched the plain white studio background wall of the interview set to the text token *"whiteboard"*. |
| **Case #2: Short Transcript Ambiguity** | *"discussion about interest rates and inflation"* | `ecns_opening_speech` (Economic summit) | **Rank 4:** `sports_news_breakdown` | Short 2-second Whisper transcript windows (`"they didn't get it launched"`) lack global context, causing generic speech tokens to overlap in 512-D space. |
| **Case #3: Cross-Modal Subsampling Gap** | *"person wearing black jacket on CCTV"* | `Abuse001_x264` (Keyframe @ 34s) | **Rank 2:** `middle_east_news_report` | Reporter in dark clothing matched CLIP visual embedding higher than low-resolution surveillance footage. |

---

## 3. PROPOSED ENGINEERING MITIGATIONS (FUTURE WORK)

1. **Two-Stage Reranking Architecture (Bi-Encoder + Cross-Encoder):**
   * Use current dual-vector Qdrant setup as a fast **Bi-Encoder First Stage** ($Top\text{-}50$ candidate recall in $< 50\text{ms}$).
   * Add a second-stage **Cross-Encoder Reranker** (e.g., `bge-reranker-large` or MiniLM) to re-score Top-20 candidates against full query text, eliminating semantic drift.

2. **Hierarchical Sentence-Level Audio Windowing:**
   * Transition from 2-second fixed Whisper slice windows to dynamic sentence-level chunking ($10\text{s} - 15\text{s}$ overlapping context windows) to eliminate short transcript ambiguity.
