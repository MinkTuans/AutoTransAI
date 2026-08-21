"""
Provider API routes.

Returns provider info to the frontend. No provider-specific logic here —
the registry handles all lookups.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.providers.registry import get_registry
from app.schemas.provider import ProviderResponse, QuotaInfo, ProviderListResponse
from app.core import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.get("", response_model=dict)
async def list_providers():
    """List all registered providers grouped by type."""
    registry = get_registry()

    async def to_response(provider, ptype: str) -> dict:
        quota_list = []
        try:
            quotas = await provider.get_quota()
            quota_list = [
                QuotaInfo(
                    resource_type=q.resource_type,
                    used=q.used,
                    limit=q.limit,
                    remaining=q.remaining,
                    unit=q.unit,
                ).model_dump()
                for q in quotas
            ]
        except Exception as e:
            logger.warning(
                "Failed to get quota",
                provider_id=provider.provider_id,
                error=str(e),
            )

        return ProviderResponse(
            id=provider.provider_id,
            name=provider.provider_name,
            provider_type=ptype,
            configured=True,  # If registered, it's configured
            api_key_set=not provider.requires_api_key,  # Free providers don't need keys
            quota=quota_list,
            free_tier=provider.is_free,
            availability="available",
        ).model_dump()

    audio = [await to_response(p, "audio") for p in registry.list_audio()]
    video = [await to_response(p, "video") for p in registry.list_video()]
    llm = [await to_response(p, "llm") for p in registry.list_llm()]

    return {
        "success": True,
        "data": {"audio": audio, "video": video, "llm": llm},
    }


@router.get("/{provider_id}/voices", response_model=dict)
async def list_voices(provider_id: str, language: str | None = None):
    """List available voices for an audio provider."""
    registry = get_registry()
    provider = registry.get_audio(provider_id)

    if not provider:
        raise HTTPException(status_code=404, detail=f"Audio provider '{provider_id}' not found")

    voices = await provider.get_voices(language=language)

    return {
        "success": True,
        "data": [
            {
                "id": v.id,
                "name": v.name,
                "language": v.language,
                "gender": v.gender,
            }
            for v in voices
        ],
    }
