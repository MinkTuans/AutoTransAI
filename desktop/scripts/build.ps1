[CmdletBinding()]
param(
    [string]$Python = 'python',
    [switch]$PrepareOnly,
    # Optional operator-owned script accepting one executable path argument.
    [string]$SignScript = ''
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if ($env:OS -ne 'Windows_NT') { throw 'Desktop builds require Windows x64 and Python 3.12 x64.' }
$Repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Push-Location $Repo
try {
    & $Python -c "import struct,sys; assert sys.version_info[:2] == (3,12) and struct.calcsize('P') == 8, 'Python3.12 x64 is required'"
    if ($LASTEXITCODE -ne 0) { throw 'Unsupported build Python.' }
    $BuildPython = Join-Path $Repo '.venv-desktop\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $BuildPython)) {
        & $Python -m venv (Join-Path $Repo '.venv-desktop')
        if ($LASTEXITCODE -ne 0) { throw 'Could not create isolated desktop build environment.' }
    }
    # Install the build backend first, then disallow unpinned isolated build deps.
    & $BuildPython -m pip install --require-hashes --no-deps -r desktop/packaging/build-bootstrap.lock
    if ($LASTEXITCODE -ne 0) { throw 'Pinned build bootstrap installation failed.' }
    & $BuildPython -m pip install --require-hashes --no-deps --no-build-isolation -r desktop/packaging/requirements-build.txt
    if ($LASTEXITCODE -ne 0) { throw 'Pinned Windows dependency installation failed.' }
    & $BuildPython -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Python dependency compatibility check failed.' }
    & $BuildPython desktop/packaging/prepare_vendor.py
    if ($LASTEXITCODE -ne 0) { throw 'Verified vendor staging failed.' }
    Push-Location frontend
    try {
        & npm.cmd ci
        if ($LASTEXITCODE -ne 0) { throw 'Locked frontend dependency installation failed.' }
        & npm.cmd run build
        if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
    } finally { Pop-Location }
    if (-not $PrepareOnly) {
        & $BuildPython desktop/packaging/export_notices.py
        if ($LASTEXITCODE -ne 0) { throw 'Dependency license inventory failed.' }
        & $BuildPython desktop/packaging/write_version.py
        if ($LASTEXITCODE -ne 0) { throw 'Windows version metadata generation failed.' }
        & $BuildPython -m PyInstaller --noconfirm --clean --distpath dist --workpath build/pyinstaller desktop/packaging/autotransai.spec
        if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed.' }
        if ($SignScript) {
            & $SignScript (Join-Path $Repo 'dist\AutoTransAI\AutoTransAI.exe')
            if (-not $?) { throw 'Application signing hook failed.' }
            $Signature = Get-AuthenticodeSignature -LiteralPath (Join-Path $Repo 'dist\AutoTransAI\AutoTransAI.exe')
            if ($Signature.Status -ne 'Valid') { throw 'Application signing hook did not produce a valid signature.' }
        }
        & $BuildPython desktop/packaging/verify_payload.py dist/AutoTransAI --write
        if ($LASTEXITCODE -ne 0) { throw 'Desktop payload verification failed.' }
        & $BuildPython desktop/packaging/smoke_frozen.py dist/AutoTransAI
        if ($LASTEXITCODE -ne 0) { throw 'Frozen backend smoke failed; do not package this build.' }
        Write-Host 'Built and smoke-tested dist/AutoTransAI. Installed GUI acceptance remains a separate step.'
    }
} finally { Pop-Location }
