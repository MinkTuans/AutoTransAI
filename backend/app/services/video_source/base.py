"""
Base Video Source Adapter interface.

Defines the contract for all video source adapters (Direct URL, YouTube, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Optional, Dict, Any


class BaseVideoSourceAdapter(ABC):
    """Abstract Base Class for Video Source Adapters."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human readable source name (e.g., 'Direct Video URL', 'YouTube')."""
        pass

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Return True if this adapter can handle the given URL."""
        pass

    @abstractmethod
    async def get_metadata(self, url: str) -> Dict[str, Any]:
        """
        Validate URL and return video metadata dictionary.

        Expected return structure:
        {
            "source": str,
            "title": str,
            "duration": float,
            "width": int,
            "height": int,
            "format": str,
            "file_size": int or None,
            "audio_available": bool,
            "url": str,
        }
        """
        pass

    @abstractmethod
    async def download(
        self,
        url: str,
        output_path: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Stream download video to local path without loading entire file into memory.

        Calls progress_callback(downloaded_bytes, total_bytes) if provided.
        """
        pass
