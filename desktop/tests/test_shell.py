import threading
import time
from types import SimpleNamespace

import pytest

from desktop.shell import DesktopShell, navigation_allowed, SingleInstance


class Event:
    def __init__(self):
        self.callbacks = []

    def __iadd__(self, callback):
        self.callbacks.append(callback)
        return self

    def fire(self, *args):
        for callback in self.callbacks:
            callback(*args)


class Window:
    def __init__(self):
        self.events = SimpleNamespace(before_show=Event(), closed=Event())
        self.native = SimpleNamespace(webview=SimpleNamespace(NavigationStarting=Event()))
        self.html = []
        self.urls = []
        self.destroyed = 0

    def load_html(self, value):
        self.html.append(value)

    def load_url(self, value):
        self.urls.append(value)

    def destroy(self):
        self.destroyed += 1


class Manager:
    def __init__(self, result='http://127.0.0.1:8000/_desktop/bootstrap?token=test'):
        self.result = result
        self.starts = 0
        self.stops = 0
        self.running = True
        self.block = None
        self.log_dir = '/known/logs'
        self.port = 8000

    def start(self):
        self.starts += 1
        if self.block:
            self.block.wait()
        if isinstance(self.result, Exception):
            raise self.result
        return self.result

    def stop(self):
        self.stops += 1
        self.running = False

    def is_running(self):
        return self.running


def settle(shell):
    shell._worker.join(timeout=2)
    assert not shell._worker.is_alive()


def test_loading_stays_local_until_backend_ready():
    window, manager = Window(), Manager()
    manager.block = threading.Event()
    shell = DesktopShell(manager, window, open_logs=lambda path: None)
    shell.on_before_show()
    assert not window.urls
    manager.block.set()
    settle(shell)
    assert window.urls == [manager.result]


def test_startup_failure_is_visible_and_retry_serialized():
    window, manager = Window(), Manager(RuntimeError('Port busy'))
    shell = DesktopShell(manager, window, open_logs=lambda path: None)
    shell.on_before_show()
    settle(shell)
    assert not window.urls
    assert 'Port busy' in window.html[-1]
    manager.result = 'http://127.0.0.1:8000/_desktop/bootstrap?token=second'
    manager.block = threading.Event()
    shell.retry()
    shell.retry()
    assert manager.starts == 2
    manager.block.set()
    settle(shell)
    assert window.urls == [manager.result]


def test_close_during_startup_prevents_navigation_and_stops_once():
    window, manager = Window(), Manager()
    manager.block = threading.Event()
    shell = DesktopShell(manager, window, open_logs=lambda path: None)
    shell.on_before_show()
    closer = threading.Thread(target=shell.close)
    closer.start()
    manager.block.set()
    closer.join(timeout=2)
    assert not closer.is_alive()
    settle(shell)
    shell.close()
    assert manager.stops == 1
    assert window.urls == []


def test_runtime_exit_shows_failure_and_view_logs_uses_fixed_path():
    window, manager, opened = Window(), Manager(), []
    shell = DesktopShell(manager, window, open_logs=opened.append)
    shell.on_before_show()
    settle(shell)
    manager.running = False
    shell.monitor_once()
    shell.view_logs()
    assert 'stopped' in window.html[-1].lower()
    assert opened == ['/known/logs']


def test_navigation_guard_blocks_remote_and_popups():
    assert navigation_allowed('about:blank', 8000)
    assert navigation_allowed('http://127.0.0.1:8000/projects?x=1', 8000)
    for url in ['https://example.org/', 'http://localhost:8000/',
                'http://127.0.0.1:8001/', 'file:///C:/secret',
                'http://127.0.0.1:8000.evil.test/']:
        assert not navigation_allowed(url, 8000)
    window, manager = Window(), Manager()
    shell = DesktopShell(manager, window, open_logs=lambda path: None)
    shell.on_before_show()
    settle(shell)
    args = SimpleNamespace(Uri='https://example.org/', Cancel=False)
    window.native.webview.NavigationStarting.fire(None, args)
    assert args.Cancel is True


def test_duplicate_instance_does_not_acquire_mutex(monkeypatch, tmp_path):
    # Windows API is isolated at the syscall boundary; the shell owns handle lifecycle.
    monkeypatch.setattr('desktop.shell._create_mutex', lambda name: (123, True))
    monkeypatch.setattr('desktop.shell._close_handle', lambda handle: None)
    instance = SingleInstance(tmp_path)
    assert instance.acquire() is False
    assert instance.handle is None


def test_backend_flag_dispatches_without_importing_shell(monkeypatch):
    import sys
    from desktop import __main__

    called = []
    monkeypatch.setitem(sys.modules, 'desktop.backend', SimpleNamespace(run_backend=lambda: called.append('backend') or 7))
    monkeypatch.delitem(sys.modules, 'desktop.shell', raising=False)
    assert __main__.main(['--desktop-backend']) == 7
    assert called == ['backend']
    assert 'desktop.shell' not in sys.modules


