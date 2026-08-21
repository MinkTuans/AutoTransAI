from __future__ import annotations

"""
Application-specific exceptions.

All custom exceptions inherit from WorkflowError for easy catching.
Error codes are used for API responses and logging.
"""


class WorkflowError(Exception):
    """Base exception for all workflow errors."""

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


# ── Script Errors ──────────────────────────────────────────────────────

class InvalidScriptError(WorkflowError):
    """Raised when a script cannot be parsed."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="INVALID_SCRIPT", details=details)


class EmptyScriptError(WorkflowError):
    """Raised when a script produces no segments."""

    def __init__(self):
        super().__init__("Script produced no segments", code="EMPTY_SCRIPT")


# ── Provider Errors ────────────────────────────────────────────────────

class ProviderError(WorkflowError):
    """Base for all provider-related errors."""
    pass


class ProviderNotConfiguredError(ProviderError):
    """Raised when a required provider has no API key."""

    def __init__(self, provider_id: str):
        super().__init__(
            f"Provider '{provider_id}' is not configured",
            code="PROVIDER_NOT_CONFIGURED",
            details={"provider_id": provider_id},
        )


class ProviderUnreachableError(ProviderError):
    """Raised when a provider API cannot be reached."""

    def __init__(self, provider_id: str, reason: str = ""):
        super().__init__(
            f"Provider '{provider_id}' is unreachable: {reason}",
            code="PROVIDER_UNREACHABLE",
            details={"provider_id": provider_id, "reason": reason},
        )


class InvalidApiKeyError(ProviderError):
    """Raised when an API key is rejected by the provider."""

    def __init__(self, provider_id: str):
        super().__init__(
            f"Invalid API key for provider '{provider_id}'",
            code="INVALID_API_KEY",
            details={"provider_id": provider_id},
        )


class QuotaExhaustedError(ProviderError):
    """Raised when provider quota is insufficient."""

    def __init__(self, provider_id: str, resource: str, required: float, available: float):
        super().__init__(
            f"Insufficient {resource} for provider '{provider_id}': "
            f"required={required}, available={available}",
            code="QUOTA_INSUFFICIENT",
            details={
                "provider_id": provider_id,
                "resource": resource,
                "required": required,
                "available": available,
            },
        )


class RateLimitError(ProviderError):
    """Raised on 429 rate limit response — should trigger retry."""

    def __init__(self, provider_id: str, retry_after: float | None = None):
        super().__init__(
            f"Rate limited by provider '{provider_id}'",
            code="RATE_LIMITED",
            details={"provider_id": provider_id, "retry_after": retry_after},
        )


class ContentPolicyError(ProviderError):
    """Raised when content is rejected by provider's content policy."""

    def __init__(self, provider_id: str, segment_id: int | None = None):
        super().__init__(
            f"Content rejected by provider '{provider_id}' policy",
            code="CONTENT_POLICY_REJECTION",
            details={"provider_id": provider_id, "segment_id": segment_id},
        )


# ── Workflow Errors ────────────────────────────────────────────────────

class WorkflowStateError(WorkflowError):
    """Raised on invalid workflow state transition."""

    def __init__(self, current_state: str, attempted_state: str):
        super().__init__(
            f"Invalid state transition: {current_state} → {attempted_state}",
            code="INVALID_STATE_TRANSITION",
            details={"current_state": current_state, "attempted_state": attempted_state},
        )


class PreflightError(WorkflowError):
    """Raised when preflight checks fail."""

    def __init__(self, failures: list[dict]):
        super().__init__(
            f"Preflight failed: {len(failures)} check(s) failed",
            code="PREFLIGHT_FAILED",
            details={"failures": failures},
        )


# ── System Errors ──────────────────────────────────────────────────────

class FFmpegNotFoundError(WorkflowError):
    """Raised when FFmpeg/FFprobe is not installed."""

    def __init__(self):
        super().__init__(
            "FFmpeg not found. Please install FFmpeg and ensure it's in PATH.",
            code="FFMPEG_NOT_FOUND",
        )


class StorageError(WorkflowError):
    """Raised on file system errors (not writable, disk full, etc.)."""

    def __init__(self, message: str, path: str = ""):
        super().__init__(
            message,
            code="STORAGE_ERROR",
            details={"path": path},
        )
