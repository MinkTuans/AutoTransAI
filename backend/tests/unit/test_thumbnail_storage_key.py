from app.services.thumbnail_service import thumbnail_object_key


def test_job_thumbnail_is_kept_outside_disposable_workspace():
    key = thumbnail_object_key(None, "job-1", None, 123, "thumb-1", ".png")
    assert key == "projects/job-1/thumbnails/thumbnail_123_thumb-1.png"


def test_project_and_asset_thumbnail_paths_keep_existing_contract():
    assert thumbnail_object_key("project-1", "job-1", "asset-1", 123, "thumb-1", ".png") == (
        "projects/project-1/thumbnails/thumbnail_123_thumb-1.png")
    assert thumbnail_object_key(None, None, "asset-1", 123, "thumb-1", ".png") == (
        "translator/assets/asset-1/thumbnails/thumbnail_123_thumb-1.png")
