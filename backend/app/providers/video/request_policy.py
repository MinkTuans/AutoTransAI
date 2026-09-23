"""Shared billing-aware failure policy for keyed video requests."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from app.providers.base import GenerationResult
from app.providers.video.catalog_media import VideoBoundaryError, VideoRoutePending

_ROTATABLE_REJECTIONS = frozenset({"HTTP_401", "HTTP_402", "HTTP_403", "HTTP_429"})


async def run_legacy_video(
    provider_id: str, key_manager: Callable[[], Any],
    invoke: Callable[[Any], Awaitable[GenerationResult]], *, no_key_message: str,
) -> GenerationResult:
    """Rotate only after an explicit key rejection, never after uncertain work."""
    last = None
    for _ in range(3):
        try:
            entry = await key_manager().get_active_key(provider_id)
        except Exception:
            return GenerationResult(False, provider_id=provider_id, error_code="PROVIDER_UNAVAILABLE",
                                    error_message="Video generation failed: provider_unavailable")
        if not entry:
            break
        last = await invoke(entry)
        if last.success or last.error_code not in _ROTATABLE_REJECTIONS:
            return last
    return last or GenerationResult(False, provider_id=provider_id, error_code="NO_API_KEY",
                                    error_message=no_key_message)


class VideoAttemptPolicy:
    """Classify one request without exposing provider, prompt, or credential text."""

    def __init__(self, provider_id: str, *, canonical: bool, key_id: str | None,
                 key_manager: Callable[[], Any]):
        self.provider_id = provider_id
        self.canonical = canonical
        self.key_id = key_id
        self.key_manager = key_manager
        self.submitted = False
        self.accepted = False

    async def success(self, result: GenerationResult) -> GenerationResult:
        if self.key_id is not None:
            try:
                await self.key_manager().report_result(self.provider_id, self.key_id, success=True)
            except Exception:
                pass  # Accounting cannot hide completed output or trigger another billed attempt.
        return result

    async def boundary_error(self, error: VideoBoundaryError) -> GenerationResult:
        if (self.submitted and not error.definitive
                and (self.accepted or error.status_code is None or error.status_code >= 500)):
            raise VideoRoutePending(error.code) from None
        if self.canonical:
            raise error
        if self.key_id is not None and error.status_code is not None:
            try:
                await self.key_manager().report_result(
                    self.provider_id, self.key_id, success=False,
                    status_code=error.status_code, error_message=str(error))
            except Exception:
                pass
        return GenerationResult(False, provider_id=self.provider_id,
                                error_code=f"HTTP_{error.status_code}" if error.status_code else error.code.upper(),
                                error_message=str(error))

    def cancelled(self) -> None:
        if self.submitted:
            raise VideoRoutePending() from None
        raise asyncio.CancelledError

    def timed_out(self) -> None:
        if self.submitted:
            raise VideoRoutePending("timeout") from None
        raise TimeoutError

    def unexpected(self) -> GenerationResult:
        if self.submitted:
            raise VideoRoutePending("provider_unavailable") from None
        if self.canonical:
            raise VideoBoundaryError("provider_unavailable") from None
        return GenerationResult(False, provider_id=self.provider_id, error_code="PROVIDER_UNAVAILABLE",
                                error_message="Video generation failed: provider_unavailable")
