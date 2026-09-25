# OpenRouter and provider catalog forward port

## Goal

On current `origin/main`, show OpenRouter in the AI Provider Catalog, let users add a persistent provider entry, and classify discovered models by supported workflow functions even when the listing omits capability fields.

## Work

1. Add the canonical `POST /api/ai/providers` contract and a visible catalog button. Unknown custom providers remain unsupported until a runtime adapter exists.
2. Add OpenRouter discovery and capability inference, including Gemini sparse listing inference. Keep uncertain functions unknown rather than claiming support.
3. Add OpenRouter runtime adapters for the six workflow capabilities, keyed through the canonical credential and routing services.
4. Verify API, UI, and workflow tests; update the knowledge base and changelog; review the complete diff before publishing.

## Acceptance

- OpenRouter appears in catalog after startup; a key can discover and select applicable models.
- A new custom provider remains listed after reload and is clearly marked unsupported without an adapter.
- STT, translation, TTS, visual gender, image generation, and video generation route through OpenRouter where the selected model supports them.
- Model classification does not turn missing API metadata into false support.
