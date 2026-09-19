"""
Video Translator API Routes.

Endpoints for checking video URLs, importing video assets, managing translation jobs,
monitoring real-time FFmpeg process stats & heartbeats, reviewing logs, cancel, and smart retry.
"""

from __future__ import annotations

import asyncio
import copy
import json
import os
import shutil
import signal
import sys
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse
import asyncio
from app.workflow.event_broker import workflow_events

from app.config import get_settings
from app.core import get_logger
from app.services.storage_service import storage_service
from app.core.job_logger import log_job_event, get_job_logs
from app.database import get_session, async_session_factory
from app.core.security_url import SSRFValidationError
from app.models.asset import Asset
from app.models.project import Project, WorkflowStatus
from app.models.video_translator import (
    VideoAsset,
    VideoTranslationJob,
    VideoTranslationSegment,
    AssetSourceType,
    TranslationJobStatus,
    AudioMixMode,
)
from app.services.video_editor.watermark_service import (
    WatermarkService,
    WatermarkConfig,
    WatermarkType,
    WatermarkPosition,
)

from app.providers.registry import get_registry
from app.services.video_source import get_video_source_service
from app.services.video_source.transfer_progress import (
    apply_yt_dlp_progress,
    create_transfer,
    get_transfer,
    update_transfer,
)
from app.services.video_translator import (
    extract_audio_from_video,
    speech_to_text_and_detect_language,
    translate_transcript_segments,
    sync_and_stretch_audio,
    render_dubbed_video,
)
from app.services.video_translator.translator_service import calculate_overall_progress
from app.services.video_translator.heartbeat import start_job_heartbeat, stop_job_heartbeat, check_and_mark_stalled_jobs
from app.media.ffprobe import probe_duration_async, get_video_metadata_async
from app.media.ffmpeg_process import FFmpegExecutionError

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/video-translator", tags=["video-translator"])

_job_sse_queues: Dict[str, asyncio.Queue] = {}
_job_cancellation_events: Dict[str, asyncio.Event] = {}
_active_render_jobs: set[str] = set()



def get_job_cancellation_event(job_id: str) -> asyncio.Event:
    if job_id not in _job_cancellation_events:
        _job_cancellation_events[job_id] = asyncio.Event()
    return _job_cancellation_events[job_id]


def signal_job_cancellation(job_id: str):
    if job_id in _job_cancellation_events:
        _job_cancellation_events[job_id].set()


def reset_job_cancellation(job_id: str) -> asyncio.Event:
    event = asyncio.Event()
    _job_cancellation_events[job_id] = event
    return event


def is_job_cancelled(job_id: str) -> bool:
    if job_id in _job_cancellation_events:
        return _job_cancellation_events[job_id].is_set()
    return False


def _parse_bool(val: Any, default: bool = False) -> bool:
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        cleaned = val.strip().lower()
        if cleaned in ("true", "1", "yes", "on"):
            return True
        if cleaned in ("false", "0", "no", "off"):
            return False
    return bool(val)


async def _emit_job_progress(job_id: str, data: dict):
    if job_id in _job_sse_queues:
        try:
            await _job_sse_queues[job_id].put(data)
        except Exception:
            pass


# ── Schemas ──────────────────────────────────────────────────────────

class CheckURLRequest(BaseModel):
    url: str = Field(..., description="Video URL to inspect")


class CreateJobRequest(BaseModel):
    project_id: Optional[str] = Field(None, description="Project ID to link job")
    asset_id: str
    source_language: str = "auto"
    target_language: str = "vi"
    audio_provider_id: str = "edge_tts"
    llm_provider_id: str = "gemini"
    voice_id: Optional[str] = None
    default_male_voice_id: Optional[str] = None
    default_female_voice_id: Optional[str] = None
    original_audio_mode: str = "mute"
    auto_confirm_translation: bool = True
    auto_confirm_voice: bool = False
    trim_filler_enabled: bool = True
    copyright_check_enabled: bool = True
    thumbnail_enabled: bool = False
    thumbnail_provider: str = "pollinations"
    thumbnail_style: str = "auto"
    thumbnail_custom_instruction: Optional[str] = None
    thumbnail_source: str = "ai"
    thumbnail_library_path: Optional[str] = None

    # Watermark Settings
    watermark_enabled: bool = False
    watermark_type: str = "image"
    watermark_image_path: Optional[str] = None
    watermark_text: Optional[str] = None
    watermark_position: str = "bottom_right"
    watermark_scale: float = 0.20
    watermark_opacity: float = 0.80
    watermark_margin: int = 20
    watermark_font_size: int = 32


class SegmentUpdateItem(BaseModel):
    id: int
    translated_text: str


class UpdateSegmentsRequest(BaseModel):
    segments: List[SegmentUpdateItem]


class UpdateStudioStateRequest(BaseModel):
    active_step: Optional[str] = None
    active_tab: Optional[str] = None
    selected_segment_id: Optional[int] = None
    extra_state: Optional[Dict[str, Any]] = None


class SaveCheckpointRequest(BaseModel):
    checkpoint_stage: str
    studio_state: Optional[Dict[str, Any]] = None


_active_job_locks: Dict[str, asyncio.Lock] = {}


def get_job_lock(job_id: str) -> asyncio.Lock:
    if job_id not in _active_job_locks:
        _active_job_locks[job_id] = asyncio.Lock()
    return _active_job_locks[job_id]


# ── Endpoints ────────────────────────────────────────────────────────

@router.post("/check-url", response_model=dict)
async def check_video_url(body: CheckURLRequest):
    """Validate Video URL and return metadata."""
    service = get_video_source_service()
    try:
        metadata = await service.get_metadata(body.url)
        return {"success": True, "data": metadata}
    except SSRFValidationError as e:
        raise HTTPException(status_code=400, detail=f"❌ {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"❌ {str(e)}")
    except Exception as e:
        logger.error("URL check failed", url=body.url, error=str(e))
        raise HTTPException(status_code=400, detail=f"❌ Không thể truy cập nguồn video: {str(e)}")


@router.post("/import", response_model=dict)
async def import_video_asset(
    source_type: str = Form("url"),
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session),
):
    """Import video asset from Video URL or File Upload."""
    service = get_video_source_service()
    asset_id = str(uuid.uuid4())[:8]
    storage_dir = settings.STORAGE_ROOT / "translator" / "assets" / asset_id
    storage_dir.mkdir(parents=True, exist_ok=True)

    if source_type == "upload":
        if not file:
            raise HTTPException(status_code=400, detail="❌ Không tìm thấy file video upload.")
        temp_upload_path = storage_dir / f"raw_input_{asset_id}.mp4"
        with open(temp_upload_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)

        try:
            meta = await service.import_uploaded_file(temp_upload_path, file.filename or "video.mp4", storage_dir)
            if temp_upload_path.exists() and Path(meta["local_path"]) != temp_upload_path:
                temp_upload_path.unlink(missing_ok=True)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"❌ Lỗi file upload: {str(e)}")

        asset = VideoAsset(
            id=asset_id,
            source_type=AssetSourceType.UPLOAD.value,
            source_url=None,
            source_domain="local",
            title=meta["title"],
            original_filename=file.filename,
            file_path=meta["local_path"],
            mime_type=meta.get("mime_type", "video/mp4"),
            file_size=meta["file_size"],
            duration=meta["duration"],
            width=meta["width"],
            height=meta["height"],
            audio_available=meta["audio_available"],
            status="ready",
        )
    else:
        if not url:
            raise HTTPException(status_code=400, detail="❌ Vui lòng nhập Video URL.")
        try:
            meta = await service.download_video(url, storage_dir)
        except Exception as e:
            msg = str(e).strip()
            stderr = getattr(e, "stderr", None)
            if not msg and stderr:
                msg = str(stderr)[:300].strip()
            if not msg:
                msg = e.__class__.__name__
            raise HTTPException(status_code=400, detail=f"❌ {msg}")

        asset = VideoAsset(
            id=asset_id,
            source_type=AssetSourceType.URL.value,
            source_url=url,
            source_domain=meta.get("domain", "web"),
            title=meta["title"],
            original_filename=Path(meta["local_path"]).name,
            file_path=meta["local_path"],
            mime_type=meta.get("mime_type", "video/mp4"),
            file_size=meta["file_size"],
            duration=meta["duration"],
            width=meta["width"],
            height=meta["height"],
            audio_available=meta["audio_available"],
            status="ready",
        )

    # Upload asset file to R2 Storage Service
    try:
        asset_local_file = Path(meta["local_path"])
        r2_asset_key = f"translator/assets/{asset_id}/{asset_local_file.name}"
        obj_key, asset_url = await storage_service.upload_file(
            asset_local_file,
            r2_asset_key,
            content_type=meta.get("mime_type", "video/mp4")
        )
        asset.r2_key = obj_key
        asset.url = asset_url
    except Exception as store_err:
        logger.warning("Error storing asset in R2", error=str(store_err), asset_id=asset_id)

    session.add(asset)
    await session.commit()

    return {
        "success": True,
        "data": {
            "asset_id": asset.id,
            "title": asset.title,
            "source_type": asset.source_type,
            "source_domain": asset.source_domain,
            "duration": asset.duration,
            "width": asset.width,
            "height": asset.height,
            "file_size": asset.file_size,
            "audio_available": asset.audio_available,
            "file_path": asset.file_path,
        },
    }


async def _run_url_transfer(transfer_id: str, url: str) -> None:
    """Background URL download so the UI can poll percent/bytes/speed."""
    update_transfer(transfer_id, status="running", message="Đang tải xuống video...")
    service = get_video_source_service()
    asset_id = str(uuid.uuid4())[:8]
    storage_dir = settings.STORAGE_ROOT / "translator" / "assets" / asset_id
    storage_dir.mkdir(parents=True, exist_ok=True)

    def _on_progress(info):
        apply_yt_dlp_progress(transfer_id, info)
        rec = get_transfer(transfer_id) or {}
        pct = rec.get("percent") or 0
        update_transfer(
            transfer_id,
            message=f"Đang tải xuống {pct:.0f}% ({rec.get('speed') or '…'})",
        )

    try:
        meta = await service.download_video(url, storage_dir, progress_callback=_on_progress)
        update_transfer(transfer_id, percent=100, message="Đang lưu file...")
        asset = VideoAsset(
            id=asset_id,
            source_type=AssetSourceType.URL.value,
            source_url=url,
            source_domain=meta.get("domain", "web"),
            title=meta["title"],
            original_filename=Path(meta["local_path"]).name,
            file_path=meta["local_path"],
            mime_type=meta.get("mime_type", "video/mp4"),
            file_size=meta["file_size"],
            duration=meta["duration"],
            width=meta["width"],
            height=meta["height"],
            audio_available=meta["audio_available"],
            status="ready",
        )
        try:
            asset_local_file = Path(meta["local_path"])
            r2_asset_key = f"translator/assets/{asset_id}/{asset_local_file.name}"
            obj_key, asset_url = await storage_service.upload_file(
                asset_local_file,
                r2_asset_key,
                content_type=meta.get("mime_type", "video/mp4"),
            )
            asset.r2_key = obj_key
            asset.url = asset_url
        except Exception as store_err:
            logger.warning("Error storing asset in R2", error=str(store_err), asset_id=asset_id)

        async with async_session_factory() as session:
            session.add(asset)
            await session.commit()

        payload = {
            "asset_id": asset.id,
            "title": asset.title,
            "source_type": asset.source_type,
            "source_domain": asset.source_domain,
            "duration": asset.duration,
            "width": asset.width,
            "height": asset.height,
            "file_size": asset.file_size,
            "audio_available": asset.audio_available,
            "file_path": asset.file_path,
        }
        update_transfer(
            transfer_id,
            status="done",
            percent=100,
            message="Tải xong",
            asset=payload,
        )
    except Exception as e:
        msg = str(e).strip() or e.__class__.__name__
        update_transfer(transfer_id, status="failed", error=msg, message=msg)


@router.post("/transfers", response_model=dict)
async def start_media_transfer(
    source_type: str = Form("url"),
    url: Optional[str] = Form(None),
):
    """Start an async URL download and return a transfer_id for progress polling."""
    if source_type != "url":
        raise HTTPException(
            status_code=400,
            detail="❌ Upload file dùng progress phía trình duyệt. URL thì gọi /transfers.",
        )
    if not url:
        raise HTTPException(status_code=400, detail="❌ Vui lòng nhập Video URL.")
    transfer_id = create_transfer("download", "Đang khởi tạo tải xuống...")
    asyncio.create_task(_run_url_transfer(transfer_id, url))
    return {"success": True, "data": get_transfer(transfer_id)}


@router.get("/transfers/{transfer_id}", response_model=dict)
async def get_media_transfer(transfer_id: str):
    rec = get_transfer(transfer_id)
    if not rec:
        raise HTTPException(status_code=404, detail="❌ Không tìm thấy tiến độ tải.")
    return {"success": True, "data": rec}


