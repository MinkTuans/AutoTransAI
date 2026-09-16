# Character Voice and Audio Timeline Design

## Purpose

Extend the existing AutoTransAI video translator pipeline with persistent
Speaker → Character → Voice mapping and post-TTS scheduling, without creating a
parallel pipeline or rewriting the existing STT → Translation → TTS → FFmpeg
flow.

The implementation must preserve current API behavior and existing single-voice
projects while allowing multi-character dubbing to proceed automatically when
mapping and voice validation are safe. Jobs requiring human decisions stop
before TTS in `needs_review`.

## Current Architecture and Integration Point

The production job path is implemented in
`backend/app/api/routes/video_translator.py`:

1. Extract audio.
2. Run STT and language detection.
3. Translate and persist `VideoTranslationSegment` rows.
4. Optionally auto-confirm translation.
5. Generate one TTS clip per segment with the job-level voice.
6. Stretch each clip to the STT slot.
7. Build a PCM timeline and mux it into the source video.

The workflow stage classes describe similar behavior, but they are not the
authoritative production path. New behavior therefore integrates into the
route-driven production path first. `AnalyzeStage`, `DubStage`, and
`WorkflowContext` are updated only to keep the documented workflow interface
consistent.

The existing `SpeakerVoiceMapping` table and `/voice-map` API remain supported.
They become the compatibility and Speaker → Character association layer rather
than being replaced.

## Data Model

### VideoTranslationSegment

Existing `start_time` and `end_time` remain readable for backward compatibility.
New code treats their existing values as the source timeline and copies them
into immutable-in-practice fields when segments are created:

- `speaker_id`: stable speaker label returned by STT, or a deterministic
  per-segment fallback when STT supplies no speaker information.
- `character_id`: project character selected by mapping.
- `voice_provider`: provider used for this segment.
- `voice_id`: voice used for this segment.
- `original_start`: STT start time. Never changed by mapping, TTS, or scheduling.
- `original_end`: STT end time. Never changed by mapping, TTS, or scheduling.
- `scheduled_start`: actual start selected for the synthesized clip.
- `scheduled_end`: actual end after compression/rescheduling.
- `tts_duration`: measured from the generated audio file after TTS succeeds.
- `overlap_with`: JSON list of segment IDs that overlap in the source or
  scheduled timeline.
- `schedule_action`: stable action code plus concise details.
- `mapping_confidence`: confidence used by the review gate.

For old rows, a compatibility normalization step initializes missing
`original_start/original_end` from `start_time/end_time` without overwriting
already populated original values.

### SpeakerVoiceMapping

The existing table remains in place and retains its existing fields. Add:

- `character_id`, nullable for legacy rows.
- `confidence`, defaulting conservatively for legacy records.
- `needs_review`.

The unique logical identity is `(project_id, speaker_id)`. Existing callers may
continue to save `speaker_name`, `voice_provider`, and `voice_id`. When a legacy
write provides a voice, the service synchronizes it into the linked character
profile if safe. The response retains every existing key and may append
character metadata.

### CharacterVoiceProfile

This is the authoritative project-scoped voice assignment:

- `id` / `character_id`.
- `project_id`.
- `name`.
- `gender`: `male`, `female`, `unknown`.
- `role`: `main`, `supporting`.
- `voice_provider`.
- `voice_id`.
- `mapping_confidence`.
- `confirmed_by_user`.
- created/updated timestamps.

The logical identity is `(project_id, character_id)`. A user-confirmed profile
has the highest priority. Automatic mapping and the scheduler must never change
its voice. Profiles are reused by every job/episode in the same project.

### VoicePoolEntry

Provider-independent voice inventory:

- `id`.
- `provider`.
- `language`.
- `gender`.
- `voice_id`.
- `display_name`.
- `enabled`.
- optional provider metadata.

`(provider, voice_id)` is unique. Provider discovery refreshes the pool without
changing Character Mapping contracts. The initial EdgeTTS pool guarantees the
preferred Vietnamese voices are represented:

