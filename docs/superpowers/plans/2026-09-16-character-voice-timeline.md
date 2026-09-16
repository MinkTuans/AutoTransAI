# Character Voice and Audio Timeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add project-persistent Speaker → Character → Voice mapping, a conditional human-review gate, and post-TTS overlap-aware scheduling to the existing production video translation pipeline.

**Architecture:** Extend the existing SQLAlchemy models and route-driven pipeline in `video_translator.py`; retain `SpeakerVoiceMapping` as the compatibility link, add authoritative project character profiles and a provider-neutral voice pool, then schedule measured TTS clips before the existing PCM/FFmpeg render. New focused services own character mapping, voice assignment/validation, and timeline scheduling so the API route remains orchestration rather than business logic.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2 async, Alembic, Pydantic, pytest/pytest-asyncio, EdgeTTS/provider registry, FFprobe/FFmpeg, React/Vite.

**Spec:** `docs/superpowers/specs/2026-09-16-character-voice-timeline-design.md`

## Global Constraints

- Do not create a parallel pipeline or rewrite the production route flow.
- Preserve the existing `/voice-map` request and response keys.
- Never overwrite populated `original_start` or `original_end`.
- Never automatically change a user-confirmed Character Voice Profile.
- `auto_confirm_translation=true` must still pass Character/Voice validation.
- Measure TTS duration from the rendered audio file.
- Never schedule two clips using the same voice at overlapping times.
- Use real SQLAlchemy sessions and real service interfaces; do not add mock production implementations.
- Update `PROJECT_KNOWLEDGE_BASE.md` and `CHANGELOG_AI.md` after implementation.

---

## File Map

### Create

- `backend/app/services/video_translator/character_mapping_service.py`: normalize and persist AI/project-aware Speaker → Character proposals.
- `backend/app/services/video_translator/voice_assignment_service.py`: seed/query voice pool, reuse profiles, assign voices, build conflict graph, validate review state.
- `backend/app/services/video_translator/timeline_scheduler.py`: pure overlap detection and bounded scheduling from measured durations.
- `backend/alembic/versions/20260916_character_voice_timeline.py`: additive tables, columns, indexes, and compatibility backfill.
- `backend/tests/unit/test_stt_speaker_parsing.py`: STT speaker metadata behavior.
- `backend/tests/unit/test_character_mapping_service.py`: mapping confidence and separation behavior.
- `backend/tests/unit/test_voice_assignment_service.py`: profile reuse and voice conflicts.
- `backend/tests/unit/test_timeline_scheduler.py`: duration and overlap scheduling matrix.
- `backend/tests/integration/test_character_voice_review_api.py`: real-DB review gate and compatibility endpoints.
- `backend/tests/integration/test_character_voice_pipeline.py`: auto-confirm lifecycle through the new gate.

### Modify

- `backend/requirements.txt`: only if the declared `pydantic-settings` dependency is missing or malformed; otherwise install unchanged requirements.
- `backend/app/models/video_translator.py`: segment metadata and `needs_review` lifecycle value.
- `backend/app/models/workflow_engine.py`: extend `SpeakerVoiceMapping`; add `CharacterVoiceProfile` and `VoicePoolEntry`.
- `backend/app/models/__init__.py`: export new models.
- `backend/app/services/settings_service.py`: validated defaults for mapping and scheduling settings.
- `backend/app/services/video_translator/stt_parser.py`: preserve speaker fields.
- `backend/app/services/video_translator/translator_service.py`: preserve metadata through timeline cleanup/translation; render using scheduled timestamps.
- `backend/app/services/video_translator/sync_service.py`: consume scheduled placement/gain and reject same-voice overlap.
- `backend/app/api/routes/video_translator.py`: run mapping/validation gate, per-segment providers, scheduler, new review/profile/pool APIs, legacy API compatibility.
- `backend/app/workflow/workflow_context.py`: carry character/review/scheduled metadata.
- `backend/app/workflow/stages/analyze_stage.py`: use `speaker_id` consistently.
- `backend/app/workflow/stages/dub_stage.py`: delegate to the same mapping/assignment/scheduler services.
- `frontend/src/api.js`: review/profile/pool client functions.
- `frontend/src/pages/VideoTranslator.jsx`: review table, validation, confirm/resume, schedule metadata.
- `PROJECT_KNOWLEDGE_BASE.md`: architecture and contract documentation.
- `CHANGELOG_AI.md`: implementation and verification record.

