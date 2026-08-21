"""
Kling AI Video Provider implementation.

Calls the official Kling AI API to generate videos from text prompts.
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
        submit_url = "https://api.klingai.com/v1/videos/text2video"

        payload = {
            "model_name": "kling-v1",
            "prompt": prompt,
            "duration": str(dur),
            "aspect_ratio": "16:9",
        }

        max_attempts = 3
        last_error = ""
        last_error_code = "GENERATION_FAILED"

        for attempt in range(max_attempts):
            key_entry = await key_mgr.get_active_key(self.provider_id)
            if not key_entry:
                msg = "Tất cả API Key của Kling AI đều hết dung lượng / invalid. Vui lòng chuyển sang 'Local AI & FFmpeg Generator' hoặc thêm API Key mới."
                logger.error("No active API keys available for Kling AI", prompt_preview=prompt[:40])
                return GenerationResult(
                    success=False,
                    error_message=msg,
                    error_code="ALL_KEYS_EXHAUSTED",
                    provider_id=self.provider_id,
                    metadata={"key_action": "All keys exhausted or disabled"},
                )

            headers = {
                "Authorization": f"Bearer {key_entry.api_key}",
                "Content-Type": "application/json",
            }

            logger.info(
                f"[VIDEO] Segment generation attempt {attempt + 1}/{max_attempts}",
                provider="kling",
                key_id=key_entry.key_id,
                masked_key=key_entry.masked_key,
            )

            try:
                async with httpx.AsyncClient(timeout=180.0) as client:
                    # 1. Create text2video task
                    res = await client.post(submit_url, json=payload, headers=headers)
                    if res.status_code != 200:
                        err_text = res.text
                        if "balance" in err_text.lower() or res.status_code in (402, 403, 429):
                            err_msg = f"HTTP {res.status_code} - Account balance empty / Rate Limit"
                        else:
                            err_msg = f"HTTP {res.status_code} - Kling AI API error: {res.text[:150]}"

                        action_text = await key_mgr.report_result(
                            self.provider_id,
                            key_entry.key_id,
                            success=False,
                            status_code=res.status_code,
                            error_message=err_msg,
                        )
                        logger.error(
                            "Kling AI HTTP submit error",
                            key=key_entry.masked_key,
                            status_code=res.status_code,
                            action=action_text,
                        )
                        last_error = f"{err_msg} | Key: {key_entry.masked_key} | Action: {action_text}"
                        last_error_code = f"HTTP_{res.status_code}"

                        # If request parameters invalid (HTTP 400), break immediately without rotating key
                        if res.status_code == 400:
                            break
                        continue

                    data = res.json()
                    if data.get("code") != 0:
                        err_msg = f"Kling AI code {data.get('code')}: {data.get('message')}"
                        action_text = await key_mgr.report_result(
                            self.provider_id,
                            key_entry.key_id,
                            success=False,
                            status_code=200,
                            error_message=err_msg,
                        )
                        last_error = f"{err_msg} | Key: {key_entry.masked_key}"
                        last_error_code = "API_ERROR"
                        continue

                    task_id = data.get("data", {}).get("task_id")
                    if not task_id:
                        last_error = f"Response missing task_id | Key: {key_entry.masked_key}"
                        last_error_code = "MISSING_TASK_ID"
                        continue

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
                                fail_msg = p_data.get('task_status_msg') or 'Task failed'
                                await key_mgr.report_result(
                                    self.provider_id,
                                    key_entry.key_id,
                                    success=False,
                                    status_code=200,
                                    error_message=fail_msg,
                                )
                                last_error = f"Kling task failed: {fail_msg} | Key: {key_entry.masked_key}"
                                last_error_code = "TASK_FAILED"
                                break

                    if not video_url:
                        if not last_error:
                            last_error = f"Kling AI task timed out | Key: {key_entry.masked_key}"
                            last_error_code = "TIMEOUT_NO_URL"
                        continue

                    # 3. Download video file
                    dl_res = await client.get(video_url)
                    if dl_res.status_code != 200:
                        last_error = f"Failed to download video file HTTP {dl_res.status_code}"
                        last_error_code = "DOWNLOAD_FAILED"
                        continue

                    output_path.write_bytes(dl_res.content)
                    if not output_path.exists() or output_path.stat().st_size == 0:
                        last_error = "Downloaded video file on disk is empty or 0 bytes"
                        last_error_code = "FILE_WRITE_ERROR"
                        continue

                    # Success!
                    await key_mgr.report_result(self.provider_id, key_entry.key_id, success=True)
                    logger.info(
                        "Kling AI video generated successfully",
                        key=key_entry.masked_key,
                        task_id=task_id,
                        size=output_path.stat().st_size,
                    )
                    return GenerationResult(
                        success=True,
                        file_path=output_path,
                        duration=float(dur),
                        provider_id=self.provider_id,
                        metadata={"key_used": key_entry.masked_key, "task_id": task_id},
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
                logger.error("Kling AI attempt failed with exception", key=key_entry.masked_key, error=err_str)
                last_error = f"Exception: {err_str} | Key: {key_entry.masked_key}"
                last_error_code = "GENERATION_EXCEPTION"

        return GenerationResult(
            success=False,
            error_message=last_error or "Kling AI video generation failed after retries",
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
        
        # Summary of local request stats across keys
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
