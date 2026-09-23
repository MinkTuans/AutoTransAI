"""Unified ANALYZE/TRANSLATE routing and resumable context contracts."""

import asyncio
import json
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models import APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, Provider
from app.models import Project, WorkflowExecution, WorkflowStageExecution, WorkflowStepExecution
from app.models import ProjectGlossary
from app.models.workflow_engine import WorkflowEngineStatus, WorkflowStepStatus
from app.models.settings import AIFunctionConfig
from app.services.credential_service import CredentialService
from app.services.ai_routing import RouteConfigurationError, RouteExhausted
from app.workflow.workflow_context import WorkflowContext
from app.workflow.stages.analyze_stage import AnalyzeStage
from app.workflow.stages.translate_stage import TranslateStage
from app.workflow.workflow_engine import WorkflowEngine


@pytest.mark.asyncio
async def test_analyze_forwards_catalog_sessions_without_holding_step_db(monkeypatch, tmp_path):
    import app.services.video_translator.translator_service as translator
    import app.workflow.stages.analyze_stage as analyze_module

    sessions = object()
    monkeypatch.setattr(analyze_module, "async_session_factory", sessions, raising=False)
    audio = tmp_path / "source.wav"
    audio.write_bytes(b"synthetic")
    calls = []

    async def transcribe(*args, **kwargs):
        calls.append(kwargs)
        assert kwargs["sessions"] is sessions
        return ([{"number": 1, "start_time": 0, "end_time": 1,
                  "speaker_id": "Speaker 1", "text": "Hello"}], "en")

    monkeypatch.setattr(translator, "speech_to_text_and_detect_language", transcribe)
    ctx = WorkflowContext(project_id="one", audio_path=str(audio))
    step_db = object()
    await AnalyzeStage()._speech_to_text(ctx, step_db)
    assert ctx.raw_transcript == "Hello"
    assert calls[0]["job_id"] == "WF-JOB"
    assert calls[0]["db"] is step_db
    assert calls[0]["audio_path"] == audio


@pytest.mark.asyncio
async def test_real_analyze_steps_qc_then_translate_accept_stt_timeline_shape(monkeypatch, tmp_path):
    import app.services.video_translator.translator_service as translator

    audio = tmp_path / "speech.wav"
    audio.write_bytes(b"synthetic")
    stt_segments = [{"number": 1, "start_time": 0.0, "end_time": 1.0,
                     "speaker_id": "Speaker 1", "text": "Hello John"}]
    monkeypatch.setattr(translator, "speech_to_text_and_detect_language",
                        AsyncMock(return_value=(stt_segments, "en")))
    monkeypatch.setattr(translator, "translate_transcript_segments",
                        AsyncMock(return_value=[{**stt_segments[0], "translated_text": "Xin chào Gioan"}]))
    ctx = WorkflowContext(project_id="real-shape", audio_path=str(audio), duration=2.0)
    analyze = AnalyzeStage()
    for step in analyze.STEPS:
        await analyze.execute_step(step, ctx, None)
    assert (await analyze.run_qc(ctx))["passed"] is True
    assert ctx.source_segments[0]["start_time"] == 0.0
    assert ctx.source_segments[0]["end_time"] == 1.0
    assert ctx.raw_transcript == "Hello John"
    translate = TranslateStage()
    await translate.execute_step("translate_transcript", ctx, None)
    await translate.execute_step("validate_segment_ids", ctx, None)
    assert (await translate.run_qc(ctx))["passed"] is True
    assert ctx.translated_segments[0]["translated_text"] == "Xin chào Gioan"


@pytest.mark.asyncio
async def test_analyze_qc_preserves_legacy_timeline_and_rejects_bad_canonical_values():
    stage = AnalyzeStage()
    legacy = WorkflowContext(project_id="legacy", duration=2.0,
                             source_segments=[{"start": 0.0, "end": 1.0, "text": "Hello"}])
    assert (await stage.run_qc(legacy))["passed"] is True
    malformed = WorkflowContext(project_id="bad", duration=2.0,
                                source_segments=[{"start_time": "not-a-number", "end_time": 1.0}])
    result = await stage.run_qc(malformed)
    assert result["passed"] is False
    assert result["issues"] == ["Invalid timestamp value at segment index 0."]


