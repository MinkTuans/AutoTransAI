"""
Subtitle Service — ASS, SRT, and VTT subtitle generator with dynamic CapCut/TikTok active word animations.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.core import get_logger

logger = get_logger(__name__)


def format_timestamp_srt(seconds: float) -> str:
    """Format seconds into SRT timestamp format: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """Format seconds into VTT timestamp format: HH:MM:SS.mmm"""
    return format_timestamp_srt(seconds).replace(",", ".")


def format_timestamp_ass(seconds: float) -> str:
    """Format seconds into ASS timestamp format: H:MM:SS.cs (centiseconds)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


class SubtitleService:
    """Service for generating SRT, VTT, and ASS dynamic animated subtitles."""

    @staticmethod
    def generate_srt(segments: List[Dict[str, Any]], output_path: Path) -> Path:
        """Generate standard SRT subtitle file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        
        for idx, seg in enumerate(segments, start=1):
            st = float(seg.get("start_time", 0.0))
            et = float(seg.get("end_time", st + 1.0))
            text = str(seg.get("translated_text") or seg.get("text") or "").strip()
            if not text:
                continue
            
            lines.append(str(idx))
            lines.append(f"{format_timestamp_srt(st)} --> {format_timestamp_srt(et)}")
            lines.append(text)
            lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Generated SRT subtitle file", path=str(output_path), count=len(segments))
        return output_path

    @staticmethod
    def generate_vtt(segments: List[Dict[str, Any]], output_path: Path) -> Path:
        """Generate WebVTT subtitle file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        lines = ["WEBVTT", ""]
        
        for idx, seg in enumerate(segments, start=1):
            st = float(seg.get("start_time", 0.0))
            et = float(seg.get("end_time", st + 1.0))
            text = str(seg.get("translated_text") or seg.get("text") or "").strip()
            if not text:
                continue
            
            lines.append(str(idx))
            lines.append(f"{format_timestamp_vtt(st)} --> {format_timestamp_vtt(et)}")
            lines.append(text)
            lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Generated VTT subtitle file", path=str(output_path), count=len(segments))
        return output_path

    @staticmethod
    def generate_ass_animated(
        segments: List[Dict[str, Any]],
        output_path: Path,
        font_name: str = "Arial",
        font_size: int = 24,
        primary_color: str = "&H00FFFFFF",  # White
        highlight_color: str = "&H0000FFFF",  # Yellow
        outline_color: str = "&H00000000",   # Black
        alignment: int = 2,  # Bottom Center
    ) -> Path:
        """
        Generate ASS (Advanced SubStation Alpha) subtitle file with word-by-word active highlight pop-up effect.
        CapCut / TikTok style.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_color},&H000000FF,{outline_color},&H80000000,1,0,0,0,100,100,0,0,1,2,1,{alignment},20,20,40,1
Style: Highlight,{font_name},{int(font_size * 1.1)},{highlight_color},&H000000FF,{outline_color},&H80000000,1,0,0,0,105,105,0,0,1,3,2,{alignment},20,20,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        for seg in segments:
            st = float(seg.get("start_time", 0.0))
            et = float(seg.get("end_time", st + 1.0))
            text = str(seg.get("translated_text") or seg.get("text") or "").strip()
            if not text:
                continue

            words = text.split()
            if not words:
                continue

            duration = max(0.5, et - st)
            word_dur = duration / len(words)

            # Generate word-by-word highlight timeline
            for w_idx, word in enumerate(words):
                w_st = st + (w_idx * word_dur)
                w_et = min(et, w_st + word_dur)

                # Format sentence text with active word highlighted in ASS tags
                formatted_words = []
                for i, w in enumerate(words):
                    if i == w_idx:
                        # Highlight active word with primary highlight color & scale pop
                        formatted_words.append(f"{{\\c{highlight_color}\\fscx110\\fscy110}}{w}{{\\r}}")
                    else:
                        formatted_words.append(w)
                
                ass_text = " ".join(formatted_words)
                events.append(
                    f"Dialogue: 0,{format_timestamp_ass(w_st)},{format_timestamp_ass(w_et)},Default,,0,0,0,,{ass_text}"
                )

        full_content = header + "\n".join(events) + "\n"
        output_path.write_text(full_content, encoding="utf-8")
        logger.info("Generated ASS animated subtitle file", path=str(output_path), count=len(events))
        return output_path
