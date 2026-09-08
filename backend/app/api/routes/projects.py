"""
Project API routes.

All project operations go through these endpoints.
The UI never calls providers directly.
"""

from __future__ import annotations

import asyncio
import copy
import uuid
from datetime import datetime, timezone

from typing import Optional
import math
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified
from sse_starlette.sse import EventSourceResponse

from app.database import get_session, async_session_factory
from app.models.project import Project, WorkflowStatus
from app.models.segment import Segment, SegmentStatus
from app.models.video_translator import VideoTranslationJob, VideoAsset, VideoTranslationSegment
from app.models.asset import Asset
from app.models.workflow_engine import ProjectGlossary, ProjectTerminologyMemory, WorkflowExecution
from app.services.storage_service import storage_service
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectListResponse,
    ProjectStatusResponse,
)
from app.schemas.estimate import EstimateResponse, ResourceEstimate
from app.schemas.workflow import PreflightResult
from app.services.estimator import estimate_project
from app.services.file_manager import (
    ensure_project_structure,
    delete_project_files,
    clean_temp_files,
)
from app.services.manifest import create_manifest
from app.usage.quota_manager import validate_quota
from app.providers.registry import get_registry
from app.workflow.orchestrator import WorkflowOrchestrator
from app.workflow.state_machine import is_resumable_state
from app.core import get_logger
from app.config import get_settings

settings = get_settings()

DEFAULT_PROJECT_SETTINGS = {
    "input_mode": "url",
    "video_url": "",
    "video_path": None,
    "source_language": "auto",
    "target_language": "vi",
    "auto_detect_language": True,
    "stt_provider_id": None,
    "stt_model": None,
    "translation_provider_id": None,
    "translation_model": None,
    "audio_provider_id": "edge_tts",
    "voice_id": "vi-VN-HoaiMyNeural",
    "voice_name": "Vietnamese - HoaiMy",
    "speed": 1.0,
    "pitch": 0.0,
    "volume": 1.0,
    "dubbing_mode": "single_voice",
    "original_audio_mode": "mute",
    "original_audio_volume": 0.20,
    "watermark_enabled": False,
    "watermark_type": "image",
    "watermark_image_path": None,
    "watermark_image_asset_id": None,
    "watermark_text": "© AutoTransAI Studio",
    "watermark_position": "bottom_right",
    "watermark_scale": 0.20,
    "watermark_opacity": 0.80,
    "watermark_margin": 20,
    "watermark_font_size": 32,
    "thumbnail_enabled": False,
    "thumbnail_provider": "pollinations",
    "thumbnail_model": "default",
    "thumbnail_style": "auto",
    "thumbnail_custom_instruction": "",
}


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


def normalize_project_settings(raw_settings: Optional[dict]) -> dict:
    """Normalize and validate project settings against system defaults and value constraints."""
    res = copy.deepcopy(DEFAULT_PROJECT_SETTINGS)
    if isinstance(raw_settings, dict):
        for k, v in raw_settings.items():
            if v is not None:
                res[k] = v

    res["watermark_enabled"] = _parse_bool(res.get("watermark_enabled"), False)
    res["thumbnail_enabled"] = _parse_bool(res.get("thumbnail_enabled"), False)

    valid_positions = {"bottom_right", "bottom_left", "top_right", "top_left", "center"}
    pos_str = str(res.get("watermark_position", "bottom_right")).lower()
    res["watermark_position"] = pos_str if pos_str in valid_positions else "bottom_right"

    valid_types = {"image", "text"}
    type_str = str(res.get("watermark_type", "image")).lower()
    res["watermark_type"] = type_str if type_str in valid_types else "image"

    try:
        scale_val = float(res.get("watermark_scale", 0.20))
        if scale_val > 1.0:
            scale_val = scale_val / 100.0
        res["watermark_scale"] = round(min(max(scale_val, 0.01), 1.0), 2)
    except (ValueError, TypeError):
        res["watermark_scale"] = 0.20

    try:
        op_val = float(res.get("watermark_opacity", 0.80))
        if op_val > 1.0:
            op_val = op_val / 100.0
        res["watermark_opacity"] = round(min(max(op_val, 0.05), 1.0), 2)
    except (ValueError, TypeError):
        res["watermark_opacity"] = 0.80

    try:
        res["watermark_margin"] = int(res.get("watermark_margin", 20))
    except (ValueError, TypeError):
        res["watermark_margin"] = 20

    if res.get("watermark_image_path"):
        path_str = str(res["watermark_image_path"]).replace("\\", "/")
        if "storage/" in path_str:
            path_str = path_str.split("storage/")[-1]
        elif "data/" in path_str:
            path_str = path_str.split("data/")[-1]
        res["watermark_image_path"] = path_str

    return res

