from __future__ import annotations

import json
import uuid
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.config import get_settings
from app.core.encryption import encrypt_data
from app.core.open_browser import oauth_done_html
from app.models.video_editor import TikTokAccount
from app.services.video_editor.tiktok_oauth import (
    DEFAULT_SCOPES,
    TOKEN_URL,
    USER_INFO_FIELDS,
    USER_INFO_URL,
    build_authorize_url,
    generate_pkce,
    generate_state,
    parse_token_payload,
    parse_user_info,
)

router = APIRouter(prefix="/tiktok", tags=["tiktok"])

# state -> {code_verifier, redirect_uri}
_oauth_sessions: dict[str, dict[str, str]] = {}


def _redirect_uri() -> str:
    curr = get_settings()
    return curr.TIKTOK_REDIRECT_URI or f"http://{curr.HOST}:{curr.PORT}/api/tiktok/oauth-callback"


def _require_tiktok_app() -> tuple[str, str, str]:
    curr = get_settings()
    if not curr.TIKTOK_CLIENT_KEY or not curr.TIKTOK_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="TikTok OAuth chưa cấu hình trong .env (TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET)",
        )
    scopes = (curr.TIKTOK_SCOPES or DEFAULT_SCOPES).strip() or DEFAULT_SCOPES
    return curr.TIKTOK_CLIENT_KEY, curr.TIKTOK_CLIENT_SECRET, scopes


async def persist_tiktok_account(
    db: AsyncSession,
    token_payload: dict,
    user_payload: dict,
) -> TikTokAccount:
    token = parse_token_payload(token_payload)
    user = parse_user_info(user_payload)
    open_id = token["open_id"]
    display_name = user.get("display_name") or "TikTok"
    encrypted = encrypt_data(json.dumps(token))

    stmt = select(TikTokAccount).where(TikTokAccount.open_id == open_id)
    result = await db.execute(stmt)
    existing = result.scalars().first()
    if existing:
        existing.credentials_json = encrypted
        existing.display_name = display_name
        existing.avatar_url = user.get("avatar_url") or existing.avatar_url
        existing.is_active = True
        account = existing
    else:
        account = TikTokAccount(
            id=str(uuid.uuid4()),
            open_id=open_id,
            display_name=display_name,
            avatar_url=user.get("avatar_url") or None,
            credentials_json=encrypted,
            is_active=True,
        )
        db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


async def _exchange_code(
    *,
    client_key: str,
    client_secret: str,
    code: str,
    redirect_uri: str,
    code_verifier: str,
) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(
            TOKEN_URL,
            data={
                "client_key": client_key,
                "client_secret": client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded", "Cache-Control": "no-cache"},
        )
        payload = res.json()
    return parse_token_payload(payload)


async def _fetch_user_info(access_token: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        res = await client.get(
            USER_INFO_URL,
            params={"fields": USER_INFO_FIELDS},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return res.json()


@router.get("/auth-url")
async def get_auth_url():
    client_key, _secret, scopes = _require_tiktok_app()
    redirect_uri = _redirect_uri()
    verifier, challenge = generate_pkce()
    state = generate_state()
    _oauth_sessions[state] = {"code_verifier": verifier, "redirect_uri": redirect_uri}
    auth_url = build_authorize_url(
        client_key=client_key,
        redirect_uri=redirect_uri,
        state=state,
        code_challenge=challenge,
        scopes=scopes,
    )
    return {"auth_url": auth_url, "state": state}


@router.get("/oauth-callback")
async def oauth_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    if error:
        html = oauth_done_html("TikTok", False, error_description or error)
        return HTMLResponse(content=html, status_code=400)
    if not code or not state:
        html = oauth_done_html("TikTok", False, "Thiếu mã ủy quyền từ TikTok.")
        return HTMLResponse(content=html, status_code=400)

    session = _oauth_sessions.pop(state, None)
    if not session:
        html = oauth_done_html("TikTok", False, "Phiên đăng nhập hết hạn. Bấm Kết nối TikTok lại trong app.")
        return HTMLResponse(content=html, status_code=400)

    try:
        client_key, client_secret, _scopes = _require_tiktok_app()
        token_payload = await _exchange_code(
            client_key=client_key,
            client_secret=client_secret,
            code=code,
            redirect_uri=session["redirect_uri"],
            code_verifier=session["code_verifier"],
        )
        user_payload = await _fetch_user_info(token_payload["access_token"])
        account = await persist_tiktok_account(db, token_payload, user_payload)
        html = oauth_done_html("TikTok", True, f"Tài khoản: {account.display_name}")
        return HTMLResponse(content=html)
    except HTTPException as exc:
        html = oauth_done_html("TikTok", False, str(exc.detail))
        return HTMLResponse(content=html, status_code=exc.status_code)
    except Exception as exc:
        html = oauth_done_html("TikTok", False, str(exc))
        return HTMLResponse(content=html, status_code=500)


@router.get("/accounts")
async def list_accounts(db: AsyncSession = Depends(get_db)):
    stmt = select(TikTokAccount).where(TikTokAccount.is_active == True)  # noqa: E712
    result = await db.execute(stmt)
    accounts = result.scalars().all()
    return [
        {
            "id": acc.id,
            "open_id": acc.open_id,
            "channel_id": acc.open_id,
            "channel_name": acc.display_name,
            "display_name": acc.display_name,
            "avatar_url": acc.avatar_url,
            "created_at": acc.created_at,
        }
        for acc in accounts
    ]


@router.delete("/accounts/{id}")
async def disconnect_account(id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(TikTokAccount).where(TikTokAccount.id == id)
    result = await db.execute(stmt)
    account = result.scalars().first()
    if not account:
        raise HTTPException(status_code=404, detail="TikTok account not found")
    account.is_active = False
    await db.commit()
    return {"success": True}
