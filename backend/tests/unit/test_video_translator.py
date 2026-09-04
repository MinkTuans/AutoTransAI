"""
Unit tests for Video Translator security, adapters, and pipeline.
"""

import os
from pathlib import Path
import pytest

from app.config import get_settings
from app.core.security_url import validate_url_security, SSRFValidationError, is_ip_private_or_blocked
from app.services.video_source import (
    DirectURLAdapter,
    PageURLAdapter,
    VideoSourceService,
    get_video_source_service,
)

settings = get_settings()


def test_ssrf_validation_blocked_ips():
    """Test 11: SSRF protection blocks private IPs and cloud metadata."""
    blocked_urls = [
        "http://localhost/video.mp4",
        "http://127.0.0.1/video.mp4",
        "http://0.0.0.0/video.mp4",
        "http://10.0.0.1/video.mp4",
        "http://172.16.0.1/video.mp4",
        "http://192.168.1.1/video.mp4",
        "http://169.254.169.254/latest/meta-data/",
    ]
    for url in blocked_urls:
        with pytest.raises(SSRFValidationError):
            validate_url_security(url)


def test_ssrf_validation_valid_url(monkeypatch):
    """Test 2: Direct valid external public URL passes validation."""
    monkeypatch.setattr("socket.getaddrinfo", lambda host, port: [(2, 1, 6, "", ("93.184.215.14", 0))])
    valid_url = "https://example.com/sample_video.mp4"
    result = validate_url_security(valid_url)
    assert result == valid_url



def test_adapter_can_handle_direct_url():
    """Test DirectURLAdapter matching."""
    adapter = DirectURLAdapter()
    assert adapter.can_handle("https://example.com/video.mp4") is True
    assert adapter.can_handle("https://example.com/clip.webm") is True
    assert adapter.can_handle("https://example.com/index.html") is False


def test_adapter_can_handle_page_url():
    """Test 3: PageURLAdapter matching video platforms."""
    adapter = PageURLAdapter()
    assert adapter.can_handle("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
    assert adapter.can_handle("https://vimeo.com/12345678") is True
    assert adapter.can_handle("https://example.com/video.mp4") is False


def test_unsupported_source():
    """Test 10: Unsupported or invalid scheme URL raises ValueError."""
    service = get_video_source_service()
    with pytest.raises(ValueError) as excinfo:
        service.resolve_adapter("ftp://example.com/video.mp4")
    assert "giao thức" in str(excinfo.value).lower() or "hỗ trợ" in str(excinfo.value).lower()


def test_invalid_url():
    """Test 4: Invalid URL format."""
    service = get_video_source_service()
    with pytest.raises(ValueError):
        service.resolve_adapter("not_a_url")
