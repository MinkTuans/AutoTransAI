"""Character mapping and thumbnail analysis use isolated catalog LLM routes."""

import json
import socket
import asyncio

import httpx
import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models import APIKey, CatalogModel, KeyModelAccess, Provider, Project
from app.models.settings import AIFunctionConfig
from app.models.video_thumbnail import VideoThumbnail
from app.models.workflow_engine import SpeakerVoiceMapping
from app.services.ai_routing import RouteConfigurationError, RouteExhausted
from app.services.credential_service import CredentialService
from app.services.video_translator.character_mapping_service import map_and_persist
from app.services.thumbnail_service import ThumbnailService


@pytest.fixture(autouse=True)
def no_outbound_network(monkeypatch):
    def reject(*args, **kwargs):
        raise AssertionError("auxiliary LLM test attempted outbound network")

    monkeypatch.setattr(socket.socket, "connect", reject)
    monkeypatch.setattr(httpx.AsyncClient, "request", reject)
    monkeypatch.setattr(httpx.AsyncClient, "get", reject)
    monkeypatch.setattr(httpx.AsyncClient, "post", reject)


@pytest.fixture
async def catalog(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'catalog.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add_all(Provider(id=p, name=p, provider_type="llm") for p in ("openai", "gemini", "anthropic"))
        db.add(Project(id="project", title="Synthetic project"))
    yield sessions, tmp_path
    await engine.dispose()


@pytest.fixture
async def constrained_catalog(tmp_path):
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{tmp_path / 'single-pool.db'}",
        pool_size=1, max_overflow=0, pool_timeout=0.2,
    )
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="openai", provider_type="llm"))
        db.add(Project(id="project", title="Synthetic project"))
    yield sessions, tmp_path
    await engine.dispose()


async def add_model(db, path, provider, remote, secret):
    model = CatalogModel(provider_id=provider, remote_model_id=remote, source="manual",
                         capability_status="KNOWN", capabilities=["LLM"])
    db.add(model)
    await db.flush()
    key = await (await CredentialService.open(db, path)).create(provider, secret)
    await db.flush()
    db.add(KeyModelAccess(key_id=key.id, model_id=model.id, provider_id=provider))
    return model


def registry(monkeypatch, responder):
    from app.services.video_editor import catalog_llm

    class Adapter:
        async def generate_text(self, prompt, *, route_target, api_key):
            return await responder(prompt, route_target, api_key)

    monkeypatch.setattr(catalog_llm, "get_registry", lambda: type("Registry", (), {
        "get_llm": lambda _, p: Adapter() if p in ("openai", "gemini") else None,
    })())


@pytest.mark.asyncio
async def test_character_mapping_uses_catalog_default_then_backup_and_persists_stable_identity(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "mapping-a", "synthetic-a")
        await add_model(db, path, "gemini", "mapping-b", "synthetic-b")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=first.id))
    calls = []

    async def answer(prompt, target, key):
        calls.append((target.remote_model_id, key))
        if target.remote_model_id == "mapping-a":
            return '{"characters":null}'
        return json.dumps({"characters": [{"character_id": "source-id", "name": "Alice",
                                          "gender": "female", "role": "main",
                                          "speaker_ids": ["S1"], "confidence": 0.95}]})

    registry(monkeypatch, answer)
    segments = [{"speaker_id": "S1", "text": "Alice says hello"}]
    async with sessions() as db:
        first_result = await map_and_persist(db, "project", segments, None, visual_genders={},
                                             sessions=sessions, data_dir=path)
        await db.commit()
        second_result = await map_and_persist(db, "project", segments, None, visual_genders={},
                                              sessions=sessions, data_dir=path)
    assert first_result.by_speaker["S1"]["name"] == "Alice"
    assert first_result.by_speaker["S1"]["character_id"] == second_result.by_speaker["S1"]["character_id"]
    assert calls == [("mapping-a", "synthetic-a"), ("mapping-b", "synthetic-b")] * 2


@pytest.mark.asyncio
async def test_unknown_only_character_candidate_advances_to_backup(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "openai", "unknown-speaker", "synthetic-a")
        await add_model(db, path, "gemini", "known-speaker", "synthetic-b")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=selected.id))
    calls = []

    async def answer(prompt, target, key):
        calls.append(target.remote_model_id)
        member = "OTHER" if target.remote_model_id == "unknown-speaker" else "S1"
        return json.dumps({"characters": [{"character_id": "alice", "name": "Alice", "gender": "female",
                                           "role": "main", "speaker_ids": [member], "confidence": 0.95}]})

    registry(monkeypatch, answer)
    async with sessions() as db:
        result = await map_and_persist(db, "project", [{"speaker_id": "S1", "text": "Hello"}], None,
                                       visual_genders={}, sessions=sessions, data_dir=path)
    assert result.by_speaker["S1"]["name"] == "Alice"
    assert calls == ["unknown-speaker", "known-speaker"]