@router.get("/assets/{asset_id}", response_model=dict)
async def get_video_asset(
    asset_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Retrieve details of a video asset by ID."""
    res = await session.execute(select(VideoAsset).where(VideoAsset.id == asset_id))
    asset = res.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="❌ Không tìm thấy VideoAsset.")

    return {
        "success": True,
        "data": {
            "id": asset.id,
            "asset_id": asset.id,
            "title": asset.title,
            "source_type": asset.source_type,
            "source_url": asset.source_url,
            "source_domain": asset.source_domain,
            "original_filename": asset.original_filename,
            "file_path": asset.file_path,
            "mime_type": asset.mime_type,
            "file_size": asset.file_size,
            "duration": asset.duration,
            "width": asset.width,
            "height": asset.height,
            "audio_available": asset.audio_available,
            "status": asset.status,
            "r2_key": asset.r2_key,
            "url": asset.url,
            "thumbnail_url": asset.thumbnail_url,
            "error_message": asset.error_message,
            "created_at": asset.created_at.isoformat() if asset.created_at else None,
            "updated_at": asset.updated_at.isoformat() if asset.updated_at else None,
        },
    }


@router.post("/upload-watermark-logo", response_model=dict)
async def upload_watermark_logo(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session),
):
    """Upload watermark logo image file (PNG/JPG/WEBP) for video processing."""
    ext = Path(file.filename or "logo.png").suffix.lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
        raise HTTPException(status_code=400, detail="❌ Định dạng logo không hợp lệ. Chỉ chấp nhận file PNG, JPG, JPEG, WEBP.")

    if project_id and project_id != "default_project":
        storage_dir = settings.STORAGE_ROOT / "projects" / project_id / "assets" / "watermarks"
    else:
        storage_dir = settings.STORAGE_ROOT / "translator" / "watermarks"
    
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    unique_filename = f"logo_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = storage_dir / unique_filename
    
    with open(dest_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    if project_id and project_id != "default_project":
        relative_key = f"projects/{project_id}/assets/watermarks/{unique_filename}"
    else:
        relative_key = f"translator/watermarks/{unique_filename}"

    obj_key, public_url = await storage_service.upload_file(
        dest_path,
        relative_key,
        content_type=file.content_type or "image/png"
    )

    asset_id = None
    if project_id and project_id != "default_project":
        p_res = await session.execute(select(Project).where(Project.id == project_id))
        project = p_res.scalar_one_or_none()
        if project:
            asset_id = str(uuid.uuid4())
            file_size = dest_path.stat().st_size if dest_path.exists() else 0
            asset = Asset(
                id=asset_id,
                project_id=project_id,
                asset_type="watermark_logo",
                file_path=relative_key,
                file_format=ext.replace(".", ""),
                file_size=file_size,
            )
            session.add(asset)

            curr_settings = project.settings_json or {}
            curr_settings["watermark_image_asset_id"] = asset_id
            curr_settings["watermark_image_path"] = relative_key
            project.settings_json = curr_settings
            await session.commit()

    return {
        "success": True,
        "data": {
            "asset_id": asset_id,
            "image_path": relative_key,
            "filename": file.filename,
            "url": public_url or f"/api/storage/files/{relative_key}",
            "relative_path": relative_key,
        }
    }


@router.post("/jobs", response_model=dict)
async def create_translation_job(
    body: CreateJobRequest,
    session: AsyncSession = Depends(get_session),
):
    """Create a new video translation job and link/create a real Project record."""
    res = await session.execute(select(VideoAsset).where(VideoAsset.id == body.asset_id))
    asset = res.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="❌ VideoAsset không tồn tại.")

    # Ensure a valid Project exists in projects table
    project_id = body.project_id
    if project_id:
        p_res = await session.execute(select(Project).where(Project.id == project_id))
        proj = p_res.scalar_one_or_none()
        if not proj:
            project_id = None

    if not project_id:
        proj_id = str(uuid.uuid4())[:8]
        proj = Project(
            id=proj_id,
            title=asset.title or "Video Translation Project",
            workflow_mode="video_translator",
            workflow_status=WorkflowStatus.CREATED.value,
        )
        session.add(proj)
        await session.flush()
        project_id = proj.id

    job_id = str(uuid.uuid4())[:8]
    proj_settings = proj.settings_json or {} if (proj and proj.settings_json) else {}
    wm_enabled = body.watermark_enabled if body.watermark_enabled else _parse_bool(proj_settings.get("watermark_enabled"), False)
    wm_type = body.watermark_type if body.watermark_type != "image" else proj_settings.get("watermark_type", "image")
    wm_img_path = body.watermark_image_path or proj_settings.get("watermark_image_path")
    wm_text = body.watermark_text or proj_settings.get("watermark_text")
    wm_pos = body.watermark_position if body.watermark_position != "bottom_right" else proj_settings.get("watermark_position", "bottom_right")
    wm_scale = body.watermark_scale if body.watermark_scale != 0.20 else proj_settings.get("watermark_scale", 0.20)
    wm_opacity = body.watermark_opacity if body.watermark_opacity != 0.80 else proj_settings.get("watermark_opacity", 0.80)
    wm_margin = body.watermark_margin if body.watermark_margin != 20 else proj_settings.get("watermark_margin", 20)
    wm_font_size = body.watermark_font_size if body.watermark_font_size != 32 else proj_settings.get("watermark_font_size", 32)

    auto_confirm = _parse_bool(body.auto_confirm_translation, proj_settings.get("auto_confirm_translation", True))
    auto_confirm_voice = _parse_bool(getattr(body, "auto_confirm_voice", False), proj_settings.get("auto_confirm_voice", False))
    trim_filler = _parse_bool(getattr(body, "trim_filler_enabled", True), proj_settings.get("trim_filler_enabled", True))
    copyright_check = _parse_bool(
        getattr(body, "copyright_check_enabled", True),
        proj_settings.get("copyright_check_enabled", True),
    )

    settings_snapshot = {
        "auto_confirm_translation": auto_confirm,
        "auto_confirm_voice": auto_confirm_voice,
        "trim_filler_enabled": trim_filler,
        "copyright_check_enabled": copyright_check,
        "stt": {
            "provider": body.llm_provider_id or proj_settings.get("stt_provider_id", "gemini"),
            "model": proj_settings.get("stt_model", "gemini-2.0-flash"),
        },
        "translation": {
            "provider": body.llm_provider_id or proj_settings.get("translation_provider_id", "gemini"),
            "model": proj_settings.get("translation_model", "gemini-2.0-flash"),
        },
        "tts": {
            "provider": body.audio_provider_id or proj_settings.get("audio_provider_id", "edge_tts"),
            "voice_id": body.voice_id or proj_settings.get("voice_id", "vi-VN-HoaiMyNeural"),
            "default_male_voice_id": body.default_male_voice_id or proj_settings.get("default_male_voice_id", "vi-VN-NamMinhNeural"),
            "default_female_voice_id": body.default_female_voice_id or proj_settings.get("default_female_voice_id", "vi-VN-HoaiMyNeural"),
        },
        "language": {
            "source_language": body.source_language or proj_settings.get("source_language", "auto"),
            "target_language": body.target_language or proj_settings.get("target_language", "vi"),
        },
        "audio_mix": {
            "original_audio_mode": body.original_audio_mode or proj_settings.get("original_audio_mode", "mute"),
            "original_audio_volume": proj_settings.get("original_audio_volume", 0.20),
        },
        "watermark": {
            "enabled": wm_enabled,
            "type": wm_type,
            "image_path": wm_img_path,
            "text": wm_text,
            "position": wm_pos,
            "scale": wm_scale,
            "opacity": wm_opacity,
            "margin": wm_margin,
            "font_size": wm_font_size,
        },
        "video": {
            "aspect_ratio": proj_settings.get("target_aspect_ratio", "16:9"),
            "enable_burned_subtitles": _parse_bool(proj_settings.get("enable_burned_subtitles"), True),
            "enable_bgm_ducking": _parse_bool(proj_settings.get("enable_bgm_ducking"), True),
            "bgm_volume_db": proj_settings.get("bgm_volume_db", -18.0),
        },
        "thumbnail_enabled": _parse_bool(
            getattr(body, "thumbnail_enabled", False),
            proj_settings.get("thumbnail_enabled", False),
        ),
        "thumbnail_provider": getattr(body, "thumbnail_provider", None)
        or proj_settings.get("thumbnail_provider", "pollinations"),
        "thumbnail_style": getattr(body, "thumbnail_style", None)
        or proj_settings.get("thumbnail_style", "auto"),
        "thumbnail_custom_instruction": getattr(body, "thumbnail_custom_instruction", None)
        or proj_settings.get("thumbnail_custom_instruction")
        or None,
        "thumbnail_source": getattr(body, "thumbnail_source", None)
        or proj_settings.get("thumbnail_source", "ai"),
        "thumbnail_library_path": getattr(body, "thumbnail_library_path", None)
        or proj_settings.get("thumbnail_library_path"),
    }

    initial_studio_state = {
        "active_step": "input",
        "active_tab": "overview",
        "selected_segment_id": None,
    }

    now_dt = datetime.now(timezone.utc).replace(tzinfo=None)

    job = VideoTranslationJob(
        id=job_id,
        project_id=project_id,
        asset_id=body.asset_id,
        source_language=body.source_language,
        target_language=body.target_language,
        audio_provider_id=body.audio_provider_id,
        llm_provider_id=body.llm_provider_id,
        voice_id=body.voice_id,
        original_audio_mode=body.original_audio_mode,
        auto_confirm_translation=auto_confirm,
        auto_confirm_voice=auto_confirm_voice,
        status=TranslationJobStatus.CREATED.value,
        stage="QUEUED",
        stage_progress_pct=0.0,
        overall_progress_pct=0.0,
        current_step="Khởi tạo job",
        watermark_enabled=wm_enabled,
        watermark_type=wm_type,
        watermark_image_path=wm_img_path,
        watermark_text=wm_text,
        watermark_position=wm_pos,
        watermark_scale=wm_scale,
        watermark_opacity=wm_opacity,
        watermark_margin=wm_margin,
        watermark_font_size=wm_font_size,
        settings_snapshot_json=json.dumps(settings_snapshot),
        studio_state_json=json.dumps(initial_studio_state),
        last_checkpoint_stage="CREATED",
        last_checkpoint_at=now_dt,
        last_heartbeat=now_dt,
    )

    session.add(job)
    await session.commit()
    log_job_event(job_id, "CREATED", f"Job created for asset '{asset.title}' (ID: {asset.id}, Project: {project_id})")

    return {
        "success": True,
        "data": {
            "id": job.id,
            "job_id": job.id,
            "asset_id": job.asset_id,
            "status": job.status,
        },
    }


async def auto_confirm_and_start_render_if_needed(job_id: str) -> bool:
    """
    Idempotent helper: Automatically confirms translation text segments and launches
    Phase 2 rendering (TTS Dubbing -> Audio Sync -> FFmpeg Render) if a job is in
    SEGMENT_EDITING / TRANSLATE stage awaiting review and auto_confirm_translation is True.
    Guaranteed strictly one-shot via auto_confirm_executed snapshot flag.
    """
    async with async_session_factory() as session:
        res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
        job = res.scalar_one_or_none()
        if not job or job.status in [TranslationJobStatus.COMPLETED.value, "completed"]:
            return False

        snap = {}
        if job.settings_snapshot_json:
            try:
                snap = json.loads(job.settings_snapshot_json)
            except Exception:
                snap = {}

        if snap.get("auto_confirm_executed"):
            return False

        is_waiting = (
            job.status in [TranslationJobStatus.SEGMENT_EDITING.value, "segment_editing"]
            or (job.stage == "TRANSLATE" and job.status not in [TranslationJobStatus.NEEDS_REVIEW.value, "needs_review", TranslationJobStatus.FAILED.value, "failed"])
        )
        if (
            is_waiting
            and job.auto_confirm_translation
            and job.status not in [TranslationJobStatus.FAILED.value, TranslationJobStatus.NEEDS_REVIEW.value, "needs_review"]
        ):
            auto_confirm_voice = getattr(job, "auto_confirm_voice", False) or bool(snap.get("auto_confirm_voice"))
            profiles = (await session.execute(select(CharacterVoiceProfile).where(CharacterVoiceProfile.project_id == job.project_id))).scalars().all()
            all_confirmed = bool(profiles) and all(p.confirmed_by_user for p in profiles)

            # Mark text segments as confirmed
            await session.execute(
                update(VideoTranslationSegment)
                .where(VideoTranslationSegment.job_id == job_id)
                .values(status="confirmed")
            )
            snap["auto_confirm_executed"] = True
            job.settings_snapshot_json = json.dumps(snap)
            job.last_checkpoint_stage = "TRANSLATION_CONFIRMED"

            if not all_confirmed and not auto_confirm_voice:
                job.status = TranslationJobStatus.NEEDS_REVIEW.value
                job.stage = "CHARACTER_VOICE_REVIEW"
                job.current_step = "Cần kiểm tra Character / Voice trước TTS"
                job.studio_state_json = json.dumps({"active_step": "character_voice_review", "active_tab": "editor"})
                job.pid = None
                job.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                await session.commit()
                log_job_event(job_id, "NEEDS_REVIEW", "Auto-confirmed translation segments, but voice review remains pending.")
                return False

            if auto_confirm_voice and not all_confirmed:
                for p in profiles:
                    p.confirmed_by_user = True

            job.status = TranslationJobStatus.GENERATING_TTS.value
            job.stage = "DUB"
            job.current_step = "Bản dịch đã hoàn tất. Tự động chuyển sang Phase 2 (TTS & Dubbing)..."
            job.studio_state_json = json.dumps({"active_step": "dubbing", "active_tab": "editor"})
            job.pid = None
            job.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await session.commit()

            log_job_event(job_id, "AUTO_CONFIRM", "Auto-confirmed translated segments (one-shot). Launching Phase 2 TTS & Dubbing pipeline.")
            asyncio.create_task(execute_job_render_pipeline(job_id))
            return True
        return False


@router.post("/jobs/{job_id}/start", response_model=dict)
async def start_translation_pipeline(
    job_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Start Phase 1 of translation pipeline (Extract Audio -> STT -> Translate -> Segment Editor)."""
    res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Translation Job không tồn tại.")
    if job.status in [TranslationJobStatus.COMPLETED.value, "completed"]:
        return {"success": True, "data": {"started": False, "job_id": job_id, "message": "Job đã hoàn tất."}}

    async def run_pipeline():
        lock = get_job_lock(job_id)
        if lock.locked():
            logger.warning(f"Job {job_id} pipeline already running in another task.")
            return

        async with lock:
            start_job_heartbeat(job_id)
            current_stage = "EXTRACTING_AUDIO"
            try:
                async with async_session_factory() as bg_session:
                    job_res = await bg_session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
                    b_job = job_res.scalar_one_or_none()
                    if not b_job or b_job.status in [TranslationJobStatus.COMPLETED.value, "completed"]:
                        return

                    asset_res = await bg_session.execute(select(VideoAsset).where(VideoAsset.id == b_job.asset_id))
                    b_asset = asset_res.scalar_one_or_none()
                    if not b_asset:
                        return

                    job_dir = settings.STORAGE_ROOT / "translator" / "jobs" / job_id
                    job_dir.mkdir(parents=True, exist_ok=True)

                    snap = {}
                    if b_job.settings_snapshot_json:
                        try:
                            snap = json.loads(b_job.settings_snapshot_json)
                        except Exception:
                            snap = {}
                    cc_prev = snap.get("copyright_check") or {}
                    skip_to_stt = bool(cc_prev.get("override")) and (
                        b_job.last_checkpoint_stage == "COPYRIGHT_HOLD"
                        or b_job.status == TranslationJobStatus.COPYRIGHT_HOLD.value
                    )

                    extracted_audio_path = job_dir / "extracted_audio.wav"
                    local_asset_path = Path(b_asset.file_path)
                    if skip_to_stt:
                        saved_audio = cc_prev.get("audio_path")
                        saved_video = cc_prev.get("video_path")
                        if saved_audio and Path(saved_audio).is_file():
                            extracted_audio_path = Path(saved_audio)
                        if saved_video and Path(saved_video).is_file():
                            local_asset_path = Path(saved_video)
                        log_job_event(job_id, "COPYRIGHT", "Override confirmed. Continuing to STT.")

                    if not skip_to_stt:
                        # 1. Extract Audio
                        current_stage = "EXTRACTING_AUDIO"
                        b_job.status = TranslationJobStatus.EXTRACTING_AUDIO.value
                        b_job.stage = "EXTRACTING_AUDIO"
                        b_job.current_step = "Trích xuất audio từ video"
                        b_job.stage_progress_pct = 0.0
                        b_job.overall_progress_pct = calculate_overall_progress("EXTRACTING_AUDIO", 0.0)
                        await bg_session.commit()


                    def on_extract_progress(stats: dict):
                        pct = stats.get("progress_pct", 0.0)
                        pid = stats.get("pid")
                        asyncio.create_task(_update_ffmpeg_stats(job_id, "EXTRACTING_AUDIO", pct, pid, stats))

                    def on_extract_pid(pid: int):
                        asyncio.create_task(_update_pid(job_id, pid))

                    if not skip_to_stt and not local_asset_path.exists() and getattr(b_asset, "r2_key", None):
                        log_job_event(job_id, "DOWNLOADING", f"Local asset missing at {local_asset_path}. Downloading from R2 ({b_asset.r2_key})...")
                        local_asset_path.parent.mkdir(parents=True, exist_ok=True)
                        try:
                            await storage_service.download_file(b_asset.r2_key, local_asset_path)
                        except Exception as download_err:
                            logger.warning("R2 asset download failed", error=str(download_err), job_id=job_id)

                    if not skip_to_stt:
                        try:
                            await extract_audio_from_video(
                                local_asset_path,
                                extracted_audio_path,
                                job_id=job_id,
                                on_progress=on_extract_progress,
                                on_pid=on_extract_pid,
                            )
                        except ValueError as ve:
                            b_job.status = TranslationJobStatus.FAILED.value
                            b_job.stage = "FAILED"
                            b_job.error_message = f"❌ {str(ve)}"
                            b_job.pid = None
                            await bg_session.commit()
                            log_job_event(job_id, "FAILED", f"Audio Extraction Error: {str(ve)}")
                            return

                        now_dt = datetime.now(timezone.utc).replace(tzinfo=None)
                        b_job.last_checkpoint_stage = "EXTRACTING_AUDIO_DONE"
                        b_job.last_checkpoint_at = now_dt
                        await bg_session.commit()

                    # 1b. Trim intro/outro filler before STT
                    trim_on = (not skip_to_stt) and _parse_bool(snap.get("trim_filler_enabled"), True)
                    if trim_on:
                        from app.services.video_translator.filler_detector import detect_and_trim_filler
                        from app.media.ffprobe import probe_duration_async

                        b_job.current_step = "Đang lọc intro/outro thừa"
                        await bg_session.commit()
                        try:
                            meta_dur = await probe_duration_async(local_asset_path)
                        except Exception:
                            meta_dur = 0.0

                        async def _llm_generate(prompt: str) -> str:
                            from app.providers.llm.gemini_provider import GeminiLLMProvider
                            return await GeminiLLMProvider().generate_text(prompt, model="gemini-2.0-flash")

                        async def _reextract(video_path, wav_path):
                            return await extract_audio_from_video(
                                video_path,
                                wav_path,
                                job_id=job_id,
                            )

                        trim_res = await detect_and_trim_filler(
                            video_path=str(local_asset_path),
                            audio_path=str(extracted_audio_path),
                            duration=float(meta_dur or 0.0),
                            output_video=str(job_dir / "content_trimmed.mp4"),
                            output_audio=str(job_dir / "extracted_audio_trimmed.wav"),
                            enabled=True,
                            llm_generate=_llm_generate,
                            extract_audio=_reextract,
                        )
                        if trim_res.get("applied") and Path(trim_res["video_path"]).is_file():
                            local_asset_path = Path(trim_res["video_path"])
                            extracted_audio_path = Path(trim_res.get("audio_path") or extracted_audio_path)
                            b_asset.file_path = str(local_asset_path)
                            snap["trim_filler"] = {
                                "applied": True,
                                "original_duration": trim_res.get("original_duration"),
                                "start_sec": trim_res.get("start_sec"),
                                "end_sec": trim_res.get("end_sec"),
                                "original_video_path": trim_res.get("original_video_path"),
                                "notice": trim_res.get("notice"),
                            }
                            b_job.settings_snapshot_json = json.dumps(snap)
                            b_job.current_step = trim_res.get("notice") or "Đã cắt intro/outro thừa"
                            log_job_event(job_id, "TRIM_FILLER", b_job.current_step)
                            await bg_session.commit()

                    # 1c. Copyright risk check before STT
                    if not skip_to_stt:
                        from app.services.video_translator.copyright_check import (
                            metadata_from_asset,
                            run_copyright_check,
                        )
                        from app.config import get_settings as _get_settings

                        cc_on = _parse_bool(snap.get("copyright_check_enabled"), True)
                        b_job.current_step = "Đang kiểm tra bản quyền"
                        await bg_session.commit()
                        try:
                            cc_meta = metadata_from_asset(b_asset, snap.get("source_metadata") or {})
                            cc_report = await run_copyright_check(
                                metadata=cc_meta,
                                audio_path=str(extracted_audio_path) if Path(extracted_audio_path).is_file() else None,
                                enabled=cc_on,
                                acoustid_api_key=_get_settings().ACOUSTID_API_KEY,
                            )
                        except Exception as cc_err:
                            logger.warning("Copyright check failed; continuing", error=str(cc_err), job_id=job_id)
                            cc_report = {
                                "level": "green",
                                "reasons": [f"Kiểm tra bản quyền lỗi, bỏ qua: {cc_err}"],
                                "enabled": cc_on,
                                "hold": False,
                                "notice": "Không kiểm tra được bản quyền, tiếp tục pipeline.",
                            }
                        cc_report["audio_path"] = str(extracted_audio_path)
                        cc_report["video_path"] = str(local_asset_path)
                        cc_report["override"] = False
                        snap["copyright_check"] = cc_report
                        b_job.settings_snapshot_json = json.dumps(snap)
                        notice = str(cc_report.get("notice") or "")
                        b_job.current_step = notice[:100] if notice else "Đã kiểm tra bản quyền"
                        log_job_event(job_id, "COPYRIGHT", notice or f"level={cc_report.get('level')}")
                        await bg_session.commit()
                        if cc_report.get("hold") and cc_report.get("level") == "red":
                            now_dt = datetime.now(timezone.utc).replace(tzinfo=None)
                            b_job.status = TranslationJobStatus.COPYRIGHT_HOLD.value
                            b_job.stage = "COPYRIGHT_HOLD"
                            b_job.last_checkpoint_stage = "COPYRIGHT_HOLD"
                            b_job.last_checkpoint_at = now_dt
                            b_job.pid = None
                            b_job.current_step = (notice or "Rủi ro bản quyền CAO — chờ xác nhận")[:100]
                            await bg_session.commit()
                            log_job_event(job_id, "COPYRIGHT_HOLD", "Paused before STT. Confirm to continue.")
                            stop_job_heartbeat(job_id)
                            return

                    # 2. STT & Language Detection
                    current_stage = "STT"
                    b_job.status = TranslationJobStatus.STT.value
                    b_job.stage = "STT"
                    b_job.pid = None
                    b_job.current_step = "Nhận diện giọng nói (Speech-to-Text)"
                    b_job.stage_progress_pct = 50.0
                    b_job.overall_progress_pct = calculate_overall_progress("STT", 50.0)
                    await bg_session.commit()

                    segments_raw, detected_lang = await speech_to_text_and_detect_language(
                        extracted_audio_path,
                        job_id=job_id,
                        target_language=b_job.target_language,
                        source_language=b_job.source_language,
                        llm_provider_id=b_job.llm_provider_id or "gemini",
                    )

                    now_dt = datetime.now(timezone.utc).replace(tzinfo=None)
                    b_job.last_checkpoint_stage = "STT_DONE"
                    b_job.last_checkpoint_at = now_dt

                    # 2b. Visual Character / Gender Analysis (IMMEDIATELY AFTER STT)
                    b_job.current_step = "Phân tích giới tính nhân vật (Visual Gender)"
                    await bg_session.commit()
                    log_job_event(job_id, "VISUAL_GENDER", "Starting Visual Character / Gender Analysis immediately after STT...")

                    video_path_str = str(local_asset_path) if 'local_asset_path' in locals() and local_asset_path and local_asset_path.is_file() else None
                    visual_genders = {}
                    if video_path_str:
                        from app.services.video_translator.visual_gender_service import detect_speakers_gender
                        try:
                            visual_genders = await detect_speakers_gender(video_path_str, segments_raw, db=bg_session)
                            log_job_event(job_id, "VISUAL_GENDER", f"Visual Gender Analysis completed: {visual_genders}")
                        except Exception as vg_err:
                            logger.error(f"[{job_id}] Visual gender detection failed: {vg_err}")
                            log_job_event(job_id, "VISUAL_GENDER", f"Visual detection error: {vg_err}. Falling back to dialogue LLM.")

                    # 2c. Character Mapping (BEFORE Translation)
                    from app.services.video_translator.character_mapping_service import map_and_persist
                    b_job.current_step = "Nhận diện và ánh xạ nhân vật (Character Mapping)"
                    await bg_session.commit()
                    llm = get_registry().get_llm(b_job.llm_provider_id or "gemini")
                    mapping_result = await map_and_persist(
                        bg_session,
                        b_job.project_id,
                        segments_raw,
                        llm,
                        video_path=video_path_str,
                        visual_genders=visual_genders,
                    )

                    # Decorate segments_raw with character metadata (including resolved gender)
                    for seg in segments_raw:
                        spk = seg.get("speaker_id") or f"UNRESOLVED_{seg.get('number', 1):04d}"
                        decision = mapping_result.by_speaker.get(spk, {})
                        seg["character_id"] = decision.get("character_id")
                        seg["speaker_name"] = decision.get("name") or spk
                        seg["gender"] = decision.get("gender", "unknown")
                        seg["role"] = decision.get("role", "supporting")
                        seg["mapping_confidence"] = decision.get("confidence", 0.0)

                    current_stage = "TRANSLATING"
                    b_job.detected_language = detected_lang
                    b_job.status = TranslationJobStatus.TRANSLATED.value
                    b_job.stage = "TRANSLATING"
                    b_job.current_step = "Đang dịch bản thoại"
                    b_job.stage_progress_pct = 50.0
                    b_job.overall_progress_pct = calculate_overall_progress("TRANSLATING", 50.0)
                    await bg_session.commit()

                    # 3. Detect terminology into the canonical project glossary before translation.
                    if b_job.project_id and b_job.project_id != "default_project":
                        from app.services.terminology_extractor import extract_and_persist_from_segments

                        b_job.current_step = "Đang cập nhật Glossary"
                        await bg_session.commit()
                        await extract_and_persist_from_segments(
                            bg_session,
                            b_job.project_id,
                            segments_raw,
                            b_job.target_language or "vi",
                        )

                    # 4. Translate with the project glossary loaded by the service.
                    translated_segs = await translate_transcript_segments(
                        segments_raw,
                        source_language=detected_lang,
                        target_language=b_job.target_language,
                        job_id=job_id,
                        llm_provider_id=b_job.llm_provider_id or "gemini",
                        db=bg_session,
                        project_id=b_job.project_id,
                    )

                    # Clear previous segments if any
                    await bg_session.execute(
                        delete(VideoTranslationSegment)
                        .where(VideoTranslationSegment.job_id == job_id)
                        .execution_options(synchronize_session=False)
                    )
                    bg_session.expire(b_job, ["segments"])

                    created_segment_rows = []
                    for seg in translated_segs:
                        spk = seg.get("speaker_id") or f"UNRESOLVED_{seg['number']:04d}"
                        decision = mapping_result.by_speaker.get(spk, {})
                        cid = seg.get("character_id") or decision.get("character_id")
                        conf = seg.get("mapping_confidence") or decision.get("confidence", 0.0)
                        db_seg = VideoTranslationSegment(
                            job_id=job_id,
                            segment_number=seg["number"],
                            start_time=seg["start_time"],
                            end_time=seg["end_time"],
                            original_start=seg["start_time"],
                            original_end=seg["end_time"],
                            speaker_id=spk,
                            character_id=cid,
                            mapping_confidence=conf,
                            original_text=seg["text"],
                            translated_text=seg.get("translated_text", seg["text"]),
                            status="translated",
                        )
                        bg_session.add(db_seg)
                        created_segment_rows.append(db_seg)

                    await bg_session.flush()
                    from app.services.video_translator.voice_assignment_service import assign_project_voices
                    segment_rows = created_segment_rows
                    # Resolve target_language from job settings snapshot or job model
                    resolved_target_lang = b_job.target_language
                    default_male_voice = None
                    default_female_voice = None
                    if b_job.settings_snapshot_json:
                        try:
                            snap = json.loads(b_job.settings_snapshot_json)
                            if isinstance(snap.get("language"), dict) and snap["language"].get("target_language"):
                                resolved_target_lang = snap["language"]["target_language"]
                            elif snap.get("target_language"):
                                resolved_target_lang = snap["target_language"]
                            if isinstance(snap.get("tts"), dict):
                                default_male_voice = snap["tts"].get("default_male_voice_id")
                                default_female_voice = snap["tts"].get("default_female_voice_id")
                        except Exception:
                            pass

                    voice_result = await assign_project_voices(
                        bg_session,
                        b_job.project_id,
                        [{
                            "character_id": row.character_id,
                            "original_start": row.original_start,
                            "original_end": row.original_end,
                        } for row in segment_rows],
                        target_language=resolved_target_lang,
                        default_male_voice_id=default_male_voice,
                        default_female_voice_id=default_female_voice,
                    )
                    for row in segment_rows:
                        assignment = voice_result.assignments.get(row.character_id, {})
                        row.voice_provider = assignment.get("voice_provider")
                        row.voice_id = assignment.get("voice_id")
                    character_voice_needs_review = mapping_result.requires_review or voice_result.requires_review

                    now_dt = datetime.now(timezone.utc).replace(tzinfo=None)
                    auto_confirm_translation = getattr(b_job, "auto_confirm_translation", True)
                    if auto_confirm_translation is None:
                        auto_confirm_translation = True

                    auto_confirm_voice = getattr(b_job, "auto_confirm_voice", False)
                    if b_job.settings_snapshot_json:
                        try:
                            snap = json.loads(b_job.settings_snapshot_json)
                            if "auto_confirm_voice" in snap:
                                auto_confirm_voice = bool(snap["auto_confirm_voice"])
                        except Exception:
                            pass

                    # Query character profiles for project to verify user confirmation state
                    profiles_in_db = (
                        await bg_session.execute(
                            select(CharacterVoiceProfile).where(
                                CharacterVoiceProfile.project_id == b_job.project_id
                            )
                        )
                    ).scalars().all()
                    all_voices_user_confirmed = bool(profiles_in_db) and all(
                        p.confirmed_by_user for p in profiles_in_db
                    )
                    all_segments_have_voices = bool(segment_rows) and all(
                        bool(row.voice_id and row.voice_provider) for row in segment_rows
                    )

                    if auto_confirm_voice and all_segments_have_voices:
                        voice_review_required = False
                    else:
                        voice_review_required = (
                            character_voice_needs_review
                            or (not auto_confirm_voice and not all_voices_user_confirmed)
                        )

                    b_job.stage_progress_pct = 100.0
                    b_job.overall_progress_pct = 60.0
                    b_job.total_segments_count = len(translated_segs)
                    b_job.completed_segments_count = 0
                    b_job.pid = None
                    b_job.last_checkpoint_stage = "TRANSLATION_DONE"
                    b_job.last_checkpoint_at = now_dt

                    # If auto_confirm_translation is True, confirm text segments
                    if auto_confirm_translation:
                        for db_seg in created_segment_rows:
                            db_seg.status = "confirmed"

                    should_launch_render = False

                    if voice_review_required:
                        b_job.status = TranslationJobStatus.NEEDS_REVIEW.value
                        b_job.stage = "CHARACTER_VOICE_REVIEW"
                        b_job.current_step = "Cần kiểm tra Character / Voice trước TTS"
                        b_job.studio_state_json = json.dumps({"active_step": "character_voice_review", "active_tab": "editor"})
                        await bg_session.commit()
                        stop_job_heartbeat(job_id)
                        snapshot_str = (
                            f"Phase 1 completed. Character / Voice review required before TTS.\n"
                            f"[STATE SNAPSHOT] Job: {job_id} | status={b_job.status} | stage={b_job.stage} | "
                            f"progress={b_job.overall_progress_pct}% | segments={len(translated_segs)}"
                        )
                        log_job_event(job_id, "NEEDS_REVIEW", snapshot_str)

                    elif auto_confirm_translation:
                        if auto_confirm_voice and not all_voices_user_confirmed:
                            for profile in profiles_in_db:
                                profile.confirmed_by_user = True

                        b_job.status = TranslationJobStatus.GENERATING_TTS.value
                        b_job.stage = "DUB"
                        b_job.current_step = "Bản dịch đã hoàn tất. Tự động chuyển sang Phase 2 (TTS & Dubbing)..."
                        b_job.studio_state_json = json.dumps({"active_step": "dubbing", "active_tab": "editor"})
                        await bg_session.commit()

                        snapshot_str = (
                            f"Phase 1 completed. Auto-confirming translated text segments for Phase 2 render (TTS & Dubbing)...\n"
                            f"[STATE SNAPSHOT] Job: {job_id} | status={b_job.status} | stage={b_job.stage} | "
                            f"progress={b_job.overall_progress_pct}% | segments={len(translated_segs)}"
                        )
                        log_job_event(job_id, "TRANSLATE", snapshot_str)
                        should_launch_render = True

                    else:
                        b_job.status = TranslationJobStatus.SEGMENT_EDITING.value
                        b_job.stage = "TRANSLATE"
                        b_job.current_step = "Bản dịch đã hoàn tất (Chờ xác nhận thủ công)"
                        b_job.studio_state_json = json.dumps({"active_step": "segment_editing", "active_tab": "editor"})
                        await bg_session.commit()

                        snapshot_str = (
                            f"Phase 1 completed. Awaiting user segment confirmation.\n"
                            f"[STATE SNAPSHOT] Job: {job_id} | status={b_job.status} | stage={b_job.stage} | "
                            f"progress={b_job.overall_progress_pct}% | heartbeat=INACTIVE | segments={len(translated_segs)}"
                        )
                        log_job_event(job_id, "TRANSLATE", snapshot_str)
                        stop_job_heartbeat(job_id)

            except Exception as e:
                tb_str = traceback.format_exc()
                err_name = type(e).__name__
                err_msg = str(e) or repr(e)
                full_err_log = f"Error: {err_name}: {err_msg}\nStage: {current_stage}\nStack:\n{tb_str}"

                db_err_detail = f"{err_name}: {err_msg}"
                if isinstance(e, FFmpegExecutionError):
                    full_err_log += f"\nFFmpeg Exit Code: {e.exit_code}\nFFmpeg Stderr: {e.stderr_text}\nCommand: {' '.join(e.cmd)}"
                    if e.stderr_text:
                        db_err_detail += f" | Stderr: {e.stderr_text[:500]}"

                logger.exception("Translation pipeline failed", job_id=job_id)
                log_job_event(job_id, "FAILED", f"Unhandled pipeline exception:\n{full_err_log}")

                try:
                    async with async_session_factory() as err_session:
                        await err_session.execute(
                            update(VideoTranslationJob)
                            .where(VideoTranslationJob.id == job_id)
                            .values(
                                status=TranslationJobStatus.FAILED.value,
                                stage="FAILED",
                                error_message=f"❌ {db_err_detail}",
                                pid=None,
                            )
                        )
                        await err_session.commit()
                except Exception as db_save_err:
                    logger.error("Failed to write pipeline failure status to DB", job_id=job_id, error=str(db_save_err))

                stop_job_heartbeat(job_id)

        # Outside async with lock: launch Phase 2 render cleanly if auto_confirm is True
        if should_launch_render:
            asyncio.create_task(execute_job_render_pipeline(job_id))

    background_tasks.add_task(run_pipeline)
    return {"success": True, "data": {"started": True, "job_id": job_id}}



STAGE_ORDER_MAP = {
    "QUEUED": 0,
    "EXTRACTING_AUDIO": 1,
    "STT": 2,
    "TRANSLATING": 3,
    "SEGMENT_EDITING": 4,
    "GENERATING_TTS": 5,
    "SYNCING_AUDIO": 6,
    "RENDERING": 7,
    "COMPLETED": 8,
    "FAILED": 99,
    "CANCELLED": 99,
}


async def _update_ffmpeg_stats(job_id: str, stage: str, pct: float, pid: Optional[int], stats: dict):
    """Helper to update FFmpeg real-time stats in DB with guard against updating terminal or later stage jobs."""
    async with async_session_factory() as session:
        res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
        job = res.scalar_one_or_none()
        if not job:
            return

        # Terminal status check
        if job.status in [TranslationJobStatus.FAILED.value, TranslationJobStatus.COMPLETED.value, "cancelled", TranslationJobStatus.SEGMENT_EDITING.value, "segment_editing"]:
            return

        # Stage order check: do not overwrite if job has already progressed past this stage
        current_job_stage_idx = STAGE_ORDER_MAP.get(job.stage, 0)
        incoming_stage_idx = STAGE_ORDER_MAP.get(stage, 0)
        if incoming_stage_idx < current_job_stage_idx:
            return

        overall = calculate_overall_progress(stage, pct)
        await session.execute(
            update(VideoTranslationJob)
            .where(VideoTranslationJob.id == job_id)
            .values(
                stage=stage,
                stage_progress_pct=pct,
                overall_progress_pct=overall,
                progress_pct=overall,
                pid=pid if pct < 100.0 else None,
                ffmpeg_stats_json=json.dumps(stats, ensure_ascii=False),
                last_heartbeat=datetime.now(timezone.utc).replace(tzinfo=None),
                updated_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
        )
        await session.commit()
        await _emit_job_progress(job_id, {
            "job_id": job_id,
            "stage": stage,
            "stage_pct": pct,
            "overall_pct": overall,
            "stats": stats,
        })



async def _update_pid(job_id: str, pid: int):
    async with async_session_factory() as session:
        res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
        job = res.scalar_one_or_none()
        if not job or job.status in [TranslationJobStatus.FAILED.value, TranslationJobStatus.COMPLETED.value, "cancelled"]:
            return
        await session.execute(
            update(VideoTranslationJob)
            .where(VideoTranslationJob.id == job_id)
            .values(pid=pid, last_heartbeat=datetime.now(timezone.utc).replace(tzinfo=None))
        )
        await session.commit()


@router.get("/jobs/{job_id}", response_model=dict)
async def get_translation_job(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get job status, heartbeat, FFmpeg stats, and segment list."""
    await auto_confirm_and_start_render_if_needed(job_id)
    await check_and_mark_stalled_jobs(stalled_threshold_seconds=60)


    res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Job không tồn tại.")

    seg_res = await session.execute(
        select(VideoTranslationSegment)
        .where(VideoTranslationSegment.job_id == job_id)
        .order_by(VideoTranslationSegment.segment_number)
    )
    segments = seg_res.scalars().all()

    asset_res = await session.execute(select(VideoAsset).where(VideoAsset.id == job.asset_id))
    asset = asset_res.scalar_one_or_none()

    # Parse FFmpeg stats
    ffmpeg_stats = None
    if job.ffmpeg_stats_json:
        try:
            ffmpeg_stats = json.loads(job.ffmpeg_stats_json)
        except Exception:
            pass

    # Check heartbeat age
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    hb_age_sec = (now - job.last_heartbeat).total_seconds() if job.last_heartbeat else 999.0

    is_terminal = job.status in [
        TranslationJobStatus.FAILED.value,
        TranslationJobStatus.COMPLETED.value,
        "cancelled",
        TranslationJobStatus.SEGMENT_EDITING.value,
        "segment_editing",
        TranslationJobStatus.COPYRIGHT_HOLD.value,
        TranslationJobStatus.NEEDS_REVIEW.value,
        "copyright_hold",
    ]
    heartbeat_active = (not is_terminal) and (hb_age_sec <= 30)

    snap_out = {}
    if job.settings_snapshot_json:
        try:
            snap_out = json.loads(job.settings_snapshot_json)
        except Exception:
            snap_out = {}

    process_status = "IDLE"
    if job.status == TranslationJobStatus.FAILED.value:
        process_status = "FAILED"
    elif job.status == "cancelled":
        process_status = "KILLED"
    elif job.status == TranslationJobStatus.COMPLETED.value:
        process_status = "COMPLETED"
    elif job.status in (TranslationJobStatus.COPYRIGHT_HOLD.value, "copyright_hold"):
        process_status = "PAUSED"
    elif is_terminal:
        process_status = "COMPLETED"
    elif job.pid:
        process_status = "RUNNING"
    elif job.stage in ["STT", "TRANSLATING", "SEGMENT_EDITING", "GENERATING_TTS", "SYNCING_AUDIO", "RENDERING", "COMPLETED"]:
        process_status = "COMPLETED"
    elif job.stage == "EXTRACTING_AUDIO":
        process_status = "STARTING"

    stt_status = "PENDING"
    if job.stage in ["SEGMENT_EDITING", "GENERATING_TTS", "SYNCING_AUDIO", "RENDERING", "COMPLETED"]:
        stt_status = "COMPLETED"
    elif job.stage == "STT":
        stt_status = "RUNNING"

    translation_status = "PENDING"
    if job.stage in ["SEGMENT_EDITING", "GENERATING_TTS", "SYNCING_AUDIO", "RENDERING", "COMPLETED"]:
        translation_status = "COMPLETED"
    elif job.stage == "TRANSLATING":
        translation_status = "RUNNING"

    profiles = []
    if job.project_id:
        profiles = (await session.execute(
            select(CharacterVoiceProfile).where(CharacterVoiceProfile.project_id == job.project_id)
        )).scalars().all()
    char_map = {p.character_id: p for p in profiles}

    return {
        "success": True,
        "data": {
            "id": job.id,
            "job_id": job.id,
            "project_id": job.project_id,
            "asset": {
                "id": asset.id if asset else None,
                "title": asset.title if asset else "",
                "duration": asset.duration if asset else 0.0,
                "file_path": asset.file_path if asset else "",
            },
            "source_language": job.source_language,
            "detected_language": job.detected_language,
            "target_language": job.target_language,
            "audio_provider_id": job.audio_provider_id,
            "llm_provider_id": job.llm_provider_id or "gemini",
            "voice_id": job.voice_id,
            "original_audio_mode": job.original_audio_mode,
            "auto_confirm_translation": job.auto_confirm_translation,
            "copyright_check": snap_out.get("copyright_check"),
            "status": job.status,
            "stage": job.stage or "QUEUED",
            "stage_progress_pct": job.stage_progress_pct or 0.0,
            "overall_progress_pct": job.overall_progress_pct or job.progress_pct or 0.0,
            "progress_pct": job.overall_progress_pct or job.progress_pct or 0.0,
            "current_step": job.current_step,
            "pid": job.pid if not is_terminal else None,
            "heartbeat": {
                "active": heartbeat_active,
                "age_seconds": round(hb_age_sec, 1),
                "message": "Worker đang hoạt động" if heartbeat_active else "Heartbeat loop stopped.",
            },
            "process": {
                "type": "ffmpeg",
                "status": process_status,
                "pid": job.pid if job.pid and not is_terminal else None,
                "exitCode": 0 if process_status == "COMPLETED" else (-1 if process_status == "FAILED" else None),
            },
            "stt": {
                "status": stt_status,
                "provider": "gemini",
                "segments": job.total_segments_count or len(segments),
                "language": job.detected_language or job.source_language,
            },
            "translation": {
                "status": translation_status,
                "segments": job.total_segments_count or len(segments),
            },
            "ffmpeg_stats": ffmpeg_stats,
            "last_heartbeat_age_sec": round(hb_age_sec, 1),
            "error": {
                "message": job.error_message,
                "stage": job.stage if job.status == TranslationJobStatus.FAILED.value else None,
            },
            "error_message": job.error_message,
            "output_video_path": job.output_video_path,
            "total_segments_count": job.total_segments_count or len(segments),
            "completed_segments_count": job.completed_segments_count or 0,
            "characters": [
                {
                    "character_id": p.character_id,
                    "name": p.name,
                    "gender": p.gender,
                    "role": p.role,
                    "voice_provider": p.voice_provider,
                    "voice_id": p.voice_id,
                    "confirmed_by_user": p.confirmed_by_user,
                }
                for p in profiles
            ],
            "segments": [
                {
                    "id": s.id,
                    "number": s.segment_number,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "original_text": s.original_text,
                    "translated_text": s.translated_text,
                    "status": s.status,
                    "speaker_id": s.speaker_id,
                    "character_id": s.character_id,
                    "character_name": char_map[s.character_id].name if (s.character_id and s.character_id in char_map) else (s.character_id or s.speaker_id),
                    "gender": char_map[s.character_id].gender if (s.character_id and s.character_id in char_map) else "unknown",
                    "voice_provider": s.voice_provider,
                    "voice_id": s.voice_id,
                    "confidence": s.mapping_confidence,
                    "original_start": s.original_start if s.original_start is not None else s.start_time,
                    "original_end": s.original_end if s.original_end is not None else s.end_time,
                    "scheduled_start": s.scheduled_start,
                    "scheduled_end": s.scheduled_end,
                    "tts_duration": s.tts_duration,
                    "overlap_with": s.overlap_with or [],
                    "schedule_action": s.schedule_action,
                }
                for s in segments
            ],
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        },
    }




@router.get("/jobs/{job_id}/studio-state", response_model=dict)
async def get_job_studio_state_api(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get persistent studio workflow state, isolated settings snapshot, segments, and stage checkpoints."""
    res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Job không tồn tại.")

    seg_res = await session.execute(
        select(VideoTranslationSegment)
        .where(VideoTranslationSegment.job_id == job_id)
        .order_by(VideoTranslationSegment.segment_number)
    )
    segments = seg_res.scalars().all()

    asset_res = await session.execute(select(VideoAsset).where(VideoAsset.id == job.asset_id))
    asset = asset_res.scalar_one_or_none()

    # Parse settings_snapshot_json
    settings_snapshot = {}
    if job.settings_snapshot_json:
        try:
            settings_snapshot = json.loads(job.settings_snapshot_json)
        except Exception:
            pass

    if not settings_snapshot:
        settings_snapshot = {
            "stt": {"provider": job.llm_provider_id or "gemini", "model": "gemini-2.0-flash"},
            "translation": {"provider": job.llm_provider_id or "gemini", "model": "gemini-2.0-flash"},
            "tts": {"provider": job.audio_provider_id or "edge_tts", "voice_id": job.voice_id or "vi-VN-HoaiMyNeural"},
            "language": {"source_language": job.source_language or "auto", "target_language": job.target_language or "vi"},
            "audio_mix": {"original_audio_mode": job.original_audio_mode or "mute", "original_audio_volume": 0.20},
            "watermark": {
                "enabled": job.watermark_enabled,
                "type": job.watermark_type or "image",
                "image_path": job.watermark_image_path,
                "text": job.watermark_text,
                "position": job.watermark_position or "bottom_right",
                "scale": job.watermark_scale or 0.20,
                "opacity": job.watermark_opacity or 0.80,
                "margin": job.watermark_margin or 20,
                "font_size": job.watermark_font_size or 32,
            },
            "video": {"aspect_ratio": "16:9", "enable_burned_subtitles": True, "enable_bgm_ducking": True, "bgm_volume_db": -18.0},
        }

    # Parse studio_state_json
    studio_state = {}
    if job.studio_state_json:
        try:
            studio_state = json.loads(job.studio_state_json)
        except Exception:
            pass

    # Infer default step if active_step not set
    if not studio_state.get("active_step"):
        if job.status == TranslationJobStatus.COMPLETED.value:
            inferred_step = "completed"
        elif job.status in [TranslationJobStatus.SEGMENT_EDITING.value, "segment_editing"]:
            inferred_step = "segment_editing"
        elif job.status in [TranslationJobStatus.GENERATING_TTS.value, TranslationJobStatus.SYNCING_AUDIO.value]:
            inferred_step = "tts"
        elif job.status == TranslationJobStatus.RENDERING.value:
            inferred_step = "rendering"
        elif job.status == TranslationJobStatus.FAILED.value:
            inferred_step = "error"
        else:
            inferred_step = "pipeline"
        studio_state["active_step"] = inferred_step

    segments_payload = [
        {
            "id": s.id,
            "number": s.segment_number,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "original_text": s.original_text,
            "translated_text": s.translated_text,
            "tts_audio_path": s.tts_audio_path,
            "tts_audio_duration": s.tts_audio_duration,
            "synced_audio_path": s.synced_audio_path,
            "status": s.status,
        }
        for s in segments
    ]

    return {
        "success": True,
        "data": {
            "job": {
                "id": job.id,
                "job_id": job.id,
                "project_id": job.project_id,
                "asset_id": job.asset_id,
                "status": job.status,
                "stage": job.stage or "QUEUED",
                "current_step": job.current_step,
                "stage_progress_pct": job.stage_progress_pct or 0.0,
                "overall_progress_pct": job.overall_progress_pct or job.progress_pct or 0.0,
                "error_message": job.error_message,
                "output_video_path": job.output_video_path,
                "output_url": job.output_url,
                "total_segments_count": job.total_segments_count or len(segments),
                "completed_segments_count": job.completed_segments_count or 0,
            },
            "asset": {
                "id": asset.id if asset else None,
                "title": asset.title if asset else "",
                "duration": asset.duration if asset else 0.0,
                "file_path": asset.file_path if asset else "",
            },
            "settings_snapshot": settings_snapshot,
            "studio_state": studio_state,
            "last_checkpoint_stage": job.last_checkpoint_stage or job.stage or "CREATED",
            "last_checkpoint_at": job.last_checkpoint_at.isoformat() if job.last_checkpoint_at else None,
            "segments": segments_payload,
        },
    }


@router.patch("/jobs/{job_id}/studio-state", response_model=dict)
async def update_job_studio_state_api(
    job_id: str,
    body: UpdateStudioStateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Save/update Studio UI state for a specific video translation job."""
    res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Job không tồn tại.")

    current_state = {}
    if job.studio_state_json:
        try:
            current_state = json.loads(job.studio_state_json)
        except Exception:
            pass

    if body.active_step is not None:
        current_state["active_step"] = body.active_step
    if body.active_tab is not None:
        current_state["active_tab"] = body.active_tab
    if body.selected_segment_id is not None:
        current_state["selected_segment_id"] = body.selected_segment_id
    if body.extra_state is not None:
        current_state.update(body.extra_state)

    job.studio_state_json = json.dumps(current_state)
    job.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()

    return {
        "success": True,
        "data": {
            "job_id": job_id,
            "studio_state": current_state,
        },
    }


@router.post("/jobs/{job_id}/checkpoint", response_model=dict)
async def save_job_checkpoint_api(
    job_id: str,
    body: SaveCheckpointRequest,
    session: AsyncSession = Depends(get_session),
):
    """Record a checkpoint stage and optional UI state for a job."""
    res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Job không tồn tại.")

    now_dt = datetime.now(timezone.utc).replace(tzinfo=None)
    job.last_checkpoint_stage = body.checkpoint_stage
    job.last_checkpoint_at = now_dt
    job.updated_at = now_dt

    if body.studio_state:
        current_state = {}
        if job.studio_state_json:
            try:
                current_state = json.loads(job.studio_state_json)
            except Exception:
                pass
        current_state.update(body.studio_state)
        job.studio_state_json = json.dumps(current_state)

    await session.commit()
    log_job_event(job_id, "CHECKPOINT", f"Checkpoint saved: {body.checkpoint_stage}")

    return {
        "success": True,
        "data": {
            "job_id": job_id,
            "checkpoint_stage": job.last_checkpoint_stage,
            "last_checkpoint_at": job.last_checkpoint_at.isoformat(),
        },
    }


@router.post("/jobs/{job_id}/resume", response_model=dict)
async def resume_job_from_checkpoint_api(
    job_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Resume video translation job execution from its last saved checkpoint stage."""
    res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Job không tồn tại.")

    lock = get_job_lock(job_id)
    if lock.locked():
        return {
            "success": True,
            "message": f"Job {job_id} đã có tiến trình đang chạy.",
            "data": {"job_id": job_id, "status": job.status, "stage": job.stage},
        }

    checkpoint = job.last_checkpoint_stage or job.stage or "CREATED"
    log_job_event(job_id, "RESUME", f"Resuming job {job_id} from checkpoint: {checkpoint} (Current status: {job.status})")

    # Reset failed status if retrying/resuming
    if job.status == TranslationJobStatus.FAILED.value:
        job.status = TranslationJobStatus.RUNNING.value
        job.error_message = None
        await session.commit()

    if checkpoint in ["TRANSLATION_DONE", "SEGMENT_EDITING_DONE", "SEGMENT_EDITING", "TTS_DONE"]:
        # Resume directly into Phase 2 (TTS -> Sync -> Render)
        return await render_final_translated_video(job_id, background_tasks, session)
    else:
        # Resume from Phase 1
        return await start_translation_pipeline(job_id, background_tasks, session)


@router.post("/jobs/{job_id}/copyright-continue", response_model=dict)
async def copyright_continue_api(
    job_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Override a red copyright hold and continue Phase 1 from STT."""
    res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Job không tồn tại.")
    if job.status not in (TranslationJobStatus.COPYRIGHT_HOLD.value, "copyright_hold"):
        raise HTTPException(status_code=400, detail="❌ Job không đang chờ xác nhận bản quyền.")

    snap = {}
    if job.settings_snapshot_json:
        try:
            snap = json.loads(job.settings_snapshot_json)
        except Exception:
            snap = {}
    cc = dict(snap.get("copyright_check") or {})
    cc["override"] = True
    snap["copyright_check"] = cc
    job.settings_snapshot_json = json.dumps(snap)
    job.last_checkpoint_stage = "COPYRIGHT_HOLD"
    job.current_step = "Đã xác nhận, tiếp tục dịch"
    await session.commit()
    log_job_event(job_id, "COPYRIGHT", "User overrode copyright hold.")
    return await start_translation_pipeline(job_id, background_tasks, session)


@router.post("/jobs/{job_id}/apply-settings", response_model=dict)
async def apply_latest_settings_to_job_api(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Explicitly copy latest project/global settings into job's isolated settings snapshot."""
    res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Job không tồn tại.")

    proj_settings = {}
    if job.project_id:
        p_res = await session.execute(select(Project).where(Project.id == job.project_id))
        proj = p_res.scalar_one_or_none()
        if proj and proj.settings_json:
            proj_settings = proj.settings_json

    new_snapshot = {
        "stt": {
            "provider": proj_settings.get("stt_provider_id", job.llm_provider_id or "gemini"),
            "model": proj_settings.get("stt_model", "gemini-2.0-flash"),
        },
        "translation": {
            "provider": proj_settings.get("translation_provider_id", job.llm_provider_id or "gemini"),
            "model": proj_settings.get("translation_model", "gemini-2.0-flash"),
        },
        "tts": {
            "provider": proj_settings.get("audio_provider_id", job.audio_provider_id or "edge_tts"),
            "voice_id": proj_settings.get("voice_id", job.voice_id or "vi-VN-HoaiMyNeural"),
        },
        "language": {
            "source_language": proj_settings.get("source_language", job.source_language or "auto"),
            "target_language": proj_settings.get("target_language", job.target_language or "vi"),
        },
        "audio_mix": {
            "original_audio_mode": proj_settings.get("original_audio_mode", job.original_audio_mode or "mute"),
            "original_audio_volume": proj_settings.get("original_audio_volume", 0.20),
        },
        "watermark": {
            "enabled": _parse_bool(proj_settings.get("watermark_enabled"), job.watermark_enabled),
            "type": proj_settings.get("watermark_type", job.watermark_type or "image"),
            "image_path": proj_settings.get("watermark_image_path", job.watermark_image_path),
            "text": proj_settings.get("watermark_text", job.watermark_text),
            "position": proj_settings.get("watermark_position", job.watermark_position or "bottom_right"),
            "scale": proj_settings.get("watermark_scale", job.watermark_scale or 0.20),
            "opacity": proj_settings.get("watermark_opacity", job.watermark_opacity or 0.80),
            "margin": proj_settings.get("watermark_margin", job.watermark_margin or 20),
            "font_size": proj_settings.get("watermark_font_size", job.watermark_font_size or 32),
        },
        "video": {
            "aspect_ratio": proj_settings.get("target_aspect_ratio", "16:9"),
            "enable_burned_subtitles": _parse_bool(proj_settings.get("enable_burned_subtitles"), True),
            "enable_bgm_ducking": _parse_bool(proj_settings.get("enable_bgm_ducking"), True),
            "bgm_volume_db": proj_settings.get("bgm_volume_db", -18.0),
        }
    }

    job.settings_snapshot_json = json.dumps(new_snapshot)
    job.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()

    log_job_event(job_id, "SETTINGS_UPDATE", "Applied latest project settings to job snapshot.")

    return {
        "success": True,
        "data": {
            "job_id": job_id,
            "settings_snapshot": new_snapshot,
        },
    }


@router.get("/jobs/{job_id}/logs", response_model=dict)
async def get_job_logs_api(job_id: str):
    """Fetch job log history."""
    logs_content = get_job_logs(job_id)
    return {
        "success": True,
        "data": {
            "job_id": job_id,
            "logs": logs_content,
        },
    }


@router.put("/jobs/{job_id}/segments", response_model=dict)
async def update_job_segments(
    job_id: str,
    body: UpdateSegmentsRequest,
    session: AsyncSession = Depends(get_session),
):
    """Update translated text for transcript segments."""
    updated_count = 0
    for item in body.segments:
        res = await session.execute(
            update(VideoTranslationSegment)
            .where(VideoTranslationSegment.id == item.id)
            .where(VideoTranslationSegment.job_id == job_id)
            .values(translated_text=item.translated_text)
            .execution_options(synchronize_session=False)
        )
        if res.rowcount > 0:
            updated_count += res.rowcount
    await session.commit()
    log_job_event(job_id, "SEGMENT_EDITING", f"Updated text for {updated_count} segments.")
    return {"success": True, "data": {"updated": updated_count}}


async def execute_job_render_pipeline(job_id: str) -> None:
    """Execute Phase 2 (TTS Generation -> Audio Sync -> FFmpeg Render Final Video)."""
    if job_id in _active_render_jobs:
        logger.warning(f"Job {job_id} render already running in another task.")
        return

    _active_render_jobs.add(job_id)
    start_job_heartbeat(job_id)
    current_stage = "GENERATING_TTS"
    cancel_evt = reset_job_cancellation(job_id)

    try:

        async with async_session_factory() as init_session:
            job_res = await init_session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
            b_job = job_res.scalar_one_or_none()
            if not b_job or is_job_cancelled(job_id) or cancel_evt.is_set():
                return
            if b_job.status in [TranslationJobStatus.COMPLETED.value, "completed"]:
                logger.info(f"[RENDER-SKIP] Job {job_id} is already COMPLETED. Skipping render pipeline.")
                return

            asset_res = await init_session.execute(select(VideoAsset).where(VideoAsset.id == b_job.asset_id))
            b_asset = asset_res.scalar_one_or_none()
            if not b_asset:
                return

            seg_res = await init_session.execute(
                select(VideoTranslationSegment)
                .where(VideoTranslationSegment.job_id == job_id)
                .order_by(VideoTranslationSegment.segment_number)
            )
            raw_segments = seg_res.scalars().all()
            
            # Extract lightweight dictionaries to avoid holding stale ORM instances across commits
            segments_data = [
                {
                    "id": s.id,
                    "segment_number": s.segment_number,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "original_text": s.original_text,
                    "translated_text": s.translated_text,
                    "tts_audio_path": s.tts_audio_path,
                    "tts_audio_duration": s.tts_audio_duration or 0.0,
                    "synced_audio_path": s.synced_audio_path,
                    "speaker_id": s.speaker_id,
                    "character_id": s.character_id,
                    "voice_provider": s.voice_provider,
                    "voice_id": s.voice_id,
                    "original_start": s.original_start if s.original_start is not None else s.start_time,
                    "original_end": s.original_end if s.original_end is not None else s.end_time,
                }
                for s in raw_segments
            ]

            job_dir = settings.STORAGE_ROOT / "translator" / "jobs" / job_id
            tts_dir = job_dir / "tts"
            sync_dir = job_dir / "synced"
            tts_dir.mkdir(parents=True, exist_ok=True)
            sync_dir.mkdir(parents=True, exist_ok=True)

            registry = get_registry()
            audio_provider = registry.get_audio(b_job.audio_provider_id or "edge_tts")
            if not audio_provider:
                await init_session.execute(
                    update(VideoTranslationJob)
                    .where(VideoTranslationJob.id == job_id)
                    .values(
                        status=TranslationJobStatus.FAILED.value,
                        stage="FAILED",
                        error_message=f"❌ Audio provider '{b_job.audio_provider_id}' không được hỗ trợ.",
                    )
                )
                await init_session.commit()
                return

            # Pre-scan existing valid TTS clips with sidecar metadata verification
            def _is_tts_cache_valid(s_dict: dict, tts_dir_p: Path) -> bool:
                audio_f = tts_dir_p / f"seg_{s_dict['segment_number']:03d}.wav"
                meta_f = tts_dir_p / f"seg_{s_dict['segment_number']:03d}.meta.json"
                if not audio_f.exists() or audio_f.stat().st_size == 0:
                    return False
                if meta_f.exists():
                    try:
                        with open(meta_f, "r", encoding="utf-8") as mf:
                            m_data = json.load(mf)
                        if m_data.get("voice_id") != s_dict.get("voice_id") or m_data.get("translated_text") != s_dict.get("translated_text"):
                            return False
                    except Exception:
                        return False
                return True

            existing_tts_count = 0
            invalidated_on_scan = []
            for s in segments_data:
                seg_f = tts_dir / f"seg_{s['segment_number']:03d}.wav"
                seg_meta = tts_dir / f"seg_{s['segment_number']:03d}.meta.json"
                if _is_tts_cache_valid(s, tts_dir):
                    existing_tts_count += 1
                elif seg_f.exists():
                    invalidated_on_scan.append(s["segment_number"])
                    seg_f.unlink(missing_ok=True)
                    seg_meta.unlink(missing_ok=True)
            if invalidated_on_scan:
                log_job_event(job_id, "TTS_CACHE", f"[TTS_CACHE] Invalidating segments: {invalidated_on_scan}")

            initial_tts_pct = round((existing_tts_count / len(segments_data)) * 100.0, 1) if segments_data else 0.0

            # 1. TTS Generation Stage
            current_stage = "GENERATING_TTS"
            await init_session.execute(
                update(VideoTranslationJob)
                .where(VideoTranslationJob.id == job_id)
                .values(
                    status=TranslationJobStatus.GENERATING_TTS.value,
                    stage="GENERATING_TTS",
                    current_step=f"Đang tạo giọng đọc TTS ({existing_tts_count}/{len(segments_data)})",
                    total_segments_count=len(segments_data),
                    completed_segments_count=existing_tts_count,
                    stage_progress_pct=initial_tts_pct,
                    overall_progress_pct=calculate_overall_progress("GENERATING_TTS", initial_tts_pct),
                )
            )
            await init_session.commit()
            log_job_event(job_id, "GENERATING_TTS", f"Starting TTS generation for {len(segments_data)} segments ({existing_tts_count} cached)...")

            voice_id = b_job.voice_id or "vi-VN-HoaiMyNeural"
            asset_file_path = Path(b_asset.file_path)
            audio_provider_id = b_job.audio_provider_id
            original_audio_mode = b_job.original_audio_mode

        # Step 1: TTS Loop with short atomic transactions
        for idx, seg in enumerate(segments_data, start=1):
            if is_job_cancelled(job_id) or cancel_evt.is_set():
                logger.info(f"[JOB-CANCEL] Job {job_id} cancelled during TTS generation. Stopping pipeline.")
                return

            seg_tts_path = tts_dir / f"seg_{seg['segment_number']:03d}.wav"
            seg_meta_path = tts_dir / f"seg_{seg['segment_number']:03d}.meta.json"

            try:
                reused = _is_tts_cache_valid(seg, tts_dir)
                if not reused:
                    log_job_event(job_id, "TTS", f"[TTS] Regenerating segments: [{seg['segment_number']}]")
                    log_job_event(job_id, "GENERATING_TTS", f"Generating TTS for segment #{seg['segment_number']}/{len(segments_data)}")
                    segment_provider = registry.get_audio(seg.get("voice_provider") or audio_provider_id) or audio_provider
                    res = await segment_provider.generate_audio(
                        text=seg["translated_text"] or "",
                        voice_id=seg.get("voice_id") or voice_id,
                        output_path=seg_tts_path,
                    )
                    if not res.success or not seg_tts_path.exists():
                        logger.warning(f"[VIDEO-SYNC] TTS failed for Segment #{seg['segment_number']}: {res.error_message}")
                        log_job_event(job_id, "GENERATING_TTS", f"[VIDEO-SYNC] ⚠️ Segment #{seg['segment_number']} TTS failed: {res.error_message}. Fallback to silence.")
                        seg["tts_audio_path"] = None
                        seg["tts_audio_duration"] = 0.0
                        seg["status"] = "failed"
                    else:
                        reused = True
                        try:
                            with open(seg_meta_path, "w", encoding="utf-8") as mf:
                                json.dump({
                                    "voice_id": seg.get("voice_id") or voice_id,
                                    "voice_provider": seg.get("voice_provider") or audio_provider_id,
                                    "translated_text": seg.get("translated_text"),
                                }, mf)
                        except Exception as me:
                            logger.warning(f"Failed to write TTS meta: {me}")
                if reused and seg_tts_path.exists():
                    dur = await probe_duration_async(seg_tts_path)
                    seg["tts_audio_path"] = str(seg_tts_path)
                    seg["tts_audio_duration"] = dur
                    seg["tts_duration"] = dur
                    seg["status"] = "tts_completed"
                    if not seg_meta_path.exists():
                        try:
                            with open(seg_meta_path, "w", encoding="utf-8") as mf:
                                json.dump({
                                    "voice_id": seg.get("voice_id") or voice_id,
                                    "voice_provider": seg.get("voice_provider") or audio_provider_id,
                                    "translated_text": seg.get("translated_text"),
                                }, mf)
                        except Exception:
                            pass
            except Exception as tts_err:
                logger.warning(f"[VIDEO-SYNC] TTS exception for Segment #{seg['segment_number']}: {str(tts_err)}")
                log_job_event(job_id, "GENERATING_TTS", f"[VIDEO-SYNC] ⚠️ Segment #{seg['segment_number']} TTS exception: {str(tts_err)}. Fallback to silence.")
                seg["tts_audio_path"] = None
                seg["tts_audio_duration"] = 0.0
                seg["status"] = "failed"

            # Atomic DB update for segment & job progress
            async with async_session_factory() as step_session:
                upd_res = await step_session.execute(
                    update(VideoTranslationSegment)
                    .where(VideoTranslationSegment.id == seg["id"])
                    .where(VideoTranslationSegment.job_id == job_id)
                    .values(
                        tts_audio_path=seg["tts_audio_path"],
                        tts_audio_duration=seg["tts_audio_duration"],
                        tts_duration=seg.get("tts_duration", 0.0),
                        status=seg["status"],
                    )
                )
                if upd_res.rowcount == 0:
                    logger.warning(f"[SEGMENT_UPDATE] Segment #{seg['id']} no longer exists in DB for job {job_id}.")

                pct = round((idx / len(segments_data)) * 100.0, 1)
                await step_session.execute(
                    update(VideoTranslationJob)
                    .where(VideoTranslationJob.id == job_id)
                    .values(
                        completed_segments_count=idx,
                        stage_progress_pct=pct,
                        overall_progress_pct=calculate_overall_progress("GENERATING_TTS", pct),
                        current_step=f"Đang tạo giọng đọc TTS ({idx}/{len(segments_data)})",
                    )
                )
                await step_session.commit()

        # Check if user has already confirmed character/voice review or audio scheduling
        snap = {}
        if b_job.settings_snapshot_json:
            try:
                snap = json.loads(b_job.settings_snapshot_json)
            except Exception:
                snap = {}

        is_review_confirmed = bool(
            snap.get("review_confirmed")
            or snap.get("audio_schedule_confirmed")
            or b_job.last_checkpoint_stage in ["CHARACTER_VOICE_REVIEW_DONE", "TTS_DONE", "AUDIO_SYNC_DONE"]
        )

        from app.services.video_translator.timeline_scheduler import SchedulePolicy, schedule_segments
        policy = SchedulePolicy(
            max_reschedule_seconds=60.0,
            max_tempo=2.0,
        ) if is_review_confirmed else SchedulePolicy()

        log_job_event(job_id, "AUDIO_SCHEDULE", "[AUDIO_SCHEDULE] Validation started")
        video_dur = float(b_asset.duration or await probe_duration_async(asset_file_path))
        schedule_result = schedule_segments(
            segments_data,
            video_dur,
            policy
        )

        # Attempt auto-resolution if same-voice overlap conflict is found
        if schedule_result.requires_review and schedule_result.unresolved_conflicts:
            log_job_event(job_id, "AUDIO_SCHEDULE", f"[AUDIO_SCHEDULE] Conflicts found: {schedule_result.unresolved_conflicts}")
            async with async_session_factory() as resolve_session:
                pool_rows = (await resolve_session.execute(
                    select(VoicePoolEntry).where(VoicePoolEntry.enabled.is_(True))
                )).scalars().all()
                pool = [{"provider": p.provider, "voice_id": p.voice_id, "gender": p.gender, "language": p.language} for p in pool_rows]

                profiles_rows = (await resolve_session.execute(
                    select(CharacterVoiceProfile).where(CharacterVoiceProfile.project_id == b_job.project_id)
                )).scalars().all()
                confirmed_char_ids = {p.character_id for p in profiles_rows if p.confirmed_by_user}

                affected_seg_nums = []
                seg_dict_by_id = {s["id"]: s for s in segments_data}
                for conflict in schedule_result.unresolved_conflicts:
                    cand_id = conflict.get("segment_id")
                    prior_id = conflict.get("with")
                    for sid in [cand_id, prior_id]:
                        target_s = seg_dict_by_id.get(sid)
                        if not target_s:
                            continue
                        if target_s.get("character_id") in confirmed_char_ids:
                            continue
                        curr_v = target_s.get("voice_id")
                        alt_choices = [v for v in pool if v.get("voice_id") != curr_v]
                        if alt_choices:
                            chosen = alt_choices[0]
                            target_s["voice_id"] = chosen["voice_id"]
                            target_s["voice_provider"] = chosen["provider"]
                            affected_seg_nums.append(target_s["segment_number"])
                            s_f = tts_dir / f"seg_{target_s['segment_number']:03d}.wav"
                            s_m = tts_dir / f"seg_{target_s['segment_number']:03d}.meta.json"
                            s_f.unlink(missing_ok=True)
                            s_m.unlink(missing_ok=True)
                            log_job_event(job_id, "TTS_CACHE", f"[TTS_CACHE] Invalidating segments: [{target_s['segment_number']}]")
                            log_job_event(job_id, "TTS", f"[TTS] Regenerating segments: [{target_s['segment_number']}]")
                            sp = registry.get_audio(chosen["provider"]) or audio_provider
                            await sp.generate_audio(text=target_s["translated_text"] or "", voice_id=chosen["voice_id"], output_path=s_f)
                            if s_f.exists():
                                dur = await probe_duration_async(s_f)
                                target_s["tts_audio_path"] = str(s_f)
                                target_s["tts_audio_duration"] = dur
                                target_s["tts_duration"] = dur
                                try:
                                    with open(s_m, "w", encoding="utf-8") as mf:
                                        json.dump({"voice_id": chosen["voice_id"], "voice_provider": chosen["provider"], "translated_text": target_s["translated_text"]}, mf)
                                except Exception:
                                    pass
                            await resolve_session.execute(
                                update(VideoTranslationSegment)
                                .where(VideoTranslationSegment.id == sid)
                                .values(
                                    voice_id=chosen["voice_id"],
                                    voice_provider=chosen["provider"],
                                    tts_audio_path=target_s["tts_audio_path"],
                                    tts_audio_duration=target_s["tts_audio_duration"],
                                    tts_duration=target_s["tts_duration"],
                                )
                            )
                            break
                await resolve_session.commit()

                if affected_seg_nums:
                    schedule_result = schedule_segments(segments_data, video_dur, policy)
                    if not schedule_result.requires_review:
                        log_job_event(job_id, "AUDIO_SCHEDULE", f"[AUDIO_SCHEDULE] Conflict resolved for segments {affected_seg_nums}")

        async with async_session_factory() as schedule_session:
            for scheduled in schedule_result.segments:
                seg = next(item for item in segments_data if item["id"] == scheduled["id"])
                seg.update(scheduled)
                await schedule_session.execute(
                    update(VideoTranslationSegment)
                    .where(VideoTranslationSegment.id == seg["id"])
                    .values(
                        scheduled_start=seg["scheduled_start"],
                        scheduled_end=seg["scheduled_end"],
                        overlap_with=seg["overlap_with"],
                        schedule_action=seg["schedule_action"],
                    )
                )

            # If schedule requires review, proceed if user already confirmed or auto-confirm enabled
            if schedule_result.requires_review:
                if is_review_confirmed or auto_confirm_voice:
                    log_job_event(job_id, "AUDIO_SCHEDULE", f"[AUDIO_SCHEDULE] User confirmed or auto-confirm enabled. Proceeding with schedule: {schedule_result.unresolved_conflicts}")
                else:
                    await schedule_session.execute(
                        update(VideoTranslationJob)
                        .where(VideoTranslationJob.id == job_id)
                        .values(
                            status=TranslationJobStatus.NEEDS_REVIEW.value,
                            stage="AUDIO_SCHEDULE_REVIEW",
                            current_step="Không thể xếp lịch TTS an toàn do xung đột cùng giọng đọc (same-voice overlap); cần kiểm tra thủ công",
                        )
                    )
                    log_job_event(job_id, "NEEDS_REVIEW", f"[NEEDS_REVIEW] Waiting for user changes: {schedule_result.unresolved_conflicts}")
                    await schedule_session.commit()
                    stop_job_heartbeat(job_id)
                    return

            # Proceed if and only if schedule passed or user confirmed
            log_job_event(job_id, "AUDIO_SCHEDULE", "[AUDIO_SCHEDULE] Final validation passed")
            await schedule_session.execute(
                update(VideoTranslationJob)
                .where(VideoTranslationJob.id == job_id)
                .values(
                    stage="SYNCING_AUDIO",
                    last_checkpoint_stage="AUDIO_SYNC_DONE",
                )
            )
            await schedule_session.commit()

        # Validation Gate & Auto-Resolution before Audio Sync:
        sorted_chk = sorted(segments_data, key=lambda s: float(s.get("scheduled_start", 0.0)))
        adjusted_any = False
        async with async_session_factory() as adjust_session:
            for p, l_seg in enumerate(sorted_chk):
                l_end = float(l_seg.get("scheduled_end", 0.0))
                l_vox = l_seg.get("voice_id")
                if not l_vox:
                    continue
                for r_seg in sorted_chk[p + 1:]:
                    r_start = float(r_seg.get("scheduled_start", 0.0))
                    if r_start >= l_end - 0.001:
                        break
                    if l_vox == r_seg.get("voice_id"):
                        overlap_amount = l_end - r_start
                        if overlap_amount > 0:
                            l_start = float(l_seg.get("scheduled_start", 0.0))
                            if (r_start - l_start) >= 0.4:
                                l_seg["scheduled_end"] = round(r_start, 3)
                                l_end = r_start
                            else:
                                r_dur = max(0.1, float(r_seg.get("scheduled_end", 0.0)) - r_start)
                                r_seg["scheduled_start"] = round(l_end, 3)
                                r_seg["scheduled_end"] = round(l_end + r_dur, 3)

                            await adjust_session.execute(
                                update(VideoTranslationSegment)
                                .where(VideoTranslationSegment.id == l_seg["id"])
                                .values(scheduled_end=l_seg["scheduled_end"])
                            )
                            await adjust_session.execute(
                                update(VideoTranslationSegment)
                                .where(VideoTranslationSegment.id == r_seg["id"])
                                .values(
                                    scheduled_start=r_seg["scheduled_start"],
                                    scheduled_end=r_seg["scheduled_end"],
                                )
                            )
                            adjusted_any = True
            if adjusted_any:
                await adjust_session.commit()

        # Re-check after auto-resolution
        sorted_chk = sorted(segments_data, key=lambda s: float(s.get("scheduled_start", 0.0)))
        has_same_voice_overlap = False
        for p, l_seg in enumerate(sorted_chk):
            l_end = float(l_seg.get("scheduled_end", 0.0))
            l_vox = l_seg.get("voice_id")
            for r_seg in sorted_chk[p + 1:]:
                r_start = float(r_seg.get("scheduled_start", 0.0))
                if r_start >= l_end - 0.001:
                    break
                if l_vox and l_vox == r_seg.get("voice_id"):
                    has_same_voice_overlap = True
                    break
            if has_same_voice_overlap:
                break

        if has_same_voice_overlap and not is_review_confirmed and not auto_confirm_voice:
            logger.error(f"[PRE-SYNC-GATE] Job {job_id} failed pre-sync gate: same-voice overlap detected.")
            async with async_session_factory() as gate_session:
                await gate_session.execute(
                    update(VideoTranslationJob)
                    .where(VideoTranslationJob.id == job_id)
                    .values(
                        status=TranslationJobStatus.NEEDS_REVIEW.value,
                        stage="AUDIO_SCHEDULE_REVIEW",
                        current_step="Phát hiện cùng giọng đọc overlap trước Audio Sync",
                    )
                )
                await gate_session.commit()
            stop_job_heartbeat(job_id)
            return

        # Step 2: Audio Synchronization Stage
        current_stage = "SYNCING_AUDIO"
        async with async_session_factory() as sync_init_session:
            await sync_init_session.execute(
                update(VideoTranslationJob)
                .where(VideoTranslationJob.id == job_id)
                .values(
                    status=TranslationJobStatus.SYNCING_AUDIO.value,
                    stage="SYNCING_AUDIO",
                    current_step="Đang đồng bộ Audio theo mốc thời gian",
                    stage_progress_pct=0.0,
                    overall_progress_pct=calculate_overall_progress("SYNCING_AUDIO", 0.0),
                )
            )
            await sync_init_session.commit()
        log_job_event(job_id, "SYNC", "[SYNC] Starting audio sync")

        for idx, seg in enumerate(segments_data, start=1):
            if is_job_cancelled(job_id) or cancel_evt.is_set():
                logger.info(f"[JOB-CANCEL] Job {job_id} cancelled during Audio Sync. Stopping pipeline.")
                return

            target_dur = max(0.1, seg["scheduled_end"] - seg["scheduled_start"])
            synced_path = sync_dir / f"seg_{seg['segment_number']:03d}_synced.wav"

            def on_sync_progress(stats: dict):
                asyncio.create_task(_update_ffmpeg_stats(job_id, "SYNCING_AUDIO", stats.get("progress_pct", 0.0), stats.get("pid"), stats))

            def on_sync_pid(pid: int):
                asyncio.create_task(_update_pid(job_id, pid))

            if not seg.get("tts_audio_path") or not Path(seg["tts_audio_path"]).exists():
                logger.warning(f"[VIDEO-SYNC] Segment #{seg['segment_number']} TTS audio missing, skipping time-stretch.")
                seg["synced_audio_path"] = None
            else:
                await sync_and_stretch_audio(
                    Path(seg["tts_audio_path"]),
                    target_duration=target_dur,
                    output_synced_path=synced_path,
                    job_id=job_id,
                    on_progress=on_sync_progress,
                    on_pid=on_sync_pid,
                )
                seg["synced_audio_path"] = str(synced_path)

            # Atomic DB update
            async with async_session_factory() as step_session:
                await step_session.execute(
                    update(VideoTranslationSegment)
                    .where(VideoTranslationSegment.id == seg["id"])
                    .where(VideoTranslationSegment.job_id == job_id)
                    .values(synced_audio_path=seg["synced_audio_path"])
                )
                sync_pct = round((idx / len(segments_data)) * 100.0, 1)
                await step_session.execute(
                    update(VideoTranslationJob)
                    .where(VideoTranslationJob.id == job_id)
                    .values(
                        stage_progress_pct=sync_pct,
                        overall_progress_pct=calculate_overall_progress("SYNCING_AUDIO", sync_pct),
                    )
                )
                await step_session.commit()

        # Step 3: Render Final Video Stage
        current_stage = "RENDERING"
        async with async_session_factory() as render_init_session:
            await render_init_session.execute(
                update(VideoTranslationJob)
                .where(VideoTranslationJob.id == job_id)
                .values(
                    status=TranslationJobStatus.RENDERING.value,
                    stage="RENDERING",
                    current_step="Đang render video lồng tiếng bằng FFmpeg",
                    stage_progress_pct=0.0,
                    overall_progress_pct=calculate_overall_progress("RENDERING", 0.0),
                )
            )
            await render_init_session.commit()
        log_job_event(job_id, "RENDERING", "Starting final FFmpeg video render...")

        if is_job_cancelled(job_id) or cancel_evt.is_set():
            logger.info(f"[JOB-CANCEL] Job {job_id} cancelled before render. Stopping pipeline.")
            return

        def on_render_progress(stats: dict):
            asyncio.create_task(_update_ffmpeg_stats(job_id, "RENDERING", stats.get("progress_pct", 0.0), stats.get("pid"), stats))

        def on_render_pid(pid: int):
            asyncio.create_task(_update_pid(job_id, pid))

        final_video_path = job_dir / "final_dubbed_video.mp4"

        # Query fresh ORM instances for rendering function
        async with async_session_factory() as render_session:
            seg_render_res = await render_session.execute(
                select(VideoTranslationSegment)
                .where(VideoTranslationSegment.job_id == job_id)
                .order_by(VideoTranslationSegment.segment_number)
            )
            db_render_segments = seg_render_res.scalars().all()

            # Final Pre-Render Validation Gate:
            sorted_render_chk = sorted(db_render_segments, key=lambda s: float(s.scheduled_start if s.scheduled_start is not None else s.start_time))
            render_overlap_found = False
            overlap_detail = ""
            for p, l_seg in enumerate(sorted_render_chk):
                l_end = float(l_seg.scheduled_end if l_seg.scheduled_end is not None else l_seg.end_time)
                l_vox = l_seg.voice_id
                for r_seg in sorted_render_chk[p + 1:]:
                    r_start = float(r_seg.scheduled_start if r_seg.scheduled_start is not None else r_seg.start_time)
                    if r_start >= l_end - 0.001:
                        break
                    if l_vox and l_vox == r_seg.voice_id:
                        render_overlap_found = True
                        overlap_detail = f"Segment #{l_seg.segment_number} và #{r_seg.segment_number} cùng sử dụng voice '{l_vox}'"
                        logger.error(f"[PRE-RENDER-GATE] Job {job_id}: {overlap_detail}")
                        break
                if render_overlap_found:
                    break

            if render_overlap_found:
                logger.error(f"[PRE-RENDER-GATE] Job {job_id} aborted render: same_voice_overlap detected.")
                async with async_session_factory() as gate_session:
                    await gate_session.execute(
                        update(VideoTranslationJob)
                        .where(VideoTranslationJob.id == job_id)
                        .values(
                            status=TranslationJobStatus.NEEDS_REVIEW.value,
                            stage="AUDIO_SCHEDULE_REVIEW",
                            current_step=f"Phát hiện xung đột cùng giọng đọc overlap trước Render FFmpeg: {overlap_detail}",
                        )
                    )
                    await gate_session.commit()
                stop_job_heartbeat(job_id)
                return

            log_job_event(job_id, "RENDER", "[RENDER] Starting final render")
            rendered_path = await render_dubbed_video(
                video_path=asset_file_path,
                segments=db_render_segments,
                original_audio_mode=original_audio_mode,
                output_video_path=final_video_path,
                work_dir=job_dir,
                job_id=job_id,
                on_progress=on_render_progress,
                on_pid=on_render_pid,
            )

        # Apply Watermark if enabled
        async with async_session_factory() as wm_session:
            job_res = await wm_session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
            job_obj = job_res.scalar_one_or_none()

            if job_obj and job_obj.watermark_enabled:
                log_job_event(job_id, "WATERMARK", f"Applying {job_obj.watermark_type} watermark ({job_obj.watermark_position})...")
                wm_config = WatermarkConfig(
                    enabled=job_obj.watermark_enabled,
                    type=WatermarkType(job_obj.watermark_type or "image"),
                    image_path=job_obj.watermark_image_path,
                    text=job_obj.watermark_text,
                    position=WatermarkPosition.normalize(job_obj.watermark_position or "bottom_right"),
                    scale=job_obj.watermark_scale or 0.20,
                    opacity=job_obj.watermark_opacity or 0.80,
                    margin=job_obj.watermark_margin or 20,
                    font_size=job_obj.watermark_font_size or 32,
                )

                watermarked_final_path = job_dir / "final_dubbed_watermarked_video.mp4"
                rendered_path = await WatermarkService.apply_watermark(
                    input_video_path=rendered_path,
                    output_video_path=watermarked_final_path,
                    config=wm_config,
                    job_id=job_id,
                )
                final_video_path = rendered_path

        # Strict FFprobe Validation
        meta = await get_video_metadata_async(rendered_path)
        if not meta.get("has_audio"):
            raise RuntimeError("❌ Output validation failed: Video thành phẩm không có audio stream.")
        if meta.get("duration", 0.0) <= 0.0:
            raise RuntimeError("❌ Output validation failed: Thời lượng video thành phẩm = 0s.")

        log_job_event(
            job_id,
            "VALIDATION",
            f"FFprobe Validation Passed: Duration={meta['duration']}s, Resolution={meta['width']}x{meta['height']}, Audio=True"
        )

        # Upload final video to Cloudflare R2 / Storage Service
        r2_key = f"translator/jobs/{job_id}/final_dubbed_video.mp4"
        object_key, output_url = await storage_service.upload_file(
            final_video_path,
            r2_key,
            content_type="video/mp4"
        )

        # Clean intermediate temporary files via unified FileCleanupService
        try:
            from app.services.cleanup_service import FileCleanupService
            clean_res = FileCleanupService.cleanup_job_workspace(job_id, keep_logs=True, keep_final_video=True)
            log_job_event(job_id, "CLEANUP", f"Intermediate files purged ({clean_res['deleted_files']} files, {clean_res['bytes_freed'] / (1024*1024):.2f} MB freed).")
        except Exception as clean_err:
            logger.warning("Error cleaning intermediate files", error=str(clean_err), job_id=job_id)

        async with async_session_factory() as final_session:
            now_dt = datetime.now(timezone.utc).replace(tzinfo=None)
            await final_session.execute(
                update(VideoTranslationJob)
                .where(VideoTranslationJob.id == job_id)
                .values(
                    status=TranslationJobStatus.COMPLETED.value,
                    stage="COMPLETED",
                    current_step="Hoàn tất lồng tiếng video",
                    stage_progress_pct=100.0,
                    overall_progress_pct=100.0,
                    output_video_path=str(final_video_path),
                    r2_key=object_key,
                    output_url=output_url,
                    is_cleaned=True,
                    pid=None,
                    last_checkpoint_stage="RENDER_DONE",
                    last_checkpoint_at=now_dt,
                    studio_state_json=json.dumps({"active_step": "completed", "active_tab": "overview"}),
                    updated_at=now_dt,
                )
            )
            await final_session.commit()
        log_job_event(job_id, "COMPLETED", f"Final video ready at {output_url or final_video_path}")

        try:
            from app.services.thumbnail_service import ThumbnailService

            async with async_session_factory() as thumb_session:
                job_row = (
                    await thumb_session.execute(
                        select(VideoTranslationJob).where(VideoTranslationJob.id == job_id)
                    )
                ).scalar_one_or_none()
                if job_row and ThumbnailService.snapshot_wants_thumbnail(
                    json.loads(job_row.settings_snapshot_json or "{}")
                    if job_row.settings_snapshot_json
                    else {}
                ):
                    await thumb_session.execute(
                        update(VideoTranslationJob)
                        .where(VideoTranslationJob.id == job_id)
                        .values(current_step="Đang tạo Thumbnail AI…")
                    )
                    await thumb_session.commit()
                    thumb_res = await ThumbnailService.maybe_generate_for_job(thumb_session, job_row)
                    log_job_event(
                        job_id,
                        "THUMBNAIL",
                        f"Auto thumbnail: generated={thumb_res.get('generated')} url={thumb_res.get('thumbnail_url')} err={thumb_res.get('error')}",
                    )
                    if thumb_res.get("thumbnail_url"):
                        await thumb_session.execute(
                            update(VideoTranslationJob)
                            .where(VideoTranslationJob.id == job_id)
                            .values(
                                thumbnail_url=thumb_res["thumbnail_url"],
                                current_step="Hoàn tất lồng tiếng video",
                            )
                        )
                        await thumb_session.commit()
        except Exception as thumb_err:
            logger.warning("Auto thumbnail after render failed", job_id=job_id, error=str(thumb_err))
            log_job_event(job_id, "THUMBNAIL", f"Auto thumbnail skipped: {thumb_err}")

    except Exception as e:
        tb_str = traceback.format_exc()
        err_name = type(e).__name__
        err_msg = str(e) or repr(e)
        full_err_log = f"Error: {err_name}: {err_msg}\nStage: {current_stage}\nStack:\n{tb_str}"

        db_err_detail = f"{err_name}: {err_msg}"
        if isinstance(e, FFmpegExecutionError):
            full_err_log += f"\nFFmpeg Exit Code: {e.exit_code}\nFFmpeg Stderr: {e.stderr_text}\nCommand: {' '.join(e.cmd)}"
            if e.stderr_text:
                db_err_detail += f" | Stderr: {e.stderr_text[:500]}"

        logger.exception("Render dubbed video failed", job_id=job_id)
        log_job_event(job_id, "FAILED", f"Render Exception:\n{full_err_log}")

        async with async_session_factory() as fail_session:
            await fail_session.execute(
                update(VideoTranslationJob)
                .where(VideoTranslationJob.id == job_id)
                .values(
                    status=TranslationJobStatus.FAILED.value,
                    stage="FAILED",
                    current_step=f"Lỗi tại stage {current_stage}: {err_name}",
                    error_message=db_err_detail[:1000],
                    pid=None,
                    updated_at=datetime.now(timezone.utc).replace(tzinfo=None),
                )
            )
            await fail_session.commit()
    finally:
        _active_render_jobs.discard(job_id)
        stop_job_heartbeat(job_id)



@router.post("/jobs/{job_id}/render", response_model=dict)
async def render_final_translated_video(
    job_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Execute Phase 2 (TTS Generation -> Audio Sync -> FFmpeg Render Final Video)."""
    res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Job không tồn tại.")
    if job.status in [TranslationJobStatus.COMPLETED.value, "completed"]:
        return {"success": True, "data": {"rendering": False, "job_id": job_id, "message": "Job đã hoàn tất."}}

    background_tasks.add_task(execute_job_render_pipeline, job_id)
    return {"success": True, "data": {"rendering": True, "job_id": job_id}}


@router.post("/jobs/{job_id}/cancel", response_model=dict)
async def cancel_job_api(job_id: str, session: AsyncSession = Depends(get_session)):
    """Cancel a running translation job and terminate FFmpeg subprocess."""
    signal_job_cancellation(job_id)

    res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Job không tồn tại.")

    stop_job_heartbeat(job_id)

    if job.pid:
        try:
            os.kill(job.pid, signal.SIGTERM)
            log_job_event(job_id, "CANCELLED", f"Killed active FFmpeg process PID {job.pid}")
        except Exception as e:
            log_job_event(job_id, "CANCELLED", f"Attempted killing PID {job.pid}: {str(e)}")

    job.status = TranslationJobStatus.FAILED.value
    job.stage = "CANCELLED"
    job.current_step = "Đã hủy bởi người dùng"
    job.error_message = "Job đã bị hủy."
    job.pid = None
    await session.commit()

    return {"success": True, "data": {"cancelled": True, "job_id": job_id}}


@router.post("/jobs/{job_id}/retry", response_model=dict)
async def smart_retry_job_api(
    job_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Smart Retry: Resume job execution from failed/stalled stage without re-running finished steps."""
    signal_job_cancellation(job_id)

    res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Job không tồn tại.")
    if job.status in [TranslationJobStatus.COMPLETED.value, "completed"]:
        return {"success": True, "data": {"started": False, "job_id": job_id, "message": "Job đã hoàn tất."}}

    checkpoint = job.last_checkpoint_stage or job.stage or "CREATED"
    phase2_checkpoints = [
        "TRANSLATION_DONE", "TRANSLATION_CONFIRMED", "SEGMENT_EDITING_DONE",
        "CHARACTER_VOICE_REVIEW_DONE", "TTS_DONE", "AUDIO_SYNC_DONE",
    ]
    phase2_stages = [
        "DUB", "GENERATING_TTS", "AUDIO_SCHEDULE_REVIEW", "CHARACTER_VOICE_REVIEW",
        "SYNCING_AUDIO", "PRODUCE", "RENDERING",
    ]

    # Check if translated segments already exist in DB
    seg_res = await session.execute(
        select(VideoTranslationSegment)
        .where(VideoTranslationSegment.job_id == job_id)
        .limit(1)
    )
    has_segments = seg_res.scalar_one_or_none() is not None

    if has_segments and (checkpoint in phase2_checkpoints or job.stage in phase2_stages or job.status == TranslationJobStatus.SEGMENT_EDITING.value):
        job.error_message = None
        job.status = TranslationJobStatus.GENERATING_TTS.value
        job.stage = "DUB"
        job.current_step = "Thực hiện Smart Retry Phase 2 (TTS & Dubbing)..."
        job.pid = None
        await session.commit()
        log_job_event(job_id, "RETRY", "Smart Retry resuming Phase 2 without re-translating existing segments.")
        background_tasks.add_task(execute_job_render_pipeline, job_id)
        return {"success": True, "data": {"started": True, "job_id": job_id, "phase": 2}}

    # Reset job status to CREATED for retry
    job.error_message = None
    job.status = TranslationJobStatus.CREATED.value
    job.stage = "QUEUED"
    job.current_step = "Thực hiện Smart Retry..."
    job.pid = None
    await session.commit()
    log_job_event(job_id, "RETRY", "Smart Retry initiated by user.")

    # Trigger restart Phase 1
    return await start_translation_pipeline(job_id, background_tasks, session)


# ── Unified 6-Stage Workflow & Glossary Routes ──────────────────────

from app.workflow.workflow_engine import WorkflowEngine
from app.services.glossary_service import (
    GlossaryConflictError,
    create_glossary_entry,
    serialize_glossary_entry,
    update_glossary_entry,
)
from app.models.workflow_engine import (
    ProjectGlossary,
    SpeakerVoiceMapping,
    CharacterVoiceProfile,
    VoicePoolEntry,
    WorkflowExecution,
    WorkflowStageExecution,
    WorkflowStepExecution,
)

_global_workflow_engine = WorkflowEngine()


class StartWorkflowRequest(BaseModel):
    video_url: Optional[str] = Field(None, description="Source video URL")
    video_path: Optional[str] = Field(None, description="Local source video file path")
    has_upload_file: Optional[bool] = Field(False, description="Whether a local video file has been selected in UI")
    target_language: Optional[str] = Field("vi", description="Target translation language")
    audio_provider_id: Optional[str] = Field("edge_tts", description="Audio TTS provider ID")
    llm_provider_id: Optional[str] = Field("gemini", description="LLM translation provider ID")
    voice_id: Optional[str] = Field(None, description="Voice model ID")
    auto_confirm_translation: Optional[bool] = Field(True, description="Automatically confirm translation text segments and proceed to TTS dubbing render")
    trim_filler_enabled: Optional[bool] = Field(True, description="Auto-trim intro/outro filler before STT")
    copyright_check_enabled: Optional[bool] = Field(True, description="Check copyright risk before STT (metadata + AcoustID)")
    watermark_enabled: Optional[bool] = Field(False, description="Enable watermark embedding")
    watermark_type: Optional[str] = Field("image", description="Watermark type: image or text")
    watermark_image_path: Optional[str] = Field(None, description="Watermark image path")
    watermark_text: Optional[str] = Field(None, description="Watermark text")
    watermark_position: Optional[str] = Field("bottom_right", description="Watermark position")
    watermark_scale: Optional[float] = Field(0.20, description="Watermark scale")
    watermark_opacity: Optional[float] = Field(0.80, description="Watermark opacity")
    watermark_margin: Optional[int] = Field(20, description="Watermark margin")
    watermark_font_size: Optional[int] = Field(32, description="Watermark font size")
    thumbnail_enabled: Optional[bool] = Field(False, description="Generate AI thumbnail after Produce")
    thumbnail_provider: Optional[str] = Field("pollinations", description="Image provider id")
    thumbnail_style: Optional[str] = Field("auto", description="Thumbnail visual style")
    thumbnail_custom_instruction: Optional[str] = Field(None, description="Extra thumbnail prompt")
    thumbnail_source: Optional[str] = Field("ai", description="ai or library")
    thumbnail_library_path: Optional[str] = Field(None, description="Selected default thumbnail file path")


async def _validate_project_exists(project_id: str, session: AsyncSession) -> Project:
    """Validate that project_id exists in the projects table, returning 404 if invalid or missing."""
    if not project_id or project_id == "default_project":
        raise HTTPException(
            status_code=404,
            detail={
                "error": "PROJECT_NOT_FOUND",
                "message": "Invalid project_id 'default_project'. Please create or select a valid project before running workflow.",
                "project_id": project_id,
            },
        )

    res = await session.execute(select(Project).where(Project.id == project_id))
    project = res.scalars().first()
    if not project:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "PROJECT_NOT_FOUND",
                "message": f"Project '{project_id}' does not exist in database.",
                "project_id": project_id,
            },
        )
    return project


@router.get("/projects/{project_id}/workflow-status", response_model=dict)
async def get_workflow_status_api(project_id: str, session: AsyncSession = Depends(get_session)):
    """Get complete 6-stage workflow execution status, current stage, steps, and QC reports."""
    await _validate_project_exists(project_id, session)

    # 1. Query latest active VideoTranslationJob for single-source-of-truth runtime status
    job_stmt = (
        select(VideoTranslationJob)
        .where((VideoTranslationJob.project_id == project_id) | (VideoTranslationJob.id == project_id))
        .order_by(VideoTranslationJob.created_at.desc())
    )
    job_res = await session.execute(job_stmt)
    job = job_res.scalars().first()

    stmt = select(WorkflowExecution).where(WorkflowExecution.project_id == project_id)
    res = await session.execute(stmt)
    wf_exec = res.scalars().first()

    STAGE_MAP = {
        "CREATED": ("INGEST", 1),
        "QUEUED": ("INGEST", 1),
        "INGEST": ("INGEST", 1),
        "EXTRACTING_AUDIO": ("INGEST", 1),
        "ANALYZE": ("ANALYZE", 2),
        "TRANSCRIBING": ("ANALYZE", 2),
        "STT": ("ANALYZE", 2),
        "TRANSLATE": ("TRANSLATE", 3),
        "TRANSLATING": ("TRANSLATE", 3),
        "SEGMENT_EDITING": ("TRANSLATE", 3),
        "CHARACTER_VOICE_REVIEW": ("TRANSLATE", 3),
        "DUB": ("DUB", 4),
        "GENERATING_TTS": ("DUB", 4),
        "AUDIO_SCHEDULE_REVIEW": ("DUB", 4),
        "TTS_DONE": ("DUB", 4),
        "SYNTHESIZING": ("DUB", 4),
        "SYNCING_AUDIO": ("DUB", 4),
        "AUDIO_SYNC_DONE": ("DUB", 4),
        "PRODUCE": ("PRODUCE", 5),
        "RENDERING": ("PRODUCE", 5),
        "RENDER_DONE": ("PRODUCE", 5),
        "PUBLISH": ("PUBLISH", 6),
        "PUBLISHING": ("PUBLISH", 6),
        "COMPLETED": ("PUBLISH", 6),
    }

    if job:
        await auto_confirm_and_start_render_if_needed(job.id)
        cur_stage_name, cur_stage_idx = STAGE_MAP.get(job.stage, ("INGEST", 1))

        if job.status == "completed":
            cur_stage_idx = 6
            cur_stage_name = "PUBLISH"

        all_stages = ["INGEST", "ANALYZE", "TRANSLATE", "DUB", "PRODUCE", "PUBLISH"]
        stages_data = []
        for idx, s_name in enumerate(all_stages, start=1):
            if job.status == "completed":
                st_status = "passed"
            elif idx < cur_stage_idx:
                st_status = "passed"
            elif idx == cur_stage_idx:
                if job.status == "failed":
                    st_status = "failed"
                elif job.status in ["segment_editing", "needs_review"]:
                    st_status = "needs_review"
                elif job.status == "paused":
                    st_status = "paused"
                elif job.status == "cancelled":
                    st_status = "cancelled"
                else:
                    st_status = "running"
            else:
                st_status = "pending"

            stages_data.append({
                "name": s_name,
                "status": st_status,
                "error": job.error_message if idx == cur_stage_idx and job.status == "failed" else None,
                "steps": [],
            })

        overall_status = "running" if job.status in [
            "extracting_audio", "stt", "translating", "generating_tts", "syncing_audio", "rendering"
        ] else job.status

        return {
            "success": True,
            "data": {
                "execution_id": wf_exec.id if wf_exec else job.id,
                "status": overall_status,
                "current_stage": cur_stage_name,
                "current_step": job.current_step or "Processing",
                "overall_progress_pct": job.overall_progress_pct or 0,
                "error_message": job.error_message,
                "stages": stages_data,
                "context": {"job_id": job.id},
            },
        }

    if not wf_exec:
        return {
            "success": True,
            "data": {
                "status": "not_started",
                "current_stage": "INGEST",
                "current_step": "import_video",
                "overall_progress_pct": 0,
                "stages": [
                    {"name": s, "status": "pending", "steps": []}
                    for s in ["INGEST", "ANALYZE", "TRANSLATE", "DUB", "PRODUCE", "PUBLISH"]
                ],
            },
        }

    stmt_stages = select(WorkflowStageExecution).where(WorkflowStageExecution.workflow_execution_id == wf_exec.id)
    stages_res = await session.execute(stmt_stages)
    stages_list = stages_res.scalars().all()

    stages_data = []
    passed_stages = 0

    for s_name in ["INGEST", "ANALYZE", "TRANSLATE", "DUB", "PRODUCE", "PUBLISH"]:
        match = next((st for st in stages_list if st.stage_name == s_name), None)
        if match:
            if match.status == "passed":
                passed_stages += 1

            stmt_steps = select(WorkflowStepExecution).where(WorkflowStepExecution.stage_execution_id == match.id)
            steps_res = await session.execute(stmt_steps)
            steps_list = steps_res.scalars().all()

            stages_data.append({
                "name": s_name,
                "status": match.status,
                "error": match.error,
                "qc_report": match.qc_report,
                "retry_count": match.retry_count,
                "progress_percentage": match.progress_percentage,
                "current_item": match.current_item,
                "total_items": match.total_items,
                "message": match.message,
                "steps": [
                    {
                        "name": step.step_name,
                        "status": step.status,
                        "error": step.error,
                        "retry_count": step.retry_count,
                    }
                    for step in steps_list
                ],
            })
        else:
            stages_data.append({"name": s_name, "status": "pending", "steps": []})

    overall_pct = int((passed_stages / 6.0) * 100)
    if wf_exec.status == "completed":
        overall_pct = 100

    return {
        "success": True,
        "data": {
            "execution_id": wf_exec.id,
            "status": wf_exec.status,
            "current_stage": wf_exec.current_stage,
            "current_step": wf_exec.current_step,
            "overall_progress_pct": overall_pct,
            "error_message": wf_exec.error_message,
            "stages": stages_data,
            "context": wf_exec.context_data,
        },
    }


@router.get("/projects/{project_id}/workflow-stream")
async def workflow_stream_api(project_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    """SSE endpoint for real-time unified workflow status updates."""
    await _validate_project_exists(project_id, session)

    async def event_generator():
        # Subscribe to workflow events
        queue = workflow_events.subscribe(project_id)
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                try:
                    # Wait for an event with a timeout to send keep-alives
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {
                        "event": "update",
                        "data": json.dumps(event)
                    }
                except asyncio.TimeoutError:
                    # Send a keep-alive ping to prevent connection drop
                    yield {
                        "event": "ping",
                        "data": "ping"
                    }
        except asyncio.CancelledError:
            pass
        finally:
            workflow_events.unsubscribe(project_id, queue)

    return EventSourceResponse(event_generator())


@router.post("/projects/{project_id}/workflow/preflight", response_model=dict)
async def preflight_workflow_api(
    project_id: str,
    payload: Optional[StartWorkflowRequest] = None,
    session: AsyncSession = Depends(get_session),
):
    """Run pre-flight checks before starting the 6-stage video translation workflow."""
    from app.services.preflight import run_video_translator_preflight

    await _validate_project_exists(project_id, session)

    p_res = await session.execute(select(Project).where(Project.id == project_id))
    project = p_res.scalar_one_or_none()
    proj_settings = (project.settings_json or {}) if project else {}

    wm_enabled = payload.watermark_enabled if (payload and payload.watermark_enabled is not None) else _parse_bool(proj_settings.get("watermark_enabled"), False)
    wm_type = (payload.watermark_type if (payload and payload.watermark_type) else None) or proj_settings.get("watermark_type", "image")
    wm_img_path = (payload.watermark_image_path if (payload and payload.watermark_image_path) else None) or proj_settings.get("watermark_image_path")
    wm_text = (payload.watermark_text if (payload and payload.watermark_text) else None) or proj_settings.get("watermark_text")

    # Fallback lookup from Project Asset table if watermark_image_path is missing
    if not wm_img_path and project_id and project_id != "default_project":
        asset_res = await session.execute(
            select(Asset)
            .where(Asset.project_id == project_id)
            .where(Asset.asset_type == "watermark_logo")
            .order_by(Asset.created_at.desc())
        )
        wm_asset = asset_res.scalars().first()
        if wm_asset and wm_asset.file_path:
            wm_img_path = wm_asset.file_path

    res = await run_video_translator_preflight(
        project_id=project_id,
        video_url=payload.video_url if payload else None,
        video_path=payload.video_path if payload else None,
        has_upload_file=payload.has_upload_file if payload else False,
        llm_provider_id=payload.llm_provider_id if payload and payload.llm_provider_id else "gemini",
        audio_provider_id=payload.audio_provider_id if payload and payload.audio_provider_id else "edge_tts",
        voice_id=payload.voice_id if payload else "vi-VN-HoaiMyNeural",
        target_language=payload.target_language if payload and payload.target_language else "vi",
        watermark_enabled=wm_enabled,
        watermark_type=wm_type,
        watermark_image_path=wm_img_path,
        watermark_text=wm_text,
        db=session,
    )

    return {"success": True, "data": res.model_dump()}


@router.post("/projects/{project_id}/workflow/start", response_model=dict)
async def start_workflow_api(
    project_id: str,
    payload: Optional[StartWorkflowRequest] = None,
    session: AsyncSession = Depends(get_session),
):
    """Start unified 6-stage workflow engine for a project."""
    await _validate_project_exists(project_id, session)

    # Snapshot Project Settings
    p_res = await session.execute(select(Project).where(Project.id == project_id))
    project = p_res.scalar_one_or_none()
    proj_settings = (project.settings_json or {}) if project else {}

    ctx_data = copy.deepcopy(proj_settings)
    if payload:
        payload_dict = payload.dict(exclude_none=True)
        for k, v in payload_dict.items():
            if k == "watermark_enabled":
                ctx_data[k] = v or _parse_bool(proj_settings.get("watermark_enabled"), False)
            elif k == "thumbnail_enabled":
                ctx_data[k] = bool(v) if v is not None else _parse_bool(proj_settings.get("thumbnail_enabled"), False)
            elif v is not None:
                ctx_data[k] = v

    ctx_data["settings_snapshot"] = proj_settings

    # Auto-resolve video_path / video_url from VideoTranslationJob & VideoAsset if not set
    if not ctx_data.get("video_path") and not ctx_data.get("video_url"):
        j_res = await session.execute(
            select(VideoTranslationJob)
            .where((VideoTranslationJob.project_id == project_id) | (VideoTranslationJob.id == project_id))
            .order_by(VideoTranslationJob.created_at.desc())
        )
        job_rec = j_res.scalars().first()
        if job_rec and job_rec.asset_id:
            a_res = await session.execute(select(VideoAsset).where(VideoAsset.id == job_rec.asset_id))
            asset_rec = a_res.scalars().first()
            if asset_rec:
                if asset_rec.file_path and Path(asset_rec.file_path).is_file():
                    ctx_data["video_path"] = asset_rec.file_path
                elif asset_rec.source_url:
                    ctx_data["video_url"] = asset_rec.source_url

    print(f"[WORKFLOW SETTINGS SNAPSHOT] Project ID: {project_id} | Settings Snapshot Frozen: {list(proj_settings.keys())}")
    wf_exec = await _global_workflow_engine.start_workflow(project_id, context_data=ctx_data, db=session)
    return {"success": True, "data": {"workflow_id": wf_exec.id, "status": wf_exec.status}}


@router.post("/projects/{project_id}/workflow/pause", response_model=dict)
async def pause_workflow_api(project_id: str, session: AsyncSession = Depends(get_session)):
    """Pause unified 6-stage workflow engine for a project."""
    await _validate_project_exists(project_id, session)
    ok = await _global_workflow_engine.pause_workflow(project_id, session)
    return {"success": True, "data": {"paused": ok}}


@router.post("/projects/{project_id}/workflow/resume", response_model=dict)
async def resume_workflow_api(
    project_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Resume unified 6-stage workflow engine from failed/paused stage."""
    await _validate_project_exists(project_id, session)
    wf_exec = await _global_workflow_engine.resume_workflow(project_id, session)

    # Automatically restart/resume any associated VideoTranslationJob
    try:
        stmt = (
            select(VideoTranslationJob)
            .where(
                (VideoTranslationJob.project_id == project_id) | (VideoTranslationJob.id == project_id)
            )
            .order_by(VideoTranslationJob.created_at.desc())
        )
        res = await session.execute(stmt)
        job = res.scalars().first()
        if job:
            if job.status == TranslationJobStatus.SEGMENT_EDITING.value and job.auto_confirm_translation:
                background_tasks.add_task(execute_job_render_pipeline, job.id)
            elif job.status in [
                TranslationJobStatus.FAILED.value,
                TranslationJobStatus.CREATED.value,
                TranslationJobStatus.SEGMENT_EDITING.value,
            ]:
                signal_job_cancellation(job.id)
                job.error_message = None
                job.status = TranslationJobStatus.CREATED.value
                job.stage = "QUEUED"
                job.current_step = "Resuming workflow pipeline..."
                job.pid = None
                await session.commit()
                log_job_event(job.id, "RESUME", "Resuming translation job via resume_workflow_api.")
                await start_translation_pipeline(job.id, background_tasks, session)
    except Exception as err:
        logger.warning(f"Failed to auto-resume job for project {project_id} in resume_workflow_api: {err}")

    return {"success": True, "data": {"workflow_id": wf_exec.id, "status": wf_exec.status}}


@router.post("/projects/{project_id}/workflow/cancel", response_model=dict)
async def cancel_workflow_api(project_id: str, session: AsyncSession = Depends(get_session)):
    """Cancel unified 6-stage workflow engine for a project."""
    await _validate_project_exists(project_id, session)
    ok = await _global_workflow_engine.cancel_workflow(project_id, session)
    return {"success": True, "data": {"cancelled": ok}}


@router.post("/projects/{project_id}/workflow/stage/{stage_name}/retry", response_model=dict)
async def retry_stage_api(
    project_id: str,
    stage_name: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Reset and retry a specific stage within the 6-stage workflow."""
    await _validate_project_exists(project_id, session)
    wf_exec = await _global_workflow_engine.retry_stage(project_id, stage_name, session)

    # Automatically restart any associated VideoTranslationJob in FAILED/PAUSED/CREATED state
    try:
        stmt = (
            select(VideoTranslationJob)
            .where(
                (VideoTranslationJob.project_id == project_id) | (VideoTranslationJob.id == project_id)
            )
            .order_by(VideoTranslationJob.created_at.desc())
        )
        res = await session.execute(stmt)
        job = res.scalars().first()
        if job and job.status in [
            TranslationJobStatus.FAILED.value,
            TranslationJobStatus.SEGMENT_EDITING.value,
            TranslationJobStatus.NEEDS_REVIEW.value,
            TranslationJobStatus.CREATED.value,
        ]:
            signal_job_cancellation(job.id)
            job.error_message = None

            phase2_stages = [
                "DUB", "PRODUCE", "AUDIO_SCHEDULE_REVIEW", "GENERATING_TTS",
                "SYNCING_AUDIO", "RENDERING",
            ]
            if stage_name in phase2_stages:
                job.status = TranslationJobStatus.GENERATING_TTS.value
                job.stage = "DUB"
                job.current_step = f"Smart Retry từ stage {stage_name} (Phase 2)..."
                job.pid = None
                await session.commit()
                log_job_event(job.id, "RETRY", f"Smart Retry initiated for stage {stage_name} (Phase 2 resume).")
                background_tasks.add_task(execute_job_render_pipeline, job.id)
            else:
                job.status = TranslationJobStatus.CREATED.value
                job.stage = "QUEUED"
                job.current_step = f"Smart Retry từ stage {stage_name}..."
                job.pid = None
                await session.commit()
                log_job_event(job.id, "RETRY", f"Smart Retry initiated for stage {stage_name}.")
                await start_translation_pipeline(job.id, background_tasks, session)
    except Exception as retry_err:
        logger.warning(f"Failed to auto-restart job for project {project_id} in retry_stage_api: {retry_err}")

    return {"success": True, "data": {"workflow_id": wf_exec.id, "status": wf_exec.status, "current_stage": wf_exec.current_stage}}


# ── Project Glossary Endpoints ─────────────────────────────────────

class GlossaryTermCreate(BaseModel):
    source_term: str = Field(..., description="Source text/name term")
    translated_term: str = Field(..., description="Translated text/name term")
    term_type: str = Field("other", description="character, location, organization, skill, title, other")


@router.get("/projects/{project_id}/glossary", response_model=dict)
async def get_project_glossary_api(project_id: str, session: AsyncSession = Depends(get_session)):
    """List all project glossary terms."""
    stmt = select(ProjectGlossary).where(ProjectGlossary.project_id == project_id)
    res = await session.execute(stmt)
    terms = res.scalars().all()
    return {
        "success": True,
        "data": [serialize_glossary_entry(t) for t in terms],
    }


@router.post("/projects/{project_id}/glossary", response_model=dict)
async def add_project_glossary_api(
    project_id: str, payload: GlossaryTermCreate, session: AsyncSession = Depends(get_session)
):
    """Create an idempotent canonical term or return a structured conflict."""
    try:
        term, created = await create_glossary_entry(
            session,
            project_id,
            payload.source_term,
            payload.translated_term,
            payload.term_type,
        )
    except GlossaryConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.to_detail()) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"success": True, "data": {**serialize_glossary_entry(term), "created": created}}


@router.patch("/projects/{project_id}/glossary/{term_id}", response_model=dict)
async def update_project_glossary_api(
    project_id: str,
    term_id: str,
    payload: GlossaryTermCreate,
    session: AsyncSession = Depends(get_session),
):
    """Edit source, translation, and type without bypassing 1:1 constraints."""
    try:
        term = await update_glossary_entry(
            session,
            project_id,
            term_id,
            payload.source_term,
            payload.translated_term,
            payload.term_type,
        )
    except GlossaryConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.to_detail()) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"success": True, "data": serialize_glossary_entry(term)}


@router.delete("/projects/{project_id}/glossary/{term_id}", response_model=dict)
async def delete_project_glossary_api(
    project_id: str, term_id: str, session: AsyncSession = Depends(get_session)
):
    """Delete a glossary term."""
    await session.execute(
        delete(ProjectGlossary).where(
            ProjectGlossary.id == term_id, ProjectGlossary.project_id == project_id
        )
    )
    await session.commit()
    return {"success": True, "data": {"deleted": True}}


# ── Speaker Voice Mapping Endpoints ─────────────────────────────────

class VoiceMapPayload(BaseModel):
    speaker_id: str = Field(..., description="Speaker ID e.g. SPEAKER_00")
    speaker_name: Optional[str] = Field(None, description="Display name for speaker")
    voice_provider: str = Field("edge", description="edge, google, elevenlabs")
    voice_id: str = Field(..., description="Voice identifier e.g. vi-VN-HoaiMyNeural")
    character_id: Optional[str] = None
    confidence: Optional[float] = None


@router.get("/projects/{project_id}/voice-map", response_model=dict)
async def get_speaker_voice_map_api(project_id: str, session: AsyncSession = Depends(get_session)):
    """List speaker voice mappings for a project."""
    stmt = select(SpeakerVoiceMapping).where(SpeakerVoiceMapping.project_id == project_id)
    res = await session.execute(stmt)
    mappings = res.scalars().all()
    return {
        "success": True,
        "data": [
            {
                "id": m.id,
                "speaker_id": m.speaker_id,
                "speaker_name": m.speaker_name,
                "voice_provider": m.voice_provider,
                "voice_id": m.voice_id,
                "character_id": m.character_id,
                "confidence": m.confidence,
                "needs_review": m.needs_review,
            }
            for m in mappings
        ],
    }


@router.post("/projects/{project_id}/voice-map", response_model=dict)
async def save_speaker_voice_map_api(
    project_id: str, payload: VoiceMapPayload, session: AsyncSession = Depends(get_session)
):
    """Create or update speaker voice mapping."""
    stmt = select(SpeakerVoiceMapping).where(
        SpeakerVoiceMapping.project_id == project_id,
        SpeakerVoiceMapping.speaker_id == payload.speaker_id,
    )
    res = await session.execute(stmt)
    mapping = res.scalars().first()

    if not mapping:
        mapping = SpeakerVoiceMapping(
            id=str(uuid.uuid4()),
            project_id=project_id,
            speaker_id=payload.speaker_id,
            speaker_name=payload.speaker_name or payload.speaker_id,
            voice_provider=payload.voice_provider,
            voice_id=payload.voice_id,
            character_id=payload.character_id,
            confidence=payload.confidence or 0.0,
        )
        session.add(mapping)
    else:
        mapping.speaker_name = payload.speaker_name or payload.speaker_id
        mapping.voice_provider = payload.voice_provider
        mapping.voice_id = payload.voice_id
        if payload.character_id is not None:
            mapping.character_id = payload.character_id
        if payload.confidence is not None:
            mapping.confidence = payload.confidence

    await session.commit()
    return {"success": True, "data": {"id": mapping.id, "speaker_id": mapping.speaker_id}}


class CharacterVoiceEdit(BaseModel):
    segment_id: Optional[int] = None
    speaker_id: str
    character_id: str
    character_name: Optional[str] = None
    gender: str = "unknown"
    role: str = "supporting"
    voice_provider: str
    voice_id: str


class CharacterVoiceReviewUpdate(BaseModel):
    mappings: List[CharacterVoiceEdit]


async def validate_voice_assignment(
    provider_id: Optional[str],
    voice_id: Optional[str],
    target_language: Optional[str] = None,
    character_gender: Optional[str] = None,
) -> Optional[Dict[str, str]]:
    """Validate provider, voice existence, target language compatibility, and character gender matching."""
    if not provider_id:
        return {"reason": "missing_provider", "message": "Chưa chọn nhà cung cấp giọng đọc (Provider)."}
    if not voice_id:
        return {"reason": "missing_voice", "message": "Chưa chọn giọng đọc (Voice)."}

    registry = get_registry()
    provider = registry.get_audio(provider_id)
    if not provider:
        return {
            "reason": "invalid_provider",
            "message": f"Nhà cung cấp âm thanh '{provider_id}' không hợp lệ hoặc không được hỗ trợ.",
        }

    try:
        voices = await provider.get_voices()
    except Exception:
        voices = []

    matched_voice = next((v for v in voices if v.id == voice_id), None)
    if not matched_voice:
        return {
            "reason": "invalid_voice",
            "message": f"Giọng đọc '{voice_id}' không tồn tại hoặc không thuộc nhà cung cấp '{provider_id}'.",
        }

    if target_language:
        norm_target = target_language.lower().split("-")[0]
        v_lang = str(matched_voice.language or "").lower()
        if not (v_lang.startswith(norm_target) or v_lang == target_language.lower()):
            return {
                "reason": "target_language_mismatch",
                "message": f"Giọng đọc '{voice_id}' (ngôn ngữ: {matched_voice.language}) không phù hợp với ngôn ngữ đích '{target_language}'.",
            }

    if character_gender is not None:
        c_gender = str(character_gender).strip().lower()
        v_gender = str(matched_voice.gender or "").lower()
        if c_gender == "unknown":
            return {
                "reason": "gender_unresolved",
                "message": "Chưa xác định giới tính nhân vật. Vui lòng chọn Nam hoặc Nữ trước khi gán giọng.",
            }
        if c_gender in ("male", "female") and v_gender in ("male", "female") and v_gender != c_gender:
            return {
                "reason": "gender_mismatch",
                "message": f"Giọng đọc '{voice_id}' ({'Nữ' if v_gender == 'female' else 'Nam'}) không khớp với giới tính nhân vật ({'Nam' if c_gender == 'male' else 'Nữ'}).",
            }

    return None


async def _character_voice_review_data(job_id: str, session: AsyncSession) -> dict:
    job = (await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    rows = (await session.execute(select(VideoTranslationSegment).where(VideoTranslationSegment.job_id == job_id).order_by(VideoTranslationSegment.segment_number))).scalars().all()
    profiles = []
    if job.project_id:
        profiles = (await session.execute(
            select(CharacterVoiceProfile).where(CharacterVoiceProfile.project_id == job.project_id)
        )).scalars().all()
    char_map = {p.character_id: p for p in profiles}

    return {
        "job_id": job_id,
        "target_language": job.target_language,
        "status": job.status,
        "passed": job.status != TranslationJobStatus.NEEDS_REVIEW.value,
        "characters": [
            {
                "character_id": p.character_id,
                "name": p.name,
                "gender": p.gender,
                "role": p.role,
                "voice_provider": p.voice_provider,
                "voice_id": p.voice_id,
                "confirmed_by_user": p.confirmed_by_user,
            }
            for p in profiles
        ],
        "segments": [{
            "id": row.id,
            "segment_number": row.segment_number,
            "speaker_id": row.speaker_id,
            "character_id": row.character_id,
            "character_name": char_map[row.character_id].name if (row.character_id and row.character_id in char_map) else (row.character_id or row.speaker_id),
            "gender": char_map[row.character_id].gender if (row.character_id and row.character_id in char_map) else "unknown",
            "voice_provider": row.voice_provider,
            "voice_id": row.voice_id,
            "confidence": row.mapping_confidence,
            "conflict": row.overlap_with or [],
            "original_start": row.original_start if row.original_start is not None else row.start_time,
            "original_end": row.original_end if row.original_end is not None else row.end_time,
            "scheduled_start": row.scheduled_start,
            "scheduled_end": row.scheduled_end,
            "schedule_action": row.schedule_action,
            "tts_duration": row.tts_duration or row.tts_audio_duration or 0.0,
        } for row in rows],
    }


@router.get("/jobs/{job_id}/character-voice-review")
async def get_character_voice_review(job_id: str, session: AsyncSession = Depends(get_session)):
    return {"success": True, "data": await _character_voice_review_data(job_id, session)}


@router.put("/jobs/{job_id}/character-voice-review")
async def update_character_voice_review(job_id: str, body: CharacterVoiceReviewUpdate, session: AsyncSession = Depends(get_session)):
    job = (await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    target_lang = job.target_language or "vi"
    for item in body.mappings:
        cur_gender = item.gender
        if cur_gender == "unknown":
            exist_prof = (await session.execute(
                select(CharacterVoiceProfile).where(
                    CharacterVoiceProfile.project_id == job.project_id,
                    CharacterVoiceProfile.character_id == item.character_id,
                )
            )).scalar_one_or_none()
            if exist_prof and exist_prof.gender != "unknown":
                cur_gender = exist_prof.gender

        err = await validate_voice_assignment(
            provider_id=item.voice_provider,
            voice_id=item.voice_id,
            target_language=target_lang,
            character_gender=cur_gender,
        )
        if err:
            raise HTTPException(
                status_code=400,
                detail=f"Lỗi cấu hình giọng đọc: {err['message']} ({err['reason']})",
            )

    job_dir = settings.STORAGE_ROOT / "translator" / "jobs" / job_id
    tts_dir = job_dir / "tts"
    invalidated_segments = []

    for item in body.mappings:
        profile = (await session.execute(select(CharacterVoiceProfile).where(CharacterVoiceProfile.project_id == job.project_id, CharacterVoiceProfile.character_id == item.character_id))).scalar_one_or_none()
        if not profile:
            profile = CharacterVoiceProfile(id=str(uuid.uuid4()), project_id=job.project_id, character_id=item.character_id, name=item.character_name or item.character_id)
            session.add(profile)
        profile.gender, profile.role = item.gender, item.role
        profile.voice_provider, profile.voice_id = item.voice_provider, item.voice_id

        # Target segments
        stmt = select(VideoTranslationSegment).where(VideoTranslationSegment.job_id == job_id)
        if item.segment_id:
            stmt = stmt.where(VideoTranslationSegment.id == item.segment_id)
        else:
            stmt = stmt.where(VideoTranslationSegment.speaker_id == item.speaker_id)
        target_segs = (await session.execute(stmt)).scalars().all()

        for seg in target_segs:
            if seg.voice_id != item.voice_id or seg.voice_provider != item.voice_provider:
                invalidated_segments.append(seg.segment_number)
                seg_f = tts_dir / f"seg_{seg.segment_number:03d}.wav"
                seg_meta = tts_dir / f"seg_{seg.segment_number:03d}.meta.json"
                if seg_f.exists():
                    seg_f.unlink(missing_ok=True)
                if seg_meta.exists():
                    seg_meta.unlink(missing_ok=True)
                seg.tts_audio_path = None
                seg.tts_audio_duration = None
                seg.tts_duration = None

            seg.character_id = item.character_id
            seg.voice_provider = item.voice_provider
            seg.voice_id = item.voice_id

        mapping = (await session.execute(select(SpeakerVoiceMapping).where(SpeakerVoiceMapping.project_id == job.project_id, SpeakerVoiceMapping.speaker_id == item.speaker_id))).scalar_one_or_none()
        if mapping:
            mapping.character_id, mapping.voice_provider, mapping.voice_id = item.character_id, item.voice_provider, item.voice_id
            mapping.needs_review = False

    await session.commit()
    if invalidated_segments:
        unique_invalidated = sorted(list(set(invalidated_segments)))
        log_job_event(job_id, "TTS_CACHE", f"[TTS_CACHE] Invalidating segments: {unique_invalidated}")

    return {"success": True, "data": await _character_voice_review_data(job_id, session)}


@router.post("/jobs/{job_id}/character-voice-review/validate")
async def validate_character_voice_review(job_id: str, session: AsyncSession = Depends(get_session)):
    data = await _character_voice_review_data(job_id, session)
    missing = [s["id"] for s in data["segments"] if not s.get("character_id") or not s.get("voice_id")]
    issues: List[Dict[str, Any]] = []
    if missing:
        issues.append({
            "reason": "missing_assignment",
            "segment_ids": missing,
            "message": f"Có {len(missing)} phân đoạn chưa được gán nhân vật hoặc giọng đọc.",
        })


    # Validate Audio Schedule and check for same-voice overlaps
    from app.services.video_translator.timeline_scheduler import SchedulePolicy, schedule_segments
    max_orig_end = max([s["original_end"] or 0.0 for s in data["segments"]] + [1.0])
    sched_payload = [{
        "id": s["id"],
        "segment_number": s.get("segment_number", s["id"]),
        "original_start": s["original_start"] or 0.0,
        "original_end": s["original_end"] or 0.0,
        "tts_duration": s.get("tts_duration", 0.0),
        "voice_id": s.get("voice_id"),
        "role": "supporting",
    } for s in data["segments"]]

    sched_res = schedule_segments(
        sched_payload,
        video_duration=max_orig_end + 60.0,
        policy=SchedulePolicy(max_reschedule_seconds=60.0, max_tempo=2.0),
    )

    # 1. Direct overlap scan in scheduled timeline
    sorted_sched = sorted(sched_res.segments, key=lambda s: float(s.get("scheduled_start", s.get("original_start", 0.0))))
    for index, left in enumerate(sorted_sched):
        left_start = float(left.get("scheduled_start", left.get("original_start", 0.0)))
        left_end = float(left.get("scheduled_end", left.get("original_end", left_start)))
        left_voice = left.get("voice_id")
        left_num = left.get("segment_number", left.get("id"))
        for right in sorted_sched[index + 1:]:
            right_start = float(right.get("scheduled_start", right.get("original_start", 0.0)))
            right_end = float(right.get("scheduled_end", right.get("original_end", right_start)))
            right_voice = right.get("voice_id")
            right_num = right.get("segment_number", right.get("id"))

            if right_start >= left_end - 0.001:
                break

            if left_voice and right_voice and left_voice == right_voice:
                issues.append({
                    "reason": "same_voice_overlap",
                    "segment_ids": [left["id"], right["id"]],
                    "segment_numbers": [left_num, right_num],
                    "voice_id": left_voice,
                    "message": f"Segment {left_num} và {right_num} đang sử dụng cùng voice {left_voice} trong khoảng thời gian overlap ({left_start:.2f}s - {right_end:.2f}s). Vui lòng thay đổi voice hoặc chỉnh schedule trước khi tiếp tục.",
                })

    # 2. Check scheduler unresolved conflicts
    if sched_res.unresolved_conflicts:
        seg_lookup = {s["id"]: s for s in data["segments"]}
        for conf in sched_res.unresolved_conflicts:
            l_s = seg_lookup.get(conf.get("with"))
            r_s = seg_lookup.get(conf.get("segment_id"))
            if l_s and r_s and l_s.get("voice_id") == r_s.get("voice_id"):
                l_num = l_s.get("segment_number", l_s["id"])
                r_num = r_s.get("segment_number", r_s["id"])
                v_id = l_s.get("voice_id")
                issues.append({
                    "reason": "same_voice_overlap",
                    "segment_ids": [l_s["id"], r_s["id"]],
                    "segment_numbers": [l_num, r_num],
                    "voice_id": v_id,
                    "message": f"Segment {l_num} và {r_num} đang sử dụng cùng voice {v_id} trong khoảng thời gian overlap. Vui lòng thay đổi voice hoặc chỉnh schedule trước khi tiếp tục.",
                })

    target_lang = data.get("target_language")
    for s in data["segments"]:
        if not s.get("character_id") or not s.get("voice_id"):
            continue
        err = await validate_voice_assignment(
            provider_id=s.get("voice_provider"),
            voice_id=s.get("voice_id"),
            target_language=target_lang,
            character_gender=s.get("gender"),
        )
        if err:
            issues.append({
                "reason": err["reason"],
                "segment_ids": [s["id"]],
                "segment_numbers": [s.get("segment_number", s["id"])],
                "voice_id": s.get("voice_id"),
                "message": f"Phân đoạn #{s.get('segment_number', s['id'])}: {err['message']}",
            })

    # Deduplicate issues with stable key
    deduped_issues: List[Dict[str, Any]] = []
    seen_keys: set = set()
    for issue in issues:
        key = (issue.get("reason"), tuple(sorted(issue.get("segment_ids", []))), issue.get("voice_id"))
        if key not in seen_keys:
            seen_keys.add(key)
            deduped_issues.append(issue)

    passed = (len(missing) == 0) and (len(deduped_issues) == 0)
    return {"success": True, "data": {**data, "passed": passed, "issues": deduped_issues}}


@router.post("/jobs/{job_id}/character-voice-review/confirm-resume")
async def confirm_character_voice_review(job_id: str, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    job = (await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Idempotency checks:
    if job.status in [TranslationJobStatus.COMPLETED.value, "completed"]:
        logger.info(f"[CONFIRM] Job {job_id} is already COMPLETED. Ignoring duplicate confirm.")
        return {"success": True, "data": {"job_id": job_id, "resumed": False, "status": job.status, "message": "Job is already completed."}}

    if job_id in _active_render_jobs or job.status in [
        TranslationJobStatus.GENERATING_TTS.value,
        TranslationJobStatus.SYNCING_AUDIO.value,
        TranslationJobStatus.RENDERING.value,
    ]:
        logger.info(f"[CONFIRM] Job {job_id} is already processing ({job.status}). Ignoring duplicate confirm.")
        return {"success": True, "data": {"job_id": job_id, "resumed": False, "status": job.status, "message": "Job is already processing."}}

    log_job_event(job_id, "CONFIRM", "[CONFIRM] User confirmed review")
    log_job_event(job_id, "CONFIRM", "[CONFIRM] Re-validating audio schedule")

    validation = await validate_character_voice_review(job_id, session)
    if not validation["data"]["passed"]:
        remaining_issues = validation["data"].get("issues", [])
        issue_msgs = [i.get("message") or i.get("reason") for i in remaining_issues]
        err_msg = "; ".join(issue_msgs) if issue_msgs else "Còn xung đột giọng đọc / lịch trình audio."
        log_job_event(job_id, "CONFIRM", f"[CONFIRM] Validation failed - remaining conflicts: {remaining_issues}")
        log_job_event(job_id, "CONFIRM", "[CONFIRM] Review confirmation rejected because unresolved conflicts remain")

        # Keep state as NEEDS_REVIEW
        job.status = TranslationJobStatus.NEEDS_REVIEW.value
        job.current_step = f"Không thể tiếp tục: {err_msg}"
        await session.commit()

        raise HTTPException(status_code=409, detail=validation["data"])

    log_job_event(job_id, "CONFIRM", "[CONFIRM] Validation passed. Proceeding to TTS & Dubbing.")

    profiles = (await session.execute(select(CharacterVoiceProfile).where(CharacterVoiceProfile.project_id == job.project_id))).scalars().all()
    for profile in profiles:
        profile.confirmed_by_user = True

    snap = {}
    if job.settings_snapshot_json:
        try:
            snap = json.loads(job.settings_snapshot_json)
        except Exception:
            snap = {}
    snap["review_confirmed"] = True
    snap["audio_schedule_confirmed"] = True
    job.settings_snapshot_json = json.dumps(snap)
    job.last_checkpoint_stage = "CHARACTER_VOICE_REVIEW_DONE"
    job.status, job.stage = TranslationJobStatus.GENERATING_TTS.value, "DUB"
    job.current_step = "Đã xác nhận Character/Voice. Đang tiếp tục xử lý TTS & Dubbing..."
    await session.commit()
    log_job_event(job_id, "CONFIRM_RESUME", "User confirmed Character/Voice and Audio Schedule review. Proceeding to TTS & Dubbing.")
    background_tasks.add_task(execute_job_render_pipeline, job_id)
    return {"success": True, "data": {"job_id": job_id, "resumed": True}}


@router.get("/projects/{project_id}/character-profiles")
async def list_character_profiles(project_id: str, session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(select(CharacterVoiceProfile).where(CharacterVoiceProfile.project_id == project_id))).scalars().all()
    return {"success": True, "data": [{"character_id": r.character_id, "name": r.name, "gender": r.gender, "role": r.role, "voice_provider": r.voice_provider, "voice_id": r.voice_id, "confirmed_by_user": r.confirmed_by_user} for r in rows]}


@router.get("/voice-pool")
async def list_voice_pool(provider: Optional[str] = None, language: Optional[str] = None, gender: Optional[str] = None, session: AsyncSession = Depends(get_session)):
    stmt = select(VoicePoolEntry).where(VoicePoolEntry.enabled.is_(True))
    if provider:
        stmt = stmt.where(VoicePoolEntry.provider == provider)
    if language:
        stmt = stmt.where(VoicePoolEntry.language == language)
    if gender:
        stmt = stmt.where(VoicePoolEntry.gender == gender)
    rows = (await session.execute(stmt)).scalars().all()
    return {"success": True, "data": [{"provider": r.provider, "language": r.language, "gender": r.gender, "voice_id": r.voice_id, "name": r.display_name} for r in rows]}