- Main male: `vi-VN-NamMinhNeural`.
- Main female: `vi-VN-HoaiMyNeural`.

Supporting characters prefer distinct enabled voices, including foreign EdgeTTS
voices when necessary.

## STT Speaker Preservation

STT normalization accepts `speaker_id`, `speaker`, `speaker_label`, and common
diarization equivalents. When upstream STT supplies speaker data, it is
preserved unchanged after safe string normalization.

When STT supplies no speaker data, the system does not pretend to have performed
diarization. It assigns deterministic fallback IDs that keep segments distinct
for conservative character mapping. No second diarization subsystem is added.

Every normalized STT segment contains `speaker_id`, `start_time`, `end_time`,
and `text`. Translation copies speaker and original timeline metadata through
unchanged.

## Character Mapping

Character Mapping analyzes the complete translated transcript and its speaker
labels in one project-aware operation. The model returns structured candidate
characters, names when recognizable, gender, role, speaker membership,
confidence, and evidence/reason codes.

The service validates AI output before persistence:

- Every source speaker appears exactly once.
- Unknown speaker IDs are rejected.
- Duplicate assignment of one speaker is rejected.
- A proposed multi-speaker merge below the configured threshold is not applied.
- Uncertain speakers remain separate characters.
- Existing user-confirmed project profiles are matched before new characters
  are created.

`character_mapping_confidence_threshold` is a `SystemSetting`, default `0.85`.
The mapping service reads and validates it through the settings layer. Routes do
not contain the numeric threshold.

A confidence below the threshold, ambiguous merge, unresolved character, or
invalid AI response marks the affected mapping as `needs_review`. Safe separate
speaker identities are persisted so the UI has an editable proposal, but the
job does not enter TTS.

## Voice Assignment and Conflict Validation

Assignment priority is:

1. User-confirmed `CharacterVoiceProfile`.
2. Existing project profile reused from an earlier episode.
3. Main male → Vietnamese male preference.
4. Main female → Vietnamese female preference.
5. Supporting → a different enabled Voice Pool entry.

The service builds a character conflict graph from segments whose original
timelines overlap or are within the configured scene proximity. It avoids using
one voice for adjacent/conflicting characters while alternatives exist.

If two user-confirmed profiles conflict, neither is changed. The job becomes
`needs_review`. A lack of eligible voices, invalid provider/voice pair, disabled
voice, or unresolved mapping also fails validation.

Successful validation stamps provider and voice onto each segment. The render
pipeline resolves the provider per segment through the existing provider
registry; it no longer assumes one provider/voice for all segments. The
job-level provider and voice remain fallback values for legacy jobs.

## Review Gate and Job Lifecycle

`auto_confirm_translation=true` skips translation text review only. After
translation, all jobs execute:

1. Character Mapping.
2. Voice Assignment.
3. Character/Voice validation.

If validation passes, the existing render pipeline continues automatically.
If it fails, the job is set to `needs_review`, its stage identifies Character
and Voice review, and no TTS request is made.

The review API allows changing Speaker → Character associations and character
voice profiles. Validation runs again against real persisted data. Resume is
accepted only when validation passes; it then launches the existing TTS render
pipeline. Confirming review sets `confirmed_by_user` and persists profiles for
future episodes.

## Post-TTS Timeline Scheduler

TTS audio is generated first. `tts_duration` is measured from the rendered file
with FFprobe and is never inferred from the STT slot.

The scheduler starts from `original_start/original_end`, preserving the source
conversation rhythm. It uses these policies:

- Overlap up to and including `0.25s`, different voices: preserve when valid.
- Overlap up to and including `0.25s`, same voice: serialize locally.
- Larger overlap: attempt mild time compression first.
- If compression is insufficient, use the nearest bounded gap while preserving
  order and minimizing displacement.
- If different voices still must overlap, duck a supporting character only as
  the final automatic option.
- Two clips with the same voice must never overlap in the scheduled timeline.

Rescheduling is bounded by configurable maximum displacement and video duration.
It must not extend the timeline indefinitely. If no valid slot exists, the
scheduler emits `cannot_fit` with conflict metadata and sends the job to
`needs_review` rather than silently truncating or mixing same-voice speech.

