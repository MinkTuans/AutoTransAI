"""
AutoTransAi Native Desktop Window & Process Orchestrator.

1. Sets explicit Windows AppUserModelID for custom Taskbar icon.
2. Starts FastAPI backend and Vite frontend hidden in background.
3. Opens native pywebview Desktop Window with custom app icon.
4. Cleans up process tree on window close.
"""

import sys
import os
import time
import urllib.request
import subprocess
import ctypes
import traceback
from pathlib import Path
from typing import TextIO

import webview

# Set AppUserModelID so Windows Taskbar displays the custom app icon
try:
    myappid = "AutoTransAi.VideoTranslationPipeline.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

ROOT_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
ICON_PATH = FRONTEND_DIR / "public" / "app-logo.ico"
PNG_ICON_PATH = FRONTEND_DIR / "public" / "app-logo.png"
LOG_DIR = ROOT_DIR / "data" / "launcher_logs"
BACKEND_LOG_PATH = LOG_DIR / "backend.log"
FRONTEND_LOG_PATH = LOG_DIR / "frontend.log"
BACKEND_HEALTH_URL = "http://127.0.0.1:8000/api/system/health"
FRONTEND_URL = "http://127.0.0.1:5173"

# Windows flag to hide child command prompt windows
CREATE_NO_WINDOW = 0x08000000


def start_backend(log_stream: TextIO):
    """Start FastAPI backend as a hidden background process."""
    python_exe = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    if not python_exe.exists():
        python_exe = "python"

    return subprocess.Popen(
        [
            str(python_exe),
            "-u",
            "-m", "uvicorn",
            "app.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
        ],
        cwd=str(BACKEND_DIR),
        creationflags=CREATE_NO_WINDOW,
        stdout=log_stream,
        stderr=log_stream,
    )


def start_frontend(log_stream: TextIO):
    """Start Vite frontend dev server as a hidden background process."""
    return subprocess.Popen(
        ["cmd.exe", "/c", "npx vite --port 5173"],
        cwd=str(FRONTEND_DIR),
        creationflags=CREATE_NO_WINDOW,
        stdout=log_stream,
        stderr=log_stream,
    )


def is_server_running(url: str) -> bool:
    """Return whether an HTTP service is already responding at the URL."""
    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            return response.status == 200
    except Exception:
        return False


def wait_for_server(url: str, process: subprocess.Popen, max_retries: int = 30) -> bool:
    """Wait for the spawned process to expose an HTTP service."""
    for _ in range(max_retries):
        if process.poll() is not None:
            return False
        if is_server_running(url) and process.poll() is None:
            return True
        time.sleep(0.5)
    return False


def show_startup_error(component: str, log_path: str) -> None:
    """Show a visible diagnostic when a hidden desktop service cannot start."""
    message = (
        f"{component} không thể khởi động. AutoTransAI sẽ không mở giao diện để tránh "
        f"chạy trong trạng thái lỗi.\n\nXem log tại:\n{log_path}"
    )
    try:
        ctypes.windll.user32.MessageBoxW(0, message, "AutoTransAI Startup Error", 0x10)
    except Exception:
        print(message, file=sys.stderr)


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
    backend_log = None
    frontend_log = None

    try:
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            show_startup_error("Launcher", f"Không thể tạo thư mục log: {exc}")
            return

        # Never open a frontend that cannot reach a healthy backend.
        try:
            backend_log = BACKEND_LOG_PATH.open("w", encoding="utf-8", buffering=1)
        except Exception as exc:
            show_startup_error("Launcher", f"Không thể mở backend log: {exc}")
            return
        if is_server_running(BACKEND_HEALTH_URL):
            backend_log.write(f"Port 8000 is already serving {BACKEND_HEALTH_URL}.\n")
            show_startup_error("Backend", str(BACKEND_LOG_PATH))
            return
        try:
            backend_proc = start_backend(backend_log)
        except Exception:
            traceback.print_exc(file=backend_log)
            show_startup_error("Backend", str(BACKEND_LOG_PATH))
            return
        if not wait_for_server(BACKEND_HEALTH_URL, backend_proc, max_retries=60):
            backend_log.write(f"Backend exited or did not become healthy (exit={backend_proc.poll()}).\n")
            if backend_proc.poll() is None:
                kill_process_tree(backend_proc.pid)
                backend_proc = None
            show_startup_error("Backend", str(BACKEND_LOG_PATH))
            return

        try:
            frontend_log = FRONTEND_LOG_PATH.open("w", encoding="utf-8", buffering=1)
        except Exception as exc:
            if backend_proc.poll() is None:
                kill_process_tree(backend_proc.pid)
                backend_proc = None
            show_startup_error("Launcher", f"Không thể mở frontend log: {exc}")
            return
        if is_server_running(FRONTEND_URL):
            frontend_log.write(f"Port 5173 is already serving {FRONTEND_URL}.\n")
            if backend_proc.poll() is None:
                kill_process_tree(backend_proc.pid)
                backend_proc = None
            show_startup_error("Frontend", str(FRONTEND_LOG_PATH))
            return
        try:
            frontend_proc = start_frontend(frontend_log)
        except Exception:
            traceback.print_exc(file=frontend_log)
            if backend_proc.poll() is None:
                kill_process_tree(backend_proc.pid)
                backend_proc = None
            show_startup_error("Frontend", str(FRONTEND_LOG_PATH))
            return
        if not wait_for_server(FRONTEND_URL, frontend_proc, max_retries=30):
            frontend_log.write(f"Frontend exited or did not become ready (exit={frontend_proc.poll()}).\n")
            if frontend_proc.poll() is None:
                kill_process_tree(frontend_proc.pid)
                frontend_proc = None
            if backend_proc.poll() is None:
                kill_process_tree(backend_proc.pid)
                backend_proc = None
            show_startup_error("Frontend", str(FRONTEND_LOG_PATH))
            return

        # The backend can die while Vite is starting; close that final race
        # before creating a desktop window that would only expose proxy errors.
        if backend_proc.poll() is not None or not is_server_running(BACKEND_HEALTH_URL):
            backend_log.write(
                f"Backend stopped after initial readiness (exit={backend_proc.poll()}).\n"
            )
            if frontend_proc.poll() is None:
                kill_process_tree(frontend_proc.pid)
                frontend_proc = None
            if backend_proc.poll() is None:
                kill_process_tree(backend_proc.pid)
                backend_proc = None
            show_startup_error("Backend", str(BACKEND_LOG_PATH))
            return

        # Determine icon path. A PNG renamed to .ico is not a Windows ICO and
        # can crash pywebview before the window appears (pythonw hides stderr).
        icon_file = str(ICON_PATH) if ICON_PATH.exists() else str(PNG_ICON_PATH)

        # Create Native GUI Window
        window = webview.create_window(
            title="AutoTransAi — AI Video Translation & Dubbing Production",
            url=FRONTEND_URL,
            width=1300,
            height=850,
            resizable=True,
            text_select=True,
        )

        # Start GUI Loop (blocks until user closes window)
        try:
            webview.start(icon=icon_file)
        except Exception:
            webview.start()

    finally:
        # Cleanup when app window is closed
        if backend_proc and backend_proc.poll() is None:
            kill_process_tree(backend_proc.pid)

        if frontend_proc and frontend_proc.poll() is None:
            kill_process_tree(frontend_proc.pid)

        if backend_log:
            backend_log.close()
        if frontend_log:
            frontend_log.close()

if __name__ == "__main__":
    main()
