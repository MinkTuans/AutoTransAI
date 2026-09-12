from __future__ import annotations

import os
import json
import uuid
import asyncio
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import google_auth_oauthlib.flow

# Allow non-HTTPS (HTTP) callback during local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from app.api.deps import get_db
from app.config import get_settings
from app.models.video_editor import YouTubeChannel, YouTubePublication, PublishStatusEnum
from app.core.encryption import encrypt_data
from app.services.video_editor.youtube_service import YouTubePublishingService

router = APIRouter(prefix="/youtube", tags=["youtube"])
settings = get_settings()

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]

class UploadVideoRequest(BaseModel):
    project_id: str
    job_id: str | None = None
    channel_id: str
    video_path: str
    title: str
    description: str
    tags: list[str] = []
    category_id: str = "22"
    privacy_status: str = "private"


def _get_redirect_uri() -> str:
    curr_settings = get_settings()
    if curr_settings.YOUTUBE_REDIRECT_URI:
        return curr_settings.YOUTUBE_REDIRECT_URI
    return f"http://{curr_settings.HOST}:{curr_settings.PORT}/api/youtube/oauth-callback"


def _get_client_config() -> dict:
    curr_settings = get_settings()
    if not curr_settings.YOUTUBE_CLIENT_ID or not curr_settings.YOUTUBE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="YouTube OAuth is not configured in .env (YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET)")
    
    redirect_uri = _get_redirect_uri()
    return {
        "web": {
            "client_id": curr_settings.YOUTUBE_CLIENT_ID,
            "project_id": "autotransai",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": curr_settings.YOUTUBE_CLIENT_SECRET,
            "redirect_uris": [redirect_uri]
        }
    }


_oauth_verifiers: dict[str, str] = {}


@router.get("/auth-url")
async def get_auth_url(redirect_uri: str = None):
    """Get the Google OAuth 2.0 authorization URL."""
    try:
        client_config = _get_client_config()
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config, scopes=SCOPES
        )
        flow.redirect_uri = _get_redirect_uri()

        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        if getattr(flow, "code_verifier", None):
            _oauth_verifiers[state] = flow.code_verifier

        return {"auth_url": authorization_url, "state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/oauth-callback")
async def oauth_callback(request: Request, state: str = None, code: str = None, db: AsyncSession = Depends(get_db)):
    """Handle the Google OAuth 2.0 callback."""
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    try:
        client_config = _get_client_config()
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config, scopes=SCOPES
        )
        flow.redirect_uri = _get_redirect_uri()
        if state and state in _oauth_verifiers:
            flow.code_verifier = _oauth_verifiers.pop(state)

        # Use the full URL to fetch tokens (allow local HTTP transport)
        authorization_response = str(request.url)
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        
        # Fetch channel info
        from googleapiclient.discovery import build
        youtube = build("youtube", "v3", credentials=credentials)
        channel_response = youtube.channels().list(mine=True, part="snippet").execute()
        
        if not channel_response.get("items"):
            raise HTTPException(status_code=404, detail="No YouTube channel found for this account")
            
        channel_info = channel_response["items"][0]
        channel_id = channel_info["id"]
        channel_title = channel_info["snippet"]["title"]
        
        # Prepare credentials dictionary
        creds_dict = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }
        
        # Encrypt the refresh token / credentials JSON
        encrypted_creds = encrypt_data(json.dumps(creds_dict))
        
        # Upsert YouTubeChannel
        stmt = select(YouTubeChannel).where(YouTubeChannel.channel_id == channel_id)
        result = await db.execute(stmt)
        existing_channel = result.scalars().first()
        
        if existing_channel:
            existing_channel.credentials_json = encrypted_creds
            existing_channel.channel_name = channel_title
            existing_channel.is_active = True
        else:
            new_channel = YouTubeChannel(
                id=str(uuid.uuid4()),
                channel_name=channel_title,
                channel_id=channel_id,
                credentials_json=encrypted_creds,
                is_active=True
            )
            db.add(new_channel)
            
        await db.commit()
        
        # Redirect back to frontend settings page
        return RedirectResponse(url="http://127.0.0.1:5173/settings/social?youtube_connected=true")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts")
async def list_accounts(db: AsyncSession = Depends(get_db)):
    """List connected YouTube accounts."""
    stmt = select(YouTubeChannel).where(YouTubeChannel.is_active == True)
    result = await db.execute(stmt)
    channels = result.scalars().all()
    
    return [{
        "id": ch.id,
        "channel_id": ch.channel_id,
        "channel_name": ch.channel_name,
        "created_at": ch.created_at
    } for ch in channels]


@router.delete("/accounts/{id}")
async def disconnect_account(id: str, db: AsyncSession = Depends(get_db)):
    """Disconnect a YouTube account."""
    stmt = select(YouTubeChannel).where(YouTubeChannel.id == id)
    result = await db.execute(stmt)
    channel = result.scalars().first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
        
    channel.is_active = False
    await db.commit()
    return {"success": True}


@router.post("/upload")
async def start_upload(req: UploadVideoRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Initiate an asynchronous resumable video upload."""
    stmt = select(YouTubeChannel).where(YouTubeChannel.id == req.channel_id, YouTubeChannel.is_active == True)
    result = await db.execute(stmt)
    channel = result.scalars().first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Active YouTube channel not found")
        
    pub = YouTubePublication(
        id=str(uuid.uuid4()),
        job_id=req.job_id,
        project_id=req.project_id,
        channel_id=channel.id,
        title=req.title,
        description=req.description,
        tags_json=json.dumps(req.tags),
        category_id=req.category_id,
        privacy_status=req.privacy_status,
        status=PublishStatusEnum.PENDING.value,
        progress=0
    )
    db.add(pub)
    await db.commit()
    await db.refresh(pub)
    
    background_tasks.add_task(
        YouTubePublishingService.execute_async_upload,
        publication_id=pub.id,
        video_path=req.video_path
    )
    
    return {"upload_id": pub.id, "status": "PENDING"}


@router.get("/upload/{upload_id}/status")
async def get_upload_status(upload_id: str, db: AsyncSession = Depends(get_db)):
    """Check upload progress."""
    stmt = select(YouTubePublication).where(YouTubePublication.id == upload_id)
    result = await db.execute(stmt)
    pub = result.scalars().first()
    
    if not pub:
        raise HTTPException(status_code=404, detail="Upload not found")
        
    return {
        "id": pub.id,
        "status": pub.status,
        "progress": pub.progress,
        "youtube_video_id": pub.youtube_video_id,
        "youtube_url": pub.youtube_url,
        "error_message": pub.error_message
    }
