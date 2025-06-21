"""
Core configuration settings for CampaignForge AI
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""

    # Basic settings
    APP_NAME: str = "CampaignForge AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str

    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["https://campaignforge-frontend.vercel.app"]
    ALLOWED_HOSTS: List[str] = ["*"]

    # AI Services
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    STABILITY_AI_API_KEY: Optional[str] = None

    # Storage
    CLOUDFLARE_R2_ENDPOINT: str
    CLOUDFLARE_R2_ACCESS_KEY: str
    CLOUDFLARE_R2_SECRET_KEY: str
    CLOUDFLARE_R2_BUCKET: str

    # File Upload
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES: List[str] = [
        "video/mp4", "video/avi", "video/mov",
        "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg", "image/png", "image/gif",
        "text/csv", "application/vnd.ms-excel"
    ]

    # External APIs
    YOUTUBE_API_KEY: Optional[str] = None
    VIMEO_ACCESS_TOKEN: Optional[str] = None

    # Monitoring
    SENTRY_DSN: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
