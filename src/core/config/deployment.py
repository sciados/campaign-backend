# =====================================
# File: src/core/config/deployment.py
# =====================================

"""
Railway deployment-specific configuration for CampaignForge.

Handles Railway-specific settings, health checks, and deployment optimizations.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import os

from src.core.config.settings import settings


@dataclass
class RailwayConfig:
    """Railway platform-specific configuration."""
    
    # Railway Environment
    railway_environment: str = os.getenv("RAILWAY_ENVIRONMENT", "production")
    railway_service_name: str = os.getenv("RAILWAY_SERVICE_NAME", "campaignforge-backend")
    railway_project_id: str = os.getenv("RAILWAY_PROJECT_ID", "")
    railway_replica_id: str = os.getenv("RAILWAY_REPLICA_ID", "")
    
    # Port Configuration
    port: int = int(os.getenv("PORT", "8000"))
    
    # Health Check Configuration
    health_check_path: str = "/health"
    health_check_interval: int = 30
    
    # Performance Settings
    worker_timeout: int = 120
    keepalive_timeout: int = 65
    max_requests: int = 1000
    max_requests_jitter: int = 100
    
    @property
    def is_railway_environment(self) -> bool:
        """Check if running on Railway platform."""
        return bool(self.railway_project_id)
    
    @property
    def host(self) -> str:
        """Get the appropriate host for the environment."""
        if self.is_railway_environment:
            return "0.0.0.0"  # Railway requires binding to all interfaces
        return "127.0.0.1"
    
    def get_uvicorn_config(self) -> Dict[str, Any]:
        """Get Uvicorn server configuration for Railway."""
        return {
            "host": self.host,
            "port": self.port,
            "workers": 1,  # Railway handles scaling
            "timeout_keep_alive": self.keepalive_timeout,
            "access_log": not settings.is_production,
            "reload": settings.is_development,
        }


class DeploymentConfig:
    """Main deployment configuration manager."""
    
    def __init__(self):
        self.railway = RailwayConfig()
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration for Railway deployment."""
        
        # Get configured origins
        cors_origins = settings.cors_origins
        
        # Add localhost origins for development
        localhost_origins = [
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:3002",
            "http://localhost:3003",
            "http://localhost:3004",
            "http://localhost:3005",
            "http://localhost:3006",
            "http://localhost:3007",
            "http://localhost:3008",
            "http://localhost:3009",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3002",
            "http://127.0.0.1:3003",
            "http://127.0.0.1:3004",
            "http://127.0.0.1:3005",
            "http://127.0.0.1:3006",
            "http://127.0.0.1:3007",
            "http://127.0.0.1:3008",
            "http://127.0.0.1:3009"
        ]
        
        # Add localhost origins if not already included
        for origin in localhost_origins:
            if origin not in cors_origins:
                cors_origins.append(origin)
        
        return {
            "allow_origins": cors_origins,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["*"],
        }
    
    def get_middleware_config(self) -> Dict[str, Any]:
        """Get middleware configuration."""
        return {
            "trusted_hosts": ["*"] if settings.is_development else [
                "*.railway.app",
                "*.vercel.app", 
                "rodgersdigital.com",
                "www.rodgersdigital.com"
            ],
            "rate_limit": {
                "calls": 100,
                "period": 60,  # 100 calls per minute
            }
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration for Railway."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "railway": {
                    "format": "[%(levelname)s] %(name)s: %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "railway" if self.railway.is_railway_environment else "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
            "loggers": {
                "uvicorn": {"level": "INFO"},
                "uvicorn.error": {"level": "INFO"},
                "uvicorn.access": {"level": "INFO" if settings.is_development else "WARNING"},
            },
        }


# Global deployment configuration
deployment_config = DeploymentConfig()