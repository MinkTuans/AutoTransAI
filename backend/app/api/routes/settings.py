"""
Settings API router — Endpoints for System Settings, AI Functions, Models Catalog,
Social Accounts, and Storage configuration.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session as get_db

from app.schemas.settings_schema import (
    AIFunctionConfigUpdateRequest,
    AddCustomModelRequest,
    AddSocialAccountRequest,
    SystemSettingsUpdateRequest,
    TestStorageRequest,
)
from app.services.settings_service import SettingsService
from app.core import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=dict)
async def get_settings(db: AsyncSession = Depends(get_db)):
    """Get all system settings."""
    await SettingsService.ensure_defaults_seeded(db)
    data = await SettingsService.get_all_settings(db)
    return {"success": True, "data": data}


@router.put("", response_model=dict)
async def update_settings(
    body: SystemSettingsUpdateRequest, db: AsyncSession = Depends(get_db)
):
    """Update system settings."""
    data = await SettingsService.update_settings(db, body.settings)
    return {"success": True, "data": data, "message": "Settings updated successfully"}


@router.get("/functions", response_model=dict)
async def get_ai_functions(db: AsyncSession = Depends(get_db)):
    """List all AI function configurations with eligible candidate providers."""
    await SettingsService.ensure_defaults_seeded(db)
    functions = await SettingsService.get_function_configs(db)

    # Attach eligible providers for each function based on capabilities and configured status
    for fn in functions:
        fn["eligible_providers"] = await SettingsService.get_eligible_providers_for_function(
            db, fn["function_id"]
        )

    return {"success": True, "data": functions}


@router.put("/functions/{function_id}", response_model=dict)
async def update_ai_function(
    function_id: str,
    body: AIFunctionConfigUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update AI function primary provider, model, and fallback settings."""
    try:
        updated = await SettingsService.update_function_config(
            db, function_id, body.model_dump(exclude_none=True)
        )
        return {"success": True, "data": updated, "message": f"AI Function '{function_id}' updated"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))


@router.get("/models", response_model=dict)
async def get_models(
    provider_id: Optional[str] = None, db: AsyncSession = Depends(get_db)
):
    """List AI models catalog."""
    await SettingsService.ensure_defaults_seeded(db)
    models = await SettingsService.get_models(db, provider_id=provider_id)
    return {"success": True, "data": models}


@router.post("/models", response_model=dict)
async def add_model(
    body: AddCustomModelRequest, db: AsyncSession = Depends(get_db)
):
    """Add a custom model definition to catalog."""
    try:
        model = await SettingsService.add_custom_model(db, body.model_dump())
        return {"success": True, "data": model, "message": "Custom model added"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.get("/social-accounts", response_model=dict)
async def get_social_accounts(db: AsyncSession = Depends(get_db)):
    """List connected social media accounts."""
    accs = await SettingsService.get_social_accounts(db)
    return {"success": True, "data": accs}


@router.post("/social-accounts", response_model=dict)
async def add_social_account(
    body: AddSocialAccountRequest, db: AsyncSession = Depends(get_db)
):
    """Add a social media account."""
    acc = await SettingsService.add_social_account(db, body.model_dump())
    return {"success": True, "data": acc, "message": f"Social account '{acc['account_name']}' added"}


@router.delete("/social-accounts/{account_id}", response_model=dict)
async def delete_social_account(
    account_id: str, db: AsyncSession = Depends(get_db)
):
    """Remove a social media account."""
    res = await SettingsService.delete_social_account(db, account_id)
    if not res:
        raise HTTPException(status_code=404, detail="Social account not found")
    return {"success": True, "message": "Social account removed"}


@router.post("/storage/test", response_model=dict)
async def test_storage_connection(body: TestStorageRequest):
    """Test Supabase Storage connection."""
    if body.storage_provider == "local":
        return {"success": True, "message": "Local Storage Fallback is operational."}

    try:
        from app.services.storage_service import _get_supabase_client, storage_service
        client = _get_supabase_client()
        if client:
            bucket = body.supabase_bucket_private or storage_service._get_bucket_name(False)
            res = client.storage.from_(bucket).list(limit=1)
            return {
                "success": True,
                "message": f"Supabase Storage Bucket '{bucket}' connection verified successfully!",
            }
        else:
            return {
                "success": False,
                "message": "Supabase Client not initialized. Please verify SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
            }
    except Exception as e:
        return {"success": False, "message": f"Supabase Storage Connection test failed: {str(e)}"}
