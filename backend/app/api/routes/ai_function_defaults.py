"""Canonical Function default write; legacy fallback columns remain untouched."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.api.routes.ai_catalog import Envelope, FunctionView
from app.database import async_session_factory
from app.models import APIKey, CatalogModel, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig
from app.services.ai_routing import _PUBLIC_CATALOG_PROVIDERS, _keyless_allowed
from app.services.capability_registry import compatible, model_evidence
from app.services.credential_service import lock_catalog_provider
from app.services.function_inventory import FUNCTION_INVENTORY


class SafeFunctionWriteRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def safe_handler(request):
            try:
                return await handler(request)
            except RequestValidationError:
                return JSONResponse(status_code=422, content={"success": False, "detail": "Invalid request."})
            except HTTPException:
                raise
            except Exception:
                return JSONResponse(status_code=500, content={"success": False, "detail": "Function update failed."})

        return safe_handler


router = APIRouter(prefix="/api/ai", tags=["ai-catalog"], route_class=SafeFunctionWriteRoute)


class FunctionDefaultInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model_id: str = Field(min_length=1, max_length=100, strict=True)


def get_function_sessions() -> async_sessionmaker:
    return async_session_factory


async def _available(db, model: CatalogModel, capability: str) -> bool:
    if _keyless_allowed(model, capability):
        return True
    if model.provider_id in _PUBLIC_CATALOG_PROVIDERS:
        query = select(APIKey.id).where(APIKey.provider_id == model.provider_id, APIKey.enabled.is_(True))
    else:
        query = (select(APIKey.id).join(KeyModelAccess, KeyModelAccess.key_id == APIKey.id)
                 .where(APIKey.provider_id == model.provider_id, APIKey.enabled.is_(True),
                        KeyModelAccess.provider_id == model.provider_id,
                        KeyModelAccess.model_id == model.id))
    return await db.scalar(query.limit(1).with_for_update()) is not None


@router.put("/functions/{function_id}", response_model=Envelope[FunctionView])
async def set_function_default(function_id: str, body: FunctionDefaultInput,
                               sessions: async_sessionmaker = Depends(get_function_sessions)):
    # Keep the provider-ID preflight outside the write transaction: on MySQL
    # REPEATABLE READ an ordinary SELECT would otherwise pin an older snapshot.
    async with sessions() as preflight:
        provider_id = await preflight.scalar(select(CatalogModel.provider_id).where(
            CatalogModel.id == body.model_id))
    if provider_id is None:
        raise HTTPException(404, "Catalog model does not exist.")
    creating = False
    try:
        async with sessions.begin() as db:
            await lock_catalog_provider(db, provider_id)
            config = await db.scalar(select(AIFunctionConfig).where(
                AIFunctionConfig.function_id == function_id).with_for_update()
                .execution_options(populate_existing=True))
            if config is None:
                definition = FUNCTION_INVENTORY.get(function_id)
                if definition is None:
                    raise HTTPException(404, "Function does not exist.")
                config = AIFunctionConfig(function_id=function_id, function_name=definition[0],
                                          capability=definition[1], primary_provider_id="", model_id="")
                db.add(config)
                creating = True
            model = await db.scalar(select(CatalogModel).where(CatalogModel.id == body.model_id)
                                    .with_for_update().execution_options(populate_existing=True))
            if model is None:
                raise HTTPException(404, "Catalog model does not exist.")
            provider = await db.scalar(select(Provider).where(Provider.id == provider_id)
                                       .with_for_update().execution_options(populate_existing=True))
            if (model.provider_id != provider_id or model.source == "legacy_import"
                    or provider is None or not provider.enabled
                    or not model.enabled or model.retired_at is not None
                    or not compatible(config.capability, model_evidence(model))
                    or not await _available(db, model, config.capability)):
                raise HTTPException(409, "Catalog model is unavailable for this function.")
            config.primary_provider_id = model.provider_id
            config.model_id = model.id
            config.configuration_error = None
            await db.flush()
            await db.refresh(config)
            result = FunctionView(function_id=config.function_id, function_name=config.function_name,
                                  capability=config.capability, primary_provider_id=model.provider_id,
                                  model_id=model.id,
                                  model_display_name=model.display_name or model.remote_model_id,
                                  configuration_error=None, default_status="ready",
                                  selectable=True, updated_at=config.updated_at)
    except IntegrityError:
        if creating:
            raise HTTPException(409, "Function changed concurrently; refresh and retry.") from None
        raise
    return Envelope(data=result)
