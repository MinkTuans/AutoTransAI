"""
REST API Routes for AI Auto Thumbnail Generation.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from app.config import get_settings
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session, async_session_factory
from app.models.video_thumbnail import VideoThumbnail, ThumbnailStatus
from app.models.project import Project
from app.models.video_translator import VideoTranslationJob, VideoAsset
from app.services.thumbnail_service import ThumbnailService
from app.services.ai_routing import classify_failure
from app.core import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/thumbnails", tags=["thumbnails"])
settings = get_settings()
_LIBRARY_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def _library_dir(project_id: str) -> Path:
    path = settings.PROJECTS_DIR / project_id / "default_thumbnails"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _library_item(project_id: str, file_path: Path) -> Dict[str, Any]:
    rel = file_path.resolve().relative_to(settings.STORAGE_ROOT.resolve()).as_posix()
    return {
        "filename": file_path.name,
        "path": str(file_path),
        "url": f"/api/storage/files/{rel}",
        "size": file_path.stat().st_size,
    }


@router.get("/library/{project_id}", response_model=Dict[str, Any])
async def list_default_thumbnails(project_id: str):
    folder = _library_dir(project_id)
    items = [
        _library_item(project_id, p)
        for p in sorted(folder.iterdir())
        if p.is_file() and p.suffix.lower() in _LIBRARY_EXTS
    ]
    # Enforce single cover photo mode by returning only the latest single item if multiple exist
    return {"success": True, "data": items[-1:] if items else []}


@router.post("/library/{project_id}", response_model=Dict[str, Any])
async def upload_default_thumbnail(project_id: str, file: UploadFile = File(...)):
    ext = Path(file.filename or "cover.png").suffix.lower()
    if ext not in _LIBRARY_EXTS:
        raise HTTPException(status_code=400, detail="❌ Chỉ nhận PNG, JPG, JPEG, WEBP.")
    folder = _library_dir(project_id)
    # Purge any previous cover images in project default_thumbnails folder to ensure single cover photo mode
    for existing in folder.iterdir():
        if existing.is_file() and existing.suffix.lower() in _LIBRARY_EXTS:
            try:
                existing.unlink()
            except Exception:
                pass
    safe_name = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in (file.filename or f"thumb{ext}"))
    dest = folder / safe_name
    dest.write_bytes(await file.read())
    return {"success": True, "data": _library_item(project_id, dest)}


@router.delete("/library/{project_id}/{filename}", response_model=Dict[str, Any])
async def delete_default_thumbnail(project_id: str, filename: str):
    dest = _library_dir(project_id) / Path(filename).name
    if dest.exists():
        dest.unlink()
    return {"success": True, "data": {"deleted": True}}



class GenerateThumbnailRequest(BaseModel):
    project_id: Optional[str] = None
    job_id: Optional[str] = None
    asset_id: Optional[str] = None
    selected_style: str = Field(default="auto")
    custom_instruction: Optional[str] = Field(default=None, max_length=500)
    provider_id: Optional[str] = None
    model_id: Optional[str] = None


class RegenerateThumbnailRequest(BaseModel):
    selected_style: str = Field(default="auto")
    custom_instruction: Optional[str] = Field(default=None, max_length=500)
    provider_id: Optional[str] = None
    model_id: Optional[str] = None


def _format_thumbnail_response(record: VideoThumbnail) -> Dict[str, Any]:
    ai_analysis = None
    if record.ai_analysis_json:
        try:
            ai_analysis = json.loads(record.ai_analysis_json)
        except Exception:
            pass

    return {
        "id": record.id,
        "project_id": record.project_id,
        "job_id": record.job_id,
        "asset_id": record.asset_id,
        "source_title": record.source_title,
        "source_description": record.source_description,
        "selected_style": record.selected_style,
        "custom_instruction": record.custom_instruction,
        "ai_analysis": ai_analysis,
        "generated_prompt": record.generated_prompt,
        "provider": record.provider,
        "model": record.model,
        "r2_key": record.r2_key,
        "thumbnail_url": record.thumbnail_url,
        "width": record.width,
        "height": record.height,
        "aspect_ratio": record.aspect_ratio,
        "status": record.status,
        "error_message": record.error_message,
        "is_active": record.is_active,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
    }


@router.post("/generate", response_model=Dict[str, Any])
async def generate_thumbnail_endpoint(
    req: GenerateThumbnailRequest,
    db: AsyncSession = Depends(get_session),
):
    """Generate a video thumbnail based on video title, transcript, style, and instructions."""
    if not req.project_id and not req.job_id and not req.asset_id:
        raise HTTPException(
            status_code=400,
            detail="Must specify at least one of 'project_id', 'job_id', or 'asset_id'.",
        )

    try:
        record = await ThumbnailService.create_thumbnail(
            db=db,
            project_id=req.project_id,
            job_id=req.job_id,
            asset_id=req.asset_id,
            selected_style=req.selected_style,
            custom_instruction=req.custom_instruction,
            provider_id=req.provider_id,
            model_id=req.model_id,
            sessions=async_session_factory,
            data_dir=settings.DATA_DIR,
        )
        return {
            "success": record.status == ThumbnailStatus.COMPLETED.value,
            "thumbnail": _format_thumbnail_response(record),
        }
    except ValueError as ve:
        detail = ("Thumbnail generation is already in progress for this video."
                  if str(ve) == "Thumbnail generation is already in progress for this video."
                  else "Invalid thumbnail request.")
        raise HTTPException(status_code=400, detail=detail)
    except Exception as ex:
        logger.error("Failed creating thumbnail", code=classify_failure(ex))
        raise HTTPException(status_code=500, detail="Thumbnail generation failed.")


@router.get("/{thumbnail_id}", response_model=Dict[str, Any])
async def get_thumbnail_endpoint(
    thumbnail_id: str,
    db: AsyncSession = Depends(get_session),
):
    """Get thumbnail details by ID."""
    stmt = select(VideoThumbnail).where(VideoThumbnail.id == thumbnail_id)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=444, detail="Thumbnail not found.")

    return {
        "success": True,
        "thumbnail": _format_thumbnail_response(record),
    }


@router.get("/by-project/{project_id}", response_model=Dict[str, Any])
async def get_thumbnails_by_project(
    project_id: str,
    db: AsyncSession = Depends(get_session),
):
    """List all generated thumbnails for a project."""
    stmt = (
        select(VideoThumbnail)
        .where(VideoThumbnail.project_id == project_id)
        .order_by(VideoThumbnail.created_at.desc())
    )
    res = await db.execute(stmt)
    records = res.scalars().all()

    return {
        "success": True,
        "thumbnails": [_format_thumbnail_response(r) for r in records],
    }


@router.get("/by-job/{job_id}", response_model=Dict[str, Any])
async def get_thumbnails_by_job(
    job_id: str,
    db: AsyncSession = Depends(get_session),
):
    """List all generated thumbnails for a video translation job."""
    stmt = (
        select(VideoThumbnail)
        .where(VideoThumbnail.job_id == job_id)
        .order_by(VideoThumbnail.created_at.desc())
    )
    res = await db.execute(stmt)
    records = res.scalars().all()

    return {
        "success": True,
        "thumbnails": [_format_thumbnail_response(r) for r in records],
    }


@router.post("/{thumbnail_id}/regenerate", response_model=Dict[str, Any])
async def regenerate_thumbnail_endpoint(
    thumbnail_id: str,
    req: RegenerateThumbnailRequest,
    db: AsyncSession = Depends(get_session),
):
    """Regenerate a thumbnail with updated style or instructions."""
    stmt = select(VideoThumbnail).where(VideoThumbnail.id == thumbnail_id)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Thumbnail not found.")

    try:
        new_record = await ThumbnailService.create_thumbnail(
            db=db,
            project_id=record.project_id,
            job_id=record.job_id,
            asset_id=record.asset_id,
            selected_style=req.selected_style or record.selected_style,
            custom_instruction=req.custom_instruction if req.custom_instruction is not None else record.custom_instruction,
            provider_id=(record.provider if req.provider_id is None and req.model_id is None
                         else req.provider_id),
            model_id=(record.model if req.provider_id is None and req.model_id is None
                      else req.model_id),
            historical_selection_hint=req.provider_id is None and req.model_id is None,
            sessions=async_session_factory,
            data_dir=settings.DATA_DIR,
        )
        return {
            "success": new_record.status == ThumbnailStatus.COMPLETED.value,
            "thumbnail": _format_thumbnail_response(new_record),
        }
    except Exception as ex:
        logger.error("Failed regenerating thumbnail", code=classify_failure(ex))
        raise HTTPException(status_code=500, detail="Thumbnail regeneration failed.")


@router.post("/{thumbnail_id}/set-active", response_model=Dict[str, Any])
async def set_active_thumbnail(
    thumbnail_id: str,
    db: AsyncSession = Depends(get_session),
):
    """Set a specific thumbnail as the current active thumbnail."""
    stmt = select(VideoThumbnail).where(VideoThumbnail.id == thumbnail_id)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()

    if not record or not record.thumbnail_url:
        raise HTTPException(status_code=404, detail="Valid thumbnail not found.")

    # Deactivate other thumbnails for same target
    deact_stmt = update(VideoThumbnail).values(is_active=False)
    if record.project_id:
        deact_stmt = deact_stmt.where(VideoThumbnail.project_id == record.project_id)
    elif record.job_id:
        deact_stmt = deact_stmt.where(VideoThumbnail.job_id == record.job_id)
    elif record.asset_id:
        deact_stmt = deact_stmt.where(VideoThumbnail.asset_id == record.asset_id)

    await db.execute(deact_stmt)

    record.is_active = True

    # Update direct entity references
    if record.project_id:
        await db.execute(
            update(Project)
            .where(Project.id == record.project_id)
            .values(thumbnail_url=record.thumbnail_url, thumbnail_r2_key=record.r2_key)
        )
    if record.job_id:
        await db.execute(
            update(VideoTranslationJob)
            .where(VideoTranslationJob.id == record.job_id)
            .values(thumbnail_url=record.thumbnail_url, thumbnail_r2_key=record.r2_key)
        )
    if record.asset_id:
        await db.execute(
            update(VideoAsset)
            .where(VideoAsset.id == record.asset_id)
            .values(thumbnail_url=record.thumbnail_url, thumbnail_r2_key=record.r2_key)
        )

    await db.commit()
    await db.refresh(record)

    return {
        "success": True,
        "thumbnail": _format_thumbnail_response(record),
    }


@router.delete("/{thumbnail_id}", response_model=Dict[str, Any])
async def delete_thumbnail_endpoint(
    thumbnail_id: str,
    db: AsyncSession = Depends(get_session),
):
    """Delete thumbnail record and purge storage object."""
    success = await ThumbnailService.delete_thumbnail(db, thumbnail_id)
    if not success:
        raise HTTPException(status_code=404, detail="Thumbnail not found or already deleted.")

    return {
        "success": True,
        "message": f"Thumbnail '{thumbnail_id}' successfully deleted.",
    }
