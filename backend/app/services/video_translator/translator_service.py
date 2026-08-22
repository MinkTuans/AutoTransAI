"""
Video Translation Pipeline Service.

Manages audio extraction, Speech-to-Text (STT), Language Detection,
LLM Translation, TTS generation, Audio Synchronization (time-stretching),
and final FFmpeg audio mix / video rendering with real-time progress & logging.
"""

from __future__ import annotations

import asyncio
import base64
import json
import re
import shutil
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List, Tuple

from app.config import get_settings
from app.core import get_logger
from app.core.job_logger import log_job_event
from app.media.ffprobe import probe_duration_async, get_video_metadata_async
from app.media.ffmpeg_process import run_ffmpeg_with_progress_async, FFmpegExecutionError
from app.providers.registry import get_registry
from app.models.video_translator import (
    VideoAsset,
    VideoTranslationJob,
    VideoTranslationSegment,
    TranslationJobStatus,
    AudioMixMode,
)

logger = get_logger(__name__)
settings = get_settings()

# Stage weights for overall progress calculation
STAGE_WEIGHTS = {
    "DOWNLOADING": 10.0,
    "EXTRACTING_AUDIO": 10.0,
    "STT": 20.0,
    "TRANSLATING": 20.0,
    "GENERATING_TTS": 20.0,
    "SYNCING_AUDIO": 5.0,
    "RENDERING": 15.0,
}

STAGE_BASE_OFFSET = {
    "QUEUED": 0.0,
    "DOWNLOADING": 0.0,
    "EXTRACTING_AUDIO": 10.0,
    "STT": 20.0,
    "TRANSLATING": 40.0,
    "SEGMENT_EDITING": 60.0,
    "GENERATING_TTS": 60.0,
    "SYNCING_AUDIO": 80.0,
    "RENDERING": 85.0,
    "COMPLETED": 100.0,
}


def calculate_overall_progress(stage: str, stage_progress_pct: float) -> float:
    """Calculate total overall progress percentage based on stage base offset and stage progress."""
    base = STAGE_BASE_OFFSET.get(stage, 0.0)
    weight = STAGE_WEIGHTS.get(stage, 0.0)
    if stage == "SEGMENT_EDITING":
        return 60.0
    if stage == "COMPLETED":
        return 100.0
    overall = base + (weight * (stage_progress_pct / 100.0))
    return round(min(99.9, max(0.0, overall)), 1)


async def extract_audio_from_video(
    video_path: Path,
    output_audio_path: Path,
    job_id: str = "VT-JOB",
    on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_pid: Optional[Callable[[int], None]] = None,
) -> float:
    """
    Extract audio track from video file into 16kHz MONO WAV using real-time FFmpeg process.
    """
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    log_job_event(job_id, "EXTRACTING_AUDIO", f"Probing metadata for {video_path.name}")
    meta = await get_video_metadata_async(video_path)
    if not meta.get("has_audio"):
        log_job_event(job_id, "EXTRACTING_AUDIO", "ERROR: Video has no audio stream.")
        raise ValueError("Video không chứa track audio. Không thể thực hiện dịch giọng nói.")

    total_duration = meta.get("duration", 0.0)
    output_audio_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_audio_path),
    ]

    log_job_event(job_id, "EXTRACTING_AUDIO", f"Starting FFmpeg audio extraction (Duration: {total_duration:.1f}s)")
    calc_timeout = max(600.0, float(total_duration) * 3.0)
    stats = await run_ffmpeg_with_progress_async(
        cmd,
        total_duration=total_duration,
        on_progress=on_progress,
        on_pid=on_pid,
        timeout=calc_timeout,
    )

    if not output_audio_path.exists() or output_audio_path.stat().st_size == 0:
        raise RuntimeError("Không thể trích xuất audio từ video.")

    actual_dur = await probe_duration_async(output_audio_path)
    log_job_event(job_id, "EXTRACTING_AUDIO", f"Audio extraction completed successfully. Duration: {actual_dur:.1f}s")
    return actual_dur


def validate_no_placeholders(segments: List[Dict[str, Any]]) -> None:
    """Ensure no segment text contains mock/placeholder text."""
    placeholder_patterns = [
        r"Phần phát biểu",
        r"Video speech",
        r"Speech segment",
        r"Placeholder",
        r"Mock transcript",
        r"Dummy transcript",
    ]
    pattern = re.compile("|".join(placeholder_patterns), re.IGNORECASE)
    for seg in segments:
        txt = seg.get("text", "")
        if pattern.search(txt):
            raise ValueError(f"STT Error: Transcript contains placeholder text: '{txt}'")


