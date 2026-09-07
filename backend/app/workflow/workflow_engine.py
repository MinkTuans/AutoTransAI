"""Unified Stage-Based Workflow Engine orchestrating 6 stages with DB persistence, retries, resume, and QC gates."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.workflow_engine import (
    WorkflowExecution,
    WorkflowStageExecution,
    WorkflowStepExecution,
    WorkflowEngineStatus,
    WorkflowStageStatus,
    WorkflowStepStatus,
)
from app.models.project import Project, WorkflowStatus
from app.workflow.workflow_context import WorkflowContext
from app.workflow.workflow_registry import WorkflowRegistry

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Core engine driving 6-stage video processing workflows."""

    def __init__(self, registry: Optional[WorkflowRegistry] = None) -> None:
        self.registry = registry or WorkflowRegistry()
        self._active_tasks: dict[str, asyncio.Task] = {}

    async def start_workflow(
        self,
        project_id: str,
        context_data: Optional[dict[str, Any]] = None,
        db: Optional[AsyncSession] = None,
    ) -> WorkflowExecution:
        """Start or restart a workflow for a project with optional context data."""
        if isinstance(context_data, AsyncSession):
            db = context_data
            context_data = None

        close_session = False
        if db is None:
            db = async_session_factory()
            close_session = True

        try:
            # Check existing execution
            stmt = select(WorkflowExecution).where(WorkflowExecution.project_id == project_id)
            res = await db.execute(stmt)
            wf_exec = res.scalars().first()

            merged_context = {"project_id": project_id}
            if context_data and isinstance(context_data, dict):
                merged_context.update(context_data)

            if not wf_exec:
                wf_exec = WorkflowExecution(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    workflow_type="video_translation",
                    status=WorkflowEngineStatus.RUNNING.value,
                    current_stage="INGEST",
                    started_at=datetime.now(timezone.utc).replace(tzinfo=None),
                    context_data=merged_context,
                )
                db.add(wf_exec)
                await db.commit()
                await db.refresh(wf_exec)
            else:
                wf_exec.status = WorkflowEngineStatus.RUNNING.value
                wf_exec.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                if context_data:
                    existing_ctx = wf_exec.context_data or {}
                    existing_ctx.update(context_data)
                    wf_exec.context_data = existing_ctx
                await db.commit()

            # Launch background execution task
            if project_id in self._active_tasks and not self._active_tasks[project_id].done():
                self._active_tasks[project_id].cancel()

            task = asyncio.create_task(self._run_workflow_loop(project_id, wf_exec.id))
            self._active_tasks[project_id] = task

            return wf_exec
        finally:
            if close_session:
                await db.close()

    async def pause_workflow(self, project_id: str, db: Optional[AsyncSession] = None) -> bool:
        """Pause a running workflow cleanly after current safe checkpoint."""
        close_session = False
        if db is None:
            db = async_session_factory()
            close_session = True

        try:
            stmt = select(WorkflowExecution).where(WorkflowExecution.project_id == project_id)
            res = await db.execute(stmt)
            wf_exec = res.scalars().first()
            if wf_exec:
                wf_exec.status = WorkflowEngineStatus.PAUSED.value
                await db.commit()

            if project_id in self._active_tasks:
                task = self._active_tasks.pop(project_id)
                if not task.done():
                    task.cancel()
            return True
        finally:
            if close_session:
                await db.close()

    async def resume_workflow(self, project_id: str, db: Optional[AsyncSession] = None) -> WorkflowExecution:
        """Resume execution from the last failed or pending checkpoint stage."""
        close_session = False
        if db is None:
            db = async_session_factory()
            close_session = True

        try:
            stmt = select(WorkflowExecution).where(WorkflowExecution.project_id == project_id)
            res = await db.execute(stmt)
            wf_exec = res.scalars().first()
            if not wf_exec:
                raise ValueError(f"No workflow execution found for project {project_id}")

            wf_exec.status = WorkflowEngineStatus.RUNNING.value
            await db.commit()

            if project_id in self._active_tasks and not self._active_tasks[project_id].done():
                self._active_tasks[project_id].cancel()

            task = asyncio.create_task(self._run_workflow_loop(project_id, wf_exec.id))
            self._active_tasks[project_id] = task
            return wf_exec
        finally:
            if close_session:
                await db.close()

    async def cancel_workflow(self, project_id: str, db: Optional[AsyncSession] = None) -> bool:
        """Safely terminate an active workflow."""
        if project_id in self._active_tasks:
            task = self._active_tasks.pop(project_id)
            if not task.done():
                task.cancel()

        close_session = False
        if db is None:
            db = async_session_factory()
            close_session = True

        try:
            stmt = select(WorkflowExecution).where(WorkflowExecution.project_id == project_id)
            res = await db.execute(stmt)
            wf_exec = res.scalars().first()
            if wf_exec:
                wf_exec.status = WorkflowEngineStatus.CANCELLED.value
                await db.commit()
            return True
        finally:
            if close_session:
                await db.close()

    async def retry_stage(self, project_id: str, stage_name: str, db: Optional[AsyncSession] = None) -> WorkflowExecution:
        """Reset a failed/paused stage state and restart execution from that stage."""
        close_session = False
        if db is None:
            db = async_session_factory()
            close_session = True

        try:
            stmt = select(WorkflowExecution).where(WorkflowExecution.project_id == project_id)
            res = await db.execute(stmt)
            wf_exec = res.scalars().first()
            if not wf_exec:
                raise ValueError(f"No workflow execution found for project {project_id}")

            # Reset specified stage and subsequent stages
            stmt_stages = select(WorkflowStageExecution).where(
                WorkflowStageExecution.workflow_execution_id == wf_exec.id
            )
            stages_res = await db.execute(stmt_stages)
            all_stages = stages_res.scalars().all()

            stages_list = self.registry.list_stages()
            if stage_name in stages_list:
                target_idx = stages_list.index(stage_name)
                for st in all_stages:
                    if st.stage_name in stages_list and stages_list.index(st.stage_name) >= target_idx:
                        st.status = WorkflowStageStatus.PENDING.value
                        st.error = None
                        st.qc_report = None
                        # Reset steps
                        stmt_steps = select(WorkflowStepExecution).where(
                            WorkflowStepExecution.stage_execution_id == st.id
                        )
                        steps_res = await db.execute(stmt_steps)
                        for step_rec in steps_res.scalars().all():
                            step_rec.status = WorkflowStepStatus.PENDING.value
                            step_rec.error = None

            wf_exec.current_stage = stage_name
            wf_exec.status = WorkflowEngineStatus.RUNNING.value
            wf_exec.error_message = None
            await db.commit()

            if project_id in self._active_tasks and not self._active_tasks[project_id].done():
                self._active_tasks[project_id].cancel()

            task = asyncio.create_task(self._run_workflow_loop(project_id, wf_exec.id))
            self._active_tasks[project_id] = task
            return wf_exec
        finally:
            if close_session:
                await db.close()

    async def _run_workflow_loop(self, project_id: str, execution_id: str) -> None:
        """Main execution loop iterating through ordered stages."""
        logger.info(f"[WorkflowEngine] Starting execution loop for project {project_id}")

        stages = self.registry.list_stages()
        
        async with async_session_factory() as db:
            # Hydrate context
            stmt = select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
            res = await db.execute(stmt)
            wf_exec = res.scalars().first()
            if not wf_exec:
                return

            ctx_dict = wf_exec.context_data or {"project_id": project_id}
            ctx = WorkflowContext.from_dict(ctx_dict)
            ctx.workflow_id = execution_id

            # Determine starting stage index
            current_stage_name = wf_exec.current_stage or stages[0]
            start_index = stages.index(current_stage_name) if current_stage_name in stages else 0

            try:
                for stage_name in stages[start_index:]:
                    # Check cancellation or pause
                    await db.refresh(wf_exec)
                    if wf_exec.status in (WorkflowEngineStatus.PAUSED.value, WorkflowEngineStatus.CANCELLED.value):
                        logger.info(f"[WorkflowEngine] Workflow loop stopped due to status: {wf_exec.status}")
                        return

                    wf_exec.current_stage = stage_name
                    await db.commit()

                    # Get or create stage execution record
                    stage_exec = await self._get_or_create_stage_exec(db, execution_id, stage_name)
                    stage_exec.status = WorkflowStageStatus.RUNNING.value
                    stage_exec.started_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    await db.commit()

                    stage_inst = self.registry.get_stage(stage_name)
                    steps = getattr(stage_inst, "STEPS", [])

                    stage_failed = False
                    for step_name in steps:
                        wf_exec.current_step = step_name
                        await db.commit()

                        step_exec = await self._get_or_create_step_exec(db, stage_exec.id, step_name)

                        # Step-aware skip if already completed
                        if step_exec.status == WorkflowStepStatus.SUCCESS.value and step_exec.output_data:
                            logger.info(f"[WorkflowEngine] Step {step_name} already completed, skipping.")
                            continue

                        step_exec.status = WorkflowStepStatus.RUNNING.value
                        step_exec.started_at = datetime.now(timezone.utc).replace(tzinfo=None)
                        await db.commit()

                        # Step retry loop
                        max_retries = 3
                        step_success = False
                        for attempt in range(max_retries):
                            try:
                                output = await getattr(stage_inst, "execute_step")(step_name, ctx, db)
                                step_exec.status = WorkflowStepStatus.SUCCESS.value
                                step_exec.output_data = output
                                step_exec.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
                                step_success = True
                                await db.commit()
                                break
                            except Exception as ex:
                                logger.error(f"[WorkflowEngine] Step {step_name} failed (attempt {attempt+1}): {str(ex)}")
                                step_exec.retry_count = attempt + 1
                                step_exec.error = str(ex)
                                if attempt < max_retries - 1:
                                    step_exec.status = WorkflowStepStatus.RETRYING.value
                                    await db.commit()
                                    await asyncio.sleep(1.0 * (attempt + 1))  # exponential backoff
                                else:
                                    step_exec.status = WorkflowStepStatus.FAILED.value
                                    step_exec.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
                                    await db.commit()

                        if not step_success:
                            stage_failed = True
                            stage_exec.status = WorkflowStageStatus.FAILED.value
                            stage_exec.error = step_exec.error
                            stage_exec.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
                            wf_exec.status = WorkflowEngineStatus.FAILED.value
                            wf_exec.error_message = step_exec.error
                            await db.commit()
                            break

                    if stage_failed:
                        break

                    # Run Stage QC Gate
                    qc_report = await getattr(stage_inst, "run_qc")(ctx)
                    stage_exec.qc_report = qc_report

                    if qc_report.get("passed"):
                        stage_exec.status = WorkflowStageStatus.PASSED.value
                        stage_exec.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
                        wf_exec.context_data = ctx.to_dict()
                        await db.commit()
                    else:
                        logger.warning(f"[WorkflowEngine] Stage {stage_name} QC failed. Issues: {qc_report.get('issues')}")
                        stage_exec.status = WorkflowStageStatus.NEEDS_REVIEW.value
                        wf_exec.status = WorkflowEngineStatus.NEEDS_REVIEW.value
                        await db.commit()
                        return  # Stop for human review

                # Check if all stages passed
                if not stage_failed and wf_exec.status == WorkflowEngineStatus.RUNNING.value:
                    wf_exec.status = WorkflowEngineStatus.COMPLETED.value
                    wf_exec.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    await db.commit()
            except asyncio.CancelledError:
                logger.info(f"[WorkflowEngine] Workflow loop cancelled cleanly for project {project_id}")
                await db.refresh(wf_exec)
                if wf_exec.status != WorkflowEngineStatus.CANCELLED.value:
                    wf_exec.status = WorkflowEngineStatus.PAUSED.value
                await db.commit()
                raise

    async def _get_or_create_stage_exec(self, db: AsyncSession, execution_id: str, stage_name: str) -> WorkflowStageExecution:
        stmt = select(WorkflowStageExecution).where(
            WorkflowStageExecution.workflow_execution_id == execution_id,
            WorkflowStageExecution.stage_name == stage_name,
        )
        res = await db.execute(stmt)
        record = res.scalars().first()
        if not record:
            record = WorkflowStageExecution(
                id=str(uuid.uuid4()),
                workflow_execution_id=execution_id,
                stage_name=stage_name,
                status=WorkflowStageStatus.PENDING.value,
            )
            db.add(record)
            await db.commit()
            await db.refresh(record)
        return record

    async def _get_or_create_step_exec(self, db: AsyncSession, stage_exec_id: str, step_name: str) -> WorkflowStepExecution:
        stmt = select(WorkflowStepExecution).where(
            WorkflowStepExecution.stage_execution_id == stage_exec_id,
            WorkflowStepExecution.step_name == step_name,
        )
        res = await db.execute(stmt)
        record = res.scalars().first()
        if not record:
            record = WorkflowStepExecution(
                id=str(uuid.uuid4()),
                stage_execution_id=stage_exec_id,
                step_name=step_name,
                status=WorkflowStepStatus.PENDING.value,
            )
            db.add(record)
            await db.commit()
            await db.refresh(record)
        return record
