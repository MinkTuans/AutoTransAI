"""OAuth must open in Google Chrome, never inside the desktop app window."""

from unittest.mock import MagicMock, patch

import pytest

from app.core.open_browser import (
    chrome_launch_command,
    is_allowed_oauth_url,
    open_oauth_in_chrome,
)


def test_google_oauth_url_is_allowed():
    assert is_allowed_oauth_url(
        "https://accounts.google.com/o/oauth2/auth?client_id=abc&redirect_uri=http://127.0.0.1:8000/api/youtube/oauth-callback"
    )


def test_tiktok_oauth_url_is_allowed():
    assert is_allowed_oauth_url(
        "https://www.tiktok.com/v2/auth/authorize/?client_key=abc&response_type=code"
    )


def test_random_and_internal_urls_are_blocked():
    assert not is_allowed_oauth_url("https://evil.example/phish")
    assert not is_allowed_oauth_url("file:///etc/passwd")
    assert not is_allowed_oauth_url("http://127.0.0.1:8000/api/system/health")
    assert not is_allowed_oauth_url("javascript:alert(1)")


def test_chrome_launch_command_opens_new_tab():
    cmd = chrome_launch_command(
        "https://www.tiktok.com/v2/auth/authorize/?client_key=abc",
        chrome_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    )
    assert cmd[0].endswith("chrome.exe")
    assert "--new-tab" in cmd
    assert cmd[-1].startswith("https://www.tiktok.com/v2/auth/authorize/")


def test_open_oauth_in_chrome_launches_allowed_url():
    url = "https://www.tiktok.com/v2/auth/authorize/?client_key=abc"
    with patch("app.core.open_browser.resolve_chrome_path", return_value="/usr/bin/google-chrome"):
        with patch("app.core.open_browser.subprocess.Popen") as popen:
            popen.return_value = MagicMock()
            result = open_oauth_in_chrome(url)
    assert result["ok"] is True
    assert result["browser"] == "chrome"
    popen.assert_called_once()
    launched = popen.call_args[0][0]
    assert "--new-tab" in launched
    assert url in launched


def test_open_oauth_in_chrome_rejects_non_oauth_url():
    with pytest.raises(ValueError, match="không được phép"):
        open_oauth_in_chrome("https://example.com")


@pytest.mark.asyncio
async def test_open_browser_api_allows_tiktok_and_blocks_other():
    from httpx import ASGITransport, AsyncClient
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        blocked = await client.post("/api/system/open-browser", json={"url": "https://example.com"})
        assert blocked.status_code == 400

        with patch("app.api.routes.system.open_oauth_in_chrome", return_value={"ok": True, "browser": "chrome"}):
            allowed = await client.post(
                "/api/system/open-browser",
                json={"url": "https://www.tiktok.com/v2/auth/authorize/?client_key=abc"},
            )
        assert allowed.status_code == 200
        assert allowed.json()["success"] is True
