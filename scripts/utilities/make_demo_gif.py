"""
Generate a portfolio demo GIF for NeuralVideo v5.0.

Simulates the search flow:
  1. Landing page
  2. Typing a query in the search console
  3. Loading state (pipeline storytelling bar + skeletons)
  4. Full results page (timeline track, keyframe gallery, video player, XAI grid)
  5. Result selected change (timeline pin moves, XAI scores update)

Frames are drawn with PIL and stitched into a GIF with ffmpeg.

Usage:
    python scripts/utilities/make_demo_gif.py
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
W, H = 1280, 720
FPS = 10
BG = (8, 8, 10)          # #08080a
CARD = (12, 12, 15)      # #0c0c0c
CYAN = (6, 182, 212)     # #06B6D4
CYAN_DIM = (6, 182, 212, 60)
EMERALD = (16, 185, 129) # #10B981
AMBER = (245, 158, 11)   # #F59E0B
SLATE = (148, 163, 184)  # #94A3B8
TEXT = (230, 225, 213)   # #E6E1D5
MUTED = (156, 163, 175)  # #9CA3AF
WIRE = (230, 225, 213, 40)

FONT_BOLD = "/System/Library/Fonts/Supplemental/Helvetica.ttc"
FONT_MONO = "/System/Library/Fonts/SFNSMonoItalic.ttf"  # SF NS Mono
FONT_UI = "/System/Library/Fonts/SFNS.ttf"


def load_font(size: int, mono: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_MONO if mono else FONT_UI
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def rounded_rect(d: ImageDraw.ImageDraw, xy, radius: int, fill, outline=None, outline_w: int = 1):
    x0, y0, x1, y1 = xy
    d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=outline_w)


def shadow_rect(d: ImageDraw.ImageDraw, xy, radius: int, fill, offset: int = 4, alpha: int = 60):
    x0, y0, x1, y1 = xy
    d.rounded_rectangle([x0 + offset, y0 + offset, x1 + offset, y1 + offset], radius=radius, fill=(*fill[:3], alpha))


class Canvas:
    def __init__(self, w: int = W, h: int = H):
        self.img = Image.new("RGBA", (w, h), (*BG, 255))
        self.d = ImageDraw.Draw(self.img, "RGBA")

    def rect(self, xy, fill, radius: int = 0, outline=None, outline_w: int = 1):
        if radius > 0:
            rounded_rect(self.d, xy, radius, fill, outline, outline_w)
        else:
            self.d.rectangle(xy, fill=fill, outline=outline, width=outline_w)

    def text(self, xy, s: str, font, fill=TEXT, anchor=None):
        self.d.text(xy, s, font=font, fill=fill, anchor=anchor)

    def line(self, xy, fill, width: int = 1):
        self.d.line(xy, fill=fill, width=width)

    def save(self, path: str):
        self.img.convert("RGB").save(path)

    def to_pil(self) -> Image.Image:
        return self.img


def make_frame() -> Canvas:
    return Canvas()


# ---------------------------------------------------------------------------
# Reusable components
# ---------------------------------------------------------------------------

def header(c: Canvas, page_label: str = "DEMO"):
    """Top header bar."""
    c.rect([0, 0, W, 72], BG)
    c.rect([0, 72, W, 73], (*WIRE[:3], 60))
    # Brand
    c.rect([24, 20, 44, 52], CYAN, radius=8)
    c.text((52, 26), "NEURALVIDEO", load_font(20, mono=True), fill=TEXT)
    c.text((52, 48), "v5.0", load_font(14, mono=True), fill=CYAN)
    # Nav
    for i, label in enumerate(["DEMO", "CONSOLE", "XAI"]):
        active = label == page_label
        x = 300 + i * 110
        c.rect([x, 24, x + 90, 50], CYAN if active else None, radius=10, outline=CYAN if active else (*WIRE[:3], 80), outline_w=2)
        c.text((x + 45, 37), label, load_font(13, mono=True), fill=TEXT if active else MUTED, anchor="mm")
    # Status right
    c.text((W - 260, 36), "SYSTEM STATUS: READY", load_font(12, mono=True), fill=EMERALD)
    c.rect([W - 236, 29, W - 226, 39], EMERALD, radius=2)


def landing_page(c: Canvas):
    header(c, "DEMO")
    c.rect([0, 72, W, H], BG)
    # Badge
    c.text((W // 2 - 220, 150), "HACKATHON JUDGE DEMO MODE  •  SUB-300MS CPU LATENCY", load_font(13, mono=True), fill=EMERALD)
    # Hero title
    c.text((W // 2 - 320, 200), "NEURALVIDEO", load_font(100), fill=TEXT)
    c.text((W // 2 + 240, 210), "PRO", load_font(100), fill=CYAN)
    # Tagline
    c.text((W // 2 - 420, 320), "Sub-second cross-modal video search fusing CLIP ViT-B/32 keyframes", load_font(20), fill=MUTED)
    c.text((W // 2 - 420, 350), "and Whisper Base dialogue transcripts with Reciprocal Rank Fusion & XAI.", load_font(20), fill=MUTED)
    # Metrics grid
    metrics = [
        ("SEARCH SLA", "< 300ms", EMERALD),
        ("VECTOR STORE", "Qdrant 512-D", CYAN),
        ("INDEX POINTS", "2086", TEXT),
        ("EXPLAINABILITY", "RRF + XAI", CYAN),
    ]
    for i, (label, val, color) in enumerate(metrics):
        x = 160 + i * 270
        y = 430
        c.rect([x, y, x + 230, y + 110], CARD, radius=16, outline=(*WIRE[:3], 60))
        c.text((x + 20, y + 16), label, load_font(11, mono=True), fill=MUTED)
        c.text((x + 20, y + 42), val, load_font(22, mono=True), fill=color)
    # CTA
    c.rect([W // 2 - 150, 580, W // 2 + 150, 640], CYAN, radius=14)
    c.text((W // 2, 607), "ENTER SEARCH CONSOLE", load_font(18, mono=True), fill=BG, anchor="mm")


def search_console(c: Canvas, query: str = "", active: bool = False):
    header(c, "CONSOLE")
    c.rect([0, 72, W, H], BG)
    c.text((40, 110), "SEARCH CONSOLE  //  LIVE PIPELINE STORYTELLING", load_font(14, mono=True), fill=CYAN)
    c.text((40, 134), "MULTIMODAL SEARCH", load_font(48, mono=True), fill=TEXT)
    # Search bar
    bar_x, bar_y, bar_w, bar_h = 120, 240, 700, 100
    c.rect([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], CARD, radius=24, outline=CYAN if active else (*WIRE[:3], 80), outline_w=3)
    c.text((bar_x + 30, bar_y + 30), 'Try "speaker discussing transformers"...', load_font(20), fill=MUTED if not query else TEXT)
    c.text((bar_x + 30, bar_y + 62), query + ("_" if active else ""), load_font(22, mono=True), fill=TEXT)
    # Submit
    btn_x = bar_x + bar_w + 20
    c.rect([btn_x, bar_y, btn_x + 140, bar_y + bar_h], CYAN, radius=24)
    c.text((btn_x + 70, bar_y + bar_h // 2), "SEARCH", load_font(18, mono=True), fill=BG, anchor="mm")
    # Query chips
    chips = [
        "security camera incident",
        "speaker discussing transformers",
        "person explaining neural networks",
        "television lowest common denominator",
    ]
    cy = 380
    cx = 40
    for chip in chips:
        c.rect([cx, cy, cx + 260, cy + 52], CARD, radius=26, outline=(*WIRE[:3], 60))
        c.text((cx + 18, cy + 26), chip, load_font(14, mono=True), fill=MUTED, anchor="lm")
        cx += 270
        if cx > W - 300:
            cx = 40
            cy += 62


def loading_state(c: Canvas, stage: int = 4):
    header(c, "CONSOLE")
    c.rect([0, 72, W, H], BG)
    c.text((40, 110), "LIVE PIPELINE STORYTELLING VISUALIZATION", load_font(14, mono=True), fill=CYAN)
    c.text((40, 134), f"STEP {stage} OF 6", load_font(14, mono=True), fill=SLATE)
    steps = [
        (1, "Encoding Query...", "CLIP ViT-B/32 & Text Transformer"),
        (2, "Searching Visual Index...", "512-D Vision Vectors"),
        (3, "Searching Audio Index...", "16kHz Whisper Transcripts"),
        (4, "Fusing Results (RRF)...", "Reciprocal Rank Fusion"),
        (5, "Diversifying Results (MMR)...", "Semantic Vector Diversity"),
        (6, "Returning Top Match...", "Confidence Scoring & Playback"),
    ]
    # Pipeline grid 2x3
    for i, (num, title, desc) in enumerate(steps):
        gx = 120 + (i % 3) * 410
        gy = 220 + (i // 3) * 140
        done = num < stage
        active = num == stage
        c.rect([gx, gy, gx + 380, gy + 120], CARD, radius=16,
               outline=CYAN if active else (EMERALD if done else (*WIRE[:3], 40)),
               outline_w=2 if active or done else 1)
        c.rect([gx + 18, gy + 50, gx + 42, gy + 84], CYAN if done else None, radius=4)
        c.text((gx + 56, gy + 22), f"STEP {num}", load_font(12, mono=True), fill=CYAN if done else MUTED)
        c.text((gx + 56, gy + 42), title, load_font(15, mono=True), fill=TEXT if active else MUTED)
        c.text((gx + 56, gy + 62), desc, load_font(12), fill=MUTED)
    # Spinner
    c.rect([W // 2 - 60, H - 140, W // 2 + 60, H - 60], CARD, radius=24)
    c.text((W // 2, H - 100), "COMPUTING...", load_font(16, mono=True), fill=CYAN, anchor="mm")


def results_page(c: Canvas, selected_idx: int = 0):
    header(c, "XAI")
    c.rect([0, 72, W, H], BG)
    c.text((40, 104), f'RESULTS  //  {3 - selected_idx} MATCHES FOR "speaker discussing transformers"  (142ms)', load_font(13, mono=True), fill=TEXT)
    # Timeline track
    c.rect([120, 160, W - 120, 220], CARD, radius=12, outline=(*WIRE[:3], 60))
    c.text((140, 170), "RETRIEVAL TIMELINE TRACK", load_font(11, mono=True), fill=CYAN)
    c.text((W - 260, 170), "0:00  ➔  19:30", load_font(11, mono=True), fill=MUTED)
    c.rect([120, 188, W - 120, 202], (*WIRE[:3], 40), radius=2)
    # Result pins
    pins = [180, 420, 760]
    colors = [CYAN, EMERALD, AMBER]
    labels = ["#1", "#2", "#3"]
    for i, (px, col, lab) in enumerate(zip(pins, colors, labels)):
        sel = i == selected_idx
        c.rect([px - 12, 184, px + 12, 206], col if sel else CARD, radius=8, outline=col if sel else (*WIRE[:3], 80), outline_w=2)
        c.text((px, 195), lab, load_font(11, mono=True), fill=BG if sel else col, anchor="mm")
    # Keyframe gallery (left)
    c.text((120, 250), "TIMELINE MATCH REEL", load_font(13, mono=True), fill=CYAN)
    cards = [
        ("Steve Jobs Interview", "09:42", "89.2%", "09:42", CYAN),
        ("Steve Jobs Interview", "11:08", "76.4%", "11:08", EMERALD),
        ("Steve Jobs Interview", "13:15", "61.8%", "13:15", AMBER),
    ]
    for i, (vid, ts, pct, h_ts, col) in enumerate(cards):
        y = 280 + i * 130
        sel = i == selected_idx
        c.rect([120, y, 460, y + 110], CARD, radius=14,
               outline=col if sel else (*WIRE[:3], 60), outline_w=3 if sel else 1)
        c.text((140, y + 14), f"RANK #{i + 1}", load_font(11, mono=True, ), fill=col if sel else MUTED)
        c.rect([140, y + 34, 440, y + 94], (20, 20, 25), radius=8)
        c.text((160, y + 56), f"FRAME {h_ts}", load_font(11, mono=True), fill=col)
        c.text((140, y + 100), f"{vid}", load_font(12, mono=True), fill=TEXT)
        c.text((300, y + 100), f"{pct} MATCH", load_font(12, mono=True, ), fill=EMERALD)
    # Video player (right)
    c.rect([490, 280, W - 40, 620], CARD, radius=16, outline=(*WIRE[:3], 60))
    c.rect([510, 300, W - 60, 500], (20, 20, 25), radius=12)
    c.text((530, 320), "SYNCHRONIZED VIDEO PLAYER", load_font(11, mono=True), fill=CYAN)
    c.text((530, 350), "Steve Jobs Interview Feb 18 1981", load_font(16), fill=TEXT)
    c.text((530, 380), "09:42", load_font(24, mono=True), fill=CYAN)
    c.rect([510, 510, W - 60, 540], (*WIRE[:3], 60), radius=4)
    c.text((510, 552), "MATCH TIMESTAMP: 09:42 (582.0s)", load_font(11, mono=True), fill=TEXT)
    c.rect([620, 544, 760, 576], CYAN, radius=10)
    c.text((690, 560), "▶ JUMP TO TIMESTAMP", load_font(11, mono=True), fill=BG, anchor="mm")
    # XAI grid bottom
    c.text((120, 640), "TECHNICAL ML SCORE CALCULATIONS", load_font(11, mono=True), fill=EMERALD)
    scores = [("FUSED SCORE", "89.2%", CYAN), ("VISUAL (CLIP)", "62.1%", CYAN), ("AUDIO (WHISPER)", "89.2%", EMERALD)]
    for i, (label, val, col) in enumerate(scores):
        x = 120 + i * 370
        c.rect([x, 660, x + 350, 660 + 120], CARD, radius=12, outline=(*WIRE[:3], 60))
        c.text((x + 16, 674), label, load_font(11, mono=True), fill=MUTED)
        c.text((x + 16, 694), val, load_font(20, mono=True), fill=col)


# ---------------------------------------------------------------------------
# Frame sequence
# ---------------------------------------------------------------------------

def build_frames(tmpdir: Path) -> list[str]:
    frames: list[str] = []

    def add(canvas: Canvas, count: int, tag: str):
        for _ in range(count):
            p = tmpdir / f"frame_{len(frames):04d}.png"
            canvas.save(str(p))
            frames.append(str(p))

    # 1. Landing page (~1s)
    c = make_frame()
    landing_page(c)
    add(c, FPS, "landing")

    # 2. Typing query (~1.5s)
    query = ""
    for ch in 'speaker discussing transformers':
        query += ch
        c = make_frame()
        search_console(c, query, active=True)
        add(c, FPS // 2, f"typing_{ch}")

    # 3. Loading (~1.5s)
    c = make_frame()
    loading_state(c, stage=4)
    add(c, FPS * 2, "loading")

    # 4. Results page - result #1 selected (~1s)
    c = make_frame()
    results_page(c, selected_idx=0)
    add(c, FPS, "results_1")

    # 5. Results page - result #2 selected (~1s)
    c = make_frame()
    results_page(c, selected_idx=1)
    add(c, FPS, "results_2")

    # 6. Results page - result #3 selected (~1s)
    c = make_frame()
    results_page(c, selected_idx=2)
    add(c, FPS, "results_3")

    return frames


def main():
    out = Path("docs/demo.gif")
    out.parent.mkdir(parents=True, exist_ok=True)

    tmpdir = Path(tempfile.mkdtemp(prefix="neuralvideo_demo_"))
    print(f"Generating frames in {tmpdir} …")

    frames = build_frames(tmpdir)
    print(f"Generated {len(frames)} frames.")

    # Stitch with ffmpeg (loop palette for smooth GIF)
    palette = tmpdir / "palette.png"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(tmpdir / "frame_%04d.png"),
        "-vf", "fps=10,scale=1280:720:flags=lanczos,palettegen",
        str(palette),
    ], check=True, capture_output=True)

    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(tmpdir / "frame_%04d.png"),
        "-i", str(palette),
        "-filter_complex", "fps=10,scale=1280:720:flags=lanczos[x];[x][1:v]paletteuse",
        "-loop", "0",
        str(out),
    ], check=True, capture_output=True)

    size = out.stat().st_size / 1024
    print(f"Demo GIF written to {out} ({size:.1f} KB)")


if __name__ == "__main__":
    main()