def validate_and_clean_timeline_segments(
    raw_segments: List[Dict[str, Any]],
    total_duration: float,
    job_id: str = "VT-JOB",
) -> List[Dict[str, Any]]:
    """
    Validate, deduplicate, sort, and enforce timeline invariants on STT segments.
    Guarantees no segment end_time exceeds total_duration.
    Logs automated TIMELINE AUDIT REPORT.
    """
    if not raw_segments:
        raise ValueError("STT Error: Không có phân đoạn hội thoại nào được nhận diện.")

    # Sort segments strictly by start_time ASC
    sorted_segs = sorted(raw_segments, key=lambda s: float(s.get("start_time", 0.0)))
    cleaned_segments: List[Dict[str, Any]] = []

    for seg in sorted_segs:
        st = float(seg.get("start_time", 0.0))
        et = float(seg.get("end_time", st + 1.0))
        txt = str(seg.get("text", "")).strip()

        if not txt:
            continue

        # Invariant 1: start_time >= 0
        if st < 0.0:
            st = 0.0

        # Invariant 2: start_time < end_time
        if et <= st:
            et = round(st + 1.0, 2)

        # Invariant 3: end_time <= total_duration
        if et > total_duration:
            diff = et - total_duration
            log_job_event(
                job_id,
                "STT_WARNING",
                f"⚠️ TIMELINE OUT OF BOUNDS: Segment #{seg.get('number')} ('{txt[:30]}...') "
                f"end_time ({et:.2f}s) exceeded video duration ({total_duration:.2f}s) by {diff:.2f}s. "
                f"Correcting end_time to total_duration."
            )
            et = round(total_duration, 2)
            if st >= et:
                st = max(0.0, round(et - 1.0, 2))

        # Deduplicate overlap segments (e.g., from chunk boundary overlap)
        if cleaned_segments:
            prev = cleaned_segments[-1]
            prev_st = prev["start_time"]
            prev_et = prev["end_time"]
            prev_txt = prev["text"]

            # If segment has identical text and starts close to previous segment
            if txt == prev_txt and abs(st - prev_st) < 5.0:
                logger.info(f"[{job_id}] Skipping duplicate segment from chunk overlap: '{txt[:30]}'")
                continue

            # If segment is completely contained within previous segment
            if st >= prev_st and et <= prev_et and (txt in prev_txt or prev_txt in txt):
                logger.info(f"[{job_id}] Skipping contained sub-segment: '{txt[:30]}'")
                continue

        cleaned_segments.append({
            "number": len(cleaned_segments) + 1,
            "start_time": round(st, 2),
            "end_time": round(et, 2),
            "text": txt,
        })

    if not cleaned_segments:
        raise ValueError("STT Error: Không còn segment hợp lệ sau khi validate timeline.")

    # Final timeline invariants verification
    first_seg = cleaned_segments[0]
    last_seg = cleaned_segments[-1]
    max_segment_end = max(s["end_time"] for s in cleaned_segments)

    if max_segment_end > total_duration + 0.05:
        raise ValueError(
            f"TIMELINE_INVALID: Max segment end ({max_segment_end:.2f}s) exceeds total video duration ({total_duration:.2f}s)."
        )

    # Gap Audit (Detect silent gaps >= 15 seconds)
    gaps = []
    prev_end = 0.0
    for s in cleaned_segments:
        gap_dur = s["start_time"] - prev_end
        if gap_dur >= 15.0:
            gaps.append((round(prev_end, 2), round(s["start_time"], 2), round(gap_dur, 2)))
        prev_end = max(prev_end, s["end_time"])

    audit_report = [
        "========================================",
        "TIMELINE AUDIT REPORT",
        "========================================",
        f"JOB ID: {job_id}",
        f"VIDEO DURATION: {total_duration:.2f}s ({int(total_duration//60)}m {total_duration%60:.1f}s)",
        f"TOTAL SEGMENTS: {len(cleaned_segments)}",
        f"FIRST SEGMENT: #{first_seg['number']} ({first_seg['start_time']:.2f}s -> {first_seg['end_time']:.2f}s)",
        f"LAST SEGMENT: #{last_seg['number']} ({last_seg['start_time']:.2f}s -> {last_seg['end_time']:.2f}s)",
        f"MAX SEGMENT END: {max_segment_end:.2f}s",
        f"TIMELINE VALID: YES",
        f"DETECTED SILENT GAPS (>=15s): {len(gaps)}",
    ]
    for g_start, g_end, g_dur in gaps:
        audit_report.append(f"  - GAP: {g_start:.2f}s -> {g_end:.2f}s (Duration: {g_dur:.2f}s)")
    audit_report.append("========================================")

    log_job_event(job_id, "STT", "\n".join(audit_report))
    return cleaned_segments