@pytest.mark.asyncio
async def test_analyze_timeline_normalization_preserves_legacy_start_end():
    ctx = WorkflowContext(project_id="legacy", duration=5.0,
                          source_segments=[{"number": 1, "start": 2.0, "end": 3.0,
                                            "text": "Hello"}])
    await AnalyzeStage()._validate_timeline(ctx)
    assert ctx.source_segments[0]["start_time"] == 2.0
    assert ctx.source_segments[0]["end_time"] == 3.0


@pytest.mark.asyncio
async def test_translate_forwards_catalog_sessions_with_preloaded_glossary(monkeypatch):
    import app.services.video_translator.translator_service as translator
    import app.workflow.stages.translate_stage as translate_module

    sessions = object()
    monkeypatch.setattr(translate_module, "async_session_factory", sessions, raising=False)
    calls = []

    async def translate(*args, **kwargs):
        calls.append(kwargs)
        assert kwargs["sessions"] is sessions
        return [{**kwargs["segments"][0], "translated_text": "Xin chào"}]

    monkeypatch.setattr(translator, "translate_transcript_segments", translate)
    ctx = WorkflowContext(project_id="one", source_segments=[{"number": 1, "text": "Hello"}])
    ctx.glossary = [{"source_term": "Hello", "translated_term": "Xin chào"}]
    step_db = object()
    await TranslateStage()._translate_transcript(ctx, step_db)
    assert calls[0]["glossary"] == {"Hello": "Xin chào"}
    assert calls[0]["db"] is step_db
    assert ctx.translated_segments[0]["translated_text"] == "Xin chào"


def test_context_roundtrip_retains_downstream_data_without_credentials():
    ctx = WorkflowContext(project_id="one")
    ctx.raw_transcript = "Hello"
    ctx.source_segments = [{"number": 1, "start_time": 0, "end_time": 1,
                            "speaker_id": "Speaker 1", "text": "Hello", "api_key": "secret"}]
    ctx.translated_segments = [{"number": 1, "text": "Hello", "translated_text": "Xin chào"}]
    ctx.speakers = [{"speaker_id": "Speaker 1", "speaker_name": "Speaker 1"}]
    ctx.glossary = [{"source_term": "Hello", "translated_term": "Xin chào"}]
    ctx.speaker_voice_map = {"Speaker 1": {"provider": "edge_tts", "voice_id": "vi-VN-HoaiMyNeural"}}
    ctx.audio_segments_info = [{"segment_number": 1, "tts_audio_path": "clip.wav"}]
    ctx.tts_voice_id = "vi-VN-HoaiMyNeural"
    ctx.tts_provider_id = "edge_tts"

    snapshot = ctx.to_dict()
    restored = WorkflowContext.from_dict(snapshot)
    assert restored.raw_transcript == "Hello"
    assert restored.source_segments[0]["text"] == "Hello"
    assert restored.translated_segments[0]["translated_text"] == "Xin chào"
    assert restored.speakers == ctx.speakers
    assert restored.glossary == ctx.glossary
    assert restored.speaker_voice_map == ctx.speaker_voice_map
    assert restored.audio_segments_info == ctx.audio_segments_info
    assert restored.tts_voice_id == ctx.tts_voice_id
    assert restored.tts_provider_id == ctx.tts_provider_id
    assert "secret" not in str(snapshot)


@pytest.mark.parametrize("field,bad", [
    ("source_segments", {"number": 1}),
    ("translated_segments", ["not an object"]),
    ("speakers", [123]),
    ("glossary", "not a list"),
    ("speaker_voice_map", ["not a map"]),
    ("audio_segments_info", [None]),
])
def test_context_rejects_malformed_resume_data(field, bad):
    with pytest.raises(ValueError, match=field):
        WorkflowContext.from_dict({"project_id": "one", field: bad})


