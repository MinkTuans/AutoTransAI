"""
Unit tests for Video Editor Automation Service, Subtitles, AI QC, YouTube SEO, and ORM models.
"""

import pytest
from pathlib import Path

from app.models.video_editor import WatermarkPositionEnum, AspectRatioEnum
from app.services.video_editor.edit_service import (
    build_watermark_filter,
    build_reframing_filter,
    VideoEditAutomationService,
)
from app.services.video_editor.subtitle_service import SubtitleService, format_timestamp_ass
from app.services.video_editor.qc_service import AIQCService
from app.services.video_editor.youtube_service import YouTubePublishingService


def test_format_timestamp_ass():
    assert format_timestamp_ass(0.0) == "0:00:00.00"
    assert format_timestamp_ass(65.25) == "0:01:05.25"
    assert format_timestamp_ass(3661.5) == "1:01:01.50"


def test_subtitle_generators(tmp_path):
    segments = [
        {"id": 1, "start_time": 0.0, "end_time": 3.5, "translated_text": "Xin chào thế giới!"},
        {"id": 2, "start_time": 4.0, "end_time": 7.2, "translated_text": "Đây là video thử nghiệm lồng tiếng."},
    ]
    srt_path = tmp_path / "subs.srt"
    SubtitleService.generate_srt(segments, srt_path)
    assert srt_path.exists()
    
    srt_content = srt_path.read_text(encoding="utf-8")
    assert "Xin chào thế giới!" in srt_content



def test_watermark_filter_builder():
    filter_top_right = build_watermark_filter(1920, 1080, logo_scale=0.15, position="top_right", opacity=0.85)
    assert "colorchannelmixer=aa=0.85" in filter_top_right or "format=rgba" in filter_top_right

    filter_top_left = build_watermark_filter(1920, 1080, logo_scale=0.20, position="top_left", opacity=0.90)
    assert "overlay=20:20" in filter_top_left or "overlay=20" in filter_top_left


def test_reframing_filter_builder():
    filter_9_16 = build_reframing_filter(1920, 1080, "9:16")
    assert "1080:1920" in filter_9_16

    filter_1_1 = build_reframing_filter(1920, 1080, "1:1")
    assert "1080:1080" in filter_1_1


@pytest.mark.asyncio
async def test_ai_qc_service_mock_run():
    report = await AIQCService.run_full_qc(
        output_video_path=Path("non_existent.mp4"),
        source_duration=10.0,
        transcript_text="Xin chào các bạn đến với video thử nghiệm.",
        job_id="VT-TEST-QC",
    )
    assert report["audio_lufs"] is not None
    assert "overall_score" in report


@pytest.mark.asyncio
async def test_youtube_service_seo_and_publish():
    meta = await YouTubePublishingService.generate_youtube_seo_metadata(
        transcript_text="Dịch thuật và lồng tiếng tự động cho video với AI Studio.",
        target_language="vi",
    )
    assert "title" in meta
    assert "description" in meta
