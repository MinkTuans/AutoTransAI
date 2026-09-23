"""Video editor QC and SEO use only synthetic catalog credentials."""

import asyncio
import json
import socket

import httpx
import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models import APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig
from app.models.video_translator import VideoAsset, VideoTranslationJob, VideoTranslationSegment
from app.services.ai_routing import RouteConfigurationError, RouteExhausted
from app.services.credential_service import CredentialService
from app.services.video_editor.qc_service import AIQCService
from app.services.video_editor.youtube_service import YouTubePublishingService


@pytest.fixture(autouse=True)
def no_outbound_network(monkeypatch):
    def reject(*args, **kwargs):
        raise AssertionError("editor auxiliary LLM test attempted outbound network")

    monkeypatch.setattr(socket.socket, "connect", reject)
    monkeypatch.setattr(httpx.AsyncClient, "request", reject)
    monkeypatch.setattr(httpx.AsyncClient, "get", reject)
    monkeypatch.setattr(httpx.AsyncClient, "post", reject)


@pytest.fixture
async def catalog(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'catalog.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for model in (Provider, APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, AIFunctionConfig):
            await conn.run_sync(model.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add_all(Provider(id=p, name=p, provider_type="llm") for p in ("openai", "gemini", "anthropic"))
    yield sessions, tmp_path
    await engine.dispose()


async def add_model(db, path, provider, remote, secret, *, metadata=None):
    model = CatalogModel(provider_id=provider, remote_model_id=remote, source="manual",
                         capability_status="KNOWN", capabilities=["LLM"], discovery_metadata=metadata or {})
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
async def test_qc_uses_exact_default_then_cross_provider_and_validates_json(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "qc-primary-v2", "synthetic-primary")
        await add_model(db, path, "gemini", "qc-backup-v3", "synthetic-backup")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=first.id))
    calls = []

    async def answer(prompt, target, key):
        calls.append((target.remote_model_id, key))
        if target.provider_id == "openai":
            return '{"content_safety_score":null,"translation_quality_score":100,"issues":[]}'
        return json.dumps({"content_safety_score": 72, "translation_quality_score": 88, "issues": ["Issue"]})

    registry(monkeypatch, answer)
    result = await AIQCService.audit_content_with_gemini("Sensitive transcript", sessions=sessions, data_dir=path)
    assert result == {"content_safety_score": 72, "translation_quality_score": 88, "issues": ["Issue"]}
    assert calls == [("qc-primary-v2", "synthetic-primary"), ("qc-backup-v3", "synthetic-backup")]


@pytest.mark.asyncio
async def test_seo_preserves_defaults_with_request_local_model_key(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "seo-v7", "synthetic-seo")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=first.id))
    calls = []

    async def answer(prompt, target, key):
        await asyncio.sleep(0)
        calls.append((target.remote_model_id, key, len(prompt.encode("utf-8"))))
        return json.dumps({"title": "AI title", "description": "AI addendum", "tags": ["#AI"], "category_id": "22"})

    registry(monkeypatch, answer)
    settings = {"youtube_title_template": "Tập {episode} | {project_name}",
                "youtube_description_default": "User description", "youtube_default_tags": "#Owner",
                "youtube_ai_seo_enabled": True}
    results = await asyncio.gather(*(YouTubePublishingService.generate_youtube_seo_metadata(
        f"Job transcript {n}", project_settings=settings, project_name="Project", sessions=sessions, data_dir=path
    ) for n in range(2)))
    assert all(item["title"] == "Tập 01 | Project" and item["description"] == "User description\n\nAI addendum"
               and item["tags"] == ["#Owner", "#AI"] for item in results)
    assert len(calls) == 2 and {(model, key) for model, key, _ in calls} == {("seo-v7", "synthetic-seo")}


@pytest.mark.asyncio
async def test_editor_invalid_default_does_not_fall_back_to_env(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        await add_model(db, path, "openai", "available", "synthetic")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id="missing"))
    with pytest.raises(RouteConfigurationError):
        await AIQCService.audit_content_with_gemini("Sensitive transcript", sessions=sessions, data_dir=path)
    with pytest.raises(RouteConfigurationError):
        await YouTubePublishingService.generate_youtube_seo_metadata("Sensitive transcript", sessions=sessions, data_dir=path)


