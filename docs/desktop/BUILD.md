# Windows development, build, package and release

Use a Windows x64 build machine with Python 3.12 x64, Node/npm and internet access for dependency downloads. Inno Setup 6.4+ is additionally required to compile Setup.exe. WebView2 is required to run the shell. The Windows CI build, real silent install, installed backend restart, basic shortcut/GUI-window/close and uninstall smoke have passed; see [FINAL_REPORT.md](FINAL_REPORT.md) for the exact artifact source revision, hashes and remaining acceptance gates. The Linux coordinator did not produce or locally download those binaries.

Run PowerShell from the repository root. Keep developer credentials, databases and storage outside build staging; the scripts use an isolated desktop virtual environment and explicit resource inputs. Never point acceptance checks at valuable user data.

## Develop

```powershell
.\desktop\scripts\dev.ps1
```

The development command prepares locked Python dependencies and verified private runtime tools in the ignored source `bin` directory, builds the frontend, then runs `python -m desktop`. It uses the desktop private data root, separate from existing web settings. To work on the existing web UI with Vite hot reload, continue using the established backend/Vite commands instead.

## Build the onedir application

```powershell
.\desktop\scripts\build.ps1
```

The build produces `dist\AutoTransAI\AutoTransAI.exe` with its `_internal` resources. The entire onedir directory is required; copying only the executable will not work. The build includes frontend dist, icon, application modules, dynamic migration resources, native Python/WebView libraries and the verified tools. No developer `.env`, project data, storage, credentials or test fixtures belong in this payload.

The Windows Python lock and vendor manifest are checked in under `desktop\packaging`. Vendor downloads are verified by SHA256 before extraction. Dependency/license inventories and extracted-binary hashes travel with the payload; its audit rejects forbidden runtime data. A frozen-backend smoke check uses fresh temporary data and tests the actual windowed executable's stdin/health/shutdown path. It is not installed GUI acceptance.

## Package Setup.exe

```powershell
.\desktop\scripts\package.ps1
```

Optional parameters include `-Python`, `-Payload`, `-OutputDirectory`, `-ISCC`, `-WebView2Installer`, and `-SignToolCommand`. By default the script downloads Microsoft's Evergreen WebView2 bootstrapper while packaging, verifies its Authenticode signature and embeds it with its SHA256. If the target machine lacks WebView2, this standard installer needs internet access. For offline deployment, supply the signed **x64 Evergreen Standalone Installer** through `-WebView2Installer`; supplying the small bootstrapper still requires network access.

The installer checks existing WebView2 registry registrations, rechecks the embedded prerequisite hash and Microsoft signature before running it, then confirms installation. It fails visibly if the prerequisite remains unavailable. It installs per user, offers directory selection and an optional Desktop shortcut, creates a Start Menu shortcut, and can launch the app. A running instance must close before upgrade/removal. No broad process kill is used. Uninstall retains `%LOCALAPPDATA%\AutoTransAI` and the shared WebView2 runtime.

Output is `dist\installer\AutoTransAI-<version>-Setup.exe`, its `.sha256` file and `package-provenance.json`. A successful compiler exit does not replace the clean-machine install/uninstall acceptance matrix.

## Release locally

Use `desktop\scripts\release.ps1` for the checked-in local release sequence. No script publishes artifacts, pushes Git branches, installs an updater or embeds signing credentials. Signing hooks use externally configured commands/certificates. Label unsigned candidates as unsigned; verify actual signatures before signed release claims.

Retain the git revision, pinned input locks, build/smoke logs, dependency inventories, prerequisite signer/hash, Setup.exe hash and [Windows acceptance evidence](TEST_PLAN.md). The GPL-enabled FFmpeg distribution also requires its corresponding source/build material or another valid fulfillment of its redistribution terms; notices and links alone are not a completed public distribution package. See the shipped third-party notices. No public release is authorized or performed by this job.

## CI and troubleshooting

The Windows workflow `.github/workflows/desktop-windows.yml` supports manual dispatch and pushes only to `feat/windows-desktop`. The user authorized feature-branch pushes and Windows CI; the successful candidate is linked in [FINAL_REPORT.md](FINAL_REPORT.md). It builds and retains unsigned artifacts for 14 days without creating GitHub Releases. Public annotations report bounded failure diagnostics and successful candidate hashes/sizes. Artifact download requires GitHub authentication in the coordinator environment. Documentation-only follow-ups use `[skip ci]` and retain the successful artifact source SHA separately.

Missing vendor assets, hash mismatches, dependency installation failures or payload-audit failures stop the build. Do not bypass integrity checks to make an artifact appear successful. Repair the cache/input or update the lock deliberately from verified upstream releases. For launch/runtime issues, see [README.md](README.md). Final build and acceptance status is recorded in [FINAL_REPORT.md](FINAL_REPORT.md).

The workflow now runs `desktop/scripts/smoke-installed.ps1` after Inno and before upload. This script refuses non-ephemeral runners, installs to a fresh temporary directory, checks both shortcuts/registration and payload hashes, runs the installed backend twice, and invokes its actual uninstaller. It leaves marked disposable data for runner retirement. `dist/installer/installed-acceptance.json` records coverage, GUI capability and one-run metrics; failures block upload. No clean-machine or p95 claim follows from this check.
