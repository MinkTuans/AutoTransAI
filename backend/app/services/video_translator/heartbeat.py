"""
Heartbeat & Stalled Process Detection Engine.

Manages active background job heartbeats and detects stalled or killed processes.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Optional

from sqlalchemy import select, update

from app.config import get_settings
from app.core import get_logger
from app.core.job_logger import log_job_event
from app.database import async_session_factory
from app.models.video_translator import VideoTranslationJob, TranslationJobStatus

logger = get_logger(__name__)
settings = get_settings()

_active_heartbeats: Dict[str, asyncio.Task] = {}


async def _heartbeat_loop(job_id: str):
    """Periodic task updating last_heartbeat in DB every 2.5 seconds."""
    log_job_event(job_id, "HEARTBEAT", "Heartbeat loop initialized.")
    while True:
        try:
            await asyncio.sleep(2.5)
            async with async_session_factory() as session:
                await session.execute(
                    update(VideoTranslationJob)
                    .where(VideoTranslationJob.id == job_id)
                    .values(
                        last_heartbeat=datetime.now(timezone.utc).replace(tzinfo=None),
                        updated_at=datetime.now(timezone.utc).replace(tzinfo=None),
                    )
                )
                await session.commit()
        except asyncio.CancelledError:
            log_job_event(job_id, "HEARTBEAT", "Heartbeat loop stopped.")
            break
        except Exception as e:
            logger.warning("Heartbeat update error", job_id=job_id, error=str(e))
            await asyncio.sleep(1.0)


def start_job_heartbeat(job_id: str) -> None:
    """Start background heartbeat loop for a job."""
    stop_job_heartbeat(job_id)
    task = asyncio.create_task(_heartbeat_loop(job_id))
    _active_heartbeats[job_id] = task


def stop_job_heartbeat(job_id: str) -> None:
    """Stop background heartbeat loop for a job."""
    if job_id in _active_heartbeats:
        task = _active_heartbeats.pop(job_id)
        if not task.done():
            task.cancel()


async def check_and_mark_stalled_jobs(stalled_threshold_seconds: int = 60) -> list[str]:
    """
    Scan DB for active jobs whose last_heartbeat is older than threshold.
    If process PID is dead or non-responsive, transition job to STALLED.
    """
    stalled_job_ids = []
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    async with async_session_factory() as session:
        res = await session.execute(
            select(VideoTranslationJob).where(
                VideoTranslationJob.status.in_([
                    TranslationJobStatus.EXTRACTING_AUDIO.value,
                    TranslationJobStatus.STT.value,
                    TranslationJobStatus.TRANSLATED.value,
                    TranslationJobStatus.GENERATING_TTS.value,
                    TranslationJobStatus.SYNCING_AUDIO.value,
                    TranslationJobStatus.RENDERING.value,
                ])
            )
        )
        running_jobs = res.scalars().all()

        for job in running_jobs:
            if not job.last_heartbeat:
                continue

            elapsed = (now - job.last_heartbeat).total_seconds()
            if elapsed > stalled_threshold_seconds:
                # Check if process is running
                process_alive = False
                if job.pid:
                    try:
                        import os
                        os.kill(job.pid, 0)
                        process_alive = True
                    except OSError:
                        process_alive = False

                if not process_alive:
                    job.status = TranslationJobStatus.FAILED.value
                    job.current_step = f"🔴 STALLED: Không nhận được heartbeat trong {int(elapsed)}s."
                    job.error_message = f"Process (PID {job.pid or 'N/A'}) đã bị ngắt hoặc ngừng phản hồi."
                    stalled_job_ids.append(job.id)
                    log_job_event(job.id, "STALLED", f"Process non-responsive for {int(elapsed)}s. Marked as STALLED.")

        if stalled_job_ids:
            await session.commit()

    return stalled_job_ids