---

### Task 1: Restore the Test Environment and Add the Database Contract

**Files:**
- Modify: `backend/app/models/video_translator.py`
- Modify: `backend/app/models/workflow_engine.py`
- Modify: `backend/app/models/__init__.py`
- Create: `backend/alembic/versions/20260916_character_voice_timeline.py`
- Test: `backend/tests/integration/test_character_voice_review_api.py`

**Interfaces:**
- Produces: `CharacterVoiceProfile`, `VoicePoolEntry`, extended `SpeakerVoiceMapping`, extended `VideoTranslationSegment`.
- Produces: `TranslationJobStatus.NEEDS_REVIEW = "needs_review"`.

- [ ] **Step 1: Install the declared backend dependencies and record the baseline**

Run:

```bash
cd backend
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q tests/unit/test_gemini_stt_parser.py tests/unit/test_timeline_validation.py tests/test_video_audio_sync.py
```

Expected: collection no longer fails on `pydantic_settings`. Record any remaining failures as baseline product failures or external FFmpeg/tooling failures before editing production code.

- [ ] **Step 2: Write failing real-model contract tests**

Add tests that create tables in the existing async test database and persist:

```python
profile = CharacterVoiceProfile(
    id="char-main",
    project_id=project.id,
    name="Main",
    gender="male",
    role="main",
    voice_provider="edge_tts",
    voice_id="vi-VN-NamMinhNeural",
    mapping_confidence=0.98,
    confirmed_by_user=True,
)
segment = VideoTranslationSegment(
    job_id=job.id,
    segment_number=1,
    start_time=1.0,
    end_time=2.0,
    original_start=1.0,
    original_end=2.0,
    speaker_id="SPEAKER_00",
)
```

Assert the profile round-trips, original timestamps remain unchanged after scheduled fields are updated, and `(provider, voice_id)` cannot be duplicated in `VoicePoolEntry`.

- [ ] **Step 3: Run the model test and verify RED**

Run:

```bash
pytest -q tests/integration/test_character_voice_review_api.py -k model_contract
```

Expected: FAIL because the new models/columns/status do not exist.

- [ ] **Step 4: Add the minimal ORM model changes**

Implement additive columns with nullable/default-safe definitions. Use a JSON column for `overlap_with`; use provider ID `edge_tts`, not the legacy shorthand `edge`. Add unique constraints/indexes for `(project_id, speaker_id)`, `(project_id, character_id)`, and `(provider, voice_id)`.

For historical compatibility, retain `start_time`, `end_time`, and all existing `SpeakerVoiceMapping` fields.

- [ ] **Step 5: Add the additive Alembic migration**

The upgrade must:

```python
op.add_column("video_translation_segments", sa.Column("original_start", sa.Float(), nullable=True))
op.add_column("video_translation_segments", sa.Column("original_end", sa.Float(), nullable=True))
op.execute("UPDATE video_translation_segments SET original_start = start_time WHERE original_start IS NULL")
op.execute("UPDATE video_translation_segments SET original_end = end_time WHERE original_end IS NULL")
```

Then add the remaining nullable/defaulted segment and mapping fields and create both new tables. Provide a symmetric downgrade that removes only artifacts introduced by this migration.

- [ ] **Step 6: Verify model and migration tests GREEN**

Run:

