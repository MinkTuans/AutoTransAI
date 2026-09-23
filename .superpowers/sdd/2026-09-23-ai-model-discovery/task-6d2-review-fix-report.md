# Task 6D2 review fixes — voice enrollment and legacy Edge activation

Scope: Studio TTS review/render in `video_translator.py`, focused integration tests, KB, changelog. This follow-up addresses both Important findings in `task-6d2-review.md`; no schema, public API shape, discovery adapter, UI, Unified workflow, real key/network, or production database change.

## Fixes

1. Review submission now retains provider-returned voice metadata after exact provider/voice, target-language, and known-gender validation. It enrolls missing voices in `VoicePoolEntry`, refreshes metadata on existing enabled rows, and rejects explicitly disabled rows without re-enabling them. A previously confirmed Edge profile whose pool row is absent is revalidated against current Edge voice metadata at render time; only the exact ID is admitted to that segment's candidate pool, and normal provider/language/gender selection still applies. The read database session closes before this voice lookup. An explicitly disabled row blocks this historical path.
2. A keyed/non-system TTS catalog entry does not activate canonical Studio rendering while the configured TTS default is exactly the seeded legacy `edge_tts`/`edge-tts` pair. This is a read-only migration hold, not a catalog write or a claimed Edge entitlement. Task 9 must idempotently create the Edge `Provider` and keyless system `CatalogModel`, then migrate the default to that row's UUID. The integration regression proves that a legacy database with no canonical Edge row continues rendering after adding a keyed ElevenLabs row; adding the real Edge row and UUID default then activates canonical Edge rendering.

## TDD and verification

- The valid reviewed Edge voice outside the seed pool first failed because no pool row existed. After review enrollment, a historical absent-row rerender failed with `No compatible TTS voice`; exact Edge revalidation fixed it. A disabled-row rerender and repeat review both reject the voice.
- The legacy Edge default plus first keyed ElevenLabs row initially failed at `build_route` before synthesis (`Configured AI model is unavailable...`); the narrow migration hold fixed it.
- From `backend/`: `/home/codexproxy/Codex-project-2/AutoTransAI/.venv/bin/python -m pytest tests/test_studio_tts_route.py tests/unit/test_character_voice_validation_api.py tests/unit/test_same_voice_overlap_lifecycle.py tests/unit/test_workflow_lifecycle_regression.py tests/unit/test_tts_request_boundary.py tests/unit/test_edge_tts_timeout.py tests/test_ai_routing_contract.py -q --tb=short` — **103 passed in 18.93s**, exit 0. `git diff --check` passed.

## Limits

- The exact unmigrated Edge-default hold retains legacy Studio silence-on-failure behavior despite a populated keyed TTS catalog; canonical all-route failures still surface job errors after the Task 9 cutover. This exception is documented in the KB and changelog, not silently treated as a completed migration.
- Historical absent-pool revalidation is Edge-only. Other providers need review resubmission to enroll their voices; Google Cloud TTS still lacks its key-scoped voice discovery/access bridge and is not end-to-end canonical.
- Tests use isolated SQLite, synthetic encrypted credentials, and fake voice/provider calls, stopping before FFmpeg muxing. Real provider voice-list drift, live entitlement, and production migration remain untested.
