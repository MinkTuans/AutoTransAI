"""
Project API routes.

All project operations go through these endpoints.
The UI never calls providers directly.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sse_starlette.sse import EventSourceResponse

from app.database import get_session, async_session_factory
from app.models.project import Project, WorkflowStatus
from app.models.segment import Segment, SegmentStatus
from app.models.video_translator import VideoTranslationJob, VideoAsset, VideoTranslationSegment
from app.services.storage_service import storage_service
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectListResponse,
    ProjectStatusResponse,
    SegmentSummary,
)
from app.schemas.estimate import EstimateResponse, ResourceEstimate
from app.schemas.workflow import PreflightResult
from app.services.script_parser import parse_script, validate_segments
from app.services.estimator import estimate_project
from app.services.preflight import run_preflight
from app.services.file_manager import (
    ensure_project_structure,
    delete_project_files,
    clean_temp_files,
)
from app.services.manifest import create_manifest
from app.usage.quota_manager import validate_quota
from app.providers.registry import get_registry
from app.workflow.orchestrator import WorkflowOrchestrator
from app.workflow.state_machine import is_resumable_state, validate_transition
from app.core import get_logger
from app.config import get_settings

settings = get_settings()

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
    """Create a new project and parse the script."""
    project_id = str(uuid.uuid4())[:8]

    # Parse script
    segments = parse_script(body.script)
    warnings = validate_segments(segments)

    # Create project
    project = Project(
        id=project_id,
        title=body.title,
        script_raw=body.script,
        workflow_mode=body.workflow_mode,
        workflow_status=WorkflowStatus.PARSED.value,
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
        "workflow_status": WorkflowStatus.PARSED.value,
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
            "segment_count": len(segments),
            "total_characters": sum(s.char_count for s in segments),
            "warnings": warnings,
        },
    }


@router.get("", response_model=dict)
async def list_projects(session: AsyncSession = Depends(get_session)):
    """List all projects (both Standard Projects and Video Translator Jobs)."""
    # 1. Fetch standard projects
    std_result = await session.execute(
        select(Project).order_by(Project.created_at.desc())
    )
    std_projects = std_result.scalars().all()

    items = []
    for p in std_projects:
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
    return {"success": True, "data": items}


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
    project.updated_at = datetime.now(timezone.utc)
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

    project.updated_at = datetime.now(timezone.utc)
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
        project.updated_at = datetime.now(timezone.utc)
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
    project.updated_at = datetime.now(timezone.utc)
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
