# AutoTransAI Windows desktop conversion — implementation report

Date: 2026-09-29. Branch: `feat/windows-desktop`, isolated worktree `windows-desktop`. Source base: `4c867ea`; accepted architecture/plan: `0deba00`.

**Status: Windows x64 build and actual installed-package acceptance succeeded.** [Run 36551294736](https://github.com/MinkTuans/AutoTransAI/actions/runs/36551294736) built source `c3bc02e17c5d915314ef57e3248af5f4ffbaaad5` on `windows-2022`, installed the generated Setup.exe, passed installed backend restart and GUI shortcut/window/close smoke, uninstalled it, and uploaded a new unsigned candidate. Full original user acceptance remains incomplete: interactive Studio/media, failure scenarios, clean-machine/upgrade and performance matrix still need evidence. Feature pushes and CI were authorized; main and public Releases are unchanged.

## Windows CI evidence

Run #8 completed successfully at **2026-09-29 09:50:56 UTC**. Build, payload audit, frozen smoke, Inno compilation, installed acceptance and candidate upload all passed. [Public annotations](https://api.github.com/repos/MinkTuans/AutoTransAI/check-runs/109349829463/annotations) report successful scope, hashes and measurements; [artifact metadata](https://api.github.com/repos/MinkTuans/AutoTransAI/actions/artifacts/11024283910) reports archive size/digest.

[Download installed-tested candidate](https://github.com/MinkTuans/AutoTransAI/actions/runs/36551294736/artifacts/11024283910): **AutoTransAI-Windows-x64-candidate**, artifact `11024283910`, expires **2026-10-13 09:50:30 UTC**. It contains the complete onedir application, Setup.exe, inventories/provenance and `installer/installed-acceptance.json`. Keep the full onedir directory for portable execution. GitHub artifact access/login is required; hashes below are public GitHub metadata/runner measurements, not a locally downloaded archive verification.

| New CI output | Bytes | SHA256 |
| --- | ---: | --- |
| Candidate archive | 335,658,837 | `184fad8409460c22b13da04bff23b83c1eec4f69715b90a2f8399cfd6f2684c8` |
| `AutoTransAI.exe` | 15,180,836 | `a184188245909686bb25ee4fe5d7a1274e2ff213b7c0f7c8ea75fb8d4eae4bbd` |
| `AutoTransAI-0.1.0-Setup.exe` | 141,476,326 | `efb8aaa834df0d431381b41617f8e6b52e2a72ffa5f42e7c9b21dfceb41051fa` |

The actual installer ran silently with an explicit fresh Unicode/space installation directory and requested Desktop task; silent mode did not autorun the app. Every inventoried installed payload file matched the build hash. Desktop and Start Menu shortcuts resolved to the installed executable/working directory; the single uninstall registration matched that installation. The installed executable reached authenticated lifespan readiness twice using disposable Unicode/space data, rejected anonymous UI requests, loaded cookie-authenticated HTML/API, initialized SQLite, rejected the prior session after restart and preserved a test database marker and storage sentinel. Both owned backend process handles exited, and no process executable under the install directory survived the checks.

The runner passed the GUI capability prerequisite (interactive, nonzero session and accessible input desktop). ShellExecute launched the **installed Start Menu shortcut**, and the harness observed a currently visible `AutoTransAI Studio` main window with one installed backend for ten seconds, no observed visible owned console window, then WM_CLOSE and exit of the observed owned process tree. This verifies native window/shortcut/lifecycle basics; it does **not** inspect Studio pixels, navigation, media, provider behavior or renderer responsiveness. It does not substitute for crash/active-media descendant cleanup acceptance.

The actual installed `unins000.exe` exited successfully; program directory, both shortcuts and uninstall registration were absent afterward. Disposable SQLite and storage sentinel survived. All writable state was explicitly temporary; no arbitrary `%LOCALAPPDATA%\AutoTransAI` or shared directory was deleted. The harness retains its marked scratch tree until runner retirement. WebView2 was available by GUI launch; this evidence does not distinguish preinstalled versus provisioned runtime. Absent-runtime provisioning/offline failure remains a separate matrix case.

| One-run CI measurement | Result |
| --- | ---: |
| Installed directory bytes (including uninstaller) | 508,156,076 |
| Silent installation | 14.017 s |
| Installed backend authenticated readiness, first / restart | 5.250 / 3.719 s |
| Owned backend shutdown, first / restart | 0.453 / 0.360 s |
| Uninstall plus removal assertions | 1.316 s |

Raw values and coverage flags are in `installed-acceptance.json`. These are two sequential backend launches in **one CI run**, not cold/warm distributions, user-machine p95, GUI startup timing, whole-tree memory/CPU or full performance acceptance.

The earlier [successful candidate](https://github.com/MinkTuans/AutoTransAI/actions/runs/36549227445/artifacts/11024087673) remains unchanged: run `36549227445`, source `eba42a9867d53375c496cbd73fe6cb99c1b6ac04`, artifact `11024087673`, archive 335,650,389 bytes / SHA256 `b40ce0e95d186dafec86f5ed34c7d22fb800149b230683eab846c51b32924d8c`; Setup 141,470,190 bytes / SHA256 `2946f3d954ee3b87caeae1bda94d51833105b49142c3a349423f914a66489591`. That run established build/frozen smoke/Inno only. No prior artifact was replaced or removed.

Earlier CI diagnosed unsupported `deno --license` and omitted dynamically loaded SQLAlchemy `aiosqlite`; source license verification and explicit selected DBAPI hidden imports fixed them. No dependency/security checks were relaxed. Installed acceptance needed no product fix: only smoke tooling, workflow and documentation changed. Independent review closed missing restart-session rejection, stale GUI-window observation and raw error rethrow findings before the successful push. All six PowerShell scripts parsed and **26 targeted packaging/guard tests passed** locally; the independent reviewer reran two guard tests/parser. GitHub emitted an action Node-runtime deprecation warning, without a failing step.

Documentation-only follow-ups use `[skip ci]`; **the new candidate source remains `c3bc02e17c5d915314ef57e3248af5f4ffbaaad5`**, separate from the documentation head. No local Windows binary build/download, public Release or signing occurred.

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
- Distribution: four `desktop/scripts/*.ps1` commands, `desktop/installer/AutoTransAI.iss`, manual/feature-branch `.github/workflows/desktop-windows.yml` and generated-output ignores.
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

The build exports dependency/license inventories, validates native resources and payload hashes, optionally signs through an external hook, then runs a real frozen-backend smoke using temporary Unicode/space-path data. The smoke **passed on the actual Windows runner** in the run above. Windows CI supports manual dispatch and pushes to `feat/windows-desktop`, and retains unsigned candidate artifacts without creating a public Release.

## Installer

Inno configuration supplies stable app identity/version, per-user directory selection, Start Menu/optional Desktop shortcuts, launch after installation and uninstaller. It checks a matching running-app mutex without broad process kills. Private data remains after uninstall.

Packaging embeds an official Microsoft WebView2 prerequisite only after signature verification and records its hash/provenance. Installation rechecks hash/signature, provisions only when absent and redetects success. The default small bootstrapper requires internet on a machine without WebView2; an explicitly supplied signed x64 Evergreen Standalone Installer supports offline deployment. Installer/uninstaller signing hooks keep credentials external.

**Inno compilation, silent installation, installed shortcut/backend/GUI-window smoke, uninstall and candidate upload succeeded**, with evidence above. Interactive installer choices, absent WebView2, upgrade/running-app cases and signing remain unverified.

## Tests

| Executed validation | Result |
| --- | --- |
| Full existing backend suite plus initial OAuth regressions, isolated checkout | **1,826 passed, 42 skipped**, two dependency deprecations, 376.62 s |
| Final desktop + OAuth/browser + database/media/storage covering suite after review fixes | **168 passed**, two dependency deprecations, 26.73 s |
| Frontend after configuration-message update | **36 passed**, six files |
| Vite production build after frontend update | Passed, 3.80 s |
| Independent supervisor/build review tests | 27 passed; 76 artifact hashes independently verified |
| Independent R1/R2 fix regression rerun | 3 passed |
| Official SHA256-verified Linux PowerShell 7.6.6 parser | All four scripts parsed successfully; native build/package subsequently passed |
| Python/spec syntax and Git whitespace checks | Passed |
| CI notice, smoke-diagnostic and dynamic DBAPI packaging regressions | **24 passed**, independently rerun |
| Safe startup diagnostic + then-current packaging suite | **37 passed**, two dependency deprecations, independently rerun |
| Initial Windows x64 CI build/audit/frozen smoke/Inno/upload | **All succeeded**, run `36549227445` |
| Installed-smoke portable guard + packaging regressions; six-script PowerShell parse | **26 passed**, parser passed; independently reviewed |
| Actual install, installed restart/session invalidation, shortcut/GUI-window/close, uninstall/retention and upload | **All succeeded**, run `36551294736` |

The real-process integration test uses actual FastAPI lifespan, temporary SQLite migrations, authenticated bootstrap/static/API, media byte-range 206, CSRF rejection, restart/session invalidation, retained media and owned shutdown. Tool-version fixtures are deliberately fake and do not prove FFmpeg or provider behavior. Supervisor/shell tests exercise real descendants and unrelated-process survival. Live provider and full interactive renderer acceptance were not run; installed native window/close smoke passed as scoped above.

The original baseline stalled near completion and was stopped; a 240-second diagnostic run ended at 62% without failures because its bound was too short. The later 900-second-bounded verbose full run completed in 376.62 seconds. The original stall was not reproduced. No product fix was inferred from that incomplete baseline. The final full-suite result precedes the two narrow review fixes; the 168-test final covering run and independent regressions validate those fixes.

Raw job evidence is in `/tmp/autotransai-desktop-backend-full.log`, `-final-targeted.log`, `-frontend-final.log`, `-build-final.log`, `-powershell-parse.log`, task reports and independent review/rereview reports. CI annotations, metadata, red/green test logs and independent reviews are retained under `/tmp/autotransai-windows-ci-*`; these temporary files are not durable release storage. [TEST_PLAN.md](TEST_PLAN.md) specifies the remaining native matrix and reproducible performance collection.

## Known Limitations

1. Windows build, silent installed package, shortcut targets, basic GUI window/close, installed backend restart/session invalidation, uninstall/retention and single-run backend timings passed. Interactive WebView2 UI/media/download/SSE, error/Retry interactions, close-during-startup/media, parent-crash cleanup, single-instance UX, clean Windows 10/11 machine/absent-runtime/upgrade and full performance matrix remain **unverified on Windows**. The hosted runner is not a clean standard-user target machine; original user A–J acceptance is not complete.
2. Live Google/TikTok OAuth and AI/media provider workflows require configured accounts/credentials and separate evidence. Portable tests do not establish live provider approval or codec/rendering compatibility.
3. Signing/SmartScreen and public distribution are pending. The GPL-enabled FFmpeg binary needs corresponding source/build material or another valid redistribution arrangement; notices alone do not complete that obligation. Complete Deno transitive notices also remain pending. No GitHub Release/public-distribution publication was performed; only the authorized unsigned CI candidate was retained.
4. Authentication does not protect against same-user malware or authenticated frontend XSS. The pre-existing unrestricted YouTube upload `video_path` remains a recorded audit residual outside this conversion.
5. Port 8000 conflicts are intentionally visible/retryable. OAuth state is in memory and expires after 600 seconds; restart/cancellation requires a new Connect attempt. Existing desktop/web databases are separate unless deliberately migrated.
6. fpcalc is optional and unbundled. Forty-two backend tests skipped according to their environmental/fixture requirements; they are not claimed as passes.

## How To Run

On Windows, run `desktop\scripts\dev.ps1` from source, or install the unsigned candidate above and launch its shortcut. Configure provider keys in Settings and optional private OAuth client values as described in [README.md](README.md). Runtime errors expose native Retry/View Logs/Close.

## How To Build

Use Windows x64, Python 3.12 x64 and Node/npm, then run `desktop\scripts\build.ps1`. Keep the entire onedir output. See [BUILD.md](BUILD.md) and [packaging inputs](../../desktop/packaging/README.md) for locks, signing, audit and smoke details.

## How To Package

Install Inno Setup 6.4+, build first, then run `desktop\scripts\package.ps1`. Supply `-WebView2Installer` for an offline standalone prerequisite and external signing options when authorized. Complete the clean-machine matrix in [TEST_PLAN.md](TEST_PLAN.md) before calling installer delivery or Windows acceptance complete.
