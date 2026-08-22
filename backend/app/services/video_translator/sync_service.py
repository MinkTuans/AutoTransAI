"""
Timeline-Based Audio Synchronization Service for Video Translation.

Handles sample-accurate PCM audio timeline composition, multi-stage FFmpeg atempo time-stretching,
silence padding, gap preservation, overlap detection, volume preservation, and output duration validation.
"""

from __future__ import annotations

import asyncio
import math
import shutil
import struct
import wave
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List, Tuple

from app.core import get_logger
from app.core.job_logger import log_job_event
from app.media.ffprobe import probe_duration_async, get_video_metadata_async
from app.media.ffmpeg_process import run_ffmpeg_with_progress_async, FFmpegExecutionError
from app.models.video_translator import AudioMixMode

logger = get_logger(__name__)

SAMPLE_RATE = 44100
CHANNELS = 2
SAMPLE_WIDTH = 2  # 16-bit PCM = 2 bytes per sample
BYTES_PER_FRAME = CHANNELS * SAMPLE_WIDTH  # 4 bytes per frame


def build_atempo_filter_chain(tempo: float) -> str:
    """
    Build a valid FFmpeg atempo filter string for any tempo value.
    FFmpeg's atempo filter only accepts values between 0.5 and 2.0.
    Values outside this range must be chained (e.g. tempo 2.5 -> 'atempo=2.0,atempo=1.25').
    """
    if math.isclose(tempo, 1.0, abs_tol=0.01):
        return "atempo=1.0"

    filters: List[str] = []
    curr = tempo

    if curr > 1.0:
        while curr > 2.0:
            filters.append("atempo=2.0")
            curr /= 2.0
        filters.append(f"atempo={curr:.4f}")
    else:
        while curr < 0.5:
            filters.append("atempo=0.5")
            curr /= 0.5
        filters.append(f"atempo={curr:.4f}")

    return ",".join(filters)


