import pytest
from app.api.routes.projects import normalize_project_settings, DEFAULT_PROJECT_SETTINGS

def test_default_project_settings_structure():
    normalized = normalize_project_settings({})
    assert normalized["watermark_enabled"] is False
    assert normalized["watermark_type"] == "image"
    assert normalized["watermark_position"] == "bottom_right"
    assert normalized["watermark_scale"] == 0.20
    assert normalized["watermark_opacity"] == 0.80
    assert normalized["watermark_margin"] == 20
    assert normalized["target_language"] == "vi"
    assert normalized["stt_model"] == "gemini-2.5-flash"


def test_normalize_project_settings_custom_values():
    raw = {
        "watermark_enabled": True,
        "watermark_type": "text",
        "watermark_text": "© Custom Watermark",
        "watermark_position": "TOP_LEFT",
        "watermark_scale": 30,  # 30% -> 0.30
        "watermark_opacity": 90,  # 90% -> 0.90
        "watermark_margin": 25,
        "target_language": "en",
        "stt_model": "gemini-2.5-flash",
    }
    normalized = normalize_project_settings(raw)
    assert normalized["watermark_enabled"] is True
    assert normalized["watermark_type"] == "text"
    assert normalized["watermark_text"] == "© Custom Watermark"
    assert normalized["watermark_position"] == "top_left"
    assert normalized["watermark_scale"] == 0.30
    assert normalized["watermark_opacity"] == 0.90
    assert normalized["watermark_margin"] == 25
    assert normalized["target_language"] == "en"


def test_normalize_project_settings_invalid_enum_fallback():
    raw = {
        "watermark_position": "invalid_position_string",
        "watermark_type": "invalid_type",
        "watermark_scale": 500,  # Extreme scale -> max clamp 1.0
        "watermark_opacity": -10, # Negative opacity -> min clamp 0.05
    }
    normalized = normalize_project_settings(raw)
    assert normalized["watermark_position"] == "bottom_right"
    assert normalized["watermark_type"] == "image"
    assert normalized["watermark_scale"] == 1.0
    assert normalized["watermark_opacity"] == 0.05
