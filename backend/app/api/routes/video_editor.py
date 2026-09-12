"""
Video Editing Automation, AI Quality Control (AI QC), and YouTube Upload API Routes.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core import get_logger
from app.database import get_session, async_session_factory
from app.models.video_translator import VideoTranslationJob, VideoTranslationSegment
from app.models.video_editor import (
    VideoEditConfig,
    QCReport,
    YouTubeChannel,
    YouTubePublication,
    AspectRatioEnum,
    WatermarkPositionEnum,
    QCStatusEnum,
)
from app.services.video_editor.edit_service import VideoEditAutomationService
from app.services.video_editor.subtitle_service import SubtitleService
from app.services.video_editor.qc_service import AIQCService
from app.services.video_editor.youtube_service import YouTubePublishingService
from app.services.storage_service import storage_service

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/video-editor", tags=["Video Editor Automation"])


class SaveEditConfigRequest(BaseModel):
    job_id: str
    target_aspect_ratio: str = AspectRatioEnum.LANDSCAPE_16_9.value
    watermark_enabled: bool = False
    watermark_type: str = "image"
    watermark_text: Optional[str] = None
    logo_position: str = WatermarkPositionEnum.BOTTOM_RIGHT.value
    logo_scale: float = 0.20
    logo_opacity: float = 0.80
    watermark_margin: int = 20
    watermark_font_size: int = 32
    bgm_volume_db: float = -18.0
    enable_bgm_ducking: bool = True
    enable_burned_subtitles: bool = True


class PublishYouTubeRequest(BaseModel):
    job_id: str
    channel_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    privacy_status: str = "private"


@router.post("/config", response_model=dict)
async def save_video_edit_config(
    body: SaveEditConfigRequest,
    session: AsyncSession = Depends(get_session),
):
    """Save or update video editing automation settings for a job."""
    res = await session.execute(select(VideoEditConfig).where(VideoEditConfig.job_id == body.job_id))
    config = res.scalar_one_or_none()
    
    if not config:
        config = VideoEditConfig(
            id=str(uuid.uuid4())[:8],
            job_id=body.job_id,
        )
        session.add(config)

    config.target_aspect_ratio = body.target_aspect_ratio
    config.watermark_enabled = body.watermark_enabled
    config.watermark_type = body.watermark_type
    config.watermark_text = body.watermark_text
    config.logo_position = body.logo_position
    config.logo_scale = body.logo_scale
    config.logo_opacity = body.logo_opacity
    config.watermark_margin = body.watermark_margin
    config.watermark_font_size = body.watermark_font_size
    config.bgm_volume_db = body.bgm_volume_db
    config.enable_bgm_ducking = body.enable_bgm_ducking
    config.enable_burned_subtitles = body.enable_burned_subtitles
    
    await session.commit()
    return {"success": True, "data": {"config_id": config.id, "job_id": body.job_id}}



@router.post("/upload-logo", response_model=dict)
async def upload_logo_file(
    job_id: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    """Upload logo / watermark PNG image file for a job."""
    storage_dir = settings.DATA_DIR / "translator" / "jobs" / job_id / "branding"
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    logo_dest = storage_dir / f"logo_{file.filename}"
    with open(logo_dest, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    res = await session.execute(select(VideoEditConfig).where(VideoEditConfig.job_id == job_id))
    config = res.scalar_one_or_none()
    if not config:
        config = VideoEditConfig(id=str(uuid.uuid4())[:8], job_id=job_id)
        session.add(config)

    config.logo_path = str(logo_dest)
    await session.commit()

    return {"success": True, "data": {"logo_path": str(logo_dest), "filename": file.filename}}


@router.post("/jobs/{job_id}/run-qc", response_model=dict)
async def run_ai_qc_endpoint(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Run automated AI Quality Control (AI QC) Suite on rendered job video."""
    job_res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
    job = job_res.scalar_one_or_none()
    if not job or not job.output_video_path or not Path(job.output_video_path).exists():
        raise HTTPException(status_code=400, detail="❌ Video thành phẩm chưa được render hoặc không tồn tại.")

    seg_res = await session.execute(
        select(VideoTranslationSegment)
        .where(VideoTranslationSegment.job_id == job_id)
        .order_by(VideoTranslationSegment.segment_number)
    )
    segments = seg_res.scalars().all()
    transcript_text = " ".join([s.translated_text or s.original_text for s in segments])
    
    source_dur = float(segments[-1].end_time if segments else 0.0)
    video_path = Path(job.output_video_path)

    report_data = await AIQCService.run_full_qc(
        output_video_path=video_path,
        source_duration=source_dur,
        transcript_text=transcript_text,
        job_id=job_id,
    )

    # Save QCReport to database
    qc = QCReport(
        id=str(uuid.uuid4())[:8],
        job_id=job_id,
        audio_lufs=report_data["audio_lufs"],
        sync_drift_ms=report_data["sync_drift_ms"],
        has_black_frames=report_data["has_black_frames"],
        content_safety_score=report_data["content_safety_score"],
        translation_quality_score=report_data["translation_quality_score"],
        overall_score=report_data["overall_score"],
        qc_status=report_data["qc_status"],
        issues_json=json.dumps(report_data["issues"], ensure_ascii=False),
    )
    session.add(qc)
    await session.commit()

    return {"success": True, "data": report_data}


