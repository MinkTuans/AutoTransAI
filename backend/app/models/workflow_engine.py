"""SQLAlchemy models for Unified Stage-Based Workflow Engine, Glossary, and Voice Mapping."""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Optional, Any

from sqlalchemy import String, Text, DateTime, Boolean, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WorkflowEngineStatus(str, enum.Enum):
    """Workflow level state machine states."""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    PAUSED = "paused"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkflowStageStatus(str, enum.Enum):
    """Stage level state machine states."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"
    SKIPPED = "skipped"


class WorkflowStepStatus(str, enum.Enum):
    """Step level state machine states."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


class ProjectGlossary(Base):
    """Glossary term mapping for translation consistency across project batches."""
    __tablename__ = "project_glossaries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    
    source_term: Mapped[str] = mapped_column(String(255), nullable=False)
    translated_term: Mapped[str] = mapped_column(String(255), nullable=False)
    
    term_type: Mapped[str] = mapped_column(String(50), default="other")  # character, location, organization, skill, weapon, item, technique, title, other
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    source_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


class SpeakerVoiceMapping(Base):
    """Voice provider assignment for specific speakers detected in the transcript."""
    __tablename__ = "speaker_voice_mappings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    
    speaker_id: Mapped[str] = mapped_column(String(100), nullable=False)
    speaker_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    voice_provider: Mapped[str] = mapped_column(String(50), default="edge")  # edge, google, elevenlabs
    voice_id: Mapped[str] = mapped_column(String(100), nullable=False)
    voice_settings: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


class WorkflowExecution(Base):
    """Top-level record for a workflow execution instance."""
    __tablename__ = "workflow_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    workflow_type: Mapped[str] = mapped_column(String(50), default="video_translation")
    
    status: Mapped[str] = mapped_column(String(30), default=WorkflowEngineStatus.NOT_STARTED.value)
    current_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    current_step: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    context_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    stages: Mapped[list["WorkflowStageExecution"]] = relationship(
        back_populates="workflow_execution", cascade="all, delete-orphan",
        order_by="WorkflowStageExecution.created_at"
    )


class WorkflowStageExecution(Base):
    """Stage execution tracking for a workflow instance."""
    __tablename__ = "workflow_stage_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workflow_execution_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workflow_executions.id", ondelete="CASCADE"), index=True
    )
    
    stage_name: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default=WorkflowStageStatus.PENDING.value)
    
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    qc_report: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    # Relationships
    workflow_execution: Mapped["WorkflowExecution"] = relationship(back_populates="stages")
    steps: Mapped[list["WorkflowStepExecution"]] = relationship(
        back_populates="stage_execution", cascade="all, delete-orphan",
        order_by="WorkflowStepExecution.created_at"
    )


class WorkflowStepExecution(Base):
    """Step execution tracking within a workflow stage."""
    __tablename__ = "workflow_step_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    stage_execution_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workflow_stage_executions.id", ondelete="CASCADE"), index=True
    )
    
    step_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default=WorkflowStepStatus.PENDING.value)
    
    input_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    output_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    # Relationships
    stage_execution: Mapped["WorkflowStageExecution"] = relationship(back_populates="steps")
