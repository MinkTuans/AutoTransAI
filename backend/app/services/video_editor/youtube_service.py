"""
YouTube Upload & SEO Publishing Automation Service — Gemini SEO Metadata Generator & YouTube Data API v3 Publisher.
"""

from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.config import get_settings
from app.core import get_logger
from app.core.job_logger import log_job_event

logger = get_logger(__name__)
settings = get_settings()


class YouTubePublishingService:
    """Service for generating YouTube SEO metadata and uploading video via YouTube Data API v3."""

    @staticmethod
    async def generate_youtube_seo_metadata(
        transcript_text: str,
        target_language: str = "vi",
        job_id: str = "VT-YT",
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate SEO-optimized YouTube Title, Description, Hashtags, Tags, and Category ID using Gemini AI Studio.
        """
        if not settings.GEMINI_API_KEY:
            return {
                "title": "Video lồng tiếng AI chất lượng cao",
                "description": "Video được tự động lồng tiếng và xử lý bằng công nghệ AI WorkflowVdAi.",
                "tags": ["AI", "VideoDubbing", "WorkflowVdAi"],
                "category_id": "22",
            }

        import httpx
        from app.services.model_resolver import AIModelResolver
        from app.providers.llm.gemini_provider import strip_gemini_model_prefix

        if not model_name:
            res_model = await AIModelResolver.resolve_llm_model(None)
            model_name = res_model.get("model_id")

        target_model = strip_gemini_model_prefix(model_name)

        prompt = (
            "Bạn là một chuyên gia SEO YouTube hàng đầu.\n"
            f"Hãy tự động tạo tiêu đề, mô tả và từ khóa tối ưu SEO YouTube bằng ngôn ngữ {target_language} dựa trên nội dung video bên dưới.\n"
            "Yêu cầu:\n"
            "1. Title (Tiêu đề): Dưới 90 ký tự, thu hút clickbait văn minh, chứa từ khóa chính.\n"
            "2. Description (Mô tả): Khoảng 150-300 từ, tóm tắt nội dung hấp dẫn, chứa 3-5 hashtag ở cuối.\n"
            "3. Tags: Mảng 10-15 từ khóa phổ biến.\n"
            "4. Category ID: '22' (People & Blogs), '27' (Education), '24' (Entertainment).\n\n"
            f"NỘI DUNG SẢN XUẤT:\n{transcript_text[:3000]}\n\n"
            "Trả về JSON thuần túy (không markdown) với cấu trúc:\n"
            "{\n"
            '  "title": "Tiêu đề hấp dẫn...",\n'
            '  "description": "Nội dung mô tả...",\n'
            '  "tags": ["tag1", "tag2", "tag3"],\n'
            '  "category_id": "22"\n'
            "}"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"}
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={settings.GEMINI_API_KEY}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    if parts:
                        raw_text = parts[0].get("text", "").strip()
                        json_str = re.sub(r"^```json\s*", "", raw_text, flags=re.MULTILINE)
                        json_str = re.sub(r"```$", "", json_str, flags=re.MULTILINE).strip()
                        return json.loads(json_str)
            except Exception as ex:
                logger.warning("Gemini YouTube SEO generation exception", error=str(ex), model=target_model)

        return {
            "title": "Video lồng tiếng AI tự động",
            "description": "Video được tạo tự động bởi hệ thống lồng tiếng AI WorkflowVdAi.",
            "tags": ["AI", "VideoDubbing"],
            "category_id": "22",
        }

    @classmethod
    async def upload_to_youtube(
        cls,
        video_path: Path,
        title: str,
        description: str,
        tags: List[str],
        category_id: str = "22",
        privacy_status: str = "private",
        credentials_json: Optional[str] = None,
        job_id: str = "VT-YT",
    ) -> Dict[str, Any]:
        """
        Upload video file to YouTube via YouTube Data API v3 (Resumable Upload protocol).
        """
        log_job_event(job_id, "PUBLISHING", f"[YOUTUBE-API] Starting YouTube video upload '{title}' (Privacy: {privacy_status})...")
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file for YouTube upload not found: {video_path}")

        # If official google-api-python-client is configured with OAuth2
        if credentials_json:
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
                from googleapiclient.http import MediaFileUpload

                creds_data = json.loads(credentials_json)
                creds = Credentials.from_authorized_user_info(creds_data)
                youtube = build("youtube", "v3", credentials=creds)

                body = {
                    "snippet": {
                        "title": title[:100],
                        "description": description,
                        "tags": tags,
                        "categoryId": category_id,
                    },
                    "status": {
                        "privacyStatus": privacy_status,
                        "selfDeclaredMadeForKids": False,
                    },
                }

                media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
                request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

                response = None
                while response is None:
                    status, response = request.next_chunk()
                    if status:
                        log_job_event(job_id, "PUBLISHING", f"[YOUTUBE-API] Upload progress: {int(status.progress() * 100)}%")

                youtube_id = response.get("id")
                yt_url = f"https://www.youtube.com/watch?v={youtube_id}"
                log_job_event(job_id, "PUBLISHING", f"[YOUTUBE-API] Video uploaded successfully: {yt_url}")
                return {
                    "success": True,
                    "youtube_video_id": youtube_id,
                    "youtube_url": yt_url,
                    "status": "PUBLISHED",
                }
            except Exception as yt_err:
                logger.error("YouTube API upload exception", error=str(yt_err), job_id=job_id)
                log_job_event(job_id, "PUBLISHING", f"[YOUTUBE-API] ⚠️ Upload failed: {str(yt_err)}")
                raise yt_err

        # Simulated upload for development / staging when credentials not set
        mock_id = f"yt_{job_id.replace('-', '_').lower()}"
        mock_url = f"https://www.youtube.com/watch?v={mock_id}"
        log_job_event(job_id, "PUBLISHING", f"[YOUTUBE-API] (Dev Mode) Published video metadata ready: {mock_url}")
        return {
            "success": True,
            "youtube_video_id": mock_id,
            "youtube_url": mock_url,
            "status": "PUBLISHED",
        }

    @classmethod
    async def execute_async_upload(cls, publication_id: str, video_path: str) -> None:
        """Executes upload in background, updates database model progress."""
        from app.database import async_session_factory
        from app.models.video_editor import YouTubePublication, YouTubeChannel, PublishStatusEnum
        from app.core.encryption import decrypt_data
        
        async with async_session_factory() as db:
            import sqlalchemy as sa
            stmt = sa.select(YouTubePublication, YouTubeChannel).join(
                YouTubeChannel, YouTubePublication.channel_id == YouTubeChannel.id
            ).where(YouTubePublication.id == publication_id)
            result = await db.execute(stmt)
            row = result.first()
            if not row:
                return
                
            pub, channel = row
            
            pub.status = PublishStatusEnum.UPLOADING.value
            await db.commit()
            
            try:
                # Decrypt credentials
                raw_creds_json = decrypt_data(channel.credentials_json)
                creds_data = json.loads(raw_creds_json)
                
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
                from googleapiclient.http import MediaFileUpload
                
                # Natively handles refresh tokens
                creds = Credentials.from_authorized_user_info(creds_data)
                youtube = build("youtube", "v3", credentials=creds)
                
                tags = json.loads(pub.tags_json) if pub.tags_json else []
                body = {
                    "snippet": {
                        "title": pub.title[:100],
                        "description": pub.description,
                        "tags": tags,
                        "categoryId": pub.category_id,
                    },
                    "status": {
                        "privacyStatus": pub.privacy_status,
                        "selfDeclaredMadeForKids": False,
                    },
                }

                # Resumable upload chunking loop for real-time progress updates
                media = MediaFileUpload(video_path, chunksize=256*1024, resumable=True)
                
                def _do_create_request():
                    return youtube.videos().insert(part="snippet,status", body=body, media_body=media)
                
                request = await asyncio.to_thread(_do_create_request)
                
                def _step_upload(req):
                    return req.next_chunk()
                
                response = None
                while response is None:
                    status, response = await asyncio.to_thread(_step_upload, request)
                    if status:
                        pct = int(status.progress() * 100)
                        pub.progress = min(pct, 99)
                        await db.commit()
                
                pub.youtube_video_id = response.get("id")
                pub.youtube_url = f"https://www.youtube.com/watch?v={pub.youtube_video_id}"
                pub.status = PublishStatusEnum.PUBLISHED.value
                pub.progress = 100
                await db.commit()
                
            except Exception as e:
                logger.error("Async YouTube Upload failed", error=str(e), publication_id=publication_id)
                pub.status = PublishStatusEnum.FAILED.value
                pub.error_message = str(e)
                await db.commit()
