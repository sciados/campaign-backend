"""
Video platform processing service
"""

import yt_dlp
from typing import Dict, Optional
import structlog

logger = structlog.get_logger()

class VideoProcessorService:
    """Video processing service for multiple platforms"""

    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False
        }

    def detect_platform(self, url: str) -> str:
        """Detect video platform from URL"""
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'tiktok.com' in url:
            return 'tiktok'
        elif 'vimeo.com' in url:
            return 'vimeo'
        elif 'instagram.com' in url:
            return 'instagram'
        elif 'linkedin.com' in url:
            return 'linkedin'
        else:
            raise ValueError(f"Unsupported platform for URL: {url}")

    async def extract_metadata(self, url: str) -> Dict:
        """Extract metadata from video URL"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                return {
                    'title': info.get('title'),
                    'description': info.get('description'),
                    'duration': info.get('duration'),
                    'view_count': info.get('view_count'),
                    'upload_date': info.get('upload_date'),
                    'uploader': info.get('uploader'),
                    'tags': info.get('tags', []),
                    'thumbnail': info.get('thumbnail'),
                    'platform': self.detect_platform(url)
                }

        except Exception as e:
            logger.error("Video metadata extraction failed", url=url, error=str(e))
            raise
