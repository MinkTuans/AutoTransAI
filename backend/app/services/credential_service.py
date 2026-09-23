"""Fail-closed credentials for the canonical catalog; never reads legacy key stores.

Call ``open`` with a private DATA_DIR and optional explicit Fernet master key.
The caller owns the session and transaction (methods flush, never commit).
After a database write failure the caller must roll back the transaction.
Only ``reveal`` returns plaintext, for internal provider requests, never API DTOs.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime
import hashlib
import hmac
import json
import os
from pathlib import Path
from uuid import uuid4

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import APIKey
from app.models.provider import Provider


async def lock_catalog_provider(session: AsyncSession, provider_id: str) -> None:
    """UPDATE takes a SQLite write lock / MySQL row lock until caller commit.

    Every credential mutation and catalog reconciliation uses this lock in provider
    ID order. The increment also invalidates discovery staged before the mutation.
    """
    result = await session.execute(update(Provider).where(Provider.id == provider_id).values(
        catalog_revision=Provider.catalog_revision + 1,
    ).execution_options(synchronize_session=False))
    if not result.rowcount:
        raise CredentialValidationError("Credential provider is unavailable.")


class CredentialError(Exception):
    """Safe to expose as an error message; never includes secret input."""


class CredentialMasterKeyError(CredentialError):
    pass


class CredentialDecryptionError(CredentialError):
    pass


class CredentialValidationError(CredentialError):
    pass


class DuplicateCredentialError(CredentialError):
    pass


class CredentialNotFoundError(CredentialError):
    pass


@dataclass(frozen=True)
class CredentialDTO:
    id: str
    provider_id: str
    masked_key: str
    enabled: bool
    revision: int
    created_at: datetime


def _dto(row: APIKey) -> CredentialDTO:
    return CredentialDTO(row.id, row.provider_id, row.masked_key, row.enabled, row.revision, row.created_at)


def _load_master(path: Path, *, allow_create: bool) -> bytes:
    """Exclusive creation prevents competing first-use writers replacing a master."""
    try:
        if not path.exists() and allow_create:
            path.parent.mkdir(parents=True, exist_ok=True)
            try:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                pass  # Another process created it; use that key, never overwrite it.
            else:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(Fernet.generate_key())
                    handle.flush()
                    os.fsync(handle.fileno())
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        with os.fdopen(os.open(path, flags), "rb") as handle:
            return handle.read(128).strip()
    except OSError:
        raise CredentialMasterKeyError("Credential master key is missing or unreadable; restore the original key.") from None


class CredentialService:
    def __init__(self, session: AsyncSession, master_key: bytes):
        self._session = session
        try:
            self._fernet = Fernet(master_key)
            raw_key = base64.urlsafe_b64decode(master_key)
        except (ValueError, TypeError):
            raise CredentialMasterKeyError("Credential master key is invalid.") from None
        # Domain separation: fingerprints do not reuse Fernet's encryption/signing keys.
        self._fingerprint_key = hmac.digest(raw_key, b"autotransai/api-key-fingerprint/v1", "sha256")

    @classmethod
    async def open(
        cls, session: AsyncSession, data_dir: Path, *, master_key: bytes | str | None = None
    ) -> CredentialService:
        first = await session.scalar(select(APIKey).limit(1))
        if master_key is None:
            master_key = _load_master(Path(data_dir) / ".api_key_master_key", allow_create=first is None)
        if isinstance(master_key, str):
            master_key = master_key.encode("utf-8")
        service = cls(session, master_key)
        if first is not None:
            service._decrypt(first)  # Wrong replacements must also prevent subsequent writes.
        return service

    def _decrypt(self, row: APIKey) -> str:
        try:
            payload = json.loads(self._fernet.decrypt(row.ciphertext.encode("utf-8")))
            if (
                payload["version"] != 1 or payload["id"] != row.id
                or payload["provider_id"] != row.provider_id
                or not isinstance(payload["secret"], str) or not payload["secret"]
            ):
                raise ValueError
            return payload["secret"]
        except (InvalidToken, ValueError, TypeError, KeyError, UnicodeError):
            raise CredentialDecryptionError("Credential cannot be decrypted; restore the original master key or replace the credential.") from None

    async def create(self, provider_id: str, secret: str, *, enabled: bool = True) -> CredentialDTO:
        if not isinstance(secret, str) or not secret or secret != secret.strip():
            raise CredentialValidationError("Credential must be nonempty and have no surrounding whitespace.")
        message = json.dumps([provider_id, secret], separators=(",", ":")).encode("utf-8")
        fingerprint = hmac.new(self._fingerprint_key, message, hashlib.sha256).hexdigest()
        await lock_catalog_provider(self._session, provider_id)
        duplicate = await self._session.scalar(select(APIKey.id).where(
            APIKey.provider_id == provider_id, APIKey.fingerprint == fingerprint,
        ))
        if duplicate:
            raise DuplicateCredentialError("Credential already exists for this provider.")
        key_id = str(uuid4())
        payload = json.dumps({"version": 1, "id": key_id, "provider_id": provider_id, "secret": secret}).encode("utf-8")
        row = APIKey(
            id=key_id, provider_id=provider_id,
            ciphertext=self._fernet.encrypt(payload).decode("ascii"), fingerprint=fingerprint,
            masked_key="****" + (secret[-4:] if len(secret) > 8 else ""),
            enabled=enabled,
        )
        try:
            self._session.add(row)
            await self._session.flush()
        except IntegrityError:
            # A uniqueness race or missing provider must not leak SQL parameters.
            # Do not use a savepoint here: SQLite's legacy transaction mode can
            # commit a first-write savepoint independently of the caller's rollback.
            raise CredentialValidationError("Credential conflicts with an existing entry or its provider is unavailable.") from None
        return _dto(row)

    async def list_keys(self, provider_id: str | None = None) -> list[CredentialDTO]:
        query = select(APIKey).order_by(APIKey.created_at, APIKey.id)
        if provider_id is not None:
            query = query.where(APIKey.provider_id == provider_id)
        return [_dto(row) for row in (await self._session.scalars(query)).all()]

    async def reveal(self, key_id: str) -> str:
        row = await self._session.get(APIKey, key_id)
        if row is None:
            raise CredentialNotFoundError("Credential does not exist.")
        return self._decrypt(row)

    async def delete(self, key_id: str) -> bool:
        row = await self._session.get(APIKey, key_id)
        if row is None:
            return False
        await lock_catalog_provider(self._session, row.provider_id)
        await self._session.delete(row)
        await self._session.flush()
        return True

    async def set_enabled(self, key_id: str, enabled: bool) -> CredentialDTO:
        row = await self._session.get(APIKey, key_id)
        if row is None:
            raise CredentialNotFoundError("Credential does not exist.")
        await lock_catalog_provider(self._session, row.provider_id)
        await self._session.refresh(row)
        row.enabled = bool(enabled)
        row.revision += 1
        await self._session.flush()
        return _dto(row)

    async def enable_if_unchanged(self, key_id: str, expected_revision: int) -> CredentialDTO | None:
        """Activate a newly discovered key only if no writer changed it since creation."""
        provider_id = await self._session.scalar(select(APIKey.provider_id).where(APIKey.id == key_id))
        if provider_id is None:
            return None
        await lock_catalog_provider(self._session, provider_id)
        row = await self._session.scalar(select(APIKey).where(APIKey.id == key_id)
                                         .execution_options(populate_existing=True))
        if row is None or row.enabled or row.revision != expected_revision:
            return None
        row.enabled = True
        row.revision += 1
        await self._session.flush()
        return _dto(row)

    async def rotate(self, key_id: str, secret: str) -> CredentialDTO:
        if not isinstance(secret, str) or not secret or secret != secret.strip():
            raise CredentialValidationError("Credential must be nonempty and have no surrounding whitespace.")
        row = await self._session.get(APIKey, key_id)
        if row is None:
            raise CredentialNotFoundError("Credential does not exist.")
        await lock_catalog_provider(self._session, row.provider_id)
        await self._session.refresh(row)
        message = json.dumps([row.provider_id, secret], separators=(",", ":")).encode("utf-8")
        fingerprint = hmac.new(self._fingerprint_key, message, hashlib.sha256).hexdigest()
        if await self._session.scalar(select(APIKey.id).where(
            APIKey.provider_id == row.provider_id, APIKey.fingerprint == fingerprint, APIKey.id != key_id,
        )):
            raise DuplicateCredentialError("Credential already exists for this provider.")
        payload = json.dumps({"version": 1, "id": key_id, "provider_id": row.provider_id, "secret": secret}).encode("utf-8")
        row.ciphertext = self._fernet.encrypt(payload).decode("ascii")
        row.fingerprint = fingerprint
        row.masked_key = "****" + (secret[-4:] if len(secret) > 8 else "")
        row.revision += 1
        # Old listing evidence cannot be attributed to the replacement credential.
        from sqlalchemy import delete
        from app.models.ai_catalog import KeyModelAccess
        await self._session.execute(delete(KeyModelAccess).where(KeyModelAccess.key_id == key_id))
        await self._session.flush()
        return _dto(row)
