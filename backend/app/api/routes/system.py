"""
System API routes — health checks, interrupted project detection, cleanup.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.media.ffprobe import is_ffmpeg_installed, get_ffmpeg_version
from app.models.project import Project
from app.workflow.state_machine import is_running_state
from app.core import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/health", response_model=dict)
async def health_check():
    """System health check."""
    ffmpeg_ok = is_ffmpeg_installed()
    ffmpeg_version = get_ffmpeg_version() if ffmpeg_ok else None

    return {
        "success": True,
        "data": {
            "status": "healthy" if ffmpeg_ok else "degraded",
            "ffmpeg_installed": ffmpeg_ok,
            "ffmpeg_version": ffmpeg_version,
        },
    }


@router.get("/interrupted", response_model=dict)
async def list_interrupted(session: AsyncSession = Depends(get_session)):
    """Detect projects that were interrupted (app crashed during workflow)."""
    result = await session.execute(select(Project))
    projects = result.scalars().all()

    interrupted = []
    for p in projects:
        if is_running_state(p.workflow_status):
            # This project was running when the app stopped
            p.workflow_status = "interrupted"
            interrupted.append({
                "id": p.id,
                "title": p.title,
                "status": "interrupted",
                "workflow_mode": p.workflow_mode,
            })

    if interrupted:
        await session.commit()

    return {"success": True, "data": interrupted}