from sqlalchemy.orm import selectinload
from app.models.project import Project
from app.api.routes.projects import normalize_project_settings
from app.services.video_editor.youtube_service import (
    YouTubePublishingService,
    calculate_project_video_episode,
    render_title_template,
    merge_youtube_tags,
)


@router.get("/jobs/{job_id}/initial-youtube-metadata", response_model=dict)
async def get_initial_youtube_metadata_endpoint(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get initial YouTube metadata populated from Project Defaults + Title Template + Episode calculation.
    """
    job_res = await session.execute(
        select(VideoTranslationJob)
        .options(selectinload(VideoTranslationJob.asset))
        .where(VideoTranslationJob.id == job_id)
    )
    job = job_res.scalar_one_or_none()
    
    project_settings = None
    project_name = "Project"
    video_name = ""
    episode_num = 1
    
    if job:
        video_name = job.asset.title if job.asset and job.asset.title else f"Video {job.id}"
        if job.project_id:
            proj_res = await session.execute(select(Project).where(Project.id == job.project_id))
            proj = proj_res.scalar_one_or_none()
            if proj:
                project_name = proj.title or "Project"
                project_settings = normalize_project_settings(proj.settings_json or {})
            episode_num = await calculate_project_video_episode(session, job.project_id, job.id)
    else:
        from app.models.video_merger import VideoMergeJob
        mjob_res = await session.execute(select(VideoMergeJob).where(VideoMergeJob.id == job_id))
        mjob = mjob_res.scalar_one_or_none()
        if mjob:
            video_name = mjob.title or f"Video {mjob.id}"

    if not project_settings:
        project_settings = normalize_project_settings({})

    yt_enabled = project_settings.get("youtube_enabled", True)
    channel_name = project_settings.get("youtube_channel_name", "Xói Xám Content")
    title_template = project_settings.get("youtube_title_template", "Tập {episode} | {project_name} | {channel_name}")
    desc_default = project_settings.get("youtube_description_default", "")
    default_tags = project_settings.get("youtube_default_tags", "")

    rendered_title = render_title_template(
        template=title_template if yt_enabled else "{video_name}",
        episode_num=episode_num,
        project_name=project_name,
        channel_name=channel_name,
        video_name=video_name or f"Video {job_id}",
    )

    rendered_desc = render_title_template(
        template=desc_default,
        episode_num=episode_num,
        project_name=project_name,
        channel_name=channel_name,
        video_name=video_name or f"Video {job_id}",
    ) if desc_default else ""

    base_tags = merge_youtube_tags(default_tags if yt_enabled else [], [])

    return {
        "success": True,
        "data": {
            "title": rendered_title,
            "description": rendered_desc,
            "tags": base_tags,
            "episode": episode_num,
            "project_name": project_name,
            "channel_name": channel_name,
        }
    }


@router.post("/jobs/{job_id}/generate-seo", response_model=dict)
async def generate_youtube_seo_endpoint(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Auto-generate YouTube SEO Title, Description, Hashtags, Tags via Gemini + Project Defaults."""
    seg_res = await session.execute(
        select(VideoTranslationSegment)
        .where(VideoTranslationSegment.job_id == job_id)
        .order_by(VideoTranslationSegment.segment_number)
    )
    segments = seg_res.scalars().all()
    transcript_text = " ".join([s.translated_text or s.original_text for s in segments])

    job_res = await session.execute(
        select(VideoTranslationJob)
        .options(selectinload(VideoTranslationJob.asset))
        .where(VideoTranslationJob.id == job_id)
    )
    job = job_res.scalar_one_or_none()
    target_lang = job.target_language if job else "vi"

    project_settings = None
    project_name = "Project"
    video_name = ""
    episode_num = 1

    if job:
        video_name = job.asset.title if job.asset and job.asset.title else f"Video {job.id}"
        if job.project_id:
            proj_res = await session.execute(select(Project).where(Project.id == job.project_id))
            proj = proj_res.scalar_one_or_none()
            if proj:
                project_name = proj.title or "Project"
                project_settings = normalize_project_settings(proj.settings_json or {})
            episode_num = await calculate_project_video_episode(session, job.project_id, job.id)
    else:
        from app.models.video_merger import VideoMergeJob
        mjob_res = await session.execute(select(VideoMergeJob).where(VideoMergeJob.id == job_id))
        mjob = mjob_res.scalar_one_or_none()
        if mjob:
            video_name = mjob.title or f"Video {mjob.id}"
            if not transcript_text:
                transcript_text = f"Video ghép {mjob.title}"

    if not project_settings:
        project_settings = normalize_project_settings({})

    seo_data = await YouTubePublishingService.generate_youtube_seo_metadata(
        transcript_text=transcript_text,
        target_language=target_lang,
        job_id=job_id,
        project_settings=project_settings,
        project_name=project_name,
        video_name=video_name,
        episode_num=episode_num,
    )

    return {"success": True, "data": seo_data}


@router.post("/jobs/{job_id}/publish-youtube", response_model=dict)
async def publish_youtube_endpoint(
    body: PublishYouTubeRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Publish dubbed video to YouTube via YouTube Data API v3 with encrypted OAuth credential enforcement and real-time progress tracking."""
    video_path = None
    target_job_id = body.job_id
    project_id = "default_project"

    # 1. Check VideoTranslationJob
    job_res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == body.job_id))
    job = job_res.scalar_one_or_none()
    if job and job.output_video_path and Path(job.output_video_path).exists():
        video_path = str(job.output_video_path)
        project_id = job.project_id or "default_project"

    # 2. Check VideoMergeJob fallback
    if not video_path:
        from app.models.video_merger import VideoMergeJob
        mjob_res = await session.execute(select(VideoMergeJob).where(VideoMergeJob.id == body.job_id))
        mjob = mjob_res.scalar_one_or_none()
        if mjob and mjob.output_video_path and Path(mjob.output_video_path).exists():
            video_path = str(mjob.output_video_path)
            project_id = "merger_project"

    if not video_path:
        raise HTTPException(
            status_code=400,
            detail="❌ Video thành phẩm chưa ready để upload. (Lỗi: Video chưa được render hoàn tất hoặc không tìm thấy file thành phẩm trên hệ thống. Vui lòng kiểm tra lại tiến trình render/merge)."
        )

    # Fetch active YouTube OAuth channel from database
    channel_res = await session.execute(
        select(YouTubeChannel).where(YouTubeChannel.is_active == True)
    )
    active_channel = channel_res.scalars().first()

    credentials_json = None
    if active_channel and active_channel.credentials_json:
        try:
            from app.core.encryption import decrypt_data
            credentials_json = decrypt_data(active_channel.credentials_json)
        except Exception as dec_err:
            logger.error(f"Failed to decrypt credentials for YouTube channel {active_channel.id}", error=str(dec_err))

    if not credentials_json:
        raise HTTPException(
            status_code=400,
            detail="❌ Chưa kết nối kênh YouTube! Vui lòng truy cập Cài Đặt -> Social Accounts -> bấm Connect Social Account để liên kết tài khoản Google trước khi xuất bản video."
        )

    title = body.title or "Video lồng tiếng AI"
    description = body.description or "Video lồng tiếng AI WorkflowVdAi"
    tags = body.tags or ["AI", "VideoDubbing"]

    import json
    from app.models.video_editor import YouTubePublication, PublishStatusEnum

    pub = YouTubePublication(
        id=str(uuid.uuid4()),
        job_id=target_job_id,
        project_id=project_id,
        channel_id=active_channel.id,
        title=title,
        description=description,
        tags_json=json.dumps(tags),
        category_id="22",
        privacy_status=body.privacy_status,
        status=PublishStatusEnum.PENDING.value,
        progress=0,
    )
    session.add(pub)
    await session.commit()
    await session.refresh(pub)

    background_tasks.add_task(
        YouTubePublishingService.execute_async_upload,
        publication_id=pub.id,
        video_path=video_path,
    )

    return {
        "success": True,
        "data": {
            "publication_id": pub.id,
            "status": "PENDING",
            "progress": 0,
        }
    }
