Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
iconScript = scriptDir & "\update_app_icon.ps1"
pythonwPath = scriptDir & "\backend\venv\Scripts\pythonw.exe"
pythonScript = scriptDir & "\app_launcher.py"
WshShell.Run "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File """ & iconScript & """", 0, True
WshShell.Run """" & pythonwPath & """ """ & pythonScript & """", 0, False
