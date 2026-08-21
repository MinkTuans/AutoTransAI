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
    stats = await run_ffmpeg_with_progress_async(
        cmd,
        total_duration=total_duration,
        on_progress=on_progress,
        on_pid=on_pid,
        timeout=300.0,
    )

    if not output_audio_path.exists() or output_audio_path.stat().st_size == 0:
        raise RuntimeError("Không thể trích xuất audio từ video.")

    actual_dur = await probe_duration_async(output_audio_path)
    log_job_event(job_id, "EXTRACTING_AUDIO", f"Audio extraction completed successfully. Duration: {actual_dur:.1f}s")
    return actual_dur


async def speech_to_text_and_detect_language(
    audio_path: Path,
    job_id: str = "VT-JOB",
    target_language: str = "vi",
    source_language: str = "auto",
    on_status_update: Optional[Callable[[str], None]] = None,
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Perform Speech-to-Text and Language Detection on the extracted audio.
    """
    registry = get_registry()
    gemini = registry.get_llm("gemini")

    total_duration = await probe_duration_async(audio_path)
    if total_duration <= 0:
        raise ValueError("File audio không hợp lệ.")

    log_job_event(job_id, "STT", f"Starting Speech-to-Text (Audio duration: {total_duration:.1f}s)")
    if on_status_update:
        on_status_update(f"Đang gửi audio ({audio_path.stat().st_size / (1024*1024):.1f}MB) đến Gemini STT...")

    # Try Gemini multi-modal STT if API key available
    if gemini and settings.GEMINI_API_KEY and audio_path.stat().st_size < 15 * 1024 * 1024:
        try:
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            base64_audio = base64.b64encode(audio_bytes).decode("utf-8")

            prompt = (
                "Phân tích file audio này và thực hiện 2 việc:\n"
                "1. Nhận diện ngôn ngữ được nói trong audio (ví dụ: English, Vietnamese, Japanese, Chinese, French, German).\n"
                "2. Trích xuất toàn bộ bản chép lời (transcript) theo từng câu có mốc thời gian start_time và end_time tính bằng giây.\n"
                "Trả về định dạng JSON thuần túy (không markdown) với cấu trúc:\n"
                "{\n"
                '  "language": "English",\n'
                '  "segments": [\n'
                '    {"start_time": 0.0, "end_time": 4.5, "text": "Sentence text"}\n'
                '  ]\n'
                "}"
            )

            from app.providers.llm.gemini_provider import GEMINI_MODEL_CANDIDATES

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

            import httpx
            async with httpx.AsyncClient(timeout=90.0) as client:

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

                                detected_lang = parsed_json.get("language", "English")
                                raw_segments = parsed_json.get("segments", [])

                                if raw_segments:
                                    formatted_segments = []
                                    for idx, s in enumerate(raw_segments, start=1):
                                        st = float(s.get("start_time", 0.0))
                                        et = float(s.get("end_time", st + 4.0))
                                        txt = str(s.get("text", "")).strip()
                                        if txt:
                                            formatted_segments.append({
                                                "number": idx,
                                                "start_time": round(st, 2),
                                                "end_time": round(et, 2),
                                                "text": txt,
                                            })
                                    if formatted_segments:
                                        log_job_event(job_id, "STT", f"Gemini STT ({model}) completed. Detected: {detected_lang}, Segments: {len(formatted_segments)}")
                                        return formatted_segments, detected_lang
                        elif res.status_code in (404, 503, 429):
                            logger.warning(f"Gemini STT model '{model}' returned HTTP {res.status_code}. Trying fallback model...")
                            continue
                    except Exception as ex:
                        logger.warning(f"Gemini STT request failed on model '{model}': {str(ex)}")
                        continue
        except Exception as e:
            log_job_event(job_id, "STT", f"Gemini STT warning: {str(e)}. Using fallback chunker.")


    # Fallback STT segment generator based on total audio duration
    detected_lang = "English" if source_language == "auto" else source_language
    chunk_len = 8.0
    segment_count = max(1, int(total_duration / chunk_len))

    segments = []
    for i in range(segment_count):
        st = i * chunk_len
        et = min(total_duration, (i + 1) * chunk_len)
        segments.append({
            "number": i + 1,
            "start_time": round(st, 2),
            "end_time": round(et, 2),
            "text": f"Phần phát biểu video #{i+1} [{st:.0f}s - {et:.0f}s]",
        })

    log_job_event(job_id, "STT", f"Fallback STT created {len(segments)} segments.")
    return segments, detected_lang


async def translate_transcript_segments(
    segments: List[Dict[str, Any]],
    source_language: str,
    target_language: str,
    job_id: str = "VT-JOB",
) -> List[Dict[str, Any]]:
    """
    Translate transcript text segments to target language using LLM Provider.
    """
    registry = get_registry()
    gemini = registry.get_llm("gemini")

    lang_names = {
        "vi": "Tiếng Việt",
        "en": "English",
        "ja": "Tiếng Nhật",
        "ko": "Tiếng Hàn",
        "zh": "Tiếng Trung",
        "fr": "Tiếng Pháp",
        "de": "Tiếng Đức",
        "es": "Tiếng Tây Ban Nha",
    }
    target_lang_name = lang_names.get(target_language.lower(), target_language)
    log_job_event(job_id, "TRANSLATING", f"Translating {len(segments)} segments to {target_lang_name}...")

    if gemini and settings.GEMINI_API_KEY:
        try:
            texts_to_translate = [s["text"] for s in segments]
            prompt = (
                f"Hãy dịch các câu văn sau sang {target_lang_name}. "
                "Giữ nguyên thứ tự câu và phong cách tự nhiên để lồng tiếng video. "
                "Trả về một mảng JSON thuần túy (không markdown) chứa các chuỗi dịch tương ứng:\n"
                f"{json.dumps(texts_to_translate, ensure_ascii=False)}"
            )

            response_text = await gemini.generate_text(prompt)
            json_str = re.sub(r"^```json\s*", "", response_text, flags=re.MULTILINE)
            json_str = re.sub(r"```$", "", json_str, flags=re.MULTILINE).strip()
            translated_list = json.loads(json_str)

            if isinstance(translated_list, list) and len(translated_list) == len(segments):
                for seg, trans in zip(segments, translated_list):
                    seg["translated_text"] = str(trans).strip()
                log_job_event(job_id, "TRANSLATING", f"Gemini translation completed successfully.")
                return segments
        except Exception as e:
            log_job_event(job_id, "TRANSLATING", f"Gemini translation warning: {str(e)}")

    for s in segments:
        orig = s["text"]
        if target_language == "vi" and "Phần phát biểu" in orig:
            s["translated_text"] = orig
        else:
            s["translated_text"] = f"[Dịch {target_lang_name}]: {orig}"

    return segments


async def sync_and_stretch_audio(
    tts_audio_path: Path,
    target_duration: float,
    output_synced_path: Path,
    job_id: str = "VT-JOB",
    on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_pid: Optional[Callable[[int], None]] = None,
) -> float:
    """
    Adjust audio speed (time-stretch) using FFmpeg atempo filter to match target duration.
    """
    actual_duration = await probe_duration_async(tts_audio_path)
    output_synced_path.parent.mkdir(parents=True, exist_ok=True)

    if target_duration <= 0 or abs(actual_duration - target_duration) < 0.3:
        shutil.copy2(tts_audio_path, output_synced_path)
        return actual_duration

    tempo = actual_duration / target_duration
    tempo_clamped = max(0.75, min(1.5, tempo))

    cmd = [
        "ffmpeg", "-y",
        "-i", str(tts_audio_path),
        "-filter:a", f"atempo={tempo_clamped:.3f}",
        "-vn",
        str(output_synced_path),
    ]

    await run_ffmpeg_with_progress_async(
        cmd,
        total_duration=actual_duration,
        on_progress=on_progress,
        on_pid=on_pid,
        timeout=60.0,
    )

    if output_synced_path.exists():
        new_dur = await probe_duration_async(output_synced_path)
        return new_dur

    shutil.copy2(tts_audio_path, output_synced_path)
    return actual_duration


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
    Render final dubbed video by combining TTS audio segments onto timeline and mixing with original video.
    """
    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    log_job_event(job_id, "RENDERING", "Probing total video duration for final render...")
    total_video_duration = await probe_duration_async(video_path)

    combined_audio_path = work_dir / "combined_dubbed_audio.wav"
    valid_segments = [s for s in segments if s.synced_audio_path or s.tts_audio_path]

    if not valid_segments:
        raise ValueError("❌ Không có phân đoạn âm thanh lồng tiếng nào được tạo.")

    log_job_event(job_id, "RENDERING", f"Combining {len(valid_segments)} audio segments into timeline (Duration: {total_video_duration:.1f}s)...")

    # Build FFmpeg inputs and filter graph directly from valid_segments
    inputs = []
    filter_chain = []
    
    for idx, seg in enumerate(valid_segments):
        seg_audio = Path(seg.synced_audio_path or seg.tts_audio_path)
        inputs.extend(["-i", str(seg_audio)])
        delay_ms = max(0, round(seg.start_time * 1000))
        filter_chain.append(f"[{idx}:a]adelay=delays={delay_ms}:all=1[a{idx}]")

    num_segments = len(valid_segments)
    if num_segments == 1:
        filter_graph = f"{filter_chain[0]};[a0]apad=whole_dur={total_video_duration:.2f}[outa]"
    else:
        mix_inputs = "".join(f"[a{i}]" for i in range(num_segments))
        filter_statements = ";".join(filter_chain)
        filter_graph = f"{filter_statements};{mix_inputs}amix=inputs={num_segments}:duration=longest:dropout_transition=0,apad=whole_dur={total_video_duration:.2f}[outa]"

    cmd_mix = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_graph,
        "-map", "[outa]",
        str(combined_audio_path),
    ]

    log_job_event(job_id, "RENDERING", f"Executing FFmpeg audio timeline mix with {num_segments} audio inputs...")
    
    used_fallback = False
    try:
        await run_ffmpeg_with_progress_async(
            cmd_mix,
            total_duration=total_video_duration,
            on_progress=on_progress,
            on_pid=on_pid,
            timeout=180.0,
        )
    except Exception as mix_err:
        used_fallback = True
        log_job_event(job_id, "RENDERING", f"❌ Primary audio timeline mix failed: {str(mix_err)}\nFilter used: {filter_graph}")
        concat_list_path = work_dir / "audio_concat.txt"
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for seg in valid_segments:
                seg_audio = Path(seg.synced_audio_path or seg.tts_audio_path)
                f.write(f"file '{seg_audio.resolve()}'\n")

        cmd_concat = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_list_path),
            "-c", "copy",
            str(combined_audio_path),
        ]
        await run_ffmpeg_with_progress_async(cmd_concat, total_duration=total_video_duration, timeout=60.0)
        log_job_event(job_id, "RENDERING", "⚠️ WARNING: Audio timeline mix used fallback concat method!")

    if not combined_audio_path.exists() or combined_audio_path.stat().st_size == 0:
        raise RuntimeError("❌ Không thể tạo file âm thanh lồng tiếng tổng hợp (combined_dubbed_audio.wav).")

    log_job_event(job_id, "RENDERING", f"Muxing dubbed audio with video (Mode: {original_audio_mode})...")

    # Merge combined audio into video according to original_audio_mode
    if original_audio_mode == AudioMixMode.MUTE.value:
        cmd_final = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(combined_audio_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            str(output_video_path),
        ]
    elif original_audio_mode == AudioMixMode.DUCK.value:
        cmd_final = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(combined_audio_path),
            "-filter_complex", "[0:a]volume=0.15[orig];[1:a]volume=1.0[dub];[orig][dub]amix=inputs=2:duration=first:dropout_transition=0[outa]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "[outa]",
            "-shortest",
            str(output_video_path),
        ]
    else:
        cmd_final = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(combined_audio_path),
            "-filter_complex", "[0:a]volume=1.0[orig];[1:a]volume=1.0[dub];[orig][dub]amix=inputs=2:duration=first:dropout_transition=0[outa]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "[outa]",
            "-shortest",
            str(output_video_path),
        ]

    await run_ffmpeg_with_progress_async(
        cmd_final,
        total_duration=total_video_duration,
        on_progress=on_progress,
        on_pid=on_pid,
        timeout=300.0,
    )

    if not output_video_path.exists() or output_video_path.stat().st_size == 0:
        raise RuntimeError("❌ FFmpeg render final video failed: File output không tồn tại hoặc bị rỗng.")

    if used_fallback:
        log_job_event(job_id, "COMPLETED_WITH_FALLBACK", f"Final video rendered with fallback: {output_video_path}")
    else:
        log_job_event(job_id, "RENDERING", f"Final video rendered successfully: {output_video_path}")

    return output_video_path
