# =====================================
# File: src/core/config/settings.py
# =====================================

"""
Main application settings for CampaignForge Railway deployment.

Manages all environment variables with proper typing, validation,
and Railway-specific configurations.
"""

from pydantic import BaseSettings, validator
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
    APP_VERSION: str = "1.0.0"
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
    
    # ===== EXTERNAL APIS =====
    CLICKBANK_API_KEY: str
    
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
    
    @validator("ALLOWED_ORIGINS")
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("DATABASE_URL_ASYNC")
    def validate_async_db_url(cls, v: str, values: dict) -> str:
        """Ensure async database URL uses asyncpg driver."""
        if not v.startswith("postgresql+asyncpg://"):
            # Convert standard PostgreSQL URL to async format
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
            else:
                raise ValueError("DATABASE_URL_ASYNC must be a PostgreSQL URL")
        return v
    
    @validator("DEBUG")
    def set_debug_mode(cls, v: bool, values: dict) -> bool:
        """Set debug mode based on environment."""
        env = values.get("ENVIRONMENT", "production")
        if env in ["development", "dev", "local"]:
            return True
        return v
    
    @property
    def cors_origins(self) -> List[str]:
        """Get parsed CORS origins as list."""
        return self.ALLOWED_ORIGINS if isinstance(self.ALLOWED_ORIGINS, list) else []
    
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