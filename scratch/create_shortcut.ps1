$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut("C:\Hack\AutoTransAI\AutoTransAI Studio.lnk")
$s.TargetPath = "C:\Hack\AutoTransAI\AutoTransAi.vbs"
$s.WorkingDirectory = "C:\Hack\AutoTransAI"
$s.IconLocation = "C:\Hack\AutoTransAI\app-logo.ico"
$s.Description = "AutoTransAI Studio - Video Translation & Dubbing Suite"
$s.Save()

Write-Host "Shortcut created successfully!"
