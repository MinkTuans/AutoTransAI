# AutoTransAI Windows desktop conversion — implementation report

Date: 2026-09-29. Branch: `feat/windows-desktop`, isolated worktree `windows-desktop`. Source base: `4c867ea`; accepted architecture/plan: `0deba00`.

**Status: implementation, portable verification, independent review and packaging configuration are ready for Windows validation. No AutoTransAI.exe or Setup.exe was built on this Linux host. Installed Windows acceptance is pending; installer delivery is not complete.** The main checkout was left unchanged. No remote push, workflow dispatch, publication, Telegram message, duplicate wakeup or repository/data deletion was performed.

## Architecture

The new pywebview shell explicitly selects Edge/WebView2 and displays loading/error content with native Retry/View Logs/Close controls. Studio navigation follows authenticated readiness. A per-user mutex prevents duplicate instances; native navigation policy rejects arbitrary remote/file/javascript destinations without exposing a general JavaScript/native bridge.

The same windowed executable dispatches `--desktop-backend` before GUI imports. The supervisor assigns the child to a kill-on-close Windows Job Object before sending protocol-1 credentials/paths through stdin. Readiness has a 90-second bound, 250 ms probes and identity verification; runtime monitoring runs every 500 ms; shutdown allows 10 seconds before owned-tree cleanup. Crashes also clean remaining workers before enabling Retry. Foreign processes/listeners are never killed.

FastAPI serves Vite dist and existing API/media routes on an exclusive `127.0.0.1:8000` socket. An outer ASGI boundary covers static/API/media/SSE, with a one-use bootstrap, HttpOnly SameSite=Strict cookie, exact Host and unsafe-request Origin checks. Readiness reflects successful application lifespan. Only exact GET OAuth callbacks are exempt from the session, and they require expiring single-use state. Callback HTML is escaped/inert; YouTube exchanges the validated code through HTTPS while preserving PKCE. OAuth opens the OS browser through the existing URL allowlist.

Immutable resources are separate from `%LOCALAPPDATA%\AutoTransAI\{data,storage,logs,webview}`. Desktop ignores source/ancestor dotenv and inherited app credentials/database settings, starts independent SQLite, and accepts only an explicit private OAuth-client allowlist in `data\desktop.env`. No existing web data is automatically migrated; no ORM schema or AI routing change was introduced.

## Agents Used

| Native agent | Exclusive implementation roles | Independent review |
| --- | --- | --- |
| `supervisor` | Task 1 process manager and Windows Job Object | Runtime, security/OAuth, shell and installer; scoped fix rereview |
| `runtime` | Task 2 backend/paths/config; then Task 6 installer and private OAuth configuration | Supervisor and build/payload |
| `security` | Task 3 HTTP/OAuth/browser security; then Task 5 build/dependency/provenance pipeline | Builder self-checks; independent approval provided by runtime |
| `shell` | Task 4 shell/entrypoint; assigned review-fix wave | Fixes independently rereviewed by supervisor |
| Coordinator | Task 7 real-process integration, full regressions, documentation and final integration | Checked reports, final source/status and verification evidence |

Completed native threads were reused with explicit ownership reassignment because the tool enforced a thread/concurrency limit. All agents completed inside this execution. Two important review findings were reproduced, fixed with red/green regressions and independently closed: OAuthlib rejected the HTTP loopback callback URL; backend crashes initially left owned descendants alive. A native payload-audit weakness was also corrected to require the exact x64 WebView2 loader and WinForms assembly. No critical/important finding remains open in reviewed code; Windows evidence remains a separate release gate.

## Files Changed

- Runtime/shell/security: `desktop/{__init__,__main__,backend,paths,process_manager,windows_job,security,shell}.py` and six `desktop/tests/test_*.py` files.
- Existing boundaries: `shared/config.py`, `backend/app/config.py`, `backend/app/core/open_browser.py`, YouTube/TikTok routers and `backend/tests/unit/test_desktop_oauth_security.py`; frontend Settings OAuth configuration guidance.
- Build: `desktop/packaging/autotransai.spec`, `requirements-build.txt`, `runtime-manifest.json`, supporting hash locks/artifact/vendor inventories, version file, staging/audit/license/version/smoke helpers and notices.
- Distribution: four `desktop/scripts/*.ps1` commands, `desktop/installer/AutoTransAI.iss`, manual `.github/workflows/desktop-windows.yml` and generated-output ignores.
- Documentation: this report, [README](README.md), [BUILD](BUILD.md), [TEST_PLAN](TEST_PLAN.md), packaging README/notices, knowledge base, AI changelog and plan progress ledger.

## Commands Added

Run from a Windows checkout:

```powershell
.\desktop\scripts\dev.ps1
.\desktop\scripts\build.ps1
.\desktop\scripts\package.ps1
.\desktop\scripts\release.ps1
```

`python -m desktop` runs the prepared source shell. `dev.ps1 -SkipPrepare` reuses staged dependencies/resources; `build.ps1 -PrepareOnly` stages them without freezing. Release produces local artifacts only. Existing backend/Vite development remains available.

## Desktop Build

The onedir pipeline targets Windows x64 CPython 3.12, version 0.1.0, output `dist\AutoTransAI\AutoTransAI.exe` with `_internal` resources. It preserves dynamically loaded migrations and sibling helpers, includes native WebView2/pythonnet resources, uses explicit source inputs and rejects private/unknown payload changes. Package analysis uses disposable configuration. Node/npm is build-only.

