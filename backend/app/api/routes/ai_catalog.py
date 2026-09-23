"""Read-only views of the canonical provider/model inventory."""
from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models import APIKey, CatalogModel, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig
from app.services.ai_routing import _PUBLIC_CATALOG_PROVIDERS, _keyless_allowed
from app.services.capability_registry import CAPABILITIES, catalog_capability_summary


class SafeCatalogReadRoute(APIRoute):
    """Never pass database or credential exception text to the global handler."""

    def get_route_handler(self):
        handler = super().get_route_handler()

        async def safe_handler(request):
            try:
                return await handler(request)
            except (HTTPException, RequestValidationError):
                raise
            except Exception:
                return JSONResponse(status_code=500, content={"success": False, "detail": "Catalog read failed."})

        return safe_handler


router = APIRouter(prefix="/api/ai", tags=["ai-catalog"], route_class=SafeCatalogReadRoute)
T = TypeVar("T")


class Envelope(BaseModel, Generic[T]):
    success: bool = True
    data: T


class ProviderView(BaseModel):
    id: str
    name: str
    provider_type: str
    enabled: bool
    supported: bool
    model_count: int
    active_model_count: int
    enabled_key_count: int
    status: str


class CapabilityView(BaseModel):
    status: str
    capabilities: list[str]
    incompatible_capabilities: list[str]
    unknown_capabilities: list[str]


class ModelView(BaseModel):
    id: str
    provider_id: str
    provider_name: str
    remote_model_id: str
    display_name: str | None
    source: str
    status: str
    enabled: bool
    retired_at: datetime | None
    last_seen: datetime | None
    available_key_count: int
    access_scope: str
    capability: CapabilityView
    default_for: list[str]


class ModelDetail(ModelView):
    metadata: dict


class ModelPage(BaseModel):
    items: list[ModelView]
    page: int
    limit: int
    total: int


class FunctionView(BaseModel):
    function_id: str
    function_name: str
    capability: str
    primary_provider_id: str
    model_id: str
    configuration_error: str | None
    default_status: str
    selectable: bool
    updated_at: datetime


def _safe_metadata(model: CatalogModel) -> dict:
    """Only expose fixed-shape evidence; stored metadata is not itself a public DTO."""
    raw = model.discovery_metadata if isinstance(model.discovery_metadata, dict) else {}
    safe = {}
    numeric = {"gemini": {"inputTokenLimit", "outputTokenLimit"},
               "openai": {"created"}, "anthropic": {"max_input_tokens", "max_tokens"}}
    boolean = {"gemini": {"thinking"}, "elevenlabs": {
        "can_do_text_to_speech", "can_do_voice_conversion", "requires_alpha_access"}}
    for key in numeric.get(model.provider_id, set()):
        value = raw.get(key)
        if type(value) is int and 0 <= value <= 2**63 - 1:
            safe[key] = value
    for key in boolean.get(model.provider_id, set()):
        if type(raw.get(key)) is bool:
            safe[key] = raw[key]
    if model.provider_id == "fal" and isinstance(raw.get("category"), str) and raw["category"] in {
        "image", "text-to-image", "image-to-image", "video", "text-to-video", "image-to-video"
    }:
        safe["category"] = raw["category"]
    if model.provider_id == "anthropic" and isinstance(raw.get("capabilities"), dict):
        flags = {}
        for key in ("batch", "citations", "code_execution", "context_management", "effort",
                    "image_input", "pdf_input", "structured_outputs", "thinking"):
            entry = raw["capabilities"].get(key)
            if isinstance(entry, dict) and type(entry.get("supported")) is bool:
                flags[key] = {"supported": entry["supported"]}
        if flags:
            safe["capabilities"] = flags
    return safe


def _view_context(keys, edges, configs):
    key_counts = {}
    for provider_id in keys.values():
        key_counts[provider_id] = key_counts.get(provider_id, 0) + 1
    access = {}
    seen = {}
    for edge in edges:
        if keys.get(edge.key_id) == edge.provider_id:
            access.setdefault(edge.model_id, set()).add(edge.key_id)
        current = seen.get(edge.model_id)
        if current is None or edge.discovered_at > current:
            seen[edge.model_id] = edge.discovered_at
    defaults = {}
    for config in configs:
        defaults.setdefault((config.model_id, config.primary_provider_id), []).append(config.function_id)
    return key_counts, access, seen, defaults