def test_historical_count_only_snapshot_remains_readable():
    ctx = WorkflowContext.from_dict({"project_id": "old", "segment_count": 4,
                                     "translated_segment_count": 4, "glossary_count": 1})
    assert ctx.source_segments == []
    assert ctx.translated_segments == []


def test_resume_rejects_nested_or_unbounded_segment_payload():
    with pytest.raises(ValueError, match="checkpoint"):
        WorkflowContext.from_dict(["not a mapping"])
    with pytest.raises(ValueError, match="source_segments"):
        WorkflowContext.from_dict({"project_id": "one", "source_segments": [{"text": {"api_key": "secret"}}]})
    with pytest.raises(ValueError, match="source_segments"):
        WorkflowContext.from_dict({"project_id": "one", "source_segments": [{"text": "x" * 65537}]})
    with pytest.raises(ValueError, match="raw_transcript"):
        WorkflowContext.from_dict({"project_id": "one", "raw_transcript": ["not a string"]})
    with pytest.raises(ValueError, match="speaker_voice_map"):
        WorkflowContext.from_dict({"project_id": "one", "speaker_voice_map":
                                   {"Speaker 1": {"voice_id": {"api_key": "secret"}}}})


@pytest.fixture
async def catalog(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'catalog.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for model in (Provider, APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, AIFunctionConfig):
            await conn.run_sync(model.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add_all(Provider(id=p, name=p, provider_type="llm") for p in ("gemini", "openai", "anthropic"))
    yield sessions, tmp_path
    await engine.dispose()


async def add_catalog_target(db, path, provider, remote, secret, capability):
    model = CatalogModel(provider_id=provider, remote_model_id=remote,
                         source="manual", capability_status="KNOWN", capabilities=[capability])
    db.add(model)
    await db.flush()
    key = await (await CredentialService.open(db, path)).create(provider, secret)
    await db.flush()
    db.add(KeyModelAccess(key_id=key.id, model_id=model.id, provider_id=provider))
    return model


@pytest.mark.asyncio
async def test_two_unified_projects_use_request_local_stt_model_and_key(catalog, monkeypatch, tmp_path):
    from app.services.video_translator import translator_service as service
    import app.workflow.stages.analyze_stage as analyze_module

    sessions, path = catalog
    real_settings = service.get_settings()
    monkeypatch.setattr(service, "get_settings", lambda: real_settings.model_copy(update={"DATA_DIR": path}))
    async with sessions.begin() as db:
        first = await add_catalog_target(db, path, "openai", "speech-one", "key-one", "STT")
        second = await add_catalog_target(db, path, "openai", "speech-two", "key-two", "STT")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id=first.id))
    monkeypatch.setattr(analyze_module, "async_session_factory", sessions)
    monkeypatch.setattr(service, "probe_duration_async", AsyncMock(return_value=1.0))
    entered = asyncio.Event()
    release = asyncio.Event()
    calls = []

    async def transcribe(audio_path, *, route_target, api_key, **kwargs):
        calls.append((route_target.remote_model_id, api_key, audio_path.name))
        if route_target.remote_model_id == "speech-one":
            entered.set()
            await release.wait()
        return ([{"number": 1, "start_time": 0, "end_time": 1,
                  "speaker_id": "Speaker 1", "text": "Hello"}], "en")

    monkeypatch.setattr(service, "transcribe_audio_with_whisper", transcribe)
    for project in ("project-one", "project-two"):
        (tmp_path / f"{project}.wav").write_bytes(b"synthetic")
    one = WorkflowContext(project_id="project-one", audio_path=str(tmp_path / "project-one.wav"))
    two = WorkflowContext(project_id="project-two", audio_path=str(tmp_path / "project-two.wav"))
    first_run = asyncio.create_task(AnalyzeStage()._speech_to_text(one, None))
    try:
        await asyncio.wait_for(entered.wait(), 5)
        async with sessions.begin() as db:
            config = await db.get(AIFunctionConfig, "stt")
            config.model_id = second.id
        await asyncio.wait_for(AnalyzeStage()._speech_to_text(two, None), 5)
    finally:
        release.set()
        await asyncio.wait_for(first_run, 5)
    assert calls == [("speech-one", "key-one", "project-one.wav"),
                     ("speech-two", "key-two", "project-two.wav")]


