"""Canonical Function default write; legacy fallback columns remain untouched."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.api.routes.ai_catalog import Envelope, FunctionView
from app.database import async_session_factory
from app.models import APIKey, CatalogModel, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig
from app.services.ai_routing import _PUBLIC_CATALOG_PROVIDERS, _keyless_allowed
from app.services.capability_registry import compatible, model_evidence
from app.services.credential_service import lock_catalog_provider


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
    return await db.scalar(query.limit(1)) is not None


@router.put("/functions/{function_id}", response_model=Envelope[FunctionView])
async def set_function_default(function_id: str, body: FunctionDefaultInput,
                               sessions: async_sessionmaker = Depends(get_function_sessions)):
    async with sessions.begin() as db:
        config = await db.get(AIFunctionConfig, function_id)
        if config is None:
            raise HTTPException(404, "Function does not exist.")
        model = await db.get(CatalogModel, body.model_id)
        if model is None:
            raise HTTPException(404, "Catalog model does not exist.")
        # Refresh and credential writes take this same provider lock. Re-read after
        # acquiring it so a just-retired model cannot become the saved default.
        await lock_catalog_provider(db, model.provider_id)
        await db.refresh(model)
        provider = await db.get(Provider, model.provider_id, populate_existing=True)
        if (provider is None or not provider.enabled or not model.enabled or model.retired_at is not None
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
                              model_id=model.id, configuration_error=None, default_status="ready",
                              selectable=True, updated_at=config.updated_at)
    return Envelope(data=result)
