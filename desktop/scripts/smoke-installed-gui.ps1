[CmdletBinding()]
param([Parameter(Mandatory)][string]$Install, [Parameter(Mandatory)][string]$Shortcut, [Parameter(Mandatory)][string]$Evidence)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if ($env:GITHUB_ACTIONS -ne 'true' -or $env:RUNNER_ENVIRONMENT -ne 'github-hosted' -or
    -not (Test-Path -LiteralPath (Join-Path (Split-Path $Install -Parent) '.installed-smoke'))) {
    throw 'GUI acceptance requires the marked disposable installed harness.'
}
if (@(Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq (Join-Path $Install 'AutoTransAI.exe') }).Count) {
    throw 'Existing installed process refused.'
}
Add-Type @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class InstalledSmokeDesktop {
    [DllImport("user32.dll", SetLastError=true)] public static extern IntPtr OpenInputDesktop(uint flags, bool inherit, uint access);
    [DllImport("user32.dll")] public static extern bool CloseDesktop(IntPtr desktop);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr window);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr window, out uint pid);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr window, StringBuilder name, int count);
    public delegate bool EnumCallback(IntPtr window, IntPtr parameter);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumCallback callback, IntPtr parameter);
    public static bool VisibleConsole(uint[] owned) {
        bool found = false;
        EnumWindows((window, unused) => {
            uint pid; GetWindowThreadProcessId(window, out pid);
            if (Array.IndexOf(owned, pid) >= 0 && IsWindowVisible(window)) {
                var name = new StringBuilder(256); GetClassName(window, name, 256);
                if (name.ToString() == "ConsoleWindowClass") found = true;
            }
            return true;
        }, IntPtr.Zero);
        return found;
    }
}
'@
$session = (Get-Process -Id $PID).SessionId
$desktop = [InstalledSmokeDesktop]::OpenInputDesktop(0, $false, 1)
$result = [ordered]@{ status = 'not-run'; user_interactive = [Environment]::UserInteractive; session_id = $session; input_desktop_opened = ($desktop -ne [IntPtr]::Zero) }
if ($desktop -ne [IntPtr]::Zero) { [void][InstalledSmokeDesktop]::CloseDesktop($desktop) }
if (-not $result.user_interactive -or $session -eq 0 -or -not $result.input_desktop_opened) {
    $result.reason = 'Runner lacks interactive non-session-zero input desktop; manual GUI acceptance remains open.'
    $result | ConvertTo-Json | Set-Content -LiteralPath $Evidence
    Write-Output "::notice title=Installed GUI capability::not-run; interactive=$($result.user_interactive); session=$session; input_desktop=$($result.input_desktop_opened)"
    return
}
$exe = Join-Path $Install 'AutoTransAI.exe'
$owned = @{}
$main = $null
try {
    # ShellExecute the real installed Start Menu shortcut, inheriting the harness's
    # disposable LOCALAPPDATA. No test-only native bridge or application switch.
    Start-Process -FilePath $Shortcut
    $deadline = [DateTime]::UtcNow.AddSeconds(100)
    $stable = $null
    do {
        $processes = @(Get-CimInstance Win32_Process)
        foreach ($p in $processes) {
            if (($p.ExecutablePath -eq $exe) -or $owned.ContainsKey([int]$p.ParentProcessId)) {
                if (-not $owned.ContainsKey([int]$p.ProcessId)) {
                    try { $owned[[int]$p.ProcessId] = Get-Process -Id $p.ProcessId -ErrorAction Stop } catch { }
                }
            }
        }
        $main = $null
        foreach ($p in $owned.Values) {
            $p.Refresh()
            if (-not $p.HasExited -and $p.MainWindowHandle -ne 0 -and $p.MainWindowTitle -eq 'AutoTransAI Studio' -and [InstalledSmokeDesktop]::IsWindowVisible($p.MainWindowHandle)) { $main = $p }
        }
        if ([InstalledSmokeDesktop]::VisibleConsole([uint[]]@($owned.Keys))) { throw 'owned-visible-console' }
        $backends = @($processes | Where-Object { $_.ExecutablePath -eq $exe -and $_.CommandLine -match '--desktop-backend' })
        if ($main -and $backends.Count -eq 1) {
            if ($null -eq $stable) { $stable = [DateTime]::UtcNow }
            if (([DateTime]::UtcNow - $stable).TotalSeconds -ge 10) { break }
        } else { $stable = $null }
        Start-Sleep -Milliseconds 500
    } while ([DateTime]::UtcNow -lt $deadline)
    if ($null -eq $stable -or ([DateTime]::UtcNow - $stable).TotalSeconds -lt 10) { throw 'owned-main-window-or-backend-not-stable' }
    $result.owned_processes_observed = $owned.Count
    $result.main_window_observed = $true
    $result.visible_owned_console = $false
    if (-not $main.CloseMainWindow()) { throw 'main-window-close-refused' }
    foreach ($p in $owned.Values) {
        if (-not $p.WaitForExit(20000)) { throw 'owned-gui-process-survived' }
    }
    $result.status = 'passed'
    $result.scope = 'Installed shortcut, stable owned main window/backend, no observed owned console window, WM_CLOSE and observed tree exit. No pixel/Studio/media interaction assertion.'
} finally {
    # Exact process objects collected from this launch only; no process-name kills.
    foreach ($p in $owned.Values) {
        if (-not $p.HasExited) { $p.Kill(); $p.WaitForExit(5000) | Out-Null }
    }
    $result | ConvertTo-Json | Set-Content -LiteralPath $Evidence
}