@pytest.mark.asyncio
async def test_seo_unsupported_adapter_fails_without_secret_in_error(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "anthropic", "unknown", "synthetic-secret")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="anthropic", model_id=first.id))
    async def answer(*args):
        raise AssertionError("adapter must be missing")
    registry(monkeypatch, answer)
    with pytest.raises(RouteExhausted, match="capability_mismatch") as error:
        await YouTubePublishingService.generate_youtube_seo_metadata("Sensitive transcript", sessions=sessions, data_dir=path)
    assert "synthetic-secret" not in str(error.value)


@pytest.mark.asyncio
async def test_editor_http_entry_points_forward_catalog_session_factory(tmp_path, monkeypatch):
    from app.api.routes import video_editor as editor

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'editor.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    video = tmp_path / "output.mp4"
    video.write_bytes(b"synthetic media")
    async with sessions.begin() as db:
        db.add(VideoAsset(id="asset", file_path=str(video)))
        db.add(VideoTranslationJob(id="job", asset_id="asset", output_video_path=str(video)))
        db.add(VideoTranslationSegment(job_id="job", segment_number=1, start_time=0, end_time=2,
                                       original_text="Alice", translated_text="An"))
    monkeypatch.setattr(editor, "async_session_factory", sessions)
    observed = []

    async def qc(**kwargs):
        observed.append(("qc", kwargs.get("sessions")))
        return {"audio_lufs": -14.0, "sync_drift_ms": 0.0, "has_black_frames": False,
                "content_safety_score": 90.0, "translation_quality_score": 90.0,
                "overall_score": 90.0, "qc_status": "passed", "issues": []}

    async def seo(**kwargs):
        observed.append(("seo", kwargs.get("sessions")))
        return {"title": "Title", "description": "", "tags": [], "category_id": "22"}

    monkeypatch.setattr(editor.AIQCService, "run_full_qc", qc)
    monkeypatch.setattr(editor.YouTubePublishingService, "generate_youtube_seo_metadata", seo)
    async with sessions() as db:
        await editor.run_ai_qc_endpoint("job", db)
        await editor.generate_youtube_seo_endpoint("job", db)
    assert observed == [("qc", sessions), ("seo", sessions)]
    await engine.dispose()


@pytest.mark.asyncio
async def test_unified_publish_stage_forwards_catalog_sessions(monkeypatch):
    from app.workflow.stages import publish_stage
    from app.workflow.workflow_context import WorkflowContext

    marker = object()
    monkeypatch.setattr(publish_stage, "async_session_factory", marker, raising=False)
    observed = []

    async def seo(**kwargs):
        observed.append(kwargs)
        return {"title": "Title", "description": "", "tags": [], "category_id": "22"}

    monkeypatch.setattr(YouTubePublishingService, "generate_youtube_seo_metadata", seo)
    ctx = WorkflowContext(project_id="project", raw_transcript="Alice sentence",
                          settings_snapshot={"youtube_description_default": "Creator words",
                                             "youtube_default_tags": "#Owner"})
    result = await publish_stage.PublishStage()._generate_seo(ctx)
    assert result["title"] == "Title"
    assert observed[0]["sessions"] is marker
    assert observed[0]["project_settings"]["youtube_description_default"] == "Creator words"
    assert observed[0]["project_settings"]["youtube_default_tags"] == "#Owner"
    assert observed[0]["project_name"] == "project"


@pytest.mark.asyncio
async def test_unified_publish_honors_ai_off_and_creator_defaults(monkeypatch):
    from app.workflow.stages import publish_stage
    from app.workflow.workflow_context import WorkflowContext

    monkeypatch.setattr(publish_stage, "async_session_factory", object(), raising=False)
    ctx = WorkflowContext(project_id="owner-project", raw_transcript="Alice sentence",
                          settings_snapshot={"youtube_ai_seo_enabled": "false",
                                             "youtube_title_template": "{project_name} — Tập {episode}",
                                             "youtube_description_default": "Creator description",
                                             "youtube_default_tags": "#Creator"})
    result = await publish_stage.PublishStage()._generate_seo(ctx)
    assert result["title"] == "owner-project — Tập 01"
    assert result["description"] == "Creator description"
    assert result["tags"] == ["#Creator"]


