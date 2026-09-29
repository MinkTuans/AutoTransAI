# Windows Desktop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Install and run the existing AutoTransAI app as a Windows desktop application while preserving web operation.

**Architecture:** pywebview/WebView2 owns a hidden Python backend process; backend serves compiled frontend same-origin. PyInstaller onedir and Inno Setup supply runtime and installation.

**Tech Stack:** Python 3.12 x64, React/Vite, FastAPI/Uvicorn, pywebview, WebView2, PyInstaller, Inno Setup.

**Spec:** `docs/superpowers/specs/2026-09-29-windows-desktop-design.md`

## Global Constraints

- Existing web commands/API/business behavior remain supported; desktop code lives in `desktop/` unless an existing shared boundary must change.
- Bind exclusively to `127.0.0.1:8000`; never kill a foreign port owner.
- Readiness deadline 90 seconds, polling 250 ms; runtime monitor 500 ms; graceful shutdown deadline 10 seconds.
- Tokens only through stdin; authenticate static/API/media/SSE. Exact callback exemptions require validated single-use state and escaped HTML.
- Explicit desktop data/resource roots; no ancestor dotenv or developer data in packages.
- Work only in `.worktrees/windows-desktop`, branch `feat/windows-desktop`; no force push/reset/history rewrite.
- Tests use disposable data. Windows installer/runtime claims require actual Windows evidence.
- Each agent lists files changed and test command/results; controller reviews diff/status/tests after each phase.

## Task 1: Owned backend supervisor (Agent 4)

**Files:** create `desktop/__init__.py`, `desktop/process_manager.py`, `desktop/windows_job.py`, `desktop/tests/test_process_manager.py`.

**Interfaces:** `BackendManager(command: list[str], resource_root: Path, data_root: Path, port: int = 8000)`; `start() -> str` returns one-use bootstrap URL only after authenticated readiness; `stop() -> None`; `is_running() -> bool`; `log_dir: Path`. Methods serialize start/stop. Command receives `--desktop-backend`; handshake/health/shutdown follow spec.

- [ ] Write tests for exit before readiness, foreign/wrong identity HTTP service, timeout, early close, restart after failure, log setup failure and surviving unrelated child. Use a real disposable Python fake backend for ownership/shutdown cases.
- [ ] Run failing tests with `AutoTransAI/.venv/bin/python -m pytest desktop/tests/test_process_manager.py -q`.
- [ ] Implement hidden argv-only Popen, Job Object assignment before handshake, bounded authenticated probe, append/rotation-safe logs, pipe graceful stop and owned group/job fallback.
- [ ] Run tests; inspect diff/status; report Windows-native coverage limits; independent review before integration.

## Task 2: Production backend and explicit paths (Agent 5)

**Files:** create `desktop/backend.py`, `desktop/paths.py`, `desktop/tests/test_backend.py`; minimally modify `shared/config.py` if required. Agent 7 exclusively owns `desktop/security.py`.

**Interfaces:** `desktop.backend.run_backend() -> int` reads stdin handshake before imports, configures desktop roots, wraps the existing ASGI app and serves built assets at `/`; import security wrapper from Task 3. Backend serves authenticated health only after existing lifespan succeeds and binaries resolve. `desktop.paths` centralizes source/frozen resource root and per-user desktop data root.

- [ ] Write failing tests for source/frozen/resource/data separation, ancestor dotenv exclusion, missing dist/binaries, preserved API/media paths and healthy identity.
- [ ] Implement explicit desktop path handling with unchanged web default behavior. Preserve dynamically loaded migrations. Use frontend dist StaticFiles only for frontend resources, never for media storage.
- [ ] Start Uvicorn with exclusive owned socket and no access query logging; stdin shutdown/EOF requests graceful exit. Probe FFmpeg/FFprobe and yt-dlp dependency availability before readiness.
- [ ] Run targeted tests and existing config/database/media regressions with disposable data; report source changes and independent review.

## Task 3: Desktop HTTP boundary and callback safety (Agent 7)

**Files:** create `desktop/security.py`, `desktop/tests/test_security.py`; narrowly modify `backend/app/core/open_browser.py`, `backend/app/api/routers/youtube.py`, `backend/app/api/routers/tiktok.py` and matching security tests as source analysis requires.

**Interfaces:** `DesktopSecurity(app, session_token: str, bootstrap_token: str, instance_id: str, port: int = 8000)` ASGI wrapper. Handles exact `/_desktop/bootstrap` and `/_desktop/health`, cookie/header auth, Host/Origin checks and response security headers. Runtime mounts this outside all routes.

- [ ] Write failing HTTP tests for anonymous API/media/static rejection; single-use bootstrap; cookie-authenticated API/media/range/SSE; wrong host/origin; token-free redirects/logging; callback state replay/missing state and HTML escaping.
- [ ] Implement middleware independent of web mode and without native bridge. Ensure callback exceptions do not create sessions or permit arbitrary endpoints.
- [ ] Preserve legitimate OAuth through safe external default-browser launch and existing URL allowlist. Keep scope confined to desktop-required auth boundary and callback safety.
- [ ] Run targeted tests; document residual local-user/XSS threat limits and review.

