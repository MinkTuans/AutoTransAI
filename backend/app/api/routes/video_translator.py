"""
Video Translator API Routes.

Endpoints for checking video URLs, importing video assets, managing translation jobs,
monitoring real-time FFmpeg process stats & heartbeats, reviewing logs, cancel, and smart retry.
"""

from __future__ import annotations

import asyncio
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
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core import get_logger
from app.services.storage_service import storage_service
from app.core.job_logger import log_job_event, get_job_logs
from app.database import get_session, async_session_factory
from app.core.security_url import SSRFValidationError
from app.models.video_translator import (
    VideoAsset,
    VideoTranslationJob,
    VideoTranslationSegment,
    AssetSourceType,
    TranslationJobStatus,
    AudioMixMode,
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
    asset_id: str
    source_language: str = "auto"
    target_language: str = "vi"
    audio_provider_id: str = "edge_tts"
    voice_id: Optional[str] = None
    original_audio_mode: str = "mute"


class SegmentUpdateItem(BaseModel):
    id: int
    translated_text: str


class UpdateSegmentsRequest(BaseModel):
    segments: List[SegmentUpdateItem]


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
        with open(temp_upload_path, "wb") as f:
            content = await file.read()
            f.write(content)

        try:
            meta = await service.import_uploaded_file(temp_upload_path, file.filename or "video.mp4", storage_dir)
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


@router.post("/jobs", response_model=dict)
async def create_translation_job(
    body: CreateJobRequest,
    session: AsyncSession = Depends(get_session),
):
    """Create a new video translation job."""
    res = await session.execute(select(VideoAsset).where(VideoAsset.id == body.asset_id))
    asset = res.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="❌ VideoAsset không tồn tại.")

    job_id = f"VT-{str(uuid.uuid4())[:6].upper()}"
    job = VideoTranslationJob(
        id=job_id,
        asset_id=body.asset_id,
        source_language=body.source_language,
        target_language=body.target_language,
        audio_provider_id=body.audio_provider_id,
        voice_id=body.voice_id,
        original_audio_mode=body.original_audio_mode,
        status=TranslationJobStatus.CREATED.value,
        stage="QUEUED",
        stage_progress_pct=0.0,
        overall_progress_pct=0.0,
        current_step="Khởi tạo job",
        last_heartbeat=datetime.now(timezone.utc),
    )
    session.add(job)
    await session.commit()
    log_job_event(job_id, "CREATED", f"Job created for asset '{asset.title}' (ID: {asset.id})")

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

                try:
                    await extract_audio_from_video(
                        Path(b_asset.file_path),
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
                )

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
                )

                # Clear previous segments if any
                existing_segs = await bg_session.execute(
                    select(VideoTranslationSegment).where(VideoTranslationSegment.job_id == job_id)
                )
                for es in existing_segs.scalars().all():
                    await bg_session.delete(es)

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

                b_job.status = TranslationJobStatus.SEGMENT_EDITING.value
                b_job.stage = "SEGMENT_EDITING"
                b_job.current_step = "Chờ xem lại & chỉnh sửa bản dịch"
                b_job.stage_progress_pct = 100.0
                b_job.overall_progress_pct = 60.0
                b_job.total_segments_count = len(translated_segs)
                b_job.completed_segments_count = 0
                b_job.pid = None
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

            if isinstance(e, FFmpegExecutionError):
                full_err_log += f"\nFFmpeg Exit Code: {e.exit_code}\nFFmpeg Stderr: {e.stderr_text}\nCommand: {' '.join(e.cmd)}"

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
                        error_message=f"{err_name}: {err_msg[:300]}",
                        pid=None,
                        updated_at=datetime.now(timezone.utc),
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
                last_heartbeat=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
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
            .values(pid=pid, last_heartbeat=datetime.now(timezone.utc))
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
    now = datetime.now(timezone.utc)
    hb_age_sec = (now - job.last_heartbeat.replace(tzinfo=timezone.utc)).total_seconds() if job.last_heartbeat else 999.0

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
    for item in body.segments:
        await session.execute(
            update(VideoTranslationSegment)
            .where(VideoTranslationSegment.id == item.id)
            .where(VideoTranslationSegment.job_id == job_id)
            .values(translated_text=item.translated_text)
        )
    await session.commit()
    log_job_event(job_id, "SEGMENT_EDITING", f"Updated text for {len(body.segments)} segments.")
    return {"success": True, "data": {"updated": len(body.segments)}}


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
        start_job_heartbeat(job_id)
        current_stage = "GENERATING_TTS"
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

                seg_res = await bg_session.execute(
                    select(VideoTranslationSegment)
                    .where(VideoTranslationSegment.job_id == job_id)
                    .order_by(VideoTranslationSegment.segment_number)
                )
                segments = seg_res.scalars().all()

                job_dir = settings.DATA_DIR / "translator" / "jobs" / job_id
                tts_dir = job_dir / "tts"
                sync_dir = job_dir / "synced"
                tts_dir.mkdir(parents=True, exist_ok=True)
                sync_dir.mkdir(parents=True, exist_ok=True)

                registry = get_registry()
                audio_provider = registry.get_audio(b_job.audio_provider_id or "edge_tts")
                if not audio_provider:
                    b_job.status = TranslationJobStatus.FAILED.value
                    b_job.stage = "FAILED"
                    b_job.error_message = f"❌ Audio provider '{b_job.audio_provider_id}' không được hỗ trợ."
                    await bg_session.commit()
                    return

                # 1. TTS Generation
                current_stage = "GENERATING_TTS"
                b_job.status = TranslationJobStatus.GENERATING_TTS.value
                b_job.stage = "GENERATING_TTS"
                b_job.current_step = f"Đang tạo giọng đọc TTS (0/{len(segments)})"
                b_job.total_segments_count = len(segments)
                b_job.completed_segments_count = 0
                b_job.stage_progress_pct = 0.0
                b_job.overall_progress_pct = calculate_overall_progress("GENERATING_TTS", 0.0)
                await bg_session.commit()
                log_job_event(job_id, "GENERATING_TTS", f"Starting TTS generation for {len(segments)} segments...")

                voice_id = b_job.voice_id or "vi-VN-HoaiMyNeural"

                for idx, seg in enumerate(segments, start=1):
                    seg_tts_path = tts_dir / f"seg_{seg.segment_number:03d}.wav"
                    log_job_event(job_id, "GENERATING_TTS", f"Generating TTS for segment #{seg.segment_number}/{len(segments)}")

                    res = await audio_provider.generate_audio(
                        text=seg.translated_text,
                        voice_id=voice_id,
                        output_path=seg_tts_path,
                    )
                    if not res.success or not seg_tts_path.exists():
                        raise RuntimeError(f"❌ Không thể tạo giọng đọc cho Segment #{seg.segment_number}: {res.error_message or 'Lỗi TTS'}")

                    dur = await probe_duration_async(seg_tts_path)
                    seg.tts_audio_path = str(seg_tts_path)
                    seg.tts_audio_duration = dur

                    b_job.completed_segments_count = idx
                    pct = round((idx / len(segments)) * 100.0, 1)
                    b_job.stage_progress_pct = pct
                    b_job.overall_progress_pct = calculate_overall_progress("GENERATING_TTS", pct)
                    b_job.current_step = f"Đang tạo giọng đọc TTS ({idx}/{len(segments)})"
                    await bg_session.commit()

                # 2. Audio Synchronization
                current_stage = "SYNCING_AUDIO"
                b_job.status = TranslationJobStatus.SYNCING_AUDIO.value
                b_job.stage = "SYNCING_AUDIO"
                b_job.current_step = "Đang đồng bộ Audio theo mốc thời gian"
                b_job.stage_progress_pct = 0.0
                b_job.overall_progress_pct = calculate_overall_progress("SYNCING_AUDIO", 0.0)
                await bg_session.commit()
                log_job_event(job_id, "SYNCING_AUDIO", "Starting audio time-stretch synchronization...")

                for idx, seg in enumerate(segments, start=1):
                    target_dur = max(1.0, seg.end_time - seg.start_time)
                    synced_path = sync_dir / f"seg_{seg.segment_number:03d}_synced.wav"

                    def on_sync_progress(stats: dict):
                        asyncio.create_task(_update_ffmpeg_stats(job_id, "SYNCING_AUDIO", stats.get("progress_pct", 0.0), stats.get("pid"), stats))

                    def on_sync_pid(pid: int):
                        asyncio.create_task(_update_pid(job_id, pid))

                    await sync_and_stretch_audio(
                        Path(seg.tts_audio_path),
                        target_duration=target_dur,
                        output_synced_path=synced_path,
                        job_id=job_id,
                        on_progress=on_sync_progress,
                        on_pid=on_sync_pid,
                    )
                    seg.synced_audio_path = str(synced_path)
                    sync_pct = round((idx / len(segments)) * 100.0, 1)
                    b_job.stage_progress_pct = sync_pct
                    b_job.overall_progress_pct = calculate_overall_progress("SYNCING_AUDIO", sync_pct)
                    await bg_session.commit()

                # 3. Render Final Video
                current_stage = "RENDERING"
                b_job.status = TranslationJobStatus.RENDERING.value
                b_job.stage = "RENDERING"
                b_job.current_step = "Đang render video lồng tiếng bằng FFmpeg"
                b_job.stage_progress_pct = 0.0
                b_job.overall_progress_pct = calculate_overall_progress("RENDERING", 0.0)
                await bg_session.commit()
                log_job_event(job_id, "RENDERING", "Starting final FFmpeg video render...")

                def on_render_progress(stats: dict):
                    asyncio.create_task(_update_ffmpeg_stats(job_id, "RENDERING", stats.get("progress_pct", 0.0), stats.get("pid"), stats))

                def on_render_pid(pid: int):
                    asyncio.create_task(_update_pid(job_id, pid))

                final_video_path = job_dir / "final_dubbed_video.mp4"
                rendered_path = await render_dubbed_video(
                    video_path=Path(b_asset.file_path),
                    segments=segments,
                    original_audio_mode=b_job.original_audio_mode,
                    output_video_path=final_video_path,
                    work_dir=job_dir / "work",
                    job_id=job_id,
                    on_progress=on_render_progress,
                    on_pid=on_render_pid,
                )

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

                # Clean intermediate temporary files (TTS audio, synced audio, FFmpeg work dir, temp audio)
                try:
                    tts_dir = job_dir / "tts"
                    if tts_dir.exists():
                        shutil.rmtree(tts_dir, ignore_errors=True)
                    synced_dir = job_dir / "synced"
                    if synced_dir.exists():
                        shutil.rmtree(synced_dir, ignore_errors=True)
                    work_dir = job_dir / "work"
                    if work_dir.exists():
                        shutil.rmtree(work_dir, ignore_errors=True)
                    extracted_audio = job_dir / "extracted_audio.mp3"
                    if extracted_audio.exists():
                        extracted_audio.unlink(missing_ok=True)
                    b_job.is_cleaned = True
                    log_job_event(job_id, "CLEANUP", "Intermediate TTS audio and FFmpeg temp files purged.")
                except Exception as clean_err:
                    logger.warning("Error cleaning intermediate files", error=str(clean_err), job_id=job_id)

                b_job.status = TranslationJobStatus.COMPLETED.value
                b_job.stage = "COMPLETED"
                b_job.current_step = "Hoàn tất lồng tiếng video"
                b_job.stage_progress_pct = 100.0
                b_job.overall_progress_pct = 100.0
                b_job.output_video_path = str(final_video_path)
                b_job.r2_key = object_key
                b_job.output_url = output_url
                b_job.pid = None
                await bg_session.commit()
                log_job_event(job_id, "COMPLETED", f"Final video ready at {output_url or final_video_path}")

        except Exception as e:
            tb_str = traceback.format_exc()
            err_name = type(e).__name__
            err_msg = str(e) or repr(e)
            full_err_log = f"Error: {err_name}: {err_msg}\nStage: {current_stage}\nStack:\n{tb_str}"

            if isinstance(e, FFmpegExecutionError):
                full_err_log += f"\nFFmpeg Exit Code: {e.exit_code}\nFFmpeg Stderr: {e.stderr_text}\nCommand: {' '.join(e.cmd)}"

            logger.exception("Render dubbed video failed", job_id=job_id)
            log_job_event(job_id, "FAILED", f"Render Exception:\n{full_err_log}")

            async with async_session_factory() as bg_session:
                await bg_session.execute(
                    update(VideoTranslationJob)
                    .where(VideoTranslationJob.id == job_id)
                    .values(
                        status=TranslationJobStatus.FAILED.value,
                        stage="FAILED",
                        current_step=f"Lỗi tại stage {current_stage}: {err_name}",
                        error_message=f"{err_name}: {err_msg[:300]}",
                        pid=None,
                        updated_at=datetime.now(timezone.utc),
                    )
                )
                await bg_session.commit()
        finally:
            stop_job_heartbeat(job_id)

    background_tasks.add_task(run_render)
    return {"success": True, "data": {"rendering": True, "job_id": job_id}}


@router.post("/jobs/{job_id}/cancel", response_model=dict)
async def cancel_job_api(job_id: str, session: AsyncSession = Depends(get_session)):
    """Cancel a running translation job and terminate FFmpeg subprocess."""
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
