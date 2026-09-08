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
    original_audio_mode: str = "mute"
    
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
    storage_dir = settings.DATA_DIR / "translator" / "assets" / asset_id
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
            raise HTTPException(status_code=400, detail=f"❌ {str(e)}")

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
        storage_dir = settings.DATA_DIR / "translator" / "watermarks"
    
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

    job_id = f"VT-{str(uuid.uuid4())[:6].upper()}"

    settings_snapshot = {
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
        }
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
                    if not b_job:
                        return

                    asset_res = await bg_session.execute(select(VideoAsset).where(VideoAsset.id == b_job.asset_id))
                    b_asset = asset_res.scalar_one_or_none()
                    if not b_asset:
                        return

                    job_dir = settings.DATA_DIR / "translator" / "jobs" / job_id
                    job_dir.mkdir(parents=True, exist_ok=True)

                    # 1. Extract Audio
                    current_stage = "EXTRACTING_AUDIO"
                    b_job.status = TranslationJobStatus.EXTRACTING_AUDIO.value
                    b_job.stage = "EXTRACTING_AUDIO"
                    b_job.current_step = "Trích xuất audio từ video"
                    b_job.stage_progress_pct = 0.0
                    b_job.overall_progress_pct = calculate_overall_progress("EXTRACTING_AUDIO", 0.0)
                    await bg_session.commit()

                    extracted_audio_path = job_dir / "extracted_audio.wav"

                    def on_extract_progress(stats: dict):
                        pct = stats.get("progress_pct", 0.0)
                        pid = stats.get("pid")
                        asyncio.create_task(_update_ffmpeg_stats(job_id, "EXTRACTING_AUDIO", pct, pid, stats))

                    def on_extract_pid(pid: int):
                        asyncio.create_task(_update_pid(job_id, pid))

                    local_asset_path = Path(b_asset.file_path)
                    if not local_asset_path.exists() and getattr(b_asset, "r2_key", None):
                        log_job_event(job_id, "DOWNLOADING", f"Local asset missing at {local_asset_path}. Downloading from R2 ({b_asset.r2_key})...")
                        local_asset_path.parent.mkdir(parents=True, exist_ok=True)
                        try:
                            await storage_service.download_file(b_asset.r2_key, local_asset_path)
                        except Exception as download_err:
                            logger.warning("R2 asset download failed", error=str(download_err), job_id=job_id)

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

                    current_stage = "TRANSLATING"
                    b_job.detected_language = detected_lang
                    b_job.status = TranslationJobStatus.TRANSLATED.value
                    b_job.stage = "TRANSLATING"
                    b_job.current_step = "Đang dịch bản thoại"
                    b_job.stage_progress_pct = 50.0
                    b_job.overall_progress_pct = calculate_overall_progress("TRANSLATING", 50.0)
                    await bg_session.commit()

                    # 3. Translate
                    translated_segs = await translate_transcript_segments(
                        segments_raw,
                        source_language=detected_lang,
                        target_language=b_job.target_language,
                        job_id=job_id,
                        llm_provider_id=b_job.llm_provider_id or "gemini",
                        db=bg_session,
                    )

                    # Clear previous segments if any
                    await bg_session.execute(
                        delete(VideoTranslationSegment)
                        .where(VideoTranslationSegment.job_id == job_id)
                        .execution_options(synchronize_session=False)
                    )
                    bg_session.expire(b_job, ["segments"])

                    for seg in translated_segs:
                        db_seg = VideoTranslationSegment(
                            job_id=job_id,
                            segment_number=seg["number"],
                            start_time=seg["start_time"],
                            end_time=seg["end_time"],
                            original_text=seg["text"],
                            translated_text=seg.get("translated_text", seg["text"]),
                            status="translated",
                        )
                        bg_session.add(db_seg)

                    now_dt = datetime.now(timezone.utc).replace(tzinfo=None)
                    b_job.status = TranslationJobStatus.SEGMENT_EDITING.value
                    b_job.stage = "SEGMENT_EDITING"
                    b_job.current_step = "Chờ xem lại & chỉnh sửa bản dịch"
                    b_job.stage_progress_pct = 100.0
                    b_job.overall_progress_pct = 60.0
                    b_job.total_segments_count = len(translated_segs)
                    b_job.completed_segments_count = 0
                    b_job.pid = None
                    b_job.last_checkpoint_stage = "TRANSLATION_DONE"
                    b_job.last_checkpoint_at = now_dt
                    b_job.studio_state_json = json.dumps({"active_step": "segment_editing", "active_tab": "editor"})
                    await bg_session.commit()
                    
                    snapshot_str = (
                        f"Phase 1 completed. Awaiting user segment confirmation.\n"
                        f"[STATE SNAPSHOT] Job: {job_id} | status={b_job.status} | stage={b_job.stage} | "
                        f"progress={b_job.overall_progress_pct}% | heartbeat=INACTIVE | segments={len(translated_segs)}"
                    )
                    log_job_event(job_id, "SEGMENT_EDITING", snapshot_str)

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

                async with async_session_factory() as bg_session:
                    await bg_session.execute(
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
                    await bg_session.commit()
            finally:
                stop_job_heartbeat(job_id)

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
    # Check for stalled jobs
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

    is_terminal = job.status in [TranslationJobStatus.FAILED.value, TranslationJobStatus.COMPLETED.value, "cancelled", TranslationJobStatus.SEGMENT_EDITING.value, "segment_editing"]
    heartbeat_active = (not is_terminal) and (hb_age_sec <= 30)

    process_status = "IDLE"
    if job.status == TranslationJobStatus.FAILED.value:
        process_status = "FAILED"
    elif job.status == "cancelled":
        process_status = "KILLED"
    elif job.status == TranslationJobStatus.COMPLETED.value:
        process_status = "COMPLETED"
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
            "segments": [
                {
                    "id": s.id,
                    "number": s.segment_number,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "original_text": s.original_text,
                    "translated_text": s.translated_text,
                    "status": s.status,
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

    async def run_render():
        lock = get_job_lock(job_id)
        if lock.locked():
            logger.warning(f"Job {job_id} render already running in another task.")
            return

        async with lock:
            start_job_heartbeat(job_id)
            current_stage = "GENERATING_TTS"
            cancel_evt = reset_job_cancellation(job_id)

        try:
            async with async_session_factory() as init_session:
                job_res = await init_session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
                b_job = job_res.scalar_one_or_none()
                if not b_job or is_job_cancelled(job_id) or cancel_evt.is_set():
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
                    }
                    for s in raw_segments
                ]

                job_dir = settings.DATA_DIR / "translator" / "jobs" / job_id
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

                # 1. TTS Generation Stage
                current_stage = "GENERATING_TTS"
                await init_session.execute(
                    update(VideoTranslationJob)
                    .where(VideoTranslationJob.id == job_id)
                    .values(
                        status=TranslationJobStatus.GENERATING_TTS.value,
                        stage="GENERATING_TTS",
                        current_step=f"Đang tạo giọng đọc TTS (0/{len(segments_data)})",
                        total_segments_count=len(segments_data),
                        completed_segments_count=0,
                        stage_progress_pct=0.0,
                        overall_progress_pct=calculate_overall_progress("GENERATING_TTS", 0.0),
                    )
                )
                await init_session.commit()
                log_job_event(job_id, "GENERATING_TTS", f"Starting TTS generation for {len(segments_data)} segments...")

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
                log_job_event(job_id, "GENERATING_TTS", f"Generating TTS for segment #{seg['segment_number']}/{len(segments_data)}")

                try:
                    res = await audio_provider.generate_audio(
                        text=seg["translated_text"],
                        voice_id=voice_id,
                        output_path=seg_tts_path,
                    )
                    if not res.success or not seg_tts_path.exists():
                        logger.warning(f"[VIDEO-SYNC] TTS failed for Segment #{seg['segment_number']}: {res.error_message}")
                        log_job_event(job_id, "GENERATING_TTS", f"[VIDEO-SYNC] ⚠️ Segment #{seg['segment_number']} TTS failed: {res.error_message}. Fallback to silence.")
                        seg["tts_audio_path"] = None
                        seg["tts_audio_duration"] = 0.0
                        seg["status"] = "failed"
                    else:
                        dur = await probe_duration_async(seg_tts_path)
                        seg["tts_audio_path"] = str(seg_tts_path)
                        seg["tts_audio_duration"] = dur
                        seg["status"] = "tts_completed"
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
            log_job_event(job_id, "SYNCING_AUDIO", "Starting audio time-stretch synchronization...")

            for idx, seg in enumerate(segments_data, start=1):
                if is_job_cancelled(job_id) or cancel_evt.is_set():
                    logger.info(f"[JOB-CANCEL] Job {job_id} cancelled during Audio Sync. Stopping pipeline.")
                    return

                target_dur = max(1.0, seg["end_time"] - seg["start_time"])
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

                rendered_path = await render_dubbed_video(
                    video_path=asset_file_path,
                    segments=db_render_segments,
                    original_audio_mode=original_audio_mode,
                    output_video_path=final_video_path,
                    work_dir=job_dir / "work",
                    job_id=job_id,
                    on_progress=on_render_progress,
                    on_pid=on_render_pid,
                )

                # Fetch fresh job configuration for watermark processing
                job_stmt = select(VideoTranslationJob).where(VideoTranslationJob.id == job_id)
                job_obj = (await render_session.execute(job_stmt)).scalar_one_or_none()

            # Watermark Processing Step: Applied ONCE on Final Video
            if job_obj and job_obj.watermark_enabled:
                log_job_event(job_id, "APPLYING_WATERMARK", "Watermark enabled. Applying logo/text watermark overlay to final video...")
                async with async_session_factory() as wm_session:
                    await wm_session.execute(
                        update(VideoTranslationJob)
                        .where(VideoTranslationJob.id == job_id)
                        .values(
                            stage="APPLYING_WATERMARK",
                            current_step="Đang gắn logo / watermark vào video bằng FFmpeg",
                            stage_progress_pct=50.0,
                            overall_progress_pct=calculate_overall_progress("RENDERING", 50.0),
                        )
                    )
                    await wm_session.commit()

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
            stop_job_heartbeat(job_id)

    background_tasks.add_task(run_render)
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

    # Reset job status to CREATED for retry
    job.error_message = None
    job.status = TranslationJobStatus.CREATED.value
    job.stage = "QUEUED"
    job.current_step = "Thực hiện Smart Retry..."
    job.pid = None
    await session.commit()
    log_job_event(job_id, "RETRY", "Smart Retry initiated by user.")

    # Trigger restart
    return await start_translation_pipeline(job_id, background_tasks, session)


# ── Unified 6-Stage Workflow & Glossary Routes ──────────────────────

from app.workflow.workflow_engine import WorkflowEngine
from app.models.workflow_engine import (
    ProjectGlossary,
    ProjectTerminologyMemory,
    SpeakerVoiceMapping,
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
    watermark_enabled: Optional[bool] = Field(False, description="Enable watermark embedding")
    watermark_type: Optional[str] = Field("image", description="Watermark type: image or text")
    watermark_image_path: Optional[str] = Field(None, description="Watermark image path")
    watermark_text: Optional[str] = Field(None, description="Watermark text")
    watermark_position: Optional[str] = Field("bottom_right", description="Watermark position")
    watermark_scale: Optional[float] = Field(0.20, description="Watermark scale")
    watermark_opacity: Optional[float] = Field(0.80, description="Watermark opacity")
    watermark_margin: Optional[int] = Field(20, description="Watermark margin")
    watermark_font_size: Optional[int] = Field(32, description="Watermark font size")


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

    stmt = select(WorkflowExecution).where(WorkflowExecution.project_id == project_id)
    res = await session.execute(stmt)
    wf_exec = res.scalars().first()

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
            elif v is not None:
                ctx_data[k] = v

    ctx_data["settings_snapshot"] = proj_settings

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
async def resume_workflow_api(project_id: str, session: AsyncSession = Depends(get_session)):
    """Resume unified 6-stage workflow engine from failed/paused stage."""
    await _validate_project_exists(project_id, session)
    wf_exec = await _global_workflow_engine.resume_workflow(project_id, session)
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
            TranslationJobStatus.PAUSED.value,
            TranslationJobStatus.CREATED.value,
        ]:
            signal_job_cancellation(job.id)
            job.error_message = None
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
        "data": [
            {
                "id": t.id,
                "source_term": t.source_term,
                "translated_term": t.translated_term,
                "term_type": t.term_type,
                "approved": t.approved,
            }
            for t in terms
        ],
    }


