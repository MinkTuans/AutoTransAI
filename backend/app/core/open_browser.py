"""Open OAuth URLs in Google Chrome, not inside the desktop app window."""

from __future__ import annotations

import os
import shutil
import subprocess
from urllib.parse import urlparse

ALLOWED_OAUTH_HOSTS = {
    "accounts.google.com",
    "www.tiktok.com",
    "tiktok.com",
}

ALLOWED_OAUTH_PATH_PREFIXES = (
    "/o/oauth2/",
    "/o/oauth2/auth",
    "/signin/oauth/",
    "/v2/auth/authorize",
    "/auth/authorize",
)


def is_allowed_oauth_url(url: str) -> bool:
    """Only Google / TikTok authorization pages may be launched externally."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
    except Exception:
        return False
    if parsed.scheme != "https":
        return False
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_OAUTH_HOSTS:
        return False
    path = parsed.path or "/"
    return any(path.startswith(prefix) for prefix in ALLOWED_OAUTH_PATH_PREFIXES)


def resolve_chrome_path() -> str | None:
    """Locate Google Chrome. Do not fall back to the in-app Edge --app profile."""
    env_path = os.environ.get("CHROME_PATH") or os.environ.get("GOOGLE_CHROME_BIN")
    candidates = [
        env_path,
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chrome"),
        shutil.which("chrome.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def chrome_launch_command(url: str, chrome_path: str) -> list[str]:
    return [chrome_path, "--new-tab", url]


def open_oauth_in_chrome(url: str) -> dict:
    """Launch an allowlisted OAuth URL as a new Google Chrome tab."""
    if not is_allowed_oauth_url(url):
        raise ValueError("URL này không được phép mở ngoài app (chỉ Google/TikTok OAuth).")

    chrome_path = resolve_chrome_path()
    if not chrome_path:
        raise FileNotFoundError(
            "Không tìm thấy Google Chrome. Cài Chrome rồi thử lại — không mở OAuth trong cửa sổ app."
        )

    cmd = chrome_launch_command(url, chrome_path)
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {"ok": True, "browser": "chrome", "url": url}


def oauth_done_html(platform: str, ok: bool, detail: str = "") -> str:
    title = f"Đã kết nối {platform}" if ok else f"Không kết nối được {platform}"
    color = "#16a34a" if ok else "#dc2626"
    extra = f"<p style='color:#64748b'>{detail}</p>" if detail else ""
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background:#0f172a; color:#e2e8f0;
           display:flex; align-items:center; justify-content:center; min-height:100vh; margin:0; }}
    .card {{ background:#1e293b; border-radius:16px; padding:2rem 2.4rem; max-width:420px; text-align:center; }}
    h1 {{ color:{color}; font-size:1.25rem; margin:0 0 0.75rem; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{title}</h1>
    <p>Bạn có thể đóng tab Chrome này và quay lại AutoTransAI.</p>
    {extra}
  </div>
</body>
</html>"""
