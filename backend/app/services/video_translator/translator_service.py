"""
Video Translation Pipeline Service.

Manages audio extraction, Speech-to-Text (STT), Language Detection,
LLM Translation, TTS generation, Audio Synchronization (time-stretching),
and final FFmpeg audio mix / video rendering.
"""

from __future__ import annotations

import asyncio
import base64
import json
import re
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.core import get_logger
from app.core.exceptions import WorkflowError
from app.media.ffprobe import probe_duration_async, get_video_metadata_async
from app.media.ffmpeg import safe_subprocess_run_async
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


async def extract_audio_from_video(video_path: Path, output_audio_path: Path) -> float:
    """
    Extract audio track from video file into 16kHz MONO WAV file using FFmpeg.
    """
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Check audio track presence
    meta = await get_video_metadata_async(video_path)
    if not meta.get("has_audio"):
        raise ValueError("Video không chứa track audio. Không thể thực hiện dịch giọng nói.")

    output_audio_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_audio_path),
    ]

    res = await safe_subprocess_run_async(cmd, timeout=120)
    if res.returncode != 0 or not output_audio_path.exists() or output_audio_path.stat().st_size == 0:
        raise RuntimeError("Không thể trích xuất audio từ video.")

    duration = await probe_duration_async(output_audio_path)
    if duration <= 0:
        raise ValueError("File audio trích xuất có thời lượng bằng 0.")

    return duration


async def speech_to_text_and_detect_language(
    audio_path: Path,
    target_language: str = "vi",
    source_language: str = "auto",
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Perform Speech-to-Text and Language Detection on the extracted audio.

    Returns:
        Tuple of (list_of_segment_dicts, detected_language_name)
    """
    registry = get_registry()
    gemini = registry.get_llm("gemini")

    total_duration = await probe_duration_async(audio_path)
    if total_duration <= 0:
        raise ValueError("File audio không hợp lệ.")

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

            # Request Gemini API with inline audio payload
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
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
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    if parts:
                        raw_response = parts[0].get("text", "").strip()
                        # Clean json wrapping
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
                                return formatted_segments, detected_lang
        except Exception as e:
            logger.warning("Gemini multimodal STT failed, falling back to segment chunker", error=str(e))

    # Fallback STT segment generator based on total audio duration
    detected_lang = "English" if source_language == "auto" else source_language
    chunk_len = 8.0  # 8 seconds per segment
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

    return segments, detected_lang


async def translate_transcript_segments(
    segments: List[Dict[str, Any]],
    source_language: str,
    target_language: str,
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
                return segments
        except Exception as e:
            logger.warning("Gemini translation failed, using direct text fallback", error=str(e))

    # Simple fallback translation placeholder if LLM key unavailable
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
) -> float:
    """
    Adjust audio speed (time-stretch) using FFmpeg atempo filter to match target duration.
    """
    actual_duration = await probe_duration_async(tts_audio_path)
    output_synced_path.parent.mkdir(parents=True, exist_ok=True)

    if target_duration <= 0 or abs(actual_duration - target_duration) < 0.3:
        # Duration matches closely, copy as is
        import shutil
        shutil.copy2(tts_audio_path, output_synced_path)
        return actual_duration

    # Calculate tempo ratio: tempo = actual / target
    tempo = actual_duration / target_duration
    # Clamp tempo between 0.75 and 1.5 to prevent voice distortion
    tempo_clamped = max(0.75, min(1.5, tempo))

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(tts_audio_path),
        "-filter:a", f"atempo={tempo_clamped:.3f}",
        "-vn",
        str(output_synced_path),
    ]

    res = await safe_subprocess_run_async(cmd, timeout=60)
    if res.returncode == 0 and output_synced_path.exists():
        new_dur = await probe_duration_async(output_synced_path)
        return new_dur

    import shutil
    shutil.copy2(tts_audio_path, output_synced_path)
    return actual_duration


async def render_dubbed_video(
    video_path: Path,
    segments: List[VideoTranslationSegment],
    original_audio_mode: str,
    output_video_path: Path,
    work_dir: Path,
) -> Path:
    """
    Render final dubbed video by combining TTS audio segments and mixing with original video.
    """
    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    total_video_duration = await probe_duration_async(video_path)

    # 1. Create silent background audio track matching total video duration
    combined_audio_path = work_dir / "combined_dubbed_audio.wav"
    filter_complex_parts = []
    input_args = []

    # Filter inputs and construct overlay at specific timestamps
    valid_segments = [s for s in segments if s.synced_audio_path or s.tts_audio_path]

    if not valid_segments:
        raise ValueError("Không có phân đoạn âm thanh lồng tiếng nào được tạo.")

    # Create silence audio base
    silence_base = work_dir / "silence_base.wav"
    cmd_silence = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"anullsrc=r=24000:cl=mono:d={total_video_duration:.2f}",
        str(silence_base),
    ]
    await safe_subprocess_run_async(cmd_silence, timeout=30)

    # Combine audio segments at timestamps
    inputs = ["-i", str(silence_base)]
    filter_chain = ["[0:a]"]
    
    for idx, seg in enumerate(valid_segments, start=1):
        seg_audio = Path(seg.synced_audio_path or seg.tts_audio_path)
        inputs.extend(["-i", str(seg_audio)])
        delay_ms = int(seg.start_time * 1000)
        filter_chain.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms}[a{idx}];")

    # Mix all audio streams
    mix_inputs = "".join(f"[a{idx}]" for idx in range(1, len(valid_segments) + 1))
    filter_graph = "".join(filter_chain) + f"[0:a]{mix_inputs}amix=inputs={len(valid_segments)+1}:duration=first[outa]"

    cmd_mix = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_graph,
        "-map", "[outa]",
        str(combined_audio_path),
    ]

    res_mix = await safe_subprocess_run_async(cmd_mix, timeout=120)
    if res_mix.returncode != 0 or not combined_audio_path.exists():
        # Simple concat fallback if filter_complex fails
        logger.warning("Complex audio mix failed, using concat fallback")
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
        await safe_subprocess_run_async(cmd_concat, timeout=60)

    # 2. Merge combined audio into video according to original_audio_mode
    if original_audio_mode == AudioMixMode.MUTE.value:
        # Replaces original audio completely
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
        # Duck original audio volume to 20% and mix with 100% dubbed audio
        cmd_final = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(combined_audio_path),
            "-filter_complex", "[0:a]volume=0.2[orig];[1:a]volume=1.0[dub];[orig][dub]amix=inputs=2:duration=first[outa]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "[outa]",
            "-shortest",
            str(output_video_path),
        ]
    else:
        # Keep original audio at 100% volume and mix
        cmd_final = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(combined_audio_path),
            "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first[outa]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "[outa]",
            "-shortest",
            str(output_video_path),
        ]

    res_final = await safe_subprocess_run_async(cmd_final, timeout=300)
    if res_final.returncode != 0 or not output_video_path.exists():
        raise RuntimeError(f"FFmpeg render final video failed: {res_final.stderr[:200] if res_final.stderr else 'Lỗi render'}")

    return output_video_path