@pytest.mark.asyncio
async def test_voice_only_mapping_receives_generated_character_id(catalog):
    sessions, _ = catalog
    async with sessions.begin() as db:
        db.add(SpeakerVoiceMapping(id="voice-only", project_id="project", speaker_id="S1",
                                   speaker_name="S1", voice_provider="edge_tts",
                                   voice_id="vi-VN-HoaiMyNeural", character_id=None))

    class LegacyLLM:
        async def generate_text(self, prompt):
            return json.dumps({"characters": [{"character_id": "alice", "name": "Alice", "gender": "female",
                                              "role": "main", "speaker_ids": ["S1"], "confidence": 0.95}]})

    async with sessions() as db:
        result = await map_and_persist(db, "project", [{"speaker_id": "S1", "text": "Hello"}],
                                       LegacyLLM(), visual_genders={})
        await db.commit()
        mapping = await db.get(SpeakerVoiceMapping, "voice-only")
    assert result.by_speaker["S1"]["character_id"]
    assert mapping.character_id == result.by_speaker["S1"]["character_id"]


@pytest.mark.asyncio
async def test_thumbnail_analysis_uses_exact_catalog_model_and_key(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "thumb-v9", "synthetic-thumb")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=first.id))
    observed = []

    async def answer(prompt, target, key):
        observed.append((target.remote_model_id, key))
        return json.dumps({"title": "Story", "main_subject": "Alice", "main_event": "Rescue",
                           "thumbnail_hook": "Alice rescues the village", "important_visual_elements": ["village"]})

    registry(monkeypatch, answer)
    result = await ThumbnailService.analyze_content_with_llm(
        "Story", "", "Alice rescues the village", sessions=sessions, data_dir=path,
    )
    assert result["main_subject"] == "Alice"
    assert observed == [("thumb-v9", "synthetic-thumb")]


@pytest.mark.asyncio
async def test_character_and_thumbnail_invalid_default_do_not_use_legacy(catalog):
    sessions, path = catalog
    async with sessions.begin() as db:
        await add_model(db, path, "openai", "available", "synthetic")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id="missing"))
    async with sessions() as db:
        with pytest.raises(RouteConfigurationError):
            await map_and_persist(db, "project", [{"speaker_id": "S1", "text": "Alice"}], None,
                                  visual_genders={}, sessions=sessions, data_dir=path)
    with pytest.raises(RouteConfigurationError):
        await ThumbnailService.analyze_content_with_llm("Story", "", "Alice sentence",
                                                        sessions=sessions, data_dir=path)


@pytest.mark.asyncio
async def test_thumbnail_missing_adapter_or_bad_output_is_visible(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "anthropic", "unsupported", "synthetic-secret")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="anthropic", model_id=first.id))
    async def never(*args):
        raise AssertionError("adapter should be absent")
    registry(monkeypatch, never)
    with pytest.raises(RouteExhausted, match="capability_mismatch") as error:
        await ThumbnailService.analyze_content_with_llm("Story", "", "Alice sentence",
                                                        sessions=sessions, data_dir=path)
    assert "synthetic-secret" not in str(error.value)


@pytest.mark.asyncio
async def test_create_thumbnail_forwards_catalog_route_and_stops_before_image(catalog, monkeypatch):
    sessions, path = catalog
    seen = []

    async def analysis(*args, **kwargs):
        seen.append(kwargs)
        raise RouteExhausted("AI route failed: invalid_output")

    monkeypatch.setattr(ThumbnailService, "analyze_content_with_llm", analysis)
    async with sessions() as db:
        record = await ThumbnailService.create_thumbnail(
            db, project_id="project", sessions=sessions, data_dir=path,
        )
    assert seen[0]["sessions"] is sessions
    assert seen[0]["data_dir"] == path
    assert record.status == "failed"
    assert record.error_message == "AI route failed: invalid_output"


