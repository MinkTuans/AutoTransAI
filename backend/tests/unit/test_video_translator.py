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


def test_adapter_can_handle_bilibili_url():
    """Bilibili watch URLs (including timestamp query) must be treated as page sources."""
    from app.services.video_source.page_url_adapter import PAGE_DOMAINS

    adapter = PageURLAdapter()
    url = "https://www.bilibili.com/video/BV1dRMP68Ehp?t=40.9"
    assert adapter.can_handle(url) is True
    assert "bilibili.com" in PAGE_DOMAINS
    assert "b23.tv" in PAGE_DOMAINS


def test_bilibili_domain_display_name():
    """Bilibili must be labeled Bilibili, not Www.bilibili.com."""
    adapter = PageURLAdapter()
    assert adapter._get_domain_display("www.bilibili.com") == "Bilibili"
    assert adapter._get_domain_display("bilibili.com") == "Bilibili"
    assert adapter._get_domain_display("b23.tv") == "Bilibili"


def test_yt_dlp_download_cmd_for_bilibili_uses_browser_headers():
    """Bilibili WAF (HTTP 412) requires browser UA/referer and merged DASH streams."""
    from app.services.video_source.page_url_adapter import build_yt_dlp_download_cmd

    url = "https://www.bilibili.com/video/BV1dRMP68Ehp?t=40.9"
    cmd = build_yt_dlp_download_cmd("yt-dlp", url, Path("/tmp/out.mp4"))
    assert "--user-agent" in cmd
    assert "--referer" in cmd
    assert any("bilibili.com" in str(part) for part in cmd)
    assert "--merge-output-format" in cmd
    assert "mp4" in cmd
    assert "-f" in cmd
    fmt = cmd[cmd.index("-f") + 1]
    assert "bv" in fmt or "+" in fmt
    assert url in cmd
    assert "--retries" in cmd
    assert "-N" in cmd
    assert cmd[cmd.index("-N") + 1] == "1"
    assert "-c" in cmd or "--continue" in cmd


def test_parse_yt_dlp_progress_line():
    """yt-dlp newline progress must yield percent and byte totals for the UI."""
    from app.services.video_source.page_url_adapter import parse_yt_dlp_progress_line

    parsed = parse_yt_dlp_progress_line(
        "[download]  45.2% of  17.22MiB at  1.10MiB/s ETA 00:13"
    )
    assert parsed is not None
    assert parsed["percent"] == 45.2
    assert parsed["total_bytes"] == int(17.22 * 1024 * 1024)
    assert parsed["speed"] == "1.10MiB/s"
    assert parsed["eta"] == "00:13"
    assert parse_yt_dlp_progress_line("ERROR: boom") is None


def test_yt_dlp_truncated_download_error_is_human_readable():
    """Incomplete CDN read must not look like a generic exit 1."""
    from app.services.video_source.page_url_adapter import raise_yt_dlp_download_error

    with pytest.raises(ValueError) as excinfo:
        raise_yt_dlp_download_error(
            "Bilibili",
            "[download] Got error: 509 bytes read, 18052770 more expected. Giving up after 10 retries",
            returncode=1,
        )
    msg = str(excinfo.value).lower()
    assert "cắt" in msg or "mạng" in msg or "không hoàn chỉnh" in msg


def test_yt_dlp_412_error_is_human_readable():
    """yt-dlp 412/WAF failures must not surface as empty ❌ or CalledProcessError."""
    from app.services.video_source.page_url_adapter import raise_yt_dlp_download_error

    with pytest.raises(ValueError) as excinfo:
        raise_yt_dlp_download_error(
            "Bilibili",
            "ERROR: [BiliBili] BV1dRMP68Ehp: Unable to download JSON metadata: HTTP Error 412: Precondition Failed",
        )
    msg = str(excinfo.value)
    assert "412" in msg
    assert "Bilibili" in msg
    assert "cookie" in msg.lower() or "chặn" in msg.lower()


def test_parse_bilibili_video_ref_ignores_timestamp_query():
    """?t= is a start offset, not a page. Default part is P1."""
    from app.services.video_source.page_url_adapter import parse_bilibili_video_ref

    ref = parse_bilibili_video_ref("https://www.bilibili.com/video/BV1dRMP68Ehp?t=40.9")
    assert ref["bvid"] == "BV1dRMP68Ehp"
    assert ref["page"] == 1

    ref_p2 = parse_bilibili_video_ref("https://www.bilibili.com/video/BV1dRMP68Ehp?p=2&t=10")
    assert ref_p2["page"] == 2


def test_bilibili_pagelist_maps_part_duration():
    """Check-url must use pagelist duration (893s), not the dummy 00:00 fallback."""
    from app.services.video_source.page_url_adapter import metadata_from_bilibili_pagelist

    pages = [
        {
            "page": 1,
            "part": "宠物心声诊所 1",
            "duration": 893,
            "dimension": {"width": 1280, "height": 720},
        },
        {
            "page": 2,
            "part": "宠物心声诊所 2",
            "duration": 895,
            "dimension": {"width": 1280, "height": 720},
        },
    ]
    meta = metadata_from_bilibili_pagelist(pages, page=1, bvid="BV1dRMP68Ehp")
    assert meta["duration"] == 893
    assert meta["title"] == "宠物心声诊所 1"
    assert meta["width"] == 1280
    assert meta["height"] == 720
    assert meta["source"] == "Bilibili"


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
