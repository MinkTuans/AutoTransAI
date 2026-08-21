"""
Video Page URL Source Adapter.

Handles video web pages (YouTube, Vimeo, TikTok, Google Drive, Dropbox, etc.).
Uses yt-dlp or native stream extractors when legally allowed and available.
Fails cleanly with clear messages if access is restricted, DRM protected, or private.
"""

from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from urllib.parse import urlparse

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
}


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
        return domain.capitalize()

    async def get_metadata(self, url: str) -> Dict[str, Any]:
        """Fetch metadata for video page URL using yt-dlp or head check."""
        safe_url = validate_url_security(url)
        parsed = urlparse(safe_url)
        domain = parsed.netloc.split(":")[0]
        source_display = self._get_domain_display(domain)

        yt_dlp_bin = _get_yt_dlp_executable()
        if not yt_dlp_bin:
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
            safe_url,
        ]

        try:
            res = await safe_subprocess_run_async(cmd, timeout=20)
            if res.returncode != 0:
                err_text = (res.stderr or "").lower()
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

        cmd = [
            yt_dlp_bin,
            "-f", "b[ext=mp4]/best[ext=mp4]/best",
            "--no-playlist",
            "-o", str(output_path),
            "--max-filesize", f"{settings.VIDEO_MAX_SIZE_MB}M",
            safe_url,
        ]

        res = await safe_subprocess_run_async(cmd, timeout=settings.VIDEO_DOWNLOAD_TIMEOUT)
        if res.returncode != 0 or not output_path.exists():
            err_text = (res.stderr or "").lower()
            if "private" in err_text or "login" in err_text or "drm" in err_text:
                raise ValueError("Nguồn này không thể được xử lý trực tiếp (bị khóa quyền truy cập hoặc DRM).")
            raise ValueError(f"Không thể download video từ {source_display}: {res.stderr[:200] if res.stderr else 'Lỗi không xác định'}")

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
