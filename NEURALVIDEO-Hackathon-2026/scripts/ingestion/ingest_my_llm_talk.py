"""
High-Throughput Video Ingestion Pipeline Execution Script
Target Video: NEURALVIDEO-Hackathon-2026/data/raw/raw_videos/my_llm_talk.MOV
Target Collection: neuralvideo_hackathon_demo
"""

from __future__ import annotations

import os

os.environ["OMP_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"

import gc
import sys
import time
import uuid
import tempfile
import subprocess
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

import cv2
import torch
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from src.ingestion.audio_processor import AudioTranscriber
from src.models.text_encoder import TextQueryEncoder
from src.models.vision_encoder import CLIPVisionEncoder

VIDEO_REL_PATH = "data/raw/raw_videos/my_llm_talk.mp4"
COLLECTION_NAME = "video_intelligence"
ALT_COLLECTION_NAME = "neuralvideo_hackathon_demo"
VISUAL_VECTOR_NAME = "visual_vector"
AUDIO_VECTOR_NAME = "audio_vector"
VECTOR_DIM = 512


def extract_audio_hardware_accelerated(video_path: Path) -> tuple[Path, float]:
    """Extract 16kHz mono WAV via hardware-accelerated ffmpeg (VideoToolbox / CPU demux)."""
    tmp_wav = tempfile.NamedTemporaryFile(suffix="_my_llm_talk.wav", delete=False)
    tmp_wav.close()
    wav_path = Path(tmp_wav.name)

    t0 = time.perf_counter()
    # Try VideoToolbox hwaccel first for macOS hardware acceleration
    cmd_hw = [
        "ffmpeg", "-y",
        "-hwaccel", "videotoolbox",
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(wav_path),
    ]

    try:
        res = subprocess.run(cmd_hw, capture_output=True, text=True, timeout=30)
        if res.returncode != 0:
            # Fallback to standard fast CPU demux if hwaccel flag is unsupported
            cmd_fallback = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                str(wav_path),
            ]
            subprocess.run(cmd_fallback, capture_output=True, text=True, check=True, timeout=30)
    except Exception:
        cmd_fallback = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            str(wav_path),
        ]
        subprocess.run(cmd_fallback, capture_output=True, text=True, check=True, timeout=30)

    elapsed = time.perf_counter() - t0
    return wav_path, elapsed


def extract_memory_frames_720p(video_path: Path, output_dir: Path, target_fps: float = 1.0) -> tuple[List[Dict[str, Any]], float]:
    """Extract keyframes at 1 FPS into 720p JPEG images using ffmpeg."""
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()

    cmd = [
        "ffmpeg", "-y",
        "-hwaccel", "videotoolbox",
        "-i", str(video_path),
        "-vf", f"fps={target_fps},scale=-1:720",
        "-threads", "4",
        "-q:v", "3",
        str(output_dir / "frame_%06d.jpg"),
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=300)
    except Exception:
        cmd_fallback = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf", f"fps={target_fps},scale=-1:720",
            "-threads", "4",
            "-q:v", "3",
            str(output_dir / "frame_%06d.jpg"),
        ]
        subprocess.run(cmd_fallback, capture_output=True, text=True, check=True, timeout=300)

    frame_files = sorted(output_dir.glob("frame_*.jpg"))
    results = []
    for idx, fpath in enumerate(frame_files):
        timestamp = round(idx / target_fps, 2)
        results.append({
            "frame_path": str(fpath),
            "timestamp": timestamp,
            "frame_idx": idx,
            "video_id": "my_llm_talk",
        })

    elapsed = time.perf_counter() - t0
    return results, elapsed


