"""TikTok Login Kit OAuth (desktop PKCE) and account persistence."""

from __future__ import annotations

import hashlib
import json
from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlparse

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.encryption import decrypt_data
from app.database import Base
from app.models.video_editor import TikTokAccount
from app.services.video_editor.tiktok_oauth import (
    DEFAULT_SCOPES,
    build_authorize_url,
    generate_pkce,
    parse_token_payload,
    parse_user_info,
    pkce_challenge,
)


def test_tiktok_pkce_challenge_is_hex_sha256_not_base64():
    verifier = "a" * 43
    challenge = pkce_challenge(verifier)
    assert challenge == hashlib.sha256(verifier.encode("ascii")).hexdigest()
    assert len(challenge) == 64
    assert challenge.isalnum()


def test_generate_pkce_length_and_roundtrip():
    verifier, challenge = generate_pkce()
    assert 43 <= len(verifier) <= 128
    assert pkce_challenge(verifier) == challenge


def test_authorize_url_contains_desktop_pkce_and_publish_scopes():
    verifier, challenge = generate_pkce()
    url = build_authorize_url(
        client_key="tt_client_key",
        redirect_uri="http://127.0.0.1:8000/api/tiktok/oauth-callback",
        state="csrf-state-1",
        code_challenge=challenge,
        scopes=DEFAULT_SCOPES,
    )
    parsed = urlparse(url)
    assert parsed.scheme == "https"
    assert parsed.netloc == "www.tiktok.com"
    assert parsed.path.rstrip("/") == "/v2/auth/authorize"
    qs = parse_qs(parsed.query)
    assert qs["client_key"] == ["tt_client_key"]
    assert qs["response_type"] == ["code"]
    assert qs["code_challenge"] == [challenge]
    assert qs["code_challenge_method"] == ["S256"]
    assert qs["state"] == ["csrf-state-1"]
    assert qs["redirect_uri"] == ["http://127.0.0.1:8000/api/tiktok/oauth-callback"]
    scope = qs["scope"][0]
    assert "user.info.basic" in scope
    assert "video.upload" in scope
    assert "video.publish" in scope


def test_parse_token_and_user_info():
    token = parse_token_payload(
        {
            "access_token": "act.abc",
            "refresh_token": "rft.abc",
            "open_id": "oid-1",
            "expires_in": 86400,
            "refresh_expires_in": 31536000,
            "scope": "user.info.basic,video.publish",
            "token_type": "Bearer",
        }
    )
    assert token["open_id"] == "oid-1"
    assert token["access_token"] == "act.abc"

    user = parse_user_info(
        {
            "data": {
                "user": {
                    "open_id": "oid-1",
                    "display_name": "Xói Xám",
                    "avatar_url": "https://example.com/a.png",
                }
            }
        }
    )
    assert user["display_name"] == "Xói Xám"
    assert user["open_id"] == "oid-1"


def test_token_error_payload_raises():
    with pytest.raises(ValueError, match="Redirect_uri is not matched"):
        parse_token_payload(
            {
                "error": "invalid_request",
                "error_description": "Redirect_uri is not matched",
            }
        )


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_callback_upserts_encrypted_tiktok_account(async_db: AsyncSession):
    from app.api.routers import tiktok as tiktok_router

    tiktok_router._oauth_sessions["csrf-state-1"] = {
        "code_verifier": "v" * 43,
        "redirect_uri": "http://127.0.0.1:8000/api/tiktok/oauth-callback",
    }

    token_payload = {
        "access_token": "act.live",
        "refresh_token": "rft.live",
        "open_id": "open-xyz",
        "expires_in": 86400,
        "refresh_expires_in": 31536000,
        "scope": "user.info.basic,video.publish",
        "token_type": "Bearer",
    }
    user_payload = {
        "data": {"user": {"open_id": "open-xyz", "display_name": "Kênh TikTok Test"}}
    }

    with patch.object(tiktok_router, "_exchange_code", new=AsyncMock(return_value=token_payload)):
        with patch.object(tiktok_router, "_fetch_user_info", new=AsyncMock(return_value=user_payload)):
            account = await tiktok_router.persist_tiktok_account(
                db=async_db,
                token_payload=token_payload,
                user_payload=user_payload,
            )

    assert account.open_id == "open-xyz"
    assert account.display_name == "Kênh TikTok Test"
    assert account.is_active is True
    creds = json.loads(decrypt_data(account.credentials_json))
    assert creds["access_token"] == "act.live"
    assert creds["refresh_token"] == "rft.live"
