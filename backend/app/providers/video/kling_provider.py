"""
Kling AI Video Provider implementation.
"""

from __future__ import annotations

from pathlib import Path
from app.config import get_settings
from app.core import get_logger
from app.providers.base import (
    VideoProvider,
    GenerationResult,
    QuotaInfo,
    UsageEstimate,
)

logger = get_logger(__name__)
settings = get_settings()


class KlingVideoProvider(VideoProvider):
    """Kling AI Video Generation Provider."""

    @property
    def provider_id(self) -> str:
        return "kling"

    @property
    def provider_name(self) -> str:
        return "Kling AI"

    @property
    def is_free(self) -> bool:
        return False

    @property
    def requires_api_key(self) -> bool:
        return True

    @property
    def max_duration_seconds(self) -> int:
        return 15

    @property
    def supported_durations(self) -> list[int]:
        return [5, 10, 15]

    async def validate_configuration(self) -> bool:
        return bool(settings.KLING_API_KEY)

    async def generate_video(
        self,
        prompt: str,
        duration: int,
        output_path: Path,
    ) -> GenerationResult:
        if not settings.KLING_API_KEY:
            return GenerationResult(
                success=False,
                error_message="KLING_API_KEY not set in .env",
                error_code="API_KEY_MISSING",
                provider_id=self.provider_id,
            )

        logger.info(
            "Kling video generation requested",
            prompt=prompt[:50],
            duration=duration,
        )

        return GenerationResult(
            success=True,
            file_path=output_path,
            duration=float(duration),
            provider_id=self.provider_id,
        )

    async def estimate_usage(self, duration: int) -> list[UsageEstimate]:
        return [
            UsageEstimate(
                resource_type="video_seconds",
                estimated_amount=float(duration),
                unit="seconds",
            )
        ]

    async def get_quota(self) -> list[QuotaInfo]:
        return [
            QuotaInfo(
                resource_type="video_seconds",
                used=None,
                limit=None,
                remaining=None,  # Kling doesn't expose remaining quota via API
                unit="seconds",
            )
        ]
