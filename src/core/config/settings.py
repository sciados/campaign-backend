"""
Main application settings for CampaignForge Railway deployment.

Manages all environment variables with proper typing, validation,
and Railway-specific configurations.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List
import os
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings with comprehensive environment variable management.
    
    Configured for Railway deployment with all AI providers and services.
    """
    
    # ===== APPLICATION =====
    APP_NAME: str = "CampaignForge"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    API_BASE_URL: str
    
    # ===== DATABASE =====
    DATABASE_URL: str
    DATABASE_URL_ASYNC: str
    REDIS_URL: Optional[str] = None
    
    # ===== AUTHENTICATION =====
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ACCESS_KEY: str
    
    # ===== AI PROVIDERS =====
    # Primary AI Providers
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    COHERE_API_KEY: str
    
    # Alternative AI Providers
    GROQ_API_KEY: str
    DEEPSEEK_API_KEY: str
    TOGETHER_API_KEY: str
    MINIMAX_API_KEY: str
    AIMLAPI_API_KEY: str
    
    # ===== MEDIA GENERATION =====
    STABILITY_API_KEY: str
    REPLICATE_API_TOKEN: str
    FAL_API_KEY: str
    
    # ===== STORAGE =====
    CLOUDFLARE_ACCOUNT_ID: str
    CLOUDFLARE_R2_ACCESS_KEY_ID: str
    CLOUDFLARE_R2_SECRET_ACCESS_KEY: str
    CLOUDFLARE_R2_BUCKET_NAME: str
    
    # ===== CORS =====
    ALLOWED_ORIGINS: str
    
    # ===== AI SYSTEM CONFIGURATION =====
    AI_CACHE_TTL_SECONDS: int = 300
    AI_COST_OPTIMIZATION: bool = True
    AI_FALLBACK_ENABLED: bool = True
    AI_MONITORING_ENABLED: bool = True
    AI_MONITORING_INTERVAL_MINUTES: int = 60
    INTELLIGENCE_ANALYSIS_ENABLED: bool = True
    
    # ===== CREDITS & LIMITS =====
    CREDIT_ENFORCEMENT_ENABLED: bool = True
    MAX_FILE_SIZE_MB: int = 50
    
    # ===== EXTERNAL SERVICES =====
    AI_DISCOVERY_DATABASE_URL: str
    AI_DISCOVERY_SERVICE_URL: str

    # ===== PLATFORMS =====
    CLICKBANK_DEV_KEY: Optional[str] = None
    # JVZOO_API_KEY: Optional[str] = None  # Commented out until needed
    
    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("DATABASE_URL_ASYNC")
    @classmethod
    def validate_async_db_url(cls, v: str, values=None) -> str:
        """Ensure async database URL uses asyncpg driver."""
        if not v.startswith("postgresql+asyncpg://"):
            # Convert standard PostgreSQL URL to async format
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
            else:
                raise ValueError("DATABASE_URL_ASYNC must be a PostgreSQL URL")
        return v
    
    @field_validator("DEBUG")
    @classmethod
    def set_debug_mode(cls, v: bool, values=None) -> bool:
        """Set debug mode based on environment."""
        env = os.getenv("ENVIRONMENT", "production")
        if env in ["development", "dev", "local"]:
            return True
        return v
    
    @property
    def cors_origins(self) -> List[str]:
        """Get parsed CORS origins as list."""
        if isinstance(self.ALLOWED_ORIGINS, list):
            return self.ALLOWED_ORIGINS
        elif isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        else:
            return []
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() in ["production", "prod"]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() in ["development", "dev", "local"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Global settings instance
settings = get_settings()


# ===== DATABASE UTILITY FUNCTIONS =====

def get_database_url(async_mode: bool = False) -> str:
    if async_mode:
        # Use async URL if available
        if settings.DATABASE_URL_ASYNC:
            return settings.DATABASE_URL_ASYNC
        elif settings.DATABASE_URL:
            # Convert sync URL to async format
            url = settings.DATABASE_URL
            if url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        else:
            raise ValueError("No database URL configured")
    else:
        # Return sync URL
        if settings.DATABASE_URL:
            # Ensure it's a sync URL (remove +asyncpg if present)
            url = settings.DATABASE_URL
            if "+asyncpg" in url:
                return url.replace("+asyncpg", "")
            return url
        else:
            raise ValueError("No database URL configured")


def get_redis_url() -> str:
    """Get Redis URL for caching"""
    return settings.REDIS_URL or "redis://localhost:6379"


def get_ai_provider_config() -> dict:
    """Get all AI provider API keys"""
    return {
        "openai": settings.OPENAI_API_KEY,
        "anthropic": settings.ANTHROPIC_API_KEY,
        "groq": settings.GROQ_API_KEY,
        "cohere": settings.COHERE_API_KEY,
        "deepseek": settings.DEEPSEEK_API_KEY,
        "together": settings.TOGETHER_API_KEY,
        "minimax": settings.MINIMAX_API_KEY,
        "aimlapi": settings.AIMLAPI_API_KEY,
    }


def get_storage_config() -> dict:
    """Get Cloudflare R2 storage configuration"""
    return {
        "access_key_id": settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
        "secret_access_key": settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
        "bucket_name": settings.CLOUDFLARE_R2_BUCKET_NAME,
        "account_id": settings.CLOUDFLARE_ACCOUNT_ID,
    }

def get_platform_config() -> dict:
    """Get platform configuration (ClickBank)"""
    return {
        "clickbank_dev_key": settings.CLICKBANK_DEV_KEY,
        # "jvzoo_api_key": settings.JVZOO_API_KEY,  # Commented out until needed
        "clickbank_enabled": settings.CLICKBANK_DEV_KEY is not None,
        # "jvzoo_enabled": settings.JVZOO_API_KEY is not None,  # Commented out until needed
    }

def get_cors_origins() -> List[str]:
    """Get CORS allowed origins as a list"""
    return settings.cors_origins