@pytest.mark.asyncio
async def test_unified_publish_uses_project_title_and_video_identity(tmp_path, monkeypatch):
    from app.models import Project
    from app.workflow.stages import publish_stage
    from app.workflow.workflow_context import WorkflowContext

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'project.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(publish_stage, "async_session_factory", object(), raising=False)
    async with sessions.begin() as db:
        db.add(Project(id="owner-project", title="Creator Series"))
    ctx = WorkflowContext(project_id="owner-project", raw_transcript="Alice sentence",
                          video_path=str(tmp_path / "Episode One.mp4"),
                          settings_snapshot={"youtube_ai_seo_enabled": False,
                                             "youtube_title_template": "{project_name}/{video_name}/Tập {episode}"})
    async with sessions() as db:
        result = await publish_stage.PublishStage().execute_step("generate_seo", ctx, db)
    assert result["title"] == "Creator Series/Episode One/Tập 01"
    await engine.dispose()


@pytest.mark.asyncio
async def test_qc_full_suite_forwards_catalog_sessions_without_media(monkeypatch, tmp_path):
    marker = object()
    observed = []

    async def audit(text, **kwargs):
        observed.append(kwargs.get("sessions"))
        return {"content_safety_score": 90, "translation_quality_score": 80, "issues": []}

    monkeypatch.setattr(AIQCService, "audit_content_with_gemini", audit)
    monkeypatch.setattr("app.services.video_editor.qc_service.log_job_event", lambda *args: None)
    result = await AIQCService.run_full_qc(tmp_path / "missing.mp4", 1.0, "Alice", sessions=marker)
    assert result["content_safety_score"] == 90
    assert observed == [marker]


@pytest.mark.asyncio
async def test_seo_invalid_json_advances_and_each_target_gets_own_budget(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "first", "synthetic-first",
                                metadata={"max_input_tokens": 8000})
        await add_model(db, path, "gemini", "second", "synthetic-second",
                        metadata={"inputTokenLimit": 2700})
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=first.id))
    seen = []

    async def answer(prompt, target, key):
        seen.append((target.remote_model_id, len(prompt.encode("utf-8"))))
        if target.remote_model_id == "first":
            return '{"title":null,"description":"bad","tags":[],"category_id":"22"}'
        return json.dumps({"title": "AI", "description": "AI desc", "tags": ["#AI"], "category_id": "22"})

    registry(monkeypatch, answer)
    result = await YouTubePublishingService.generate_youtube_seo_metadata(
        "Alice " + "長文本" * 3000, sessions=sessions, data_dir=path,
    )
    assert result["description"] == "AI desc"
    assert [name for name, _ in seen] == ["first", "second"]
    assert seen[0][1] <= 6000 and seen[1][1] <= 2700 - 512


@pytest.mark.asyncio
async def test_disabled_ai_seo_preserves_user_defaults_even_if_catalog_invalid(catalog):
    sessions, path = catalog
    async with sessions.begin() as db:
        await add_model(db, path, "openai", "available", "synthetic")
    result = await YouTubePublishingService.generate_youtube_seo_metadata(
        "Alice sentence", project_settings={"youtube_ai_seo_enabled": False,
                                            "youtube_description_default": "User text",
                                            "youtube_default_tags": "#Owner"},
        sessions=sessions, data_dir=path,
    )
    assert result["description"] == "User text"
    assert result["tags"] == ["#Owner"]


@pytest.mark.asyncio
async def test_legacy_qc_and_seo_errors_do_not_log_secret(monkeypatch):
    import app.services.video_editor.qc_service as qc_module
    import app.services.video_editor.youtube_service as seo_module

    marker = "SYNTHETIC_SECRET_RESPONSE"
    monkeypatch.setattr(qc_module.settings, "GEMINI_API_KEY", "synthetic-key")
    monkeypatch.setattr(seo_module.settings, "GEMINI_API_KEY", "synthetic-key")
    logged = []
    monkeypatch.setattr(qc_module.logger, "warning", lambda *a, **k: logged.append((a, k)))
    monkeypatch.setattr(seo_module.logger, "warning", lambda *a, **k: logged.append((a, k)))

    async def fail(*args, **kwargs):
        raise RuntimeError(marker)

    monkeypatch.setattr(httpx.AsyncClient, "post", fail)
    await AIQCService.audit_content_with_gemini("Alice sentence", model_name="gemini-legacy")
    await YouTubePublishingService.generate_youtube_seo_metadata("Alice sentence", model_name="gemini-legacy")
    assert len(logged) == 2 and marker not in str(logged)


