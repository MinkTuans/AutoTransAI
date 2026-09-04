# WORKFLOWVDAI UNIFIED STAGE-BASED WORKFLOW ENGINE ARCHITECTURE & REFACTOR PLAN

## 1. Executive Summary & Core Requirements

This document outlines the architectural plan to refactor the **WorkflowVdAi** video translation and automation platform into a **unified 6-stage workflow engine**.

### Target Stages:
```text
PROJECT
   │
   ▼
UNIFIED WORKFLOW ENGINE
   │
   ├── STAGE 1: INGEST    (Import, validate, probe video, store asset, extract audio)
   ├── STAGE 2: ANALYZE   (Gemini/Whisper STT, language/speaker detection, timeline cleanup, STT QC)
   ├── STAGE 3: TRANSLATE (Project Glossary, cross-batch context, Gemini translation, ID recovery, QC)
   ├── STAGE 4: DUB       (Speaker-to-voice mapping, TTS generation, atempo stretch, 44.1kHz PCM timeline, QC)
   ├── STAGE 5: PRODUCE   (Subtitles ASS/SRT/VTT, reframing, watermark/logo, intro/outro, BGM ducking, QC)
   └── STAGE 6: PUBLISH   (Gemini SEO, thumbnail selection, user approval, YouTube publishing/blocked check)
```

---

## 2. Structural & Service Reuse Strategy

No working implementation will be deleted or rewritten from scratch. Existing services will be wrapped into single-responsibility Workflow Steps orchestrated by the core engine:

| Stage | Step | Wrapped Service / Implementation |
|---|---|---|
| **INGEST** | `ImportVideoStep`, `ProbeStep`, `ExtractAudioStep` | `app.services.video_source` & `app.services.storage_service` |
| **ANALYZE** | `SpeechToTextStep`, `TimelineCleanupStep` | `VideoTranslatorService.transcribe_video` (Gemini STT + Whisper fallback) |
| **TRANSLATE** | `GlossaryLoadStep`, `EntityExtractStep`, `TranslateBatchStep` | `VideoTranslatorService.translate_segments` + `ProjectGlossary` system |
| **DUB** | `VoiceMapStep`, `TTSGenerationStep`, `PCMAssemblyStep` | `VideoTranslatorService.synthesize_speech` & PCM timeline assembly |
| **PRODUCE** | `SubtitleStep`, `ReframeStep`, `WatermarkBGMStep`, `RenderStep` | `edit_service.py`, `subtitle_service.py`, `qc_service.py` |
| **PUBLISH** | `SEOGenerationStep`, `YouTubePublishStep` | `youtube_service.py` (with OAuth status enforcement) |

---

## 3. Database Schema Extensions (`backend/app/models/workflow_engine.py`)

New SQLAlchemy 2.0 async ORM models registered in `backend/app/models/__init__.py`:

```text
- ProjectGlossary
  * id, project_id, source_term, translated_term, term_type, confidence, source_context, approved, timestamps

- SpeakerVoiceMapping
  * id, project_id, speaker_id, speaker_name, voice_provider, voice_id, voice_settings, timestamps

- WorkflowExecution
  * id, project_id, workflow_type, status, current_stage, current_step, context_data, error_message, timestamps

- WorkflowStageExecution
  * id, workflow_execution_id, stage_name, status, started_at, completed_at, error, qc_report, retry_count

- WorkflowStepExecution
  * id, stage_execution_id, step_name, status, input_data, output_data, error, retry_count, timestamps
```

---

## 4. State Machine & Execution Lifecycle

### State Hierarchies:
- **Workflow State**: `NOT_STARTED`, `RUNNING`, `PAUSED`, `NEEDS_REVIEW`, `FAILED`, `COMPLETED`, `CANCELLED`
- **Stage State**: `PENDING`, `RUNNING`, `PASSED`, `FAILED`, `NEEDS_REVIEW`, `SKIPPED`
- **Step State**: `PENDING`, `RUNNING`, `SUCCESS`, `FAILED`, `RETRYING`, `SKIPPED`

### QC Gate Workflow:
```text
STAGE STEP EXECUTION
       ↓
STAGE QC EVALUATION
       ├── PASS ──────────► AUTOMATIC CONTINUATION (Next Stage)
       ├── FAIL (Retryable) ► AUTO-FIX & RETRY (Up to Max Retries)
       └── FAIL (Critical) ─► NEEDS_REVIEW (Pause for user approval / fix)
```

### Resume & Checkpoint Strategy:
Workflow checkpoints are persisted in SQLite after every completed step. If execution fails at Stage 4 Step 2 (`TTSGenerationStep`), resuming the workflow will read the DB checkpoint and restart cleanly from Stage 4 Step 2 without re-running Stage 1, Stage 2, or Stage 3.

---

## 5. API Compatibility Strategy

Existing API endpoints in `backend/app/api/routes/video_translator.py` and `projects.py` will act as **Adapters**:
- `POST /api/video-translator/jobs/{id}/start` ➔ Triggers `WorkflowEngine.start_workflow(project_id)`
- `POST /api/video-translator/jobs/{id}/resume` ➔ Triggers `WorkflowEngine.resume_workflow(project_id)`
- `GET /api/video-translator/jobs/{id}/status` ➔ Returns current stage, step, progress, and stage details from `WorkflowExecution`.

---

## 6. Frontend Visual Workflow Timeline UI

The React SPA interface will present an interactive 6-stage workflow component:
- Visual stage indicators (Ingest, Analyze, Translate, Dub, Produce, Publish).
- Stage progress bars, status indicators (🟢 Completed, 🟡 Needs Review, 🔴 Failed, ⚪ Waiting).
- Step level breakdown modal/drawer with error messages, retry buttons, and glossary/voice mapping controls.

---

## 7. Verification Plan

1. **Automated Tests**:
   - `tests/unit/test_workflow_engine.py`: Tests workflow initialization, execution, stage transitions, state persistence, error retries, and resume capability.
   - `tests/unit/test_glossary_context.py`: Tests project glossary lookup and cross-batch translation context preservation.
   - Run full pytest test suite (`pytest`) to ensure 0 regressions on existing unit/integration tests.
2. **Frontend Verification**:
   - `npm run build` in `frontend/` to verify Vite bundle compiles cleanly.
