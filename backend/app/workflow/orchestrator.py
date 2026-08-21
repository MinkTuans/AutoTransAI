"""
Workflow orchestrator — the central controller for the generation pipeline.

The UI never calls providers directly. It calls the orchestrator which:
1. Manages state transitions
2. Runs preflight checks
3. Coordinates audio/video generation
4. Handles sync and merge
5. Manages idempotency (skips completed segments)
6. Updates manifest after each step
7. Supports cancellation
8. Supports resume after failure
"""

import asyncio
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core import get_logger
from app.core.exceptions import PreflightError, WorkflowError
from app.core.retry import RetryConfig, retry_async
from app.media.ffprobe import probe_duration, probe_duration_async
from app.media.ffmpeg import merge_audio_video, concatenate_videos, merge_audio_video_async, concatenate_videos_async
from app.media.strategies import SyncStrategy, plan_sync, execute_sync, execute_sync_async
from app.models.project import Project, WorkflowMode, WorkflowStatus
from app.models.segment import Segment, SegmentStatus
from app.models.job import Job, JobType, JobStatus
from app.models.error import Error
from app.providers.base import AudioProvider, VideoProvider
from app.providers.registry import get_registry
from app.services.file_manager import (
    ensure_project_structure,
    ensure_segment_dirs,
    get_segment_audio_path,
    get_segment_video_path,
    get_segment_merged_path,
    get_final_output_path,
    get_project_dir,
)
from app.services.manifest import update_manifest, update_segment_in_manifest
from app.workflow.state_machine import validate_transition, is_resumable_state

logger = get_logger(__name__)
settings = get_settings()


