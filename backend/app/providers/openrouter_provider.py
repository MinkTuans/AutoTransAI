"""OpenRouter runtime adapters using exact catalog models and request credentials."""

from __future__ import annotations

import asyncio
import base64
import os
import tempfile
from pathlib import Path

import httpx

from app.config import get_settings
from app.providers.base import (AudioProvider, GenerationResult, ImageProvider, LLMProvider,
                                QuotaInfo, UsageEstimate, VideoProvider, VisionProvider, VoiceInfo)
from app.providers.image.catalog_media import (CatalogImageError, decode_image_base64,
                                               download_image, request_json as image_request_json,
                                               validated_output_path)
from app.providers.request_target import resolve_request_target
from app.providers.video.catalog_media import (VideoBoundaryError, VideoRoutePending,
                                               MAX_VIDEO_BYTES, validate_mp4_file,
                                               request_json as video_request_json,
                                               validated_video_path)
from app.services.ai_routing import RouteTarget, UnsupportedModalityError

BASE = "https://openrouter.ai/api/v1"
# OpenRouter documents verbose segment timestamps for OpenAI-compatible STT.
# Keep this opt-in to the documented Whisper slug; other routes can reject it.
_VERBOSE_STT_MODELS = frozenset({"openai/whisper-1"})


def _route(target: RouteTarget | None, key: str | None, capabilities: tuple[str, ...]) -> tuple[str, str]:
    model, secret = resolve_request_target(target, key, provider_id="openrouter",
                                           capabilities=capabilities, legacy_model=None, legacy_key=None)
    if not model or not secret:
        raise ValueError("OpenRouter requires a catalog route target and request credential.")
    return model, secret


def _headers(secret: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {secret}"}


class _Common:
    provider_id = "openrouter"
    provider_name = "OpenRouter"
    is_free = False
    requires_api_key = True

    async def validate_configuration(self) -> bool:
        # Canonical keys are selected per route, not kept on provider instances.
        return True

    async def get_quota(self) -> list[QuotaInfo]:
        return [QuotaInfo("credits", unit="USD")]


class OpenRouterLLMProvider(_Common, LLMProvider):
    async def generate_text(self, prompt: str, system_prompt: str = "", model: str | None = None,
                            *, route_target: RouteTarget | None = None, api_key: str | None = None) -> str:
        remote, secret = _route(route_target, api_key, ("LLM", "TRANSLATION"))
        messages = ([{"role": "system", "content": system_prompt}] if system_prompt else [])
        messages.append({"role": "user", "content": prompt})
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(f"{BASE}/chat/completions", headers=_headers(secret),
                                         json={"model": remote, "messages": messages})
        if response.status_code != 200:
            raise OpenRouterHTTPError(response.status_code)
        content = _chat_content(response.json())
        if not content:
            raise ValueError("OpenRouter returned empty text.")
        return content

    async def estimate_usage(self, input_text: str) -> list[UsageEstimate]:
        return [UsageEstimate("input_tokens", len(input_text) / 4, "tokens")]


class OpenRouterHTTPError(Exception):
    """Safe HTTP status without upstream body, URL or credential."""

    def __init__(self, status_code: int):
        self.status_code = status_code
        super().__init__(f"OpenRouter request failed with HTTP {status_code}.")


def _chat_content(data: object) -> str:
    if not isinstance(data, dict):
        return ""
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return ""
    message = choices[0].get("message")
    content = message.get("content") if isinstance(message, dict) else None
    return content.strip() if isinstance(content, str) else ""


class OpenRouterVisionProvider(_Common, VisionProvider):
    async def analyze_image(self, image_path: Path | str, prompt: str, model: str | None = None,
                            api_key: str | None = None, **kwargs) -> str:
        remote, secret = _route(kwargs.get("route_target"), api_key, ("VISUAL_GENDER",))
        image = Path(image_path)
        if image.stat().st_size > 10 * 1024 * 1024:
            raise ValueError("Vision image exceeds size limit.")
        mime = "image/png" if image.suffix.lower() == ".png" else "image/jpeg"
        encoded = base64.b64encode(image.read_bytes()).decode("ascii")
        payload = {"model": remote, "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}},
        ]}]}
        async with httpx.AsyncClient(timeout=float(kwargs.get("timeout", 60.0))) as client:
            response = await client.post(f"{BASE}/chat/completions", headers=_headers(secret), json=payload)
        if response.status_code != 200:
            raise OpenRouterHTTPError(response.status_code)
        answer = _chat_content(response.json())
        if not answer:
            raise ValueError("OpenRouter returned empty vision text.")
        return answer


