"""Voice-safe Studio TTS routing without shared provider state."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.ai_routing import (
    RouteConfigurationError, RoutePlan, RouteTarget, UnsupportedModalityError, invoke_route,
)


@dataclass(frozen=True)
class GeneratedClip:
    target: RouteTarget
    voice_id: str


class TTSGenerationFailure(Exception):
    """A sanitized provider result that route classification can inspect."""

    def __init__(self, error_code: str | None):
        safe_code = error_code or "GENERATION_FAILED"
        self.status_code = None
        if safe_code.startswith("HTTP_"):
            try:
                self.status_code = int(safe_code[5:])
            except ValueError:
                pass
        self.code = "invalid_output" if safe_code in ("EMPTY_RESPONSE", "MISSING_AUDIO_CONTENT", "EMPTY_AUDIO") else None
        super().__init__("TTS generation failed")


def _compatible_voice(row: dict[str, Any], target_language: str, gender: str | None) -> bool:
    language = str(row.get("language") or "").lower()
    wanted = str(target_language or "").lower().split("-")[0]
    if not wanted or not language.startswith(wanted):
        return False
    known_gender = str(gender or "").lower()
    if known_gender in ("female", "male") and str(row.get("gender") or "").lower() != known_gender:
        return False
    return bool(row.get("voice_id"))


def select_segment_route(route: RoutePlan, segment: dict[str, Any], pool: list[dict[str, Any]],
                         target_language: str) -> tuple[RoutePlan, dict[RouteTarget, str]]:
    """Keep only targets with an eligible provider-local voice for this segment."""
    chosen: dict[RouteTarget, str] = {}
    confirmed = bool(segment.get("confirmed_by_user"))
    for target in route.targets:
        # Google has no key-scoped voice discovery/access bridge yet.
        if target.provider_id not in ("edge_tts", "elevenlabs"):
            continue
        if confirmed and target.provider_id != segment.get("voice_provider"):
            continue
        matching = [row for row in pool if row.get("provider") == target.provider_id
                    and _compatible_voice(row, target_language, segment.get("gender"))]
        if confirmed:
            match = next((row for row in matching if row["voice_id"] == segment.get("voice_id")), None)
        else:
            match = next((row for row in matching if target.provider_id == segment.get("voice_provider")
                          and row["voice_id"] == segment.get("voice_id")), None)
            match = match or (matching[0] if matching else None)
        if match:
            chosen[target] = match["voice_id"]
    if not chosen:
        raise RouteConfigurationError("No compatible TTS voice is available for this segment.")
    return RoutePlan("TTS", tuple(chosen), route.configured_model_id), chosen


def cache_identity(target: RouteTarget, voice_id: str, text: str,
                   configured_model_id: str | None = None) -> dict[str, str | None]:
    return {"voice_provider": target.provider_id, "catalog_model_id": target.model_id,
            "model_id": target.remote_model_id, "key_id": target.key_id,
            "voice_id": voice_id, "translated_text": text,
            "route_default_model_id": configured_model_id}


def cache_matches(metadata: dict[str, Any], route: RoutePlan, voices: dict[RouteTarget, str], text: str) -> bool:
    return any(metadata == cache_identity(target, voices[target], text, route.configured_model_id)
               for target in route.targets)


async def generate_segment_audio(route: RoutePlan, voices: dict[RouteTarget, str], text: str,
                                 output_path: Path, sessions, data_dir: Path, registry) -> GeneratedClip:
    async def transport(target: RouteTarget, secret: str | None) -> GeneratedClip:
        provider = registry.get_audio(target.provider_id)
        if provider is None:
            raise UnsupportedModalityError("TTS provider adapter is unavailable.")
        output_path.unlink(missing_ok=True)
        result = await provider.generate_audio(text=text, voice_id=voices[target], output_path=output_path,
                                               route_target=target, api_key=secret)
        if not result.success:
            if result.error_code == "TTS_TIMEOUT":
                raise asyncio.TimeoutError("TTS generation timed out")
            raise TTSGenerationFailure(result.error_code)
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise TTSGenerationFailure("EMPTY_AUDIO")
        return GeneratedClip(target, voices[target])

    return await invoke_route(route, transport, sessions, data_dir, timeout=180.0)
