# AutoTransAI Windows desktop

The Windows desktop entrypoint reuses the existing React Studio and FastAPI workflow engine. A pywebview window requires Edge/WebView2. Its owned hidden backend serves the production Vite build and API at `http://127.0.0.1:8000`; Node/Vite is not a packaged runtime requirement. OAuth deliberately opens the default external browser.

This branch supplies implementation and build configuration. Windows installation, renderer/media and performance acceptance must be established on Windows; see [FINAL_REPORT.md](FINAL_REPORT.md) and [TEST_PLAN.md](TEST_PLAN.md).

## Private data and process lifecycle

Resources come from the immutable payload. Writable data lives under `%LOCALAPPDATA%\AutoTransAI`: `data` contains SQLite and credentials, `storage` contains media, `logs` contains backend diagnostics and `webview` contains the renderer profile. Desktop startup ignores developer `.env`, ancestor configuration and inherited application credentials. A new desktop install does not import an existing web database. Keep a backup of the entire private data directory, including encryption keys, before migrating or upgrading valuable projects.

The shell owns one backend process and its descendants using a Windows Job Object. Backend credentials travel through stdin, not command arguments or environment variables. A one-use bootstrap creates an HttpOnly, SameSite=Strict session cookie covering static files, API, media and SSE. The window loads Studio after authenticated backend lifespan readiness. Startup and runtime failures expose Retry, View Logs and Close. Retrying never silently resumes billable work.

Port 8000 remains fixed for existing OAuth callbacks. An unrelated owner causes a retryable error and is never terminated by the desktop app. Close the conflicting application yourself, then Retry. The app does not attach to a foreign backend.

## Development, build and packaging

Use Windows x64 and Python 3.12 for desktop development/builds. Node/npm is needed only while building the frontend. Build scripts stage verified FFmpeg/FFprobe, official yt-dlp with EJS, and private Deno; optional Chromaprint `fpcalc` is not bundled. Inno Setup is needed for packaging. Follow [BUILD.md](BUILD.md) for exact commands and prerequisites.

Existing web development remains available: run the backend with Uvicorn and `frontend/npm run dev`. The historical `app_launcher.py` remains separate; use the new desktop commands for the packaged architecture. Desktop OAuth client configuration uses the explicit private file below; developer environment credentials are deliberately not inherited.

## OAuth client configuration

Create `%LOCALAPPDATA%\AutoTransAI\data\desktop.env` yourself using UTF-8, then restart the desktop app. Only these keys are accepted:

```dotenv
YOUTUBE_CLIENT_ID=your-provider-client-id
YOUTUBE_CLIENT_SECRET=your-provider-client-secret
TIKTOK_CLIENT_KEY=your-provider-client-key
TIKTOK_CLIENT_SECRET=your-provider-client-secret
TIKTOK_SCOPES=user.info.basic,video.upload
```

Omit providers you do not use. This file is private configuration containing your own provider client credentials; do not commit, distribute or attach it to bug reports. It is never bundled. Values are not interpolated. Unknown or duplicate keys and malformed entries fail startup without logging values; the file is limited to 16 KiB. Database URLs, storage paths, session tokens and arbitrary environment variables are not accepted here. Callback URLs remain `http://127.0.0.1:8000/api/youtube/oauth-callback` and the equivalent TikTok path; register the required callback with your provider where supported. Add service API keys through the existing Settings key-management UI.

## Troubleshooting

- **Port conflict:** release port 8000 by closing its owning application, then Retry. Never use broad process-kill commands as a workaround.
- **Missing or failing runtime tool/front-end:** repair/rebuild the payload. Startup validates the compiled frontend and all required tool executables before declaring readiness.
- **WebView2 unavailable:** install the Microsoft Edge WebView2 Evergreen Runtime using the installer prerequisite flow. There is no obsolete-renderer fallback.
- **Backend stopped:** inspect the fixed logs directory from the native controls. Retry launches a fresh owned backend; inspect interrupted projects before choosing to resume them.
- **OAuth rejected:** begin Connect again after cancellation, expiry or restart. Callback state is expiring, single-use and held in memory.
- **Data appears absent:** desktop has its own private root. It does not silently switch to a source checkout's database. Do not copy a live SQLite file or omit its encryption keys during an explicit migration.
- **Download/provider feature unavailable:** network access, provider configuration and account/API permissions are still required; a self-contained runtime does not supply paid service credentials.

Uninstall retains private user data by default and removes program files/shortcuts. Remove retained data only deliberately after a verified backup. The app has no automatic updater or publishing step. Release/signing procedures are documented in [BUILD.md](BUILD.md).

The session boundary protects against other browser origins; it cannot defend against malware running as the same OS user or arbitrary code executing inside authenticated Studio. The pre-existing unrestricted YouTube upload `video_path` remains a separate audit finding.