@pytest.mark.asyncio
async def test_concurrent_seo_jobs_keep_configured_model_and_key_local(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "first-v1", "synthetic-first")
        second = await add_model(db, path, "openai", "second-v2", "synthetic-second")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=first.id))
    first_entered = asyncio.Event()
    release_first = asyncio.Event()
    seen = []

    async def answer(prompt, target, key):
        seen.append((target.remote_model_id, key))
        if target.remote_model_id == "first-v1":
            first_entered.set()
            await release_first.wait()
        return json.dumps({"title": "AI", "description": "AI desc", "tags": ["#AI"], "category_id": "22"})

    registry(monkeypatch, answer)
    job_one = asyncio.create_task(YouTubePublishingService.generate_youtube_seo_metadata(
        "Alice first", sessions=sessions, data_dir=path,
    ))
    await asyncio.wait_for(first_entered.wait(), 5)
    async with sessions.begin() as db:
        (await db.get(AIFunctionConfig, "translation")).model_id = second.id
    job_two = asyncio.create_task(YouTubePublishingService.generate_youtube_seo_metadata(
        "Alice second", sessions=sessions, data_dir=path,
    ))
    try:
        assert (await asyncio.wait_for(job_two, 5))["description"] == "AI desc"
    finally:
        release_first.set()
    assert (await asyncio.wait_for(job_one, 5))["description"] == "AI desc"
    assert seen == [("first-v1", "synthetic-first"), ("second-v2", "synthetic-second")]


@pytest.mark.asyncio
async def test_invalid_qc_output_exhaustion_is_visible_not_passing(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "qc-only", "synthetic-secret")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=first.id))

    async def answer(prompt, target, key):
        return json.dumps({"content_safety_score": None, "translation_quality_score": 100,
                           "issues": ["SYNTHETIC_PRIVATE_RESPONSE"]})

    registry(monkeypatch, answer)
    with pytest.raises(RouteExhausted, match="invalid_output") as error:
        await AIQCService.audit_content_with_gemini("Alice sentence", sessions=sessions, data_dir=path)
    assert "synthetic-secret" not in str(error.value)
    assert "SYNTHETIC_PRIVATE_RESPONSE" not in str(error.value)


@pytest.mark.asyncio
async def test_invalid_seo_output_exhaustion_is_visible_not_default_success(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "seo-only", "synthetic-secret")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=first.id))

    async def answer(prompt, target, key):
        return '{"title":"AI","description":null,"tags":[],"category_id":"22"}'

    registry(monkeypatch, answer)
    with pytest.raises(RouteExhausted, match="invalid_output"):
        await YouTubePublishingService.generate_youtube_seo_metadata(
            "Alice sentence", sessions=sessions, data_dir=path,
        )


@pytest.mark.asyncio
async def test_all_empty_seo_response_advances_to_backup(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "a-empty", "synthetic-primary")
        await add_model(db, path, "gemini", "b-valid", "synthetic-backup")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=first.id))
    seen = []

    async def answer(prompt, target, key):
        seen.append(target.remote_model_id)
        if target.remote_model_id == "a-empty":
            return '{"title":"","description":"","tags":[],"category_id":"22"}'
        return '{"title":"AI","description":"Useful AI summary","tags":["#AI"],"category_id":"22"}'

    registry(monkeypatch, answer)
    result = await YouTubePublishingService.generate_youtube_seo_metadata(
        "Alice sentence", sessions=sessions, data_dir=path,
    )
    assert result["description"] == "Useful AI summary"
    assert seen == ["a-empty", "b-valid"]


@pytest.mark.asyncio
async def test_seo_empty_disabled_ai_fields_do_not_trigger_invalid_output(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "only", "synthetic-primary")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=first.id))
    seen = []

    async def answer(prompt, target, key):
        seen.append(target.remote_model_id)
        return '{"title":"AI","description":"","tags":[],"category_id":"22"}'

    registry(monkeypatch, answer)
    result = await YouTubePublishingService.generate_youtube_seo_metadata(
        "Alice sentence", project_settings={"youtube_ai_allow_description": False,
                                            "youtube_ai_allow_tags": False,
                                            "youtube_description_default": "Owner text",
                                            "youtube_default_tags": "#Owner"},
        sessions=sessions, data_dir=path,
    )
    assert result["description"] == "Owner text"
    assert result["tags"] == ["#Owner"]
    assert seen == ["only"]
