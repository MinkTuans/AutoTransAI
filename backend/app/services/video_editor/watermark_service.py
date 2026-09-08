"""
Watermark Service — Automatic Video Logo & Text Watermark Processing via FFmpeg.
Provides robust filtergraph construction, dynamic scaling, opacity blending, drawtext escaping,
concurrency-safe execution, and clean temporary file lifecycle management.
"""

from __future__ import annotations

import asyncio
import enum
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field

from app.core import get_logger
from app.core.job_logger import log_job_event
from app.media.ffprobe import get_video_metadata_async
from app.media.ffmpeg_process import run_ffmpeg_with_progress_async, FFmpegExecutionError

logger = get_logger(__name__)


class WatermarkType(str, enum.Enum):
    IMAGE = "image"
    TEXT = "text"


class WatermarkPosition(str, enum.Enum):
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"

    @classmethod
    def normalize(cls, val: str) -> "WatermarkPosition":
        """Normalize hyphenated or lowercase position strings like 'top-left' to enum."""
        cleaned = str(val).lower().replace("-", "_").strip()
        try:
            return cls(cleaned)
        except ValueError:
            return cls.BOTTOM_RIGHT


def resolve_watermark_image_path(image_path: Optional[str]) -> Optional[Path]:
    """
    Safely resolve a watermark image path whether it is absolute, relative to CWD,
    relative to STORAGE_ROOT, or relative to DATA_DIR.
    """
    if not image_path or not str(image_path).strip():
        return None

    p = Path(image_path)
    if p.is_file():
        return p.resolve()

    from app.config import get_settings
    settings = get_settings()

    # Check relative to STORAGE_ROOT
    storage_p = settings.STORAGE_ROOT / image_path
    if storage_p.is_file():
        return storage_p.resolve()

    # Check relative to DATA_DIR
    data_p = settings.DATA_DIR / image_path
    if data_p.is_file():
        return data_p.resolve()

    # Strip leading 'storage/' or 'data/' if present in path string
    clean_path = str(image_path).replace("\\", "/")
    if clean_path.startswith("storage/"):
        clean_path = clean_path[len("storage/"):]
    elif clean_path.startswith("data/"):
        clean_path = clean_path[len("data/"):]

    storage_p2 = settings.STORAGE_ROOT / clean_path
    if storage_p2.is_file():
        return storage_p2.resolve()

    data_p2 = settings.DATA_DIR / clean_path
    if data_p2.is_file():
        return data_p2.resolve()

    return None


class WatermarkConfig(BaseModel):
    enabled: bool = False
    type: WatermarkType = WatermarkType.IMAGE
    image_path: Optional[str] = None
    text: Optional[str] = None
    position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT
    scale: float = Field(default=0.20, ge=0.05, le=0.80)  # Scale relative to video width
    opacity: float = Field(default=0.80, ge=0.05, le=1.0)
    margin: int = Field(default=20, ge=0, le=200)         # Pixel margin from video edge
    font_size: int = Field(default=32, ge=10, le=120)     # Font size for text mode

    def validate_for_execution(self) -> None:
        """Validate config parameters before running watermark process."""
        if not self.enabled:
            return
        if self.type == WatermarkType.IMAGE:
            if not self.image_path or not str(self.image_path).strip():
                raise ValueError("WATERMARK_LOGO_NOT_FOUND: Chế độ logo ảnh được bật nhưng đường dẫn logo trống.")
            resolved = resolve_watermark_image_path(self.image_path)
            if not resolved:
                raise FileNotFoundError(f"WATERMARK_LOGO_NOT_FOUND: File logo không tồn tại: {self.image_path}")
            if resolved.suffix.lower() not in [".png", ".jpg", ".jpeg", ".webp"]:
                raise ValueError(f"INVALID_WATERMARK_IMAGE: Định dạng file logo không hỗ trợ: {resolved.suffix}")
        elif self.type == WatermarkType.TEXT:
            if not self.text or not str(self.text).strip():
                raise ValueError("INVALID_WATERMARK_TEXT: Chế độ chữ được bật nhưng nội dung watermark trống.")


def escape_ffmpeg_drawtext(text: str) -> str:
    """
    Safely escape user-supplied string for FFmpeg drawtext filter syntax.
    Escapes quotes, backslashes, colons, commas, percent signs, and brackets.
    """
    if not text:
        return ""
    # Replace backslash first
    s = text.replace("\\", "\\\\")
    # Replace single quotes, double quotes, colons, commas, equals, percentages
    s = s.replace("'", "'\\\\''")
    s = s.replace(":", "\\:")
    s = s.replace(",", "\\,")
    s = s.replace("=", "\\=")
    s = s.replace("%", "\\%")
    s = s.replace("[", "\\[").replace("]", "\\]")
    return s


