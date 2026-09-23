"""Public media routes must never serve local application credentials."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.routes import storage as storage_routes
from app.config import Settings
from app.main import app
from app.services import storage_service


def test_credentials_directory_cannot_be_inside_public_storage(tmp_path):
    with pytest.raises(ValueError, match="DATA_DIR must be outside STORAGE_ROOT"):
        Settings(DATA_DIR=tmp_path / "storage" / "data", STORAGE_ROOT=tmp_path / "storage")


@pytest.fixture
def media_roots(tmp_path: Path, monkeypatch):
    data_dir = tmp_path / "data"
    storage_dir = tmp_path / "storage"
    data_dir.mkdir()
    storage_dir.mkdir()

    monkeypatch.setattr(storage_routes.settings, "DATA_DIR", data_dir)
    monkeypatch.setattr(storage_routes.settings, "STORAGE_ROOT", storage_dir)
    monkeypatch.setattr(storage_service.settings, "STORAGE_ROOT", storage_dir)

    media_mount = next(route for route in app.routes if getattr(route, "name", None) == "media")
    monkeypatch.setattr(media_mount.app, "directory", str(data_dir))
    monkeypatch.setattr(media_mount.app, "all_directories", [str(data_dir)])
    if hasattr(media_mount.app, "storage_root"):
        monkeypatch.setattr(media_mount.app, "storage_root", storage_dir)

    return data_dir, storage_dir


@pytest.mark.parametrize("secret_name", ["api_keys.json", "workflow.db", ".encryption_key", "job.log"])
@pytest.mark.parametrize("prefix", ["", "translator/jobs/sample/"])
def test_media_rejects_private_files(media_roots, secret_name, prefix):
    data_dir, _ = media_roots
    secret = data_dir / prefix / secret_name
    secret.parent.mkdir(parents=True, exist_ok=True)
    secret.write_bytes(b"fake-private-content")

    response = TestClient(app).get(f"/media/{prefix}{secret_name}")

    assert response.status_code == 404


@pytest.mark.parametrize("route", ["files", "download"])
@pytest.mark.parametrize("secret_name", ["api_keys.json", "workflow.db", ".encryption_key", "job.log"])
@pytest.mark.parametrize("prefix", ["", "translator/jobs/sample/"])
def test_storage_routes_reject_private_files(media_roots, route, secret_name, prefix):
    data_dir, _ = media_roots
    secret = data_dir / prefix / secret_name
    secret.parent.mkdir(parents=True, exist_ok=True)
    secret.write_bytes(b"fake-private-content")
    path = f"{prefix}{secret_name}"

    client = TestClient(app)
    response = client.get(f"/api/storage/files/{path}" if route == "files" else "/api/storage/download", params=None if route == "files" else {"path": path})

    assert response.status_code == 404


@pytest.mark.parametrize("route", ["media", "files", "download"])
@pytest.mark.parametrize("secret_name", ["api_keys.json", "workflow.db", ".encryption_key", "job.log"])
def test_storage_root_rejects_private_files(media_roots, route, secret_name):
    _, storage_dir = media_roots
    path = f"projects/sample/{secret_name}"
    secret = storage_dir / path
    secret.parent.mkdir(parents=True, exist_ok=True)
    secret.write_bytes(b"fake-private-content")

    client = TestClient(app)
    if route == "media":
        response = client.get(f"/media/{path}")
    elif route == "files":
        response = client.get(f"/api/storage/files/{path}")
    else:
        response = client.get("/api/storage/download", params={"path": path})

    assert response.status_code == 404


@pytest.mark.parametrize("route", ["media", "files", "download"])
@pytest.mark.parametrize("root", ["storage", "legacy"])
def test_media_routes_serve_video_from_valid_roots(media_roots, route, root):
    data_dir, storage_dir = media_roots
    root_dir = storage_dir if root == "storage" else data_dir
    path = "translator/jobs/sample/final_dubbed_video.mp4"
    video = root_dir / path
    video.parent.mkdir(parents=True, exist_ok=True)
    video.write_bytes(b"fake-video-content")

    client = TestClient(app)
    if route == "media":
        response = client.get(f"/media/{path}")
    elif route == "files":
        response = client.get(f"/api/storage/files/{path}")
    else:
        response = client.get("/api/storage/download", params={"path": path, "filename": "dubbed.mp4"})

    assert response.status_code == 200
    assert response.content == b"fake-video-content"


@pytest.mark.parametrize("suffix", [".flv", ".ts", ".3gp"])
@pytest.mark.parametrize("route", ["media", "files", "download"])
def test_media_routes_serve_accepted_video_formats(media_roots, route, suffix):
    _, storage_dir = media_roots
    path = f"merger/uploads/source{suffix}"
    video = storage_dir / path
    video.parent.mkdir(parents=True, exist_ok=True)
    video.write_bytes(b"accepted-video-format")

    client = TestClient(app)
    if route == "media":
        response = client.get(f"/media/{path}")
    elif route == "files":
        response = client.get(f"/api/storage/files/{path}")
    else:
        response = client.get("/api/storage/download", params={"path": path})

    assert response.status_code == 200
    assert response.content == b"accepted-video-format"


@pytest.mark.parametrize("route", ["media", "files", "download"])
def test_nested_storage_root_serves_media_without_exposing_data_root(media_roots, monkeypatch, route):
    data_dir, _ = media_roots
    nested_storage = data_dir / "storage"
    nested_storage.mkdir()
    Settings(DATA_DIR=data_dir, STORAGE_ROOT=nested_storage)
    monkeypatch.setattr(storage_routes.settings, "STORAGE_ROOT", nested_storage)
    monkeypatch.setattr(storage_service.settings, "STORAGE_ROOT", nested_storage)
    media_mount = next(route_item for route_item in app.routes if getattr(route_item, "name", None) == "media")
    monkeypatch.setattr(media_mount.app, "storage_root", nested_storage)

    path = "projects/sample/video.mp4"
    video = nested_storage / path
    video.parent.mkdir(parents=True, exist_ok=True)
    video.write_bytes(b"nested-storage-video")
    (data_dir / "private.mp4").write_bytes(b"private-root-file")
    (data_dir / "api_keys.json").write_bytes(b"fake-private-content")

    client = TestClient(app)
    if route == "media":
        public = client.get(f"/media/{path}")
        private_media = client.get("/media/private.mp4")
        private_keys = client.get("/media/api_keys.json")
    elif route == "files":
        public = client.get(f"/api/storage/files/{path}")
        private_media = client.get("/api/storage/files/private.mp4")
        private_keys = client.get("/api/storage/files/api_keys.json")
    else:
        public = client.get("/api/storage/download", params={"path": path})
        private_media = client.get("/api/storage/download", params={"path": "private.mp4"})
        private_keys = client.get("/api/storage/download", params={"path": "api_keys.json"})

    assert public.status_code == 200
    assert public.content == b"nested-storage-video"
    assert private_media.status_code == 404
    assert private_keys.status_code == 404


@pytest.mark.parametrize("route", ["media", "files", "download"])
def test_media_routes_reject_data_root_media(media_roots, route):
    data_dir, _ = media_roots
    (data_dir / "private.mp4").write_bytes(b"fake-private-video")

    client = TestClient(app)
    if route == "media":
        response = client.get("/media/private.mp4")
    elif route == "files":
        response = client.get("/api/storage/files/private.mp4")
    else:
        response = client.get("/api/storage/download", params={"path": "private.mp4"})

    assert response.status_code == 404


@pytest.mark.parametrize("route", ["media", "files", "download"])
def test_media_routes_reject_symlink_outside_media_roots(media_roots, route):
    data_dir, storage_dir = media_roots
    private = data_dir.parent / "private-video.mp4"
    private.write_bytes(b"fake-private-video")
    link = storage_dir / "projects" / "sample" / "video.mp4"
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(private)
    path = "projects/sample/video.mp4"

    client = TestClient(app)
    if route == "media":
        response = client.get(f"/media/{path}")
    elif route == "files":
        response = client.get(f"/api/storage/files/{path}")
    else:
        response = client.get("/api/storage/download", params={"path": path})

    assert response.status_code == 404


@pytest.mark.parametrize("route", ["media", "files", "download"])
def test_media_routes_reject_symlink_loop(media_roots, route):
    _, storage_dir = media_roots
    path = "projects/sample/loop.mp4"
    link = storage_dir / path
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(link)

    client = TestClient(app, raise_server_exceptions=False)
    if route == "media":
        response = client.get(f"/media/{path}")
    elif route == "files":
        response = client.get(f"/api/storage/files/{path}")
    else:
        response = client.get("/api/storage/download", params={"path": path})

    assert response.status_code == 404
