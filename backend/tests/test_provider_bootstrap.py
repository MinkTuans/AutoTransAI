"""Provider bootstrap contracts on disposable SQLite only."""
import importlib.util
import io
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

from app.models import CatalogModel, Provider
from app.providers.registry import ProviderRegistry


class StubProvider:
    def __init__(self, provider_id, name, requires_api_key):
        self.provider_id = provider_id
        self.provider_name = name
        self.requires_api_key = requires_api_key

    async def validate_configuration(self):
        raise AssertionError("bootstrap must not validate providers")


@pytest.mark.asyncio
@pytest.mark.parametrize("existing_source", ["manual", "discovered", "system"])
async def test_bootstrap_registers_once_and_preserves_existing_state(tmp_path, existing_source):
    from app.services.provider_bootstrap import bootstrap_providers

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'bootstrap.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Provider.__table__.create)
        await conn.run_sync(CatalogModel.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    registry = ProviderRegistry()
    registry.register_audio(StubProvider("edge_tts", "Edge TTS", False))
    registry.register_image(StubProvider("pollinations", "Pollinations", False))
    registry.register_image(StubProvider("local_image", "Local Image", False))
    registry.register_video(StubProvider("local_video", "Local Video", False))
    registry.register_llm(StubProvider("openai", "OpenAI", True))
    registry.register_vision(StubProvider("openai", "OpenAI Vision", True))
    async with sessions.begin() as db:
        db.add_all([
            Provider(id="edge_tts", name="My Edge", provider_type="audio", enabled=False,
                     requires_api_key=True, base_url="https://example.invalid"),
            Provider(id="custom", name="Custom", provider_type="image", is_custom=True),
        ])
        db.add(CatalogModel(id="existing", provider_id="edge_tts", remote_model_id="edge-tts",
                            source=existing_source, enabled=False, capability_status="FULL_UNKNOWN"))
    for _ in range(2):
        async with sessions.begin() as db:
            await bootstrap_providers(db, registry)
    async with sessions() as db:
        providers = {p.id: p for p in (await db.scalars(select(Provider))).all()}
        models = {(m.provider_id, m.remote_model_id): m for m in (await db.scalars(select(CatalogModel))).all()}
    assert set(providers) == {"edge_tts", "pollinations", "local_image", "local_video", "openai", "custom"}
    assert providers["edge_tts"].name == "My Edge" and not providers["edge_tts"].enabled
    assert providers["edge_tts"].base_url == "https://example.invalid"
    assert not providers["edge_tts"].requires_api_key
    assert providers["custom"].requires_api_key
    assert providers["openai"].requires_api_key and providers["openai"].provider_type == "llm"
    assert not providers["local_video"].requires_api_key
    assert set(models) == {("edge_tts", "edge-tts"), ("pollinations", "pollinations-default"),
                           ("local_image", "default")}
    assert models[("edge_tts", "edge-tts")].id == "existing"
    assert not models[("edge_tts", "edge-tts")].enabled
    assert models[("edge_tts", "edge-tts")].source == existing_source
    assert models[("edge_tts", "edge-tts")].capability_status == "FULL_UNKNOWN"
    for identity in (("pollinations", "pollinations-default"), ("local_image", "default")):
        model = models[identity]
        assert model.source == "system" and model.capability_status == "KNOWN"
        assert model.capabilities == ["IMAGE_GENERATION"]
    await engine.dispose()


@pytest.mark.asyncio
async def test_fresh_edge_route_has_known_tts_evidence(tmp_path):
    from app.services.provider_bootstrap import bootstrap_providers

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'edge.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Provider.__table__.create)
        await conn.run_sync(CatalogModel.__table__.create)
    registry = ProviderRegistry()
    registry.register_audio(StubProvider("edge_tts", "Edge TTS", False))
    sessions = async_sessionmaker(engine)
    async with sessions.begin() as db:
        await bootstrap_providers(db, registry)
    async with sessions() as db:
        model = (await db.scalars(select(CatalogModel))).one()
        assert (model.provider_id, model.remote_model_id, model.source) == ("edge_tts", "edge-tts", "system")
        assert model.capability_status == "KNOWN" and model.capabilities == ["TTS"]
    await engine.dispose()


def _revision():
    path = Path(__file__).parents[1] / "alembic/versions/20260923_provider_key_requirement.py"
    spec = importlib.util.spec_from_file_location("provider_key_requirement", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_migration_preserves_provider_and_defaults_unknown_to_keyed():
    engine = create_engine("sqlite://")
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE providers (id VARCHAR(50) PRIMARY KEY, name VARCHAR(100))"))
        conn.execute(text("INSERT INTO providers VALUES ('custom', 'Custom')"))
        with Operations.context(MigrationContext.configure(conn)):
            _revision().upgrade()
        assert conn.execute(text("SELECT id, requires_api_key FROM providers")).one() == ("custom", 1)
    engine.dispose()


def test_migration_compiles_offline_mysql():
    output = io.StringIO()
    context = MigrationContext.configure(dialect_name="mysql", opts={"as_sql": True, "output_buffer": output})
    with Operations.context(context):
        _revision().upgrade()
    assert "ADD COLUMN requires_api_key" in output.getvalue()
    assert "DEFAULT true" in output.getvalue()


@pytest.mark.asyncio
async def test_startup_commits_bootstrap_after_registration_and_sanitizes_failure(tmp_path, monkeypatch):
    from app import main

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'startup.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Provider.__table__.create)
        await conn.run_sync(CatalogModel.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    registry = ProviderRegistry()

    async def no_op():
        return None

    monkeypatch.setattr(main, "init_db", no_op)
    monkeypatch.setattr(main, "async_session_factory", sessions, raising=False)
    monkeypatch.setattr(main, "get_registry", lambda: registry)
    monkeypatch.setattr("app.services.reconciliation.reconcile_zombie_jobs", no_op)
    async with main.lifespan(main.app):
        pass
    async with sessions() as db:
        assert (await db.get(Provider, "edge_tts")).requires_api_key is False

    from app.services import provider_bootstrap

    async def fail_after_write(db, _registry):
        db.add(Provider(id="partial", name="Partial", provider_type="audio"))
        await db.flush()
        raise RuntimeError("mysql://user:secret@example.invalid/db")

    monkeypatch.setattr(provider_bootstrap, "bootstrap_providers", fail_after_write)
    with pytest.raises(RuntimeError, match="Provider bootstrap failed") as error:
        async with main.lifespan(main.app):
            pass
    assert "secret" not in str(error.value)
    async with sessions() as db:
        assert await db.get(Provider, "partial") is None
    await engine.dispose()