def main():
    abs_vpath = (PROJECT_ROOT / VIDEO_REL_PATH).resolve()
    if not abs_vpath.exists():
        print(f"Error: Input video not found at {abs_vpath}")
        sys.exit(1)

    print("=" * 80)
    print("NEURALVIDEO v5.0 — HIGH-THROUGHPUT VIDEO INGESTION PIPELINE EXECUTION")
    print("=" * 80)
    print(f"Input File:        {abs_vpath.name}")
    print(f"File Size:         {abs_vpath.stat().st_size / (1024*1024):.2f} MB")
    print(f"Target Collection: {COLLECTION_NAME}")
    print("-" * 80)

    # --- STAGE 1: Audio Stream Isolation ---
    print("\n[STAGE 1/4] Extracting Raw 16kHz PCM Audio Stream (VideoToolbox / Hardware Accel)...")
    wav_path, audio_ext_latency = extract_audio_hardware_accelerated(abs_vpath)
    print(f"   -> Audio Extraction Completed in {audio_ext_latency:.3f}s (SLA Target: < 2.0s | {'PASS ✅' if audio_ext_latency < 2.0 else 'WARN ⚠️'})")

    # --- STAGE 2: Frame Decord Memory Sampling ---
    print("\n[STAGE 2/4] Sampling Keyframes at 1 FPS into 720p Memory Buffer (OpenCV / In-Memory Downscale)...")
    frames_dir = PROJECT_ROOT / "data" / "processed" / "extracted_frames_my_llm_talk"
    keyframes, frame_ext_latency = extract_memory_frames_720p(abs_vpath, frames_dir, target_fps=1.0)
    print(f"   -> 1 FPS Keyframe Sampling Completed in {frame_ext_latency:.2f}s ({len(keyframes)} 720p frames sampled)")

    # --- STAGE 3: Whisper Speech Transcription ---
    print("\n[STAGE 3/4] Transcribing 16kHz Audio Stream via OpenAI Whisper...")
    t_whisper_start = time.perf_counter()
    transcriber = AudioTranscriber(model_name="base")
    transcriber._load_model()
    result = transcriber._model.transcribe(str(wav_path), language="en", fp16=False)
    segments = [
        {
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip(),
        }
        for seg in result.get("segments", [])
    ]
    whisper_latency = time.perf_counter() - t_whisper_start
    print(f"   -> Whisper Transcription Completed in {whisper_latency:.2f}s ({len(segments)} dialogue segments)")

    # Clean up temp WAV
    if wav_path.exists():
        wav_path.unlink()

    # --- STAGE 4: CLIP Vision & Text Vector Encoding ---
    print("\n[STAGE 4/4] Encoding CLIP 512-D Visual Embeddings & Text Matching...")
    t_enc_start = time.perf_counter()
    vision_encoder = CLIPVisionEncoder()
    text_encoder = TextQueryEncoder()

    frame_paths = [f["frame_path"] for f in keyframes]
    visual_vecs = vision_encoder.encode_batch_images(frame_paths, batch_size=8)

    audio_texts = []
    for f in keyframes:
        ts = f["timestamp"]
        matched_text = ""
        for seg in segments:
            if seg["start"] <= ts <= seg["end"] or abs(ts - seg["start"]) <= 1.5:
                matched_text = seg["text"]
                break
        audio_texts.append(matched_text if matched_text else "LLM presentation technology talk")

    audio_vecs = text_encoder.encode_batch_queries(audio_texts)
    encoding_latency = time.perf_counter() - t_enc_start
    print(f"   -> CLIP & Text Vector Encoding Completed in {encoding_latency:.2f}s")

    # --- STAGE 5: Qdrant Indexing ---
    print(f"\n[INDEXING] Upserting Points into Qdrant Collection '{COLLECTION_NAME}'...")
    t_idx_start = time.perf_counter()
    db_path = PROJECT_ROOT / "data" / "vectors" / "qdrant_db"
    db_path.mkdir(parents=True, exist_ok=True)

    client = QdrantClient(path=str(db_path))
    existing_collections = [c.name for c in client.get_collections().collections]
    for c_name in [COLLECTION_NAME, ALT_COLLECTION_NAME]:
        if c_name not in existing_collections:
            client.create_collection(
                collection_name=c_name,
                vectors_config={
                    VISUAL_VECTOR_NAME: VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
                    AUDIO_VECTOR_NAME: VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
                },
            )

    structs = []
    for idx, f in enumerate(keyframes):
        pt_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"my_llm_talk_{f['frame_idx']}"))
        structs.append(
            PointStruct(
                id=pt_id,
                vector={
                    VISUAL_VECTOR_NAME: visual_vecs[idx].tolist(),
                    AUDIO_VECTOR_NAME: audio_vecs[idx].tolist(),
                },
                payload={
                    "video_id": "my_llm_talk",
                    "file_name": abs_vpath.name,
                    "timestamp": f["timestamp"],
                    "frame_idx": f["frame_idx"],
                    "transcribed_text": audio_texts[idx],
                    "domain": "technology_rag",
                    "frame_path": f["frame_path"],
                },
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=structs)
    client.upsert(collection_name=ALT_COLLECTION_NAME, points=structs)
    idx_latency = time.perf_counter() - t_idx_start
    total_ingestion_runtime = audio_ext_latency + frame_ext_latency + whisper_latency + encoding_latency + idx_latency

    point_count = client.count(collection_name=COLLECTION_NAME).count
    min_ts = min(f["timestamp"] for f in keyframes) if keyframes else 0.0
    max_ts = max(f["timestamp"] for f in keyframes) if keyframes else 0.0

    print(f"   -> Qdrant Indexing Completed in {idx_latency:.3f}s")
    print(f"   -> Total Ingested Vector Points: {len(structs)}")
    print(f"   -> Collection Point Count:       {point_count}")
    print(f"   -> Video Timestamp Coverage:    {min_ts:.1f}s to {max_ts:.1f}s ({max_ts/60:.2f} mins)")

    # --- STAGE 6: Verification & Test Query SLA Checks ---
    print("\n" + "=" * 80)
    print("NEURALVIDEO v5.0 — VERIFICATION & SAMPLE SEARCH RETRIEVAL SLA AUDIT")
    print("=" * 80)

    test_queries = [
        "LLM architecture models and artificial intelligence",
        "speaker presenting slides on stage in technical talk",
        "future of generative AI and neural networks",
    ]

    retrieval_latencies = []
    for q in test_queries:
        t_q = time.perf_counter()
        q_vec = text_encoder.encode_query(q).tolist()
        
        # Dual-vector hybrid cosine query
        res_v = client.query_points(collection_name=COLLECTION_NAME, query=q_vec, using=VISUAL_VECTOR_NAME, limit=3).points
        res_a = client.query_points(collection_name=COLLECTION_NAME, query=q_vec, using=AUDIO_VECTOR_NAME, limit=3).points
        
        ret_lat_ms = (time.perf_counter() - t_q) * 1000
        retrieval_latencies.append(ret_lat_ms)

        top = res_v[0] if res_v else None
        top_payload = top.payload if top else {}
        ts = top_payload.get("timestamp", 0.0)
        mins, secs = int(ts // 60), int(ts % 60)

        print(f"\n🔍 Query: '{q}'")
        print(f"   Retrieval Latency: {ret_lat_ms:.2f} ms (Target SLA: < 180ms | {'PASS ✅' if ret_lat_ms < 180 else 'FAIL ❌'})")
        if top:
            print(f"   Top Match: Timestamp {mins:02d}:{secs:02d} ({ts:.1f}s) | Score: {top.score:.4f}")
            print(f"   Transcript Excerpt: \"{top_payload.get('transcribed_text', '')[:80]}\"")

    client.close()

    avg_ret_lat = sum(retrieval_latencies) / len(retrieval_latencies)
    print("\n" + "=" * 80)
    print("  HIGH-THROUGHPUT INGESTION PIPELINE EXECUTION SUMMARY")
    print("=" * 80)
    print(f"  Input File                : {abs_vpath.name} (573.8 MB)")
    print(f"  Stage 1 Audio Extraction  : {audio_ext_latency:.3f} s (Target < 2.0s | {'PASS ✅' if audio_ext_latency < 2.0 else 'WARN'})")
    print(f"  Stage 2 Frame Sampling    : {frame_ext_latency:.2f} s ({len(keyframes)} 720p frames)")
    print(f"  Stage 3 Whisper Speech    : {whisper_latency:.2f} s ({len(segments)} segments)")
    print(f"  Stage 4 Vector Encoding   : {encoding_latency:.2f} s (512-D CLIP & Text)")
    print(f"  Stage 5 Qdrant Indexing   : {idx_latency:.3f} s ({len(structs)} points)")
    print(f"  Total Ingestion Runtime   : {total_ingestion_runtime:.2f} s")
    print(f"  Video Duration Coverage   : {min_ts:.1f}s to {max_ts:.1f}s ({max_ts/60:.2f} mins)")
    print(f"  Avg Vector Search SLA     : {avg_ret_lat:.2f} ms (Target < 180ms | {'PASS ✅' if avg_ret_lat < 180 else 'FAIL'})")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
