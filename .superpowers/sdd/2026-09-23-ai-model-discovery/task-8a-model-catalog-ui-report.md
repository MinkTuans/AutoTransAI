# Task 8A — Dynamic Model Catalog UI report

Implemented a read-only canonical Models tab in `Settings.jsx` through `ModelCatalog`. Provider tabs come from `GET /api/ai/providers`; search, provider filtering, and 25-row pages use `GET /api/ai/models`; details use `GET /api/ai/models/{id}`. Rows show active/retired/disabled, capability evidence including `FULL_UNKNOWN`, keyless/no-key/listing access, available-key count, and exact `default_for` uses. Detail metadata is restricted to a provider-specific primitive-value allowlist. Removed this tab's legacy Add/Edit/Delete model controls while retaining legacy model loading for the unchanged Function tab.

TDD evidence: initial focused run failed on missing `ModelCatalog`; after implementation, two assertion-shape mismatches were corrected (omitted empty query and lowercase status). Final `npm test -- --run`: 1 file, 5 tests passed. Final `npm run build`: Vite 5.4.21 built 100 modules successfully. `git diff --check` passed. Tests mock `aiApi`; no live backend, database, provider traffic, or credentials were used.

Dependency setup: pinned Vitest 2.1.9, React Testing Library 16.2.0, DOM Testing Library 10.4.0, and jsdom 25.0.1 for this Vite 5/React 18 frontend. The package lock changed mechanically. No backend/API contract or database change. `PROJECT_KNOWLEDGE_BASE.md` and `CHANGELOG_AI.md` reflect the UI slice.

Known limits: public catalog/listing visibility is not per-key generation entitlement; the UI says so and does not claim verification. Function and Key Pool tabs remain on their legacy surfaces for Task 8B/C. Metadata outside the explicit allowlist is intentionally hidden. No screenshot or live integration test was performed in this offline slice.