async def transcribe_audio(audio_path: Path, duration: float, *, route_target: RouteTarget | None,
                           api_key: str | None) -> tuple[list[dict], str]:
    """Transcribe one bounded audio chunk through the OpenRouter STT endpoint."""
    remote, secret = _route(route_target, api_key, ("STT",))
    if audio_path.stat().st_size > 15 * 1024 * 1024:
        raise ValueError("STT audio chunk exceeds size limit.")
    audio_format = audio_path.suffix.lower().lstrip(".")
    if audio_format not in {"wav", "mp3", "flac", "m4a", "ogg", "webm", "aac"}:
        raise ValueError("STT audio format is unsupported.")
    payload = {"model": remote, "input_audio": {
        "data": base64.b64encode(audio_path.read_bytes()).decode("ascii"),
        "format": audio_format,
    }}
    if remote in _VERBOSE_STT_MODELS:
        payload["response_format"] = "verbose_json"
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(f"{BASE}/audio/transcriptions", headers=_headers(secret), json=payload)
    if response.status_code != 200:
        raise OpenRouterHTTPError(response.status_code)
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("OpenRouter returned invalid transcription.")
    language = str(data.get("language") or "English")
    source = data.get("segments")
    if not isinstance(source, list) or not source:
        source = [{"start": 0.0, "end": duration, "text": data.get("text")}]
    segments = []
    for item in source:
        if not isinstance(item, dict) or not isinstance(item.get("text"), str) or not item["text"].strip():
            continue
        start = max(0.0, min(duration, float(item.get("start", 0.0))))
        end = max(start, min(duration, float(item.get("end", duration))))
        if end <= start:
            continue
        segments.append({"number": len(segments) + 1, "start_time": round(start, 2),
                         "end_time": round(end, 2), "text": item["text"].strip(),
                         "speaker_id": f"UNRESOLVED_{len(segments) + 1:04d}"})
    if not segments:
        raise ValueError("OpenRouter returned empty transcription.")
    return segments, language


