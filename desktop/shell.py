"""Windows WebView2 shell for the owned, authenticated desktop backend."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import hashlib
import html
import os
from pathlib import Path
import sys
import threading
from urllib.parse import urlsplit

from desktop.paths import data_root, resource_root
from desktop.process_manager import BackendManager

_TITLE = 'AutoTransAI Studio'
_APP_ID = 'AutoTransAI.Studio.Desktop'


def navigation_allowed(uri: str, port: int = 8000) -> bool:
    """Allow only the loading document and our exact internal HTTP origin."""
    if uri == 'about:blank':
        return True
    try:
        parsed = urlsplit(uri)
        return (parsed.scheme == 'http' and parsed.hostname == '127.0.0.1'
                and parsed.port == port and parsed.username is None
                and parsed.password is None)
    except ValueError:
        return False


def _page(title: str, message: str) -> str:
    # This document never contains a privileged script or link. Actions live in
    # the native menu so backend/remote HTML cannot call process operations.
    return ("<!doctype html><html><head><meta charset='utf-8'>"
            "<meta http-equiv='Content-Security-Policy' content=\"default-src 'none'; style-src 'unsafe-inline'\">"
            "<style>body{font:16px Segoe UI,Arial,sans-serif;background:#171923;color:#f7f7fa;"
            "padding:55px;line-height:1.6}h1{font-size:26px}p{max-width:720px}"
            "</style></head><body><h1>" + html.escape(title) + "</h1><p>"
            + html.escape(message) + "</p><p>Use the App menu for Retry, View Logs, or Close."
            "</p></body></html>")


def _create_mutex(name: str) -> tuple[int, bool]:
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    create = kernel.CreateMutexW
    create.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR)
    create.restype = wintypes.HANDLE
    handle = create(None, False, name)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    return handle, ctypes.get_last_error() == 183  # ERROR_ALREADY_EXISTS


def _close_handle(handle: int) -> None:
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    close = kernel.CloseHandle
    close.argtypes = (wintypes.HANDLE,)
    close.restype = wintypes.BOOL
    if not close(handle):
        raise ctypes.WinError(ctypes.get_last_error())


class SingleInstance:
    def __init__(self, writable: Path):
        # Global namespace spans Windows login sessions; the private data root
        # distinguishes users without exposing usernames in the mutex name.
        digest = hashlib.sha256(str(Path(writable).resolve()).lower().encode('utf-8')).hexdigest()[:24]
        self.name = 'Global\\AutoTransAI.Desktop.' + digest
        self.handle = None

    def acquire(self) -> bool:
        if self.handle is not None:
            return True
        handle, exists = _create_mutex(self.name)
        if exists:
            _close_handle(handle)
            return False
        self.handle = handle
        return True

    def release(self) -> None:
        if self.handle is not None:
            handle, self.handle = self.handle, None
            _close_handle(handle)


def _open_logs(path: Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)
    os.startfile(str(path))


class DesktopShell:
    def __init__(self, manager: BackendManager, window, open_logs=_open_logs):
        self.manager = manager
        self.window = window
        self.open_logs = open_logs
        self._closed = threading.Event()
        self._stopped = threading.Event()
        self._lock = threading.RLock()
        self._worker = None
        self._monitor = None
        self._guard = None
        self._started = False
        self._failed = False
        self._reaping = False
        self._cleanup_failed = False

    def on_before_show(self, *_):
        try:
            if os.name == 'nt':
                from webview.platforms import winforms
                if winforms.renderer != 'edgechromium':
                    raise RuntimeError('Microsoft Edge WebView2 Runtime is required.')
            native = self.window.native
            control = native.webview
            if control is None or not hasattr(control, 'NavigationStarting'):
                raise RuntimeError('WebView2 navigation protection is unavailable.')

            def guard(sender, args):
                if not navigation_allowed(str(args.Uri), self.manager.port):
                    args.Cancel = True

            # Keep the Python delegate alive for the whole window lifetime.
            self._guard = guard
            control.NavigationStarting += guard
        except Exception as exc:
            message = f'Cannot initialize secure WebView2: {exc}'
            if os.name == 'nt':
                _message_box(message)
            threading.Thread(target=self._show_error, args=(message,), daemon=True).start()
            return
        self._start_async()

    def _start_async(self):
        with self._lock:
            if self._closed.is_set() or self._guard is None or (self._worker and self._worker.is_alive()):
                return
            self._failed = False
            self._worker = threading.Thread(target=self._start_backend, daemon=True)
            self._worker.start()

    def _start_backend(self):
        try:
            url = self.manager.start()
            if not navigation_allowed(url, self.manager.port):
                raise RuntimeError('Backend returned an invalid desktop URL.')
            if self._closed.is_set():
                return
            self.window.load_url(url)
            with self._lock:
                if self._closed.is_set():
                    return
                self._started = True
                self._monitor = threading.Thread(target=self._monitor_loop, daemon=True)
                self._monitor.start()
        except Exception as exc:
            if not self._closed.is_set():
                self._show_error(str(exc))

    def retry(self):
        with self._lock:
            if (self._closed.is_set() or self._guard is None or not self._failed
                    or self._reaping or self._cleanup_failed
                    or (self._worker and self._worker.is_alive())):
                return
            self._started = False
            self._failed = False
        if self._closed.is_set():
            return
        self.window.load_html(_page('Starting AutoTransAI', 'Retrying backend startup…'))
        self._start_async()

    def view_logs(self):
        self.open_logs(self.manager.log_dir)

    def monitor_once(self):
        with self._lock:
            failed = self._started and not self._closed.is_set() and not self.manager.is_running()
            if failed:
                self._started = False
                self._reaping = True
        if not failed:
            return
        # A dead leader can leave media descendants in the owned Job Object or
        # POSIX process group. Reap the whole group before exposing Retry.
        try:
            self.manager.stop()
        except Exception as exc:
            with self._lock:
                self._cleanup_failed = True
            self._show_error(f'The backend stopped and cleanup failed: {exc}. Close the app and view logs.')
        else:
            self._show_error('The backend stopped unexpectedly. View Logs or Retry.')
        finally:
            with self._lock:
                self._reaping = False

    def _monitor_loop(self):
        while not self._closed.wait(0.5):
            self.monitor_once()
            if not self._started:
                return

    def _show_error(self, message: str):
        with self._lock:
            if self._closed.is_set():
                return
            self._failed = True
        self.window.load_html(_page('AutoTransAI could not continue', message))

    def close(self, *_):
        with self._lock:
            first = not self._closed.is_set()
            if first:
                self._closed.set()
        if first:
            try:
                # BackendManager.cancel precedes its start lock, so closing
                # during readiness interrupts startup and cannot publish a late URL.
                self.manager.stop()
            finally:
                self._stopped.set()
        else:
            self._stopped.wait()


def _message_box(message: str) -> None:
    ctypes.windll.user32.MessageBoxW(None, message, _TITLE, 0x10)


def _set_app_id() -> None:
    shell = ctypes.WinDLL('shell32', use_last_error=True)
    set_id = shell.SetCurrentProcessExplicitAppUserModelID
    set_id.argtypes = (wintypes.LPCWSTR,)
    set_id.restype = ctypes.c_long
    result = set_id(_APP_ID)
    if result != 0:
        raise OSError(f'Cannot set desktop taskbar identity (HRESULT 0x{result & 0xffffffff:08x}).')


def run_shell() -> int:
    if os.name != 'nt':
        raise RuntimeError('The desktop shell requires Windows and WebView2.')
    instance = None
    manager = None
    try:
        writable = data_root()
        instance = SingleInstance(writable)
        if not instance.acquire():
            _message_box('AutoTransAI Studio is already running for this user.')
            return 0
        try:
            import webview
            from webview.menu import Menu, MenuAction
        except Exception as exc:
            _message_box(f'Cannot load the desktop window: {exc}')
            return 1
        _set_app_id()
        webview.settings['OPEN_EXTERNAL_LINKS_IN_BROWSER'] = False
        webview.settings['ALLOW_DOWNLOADS'] = True
        webview.settings['ALLOW_FILE_URLS'] = False
        resources = resource_root()
        command = [sys.executable] if getattr(sys, 'frozen', False) else [sys.executable, '-m', 'desktop']
        manager = BackendManager(command, resources, writable)
        window = webview.create_window(_TITLE, html=_page('Starting AutoTransAI', 'Preparing desktop window…'),
                                       width=1280, height=800, min_size=(800, 600), resizable=True,
                                       background_color='#171923')
        shell = DesktopShell(manager, window)
        window.events.before_show += shell.on_before_show
        window.events.closed += shell.close
        menu = [Menu('App', [MenuAction('Retry', shell.retry),
                             MenuAction('View Logs', shell.view_logs),
                             MenuAction('Close', window.destroy)])]
        icon = resources / 'frontend' / 'public' / 'app-logo.ico'
        try:
            webview.start(gui='edgechromium', menu=menu, icon=str(icon),
                          storage_path=str(writable / 'webview'))
        finally:
            shell.close()
        return 0
    except Exception as exc:
        _message_box(f'AutoTransAI desktop startup failed: {exc}')
        if manager is not None:
            manager.stop()
        return 1
    finally:
        if instance is not None:
            instance.release()
