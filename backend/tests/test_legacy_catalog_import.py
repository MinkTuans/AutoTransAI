"""Explicit legacy model import on disposable databases; no provider traffic."""
import json

import pytest
from sqlalchemy import MetaData, String, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, Provider
from app.models.settings import AIModel, AIFunctionConfig
from app.api.routes.ai_catalog import _model_view, _view_context, list_providers
from app.providers.discovery.types import DiscoveredModel, DiscoveryResult
from app.services.ai_routing import RouteConfigurationError, build_route
from app.services.legacy_catalog_import import import_legacy_catalog
from app.services.model_refresh_service import ModelRefreshService
from app.services.video_editor.catalog_llm import generate_catalog_json


@pytest.fixture
async def sessions(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'catalog-import.sqlite'}")
    async with engine.begin() as db:
        for table in (Provider.__table__, CatalogModel.__table__, AIModel.__table__,
                      AIFunctionConfig.__table__,
                      APIKey.__table__, KeyModelAccess.__table__, CatalogRefreshRun.__table__):
            await db.run_sync(table.create)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


async def test_import_keeps_archive_and_replays_without_mutating_existing_model(sessions):
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
        db.add(AIModel(id="private-model", provider_id="openai", model_name="Private name",
                       capabilities=json.dumps(["LLM"]), enabled=True,
                       description="private description"))
    async with sessions.begin() as db:
        first = await import_legacy_catalog(db)
        assert first == {"status": "imported", "counts": {"imported": 1, "existing": 0},
                         "issues": []}
        row = (await db.scalars(select(CatalogModel))).one()
        assert row.remote_model_id == "private-model"
        assert row.provider_id == "openai"
        assert row.source == "legacy_import"
        assert row.discovery_metadata is None
        assert row.capabilities == []
        assert (await db.get(AIModel, "private-model")).description == "private description"
        identity, updated = row.id, row.updated_at
        second = await import_legacy_catalog(db)
        assert second == {"status": "imported", "counts": {"imported": 0, "existing": 1},
                          "issues": []}
        assert row.id == identity and row.updated_at == updated


async def test_missing_provider_refuses_whole_batch_before_writes(sessions):
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
        db.add_all([
            AIModel(id="valid", provider_id="openai", model_name="Valid", capabilities="[]"),
            AIModel(id="orphan", provider_id="absent", model_name="Orphan", capabilities="[]"),
        ])
    async with sessions.begin() as db:
        result = await import_legacy_catalog(db)
        assert result["status"] == "conflict"
        assert result["issues"] == ["missing_provider"]
        assert (await db.scalars(select(CatalogModel))).all() == []


async def test_collation_equal_provider_id_is_not_treated_as_exact(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'nocase.sqlite'}")
    metadata = MetaData()
    for table in (Provider.__table__, CatalogModel.__table__, AIModel.__table__):
        table.to_metadata(metadata)
    metadata.tables["providers"].c.id.type = String(50, collation="NOCASE")
    metadata.tables["ai_models"].c.provider_id.type = String(50, collation="NOCASE")
    async with engine.begin() as db:
        await db.run_sync(metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessions.begin() as db:
            db.add(Provider(id="OpenAI", name="Private", provider_type="llm"))
            db.add(AIModel(id="model", provider_id="openai", model_name="Private",
                           capabilities="[]"))
        async with sessions.begin() as db:
            result = await import_legacy_catalog(db)
            assert result["status"] == "conflict"
            assert result["issues"] == ["provider_identity_conflict"]
            assert (await db.scalars(select(CatalogModel))).all() == []
    finally:
        await engine.dispose()


async def test_imported_public_catalog_model_routes_only_after_discovery(sessions, tmp_path):
    async with sessions.begin() as db:
        db.add(Provider(id="fal", name="Fal", provider_type="video"))
        db.add(AIModel(id="private-image", provider_id="fal", model_name="Private",
                       capabilities='["IMAGE_GENERATION"]'))
        db.add(APIKey(id="key-1", provider_id="fal", ciphertext="synthetic-only",
                      fingerprint="a" * 64, masked_key="****", enabled=True))
    async with sessions.begin() as db:
        await import_legacy_catalog(db)
        archival = (await db.scalars(select(CatalogModel))).one()
        view = _model_view(archival, {"fal": await db.get(Provider, "fal")},
                           _view_context({"key-1": "fal"}, [], []), "IMAGE_GENERATION")
        assert view.selectable is False
        assert view.available_key_count == 0
        with pytest.raises(RouteConfigurationError):
            await build_route(db, "IMAGE_GENERATION")
        service = ModelRefreshService(sessions, tmp_path)
        await service._apply_provider(db, "fal", [("key-1", DiscoveryResult(
            "complete", (DiscoveredModel("private-image", "Provider name", {}),),
            access_scope="catalog"))], False, {"retired": 0})
        model = (await db.scalars(select(CatalogModel))).one()
        assert model.source == "discovered"
        route = await build_route(db, "IMAGE_GENERATION")
        assert [(target.remote_model_id, target.key_id) for target in route.targets] == [
            ("private-image", "key-1")]


async def test_imported_archival_llm_alone_keeps_legacy_caller_path(sessions):
    async with sessions.begin() as db:
        db.add(Provider(id="gemini", name="Gemini", provider_type="llm"))
        db.add(AIModel(id="old-llm", provider_id="gemini", model_name="Private",
                       capabilities='["LLM"]'))
    async with sessions.begin() as db:
        await import_legacy_catalog(db)
    result = await generate_catalog_json(
        sessions=sessions, data_dir=None, prompt_prefix="", transcript="private text",
        prompt_suffix="", validate=lambda value: value)
    assert result is None


async def test_keyless_provider_does_not_report_unverified_archive_as_ready(sessions):
    async with sessions.begin() as db:
        db.add(Provider(id="edge_tts", name="Edge", provider_type="audio",
                        requires_api_key=False))
        db.add(AIModel(id="old-voice", provider_id="edge_tts", model_name="Private",
                       capabilities='["TTS"]'))
    async with sessions.begin() as db:
        await import_legacy_catalog(db)
        response = await list_providers(db)
        assert response.data[0].model_count == 1
        assert response.data[0].active_model_count == 0
        assert response.data[0].status != "ready"