@router.post("/projects/{project_id}/glossary", response_model=dict)
async def add_project_glossary_api(
    project_id: str, payload: GlossaryTermCreate, session: AsyncSession = Depends(get_session)
):
    """Add a new term to the project glossary."""
    term = ProjectGlossary(
        id=str(uuid.uuid4()),
        project_id=project_id,
        source_term=payload.source_term,
        translated_term=payload.translated_term,
        term_type=payload.term_type,
        approved=True,
    )
    session.add(term)
    await session.commit()
    return {"success": True, "data": {"id": term.id, "source_term": term.source_term}}


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


# ── Terminology Memory Endpoints ────────────────────────────────────

class TerminologyMemoryCreate(BaseModel):
    source_term: str = Field(..., description="Source term")
    suggested_term: str = Field(..., description="Suggested/translated term")
    term_type: str = Field("other", description="character, location, organization, skill, weapon, title, other")
    confidence: float = Field(0.9, description="Confidence score")
    needs_review: bool = Field(False, description="Requires human review")


@router.get("/projects/{project_id}/terminology-memory", response_model=dict)
async def get_terminology_memory_api(project_id: str, session: AsyncSession = Depends(get_session)):
    """List AI auto-detected terminology memory terms."""
    stmt = select(ProjectTerminologyMemory).where(ProjectTerminologyMemory.project_id == project_id)
    res = await session.execute(stmt)
    terms = res.scalars().all()
    return {
        "success": True,
        "data": [
            {
                "id": t.id,
                "source_term": t.source_term,
                "suggested_term": t.suggested_term,
                "term_type": t.term_type,
                "confidence": t.confidence,
                "needs_review": t.needs_review,
            }
            for t in terms
        ],
    }


