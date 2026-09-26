"""The retired Gemini Live page must not expose an API or dedicated config."""

from app.config import Settings
from app.main import app


def test_live_translation_routes_and_config_are_removed():
    prefixes = {route.original_router.prefix for route in app.routes if hasattr(route, "original_router")}
    assert "/api/live-audio-translations" not in prefixes
    assert "GEMINI_LIVE_TRANSLATE_API_KEY" not in Settings.model_fields
    assert "GEMINI_LIVE_TRANSLATE_MODEL" not in Settings.model_fields
    assert "LIVE_AUDIO_TRANSLATION_ENABLED" not in Settings.model_fields


def test_studio_video_route_is_still_registered():
    prefixes = {route.original_router.prefix for route in app.routes if hasattr(route, "original_router")}
    assert "/api/video-translator" in prefixes
