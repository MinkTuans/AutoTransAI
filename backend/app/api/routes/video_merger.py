"""
Video Merger API Routes.

Provides endpoints for video file uploads, asset browsing, merge job creation,
background processing initiation, real-time status polling, and retry operations.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core import get_logger
from app.database import get_session
from app.models.video_merger import VideoMergeJob, VideoMergeAsset, MergeJobStatus
from app.models.video_translator import VideoAsset
from app.models.asset import Asset
from app.services.video_merger.merger_service import VideoMergerService
from app.media.ffprobe import get_video_metadata_async
from app.services.storage_service import LocalStorageService

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/video-merger", tags=["Video Merger"])


class VideoItemInput(BaseModel):
    id: Optional[str] = None
    original_filename: str
    file_path: str
    file_size: Optional[int] = 0
    duration: float = 0.0
    width: Optional[int] = 0
    height: Optional[int] = 0
    fps: Optional[float] = 30.0
    has_audio: Optional[bool] = True
    thumbnail_url: Optional[str] = None
    order_index: Optional[int] = 0


class CreateMergeJobRequest(BaseModel):
    title: Optional[str] = None
    items: List[VideoItemInput]


@router.post("/upload", response_model=dict)
async def upload_merger_video(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    """
    Upload a video file specifically for the Video Merger workflow.
    Validates MIME/extension, stores file under storage/merger/uploads/,
    extracts metadata via FFprobe, and generates a thumbnail frame.
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="❌ Không tìm thấy file upload.")

    ext = Path(file.filename).suffix.lower()
    allowed_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".ts", ".m4v"}
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"❌ Định dạng file '{ext}' không được hỗ trợ. Chỉ hỗ trợ video: {', '.join(allowed_exts)}",
        )

    asset_id = f"m_asset_{str(uuid.uuid4())[:8]}"
    uploads_dir = VideoMergerService.get_merger_storage_dir() / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    dest_path = uploads_dir / f"{asset_id}_{file.filename}"
    with open(dest_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    if not dest_path.exists() or dest_path.stat().st_size == 0:
        raise HTTPException(status_code=400, detail="❌ Upload thất bại: File 0 byte.")

    # Probe metadata via FFprobe
    try:
        meta = await get_video_metadata_async(dest_path)
    except Exception as e:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"❌ File video upload bị lỗi hoặc không thể đọc được: {str(e)}")

    # Extract thumbnail frame
    thumb_name = f"thumb_{asset_id}.jpg"
    thumb_url = await VideoMergerService.extract_thumbnail_async(dest_path, thumb_name)

    asset = VideoMergeAsset(
        id=asset_id,
        original_filename=file.filename,
        file_path=str(dest_path.resolve()),
        file_size=meta.get("file_size", dest_path.stat().st_size),
        duration=meta.get("duration", 0.0),
        width=meta.get("width", 0),
        height=meta.get("height", 0),
        fps=30.0,
        has_audio=meta.get("has_audio", True),
        thumbnail_url=thumb_url,
    )
    session.add(asset)
    await session.commit()
    await session.refresh(asset)

    return {
        "success": True,
        "data": {
            "id": asset.id,
            "original_filename": asset.original_filename,
            "file_path": asset.file_path,
            "file_size": asset.file_size,
            "duration": asset.duration,
            "width": asset.width,
            "height": asset.height,
            "fps": asset.fps,
            "has_audio": asset.has_audio,
            "thumbnail_url": asset.thumbnail_url,
        },
    }


@router.get("/assets", response_model=dict)
async def list_available_video_assets(
    session: AsyncSession = Depends(get_session),
):
    """
    List existing video assets available in the system across Merger Uploads,
    VideoTranslator VideoAssets, and Project Assets for selecting existing files.
    """
    results: List[Dict[str, Any]] = []

    # 1. Fetch VideoMergeAssets
    res_m = await session.execute(
        select(VideoMergeAsset).order_by(VideoMergeAsset.created_at.desc()).limit(50)
    )
    for m in res_m.scalars().all():
        if Path(m.file_path).exists():
            results.append({
                "id": m.id,
                "source": "merger_upload",
                "original_filename": m.original_filename,
                "file_path": m.file_path,
                "file_size": m.file_size,
                "duration": m.duration,
                "width": m.width,
                "height": m.height,
                "fps": m.fps,
                "has_audio": m.has_audio,
                "thumbnail_url": m.thumbnail_url,
                "title": m.original_filename,
            })

    # 2. Fetch VideoAssets from VideoTranslator
    res_vt = await session.execute(
        select(VideoAsset).order_by(VideoAsset.created_at.desc()).limit(50)
    )
    for v in res_vt.scalars().all():
        if v.file_path and Path(v.file_path).exists():
            results.append({
                "id": v.id,
                "source": "video_translator",
                "original_filename": v.original_filename or v.title,
                "file_path": v.file_path,
                "file_size": v.file_size or 0,
                "duration": v.duration or 0.0,
                "width": v.width or 0,
                "height": v.height or 0,
                "fps": 30.0,
                "has_audio": v.audio_available if v.audio_available is not None else True,
                "thumbnail_url": None,
                "title": v.title or v.original_filename,
            })

    return {"success": True, "data": results}