@pytest.mark.asyncio
async def test_concurrent_thumbnail_analysis_keeps_each_prompt_request_local(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "openai", "thumb-concurrent", "synthetic-concurrent")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=selected.id))
    observed = []

    async def answer(prompt, target, key):
        await asyncio.sleep(0)
        observed.append((prompt, target.remote_model_id, key))
        title = "Alpha" if "Video Title: Alpha" in prompt else "Beta"
        return json.dumps({"title": title, "main_subject": title, "main_event": "Event",
                           "thumbnail_hook": "Interesting event", "important_visual_elements": [title]})

    registry(monkeypatch, answer)
    first, second = await asyncio.gather(
        ThumbnailService.analyze_content_with_llm("Alpha", "", "alpha transcript", sessions=sessions, data_dir=path),
        ThumbnailService.analyze_content_with_llm("Beta", "", "beta transcript", sessions=sessions, data_dir=path),
    )
    assert (first["title"], second["title"]) == ("Alpha", "Beta")
    assert len(observed) == 2
    assert all(model == "thumb-concurrent" and key == "synthetic-concurrent" for _, model, key in observed)
    assert "beta transcript" not in next(prompt for prompt, _, _ in observed if "Video Title: Alpha" in prompt)
    assert "alpha transcript" not in next(prompt for prompt, _, _ in observed if "Video Title: Beta" in prompt)


@pytest.mark.asyncio
async def test_thumbnail_semantically_invalid_default_falls_back(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "openai", "thumb-invalid", "synthetic-invalid")
        await add_model(db, path, "gemini", "thumb-good", "synthetic-good")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=selected.id))
    calls = []

    async def answer(prompt, target, key):
        calls.append(target.remote_model_id)
        if target.remote_model_id == "thumb-invalid":
            return '{"title":"", "main_subject":"", "main_event":"", "thumbnail_hook":""}'
        return json.dumps({"title": "Valid", "main_subject": "Person", "main_event": "Event",
                           "thumbnail_hook": "Interesting event", "important_visual_elements": ["person"]})

    registry(monkeypatch, answer)
    result = await ThumbnailService.analyze_content_with_llm(
        "Story", "", "Transcript", sessions=sessions, data_dir=path,
    )
    assert result["title"] == "Valid"
    assert calls == ["thumb-invalid", "thumb-good"]


@pytest.mark.asyncio
async def test_legacy_malformed_mapping_is_unresolved_instead_of_crashing(catalog):
    sessions, _ = catalog

    class MalformedLLM:
        async def generate_text(self, prompt):
            return '{"characters":[{"speaker_ids":["S1"],"confidence":"not-a-number"}]}'

    async with sessions() as db:
        result = await map_and_persist(db, "project", [{"speaker_id": "S1", "text": "Hello"}],
                                       MalformedLLM(), visual_genders={})
    assert result.requires_review
    assert result.by_speaker["S1"]["confidence"] == 0.0


@pytest.mark.asyncio
async def test_thumbnail_generate_endpoint_passes_catalog_factory(catalog, monkeypatch):
    from app.api.routes import thumbnail as route

    sessions, path = catalog
    seen = {}

    async def create(**kwargs):
        seen.update(kwargs)
        return VideoThumbnail(id="synthetic", project_id="project", status="failed")

    monkeypatch.setattr(route, "async_session_factory", sessions)
    monkeypatch.setattr(route.settings, "DATA_DIR", path)
    monkeypatch.setattr(route.ThumbnailService, "create_thumbnail", create)
    result = await route.generate_thumbnail_endpoint(
        route.GenerateThumbnailRequest(project_id="project"), db=object(),
    )
    assert result["success"] is False
    assert seen["sessions"] is sessions
    assert seen["data_dir"] == path


@pytest.mark.asyncio
async def test_character_mapping_releases_outer_connection_before_catalog_route(constrained_catalog, monkeypatch):
    sessions, path = constrained_catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "openai", "single-pool-map", "synthetic")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=selected.id))
    calls = []

    async def answer(prompt, target, key):
        calls.append(target.remote_model_id)
        return json.dumps({"characters": [{"character_id": "alice", "name": "Alice", "gender": "female",
                                           "role": "main", "speaker_ids": ["S1"], "confidence": 0.95}]})

    registry(monkeypatch, answer)
    async with sessions() as db:
        result = await map_and_persist(db, "project", [{"speaker_id": "S1", "text": "Hello"}], None,
                                       visual_genders={}, sessions=sessions, data_dir=path)
    assert calls == ["single-pool-map"]
    assert result.by_speaker["S1"]["name"] == "Alice"


@pytest.mark.asyncio
async def test_thumbnail_releases_outer_connection_before_catalog_route(constrained_catalog, monkeypatch):
    sessions, path = constrained_catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "openai", "single-pool-thumb", "synthetic")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=selected.id))
    calls = []

    async def answer(prompt, target, key):
        calls.append(target.remote_model_id)
        return '{"title":""}'

    registry(monkeypatch, answer)
    async with sessions() as db:
        record = await ThumbnailService.create_thumbnail(
            db, project_id="project", sessions=sessions, data_dir=path,
        )
    assert calls == ["single-pool-thumb"]
    assert record.status == "failed"
    assert record.error_message == "AI route failed: invalid_output"
