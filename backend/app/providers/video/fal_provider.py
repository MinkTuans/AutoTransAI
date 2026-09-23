"""fal.ai video generation with a request-local catalog boundary."""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx

from app.config import get_settings
from app.providers.base import GenerationResult, QuotaInfo, UsageEstimate, VideoProvider
from app.providers.request_target import resolve_request_target
from app.providers.video.catalog_media import (
    VideoBoundaryError, VideoRoutePending, download_video, provider_url, request_json,
    validated_video_path,
)
from app.services.ai_routing import RouteTarget, UnsupportedModalityError
from app.services.key_manager import get_key_manager

settings = get_settings()
_MODEL = "fal-ai/hunyuan-video"
_QUEUE = f"https://queue.fal.run/{_MODEL}"


class FalVideoProvider(VideoProvider):
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
        return await get_key_manager().get_active_key(self.provider_id) is not None

    async def generate_video(self, prompt: str, duration: int, output_path: Path, *,
                             route_target: RouteTarget | None = None,
                             api_key: str | None = None) -> GenerationResult:
        if route_target is not None:
            model, secret = resolve_request_target(
                route_target, api_key, provider_id=self.provider_id,
                capabilities=("VIDEO_GENERATION",), legacy_model=None, legacy_key=None)
            if model != _MODEL:
                raise UnsupportedModalityError("Video generation unsupported for this model.")
            return await self._generate(prompt, duration, output_path, secret, canonical=True)
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
            last = await self._generate(prompt, duration, output_path, key_entry.api_key,
                                        canonical=False, key_id=key_entry.key_id)
            if last.success or last.error_code not in ("HTTP_401", "HTTP_402", "HTTP_403", "HTTP_429"):
                return last
        return last or GenerationResult(False, provider_id=self.provider_id, error_code="NO_API_KEY",
                                        error_message="No valid fal.ai API key configured.")

    async def _generate(self, prompt: str, duration: int, output_path: Path, secret: str,
                        *, canonical: bool, key_id: str | None = None) -> GenerationResult:
        submitted = False
        accepted = False
        try:
            target_path = validated_video_path(output_path, settings.DATA_DIR)
            headers = {"Authorization": f"Key {secret}", "Content-Type": "application/json"}
            # The historical no-route payload is retained until caller migration.
            payload = ({"prompt": prompt, "aspect_ratio": "16:9", "resolution": "720p", "num_frames": 129}
                       if canonical else {"prompt": prompt, "seconds_total": min(duration, 10),
                                          "aspect_ratio": "16:9"})
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=False) as client:
                submitted = True
                data = await request_json(client, "POST", _QUEUE, headers=headers, payload=payload,
                                          accepted=(200, 202))
                accepted = True
                video = data.get("video")
                if not isinstance(video, dict):
                    request_id = data.get("request_id")
                    if not isinstance(request_id, str) or not request_id.isascii() or not request_id.replace("-", "").replace("_", "").isalnum() or len(request_id) > 128:
                        raise VideoRoutePending("invalid_output")
                    base_path = f"/{_MODEL}/requests/{request_id}"
                    status_url = await provider_url(data.get("status_url") or f"https://queue.fal.run{base_path}/status",
                                                    host="queue.fal.run", path=f"{base_path}/status")
                    result_url = await provider_url(data.get("response_url") or f"https://queue.fal.run{base_path}",
                                                    host="queue.fal.run", path=base_path)
                    async with asyncio.timeout(75.0):
                        for _ in range(60):
                            state = (await request_json(client, "GET", status_url, headers=headers)).get("status")
                            if state == "COMPLETED":
                                break
                            if state in ("FAILED", "CANCELED"):
                                raise VideoBoundaryError("job_failed", definitive=True)
                            if state not in ("IN_QUEUE", "IN_PROGRESS"):
                                raise VideoRoutePending("invalid_output")
                            await asyncio.sleep(1.0)
                        else:
                            raise VideoRoutePending("timeout")
                        video = (await request_json(client, "GET", result_url, headers=headers)).get("video")
                if not isinstance(video, dict):
                    raise VideoRoutePending("invalid_output")
                async with asyncio.timeout(120.0):
                    size = await download_video(client, video.get("url"), target_path)
            if key_id is not None:
                try:
                    await get_key_manager().report_result(self.provider_id, key_id, success=True)
                except Exception:
                    pass  # Local accounting cannot turn a completed video into another billed attempt.
            return GenerationResult(True, file_path=target_path,
                                    provider_id=self.provider_id, metadata={"model": _MODEL, "size": size})
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