async def _inventory(db: AsyncSession):
    providers = {p.id: p for p in (await db.scalars(select(Provider))).all()}
    models = (await db.scalars(select(CatalogModel))).all()
    key_rows = (await db.execute(select(APIKey.id, APIKey.provider_id).where(APIKey.enabled.is_(True)))).all()
    keys = {row.id: row.provider_id for row in key_rows}
    edges = (await db.execute(select(KeyModelAccess.key_id, KeyModelAccess.model_id,
                                     KeyModelAccess.provider_id, KeyModelAccess.discovered_at))).all()
    configs = (await db.scalars(select(AIFunctionConfig))).all()
    return providers, models, keys, edges, configs


def _model_view(model, providers, context) -> ModelView:
    key_counts, access, seen, defaults = context
    provider = providers[model.provider_id]
    active = provider.enabled and model.enabled and model.retired_at is None
    public = model.provider_id in _PUBLIC_CATALOG_PROVIDERS
    keyless = any(_keyless_allowed(model, capability) for capability in CAPABILITIES)
    if public:
        count = key_counts.get(model.provider_id, 0)
    else:
        count = len(access.get(model.id, ()))
    return ModelView(
        id=model.id, provider_id=model.provider_id, provider_name=provider.name,
        remote_model_id=model.remote_model_id, display_name=model.display_name,
        source=model.source, status="retired" if model.retired_at else "disabled" if not active else "active",
        enabled=model.enabled, retired_at=model.retired_at, last_seen=seen.get(model.id),
        available_key_count=count if active else 0,
        access_scope="keyless" if keyless else "catalog_unverified" if public else "listing_unverified" if count else "none",
        capability=CapabilityView(**catalog_capability_summary(model)),
        default_for=sorted(defaults.get((model.id, model.provider_id), ())),
    )


@router.get("/providers", response_model=Envelope[list[ProviderView]])
async def list_providers(db: AsyncSession = Depends(get_db)):
    providers, models, keys, _, _ = await _inventory(db)
    rows = []
    for p in sorted(providers.values(), key=lambda item: item.id):
        owned = [m for m in models if m.provider_id == p.id]
        enabled_keys = sum(pid == p.id for pid in keys.values())
        keyless = any(m.enabled and m.retired_at is None and any(
            _keyless_allowed(m, capability) for capability in CAPABILITIES) for m in owned)
        rows.append(ProviderView(id=p.id, name=p.name, provider_type=p.provider_type,
                                 enabled=p.enabled, supported=p.supported, model_count=len(owned),
                                 active_model_count=sum(m.enabled and m.retired_at is None for m in owned),
                                 enabled_key_count=enabled_keys,
                                 status="disabled" if not p.enabled else "ready" if enabled_keys or keyless else "no_key"))
    return Envelope(data=rows)


