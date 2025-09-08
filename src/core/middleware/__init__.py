# =====================================
# File: src/core/middleware/__init__.py
# =====================================

"""
Middleware components for CampaignForge Core Infrastructure.

Provides authentication, CORS, rate limiting, and error handling
middleware for the FastAPI application.
"""

from src.users.middleware.auth_middleware import AuthMiddleware

from src.core.middleware.rate_limiting import RateLimitMiddleware
from src.core.middleware.error_handling import ErrorHandlingMiddleware

from src.core.middleware.cors_middleware import setup_cors

__all__ = [
    "AuthMiddleware",
    "setup_cors",
    "RateLimitMiddleware", 
    "ErrorHandlingMiddleware",
]