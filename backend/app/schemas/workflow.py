"""Workflow-related Pydantic schemas (preflight, status)."""

from __future__ import annotations

from pydantic import BaseModel


class PreflightCheck(BaseModel):
    """Result of a single preflight check."""
    name: str
    description: str
    passed: bool
    required: bool
    error_code: str | None = None
    error_message: str | None = None


class PreflightResult(BaseModel):
    """Overall preflight check result."""
    project_id: str
    passed: bool
    checks: list[PreflightCheck] = []
    blocking_failures: list[PreflightCheck] = []
