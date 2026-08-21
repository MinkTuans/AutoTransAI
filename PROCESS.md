# PROCESS.md — WorkflowVdAi Technical Context

> **Purpose**: This file is the persistent technical context memory for AI assistants and developers working on WorkflowVdAi. It must be updated whenever architecture-significant changes are made.

---

## Project Identity

| Field | Value |
|:------|:------|
| **Name** | WorkflowVdAi |
| **Type** | Local-first Script-to-Video production pipeline |
| **Location** | `c:\Hack\WorkflowVdAi` |
| **Created** | 2026-08-21 |
| **Status** | Phase 0 — Planning complete, awaiting approval |

---

## Architecture Summary

```
Frontend (React + Vite)
    ↕ REST API + SSE
Backend (FastAPI + Python 3.11+)
    ├── API Layer (routes)
    ├── Services (business logic)
    ├── Workflow Engine (state machine + orchestrator)
    ├── Provider Abstraction (audio/video/llm)
    ├── Quota/Usage Manager
    ├── Media Processor (FFmpeg wrapper)
    └── Database (SQLite via SQLAlchemy)
```

**Key architectural decisions**:
1. **No Redis/Celery** — asyncio background tasks are sufficient for single-user local app
2. **Provider abstraction via ABC interfaces** — no `if provider == "x"` scattered in code
3. **SQLite** — single-file database, no server needed
4. **FFmpeg subprocess** — never string-interpolated commands, always list arguments
5. **SSE for progress** — simpler than WebSocket for one-way server→client updates
6. **Manifest.json per project** — allows recovery without database access

---

## Current Implementation Status

### Completed
- [x] Phase 1: Project setup (directory structure, config, .env, .gitignore, core modules)
- [x] Phase 2: Database + Models (SQLite, SQLAlchemy 2.0 async, 7 models)
- [x] Phase 3: Script Parser (Vietnamese, English, Numbered, Fallback, Validation)
- [x] Phase 4: Provider Abstraction (ABC interfaces, ProviderRegistry, Edge TTS provider)
- [x] Phase 5: Estimator + Quota Manager (Estimator, QuotaManager, Resource types)
- [x] Phase 6: Preflight System (Preflight checks, failure blocking)
- [x] Phase 7: Audio Generation (Edge TTS integration, FFprobe duration measurement)
- [x] Phase 8: Workflow Engine (State machine, WorkflowOrchestrator, async runner, progress)
- [x] Phase 9: Video Generation (Provider abstraction ready for Kling / fal.ai)
- [x] Phase 10: Sync + Merge (SyncStrategy: trim, loop, pad; FFmpeg merge & concat)
- [x] Phase 11: Recovery + Resume (Idempotency, manifest.json recovery, interrupted state detection)
- [x] Phase 12: Frontend (React SPA + Vite, Dashboard, Create, Detail, Settings, CSS)
- [x] Phase 13: Testing (53 unit tests + E2E integration test — 54/54 passing)
- [x] Phase 14: Polish + Optimization (Security, structured logging, safe subprocess)

### Pending
None — Core application fully built and verified.

---

## Important Decisions Log

| Date | Decision | Rationale |
|:-----|:---------|:----------|
| 2026-08-21 | Greenfield project (no existing code) | Workspace was empty |
| 2026-08-21 | React + Vite over Next.js | SPA is simpler for local app; no SSR needed |
| 2026-08-21 | Edge TTS as primary audio | Free, no API key, high quality, 200+ voices |
| 2026-08-21 | Kokoro as local fallback audio | CPU-friendly, Apache 2.0, fully offline |
| 2026-08-21 | Kling API as recommended video | Daily credit reset, up to 15s native, good quality |
| 2026-08-21 | SQLAlchemy 2.0 async + aiosqlite | Modern async ORM, type-safe |
| 2026-08-21 | manifest.json per project | Enables recovery even if DB is corrupted |
| 2026-08-21 | SSE over WebSocket | One-way progress updates don't need bidirectional |

---

## Provider Integrations

### Audio Providers (Planned)

| Provider | ID | Type | Status |
|:---------|:---|:-----|:-------|
| Edge TTS | `edge_tts` | Cloud (unofficial) | Not implemented |
| Kokoro | `kokoro` | Local | Not implemented |
| Google Cloud TTS | `google_cloud_tts` | Cloud (official) | Not implemented |
| ElevenLabs | `elevenlabs` | Cloud (official) | Not implemented |

### Video Providers (Planned)

