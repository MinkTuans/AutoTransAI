"""Workflow context data object shared across workflow stages and steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class WorkflowContext:
    """Holds runtime metadata and lightweight resource references across stage steps."""

    project_id: str
    job_id: Optional[str] = None
    workflow_id: Optional[str] = None

    # Source asset info
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    video_url: Optional[str] = None
    duration: float = 0.0
    resolution: Optional[str] = None
    fps: float = 0.0
    video_metadata: dict[str, Any] = field(default_factory=dict)

    # Languages
    source_language: str = "auto"
    target_language: str = "vi"

    # Transcript & Segments
    raw_transcript: Optional[str] = None
    source_segments: list[dict[str, Any]] = field(default_factory=list)
    speakers: list[dict[str, Any]] = field(default_factory=list)

    # Translation & Glossary
    glossary: list[dict[str, Any]] = field(default_factory=list)
    translated_segments: list[dict[str, Any]] = field(default_factory=list)

    # Dubbing & Voice Mapping
    speaker_voice_map: dict[str, dict[str, Any]] = field(default_factory=dict)
    tts_voice_id: str = "vi-VN-HoaiMyNeural"
    dubbed_audio_path: Optional[str] = None
    audio_segments_info: list[dict[str, Any]] = field(default_factory=list)

    # Production & Watermark
    subtitle_files: dict[str, str] = field(default_factory=dict)  # srt, ass, vtt paths
    final_video_path: Optional[str] = None
    r2_key: Optional[str] = None

    watermark_enabled: bool = False
    watermark_type: str = "image"
    watermark_image_path: Optional[str] = None
    watermark_image_asset_id: Optional[str] = None
    watermark_text: Optional[str] = "© AutoTransAI Studio"
    watermark_position: str = "bottom_right"
    watermark_scale: float = 0.20
    watermark_opacity: float = 0.80
    watermark_margin: int = 20
    watermark_font_size: int = 32
    settings_snapshot: dict[str, Any] = field(default_factory=dict)

    # QC Reports per stage
    qc_reports: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Publication data
    seo_metadata: dict[str, Any] = field(default_factory=dict)
    publication_status: Optional[str] = None
    publication_record: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize context data to a DB-storable dictionary (excluding heavy binaries)."""
        return {
            "project_id": self.project_id,
            "job_id": self.job_id,
            "workflow_id": self.workflow_id,
            "video_path": self.video_path,
            "audio_path": self.audio_path,
            "video_url": self.video_url,
            "duration": self.duration,
            "resolution": self.resolution,
            "fps": self.fps,
            "video_metadata": self.video_metadata,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "segment_count": len(self.source_segments),
            "translated_segment_count": len(self.translated_segments),
            "glossary_count": len(self.glossary),
            "dubbed_audio_path": self.dubbed_audio_path,
            "subtitle_files": self.subtitle_files,
            "final_video_path": self.final_video_path,
            "r2_key": self.r2_key,
            "watermark_enabled": self.watermark_enabled,
            "watermark_type": self.watermark_type,
            "watermark_image_path": self.watermark_image_path,
            "watermark_image_asset_id": self.watermark_image_asset_id,
            "watermark_text": self.watermark_text,
            "watermark_position": self.watermark_position,
            "watermark_scale": self.watermark_scale,
            "watermark_opacity": self.watermark_opacity,
            "watermark_margin": self.watermark_margin,
            "watermark_font_size": self.watermark_font_size,
            "settings_snapshot": self.settings_snapshot,
            "qc_reports": self.qc_reports,
            "seo_metadata": self.seo_metadata,
            "publication_status": self.publication_status,
            "publication_record": self.publication_record,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowContext:
        """Hydrate WorkflowContext from serialized dictionary."""
        ctx = cls(project_id=data.get("project_id", ""))
        ctx.job_id = data.get("job_id")
        ctx.workflow_id = data.get("workflow_id")
        ctx.video_path = data.get("video_path")
        ctx.audio_path = data.get("audio_path")
        ctx.video_url = data.get("video_url")
        ctx.duration = data.get("duration", 0.0)
        ctx.resolution = data.get("resolution")
        ctx.fps = data.get("fps", 0.0)
        ctx.video_metadata = data.get("video_metadata", {})
        ctx.source_language = data.get("source_language", "auto")
        ctx.target_language = data.get("target_language", "vi")
        ctx.dubbed_audio_path = data.get("dubbed_audio_path")
        ctx.subtitle_files = data.get("subtitle_files", {})
        ctx.final_video_path = data.get("final_video_path")
        ctx.r2_key = data.get("r2_key")

        # Hydrate settings snapshot if present
        ctx.settings_snapshot = data.get("settings_snapshot", {})

        # Hydrate watermark options with fallbacks to settings_snapshot
        snapshot = ctx.settings_snapshot or {}
        wm_enabled_raw = data.get("watermark_enabled") if "watermark_enabled" in data else snapshot.get("watermark_enabled")
        if isinstance(wm_enabled_raw, str):
            ctx.watermark_enabled = wm_enabled_raw.strip().lower() in ("true", "1", "yes", "on")
        else:
            ctx.watermark_enabled = bool(wm_enabled_raw) if wm_enabled_raw is not None else False

        ctx.watermark_type = data.get("watermark_type") or snapshot.get("watermark_type", "image")
        ctx.watermark_image_path = data.get("watermark_image_path") or snapshot.get("watermark_image_path")
        ctx.watermark_image_asset_id = data.get("watermark_image_asset_id") or snapshot.get("watermark_image_asset_id")
        ctx.watermark_text = data.get("watermark_text") or snapshot.get("watermark_text", "© AutoTransAI Studio")
        ctx.watermark_position = data.get("watermark_position") or snapshot.get("watermark_position", "bottom_right")
        ctx.watermark_scale = float(data.get("watermark_scale") or snapshot.get("watermark_scale", 0.20))
        ctx.watermark_opacity = float(data.get("watermark_opacity") or snapshot.get("watermark_opacity", 0.80))
        ctx.watermark_margin = int(data.get("watermark_margin") or snapshot.get("watermark_margin", 20))
        ctx.watermark_font_size = int(data.get("watermark_font_size") or snapshot.get("watermark_font_size", 32))

        ctx.qc_reports = data.get("qc_reports", {})
        ctx.seo_metadata = data.get("seo_metadata", {})
        ctx.publication_status = data.get("publication_status")
        ctx.publication_record = data.get("publication_record", {})
        return ctx
