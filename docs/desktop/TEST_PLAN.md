# Desktop verification and Windows acceptance

The automated portable tests are necessary but do not establish Windows installer or GUI acceptance. Run Windows checks on a disposable Windows 10/11 x64 machine, using a standard user with no developer Python, Node, FFmpeg or yt-dlp installed. Do not use production credentials or projects. Preserve raw command output and artifact hashes with the release candidate.

## Portable verification

Run backend tests from the isolated checkout with its empty ignored `.env` and the project's dependency environment. Unset `AUTOTRANSAI_DISPOSABLE_MYSQL_URL` unless intentionally exercising a disposable database. Existing test isolation provisions temporary SQLite/data/storage. Historical cleanup tests also derive source-root paths, so never run this suite against a checkout containing valuable runtime files.

Run `python -m pytest desktop/tests -q`, `python -m pytest backend/tests -vv -o faulthandler_timeout=60`, and in `frontend`, `npm ci`, `npm test -- --run`, `npm run build`. Use an external deadline for the full suite and retain the last test name/traceback if it hangs. Missing dependencies and an interrupted suite are not passing results.

Portable tests must exercise authenticated readiness, child exit/timeout, foreign listener identity, cancellation during startup, serialized retry, graceful shutdown and owned process cleanup. Verify anonymous static/API/media/SSE rejection, one-use bootstrap, cookie media ranges, exact Host/Origin policy, callback state expiration/replay, inert HTML and source/frozen data separation.

## Windows acceptance matrix

| Scenario | Required evidence |
| --- | --- |
| Build and package | Clean Python 3.12 x64 build, dependency inventory, vendor SHA256 verification, freezer output, Inno compile output, Setup.exe SHA256 |
| Fresh install | Standard-user install, directory selection, Start Menu and optional Desktop shortcuts; no unexpected elevation |
| WebView2 absent | Clear prerequisite policy; online provision succeeds or actionable failure; offline installation refuses cleanly when runtime unavailable |
| First launch | Loading window immediately visible; no console, Vite or external application browser tab; existing Studio appears only after authenticated readiness |
| Existing foreign port 8000 | Retryable error; foreign listener remains alive and unchanged; retry succeeds after owner releases port |
| Backend crash/startup failure | Visible Retry/View Logs/Close; retry launches one backend; billable work never silently restarted |
| Close during startup | Bounded close without lock deadlock; backend and owned descendants exit |
| Close during media work | FFmpeg/yt-dlp/deno descendants exit; unrelated process survives |
| Shell forced termination | Windows Job Object removes backend/owned descendants |
| Reopen/single instance | Second launch explains existing instance; normal reopen preserves SQLite, encrypted keys, settings and project media |
| Navigation/security | Arbitrary remote/file/javascript navigation blocked; no general native bridge; foreign browser cannot access private endpoints |
| Media | File picker/upload, URL download, download-to-disk, range seek/playback and SSE progress work inside WebView2 |
| OAuth | Real authorized Google/TikTok login opens OS browser; callback accepted once; denied/expired/replayed/missing-state requests inert and rejected |
| Unicode/space paths | Install and data roots containing Unicode/spaces; successful synthetic FFmpeg workflow |
| Upgrade/uninstall | Upgrade preserves private data; uninstaller removes program/shortcuts, retains user data; running app handled without broad process killing |
| Web regression | Existing backend and Vite development commands, APIs and configured web database remain supported |

Live provider checks require separately supplied disposable provider credentials and permission for billable calls. OAuth registration constraints remain provider-specific. Do not fabricate successful media/provider results from mocked tests.

## Performance collection

Record OS build, CPU/RAM, storage, WebView2 version, app revision, dependency inventory, antivirus state and power profile. Collect at least 10 cold launches after process/cache conditions are documented, and 20 warm launches. Measure executable start → loading window, authenticated ready, and interactive Studio separately. Record individual samples in CSV with monotonic timestamps. Report median and p95 with sample count, never estimates.

Measure full owned process tree and renderer working-set/private bytes and CPU at idle and during a fixed synthetic FFmpeg workflow; keep workload duration/resolution/codec constant. Record package and installed byte sizes, frame/input responsiveness, shutdown duration, and remaining PIDs after close. A shell-only measurement excludes meaningful renderer/backend cost and is insufficient.

## Release gate

Block delivery claims until Windows build, install, renderer, lifecycle, media and uninstall evidence exists. An unsigned artifact must be labeled unsigned. Signing, live provider compatibility and performance claims require their own evidence. See `FINAL_REPORT.md` for the actual executed checks and outstanding items.
