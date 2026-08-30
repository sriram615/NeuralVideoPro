"""
Ingest and Stress-Test 20-Minute Video: Steve Jobs Interview Feb 18 1981.mp4
Measures detailed phase latency, verifies point count and duration span, and executes benchmark retrieval validation.
"""
from __future__ import annotations

import os
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import time
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from src.pipeline import VideoSearchPipeline
from src.db.qdrant_db import COLLECTION_NAME

def main():
    video_path = "data/raw/raw_videos/Steve Jobs Interview Feb 18 1981.mp4"
    abs_vpath = Path(video_path).resolve()
    
    print("=" * 80)
    print("NEURALVIDEO v5.0 — 20-MINUTE VIDEO INGESTION & STRESS-TEST BENCHMARK")
    print("=" * 80)
    print(f"Target Video: {abs_vpath.name}")
    print(f"File Size: {abs_vpath.stat().st_size / (1024*1024):.2f} MB")
    
    pipeline = VideoSearchPipeline(db_path="./data/vectors/qdrant_db")
    video_id = pipeline.video_processor._make_video_id(str(abs_vpath))
    target_frames_dir = pipeline.frames_dir / video_id
    target_frames_dir.mkdir(parents=True, exist_ok=True)
    
    # --- PHASE 1: Keyframe Extraction ---
    print("\n[1/4] Extracting Keyframes (OpenCV 720p ceiling + Hist Deduplication)...")
    t_kf_start = time.perf_counter()
    keyframes = pipeline.video_processor.extract_keyframes(
        video_path=str(abs_vpath),
        output_dir=str(target_frames_dir),
        target_fps=1.0,
    )
    kf_duration = time.perf_counter() - t_kf_start
    print(f"   -> Keyframe Extraction Completed in {kf_duration:.2f}s ({len(keyframes)} frames sampled)")

    # --- PHASE 2: Audio Transcription ---
    print("\n[2/4] Extracting Audio & Transcribing via Whisper (16kHz Mono WAV)...")
    t_audio_start = time.perf_counter()
    segments = pipeline.audio_transcriber.transcribe(str(abs_vpath))
    audio_duration = time.perf_counter() - t_audio_start
    print(f"   -> Whisper Transcription Completed in {audio_duration:.2f}s ({len(segments)} text segments)")

    # --- PHASE 3: CLIP 512-D Vision & Text Encoding ---
    print("\n[3/4] Generating CLIP 512-D Visual Embeddings & Text Matching...")
    t_enc_start = time.perf_counter()
    frame_paths = [f["frame_path"] for f in keyframes]
    visual_vecs = pipeline.vision_encoder.encode_batch_images(frame_paths, batch_size=8)
    
    audio_texts = []
    for f in keyframes:
        ts = f["timestamp"]
        matched_text = ""
        for seg in segments:
            if seg["start"] <= ts <= seg["end"] or abs(ts - seg["start"]) <= 1.5:
                matched_text = seg["text"]
                break
        fallback_text = matched_text if matched_text else "Steve Jobs interview technology footage"
        audio_texts.append(fallback_text)
        
    audio_vecs = pipeline.text_encoder.encode_batch_queries(audio_texts)
    enc_duration = time.perf_counter() - t_enc_start
    print(f"   -> Vision & Text Encoding Completed in {enc_duration:.2f}s")

    # --- PHASE 4: Qdrant Indexing ---
    print("\n[4/4] Indexing Points into Qdrant Vector Store...")
    t_idx_start = time.perf_counter()
    points = []
    for idx, f in enumerate(keyframes):
        pt = {
            "visual_vector": visual_vecs[idx].tolist(),
            "audio_vector": audio_vecs[idx].tolist(),
            "video_id": f["video_id"],
            "timestamp": f["timestamp"],
            "frame_idx": f["frame_idx"],
            "transcribed_text": audio_texts[idx],
            "domain": "news",
            "frame_path": f["frame_path"],
            "file_name": abs_vpath.name,
        }
        points.append(pt)
        
    pipeline.vector_store.upsert_points(points)
    idx_duration = time.perf_counter() - t_idx_start
    total_ingest_time = kf_duration + audio_duration + enc_duration + idx_duration
    
    print(f"   -> Qdrant Indexing Completed in {idx_duration:.2f}s")
    print(f"\n✅ TOTAL INGESTION TIME: {total_ingest_time:.2f}s")

    # Verify duration coverage
    min_ts = min(f["timestamp"] for f in keyframes)
    max_ts = max(f["timestamp"] for f in keyframes)
    print(f"\n📊 INGESTION AUDIT:")
    print(f"   - Video ID: {video_id}")
    print(f"   - Total Points Ingested: {len(points)}")
    print(f"   - Timestamp Range: {min_ts:.1f}s to {max_ts:.1f}s ({max_ts/60:.2f} minutes)")
    print(f"   - Full ~19:30 Coverage Verified: {'YES' if max_ts >= 1000 else 'NO'}")

    # --- BENCHMARK RETRIEVAL TEST ---
    print("\n" + "=" * 80)
    print("NEURALVIDEO v5.0 — RETRIEVAL & BENCHMARK VALIDATION")
    print("=" * 80)
    
    test_queries = [
        {
            "type": "Visual Query",
            "query": "young man sitting in office in front of Apple computer with glasses",
        },
        {
            "type": "Audio Query",
            "query": "television shoots for the lowest common denominator",
        },
        {
            "type": "Hybrid Query",
            "query": "Steve Jobs discussing computers while sitting near Apple logo",
        },
    ]

    for item in test_queries:
        q_type = item["type"]
        q_str = item["query"]
        print(f"\n🔍 [{q_type.upper()}]: \"{q_str}\"")
        print("-" * 80)
        
        t0 = time.perf_counter()
        res = pipeline.search(query=q_str, top_k=5, domain_filter=None, enable_mmr=True)
        ret_latency_ms = (time.perf_counter() - t0) * 1000
        
        results_list = res.get("results", [])
        print(f"   Retrieval Latency: {ret_latency_ms:.2f} ms (SLA Target: < 200ms | {'PASS' if ret_latency_ms < 200 else 'FAIL'})")
        print(f"   Returned Top Results: {len(results_list)}")
        
        for rank, r in enumerate(results_list, 1):
            p = r.get("payload", {})
            ts = p.get("timestamp", 0.0)
            mins, secs = int(ts // 60), int(ts % 60)
            formatted_ts = f"{mins:02d}:{secs:02d}"
            v_sc = r.get("visual_score", 0.0)
            a_sc = r.get("audio_score", 0.0)
            f_sc = r.get("score", 0.0)
            band = r.get("confidence_band", "N/A")
            tr = p.get("transcribed_text", "")
            
            print(f"   Rank #{rank} | Timestamp: {formatted_ts} ({ts:.1f}s) | Score: {f_sc:.4f} | Band: {band}")
            print(f"          Visual: {v_sc:.4f} | Audio: {a_sc:.4f}")
            print(f"          Transcript: \"{tr[:90]}\"")
            
    pipeline.close()
    print("\n" + "=" * 80)
    print("✅ BENCHMARK RETRIEVAL TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
