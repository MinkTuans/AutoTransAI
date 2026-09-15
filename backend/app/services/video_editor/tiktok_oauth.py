"""TikTok Login Kit (desktop) — PKCE with hex SHA256, token + user info helpers."""

from __future__ import annotations

import hashlib
import secrets
import string
from urllib.parse import urlencode

AUTHORIZE_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
REVOKE_URL = "https://open.tiktokapis.com/v2/oauth/revoke/"
USER_INFO_URL = "https://open.tiktokapis.com/v2/user/info/"
USER_INFO_FIELDS = "open_id,union_id,avatar_url,display_name"

DEFAULT_SCOPES = "user.info.basic,video.upload,video.publish"

_PKCE_ALPHABET = string.ascii_letters + string.digits + "-._~"


def pkce_challenge(code_verifier: str) -> str:
    """TikTok desktop PKCE uses hex-encoded SHA256, not base64url."""
    return hashlib.sha256(code_verifier.encode("ascii")).hexdigest()


def generate_pkce(length: int = 64) -> tuple[str, str]:
    length = min(128, max(43, length))
    verifier = "".join(secrets.choice(_PKCE_ALPHABET) for _ in range(length))
    return verifier, pkce_challenge(verifier)


def generate_state() -> str:
    return secrets.token_urlsafe(24)


def build_authorize_url(
    *,
    client_key: str,
    redirect_uri: str,
    state: str,
    code_challenge: str,
    scopes: str = DEFAULT_SCOPES,
) -> str:
    query = urlencode(
        {
            "client_key": client_key,
            "response_type": "code",
            "scope": scopes,
            "redirect_uri": redirect_uri,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
    )
    return f"{AUTHORIZE_URL}?{query}"


def parse_token_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("TikTok token response is empty")
    if payload.get("error"):
        desc = payload.get("error_description") or payload.get("error")
        raise ValueError(str(desc))
    if not payload.get("access_token") or not payload.get("open_id"):
        raise ValueError("TikTok token response missing access_token/open_id")
    return {
        "access_token": payload["access_token"],
        "refresh_token": payload.get("refresh_token") or "",
        "open_id": payload["open_id"],
        "expires_in": int(payload.get("expires_in") or 0),
        "refresh_expires_in": int(payload.get("refresh_expires_in") or 0),
        "scope": payload.get("scope") or "",
        "token_type": payload.get("token_type") or "Bearer",
    }


def parse_user_info(payload: dict) -> dict:
    user = {}
    if isinstance(payload, dict):
        data = payload.get("data") or {}
        if isinstance(data, dict):
            user = data.get("user") or data
    if not isinstance(user, dict):
        user = {}
    return {
        "open_id": user.get("open_id") or "",
        "union_id": user.get("union_id") or "",
        "display_name": user.get("display_name") or user.get("username") or "TikTok",
        "avatar_url": user.get("avatar_url") or "",
    }
