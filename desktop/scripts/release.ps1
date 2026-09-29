[CmdletBinding()]
param(
    [string]$Python = 'python',
    [string]$SignScript = '',
    [string]$SignToolCommand = '',
    [string]$WebView2Installer = '',
    [string]$ISCC = ''
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
# Local artifact production only: no upload, publishing, automatic update or credentials.
& (Join-Path $PSScriptRoot 'build.ps1') -Python $Python -SignScript $SignScript
& (Join-Path $PSScriptRoot 'package.ps1') -SignToolCommand $SignToolCommand -WebView2Installer $WebView2Installer -ISCC $ISCC
Write-Host 'Release candidate artifacts created locally. Complete Windows installed acceptance and third-party redistribution review before publication.'
