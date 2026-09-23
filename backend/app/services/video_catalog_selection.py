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


def supported_video_target(provider_id: str, remote_model_id: str) -> bool:
    """Models with a documented schema in the installed Fal/Kling adapters."""
    if provider_id == "fal":
        return remote_model_id == "fal-ai/hunyuan-video"
    if provider_id == "kling":
        return remote_model_id in {"kling-v2-5-turbo", "kling-v2-6", "kling-v3"}
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