class BatchDeleteRequest(BaseModel):
    ids: list[str]

logger = get_logger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])

# Track running workflows for cancellation
_running_workflows: dict[str, WorkflowOrchestrator] = {}


@router.post("", response_model=dict)
async def create_project(
    body: ProjectCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create a new project and parse script if provided."""
    project_id = str(uuid.uuid4())[:8]

    # Parse script if script provided
    segments = parse_script(body.script) if body.script and body.script.strip() else []
    warnings = validate_segments(segments) if segments else []

    # Create project
    project = Project(
        id=project_id,
        title=body.title or "Untitled Project",
        description=body.description,
        script_raw=body.script or "",
        workflow_mode=body.workflow_mode,
        workflow_status=WorkflowStatus.PARSED.value if segments else WorkflowStatus.CREATED.value,
        settings_json=normalize_project_settings(body.settings_json or {}),
    )
    session.add(project)

    # Create segments
    for seg in segments:
        db_segment = Segment(
            project_id=project_id,
            segment_number=seg.number,
            text_content=seg.text,
            char_count=seg.char_count,
        )
        session.add(db_segment)

    await session.commit()

    # Create project directory structure
    ensure_project_structure(project_id)

    # Create initial manifest
    create_manifest(project_id, {
        "title": body.title,
        "workflow_mode": body.workflow_mode,
        "workflow_status": WorkflowStatus.PARSED.value if segments else WorkflowStatus.CREATED.value,
        "segments": [
            {"number": s.number, "text": s.text[:100], "char_count": s.char_count}
            for s in segments
        ],
    })

    logger.info(
        "Project created",
        project_id=project_id,
        segments=len(segments),
        mode=body.workflow_mode,
    )

    return {
        "success": True,
        "data": {
            "project_id": project_id,
            "id": project_id,
            "title": project.title,
            "description": project.description,
            "settings_json": project.settings_json,
            "segment_count": len(segments),
            "total_characters": sum(s.char_count for s in segments),
            "warnings": warnings,
        },
    }


@router.get("", response_model=dict)
async def list_projects(
    page: Optional[int] = Query(None, ge=1, description="Page number (1-based)"),
    page_size: int = Query(8, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_session)
):
    """List projects with optional server-side pagination (default page_size=8)."""
    # 1. Fetch standard projects
    std_result = await session.execute(
        select(Project).order_by(Project.created_at.desc())
    )
    std_projects = std_result.scalars().all()

    seen_ids = set()
    items = []
    for p in std_projects:
        seen_ids.add(p.id)
        seg_count = await session.execute(
            select(func.count(Segment.id)).where(Segment.project_id == p.id)
        )
        count = seg_count.scalar() or 0
        items.append({
            "id": p.id,
            "job_id": p.id,
            "title": p.title,
            "type": "standard",
            "workflow_mode": p.workflow_mode,
            "workflow_status": p.workflow_status,
            "status": p.workflow_status,
            "progress": 100.0 if p.workflow_status == "completed" else 0.0,
            "segment_count": count,
            "output_video_url": p.media_url,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        })

    # 2. Fetch Video Translator jobs
    vt_result = await session.execute(
        select(VideoTranslationJob)
        .options(selectinload(VideoTranslationJob.asset))
        .order_by(VideoTranslationJob.created_at.desc())
    )
    vt_jobs = vt_result.scalars().all()

    for vt in vt_jobs:
        if vt.id in seen_ids or (vt.project_id and vt.project_id in seen_ids):
            continue
        seen_ids.add(vt.id)
        title = vt.asset.title if (vt.asset and vt.asset.title) else f"Video Translation {vt.id}"
        output_url = vt.output_url or (
            storage_service.get_url(vt.r2_key) if vt.r2_key else (
                f"/api/storage/files/translator/jobs/{vt.id}/final_dubbed_video.mp4" if vt.status == "completed" else None
            )
        )
        items.append({
            "id": vt.id,
            "job_id": vt.id,
            "title": title,
            "type": "video_translator",
            "workflow_mode": "video_translator",
            "workflow_status": vt.status,
            "status": vt.status,
            "stage": vt.stage,
            "progress": vt.overall_progress_pct or 0.0,
            "segment_count": vt.total_segments_count or 0,
            "output_video_url": output_url,
            "created_at": vt.created_at.isoformat() if vt.created_at else None,
            "updated_at": vt.updated_at.isoformat() if vt.updated_at else None,
        })

    # Sort all items by created_at descending
    items.sort(key=lambda x: x["created_at"] or "", reverse=True)
    total_count = len(items)

    if page is not None:
        start = (page - 1) * page_size
        end = start + page_size
        paginated_items = items[start:end]
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1
        return {
            "success": True,
            "data": paginated_items,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    return {"success": True, "data": items, "total": total_count}


async def _delete_single_item(item_id: str, session: AsyncSession) -> bool:
    from app.services.cleanup_service import FileCleanupService
    if item_id in _running_workflows:
        _running_workflows[item_id].cancel()

    res = await FileCleanupService.cleanup_project(item_id, session)
    return res.get("status") == "success"


@router.post("/batch-delete", response_model=dict)
async def batch_delete_projects(
    body: BatchDeleteRequest,
    session: AsyncSession = Depends(get_session),
):
    """Delete multiple projects (Standard or Video Translator)."""
    deleted = []
    failed = []

    for item_id in body.ids:
        try:
            ok = await _delete_single_item(item_id, session)
            if ok:
                deleted.append(item_id)
            else:
                failed.append(item_id)
        except Exception as e:
            logger.error("Failed to delete item", item_id=item_id, error=str(e))
            failed.append(item_id)

    return {"success": True, "data": {"deleted": deleted, "failed": failed}}


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Delete a single project or video translator job."""
    ok = await _delete_single_item(project_id, session)
    if not ok:
        raise HTTPException(status_code=404, detail="Project or job not found")
    return {"success": True, "data": {"deleted": project_id}}


@router.post("/{project_id}/estimate", response_model=dict)
async def estimate(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Estimate resource requirements for a project."""
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    seg_result = await session.execute(
        select(Segment)
        .where(Segment.project_id == project_id)
        .order_by(Segment.segment_number)
    )
    segments = seg_result.scalars().all()

    seg_data = [{"number": s.segment_number, "char_count": s.char_count} for s in segments]
    est = estimate_project(seg_data, project.workflow_mode)

    # Update project status
    project.workflow_status = WorkflowStatus.ESTIMATED.value
    project.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()

    return {
        "success": True,
        "data": EstimateResponse(
            project_id=project_id,
            total_segments=est.total_segments,
            total_characters=est.total_characters,
            estimated_audio_duration_seconds=est.estimated_audio_duration_seconds,
            estimated_video_clips=est.estimated_video_clips if project.workflow_mode == "audio_video" else None,
            estimated_video_seconds=est.estimated_video_seconds if project.workflow_mode == "audio_video" else None,
        ).model_dump(),
    }


@router.get("/{project_id}", response_model=dict)
async def get_project(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get single project metadata, settings, video list, and script segments."""
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if project:
        # Load standard project segments
        seg_result = await session.execute(
            select(Segment)
            .where(Segment.project_id == project_id)
            .order_by(Segment.segment_number)
        )
        segments = seg_result.scalars().all()
        segments_data = [
            {
                "id": s.id,
                "number": s.segment_number,
                "text_content": s.text_content or "",
                "text_preview": (s.text_content[:80] + "...") if s.text_content and len(s.text_content) > 80 else (s.text_content or ""),
                "char_count": s.char_count or 0,
                "audio_status": s.status or "pending",
                "video_status": s.video_status or "pending",
                "audio_duration": s.audio_duration,
                "video_error_message": s.error_message,
            }
            for s in segments
        ]

        # Fetch associated translation jobs / videos
        job_res = await session.execute(
            select(VideoTranslationJob)
            .options(selectinload(VideoTranslationJob.asset))
            .where(VideoTranslationJob.project_id == project_id)
            .order_by(VideoTranslationJob.created_at.desc())
        )
        jobs = job_res.scalars().all()
        videos_data = [
            {
                "id": j.id,
                "job_id": j.id,
                "title": (j.asset.title if j.asset and j.asset.title else f"Video {j.id}"),
                "status": j.status,
                "stage": j.stage,
                "overall_progress_pct": j.overall_progress_pct,
                "current_step": j.current_step,
                "output_url": j.output_url,
                "created_at": j.created_at.isoformat() if j.created_at else None,
                "updated_at": j.updated_at.isoformat() if j.updated_at else None,
            }
            for j in jobs
        ]

        # Fetch glossary summary stats
        gloss_count_res = await session.execute(
            select(func.count(ProjectGlossary.id)).where(ProjectGlossary.project_id == project_id)
        )
        glossary_count = gloss_count_res.scalar() or 0

        term_count_res = await session.execute(
            select(func.count(ProjectTerminologyMemory.id)).where(ProjectTerminologyMemory.project_id == project_id)
        )
        terminology_count = term_count_res.scalar() or 0

        normalized_settings = normalize_project_settings(project.settings_json or {})

        return {
            "success": True,
            "data": {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "workflow_mode": project.workflow_mode,
                "workflow_status": project.workflow_status,
                "audio_provider_id": project.audio_provider_id,
                "video_provider_id": project.video_provider_id,
                "voice_id": project.voice_id,
                "voice_name": project.voice_name,
                "settings": normalized_settings,
                "media_url": project.media_url,
                "segments": segments_data,
                "videos": videos_data,
                "glossary_count": glossary_count,
                "terminology_count": terminology_count,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            },
        }

    # Fallback: check VideoTranslationJob table
    vt_result = await session.execute(
        select(VideoTranslationJob)
        .options(selectinload(VideoTranslationJob.asset))
        .where(
            (VideoTranslationJob.id == project_id) | (VideoTranslationJob.project_id == project_id)
        )
    )
    job = vt_result.scalars().first()

    if job:
        # Load VideoTranslationSegments
        vt_seg_result = await session.execute(
            select(VideoTranslationSegment)
            .where(VideoTranslationSegment.job_id == job.id)
            .order_by(VideoTranslationSegment.segment_number)
        )
        vt_segments = vt_seg_result.scalars().all()
        segments_data = [
            {
                "id": str(s.id),
                "number": s.segment_number,
                "text_content": s.original_text or "",
                "text_preview": (s.original_text[:80] + "...") if s.original_text and len(s.original_text) > 80 else (s.original_text or ""),
                "char_count": len(s.original_text) if s.original_text else 0,
                "audio_status": s.tts_status or "pending",
                "video_status": s.tts_status or "pending",
                "audio_duration": s.audio_duration,
                "video_error_message": s.error_message,
            }
            for s in vt_segments
        ]

        title = job.asset.title if (job.asset and job.asset.title) else f"Video Translation {job.id}"
        
        # Load real Project settings if project exists
        real_p_id = job.project_id or job.id
        real_p_res = await session.execute(select(Project).where(Project.id == real_p_id))
        real_proj = real_p_res.scalar_one_or_none()
        if not real_proj:
            job_settings_dict = {
                "watermark_enabled": job.watermark_enabled,
                "watermark_type": job.watermark_type,
                "watermark_image_path": job.watermark_image_path,
                "watermark_text": job.watermark_text,
                "watermark_position": job.watermark_position,
                "watermark_scale": job.watermark_scale,
                "watermark_opacity": job.watermark_opacity,
                "watermark_margin": job.watermark_margin,
                "watermark_font_size": job.watermark_font_size,
                "target_language": job.target_language,
                "source_language": job.source_language,
                "audio_provider_id": job.audio_provider_id,
                "llm_provider_id": job.llm_provider_id,
                "voice_id": job.voice_id,
                "original_audio_mode": job.original_audio_mode,
            }
            real_proj = Project(
                id=real_p_id,
                title=title,
                workflow_mode="video_translator",
                workflow_status=job.status or "created",
                settings_json=normalize_project_settings(job_settings_dict),
            )
            session.add(real_proj)
            job.project_id = real_p_id
            await session.commit()

        normalized_settings = normalize_project_settings(real_proj.settings_json or {})

        return {
            "success": True,
            "data": {
                "id": job.id,
                "title": title,
                "description": f"Video Translation Pipeline Job ({job.id})",
                "workflow_mode": "video_translator",
                "workflow_status": job.status,
                "audio_provider_id": job.audio_provider_id,
                "video_provider_id": None,
                "voice_id": job.voice_id,
                "voice_name": None,
                "settings": normalized_settings,
                "media_url": job.output_url,
                "segments": segments_data,
                "videos": [],
                "glossary_count": 0,
                "terminology_count": 0,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "updated_at": job.updated_at.isoformat() if job.updated_at else None,
            },
        }

    raise HTTPException(status_code=404, detail="Project not found")


@router.get("/{project_id}/settings", response_model=dict)
async def get_project_settings(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get project configuration settings with normalization and defaults."""
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    # Fallback search in VideoTranslationJob
    if not project:
        job_res = await session.execute(
            select(VideoTranslationJob).where(
                (VideoTranslationJob.id == project_id) | (VideoTranslationJob.project_id == project_id)
            )
        )
        job = job_res.scalar_one_or_none()
        if job:
            real_p_id = job.project_id or job.id
            p_res = await session.execute(select(Project).where(Project.id == real_p_id))
            project = p_res.scalar_one_or_none()
            if not project:
                # Return job hydrated settings if project model does not exist yet
                job_settings = {
                    "watermark_enabled": job.watermark_enabled,
                    "watermark_type": job.watermark_type,
                    "watermark_image_path": job.watermark_image_path,
                    "watermark_text": job.watermark_text,
                    "watermark_position": job.watermark_position,
                    "watermark_scale": job.watermark_scale,
                    "watermark_opacity": job.watermark_opacity,
                    "watermark_margin": job.watermark_margin,
                    "watermark_font_size": job.watermark_font_size,
                    "target_language": job.target_language,
                    "source_language": job.source_language,
                    "audio_provider_id": job.audio_provider_id,
                    "llm_provider_id": job.llm_provider_id,
                    "voice_id": job.voice_id,
                    "original_audio_mode": job.original_audio_mode,
                }
                settings_dict = normalize_project_settings(job_settings)
                return {
                    "success": True,
                    "project_id": project_id,
                    "data": settings_dict,
                    "settings": settings_dict,
                    "updated_at": job.updated_at.isoformat() if job.updated_at else None,
                }

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    settings_dict = normalize_project_settings(project.settings_json or {})
    print(f"[PROJECT SETTINGS LOAD] Project ID: {project_id} | Settings Source: DATABASE | Watermark Enabled: {settings_dict.get('watermark_enabled')} | Type: {settings_dict.get('watermark_type')} | Position: {settings_dict.get('watermark_position')} | Scale: {settings_dict.get('watermark_scale')} | Opacity: {settings_dict.get('watermark_opacity')} | Margin: {settings_dict.get('watermark_margin')}")

    return {
        "success": True,
        "project_id": project_id,
        "data": settings_dict,
        "settings": settings_dict,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
    }


@router.post("/{project_id}/settings", response_model=dict)
@router.put("/{project_id}/settings", response_model=dict)
async def save_project_settings(
    project_id: str,
    body: dict,
    session: AsyncSession = Depends(get_session),
):
    """Save/update project configuration settings."""
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    # Fallback to job search & auto-create project record if missing
    job_ref = None
    if not project:
        job_res = await session.execute(
            select(VideoTranslationJob).where(
                (VideoTranslationJob.id == project_id) | (VideoTranslationJob.project_id == project_id)
            )
        )
        job_ref = job_res.scalar_one_or_none()
        if job_ref:
            real_p_id = job_ref.project_id or job_ref.id
            p_res = await session.execute(select(Project).where(Project.id == real_p_id))
            project = p_res.scalar_one_or_none()
            if not project:
                project = Project(
                    id=real_p_id,
                    title=f"Project {real_p_id}",
                    workflow_mode="video_translator",
                    workflow_status=job_ref.status or "created",
                    settings_json={},
                )
                session.add(project)
                await session.flush()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    raw_incoming = body.get("settings", body) if isinstance(body, dict) else {}
    current_settings = copy.deepcopy(project.settings_json or {})
    current_settings.update(raw_incoming)

    normalized = normalize_project_settings(current_settings)
    project.settings_json = copy.deepcopy(normalized)
    flag_modified(project, "settings_json")

    if "audio_provider_id" in normalized:
        project.audio_provider_id = normalized["audio_provider_id"]
    if "video_provider_id" in normalized:
        project.video_provider_id = normalized["video_provider_id"]
    if "voice_id" in normalized:
        project.voice_id = normalized["voice_id"]
    if "voice_name" in normalized:
        project.voice_name = normalized["voice_name"]

    # Sync linked VideoTranslationJob watermark fields if present
    jobs_sync_res = await session.execute(
        select(VideoTranslationJob).where(
            (VideoTranslationJob.id == project.id) | (VideoTranslationJob.project_id == project.id)
        )
    )
    for j in jobs_sync_res.scalars().all():
        j.project_id = project.id
        j.watermark_enabled = normalized.get("watermark_enabled", False)
        j.watermark_type = normalized.get("watermark_type", "image")
        if normalized.get("watermark_image_path"):
            j.watermark_image_path = normalized.get("watermark_image_path")
        if normalized.get("watermark_text"):
            j.watermark_text = normalized.get("watermark_text")
        j.watermark_position = normalized.get("watermark_position", "bottom_right")
        j.watermark_scale = normalized.get("watermark_scale", 0.20)
        j.watermark_opacity = normalized.get("watermark_opacity", 0.80)
        j.watermark_margin = normalized.get("watermark_margin", 20)
        j.watermark_font_size = normalized.get("watermark_font_size", 32)

    project.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()

    print(f"[PROJECT SETTINGS SAVE] Project ID: {project.id} | Changed Fields: {list(raw_incoming.keys())} | Database Commit: SUCCESS | Watermark Enabled: {normalized.get('watermark_enabled')}")

    return {
        "success": True,
        "project_id": project.id,
        "data": normalized,
        "settings": normalized,
        "updated_at": project.updated_at.isoformat(),
    }


@router.post("/{project_id}/configure", response_model=dict)
async def configure_project(
    project_id: str,
    body: dict,
    session: AsyncSession = Depends(get_session),
):
    """Configure project providers and voice."""
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if "audio_provider_id" in body:
        project.audio_provider_id = body["audio_provider_id"]
    if "video_provider_id" in body:
        project.video_provider_id = body["video_provider_id"]
    if "voice_id" in body:
        project.voice_id = body["voice_id"]
    if "voice_name" in body:
        project.voice_name = body["voice_name"]
    if "sync_strategy" in body:
        project.sync_strategy = body["sync_strategy"]

    project.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()

    return {"success": True, "data": {"configured": True}}


@router.post("/{project_id}/precheck", response_model=dict)
async def precheck(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Run preflight checks before generation."""
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    seg_count = await session.execute(
        select(func.count(Segment.id)).where(Segment.project_id == project_id)
    )
    total_segments = seg_count.scalar() or 0

    preflight_result = await run_preflight(
        project_id=project_id,
        workflow_mode=project.workflow_mode,
        audio_provider_id=project.audio_provider_id,
        video_provider_id=project.video_provider_id,
        voice_id=project.voice_id,
        total_segments=total_segments,
    )

    if preflight_result.passed:
        project.workflow_status = WorkflowStatus.PRECHECKED.value
        project.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await session.commit()

    return {
        "success": True,
        "data": preflight_result.model_dump(),
    }


@router.post("/{project_id}/run", response_model=dict)
async def run_workflow(
    project_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Start the generation workflow."""
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.workflow_status != WorkflowStatus.PRECHECKED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start workflow from state '{project.workflow_status}'. Run precheck first.",
        )

    async def run_and_cleanup():
        async with async_session_factory() as bg_session:
            orchestrator = WorkflowOrchestrator(bg_session, project_id)
            _running_workflows[project_id] = orchestrator
            try:
                await orchestrator.run()
            finally:
                _running_workflows.pop(project_id, None)

    background_tasks.add_task(run_and_cleanup)

    return {"success": True, "data": {"started": True, "project_id": project_id}}


@router.post("/{project_id}/resume", response_model=dict)
async def resume_workflow(
    project_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Resume a failed/interrupted workflow."""
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not is_resumable_state(project.workflow_status):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot resume from state '{project.workflow_status}'",
        )

    # Transition back to PRECHECKED for re-validation
    project.workflow_status = WorkflowStatus.PRECHECKED.value
    project.error_message = None
    project.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()

    async def run_and_cleanup():
        async with async_session_factory() as bg_session:
            orchestrator = WorkflowOrchestrator(bg_session, project_id)
            _running_workflows[project_id] = orchestrator
            try:
                await orchestrator.run()
            finally:
                _running_workflows.pop(project_id, None)

    background_tasks.add_task(run_and_cleanup)

    return {"success": True, "data": {"resumed": True, "project_id": project_id}}


@router.post("/{project_id}/cancel", response_model=dict)
async def cancel_workflow(project_id: str):
    """Cancel a running workflow. Completed assets are preserved."""
    orchestrator = _running_workflows.get(project_id)
    if not orchestrator:
        raise HTTPException(status_code=400, detail="No running workflow for this project")

    orchestrator.cancel()
    return {"success": True, "data": {"cancelling": True, "project_id": project_id}}


@router.get("/{project_id}/status", response_model=dict)
async def get_status(
    project_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get current workflow status."""
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    seg_result = await session.execute(
        select(Segment).where(Segment.project_id == project_id)
    )
    segments = seg_result.scalars().all()

    audio_done = sum(1 for s in segments if s.audio_status == SegmentStatus.COMPLETED.value)
    video_done = sum(1 for s in segments if s.video_status == SegmentStatus.COMPLETED.value)
    total = len(segments)

    return {
        "success": True,
        "data": ProjectStatusResponse(
            project_id=project_id,
            workflow_status=project.workflow_status,
            total_segments=total,
            audio_completed=audio_done,
            video_completed=video_done,
            audio_progress_pct=round(audio_done / total * 100, 1) if total > 0 else 0,
            video_progress_pct=round(video_done / total * 100, 1) if total > 0 else 0,
            error_message=project.error_message,
        ).model_dump(),
    }
