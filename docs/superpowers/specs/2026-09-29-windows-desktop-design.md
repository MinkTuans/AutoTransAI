# Windows Desktop Design

## Goal and acceptance

Deliver an installable Windows AutoTransAI application: Setup.exe installs Desktop/Start Menu shortcuts; double-click starts an owned backend and opens the existing UI without a console, developer runtime, browser tab or user-visible port configuration. Existing web development and business features remain supported. Startup failure and later backend failure have Retry, View Logs and Close. Closing the app terminates its descendants; unrelated processes survive. Uninstall removes application files and shortcuts, retaining user projects/credentials by default with clear documentation.

Completion requires actual Windows installation, startup, restart, failure, shutdown, uninstall and renderer/media evidence. Linux tests and a build recipe alone do not satisfy this acceptance criterion. OAuth still legitimately opens an external browser for provider authentication.

## Audited baseline

Source revision: `4c867ea`, clean `main`. Work proceeds on `feat/windows-desktop` in `.worktrees/windows-desktop`.

The checked-in shortcut targets `C:\Hack\AutoTransAI\AutoTransAi.vbs`. VBS runs an icon updater that terminates Windows shell/search processes, then launches source-tree pythonw. `app_launcher.py` runs Uvicorn on 8000 and `npx vite` on 5173, checks HTTP 200, opens pywebview and force-kills children on close. There is no production frontend host, frozen runtime or installer. Frontend uses relative `/api`, `/media` and EventSource URLs. SQLite is the default; configured MySQL remains supported. Media requires FFmpeg/FFprobe and page downloads require yt-dlp. fpcalc is optional. Startup imports migration files dynamically and changes the database, so verification uses disposable data only.

Configuration currently searches parents for `.env`/README and overrides environment. Installed desktop must explicitly separate resource paths from writable data; it must never discover developer secrets in an ancestor directory. Existing web behavior stays unchanged.

## Decision and alternatives

Keep pywebview and explicitly require Edge Chromium/WebView2. Freeze a Python 3.12 x64 application with PyInstaller onedir; the same executable accepts a private backend mode. Package with Inno Setup per user. Production serves Vite-built static assets and the existing FastAPI application at the same origin. Node/npm are build/development tools only.

Electron would add Chromium and a Node supervisor to a Python application that already has a native shell. It offers mature packaging but increases runtime and integration work without a demonstrated requirement. Tauri adds a Rust/native build boundary while retaining Python and WebView2 requirements. PWA alone does not own the required native services and installer lifecycle. Reusing pywebview minimizes migration; the tradeoff is explicit WebView2 provisioning and custom, tested process supervision. No size/RAM superiority is claimed without measurement.

## Runtime contract

* Bind exclusively to `127.0.0.1:8000`, preserving existing OAuth callback configuration. Never attach to or kill a pre-existing service. A conflict is a retryable startup failure. A random-port callback relay is outside this first implementation.
* Launch the executable with `--desktop-backend` (development: Python plus desktop entrypoint), hidden on Windows, stdin as a control pipe and stdout/stderr in private logs. No shell command construction.
* Before importing backend code or starting workers, child waits for one JSON line: `protocol=1`, `instance_id`, `session_token`, `bootstrap_token`, `data_root`, `resource_root`, `port=8000`. Assign child to an owned Windows Job Object with kill-on-close before sending this handshake. Tokens never appear in argv or files.
* Backend mode prepares private configuration, bundled binary PATH and imports the existing app. Preserve migration tree resources. Serve only compiled frontend assets; preserve existing validated media routes. Hold the listening socket continuously into Uvicorn, with Windows exclusive address use.
* `GET /_desktop/health` requires `Authorization: Bearer <session_token>`, returns `instance_id` and `ready=true` only after lifespan startup and required binary checks. Readiness deadline 90 seconds, polling 250 ms. The manager checks its own child has not exited and validates identity.
* UI uses one-use `/_desktop/bootstrap?token=...`, which issues an HttpOnly SameSite=Strict host-only session cookie and redirects to `/`. Never log bootstrap query/token; responses use no-store and no-referrer. Authentication covers static assets, API, media and SSE without rewriting React. Enforce exact Host and reject cross-origin unsafe requests. OAuth exceptions are only the exact GET callback routes, never a prefix; they must validate single-use state and render escaped inert HTML.
* Shutdown sends `{"command":"shutdown"}` or closes stdin. Backend requests Uvicorn graceful exit. Allow up to 10 seconds, then close the owned Job Object to remove remaining backend/FFmpeg descendants. POSIX tests use a dedicated process group. Parent crash also closes the Job handle. Retry serializes cleanup before respawn; monitor exits every 500 ms, with no silent restart of billable work.
* Shell opens a loading/error window immediately; existing application content is loaded only after readiness. No general-purpose native JS bridge. Fixed native error controls or a tightly constrained local control surface provide Retry/View Logs/Close; View Logs opens only the known logs directory. Block navigation to arbitrary remote content in the privileged application window.

## Resources and writable data

Installed resources are immutable. Default writable root is `%LOCALAPPDATA%\AutoTransAI`; use separate `data`, `storage`, `logs` and renderer profile directories. Keep credentials outside media roots. Desktop-specific configuration is explicit and must not load source-tree/ancestor `.env`. New desktop installs do not silently import or migrate an existing web database. Upgrades preserve desktop data and encryption keys.

Payload allowlist includes frozen Python dependencies/native libraries, compiled frontend/icon, migration resources, FFmpeg/FFprobe, yt-dlp and recorded third-party notices/versions. Never copy developer `.env`, databases, storage, logs, environments or worktrees. WebView2 prerequisite is detected/provisioned by the installer; unsupported renderer fallback is not allowed. Optional fpcalc absence is documented. No automatic updater is added; stable app identity/version and optional signing hooks prepare release tooling without embedding credentials.

## Ownership and phase order

Agents 1/2 audit and architecture are read-only. Agent 3 owns shell/entrypoint. Agent 4 owns process manager/Job Object. Agent 5 owns runtime adapter and resource configuration. Agent 6 owns installer. Agent 7 owns desktop HTTP guard and necessary OAuth callback hardening. Agent 8 owns acceptance/performance plan and lifecycle integration tests. Agent 9 owns build scripts/freezer/CI. Controller owns design, plan, integration documentation, knowledge base and changelog. Assign exact files before each task; dependent implementation waits for its contract. Check diff/status/tests after each phase and independently review integrated changes.

## Evidence plan and limitations

Run portable lifecycle/auth/static-host tests, existing backend/frontend regressions and Vite build in the isolated checkout. Run Windows build and installed acceptance on a Windows host, with no developer Python/Node/FFmpeg and with WebView2 initially absent/present. Exercise media playback/ranges, uploads/downloads, SSE, OAuth, fresh/copied databases, spaces/Unicode paths, crash/retry and descendant cleanup. Measure cold/warm startup, backend readiness, whole-tree RAM/CPU, installer/installed size and renderer responsiveness; retain raw samples and report median/p95 rather than invented metrics. Signing and live provider tests require their actual credentials/environment. Unverified acceptance items remain explicitly open.
