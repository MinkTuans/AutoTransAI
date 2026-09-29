[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
# This harness installs/uninstalls a real app. Refuse developer/user machines.
if ($env:OS -ne 'Windows_NT' -or $env:GITHUB_ACTIONS -ne 'true' -or $env:RUNNER_ENVIRONMENT -ne 'github-hosted') {
    throw 'Installed acceptance requires an ephemeral GitHub-hosted Windows runner.'
}
$Repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$Python = Join-Path $Repo '.venv-desktop/Scripts/python.exe'
$Payload = Join-Path $Repo 'dist/AutoTransAI'
$Version = (Get-Content (Join-Path $Repo 'desktop/packaging/version.txt') -Raw).Trim()
$Setup = Join-Path $Repo "dist/installer/AutoTransAI-$Version-Setup.exe"
$Evidence = Join-Path $Repo 'dist/installer/installed-acceptance.json'
$Workspace = Join-Path $env:RUNNER_TEMP ('AutoTransAI installed ü ' + [guid]::NewGuid().ToString('N'))
$Install = Join-Path $Workspace 'Program ü files'
$Profile = Join-Path $Workspace 'profile'
$Data = Join-Path $Profile 'AutoTransAI'
$DesktopLink = Join-Path ([Environment]::GetFolderPath('DesktopDirectory')) 'AutoTransAI.lnk'
$MenuLink = Join-Path ([Environment]::GetFolderPath('Programs')) 'AutoTransAI/AutoTransAI.lnk'
$RegistryPaths = @(
    'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{941E34A3-7818-4C0D-AE9A-D169D14C3E63}_is1',
    'HKCU:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{941E34A3-7818-4C0D-AE9A-D169D14C3E63}_is1',
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{941E34A3-7818-4C0D-AE9A-D169D14C3E63}_is1',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{941E34A3-7818-4C0D-AE9A-D169D14C3E63}_is1'
)
$Result = [ordered]@{ source = $env:GITHUB_SHA; status = 'failed'; scope = 'one GitHub-hosted Windows CI run; not clean-machine matrix or p95'; phase = 'preflight' }
$OldLocal = $env:LOCALAPPDATA
$Installed = $false
function Assert-Check([bool]$Condition, [string]$Code) { if (-not $Condition) { throw $Code } }
function Invoke-Bounded([string]$File, [string[]]$Arguments, [int]$Seconds) {
    $p = Start-Process -FilePath $File -ArgumentList $Arguments -PassThru
    # Do not kill Setup on timeout or guess at ownership; fail this disposable runner.
    Assert-Check ($p.WaitForExit($Seconds * 1000)) 'process-timeout'
    Assert-Check ($p.ExitCode -eq 0) "process-exit-$($p.ExitCode)"
}
function Assert-NoInstalledProcesses {
    $remaining = @(Get-CimInstance Win32_Process | Where-Object {
        $_.ExecutablePath -and ($_.ExecutablePath.StartsWith($Install + '\', [StringComparison]::OrdinalIgnoreCase))
    })
    Assert-Check ($remaining.Count -eq 0) 'installed-process-survived'
}
try {
    foreach ($path in @($DesktopLink, $MenuLink) + $RegistryPaths) {
        Assert-Check (-not (Test-Path -LiteralPath $path)) 'existing-installation-or-shortcut-refused'
    }
    Assert-Check (-not (Test-Path -LiteralPath $Workspace)) 'workspace-already-exists'
    New-Item -ItemType Directory -Path $Data -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $Workspace '.installed-smoke') -Value 'AutoTransAI installed acceptance'
    # Only this process and its children see the disposable profile. Known-folder
    # shortcuts and HKCU still refer to the runner account and are preflighted above.
    $env:LOCALAPPDATA = $Profile
    $Result.phase = 'silent-install'
    $timer = [Diagnostics.Stopwatch]::StartNew()
    Invoke-Bounded $Setup @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/SP-', '/TASKS=desktopicon', "/DIR=`"$Install`"", "/LOG=`"$Workspace/install.log`"") 300
    $Result.install_seconds = $timer.Elapsed.TotalSeconds
    $Installed = $true
    $Result.installer_bytes = (Get-Item -LiteralPath $Setup).Length
    $Result.phase = 'installed-payload'
    $inventory = Get-Content (Join-Path $Payload 'payload-sha256.json') -Raw | ConvertFrom-Json -AsHashtable
    foreach ($relative in $inventory.Keys) {
        $path = Join-Path $Install $relative
        Assert-Check (Test-Path -LiteralPath $path -PathType Leaf) 'installed-file-missing'
        Assert-Check ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -eq $inventory[$relative]) 'installed-file-hash-mismatch'
    }
    $Result.installed_bytes = (Get-ChildItem -LiteralPath $Install -File -Recurse | Measure-Object Length -Sum).Sum
    $Result.payload_files_verified = $inventory.Count
    $Result.phase = 'shortcuts-registration'
    $shell = New-Object -ComObject WScript.Shell
    foreach ($link in @($DesktopLink, $MenuLink)) {
        Assert-Check (Test-Path -LiteralPath $link) 'shortcut-missing'
        $shortcut = $shell.CreateShortcut($link)
        Assert-Check ($shortcut.TargetPath -eq (Join-Path $Install 'AutoTransAI.exe')) 'shortcut-target-mismatch'
        Assert-Check ($shortcut.WorkingDirectory -eq $Install) 'shortcut-working-directory-mismatch'
    }
    $entries = @($RegistryPaths | Where-Object { Test-Path -LiteralPath $_ })
    Assert-Check ($entries.Count -eq 1) 'uninstall-registration-count'
    $registration = Get-ItemProperty -LiteralPath $entries[0]
    Assert-Check ($registration.InstallLocation.TrimEnd('\') -eq $Install) 'uninstall-location-mismatch'
    $Uninstaller = Join-Path $Install 'unins000.exe'
    Assert-Check ($registration.UninstallString.Trim('"') -eq $Uninstaller) 'uninstall-command-mismatch'
    Assert-NoInstalledProcesses # skipifsilent must prevent autorun.
    $Result.phase = 'installed-backend-restart'
    & $Python (Join-Path $Repo 'desktop/packaging/smoke_frozen.py') $Install --data-root $Data --evidence (Join-Path $Workspace 'backend.json') *> (Join-Path $Workspace 'backend-smoke.log')
    Assert-Check ($LASTEXITCODE -eq 0) 'installed-backend-smoke-failed'
    Assert-NoInstalledProcesses
    $Result.backend = Get-Content (Join-Path $Workspace 'backend.json') -Raw | ConvertFrom-Json
    $Result.phase = 'gui-capability'
    & (Join-Path $PSScriptRoot 'smoke-installed-gui.ps1') -Install $Install -Shortcut $MenuLink -Evidence (Join-Path $Workspace 'gui.json')
    $Result.gui = Get-Content (Join-Path $Workspace 'gui.json') -Raw | ConvertFrom-Json
    Assert-NoInstalledProcesses
    $Result.phase = 'uninstall'
} catch {
    # Only known lowercase assertion codes are public; never arbitrary values.
    $code = 'native-operation-failed'
    if ($_.Exception.Message -cmatch '^[a-z][a-z0-9-]{1,70}$') { $code = $_.Exception.Message }
    Write-Output "::error title=Installed acceptance failed::phase=$($Result.phase); code=$code; type=$($_.Exception.GetType().Name); line=$($_.InvocationInfo.ScriptLineNumber)."
    throw 'Installed acceptance failed; inspect the bounded phase annotation.'
} finally {
    try {
        if ($Installed) {
            $timer = [Diagnostics.Stopwatch]::StartNew()
            Invoke-Bounded (Join-Path $Install 'unins000.exe') @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', "/LOG=`"$Workspace/uninstall.log`"") 120
            # Inno may finish final deletion in its temporary child.
            $deadline = [DateTime]::UtcNow.AddSeconds(30)
            while ((Test-Path -LiteralPath $Install) -and [DateTime]::UtcNow -lt $deadline) { Start-Sleep -Milliseconds 250 }
            Assert-Check (-not (Test-Path -LiteralPath $Install)) 'program-directory-retained'
            foreach ($path in @($DesktopLink, $MenuLink) + $RegistryPaths) {
                Assert-Check (-not (Test-Path -LiteralPath $path)) 'shortcut-or-registration-retained'
            }
            Assert-NoInstalledProcesses
            $Result.uninstall_seconds = $timer.Elapsed.TotalSeconds
            if ($Result.phase -eq 'uninstall') {
                Assert-Check ((Get-Content (Join-Path $Data 'storage/installed-smoke-sentinel.txt') -Raw) -eq 'retained disposable user data') 'user-data-not-retained'
                Assert-Check (Test-Path -LiteralPath (Join-Path $Data 'data/workflow.db')) 'database-not-retained'
                $Result.user_data_retained = $true
                $Result.status = 'passed'
            }
        }
    } catch {
        $Result.status = 'failed'
        Write-Output '::error title=Installed acceptance cleanup failed::Owned uninstaller or removal/retention assertions failed.'
        throw 'Installed acceptance cleanup failed.'
    } finally {
        $env:LOCALAPPDATA = $OldLocal
        $Result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Evidence -Encoding utf8
        # No recursive deletion: runner retirement disposes of this marked workspace.
    }
}
Assert-Check ($Result.status -eq 'passed') 'installed-acceptance-incomplete'
Write-Output "::notice title=Installed acceptance evidence::install/restart/uninstall passed; installer_bytes=$($Result.installer_bytes); installed_bytes=$($Result.installed_bytes); install_seconds=$([math]::Round($Result.install_seconds,3)); uninstall_seconds=$([math]::Round($Result.uninstall_seconds,3)); gui=$($Result.gui.status)"
foreach ($sample in $Result.backend.samples) {
    Write-Output "::notice title=Installed backend timing::startup_seconds=$([math]::Round($sample.startup_seconds,3)); shutdown_seconds=$([math]::Round($sample.shutdown_seconds,3)); single CI run, not p95."
}
