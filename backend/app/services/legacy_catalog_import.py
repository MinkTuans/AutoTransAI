"""Explicit, caller-transactional import of archival model identities.

Imported rows have no discovery evidence or key access. The original
``ai_models`` rows remain the archival source for historical settings.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CatalogModel, Provider
from app.models.settings import AIModel


async def import_legacy_catalog(db: AsyncSession) -> dict[str, object]:
    """Copy exact legacy identities, failing the whole batch on ambiguity."""
    counts = {"imported": 0, "existing": 0}
    issues: set[str] = set()
    pending: list[AIModel] = []
    with db.no_autoflush:
        legacy = (await db.scalars(select(AIModel).order_by(AIModel.id))).all()
        for model in legacy:
            providers = (await db.scalars(select(Provider).where(
                Provider.id == model.provider_id))).all()
            if not providers:
                issues.add("missing_provider")
                continue
            if len(providers) != 1 or providers[0].id != model.provider_id:
                issues.add("provider_identity_conflict")
                continue
            matches = (await db.scalars(select(CatalogModel).where(
                CatalogModel.provider_id == model.provider_id,
                CatalogModel.remote_model_id == model.id))).all()
            if any(row.provider_id != model.provider_id or row.remote_model_id != model.id
                   for row in matches) or len(matches) > 1:
                issues.add("catalog_identity_conflict")
            elif matches:
                counts["existing"] += 1
            else:
                pending.append(model)
    if issues:
        return {"status": "conflict", "counts": {"imported": 0, "existing": counts["existing"]},
                "issues": sorted(issues)}
    for model in pending:
        db.add(CatalogModel(
            provider_id=model.provider_id, remote_model_id=model.id,
            display_name=model.model_name, source="legacy_import",
            discovery_metadata=None, capabilities=[], capability_status="FULL_UNKNOWN",
            enabled=model.enabled, created_at=model.created_at,
        ))
        counts["imported"] += 1
    await db.flush()
    return {"status": "imported", "counts": counts, "issues": []}
