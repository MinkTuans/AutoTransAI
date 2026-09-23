# Task 9B2A — key rotation domain report

Status: implemented in the isolated `ai-model-discovery` worktree. Base HEAD was `0f3b2a4`; commit recorded below after verification.

## Delivered

- Canonical `APIKey` persists priority (positive, deterministic default 100), independent runtime status, optional cooldown, allowlisted last error code, and nonnegative request/success/failure counters. No upstream exception text column was introduced.
- Additive Alembic `20260923_key_rotation_domain` joins the two existing catalog heads. Defaults preserve existing ciphertext, enabled state, and key-model associations. SQLite uses additive validation triggers because rebuilding a referenced `api_keys` table fails with foreign keys enabled; MySQL emits check constraints.
- Credential DTO and masked key GET include safe metadata. Unknown persisted error text is suppressed at the DTO boundary. Priority-only PATCH accepts a strict positive integer, locks/revisions its provider, and preserves enabled state. Existing enable/disable PATCH remains available. The key view keeps `enabled` distinct from `runtime_status`.
- `build_route` filters disabled, invalid, exhausted, and active-cooldown keys, then orders keys within each model by explicit preference, priority, local request count, and stable ID. Expired cooldown is eligible. `invoke_route` repeats eligibility validation before secret reveal and transport. Response-derived status/counter writes are intentionally left to Task 9B2B.
- Updated `PROJECT_KNOWLEDGE_BASE.md` and `CHANGELOG_AI.md`. No UI priority control or legacy importer was added.

## RED/GREEN evidence

All commands ran under `backend/` with `DATABASE_URL=sqlite+aiosqlite:///:memory:` and the repository `.venv` Python. Test fixtures used synthetic credentials and disposable SQLite only; API tests block outbound sockets.

1. RED: `python -m pytest -q tests/test_credential_service.py::test_priority_update_is_validated_revisioned_and_preserves_enable_state tests/test_ai_key_api.py::test_priority_patch_and_masked_get_preserve_disabled_state tests/test_ai_routing_contract.py::test_same_model_orders_eligible_keys_by_priority_usage_and_preference tests/test_ai_routing_contract.py::test_stale_plan_rejects_newly_ineligible_credential` → 4 failed for missing DTO metadata, missing PATCH, wrong ordering/filtering, and stale plan transport.
2. GREEN after domain/API/router code: same four tests passed; migration tests failed RED because revision was absent, then passed after adding it.
3. Safety RED: `test_read_dto_never_exposes_unrecognized_error_text` failed on an unrecognized persisted string; GREEN after allowlist suppression.
4. Migration safety RED: with an existing key-model foreign key and `PRAGMA foreign_keys=ON`, a SQLite table rebuild failed with `FOREIGN KEY constraint failed`. GREEN after replacing the rebuild with additive SQLite triggers. The rehearsal also checks existing row preservation, positive-priority enforcement, downgrade preservation, and offline MySQL DDL.
5. Final GREEN: `python -m pytest -q tests/test_key_rotation_migration.py tests/test_credential_service.py tests/test_ai_key_api.py tests/test_ai_routing_contract.py tests/test_catalog_refresh_migration.py tests/test_thumbnail_model_length_migration.py` → **89 passed**. `python -m alembic heads` → `20260923_key_rotation_domain (head)`. `git diff --check` → clean.

## Self-review and limits

- Reviewed the final diff for plaintext leaks, accidental enable changes, preference bypass, stale plan transport, and schema destructive operations. The API emits only the masked key and safe metadata. Provider calls are absent from these tests and this change.
- Migration was rehearsed on disposable SQLite with a referenced existing key, plus MySQL offline SQL compilation. It was not run against a production database or the full historical Alembic chain; that chain still has the documented older `20260918_add_fk` repair dependency.
- Runtime status/counters are stored and read but not updated from responses here. Priority defaults to 100 for new and existing canonical credentials until import/UI work defines user-facing priority choices.

Commit: this report and implementation are committed together on the task branch; see branch HEAD.