All 76 selected Python/build artifacts were actually downloaded and SHA256-checked against official PyPI metadata, with Windows dependency closure independently checked. FFmpeg/FFprobe Gyan 9.0.2, official yt-dlp 2026.08.19 (EJS included) and private Deno 2.9.7 were downloaded/checksummed from upstream release metadata. Locks record exact URLs/hashes; no fabricated placeholders remain. Optional fpcalc is not included.

The build exports dependency/license inventories, validates native resources and payload hashes, optionally signs through an external hook, then runs a real frozen-backend smoke using temporary Unicode/space-path data. The smoke is implemented but has **not executed on Windows here**. Windows CI is manual and configured to retain unsigned candidate artifacts, without publication.

## Installer

Inno configuration supplies stable app identity/version, per-user directory selection, Start Menu/optional Desktop shortcuts, launch after installation and uninstaller. It checks a matching running-app mutex without broad process kills. Private data remains after uninstall.

Packaging embeds an official Microsoft WebView2 prerequisite only after signature verification and records its hash/provenance. Installation rechecks hash/signature, provisions only when absent and redetects success. The default small bootstrapper requires internet on a machine without WebView2; an explicitly supplied signed x64 Evergreen Standalone Installer supports offline deployment. Installer/uninstaller signing hooks keep credentials external.

**No installer compile, Setup.exe hash, install/upgrade/uninstall result or signed artifact exists from this job.**

## Tests

| Executed validation | Result |
| --- | --- |
| Full existing backend suite plus initial OAuth regressions, isolated checkout | **1,826 passed, 42 skipped**, two dependency deprecations, 376.62 s |
| Final desktop + OAuth/browser + database/media/storage covering suite after review fixes | **168 passed**, two dependency deprecations, 26.73 s |
| Frontend after configuration-message update | **36 passed**, six files |
| Vite production build after frontend update | Passed, 3.80 s |
| Independent supervisor/build review tests | 27 passed; 76 artifact hashes independently verified |
| Independent R1/R2 fix regression rerun | 3 passed |
| Official SHA256-verified Linux PowerShell 7.6.6 parser | All four scripts parsed successfully; Windows execution not established |
| Python/spec syntax and Git whitespace checks | Passed |

The real-process integration test uses actual FastAPI lifespan, temporary SQLite migrations, authenticated bootstrap/static/API, media byte-range 206, CSRF rejection, restart/session invalidation, retained media and owned shutdown. Tool-version fixtures are deliberately fake and do not prove FFmpeg or provider behavior. Supervisor/shell tests exercise real descendants and unrelated-process survival. Live provider and installed renderer acceptance were not run.

The original baseline stalled near completion and was stopped; a 240-second diagnostic run ended at 62% without failures because its bound was too short. The later 900-second-bounded verbose full run completed in 376.62 seconds. The original stall was not reproduced. No product fix was inferred from that incomplete baseline. The final full-suite result precedes the two narrow review fixes; the 168-test final covering run and independent regressions validate those fixes.

Raw job evidence is in `/tmp/autotransai-desktop-backend-full.log`, `-final-targeted.log`, `-frontend-final.log`, `-build-final.log`, `-powershell-parse.log`, task reports and independent review/rereview reports. [TEST_PLAN.md](TEST_PLAN.md) specifies the remaining native matrix and reproducible performance collection.

## Known Limitations

1. Actual Windows freezing/Inno compilation, windowed pipe inheritance, WebView2 UI/media/download/SSE, Job cleanup including parent crash, clean install/reopen/upgrade/uninstall and measured performance remain **unverified**. No Windows host/runner was available or remotely dispatched.
2. Live Google/TikTok OAuth and AI/media provider workflows require configured accounts/credentials and separate evidence. Portable tests do not establish live provider approval or codec/rendering compatibility.
3. Signing/SmartScreen and public distribution are pending. The GPL-enabled FFmpeg binary needs corresponding source/build material or another valid redistribution arrangement; notices alone do not complete that obligation. No public distribution was performed.
4. Authentication does not protect against same-user malware or authenticated frontend XSS. The pre-existing unrestricted YouTube upload `video_path` remains a recorded audit residual outside this conversion.
5. Port 8000 conflicts are intentionally visible/retryable. OAuth state is in memory and expires after 600 seconds; restart/cancellation requires a new Connect attempt. Existing desktop/web databases are separate unless deliberately migrated.
6. fpcalc is optional and unbundled. Forty-two backend tests skipped according to their environmental/fixture requirements; they are not claimed as passes.

## How To Run

On Windows, run `desktop\scripts\dev.ps1` from source, or launch the installed shortcut once a Windows-validated package is available. Configure provider keys in Settings and optional private OAuth client values as described in [README.md](README.md). Runtime errors expose native Retry/View Logs/Close.

## How To Build

Use Windows x64, Python 3.12 x64 and Node/npm, then run `desktop\scripts\build.ps1`. Keep the entire onedir output. See [BUILD.md](BUILD.md) and [packaging inputs](../../desktop/packaging/README.md) for locks, signing, audit and smoke details.

## How To Package

Install Inno Setup 6.4+, build first, then run `desktop\scripts\package.ps1`. Supply `-WebView2Installer` for an offline standalone prerequisite and external signing options when authorized. Complete the clean-machine matrix in [TEST_PLAN.md](TEST_PLAN.md) before calling installer delivery or Windows acceptance complete.
