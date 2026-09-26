# Live Video Translation Implementation Plan

**Goal:** Accept short MP4 files on the existing Live page, translate their audio with Gemini Live, and return an MP4 with the original video track and Vietnamese audio.

**Architecture:** Keep the audio-only path unchanged. A dedicated Live video FFmpeg adapter validates and extracts 16 kHz PCM, the existing Live WebSocket translates it, then the adapter muxes the WAV with the original MP4. Store only the translated result for a completed job; failed/cancelled jobs remove their workspace. No Studio workflow, STT, text translation, glossary, or TTS calls.

**Tech Stack:** FastAPI, asyncio, FFmpeg/FFprobe, React, pytest, Vitest.

## Steps

- [x] Add failing tests for MP4 extraction, limits, no audio, mux duration, job lifecycle, API result and UI video playback.
- [x] Implement the dedicated Live video adapter and connect it to the existing process-local job manager.
- [x] Extend the route and page for MP4 upload and MP4 playback/download; preserve audio behavior.
- [x] Verify focused tests, frontend build, backend regression, and final diff.

## Constraints

- MP4 only for video input, at most five minutes and 250 MiB. Gemini receives audio only.
- Keep all frames of the input video. Pad a shorter translation with silence; if translated audio exceeds video duration, retain its full audio track without cutting speech. Playback after the last video frame depends on the player.
- Translation is continuous speech to speech, with no timestamp alignment guarantee. The returned video replaces the original audio track; it does not preserve or mix source audio.
- No automatic fallback to the existing Studio video pipeline.
