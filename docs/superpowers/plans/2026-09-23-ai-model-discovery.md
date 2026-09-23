# AI Model Discovery and Routing Implementation Plan

> **For agentic workers:** Implement task by task with test-first changes and review checkpoints. The user-approved audit and 10-phase roadmap in the conversation are the specification for this plan.

**Goal:** Discover provider models through credentials, maintain a safe refreshable catalog, and route every AI function through compatible models without exposing API keys.

**Architecture:** Introduce a canonical provider-scoped catalog and encrypted credential store alongside legacy tables, then move API and pipeline consumers to immutable routing targets. Explicit refresh alone retires absent discovered models. Preserve Edge TTS and historical snapshots.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy async, SQLite/MySQL, React/Vite.

**Spec:** User-approved 18-section audit and 10-phase roadmap delivered in this conversation on 2026-09-23.

## Global Constraints

- No migration may delete production models, keys, project settings, or historical job snapshots.
- Adding or deleting a key never removes a catalog model; only explicit complete refresh retires discovered models.
- A failed, partial, unsupported, malformed, or ambiguous empty discovery result cannot authorize cleanup.
- A completely unknown model receives FULL_UNKNOWN and remains selectable for every function.
- Edge TTS is keyless and is never removed by provider refresh.
- Plaintext API keys cannot appear in read responses, logs, error DTOs, or media/download paths.
- Preserve the existing dark theme and API response envelope while migrating consumers.
- Use a failing test before each production behavior change. Keep commits reviewable.

---

### Task 1: Isolate secrets from media and tests

**Files:** `backend/app/main.py`, `backend/app/api/routes/storage.py`, `backend/app/config.py`, `backend/tests/`.

- [ ] Add failing tests showing requests cannot retrieve the key store, database, or encryption key through static media or storage routes.
- [ ] Confirm the tests fail against current source.
- [ ] Restrict media serving to validated media roots and put credential storage outside that root.
- [ ] Run the focused tests and a safe isolated backend test subset.
- [ ] Document compatibility and commit.

### Task 2: Canonical catalog and encrypted key domain

**Files:** `backend/app/models/ai_catalog.py`, `backend/app/models/api_key.py`, `backend/app/models/__init__.py`, `backend/app/services/credential_service.py`, `backend/alembic/versions/`, isolated tests.

- [ ] Test provider plus remote ID uniqueness, many-key access, key deletion retention, encrypted storage, and missing master key failure.
- [ ] Confirm the new tests fail.
- [ ] Add additive tables and versioned migration with no old-table rewrite or auto-cleanup.
- [ ] Add stable key IDs, masked DTOs, keyed duplicate detection, and fail-closed decryption.
- [ ] Run DB and credential tests on SQLite; prepare a MySQL migration fixture path.
- [ ] Commit.

### Task 3: Provider discovery adapters

**Files:** `backend/app/providers/discovery/`, `backend/app/services/model_discovery_service.py`, fixtures/tests.

- [ ] Test complete pagination, normalization, duplicate IDs, safe metadata, and classified failures.
- [ ] Confirm tests fail.
- [ ] Implement official list-model adapters for Gemini, OpenAI, Anthropic, ElevenLabs, and Fal where documented; represent unsupported providers honestly.
- [ ] Bound pages, bytes, model counts and credential forwarding; avoid generation probes.
- [ ] Run discovery tests and commit.

### Task 4: Additive key discovery and explicit refresh

**Files:** `backend/app/services/model_refresh_service.py`, `backend/app/services/credential_service.py`, `backend/app/models/ai_catalog.py`, tests.

- [ ] Test A/B/C union, key deletion retention, full-refresh retirement, partial-error preservation, Edge preservation, and concurrent key rotation.
- [ ] Confirm tests fail.
- [ ] Stage discovery outside the write transaction; reconcile complete provider snapshots transactionally with revision checks.
- [ ] Reconcile invalid defaults deterministically or set visible configuration error.
- [ ] Run focused tests and commit.

### Task 5: Capability registry and routing contract

**Files:** `backend/app/services/capability_registry.py`, `backend/app/services/ai_routing/`, `backend/app/services/model_resolver.py`, tests.

- [ ] Test known capabilities, known negative, FULL_UNKNOWN, provider/model consistency, key access and fallback ordering.
- [ ] Confirm tests fail.
- [ ] Add evidence-based capabilities and immutable request-scoped targets.
- [ ] Add bounded retries, model-aware key selection and sanitized aggregate errors.
- [ ] Run focused tests and commit.

### Task 6: Route actual pipeline consumers

**Files:** `backend/app/services/video_translator/translator_service.py`, `backend/app/api/routes/video_translator.py`, `backend/app/workflow/`, `backend/app/providers/`, auxiliary LLM services, tests.

- [ ] Write failing tests proving configured provider, remote model and key reach STT/translation/TTS/video/image calls, including two concurrent jobs.
- [ ] Remove mutable adapter model state and hardcoded request models in small modality batches.
- [ ] Preserve confirmed TTS voices, fix workflow context hydration, and include route identity in TTS cache.
- [ ] Bound translation/glossary requests by effective model limits.
- [ ] Verify Studio, Unified, and legacy paths; commit each independently testable modality batch.

### Task 7: Backend APIs and compatibility

**Files:** `backend/app/api/routes/models.py`, `providers.py`, `settings.py`, schemas, tests.

- [ ] Test masked key CRUD, additive add, explicit refresh status, paginated search, catalog details, function defaults, and immutable discovered records.
- [ ] Confirm tests fail.
- [ ] Implement typed APIs and compatibility wrappers; GET requests cannot seed remote models or mutate defaults.
- [ ] Run API contract tests and commit.

### Task 8: Catalog and picker UI

**Files:** `frontend/src/pages/Settings.jsx`, `frontend/src/api.js`, `frontend/src/components/settings/`, `frontend/package.json`, UI tests.

- [ ] Test dynamic provider grouping, search/filter, FULL_UNKNOWN, no-key and empty states, refresh behavior, and removed defaults.
- [ ] Confirm tests fail.
- [ ] Replace manual model management with provider catalog and capability-aware picker; place Refresh Models before Add Key.
- [ ] Remove primary/fallback controls; retain the current visual language.
- [ ] Run UI tests/build and commit.

### Task 9: Data migration and cutover

**Files:** migration utilities, Alembic revisions, compatibility adapters, migration tests.

- [ ] Test idempotent import of legacy catalog/keys/mappings, provider ID collisions, historical snapshots, and startup-managed versus Alembic-managed databases.
- [ ] Confirm tests fail.
- [ ] Add dry-run inventory, migration and shadow comparison; make DB migration errors explicit rather than falling back to another database.
- [ ] Rehearse upgrade and rollback on disposable SQLite and MySQL fixtures.
- [ ] Commit.

### Task 10: End-to-end verification and cleanup

**Files:** backend/frontend tests, `PROJECT_KNOWLEDGE_BASE.md`, `CHANGELOG_AI.md`, deprecated seed/fallback/JSON key paths.

- [ ] Run isolated full backend suite, frontend tests/build, mocked three-pipeline end-to-end tests, migration fixtures, and security checks.
- [ ] Remove legacy writers and hardcoded remote seeds only after all consumers use the new catalog.
- [ ] Update project knowledge base and AI changelog.
- [ ] Review the full diff and commit.

