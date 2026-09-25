"""Shared compatibility gate for Unified script-to-video callers.

The historical project provider remains authoritative until Settings stores an
exact catalog model ID. A broken explicit selection is never silently routed
through the legacy key store.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CatalogModel
from app.models.settings import AIFunctionConfig
from app.services.ai_routing import RouteConfigurationError

_LEGACY_VIDEO_DEFAULTS = frozenset({("kling", "kling-v1"),
                                    ("fal", "fal-ai/hunyuan-video")})


def supported_video_target(provider_id: str, remote_model_id: str, *,
                           metadata: dict | None = None, duration: int | None = None) -> bool:
    """Check adapter schema and known OpenRouter text-to-video duration evidence."""
    if provider_id == "fal":
        return remote_model_id == "fal-ai/hunyuan-video"
    if provider_id == "kling":
        return remote_model_id in {"kling-v2-5-turbo", "kling-v2-6", "kling-v3"}
    if provider_id == "openrouter":
        if not remote_model_id or not isinstance(metadata, dict):
            return False
        architecture = metadata.get("architecture")
        video = metadata.get("video")
        if not isinstance(architecture, dict) or not isinstance(video, dict):
            return False
        inputs = architecture.get("input_modalities")
        outputs = architecture.get("output_modalities")
        durations = video.get("supported_durations")
        return (isinstance(inputs, list) and "text" in inputs
                and isinstance(outputs, list) and "video" in outputs
                and isinstance(durations, list) and 0 < len(durations) <= 64
                and all(type(value) is int and 1 <= value <= 300 for value in durations)
                and (duration is None or duration in durations))
    return False


async def canonical_video_selected(db: AsyncSession) -> bool:
    config = await db.get(AIFunctionConfig, "video_generation")
    if config is None or not config.model_id or config.model_id == "default":
        if config is not None and config.configuration_error:
            raise RouteConfigurationError("Configured video model needs review.")
        return False
    if config.configuration_error:
        raise RouteConfigurationError("Configured video model needs review.")
    model = await db.get(CatalogModel, config.model_id)
    if model is None:
        if (config.primary_provider_id, config.model_id) in _LEGACY_VIDEO_DEFAULTS:
            return False
        raise RouteConfigurationError("Configured video model is unavailable.")
    return True
