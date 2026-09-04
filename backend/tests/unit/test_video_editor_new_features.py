"""
Unit and Integration tests for Video Editor Automation, Subtitle ASS/SRT/VTT, AI QC, and YouTube Publishing.
"""

import pytest
from pathlib import Path
from app.services.video_editor.subtitle_service import SubtitleService, format_timestamp_ass
from app.services.video_editor.edit_service import build_watermark_filter, build_reframing_filter
from app.services.video_editor.qc_service import AIQCService
from app.services.video_editor.youtube_service import YouTubePublishingService
from app.database import init_db, async_session_factory
from app.models.video_editor import VideoEditConfig, QCReport, YouTubePublication


def test_format_timestamp_ass():
    assert format_timestamp_ass(0.0) == "0:00:00.00"
    assert format_timestamp_ass(65.45) == "0:01:05.45"


def test_subtitle_generators(tmp_path):
    segments = [
        {"start_time": 0.0, "end_time": 2.5, "translated_text": "Xin chào thế giới"},
        {"start_time": 3.0, "end_time": 5.0, "translated_text": "Hệ thống AI lồng tiếng v2"},
    ]
    
    srt_path = tmp_path / "sub.srt"
    SubtitleService.generate_srt(segments, srt_path)
    assert srt_path.exists()
    assert "Xin chào thế giới" in srt_path.read_text(encoding="utf-8")

    vtt_path = tmp_path / "sub.vtt"
    SubtitleService.generate_vtt(segments, vtt_path)
    assert vtt_path.exists()
    assert "WEBVTT" in vtt_path.read_text(encoding="utf-8")

    ass_path = tmp_path / "sub.ass"
    SubtitleService.generate_ass_animated(segments, ass_path)
    assert ass_path.exists()
    ass_content = ass_path.read_text(encoding="utf-8")
    assert "[Script Info]" in ass_content
    assert "Xin" in ass_content


def test_watermark_filter_builder():
    filter_top_right = build_watermark_filter(1920, 1080, logo_scale=0.15, position="top_right", opacity=0.85)
    assert "main_w-overlay_w" in filter_top_right
    assert "colorchannelmixer=aa=0.85" in filter_top_right

    filter_top_left = build_watermark_filter(1920, 1080, logo_scale=0.20, position="top_left", opacity=0.90)
    assert "overlay=20:20" in filter_top_left


def test_reframing_filter_builder():
    filter_9_16 = build_reframing_filter(1920, 1080, "9:16")
    assert "gblur=sigma=30" in filter_9_16 or "1080:1920" in filter_9_16

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
    assert report["qc_status"] in ["PASSED", "WARNING", "FAILED"]


@pytest.mark.asyncio
async def test_youtube_service_seo_and_publish(tmp_path):
    seo = await YouTubePublishingService.generate_youtube_seo_metadata(
        transcript_text="Hướng dẫn tự động hoá dựng video bằng Python và FFmpeg.",
        target_language="vi",
    )
    assert "title" in seo
    assert "description" in seo
    assert isinstance(seo.get("tags"), list)

    dummy_video = tmp_path / "dummy.mp4"
    dummy_video.write_bytes(b"DUMMY_VIDEO_BYTES")

    pub_res = await YouTubePublishingService.upload_to_youtube(
        video_path=dummy_video,
        title=seo["title"],
        description=seo["description"],
        tags=seo["tags"],
        privacy_status="private",
    )
    assert pub_res["success"] is True
    assert "youtube_url" in pub_res


@pytest.mark.asyncio
async def test_video_editor_orm_models_db():
    import uuid
    await init_db()
    edt_id = f"EDT-{uuid.uuid4().hex[:6]}"
    qc_id = f"QC-{uuid.uuid4().hex[:6]}"
    async with async_session_factory() as session:
        cfg = VideoEditConfig(
            id=edt_id,
            job_id="VT-TEST-001",
            target_aspect_ratio="9:16",
            logo_position="top_right",
        )
        qc = QCReport(
            id=qc_id,
            job_id="VT-TEST-001",
            overall_score=95.0,
            qc_status="PASSED",
        )
        session.add(cfg)
        session.add(qc)
        await session.commit()

        fetch_cfg = (await session.execute(
            VideoEditConfig.__table__.select().where(VideoEditConfig.id == edt_id)
        )).fetchone()
        assert fetch_cfg is not None
