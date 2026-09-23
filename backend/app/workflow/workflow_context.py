"""Workflow context data object shared across workflow stages and steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


_SEGMENT_FIELDS = frozenset({
    "id", "index", "number", "segment_number", "start", "end", "start_time",
    "end_time", "text", "original_text", "translated_text", "speaker",
    "speaker_id", "speaker_name", "character_id", "gender", "role",
})
_SPEAKER_FIELDS = frozenset({"speaker_id", "speaker_name", "gender", "role"})
_GLOSSARY_FIELDS = frozenset({"source_term", "translated_term", "term_type", "approved", "priority"})
_AUDIO_FIELDS = frozenset({
    "id", "segment_number", "start_time", "end_time", "tts_audio_path",
    "tts_audio_duration", "tts_duration", "speaker_id", "synced_audio_path",
    "voice_provider", "catalog_model_id", "model_id", "key_id", "voice_id",
    "translated_text", "route_default_model_id",
})


def _records(value: Any, field_name: str, allowed: frozenset[str]) -> list[dict[str, Any]]:
    """Bound checkpoint lists and retain only downstream, non-credential fields."""
    if not isinstance(value, list) or len(value) > 10000 or any(not isinstance(row, dict) for row in value):
        raise ValueError(f"Invalid workflow checkpoint: {field_name}.")
    result = []
    for row in value:
        kept = {key: item for key, item in row.items() if key in allowed}
        if any(item is not None and (
            not isinstance(item, (str, int, float, bool)) or
            isinstance(item, str) and len(item) > 65536
        ) for item in kept.values()):
            raise ValueError(f"Invalid workflow checkpoint: {field_name}.")
        result.append(kept)
    return result


def _transcript(value: Any) -> str | None:
    if value is not None and (not isinstance(value, str) or len(value) > 2_000_000):
        raise ValueError("Invalid workflow checkpoint: raw_transcript.")
    return value


def _voice_map(value: Any) -> dict[str, dict[str, Any]]:
    if (not isinstance(value, dict) or len(value) > 1000 or
            any(not isinstance(key, str) or not isinstance(row, dict) for key, row in value.items())):
        raise ValueError("Invalid workflow checkpoint: speaker_voice_map.")
    result = {key: {field: row[field] for field in ("provider", "voice_id", "gender", "confirmed_by_user") if field in row}
              for key, row in value.items()}
    if any(len(key) > 255 or any(
        (not isinstance(item, bool) if field == "confirmed_by_user" else
         not isinstance(item, str) or len(item) > 512)
        for field, item in row.items()) for key, row in result.items()):
        raise ValueError("Invalid workflow checkpoint: speaker_voice_map.")
    return result


@dataclass
class WorkflowContext:
    """Holds runtime metadata and lightweight resource references across stage steps."""

    project_id: str
    job_id: Optional[str] = None
    workflow_id: Optional[str] = None
    
    # Progress callback for unified SSE
    progress_callback: Optional[Any] = None

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
    tts_provider_id: Optional[str] = None
    tts_voice_id: str = "vi-VN-HoaiMyNeural"
    dubbed_audio_path: Optional[str] = None
    audio_segments_info: list[dict[str, Any]] = field(default_factory=list)
    character_voice_requires_review: bool = False
    character_voice_issues: list[dict[str, Any]] = field(default_factory=list)

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
    thumbnail_enabled: bool = False
    thumbnail_provider: str = "pollinations"
    thumbnail_style: str = "auto"
    thumbnail_custom_instruction: Optional[str] = None
    thumbnail_url: Optional[str] = None
    thumbnail_source: str = "ai"
    thumbnail_library_path: Optional[str] = None
    trim_filler_enabled: bool = True
    copyright_check_enabled: bool = True
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
            "raw_transcript": _transcript(self.raw_transcript),
            "source_segments": _records(self.source_segments, "source_segments", _SEGMENT_FIELDS),
            "speakers": _records(self.speakers, "speakers", _SPEAKER_FIELDS),
            "glossary": _records(self.glossary, "glossary", _GLOSSARY_FIELDS),
            "translated_segments": _records(self.translated_segments, "translated_segments", _SEGMENT_FIELDS),
            "speaker_voice_map": _voice_map(self.speaker_voice_map),
            "tts_provider_id": self.tts_provider_id,
            "tts_voice_id": self.tts_voice_id,
            "audio_segments_info": _records(self.audio_segments_info, "audio_segments_info", _AUDIO_FIELDS),
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
            "thumbnail_enabled": self.thumbnail_enabled,
            "thumbnail_provider": self.thumbnail_provider,
            "thumbnail_style": self.thumbnail_style,
            "thumbnail_custom_instruction": self.thumbnail_custom_instruction,
            "thumbnail_url": self.thumbnail_url,
            "thumbnail_source": self.thumbnail_source,
            "thumbnail_library_path": self.thumbnail_library_path,
            "trim_filler_enabled": self.trim_filler_enabled,
            "copyright_check_enabled": self.copyright_check_enabled,
            "settings_snapshot": self.settings_snapshot,
            "trim_filler": (self.video_metadata or {}).get("trim_applied"),
            "qc_reports": self.qc_reports,
            "seo_metadata": self.seo_metadata,
            "publication_status": self.publication_status,
            "publication_record": self.publication_record,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowContext:
        """Hydrate WorkflowContext from serialized dictionary."""
        if not isinstance(data, dict):
            raise ValueError("Invalid workflow checkpoint.")
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
        ctx.raw_transcript = _transcript(data.get("raw_transcript"))
        ctx.source_segments = _records(data.get("source_segments", []), "source_segments", _SEGMENT_FIELDS)
        ctx.speakers = _records(data.get("speakers", []), "speakers", _SPEAKER_FIELDS)
        ctx.glossary = _records(data.get("glossary", []), "glossary", _GLOSSARY_FIELDS)
        ctx.translated_segments = _records(data.get("translated_segments", []), "translated_segments", _SEGMENT_FIELDS)
        ctx.speaker_voice_map = _voice_map(data.get("speaker_voice_map", {}))
        ctx.tts_provider_id = data.get("tts_provider_id")
        ctx.tts_voice_id = data.get("tts_voice_id") or ctx.tts_voice_id
        ctx.audio_segments_info = _records(data.get("audio_segments_info", []), "audio_segments_info", _AUDIO_FIELDS)
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

        th_enabled_raw = data.get("thumbnail_enabled") if "thumbnail_enabled" in data else snapshot.get("thumbnail_enabled")
        if isinstance(th_enabled_raw, str):
            ctx.thumbnail_enabled = th_enabled_raw.strip().lower() in ("true", "1", "yes", "on")
        else:
            ctx.thumbnail_enabled = bool(th_enabled_raw) if th_enabled_raw is not None else False
        ctx.thumbnail_provider = data.get("thumbnail_provider") or snapshot.get("thumbnail_provider", "pollinations")
        ctx.thumbnail_style = data.get("thumbnail_style") or snapshot.get("thumbnail_style", "auto")
        ctx.thumbnail_custom_instruction = (
            data.get("thumbnail_custom_instruction")
            or snapshot.get("thumbnail_custom_instruction")
        )
        ctx.thumbnail_url = data.get("thumbnail_url")
        ctx.thumbnail_source = data.get("thumbnail_source") or snapshot.get("thumbnail_source") or "ai"
        ctx.thumbnail_library_path = data.get("thumbnail_library_path") or snapshot.get("thumbnail_library_path")

        trim_raw = data.get("trim_filler_enabled") if "trim_filler_enabled" in data else snapshot.get("trim_filler_enabled")
        if isinstance(trim_raw, str):
            ctx.trim_filler_enabled = trim_raw.strip().lower() in ("true", "1", "yes", "on")
        elif trim_raw is None:
            ctx.trim_filler_enabled = True
        else:
            ctx.trim_filler_enabled = bool(trim_raw)

        cc_raw = data.get("copyright_check_enabled") if "copyright_check_enabled" in data else snapshot.get("copyright_check_enabled")
        if isinstance(cc_raw, str):
            ctx.copyright_check_enabled = cc_raw.strip().lower() in ("true", "1", "yes", "on")
        elif cc_raw is None:
            ctx.copyright_check_enabled = True
        else:
            ctx.copyright_check_enabled = bool(cc_raw)

        ctx.qc_reports = data.get("qc_reports", {})
        ctx.seo_metadata = data.get("seo_metadata", {})
        ctx.publication_status = data.get("publication_status")
        ctx.publication_record = data.get("publication_record", {})
        return ctx
