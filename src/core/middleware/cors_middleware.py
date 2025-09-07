# =====================================
# File: src/core/middleware/cors_middleware.py
# =====================================

"""
CORS middleware configuration for CampaignForge.

Handles Cross-Origin Resource Sharing for Vercel frontend integration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.core.config import deployment_config

logger = logging.getLogger(__name__)


def setup_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    cors_config = deployment_config.get_cors_config()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config["allow_origins"],
        allow_credentials=cors_config["allow_credentials"],
        allow_methods=cors_config["allow_methods"],
        allow_headers=cors_config["allow_headers"],
        expose_headers=["X-Total-Count", "X-Page-Count"],
    )
    
    logger.info(f"CORS configured with origins: {cors_config['allow_origins']}")