def build_image_watermark_filter(
    video_w: int,
    video_h: int,
    position: WatermarkPosition,
    scale: float = 0.20,
    opacity: float = 0.80,
    margin_px: int = 20,
) -> tuple[str, str]:
    """
    Build FFmpeg complex filter chain for image logo overlay.
    Returns tuple of (filter_complex_string, output_video_label).
    """
    logo_w = max(10, int(video_w * scale))
    
    pos = WatermarkPosition.normalize(position.value if isinstance(position, enum.Enum) else str(position))
    
    if pos == WatermarkPosition.TOP_LEFT:
        x_expr = f"{margin_px}"
        y_expr = f"{margin_px}"
    elif pos == WatermarkPosition.BOTTOM_LEFT:
        x_expr = f"{margin_px}"
        y_expr = f"main_h-overlay_h-{margin_px}"
    elif pos == WatermarkPosition.BOTTOM_RIGHT:
        x_expr = f"main_w-overlay_w-{margin_px}"
        y_expr = f"main_h-overlay_h-{margin_px}"
    elif pos == WatermarkPosition.CENTER:
        x_expr = "(main_w-overlay_w)/2"
        y_expr = "(main_h-overlay_h)/2"
    else:  # TOP_RIGHT
        x_expr = f"main_w-overlay_w-{margin_px}"
        y_expr = f"{margin_px}"

    # Filter string: scale logo -> format rgba -> apply opacity alpha channel -> overlay
    filter_chain = (
        f"[1:v]scale={logo_w}:-1,format=rgba,"
        f"colorchannelmixer=aa={opacity:.2f}[logo];"
        f"[0:v][logo]overlay={x_expr}:{y_expr}[wm_outv]"
    )
    return filter_chain, "[wm_outv]"


import sys

def resolve_system_font_path() -> Optional[str]:
    """
    Locate an available system font file (.ttf) for FFmpeg drawtext on Windows/Linux/macOS.
    Prevents FFmpeg fontconfig exit code 3221225477 (Access Violation) when fontconfig is missing on Windows.
    Returns FFmpeg filter-escaped file path string or None.
    """
    candidates: List[Path] = []
    if sys.platform.startswith("win"):
        candidates = [
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/calibri.ttf"),
            Path("C:/Windows/Fonts/segoeui.ttf"),
            Path("C:/Windows/Fonts/tahoma.ttf"),
            Path("C:/Windows/Fonts/verdana.ttf"),
        ]
    elif sys.platform == "darwin":
        candidates = [
            Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
            Path("/Library/Fonts/Arial.ttf"),
            Path("/System/Library/Fonts/Helvetica.ttc"),
        ]
    else:  # linux
        candidates = [
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
            Path("/usr/share/fonts/TTF/DejaVuSans.ttf"),
        ]

    for p in candidates:
        if p.exists():
            # Escape path for FFmpeg filter syntax (escape ':' with '\:')
            return str(p.as_posix()).replace(":", "\\:")
    return None


def build_text_watermark_filter(
    video_w: int,
    video_h: int,
    text: str,
    position: WatermarkPosition,
    font_size: int = 32,
    opacity: float = 0.80,
    margin_px: int = 20,
) -> tuple[str, str]:
    """
    Build FFmpeg complex filter chain for text watermark using drawtext.
    Returns tuple of (filter_complex_string, output_video_label).
    """
    escaped_text = escape_ffmpeg_drawtext(text)
    pos = WatermarkPosition.normalize(position.value if isinstance(position, enum.Enum) else str(position))

    if pos == WatermarkPosition.TOP_LEFT:
        x_expr = f"{margin_px}"
        y_expr = f"{margin_px}"
    elif pos == WatermarkPosition.BOTTOM_LEFT:
        x_expr = f"{margin_px}"
        y_expr = f"h-th-{margin_px}"
    elif pos == WatermarkPosition.BOTTOM_RIGHT:
        x_expr = f"w-tw-{margin_px}"
        y_expr = f"h-th-{margin_px}"
    elif pos == WatermarkPosition.CENTER:
        x_expr = "(w-tw)/2"
        y_expr = "(h-th)/2"
    else:  # TOP_RIGHT
        x_expr = f"w-tw-{margin_px}"
        y_expr = f"{margin_px}"

    font_path = resolve_system_font_path()
    fontfile_opt = f"fontfile='{font_path}':" if font_path else ""

    # Drawtext filter with high legibility background box
    filter_chain = (
        f"[0:v]drawtext={fontfile_opt}text='{escaped_text}':"
        f"fontsize={font_size}:"
        f"fontcolor=white@{opacity:.2f}:"
        f"x={x_expr}:y={y_expr}:"
        f"box=1:boxcolor=black@0.45:boxborderw=6[wm_outv]"
    )
    return filter_chain, "[wm_outv]"


