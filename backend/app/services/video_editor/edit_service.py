"""
Video Editing Automation Service — Reframing (16:9 / 9:16 / 1:1), Watermark Overlay, BGM Ducking & Bumper Concatenation.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List

from app.core import get_logger
from app.core.job_logger import log_job_event
from app.media.ffprobe import probe_duration_async, get_video_metadata_async
from app.models.video_editor import AspectRatioEnum, WatermarkPositionEnum
from app.services.video_editor.watermark_service import build_image_watermark_filter, WatermarkPosition

logger = get_logger(__name__)



def build_watermark_filter(
    video_w: int,
    video_h: int,
    logo_scale: float = 0.20,
    position: str = "bottom_right",
    opacity: float = 0.80,
    margin_px: int = 20,
) -> str:
    """
    Build FFmpeg complex filter string for logo overlay with scaling, opacity, and positioning.
    """
    pos = WatermarkPosition.normalize(position)
    filter_chain, _ = build_image_watermark_filter(
        video_w=video_w,
        video_h=video_h,
        position=pos,
        scale=logo_scale,
        opacity=opacity,
        margin_px=margin_px,
    )
    return filter_chain



def build_reframing_filter(
    source_w: int,
    source_h: int,
    target_aspect_ratio: str,
) -> str:
    """
    Build FFmpeg video filter string for aspect ratio reframing (9:16 portrait or 1:1 square or 16:9 landscape).
    Uses smart crop or blur background padding.
    """
    if target_aspect_ratio == AspectRatioEnum.PORTRAIT_9_16.value:
        # 1080x1920 vertical video with blurred background padding
        filter_str = (
            "[0:v]split[bg][fg];"
            "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40[blurred];"
            "[fg]scale=1080:1920:force_original_aspect_ratio=decrease[scaled];"
            "[blurred][scaled]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[outv]"
        )
    elif target_aspect_ratio == AspectRatioEnum.SQUARE_1_1.value:
        # 1080x1080 square video
        filter_str = (
            "[0:v]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080[outv]"
        )
    else:
        # 16:9 1920x1080 default
        filter_str = (
            "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[outv]"
        )
    return filter_str


class VideoEditAutomationService:
    """Service for executing automated video editing tasks via FFmpeg."""

    @staticmethod
    async def apply_watermark_and_reframing(
        input_video_path: Path,
        output_video_path: Path,
        logo_path: Optional[Path] = None,
        logo_position: str = "top_right",
        logo_scale: float = 0.15,
        logo_opacity: float = 0.85,
        target_aspect_ratio: str = "16:9",
        bgm_path: Optional[Path] = None,
        bgm_volume_db: float = -18.0,
        job_id: str = "VT-EDIT",
    ) -> Path:
        """
        Apply watermark, aspect ratio reframing, and optional background music (BGM) mixing in a single FFmpeg pass.
        """
        output_video_path.parent.mkdir(parents=True, exist_ok=True)
        meta = await get_video_metadata_async(input_video_path)
        video_w = meta.get("width", 1920) or 1920
        video_h = meta.get("height", 1080) or 1080
        total_duration = meta.get("duration", 0.0)

        cmd = ["ffmpeg", "-y", "-i", str(input_video_path)]
        
        inputs_count = 1
        filter_complex_parts = []
        video_stream_map = "0:v"
        audio_stream_map = "0:a?"

        # 1. Add Logo Input if provided
        if logo_path and logo_path.exists():
            cmd.extend(["-i", str(logo_path)])
            logo_input_idx = inputs_count
            inputs_count += 1
            
            logo_w = int(video_w * logo_scale)
            pos_expr = f"main_w-overlay_w-20:20"
            if logo_position == WatermarkPositionEnum.TOP_LEFT.value:
                pos_expr = "20:20"
            elif logo_position == WatermarkPositionEnum.BOTTOM_LEFT.value:
                pos_expr = "20:main_h-overlay_h-20"
            elif logo_position == WatermarkPositionEnum.BOTTOM_RIGHT.value:
                pos_expr = "main_w-overlay_w-20:main_h-overlay_h-20"
            elif logo_position == WatermarkPositionEnum.CENTER.value:
                pos_expr = "(main_w-overlay_w)/2:(main_h-overlay_h)/2"

            filter_complex_parts.append(
                f"[{logo_input_idx}:v]scale={logo_w}:-1,format=rgba,colorchannelmixer=aa={logo_opacity:.2f}[logo];"
                f"[0:v][logo]overlay={pos_expr}[v_logo]"
            )
            video_stream_map = "[v_logo]"

        # 2. Reframing if needed
        if target_aspect_ratio == AspectRatioEnum.PORTRAIT_9_16.value:
            bg_fg_in = video_stream_map if video_stream_map.startswith("[") else f"[{video_stream_map}]"
            filter_complex_parts.append(
                f"{bg_fg_in}split[bg][fg];"
                f"[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30[blurred];"
                f"[fg]scale=1080:1920:force_original_aspect_ratio=decrease[scaled];"
                f"[blurred][scaled]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[v_reframe]"
            )
            video_stream_map = "[v_reframe]"

        # 3. Background Music (BGM) Auto-Ducking if BGM file provided
        if bgm_path and bgm_path.exists():
            cmd.extend(["-i", str(bgm_path)])
            bgm_idx = inputs_count
            inputs_count += 1
            bgm_vol_linear = 10 ** (bgm_volume_db / 20.0)
            
            filter_complex_parts.append(
                f"[{bgm_idx}:a]volume={bgm_vol_linear:.3f}[bgm_adj];"
                f"[0:a][bgm_adj]amix=inputs=2:duration=first:dropout_transition=2[a_out]"
            )
            audio_stream_map = "[a_out]"

        # Build FFmpeg command execution
        if filter_complex_parts:
            complex_str = ";".join(filter_complex_parts)
            cmd.extend(["-filter_complex", complex_str])
            cmd.extend(["-map", video_stream_map.replace("[", "").replace("]", "") if not filter_complex_parts else video_stream_map])
            if audio_stream_map != "0:a?":
                cmd.extend(["-map", audio_stream_map])
            else:
                cmd.extend(["-map", "0:a?"])
        else:
            cmd.extend(["-c:v", "copy", "-c:a", "copy"])

        cmd.extend(["-c:v", "libx264", "-preset", "fast", "-crf", "22", "-c:a", "aac", "-b:a", "192k", str(output_video_path)])

        log_job_event(job_id, "RENDERING", f"Running Video Editing Automation (Aspect: {target_aspect_ratio}, Watermark: {bool(logo_path)})...")
        await run_ffmpeg_with_progress_async(cmd, total_duration=total_duration, timeout=300.0)

        if not output_video_path.exists() or output_video_path.stat().st_size == 0:
            raise RuntimeError(f"Video editing automation failed to generate output file: {output_video_path}")

        log_job_event(job_id, "RENDERING", f"Video editing automation completed: {output_video_path.name}")
        return output_video_path