```bash
pytest -q tests/integration/test_character_voice_review_api.py -k model_contract
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

Expected: PASS against the configured test database. Do not run downgrade against user production data.

- [ ] **Step 7: Commit the database contract**

```bash
git add backend/app/models backend/alembic/versions/20260916_character_voice_timeline.py backend/tests/integration/test_character_voice_review_api.py
git commit -m "feat: add character voice timeline schema"
```

---

### Task 2: Preserve Speaker Metadata From STT Through Translation

**Files:**
- Modify: `backend/app/services/video_translator/stt_parser.py`
- Modify: `backend/app/services/video_translator/translator_service.py`
- Modify: `backend/app/api/routes/video_translator.py`
- Modify: `backend/app/workflow/stages/analyze_stage.py`
- Test: `backend/tests/unit/test_stt_speaker_parsing.py`
- Test: `backend/tests/unit/test_gemini_stt_parser.py`

**Interfaces:**
- Produces: normalized STT dictionaries containing `speaker_id`, `start_time`, `end_time`, `text`.
- Produces: `normalize_speaker_id(segment: dict, fallback_index: int) -> str`.

- [ ] **Step 1: Write failing speaker parser tests**

Cover upstream keys and conservative fallback:

```python
result = parse_gemini_stt_response(
    '{"segments":[{"start":0,"end":1,"text":"A","speaker":"SPEAKER_03"}]}',
    actual_chunk_dur=1.0,
)
assert result["segments"][0]["speaker_id"] == "SPEAKER_03"

