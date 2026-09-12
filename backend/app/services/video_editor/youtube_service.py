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


def merge_youtube_tags(
    default_tags: Optional[Any],
    ai_tags: Optional[Any],
) -> List[str]:
    """
    Merge default tags and AI tags with case-insensitive duplicate detection,
    preserving default tags order and ensuring clean string/array formatting.
    """
    def parse_to_list(val: Optional[Any]) -> List[str]:
        if not val:
            return []
        if isinstance(val, list):
            raw_list = val
        else:
            cleaned_str = str(val).replace("\n", ",")
            raw_list = cleaned_str.split(",")
        
        result = []
        for item in raw_list:
            tag = item.strip()
            if tag:
                result.append(tag)
        return result

    def_list = parse_to_list(default_tags)
    ai_list = parse_to_list(ai_tags)

    merged: List[str] = []
    seen_lower = set()

    for tag in def_list:
        tag_lower = tag.lower()
        if tag_lower not in seen_lower:
            seen_lower.add(tag_lower)
            merged.append(tag)

    for tag in ai_list:
        tag_lower = tag.lower()
        if tag_lower not in seen_lower:
            seen_lower.add(tag_lower)
            merged.append(tag)

    return merged


def render_title_template(
    template: str,
    episode_num: int = 1,
    project_name: str = "Project",
    channel_name: str = "",
    video_name: str = "",
) -> str:
    """
    Render video title using configurable template variables safely.
    Episode is zero-padded (e.g., 1 -> '01', 12 -> '12').
    """
    if not template:
        template = "Tập {episode} | {project_name} | {channel_name}"
    
    ep_str = f"{int(episode_num):02d}" if episode_num > 0 else "01"
    
    replacements = {
        "{episode}": ep_str,
        "{project_name}": project_name or "",
        "{channel_name}": channel_name or "",
        "{video_name}": video_name or "",
    }
    
    res = template
    for key, val in replacements.items():
        res = res.replace(key, val)
    
    res = re.sub(r"\s+\|\s+(?=\||$)", "", res).strip()
    return res


async def calculate_project_video_episode(
    session: Any,
    project_id: Optional[str],
    job_id: str,
) -> int:
    """
    Determine 1-indexed video episode sequence number within a project based on created_at timestamp order.
    """
    if not project_id or not session:
        return 1
    
    try:
        from sqlalchemy import select
        from app.models.video_translator import VideoTranslationJob
        
        result = await session.execute(
            select(VideoTranslationJob)
            .where(VideoTranslationJob.project_id == project_id)
            .order_by(VideoTranslationJob.created_at.asc())
        )
        jobs = result.scalars().all()
        
        for index, job in enumerate(jobs, start=1):
            if job.id == job_id or (job.project_id and job.id == job_id):
                return index
    except Exception as err:
        logger.warning(f"Failed to calculate episode number for job {job_id}: {err}")
    
    return 1


