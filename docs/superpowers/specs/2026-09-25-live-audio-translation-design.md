# Live Audio Translation design

The new Audio → Audio page uses Gemini's `gemini-3.5-live-translate-preview` over a server-side Live API WebSocket. It does not call the existing STT, translation, glossary, TTS, model routing, or video workflow services. The current application uses `?page=` navigation and localhost FastAPI routes without a separate login layer; the new route follows that boundary.

## Flow

1. The user selects an audio file. Source language shows automatic detection because the documented Live Translation configuration exposes a target language only. Target language is Vietnamese (`vi`).
2. `POST /api/live-audio-translations` accepts one bounded multipart file and starts a process-local job. `GET /api/live-audio-translations/{id}` reports status; `POST /{id}/cancel` cancels it; `GET /{id}/audio` downloads the completed WAV.
3. A dedicated audio adapter checks file format and duration, converts to raw mono signed 16-bit 16 kHz PCM using FFmpeg, and limits input to five minutes. The Live adapter sends 100 ms PCM chunks at real-time pace and collects signed 16-bit 24 kHz PCM output into a WAV. Its WebSocket and configuration exist only for that job.
4. The job manager stores short-lived status in process memory and files under `STORAGE_ROOT/live_audio_translation/{uuid}`. It retains at most ten terminal jobs, removes tracked files on shutdown, and removes crash leftovers older than 24 hours at startup. No schema changes. Server restart loses active status; it does not resume a Live session. In the desktop server's single process, status and cancellation work across its requests.

## Boundaries

`LIVE_AUDIO_TRANSLATION_ENABLED`, `GEMINI_LIVE_TRANSLATE_API_KEY`, and `GEMINI_LIVE_TRANSLATE_MODEL` are separate from legacy Gemini/provider configuration. Missing key and disabled feature fail before upload processing. Upstream errors use stable safe codes; no API key or upstream body is returned. A job never falls back to Edge TTS or any video pipeline. A single session has a bounded input duration below Google's 15-minute audio-only session limit. Longer files are rejected, not split across sessions.

The continuous Live Translate reference does not guarantee a terminal event after a file source stops. Following Google's file-stream example, the adapter collects output for four quiet seconds after the last audio chunk and caps the final wait at thirty seconds. Without a real key, end-of-file completeness cannot be guaranteed; a delayed final chunk may be omitted. Validate with representative speech before production use.

## Verification

Use mocked WebSocket messages for audio-in/audio-out, completion, cancellation and upstream failures; a real FFmpeg conversion test; HTTP route tests for upload, status, result and config errors; React tests for navigation, state, playback and download; then STT, translation, glossary, TTS and video regression suites. No live credential is used in tests.

Google references: [Live Translation](https://ai.google.dev/gemini-api/docs/live-api/live-translate), [Live API limitations](https://ai.google.dev/gemini-api/docs/live-api/capabilities).