@router.post("/jobs", response_model=dict)
async def create_merge_job(
    body: CreateMergeJobRequest,
    session: AsyncSession = Depends(get_session),
):
    """Create a new Video Merge Job with the specified video order."""
    if not body.items or len(body.items) == 0:
        raise HTTPException(status_code=400, detail="❌ Vui lòng chọn ít nhất 1 video để ghép.")

    job_id = f"mjob_{str(uuid.uuid4())[:8]}"
    title = body.title or f"Ghép Video {job_id[:8]}"

    items_payload = [item.model_dump() for item in body.items]
    total_dur = sum(item.duration for item in body.items)

    job = VideoMergeJob(
        id=job_id,
        title=title,
        status=MergeJobStatus.PENDING.value,
        progress=0.0,
        input_files_json=json.dumps(items_payload, ensure_ascii=False),
        total_duration=round(total_dur, 2),
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    return {
        "success": True,
        "data": {
            "id": job.id,
            "title": job.title,
            "status": job.status,
            "progress": job.progress,
            "total_duration": job.total_duration,
            "items": items_payload,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        },
    }


@router.post("/jobs/{job_id}/start", response_model=dict)
async def start_merge_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Start background video merge processing for a created job (includes double-click guard)."""
    res = await session.execute(select(VideoMergeJob).where(VideoMergeJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Không tìm thấy merge job.")

    if job.status in (MergeJobStatus.PROCESSING.value, MergeJobStatus.PREPARING.value):
        return {
            "success": True,
            "message": "⚠️ Tiến trình ghép video đã đang chạy.",
            "data": {"job_id": job.id, "status": job.status},
        }

    try:
        items = json.loads(job.input_files_json or "[]")
    except Exception:
        items = []

    if not items:
        raise HTTPException(status_code=400, detail="❌ Job không có danh sách video nguồn hợp lệ.")

    # Guard against double submission by marking status PREPARING immediately
    job.status = MergeJobStatus.PREPARING.value
    job.progress = 2.0
    job.error_message = None
    await session.commit()

    background_tasks.add_task(
        VideoMergerService.execute_merge_job,
        job_id=job.id,
        input_items=items,
        custom_title=job.title,
    )

    return {
        "success": True,
        "data": {
            "job_id": job.id,
            "status": "preparing",
            "progress": 2.0,
        },
    }


@router.get("/jobs/{job_id}", response_model=dict)
async def get_merge_job_status(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get real-time merge job status, progress, input items, and output URL."""
    res = await session.execute(select(VideoMergeJob).where(VideoMergeJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Không tìm thấy merge job.")

    try:
        items = json.loads(job.input_files_json or "[]")
    except Exception:
        items = []

    return {
        "success": True,
        "data": {
            "id": job.id,
            "title": job.title,
            "status": job.status,
            "progress": job.progress,
            "total_duration": job.total_duration,
            "processed_duration": job.processed_duration,
            "output_video_path": job.output_video_path,
            "output_relative_url": job.output_relative_url,
            "output_filename": job.output_filename,
            "error_message": job.error_message,
            "items": items,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        },
    }


@router.get("/jobs", response_model=dict)
async def list_merge_jobs(
    session: AsyncSession = Depends(get_session),
):
    """List recent video merge jobs."""
    res = await session.execute(
        select(VideoMergeJob).order_by(VideoMergeJob.created_at.desc()).limit(30)
    )
    jobs = res.scalars().all()
    out = []
    for j in jobs:
        out.append({
            "id": j.id,
            "title": j.title,
            "status": j.status,
            "progress": j.progress,
            "total_duration": j.total_duration,
            "output_relative_url": j.output_relative_url,
            "error_message": j.error_message,
            "created_at": j.created_at.isoformat() if j.created_at else None,
        })
    return {"success": True, "data": out}


@router.post("/jobs/{job_id}/retry", response_model=dict)
async def retry_merge_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Retry a failed merge job."""
    res = await session.execute(select(VideoMergeJob).where(VideoMergeJob.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="❌ Không tìm thấy merge job.")

    try:
        items = json.loads(job.input_files_json or "[]")
    except Exception:
        items = []

    if not items:
        raise HTTPException(status_code=400, detail="❌ Job không có video nào để thử lại.")

    job.status = MergeJobStatus.PREPARING.value
    job.progress = 2.0
    job.error_message = None
    await session.commit()

    background_tasks.add_task(
        VideoMergerService.execute_merge_job,
        job_id=job.id,
        input_items=items,
        custom_title=job.title,
    )

    return {"success": True, "data": {"job_id": job.id, "status": "preparing"}}


@router.delete("/jobs/{job_id}", response_model=dict)
async def delete_merge_job(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Delete a merge job record."""
    await session.execute(delete(VideoMergeJob).where(VideoMergeJob.id == job_id))
    await session.commit()
    return {"success": True, "message": "Đã xóa merge job."}