async def transcribe_audio_with_whisper(
    audio_path: Path,
    job_id: str = "VT-JOB",
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Transcribe audio file using OpenAI Whisper API (whisper-1).
    Handles large audio files by chunking via FFmpeg with exact chunk duration bounds and overlap.
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY chưa được cấu hình trong .env")

    import httpx
    total_duration = await probe_duration_async(audio_path)
    file_size_mb = audio_path.stat().st_size / (1024 * 1024)

    max_chunk_sec = 120.0
    overlap_sec = 5.0
    chunks: List[Tuple[Path, float, float]] = []  # (chunk_path, time_offset, actual_chunk_duration)
    temp_dir: Optional[Path] = None

    try:
        if file_size_mb > 15.0 or total_duration > max_chunk_sec:
            log_job_event(job_id, "STT", f"[Whisper] Large audio file ({file_size_mb:.1f}MB, {total_duration:.1f}s). Slicing audio into {max_chunk_sec}s chunks (Overlap: {overlap_sec}s)...")
            temp_dir = audio_path.parent / f"whisper_chunks_{job_id}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            chunk_idx = 0
            curr_start = 0.0
            while curr_start < total_duration:
                chunk_len = min(max_chunk_sec, total_duration - curr_start)
                if chunk_len <= 0:
                    break

                chunk_path = temp_dir / f"chunk_{chunk_idx:03d}.wav"
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(audio_path),
                    "-ss", f"{curr_start:.2f}",
                    "-t", f"{chunk_len:.2f}",
                    "-acodec", "pcm_s16le",
                    "-ar", "16000",
                    "-ac", "1",
                    str(chunk_path)
                ]
                await run_ffmpeg_with_progress_async(cmd, timeout=120.0)
                if not chunk_path.exists() or chunk_path.stat().st_size == 0:
                    raise RuntimeError(f"Whisper STT: Audio chunk file lost or failed to generate: {chunk_path.name}")

                actual_dur = await probe_duration_async(chunk_path)
                chunks.append((chunk_path, curr_start, actual_dur))

                if curr_start + chunk_len >= total_duration:
                    break
                curr_start += (chunk_len - overlap_sec)
                chunk_idx += 1
        else:
            chunks.append((audio_path, 0.0, total_duration))

        all_segments = []
        detected_lang = "English"
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}

        async with httpx.AsyncClient(timeout=180.0) as client:
            for chunk_path, time_offset, actual_chunk_dur in chunks:
                if not chunk_path.exists() or chunk_path.stat().st_size == 0:
                    raise RuntimeError(f"Whisper STT: Audio chunk file missing before API call: {chunk_path.name}")

                log_job_event(job_id, "STT", f"[Whisper] Transcribing chunk {chunk_path.name} (Offset: {time_offset:.1f}s, Dur: {actual_chunk_dur:.1f}s)...")
                with open(chunk_path, "rb") as f:
                    files = {"file": (chunk_path.name, f, "audio/wav")}
                    data = {"model": "whisper-1", "response_format": "verbose_json"}
                    res = await client.post(url, headers=headers, files=files, data=data)

                if res.status_code != 200:
                    raise RuntimeError(f"OpenAI Whisper API HTTP {res.status_code}: {res.text[:200]}")

                res_json = res.json()
                detected_lang = res_json.get("language", detected_lang)
                whisper_segs = res_json.get("segments", [])

                if not whisper_segs and res_json.get("text"):
                    whisper_segs = [{
                        "start": 0.0,
                        "end": actual_chunk_dur,
                        "text": res_json["text"]
                    }]

                for w_seg in whisper_segs:
                    local_st = float(w_seg.get("start", 0.0))
                    local_et = float(w_seg.get("end", local_st + 4.0))
                    txt = str(w_seg.get("text", "")).strip()

                    if not txt:
                        continue

                    if local_st >= time_offset and time_offset > 0:
                        local_st -= time_offset
                        local_et -= time_offset

                    if local_st < 0.0:
                        local_st = 0.0
                    if local_et > actual_chunk_dur + 0.5:
                        local_et = min(local_et, actual_chunk_dur)

                    if local_st >= actual_chunk_dur:
                        continue

                    st = round(time_offset + local_st, 2)
                    et = round(time_offset + max(local_st + 0.5, local_et), 2)

                    all_segments.append({
                        "number": len(all_segments) + 1,
                        "start_time": st,
                        "end_time": et,
                        "text": txt,
                    })

        if not all_segments:
            raise RuntimeError("OpenAI Whisper API không nhận diện được giọng nói trong audio.")

        validate_no_placeholders(all_segments)
        validated_segments = validate_and_clean_timeline_segments(all_segments, total_duration, job_id=job_id)
        log_job_event(job_id, "STT", f"Whisper STT completed successfully. Detected: {detected_lang}, Validated Segments: {len(validated_segments)}")
        return validated_segments, detected_lang
    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


