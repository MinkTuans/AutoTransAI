# Desktop build inputs

Run from a Windows x64 checkout using Python 3.12 x64, Node 22/npm and Inno Setup
6.4+ for the installer. These are build tools, not installed-app prerequisites.

```powershell
./desktop/scripts/dev.ps1                 # prepare tools/Vite/venv and launch source desktop
./desktop/scripts/dev.ps1 -SkipPrepare    # launch already prepared source checkout
./desktop/scripts/build.ps1               # frozen app, audit, actual backend smoke
./desktop/scripts/package.ps1             # Inno Setup from verified frozen payload
./desktop/scripts/release.ps1             # build + package locally; never publish
```

`build.ps1 -PrepareOnly` prepares the development environment without freezing.
The script creates `.venv-desktop`, downloads verified tools into ignored `bin/`,
and stores cache/build data in `.desktop-cache/` and `build/`. It never copies the
repository root into the payload. PyInstaller analysis uses disposable desktop
configuration before discovery imports, bypassing developer dotenv/data settings.
No application data is migrated by a build or by the installer.

Version: `version.txt`. PyInstaller spec: `autotransai.spec`.
`requirements-build.txt` is the plan's stable entrypoint to `requirements.lock`.
The latter pins 76 application/build distributions and approved Windows CPython
3.12 artifacts; `python-artifacts.json` records their PyPI URLs and SHA256 values.
`build-bootstrap.lock` supplies pip/setuptools/wheel/packaging before the one small
pure-Python `proxy-tools` source distribution builds without isolation or floating
build dependencies. Installation uses `--require-hashes --no-deps`, followed by
`pip check`. No package version is resolved afresh during a normal build.

The lock was resolved with uv 0.10.12 for x86_64-pc-windows-msvc/Python 3.12,
then all selected artifacts were downloaded, hashed and matched against PyPI
release metadata. Updating it requires repeating that resolution/download/hash
verification, updating the artifact inventory and bootstrap pins, and running
Windows regression/build tests. Do not paste unchecked hashes into the manifests.

`vendor-lock.json` pins upstream Windows FFmpeg/FFprobe, yt-dlp and Deno releases
and license documents. `prepare_vendor.py` verifies downloaded hashes, extracts
only explicit executable/license members, and records extracted binary hashes.
The official yt-dlp executable includes EJS; Deno is a private packaged runtime.
Optional fpcalc is not included. `export_notices.py` records installed Python/npm
versions and licenses, CPython terms, and Deno's complete executable license text.

`runtime-manifest.json` defines required payload files and links the inventories.
The application lands at `dist/AutoTransAI/AutoTransAI.exe`; immutable resources are
under `_internal`. The migration tree is supplied both at `backend/alembic` and
`alembic`: the frozen `app.database.__file__` sibling lookup requires the latter.
`verify_payload.py` rejects private/developer files and verifies the whole payload
hash manifest plus native renderer DLLs. `smoke_frozen.py` starts the actual frozen
backend with disposable Unicode-path data, checks authentication/UI/API readiness,
and shuts down the owned child. It does not claim GUI or installer acceptance.

`build.ps1 -SignScript path.ps1` invokes an operator-owned signing hook with the
application executable path, then verifies Authenticode before writing hashes.
`release.ps1 -SignToolCommand '...'` forwards an external Inno signing command to
package.ps1 (including installer/uninstaller signing). Credentials remain outside
the repository. No automatic publishing/updater is configured. CI runs manually
and uploads unsigned candidate artifacts unless operators add their signing setup.

The Linux implementation host verified downloads, locks, unit tests, Python/spec
syntax and PowerShell parsing. Actual Windows freezer/installer runs and installed
acceptance remain required. The GPL-enabled FFmpeg build also requires appropriate
corresponding source/build material or another valid compliance arrangement before
public redistribution; see THIRD_PARTY_NOTICES.md. Build success alone does not
establish redistribution readiness.
