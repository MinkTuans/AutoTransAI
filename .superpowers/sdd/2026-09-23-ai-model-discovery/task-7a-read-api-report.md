# Task 7A — canonical AI catalog read API

Implemented typed read-only GET routes under `/api/ai` for providers, paginated/searchable models, model detail, and function defaults. The router uses canonical DB rows and the current capability registry. It does not seed defaults, call providers, or return credential fields. Public Fal/ElevenLabs listings report `catalog_unverified`; keyless system Edge/image models report `keyless` without inventing key counts. Unexpected read exceptions return a fixed error body.

Contract details:

- `GET /api/ai/providers`: dynamic DB providers with total/active models, enabled-key counts, and `ready`/`no_key`/`disabled` status.
- `GET /api/ai/models`: `page` (1+), `limit` (1–100, default 25), exact `provider_id`, known `capability`, and case-insensitive `q` across remote ID, display name, provider ID/name, and positive capability names. FULL_UNKNOWN models survive capability filtering unless negative evidence exists. Unknown provider returns 404.
- `GET /api/ai/models/{id}`: status, last listing-edge time where present, default usage, and fixed-shape allowlisted metadata only.
- `GET /api/ai/functions`: stored defaults plus derived `default_status` and `selectable`. Existing `configuration_error` takes priority. A provider-scoped remote-name match or `default` sentinel is `legacy_unmigrated`; unmatched non-default strings are `missing` because the schema has no canonical/legacy marker. Task 9 must make that distinction durable.

TDD evidence: new tests first failed with 404/missing `data`; after implementation, keyless readiness, default-state, malformed metadata, and arbitrary configuration-error text tests failed on their intended assertions, then passed after targeted changes. The focused guarded suite passed: `160 passed` across read API, catalog domain, routing contract, refresh, and discovery tests using disposable SQLite and synthetic credentials. No real credentials, provider calls, or production DB were used.

Remaining scope: Task 7B handles canonical writes and legacy endpoint compatibility; Task 9 handles default identity migration. This task adds no tables or migration.