unknown = parse_gemini_stt_response(
    '{"segments":[{"start":0,"end":1,"text":"A"},{"start":1,"end":2,"text":"B"}]}',
    actual_chunk_dur=2.0,
)
assert [s["speaker_id"] for s in unknown["segments"]] == ["UNRESOLVED_0001", "UNRESOLVED_0002"]
```

Also cover `speaker_id`, `speaker_label`, and preservation across timeline cleanup and translation ordering.

- [ ] **Step 2: Run speaker tests and verify RED**

Run:

```bash
pytest -q tests/unit/test_stt_speaker_parsing.py tests/unit/test_gemini_stt_parser.py
```

Expected: new assertions FAIL because normalization currently drops speaker metadata.

- [ ] **Step 3: Implement minimal normalization and propagation**

Read the first non-empty key from `speaker_id`, `speaker`, `speaker_label`, `speaker_tag`, and `diarization_label`. When absent, generate `UNRESOLVED_{index:04d}`. Preserve `speaker_id` inside `validate_and_clean_timeline_segments`, translation envelopes, and DB creation.

When persisting a new segment, set all four source fields once:

```python
start = float(seg["start_time"])
end = float(seg["end_time"])
VideoTranslationSegment(
    start_time=start,
    end_time=end,
    original_start=start,
    original_end=end,
    speaker_id=seg["speaker_id"],
    ...,
)
```

- [ ] **Step 4: Verify STT tests GREEN and existing translation tests remain green**

Run:

```bash
pytest -q tests/unit/test_stt_speaker_parsing.py tests/unit/test_gemini_stt_parser.py tests/unit/test_gemini_translation.py tests/unit/test_timeline_validation.py
```

- [ ] **Step 5: Commit speaker preservation**

```bash
git add backend/app/services/video_translator/stt_parser.py backend/app/services/video_translator/translator_service.py backend/app/api/routes/video_translator.py backend/app/workflow/stages/analyze_stage.py backend/tests/unit
git commit -m "feat: preserve STT speaker metadata"
```

---

### Task 3: Implement Conservative Character Mapping

**Files:**
- Create: `backend/app/services/video_translator/character_mapping_service.py`
- Modify: `backend/app/services/settings_service.py`
- Test: `backend/tests/unit/test_character_mapping_service.py`

**Interfaces:**
- Produces: `CharacterMappingDecision` dataclass.
- Produces: `CharacterMappingService.map_and_persist(db, project_id, job_id, segments, llm_provider) -> CharacterMappingResult`.
- Produces: `CharacterMappingResult.requires_review: bool` and `issues: list[dict]`.

- [ ] **Step 1: Write failing character mapping tests**

Use deterministic structured AI response inputs passed to the service parser, while persistence uses the real async database. Cover:

```python
assert result.by_speaker["SPEAKER_00"].character_id == result.by_speaker["SPEAKER_02"].character_id
assert result.by_speaker["SPEAKER_01"].character_id != result.by_speaker["SPEAKER_00"].character_id
```

Also assert a proposed merge at `0.70` with threshold `0.85` keeps both speakers separate, flags both for review, and never persists the low-confidence merge.

- [ ] **Step 2: Run mapping tests and verify RED**

Run:

```bash
pytest -q tests/unit/test_character_mapping_service.py
```

- [ ] **Step 3: Add validated settings defaults**

Add these `SystemSetting` defaults:

```python
"character_mapping_confidence_threshold": "0.85",
"character_scene_proximity_seconds": "1.0",
"scheduler_small_overlap_seconds": "0.25",
"scheduler_max_reschedule_seconds": "3.0",
"scheduler_max_tempo": "1.85",
"scheduler_ducking_gain": "0.45",
```

Provide a helper that reads a float, enforces an explicit allowed range, and falls back to the declared default. Business services call the helper; routes do not embed these values.

- [ ] **Step 4: Implement mapping validation and persistence**

Build one whole-transcript prompt, parse strict JSON, validate complete and unique speaker coverage, and match existing confirmed profiles first. Generate stable project-scoped character IDs for new separate proposals. If parsing or provider execution fails, persist one separate proposal per speaker and require review; do not fabricate a confident merge.

- [ ] **Step 5: Verify mapping tests GREEN**

Run:

```bash
pytest -q tests/unit/test_character_mapping_service.py tests/unit/test_terminology_memory.py
```

- [ ] **Step 6: Commit character mapping**

```bash
git add backend/app/services/settings_service.py backend/app/services/video_translator/character_mapping_service.py backend/tests/unit/test_character_mapping_service.py
git commit -m "feat: add conservative character mapping"
```

---

### Task 4: Implement Voice Pool, Profile Reuse, and Conflict Validation

**Files:**
- Create: `backend/app/services/video_translator/voice_assignment_service.py`
- Modify: `backend/app/providers/base.py`
- Test: `backend/tests/unit/test_voice_assignment_service.py`

**Interfaces:**
- Produces: `VoiceAssignmentService.refresh_provider_voices(db, provider) -> int`.
- Produces: `VoiceAssignmentService.assign_and_validate(db, project_id, segments) -> VoiceValidationResult`.
- Produces: `VoiceValidationResult.passed`, `assignments`, `conflicts`, `requires_review`.

- [ ] **Step 1: Write failing assignment tests**

Required cases:

- Main male receives `vi-VN-NamMinhNeural` when available.
- Main female receives `vi-VN-HoaiMyNeural` when available.
- Supporting characters receive distinct pool voices where possible.
- Two characters with overlapping source segments do not receive the same voice when an alternative exists.
- A confirmed profile is reused on a later job.
- Two conflicting confirmed profiles retain their voices and produce `requires_review=True`.
- One character across multiple segments receives one voice.

- [ ] **Step 2: Run assignment tests and verify RED**

Run:

```bash
pytest -q tests/unit/test_voice_assignment_service.py
```

- [ ] **Step 3: Implement pool refresh and conflict graph**

Convert existing `VoiceInfo` records directly into pool rows. Do not change provider-specific discovery contracts. Build graph edges when original intervals overlap or fall within configured scene proximity.

- [ ] **Step 4: Implement priority assignment and immutable confirmed profiles**

Assignment pseudocode:

```python
if profile.confirmed_by_user:
    keep(profile.voice_id)
elif profile.voice_id and pool_entry_enabled(profile):
    reuse(profile.voice_id)
else:
    assign(best_available_voice(character, neighboring_voice_ids))
