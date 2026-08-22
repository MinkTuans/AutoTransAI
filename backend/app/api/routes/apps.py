"""
Apps manager route for status checking and background process launching
of KrillinAI, pyVideoTrans, and SoniTranslate.
"""

import sys
import os
import shutil
import socket
import asyncio
import subprocess
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/apps", tags=["Apps Launcher"])

ROOT_DIR = Path(__file__).resolve().parents[3]
EXTERNAL_DIR = ROOT_DIR / "external"

APP_PORTS = {
    "workflow_vd_ai": 8000,
    "krillin_ai": 8888,
    "py_video_trans": 9999,
    "soni_translate": 7860,
}

RUNNING_PROCESSES = {}

def is_port_open(port: int, host: str = "127.0.0.1") -> bool:
    """Check if TCP port is active and accepting connections."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

@router.get("/status")
async def get_apps_status():
    """Return online/offline status of all 4 applications."""
    status = {}
    for app_key, port in APP_PORTS.items():
        running = is_port_open(port)
        status[app_key] = {
            "running": running,
            "port": port,
            "url": f"http://localhost:{port}" if app_key != "workflow_vd_ai" else "http://localhost:5173",
        }
    return status

@router.post("/launch/{app_key}")
async def launch_app(app_key: str):
    """Launch an external app background process if not already running."""
    if app_key not in APP_PORTS:
        raise HTTPException(status_code=400, detail="Unknown app key")

    port = APP_PORTS[app_key]
    if is_port_open(port):
        return {
            "success": True,
            "message": f"App {app_key} is already running",
            "url": f"http://localhost:{port}",
        }

    CREATE_NO_WINDOW = 0x08000000

    if app_key == "py_video_trans":
        py_dir = EXTERNAL_DIR / "pyvideotrans"
        if not py_dir.exists():
            raise HTTPException(status_code=404, detail="pyVideoTrans folder not found")
        
        proc = subprocess.Popen(
            [sys.executable, "webui.py"],
            cwd=str(py_dir),
            creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        RUNNING_PROCESSES[app_key] = proc

    elif app_key == "soni_translate":
        soni_dir = EXTERNAL_DIR / "SoniTranslate"
        if not soni_dir.exists():
            raise HTTPException(status_code=404, detail="SoniTranslate folder not found")
        
        proc = subprocess.Popen(
            [sys.executable, "app_rvc.py"],
            cwd=str(soni_dir),
            creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        RUNNING_PROCESSES[app_key] = proc

    elif app_key == "krillin_ai":
        krillin_dir = EXTERNAL_DIR / "KrillinAI"
        if not krillin_dir.exists():
            raise HTTPException(status_code=404, detail="KrillinAI folder not found")
        
        proc = subprocess.Popen(
            [sys.executable, "python_server.py"],
            cwd=str(krillin_dir),
            creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        RUNNING_PROCESSES[app_key] = proc

    # Wait up to 5s for process startup
    for _ in range(10):
        if is_port_open(port):
            break
        await asyncio.sleep(0.5)

    return {
        "success": True,
        "message": f"Launched {app_key}",
        "url": f"http://localhost:{port}",
    }