class OpenRouterAudioProvider(_Common, AudioProvider):
    async def get_voices(self, language: str | None = None) -> list[VoiceInfo]:
        # Voice lists vary by model and key. No global voice is safe to invent.
        return []

    async def generate_audio(self, text: str, voice_id: str, output_path: Path, *,
                             route_target: RouteTarget | None = None,
                             api_key: str | None = None) -> GenerationResult:
        remote, secret = _route(route_target, api_key, ("TTS",))
        payload = {"model": remote, "input": text, "response_format": "mp3"}
        if not voice_id or voice_id == "__default__":
            return GenerationResult(False, error_code="VOICE_REQUIRED", provider_id=self.provider_id)
        payload["voice"] = voice_id
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(f"{BASE}/audio/speech", headers=_headers(secret), json=payload)
            if response.status_code != 200:
                return GenerationResult(False, error_code=f"HTTP_{response.status_code}", provider_id=self.provider_id)
            if not response.content or len(response.content) > 20 * 1024 * 1024:
                return GenerationResult(False, error_code="EMPTY_AUDIO", provider_id=self.provider_id)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(prefix=f".{output_path.name}.", suffix=".mp3",
                                             dir=output_path.parent, delete=False) as file:
                source = Path(file.name)
                file.write(response.content)
            with tempfile.NamedTemporaryFile(prefix=f".{output_path.name}.", suffix=output_path.suffix,
                                             dir=output_path.parent, delete=False) as file:
                converted = Path(file.name)
            try:
                process = await asyncio.create_subprocess_exec(
                    "ffmpeg", "-y", "-i", str(source), str(converted),
                    stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
                try:
                    async with asyncio.timeout(45):
                        await process.wait()
                except (TimeoutError, asyncio.CancelledError):
                    process.kill()
                    await process.wait()
                    raise
                if process.returncode != 0 or not converted.is_file() or converted.stat().st_size == 0:
                    return GenerationResult(False, error_code="INVALID_OUTPUT", provider_id=self.provider_id)
                os.replace(converted, output_path)
            finally:
                source.unlink(missing_ok=True)
                converted.unlink(missing_ok=True)
            return GenerationResult(True, file_path=output_path, provider_id=self.provider_id,
                                    metadata={"model": remote})
        except (OSError, httpx.HTTPError, TimeoutError):
            return GenerationResult(False, error_code="PROVIDER_UNAVAILABLE", provider_id=self.provider_id)

    async def estimate_usage(self, text: str) -> list[UsageEstimate]:
        return [UsageEstimate("characters", len(text), "characters")]


class OpenRouterImageProvider(_Common, ImageProvider):
    async def generate_image(self, prompt: str, width: int = 1280, height: int = 720,
                             aspect_ratio: str = "16:9", model: str = "default", options: dict | None = None,
                             *, route_target: RouteTarget | None = None,
                             api_key: str | None = None) -> GenerationResult:
        remote, secret = _route(route_target, api_key, ("IMAGE_GENERATION",))
        try:
            output = validated_output_path((options or {}).get("output_path"), get_settings().DATA_DIR)
            async with httpx.AsyncClient(timeout=120.0, follow_redirects=False) as client:
                data = await image_request_json(client, "POST", f"{BASE}/images",
                                                headers=_headers(secret), payload={"model": remote, "prompt": prompt, "n": 1})
                items = data.get("data")
                item = items[0] if isinstance(items, list) and items and isinstance(items[0], dict) else {}
                if isinstance(item.get("b64_json"), str):
                    content = decode_image_base64(item["b64_json"])
                elif isinstance(item.get("url"), str):
                    content = await download_image(client, item["url"])
                else:
                    raise CatalogImageError("invalid_output")
            if output:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(content)
            return GenerationResult(True, file_path=output, provider_id=self.provider_id,
                                    metadata={"image_bytes": content, "model": remote,
                                              "width": width, "height": height, "aspect_ratio": aspect_ratio})
        except CatalogImageError as error:
            return GenerationResult(False, error_code=f"HTTP_{error.status_code}" if error.status_code else error.code.upper(),
                                    provider_id=self.provider_id)

    async def estimate_usage(self, prompt: str) -> list[UsageEstimate]:
        return [UsageEstimate("images", 1, "image")]


class OpenRouterVideoProvider(_Common, VideoProvider):
    max_duration_seconds = 60
    supported_durations = [5, 8, 10, 15]

    async def generate_video(self, prompt: str, duration: int, output_path: Path, *,
                             route_target: RouteTarget | None = None,
                             api_key: str | None = None) -> GenerationResult:
        remote, secret = _route(route_target, api_key, ("VIDEO_GENERATION",))
        path = validated_video_path(output_path, get_settings().DATA_DIR)
        headers = _headers(secret)
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
                try:
                    listing = await video_request_json(client, "GET", f"{BASE}/videos/models", headers=headers)
                except VideoBoundaryError as error:
                    raise VideoBoundaryError("provider_unavailable", error.status_code,
                                             definitive=True) from None
                models = listing.get("data")
                selected = next((item for item in models if isinstance(item, dict) and item.get("id") == remote), None) if isinstance(models, list) else None
                durations = selected.get("supported_durations") if selected else None
                if (not isinstance(durations, list) or not durations or len(durations) > 64
                        or any(type(value) is not int or not 1 <= value <= 300 for value in durations)
                        or duration not in durations):
                    raise UnsupportedModalityError("OpenRouter video model does not support requested duration.")
                try:
                    async with asyncio.timeout(30):
                        job = await video_request_json(client, "POST", f"{BASE}/videos", headers=headers,
                                                       payload={"model": remote, "prompt": prompt, "duration": duration},
                                                       accepted=(200, 201, 202))
                except VideoBoundaryError as error:
                    if error.status_code in (400, 401, 402, 403, 404, 422, 429):
                        raise VideoBoundaryError("provider_unavailable", error.status_code,
                                                 definitive=True) from None
                    raise VideoRoutePending("submission_uncertain") from None
                except (TimeoutError, httpx.HTTPError):
                    raise VideoRoutePending("submission_uncertain") from None
                job_id = job.get("id")
                if not isinstance(job_id, str) or not job_id or len(job_id) > 128 or not all(c.isalnum() or c in "_-" for c in job_id):
                    raise VideoRoutePending("invalid_output")
                for _ in range(90):
                    await asyncio.sleep(2)
                    status = await video_request_json(client, "GET", f"{BASE}/videos/{job_id}", headers=headers)
                    state = status.get("status")
                    if state in ("failed", "cancelled"):
                        return GenerationResult(False, error_code="JOB_FAILED", provider_id=self.provider_id)
                    if state == "completed":
                        size = await _download_video_content(client, job_id, headers, path)
                        return GenerationResult(True, file_path=path, provider_id=self.provider_id,
                                                metadata={"model": remote, "size": size})
                raise VideoRoutePending("timeout")
        except VideoRoutePending:
            raise
        except UnsupportedModalityError:
            raise
        except VideoBoundaryError as error:
            if error.definitive:
                raise
            raise VideoRoutePending("provider_unavailable") from None
        except (TimeoutError, httpx.HTTPError):
            raise VideoRoutePending("provider_unavailable") from None

    async def estimate_usage(self, duration: int) -> list[UsageEstimate]:
        return [UsageEstimate("seconds", duration, "seconds")]


async def _download_video_content(client: httpx.AsyncClient, job_id: str,
                                  headers: dict[str, str], output: Path) -> int:
    """Download authenticated OpenRouter content into a bounded validated MP4."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f".{output.name}.", suffix=".part",
                                     dir=output.parent, delete=False) as file:
        temporary = Path(file.name)
    try:
        async with client.stream("GET", f"{BASE}/videos/{job_id}/content", headers=headers,
                                 follow_redirects=False) as response:
            if response.status_code != 200:
                raise VideoRoutePending("content_unavailable")
            if response.headers.get("content-type", "").split(";", 1)[0].lower() != "video/mp4":
                raise VideoRoutePending("invalid_output")
            size = 0
            with temporary.open("wb") as file:
                async for chunk in response.aiter_bytes():
                    size += len(chunk)
                    if size > MAX_VIDEO_BYTES:
                        raise VideoRoutePending("invalid_output")
                    file.write(chunk)
        try:
            await validate_mp4_file(temporary, size)
        except VideoBoundaryError:
            raise VideoRoutePending("invalid_output") from None
        os.replace(temporary, output)
        return size
    finally:
        temporary.unlink(missing_ok=True)
