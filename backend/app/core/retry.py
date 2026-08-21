"""
Retry logic with exponential backoff, jitter, and error classification.

Classifies errors into retryable vs terminal to avoid wasting quota
on requests that will never succeed.
"""

from __future__ import annotations

import asyncio
import random
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import httpx

from app.core import get_logger
from app.core.exceptions import (
    ContentPolicyError,
    InvalidApiKeyError,
    ProviderError,
    QuotaExhaustedError,
    RateLimitError,
)

logger = get_logger(__name__)

T = TypeVar("T")


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 2.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number (0-indexed)."""
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        delay = min(delay, self.max_delay)
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)  # noqa: S311
        return delay


def classify_error(error: Exception) -> str:
    """
    Classify an error as retryable or terminal.

    Returns:
        "retry" — should retry with backoff
        "stop" — terminal error, do not retry
        "rate_limit" — retry with longer backoff
    """
    # Our own exception types
    if isinstance(error, (InvalidApiKeyError, QuotaExhaustedError, ContentPolicyError)):
        return "stop"
    if isinstance(error, RateLimitError):
        return "rate_limit"

    # HTTP status-based classification
    if isinstance(error, httpx.HTTPStatusError):
        status = error.response.status_code
        if status == 429:
            return "rate_limit"
        if status in (401, 403):
            return "stop"
        if status == 400:
            return "stop"
        if 500 <= status < 600:
            return "retry"
        return "stop"

    # Network / timeout errors
    if isinstance(error, (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError)):
        return "retry"

    # Connection errors
    if isinstance(error, (ConnectionError, TimeoutError, OSError)):
        return "retry"

    # Unknown errors — don't retry to be safe
    return "stop"


async def retry_async(
    func: Callable[..., Any],
    *args: Any,
    config: RetryConfig | None = None,
    context: dict | None = None,
    **kwargs: Any,
) -> Any:
    """
    Execute an async function with retry logic.

    Args:
        func: Async function to execute.
        config: Retry configuration. Uses defaults if None.
        context: Extra context for logging (provider_id, segment_id, etc.).

    Returns:
        The result of the function.

    Raises:
        The last error if all retries are exhausted or error is terminal.
    """
    config = config or RetryConfig()
    context = context or {}
    last_error: Exception | None = None

    for attempt in range(config.max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_error = e
            classification = classify_error(e)

            log_ctx = {
                "attempt": attempt + 1,
                "max_retries": config.max_retries,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "classification": classification,
                **context,
            }

            if classification == "stop":
                logger.error("Terminal error, not retrying", **log_ctx)
                raise

            if attempt >= config.max_retries:
                logger.error("Max retries exhausted", **log_ctx)
                raise

            delay = config.get_delay(attempt)

            # Rate limit errors get extra delay
            if classification == "rate_limit":
                if isinstance(e, RateLimitError) and e.details.get("retry_after"):
                    delay = max(delay, e.details["retry_after"])
                else:
                    delay = delay * 2

            logger.warning(
                "Retrying after error",
                delay_seconds=round(delay, 2),
                **log_ctx,
            )
            await asyncio.sleep(delay)

    # Should not reach here, but just in case
    if last_error:
        raise last_error
    raise RuntimeError("Retry loop exited without result or error")
