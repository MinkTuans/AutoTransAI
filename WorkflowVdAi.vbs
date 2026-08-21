Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonwPath = scriptDir & "\backend\venv\Scripts\pythonw.exe"
pythonScript = scriptDir & "\app_launcher.py"
WshShell.Run """" & pythonwPath & """ """ & pythonScript & """", 0, False