Stable schedule action codes include:

- `kept_original`
- `kept_small_overlap`
- `compressed`
- `rescheduled`
- `compressed_and_rescheduled`
- `ducked_supporting`
- `serialized_same_voice`
- `cannot_fit`

The scheduler writes only `scheduled_start`, `scheduled_end`, `overlap_with`,
and `schedule_action`. It does not modify either original timestamp.

## PCM Timeline and FFmpeg

The existing `VideoAudioSyncService` remains the audio assembly implementation.
It consumes scheduled timestamps and per-segment gain/action metadata.

PCM assembly must explicitly reject an overlapping same-voice pair that escaped
scheduling. Different-voice overlaps are mixed with clipping protection; only a
segment marked `ducked_supporting` receives reduced gain. The final FFmpeg mux,
original-audio mode, watermark, output validation, and storage flow remain
unchanged.

## API Contract

The existing endpoints remain valid:

- `GET /api/video-translator/projects/{project_id}/voice-map`
- `POST /api/video-translator/projects/{project_id}/voice-map`

Their existing response keys are preserved. New character/profile information
is additive.

New endpoints provide:

- Job Character/Speaker/Voice review state.
- Atomic review edits for speaker-character links and character profiles.
- Validation without starting TTS.
- Confirm-and-resume after successful validation.
- Project Character Voice Profiles.
- Voice Pool listing, filtered by provider/language/gender.

Invalid resume requests return a validation response and do not enqueue TTS.

## UI

The existing Segment Editor is extended rather than replaced. Before TTS it
shows:

- Speaker.
- Character.
- Voice.
- Provider.
- Confidence.
- Conflict reason.
- Original timeline.
- Scheduled timeline when available.
- Schedule action when available.

For `needs_review`, Character and Voice are editable. “Validate” refreshes the
persisted validation result. “Confirm & Resume TTS” is enabled only after a
passing validation. Auto-safe jobs do not require UI interaction.

## Backward Compatibility and Migration

An Alembic migration creates the two new tables and adds nullable/defaulted
columns. Existing segment rows and voice-map rows remain valid. Runtime
compatibility normalization handles historical jobs without rewriting original
timestamps repeatedly.

Legacy jobs with no character mapping continue to use the job-level voice only
when they predate the new review gate. Newly translated jobs must pass the new
gate.

## Testing and Verification

Tests use the repository's real SQLAlchemy models, async database sessions,
provider interfaces, generated WAV fixtures, FFprobe, and FFmpeg where required.
No fake production implementation is introduced to satisfy tests.

Each subsystem is verified separately before integration:

1. STT speaker parsing and preservation.
2. Character mapping, including separate fallback and low confidence.
3. Project profile reuse and voice assignment.
4. Actual TTS duration probing.
5. Overlap detection.
6. Timeline scheduling.
7. PCM assembly and FFmpeg mux.
8. Route lifecycle and `/voice-map` compatibility.
9. Frontend production build.

Required cases include:

- Two overlapping speakers with different voices.
- Two overlapping speakers with the same voice.
- Three overlapping speakers.
- One character appearing in multiple segments.
- Mapping confidence below threshold.
- A confirmed profile involved in a voice conflict.
- TTS longer than its source slot.
- TTS shorter than its source slot.
- No bounded replacement slot available.
- `auto_confirm_translation=true` still entering the validation gate.
- Backward-compatible `/voice-map` request and response behavior.

The final acceptance check uses a video with at least three speakers and at
least two overlapping speakers. The resulting schedule and audio output must
prove that one voice never speaks two clips simultaneously.

The Python environment is installed from `backend/requirements.txt` because
`pydantic-settings` is already a legitimate declared dependency. Test reporting
distinguishes dependency/tooling failures from product-code failures.

## Documentation

On implementation completion, update `PROJECT_KNOWLEDGE_BASE.md` with the data
model, gate, APIs, and scheduler behavior, and append the completed change and
verification evidence to `CHANGELOG_AI.md`.