@pytest.mark.asyncio
async def test_two_unified_projects_use_request_local_translation_model_and_key(catalog, monkeypatch):
    from app.services.video_translator import translator_service as service
    import app.workflow.stages.translate_stage as translate_module

    sessions, path = catalog
    real_settings = service.get_settings()
    monkeypatch.setattr(service, "get_settings", lambda: real_settings.model_copy(update={"DATA_DIR": path}))
    async with sessions.begin() as db:
        first = await add_catalog_target(db, path, "openai", "text-one", "key-one", "TRANSLATION")
        second = await add_catalog_target(db, path, "openai", "text-two", "key-two", "TRANSLATION")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="openai", model_id=first.id))
    monkeypatch.setattr(translate_module, "async_session_factory", sessions)
    entered = asyncio.Event()
    release = asyncio.Event()
    calls = []

    class LLM:
        provider_id = "openai"
        provider_name = "synthetic"

        async def generate_text(self, prompt, *, route_target, api_key, **kwargs):
            calls.append((route_target.remote_model_id, api_key))
            if route_target.remote_model_id == "text-one":
                entered.set()
                await release.wait()
            return json.dumps({"lines": [{"n": 1, "text": "Xin chào"}], "names": []})

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    one = WorkflowContext(project_id="project-one", source_language="en",
                          source_segments=[{"number": 1, "text": "Hello"}])
    two = WorkflowContext(project_id="project-two", source_language="en",
                          source_segments=[{"number": 1, "text": "Hello"}])
    first_run = asyncio.create_task(TranslateStage()._translate_transcript(one, None))
    try:
        await asyncio.wait_for(entered.wait(), 5)
        async with sessions.begin() as db:
            config = await db.get(AIFunctionConfig, "translation")
            config.model_id = second.id
        await asyncio.wait_for(TranslateStage()._translate_transcript(two, None), 5)
    finally:
        release.set()
        await asyncio.wait_for(first_run, 5)
    assert calls == [("text-one", "key-one"), ("text-two", "key-two")]
    assert one.translated_segments[0]["translated_text"] == "Xin chào"
    assert two.translated_segments[0]["translated_text"] == "Xin chào"


@pytest.mark.asyncio
async def test_unified_translation_does_not_open_workflow_transaction_during_provider_call(catalog, monkeypatch):
    from app.services.video_translator import translator_service as service
    import app.workflow.stages.translate_stage as translate_module

    sessions, path = catalog
    real_settings = service.get_settings()
    monkeypatch.setattr(service, "get_settings", lambda: real_settings.model_copy(update={"DATA_DIR": path}))
    monkeypatch.setattr(translate_module, "async_session_factory", sessions)
    async with sessions.kw["bind"].begin() as conn:
        await conn.run_sync(Project.__table__.create)
        await conn.run_sync(ProjectGlossary.__table__.create)
    async with sessions.begin() as db:
        model = await add_catalog_target(db, path, "openai", "text-exact", "request-local", "TRANSLATION")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="openai", model_id=model.id))
        db.add(Project(id="one", title="One"))

    async with sessions() as step_db:
        observed = []

        class LLM:
            provider_id = "openai"
            provider_name = "synthetic"

            async def generate_text(self, prompt, *, route_target, api_key, **kwargs):
                observed.append((step_db.in_transaction(), route_target.remote_model_id, api_key))
                return json.dumps({"lines": [{"n": 1, "text": "Xin chào Gioan"}],
                                   "names": [{"source": "John", "translation": "Gioan", "type": "character"}]})

        monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
        ctx = WorkflowContext(project_id="one", source_language="en",
                              source_segments=[{"number": 1, "text": "Hello John"}])
        ctx.glossary = []
        await TranslateStage()._translate_transcript(ctx, step_db)
    assert observed == [(False, "text-exact", "request-local")]
    async with sessions() as db:
        terms = (await db.execute(select(ProjectGlossary).where(ProjectGlossary.project_id == "one"))).scalars().all()
        assert [(term.source_term, term.translated_term) for term in terms] == [("John", "Gioan")]