@router.post("/projects/{project_id}/terminology-memory", response_model=dict)
async def add_terminology_memory_api(
    project_id: str, payload: TerminologyMemoryCreate, session: AsyncSession = Depends(get_session)
):
    """Add or update term in terminology memory."""
    stmt = select(ProjectTerminologyMemory).where(
        ProjectTerminologyMemory.project_id == project_id,
        ProjectTerminologyMemory.source_term == payload.source_term,
    )
    res = await session.execute(stmt)
    term = res.scalars().first()

    if not term:
        term = ProjectTerminologyMemory(
            id=str(uuid.uuid4()),
            project_id=project_id,
            source_term=payload.source_term,
            suggested_term=payload.suggested_term,
            term_type=payload.term_type,
            confidence=payload.confidence,
            needs_review=payload.needs_review,
        )
        session.add(term)
    else:
        term.suggested_term = payload.suggested_term
        term.term_type = payload.term_type
        term.confidence = payload.confidence
        term.needs_review = payload.needs_review

    await session.commit()
    return {"success": True, "data": {"id": term.id, "source_term": term.source_term}}


@router.delete("/projects/{project_id}/terminology-memory/{term_id}", response_model=dict)
async def delete_terminology_memory_api(
    project_id: str, term_id: str, session: AsyncSession = Depends(get_session)
):
    """Delete a terminology memory item."""
    await session.execute(
        delete(ProjectTerminologyMemory).where(
            ProjectTerminologyMemory.id == term_id, ProjectTerminologyMemory.project_id == project_id
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
        )
        session.add(mapping)
    else:
        mapping.speaker_name = payload.speaker_name or payload.speaker_id
        mapping.voice_provider = payload.voice_provider
        mapping.voice_id = payload.voice_id

    await session.commit()
    return {"success": True, "data": {"id": mapping.id, "speaker_id": mapping.speaker_id}}

