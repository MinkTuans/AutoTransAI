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

        is_configured = await provider.validate_configuration()

        return ProviderResponse(
            id=provider.provider_id,
            name=provider.provider_name,
            provider_type=ptype,
            configured=is_configured,
            api_key_set=is_configured or (not provider.requires_api_key),
            quota=quota_list,
            free_tier=provider.is_free,
            availability="available" if is_configured else "api_key_missing",
        ).model_dump()

    audio = [await to_response(p, "audio") for p in registry.list_audio()]
    video = [await to_response(p, "video") for p in registry.list_video()]
    llm = [await to_response(p, "llm") for p in registry.list_llm()]

    return {
        "success": True,
        "data": {"audio": audio, "video": video, "llm": llm},
    }


import os
from pathlib import Path
from app.config import get_settings, ENV_FILE_PATH
from app.schemas.provider import ProviderConfigureRequest

settings = get_settings()

PROVIDER_ENV_MAP = {
    "gemini": "GEMINI_API_KEY",
    "google_cloud_tts": "GOOGLE_CLOUD_TTS_API_KEY",
    "elevenlabs": "ELEVENLABS_API_KEY",
    "kling": "KLING_API_KEY",
    "fal": "FAL_API_KEY",
}


@router.post("/{provider_id}/config", response_model=dict)
async def configure_provider(provider_id: str, body: ProviderConfigureRequest):
    """Configure API key for a provider and persist to .env file."""
    env_var = PROVIDER_ENV_MAP.get(provider_id)
    if not env_var:
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{provider_id}' does not require an API key or is invalid",
        )

    api_key = body.api_key.strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="API Key cannot be empty")

    # Update runtime env and settings
    os.environ[env_var] = api_key
    setattr(settings, env_var, api_key)

    # Persist to .env file
    env_path = Path(ENV_FILE_PATH)
    env_lines = []
    if env_path.exists():
        env_lines = env_path.read_text(encoding="utf-8").splitlines()

    updated = False
    new_lines = []
    for line in env_lines:
        if line.startswith(f"{env_var}="):
            new_lines.append(f"{env_var}={api_key}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"{env_var}={api_key}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    # Validate provider with new key
    registry = get_registry()
    provider = (
        registry.get_audio(provider_id)
        or registry.get_video(provider_id)
        or registry.get_llm(provider_id)
    )

    is_valid = False
    if provider:
        is_valid = await provider.validate_configuration()

    logger.info("Provider configured", provider_id=provider_id, valid=is_valid)

    return {
        "success": True,
        "data": {
            "provider_id": provider_id,
            "configured": is_valid,
        },
    }


from app.services.key_manager import get_key_manager

@router.get("/{provider_id}/keys", response_model=dict)
async def get_provider_keys(provider_id: str):
    """List all API keys for a provider (masked)."""
    key_mgr = get_key_manager()
    keys = await key_mgr.get_keys_for_provider(provider_id)
    return {"success": True, "data": keys}


@router.post("/{provider_id}/keys", response_model=dict)
async def add_provider_key(provider_id: str, body: dict):
    """Add a new API key for a provider."""
    api_key = body.get("api_key", "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    priority = body.get("priority")
    key_mgr = get_key_manager()
    entry = await key_mgr.add_key(provider_id, api_key, priority=priority)

    # Also sync with .env for backward compatibility
    env_var = PROVIDER_ENV_MAP.get(provider_id)
    if env_var:
        try:
            os.environ[env_var] = api_key
            setattr(settings, env_var, api_key)
        except Exception:
            pass

    return {"success": True, "data": entry.to_dict(include_raw_key=False)}


@router.delete("/{provider_id}/keys/{key_id}", response_model=dict)
async def delete_provider_key(provider_id: str, key_id: str):
    """Delete an API key."""
    key_mgr = get_key_manager()
    res = await key_mgr.delete_key(provider_id, key_id)
    return {"success": res, "message": "Key deleted successfully"}


@router.put("/{provider_id}/keys/{key_id}", response_model=dict)
async def update_provider_key(provider_id: str, key_id: str, body: dict):
    """Update API key priority or status."""
    key_mgr = get_key_manager()
    priority = body.get("priority")
    status = body.get("status")
    entry = await key_mgr.update_key(provider_id, key_id, priority=priority, status=status)
    if not entry:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"success": True, "data": entry.to_dict(include_raw_key=False)}


@router.post("/{provider_id}/keys/{key_id}/test", response_model=dict)
async def test_provider_key(provider_id: str, key_id: str):
    """Test validity of a specific API key."""
    key_mgr = get_key_manager()
    res = await key_mgr.test_key(provider_id, key_id)
    return {"success": True, "data": res}


@router.post("/{provider_id}/keys/{key_id}/quota", response_model=dict)
async def fetch_provider_key_quota(provider_id: str, key_id: str):
    """Fetch official quota/balance for an API key."""
    key_mgr = get_key_manager()
    res = await key_mgr.fetch_quota(provider_id, key_id)
    return {"success": True, "data": res}


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

