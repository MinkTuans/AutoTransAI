"""Validated catalog access writes with database-enforced provider matching."""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_catalog import CatalogModel, KeyModelAccess
from app.models.api_key import APIKey


class CatalogAccessError(ValueError):
    """Safe association-validation error; contains no credential data."""


async def grant_model_access(session: AsyncSession, key_id: str, model_id: str) -> KeyModelAccess:
    """Ensure a same-provider access row, leaving commit/rollback to the caller.

    On a concurrent constraint failure the caller must roll back before retrying.
    Composite foreign keys protect this invariant even for direct SQL writers.
    """
    key = await session.get(APIKey, key_id)
    model = await session.get(CatalogModel, model_id)
    if key is None or model is None:
        raise CatalogAccessError("Credential or model does not exist.")
    if key.provider_id != model.provider_id:
        raise CatalogAccessError("Credential and model must belong to the same provider.")
    existing = await session.get(KeyModelAccess, (key_id, model_id))
    if existing is not None:
        return existing
    access = KeyModelAccess(key_id=key_id, model_id=model_id, provider_id=key.provider_id)
    session.add(access)
    try:
        await session.flush()
    except IntegrityError:
        raise CatalogAccessError("Catalog access changed concurrently; roll back and retry.") from None
    return access
