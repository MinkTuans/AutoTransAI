"""
AutoTransAi Application Status Route.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/apps", tags=["Apps Launcher"])

@router.get("/status")
async def get_apps_status():
    """Return status of AutoTransAi unified application."""
    return {
        "autotrans_ai": {
            "running": True,
            "port": 8000,
            "url": "/",
            "name": "AutoTransAi",
        }
    }
