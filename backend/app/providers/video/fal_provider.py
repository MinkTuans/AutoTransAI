"""
fal.ai Video Aggregator Provider implementation.

Calls the official fal.ai queue API to generate videos from text prompts.
Integrates KeyManager for multi-key failover rotation and detailed error tracking.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import httpx

from app.config import get_settings
from app.core import get_logger
from app.services.key_manager import get_key_manager
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
        key_mgr = get_key_manager()
        active_key = await key_mgr.get_active_key(self.provider_id)
        return active_key is not None

    async def generate_video(
        self,
        prompt: str,
        duration: int,
        output_path: Path,
    ) -> GenerationResult:
        key_mgr = get_key_manager()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dur = min(duration, self.max_duration_seconds)
        submit_url = "https://queue.fal.run/fal-ai/hunyuan-video"
        payload = {
            "prompt": prompt,
            "seconds_total": dur,
            "aspect_ratio": "16:9",
        }

        max_attempts = 3
        last_error = ""
        last_error_code = "GENERATION_FAILED"

        for attempt in range(max_attempts):
            key_entry = await key_mgr.get_active_key(self.provider_id)
            if not key_entry:
                msg = "Tất cả API Key của fal.ai đều hết dung lượng / invalid. Vui lòng chuyển sang 'Local AI & FFmpeg Generator' hoặc thêm API Key mới."
                logger.error("No active API keys available for fal.ai", prompt_preview=prompt[:40])
                return GenerationResult(
                    success=False,
                    error_message=msg,
                    error_code="ALL_KEYS_EXHAUSTED",
                    provider_id=self.provider_id,
                )

            headers = {
                "Authorization": f"Key {key_entry.api_key}",
                "Content-Type": "application/json",
            }

            logger.info(
                f"[VIDEO] Segment generation attempt {attempt + 1}/{max_attempts}",
                provider="fal",
                key_id=key_entry.key_id,
                masked_key=key_entry.masked_key,
            )

            try:
                async with httpx.AsyncClient(timeout=180.0) as client:
                    # 1. Submit request
                    res = await client.post(submit_url, json=payload, headers=headers)
                    if res.status_code not in (200, 202):
                        err_text = res.text
                        if "balance" in err_text.lower() or res.status_code in (402, 403, 429):
                            err_msg = f"HTTP {res.status_code} - Account balance empty / Rate Limit"
                        else:
                            err_msg = f"HTTP {res.status_code} - fal.ai submit error: {res.text[:150]}"

                        action_text = await key_mgr.report_result(
                            self.provider_id,
                            key_entry.key_id,
                            success=False,
                            status_code=res.status_code,
                            error_message=err_msg,
                        )
                        logger.error(
                            "fal.ai HTTP submit error",
                            key=key_entry.masked_key,
                            status_code=res.status_code,
                            action=action_text,
                        )
                        last_error = f"{err_msg} | Key: {key_entry.masked_key} | Action: {action_text}"
                        last_error_code = f"HTTP_{res.status_code}"

                        if res.status_code == 400:
                            break
                        continue

                    submit_data = res.json()
                    request_id = submit_data.get("request_id")
                    status_url = submit_data.get("status_url") or f"{submit_url}/requests/{request_id}/status"
                    response_url = submit_data.get("response_url") or f"{submit_url}/requests/{request_id}"

                    # 2. Poll status until completed
                    max_polls = 60
                    video_url = None

                    for _ in range(max_polls):
                        await asyncio.sleep(3.0)
                        status_res = await client.get(status_url, headers=headers)
                        if status_res.status_code == 200:
                            s_data = status_res.json()
                            status_str = s_data.get("status")
                            if status_str == "COMPLETED":
                                break
                            elif status_str == "FAILED":
                                fail_msg = s_data.get('error') or 'fal task failed'
                                await key_mgr.report_result(
                                    self.provider_id,
                                    key_entry.key_id,
                                    success=False,
                                    status_code=200,
                                    error_message=fail_msg,
                                )
                                last_error = f"fal.ai generation failed: {fail_msg} | Key: {key_entry.masked_key}"
                                last_error_code = "TASK_FAILED"
                                break

                    # 3. Fetch final result
                    result_res = await client.get(response_url, headers=headers)
                    if result_res.status_code == 200:
                        res_data = result_res.json()
                        video_info = res_data.get("video", {}) or res_data.get("images", [{}])[0]
                        video_url = video_info.get("url")

                    if not video_url:
                        if not last_error:
                            last_error = f"fal.ai task timed out or missing video URL | Key: {key_entry.masked_key}"
                            last_error_code = "MISSING_VIDEO_URL"
                        continue

                    # 4. Download video file
                    video_dl_res = await client.get(video_url)
                    if video_dl_res.status_code != 200:
                        last_error = f"Failed to download video file HTTP {video_dl_res.status_code}"
                        last_error_code = "DOWNLOAD_FAILED"
                        continue

                    output_path.write_bytes(video_dl_res.content)
                    if not output_path.exists() or output_path.stat().st_size == 0:
                        last_error = "Downloaded video file on disk is empty or 0 bytes"
                        last_error_code = "FILE_WRITE_ERROR"
                        continue

                    # Success!
                    await key_mgr.report_result(self.provider_id, key_entry.key_id, success=True)
                    logger.info(
                        "fal.ai video generated successfully",
                        key=key_entry.masked_key,
                        request_id=request_id,
                        size=output_path.stat().st_size,
                    )
                    return GenerationResult(
                        success=True,
                        file_path=output_path,
                        duration=float(dur),
                        provider_id=self.provider_id,
                        metadata={"key_used": key_entry.masked_key, "request_id": request_id},
                    )

            except Exception as e:
                err_str = str(e)
                action_text = await key_mgr.report_result(
                    self.provider_id,
                    key_entry.key_id,
                    success=False,
                    status_code=500,
                    error_message=err_str,
                )
                logger.error("fal.ai attempt failed with exception", key=key_entry.masked_key, error=err_str)
                last_error = f"Exception: {err_str} | Key: {key_entry.masked_key}"
                last_error_code = "GENERATION_EXCEPTION"

        return GenerationResult(
            success=False,
            error_message=last_error or "fal.ai video generation failed after retries",
            error_code=last_error_code,
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
        key_mgr = get_key_manager()
        keys = await key_mgr.get_keys_for_provider(self.provider_id)
        if not keys:
            return [QuotaInfo(resource_type="video_seconds", used=0, limit=0, remaining=0, unit="seconds")]
        
        tot_requests = sum(k.get("total_requests", 0) for k in keys)
        tot_success = sum(k.get("successful_requests", 0) for k in keys)
        return [
            QuotaInfo(
                resource_type="video_seconds",
                used=tot_success * 5,
                limit=None,
                remaining=None,
                unit="seconds",
            )
        ]
