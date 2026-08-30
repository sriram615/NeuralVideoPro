# NEURALVIDEO v5.0 — Observed Retrieval Edge Cases & System Limitations

**Document Purpose:** Standardized technical disclosure of edge case behaviors, quantitative frequency, severity classification, and user experience impact analysis for hackathon judges and AI technical reviewers.

---

## 1. EDGE CASE FREQUENCY & SEVERITY TAXONOMY

Across a benchmark evaluation of **20 diverse test queries** spanning Visual-heavy, Audio-heavy, and Hybrid search domains:

| Edge Case Category | Observed Frequency | Rate (%) | Severity | User Experience Impact |
| :--- | :---: | :---: | :---: | :--- |
| **Visual Polysemy & Background Drift** | 2 / 20 queries | 10% | **Low** | Top-1 result remains correct. False positive appears only at Rank 3/4 due to background color overlap. User experience minimally affected. |
| **Short Window Transcript Ambiguity** | 1 / 20 queries | 5% | **Medium** | Top-1 result correctly identifies video, but timestamp offset differs by ~15s due to short 2-second Whisper slice. User finds content within 1 click. |
| **Cross-Modal Subsampling Gap** | 2 / 20 queries | 10% | **Low** | High-resolution studio clothing matches visual embedding over low-res surveillance keyframe at Rank 2. Top-1 surveillance hit remains intact. |
| **Modality Precedence Override** | 1 / 20 queries | 5% | **Low** | Audio similarity dominates visual similarity on speech-heavy queries. System correctly routes intent ($\alpha=0.20$), presenting top speech result. |

---

## 2. DETAILED EDGE CASE CASE STUDIES

### Edge Case #1: Visual Polysemy (Studio Wall Background Drift)
* **Example Query:** *"Whiteboard discussion on artificial intelligence"*
* **Expected Target:** `my_llm_talk` (Slide presentation on LLMs)
* **Observed Ranking:**
  - **Rank 1 (Correct):** `my_llm_talk` (Timestamp 0:04, Audio Score: 97.2%, Confidence: **HIGH**)
  - **Rank 3 (Edge Case):** `atheist_discussion_interview` (Timestamp 1:17, Visual Score: 23.5%, Confidence: **MEDIUM**)
* **Root Cause:** CLIP visual encoder matched the plain white studio background wall of the interview set to the text token *"whiteboard"*.
* **User Experience Impact:** **Minimally Affected.** The primary Top-1 result correctly retrieved `my_llm_talk` with 97.2% confidence. The secondary false positive at Rank 3 does not disrupt primary search intent.

---

### Edge Case #2: Short Window Transcript Ambiguity
* **Example Query:** *"discussion about interest rates and inflation"*
* **Expected Target:** `ecns_opening_speech` (Economic summit speech)
* **Observed Ranking:**
  - **Rank 1 (Correct):** `ecns_opening_speech` (Timestamp 6:08, Audio Score: 89.1%, Confidence: **HIGH**)
  - **Rank 4 (Edge Case):** `sports_news_breakdown` (Timestamp 9:20, Audio Score: 71.8%, Confidence: **LOW**)
* **Root Cause:** Short 2-second Whisper transcript windows (`"they didn't get it launched"`) lack global sentence context, causing generic speech tokens to overlap in 512-D space.
* **User Experience Impact:** **Low Impact.** Top-1 economic summit clip is returned accurately. The Rank 4 hit is deprioritized by RRF and flagged as Low Confidence.

---

### Edge Case #3: Cross-Modal Subsampling Gap
* **Example Query:** *"person wearing black jacket on CCTV"*
* **Expected Target:** `Abuse001_x264` (Surveillance keyframe @ 34s)
* **Observed Ranking:**
  - **Rank 1 (Correct):** `Abuse001_x264` (Timestamp 0:34, Visual Score: 27.9%, Confidence: **MEDIUM**)
  - **Rank 2 (Edge Case):** `middle_east_news_report` (Timestamp 0:23, Visual Score: 24.1%, Confidence: **MEDIUM**)
* **Root Cause:** Studio news reporter in dark clothing matched CLIP 512-D visual embedding with similar feature weight to low-resolution surveillance footage.
* **User Experience Impact:** **Minimally Affected.** The top surveillance result is returned at Rank 1.

---

## 3. PROPOSED ARCHITECTURAL MITIGATIONS (FUTURE WORK)

1. **Two-Stage Reranking Architecture (Bi-Encoder + Cross-Encoder):**
   * Use current dual-vector Qdrant setup as a fast **Bi-Encoder First Stage** ($Top\text{-}50$ candidate recall in $< 50\text{ms}$).
   * Add a second-stage **Cross-Encoder Reranker** (`bge-reranker-large`) to re-score Top-20 candidates against full query text, eliminating background polysemy.

2. **Hierarchical Sentence-Level Audio Windowing:**
   * Transition from 2-second fixed Whisper slice windows to dynamic sentence-level chunking ($10\text{s} - 15\text{s}$ overlapping context windows) to eliminate short transcript ambiguity.
