"""
Unit tests verifying workflow lifecycle, state machine integrity,
one-shot auto confirm, and smart retry segment preservation.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.video_translator import (
    VideoTranslationJob,
    VideoTranslationSegment,
    TranslationJobStatus,
)


# ── Test 1: STAGE_MAP includes AUDIO_SCHEDULE_REVIEW in DUB (Stage 4) ─────────

def test_audio_schedule_review_stage_mapping():
    """Verify that AUDIO_SCHEDULE_REVIEW maps to DUB (Stage 4), NOT INGEST (Stage 1)."""
    import inspect
    from app.api.routes import video_translator

    source = inspect.getsource(video_translator.get_workflow_status_api)
    assert '"AUDIO_SCHEDULE_REVIEW": ("DUB", 4)' in source
    assert '"TTS_DONE": ("DUB", 4)' in source


# ── Test 2: Auto-confirm is strictly one-shot ─────────────────────────────────

@pytest.mark.asyncio
async def test_auto_confirm_is_strictly_one_shot():
    """auto_confirm_and_start_render_if_needed must only run once per job."""
    from app.api.routes.video_translator import auto_confirm_and_start_render_if_needed

    fake_job = VideoTranslationJob(
        id="JOB-ONESHOT-001",
        project_id="PROJ-001",
        status=TranslationJobStatus.SEGMENT_EDITING.value,
        stage="TRANSLATE",
        auto_confirm_translation=True,
        settings_snapshot_json="{}",
    )

    mock_session = AsyncMock()
    mock_session.execute.return_value = MagicMock(scalar_one_or_none=lambda: fake_job)

    with patch("app.api.routes.video_translator.async_session_factory") as mock_factory, \
         patch("app.api.routes.video_translator.execute_job_render_pipeline"):

        mock_factory.return_value.__aenter__.return_value = mock_session

        # First call: should succeed and confirm
        first_call = await auto_confirm_and_start_render_if_needed("JOB-ONESHOT-001")
        assert first_call is True

        snap = json.loads(fake_job.settings_snapshot_json)
        assert snap.get("auto_confirm_executed") is True

        # Second call: snap already has auto_confirm_executed=True -> must return False
        second_call = await auto_confirm_and_start_render_if_needed("JOB-ONESHOT-001")
        assert second_call is False


# ── Test 3: Completed job terminal status protection ──────────────────────────

@pytest.mark.asyncio
async def test_completed_job_terminal_status_protection():
    """Calling start, retry, or render on a COMPLETED job must return without re-running."""
    from app.api.routes.video_translator import (
        start_translation_pipeline,
        smart_retry_job_api,
        render_final_translated_video,
        auto_confirm_and_start_render_if_needed,
    )

    fake_job = VideoTranslationJob(
        id="JOB-COMPLETED-001",
        project_id="PROJ-001",
        status=TranslationJobStatus.COMPLETED.value,
        stage="COMPLETED",
        auto_confirm_translation=True,
    )

    mock_session = AsyncMock()
    mock_session.execute.return_value = MagicMock(scalar_one_or_none=lambda: fake_job)

    # 1. auto_confirm should return False on completed job
    with patch("app.api.routes.video_translator.async_session_factory") as mock_factory:
        mock_factory.return_value.__aenter__.return_value = mock_session
        assert await auto_confirm_and_start_render_if_needed("JOB-COMPLETED-001") is False

    # 2. start_translation_pipeline should return without started=True
    bg_tasks = MagicMock()
    res_start = await start_translation_pipeline("JOB-COMPLETED-001", bg_tasks, mock_session)
    assert res_start["data"]["started"] is False

    # 3. smart_retry_job_api should return without started=True
    res_retry = await smart_retry_job_api("JOB-COMPLETED-001", bg_tasks, mock_session)
    assert res_retry["data"]["started"] is False

    # 4. render_final_translated_video should return without rendering=True
    res_render = await render_final_translated_video("JOB-COMPLETED-001", bg_tasks, mock_session)
    assert res_render["data"]["rendering"] is False


# ── Test 4: Confirmed character voice review persists and proceeds past schedule ──

@pytest.mark.asyncio
async def test_confirmed_review_persists_in_snapshot():
    """confirm_character_voice_review must persist review_confirmed flag in settings snapshot."""
    from app.api.routes.video_translator import confirm_character_voice_review

    fake_job = VideoTranslationJob(
        id="JOB-REVIEW-CONFIRM-001",
        project_id="PROJ-REVIEW-001",
        status=TranslationJobStatus.NEEDS_REVIEW.value,
        stage="AUDIO_SCHEDULE_REVIEW",
        settings_snapshot_json="{}",
    )

    mock_session = AsyncMock()
    mock_session.execute.return_value = MagicMock(
        scalar_one=lambda: fake_job,
        scalar_one_or_none=lambda: fake_job,
        scalars=lambda: MagicMock(all=lambda: []),
    )

    bg_tasks = MagicMock()
    with patch("app.api.routes.video_translator.validate_character_voice_review", return_value={"data": {"passed": True}}):
        res = await confirm_character_voice_review("JOB-REVIEW-CONFIRM-001", bg_tasks, mock_session)

    assert res["success"] is True
    snap = json.loads(fake_job.settings_snapshot_json)
    assert snap.get("review_confirmed") is True
    assert snap.get("audio_schedule_confirmed") is True
    assert fake_job.last_checkpoint_stage == "CHARACTER_VOICE_REVIEW_DONE"
    assert fake_job.status == TranslationJobStatus.GENERATING_TTS.value
    assert fake_job.stage == "DUB"


# ── Test 5: Smart retry preserves segments for Phase 2 stages ──────────────────

@pytest.mark.asyncio
async def test_smart_retry_preserves_segments_for_phase2_stages():
    """When retrying at DUB/AUDIO_SCHEDULE_REVIEW, smart_retry resumes Phase 2 without re-translating."""
    from app.api.routes.video_translator import smart_retry_job_api

    fake_job = VideoTranslationJob(
        id="JOB-RETRY-PHASE2",
        project_id="PROJ-001",
        status=TranslationJobStatus.NEEDS_REVIEW.value,
        stage="AUDIO_SCHEDULE_REVIEW",
        last_checkpoint_stage="TRANSLATION_DONE",
    )
    fake_segment = VideoTranslationSegment(
        id=1,
        job_id="JOB-RETRY-PHASE2",
        segment_number=1,
        original_text="Hello",
        translated_text="Xin chào",
    )

    mock_session = AsyncMock()

    def mock_exec(stmt):
        stmt_str = str(stmt)
        m = MagicMock()
        if "video_translation_jobs" in stmt_str:
            m.scalar_one_or_none.return_value = fake_job
        elif "video_translation_segments" in stmt_str:
            m.scalar_one_or_none.return_value = fake_segment
        return m

    mock_session.execute = AsyncMock(side_effect=mock_exec)

    bg_tasks = MagicMock()
    with patch("app.api.routes.video_translator.signal_job_cancellation"):
        res = await smart_retry_job_api("JOB-RETRY-PHASE2", bg_tasks, mock_session)

    assert res["success"] is True
    assert res["data"]["phase"] == 2
    assert fake_job.stage == "DUB"
    assert fake_job.status == TranslationJobStatus.GENERATING_TTS.value
    # Background task should be execute_job_render_pipeline, NOT start_translation_pipeline
    bg_tasks.add_task.assert_called_once()


# ── Test 6: 42 segments with 22 verbatim echoes -> Targeted retry ONLY 22 -> Merge 42 ──

@pytest.mark.asyncio
async def test_verbatim_echo_targeted_retry_and_merge():
    """
    Production regression test:
    Input: 42 segments.
    Gemini initially translates 20 correctly and verbatim echoes 22.
    Workflow identifies the 22 echoes, retries ONLY those 22 invalid segments,
    preserves the 20 valid ones, merges 20 + 22 = 42 final segments.
    """
    from tests.unit.test_gemini_translation import MockLLM
    from app.services.video_translator.translator_service import translate_transcript_segments

    segments = [{"number": i, "text": f"中文句子 {i}"} for i in range(1, 43)]

    # Initial response: 20 valid Vietnamese, 22 verbatim echoed Chinese
    initial_lines = [{"n": i, "text": f"Câu dịch {i}"} for i in range(1, 21)] + [
        {"n": i, "text": f"中文句子 {i}"} for i in range(21, 43)
    ]
    resp_initial = json.dumps({"lines": initial_lines, "names": []}, ensure_ascii=False)

    # Targeted retry response: strictly ONLY the 22 invalid segments (21..42)
    retry_lines = [{"n": i, "text": f"Câu đã sửa {i}"} for i in range(21, 43)]
    resp_retry = json.dumps({"lines": retry_lines, "names": []}, ensure_ascii=False)

    mock_llm = MockLLM(responses=[resp_initial, resp_retry])

    with patch("app.services.video_translator.translator_service.get_registry") as mock_reg:
        reg_instance = MagicMock()
        reg_instance.get_llm.return_value = mock_llm
        mock_reg.return_value = reg_instance

        results = await translate_transcript_segments(
            segments=segments,
            source_language="Chinese",
            target_language="Vietnamese",
            job_id="TEST-VERBATIM-42",
            llm_provider_id="mock_gemini",
            batch_size=42,
        )

        assert len(results) == 42
        # First 20 segments must be preserved from the original valid translations
        for i in range(20):
            assert results[i]["translated_text"] == f"Câu dịch {i+1}"
        # Last 22 segments must be updated from the targeted retry
        for i in range(20, 42):
            assert results[i]["translated_text"] == f"Câu đã sửa {i+1}"

        # LLM was called twice: 1 full batch + 1 targeted retry of 22 segments
        assert mock_llm.call_count == 2
        # Verify targeted retry prompt only asked for the 22 invalid IDs
        retry_prompt = mock_llm.prompts[1]
        assert "Có 22 câu thoại bị giữ nguyên tiếng gốc" in retry_prompt
        assert '"n": 21' in retry_prompt
        assert '"n": 42' in retry_prompt
        assert '"text": "中文句子 1"' not in retry_prompt  # Did NOT re-request valid segment 1
        assert '"text": "中文句子 21"' in retry_prompt


# ── Test 7: Persistent verbatim echoes fail the provider cleanly and trigger failover ──

@pytest.mark.asyncio
async def test_verbatim_echo_persistent_triggers_validation_error_and_failover():
    """
    If a provider persistently returns verbatim echoes after retries,
    it must log the exact validation failure and failover to the next candidate provider.
    """
    from tests.unit.test_gemini_translation import MockLLM
    from app.services.video_translator.translator_service import translate_transcript_segments

    segments = [{"number": i, "text": f"中文句子 {i}"} for i in range(1, 43)]

    # Provider 1 persistently returns Chinese echoes on initial and retry attempts
    echo_lines = [{"n": i, "text": f"Câu dịch {i}"} for i in range(1, 21)] + [
        {"n": i, "text": f"中文句子 {i}"} for i in range(21, 43)
    ]
    resp_echo = json.dumps({"lines": echo_lines, "names": []}, ensure_ascii=False)
    provider1 = MockLLM(responses=[resp_echo, resp_echo, resp_echo, resp_echo])

    # Provider 2 translates all 42 segments cleanly to Vietnamese
    valid_lines = [{"n": i, "text": f"Bản dịch P2 câu {i}"} for i in range(1, 43)]
    resp_valid = json.dumps({"lines": valid_lines, "names": []}, ensure_ascii=False)
    provider2 = MockLLM(responses=[resp_valid])
    provider2._provider_id = "openai"

    with patch("app.services.video_translator.translator_service.get_registry") as mock_reg:
        with patch("app.services.video_translator.translator_service.get_settings") as mock_settings:
            settings_instance = MagicMock()
            settings_instance.DEFAULT_LLM_PROVIDER = "gemini"
            settings_instance.ENABLE_OPENAI_FALLBACK = True
            mock_settings.return_value = settings_instance

            reg_instance = MagicMock()
            def get_mock_llm(pid):
                if pid == "openai":
                    return provider2
                return provider1

            reg_instance.get_llm.side_effect = get_mock_llm
            mock_reg.return_value = reg_instance

            results = await translate_transcript_segments(
                segments=segments,
                source_language="Chinese",
                target_language="Vietnamese",
                job_id="TEST-VERBATIM-FAILOVER",
                llm_provider_id="gemini",
                batch_size=42,
            )

            assert len(results) == 42
            assert results[0]["translated_text"] == "Bản dịch P2 câu 1"
            assert results[41]["translated_text"] == "Bản dịch P2 câu 42"


