"""Authenticated, bounded supervision of the desktop's owned backend tree."""
import http.client
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import secrets
import signal
import socket
import subprocess
import threading
import time
from urllib.parse import urlencode

from desktop.windows_job import WindowsJob


class StartupError(RuntimeError):
    """Retryable startup failure suitable for the native error window."""


class BackendManager:
    STARTUP_TIMEOUT = 90.0
    STOP_TIMEOUT = 10.0
    POLL_INTERVAL = 0.25
    MONITOR_INTERVAL = 0.5

    def __init__(self, command: list[str], resource_root: Path, data_root: Path, port: int = 8000):
        self.command = list(command)
        self.resource_root = Path(resource_root).resolve()
        self.data_root = Path(data_root).resolve()
        self.port = port
        self.log_dir = self.data_root / 'logs'
        self._lock = threading.RLock()
        self._cancel = threading.Event()
        self._process = None
        self._job = None
        self._reader = None
        self._log = None
        self._url = None

    def is_running(self) -> bool:
        process = self._process
        return process is not None and process.poll() is None

    def start(self) -> str:
        with self._lock:
            if self.is_running() and self._url:
                return self._url
            self._cleanup()
            self._cancel.clear()
            self._url = None
            session, bootstrap = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
            instance = secrets.token_hex(16)
            try:
                try:
                    self.log_dir.mkdir(parents=True, exist_ok=True)
                    self._log = RotatingFileHandler(self.log_dir / 'backend.log', maxBytes=5 * 1024 * 1024,
                                                   backupCount=3, encoding='utf-8')
                except OSError as exc:
                    raise StartupError(f'Cannot prepare backend logs at {self.log_dir}') from exc
                options = dict(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, encoding='utf-8', errors='replace', bufsize=1,
                               cwd=str(self.resource_root))
                if os.name == 'nt':
                    self._job = WindowsJob()
                    options['creationflags'] = subprocess.CREATE_NO_WINDOW
                else:
                    options['start_new_session'] = True
                self._process = subprocess.Popen([*self.command, '--desktop-backend'], **options)
                if self._job:
                    self._job.assign(self._process)
                self._reader = threading.Thread(target=self._read_log,
                                                args=(self._process.stdout, self._log, (session, bootstrap)),
                                                daemon=True)
                self._reader.start()
                handshake = dict(protocol=1, instance_id=instance, session_token=session,
                                 bootstrap_token=bootstrap, data_root=str(self.data_root),
                                 resource_root=str(self.resource_root), port=self.port)
                self._process.stdin.write(json.dumps(handshake) + '\n')
                self._process.stdin.flush()
                deadline = time.monotonic() + self.STARTUP_TIMEOUT
                while True:
                    if self._cancel.is_set():
                        raise StartupError('Backend startup cancelled')
                    if not self.is_running():
                        raise StartupError('Backend exited before readiness; view logs and retry (check port 8000).')
                    if time.monotonic() >= deadline:
                        raise StartupError('Backend startup timed out; view logs and retry.')
                    if self._ready(session, instance):
                        if self._cancel.is_set():
                            raise StartupError('Backend startup cancelled')
                        if not self.is_running():
                            raise StartupError('Backend exited before readiness')
                        self._url = f'http://127.0.0.1:{self.port}/_desktop/bootstrap?' + urlencode({'token': bootstrap})
                        return self._url
                    self._cancel.wait(self.POLL_INTERVAL)
            except Exception as exc:
                self._cleanup()
                if isinstance(exc, StartupError):
                    raise
                raise StartupError('Cannot start the owned backend; view logs and retry.') from exc

    def _ready(self, session, instance):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=self.POLL_INTERVAL)
        watchdog = None
        try:
            connection.connect()
            # Socket timeouts alone reset on every byte. Bound the entire exchange,
            # including headers, even if a foreign service dribbles data forever.
            probe_socket = connection.sock
            def expire():
                try:
                    probe_socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
            watchdog = threading.Timer(self.POLL_INTERVAL, expire)
            watchdog.daemon = True
            watchdog.start()
            connection.request('GET', '/_desktop/health', headers={'Authorization': f'Bearer {session}'})
            response = connection.getresponse()
            if response.status != 200:
                return False
            data = json.loads(response.read(4097))
            if not isinstance(data, dict):
                return False
            if data.get('instance_id') != instance:
                raise StartupError(f'Backend identity mismatch on port {self.port}; close the conflicting service and retry.')
            return data.get('protocol') == 1 and data.get('ready') is True
        except (OSError, ValueError, http.client.HTTPException):
            return False
        finally:
            if watchdog:
                watchdog.cancel()
            connection.close()

    @staticmethod
    def _read_log(stream, handler, tokens):
        try:
            for line in stream:
                for token in tokens:
                    line = line.replace(token, '[REDACTED]')
                record = logging.LogRecord('desktop.backend', logging.INFO, '', 0, line.rstrip('\r\n'), (), None)
                handler.emit(record)
        finally:
            stream.close()

    def stop(self) -> None:
        # Cancellation must precede acquiring the lock held by the readiness loop.
        self._cancel.set()
        with self._lock:
            self._cleanup()

    def _cleanup(self):
        process = self._process
        if process:
            if process.stdin:
                try:
                    process.stdin.write('{"command":"shutdown"}\n')
                    process.stdin.flush()
                except (OSError, ValueError):
                    pass
                finally:
                    try:
                        process.stdin.close()
                    except OSError:
                        pass
            try:
                process.wait(timeout=self.STOP_TIMEOUT)
            except subprocess.TimeoutExpired:
                pass
            if self._job:
                self._job.close()
            elif os.name != 'nt':
                # The dedicated group remains owned even when its leader exits first.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            if process.poll() is None:
                process.kill()  # Assignment failure fallback: only our exact child.
            process.wait(timeout=2)
        if self._job:
            self._job.close()
        if self._reader:
            self._reader.join(timeout=2)
        if self._log:
            self._log.close()
        self._process = self._job = self._reader = self._log = self._url = None
