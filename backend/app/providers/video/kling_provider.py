"""Kling text-to-video with exact request-local model and credential."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

import httpx

from app.config import get_settings
from app.providers.base import GenerationResult, QuotaInfo, UsageEstimate, VideoProvider
from app.providers.request_target import resolve_request_target
from app.providers.video.catalog_media import (
    VideoBoundaryError, VideoRoutePending, download_video, request_json,
    validated_video_path,
)
from app.services.ai_routing import RouteTarget, UnsupportedModalityError
from app.services.key_manager import get_key_manager

settings = get_settings()
_ENDPOINT = "https://api.klingai.com/v1/videos/text2video"
_MODELS = frozenset({"kling-v2-5-turbo", "kling-v2-6", "kling-v3"})


class KlingVideoProvider(VideoProvider):
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
        return await get_key_manager().get_active_key(self.provider_id) is not None

    async def generate_video(self, prompt: str, duration: int, output_path: Path, *,
                             route_target: RouteTarget | None = None,
                             api_key: str | None = None) -> GenerationResult:
        if route_target is not None:
            model, secret = resolve_request_target(
                route_target, api_key, provider_id=self.provider_id,
                capabilities=("VIDEO_GENERATION",), legacy_model=None, legacy_key=None)
            if model not in _MODELS:
                raise UnsupportedModalityError("Video generation unsupported for this model.")
            return await self._generate(prompt, duration, output_path, model, secret, canonical=True)
        if api_key is not None:
            raise ValueError("A request credential requires a route target.")
        last = None
        for _ in range(3):
            try:
                key_entry = await get_key_manager().get_active_key(self.provider_id)
            except Exception:
                return GenerationResult(False, provider_id=self.provider_id,
                                        error_code="PROVIDER_UNAVAILABLE",
                                        error_message="Video generation failed: provider_unavailable")
            if not key_entry:
                break
            last = await self._generate(prompt, duration, output_path, "kling-v1", key_entry.api_key,
                                        canonical=False, key_id=key_entry.key_id)
            if last.success or last.error_code not in ("HTTP_401", "HTTP_402", "HTTP_403", "HTTP_429"):
                return last
        return last or GenerationResult(False, provider_id=self.provider_id, error_code="NO_API_KEY",
                                        error_message="No valid Kling API key configured.")

    async def _generate(self, prompt: str, duration: int, output_path: Path,
                        model: str, secret: str, *, canonical: bool,
                        key_id: str | None = None) -> GenerationResult:
        submitted = False
        accepted = False
        try:
            target_path = validated_video_path(output_path, settings.DATA_DIR)
            headers = {"Authorization": f"Bearer {secret}", "Content-Type": "application/json"}
            payload = {"model_name": model, "prompt": prompt,
                       "duration": str(min(duration, 15)), "aspect_ratio": "16:9"}
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=False) as client:
                submitted = True
                data = await request_json(client, "POST", _ENDPOINT, headers=headers, payload=payload)
                if data.get("code") != 0:
                    raise VideoBoundaryError("provider_unavailable", definitive=True)
                accepted = True
                task = data.get("data")
                task_id = task.get("task_id") if isinstance(task, dict) else None
                if not isinstance(task_id, str) or len(task_id) > 128 or not re.fullmatch(r"[A-Za-z0-9_-]+", task_id):
                    raise VideoRoutePending("invalid_output")
                async with asyncio.timeout(75.0):
                    for _ in range(60):
                        await asyncio.sleep(1.0)
                        status = await request_json(client, "GET", f"{_ENDPOINT}/{task_id}", headers=headers)
                        if status.get("code") != 0:
                            raise VideoRoutePending("provider_unavailable")
                        detail = status.get("data")
                        if not isinstance(detail, dict):
                            raise VideoRoutePending("invalid_output")
                        state = detail.get("task_status")
                        if state == "succeed":
                            result = detail.get("task_result")
                            videos = result.get("videos") if isinstance(result, dict) else None
                            if not isinstance(videos, list) or not videos or not isinstance(videos[0], dict):
                                raise VideoRoutePending("invalid_output")
                            video_url = videos[0].get("url")
                            break
                        if state == "failed":
                            raise VideoBoundaryError("job_failed", definitive=True)
                        if state not in ("submitted", "processing"):
                            raise VideoRoutePending("invalid_output")
                    else:
                        raise VideoRoutePending("timeout")
                async with asyncio.timeout(120.0):
                    size = await download_video(client, video_url, target_path)
            if key_id is not None:
                try:
                    await get_key_manager().report_result(self.provider_id, key_id, success=True)
                except Exception:
                    pass  # Local accounting cannot turn a completed video into another billed attempt.
            return GenerationResult(True, file_path=target_path, duration=float(min(duration, 15)),
                                    provider_id=self.provider_id, metadata={"model": model, "size": size})
        except VideoRoutePending:
            raise
        except asyncio.CancelledError:
            if submitted:
                raise VideoRoutePending() from None
            raise
        except (TimeoutError, httpx.TimeoutException):
            if submitted:
                raise VideoRoutePending("timeout") from None
            raise
        except VideoBoundaryError as error:
            if submitted and not error.definitive and (accepted or error.status_code is None or error.status_code >= 500):
                raise VideoRoutePending(error.code) from None
            if canonical:
                raise
            if key_id is not None and error.status_code is not None:
                try:
                    await get_key_manager().report_result(self.provider_id, key_id, success=False,
                                                          status_code=error.status_code,
                                                          error_message=str(error))
                except Exception:
                    pass
            return GenerationResult(False, provider_id=self.provider_id,
                                    error_code=f"HTTP_{error.status_code}" if error.status_code else error.code.upper(),
                                    error_message=str(error))
        except Exception:
            if submitted:
                raise VideoRoutePending("provider_unavailable") from None
            if canonical:
                raise VideoBoundaryError("provider_unavailable") from None
            return GenerationResult(False, provider_id=self.provider_id, error_code="PROVIDER_UNAVAILABLE",
                                    error_message="Video generation failed: provider_unavailable")

    async def estimate_usage(self, duration: int) -> list[UsageEstimate]:
        return [UsageEstimate("video_seconds", float(duration), "seconds")]

    async def get_quota(self) -> list[QuotaInfo]:
        keys = await get_key_manager().get_keys_for_provider(self.provider_id)
        if not keys:
            return [QuotaInfo("video_seconds", 0, 0, 0, "seconds")]
        successes = sum(k.get("successful_requests", 0) for k in keys)
        return [QuotaInfo("video_seconds", successes * 5, None, None, "seconds")]