## Task 4: Native shell and entrypoint (Agent 3)

**Files:** create `desktop/__main__.py`, `desktop/shell.py`, `desktop/tests/test_shell.py`; optional `desktop/ui/` fixed loading/error assets.

**Interfaces:** `python -m desktop` starts desktop source mode; `--desktop-backend` dispatches Task 2 before importing GUI. Shell consumes Task 1 manager. Production executable uses same entrypoint.

- [ ] Write failing shell tests proving no content navigation before readiness, visible startup/runtime failure, serialized Retry, View Logs fixed path, close during startup and idempotent teardown.
- [ ] Implement immediate loading shell, explicit WebView2 selection, title/icon, normal resize/minimize/maximize, error text and controls; keep privileged operations unavailable to existing frontend/remote content.
- [ ] Monitor child and dispatch failure state; closing stops all owned descendants. Avoid existing icon-update script and broad port-kill scripts.
- [ ] Run shell/supervisor regressions; perform actual GUI checks only on supported host and mark others pending.

## Task 5: Build and runtime payload (Agent 9 with Agent 5 review)

**Files:** create `desktop/packaging/autotransai.spec`, `desktop/packaging/requirements-build.txt`, `desktop/scripts/build.ps1`, `desktop/scripts/dev.ps1`, `.github/workflows/desktop-windows.yml`, `desktop/packaging/runtime-manifest.json`; modify `.gitignore` only for generated desktop artifacts.

- [ ] Define separate source development, frontend production build, freezer build, packaging and release commands. Do not run Vite/Node in packaged runtime.
- [ ] Build from explicit allowlist with Python/native dependency version inventory, migration tree, frontend/icon, verified FFmpeg/FFprobe/yt-dlp payload and third-party notices. Fail clearly on missing prerequisites or hashes; never package .env/data/storage.
- [ ] Provide Windows CI build and disposable smoke evidence/artifacts. Keep signing optional through external credentials; no automatic publishing or updater.
- [ ] Validate syntax/config/payload manifests locally and execute real Windows build when a Windows runner is available. Report absence of artifact as unbuilt, not successful.

## Task 6: Installer (Agent 6)

**Files:** create `desktop/installer/AutoTransAI.iss`, `desktop/scripts/package.ps1`; depends on Task 5 payload layout.

- [ ] Configure stable app ID/name/version, per-user install directory, icon, Desktop/Start Menu shortcuts, launch-after-install and uninstaller.
- [ ] Detect/provision WebView2 and fail visibly if prerequisite unavailable. Do not silently use obsolete renderer.
- [ ] Handle running app safely; uninstall program payload/shortcuts only, retain private user data with explicit documentation. Never invoke broad process-name/port kills.
- [ ] Compile on Windows, install on disposable clean VM and verify shortcuts/startup/reopen/uninstall. Save results and installer SHA256.

## Task 7: Acceptance, performance and final review (Agent 8 + independent reviewer)

**Files:** create `docs/desktop/TEST_PLAN.md`, `docs/desktop/README.md`, `desktop/tests/test_lifecycle_integration.py`; controller updates `PROJECT_KNOWLEDGE_BASE.md`, `CHANGELOG_AI.md`, `docs/desktop/FINAL_REPORT.md`.

- [ ] Run meaningful real-process lifecycle/auth/static tests and existing full backend/frontend suites from isolated checkout; run Vite build. Record pre-existing failures separately.
- [ ] Execute Windows installation/launch/restart/failure/shutdown/uninstall matrix and feature regression: upload, download, media seek/playback, SSE, OAuth, settings, project reopen and synthetic FFmpeg workflow.
- [ ] Measure cold/warm launch and backend readiness, whole-tree memory/CPU, package/installed size and renderer responsiveness; retain raw data and median/p95. Do not invent performance claims when Windows unavailable.
- [ ] Independent whole-diff review for correctness, security, packaging exclusions and web compatibility; fix consequential findings and rerun covering tests.
- [ ] Update architecture/development/build/package/release/troubleshooting docs, knowledge base and changelog. Final report lists Architecture, Agents Used, Files Changed, Commands Added, Desktop Build, Installer, Tests, Known Limitations, How To Run, How To Build, How To Package; mark unverified Windows acceptance as open.

## Progress ledger

- Audit complete: Agents 1, 5 and 8; architecture selected with Agent 2; security/build specialist input in progress.
- Baseline first attempt used system Python and stopped at 112 collection errors (missing dependencies), then job was stopped. No tests executed during that collection failure. Full suite moved to isolated worktree because legacy cleanup tests derive source-root paths.
- Baseline job `67975f28` uses existing repo `.venv` and isolated worktree `.env`; results pending.
- Decision: preserve fixed internal port for OAuth compatibility; conflict produces actionable startup failure. No Windows runner detected; release acceptance is not yet proven.
