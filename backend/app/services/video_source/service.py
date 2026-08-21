"""
Video Source Service.

Unified service that manages video adapters, URL resolution, caching,
metadata extraction, streaming downloads, and local file imports.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List
from urllib.parse import urlparse

from app.config import get_settings
from app.core import get_logger
from app.core.security_url import validate_url_security, SSRFValidationError
from app.media.ffprobe import get_video_metadata_async
from app.services.video_source.base import BaseVideoSourceAdapter
from app.services.video_source.direct_url_adapter import DirectURLAdapter
from app.services.video_source.page_url_adapter import PageURLAdapter

logger = get_logger(__name__)
settings = get_settings()


class VideoSourceService:
    """Service for resolving and downloading video assets from URLs or local uploads."""

    def __init__(self):
        self.adapters: List[BaseVideoSourceAdapter] = [
            DirectURLAdapter(),
            PageURLAdapter(),
        ]

    def register_adapter(self, adapter: BaseVideoSourceAdapter) -> None:
        """Register a custom video source adapter."""
        self.adapters.insert(0, adapter)

    def resolve_adapter(self, url: str) -> BaseVideoSourceAdapter:
        """
        Find the matching adapter for a URL or raise ValueError if unsupported.
        """
        if not url or not isinstance(url, str):
            raise ValueError("URL không hợp lệ.")

        # Pre-validate security / SSRF
        validate_url_security(url)

        for adapter in self.adapters:
            if adapter.can_handle(url):
                return adapter

        raise ValueError("Nguồn video này hiện chưa được hỗ trợ.")

    def get_url_hash(self, url: str) -> str:
        """Compute SHA256 hash of URL for cache keying."""
        return hashlib.sha256(url.strip().encode("utf-8")).hexdigest()[:16]

    async def get_metadata(self, url: str) -> Dict[str, Any]:
        """
        Validate URL and fetch video metadata without downloading full video.
        """
        adapter = self.resolve_adapter(url)
        metadata = await adapter.get_metadata(url)
        return metadata

    async def download_video(
        self,
        url: str,
        output_dir: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Download video from URL with caching support and size limits.
        """
        adapter = self.resolve_adapter(url)
        url_hash = self.get_url_hash(url)
        output_dir.mkdir(parents=True, exist_ok=True)
        cached_file = output_dir / f"url_video_{url_hash}.mp4"

        # Check Cache
        if cached_file.exists() and cached_file.stat().st_size > 0:
            logger.info("Using cached video asset", hash=url_hash, path=str(cached_file))
            meta = await get_video_metadata_async(cached_file)
            parsed = urlparse(url)
            return {
                "source": adapter.source_name,
                "domain": parsed.netloc,
                "title": f"Video ({url_hash})",
                "duration": meta["duration"],
                "width": meta["width"],
                "height": meta["height"],
                "format": meta["format"],
                "file_size": cached_file.stat().st_size,
                "audio_available": meta["has_audio"],
                "local_path": str(cached_file),
                "mime_type": "video/mp4",
            }

        # Download via adapter
        result = await adapter.download(url, cached_file, progress_callback)
        return result

    async def import_uploaded_file(
        self,
        source_path: Path,
        original_filename: str,
        output_dir: Path,
    ) -> Dict[str, Any]:
        """
        Import a locally uploaded video file into the project storage.
        """
        if not source_path.exists():
            raise FileNotFoundError(f"File upload không tồn tại: {source_path}")

        file_size = source_path.stat().st_size
        max_bytes = settings.VIDEO_MAX_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise ValueError(
                f"File upload ({file_size / (1024*1024):.1f}MB) vượt quá dung lượng tối đa ({settings.VIDEO_MAX_SIZE_MB}MB)."
            )

        output_dir.mkdir(parents=True, exist_ok=True)
        ext = Path(original_filename).suffix or ".mp4"
        dest_filename = f"upload_{Path(original_filename).stem}_{source_path.name[:8]}{ext}"
        dest_path = output_dir / dest_filename

        if source_path.resolve() != dest_path.resolve():
            shutil.copy2(source_path, dest_path)

        meta = await get_video_metadata_async(dest_path)
        max_duration_sec = settings.VIDEO_MAX_DURATION_MINUTES * 60
        if meta.get("duration", 0.0) > max_duration_sec:
            dest_path.unlink(missing_ok=True)
            raise ValueError(
                f"Thời lượng video upload ({meta['duration']/60:.1f} phút) vượt quá giới hạn ({settings.VIDEO_MAX_DURATION_MINUTES} phút)."
            )

        return {
            "source": "Local Upload",
            "domain": "local",
            "title": Path(original_filename).stem,
            "duration": meta["duration"],
            "width": meta["width"],
            "height": meta["height"],
            "format": meta["format"],
            "file_size": dest_path.stat().st_size,
            "audio_available": meta["has_audio"],
            "local_path": str(dest_path),
            "mime_type": f"video/{meta['format']}",
        }


# Singleton service instance
_video_source_service = VideoSourceService()


def get_video_source_service() -> VideoSourceService:
    """Get global VideoSourceService instance."""
    return _video_source_service