```

If confirmed neighbors collide, return a review conflict without updating either profile.

- [ ] **Step 5: Verify assignment tests GREEN**

Run:

```bash
pytest -q tests/unit/test_voice_assignment_service.py
```

- [ ] **Step 6: Commit voice assignment**

```bash
git add backend/app/services/video_translator/voice_assignment_service.py backend/app/providers/base.py backend/tests/unit/test_voice_assignment_service.py
git commit -m "feat: add persistent character voice assignment"
```

---

### Task 5: Add the Character/Voice Review Gate and Backward-Compatible APIs

**Files:**
- Modify: `backend/app/api/routes/video_translator.py`
- Modify: `backend/app/workflow/workflow_context.py`
- Modify: `backend/app/workflow/stages/dub_stage.py`
- Modify: `frontend/src/api.js`
- Test: `backend/tests/integration/test_character_voice_review_api.py`
- Test: `backend/tests/integration/test_character_voice_pipeline.py`

**Interfaces:**
- Produces: `GET /jobs/{job_id}/character-voice-review`.
- Produces: `PUT /jobs/{job_id}/character-voice-review`.
- Produces: `POST /jobs/{job_id}/character-voice-review/validate`.
- Produces: `POST /jobs/{job_id}/character-voice-review/confirm-resume`.
- Produces: `GET /projects/{project_id}/character-profiles`.
- Produces: `GET /voice-pool` with provider/language/gender filters.

- [ ] **Step 1: Write failing API lifecycle tests**

With the real test database and FastAPI client, assert:

```python
response = await client.post(f"/api/video-translator/jobs/{job_id}/character-voice-review/validate")
assert response.json()["data"]["passed"] is False
assert refreshed_job.status == "needs_review"
assert tts_files_created == []
```

Cover low confidence, confirmed-profile conflict, editing Character/Voice, validate-again, and confirm/resume rejection until validation passes.

- [ ] **Step 2: Write failing `/voice-map` compatibility test**

POST the legacy body and assert existing keys and behavior remain:

```python
payload = {
    "speaker_id": "SPEAKER_00",
    "speaker_name": "Speaker 0",
    "voice_provider": "edge",
    "voice_id": "vi-VN-HoaiMyNeural",
}
assert saved["success"] is True
assert {"id", "speaker_id"} <= saved["data"].keys()
assert {"speaker_id", "speaker_name", "voice_provider", "voice_id"} <= listed[0].keys()
```

- [ ] **Step 3: Run route tests and verify RED**

Run:

```bash
pytest -q tests/integration/test_character_voice_review_api.py tests/integration/test_character_voice_pipeline.py
```

- [ ] **Step 4: Insert the gate into the production Phase 1 path**

After translated segments are committed and before `should_launch_render`:

```python
mapping = await character_mapper.map_and_persist(...)
voices = await voice_assigner.assign_and_validate(...)
if mapping.requires_review or not voices.passed:
    set_job_needs_review(...)
    should_launch_render = False
elif auto_confirm:
    should_launch_render = True