class WatermarkService:
    """Service for validating, processing, and applying watermarks to videos."""

    @classmethod
    async def apply_watermark(
        cls,
        input_video_path: Path,
        output_video_path: Path,
        config: WatermarkConfig,
        job_id: str = "WATERMARK-JOB",
    ) -> Path:
        """
        Apply image or text watermark to a video file in a single FFmpeg pass.
        Guarantees cleanup of isolated temporary working files and concurrency safety.
        """
        if not config.enabled:
            logger.info(f"[WATERMARK] Job {job_id}: Watermark disabled. Skipping.")
            return input_video_path

        config.validate_for_execution()

        if not input_video_path.exists():
            raise FileNotFoundError(f"Input video file not found: {input_video_path}")

        output_video_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create unique concurrency-safe temporary working directory
        temp_dir = Path(tempfile.mkdtemp(prefix=f"wm_{job_id}_"))
        temp_target = temp_dir / f"watermarked_{output_video_path.name}"

        try:
            log_job_event(job_id, "APPLYING_WATERMARK", f"Probing video dimensions for watermark overlay: {input_video_path.name}")
            meta = await get_video_metadata_async(input_video_path)
            video_w = meta.get("width", 1920) or 1920
            video_h = meta.get("height", 1080) or 1080
            duration = meta.get("duration", 0.0)
            has_audio = meta.get("has_audio", True)

            cmd = ["ffmpeg", "-y", "-i", str(input_video_path)]

            if config.type == WatermarkType.IMAGE:
                logo_path = resolve_watermark_image_path(config.image_path)
                if not logo_path:
                    raise FileNotFoundError(f"WATERMARK_LOGO_NOT_FOUND: File logo không tồn tại: {config.image_path}")
                cmd.extend(["-i", str(logo_path)])
                
                filter_str, out_label = build_image_watermark_filter(
                    video_w=video_w,
                    video_h=video_h,
                    position=config.position,
                    scale=config.scale,
                    opacity=config.opacity,
                    margin_px=config.margin,
                )
            else:  # TEXT
                filter_str, out_label = build_text_watermark_filter(
                    video_w=video_w,
                    video_h=video_h,
                    text=config.text or "",
                    position=config.position,
                    font_size=config.font_size,
                    opacity=config.opacity,
                    margin_px=config.margin,
                )

            cmd.extend([
                "-filter_complex", filter_str,
                "-map", out_label,
            ])

            if has_audio:
                cmd.extend(["-c:a", "copy", "-map", "0:a:0?"])

            cmd.extend([
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "22",
                str(temp_target)
            ])

            log_job_event(
                job_id,
                "APPLYING_WATERMARK",
                f"Executing FFmpeg Watermark render (Type: {config.type.value}, Position: {config.position.value}, Scale: {config.scale*100:.0f}%, Opacity: {config.opacity:.2f})..."
            )

            await run_ffmpeg_with_progress_async(cmd, total_duration=duration, timeout=600.0)

            if not temp_target.exists() or temp_target.stat().st_size == 0:
                raise RuntimeError(f"WATERMARK_PROCESSING_FAILED: FFmpeg failed to produce watermarked file: {temp_target}")

            # Move successfully watermarked video to final output path
            if output_video_path.exists():
                output_video_path.unlink()
            shutil.move(str(temp_target), str(output_video_path))

            log_job_event(job_id, "APPLYING_WATERMARK", f"Watermark applied successfully to {output_video_path.name}")
            return output_video_path

        except Exception as ex:
            log_job_event(job_id, "APPLYING_WATERMARK", f"ERROR: Watermark rendering failed: {str(ex)}")
            raise RuntimeError(f"WATERMARK_PROCESSING_FAILED: {str(ex)}") from ex
        finally:
            # Guarantee cleanup of temporary working directory
            if temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as clean_err:
                    logger.warning(f"Failed to cleanup watermark temp dir {temp_dir}: {clean_err}")
