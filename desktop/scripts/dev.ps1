[CmdletBinding()]
param([string]$Python = 'python', [switch]$SkipPrepare)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if (-not $SkipPrepare) { & (Join-Path $PSScriptRoot 'build.ps1') -Python $Python -PrepareOnly }
$BuildPython = Join-Path $Repo '.venv-desktop\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $BuildPython)) { throw 'Run desktop/scripts/dev.ps1 without -SkipPrepare first.' }
Push-Location $Repo
try {
    & $BuildPython -m desktop
    if ($LASTEXITCODE -ne 0) { throw 'Desktop application exited with an error. Check LOCALAPPDATA\AutoTransAI\logs.' }
} finally { Pop-Location }
