@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0update_app_icon.ps1"
echo Updated AutoTransAI Studio icon. Open Windows Search again if it still shows the old wolf.
pause