async def transcribe_audio_with_gemini(
    audio_path: Path,
    job_id: str = "VT-JOB",
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Transcribe audio file using Google Gemini API.
    Handles large audio files (>5MB or >90s) by chunking via FFmpeg with exact chunk duration bounds and overlap.
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY chưa được cấu hình trong .env")

    import httpx
    total_duration = await probe_duration_async(audio_path)
    file_size_mb = audio_path.stat().st_size / (1024 * 1024)

    max_chunk_sec = 90.0
    overlap_sec = 5.0
    chunks: List[Tuple[Path, float, float]] = []  # (chunk_path, time_offset, actual_chunk_duration)
    temp_dir: Optional[Path] = None

    try:
        if file_size_mb > 5.0 or total_duration > max_chunk_sec:
            log_job_event(job_id, "STT", f"[Gemini] Large audio file ({file_size_mb:.1f}MB, {total_duration:.1f}s). Slicing audio into {max_chunk_sec}s chunks (Overlap: {overlap_sec}s)...")
            temp_dir = audio_path.parent / f"gemini_chunks_{job_id}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            chunk_idx = 0
            curr_start = 0.0
            while curr_start < total_duration:
                chunk_len = min(max_chunk_sec, total_duration - curr_start)
                if chunk_len <= 0:
                    break

                chunk_path = temp_dir / f"g_chunk_{chunk_idx:03d}.wav"
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(audio_path),
                    "-ss", f"{curr_start:.2f}",
                    "-t", f"{chunk_len:.2f}",
                    "-acodec", "pcm_s16le",
                    "-ar", "16000",
                    "-ac", "1",
                    str(chunk_path)
                ]
                await run_ffmpeg_with_progress_async(cmd, timeout=120.0)
                if not chunk_path.exists() or chunk_path.stat().st_size == 0:
                    raise RuntimeError(f"Gemini STT: Audio chunk file lost or failed to generate: {chunk_path.name}")

                actual_dur = await probe_duration_async(chunk_path)
                chunks.append((chunk_path, curr_start, actual_dur))

                if curr_start + chunk_len >= total_duration:
                    break
                curr_start += (chunk_len - overlap_sec)
                chunk_idx += 1
        else:
            chunks.append((audio_path, 0.0, total_duration))

        from app.providers.llm.gemini_provider import GEMINI_MODEL_CANDIDATES
        all_segments = []
        detected_lang = "English"

        async with httpx.AsyncClient(timeout=120.0) as client:
            for chunk_path, time_offset, actual_chunk_dur in chunks:
                if not chunk_path.exists() or chunk_path.stat().st_size == 0:
                    raise RuntimeError(f"Gemini STT: Audio chunk file missing before API call: {chunk_path.name}")

                log_job_event(job_id, "STT", f"[Gemini] Transcribing chunk {chunk_path.name} (Offset: {time_offset:.1f}s, Dur: {actual_chunk_dur:.1f}s)...")
                with open(chunk_path, "rb") as f:
                    audio_bytes = f.read()

                prompt = (
                    f"Phân tích file audio này (độ dài thực tế file audio: {actual_chunk_dur:.2f} giây) và thực hiện 2 việc:\n"
                    "1. Nhận diện ngôn ngữ được nói trong audio (ví dụ: English, Vietnamese, Japanese, Chinese, French, German).\n"
                    "2. Trích xuất toàn bộ bản chép lời (transcript) theo từng câu có mốc thời gian start_time và end_time tính bằng giây.\n"
                    "LƯU Ý BẮT BUỘC VỀ TIMESTAMP:\n"
                    f"- mốc thời gian (start_time, end_time) BẮT BUỘC là thời gian RELATIVE tính từ 0.0 giây đến tối đa {actual_chunk_dur:.2f} giây trong file audio chunk này.\n"
                    f"- KHÔNG ĐƯỢC tạo timestamp vượt quá {actual_chunk_dur:.2f} giây.\n"
                    "- KHÔNG ĐƯỢC dùng mốc thời gian tuyệt đối của toàn bộ video.\n"
                    "Trả về định dạng JSON thuần túy (không markdown) với cấu trúc:\n"
                    "{\n"
                    '  "language": "English",\n'
                    '  "segments": [\n'
                    '    {"start_time": 0.0, "end_time": 4.5, "text": "Sentence text"}\n'
                    '  ]\n'
                    "}"
                )

                base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt},
                                {
                                    "inline_data": {
                                        "mime_type": "audio/wav",
                                        "data": base64_audio,
                                    }
                                },
                            ]
                        }
                    ]
                }

                chunk_success = False
                last_err = ""

                for model in GEMINI_MODEL_CANDIDATES:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
                    try:
                        res = await client.post(url, json=payload)
                        if res.status_code == 200:
                            data = res.json()
                            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                            if parts:
                                raw_response = parts[0].get("text", "").strip()
                                json_str = re.sub(r"^```json\s*", "", raw_response, flags=re.MULTILINE)
                                json_str = re.sub(r"```$", "", json_str, flags=re.MULTILINE).strip()
                                parsed_json = json.loads(json_str)

                                detected_lang = parsed_json.get("language", detected_lang)
                                raw_segments = parsed_json.get("segments", [])

                                if raw_segments:
                                    for s in raw_segments:
                                        local_st = float(s.get("start_time", 0.0))
                                        local_et = float(s.get("end_time", local_st + 4.0))
                                        txt = str(s.get("text", "")).strip()

                                        if not txt:
                                            continue

                                        # Handle case where model returns absolute video timestamps
                                        if local_st >= time_offset and time_offset > 0:
                                            logger.info(f"[{job_id}] Model returned absolute timestamp {local_st:.2f}s for chunk starting at {time_offset:.2f}s. Adjusting relative timestamp.")
                                            local_st -= time_offset
                                            local_et -= time_offset

                                        # Enforce chunk bounds
                                        if local_st < 0.0:
                                            local_st = 0.0
                                        if local_et > actual_chunk_dur + 0.5:
                                            logger.warning(f"[{job_id}] Segment end {local_et:.2f}s exceeded chunk duration {actual_chunk_dur:.2f}s for {chunk_path.name}. Capping to chunk duration.")
                                            local_et = min(local_et, actual_chunk_dur)

                                        if local_st >= actual_chunk_dur:
                                            continue

                                        st = round(time_offset + local_st, 2)
                                        et = round(time_offset + max(local_st + 0.5, local_et), 2)

                                        all_segments.append({
                                            "number": len(all_segments) + 1,
                                            "start_time": st,
                                            "end_time": et,
                                            "text": txt,
                                        })
                                    chunk_success = True
                                    break
                        else:
                            last_err = f"HTTP {res.status_code}: {res.text[:150]}"
                    except Exception as ex:
                        last_err = str(ex)
                        continue

                if not chunk_success:
                    raise RuntimeError(f"Gemini STT failed for chunk {chunk_path.name}: {last_err}")

        if not all_segments:
            raise RuntimeError("Gemini STT không nhận diện được giọng nói trong audio.")

        validate_no_placeholders(all_segments)
        validated_segments = validate_and_clean_timeline_segments(all_segments, total_duration, job_id=job_id)
        log_job_event(job_id, "STT", f"Gemini STT completed successfully. Detected: {detected_lang}, Validated Segments: {len(validated_segments)}")
        return validated_segments, detected_lang
    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


