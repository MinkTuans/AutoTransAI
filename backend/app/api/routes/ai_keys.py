"""Canonical encrypted key management and explicit catalog refresh."""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import get_settings
from app.database import async_session_factory
from app.models import Provider
from app.services.credential_service import (CredentialDTO, CredentialError, CredentialService,
                                             CredentialNotFoundError, DuplicateCredentialError)
from app.services.model_refresh_service import ModelRefreshService, RefreshOutcome


class SafeKeyRoute(APIRoute):
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
                # The global handler includes str(exc), which can hold a submitted secret.
                return JSONResponse(status_code=500, content={"success": False, "detail": "Key operation failed."})

        return safe_handler


router = APIRouter(prefix="/api/ai", tags=["ai-keys"], route_class=SafeKeyRoute)


@dataclass(frozen=True)
class KeyAPIContext:
    sessions: async_sessionmaker
    data_dir: Path
    refresh: ModelRefreshService


def get_key_api_context() -> KeyAPIContext:
    return KeyAPIContext(async_session_factory, get_settings().DATA_DIR,
                         ModelRefreshService(async_session_factory, get_settings().DATA_DIR))


class KeyInput(BaseModel):
    key: str = Field(min_length=1)


class KeyView(BaseModel):
    id: str
    provider_id: str
    masked_key: str
    enabled: bool
    revision: int
    created_at: datetime


class DiscoveryView(BaseModel):
    status: str
    access_scope: str = "unknown"
    error_code: str | None = None
    verified_for_generation: bool = False


class AddKeyView(BaseModel):
    key: KeyView
    discovery: DiscoveryView


class EnabledInput(BaseModel):
    enabled: bool


class RefreshKeyResult(BaseModel):
    key_id: str
    status: str
    access_scope: str
    error_code: str | None
    complete: bool


class ProviderRefreshView(BaseModel):
    keys_scanned: int
    retired: int
    status: str
    reason: str | None = None
    results: list[RefreshKeyResult]


class RefreshView(BaseModel):
    id: str
    status: str
    providers: dict[str, ProviderRefreshView] = Field(default_factory=dict)
    error_code: str | None = None


def _key_view(key: CredentialDTO) -> KeyView:
    return KeyView.model_validate(key, from_attributes=True)


def _discovery_view(outcome: RefreshOutcome, provider_id: str, key_id: str) -> DiscoveryView:
    reports = outcome.summary.get("providers", {})
    rows = reports.get(provider_id, {}).get("results", [])
    result = next((row for row in rows if row.get("key_id") == key_id), None)
    if result is None:
        return DiscoveryView(status=outcome.status, error_code="key_unavailable")
    return DiscoveryView(status=result["status"], access_scope=result["access_scope"],
                         error_code=result["error_code"])


@router.get("/providers/{provider_id}/keys")
async def list_keys(provider_id: str, context: KeyAPIContext = Depends(get_key_api_context)) -> dict:
    async with context.sessions() as db:
        if await db.get(Provider, provider_id) is None:
            raise HTTPException(404, "Provider does not exist.")
        credentials = await CredentialService.open(db, context.data_dir)
        return {"success": True, "data": [_key_view(key).model_dump(mode="json")
                                          for key in await credentials.list_keys(provider_id)]}


@router.post("/providers/{provider_id}/keys", status_code=201)
async def add_key(provider_id: str, body: KeyInput,
                  context: KeyAPIContext = Depends(get_key_api_context)) -> dict:
    try:
        async with context.sessions.begin() as db:
            credentials = await CredentialService.open(db, context.data_dir)
            key = await credentials.create(provider_id, body.key, enabled=False)
    except DuplicateCredentialError:
        raise HTTPException(409, "Credential already exists for this provider.") from None
    except CredentialError:
        raise HTTPException(400, "Credential cannot be added.") from None
    outcome = await context.refresh.discover_key(key.id)
    discovery = _discovery_view(outcome, provider_id, key.id)
    if outcome.status == "complete" and discovery.status == "complete" and discovery.access_scope == "credential" and discovery.error_code is None:
        try:
            async with context.sessions.begin() as db:
                activated = await (await CredentialService.open(db, context.data_dir)).enable_if_unchanged(
                    key.id, key.revision)
            if activated is None:
                raise HTTPException(409, "Credential changed during discovery.")
            key = activated
        except CredentialError:
            raise HTTPException(409, "Credential changed during discovery.") from None
    view = AddKeyView(key=_key_view(key), discovery=discovery)
    return {"success": True, "data": view.model_dump(mode="json")}


@router.patch("/keys/{key_id}")
async def set_key_enabled(key_id: str, body: EnabledInput,
                          context: KeyAPIContext = Depends(get_key_api_context)) -> dict:
    try:
        async with context.sessions() as db:
            current = await (await CredentialService.open(db, context.data_dir)).get(key_id)
        if not body.enabled:
            async with context.sessions.begin() as db:
                current = await (await CredentialService.open(db, context.data_dir)).set_enabled(key_id, False)
            view = AddKeyView(key=_key_view(current), discovery=DiscoveryView(status="disabled"))
        elif current.enabled:
            view = AddKeyView(key=_key_view(current), discovery=DiscoveryView(status="already_enabled"))
        else:
            outcome = await context.refresh.discover_key(key_id)
            discovery = _discovery_view(outcome, current.provider_id, key_id)
            if outcome.status == "stale":
                raise HTTPException(409, "Credential changed during discovery.")
            if (outcome.status == "complete" and discovery.status == "complete"
                    and discovery.access_scope == "credential" and discovery.error_code is None):
                async with context.sessions.begin() as db:
                    activated = await (await CredentialService.open(db, context.data_dir)).enable_if_unchanged(
                        key_id, current.revision)
                if activated is None:
                    raise HTTPException(409, "Credential changed during discovery.")
                current = activated
            view = AddKeyView(key=_key_view(current), discovery=discovery)
        return {"success": True, "data": view.model_dump(mode="json")}
    except CredentialNotFoundError:
        raise HTTPException(404, "Credential does not exist.") from None


@router.delete("/keys/{key_id}")
async def delete_key(key_id: str, context: KeyAPIContext = Depends(get_key_api_context)) -> dict:
    async with context.sessions.begin() as db:
        deleted = await (await CredentialService.open(db, context.data_dir)).delete(key_id)
    if not deleted:
        raise HTTPException(404, "Credential does not exist.")
    return {"success": True, "data": {"deleted": True}}


@router.post("/models/refresh")
async def refresh_models(context: KeyAPIContext = Depends(get_key_api_context)) -> dict:
    outcome = await context.refresh.refresh()
    data = RefreshView.model_validate({"id": outcome.id, "status": outcome.status,
                                      **outcome.summary}).model_dump(mode="json")
    return {"success": outcome.status == "complete", "data": data}
