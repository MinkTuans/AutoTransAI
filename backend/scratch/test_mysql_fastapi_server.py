import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

async def test_mysql_fastapi():
    print("Testing FastAPI app on MySQL Laragon DB...")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get("/api/projects")
        assert res.status_code == 200
        data = res.json()
        print("Response status: 200 OK")
        print("Projects returned from MySQL DB:", len(data["data"]))
        for p in data["data"]:
            print("  - Item:", p["id"], "| Title:", p["title"], "| Type:", p["type"], "| Status:", p["status"])
    print("✓ FastAPI MySQL Database Integration Test PASSED!")

if __name__ == "__main__":
    asyncio.run(test_mysql_fastapi())
