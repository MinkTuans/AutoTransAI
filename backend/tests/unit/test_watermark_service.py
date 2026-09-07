"""
Unit tests for WatermarkService, filter construction, drawtext escaping, and parameter validation.
"""

import pytest
from pathlib import Path

from app.services.video_editor.watermark_service import (
    WatermarkService,
    WatermarkConfig,
    WatermarkType,
    WatermarkPosition,
    build_image_watermark_filter,
    build_text_watermark_filter,
    escape_ffmpeg_drawtext,
)


def test_escape_ffmpeg_drawtext():
    """Verify special character escaping for FFmpeg drawtext filter syntax."""
    raw_text = "Hello: World, 'Test' & 100% \"Awesome\" \\ [Code]"
    escaped = escape_ffmpeg_drawtext(raw_text)
    
    assert "\\:" in escaped
    assert "\\," in escaped
    assert "Test" in escaped
    assert "\\%" in escaped
    assert "\\[Code\\]" in escaped



def test_build_image_watermark_filter_positions():
    """Test image logo watermark filtergraph creation for all supported positions."""
    # Bottom Right (Default)
    filter_br, label_br = build_image_watermark_filter(
        video_w=1920, video_h=1080, position=WatermarkPosition.BOTTOM_RIGHT, scale=0.20, opacity=0.80, margin_px=25
    )
    assert "[1:v]scale=384:-1,format=rgba,colorchannelmixer=aa=0.80[logo]" in filter_br
    assert "overlay=main_w-overlay_w-25:main_h-overlay_h-25" in filter_br
    assert label_br == "[wm_outv]"

    # Top Left
    filter_tl, _ = build_image_watermark_filter(
        video_w=1080, video_h=1920, position=WatermarkPosition.TOP_LEFT, scale=0.15, opacity=0.90, margin_px=15
    )
    assert "[1:v]scale=162:-1,format=rgba,colorchannelmixer=aa=0.90[logo]" in filter_tl
    assert "overlay=15:15" in filter_tl

    # Center
    filter_c, _ = build_image_watermark_filter(
        video_w=1280, video_h=720, position=WatermarkPosition.CENTER, scale=0.30, opacity=0.50, margin_px=20
    )
    assert "overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2" in filter_c


def test_build_text_watermark_filter():
    """Test text watermark drawtext filter construction."""
    filter_text, label = build_text_watermark_filter(
        video_w=1920,
        video_h=1080,
        text="© AutoTransAI Studio",
        position=WatermarkPosition.BOTTOM_RIGHT,
        font_size=36,
        opacity=0.75,
        margin_px=30,
    )
    assert "drawtext=text='© AutoTransAI Studio':fontsize=36:fontcolor=white@0.75" in filter_text
    assert "x=w-tw-30:y=h-th-30" in filter_text
    assert label == "[wm_outv]"


def test_watermark_config_validation():
    """Verify validation rules for WatermarkConfig."""
    # Disabled config should be valid regardless of missing image
    disabled_cfg = WatermarkConfig(enabled=False, type=WatermarkType.IMAGE, image_path=None)
    disabled_cfg.validate_for_execution()

    # Image mode with missing path should raise FileNotFoundError or ValueError
    invalid_image_cfg = WatermarkConfig(enabled=True, type=WatermarkType.IMAGE, image_path="")
    with pytest.raises(ValueError, match="WATERMARK_LOGO_NOT_FOUND"):
        invalid_image_cfg.validate_for_execution()

    non_existent_image_cfg = WatermarkConfig(enabled=True, type=WatermarkType.IMAGE, image_path="non_existent_logo.png")
    with pytest.raises(FileNotFoundError, match="WATERMARK_LOGO_NOT_FOUND"):
        non_existent_image_cfg.validate_for_execution()

    # Text mode with empty text should raise ValueError
    empty_text_cfg = WatermarkConfig(enabled=True, type=WatermarkType.TEXT, text="   ")
    with pytest.raises(ValueError, match="INVALID_WATERMARK_TEXT"):
        empty_text_cfg.validate_for_execution()


@pytest.mark.asyncio
async def test_apply_watermark_disabled_passthrough(tmp_path):
    """Test that apply_watermark returns original video path when enabled=False."""
    dummy_video = tmp_path / "input_test.mp4"
    dummy_video.write_bytes(b"DUMMY_HEADER")

    cfg = WatermarkConfig(enabled=False)
    result_path = await WatermarkService.apply_watermark(
        input_video_path=dummy_video,
        output_video_path=tmp_path / "output_test.mp4",
        config=cfg,
    )

    assert result_path == dummy_video
