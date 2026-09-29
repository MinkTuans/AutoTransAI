"""Private backend entrypoint. No application imports before the stdin handshake."""
from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading


def restore_standard_streams() -> None:
    """PyInstaller windowed sets sys.std* to None despite inherited pipe handles."""
    if os.name != 'nt':
        return
    import ctypes
    from ctypes import wintypes
    import msvcrt
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetStdHandle.argtypes = [wintypes.DWORD]
    kernel.GetStdHandle.restype = wintypes.HANDLE
    for name, number, mode, flags in (
        ('stdin', -10, 'r', os.O_RDONLY),
        ('stdout', -11, 'w', os.O_WRONLY),
        ('stderr', -12, 'w', os.O_WRONLY),
    ):
        if getattr(sys, name) is not None:
            continue
        handle = kernel.GetStdHandle(number & 0xffffffff)
        if not handle or handle == ctypes.c_void_p(-1).value:
            raise RuntimeError('Desktop standard pipe is unavailable')
        fd = msvcrt.open_osfhandle(handle, flags)
        setattr(sys, name, os.fdopen(fd, mode, encoding='utf-8', buffering=1))


def read_handshake(stream) -> dict:
    try:
        raw = stream.readline(65537)
        if len(raw) > 65536 or not raw.endswith('\n'):
            raise ValueError
        value = json.loads(raw)
        if not isinstance(value, dict) or value.get('protocol') != 1 or value.get('port') != 8000:
            raise ValueError
        for name in ('instance_id', 'session_token', 'bootstrap_token', 'data_root', 'resource_root'):
            if not isinstance(value.get(name), str) or not value[name] or '\x00' in value[name]:
                raise ValueError
        for name in ('data_root', 'resource_root'):
            if not Path(value[name]).is_absolute():
                raise ValueError
        return value
    except (ValueError, TypeError):
        raise ValueError('Invalid desktop handshake') from None


def validate_resources(resources: Path) -> Path:
    dist = resources / 'frontend' / 'dist'
    if not (dist / 'index.html').is_file():
        raise RuntimeError('Built frontend is missing. Build the desktop payload again.')
    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    for name, option in (('ffmpeg', '-version'), ('ffprobe', '-version'), ('yt-dlp', '--version'), ('deno', '--version')):
        binary = resources / 'bin' / (name + ('.exe' if os.name == 'nt' else ''))
        if not binary.is_file():
            raise RuntimeError(f'Required desktop tool {name} is missing. Repair the installation.')
        try:
            subprocess.run([str(binary), option], stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=10, check=True, creationflags=flags)
        except (OSError, subprocess.SubprocessError):
            raise RuntimeError(f'Required desktop tool {name} failed its startup check.') from None
    return dist


class FrontendHost:
    """Serve compiled assets without changing existing API/media dispatch."""
    def __init__(self, app, directory: Path):
        from starlette.staticfiles import StaticFiles
        self.app = app
        self.directory = directory.resolve()
        self.static = StaticFiles(directory=str(directory), check_dir=True)

    async def __call__(self, scope, receive, send):
        path = scope.get('path', '')
        if scope['type'] != 'http' or any(path == p or path.startswith(p + '/') for p in ('/api', '/media', '/_desktop')) or path in ('/docs', '/redoc', '/openapi.json'):
            return await self.app(scope, receive, send)
        from starlette.exceptions import HTTPException
        from starlette.responses import FileResponse, PlainTextResponse
        try:
            return await self.static(scope, receive, send)
        except HTTPException as exc:
            if exc.status_code == 404 and scope['method'] in ('GET', 'HEAD') and not Path(path).suffix:
                # No traversal and no asset misses silently returning HTML.
                target = (self.directory / path.lstrip('/')).resolve()
                if target.is_relative_to(self.directory):
                    return await FileResponse(self.directory / 'index.html')(scope, receive, send)
            return await PlainTextResponse('Not found' if exc.status_code == 404 else 'Method not allowed', status_code=exc.status_code)(scope, receive, send)


def bind_socket(port: int = 8000) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if os.name == 'nt':
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        sock.bind(('127.0.0.1', port))
        sock.listen(128)
        sock.setblocking(False)
        return sock
    except OSError:
        sock.close()
        raise RuntimeError(f'Local port {port} is already in use or unavailable. Close the other application and Retry.') from None


def watch_control(stream, server) -> None:
    try:
        for line in stream:
            try:
                message = json.loads(line)
            except ValueError:
                continue
            if isinstance(message, dict) and message.get('command') == 'shutdown':
                break
    finally:
        server.should_exit = True


def run_backend() -> int:
    restore_standard_streams()
    try:
        handshake = read_handshake(sys.stdin)
        from desktop.paths import configure_environment
        resources = Path(handshake['resource_root']).resolve()
        writable = Path(handshake['data_root']).resolve()
        configure_environment(resources, writable)
        with bind_socket(handshake['port']) as sock:
            dist = validate_resources(resources)
            sys.path.insert(0, str(resources / 'backend'))
            from app.main import app
            from desktop.security import DesktopSecurity
            import uvicorn
            guarded = DesktopSecurity(FrontendHost(app, dist),
                                      session_token=handshake['session_token'],
                                      bootstrap_token=handshake['bootstrap_token'],
                                      instance_id=handshake['instance_id'], port=handshake['port'])
            config = uvicorn.Config(guarded, host='127.0.0.1', port=handshake['port'],
                                    access_log=False, log_level='info', lifespan='on',
                                    timeout_graceful_shutdown=8)
            server = uvicorn.Server(config)
            threading.Thread(target=watch_control, args=(sys.stdin, server), daemon=True).start()
            server.run(sockets=[sock])
            return 0 if server.started else 1
    except Exception as exc:
        # Do not emit handshake content or exception representations with secrets.
        if isinstance(exc, (RuntimeError, ValueError)):
            print(str(exc), file=sys.stderr)
        else:
            print('Desktop backend startup failed. Inspect application logs.', file=sys.stderr)
        return 1
