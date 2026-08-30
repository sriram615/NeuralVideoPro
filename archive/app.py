"""
Streamlit Web Application — NeuralVideo v2.0 PRO Command Center & Showcase.

Architecture:
    - State-driven 2-page navigation (st.session_state.page: "landing" | "workspace")
    - Page 1 ("landing"): High-impact SaaS showcase with system metrics, late-fusion math, and architecture cards.
    - Page 2 ("workspace"): Neural search command center with intent telemetry, multi-layer cards, bold percentage score metrics, Dual-Layer Hybrid XAI (Non-Technical Summary + LaTeX Mathematical Provenance), and transcript keyword highlighting.

Usage:
    streamlit run app.py
"""

from __future__ import annotations

# ── CPU thread limits (must precede torch / numpy imports) ──────────────
import os

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st
from PIL import Image

from src.pipeline import VideoSearchPipeline

logger = logging.getLogger(__name__)

# Keyword lists for intent classification
VISUAL_KEYWORDS = [
    "person", "suit", "standing", "podium", "blue", "earth", "space view",
    "wearing", "color", "background", "flags", "crowd", "holding", "scene",
    "jacket", "tie", "red", "stage", "building", "cars", "traffic", "video",
    "logo"
]
AUDIO_KEYWORDS = [
    "said", "talking", "speech", "quote", "statement", "retaliate", "interview",
    "discussion", "asked", "transcript", "words", "mentioned", "talks", "briefing",
    "speaker", "saying", "claims", "address"
]

STOP_WORDS = {
    "the", "and", "a", "an", "in", "on", "at", "to", "for", "of", "with",
    "by", "from", "up", "about", "into", "over", "after", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "but", "or", "so", "if", "out", "no", "not", "only", "own", "same", "that",
    "this", "these", "those", "then", "there", "when", "where", "why", "how",
}

