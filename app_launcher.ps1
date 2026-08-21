# WorkflowVdAi Silent Desktop App Launcher & Process Manager
$rootDir = $PSScriptRoot

# 1. Start Backend Process (Hidden)
$backendInfo = New-Object System.Diagnostics.ProcessStartInfo
$backendInfo.FileName = "$rootDir\backend\venv\Scripts\python.exe"
$backendInfo.Arguments = "-m uvicorn app.main:app --host 127.0.0.1 --port 8000"
$backendInfo.WorkingDirectory = "$rootDir\backend"
$backendInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$backendInfo.CreateNoWindow = $true

$backendProcess = [System.Diagnostics.Process]::Start($backendInfo)

# 2. Start Frontend Process (Hidden)
$frontendInfo = New-Object System.Diagnostics.ProcessStartInfo
$frontendInfo.FileName = "cmd.exe"
$frontendInfo.Arguments = "/c npx vite --port 5173"
$frontendInfo.WorkingDirectory = "$rootDir\frontend"
$frontendInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$frontendInfo.CreateNoWindow = $true

$frontendProcess = [System.Diagnostics.Process]::Start($frontendInfo)

# 3. Wait for Frontend Server to be responsive
$url = "http://localhost:5173"
$maxAttempts = 30
$attempt = 0
$serverReady = $false

while ($attempt -lt $maxAttempts) {
    try {
        $req = [System.Net.WebRequest]::Create($url)
        $req.Timeout = 1000
        $res = $req.GetResponse()
        $res.Close()
        $serverReady = $true
        break
    } catch {
        Start-Sleep -Milliseconds 500
        $attempt++
    }
}

# 4. Launch Desktop App Window (Edge App mode or Default Browser)
$appWindowProcess = $null

$edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edgePath)) {
    $edgePath = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
}

if (Test-Path $edgePath) {
    # Launch in standalone App Window mode (feels like a native desktop app with icon)
    $appInfo = New-Object System.Diagnostics.ProcessStartInfo
    $appInfo.FileName = $edgePath
    $appInfo.Arguments = "--app=http://localhost:5173 --user-data-dir=`"$rootDir\data\browser_profile`""
    $appWindowProcess = [System.Diagnostics.Process]::Start($appInfo)
} else {
    # Fallback to default browser
    Start-Process $url
}

# 5. Monitor App Window - When user closes app window, perform cleanup!
if ($null -ne $appWindowProcess) {
    $appWindowProcess.WaitForExit()
}

# 6. CLEANUP: Terminate child backend and frontend processes cleanly when app is closed
try {
    if ($null -ne $backendProcess -and -not $backendProcess.HasExited) {
        cmd.exe /c "taskkill /PID $($backendProcess.Id) /T /F" | Out-Null
    }
} catch {}

try {
    if ($null -ne $frontendProcess -and -not $frontendProcess.HasExited) {
        cmd.exe /c "taskkill /PID $($frontendProcess.Id) /T /F" | Out-Null
    }
} catch {}

# Fallback cleanup for node/uvicorn child processes on port 8000/5173 if any remain
try {
    $port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    if ($port8000) { Stop-Process -Id $port8000.OwningProcess -Force -ErrorAction SilentlyContinue }
    $port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
    if ($port5173) { Stop-Process -Id $port5173.OwningProcess -Force -ErrorAction SilentlyContinue }
} catch {}
