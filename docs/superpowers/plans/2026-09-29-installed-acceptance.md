# Installed Windows acceptance implementation plan

**Goal:** Gate candidate upload on actual silent install, installed backend restart and uninstall evidence.
**Architecture:** Execute the accepted per-user installer unchanged on an ephemeral Windows runner. Reuse the existing frozen smoke; isolate all writable state in a freshly created temporary Unicode/space directory. No product/API/schema/provider changes.
**Tech stack:** PowerShell, Python standard library, Inno Setup, GitHub Actions.
**Spec:** User-authorized installed acceptance scope; existing docs/desktop/TEST_PLAN.md and accepted desktop design remain binding.

## Impact and constraints
Existing smoke callers are build.ps1 and packaging tests; preserve main(payload) and its failure diagnostics. New optional evidence/data arguments are test tooling only. Installer identity, shortcuts, mutex and skipifsilent remain unchanged. No backend/frontend signatures, REST/SSE, DB schema, provider keys or production storage paths change. Refuse an existing installation/shortcut before executing Setup. Never remove shared folders or existing private data. Normal feature push only, no release or main merge.

- [x] Add portable negative tests for disposable-root guard and installed inventory tampering before helper implementation. Run targeted pytest red/green; existing payload tampering coverage is reused.
- [x] Extend reusable frozen smoke with two launches, retained SQLite marker/media sentinel, session invalidation, exact owned-process exit observation and monotonic duration samples. Preserve disposable default invocation and bounded diagnostics.
- [x] Add installed-smoke.ps1: enforce ephemeral Actions runner, preflight absent registration/shortcuts, create unique install/data roots, run silent Setup with explicit /DIR and desktopicon task, compare all payload hashes, resolve both shortcuts, check uninstall registration, invoke installed smoke, run actual uninstaller in finally, assert removal and data retention, emit bounded static phase failures and JSON metrics. Never manually remove unknown installation paths.
- [x] Probe native interactive desktop; if available launch installed shortcut with disposable LOCALAPPDATA, observe owned window/no owned console and bounded WM_CLOSE/owned termination. Otherwise record exact capability limitation without claiming GUI coverage.
- [x] Add workflow gate after package, before candidate upload; preserve JSON in candidate artifact. Parse PowerShell locally and run only relevant tests.
- [x] Obtain independent review, resolve findings, commit and normal push. Poll exact source SHA; use bounded public annotations to diagnose and minimally repair any native failures.
- [x] Record actual successful run/artifact/hash/one-run timings and remaining manual GUI/media/provider/performance gates in FINAL_REPORT, TEST_PLAN, BUILD, KB and changelog. Final docs commit may skip CI.

Executed: commit c3bc02e, successful Windows run 36551294736, artifact 11024283910. Independent review findings closed; 26 portable tests and six-script parser passed. Exact native scope and remaining manual gates are recorded in docs/desktop/FINAL_REPORT.md.
