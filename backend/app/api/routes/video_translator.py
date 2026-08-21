"""
Video Translator API Routes.

Endpoints for checking video URLs, importing video assets (Upload & URL),
managing translation jobs, reviewing transcript segments, and triggering render.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.config import get_settings
from app.core import get_logger
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

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/video-translator", tags=["video-translator"])

# Progress queues for SSE stream
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


class ImportURLRequest(BaseModel):
    source_type: str = Field("url", description="url or upload")
    url: Optional[str] = None
    title: Optional[str] = None


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
    """
    Validate Video URL and return metadata (Source, Title, Duration, Resolution, Audio).
    """
    service = get_video_source_service()
    try:
        metadata = await service.get_metadata(body.url)
        return {
            "success": True,
            "data": metadata,
        }
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
    """
    Import video asset from Video URL or File Upload.
    """
    service = get_video_source_service()
    asset_id = str(uuid.uuid4())[:8]
    storage_dir = settings.DATA_DIR / "translator" / "assets" / asset_id
    storage_dir.mkdir(parents=True, exist_ok=True)

    if source_type == "upload":
        if not file:
            raise HTTPException(status_code=400, detail="❌ Không tìm thấy file video upload.")
        temp_upload_path = storage_dir / f"raw_{file.filename}"
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


@router.get("/assets/{asset_id}", response_model=dict)
async def get_video_asset(asset_id: str, session: AsyncSession = Depends(get_session)):
    """Get video asset metadata by ID."""
    res = await session.execute(select(VideoAsset).where(VideoAsset.id == asset_id))
    asset = res.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="❌ VideoAsset không tồn tại.")

    return {
        "success": True,
        "data": {
            "id": asset.id,
            "source_type": asset.source_type,
            "source_url": asset.source_url,
            "source_domain": asset.source_domain,
            "title": asset.title,
            "duration": asset.duration,
            "width": asset.width,
            "height": asset.height,
            "file_size": asset.file_size,
            "audio_available": asset.audio_available,
            "file_path": asset.file_path,
            "status": asset.status,
            "created_at": asset.created_at,
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

    job_id = str(uuid.uuid4())[:8]
    job = VideoTranslationJob(
        id=job_id,
        asset_id=body.asset_id,
        source_language=body.source_language,
        target_language=body.target_language,
        audio_provider_id=body.audio_provider_id,
        voice_id=body.voice_id,
        original_audio_mode=body.original_audio_mode,
        status=TranslationJobStatus.CREATED.value,
        progress_pct=0.0,
        current_step="Khởi tạo job",
    )
    session.add(job)
    await session.commit()

    return {
        "success": True,
        "data": {
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
    """
    Start Phase 1 of translation pipeline (Extract Audio -> STT -> Translate -> Segment Editor).
    """
    res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Translation Job không tồn tại.")

    async def run_pipeline():
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

            try:
                # 1. Extract Audio
                b_job.status = TranslationJobStatus.EXTRACTING_AUDIO.value
                b_job.current_step = "Trích xuất audio từ video"
                b_job.progress_pct = 20.0
                await bg_session.commit()
                await _emit_job_progress(job_id, {"step": "extracting_audio", "pct": 20})

                extracted_audio_path = job_dir / "extracted_audio.wav"
                try:
                    await extract_audio_from_video(Path(b_asset.file_path), extracted_audio_path)
                except ValueError as ve:
                    b_job.status = TranslationJobStatus.FAILED.value
                    b_job.error_message = f"❌ {str(ve)}"
                    await bg_session.commit()
                    return

                # 2. STT & Language Detection
                b_job.status = TranslationJobStatus.STT.value
                b_job.current_step = "Nhận diện giọng nói (Speech-to-Text)"
                b_job.progress_pct = 40.0
                await bg_session.commit()
                await _emit_job_progress(job_id, {"step": "stt", "pct": 40})

                segments_raw, detected_lang = await speech_to_text_and_detect_language(
                    extracted_audio_path,
                    target_language=b_job.target_language,
                    source_language=b_job.source_language,
                )

                b_job.detected_language = detected_lang
                b_job.status = TranslationJobStatus.TRANSLATED.value
                b_job.current_step = "Đang dịch bản thoại"
                b_job.progress_pct = 60.0
                await bg_session.commit()

                # 3. Translate
                translated_segs = await translate_transcript_segments(
                    segments_raw,
                    source_language=detected_lang,
                    target_language=b_job.target_language,
                )

                # Save segments to DB
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
                b_job.current_step = "Chờ xem lại & chỉnh sửa bản dịch"
                b_job.progress_pct = 70.0
                await bg_session.commit()
                await _emit_job_progress(job_id, {"step": "segment_editing", "pct": 70})

            except Exception as e:
                logger.exception("Translation pipeline failed", job_id=job_id)
                b_job.status = TranslationJobStatus.FAILED.value
                b_job.error_message = str(e)
                await bg_session.commit()
                await _emit_job_progress(job_id, {"step": "failed", "error": str(e)})

    background_tasks.add_task(run_pipeline)
    return {"success": True, "data": {"started": True, "job_id": job_id}}


@router.get("/jobs/{job_id}", response_model=dict)
async def get_translation_job(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get job progress status and segment details."""
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

    return {
        "success": True,
        "data": {
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
            "progress_pct": job.progress_pct,
            "current_step": job.current_step,
            "output_video_path": job.output_video_path,
            "error_message": job.error_message,
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
    return {"success": True, "data": {"updated": len(body.segments)}}


@router.post("/jobs/{job_id}/render", response_model=dict)
async def render_final_translated_video(
    job_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """
    Execute Phase 2 (TTS Generation -> Audio Sync -> FFmpeg Render Final Video).
    """
    res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Job không tồn tại.")

    async def run_render():
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
                b_job.error_message = f"❌ Audio provider '{b_job.audio_provider_id}' không được hỗ trợ."
                await bg_session.commit()
                return

            try:
                # 1. TTS Generation
                b_job.status = TranslationJobStatus.GENERATING_TTS.value
                b_job.current_step = "Đang tạo giọng đọc TTS"
                b_job.progress_pct = 75.0
                await bg_session.commit()
                await _emit_job_progress(job_id, {"step": "tts", "pct": 75})

                voice_id = b_job.voice_id or "vi-VN-HoaiMyNeural"

                for seg in segments:
                    seg_tts_path = tts_dir / f"seg_{seg.segment_number:03d}.wav"
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
                    await bg_session.commit()

                # 2. Audio Synchronization (Time-stretch)
                b_job.status = TranslationJobStatus.SYNCING_AUDIO.value
                b_job.current_step = "Đang đồng bộ Audio theo mốc thời gian"
                b_job.progress_pct = 85.0
                await bg_session.commit()
                await _emit_job_progress(job_id, {"step": "syncing", "pct": 85})

                for seg in segments:
                    target_dur = max(1.0, seg.end_time - seg.start_time)
                    synced_path = sync_dir / f"seg_{seg.segment_number:03d}_synced.wav"
                    await sync_and_stretch_audio(
                        Path(seg.tts_audio_path),
                        target_duration=target_dur,
                        output_synced_path=synced_path,
                    )
                    seg.synced_audio_path = str(synced_path)
                    await bg_session.commit()

                # 3. Render Final Video
                b_job.status = TranslationJobStatus.RENDERING.value
                b_job.current_step = "Đang render video lồng tiếng bằng FFmpeg"
                b_job.progress_pct = 95.0
                await bg_session.commit()
                await _emit_job_progress(job_id, {"step": "rendering", "pct": 95})

                final_video_path = job_dir / "final_dubbed_video.mp4"
                await render_dubbed_video(
                    video_path=Path(b_asset.file_path),
                    segments=segments,
                    original_audio_mode=b_job.original_audio_mode,
                    output_video_path=final_video_path,
                    work_dir=job_dir / "work",
                )

                b_job.status = TranslationJobStatus.COMPLETED.value
                b_job.current_step = "Hoàn tất lồng tiếng video"
                b_job.progress_pct = 100.0
                b_job.output_video_path = str(final_video_path)
                await bg_session.commit()
                await _emit_job_progress(job_id, {"step": "completed", "pct": 100, "file": str(final_video_path)})

            except Exception as e:
                logger.exception("Render dubbed video failed", job_id=job_id)
                b_job.status = TranslationJobStatus.FAILED.value
                b_job.error_message = str(e)
                await bg_session.commit()
                await _emit_job_progress(job_id, {"step": "failed", "error": str(e)})

    background_tasks.add_task(run_render)
    return {"success": True, "data": {"rendering": True, "job_id": job_id}}


@router.get("/jobs/{job_id}/stream")
async def job_sse_stream(job_id: str):
    """SSE endpoint for real-time translation job progress updates."""
    queue: asyncio.Queue = asyncio.Queue()
    _job_sse_queues[job_id] = queue

    async def event_generator():
        try:
            while True:
                data = await queue.get()
                yield {
                    "event": "progress",
                    "data": json.dumps(data, ensure_ascii=False),
                }
        except asyncio.CancelledError:
            _job_sse_queues.pop(job_id, None)

    return EventSourceResponse(event_generator())
