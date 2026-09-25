"""Idempotent startup catalog bootstrap from registered runtime providers."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CatalogModel, Provider
from app.providers.registry import ProviderRegistry


_SENTINELS = {
    "edge_tts": ("edge-tts", "TTS"),
    "pollinations": ("pollinations-default", "IMAGE_GENERATION"),
    "local_image": ("default", "IMAGE_GENERATION"),
}


async def bootstrap_providers(db: AsyncSession, registry: ProviderRegistry) -> None:
    """Add registered providers and supported keyless routes in caller transaction."""
    existing = {row.id: row for row in (await db.scalars(select(Provider))).all()}
    registered = {}
    for provider_type, providers in registry.get_all_providers().items():
        for runtime in providers:
            provider_id = runtime.provider_id
            if provider_id in registered:
                # One keyed modality means the shared provider must not claim to be keyless.
                registered[provider_id][2] |= bool(runtime.requires_api_key)
            else:
                registered[provider_id] = [runtime.provider_name, provider_type,
                                           bool(runtime.requires_api_key)]

    for provider_id, (name, provider_type, requires_api_key) in registered.items():
        if provider_id == "openrouter":
            provider_type = "multimodal"
        row = existing.get(provider_id)
        if row is None:
            row = Provider(id=provider_id, name=name, provider_type=provider_type,
                           requires_api_key=requires_api_key)
            db.add(row)
        else:
            # Preserve all user controlled settings and refresh known policy only.
            row.requires_api_key = requires_api_key
            if provider_id == "openrouter":
                row.provider_type = provider_type
    await db.flush()

    for provider_id, (remote_model_id, capability) in _SENTINELS.items():
        if provider_id not in registered or registered[provider_id][2]:
            continue
        found = await db.scalar(select(CatalogModel.id).where(
            CatalogModel.provider_id == provider_id,
            CatalogModel.remote_model_id == remote_model_id,
        ))
        if found is None:
            db.add(CatalogModel(provider_id=provider_id, remote_model_id=remote_model_id,
                                source="system", capability_status="KNOWN", capabilities=[capability]))
