"""
Startup Reconciliation Service.

Scans the database upon application startup and resolves any zombie / orphan
jobs or projects left in RUNNING/PROCESSING states due to server restarts or crashes.
"""

from __future__ import annotations

from sqlalchemy import select
from app.core import get_logger
from app.database import async_session_factory
from app.models.project import Project, WorkflowStatus
from app.models.video_translator import VideoTranslationJob, TranslationJobStatus
from app.models.video_merger import VideoMergeJob, MergeJobStatus
from app.models.job import Job, JobStatus

logger = get_logger(__name__)


async def reconcile_zombie_jobs() -> dict[str, int]:
    """Reconcile zombie jobs and projects on server startup."""
    reconciled = {
        "projects": 0,
        "translation_jobs": 0,
        "merge_jobs": 0,
        "segment_jobs": 0,
    }

    async with async_session_factory() as session:
        try:
            # 1. Projects in active running states
            running_project_statuses = [
                WorkflowStatus.GENERATING_AUDIO.value,
                WorkflowStatus.GENERATING_VIDEO.value,
                WorkflowStatus.SYNCING.value,
                WorkflowStatus.MERGING.value,
            ]
            stmt = select(Project).where(Project.workflow_status.in_(running_project_statuses))
            res = await session.execute(stmt)
            projects = res.scalars().all()
            for p in projects:
                p.workflow_status = WorkflowStatus.INTERRUPTED.value
                reconciled["projects"] += 1
                logger.info(f"Reconciled zombie project {p.id} to INTERRUPTED")

            # 2. VideoTranslationJob in active processing states
            active_translation_statuses = [
                TranslationJobStatus.CHECKING.value,
                TranslationJobStatus.DOWNLOADING.value,
                TranslationJobStatus.EXTRACTING_AUDIO.value,
                TranslationJobStatus.STT.value,
                TranslationJobStatus.GENERATING_TTS.value,
                TranslationJobStatus.SYNCING_AUDIO.value,
                TranslationJobStatus.RENDERING.value,
            ]
            stmt = select(VideoTranslationJob).where(VideoTranslationJob.status.in_(active_translation_statuses))
            res = await session.execute(stmt)
            t_jobs = res.scalars().all()
            for tj in t_jobs:
                tj.status = TranslationJobStatus.FAILED.value
                tj.error_message = "Tiến trình bị gián đoạn do máy chủ khởi động lại."
                reconciled["translation_jobs"] += 1
                logger.info(f"Reconciled zombie translation job {tj.id} to FAILED")

            # 3. VideoMergeJob in transient states
            active_merge_statuses = [
                MergeJobStatus.PREPARING.value,
                MergeJobStatus.PROCESSING.value,
            ]
            stmt = select(VideoMergeJob).where(VideoMergeJob.status.in_(active_merge_statuses))
            res = await session.execute(stmt)
            m_jobs = res.scalars().all()
            for mj in m_jobs:
                mj.status = MergeJobStatus.FAILED.value
                mj.error_message = "Tiến trình ghép video bị gián đoạn do máy chủ khởi động lại."
                reconciled["merge_jobs"] += 1
                logger.info(f"Reconciled zombie merge job {mj.id} to FAILED")

            # 4. Individual generation tasks (Job model)
            stmt = select(Job).where(Job.status == JobStatus.RUNNING.value)
            res = await session.execute(stmt)
            jobs = res.scalars().all()
            for j in jobs:
                j.status = JobStatus.FAILED.value
                j.error_message = "Interrupted by server restart"
                reconciled["segment_jobs"] += 1

            await session.commit()
            if any(reconciled.values()):
                logger.info("Startup reconciliation finished", **reconciled)
        except Exception as e:
            logger.error("Error during startup reconciliation", error=str(e))
            await session.rollback()

    return reconciled
