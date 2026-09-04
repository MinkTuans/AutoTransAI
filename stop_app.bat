@echo off
echo Stopping AutoTransAi background processes...
powershell -Command "Get-Process -Name python, uvicorn, node, vite -ErrorAction SilentlyContinue | Where-Object {$_.Path -like '*AutoTransAi*' -or $_.Path -like '*WorkflowVdAi*'} | Stop-Process -Force"
powershell -Command "$p8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue; if ($p8000) { Stop-Process -Id $p8000.OwningProcess -Force }"
powershell -Command "$p5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue; if ($p5173) { Stop-Process -Id $p5173.OwningProcess -Force }"
echo Stopped successfully.
