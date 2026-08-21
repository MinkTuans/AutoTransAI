"""Video Translator Service package."""

from app.services.video_translator.translator_service import (
    extract_audio_from_video,
    speech_to_text_and_detect_language,
    translate_transcript_segments,
    sync_and_stretch_audio,
    render_dubbed_video,
)

__all__ = [
    "extract_audio_from_video",
    "speech_to_text_and_detect_language",
    "translate_transcript_segments",
    "sync_and_stretch_audio",
    "render_dubbed_video",
]
