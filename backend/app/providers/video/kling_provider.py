"""
Kling AI Video Provider implementation.

Calls the official Kling AI API to generate videos from text prompts.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import httpx

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

        headers = {
            "Authorization": f"Bearer {settings.KLING_API_KEY}",
            "Content-Type": "application/json",
        }
        submit_url = "https://api.klingai.com/v1/videos/text2video"
        payload = {
            "model_name": "kling-v1",
            "prompt": prompt,
            "duration": str(min(duration, self.max_duration_seconds)),
            "aspect_ratio": "16:9",
        }

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            async with httpx.AsyncClient(timeout=180.0) as client:
                # 1. Create text2video task
                res = await client.post(submit_url, json=payload, headers=headers)
                if res.status_code != 200:
                    err_text = res.text
                    if "balance" in err_text.lower() or res.status_code in (402, 403, 429):
                        err_msg = "Tài khoản Kling AI đã hết số dư (Account balance not enough). Vui lòng chuyển sang chọn 'Local FFmpeg Generator' để tạo video hoàn toàn miễn phí."
                    else:
                        err_msg = f"Kling AI API error HTTP {res.status_code}: {res.text[:200]}"
                    logger.error(err_msg)
                    return GenerationResult(
                        success=False,
                        error_message=err_msg,
                        error_code=f"HTTP_{res.status_code}",
                        provider_id=self.provider_id,
                    )

                data = res.json()
                if data.get("code") != 0:
                    return GenerationResult(
                        success=False,
                        error_message=f"Kling AI error code {data.get('code')}: {data.get('message')}",
                        error_code="API_ERROR",
                        provider_id=self.provider_id,
                    )

                task_id = data.get("data", {}).get("task_id")
                if not task_id:
                    return GenerationResult(
                        success=False,
                        error_message="Kling AI response missing task_id",
                        error_code="MISSING_TASK_ID",
                        provider_id=self.provider_id,
                    )

                # 2. Poll task status
                task_url = f"https://api.klingai.com/v1/videos/text2video/{task_id}"
                max_polls = 60
                video_url = None

                for _ in range(max_polls):
                    await asyncio.sleep(4.0)
                    poll_res = await client.get(task_url, headers=headers)
                    if poll_res.status_code == 200:
                        p_data = poll_res.json().get("data", {})
                        status_str = p_data.get("task_status")
                        if status_str == "succeed":
                            videos = p_data.get("task_result", {}).get("videos", [])
                            if videos:
                                video_url = videos[0].get("url")
                            break
                        elif status_str == "failed":
                            return GenerationResult(
                                success=False,
                                error_message=f"Kling task failed: {p_data.get('task_status_msg')}",
                                error_code="TASK_FAILED",
                                provider_id=self.provider_id,
                            )

                if not video_url:
                    return GenerationResult(
                        success=False,
                        error_message="Kling AI task timed out or returned no video URL",
                        error_code="TIMEOUT_NO_URL",
                        provider_id=self.provider_id,
                    )

                # 3. Download video file
                dl_res = await client.get(video_url)
                if dl_res.status_code != 200:
                    return GenerationResult(
                        success=False,
                        error_message=f"Failed to download Kling video HTTP {dl_res.status_code}",
                        error_code="DOWNLOAD_FAILED",
                        provider_id=self.provider_id,
                    )

                output_path.write_bytes(dl_res.content)

                if not output_path.exists() or output_path.stat().st_size == 0:
                    return GenerationResult(
                        success=False,
                        error_message="Kling video file on disk is missing or 0 bytes",
                        error_code="FILE_WRITE_ERROR",
                        provider_id=self.provider_id,
                    )

                logger.info(
                    "Kling AI video generated successfully",
                    task_id=task_id,
                    size=output_path.stat().st_size,
                    output_path=str(output_path),
                )
                return GenerationResult(
                    success=True,
                    file_path=output_path,
                    duration=float(duration),
                    provider_id=self.provider_id,
                )

        except Exception as e:
            logger.error("Kling AI generation failed", error=str(e))
            return GenerationResult(
                success=False,
                error_message=str(e),
                error_code="GENERATION_EXCEPTION",
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
                remaining=None,
                unit="seconds",
            )
        ]