@pytest.mark.asyncio
async def test_unified_stt_uses_compatible_fallback_and_redacts_upstream_error(catalog, monkeypatch, tmp_path, caplog):
    from app.services.video_translator import translator_service as service
    import app.workflow.stages.analyze_stage as analyze_module

    sessions, path = catalog
    real_settings = service.get_settings()
    monkeypatch.setattr(service, "get_settings", lambda: real_settings.model_copy(update={"DATA_DIR": path}))
    monkeypatch.setattr(analyze_module, "async_session_factory", sessions)
    monkeypatch.setattr(service, "probe_duration_async", AsyncMock(return_value=1.0))
    async with sessions.begin() as db:
        first = await add_catalog_target(db, path, "openai", "speech-first", "secret-one", "STT")
        await add_catalog_target(db, path, "gemini", "speech-backup", "secret-two", "STT")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id=first.id, fallback_enabled=False))
    calls = []

    async def fail(*args, route_target, api_key, **kwargs):
        calls.append((route_target.remote_model_id, api_key))
        error = RuntimeError("provider said secret-one secret-two")
        error.http_status = 401
        raise error

    async def succeed(*args, route_target, api_key, **kwargs):
        calls.append((route_target.remote_model_id, api_key))
        return ([{"number": 1, "text": "Hello", "start_time": 0, "end_time": 1}], "en")

    monkeypatch.setattr(service, "transcribe_audio_with_whisper", fail)
    monkeypatch.setattr(service, "transcribe_audio_with_gemini", succeed)
    audio = tmp_path / "source.wav"
    audio.write_bytes(b"synthetic")
    ctx = WorkflowContext(project_id="one", audio_path=str(audio))
    await AnalyzeStage()._speech_to_text(ctx, None)
    assert calls == [("speech-first", "secret-one"), ("speech-backup", "secret-two")]
    assert ctx.source_segments[0]["text"] == "Hello"
    assert "secret-one" not in caplog.text
    assert "secret-two" not in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["analyze", "translate"])
async def test_unified_missing_canonical_default_fails_instead_of_env(catalog, monkeypatch, tmp_path, stage):
    from app.services.video_translator import translator_service as service
    import app.workflow.stages.analyze_stage as analyze_module
    import app.workflow.stages.translate_stage as translate_module

    sessions, path = catalog
    monkeypatch.setattr(analyze_module, "async_session_factory", sessions)
    monkeypatch.setattr(translate_module, "async_session_factory", sessions)
    async with sessions.begin() as db:
        await add_catalog_target(db, path, "openai", "available", "synthetic-key",
                                 "STT" if stage == "analyze" else "TRANSLATION")
    if stage == "analyze":
        monkeypatch.setattr(service, "probe_duration_async", AsyncMock(return_value=1.0))
        audio = tmp_path / "source.wav"
        audio.write_bytes(b"synthetic")
        ctx = WorkflowContext(project_id="one", audio_path=str(audio))
        with pytest.raises(RouteConfigurationError, match="default"):
            await AnalyzeStage()._speech_to_text(ctx, None)
    else:
        ctx = WorkflowContext(project_id="one", source_segments=[{"number": 1, "text": "Hello"}])
        with pytest.raises(RouteConfigurationError, match="default"):
            await TranslateStage()._translate_transcript(ctx, None)