```

The existing translation review path remains available when auto-confirm is false. TTS is never queued from either path until Character/Voice validation passes.

- [ ] **Step 5: Implement atomic review edit, validation, and confirm/resume APIs**

Validate project/job ownership and provider/voice pool membership. Apply all submitted changes in one transaction. Confirm profiles only after validation passes. Reuse the existing `execute_job_render_pipeline(job_id)` entry point rather than creating a new worker path.

- [ ] **Step 6: Extend `/voice-map` additively**

Continue accepting `edge` and normalize it internally to `edge_tts` while retaining the legacy response value where required by an existing row. Link/create a character profile without removing old voice columns.

- [ ] **Step 7: Verify review lifecycle and auto-confirm GREEN**

Run:

```bash
pytest -q tests/integration/test_character_voice_review_api.py tests/integration/test_character_voice_pipeline.py tests/integration/test_auto_confirm_and_stage_sync.py tests/integration/test_video_translator_api.py
```

- [ ] **Step 8: Commit review gate and APIs**

```bash
git add backend/app/api/routes/video_translator.py backend/app/workflow frontend/src/api.js backend/tests/integration
git commit -m "feat: gate TTS on character voice validation"
```

---

### Task 6: Generate Per-Segment TTS and Measure Actual Duration

**Files:**
- Modify: `backend/app/api/routes/video_translator.py`
- Modify: `backend/app/services/video_translator/translator_service.py`
- Test: `backend/tests/unit/test_video_translator.py`
- Test: `backend/tests/integration/test_character_voice_pipeline.py`

**Interfaces:**
- Consumes: validated segment `voice_provider` and `voice_id`.
- Produces: measured `tts_duration` and unmodified raw TTS clip.

- [ ] **Step 1: Write failing per-segment TTS duration tests**

Generate real short WAV fixtures with FFmpeg, feed them through the same duration-probe and persistence function used after provider output, and assert FFprobe duration—not source slot duration—is persisted. Separately assert that segment provider/voice selection resolves the actual registered provider. Do not introduce a fake provider or alternate TTS implementation. Include audio longer and shorter than the original slot.

- [ ] **Step 2: Run TTS tests and verify RED**

Run:

```bash
pytest -q tests/unit/test_video_translator.py -k "per_segment_voice or actual_duration"
```

- [ ] **Step 3: Change the existing render loop surgically**

For each segment, resolve:

```python
provider = registry.get_audio(seg["voice_provider"] or job.audio_provider_id)
result = await provider.generate_audio(
    text=seg["translated_text"],
    voice_id=seg["voice_id"] or job.voice_id,
    output_path=seg_tts_path,
)
duration = await probe_duration_async(result.file_path)
```

Do not stretch clips in this step. Persist measured duration and selected provider/voice.

- [ ] **Step 4: Verify TTS duration tests GREEN**

Run:

```bash
pytest -q tests/unit/test_video_translator.py -k "per_segment_voice or actual_duration" tests/unit/test_edge_tts_timeout.py
```

- [ ] **Step 5: Commit per-segment TTS**

```bash
git add backend/app/api/routes/video_translator.py backend/app/services/video_translator/translator_service.py backend/tests
git commit -m "feat: render and measure per-character TTS"
```

---

### Task 7: Implement Bounded Overlap-Aware Timeline Scheduling

**Files:**
- Create: `backend/app/services/video_translator/timeline_scheduler.py`
- Modify: `backend/app/services/video_translator/translator_service.py`
- Test: `backend/tests/unit/test_timeline_scheduler.py`

**Interfaces:**
- Produces: `schedule_segments(segments, video_duration, policy) -> ScheduleResult`.
- Produces: per-segment `scheduled_start`, `scheduled_end`, `tempo`, `gain`, `overlap_with`, `schedule_action`.
- Produces: `ScheduleResult.requires_review` and `unresolved_conflicts`.

- [ ] **Step 1: Write the complete failing scheduling matrix**

Use pure data tests for:

- Two speakers overlap ≤0.25s with different voices → `kept_small_overlap`.
- Two speakers overlap ≤0.25s with same voice → `serialized_same_voice`.
- Large overlap → mild compression before reschedule.
- Three-speaker overlap → no same-voice collision.
- TTS longer than slot.
- TTS shorter than slot → preserve start and actual end.
- No bounded slot → `cannot_fit`, review required.
- Supporting duck only when compression/reschedule cannot preserve a different-voice overlap.

Example invariant:

```python
for left, right in combinations(result.segments, 2):
    if left.voice_id == right.voice_id:
        assert left.scheduled_end <= right.scheduled_start or right.scheduled_end <= left.scheduled_start
