import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_list_projects():
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    projects = data["data"]
    print("API /api/projects count:", len(projects))
    job_ids = [p["id"] for p in projects]
    assert "VT-9B1B32" in job_ids
    print("✓ VT-9B1B32 present in /api/projects response!")

def test_api_create_and_batch_delete():
    # 1. Create standard project
    res = client.post("/api/projects", json={
        "title": "Batch Delete Test Project 1",
        "script": "[00:00] First segment test.\n[00:05] Second segment test.",
        "workflow_mode": "audio_only"
    })
    assert res.status_code == 200
    p1_id = res.json()["data"]["project_id"]
    print(f"Created test project: {p1_id}")

    # 2. Verify list contains p1_id and VT-9B1B32
    list_res = client.get("/api/projects").json()
    all_ids = [p["id"] for p in list_res["data"]]
    assert p1_id in all_ids
    assert "VT-9B1B32" in all_ids

    # 3. Batch delete p1_id
    del_res = client.post("/api/projects/batch-delete", json={"ids": [p1_id]})
    assert del_res.status_code == 200
    assert p1_id in del_res.json()["data"]["deleted"]
    print(f"Batch deleted project: {p1_id}")

    # 4. Verify p1_id is removed and VT-9B1B32 is still present
    list_res2 = client.get("/api/projects").json()
    all_ids2 = [p["id"] for p in list_res2["data"]]
    assert p1_id not in all_ids2
    assert "VT-9B1B32" in all_ids2
    print("✓ Batch delete verified, VT-9B1B32 unharmed!")

if __name__ == "__main__":
    test_api_list_projects()
    test_api_create_and_batch_delete()
