"""
Video Page URL Source Adapter.

Handles video web pages (YouTube, Vimeo, TikTok, Google Drive, Dropbox, etc.).
Uses yt-dlp or native stream extractors when legally allowed and available.
Fails cleanly with clear messages if access is restricted, DRM protected, or private.
"""

from __future__ import annotations

import asyncio
import json
import re
import shutil
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from urllib.parse import parse_qs, urlparse

import httpx

from app.config import get_settings
from app.core import get_logger
from app.core.security import safe_subprocess_run_async
from app.core.security_url import validate_url_security, SSRFValidationError
from app.media.ffprobe import get_video_metadata_async
from app.services.video_source.base import BaseVideoSourceAdapter

logger = get_logger(__name__)
settings = get_settings()

PAGE_DOMAINS = {
    "youtube.com", "youtu.be", "www.youtube.com",
    "vimeo.com", "www.vimeo.com",
    "tiktok.com", "www.tiktok.com",
    "facebook.com", "fb.watch", "www.facebook.com",
    "instagram.com", "www.instagram.com",
    "drive.google.com",
    "dropbox.com", "www.dropbox.com",
    "bilibili.com", "www.bilibili.com", "m.bilibili.com",
    "b23.tv",
}

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def _is_bilibili_domain(domain: str) -> bool:
    d = (domain or "").lower()
    return "bilibili" in d or d == "b23.tv" or d.endswith(".b23.tv")


def build_yt_dlp_download_cmd(yt_dlp_bin: str, url: str, output_path: Path) -> list[str]:
    """Build yt-dlp args. Bilibili needs browser headers + merged DASH, not mp4-only `best`."""
    parsed = urlparse(url.strip())
    domain = (parsed.netloc or "").split(":")[0]
    cmd = [
        yt_dlp_bin,
        "-f", "bv*+ba/b[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "--no-playlist",
        "-o", str(output_path),
        "--max-filesize", f"{settings.VIDEO_MAX_SIZE_MB}M",
    ]
    if _is_bilibili_domain(domain):
        cmd.extend([
            "--user-agent", BROWSER_UA,
            "--referer", "https://www.bilibili.com/",
            "--add-header", "Origin:https://www.bilibili.com",
        ])
    cmd.append(url)
    return cmd


def raise_yt_dlp_download_error(source_display: str, stderr: str | None, returncode: int | None = None) -> None:
    """Map yt-dlp stderr to a user-facing ValueError. Never raise an empty message."""
    err_text = (stderr or "").strip()
    err_lower = err_text.lower()
    if "412" in err_text or "precondition failed" in err_lower or "风控" in err_text:
        raise ValueError(
            f"Bilibili chặn tải video (HTTP 412 / anti-bot). "
            f"Cần cookie đăng nhập Bilibili hoặc thử lại từ mạng khác. "
            f"Chi tiết: {err_text[:180] or 'empty stderr'}"
        )
    if "login" in err_lower or "private" in err_lower or "drm" in err_lower or "confirm your age" in err_lower:
        raise ValueError("Nguồn này không thể được xử lý trực tiếp (yêu cầu đăng nhập, riêng tư hoặc chứa DRM).")
    snippet = err_text[:200] if err_text else "Lỗi không xác định"
    code = f" (exit {returncode})" if returncode not in (None, 0) else ""
    raise ValueError(f"Không thể download video từ {source_display}{code}: {snippet}")


_BVID_RE = re.compile(r"(BV[0-9A-Za-z]+)")


def parse_bilibili_video_ref(url: str) -> dict[str, Any] | None:
    """Extract BVID and 1-indexed part. Query `t` is a timestamp, not a page."""
    if not url or not isinstance(url, str):
        return None
    parsed = urlparse(url.strip())
    match = _BVID_RE.search(parsed.path) or _BVID_RE.search(url)
    if not match:
        return None
    query = parse_qs(parsed.query)
    page = 1
    if "p" in query:
        try:
            page = max(1, int(query["p"][0]))
        except (TypeError, ValueError):
            page = 1
    return {"bvid": match.group(1), "page": page}


