"""
fal.ai Video Aggregator Provider implementation.

Calls the official fal.ai queue API to generate videos from text prompts.
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


class FalVideoProvider(VideoProvider):
    """fal.ai Video Generation Aggregator Provider."""

    @property
    def provider_id(self) -> str:
        return "fal"

    @property
    def provider_name(self) -> str:
        return "fal.ai (Hunyuan / LTX-2)"

    @property
    def is_free(self) -> bool:
        return False

    @property
    def requires_api_key(self) -> bool:
        return True

    @property
    def max_duration_seconds(self) -> int:
        return 10

    @property
    def supported_durations(self) -> list[int]:
        return [5, 8, 10]

    async def validate_configuration(self) -> bool:
        if not settings.FAL_API_KEY:
            return False
        try:
            headers = {"Authorization": f"Key {settings.FAL_API_KEY}"}
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get("https://rest.alpha.fal.ai/tokens/", headers=headers)
                return res.status_code in (200, 400, 404)  # Key is authorized
        except Exception as e:
            logger.warning("fal.ai validation check failed", error=str(e))
            return False

    async def generate_video(
        self,
        prompt: str,
        duration: int,
        output_path: Path,
    ) -> GenerationResult:
        if not settings.FAL_API_KEY:
            return GenerationResult(
                success=False,
                error_message="FAL_API_KEY not set in .env",
                error_code="API_KEY_MISSING",
                provider_id=self.provider_id,
            )

        headers = {
            "Authorization": f"Key {settings.FAL_API_KEY}",
            "Content-Type": "application/json",
        }
        submit_url = "https://queue.fal.run/fal-ai/hunyuan-video"
        payload = {
            "prompt": prompt,
            "seconds_total": min(duration, self.max_duration_seconds),
            "aspect_ratio": "16:9",
        }

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            async with httpx.AsyncClient(timeout=180.0) as client:
                # 1. Submit request
                res = await client.post(submit_url, json=payload, headers=headers)
                if res.status_code not in (200, 202):
                    err_text = res.text
                    if "balance" in err_text.lower() or res.status_code in (402, 403, 429):
                        err_msg = "Tài khoản fal.ai đã hết số dư (Exhausted balance). Vui lòng chuyển sang chọn 'Local FFmpeg Generator' để tạo video hoàn toàn miễn phí."
                    else:
                        err_msg = f"fal.ai API submit error HTTP {res.status_code}: {res.text[:200]}"
                    logger.error(err_msg)
                    return GenerationResult(
                        success=False,
                        error_message=err_msg,
                        error_code=f"HTTP_{res.status_code}",
                        provider_id=self.provider_id,
                    )

                submit_data = res.json()
                request_id = submit_data.get("request_id")
                status_url = submit_data.get("status_url") or f"{submit_url}/requests/{request_id}/status"
                response_url = submit_data.get("response_url") or f"{submit_url}/requests/{request_id}"

                # 2. Poll status until completed
                max_polls = 60
                for _ in range(max_polls):
                    await asyncio.sleep(3.0)
                    status_res = await client.get(status_url, headers=headers)
                    if status_res.status_code == 200:
                        s_data = status_res.json()
                        status_str = s_data.get("status")
                        if status_str == "COMPLETED":
                            break
                        elif status_str == "FAILED":
                            return GenerationResult(
                                success=False,
                                error_message=f"fal.ai generation task failed: {s_data.get('error')}",
                                error_code="TASK_FAILED",
                                provider_id=self.provider_id,
                            )

                # 3. Fetch final result
                result_res = await client.get(response_url, headers=headers)
                if result_res.status_code != 200:
                    return GenerationResult(
                        success=False,
                        error_message=f"Failed to fetch fal.ai result HTTP {result_res.status_code}",
                        error_code="RESULT_FETCH_FAILED",
                        provider_id=self.provider_id,
                    )

                res_data = result_res.json()
                video_info = res_data.get("video", {}) or res_data.get("images", [{}])[0]
                video_url = video_info.get("url")

                if not video_url:
                    return GenerationResult(
                        success=False,
                        error_message="fal.ai response did not contain video URL",
                        error_code="MISSING_VIDEO_URL",
                        provider_id=self.provider_id,
                    )

                # 4. Download video file
                video_dl_res = await client.get(video_url)
                if video_dl_res.status_code != 200:
                    return GenerationResult(
                        success=False,
                        error_message=f"Failed to download video file HTTP {video_dl_res.status_code}",
                        error_code="DOWNLOAD_FAILED",
                        provider_id=self.provider_id,
                    )

                output_path.write_bytes(video_dl_res.content)

                if not output_path.exists() or output_path.stat().st_size == 0:
                    return GenerationResult(
                        success=False,
                        error_message="Downloaded video file is missing or 0 bytes",
                        error_code="FILE_WRITE_ERROR",
                        provider_id=self.provider_id,
                    )

                logger.info(
                    "fal.ai video generated successfully",
                    request_id=request_id,
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
            logger.error("fal.ai generation failed", error=str(e))
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