def test_mutex_handle_is_released_idempotently(monkeypatch, tmp_path):
    closed = []
    monkeypatch.setattr('desktop.shell._create_mutex', lambda name: (456, False))
    monkeypatch.setattr('desktop.shell._close_handle', closed.append)
    instance = SingleInstance(tmp_path)
    assert instance.acquire()
    instance.release()
    instance.release()
    assert closed == [456]


def test_failed_navigation_guard_cannot_retry_backend():
    window, manager = Window(), Manager()
    window.native.webview = None
    shell = DesktopShell(manager, window, open_logs=lambda path: None)
    shell.on_before_show()
    for _ in range(50):
        if shell._failed:
            break
        time.sleep(0.01)
    shell.retry()
    assert manager.starts == 0
    assert window.urls == []


def test_gui_close_callback_does_not_deadlock_navigation():
    window, manager = Window(), Manager()
    shell = DesktopShell(manager, window, open_logs=lambda path: None)

    def gui_navigation(url):
        callback = threading.Thread(target=shell.close)
        callback.start()
        callback.join(timeout=1)
        assert not callback.is_alive(), 'GUI close was blocked by shell state lock'
        window.urls.append(url)

    window.load_url = gui_navigation
    shell.on_before_show()
    settle(shell)
    assert manager.stops == 1


def test_gui_close_callback_does_not_deadlock_error_render():
    window, manager = Window(), Manager(RuntimeError('failed'))
    shell = DesktopShell(manager, window, open_logs=lambda path: None)

    def gui_error(html):
        callback = threading.Thread(target=shell.close)
        callback.start()
        callback.join(timeout=1)
        assert not callback.is_alive(), 'GUI close was blocked by shell state lock'
        window.html.append(html)

    window.load_html = gui_error
    shell.on_before_show()
    settle(shell)
    assert manager.stops == 1


def test_pre_window_data_failure_is_visible(monkeypatch):
    import desktop.shell as shell_module

    seen = []
    monkeypatch.setattr(shell_module, 'os', SimpleNamespace(name='nt'))
    monkeypatch.setattr(shell_module, 'data_root', lambda: (_ for _ in ()).throw(RuntimeError('profile unavailable')))
    monkeypatch.setattr(shell_module, '_message_box', seen.append)
    assert shell_module.run_shell() == 1
    assert len(seen) == 1 and 'profile unavailable' in seen[0]


def test_crashed_backend_cleans_owned_descendant_before_error_and_retry(tmp_path):
    import socket
    import sys
    from desktop.process_manager import BackendManager
    from desktop.tests.test_process_manager import FAKE

    script = tmp_path / 'fake.py'
    script.write_text(FAKE)
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    manager = BackendManager([sys.executable, str(script), 'tree'], tmp_path,
                             tmp_path / 'data', port)
    manager.STARTUP_TIMEOUT = 2
    manager.STOP_TIMEOUT = .3
    manager.POLL_INTERVAL = .025
    window = Window()
    shell = DesktopShell(manager, window, open_logs=lambda path: None)
    try:
        shell.on_before_show()
        shell._worker.join(timeout=3)
        assert not shell._worker.is_alive() and shell._started
        heartbeat = manager.data_root / 'heartbeat'
        deadline = time.monotonic() + 2
        while not heartbeat.exists() and time.monotonic() < deadline:
            time.sleep(.02)
        assert heartbeat.exists()
        manager._process.kill()
        manager._process.wait(timeout=2)
        shell.monitor_once()
        snapshot = heartbeat.read_text()
        time.sleep(.15)
        assert heartbeat.read_text() == snapshot
        assert shell._failed and 'stopped' in window.html[-1].lower()
        assert manager._process is None
    finally:
        shell.close()


def test_crash_waits_for_cleanup_before_showing_retry():
    window, manager = Window(), Manager()
    shell = DesktopShell(manager, window, open_logs=lambda path: None)
    shell.on_before_show()
    settle(shell)
    manager.running = False
    entered, release = threading.Event(), threading.Event()
    original_stop = manager.stop

    def slow_stop():
        entered.set()
        release.wait(timeout=2)
        original_stop()

    manager.stop = slow_stop
    watcher = threading.Thread(target=shell.monitor_once)
    watcher.start()
    assert entered.wait(timeout=1)
    shell.retry()
    assert manager.starts == 1
    assert not window.html
    release.set()
    watcher.join(timeout=2)
    assert not watcher.is_alive()
    assert shell._failed and 'stopped' in window.html[-1].lower()
