# SETTINGS & AI PROVIDER MANAGEMENT IMPLEMENTATION PLAN

## 1. Current Settings Audit
- **Settings Router & Service:** [settings.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/settings.py) & [settings_service.py](file:///c:/Hack/AutoTransAI/backend/app/services/settings_service.py) handle system key-value settings, AI function routing, custom model definitions, social media accounts, and storage testing.
- **Provider Router & Key Manager:** [providers.py](file:///c:/Hack/AutoTransAI/backend/app/api/routes/providers.py) & [key_manager.py](file:///c:/Hack/AutoTransAI/backend/app/services/key_manager.py) manage multi-key rotation pools per provider, priority levels, rate-limit 429 cooldowns, and key masking (`AIza****XXXX`).
- **ORM Models:** [settings.py](file:///c:/Hack/AutoTransAI/backend/app/models/settings.py) and [provider.py](file:///c:/Hack/AutoTransAI/backend/app/models/provider.py) define `SystemSetting`, `AIFunctionConfig`, `AIModel`, `SocialAccount`, `Provider`.

---

## 2. Existing API Key System
- **Security & Protection:** Raw API keys are stored in `data/api_keys.json` or environment variables, accessible only by backend key manager. Full API keys are NEVER returned in REST responses; only masked representations (`AIza****XXXX`) are exposed to the frontend.
- **Rotation Strategy:** Keys are rotated only when HTTP 429 Rate Limit or Quota Exceeded errors occur. Cooldown timer (60 seconds) is activated for rate-limited keys.
- **Multi-Key Support:** Multiple keys per provider with priority levels (`P1`, `P2`, `P3`).

---

## 3. Reusable Components
- **Frontend UI:** [Settings.jsx](file:///c:/Hack/AutoTransAI/frontend/src/pages/Settings.jsx) provides tabbed management for:
  - 🤖 AI & API Providers
  - ⚡ AI Function Configuration
  - 🧠 AI Models Catalog
  - 📱 Social Accounts
  - ☁️ Storage & Supabase / R2 Testing
  - ⚙️ Processing & Concurrency
  - 🎯 Workflow Defaults
  - 🛠️ Advanced Diagnostics
- **Backend Services:** `SettingsService`, `KeyManager`, `ProviderRegistry`.

---

## 4. Target Architecture

```text
SETTINGS STUDIO UI (React Settings.jsx)
          │
          ├── GET/PUT /api/settings/functions
          ├── GET/POST/DELETE /api/providers/keys
          ├── GET/POST /api/settings/models
          └── GET/POST/DELETE /api/settings/social-accounts
          │
          ▼
    FASTAPI BACKEND
          │
    ┌─────┴─────────────────────────────┐
    ▼                                   ▼
AI ROUTER / FUNCTION CONFIG     KEY MANAGER (Masked Keys / 429 Cooldown)
    │                                   │
    ▼                                   ▼
PROVIDER REGISTRY               SUPABASE POSTGRESQL DB
(Gemini, OpenAI, Edge TTS,      (SystemSettings, AIFunctionConfigs,
 ElevenLabs, Google TTS,         AIModels, SocialAccounts, Providers)
 Kling AI, fal.ai)
```

---

## 5. Database Changes
- All ORM tables (`system_settings`, `ai_function_configs`, `ai_models`, `social_accounts`, `providers`) exist in SQLAlchemy metadata and are supported on Supabase PostgreSQL via `scripts/migrate_to_supabase.py`.

---

## 6. Backend Changes
- Ensure STT router in `VideoTranslatorService` enforces Gemini STT as primary provider.
- Verify fallback behavior: If Gemini STT fails and `ENABLE_OPENAI_FALLBACK` is `False` (default), stop execution and raise a clear `RuntimeError` without invoking OpenAI / Whisper.
- Ensure candidate provider dropdown API `/api/settings/functions` filters candidate providers based on capability compatibility, configured key status, and provider enablement.

---

## 7. Frontend Changes
- Verify Settings Studio UI tabs and modal dialogs.
- Ensure STT info banner clearly states the Gemini-only STT policy and no-fallback rule when fallback is disabled.
- Mask all API key displays (`AIza****XXXX`).

---

## 8. AI Provider Architecture
- `AI FUNCTION -> AI ROUTER -> FUNCTION CONFIG -> PROVIDER REGISTRY -> PROVIDER ADAPTER`
- Supported Providers:
  - Google Gemini (`STT`, `LLM`, `TRANSLATION`)
  - OpenAI (`LLM`, `TRANSLATION`, `STT`)
  - Microsoft Edge TTS (`TTS` - Free)
  - Google Cloud TTS (`TTS`)
  - ElevenLabs (`TTS`)
  - Kling AI (`VIDEO_GENERATION`)
  - fal.ai (`VIDEO_GENERATION`, `IMAGE_GENERATION`)

---

## 9. STT Gemini Configuration & Flow
- **Primary STT Provider:** Google Gemini (`gemini-2.5-flash`).
- **Required Flow:** Video ➔ Extract Audio ➔ Gemini STT ➔ Transcript.
- **Fallback Policy:** OpenAI Whisper fallback occurs ONLY if `fallback_enabled` / `ENABLE_OPENAI_FALLBACK` is explicitly set to `True`. If `False`, pipeline stops immediately with a descriptive error.
- **Extensibility:** STT architecture uses `transcribe_audio_with_gemini` and `transcribe_audio_with_whisper` adapters, enabling future STT providers to be added via Provider Registry without altering the core pipeline.

---

## 10. Testing Plan
- **Settings CRUD Tests:** Test API Key addition, key masking, status toggling, custom model addition, social account management, and system settings update via pytest.
- **Gemini STT Execution Test:** Verify video audio extraction and Gemini STT execution.
- **Gemini Error & Fallback Test:** Simulate Gemini STT failure with fallback disabled; confirm Whisper/OpenAI is NOT called and clear error is returned.

---

## 11. Compatibility Risks
- **Zero Risk:** All existing workflow engine stages, project data, and API endpoints remain 100% backward compatible.
