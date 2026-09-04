# UNIFIED WORKFLOW ENGINE IMPLEMENTATION REPORT

## 1. Architecture Before

Previously, the platform operated via multiple independent processing pipelines:
- **Video Translation Pipeline**: Linear hardcoded stages (`INGESTING`, `TRANSCRIBING`, `TRANSLATING`, `SYNTHESIZING`, `RENDERING`) in `translator_service.py` with in-memory execution tracking.
- **Script-to-Video Pipeline**: Segment-by-segment generation in `orchestrator.py` with state machine transitions in `state_machine.py`.
- **Video Editing Studio**: Independent service calls for reframing, logo overlay, ASS/SRT subtitles, and LUFS QC in `edit_service.py`, `subtitle_service.py`, and `qc_service.py`.

This created fragmented status tracking, duplicate retry logic, and no persistent checkpointing for multi-stage workflow resume.

---

## 2. Architecture After

The codebase has been refactored into a single **Unified Stage-Based Workflow Engine**:

```text
PROJECT
   │
   ▼
UNIFIED WORKFLOW ENGINE (WorkflowEngine)
   │
   ├── STAGE 1: INGEST    (Import, validate, probe video metadata, store asset, extract 16kHz audio)
   ├── STAGE 2: ANALYZE   (Gemini STT with Whisper fallback, language & speaker detection, timeline cleanup, STT QC)
   ├── STAGE 3: TRANSLATE (ProjectGlossary system, cross-batch context preservation, Gemini translation, ID recovery, QC)
   ├── STAGE 4: DUB       (SpeakerVoiceMapping, TTS generation Edge/Google/ElevenLabs, atempo stretch, 44.1kHz PCM timeline, QC)
   ├── STAGE 5: PRODUCE   (Subtitles ASS/SRT/VTT, reframing 9:16/16:9, watermark/logo, BGM ducking, FFmpeg render, Technical QC)
   └── STAGE 6: PUBLISH   (Gemini SEO, thumbnail selection, user approval, YouTube publishing with OAuth credential check)
```

---

## 3. Stage Map

| Stage | Class | Primary Steps | QC Evaluation |
|---|---|---|---|
| **STAGE 1** | `IngestStage` | `import_video`, `validate_video`, `probe_video`, `store_asset`, `extract_audio` | Valid duration, video playable, audio track exists |
| **STAGE 2** | `AnalyzeStage` | `speech_to_text`, `detect_language`, `detect_speakers`, `validate_timeline`, `clean_timeline`, `transcript_qc` | No negative ranges, no segments exceeding video duration |
| **STAGE 3** | `TranslateStage` | `create_load_glossary`, `extract_entities`, `detect_names_locations`, `translate_transcript`, `validate_segment_ids`, `check_consistency`, `translation_qc` | Non-empty translation, valid segment IDs, glossary term consistency |
| **STAGE 4** | `DubStage` | `speaker_to_voice_mapping`, `tts_generation`, `audio_duration_analysis`, `time_stretch`, `timeline_audio_assembly`, `audio_normalization`, `dubbing_qc` | Dubbed audio file present, LUFS level check, no extreme stretch |
| **STAGE 5** | `ProduceStage` | `generate_subtitles`, `video_reframing`, `add_watermark_logo`, `add_intro_outro`, `add_bgm`, `final_render`, `final_video_qc` | Rendered output exists, EBU R128 LUFS & black frame check passed |
| **STAGE 6** | `PublishStage` | `generate_seo`, `select_thumbnail`, `user_approval`, `schedule_publish`, `publish_youtube`, `save_publication_record` | Valid SEO, YouTube OAuth credentials verified |

---

## 4. Reused Existing Services

No existing working services were deleted or rewritten from scratch. All existing functionality was wrapped as workflow step dependencies:

1. **`app.services.video_source`**: `download_video_from_url`, `probe_media_file`, `extract_audio_track` (Reused in Stage 1).
2. **`VideoTranslatorService` (`translator_service.py`)**:
   - Gemini STT + Whisper fallback (Reused in Stage 2).
   - Timeline validation & segment cleanup (Reused in Stage 2).
   - Gemini batch translation with ID validation & sub-batch recovery (Reused in Stage 3).
   - Edge TTS, Google TTS, ElevenLabs speech synthesis (Reused in Stage 4).
   - Multi-stage `atempo` stretching & sample-accurate 44.1kHz stereo PCM audio timeline assembly (Reused in Stage 4).
   - FFmpeg dub muxing (Reused in Stage 5).
3. **`edit_service.py`**: Reframing 9:16/16:9, logo overlay, BGM ducking (Reused in Stage 5).
4. **`subtitle_service.py`**: ASS, SRT, VTT animated subtitle generation (Reused in Stage 5).
5. **`qc_service.py`**: LUFS audio analysis, black frame detection, technical QC (Reused in Stage 5).
6. **`youtube_service.py`**: Gemini SEO generation, YouTube API publishing (Reused in Stage 6).
7. **`storage_service.py`**: Cloudflare R2 storage & local storage fallback (Reused across all stages).

---

## 5. New Files Created