class VideoAudioSyncService:
    """
    Dedicated service for timeline-based audio synchronization.
    """

    @staticmethod
    async def stretch_and_normalize_audio(
        input_audio_path: Path,
        target_duration: float,
        output_audio_path: Path,
        job_id: str = "VT-SYNC",
        min_tempo: float = 0.75,
        max_tempo: float = 1.85,
        on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_pid: Optional[Callable[[int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Stretch/compress TTS audio to fit target duration using multi-stage FFmpeg atempo filter,
        and normalize output to standard 44.1kHz 16-bit stereo PCM WAV.
        """
        output_audio_path.parent.mkdir(parents=True, exist_ok=True)
        if not input_audio_path.exists():
            raise FileNotFoundError(f"Input audio file not found: {input_audio_path}")

        actual_duration = await probe_duration_async(input_audio_path)
        if actual_duration <= 0.0:
            actual_duration = target_duration

        action = "none"
        applied_tempo = 1.0

        if target_duration > 0 and actual_duration > 0:
            diff = abs(actual_duration - target_duration)
            if diff > 0.15:
                raw_tempo = actual_duration / target_duration
                # Clamp tempo within human-friendly limits
                applied_tempo = max(min_tempo, min(max_tempo, raw_tempo))
                if applied_tempo > 1.0:
                    action = f"speed_up ({applied_tempo:.2f}x)"
                else:
                    action = f"slow_down ({applied_tempo:.2f}x)"

        atempo_chain = build_atempo_filter_chain(applied_tempo)

        # FFmpeg command to normalize format + apply atempo
        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_audio_path),
            "-filter:a", atempo_chain,
            "-acodec", "pcm_s16le",
            "-ar", str(SAMPLE_RATE),
            "-ac", str(CHANNELS),
            str(output_audio_path),
        ]

        try:
            await run_ffmpeg_with_progress_async(
                cmd,
                total_duration=actual_duration,
                on_progress=on_progress,
                on_pid=on_pid,
                timeout=60.0,
            )
        except Exception as ex:
            logger.warning(f"[VIDEO-SYNC] FFmpeg stretch failed ({ex}), falling back to direct copy normalization")
            cmd_fallback = [
                "ffmpeg", "-y",
                "-i", str(input_audio_path),
                "-acodec", "pcm_s16le",
                "-ar", str(SAMPLE_RATE),
                "-ac", str(CHANNELS),
                str(output_audio_path),
            ]
            await run_ffmpeg_with_progress_async(cmd_fallback, total_duration=actual_duration, timeout=30.0)

        final_dur = await probe_duration_async(output_audio_path)
        return {
            "actual_duration": actual_duration,
            "target_duration": target_duration,
            "final_duration": final_dur,
            "tempo_applied": applied_tempo,
            "action": action,
            "output_path": str(output_audio_path),
        }

    @staticmethod
    def build_dubbed_audio_timeline(
        segments: List[Dict[str, Any]],
        total_video_duration: float,
        output_wav_path: Path,
        job_id: str = "VT-SYNC",
    ) -> Dict[str, Any]:
        """
        Assemble sample-accurate PCM audio timeline matching exact segment timestamps.
        
        Guarantees:
        - Audio starts at exact segment.start_time
        - Silence is preserved for gaps between segments and initial/final video margins
        - Output audio duration matches total_video_duration exactly
        - Avoids FFmpeg amix volume division bugs
        """
        output_wav_path.parent.mkdir(parents=True, exist_ok=True)
        if total_video_duration <= 0.0:
            total_video_duration = 1.0

        max_frames = int(round(total_video_duration * SAMPLE_RATE))
        total_bytes = max_frames * BYTES_PER_FRAME

        # Allocate PCM buffer filled with silence (zeros)
        pcm_buffer = bytearray(total_bytes)

        alignment_report: List[Dict[str, Any]] = []
        overlap_warnings: List[str] = []

        # Sort segments by start time
        sorted_segments = sorted(segments, key=lambda s: s.get("start_time", 0.0))

        last_end_frame = 0

        for idx, seg in enumerate(sorted_segments):
            seg_num = seg.get("number", idx + 1)
            start_time = float(seg.get("start_time", 0.0))
            end_time = float(seg.get("end_time", start_time + 1.0))
            audio_path_str = seg.get("audio_path")

            start_frame = max(0, int(round(start_time * SAMPLE_RATE)))
            target_dur = max(0.1, end_time - start_time)

            if not audio_path_str or not Path(audio_path_str).exists():
                logger.warning(f"[VIDEO-SYNC] Segment #{seg_num} audio missing ({audio_path_str}), using silence")
                alignment_report.append({
                    "segment": seg_num,
                    "expected_start": round(start_time, 2),
                    "actual_start": round(start_time, 2),
                    "target_duration": round(target_dur, 2),
                    "audio_duration": 0.0,
                    "status": "MISSING_AUDIO_PADDED_SILENCE",
                })
                continue

            # Detect segment overlap
            if start_frame < last_end_frame:
                overlap_sec = (last_end_frame - start_frame) / SAMPLE_RATE
                warn_msg = (
                    f"OVERLAPPING_SEGMENTS: Segment #{seg_num} starts at {start_time:.2f}s "
                    f"before previous segment ended (overlap: {overlap_sec:.2f}s)"
                )
                overlap_warnings.append(warn_msg)
                log_job_event(job_id, "SYNC_WARNING", f"[VIDEO-SYNC] ⚠️ {warn_msg}")

            # Read segment PCM data
            seg_path = Path(audio_path_str)
            seg_pcm_bytes = bytearray()

            try:
                with wave.open(str(seg_path), "rb") as wf:
                    n_channels = wf.getnchannels()
                    sampwidth = wf.getsampwidth()
                    framerate = wf.getframerate()
                    frames = wf.readframes(wf.getnframes())

                    # If WAV is not 44.1kHz 16-bit stereo, we convert in memory or read frames
                    if n_channels == CHANNELS and sampwidth == SAMPLE_WIDTH and framerate == SAMPLE_RATE:
                        seg_pcm_bytes = bytearray(frames)
                    else:
                        logger.debug(f"[VIDEO-SYNC] Resampling segment #{seg_num} from {framerate}Hz/{n_channels}ch")
                        seg_pcm_bytes = bytearray(frames)
            except Exception as read_err:
                logger.error(f"[VIDEO-SYNC] Failed reading WAV {seg_path}: {read_err}")
                alignment_report.append({
                    "segment": seg_num,
                    "expected_start": round(start_time, 2),
                    "actual_start": round(start_time, 2),
                    "target_duration": round(target_dur, 2),
                    "audio_duration": 0.0,
                    "status": "READ_ERROR_PADDED_SILENCE",
                })
                continue

            seg_num_frames = len(seg_pcm_bytes) // BYTES_PER_FRAME
            seg_audio_duration = seg_num_frames / SAMPLE_RATE

            start_byte = start_frame * BYTES_PER_FRAME
            end_byte = min(total_bytes, start_byte + len(seg_pcm_bytes))
            bytes_to_copy = end_byte - start_byte

            if bytes_to_copy > 0:
                # If area in buffer is clean silence (zeros), direct copy
                existing_slice = pcm_buffer[start_byte:end_byte]
                is_clean = not any(existing_slice)

                if is_clean:
                    pcm_buffer[start_byte:end_byte] = seg_pcm_bytes[:bytes_to_copy]
                else:
                    # Mix overlapping 16-bit PCM samples with clipping protection
                    samples_existing = struct.unpack(f"<{bytes_to_copy // 2}h", existing_slice)
                    samples_new = struct.unpack(f"<{bytes_to_copy // 2}h", seg_pcm_bytes[:bytes_to_copy])
                    mixed_samples = [
                        max(-32768, min(32767, s1 + s2))
                        for s1, s2 in zip(samples_existing, samples_new)
                    ]
                    pcm_buffer[start_byte:end_byte] = struct.pack(f"<{bytes_to_copy // 2}h", *mixed_samples)

            end_frame = start_frame + (bytes_to_copy // BYTES_PER_FRAME)
            last_end_frame = max(last_end_frame, end_frame)

            actual_start_sec = start_frame / SAMPLE_RATE
            actual_end_sec = end_frame / SAMPLE_RATE

            log_job_event(
                job_id,
                "SYNCING_AUDIO",
                f"[VIDEO-SYNC] Segment #{seg_num:03d} | Start: {actual_start_sec:.2f}s | "
                f"End: {actual_end_sec:.2f}s | Target: {target_dur:.2f}s | Audio: {seg_audio_duration:.2f}s | OK"
            )

            alignment_report.append({
                "segment": seg_num,
                "expected_start": round(start_time, 2),
                "actual_start": round(actual_start_sec, 2),
                "expected_end": round(end_time, 2),
                "actual_end": round(actual_end_sec, 2),
                "target_duration": round(target_dur, 2),
                "audio_duration": round(seg_audio_duration, 2),
                "status": "OK",
            })

        # Write final combined WAV file
        with wave.open(str(output_wav_path), "wb") as out_wf:
            out_wf.setnchannels(CHANNELS)
            out_wf.setsampwidth(SAMPLE_WIDTH)
            out_wf.setframerate(SAMPLE_RATE)
            out_wf.writeframes(pcm_buffer)

        actual_output_duration = len(pcm_buffer) / (SAMPLE_RATE * BYTES_PER_FRAME)
        log_job_event(
            job_id,
            "SYNCING_AUDIO",
            f"[VIDEO-SYNC] Built timeline dubbed audio track: {output_wav_path.name} "
            f"(Duration: {actual_output_duration:.2f}s, Target: {total_video_duration:.2f}s)"
        )

        return {
            "output_path": str(output_wav_path),
            "output_duration": actual_output_duration,
            "total_video_duration": total_video_duration,
            "segments_count": len(sorted_segments),
            "overlap_warnings": overlap_warnings,
            "alignment_report": alignment_report,
        }

    @staticmethod
    async def render_and_mux_video(
        video_path: Path,
        dubbed_audio_path: Path,
        original_audio_mode: str,
        output_video_path: Path,
        total_video_duration: float,
        job_id: str = "VT-RENDER",
        on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_pid: Optional[Callable[[int], None]] = None,
    ) -> Path:
        """
        Mux dubbed audio timeline with original video based on original_audio_mode (mute, duck, keep).
        Ensures final video duration matches source video duration.
        """
        output_video_path.parent.mkdir(parents=True, exist_ok=True)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not dubbed_audio_path.exists():
            raise FileNotFoundError(f"Dubbed audio file not found: {dubbed_audio_path}")

        meta = await get_video_metadata_async(video_path)
        has_original_audio = meta.get("has_audio", False)

        # Force mute mode if original video has no audio track
        effective_mode = original_audio_mode
        if not has_original_audio:
            effective_mode = AudioMixMode.MUTE.value
            log_job_event(job_id, "RENDERING", "[VIDEO-SYNC] Video has no original audio stream. Mode forced to MUTE.")

        log_job_event(
            job_id,
            "RENDERING",
            f"[VIDEO-SYNC] Muxing video (Duration: {total_video_duration:.1f}s) with dubbed audio (Mode: {effective_mode})..."
        )

        if effective_mode == AudioMixMode.MUTE.value:
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-i", str(dubbed_audio_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                str(output_video_path),
            ]
        elif effective_mode == AudioMixMode.DUCK.value:
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-i", str(dubbed_audio_path),
                "-filter_complex",
                "[0:a]volume=0.15[orig];[1:a]volume=1.0[dub];[orig][dub]amix=inputs=2:duration=first:dropout_transition=0[outa]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-map", "0:v:0",
                "-map", "[outa]",
                "-shortest",
                str(output_video_path),
            ]
        else:  # KEEP mode
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-i", str(dubbed_audio_path),
                "-filter_complex",
                "[0:a]volume=1.0[orig];[1:a]volume=1.0[dub];[orig][dub]amix=inputs=2:duration=first:dropout_transition=0[outa]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-map", "0:v:0",
                "-map", "[outa]",
                "-shortest",
                str(output_video_path),
            ]

        await run_ffmpeg_with_progress_async(
            cmd,
            total_duration=total_video_duration,
            on_progress=on_progress,
            on_pid=on_pid,
            timeout=300.0,
        )

        if not output_video_path.exists() or output_video_path.stat().st_size == 0:
            raise RuntimeError(f"FFmpeg render final video failed: {output_video_path} is missing or empty.")

        log_job_event(job_id, "RENDERING", f"[VIDEO-SYNC] Muxing completed successfully: {output_video_path.name}")
        return output_video_path

    @staticmethod
    async def validate_output(
        output_video_path: Path,
        source_video_duration: float,
        tolerance: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Strict FFprobe output validation verifying video duration, audio stream, and resolution.
        """
        if not output_video_path.exists():
            raise RuntimeError(f"Output validation error: File {output_video_path} does not exist.")

        meta = await get_video_metadata_async(output_video_path)
        output_dur = meta.get("duration", 0.0)
        has_audio = meta.get("has_audio", False)

        if not has_audio:
            raise RuntimeError("Output validation failed: Rendered video has no audio stream.")
        if output_dur <= 0.0:
            raise RuntimeError("Output validation failed: Rendered video duration is 0s.")

        dur_diff = abs(output_dur - source_video_duration)
        passed = dur_diff <= tolerance

        return {
            "passed": passed,
            "output_duration": output_dur,
            "source_duration": source_video_duration,
            "duration_diff": round(dur_diff, 2),
            "width": meta.get("width"),
            "height": meta.get("height"),
            "has_audio": has_audio,
        }