@pytest.mark.asyncio
@pytest.mark.parametrize("function", ["stt", "translation"])
async def test_unrelated_catalog_state_preserves_unmigrated_legacy_function(catalog, monkeypatch, function):
    from app.services.video_translator import translator_service as service

    sessions, path = catalog
    async with sessions.begin() as db:
        await add_catalog_target(db, path, "anthropic", "unrelated", "synthetic-only", "TTS")
    unexpected = AsyncMock(side_effect=AssertionError("canonical route was activated"))
    monkeypatch.setattr(service, "build_route", unexpected)
    if function == "stt":
        real_settings = service.get_settings()
        monkeypatch.setattr(service, "get_settings", lambda: real_settings.model_copy(update={
            "GEMINI_API_KEY": "synthetic-legacy", "OPENAI_API_KEY": "", "ENABLE_OPENAI_FALLBACK": False,
        }))
        monkeypatch.setattr(service, "probe_duration_async", AsyncMock(return_value=1.0))
        legacy = AsyncMock(return_value=([{"number": 1, "text": "Hello"}], "en"))
        monkeypatch.setattr(service, "transcribe_audio_with_gemini", legacy)
        result = await service.speech_to_text_and_detect_language(path / "unused.wav", sessions=sessions)
        assert result[1] == "en"
        legacy.assert_awaited_once()
    else:
        class LegacyLLM:
            provider_id = "gemini"
            provider_name = "synthetic legacy"

            async def generate_text(self, prompt, **kwargs):
                return json.dumps({"lines": [{"n": 1, "text": "Xin chào"}], "names": []})

        monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LegacyLLM())
        result = await service.translate_transcript_segments([{"number": 1, "text": "Hello"}], "en", "vi",
                                                              sessions=sessions, data_dir=path)
        assert result[0]["translated_text"] == "Xin chào"
    unexpected.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("function", ["stt", "translation"])
async def test_non_gemini_catalog_default_cannot_escape_to_legacy(catalog, monkeypatch, function):
    from app.services.video_translator import translator_service as service

    sessions, path = catalog
    async with sessions.begin() as db:
        model = CatalogModel(provider_id="anthropic", remote_model_id="exact-anthropic",
                             source="manual", capability_status="UNKNOWN", capabilities=[])
        db.add(model)
        await db.flush()
        key = await (await CredentialService.open(db, path)).create("anthropic", "synthetic-secret")
        await db.flush()
        db.add(KeyModelAccess(key_id=key.id, model_id=model.id, provider_id="anthropic"))
        db.add(AIFunctionConfig(function_id=function, function_name=function, capability=function.upper(),
                                primary_provider_id="anthropic", model_id=model.id))
    legacy = AsyncMock()
    monkeypatch.setattr(service, "transcribe_audio_with_gemini", legacy)
    monkeypatch.setattr(service, "transcribe_audio_with_whisper", legacy)
    if function == "stt":
        monkeypatch.setattr(service, "probe_duration_async", AsyncMock(return_value=1.0))
        with pytest.raises(RouteExhausted, match="capability_mismatch"):
            await service.speech_to_text_and_detect_language(path / "unused.wav", sessions=sessions, data_dir=path)
    else:
        with pytest.raises(RuntimeError, match="TRANSLATION FAILED") as caught:
            await service.translate_transcript_segments([{"number": 1, "text": "Hello"}], "en", "vi",
                                                        sessions=sessions, data_dir=path)
        assert "synthetic-secret" not in str(caught.value)
        assert ".env" not in str(caught.value)
    legacy.assert_not_awaited()