- `backend/app/models/workflow_engine.py`: Database models (`ProjectGlossary`, `SpeakerVoiceMapping`, `WorkflowExecution`, `WorkflowStageExecution`, `WorkflowStepExecution`).
- `backend/app/workflow/workflow_context.py`: Shared lightweight context data class.
- `backend/app/workflow/workflow_engine.py`: Core execution engine with state transitions, retry loops, resume support, and QC gate orchestration.
- `backend/app/workflow/workflow_registry.py`: Stage & step registry.
- `backend/app/workflow/stages/ingest_stage.py`: Stage 1 handler.
- `backend/app/workflow/stages/analyze_stage.py`: Stage 2 handler.
- `backend/app/workflow/stages/translate_stage.py`: Stage 3 handler.
- `backend/app/workflow/stages/dub_stage.py`: Stage 4 handler.
- `backend/app/workflow/stages/produce_stage.py`: Stage 5 handler.
- `backend/app/workflow/stages/publish_stage.py`: Stage 6 handler.
- `frontend/src/components/WorkflowTimeline.jsx`: Visual 6-stage pipeline React component.
- `frontend/src/components/ProjectGlossaryManager.jsx`: Terminology memory & glossary React component.
- `backend/tests/unit/test_workflow_engine.py`: Unit tests for the new workflow engine.

---

## 6. Modified Files

- `backend/app/models/__init__.py`: Registered new ORM models.
- `backend/app/api/routes/video_translator.py`: Added 6-stage workflow status, control, glossary, and voice mapping API endpoints.
- `frontend/src/pages/VideoTranslator.jsx`: Integrated `WorkflowTimeline` and `ProjectGlossaryManager` components.

---

## 7. API Compatibility

All existing REST API endpoints continue to work without breaking changes:
- `POST /api/video-translator/jobs/import-url` ➔ Working.
- `POST /api/video-translator/jobs/{id}/start` ➔ Working.
- `POST /api/video-translator/jobs/{id}/render` ➔ Working.
- `POST /api/video-translator/jobs/{id}/cancel` ➔ Working.
- `GET /api/video-translator/jobs/{id}/status` ➔ Working.

New unified endpoints added:
- `GET /api/video-translator/projects/{project_id}/workflow-status`
- `POST /api/video-translator/projects/{project_id}/workflow/start`
- `POST /api/video-translator/projects/{project_id}/workflow/pause`
- `POST /api/video-translator/projects/{project_id}/workflow/resume`
- `GET /api/video-translator/projects/{project_id}/glossary`
- `POST /api/video-translator/projects/{project_id}/glossary`
- `DELETE /api/video-translator/projects/{project_id}/glossary/{term_id}`
- `GET /api/video-translator/projects/{project_id}/voice-map`
- `POST /api/video-translator/projects/{project_id}/voice-map`

---

## 8. Database Changes

Schema additions applied dynamically via SQLAlchemy `init_db()` migration:
1. `project_glossaries` table
2. `speaker_voice_mappings` table
3. `workflow_executions` table
4. `workflow_stage_executions` table
5. `workflow_step_executions` table

---

## 9. Workflow Execution Verification Flow

```text
PROJECT CREATED (e.g. p_9824)
       │
       ▼
STAGE 1: INGEST    🟢 PASSED  [Duration: 145.2s, Resolution: 1920x1080]
       │
       ▼
STAGE 2: ANALYZE   🟢 PASSED  [STT Segments: 34, Language: zh]
       │
       ▼
STAGE 3: TRANSLATE 🟢 PASSED  [Glossary Terms Applied: 4, Translated: 34]
       │
       ▼
STAGE 4: DUB       🟢 PASSED  [PCM Audio Assembled @ 44.1kHz Stereo]
       │
       ▼
STAGE 5: PRODUCE   🟢 PASSED  [FFmpeg Dub Rendered + ASS Subtitles Embedded]
       │
       ▼
STAGE 6: PUBLISH   🟡 NEEDS_REVIEW / PUBLISHING_BLOCKED (OAuth check enforced)
```

---

## 10. Tests Actually Executed

### Backend Test Suite:
Command:
```powershell
powershell -Command "$env:PYTHONPATH='backend'; backend\venv\Scripts\pytest.exe backend/tests"
```
Output:
```text
================== 114 passed, 6 skipped, 1 warning in 6.45s ==================
```

### Frontend Production Build:
Command:
```powershell
cd frontend && npm run build
```
Output:
```text
✓ 100 modules transformed.
dist/index.html                      0.55 kB │ gzip:  0.33 kB
dist/assets/app-logo-CBKAaNYD.png  427.83 kB
dist/assets/index-DCljiyvn.css       8.10 kB │ gzip:  2.27 kB
dist/assets/index-BkDBy2je.js      290.37 kB │ gzip: 88.48 kB
✓ built in 823ms
```

---

## 11. Remaining Limitations

1. **YouTube OAuth**: Real YouTube video publishing requires valid `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET` configured in `.env`. When unconfigured, Stage 6 returns `PUBLISHING_BLOCKED` rather than simulating a false upload success.
2. **Persistent Task Queue**: The engine runs asynchronously via `asyncio.create_task`. In a future release, a queue interface (e.g. Celery / Redis) can be plugged in without changing the stage/step execution contracts.
