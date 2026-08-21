"""
Unit tests for the retry module.
"""

import pytest

from app.core.retry import classify_error, RetryConfig
from app.core.exceptions import (
    InvalidApiKeyError,
    QuotaExhaustedError,
    RateLimitError,
    ContentPolicyError,
)
import httpx


class TestClassifyError:
    def test_invalid_api_key_is_stop(self):
        assert classify_error(InvalidApiKeyError("test")) == "stop"

    def test_quota_exhausted_is_stop(self):
        assert classify_error(QuotaExhaustedError("p", "chars", 100, 50)) == "stop"

    def test_content_policy_is_stop(self):
        assert classify_error(ContentPolicyError("p")) == "stop"

    def test_rate_limit_is_rate_limit(self):
        assert classify_error(RateLimitError("p")) == "rate_limit"

    def test_timeout_is_retry(self):
        assert classify_error(TimeoutError()) == "retry"

    def test_connection_error_is_retry(self):
        assert classify_error(ConnectionError()) == "retry"

    def test_unknown_is_stop(self):
        assert classify_error(ValueError("random")) == "stop"


class TestRetryConfig:
    def test_basic_delay(self):
        config = RetryConfig(
            initial_delay=1.0, backoff_factor=2.0, jitter=False
        )
        assert config.get_delay(0) == 1.0
        assert config.get_delay(1) == 2.0
        assert config.get_delay(2) == 4.0

    def test_max_delay(self):
        config = RetryConfig(
            initial_delay=1.0, backoff_factor=2.0, max_delay=5.0, jitter=False
        )
        assert config.get_delay(10) == 5.0  # Capped

    def test_jitter_varies(self):
        config = RetryConfig(
            initial_delay=10.0, backoff_factor=1.0, jitter=True
        )
        delays = [config.get_delay(0) for _ in range(10)]
        # With jitter, not all delays should be identical
        assert len(set(delays)) > 1