@router.get("/models", response_model=Envelope[ModelPage])
async def list_models(provider_id: str | None = None, capability: str | None = None,
                      q: str | None = Query(default=None, max_length=200),
                      page: int = Query(default=1, ge=1), limit: int = Query(default=25, ge=1, le=100),
                      db: AsyncSession = Depends(get_db)):
    providers = {p.id: p for p in (await db.scalars(select(Provider))).all()}
    if provider_id is not None and provider_id not in providers:
        raise HTTPException(status_code=404, detail="Provider not found.")
    if capability is not None and capability not in CAPABILITIES:
        raise HTTPException(status_code=422, detail="Unknown AI capability.")
    query = select(CatalogModel).join(Provider, CatalogModel.provider_id == Provider.id)
    if provider_id is not None:
        query = query.where(CatalogModel.provider_id == provider_id)
    query = query.order_by(CatalogModel.provider_id, CatalogModel.remote_model_id, CatalogModel.id)
    start = (page - 1) * limit
    term = q.strip().casefold() if q else ""
    if not capability and not term:
        count_query = select(func.count()).select_from(CatalogModel).join(
            Provider, CatalogModel.provider_id == Provider.id)
        if provider_id is not None:
            count_query = count_query.where(CatalogModel.provider_id == provider_id)
        total = await db.scalar(count_query) or 0
        selected = (await db.scalars(query.offset(start).limit(limit))).all()
    else:
        result = await db.stream_scalars(query.execution_options(yield_per=100))
        selected = []
        total = 0
        try:
            async for model in result:
                provider = providers[model.provider_id]
                summary = catalog_capability_summary(model)
                if capability and capability in summary["incompatible_capabilities"]:
                    continue
                if term and not any(term in value.casefold() for value in (
                    model.remote_model_id, model.display_name or "", provider.name, provider.id,
                    *summary["capabilities"])):
                    continue
                if start <= total < start + limit:
                    selected.append(model)
                total += 1
        finally:
            await result.close()
    ids = [model.id for model in selected]
    provider_ids = {model.provider_id for model in selected}
    keys = {row.id: row.provider_id for row in (await db.execute(
        select(APIKey.id, APIKey.provider_id).where(APIKey.enabled.is_(True),
                                                   APIKey.provider_id.in_(provider_ids)))).all()}
    edges = (await db.execute(select(KeyModelAccess.key_id, KeyModelAccess.model_id,
                                     KeyModelAccess.provider_id, KeyModelAccess.discovered_at)
                              .where(KeyModelAccess.model_id.in_(ids)))).all()
    configs = (await db.scalars(select(AIFunctionConfig).where(AIFunctionConfig.model_id.in_(ids)))).all()
    context = _view_context(keys, edges, configs)
    return Envelope(data=ModelPage(items=[_model_view(model, providers, context) for model in selected],
                                   page=page, limit=limit, total=total))


@router.get("/models/{model_id}", response_model=Envelope[ModelDetail])
async def model_detail(model_id: str, db: AsyncSession = Depends(get_db)):
    providers, models, keys, edges, configs = await _inventory(db)
    model = next((m for m in models if m.id == model_id), None)
    if model is None or model.provider_id not in providers:
        raise HTTPException(status_code=404, detail="Model not found.")
    return Envelope(data=ModelDetail(**_model_view(model, providers, _view_context(keys, edges, configs)).model_dump(),
                                     metadata=_safe_metadata(model)))


@router.get("/functions", response_model=Envelope[list[FunctionView]])
async def list_functions(db: AsyncSession = Depends(get_db)):
    providers, models, keys, edges, configs = await _inventory(db)
    context = _view_context(keys, edges, configs)
    by_id = {m.id: m for m in models}
    rows = []
    for c in sorted(configs, key=lambda config: config.function_id):
        model = by_id.get(c.model_id)
        if model is None:
            legacy = c.model_id == "default" or any(
                m.provider_id == c.primary_provider_id and m.remote_model_id == c.model_id for m in models)
            status = "legacy_unmigrated" if legacy else "missing"
        elif model.provider_id != c.primary_provider_id:
            status = "provider_mismatch"
        elif model.retired_at is not None:
            status = "retired"
        elif not model.enabled or not providers.get(model.provider_id) or not providers[model.provider_id].enabled:
            status = "disabled"
        elif c.capability not in CAPABILITIES or c.capability in catalog_capability_summary(model)["incompatible_capabilities"]:
            status = "incompatible"
        elif _model_view(model, providers, context).available_key_count == 0 and not _keyless_allowed(model, c.capability):
            status = "no_key"
        else:
            status = "ready"
        rows.append(FunctionView(function_id=c.function_id, function_name=c.function_name,
                                 capability=c.capability, primary_provider_id=c.primary_provider_id,
                                 model_id=c.model_id,
                                 configuration_error=("catalog_model_retired" if c.configuration_error == "catalog_model_retired"
                                                      else "configuration_error" if c.configuration_error else None),
                                 default_status="configuration_error" if c.configuration_error else status,
                                 selectable=status == "ready" and not c.configuration_error,
                                 updated_at=c.updated_at))
    return Envelope(data=rows)
