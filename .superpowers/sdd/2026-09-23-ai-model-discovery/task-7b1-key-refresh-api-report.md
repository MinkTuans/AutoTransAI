# Task 7B1 — canonical key and explicit refresh API

Base `36d7937`; implementation commits `cad642b`, `645d5a8`, `8f65d30`.

Implemented masked provider key listing, disabled-first add with additive discovery after commit, guarded enable/disable, delete, and typed explicit global refresh. No provider call occurs inside a DB write transaction. Key deletion leaves catalog rows; only explicit refresh can retire discovered rows, and only for providers whose scan is complete (including a supported provider with no active keys). An overall partial refresh can still reconcile another complete provider. Failed, partial, unsupported, empty, rate-limited, and catalog-scope discovery leaves a new key disabled. Explicit enable repeats discovery and requires a complete credential-scoped listing. Public Fal/ElevenLabs listing is catalog visibility, not per-key entitlement or generation validation. The response's `verified_for_generation` field remains false even on a credential-scoped listing because listing cannot prove generation entitlement.

Red/green evidence:

- Initial API tests failed on missing route, then passed (`3 passed`); credential/refresh/catalog/API suite `66 passed` after `cad642b`.
- Deterministic rotate/disable interleaving after discovery returned 201 and enabled a changed key before the fix; the tests then returned safe 409 with the key disabled. Guarded suite `68 passed` after `645d5a8`.
- Toggle/delete/refresh tests failed with missing endpoints; after implementation, failed/stale refresh tests exposed a 500 from absent `providers` and passed after the DTO fix. Guarded suite `81 passed` after `8f65d30`.

Guarded suite: `cd backend && ../.venv/bin/pytest -q tests/test_ai_key_api.py tests/test_credential_service.py tests/test_model_refresh.py tests/test_ai_catalog_read_api.py` → `81 passed` (21.16s fresh final run). API tests use disposable SQLite, synthetic credentials, injected discovery, and a socket-connect guard. `git diff --check` passed. A full repository suite was not run because this checkpoint is deliberately scoped to isolated synthetic credentials and must not touch a configured production database or real provider.

Security checks cover bad JSON/type validation, duplicate input, injected exception text absent from response/logs, masked DTOs, revision races, and no outbound socket calls. The global FastAPI exception handler still echoes arbitrary exceptions on legacy routes; the new secret-bearing routes use a narrow safe route handler. No plaintext, fingerprint, ciphertext, raw upstream body, or arbitrary exception text is returned by the canonical key DTOs.

Limits and follow-up: `api_keys` has only `enabled` and `revision`, so there is no durable validation status or priority. Task 9 needs an additive schema/data migration for those fields and cutover of legacy plaintext/settings writers. These endpoints do not change fallback/provider selection, Settings UI, or legacy routes. Existing service result semantics remain unchanged apart from explicitly allowing single-key discovery of a disabled candidate; global refresh continues to scan enabled keys only.
