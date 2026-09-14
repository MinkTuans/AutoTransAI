# Recreate AutoTransAI Studio shortcuts so Windows Search/Start uses app-logo.ico.
$ErrorActionPreference = 'SilentlyContinue'
$rootDir = $PSScriptRoot
$ico = Join-Path $rootDir 'app-logo.ico'
$target = Join-Path $rootDir 'AutoTransAi.vbs'
$name = 'AutoTransAI Studio.lnk'

if (-not (Test-Path $ico) -or -not (Test-Path $target)) { exit 0 }

function Write-AppShortcut([string]$path) {
    $dir = Split-Path $path -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    if (Test-Path $path) { Remove-Item $path -Force }
    $w = New-Object -ComObject WScript.Shell
    $s = $w.CreateShortcut($path)
    $s.TargetPath = $target
    $s.WorkingDirectory = $rootDir
    $s.WindowStyle = 7
    $s.Description = 'AutoTransAI Studio'
    $s.IconLocation = "$ico,0"
    $s.Save()
}

Write-AppShortcut (Join-Path $rootDir $name)
Write-AppShortcut (Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\$name")

$desktop = [Environment]::GetFolderPath('Desktop')
$desktopLnk = Join-Path $desktop $name
if (Test-Path $desktopLnk) { Write-AppShortcut $desktopLnk }

# Bump ICO mtime so Explorer does not keep a stale cache entry.
(Get-Item $ico).LastWriteTime = Get-Date

# Refresh shell icons without killing Explorer.
$ie4 = Join-Path $env:SystemRoot 'System32\ie4uinit.exe'
if (Test-Path $ie4) { & $ie4 -show }

# Start/Search hosts reload their icon cache on next launch.
Get-Process StartMenuExperienceHost, SearchHost, SearchApp -ErrorAction SilentlyContinue |
    Stop-Process -Force -ErrorAction SilentlyContinue
