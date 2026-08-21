"""
Direct Video URL Source Adapter.

Handles direct media files (MP4, WEBM, MOV, MKV, AVI, etc.) accessible over HTTP/HTTPS.
Implements SSRF protection, streaming download, and file size limits.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional, Dict, Any
from urllib.parse import urlparse
import httpx

from app.config import get_settings
from app.core import get_logger
from app.core.security_url import validate_url_security, safe_http_head_or_get, SSRFValidationError
from app.media.ffprobe import get_video_metadata_async
from app.services.video_source.base import BaseVideoSourceAdapter

logger = get_logger(__name__)
settings = get_settings()

DIRECT_EXTENSIONS = {".mp4", ".webm", ".mov", ".mkv", ".avi", ".flv", ".m4v", ".ts", ".3gp"}


class DirectURLAdapter(BaseVideoSourceAdapter):
    """Adapter for direct video URL endpoints."""

    @property
    def source_name(self) -> str:
        return "Direct Video URL"

    def can_handle(self, url: str) -> bool:
        if not url or not isinstance(url, str):
            return False
        try:
            parsed = urlparse(url.strip())
            if parsed.scheme.lower() not in ("http", "https"):
                return False
            path = parsed.path.lower()
            return any(path.endswith(ext) for ext in DIRECT_EXTENSIONS)
        except Exception:
            return False

    async def get_metadata(self, url: str) -> Dict[str, Any]:
        """Validate URL, perform SSRF check, check Content-Length & Content-Type."""
        safe_url = validate_url_security(url)

        timeout = httpx.Timeout(15.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            res = await safe_http_head_or_get(client, safe_url)
            if res.status_code >= 400:
                raise ValueError(f"Không thể truy cập URL (HTTP {res.status_code}). Video không tồn tại hoặc bị chặn.")

            content_type = res.headers.get("Content-Type", "").lower()
            content_length = res.headers.get("Content-Length")
            file_size = int(content_length) if content_length and content_length.isdigit() else None

            # Check max size limit if header present
            max_bytes = settings.VIDEO_MAX_SIZE_MB * 1024 * 1024
            if file_size and file_size > max_bytes:
                raise ValueError(
                    f"Dung lượng video ({file_size / (1024*1024):.1f}MB) vượt quá giới hạn tối đa ({settings.VIDEO_MAX_SIZE_MB}MB)."
                )

            # Derive title from filename or host
            parsed = urlparse(safe_url)
            filename = Path(parsed.path).name or "video.mp4"
            title = Path(filename).stem or "Direct Video"

            return {
                "source": "Direct URL",
                "domain": parsed.netloc,
                "title": title,
                "duration": 0.0,
                "width": 0,
                "height": 0,
                "format": Path(filename).suffix.lstrip(".").lower() or "mp4",
                "file_size": file_size,
                "audio_available": True,
                "url": safe_url,
                "mime_type": content_type or "video/mp4",
            }

    async def download(
        self,
        url: str,
        output_path: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, Any]:
        """Stream download direct video file with size enforcement."""
        safe_url = validate_url_security(url)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        max_bytes = settings.VIDEO_MAX_SIZE_MB * 1024 * 1024
        download_timeout = settings.VIDEO_DOWNLOAD_TIMEOUT

        timeout = httpx.Timeout(download_timeout, connect=10.0)

        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            # SSRF check on final target
            validate_url_security(safe_url)
            async with client.stream("GET", safe_url) as response:
                if response.status_code >= 400:
                    raise ValueError(f"Không thể download video (HTTP {response.status_code}).")

                total_bytes = int(response.headers.get("Content-Length", 0))
                if total_bytes > max_bytes:
                    raise ValueError(f"Video lớn hơn giới hạn cho phép ({settings.VIDEO_MAX_SIZE_MB}MB).")

                downloaded_bytes = 0
                with open(output_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=65536):
                        downloaded_bytes += len(chunk)
                        if downloaded_bytes > max_bytes:
                            output_path.unlink(missing_ok=True)
                            raise ValueError(
                                f"Đã dừng download: Dung lượng file vượt quá giới hạn ({settings.VIDEO_MAX_SIZE_MB}MB)."
                            )
                        f.write(chunk)
                        if progress_callback:
                            try:
                                progress_callback(downloaded_bytes, total_bytes)
                            except Exception:
                                pass

        # Probe downloaded file metadata
        try:
            meta = await get_video_metadata_async(output_path)
        except Exception as e:
            logger.warning("Failed probing downloaded video metadata", error=str(e))
            meta = {
                "duration": 0.0,
                "width": 0,
                "height": 0,
                "format": output_path.suffix.lstrip(".").lower() or "mp4",
                "file_size": output_path.stat().st_size,
                "has_audio": True,
            }

        # Check duration limit
        max_duration_sec = settings.VIDEO_MAX_DURATION_MINUTES * 60
        if meta.get("duration", 0.0) > max_duration_sec:
            output_path.unlink(missing_ok=True)
            raise ValueError(
                f"Thời lượng video ({meta['duration']/60:.1f} phút) vượt quá giới hạn tối đa ({settings.VIDEO_MAX_DURATION_MINUTES} phút)."
            )

        parsed = urlparse(safe_url)
        return {
            "source": "Direct URL",
            "domain": parsed.netloc,
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