@pytest.mark.asyncio
async def test_fresh_engine_resumes_translate_with_committed_analyze_checkpoint(tmp_path, monkeypatch):
    import app.workflow.workflow_engine as engine_module

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'workflow.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(engine_module, "async_session_factory", sessions)

    project_id = "project-resume"
    run_id = "run-resume"
    ctx = WorkflowContext(project_id=project_id, workflow_id=run_id)
    ctx.audio_path = str(tmp_path / "speech.wav")
    ctx.raw_transcript = "Hello there"
    ctx.source_segments = [{"number": 1, "start_time": 0, "end_time": 1,
                            "speaker_id": "Speaker 1", "text": "Hello there"}]
    ctx.speakers = [{"speaker_id": "Speaker 1", "speaker_name": "Speaker 1"}]
    ctx.glossary = [{"source_term": "Hello", "translated_term": "Xin chào"}]
    async with sessions.begin() as db:
        db.add(Project(id=project_id, title="Resume"))
        db.add(WorkflowExecution(id=run_id, project_id=project_id, workflow_type="video_translation",
                                 status=WorkflowEngineStatus.RUNNING.value, current_stage="TRANSLATE",
                                 context_data=ctx.to_dict()))

    class ResumeTranslate:
        STAGE_NAME = "TRANSLATE"
        STEPS = ["translate_transcript"]

        async def execute_step(self, step_name, loaded, db):
            assert loaded.source_segments == ctx.source_segments
            assert loaded.raw_transcript == "Hello there"
            assert loaded.speakers == ctx.speakers
            assert loaded.glossary == ctx.glossary
            assert not db.in_transaction(), "workflow DB transaction must close before provider I/O"
            loaded.translated_segments = [{**loaded.source_segments[0], "translated_text": "Xin chào"}]
            return {"translated_count": 1}

        async def run_qc(self, loaded):
            return {"passed": True, "issues": []}

    class Registry:
        def list_stages(self):
            return ["ANALYZE", "TRANSLATE"]

        def get_stage(self, name):
            assert name == "TRANSLATE"
            return ResumeTranslate()

    restarted = WorkflowEngine(registry=Registry())
    await restarted._run_workflow_loop(project_id, run_id)
    async with sessions() as db:
        saved = await db.get(WorkflowExecution, run_id)
        assert saved.status == WorkflowEngineStatus.COMPLETED.value
        assert saved.context_data["source_segments"] == ctx.source_segments
        assert saved.context_data["translated_segments"][0]["translated_text"] == "Xin chào"
    await engine.dispose()


@pytest.mark.asyncio
async def test_fresh_engine_retry_uses_committed_checkpoint(tmp_path, monkeypatch):
    import app.workflow.workflow_engine as engine_module

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'retry.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(engine_module, "async_session_factory", sessions)
    ctx = WorkflowContext(project_id="retry")
    ctx.source_segments = [{"number": 1, "text": "Hello"}]
    async with sessions.begin() as db:
        db.add(Project(id="retry", title="Retry"))
        db.add(WorkflowExecution(id="run-retry", project_id="retry", workflow_type="video_translation",
                                 status=WorkflowEngineStatus.FAILED.value, current_stage="TRANSLATE",
                                 context_data=ctx.to_dict()))
        db.add(WorkflowStageExecution(id="stage-retry", workflow_execution_id="run-retry",
                                      stage_name="TRANSLATE", status="failed"))
        db.add(WorkflowStepExecution(id="step-retry", stage_execution_id="stage-retry",
                                     step_name="translate_transcript", status="failed", error="old failure"))

    class RetryTranslate:
        STAGE_NAME = "TRANSLATE"
        STEPS = ["translate_transcript"]

        async def execute_step(self, step_name, loaded, db):
            assert loaded.source_segments == ctx.source_segments
            loaded.translated_segments = [{**loaded.source_segments[0], "translated_text": "Xin chào"}]
            return {"translated_count": 1}

        async def run_qc(self, loaded):
            return {"passed": True, "issues": []}

    class Registry:
        def list_stages(self):
            return ["ANALYZE", "TRANSLATE"]

        def get_stage(self, name):
            return RetryTranslate()

    restarted = WorkflowEngine(registry=Registry())
    await restarted.retry_stage("retry", "TRANSLATE")
    await restarted._active_tasks["retry"]
    async with sessions() as db:
        saved = await db.get(WorkflowExecution, "run-retry")
        step = await db.get(WorkflowStepExecution, "step-retry")
        assert saved.status == WorkflowEngineStatus.COMPLETED.value
        assert step.status == WorkflowStepStatus.SUCCESS.value
        assert saved.context_data["translated_segments"][0]["translated_text"] == "Xin chào"
    await engine.dispose()


