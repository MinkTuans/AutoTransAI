"""Workflow-related Pydantic schemas (preflight, status)."""

from __future__ import annotations

from pydantic import BaseModel


class PreflightCheck(BaseModel):
    """Result of a single preflight check."""
    name: str
    description: str
    passed: bool
    required: bool
    category: str = "critical"  # "critical" or "optional"
    error_code: str | None = None
    error_message: str | None = None


class PreflightResult(BaseModel):
    """Overall preflight check result."""
    project_id: str
    passed: bool
    can_start: bool = True
    checks: list[PreflightCheck] = []
    blocking_failures: list[PreflightCheck] = []
    warnings: list[PreflightCheck] = []
