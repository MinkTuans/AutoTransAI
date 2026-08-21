"""
WorkflowVdAi Native Desktop Window & Process Orchestrator.

1. Sets explicit Windows AppUserModelID for custom Taskbar icon.
2. Starts FastAPI backend and Vite frontend hidden in background.
3. Opens native pywebview Desktop Window with custom cyber-wolf app-logo.ico.
4. Cleans up process tree on window close.
"""

import sys
import os
import time
import urllib.request
import subprocess
import ctypes
from pathlib import Path

import webview

# Set AppUserModelID so Windows Taskbar displays the custom app icon
try:
    myappid = "WorkflowVdAi.ScriptToVideoPipeline.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

ROOT_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
ICON_PATH = FRONTEND_DIR / "public" / "app-logo.ico"
PNG_ICON_PATH = FRONTEND_DIR / "public" / "app-logo.png"

# Windows flag to hide child command prompt windows
CREATE_NO_WINDOW = 0x08000000


def start_backend():
    """Start FastAPI backend as a hidden background process."""
    python_exe = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    if not python_exe.exists():
        python_exe = "python"

    return subprocess.Popen(
        [
            str(python_exe),
            "-m", "uvicorn",
            "app.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
        ],
        cwd=str(BACKEND_DIR),
        creationflags=CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def start_frontend():
    """Start Vite frontend dev server as a hidden background process."""
    return subprocess.Popen(
        ["cmd.exe", "/c", "npx vite --port 5173"],
        cwd=str(FRONTEND_DIR),
        creationflags=CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_for_server(url: str, max_retries: int = 30) -> bool:
    """Wait for web server to respond."""
    for _ in range(max_retries):
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def kill_process_tree(pid: int):
    """Cleanly terminate a process tree on Windows."""
    try:
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            creationflags=CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except Exception:
        pass


def main():
    backend_proc = None
    frontend_proc = None

    try:
        # Start processes hidden
        backend_proc = start_backend()
        frontend_proc = start_frontend()

        # Wait for frontend server
        wait_for_server("http://localhost:5173")

        # Determine icon path
        icon_file = str(ICON_PATH) if ICON_PATH.exists() else str(PNG_ICON_PATH)

        # Create Native GUI Window
        window = webview.create_window(
            title="WorkflowVdAi — Script to Video Production",
            url="http://localhost:5173",
            width=1300,
            height=850,
            resizable=True,
            text_select=True,
        )

        # Start GUI Loop (blocks until user closes window)
        webview.start(icon=icon_file)

    finally:
        # Cleanup when app window is closed
        if backend_proc and backend_proc.poll() is None:
            kill_process_tree(backend_proc.pid)

        if frontend_proc and frontend_proc.poll() is None:
            kill_process_tree(frontend_proc.pid)

        # Fallback port cleanup
        for port in [8000, 5173]:
            try:
                res = subprocess.run(
                    ["powershell", "-Command", f"(Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue).OwningProcess"],
                    capture_output=True,
                    text=True,
                    creationflags=CREATE_NO_WINDOW,
                )
                pid_str = res.stdout.strip()
                if pid_str and pid_str.isdigit():
                    kill_process_tree(int(pid_str))
            except Exception:
                pass


if __name__ == "__main__":
    main()