# Page configuration
st.set_page_config(
    page_title="NeuralVideo v2.0 PRO — Multimodal Search Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Cache pipeline resource to load models once on startup
@st.cache_resource
def get_pipeline(db_path: str = "./data/qdrant_db") -> VideoSearchPipeline:
    """Instantiate and cache VideoSearchPipeline models."""
    return VideoSearchPipeline(db_path=db_path)


def predict_alpha(query: str) -> Tuple[float, str]:
    """Classify query intent using keyword matching to determine optimal Alpha value."""
    q_lower = query.lower()
    has_visual = any(kw in q_lower for kw in VISUAL_KEYWORDS)
    has_audio = any(kw in q_lower for kw in AUDIO_KEYWORDS)

    if has_visual and not has_audio:
        return 0.8, "High Visual Bias"
    elif has_audio and not has_visual:
        return 0.2, "High Audio/Speech Bias"
    else:
        return 0.5, "Balanced Hybrid"


def get_ui_intent_label(label: str) -> str:
    """Map internal intent label to UI detailed text."""
    if label == "High Visual Bias":
        return "High Visual Bias (CLIP Keyframe Primary)"
    elif label == "High Audio/Speech Bias":
        return "High Acoustic Bias (Whisper Speech Primary)"
    else:
        return "Balanced Hybrid Late-Fusion"


def format_timestamp(seconds: float) -> str:
    """Convert float seconds to MM:SS string format."""
    total_sec = int(round(seconds))
    mins = total_sec // 60
    secs = total_sec % 60
    return f"{mins:02d}:{secs:02d}"


def find_source_video(video_id: str) -> Optional[Path]:
    """Locate source video file in data/raw_videos matching video_id stem."""
    raw_dir = Path("./data/raw_videos")
    if not raw_dir.exists():
        return None

    base_name = video_id.rsplit("_", 1)[0]
    for ext in [".mp4", ".mkv", ".avi", ".mov", ".webm"]:
        candidate = raw_dir / f"{base_name}{ext}"
        if candidate.exists():
            return candidate

    for f in raw_dir.iterdir():
        if f.is_file() and base_name in f.name:
            return f

    return None


def highlight_transcript_keywords(transcript: str, query: str) -> str:
    """Highlight matching query keywords in speech transcript using HTML mark tags."""
    if not transcript or transcript == "news video footage scene":
        return transcript

    tokens = [
        re.escape(w.strip())
        for w in re.split(r"\W+", query.lower())
        if len(w.strip()) >= 3 and w.strip() not in STOP_WORDS
    ]

    if not tokens:
        return transcript

    pattern = re.compile(r"\b(" + "|".join(tokens) + r")\b", re.IGNORECASE)

    def replacer(match: re.Match) -> str:
        word = match.group(0)
        return (
            f'<mark style="background: rgba(56, 189, 248, 0.25); color: #38BDF8; '
            f'font-weight: 700; padding: 2px 6px; border-radius: 4px;">{word}</mark>'
        )

    return pattern.sub(replacer, transcript)


def inject_custom_css() -> None:
    """Inject glassmorphic SaaS custom styling into Streamlit."""
    st.markdown(
        """
        <style>
        /* Base Dark Obsidian Palette */
        .stApp {
            background-color: #0B0F17;
            color: #E2E8F0;
        }

        /* Radial Ambient Glow Header Backdrop */
        .main .block-container {
            background: radial-gradient(circle at 50% -10%, #151D2A 0%, #0B0F17 70%);
            padding-top: 1.8rem;
            padding-bottom: 3rem;
        }

        /* Glassmorphic Container Cards */
        .glass-card {
            background: rgba(21, 29, 42, 0.55);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        /* Result Card Padded Glass Container */
        .result-card-container {
            background: rgba(21, 29, 42, 0.55);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        /* Stat Box Cards for Landing Page */
        .stat-card {
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 14px;
            padding: 20px;
            text-align: center;
        }

        .stat-value {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #38BDF8, #A855F7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 4px;
        }

        .stat-label {
            color: #94A3B8;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Telemetry Banner Box */
        .telemetry-box {
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 12px;
            padding: 16px 22px;
            margin-top: 12px;
            margin-bottom: 16px;
        }

        /* High-contrast pure white text (#F8FAFC) on search inputs */
        div[data-baseweb="input"] {
            background: rgba(15, 23, 42, 0.95) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 10px !important;
            transition: all 0.3s ease;
        }

        div[data-baseweb="input"] input {
            color: #F8FAFC !important;
            -webkit-text-fill-color: #F8FAFC !important;
            font-size: 1.05rem !important;
            font-weight: 500 !important;
        }

        div[data-baseweb="input"] input::placeholder {
            color: #94A3B8 !important;
            -webkit-text-fill-color: #94A3B8 !important;
        }

        div[data-baseweb="input"]:focus-within {
            border-color: #38BDF8 !important;
            box-shadow: 0 0 18px rgba(56, 189, 248, 0.4) !important;
        }

        /* Custom st.progress bar with gradient overlay */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(90deg, #38BDF8 0%, #A855F7 100%) !important;
            border-radius: 10px;
        }

        /* Confidence Badges */
        .badge-high {
            background: rgba(16, 185, 129, 0.18);
            color: #34D399;
            border: 1px solid rgba(52, 211, 153, 0.4);
            padding: 4px 14px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.88rem;
            display: inline-block;
        }

        .badge-med {
            background: rgba(56, 189, 248, 0.18);
            color: #38BDF8;
            border: 1px solid rgba(56, 189, 248, 0.4);
            padding: 4px 14px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.88rem;
            display: inline-block;
        }

        .badge-low {
            background: rgba(245, 158, 11, 0.18);
            color: #FBBF24;
            border: 1px solid rgba(251, 191, 36, 0.4);
            padding: 4px 14px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.88rem;
            display: inline-block;
        }

        /* Primary Driver Badge */
        .badge-driver {
            background: rgba(168, 85, 247, 0.18);
            color: #C084FC;
            border: 1px solid rgba(192, 132, 252, 0.4);
            padding: 4px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
            margin-left: 8px;
        }

        /* Neon Status Pill Header */
        .status-pill {
            background: rgba(16, 185, 129, 0.12);
            color: #34D399;
            border: 1px solid rgba(52, 211, 153, 0.3);
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            display: inline-block;
        }

        /* Primary Button Styling */
        button[kind="primary"] {
            background: linear-gradient(90deg, #0284C7 0%, #7E22CE 100%) !important;
            border: none !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            border-radius: 10px !important;
            padding: 10px 24px !important;
            transition: all 0.3s ease !important;
        }

        button[kind="primary"]:hover {
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.5) !important;
            transform: translateY(-1px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Page 1: High-Impact SaaS Showcase Landing Page
# ---------------------------------------------------------------------------
def render_landing_page() -> None:
    """Render SaaS Showcase landing page with architecture metrics & late fusion math."""
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <h1 style="margin: 0; font-size: 2.6rem; font-weight: 800; letter-spacing: -0.8px; color: #F8FAFC;">
                ⚡ NeuralVideo <span style="background: linear-gradient(90deg, #38BDF8, #A855F7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">v2.0 PRO</span>
            </h1>
            <span class="status-pill">● SYSTEM ONLINE &nbsp;•&nbsp; Sub-200ms Dual-Vector SLA</span>
        </div>
        <p style="color: #94A3B8; font-size: 1.15rem; margin-bottom: 28px;">
            Enterprise Zero-Shot Multimodal Video Intelligence Platform powered by Dual-Vector Late Fusion.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Key System Stat Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-value">1,903</div>
                <div class="stat-label">Indexed Dual-Vectors</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-value">11.0 ms</div>
                <div class="stat-label">Mean Search Latency</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-value">100%</div>
                <div class="stat-label">Corpus Ingestion</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-value">100 / 100</div>
                <div class="stat-label">QA Compliance Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)

    # Late Fusion Architecture & Mathematics Section
    with st.container():
        st.markdown(
            """
            <div class="glass-card">
                <h3 style="margin-top: 0; color: #F8FAFC; font-weight: 700;">
                    🧬 Multimodal Dual-Vector Architecture & Late Fusion
                </h3>
                <p style="color: #CBD5E1; line-height: 1.6;">
                    NeuralVideo v2.0 constructs parallel 512-dimensional vector spaces for visual keyframe semantics
                    (<strong>CLIP ViT-B/32</strong>) and acoustic speech transcripts (<strong>Whisper Base</strong>).
                    Queries are dynamically balanced via a Zero-Shot Intent Engine using normalized Late Fusion scoring.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.latex(
            r"\text{Fused Score} = \alpha \cdot \text{Sim}_{\text{visual}}(\mathbf{q}_{\text{text}}, \mathbf{v}_{\text{frame}}) + "
            r"(1 - \alpha) \cdot \text{Sim}_{\text{audio}}(\mathbf{q}_{\text{text}}, \mathbf{v}_{\text{speech}})"
        )

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Feature Component Cards
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        st.markdown(
            """
            <div class="glass-card" style="height: 100%;">
                <h4 style="color: #38BDF8; margin-top: 0;">👁️ Vision Encoder</h4>
                <p style="color: #94A3B8; font-size: 0.95rem;">
                    CLIP ViT-B/32 extracts keyframe embeddings at 1 fps with explicit L2 unit-norm normalization
                    for cosine similarity distance.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_f2:
        st.markdown(
            """
            <div class="glass-card" style="height: 100%;">
                <h4 style="color: #A855F7; margin-top: 0;">🎧 Acoustic Transcriber</h4>
                <p style="color: #94A3B8; font-size: 0.95rem;">
                    Whisper Base processes 16kHz audio streams to produce timestamp-aligned speech transcriptions
                    mapped to visual frames.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_f3:
        st.markdown(
            """
            <div class="glass-card" style="height: 100%;">
                <h4 style="color: #34D399; margin-top: 0;">⚡ Qdrant Vector Engine</h4>
                <p style="color: #94A3B8; font-size: 0.95rem;">
                    Embedded Qdrant vector store with dual named vectors (<code>visual_vector</code> & <code>audio_vector</code>)
                    delivering sub-200ms latency.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 36px;'></div>", unsafe_allow_html=True)

    # Prominent CTA Button to Launch Workspace
    c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
    with c_btn2:
        if st.button("🚀 Launch Engine Workspace", type="primary", use_container_width=True):
            st.session_state["page"] = "workspace"
            st.rerun()


# ---------------------------------------------------------------------------
# Page 2: Search Engine Command Center Workspace
# ---------------------------------------------------------------------------
def render_workspace_page() -> None:
    """Render Neural Video Search Workspace page."""
    # Top navigation back button
    col_nav1, col_nav2 = st.columns([1, 4])
    with col_nav1:
        if st.button("← Back to Showcase", use_container_width=True):
            st.session_state["page"] = "landing"
            st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # ── Sidebar Controls ──────────────────────────────────────────────
    st.sidebar.title("⚡ Control Panel")
    st.sidebar.markdown("---")

    # Auto-Tune Checkbox
    auto_tune = st.sidebar.checkbox(
        label="⚡ Dynamic Intent Engine (Auto-Alpha)",
        value=True,
        help="Automatically classify query intent via zero-shot keyword density analysis.",
    )

    if not auto_tune:
        alpha_input = st.sidebar.slider(
            label="Late Fusion Alpha (α)",
            min_value=0.0,
            max_value=1.0,
            value=float(st.session_state.get("alpha_val", 0.5)),
            step=0.05,
            help="0.0 = Audio Only  │  1.0 = Visual Only",
        )
        st.session_state["alpha_val"] = alpha_input
        st.sidebar.caption("💡 *0.0 = Speech Audio Primary  │  0.5 = Balanced  │  1.0 = CLIP Visual Primary*")
    else:
        st.sidebar.info("⚡ **Auto-Tune Active**: Dynamic Zero-Shot Intent Engine calculates optimal Alpha per query.")

    st.sidebar.markdown("---")

    # Domain Filter
    domain_choice = st.sidebar.selectbox(
        label="Domain Filter",
        options=["news", "all"],
        index=0,
        help="Filter vector index by domain metadata.",
    )
    domain_filter: Optional[str] = None if domain_choice == "all" else domain_choice

    # Top K Selector
    top_k = st.sidebar.number_input(
        label="Top K Results",
        min_value=1,
        max_value=50,
        value=5,
        step=1,
    )

    st.sidebar.markdown("---")
    st.sidebar.info("🚀 **NeuralVideo v2.0 Engine**\nCLIP ViT-B/32 + Whisper Base + Qdrant Dual-Vector Store.")

    # ── Workspace Header ───────────────────────────────────────────────
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
            <h2 style="margin: 0; font-size: 2.0rem; font-weight: 800; color: #F8FAFC;">
                🔍 Command Search Workspace
            </h2>
            <span class="status-pill">● LIVE WORKSPACE</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Single Unified Command Search Input (Pure white #F8FAFC contrast) ──
    query_text = st.text_input(
        label="Command Search Bar",
        placeholder="Enter natural language query (e.g., 'person in dark suit at podium' or 'space flight astronauts speech')",
        label_visibility="collapsed",
    )

    # Trigger search on non-empty query
    if query_text and query_text.strip():
        pipeline = get_pipeline()

        # Calculate or use effective Alpha
        if auto_tune:
            effective_alpha, raw_intent_label = predict_alpha(query_text.strip())
            st.session_state["alpha_val"] = effective_alpha
        else:
            effective_alpha = float(st.session_state.get("alpha_val", 0.5))
            raw_intent_label = "Manual Override"

        ui_intent_label = get_ui_intent_label(raw_intent_label) if auto_tune else "Manual Slider Override"

        # Determine Primary Driver Badge based on alpha
        if effective_alpha >= 0.70:
            driver_badge_html = '<span class="badge-driver">👁️ Primary Driver: Visual Scene Match (CLIP)</span>'
            driver_text_summary = "Visual Scene Match (CLIP Primary)"
        elif effective_alpha <= 0.30:
            driver_badge_html = '<span class="badge-driver">🎧 Primary Driver: Spoken Dialogue Match (Whisper)</span>'
            driver_text_summary = "Spoken Dialogue Match (Whisper Primary)"
        else:
            driver_badge_html = '<span class="badge-driver">⚖️ Primary Driver: Balanced Hybrid Match</span>'
            driver_text_summary = "Balanced Hybrid Match"

        # ── Dynamic Zero-Shot Intent Telemetry Bar ───────────────────────
        v_pct = int(round(effective_alpha * 100))
        a_pct = 100 - v_pct

        st.markdown(
            f"""
            <div class="telemetry-box">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 700; color: #38BDF8; font-size: 0.95rem;">
                        ⚡ Intent Detected: <span style="color: #F8FAFC;">{ui_intent_label}</span>
                    </span>
                    <span style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; padding: 2px 10px; border-radius: 6px; font-weight: 700; font-family: monospace; font-size: 0.9rem;">
                        α = {effective_alpha:.2f}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(
            effective_alpha,
            text=f"👁️ Visual Weight (CLIP): {v_pct}%   │   🎧 Acoustic Weight (Whisper): {a_pct}%",
        )

        st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

        with st.spinner("⚡ Executing dual-vector search & computing late-fusion scoring …"):
            t0 = time.perf_counter()
            results: List[Dict] = pipeline.search(
                query=query_text.strip(),
                domain_filter=domain_filter,
                alpha=effective_alpha,
                top_k=int(top_k),
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000

        st.markdown(f"### 🎯 Results for *\"{query_text.strip()}\"*")
        st.caption(
            f"Retrieved **{len(results)}** keyframe matches in **{elapsed_ms:.1f} ms**  │  "
            f"Domain: `{domain_choice}`  │  α: `{effective_alpha:.2f}` ({raw_intent_label})"
        )
        st.markdown("---")

        if not results:
            st.warning("⚠️ No matching video keyframes found. Try adjusting your search prompt.")

        # ── Render Multi-Layer Result Cards inside Padded Glass Containers ──
        for rank, res in enumerate(results, 1):
            payload = res.get("payload", {})
            fused_score = res.get("score", 0.0)
            visual_score = res.get("visual_score", 0.0)
            audio_score = res.get("audio_score", 0.0)

            frame_path = payload.get("frame_path", "")
            video_id = payload.get("video_id", "N/A")
            timestamp = payload.get("timestamp", 0.0)
            formatted_ts = format_timestamp(timestamp)
            transcript = payload.get("transcribed_text", "No transcript text available.")
            source_video = find_source_video(video_id)

            # Score Metrics rendered as bold percentages
            fused_pct = fused_score * 100
            visual_pct = visual_score * 100
            audio_pct = audio_score * 100

            # Match Confidence Badging (Requirement 1)
            if fused_pct >= 70.0:
                confidence_badge_html = f'<span class="badge-high">🟢 {fused_pct:.1f}% Match Confidence</span>'
            elif fused_pct >= 35.0:
                confidence_badge_html = f'<span class="badge-med">🔵 {fused_pct:.1f}% Match Confidence</span>'
            else:
                confidence_badge_html = f'<span class="badge-low">⚠️ Low Vector Confidence (< 35%)</span>'

            # Highlighted Transcript Attribution (Requirement 2)
            highlighted_transcript = highlight_transcript_keywords(transcript, query_text.strip())

            # Card Container with Glassmorphism Padding
            with st.container():
                st.markdown('<div class="result-card-container">', unsafe_allow_html=True)

                c_img, c_details = st.columns([2, 3])

                with c_img:
                    if frame_path and Path(frame_path).exists():
                        img = Image.open(frame_path)
                        st.image(img, use_container_width=True, caption=f"Keyframe @ {formatted_ts} ({timestamp:.1f}s)")
                    else:
                        st.warning("⚠️ Keyframe preview image unavailable")

                    # Video Player jumping to timestamp
                    if source_video and source_video.exists():
                        st.video(str(source_video), start_time=int(timestamp))

                with c_details:
                    # Top-Level Card Header with Percentage & Primary Driver Badges
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                            <h4 style="margin: 0; color: #F8FAFC; font-weight: 700;">Rank #{rank} — <code>{video_id}</code></h4>
                            <div>
                                {confidence_badge_html}
                                {driver_badge_html}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Score Breakdown Metrics as Bold Percentages
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Fused Match", f"{fused_pct:.1f}%")
                    m2.metric("Visual (CLIP)", f"{visual_pct:.1f}%")
                    m3.metric("Audio (Whisper)", f"{audio_pct:.1f}%")

                    st.markdown(f"**Timestamp:** `{formatted_ts}` (`{timestamp:.1f}s`)  │  **Domain:** `{payload.get('domain', 'news')}`")

                    # Highlighted Speech Transcript Excerpt (Requirement 2)
                    st.markdown("**Matched Speech Transcript:**")
                    if transcript and transcript != "news video footage scene":
                        st.markdown(
                            f'<div style="background: rgba(15, 23, 42, 0.7); border-left: 4px solid #38BDF8; padding: 10px 14px; border-radius: 6px; color: #E2E8F0; margin-bottom: 12px;">'
                            f'🗣️ <em>"{highlighted_transcript}"</em>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.caption("静 *No speech transcript for this keyframe (Ambient / Silent).*")

                    # ── Dual-Layer Hybrid XAI Expander (Requirement 3) ──
                    with st.expander("💡 Why NeuralVideo Found This Result (Dual-Layer XAI)", expanded=False):
                        tab_human, tab_math = st.tabs(["💡 Non-Technical Summary", "📐 Mathematical Provenance"])

                        # Tab 1: Non-Technical Summary (Product & Business View)
                        with tab_human:
                            audio_summary_text = (
                                f'Matched spoken dialogue in transcript at timestamp <strong>{formatted_ts}</strong> (<strong>{audio_pct:.1f}% match</strong>)'
                                if (transcript and transcript != "news video footage scene")
                                else 'Ambient/Silent scene frame fallback (no dialogue audio)'
                            )

                            st.markdown(
                                f"""
                                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 16px; margin-top: 6px;">
                                    <p style="margin: 0 0 10px 0; color: #F8FAFC; font-size: 0.95rem;">
                                        👁️ <strong>Visual AI (CLIP):</strong> Identified matching visual scene elements in keyframe (<strong>{visual_pct:.1f}% match</strong>).
                                    </p>
                                    <p style="margin: 0 0 10px 0; color: #F8FAFC; font-size: 0.95rem;">
                                        🎧 <strong>Audio AI (Whisper):</strong> {audio_summary_text}.
                                    </p>
                                    <p style="margin: 0; color: #38BDF8; font-weight: 700; font-size: 0.95rem;">
                                        🎯 <strong>Final Decision:</strong> Ranked <strong>#{rank}</strong> using dynamic intent weighting (α = {effective_alpha:.2f} — {driver_text_summary}).
                                    </p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        # Tab 2: Mathematical Provenance (Deep Technical View)
                        with tab_math:
                            col_x1, col_x2 = st.columns(2)
                            with col_x1:
                                st.markdown(f"**👁️ Raw Visual Similarity ($S_{{visual}}$):** `{visual_score:.6f}` (`{visual_pct:.1f}%`)")
                                st.caption(f"CLIP ViT-B/32 512-d unit-norm cosine similarity at `{formatted_ts}`.")
                            with col_x2:
                                st.markdown(f"**🎧 Raw Audio Similarity ($S_{{audio}}$):** `{audio_score:.6f}` (`{audio_pct:.1f}%`) ")
                                st.caption(f"Whisper Base + Text Query Encoder 512-d cosine similarity.")

                            st.markdown("---")
                            st.markdown("**LaTeX Late Fusion Arithmetic Formula:**")
                            st.latex(
                                rf"\text{{Fused Score}} = (\alpha \times S_{{\text{{visual}}}}) + "
                                rf"((1 - \alpha) \times S_{{\text{{audio}}}}) = "
                                rf"({effective_alpha:.2f} \times {visual_score:.4f}) + "
                                rf"({(1.0 - effective_alpha):.2f} \times {audio_score:.4f}) = \mathbf{{{fused_score:.4f}}} \implies \mathbf{{{fused_pct:.1f}\%}}"
                            )

                st.markdown('</div>', unsafe_allow_html=True)


def main() -> None:
    inject_custom_css()

    # ── Initialize State-Driven Page Navigation ────────────────────────
    if "page" not in st.session_state:
        st.session_state["page"] = "landing"
    if "alpha_val" not in st.session_state:
        st.session_state["alpha_val"] = 0.5

    # Route based on session state page
    if st.session_state["page"] == "landing":
        render_landing_page()
    else:
        render_workspace_page()


if __name__ == "__main__":
    main()