async def speech_to_text_and_detect_language(
    audio_path: Path,
    job_id: str = "VT-JOB",
    target_language: str = "vi",
    source_language: str = "auto",
    llm_provider_id: str = "openai",
    on_status_update: Optional[Callable[[str], None]] = None,
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Perform Speech-to-Text and Language Detection on extracted audio track.
    Strictly uses real STT (OpenAI Whisper or Gemini AI Studio).
    Raises RuntimeError on failure — NO placeholder fallbacks permitted.
    """
    total_duration = await probe_duration_async(audio_path)
    if total_duration <= 0:
        raise ValueError("File audio không hợp lệ hoặc không thể đọc.")

    log_job_event(job_id, "STT", f"Starting Speech-to-Text (Audio duration: {total_duration:.1f}s, Primary Provider: {llm_provider_id})")
    if on_status_update:
        on_status_update(f"Đang phân tích audio ({audio_path.stat().st_size / (1024*1024):.1f}MB) với STT...")

    stt_errors = []

    # Priority 1: OpenAI Whisper if OPENAI_API_KEY set and preferred or default
    if settings.OPENAI_API_KEY and (llm_provider_id == "openai" or not settings.GEMINI_API_KEY):
        try:
            return await transcribe_audio_with_whisper(audio_path, job_id=job_id)
        except Exception as e:
            err_msg = f"Whisper STT failed: {str(e)}"
            logger.warning(err_msg)
            stt_errors.append(err_msg)

    # Priority 2: Gemini STT if GEMINI_API_KEY set
    if settings.GEMINI_API_KEY:
        try:
            return await transcribe_audio_with_gemini(audio_path, job_id=job_id)
        except Exception as e:
            err_msg = f"Gemini STT failed: {str(e)}"
            logger.warning(err_msg)
            stt_errors.append(err_msg)

    # Secondary try OpenAI Whisper if not tried yet
    if settings.OPENAI_API_KEY and llm_provider_id != "openai":
        try:
            return await transcribe_audio_with_whisper(audio_path, job_id=job_id)
        except Exception as e:
            err_msg = f"Whisper STT fallback failed: {str(e)}"
            logger.warning(err_msg)
            stt_errors.append(err_msg)

    # If all STT attempts fail
    error_summary = " | ".join(stt_errors) if stt_errors else "Chưa cấu hình OPENAI_API_KEY hoặc GEMINI_API_KEY trong .env."
    raise RuntimeError(f"STT FAILED: {error_summary}")


def _safe_parse_json_list(text: str) -> list:
    """Parse JSON array robustly, handling markdown blocks, control characters, strict=False, and regex string extraction fallback."""
    json_str = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
    json_str = re.sub(r"```$", "", json_str, flags=re.MULTILINE).strip()
    match = re.search(r"\[.*\]", json_str, re.DOTALL)
    if match:
        json_str = match.group(0)

    try:
        res = json.loads(json_str, strict=False)
        if isinstance(res, list):
            return res
    except Exception:
        pass

    try:
        # Sanitize control characters / unescaped newlines inside strings
        cleaned_str = re.sub(r'[\r\n\t]+', ' ', json_str)
        res = json.loads(cleaned_str, strict=False)
        if isinstance(res, list):
            return res
    except Exception:
        pass

    # Regex fallback: Extract individual JSON string values if structural parsing fails
    items = re.findall(r'"((?:[^"\\]|\\.)*)"', json_str)
    if items:
        return [item.replace('\\"', '"').replace('\\n', '\n').strip() for item in items]

    raise ValueError(f"Could not parse valid JSON list from response: {text[:200]}")


async def translate_transcript_segments(
    segments: List[Dict[str, Any]],
    source_language: str,
    target_language: str,
    job_id: str = "VT-JOB",
    llm_provider_id: str = "openai",
    batch_size: int = 30,
) -> List[Dict[str, Any]]:
    """
    Translate transcript text segments to target language using LLM Provider (OpenAI / Gemini).
    Implements per-batch retries, multi-provider failover chain, anti-verbatim validation safeguards,
    and structured [TRANSLATION_PROVIDER] audit logging.
    Raises RuntimeError on failure — NO dummy/placeholder fallbacks permitted.
    """
    if not segments:
        return segments

    registry = get_registry()
    
    # Build LLM provider candidates chain (Configured Primary -> Fallbacks)
    primary_llm = registry.get_llm(llm_provider_id)
    fallback_ids = ["gemini", "openai"] if llm_provider_id == "openai" else ["openai", "gemini"]
    
    candidate_llms = []
    if primary_llm:
        candidate_llms.append(primary_llm)
    for fid in fallback_ids:
        fb_llm = registry.get_llm(fid)
        if fb_llm and fb_llm not in candidate_llms:
            candidate_llms.append(fb_llm)

    if not candidate_llms:
        raise RuntimeError("Không tìm thấy LLM Provider nào khả thi trong hệ thống.")

    lang_names = {
        "vi": "Tiếng Việt",
        "vietnamese": "Tiếng Việt",
        "en": "English",
        "english": "English",
        "ja": "Tiếng Nhật",
        "japanese": "Tiếng Nhật",
        "ko": "Tiếng Hàn",
        "korean": "Tiếng Hàn",
        "zh": "Tiếng Trung",
        "chinese": "Tiếng Trung",
        "fr": "Tiếng Pháp",
        "french": "Tiếng Pháp",
        "de": "Tiếng Đức",
        "german": "Tiếng Đức",
        "es": "Tiếng Tây Ban Nha",
        "spanish": "Tiếng Tây Ban Nha",
        "auto": "Tự động",
    }
    source_lang_name = lang_names.get(str(source_language).lower(), source_language or "Tự động")
    target_lang_name = lang_names.get(str(target_language).lower(), target_language or "Tiếng Việt")

    provider_errors: List[str] = []

    for llm_idx, llm in enumerate(candidate_llms):
        is_primary = (llm_idx == 0)
        log_job_event(
            job_id,
            "TRANSLATING",
            f"[TRANSLATION_PROVIDER] job_id={job_id} | configured_provider={llm_provider_id} | "
            f"resolved_provider={llm.provider_id} | actual_provider={llm.provider_name} | "
            f"is_primary={is_primary} | source_language={source_lang_name} | "
            f"target_language={target_lang_name} | segments_count={len(segments)}"
        )

        try:
            translated_results: List[str] = []
            total_batches = (len(segments) + batch_size - 1) // batch_size

            for batch_idx in range(total_batches):
                start_i = batch_idx * batch_size
                end_i = min(len(segments), start_i + batch_size)
                batch_segments = segments[start_i:end_i]
                texts_to_translate = [s["text"] for s in batch_segments]

                prompt = (
                    "Bạn là một dịch giả phim chuyên nghiệp.\n"
                    f"Nhiệm vụ: Dịch chính xác danh sách câu thoại bên dưới từ {source_lang_name} sang {target_lang_name}.\n"
                    "Yêu cầu bắt buộc:\n"
                    f"1. Phải dịch TOÀN BỘ nội dung sang {target_lang_name} tự nhiên, hợp ngữ cảnh lồng tiếng video.\n"
                    f"2. Tuyệt đối KHÔNG ĐƯỢC trả lại nguyên văn {source_lang_name} hay giữ lại văn bản chưa dịch (trừ tên riêng nếu có).\n"
                    "3. Trả về duy nhất một mảng JSON thuần túy (không markdown, không giải thích) chứa các chuỗi dịch tương ứng theo đúng thứ tự.\n\n"
                    f"Danh sách câu thoại gốc ({source_lang_name}):\n"
                    f"{json.dumps(texts_to_translate, ensure_ascii=False)}"
                )

                # Retry up to 2 attempts per batch on the SAME LLM provider before failing the provider
                translated_list = None
                batch_error = None
                for attempt in range(2):
                    try:
                        response_text = await llm.generate_text(prompt if attempt == 0 else prompt + "\nLƯU Ý: Đảm bảo định dạng JSON mảng hợp lệ [\"...\"]")
                        translated_list = _safe_parse_json_list(response_text)
                        if isinstance(translated_list, list) and len(translated_list) == len(batch_segments):
                            break
                        else:
                            batch_error = f"Output length mismatch: expected {len(batch_segments)}, got {len(translated_list) if isinstance(translated_list, list) else type(translated_list)}"
                    except Exception as ex:
                        batch_error = str(ex)
                        logger.warning(f"Batch {batch_idx+1}/{total_batches} attempt {attempt+1} failed on {llm.provider_id}: {batch_error}")

                if not isinstance(translated_list, list) or len(translated_list) != len(batch_segments):
                    raise ValueError(f"LLM translation failed for batch {batch_idx+1}/{total_batches} on {llm.provider_name}: {batch_error}")

                # Check for verbatim echo (where translation is identical to original for non-same languages)
                verbatim_echo_count = 0
                for orig, trans in zip(texts_to_translate, translated_list):
                    trans_str = str(trans).strip()
                    if orig.strip() and trans_str == orig.strip() and source_language.lower() != target_language.lower():
                        verbatim_echo_count += 1

                # If more than 30% of batch was echoed unchanged, retry batch with stronger prompt
                if verbatim_echo_count > max(1, int(len(batch_segments) * 0.3)):
                    logger.warning(f"Batch {batch_idx+1}/{total_batches} on {llm.provider_id} had {verbatim_echo_count} verbatim echoes. Retrying batch with strict prompt...")
                    strict_prompt = (
                        f"CẢNH BÁO: Bạn đã trả về nguyên văn {source_lang_name}. HÃY DỊCH BẮT BUỘC SANG {target_lang_name}.\n"
                        f"Bắt buộc dịch toàn bộ các câu thoại này sang {target_lang_name} cho lồng tiếng phim:\n"
                        f"{json.dumps(texts_to_translate, ensure_ascii=False)}\n\n"
                        "Chỉ trả về mảng JSON chứa các câu đã dịch sang tiếng Việt."
                    )
                    try:
                        retry_resp = await llm.generate_text(strict_prompt)
                        retry_list = _safe_parse_json_list(retry_resp)
                        if isinstance(retry_list, list) and len(retry_list) == len(batch_segments):
                            translated_list = retry_list
                    except Exception as retry_ex:
                        logger.warning(f"Batch {batch_idx+1} anti-echo retry failed: {retry_ex}")

                translated_results.extend([str(t).strip() for t in translated_list])
                log_job_event(job_id, "TRANSLATING", f"Translated batch {batch_idx+1}/{total_batches} via {llm.provider_name} ({len(translated_list)} items)")

            if len(translated_results) == len(segments):
                # Translation Safeguard Validation: Ensure output is non-empty and not dummy text
                untranslated_count = 0
                for orig_s, trans_t in zip(segments, translated_results):
                    orig_txt = orig_s.get("text", "").strip()
                    trans_txt = trans_t.strip()
                    if orig_txt and trans_txt == orig_txt and source_language.lower() != target_language.lower():
                        untranslated_count += 1

                if untranslated_count > max(1, int(len(segments) * 0.5)):
                    err_msg = f"Translation validation failed on {llm.provider_name}: {untranslated_count}/{len(segments)} segments were verbatim echoes."
                    logger.warning(err_msg)
                    provider_errors.append(f"[{llm.provider_name}] {err_msg}")
                    continue

                for seg, trans in zip(segments, translated_results):
                    seg["translated_text"] = trans

                log_job_event(job_id, "TRANSLATING", f"LLM translation ({llm.provider_name}) completed successfully for all {len(segments)} segments.")
                return segments

        except Exception as e:
            err_detail = f"[{llm.provider_name} ({llm.provider_id})] {str(e)}"
            logger.warning(err_detail)
            log_job_event(
                job_id,
                "TRANSLATING",
                f"LLM translation provider failed ({llm.provider_name}): {str(e)}. "
                f"{'Chuyển sang Provider dự phòng...' if llm_idx + 1 < len(candidate_llms) else 'Không còn Provider dự phòng nào.'}"
            )
            provider_errors.append(err_detail)

    # If all LLM providers in failover chain failed
    error_summary = " | ".join(provider_errors) if provider_errors else "Tất cả LLM Provider đều thất bại."
    raise RuntimeError(f"TRANSLATION FAILED: {error_summary}")


from app.services.video_translator.sync_service import VideoAudioSyncService

async def sync_and_stretch_audio(
    tts_audio_path: Path,
    target_duration: float,
    output_synced_path: Path,
    job_id: str = "VT-JOB",
    on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_pid: Optional[Callable[[int], None]] = None,
) -> float:
    """
    Adjust audio speed (time-stretch) using FFmpeg multi-stage atempo filter to match target duration.
    """
    res = await VideoAudioSyncService.stretch_and_normalize_audio(
        input_audio_path=tts_audio_path,
        target_duration=target_duration,
        output_audio_path=output_synced_path,
        job_id=job_id,
        on_progress=on_progress,
        on_pid=on_pid,
    )
    
    log_job_event(
        job_id,
        "SYNCING_AUDIO",
        f"[VIDEO-SYNC] Audio stretched/normalized: target={target_duration:.2f}s, "
        f"actual={res['actual_duration']:.2f}s, final={res['final_duration']:.2f}s, "
        f"tempo={res['tempo_applied']:.2f}x, action={res['action']}"
    )
    return res["final_duration"]


async def render_dubbed_video(
    video_path: Path,
    segments: List[VideoTranslationSegment],
    original_audio_mode: str,
    output_video_path: Path,
    work_dir: Path,
    job_id: str = "VT-JOB",
    on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_pid: Optional[Callable[[int], None]] = None,
) -> Path:
    """
    Render final dubbed video by building a sample-accurate timeline audio track and muxing with video.
    """
    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    log_job_event(job_id, "RENDERING", "[VIDEO-SYNC] Probing total video duration for timeline render...")
    total_video_duration = await probe_duration_async(video_path)

    valid_segments = [s for s in segments if s.synced_audio_path or s.tts_audio_path]
    if not valid_segments:
        raise ValueError("❌ Không có phân đoạn âm thanh lồng tiếng nào được tạo.")

    log_job_event(
        job_id,
        "RENDERING",
        f"[VIDEO-SYNC] Building PCM audio timeline for {len(valid_segments)} segments (Master duration: {total_video_duration:.2f}s)..."
    )

    segment_dicts = []
    for s in valid_segments:
        if s.end_time > total_video_duration + 0.05:
            raise ValueError(
                f"TIMELINE_INVALID: Segment #{s.segment_number} end_time ({s.end_time:.2f}s) "
                f"exceeds total video duration ({total_video_duration:.2f}s). Render aborted."
            )
        segment_dicts.append({
            "number": s.segment_number,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "audio_path": s.synced_audio_path or s.tts_audio_path,
        })

    combined_audio_path = work_dir / "combined_dubbed_audio.wav"

    # Step 1: Assemble timeline PCM audio track with exact zero-volume-loss and silence gaps
    timeline_res = VideoAudioSyncService.build_dubbed_audio_timeline(
        segments=segment_dicts,
        total_video_duration=total_video_duration,
        output_wav_path=combined_audio_path,
        job_id=job_id,
    )

    if timeline_res.get("overlap_warnings"):
        for warn in timeline_res["overlap_warnings"]:
            logger.warning(f"[VIDEO-SYNC] Job {job_id}: {warn}")

    # Step 2: Mux combined dubbed audio timeline with original video
    rendered_path = await VideoAudioSyncService.render_and_mux_video(
        video_path=video_path,
        dubbed_audio_path=combined_audio_path,
        original_audio_mode=original_audio_mode,
        output_video_path=output_video_path,
        total_video_duration=total_video_duration,
        job_id=job_id,
        on_progress=on_progress,
        on_pid=on_pid,
    )

    # Step 3: Validate final output duration and audio track
    val_res = await VideoAudioSyncService.validate_output(
        output_video_path=rendered_path,
        source_video_duration=total_video_duration,
    )

    log_job_event(
        job_id,
        "VALIDATION",
        f"[VIDEO-SYNC] Validation passed: Duration={val_res['output_duration']:.2f}s (Diff={val_res['duration_diff']}s), "
        f"Resolution={val_res['width']}x{val_res['height']}, HasAudio={val_res['has_audio']}"
    )

    return rendered_path
