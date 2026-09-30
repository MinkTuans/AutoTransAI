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
    [DllImport("user32.dll")] public static extern IntPtr GetMenu(IntPtr window);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr window);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
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
$oldArguments = $env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS
$socket = $null
$sequence = 0
function Invoke-Cdp([string]$Method, [hashtable]$Parameters) {
    $script:sequence++
    $id = $script:sequence
    $cancel = [Threading.CancellationTokenSource]::new(10000)
    try {
        $bytes = [Text.Encoding]::UTF8.GetBytes((@{ id=$id; method=$Method; params=$Parameters } | ConvertTo-Json -Depth 8 -Compress))
        $socket.SendAsync([ArraySegment[byte]]::new($bytes), [Net.WebSockets.WebSocketMessageType]::Text, $true, $cancel.Token).GetAwaiter().GetResult()
        do {
            $stream = [IO.MemoryStream]::new()
            try {
                do {
                    $buffer = [byte[]]::new(65536)
                    $received = $socket.ReceiveAsync([ArraySegment[byte]]::new($buffer), $cancel.Token).GetAwaiter().GetResult()
                    if ($received.MessageType -eq [Net.WebSockets.WebSocketMessageType]::Close) { throw 'cdp-closed' }
                    $stream.Write($buffer, 0, $received.Count)
                    if ($stream.Length -gt 1048576) { throw 'cdp-response-too-large' }
                } until ($received.EndOfMessage)
                $message = [Text.Encoding]::UTF8.GetString($stream.ToArray()) | ConvertFrom-Json -AsHashtable
            } finally { $stream.Dispose() }
        } until ($message.ContainsKey('id') -and $message.id -eq $id)
        if ($message.ContainsKey('error')) { throw 'cdp-operation-failed' }
        return $message.result
    } finally { $cancel.Dispose() }
}
function Get-PageState {
    $reply = Invoke-Cdp 'Runtime.evaluate' @{ expression="(async()=>({origin:performance.timeOrigin,ready:document.readyState,studio:!!document.querySelector('#root')?.children.length,status:(await fetch('/api/system/health')).status}))()"; awaitPromise=$true; returnByValue=$true }
    if (-not $reply.result.ContainsKey('value')) { throw 'page-state-unavailable' }
    return $reply.result.value
}
try {
    if (Get-NetTCPConnection -LocalPort 9229 -State Listen -ErrorAction SilentlyContinue) { throw 'debug-port-occupied' }
    # Instrument only this disposable launch, never ship debugging settings.
    $env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = '--remote-debugging-port=9229'

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
    if ([InstalledSmokeDesktop]::GetMenu($main.MainWindowHandle) -ne [IntPtr]::Zero) { throw 'native-menu-present' }
    $result.native_menu_absent = $true
    $targets = @(@(Invoke-RestMethod 'http://127.0.0.1:9229/json/list' -TimeoutSec 5) | Where-Object { $_.type -eq 'page' -and $_.url.StartsWith('http://127.0.0.1:8000/') })
    if ($targets.Count -ne 1) { throw 'studio-debug-target-count' }
    $socket = [Net.WebSockets.ClientWebSocket]::new()
    $cancel = [Threading.CancellationTokenSource]::new(10000)
    try { $socket.ConnectAsync([Uri]$targets[0].webSocketDebuggerUrl, $cancel.Token).GetAwaiter().GetResult() } finally { $cancel.Dispose() }
    $before = Get-PageState
    if ($before.status -ne 200 -or -not $before.studio -or $before.ready -ne 'complete') { throw 'studio-not-ready' }
    $cookiesBefore = (Invoke-Cdp 'Network.getCookies' @{ urls=@('http://127.0.0.1:8000/') }).cookies | ConvertTo-Json -Depth 8 -Compress
    $backendId = $backends[0].ProcessId
    [void][InstalledSmokeDesktop]::SetForegroundWindow($main.MainWindowHandle)
    Start-Sleep -Milliseconds 500
    if ([InstalledSmokeDesktop]::GetForegroundWindow() -ne $main.MainWindowHandle) { throw 'keyboard-focus-unavailable' }
    (New-Object -ComObject WScript.Shell).SendKeys('{F5}')
    $deadline = [DateTime]::UtcNow.AddSeconds(30)
    do {
        Start-Sleep -Milliseconds 500
        $after = Get-PageState
        if ($after.origin -gt $before.origin -and $after.ready -eq 'complete' -and $after.studio -and $after.status -eq 200) { break }
    } while ([DateTime]::UtcNow -lt $deadline)
    if ($after.origin -le $before.origin -or $after.status -ne 200 -or -not $after.studio) { throw 'f5-reload-not-observed' }
    $cookiesAfter = (Invoke-Cdp 'Network.getCookies' @{ urls=@('http://127.0.0.1:8000/') }).cookies | ConvertTo-Json -Depth 8 -Compress
    if ($cookiesBefore -ne $cookiesAfter -or $cookiesBefore -eq '[]') { throw 'f5-session-changed' }
    $currentBackends = @(Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq $exe -and $_.CommandLine -match '--desktop-backend' })
    if ($currentBackends.Count -ne 1 -or $currentBackends[0].ProcessId -ne $backendId) { throw 'f5-backend-changed' }
    $result.f5 = @{ status='passed'; keyboard='WScript SendKeys F5 to verified foreground installed window'; document_time_origin_changed=$true; authenticated_health_after=200; same_session_cookie=$true; same_backend_pid=$true }
    Write-Output '::notice title=Installed F5/menu evidence::Injected keyboard F5 delivery; document timeOrigin changed; Studio DOM and authenticated health returned; backend PID/session cookie unchanged; Win32 native menu absent.'
    $result.owned_processes_observed = $owned.Count
    $result.main_window_observed = $true
    $result.visible_owned_console = $false
    if (-not $main.CloseMainWindow()) { throw 'main-window-close-refused' }
    foreach ($p in $owned.Values) {
        if (-not $p.WaitForExit(20000)) { throw 'owned-gui-process-survived' }
    }
    $result.status = 'passed'
    $result.scope = 'Installed shortcut, stable owned main window/backend, no observed owned console window, WM_CLOSE and observed tree exit. F5 reload and native menu absence asserted through disposable CDP instrumentation; no pixel/media/provider assertion.'
} finally {
    $env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = $oldArguments
    if ($null -ne $socket) { $socket.Dispose() }
    # Exact process objects collected from this launch only; no process-name kills.
    foreach ($p in $owned.Values) {
        if (-not $p.HasExited) { $p.Kill(); $p.WaitForExit(5000) | Out-Null }
    }
    $result | ConvertTo-Json | Set-Content -LiteralPath $Evidence
}
