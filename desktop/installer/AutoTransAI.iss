; Compile through desktop/scripts/package.ps1 after payload and signature audits.
; WebView2 policy: default bundle contains the online Evergreen bootstrapper.
; A supplied x64 Evergreen Standalone Installer supports offline installation.
#ifndef AppVersion
  #error AppVersion must be provided by package.ps1
#endif
#ifndef PayloadDir
  #error PayloadDir must be provided by package.ps1
#endif
#ifndef WebViewInstaller
  #error A verified WebView2 prerequisite installer must be supplied
#endif
#ifndef WebViewSHA256
  #error WebViewSHA256 must be provided by package.ps1
#endif
#ifndef OutputDir
  #define OutputDir "..\..\dist\installer"
#endif
#ifndef AppIcon
  #define AppIcon "..\..\frontend\public\app-logo.ico"
#endif

[Setup]
AppId={{941E34A3-7818-4C0D-AE9A-D169D14C3E63}
AppName=AutoTransAI
AppVersion={#AppVersion}
AppPublisher=AutoTransAI
VersionInfoVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\AutoTransAI
DefaultGroupName=AutoTransAI
DisableDirPage=no
DisableWelcomePage=no
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.19041
OutputDir={#OutputDir}
OutputBaseFilename=AutoTransAI-{#AppVersion}-Setup
SetupIconFile={#AppIcon}
UninstallDisplayIcon={app}\AutoTransAI.exe
UninstallDisplayName=AutoTransAI
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
AppMutex={code:DesktopMutex}
CloseApplications=no
RestartApplications=no
#ifdef EnableSigning
SignTool=external
SignedUninstaller=yes
#endif

[Tasks]
Name: "desktopicon"; Description: "Create a Desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: unchecked

[Files]
Source: "{#PayloadDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#WebViewInstaller}"; DestName: "AutoTransAI-WebView2Installer.exe"; Flags: dontcopy

[Icons]
Name: "{userprograms}\AutoTransAI\AutoTransAI"; Filename: "{app}\AutoTransAI.exe"; WorkingDir: "{app}"
Name: "{userdesktop}\AutoTransAI"; Filename: "{app}\AutoTransAI.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\AutoTransAI.exe"; Description: "Launch AutoTransAI"; Flags: nowait postinstall skipifsilent runasoriginaluser

[Code]
const
  WebViewKey = 'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}';

function DesktopMutex(Param: String): String;
begin
  Result := 'Global\AutoTransAI.Desktop.' + Copy(Lowercase(GetSHA256OfString(
    Utf8Encode(Lowercase(ExpandConstant('{localappdata}\AutoTransAI'))))), 1, 24);
end;

function HasWebViewVersion(Root: Integer): Boolean;
var
  Version: String;
  PackedVersion: Int64;
begin
  Result := RegQueryStringValue(Root, WebViewKey, 'pv', Version);
  if Result then
    Result := StrToVersion(Version, PackedVersion);
  if Result then
    Result := PackedVersion > 0;
end;

function HasWebView2(): Boolean;
begin
  Result := HasWebViewVersion(HKCU32) or HasWebViewVersion(HKLM32);
  if IsWin64 then
    Result := Result or HasWebViewVersion(HKCU64) or HasWebViewVersion(HKLM64);
end;

function VerifyMicrosoftSignature(const InstallerPath: String): Boolean;
var
  ScriptPath, ScriptText, QuotedPath: String;
  ScriptLines: TArrayOfString;
  ExitCode: Integer;
begin
  Result := False;
  ScriptPath := ExpandConstant('{tmp}\verify-webview2.ps1');
  QuotedPath := InstallerPath;
  StringChangeEx(QuotedPath, '''', '''''', True);
  ScriptText := '$ErrorActionPreference = ''Stop''' + #13#10 +
    '$s = Get-AuthenticodeSignature -LiteralPath ''' + QuotedPath + '''' + #13#10 +
    'if ($s.Status -ne ''Valid'' -or $null -eq $s.SignerCertificate -or ' +
    '$s.SignerCertificate.Subject -notmatch ''(^|,\s*)O=Microsoft Corporation(,|$)'') { exit 1 }' + #13#10 +
    'exit 0' + #13#10;
  SetArrayLength(ScriptLines, 1);
  ScriptLines[0] := ScriptText;
  if not SaveStringsToUTF8File(ScriptPath, ScriptLines, False) then
    Exit;
  if Exec(ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe'),
      '-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' + ScriptPath + '"',
      '', SW_HIDE, ewWaitUntilTerminated, ExitCode) then
    Result := ExitCode = 0;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  InstallerPath: String;
  ExitCode: Integer;
begin
  Result := '';
  if HasWebView2() then
    Exit;
  WizardForm.StatusLabel.Caption := 'Installing Microsoft Edge WebView2 Runtime...';
  ExtractTemporaryFile('AutoTransAI-WebView2Installer.exe');
  InstallerPath := ExpandConstant('{tmp}\AutoTransAI-WebView2Installer.exe');
  if (Lowercase(GetSHA256OfFile(InstallerPath)) <> Lowercase('{#WebViewSHA256}')) or
      (not VerifyMicrosoftSignature(InstallerPath)) then
  begin
    Result := 'WebView2 prerequisite verification failed. Download a fresh AutoTransAI installer or install the official Microsoft WebView2 Runtime, then retry.';
    Exit;
  end;
  if not Exec(InstallerPath, '/silent /install', '', SW_HIDE, ewWaitUntilTerminated, ExitCode) then
  begin
    Result := 'Could not start the Microsoft WebView2 installer. Install the official WebView2 Runtime and retry.';
    Exit;
  end;
  if (ExitCode <> 0) and (ExitCode <> 3010) then
  begin
    Result := 'WebView2 installation failed (code ' + IntToStr(ExitCode) + '). The standard setup needs internet access. For offline computers, use a package containing the Evergreen Standalone Installer or preinstall WebView2.';
    Exit;
  end;
  if not HasWebView2() then
  begin
    Result := 'WebView2 Runtime is still unavailable. Finish any required restart, or install the official x64 Evergreen WebView2 Runtime and retry.';
    Exit;
  end;
  NeedsRestart := ExitCode = 3010;
end;

procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.Caption :=
    'Install AutoTransAI for this Windows user. Microsoft Edge WebView2 is required; the standard setup needs internet access if it is missing.' + #13#10 + #13#10 +
    'Uninstall removes program files and shortcuts. Projects, credentials, logs and browser profile remain in %LOCALAPPDATA%\AutoTransAI. Back up this folder before removing it manually.';
end;