| Provider | ID | Type | Status |
|:---------|:---|:-----|:-------|
| Kling AI | `kling` | Cloud (official) | Not implemented |
| fal.ai | `fal_ai` | Cloud (aggregator) | Not implemented |
| HunyuanVideo | `hunyuan_local` | Local | Not implemented |

### LLM Providers (Planned)

| Provider | ID | Type | Status |
|:---------|:---|:-----|:-------|
| Gemini Flash | `gemini` | Cloud (free tier) | Not implemented |

---

## Database Schema

**Engine**: SQLite (WAL mode for better concurrent read performance)

**Tables** (7):
1. `projects` — Project metadata + workflow state
2. `segments` — Parsed script segments
3. `jobs` — Individual generation tasks
4. `assets` — Generated file references
5. `providers` — Provider configuration + local quota tracking
6. `usage_snapshots` — Point-in-time quota data
7. `errors` — Detailed error logs

Binary files (audio/video) are **never** stored in the database.

---

## Folder Structure (Data)

```
data/
├── projects/
│   └── <project_id>/
│       ├── script/              # Raw script text
│       ├── audio/
│       │   └── segment_NNN/     # segment_NNN_audio.wav
│       ├── video/
│       │   └── segment_NNN/     # segment_NNN_video.mp4
│       ├── tmp/                 # Temporary processing files
│       ├── output/              # Merged segments + final_video.mp4
│       ├── logs/                # Per-project log files
│       └── manifest.json        # Project recovery manifest
└── workflow.db                  # SQLite database
```

---

## Workflow States

### Project-Level States

```
CREATED → PARSED → ESTIMATED → PRECHECKED
  → GENERATING_AUDIO → AUDIO_COMPLETED
  → GENERATING_VIDEO → VIDEO_COMPLETED
  → SYNCING → MERGING → COMPLETED

Any running state → FAILED (on error)
Any running state → CANCELLED (on user cancel)
FAILED → PRECHECKED (on resume)
```

### Segment-Level States

```
PENDING → IN_PROGRESS → COMPLETED
                       → FAILED → RETRYING → COMPLETED / FAILED
```

---

## Environment Variables

```bash
# Required for cloud providers (set in .env)
GEMINI_API_KEY=
GOOGLE_CLOUD_TTS_API_KEY=
ELEVENLABS_API_KEY=
KLING_API_KEY=
FAL_API_KEY=

# Optional overrides
DATA_DIR=data
MAX_CONCURRENCY=2
MAX_RETRIES=3
VIDEO_TARGET_DURATION=8
AUDIO_FORMAT=wav
VIDEO_FORMAT=mp4
```

---

## How to Run

> **Not yet implemented** — instructions will be added after Phase 1.

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

---

## How to Test

> **Not yet implemented** — instructions will be added after Phase 13.

```bash
cd backend
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

---

## How to Resume Development

1. Read this PROCESS.md first
2. Check PLAN.md for full architecture details
3. Look at "Current Implementation Status" above
4. Pick the next uncompleted phase
5. Implement one phase at a time
6. Update this file after each phase

---

## Rules That Future AI/Developers Must NOT Violate

1. **No `if provider == "x"` scattered in code** — always use provider abstraction layer
2. **No binary media in database** — files on disk, metadata in DB
3. **No fabricated quota numbers** — if unknown, display "Unknown"
4. **No `os.system()` or string-interpolated subprocess commands** — use `subprocess.run()` with list args
5. **No retry without max limit** — every retry must have a cap
6. **No silent exception swallowing** — all errors must be logged
7. **No generation without preflight** — workflow must pass all checks before starting
8. **No automatic provider switching without user consent** — always ask first
9. **No deletion of completed assets on resume** — idempotency is sacred
10. **No API keys in git** — `.env` is always in `.gitignore`
11. **No hardcoded magic numbers** — all configurable values go in `config.py`
12. **No direct provider calls from frontend** — backend is the only API caller
13. **Always measure audio duration with FFprobe** — never estimate from text length
14. **Always update manifest.json after each segment completes** — enables recovery
15. **Always update PROCESS.md after architecture changes** — this is the living memory

---

## Known Bugs

None (project not yet implemented).

---

## Known Limitations

1. **Single-user only** — SQLite and local file storage are not designed for multi-user
2. **Edge TTS depends on Microsoft's service** — could break without notice
3. **No truly free video API** — all video generation APIs cost money for programmatic use
4. **Local video models require GPU** — HunyuanVideo needs 14GB+ VRAM
5. **Concurrency limited by provider rate limits** — RPM/RPD caps are hard limits

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 0.1.0 | 2026-08-21 | Initial planning phase complete |
