[CmdletBinding()]
param(
    [string]$Python = "",
    [string]$Payload = "",
    [string]$OutputDirectory = "",
    [string]$ISCC = "",
    # Supply Microsoft's signed x64 Evergreen Standalone Installer for offline deployment.
    [string]$WebView2Installer = "",
    # Inno SignTool command: credentials/certificates remain external to source control.
    [string]$SignToolCommand = ""
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if ($env:OS -ne 'Windows_NT') { throw 'Installer packaging requires Windows, PowerShell and Inno Setup 6.4+.' }
$Repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if (-not $Python) { $Python = Join-Path $Repo '.venv-desktop\Scripts\python.exe' }
if (-not $Payload) { $Payload = Join-Path $Repo 'dist\AutoTransAI' }
if (-not $OutputDirectory) { $OutputDirectory = Join-Path $Repo 'dist\installer' }
$Payload = (Resolve-Path -LiteralPath $Payload).Path
$Version = (Get-Content -LiteralPath (Join-Path $Repo 'desktop\packaging\version.txt') -Raw).Trim()
if ($Version -notmatch '^\d+\.\d+\.\d+(\.\d+)?$') { throw 'Invalid Windows application version.' }
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw 'Desktop build Python missing. Run desktop/scripts/build.ps1 first or pass -Python.' }
& $Python (Join-Path $Repo 'desktop\packaging\verify_payload.py') $Payload
if ($LASTEXITCODE -ne 0) { throw 'Payload verification failed. Packaging aborted.' }
if (-not $ISCC) {
    $Compiler = Get-Command 'ISCC.exe' -ErrorAction SilentlyContinue
    if ($Compiler) { $ISCC = $Compiler.Source }
    else { $ISCC = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe' }
}
if (-not (Test-Path -LiteralPath $ISCC -PathType Leaf)) { throw 'Install Inno Setup 6.4+ or pass -ISCC with its compiler path.' }
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$OutputDirectory = (Resolve-Path -LiteralPath $OutputDirectory).Path
$PrerequisiteDirectory = Join-Path $Repo 'build\desktop-prerequisites'
New-Item -ItemType Directory -Force -Path $PrerequisiteDirectory | Out-Null
$PrerequisiteSource = 'Provided Microsoft installer'
if (-not $WebView2Installer) {
    $WebView2Installer = Join-Path $PrerequisiteDirectory 'MicrosoftEdgeWebview2Setup.exe'
    $PrerequisiteSource = 'https://go.microsoft.com/fwlink/p/?LinkId=2124703'
    Invoke-WebRequest -Uri $PrerequisiteSource -OutFile $WebView2Installer -UseBasicParsing
}
$WebView2Installer = (Resolve-Path -LiteralPath $WebView2Installer).Path
$Signature = Get-AuthenticodeSignature -LiteralPath $WebView2Installer
if ($Signature.Status -ne 'Valid' -or $null -eq $Signature.SignerCertificate -or
    $Signature.SignerCertificate.Subject -notmatch '(^|,\s*)O=Microsoft Corporation(,|$)') {
    throw 'WebView2 installer does not have a valid Microsoft Authenticode signature.'
}
$PrerequisiteHash = (Get-FileHash -LiteralPath $WebView2Installer -Algorithm SHA256).Hash.ToLowerInvariant()
$Arguments = @(
    "/DAppVersion=$Version", "/DPayloadDir=$Payload", "/DOutputDir=$OutputDirectory",
    "/DAppIcon=$(Join-Path $Repo 'frontend\public\app-logo.ico')",
    "/DWebViewInstaller=$WebView2Installer", "/DWebViewSHA256=$PrerequisiteHash"
)
if ($SignToolCommand) { $Arguments += '/DEnableSigning=1'; $Arguments += "/Sexternal=$SignToolCommand" }
$Arguments += (Join-Path $Repo 'desktop\installer\AutoTransAI.iss')
& $ISCC @Arguments
if ($LASTEXITCODE -ne 0) { throw 'Inno Setup compilation failed.' }
$Setup = Join-Path $OutputDirectory "AutoTransAI-$Version-Setup.exe"
if (-not (Test-Path -LiteralPath $Setup -PathType Leaf)) { throw 'Compiler did not produce the expected installer.' }
if ($SignToolCommand -and (Get-AuthenticodeSignature -LiteralPath $Setup).Status -ne 'Valid') {
    throw 'Requested installer signing did not produce a valid Authenticode signature.'
}
$SetupHash = (Get-FileHash -LiteralPath $Setup -Algorithm SHA256).Hash.ToLowerInvariant()
"$SetupHash  $(Split-Path $Setup -Leaf)" | Set-Content -LiteralPath "$Setup.sha256" -Encoding Ascii
[ordered]@{
    version = $Version
    installer = (Split-Path $Setup -Leaf)
    sha256 = $SetupHash
    signed = [bool]$SignToolCommand
    webview2_source = $PrerequisiteSource
    webview2_sha256 = $PrerequisiteHash
    webview2_signer = $Signature.SignerCertificate.Subject
    webview2_certificate_thumbprint = $Signature.SignerCertificate.Thumbprint
    created_utc = [DateTime]::UtcNow.ToString('o')
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $OutputDirectory 'package-provenance.json') -Encoding UTF8
Write-Output "Installer compiled: $Setup"
Write-Output 'Installed Windows acceptance remains a separate required verification step.'