def metadata_from_bilibili_pagelist(
    pages: list[dict[str, Any]],
    page: int,
    bvid: str,
) -> dict[str, Any]:
    """Map Bilibili pagelist JSON to check-url metadata. Duration is seconds."""
    if not pages:
        raise ValueError("Bilibili không trả về danh sách phần video.")
    entry = next((p for p in pages if int(p.get("page") or 0) == page), None)
    if entry is None:
        entry = pages[0]
        page = int(entry.get("page") or 1)
    duration = float(entry.get("duration") or 0.0)
    if duration <= 0:
        raise ValueError("Bilibili không trả về thời lượng video.")
    dim = entry.get("dimension") or {}
    title = (entry.get("part") or "").strip() or f"Bilibili {bvid}"
    return {
        "source": "Bilibili",
        "domain": "www.bilibili.com",
        "title": title,
        "duration": round(duration, 2),
        "width": int(dim.get("width") or 0),
        "height": int(dim.get("height") or 0),
        "format": "mp4",
        "file_size": None,
        "audio_available": True,
        "url": f"https://www.bilibili.com/video/{bvid}?p={page}",
        "mime_type": "video/mp4",
        "bvid": bvid,
        "page": page,
        "page_count": len(pages),
    }


async def fetch_bilibili_page_metadata(url: str) -> dict[str, Any]:
    """Fetch title/duration from Bilibili pagelist API (works when view API is 412)."""
    ref = parse_bilibili_video_ref(url)
    if not ref:
        raise ValueError("Không nhận diện được mã video Bilibili từ URL.")
    api = f"https://api.bilibili.com/x/player/pagelist?bvid={ref['bvid']}"
    timeout = httpx.Timeout(15.0, connect=8.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        res = await client.get(
            api,
            headers={
                "User-Agent": BROWSER_UA,
                "Referer": "https://www.bilibili.com/",
            },
        )
        if res.status_code >= 400:
            raise ValueError(f"Không lấy được metadata Bilibili (HTTP {res.status_code}).")
        payload = res.json()
    if payload.get("code") != 0 or not payload.get("data"):
        raise ValueError(
            f"Bilibili pagelist lỗi: {payload.get('message') or payload.get('code')}"
        )
    return metadata_from_bilibili_pagelist(payload["data"], ref["page"], ref["bvid"])


def _get_yt_dlp_executable() -> str | None:
    """Find yt-dlp executable in system PATH or python environment."""
    found = shutil.which("yt-dlp")
    if found:
        return found
    return None


class PageURLAdapter(BaseVideoSourceAdapter):
    """Adapter for video web page URLs."""

    @property
    def source_name(self) -> str:
        return "Video Page"

    def can_handle(self, url: str) -> bool:
        if not url or not isinstance(url, str):
            return False
        try:
            parsed = urlparse(url.strip())
            if parsed.scheme.lower() not in ("http", "https"):
                return False
            domain = parsed.netloc.lower().split(":")[0]
            # Match known domains or fallback web URLs
            if any(domain.endswith(d) for d in PAGE_DOMAINS):
                return True
            # Also handle any generic page URL (not a direct file extension)
            path = parsed.path.lower()
            return not path.endswith((".mp4", ".webm", ".mov", ".mkv", ".avi", ".flv"))
        except Exception:
            return False

    def _get_domain_display(self, domain: str) -> str:
        domain_lower = domain.lower()
        if "youtube" in domain_lower or "youtu.be" in domain_lower:
            return "YouTube"
        if "vimeo" in domain_lower:
            return "Vimeo"
        if "tiktok" in domain_lower:
            return "TikTok"
        if "facebook" in domain_lower or "fb.watch" in domain_lower:
            return "Facebook"
        if "instagram" in domain_lower:
            return "Instagram"
        if "drive.google" in domain_lower:
            return "Google Drive"
        if "dropbox" in domain_lower:
            return "Dropbox"
        if _is_bilibili_domain(domain_lower):
            return "Bilibili"
        return domain.capitalize()

    async def get_metadata(self, url: str) -> Dict[str, Any]:
        """Fetch metadata for video page URL using yt-dlp or head check."""
        safe_url = validate_url_security(url)
        parsed = urlparse(safe_url)
        domain = parsed.netloc.split(":")[0]
        source_display = self._get_domain_display(domain)

        if _is_bilibili_domain(domain):
            try:
                return await fetch_bilibili_page_metadata(safe_url)
            except Exception as bili_err:
                logger.warning("Bilibili pagelist metadata failed, falling back to yt-dlp", error=str(bili_err))

        yt_dlp_bin = _get_yt_dlp_executable()
        if not yt_dlp_bin:
            if _is_bilibili_domain(domain):
                raise ValueError(
                    "Không lấy được thời lượng Bilibili. Kiểm tra mạng hoặc cài yt-dlp."
                )
            # Fallback metadata when yt-dlp binary is not installed
            return {
                "source": source_display,
                "domain": domain,
                "title": f"Video từ {source_display}",
                "duration": 0.0,
                "width": 1920,
                "height": 1080,
                "format": "mp4",
                "file_size": None,
                "audio_available": True,
                "url": safe_url,
                "mime_type": "video/mp4",
            }

        cmd = [
            yt_dlp_bin,
            "--dump-single-json",
            "--no-playlist",
            "--skip-download",
        ]
        if _is_bilibili_domain(domain):
            cmd.extend([
                "--user-agent", BROWSER_UA,
                "--referer", "https://www.bilibili.com/",
            ])
        cmd.append(safe_url)

        try:
            res = await safe_subprocess_run_async(cmd, timeout=20, check=False)
            if res.returncode != 0:
                err_text = (res.stderr or "").lower()
                if "412" in err_text or "precondition failed" in err_text:
                    raise ValueError(
                        f"Bilibili chặn truy cập metadata (HTTP 412). Cần cookie hoặc thử lại từ mạng khác."
                    )
                if "login" in err_text or "private" in err_text or "drm" in err_text or "confirm your age" in err_text:
                    raise ValueError("Nguồn này không thể được xử lý trực tiếp (yêu cầu đăng nhập, riêng tư hoặc chứa DRM).")
                raise ValueError(f"Không thể truy cập nguồn video ({source_display}). Video có thể không tồn tại.")

            data = json.loads(res.stdout)
            title = data.get("title", "Video từ " + source_display)
            duration = float(data.get("duration") or 0.0)
            width = int(data.get("width") or 0)
            height = int(data.get("height") or 0)
            ext = data.get("ext", "mp4")

            return {
                "source": source_display,
                "domain": domain,
                "title": title,
                "duration": round(duration, 2),
                "width": width,
                "height": height,
                "format": ext,
                "file_size": data.get("filesize") or data.get("filesize_approx"),
                "audio_available": True,
                "url": safe_url,
                "mime_type": f"video/{ext}",
            }
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            logger.warning("yt-dlp metadata extraction failed", url=safe_url, error=str(e))
            if _is_bilibili_domain(domain):
                raise ValueError(f"Không lấy được metadata Bilibili: {e}") from e
            return {
                "source": source_display,
                "domain": domain,
                "title": f"Video từ {source_display}",
                "duration": 0.0,
                "width": 0,
                "height": 0,
                "format": "mp4",
                "file_size": None,
                "audio_available": True,
                "url": safe_url,
                "mime_type": "video/mp4",
            }

    async def download(
        self,
        url: str,
        output_path: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, Any]:
        """Download video page content using yt-dlp or direct stream resolution."""
        safe_url = validate_url_security(url)
        parsed = urlparse(safe_url)
        domain = parsed.netloc.split(":")[0]
        source_display = self._get_domain_display(domain)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        yt_dlp_bin = _get_yt_dlp_executable()

        if not yt_dlp_bin:
            raise ValueError(
                f"Nguồn video '{source_display}' yêu cầu bộ tải media. Vui lòng cài đặt yt-dlp hoặc sử dụng Direct MP4 URL."
            )

        cmd = build_yt_dlp_download_cmd(yt_dlp_bin, safe_url, output_path)

        res = await safe_subprocess_run_async(cmd, timeout=settings.VIDEO_DOWNLOAD_TIMEOUT, check=False)
        if res.returncode != 0 or not output_path.exists():
            raise_yt_dlp_download_error(source_display, res.stderr, res.returncode)

        # Probe metadata of downloaded file
        meta = await get_video_metadata_async(output_path)
        max_duration_sec = settings.VIDEO_MAX_DURATION_MINUTES * 60
        if meta.get("duration", 0.0) > max_duration_sec:
            output_path.unlink(missing_ok=True)
            raise ValueError(
                f"Thời lượng video ({meta['duration']/60:.1f} phút) vượt quá giới hạn tối đa ({settings.VIDEO_MAX_DURATION_MINUTES} phút)."
            )

        return {
            "source": source_display,
            "domain": domain,
            "title": output_path.stem,
            "duration": meta["duration"],
            "width": meta["width"],
            "height": meta["height"],
            "format": meta["format"],
            "file_size": output_path.stat().st_size,
            "audio_available": meta["has_audio"],
            "local_path": str(output_path),
            "mime_type": "video/mp4",
        }