class WorkflowOrchestrator:
    """
    Central workflow controller.

    Each instance manages one project's generation lifecycle.
    """

    def __init__(self, session: AsyncSession, project_id: str):
        self.session = session
        self.project_id = project_id
        self._cancelled = False
        self._registry = get_registry()
        self._retry_config = RetryConfig(
            max_retries=settings.MAX_RETRIES,
            initial_delay=settings.RETRY_INITIAL_DELAY,
            max_delay=settings.RETRY_MAX_DELAY,
            backoff_factor=settings.RETRY_BACKOFF_FACTOR,
            jitter=settings.RETRY_JITTER,
        )
        # Progress callback for SSE
        self._progress_callback: asyncio.Queue | None = None

    def set_progress_queue(self, queue: asyncio.Queue) -> None:
        """Set a queue for sending progress updates (used by SSE)."""
        self._progress_callback = queue

    async def _emit_progress(self, event: dict) -> None:
        """Send a progress event to the SSE queue."""
        if self._progress_callback:
            await self._progress_callback.put(event)

    def cancel(self) -> None:
        """Signal the workflow to cancel. Currently running jobs finish safely."""
        self._cancelled = True
        logger.info("Workflow cancellation requested", project_id=self.project_id)

    async def _get_project(self) -> Project:
        """Fetch the project from the database."""
        result = await self.session.execute(
            select(Project).where(Project.id == self.project_id)
        )
        project = result.scalar_one_or_none()
        if not project:
            raise WorkflowError(f"Project {self.project_id} not found", code="PROJECT_NOT_FOUND")
        return project

    async def _update_status(self, new_status: str) -> None:
        """Update project workflow status with state machine validation."""
        project = await self._get_project()
        validate_transition(project.workflow_status, new_status)

        await self.session.execute(
            update(Project)
            .where(Project.id == self.project_id)
            .values(
                workflow_status=new_status,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.commit()

        update_manifest(self.project_id, {"workflow_status": new_status})
        await self._emit_progress({
            "type": "status_change",
            "status": new_status,
            "project_id": self.project_id,
        })

        logger.info("Status updated", project_id=self.project_id, status=new_status)

    async def _get_segments(self) -> list[Segment]:
        """Get all segments for the project, ordered by number."""
        result = await self.session.execute(
            select(Segment)
            .where(Segment.project_id == self.project_id)
            .order_by(Segment.segment_number)
        )
        return list(result.scalars().all())

    async def run(self) -> None:
        """
        Execute the full workflow pipeline.

        Follows: PRECHECKED → AUDIO → VIDEO → SYNC → MERGE → COMPLETED
        Skips completed segments (idempotency).
        Stops on cancellation.
        """
        try:
            project = await self._get_project()
            ensure_project_structure(self.project_id)

            # Start audio generation
            await self._update_status(WorkflowStatus.GENERATING_AUDIO.value)
            await self._generate_all_audio()

            if self._cancelled:
                await self._update_status(WorkflowStatus.CANCELLED.value)
                return

            await self._update_status(WorkflowStatus.AUDIO_COMPLETED.value)

            # Check if audio-only mode
            project = await self._get_project()
            if project.workflow_mode == WorkflowMode.AUDIO_ONLY.value:
                await self._update_status(WorkflowStatus.COMPLETED.value)
                await self._emit_progress({
                    "type": "completed",
                    "project_id": self.project_id,
                    "mode": "audio_only",
                })
                return

            # Video generation
            await self._update_status(WorkflowStatus.GENERATING_VIDEO.value)
            await self._generate_all_video()

            if self._cancelled:
                await self._update_status(WorkflowStatus.CANCELLED.value)
                return

            await self._update_status(WorkflowStatus.VIDEO_COMPLETED.value)

            # Sync + Merge
            await self._update_status(WorkflowStatus.SYNCING.value)
            await self._sync_all_segments()
            await self._update_status(WorkflowStatus.MERGING.value)
            await self._merge_final()
            await self._update_status(WorkflowStatus.COMPLETED.value)

            await self._emit_progress({
                "type": "completed",
                "project_id": self.project_id,
                "mode": "audio_video",
            })

        except WorkflowError as e:
            logger.error(
                "Workflow failed",
                project_id=self.project_id,
                error_code=e.code,
                error=e.message,
            )
            project = await self._get_project()
            await self.session.execute(
                update(Project)
                .where(Project.id == self.project_id)
                .values(
                    workflow_status=WorkflowStatus.FAILED.value,
                    error_message=e.message,
                    updated_at=datetime.now(timezone.utc),
                )
            )
            # Create Error record in DB
            try:
                db_error = Error(
                    job_id=None,
                    error_type=e.code,
                    message=e.message,
                )
                self.session.add(db_error)
                await self.session.commit()
            except Exception as err_ex:
                logger.warning("Failed to insert Error record", error=str(err_ex))

            update_manifest(self.project_id, {
                "workflow_status": WorkflowStatus.FAILED.value,
                "error": e.message,
            })
            await self._emit_progress({
                "type": "error",
                "project_id": self.project_id,
                "error_code": e.code,
                "error_message": e.message,
            })
        except Exception as e:
            logger.exception("Unexpected workflow error", project_id=self.project_id)
            await self.session.execute(
                update(Project)
                .where(Project.id == self.project_id)
                .values(
                    workflow_status=WorkflowStatus.FAILED.value,
                    error_message=str(e),
                    updated_at=datetime.now(timezone.utc),
                )
            )
            try:
                db_error = Error(
                    job_id=None,
                    error_type=type(e).__name__,
                    message=str(e),
                )
                self.session.add(db_error)
                await self.session.commit()
            except Exception as err_ex:
                logger.warning("Failed to insert Error record", error=str(err_ex))

            update_manifest(self.project_id, {
                "workflow_status": WorkflowStatus.FAILED.value,
                "error": str(e),
            })


    async def _generate_all_audio(self) -> None:
        """Generate audio for all pending segments."""
        project = await self._get_project()
        provider = self._registry.get_audio(project.audio_provider_id)
        if not provider:
            raise WorkflowError(
                f"Audio provider '{project.audio_provider_id}' not found",
                code="PROVIDER_NOT_FOUND",
            )

        segments = await self._get_segments()
        for seg in segments:
            if self._cancelled:
                return
            await self._generate_segment_audio(seg, provider, project.voice_id or "")

        # Check for any failures
        segments = await self._get_segments()
        failed = [s for s in segments if s.audio_status == SegmentStatus.FAILED.value]
        if failed:
            raise WorkflowError(
                f"{len(failed)} segment(s) failed audio generation",
                code="AUDIO_GENERATION_FAILED",
                details={"failed_segments": [s.segment_number for s in failed]},
            )

    async def _generate_segment_audio(
        self, segment: Segment, provider: AudioProvider, voice_id: str
    ) -> None:
        """Generate audio for a single segment with idempotency and retry."""
        # IDEMPOTENCY: Skip completed segments
        if segment.audio_status == SegmentStatus.COMPLETED.value:
            audio_path = get_segment_audio_path(self.project_id, segment.segment_number)
            if audio_path.exists():
                logger.info(
                    "Skipping completed audio segment",
                    segment=segment.segment_number,
                )
                return

        # Mark in progress
        segment.audio_status = SegmentStatus.IN_PROGRESS.value
        await self.session.commit()

        output_path = get_segment_audio_path(self.project_id, segment.segment_number)
        ensure_segment_dirs(self.project_id, segment.segment_number)

        await self._emit_progress({
            "type": "segment_audio_start",
            "segment": segment.segment_number,
            "project_id": self.project_id,
        })

        try:
            # Retry-wrapped generation
            result = await retry_async(
                provider.generate_audio,
                segment.text_content,
                voice_id,
                output_path,
                config=self._retry_config,
                context={
                    "provider_id": provider.provider_id,
                    "segment": segment.segment_number,
                    "project_id": self.project_id,
                },
            )

            if result.success and result.file_path and result.file_path.exists():
                # Measure actual duration with FFprobe
                duration = await probe_duration_async(result.file_path)
                segment.audio_status = SegmentStatus.COMPLETED.value
                segment.audio_duration = duration
                segment.audio_file_path = str(result.file_path)
                await self.session.commit()

                update_segment_in_manifest(self.project_id, segment.segment_number, {
                    "audio_status": "completed",
                    "audio_duration": duration,
                    "audio_file": str(result.file_path),
                })

                await self._emit_progress({
                    "type": "segment_audio_complete",
                    "segment": segment.segment_number,
                    "duration": duration,
                    "project_id": self.project_id,
                })

                logger.info(
                    "Segment audio completed",
                    segment=segment.segment_number,
                    duration=duration,
                )
            else:
                segment.audio_status = SegmentStatus.FAILED.value
                await self.session.commit()
                err_msg = result.error_message or "Audio generation returned failure"
                logger.error("Audio generation failed", segment=segment.segment_number, error=err_msg)
                raise WorkflowError(err_msg, code="AUDIO_GENERATION_FAILED")

        except Exception as e:
            segment.audio_status = SegmentStatus.FAILED.value
            await self.session.commit()
            logger.error(
                "Segment audio failed",
                segment=segment.segment_number,
                error=str(e),
            )

    async def _generate_all_video(self) -> None:
        """Generate video for all pending segments."""
        project = await self._get_project()
        provider = self._registry.get_video(project.video_provider_id)
        if not provider:
            raise WorkflowError(
                f"Video provider '{project.video_provider_id}' not found",
                code="PROVIDER_NOT_FOUND",
            )

        segments = await self._get_segments()
        for seg in segments:
            if self._cancelled:
                return
            await self._generate_segment_video(seg, provider)

        segments = await self._get_segments()
        failed = [s for s in segments if s.video_status == SegmentStatus.FAILED.value]
        if failed:
            raise WorkflowError(
                f"{len(failed)} segment(s) failed video generation",
                code="VIDEO_GENERATION_FAILED",
                details={"failed_segments": [s.segment_number for s in failed]},
            )

    async def _generate_segment_video(
        self, segment: Segment, provider: VideoProvider
    ) -> None:
        """Generate video for a single segment with idempotency and retry."""
        # IDEMPOTENCY: Skip completed segments
        if segment.video_status == SegmentStatus.COMPLETED.value:
            video_path = get_segment_video_path(self.project_id, segment.segment_number)
            if video_path.exists():
                logger.info(
                    "Skipping completed video segment",
                    segment=segment.segment_number,
                )
                return

        segment.video_status = SegmentStatus.IN_PROGRESS.value
        await self.session.commit()

        output_path = get_segment_video_path(self.project_id, segment.segment_number)
        ensure_segment_dirs(self.project_id, segment.segment_number)

        await self._emit_progress({
            "type": "segment_video_start",
            "segment": segment.segment_number,
            "project_id": self.project_id,
        })

        try:
            result = await retry_async(
                provider.generate_video,
                segment.text_content,
                settings.VIDEO_TARGET_DURATION,
                output_path,
                config=self._retry_config,
                context={
                    "provider_id": provider.provider_id,
                    "segment": segment.segment_number,
                    "project_id": self.project_id,
                },
            )

            if result.success and result.file_path and result.file_path.exists():
                duration = await probe_duration_async(result.file_path)
                segment.video_status = SegmentStatus.COMPLETED.value
                segment.video_duration = duration
                segment.video_file_path = str(result.file_path)
                segment.video_error_message = None
                await self.session.commit()

                update_segment_in_manifest(self.project_id, segment.segment_number, {
                    "video_status": "completed",
                    "video_duration": duration,
                    "video_file": str(result.file_path),
                    "video_error": None,
                })

                await self._emit_progress({
                    "type": "segment_video_complete",
                    "segment": segment.segment_number,
                    "duration": duration,
                    "project_id": self.project_id,
                })
            else:
                err_msg = result.error_message or "Video generation returned failure"
                segment.video_status = SegmentStatus.FAILED.value
                segment.video_error_message = err_msg
                await self.session.commit()

                update_segment_in_manifest(self.project_id, segment.segment_number, {
                    "video_status": "failed",
                    "video_error": err_msg,
                })

                logger.error("Video generation failed", segment=segment.segment_number, error=err_msg)
                raise WorkflowError(err_msg, code="VIDEO_GENERATION_FAILED")

        except Exception as e:
            err_msg = str(e)
            segment.video_status = SegmentStatus.FAILED.value
            segment.video_error_message = err_msg
            await self.session.commit()

            update_segment_in_manifest(self.project_id, segment.segment_number, {
                "video_status": "failed",
                "video_error": err_msg,
            })

            logger.error(
                "Segment video failed",
                segment=segment.segment_number,
                error=err_msg,
            )

    async def _sync_all_segments(self) -> None:
        """Sync audio and video durations for all segments."""
        project = await self._get_project()
        segments = await self._get_segments()

        for segment in segments:
            if self._cancelled:
                return

            if not segment.audio_duration or not segment.video_duration:
                continue

            sync_plan = plan_sync(
                segment.segment_number,
                segment.audio_duration,
                segment.video_duration,
                default_strategy=project.sync_strategy,
                tolerance=settings.SYNC_TOLERANCE_SECONDS,
            )

            video_path = Path(segment.video_file_path) if segment.video_file_path else None
            if not video_path or not video_path.exists():
                continue

            if sync_plan.strategy != SyncStrategy.NONE:
                tmp_dir = get_project_dir(self.project_id) / "tmp"
                synced_path = tmp_dir / f"segment_{segment.segment_number:03d}_synced.mp4"
                await execute_sync_async(sync_plan, video_path, synced_path)
                # Update the video path to the synced version
                segment.video_file_path = str(synced_path)

            segment.target_duration = sync_plan.target_duration
            segment.sync_strategy_used = sync_plan.strategy.value
            await self.session.commit()

            update_segment_in_manifest(self.project_id, segment.segment_number, {
                "sync_strategy": sync_plan.strategy.value,
                "target_duration": sync_plan.target_duration,
            })

    async def _merge_final(self) -> None:
        """Merge all segments into the final output video."""
        segments = await self._get_segments()
        merged_paths: list[Path] = []
        tmp_dir = get_project_dir(self.project_id) / "tmp"

        for segment in segments:
            if not segment.audio_file_path or not segment.video_file_path:
                continue

            audio_path = Path(segment.audio_file_path)
            video_path = Path(segment.video_file_path)

            if not audio_path.exists() or not video_path.exists():
                continue

            merged_path = get_segment_merged_path(self.project_id, segment.segment_number)
            await merge_audio_video_async(audio_path, video_path, merged_path)
            merged_paths.append(merged_path)

            segment.merged_file_path = str(merged_path)
            await self.session.commit()

            update_segment_in_manifest(self.project_id, segment.segment_number, {
                "merged_file": str(merged_path),
            })

        if not merged_paths:
            raise WorkflowError("No merged segments to concatenate", code="NO_SEGMENTS")

        # Concatenate all merged segments
        final_path = get_final_output_path(self.project_id)
        await concatenate_videos_async(merged_paths, final_path, tmp_dir)

        final_duration = await probe_duration_async(final_path)

        update_manifest(self.project_id, {
            "output": {
                "final_file": str(final_path),
                "duration": final_duration,
                "format": settings.VIDEO_FORMAT,
            }
        })

        await self._emit_progress({
            "type": "final_merged",
            "project_id": self.project_id,
            "duration": final_duration,
            "file": str(final_path),
        })

        logger.info(
            "Final video created",
            project_id=self.project_id,
            duration=final_duration,
            path=str(final_path),
        )
