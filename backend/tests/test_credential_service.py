"""Real encryption/database tests; every credential and master key is synthetic."""
import importlib.util
import json
import os
from dataclasses import asdict

import pytest
from cryptography.fernet import Fernet
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import APIKey, CatalogModel, KeyModelAccess, Provider


@pytest.fixture
def credentials():
    assert importlib.util.find_spec("app.services.credential_service") is not None, "credential service is missing"
    from app.services import credential_service
    return credential_service


@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite://")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as connection:
        for model in (Provider, APIKey, CatalogModel, KeyModelAccess):
            await connection.run_sync(model.__table__.create)
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        session.add_all([Provider(id=p, name=p, provider_type="llm") for p in ("one", "two")])
        await session.commit()
        yield session
    await engine.dispose()


async def test_first_use_persists_private_master_and_only_encrypted_secret(credentials, db, tmp_path):
    service = await credentials.CredentialService.open(db, tmp_path)
    secret = "synthetic-secret-1234567890"
    dto = await service.create("one", secret)
    await db.commit()
    row = await db.get(APIKey, dto.id)
    assert row.ciphertext != secret and secret not in row.ciphertext
    assert len(dto.id) == 36 and dto.masked_key == "****7890"
    assert secret not in json.dumps(asdict(dto), default=str)
    assert not {"ciphertext", "fingerprint", "secret", "api_key"} & asdict(dto).keys()
    master_file = tmp_path / ".api_key_master_key"
    if os.name != "nt":
        assert master_file.stat().st_mode & 0o777 == 0o600
    reopened = await credentials.CredentialService.open(db, tmp_path)
    assert await reopened.reveal(dto.id) == secret
    assert (await reopened.list_keys("one"))[0].id == dto.id


async def test_duplicate_detection_is_provider_scoped_and_keyed(credentials, db, tmp_path):
    service = await credentials.CredentialService.open(db, tmp_path)
    first = await service.create("one", "same-synthetic-secret")
    with pytest.raises(credentials.DuplicateCredentialError) as exc:
        await service.create("one", "same-synthetic-secret")
    assert "same-synthetic-secret" not in str(exc.value)
    second = await service.create("two", "same-synthetic-secret")
    assert first.id != second.id
    one, two = await db.get(APIKey, first.id), await db.get(APIKey, second.id)
    assert one.fingerprint != two.fingerprint
    assert one.ciphertext != two.ciphertext


async def test_lost_master_with_existing_rows_does_not_generate_replacement(credentials, db, tmp_path):
    service = await credentials.CredentialService.open(db, tmp_path)
    await service.create("one", "synthetic-secret")
    await db.commit()
    master_file = tmp_path / ".api_key_master_key"
    master_file.unlink()
    with pytest.raises(credentials.CredentialMasterKeyError):
        await credentials.CredentialService.open(db, tmp_path)
    assert not master_file.exists()


@pytest.mark.parametrize("master", [b"invalid", None])
async def test_invalid_or_wrong_master_fails_closed(credentials, db, tmp_path, master):
    service = await credentials.CredentialService.open(db, tmp_path)
    await service.create("one", "synthetic-secret")
    await db.commit()
    with pytest.raises(credentials.CredentialError):
        await credentials.CredentialService.open(db, tmp_path, master_key=master or Fernet.generate_key())


async def test_corrupt_ciphertext_never_returns_blank_or_raw_value(credentials, db, tmp_path):
    service = await credentials.CredentialService.open(db, tmp_path)
    dto = await service.create("one", "synthetic-secret")
    row = await db.get(APIKey, dto.id)
    row.ciphertext = "corrupt-secret-sentinel"
    await db.flush()
    with pytest.raises(credentials.CredentialDecryptionError) as exc:
        await service.reveal(dto.id)
    assert "corrupt-secret-sentinel" not in str(exc.value)


async def test_delete_credential_preserves_catalog_and_other_access(credentials, db, tmp_path):
    service = await credentials.CredentialService.open(db, tmp_path)
    first = await service.create("one", "first-synthetic-key")
    second = await service.create("one", "second-synthetic-key")
    model = CatalogModel(provider_id="one", remote_model_id="models/CaseSensitive")
    db.add(model)
    await db.flush()
    db.add_all([KeyModelAccess(key_id=k.id, model_id=model.id) for k in (first, second)])
    await db.commit()
    assert await service.delete(first.id)
    await db.commit()
    assert await db.get(CatalogModel, model.id) is not None
    assert [a.key_id for a in (await db.scalars(select(KeyModelAccess))).all()] == [second.id]
    assert not await service.delete(first.id)


@pytest.mark.parametrize("secret", ["", "   ", " padded "])
async def test_invalid_secrets_are_rejected_without_echo(credentials, db, tmp_path, secret):
    service = await credentials.CredentialService.open(db, tmp_path)
    with pytest.raises(credentials.CredentialValidationError):
        await service.create("one", secret)
    assert (await db.scalars(select(APIKey))).all() == []


async def test_short_secret_is_completely_masked_and_missing_id_is_safe(credentials, db, tmp_path):
    service = await credentials.CredentialService.open(db, tmp_path, master_key=Fernet.generate_key())
    dto = await service.create("one", "tiny")
    assert dto.masked_key == "****"
    assert not (tmp_path / ".api_key_master_key").exists()
    with pytest.raises(credentials.CredentialNotFoundError):
        await service.reveal("absent")


async def test_ciphertext_cannot_be_swapped_between_credentials(credentials, db, tmp_path):
    service = await credentials.CredentialService.open(db, tmp_path)
    first = await service.create("one", "first-secret")
    second = await service.create("two", "second-secret")
    row = await db.get(APIKey, second.id)
    row.ciphertext = (await db.get(APIKey, first.id)).ciphertext
    await db.flush()
    with pytest.raises(credentials.CredentialDecryptionError):
        await service.reveal(second.id)


async def test_caller_can_roll_back_created_credentials(credentials, db, tmp_path):
    service = await credentials.CredentialService.open(db, tmp_path)
    dto = await service.create("one", "rolled-back-secret")
    await db.rollback()
    assert await db.get(APIKey, dto.id) is None


async def test_invalid_persisted_master_is_not_overwritten(credentials, db, tmp_path):
    path = tmp_path / ".api_key_master_key"
    path.write_bytes(b"broken-master")
    with pytest.raises(credentials.CredentialMasterKeyError):
        await credentials.CredentialService.open(db, tmp_path)
    assert path.read_bytes() == b"broken-master"


async def test_database_error_hides_secret_and_allows_caller_rollback(credentials, db, tmp_path):
    service = await credentials.CredentialService.open(db, tmp_path)
    with pytest.raises(credentials.CredentialValidationError) as exc:
        await service.create("absent", "secret-sentinel")
    assert "secret-sentinel" not in str(exc.value)
    await db.rollback()
    assert (await service.list_keys()) == []


async def test_fingerprint_depends_on_master_key(credentials, db, tmp_path):
    first = await credentials.CredentialService.open(db, tmp_path, master_key=Fernet.generate_key())
    dto = await first.create("one", "same-synthetic-secret")
    fingerprint = (await db.get(APIKey, dto.id)).fingerprint
    await first.delete(dto.id)
    await db.commit()
    second = await credentials.CredentialService.open(db, tmp_path, master_key=Fernet.generate_key())
    replacement = await second.create("one", "same-synthetic-secret")
    assert (await db.get(APIKey, replacement.id)).fingerprint != fingerprint
