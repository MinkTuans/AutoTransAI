from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock


ROOT_DIR = Path(__file__).resolve().parents[3]


def _load_launcher(monkeypatch):
    webview = SimpleNamespace(create_window=Mock(), start=Mock())
    monkeypatch.setitem(sys.modules, "webview", webview)
    spec = importlib.util.spec_from_file_location(
        "app_launcher_under_test",
        ROOT_DIR / "app_launcher.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module, webview


def test_backend_startup_failure_does_not_open_frontend_or_window(monkeypatch, tmp_path):
    """Catch the desktop app opening a dead frontend when port 8000 never becomes ready."""
    launcher, webview = _load_launcher(monkeypatch)
    backend_process = Mock()
    backend_process.poll.return_value = None
    start_frontend = Mock()
    show_startup_error = Mock()

    monkeypatch.setattr(launcher, "LOG_DIR", tmp_path, raising=False)
    monkeypatch.setattr(launcher, "BACKEND_LOG_PATH", tmp_path / "backend.log", raising=False)
    monkeypatch.setattr(launcher, "FRONTEND_LOG_PATH", tmp_path / "frontend.log", raising=False)
    monkeypatch.setattr(launcher, "start_backend", Mock(return_value=backend_process))
    monkeypatch.setattr(launcher, "start_frontend", start_frontend)
    monkeypatch.setattr(launcher, "wait_for_server", Mock(return_value=False))
    monkeypatch.setattr(launcher, "show_startup_error", show_startup_error, raising=False)
    monkeypatch.setattr(launcher, "kill_process_tree", Mock())
    monkeypatch.setattr(launcher.subprocess, "run", Mock(return_value=SimpleNamespace(stdout="")))

    launcher.main()

    start_frontend.assert_not_called()
    webview.create_window.assert_not_called()
    show_startup_error.assert_called_once()
    assert "backend.log" in show_startup_error.call_args.args[1]


def test_backend_process_logs_output_and_does_not_use_reloader(monkeypatch, tmp_path):
    """Catch hidden backend failures and the extra Windows reload child process."""
    launcher, _ = _load_launcher(monkeypatch)
    popen = Mock(return_value=Mock())
    monkeypatch.setattr(launcher.subprocess, "Popen", popen)

    with (tmp_path / "backend.log").open("a", encoding="utf-8") as log_stream:
        launcher.start_backend(log_stream)

    args = popen.call_args.args[0]
    assert "--reload" not in args
    assert popen.call_args.kwargs["stdout"] is log_stream
    assert popen.call_args.kwargs["stderr"] is log_stream


def test_frontend_startup_failure_does_not_open_window(monkeypatch, tmp_path):
    """Catch the desktop window opening when Vite never becomes reachable."""
    launcher, webview = _load_launcher(monkeypatch)
    backend_process = Mock()
    backend_process.poll.return_value = None
    frontend_process = Mock()
    frontend_process.poll.return_value = None
    show_startup_error = Mock()

    monkeypatch.setattr(launcher, "LOG_DIR", tmp_path, raising=False)
    monkeypatch.setattr(launcher, "BACKEND_LOG_PATH", tmp_path / "backend.log", raising=False)
    monkeypatch.setattr(launcher, "FRONTEND_LOG_PATH", tmp_path / "frontend.log", raising=False)
    monkeypatch.setattr(launcher, "is_server_running", Mock(return_value=False), raising=False)
    monkeypatch.setattr(launcher, "start_backend", Mock(return_value=backend_process))
    monkeypatch.setattr(launcher, "start_frontend", Mock(return_value=frontend_process))
    monkeypatch.setattr(launcher, "wait_for_server", Mock(side_effect=[True, False]))
    monkeypatch.setattr(launcher, "show_startup_error", show_startup_error, raising=False)
    monkeypatch.setattr(launcher, "kill_process_tree", Mock())
    monkeypatch.setattr(launcher.subprocess, "run", Mock(return_value=SimpleNamespace(stdout="")))

    launcher.main()

    webview.create_window.assert_not_called()
    show_startup_error.assert_called_once()
    assert "frontend.log" in show_startup_error.call_args.args[1]


def test_backend_spawn_error_is_logged_and_shown(monkeypatch, tmp_path):
    """Catch pythonw swallowing errors such as a missing backend interpreter."""
    launcher, webview = _load_launcher(monkeypatch)
    show_startup_error = Mock()

    monkeypatch.setattr(launcher, "LOG_DIR", tmp_path)
    monkeypatch.setattr(launcher, "BACKEND_LOG_PATH", tmp_path / "backend.log")
    monkeypatch.setattr(launcher, "FRONTEND_LOG_PATH", tmp_path / "frontend.log")
    monkeypatch.setattr(launcher, "is_server_running", Mock(return_value=False), raising=False)
    monkeypatch.setattr(launcher, "start_backend", Mock(side_effect=OSError("python missing")))
    monkeypatch.setattr(launcher, "show_startup_error", show_startup_error)
    monkeypatch.setattr(launcher.subprocess, "run", Mock(return_value=SimpleNamespace(stdout="")))

    launcher.main()

    webview.create_window.assert_not_called()
    show_startup_error.assert_called_once()
    assert "python missing" in (tmp_path / "backend.log").read_text(encoding="utf-8")


def test_existing_backend_port_is_refused_without_killing_unowned_process(monkeypatch, tmp_path):
    """Catch a stale server being mistaken for the backend spawned by this launcher."""
    launcher, webview = _load_launcher(monkeypatch)
    start_backend = Mock()
    kill_process_tree = Mock()
    show_startup_error = Mock()

    monkeypatch.setattr(launcher, "LOG_DIR", tmp_path)
    monkeypatch.setattr(launcher, "BACKEND_LOG_PATH", tmp_path / "backend.log")
    monkeypatch.setattr(launcher, "FRONTEND_LOG_PATH", tmp_path / "frontend.log")
    monkeypatch.setattr(launcher, "is_server_running", Mock(return_value=True), raising=False)
    monkeypatch.setattr(launcher, "start_backend", start_backend)
    monkeypatch.setattr(launcher, "wait_for_server", Mock(return_value=False))
    monkeypatch.setattr(launcher, "show_startup_error", show_startup_error)
    monkeypatch.setattr(launcher, "kill_process_tree", kill_process_tree)

    launcher.main()

    start_backend.assert_not_called()
    webview.create_window.assert_not_called()
    kill_process_tree.assert_not_called()
    show_startup_error.assert_called_once()


def test_readiness_fails_immediately_when_spawned_process_exits(monkeypatch):
    """Catch a dead child being hidden by an unrelated HTTP 200 on the same port."""
    launcher, _ = _load_launcher(monkeypatch)
    process = Mock()
    process.poll.return_value = 1
    urlopen = Mock()
    sleep = Mock()
    monkeypatch.setattr(launcher.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(launcher.time, "sleep", sleep)

    ready = launcher.wait_for_server("http://127.0.0.1:8000/health", process, max_retries=30)

    assert ready is False
    urlopen.assert_not_called()
    sleep.assert_not_called()


def test_log_directory_failure_is_visible_under_pythonw(monkeypatch):
    """Catch ACL/disk failures escaping without a Windows-visible diagnostic."""
    launcher, webview = _load_launcher(monkeypatch)
    log_dir = Mock()
    log_dir.mkdir.side_effect = OSError("access denied")
    show_startup_error = Mock()
    monkeypatch.setattr(launcher, "LOG_DIR", log_dir)
    monkeypatch.setattr(launcher, "show_startup_error", show_startup_error)

    launcher.main()

    webview.create_window.assert_not_called()
    show_startup_error.assert_called_once()
    assert "access denied" in show_startup_error.call_args.args[1]


def test_backend_is_rechecked_after_frontend_becomes_ready(monkeypatch, tmp_path):
    """Catch the backend dying while Vite starts but before pywebview opens."""
    launcher, webview = _load_launcher(monkeypatch)
    backend_process = Mock()
    backend_process.poll.return_value = None
    frontend_process = Mock()
    frontend_process.poll.return_value = None
    is_server_running = Mock(side_effect=[False, False, False])
    kill_process_tree = Mock()
    show_startup_error = Mock()

    monkeypatch.setattr(launcher, "LOG_DIR", tmp_path)
    monkeypatch.setattr(launcher, "BACKEND_LOG_PATH", tmp_path / "backend.log")
    monkeypatch.setattr(launcher, "FRONTEND_LOG_PATH", tmp_path / "frontend.log")
    monkeypatch.setattr(launcher, "is_server_running", is_server_running)
    monkeypatch.setattr(launcher, "start_backend", Mock(return_value=backend_process))
    monkeypatch.setattr(launcher, "start_frontend", Mock(return_value=frontend_process))
    monkeypatch.setattr(launcher, "wait_for_server", Mock(side_effect=[True, True]))
    monkeypatch.setattr(launcher, "kill_process_tree", kill_process_tree)
    monkeypatch.setattr(launcher, "show_startup_error", show_startup_error)

    launcher.main()

    webview.create_window.assert_not_called()
    assert is_server_running.call_count == 3
    assert kill_process_tree.call_count >= 1
    show_startup_error.assert_called_once()
    assert "backend.log" in show_startup_error.call_args.args[1]


def test_frontend_spawn_error_stops_backend_before_showing_dialog(monkeypatch, tmp_path):
    """Catch a blocking error dialog leaving the healthy backend running indefinitely."""
    launcher, webview = _load_launcher(monkeypatch)
    backend_process = Mock()
    backend_process.poll.return_value = None
    events = []

    monkeypatch.setattr(launcher, "LOG_DIR", tmp_path)
    monkeypatch.setattr(launcher, "BACKEND_LOG_PATH", tmp_path / "backend.log")
    monkeypatch.setattr(launcher, "FRONTEND_LOG_PATH", tmp_path / "frontend.log")
    monkeypatch.setattr(launcher, "is_server_running", Mock(side_effect=[False, False]))
    monkeypatch.setattr(launcher, "start_backend", Mock(return_value=backend_process))
    monkeypatch.setattr(launcher, "wait_for_server", Mock(return_value=True))
    monkeypatch.setattr(launcher, "start_frontend", Mock(side_effect=OSError("npm missing")))
    monkeypatch.setattr(launcher, "kill_process_tree", lambda _pid: events.append("kill"))
    monkeypatch.setattr(
        launcher,
        "show_startup_error",
        lambda _component, _detail: events.append("show"),
    )

    launcher.main()

    webview.create_window.assert_not_called()
    assert events[:2] == ["kill", "show"]