class YouTubePublishingService:
    """Service for generating YouTube SEO metadata and uploading video via YouTube Data API v3."""

    @staticmethod
    async def generate_youtube_seo_metadata(
        transcript_text: str,
        target_language: str = "vi",
        job_id: str = "VT-YT",
        project_settings: Optional[Dict[str, Any]] = None,
        project_name: str = "Project",
        video_name: str = "",
        episode_num: int = 1,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate SEO-optimized YouTube Title, Description, Hashtags, Tags, and Category ID using Gemini AI Studio,
        strictly respecting Project YouTube Defaults and tag merging rules.
        """
        p_settings = project_settings or {}
        yt_enabled = p_settings.get("youtube_enabled", True)
        channel_name = p_settings.get("youtube_channel_name", "Xói Xám Content")
        title_template = p_settings.get("youtube_title_template", "Tập {episode} | {project_name} | {channel_name}")
        desc_default = p_settings.get("youtube_description_default", "")
        default_tags = p_settings.get("youtube_default_tags", "")
        ai_seo_enabled = p_settings.get("youtube_ai_seo_enabled", True)
        ai_allow_desc = p_settings.get("youtube_ai_allow_description", True)
        ai_allow_tags = p_settings.get("youtube_ai_allow_tags", True)

        # Render default title template
        rendered_title = render_title_template(
            template=title_template if yt_enabled else "{video_name}",
            episode_num=episode_num,
            project_name=project_name,
            channel_name=channel_name,
            video_name=video_name or f"Video {job_id}",
        )

        # Render default description (replacing template variables)
        rendered_desc = render_title_template(
            template=desc_default,
            episode_num=episode_num,
            project_name=project_name,
            channel_name=channel_name,
            video_name=video_name or f"Video {job_id}",
        ) if desc_default else ""

        # Default tags parsed as list
        base_tags = merge_youtube_tags(default_tags if yt_enabled else [], [])

        # If Gemini API key is missing or AI SEO is disabled, return default rendered metadata
        if not settings.GEMINI_API_KEY or not ai_seo_enabled:
            return {
                "title": rendered_title or f"Video {episode_num}",
                "description": rendered_desc,
                "tags": base_tags,
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
            f"Dự án đã có các giá trị SEO mặc định. Bạn chỉ được tạo nội dung bổ sung, KHÔNG được xóa hay thay thế các giá trị mặc định của người dùng.\n"
            f"Hãy sinh thêm nội dung SEO bổ sung bằng ngôn ngữ {target_language} dựa trên nội dung transcript video bên dưới.\n"
            "Yêu cầu:\n"
            "1. Title Suggestion (Gợi ý tiêu đề): Dưới 90 ký tự, thu hút clickbait văn minh.\n"
            "2. Additional Description (Mô tả bổ sung): Tóm tắt nội dung hấp dẫn 100-200 từ, kèm 3-5 hashtag.\n"
            "3. Additional Tags (Từ khóa bổ sung): Mảng 5-10 từ khóa liên quan đến nội dung video. DO NOT remove, replace, or modify default tags. Only provide additional relevant tags.\n"
            "4. Category ID: '22' (People & Blogs), '27' (Education), '24' (Entertainment).\n\n"
            f"NỘI DUNG TRANSCRIPT:\n{transcript_text[:3000]}\n\n"
            "Trả về JSON thuần túy (không markdown):\n"
            "{\n"
            '  "title": "Tiêu đề gợi ý...",\n'
            '  "description": "Mô tả bổ sung...",\n'
            '  "tags": ["tag1", "tag2"],\n'
            '  "category_id": "22"\n'
            "}"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"}
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={settings.GEMINI_API_KEY}"
        ai_res = {}
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
                        ai_res = json.loads(json_str)
            except Exception as ex:
                logger.warning("Gemini YouTube SEO generation exception", error=str(ex), model=target_model)

        ai_desc = ai_res.get("description", "") if ai_allow_desc else ""
        ai_tags = ai_res.get("tags", []) if ai_allow_tags else []

        # Merge Description: Default + AI Description
        if rendered_desc and ai_desc:
            final_description = f"{rendered_desc}\n\n{ai_desc}".strip()
        else:
            final_description = rendered_desc or ai_desc

        # Merge Tags: Code-level enforcement
        final_tags = merge_youtube_tags(default_tags if yt_enabled else [], ai_tags)

        return {
            "title": rendered_title or ai_res.get("title", f"Video {episode_num}"),
            "description": final_description,
            "tags": final_tags,
            "category_id": ai_res.get("category_id", "22"),
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
                
                def _step_upload_with_retry(req, max_retries=3):
                    import time
                    for attempt in range(max_retries):
                        try:
                            return req.next_chunk()
                        except Exception as chunk_err:
                            err_msg = str(chunk_err)
                            if any(k in err_msg for k in ("Unable to find the server", "gaierror", "ConnectionResetError", "timed out", "503", "500")):
                                if attempt < max_retries - 1:
                                    logger.warning("YouTube chunk upload connection drop, retrying", attempt=attempt+1, error=err_msg)
                                    time.sleep(2 * (attempt + 1))
                                    continue
                            raise chunk_err
                
                response = None
                while response is None:
                    status, response = await asyncio.to_thread(_step_upload_with_retry, request)
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
                err_text = str(e)
                if "Unable to find the server" in err_text or "gaierror" in err_text or "getaddrinfo failed" in err_text:
                    clean_err = "❌ Không thể kết nối tới máy chủ Google YouTube (youtube.googleapis.com). Vui lòng kiểm tra kết nối Internet, DNS hoặc tạm thời tắt VPN/Proxy trên máy tính."
                else:
                    clean_err = f"❌ Lỗi đăng YouTube: {err_text}"
                
                logger.error("Async YouTube Upload failed", error=clean_err, publication_id=publication_id)
                pub.status = PublishStatusEnum.FAILED.value
                pub.error_message = clean_err
                await db.commit()
