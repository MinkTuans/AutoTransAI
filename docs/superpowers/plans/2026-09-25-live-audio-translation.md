# Live Audio Translation Implementation Plan

> **For agentic workers:** Use the Superpowers test-driven-development workflow task by task. Steps use checkboxes for tracking.

**Goal:** Add an isolated Gemini Live speech-to-speech translation page that returns downloadable Vietnamese WAV audio.

**Architecture:** New FastAPI route and dedicated audio, WebSocket and job services. Existing workflow services remain untouched. The React page uses a small API client and the current `?page=` navigation.

**Tech Stack:** FastAPI, asyncio, websockets, FFmpeg, React, Vitest, pytest.

**Spec:** `docs/superpowers/specs/2026-09-25-live-audio-translation-design.md`

## Global Constraints

- Do not change the STT → Translation → Glossary → TTS workflow, default routing, voice assignment, or database schema.
- Live API credentials and model come only from dedicated settings.
- Limit uploaded audio to five minutes; reject longer input without automatic session continuation.
- Never expose credentials, raw upstream error bodies, or mutable provider state.

## Task 1: Audio boundary and Live adapter

**Files:** Create `backend/app/services/live_audio_translation/audio.py`, `live_api.py`; modify `backend/app/config.py`, `backend/requirements.txt`, `.env.example`; test `backend/tests/test_live_audio_service.py`.

- [ ] Write a failing test that converts a WAV to mono 16 kHz PCM, preserving duration, and rejects unsupported/long audio.
- [ ] Run that test and confirm failure due to missing adapter.
- [ ] Implement bounded FFprobe/FFmpeg conversion and rerun it.
- [ ] Write a failing synthetic WebSocket test asserting setup model and target `vi`, 100 ms PCM audio frames, `audioStreamEnd`, and collected 24 kHz output.
- [ ] Implement the isolated WebSocket adapter; rerun success, malformed, quota, timeout, model and connection tests.

## Task 2: Job lifecycle and HTTP API

**Files:** Create `backend/app/services/live_audio_translation/jobs.py`, `backend/app/api/routes/live_audio_translation.py`; modify `backend/app/main.py`; test `backend/tests/test_live_audio_api.py`.

- [ ] Write failing route tests for missing config, upload size/format, 202 start, status, cancellation and WAV result.
- [ ] Run tests and confirm the new route is absent.
- [ ] Implement process-local bounded job manager, per-job directory and new route; rerun tests.
- [ ] Assert no old provider registry, routing, glossary, or TTS service is called.

## Task 3: Standalone page

**Files:** Create `frontend/src/pages/LiveAudioTranslation.jsx`, `frontend/src/pages/LiveAudioTranslation.test.jsx`; modify `frontend/src/api.js`, `frontend/src/App.jsx`, `frontend/src/components/Navbar.jsx`; test frontend Vitest.

- [ ] Write failing DOM test for page navigation, upload/source/target fields, start, status, playback and download.
- [ ] Run test and confirm missing UI behavior.
- [ ] Implement page and navigation without changing existing pages; rerun frontend suite and build.

## Task 4: Documentation and regression

**Files:** Modify `PROJECT_KNOWLEDGE_BASE.md`, `CHANGELOG_AI.md`.

- [ ] Document API, config, five-minute cap, process-local state and no fallback.
- [ ] Run focused new tests and existing STT, translation, glossary, TTS, video tests.
- [ ] Run `git diff --check`, review scope, and report any unverified live-key behavior.