@pytest.mark.asyncio
async def test_malformed_resume_checkpoint_fails_visibly_without_leaking_payload(tmp_path, monkeypatch):
    import app.workflow.workflow_engine as engine_module

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'invalid.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(engine_module, "async_session_factory", sessions)
    async with sessions.begin() as db:
        db.add(Project(id="invalid", title="Invalid"))
        db.add(WorkflowExecution(id="run-invalid", project_id="invalid", workflow_type="video_translation",
                                 status=WorkflowEngineStatus.RUNNING.value, current_stage="TRANSLATE",
                                 context_data={"project_id": "invalid", "source_segments":
                                               {"api_key": "secret-must-not-leak"}}))
    runner = WorkflowEngine()
    await runner._run_workflow_loop("invalid", "run-invalid")
    async with sessions() as db:
        saved = await db.get(WorkflowExecution, "run-invalid")
        assert saved.status == WorkflowEngineStatus.FAILED.value
        assert saved.error_message == "Invalid workflow checkpoint."
        assert "secret-must-not-leak" not in saved.error_message
    await engine.dispose()


@pytest.mark.asyncio
async def test_unified_step_failure_persists_only_sanitized_route_error(tmp_path, monkeypatch, caplog, capsys):
    import app.workflow.workflow_engine as engine_module
    import app.workflow.stages.analyze_stage as analyze_module
    from app.services.video_translator import translator_service as service

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'safe-failure.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(engine_module, "async_session_factory", sessions)
    monkeypatch.setattr(analyze_module, "async_session_factory", sessions)
    real_settings = service.get_settings()
    monkeypatch.setattr(service, "get_settings", lambda: real_settings.model_copy(update={"DATA_DIR": tmp_path}))
    monkeypatch.setattr(service, "probe_duration_async", AsyncMock(return_value=1.0))
    async with sessions.begin() as db:
        db.add(Project(id="safe", title="Safe"))
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
    async with sessions.begin() as db:
        model = await add_catalog_target(db, tmp_path, "openai", "speech-exact",
                                         "synthetic-upstream-secret", "STT")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id=model.id))
    audio = tmp_path / "source.wav"
    audio.write_bytes(b"synthetic")
    ctx = WorkflowContext(project_id="safe", audio_path=str(audio))
    async with sessions.begin() as db:
        db.add(WorkflowExecution(id="safe-run", project_id="safe", workflow_type="video_translation",
                                 status=WorkflowEngineStatus.RUNNING.value, current_stage="ANALYZE",
                                 context_data=ctx.to_dict()))

    async def fail(*args, **kwargs):
        error = RuntimeError("provider echoed synthetic-upstream-secret")
        error.http_status = 401
        raise error

    monkeypatch.setattr(service, "transcribe_audio_with_whisper", fail)

    class OnlySTT(AnalyzeStage):
        STEPS = ["speech_to_text"]

    class Registry:
        def list_stages(self):
            return ["ANALYZE"]

        def get_stage(self, name):
            return OnlySTT()

    runner = WorkflowEngine(registry=Registry())
    monkeypatch.setattr(engine_module.asyncio, "sleep", AsyncMock())
    await runner._run_workflow_loop("safe", "safe-run")
    async with sessions() as db:
        saved = await db.get(WorkflowExecution, "safe-run")
        steps = (await db.execute(select(WorkflowStepExecution))).scalars().all()
        key = (await db.scalars(select(APIKey))).one()
        assert saved.status == WorkflowEngineStatus.FAILED.value
        assert saved.error_message == "Configured AI model is unavailable, incompatible, or has no credential access."
        assert key.runtime_status == "invalid" and key.last_error_code == "auth"
        assert "AI route failed: auth" in caplog.text
        assert "synthetic-upstream-secret" not in str(saved.context_data) + saved.error_message + steps[0].error
    assert "synthetic-upstream-secret" not in caplog.text + capsys.readouterr().out
    await engine.dispose()