```

- [ ] **Step 2: Run scheduler tests and verify RED**

Run:

```bash
pytest -q tests/unit/test_timeline_scheduler.py
```

- [ ] **Step 3: Implement interval detection and bounded placement**

Keep the scheduler pure. Use measured duration, original order, configured `0.25s` small-overlap threshold, maximum tempo, maximum displacement, and video duration. Search the nearest legal gap before moving farther away. Never mutate `original_start/original_end`.

- [ ] **Step 4: Implement explicit failure and action metadata**

Every segment receives a stable action. If placement is impossible within bounds, retain a diagnostic proposal, set `cannot_fit`, enumerate conflicting segment IDs, and require review.

- [ ] **Step 5: Verify all scheduler tests GREEN**

Run:

```bash
pytest -q tests/unit/test_timeline_scheduler.py
```

- [ ] **Step 6: Commit scheduler**

```bash
git add backend/app/services/video_translator/timeline_scheduler.py backend/app/services/video_translator/translator_service.py backend/tests/unit/test_timeline_scheduler.py
git commit -m "feat: schedule overlapping dubbed speech"
```

---

### Task 8: Apply the Schedule to Audio and FFmpeg Rendering

**Files:**
- Modify: `backend/app/services/video_translator/sync_service.py`
- Modify: `backend/app/services/video_translator/translator_service.py`
- Modify: `backend/app/api/routes/video_translator.py`
- Test: `backend/tests/test_video_audio_sync.py`
- Test: `backend/tests/test_ffmpeg_filter.py`

**Interfaces:**
- Consumes: scheduled segment dictionaries with `voice_id`, `tempo`, and `gain`.
- Produces: synchronized WAV paths and a PCM timeline with no same-voice overlap.

- [ ] **Step 1: Write failing PCM and FFmpeg tests**

Generate three real PCM WAV files and verify:

- Different voices with allowed overlap are mixed.
- Same-voice overlap raises a scheduling invariant error instead of mixing.
- `ducked_supporting` applies configured gain only to that segment.
- Scheduled timestamps, not original timestamps, determine frame offsets.
- Final WAV duration equals video duration.

- [ ] **Step 2: Run audio tests and verify RED**

Run:

```bash
pytest -q tests/test_video_audio_sync.py tests/test_ffmpeg_filter.py
```

- [ ] **Step 3: Apply scheduler tempo and persist scheduled metadata**

Use the existing `stretch_and_normalize_audio`; pass the scheduler's target duration/tempo outcome instead of mechanically using `end_time-start_time`. Persist synchronized path and all schedule fields atomically.

- [ ] **Step 4: Make PCM assembly consume scheduled fields and gain**

Preflight all scheduled intervals. Reject same-voice intersections. Scale supporting PCM samples for duck actions before clipping-safe addition. Keep existing original-audio mux modes unchanged.

- [ ] **Step 5: Make final rendering read scheduled timestamps**

Build render dictionaries with:

```python
{
    "start_time": segment.scheduled_start,
    "end_time": segment.scheduled_end,
    "voice_id": segment.voice_id,
    "gain": schedule_gain(segment.schedule_action),
    "audio_path": segment.synced_audio_path or segment.tts_audio_path,
}
```

Abort to review before FFmpeg if any segment has `cannot_fit`.

- [ ] **Step 6: Verify audio and FFmpeg tests GREEN**

Run:

```bash
pytest -q tests/test_video_audio_sync.py tests/test_ffmpeg_filter.py tests/unit/test_timeline_scheduler.py
```

- [ ] **Step 7: Commit scheduled rendering**

```bash
git add backend/app/services/video_translator/sync_service.py backend/app/services/video_translator/translator_service.py backend/app/api/routes/video_translator.py backend/tests
git commit -m "feat: render scheduled multi-voice audio"
```

---

### Task 9: Add the Character and Voice Review UI

**Files:**
- Modify: `frontend/src/api.js`
- Modify: `frontend/src/pages/VideoTranslator.jsx`
- Modify: `frontend/src/App.css` only if existing inline/component styles cannot express the review state cleanly.

**Interfaces:**
- Consumes: review APIs from Task 5.
- Produces: editable Character/Voice review and read-only scheduling diagnostics.

- [ ] **Step 1: Add API client methods and a failing frontend build checkpoint**

Add:

```javascript
getCharacterVoiceReview: (jobId) => api.get(`/video-translator/jobs/${jobId}/character-voice-review`).then(r => r.data),
updateCharacterVoiceReview: (jobId, data) => api.put(`/video-translator/jobs/${jobId}/character-voice-review`, data).then(r => r.data),
validateCharacterVoiceReview: (jobId) => api.post(`/video-translator/jobs/${jobId}/character-voice-review/validate`).then(r => r.data),
confirmCharacterVoiceReview: (jobId) => api.post(`/video-translator/jobs/${jobId}/character-voice-review/confirm-resume`).then(r => r.data),
```

Run `npm run build` after referencing the new review panel but before defining it; verify the build fails for the missing symbol.

- [ ] **Step 2: Implement the smallest review panel in the existing Segment Editor**

Display Speaker, Character, Voice, Provider, confidence, conflict, original timeline, scheduled timeline, and schedule action. Allow Character and Voice changes only while review is required. Keep translated-text editing intact.

- [ ] **Step 3: Add Validate and Confirm & Resume state handling**

Disable confirm until the most recent server validation passes. Display server conflict reasons. After confirm, resume existing job polling; do not add a second frontend workflow.

- [ ] **Step 4: Verify production frontend build**

Run:

```bash
cd frontend
npm ci
npm run build
```

Expected: build succeeds without new warnings/errors.

- [ ] **Step 5: Commit UI**

```bash
git add frontend/src/api.js frontend/src/pages/VideoTranslator.jsx frontend/src/App.css
git commit -m "feat: add character voice review UI"
```

---

### Task 10: End-to-End Regression, Three-Speaker Fixture, and Documentation

**Files:**
- Modify: `backend/tests/integration/test_character_voice_pipeline.py`
- Modify: `PROJECT_KNOWLEDGE_BASE.md`
- Modify: `CHANGELOG_AI.md`

**Interfaces:**
- Verifies the complete production orchestration and documents final contracts.

- [ ] **Step 1: Add a three-speaker overlapping integration fixture**

Create or reuse a committed/generated test media fixture with three segment WAVs and at least one overlap. Run the real scheduler and PCM timeline assembly, then assert no same-voice scheduled intersection and probe the resulting audio/video stream.

- [ ] **Step 2: Run subsystem suites separately**

Run:

```bash
cd backend
pytest -q tests/unit/test_stt_speaker_parsing.py tests/unit/test_gemini_stt_parser.py
pytest -q tests/unit/test_character_mapping_service.py
pytest -q tests/unit/test_voice_assignment_service.py
pytest -q tests/unit/test_video_translator.py -k "per_segment_voice or actual_duration"
pytest -q tests/unit/test_timeline_scheduler.py
pytest -q tests/test_video_audio_sync.py tests/test_ffmpeg_filter.py
pytest -q tests/integration/test_character_voice_review_api.py tests/integration/test_character_voice_pipeline.py
```

Expected: every part passes independently.

- [ ] **Step 3: Run the full backend suite and frontend build**

Run:

```bash
cd backend
pytest -q
cd ../frontend
npm run build
```

Classify any failure explicitly as product code, unavailable external service, missing binary, database availability, or pre-existing baseline failure.

- [ ] **Step 4: Run migration and repository checks**

Run:

```bash
cd backend
alembic current
alembic upgrade head
cd ..
git diff --check
git status --short
```

- [ ] **Step 5: Update architecture documentation and changelog**

Document the actual route-driven flow, schema, review APIs, threshold settings,
profile priority, scheduling rules, test evidence, and any environment-limited
verification. Do not claim a live external TTS/video check if only generated
fixtures were available.

- [ ] **Step 6: Perform final requirement traceability review**

Map every required case in the spec to a named passing test. Confirm that:

- no populated original timestamp is assigned after segment creation/backfill;
- no confirmed voice is automatically changed;
- no same-voice scheduled intervals intersect;
- legacy `/voice-map` keys still exist;
- the production `execute_job_render_pipeline` consumes the new data.

- [ ] **Step 7: Commit verification and documentation**

```bash
git add backend/tests/integration/test_character_voice_pipeline.py PROJECT_KNOWLEDGE_BASE.md CHANGELOG_AI.md
git commit -m "docs: record character voice pipeline verification"
```

---

## Completion Report

Report:

- Exact files changed.
- Migration revision and upgrade behavior.
- New and modified APIs, including compatibility guarantees.
- Actual production pipeline flow.
- Subsystem and full-suite test counts/results.
- Three-speaker overlap fixture result.
- Environment failures separated from code failures.
- Any incomplete work and the concrete reason.
