# =====================================
# File: src/core/middleware/__init__.py
# =====================================

"""
Middleware components for CampaignForge Core Infrastructure.

Provides authentication, CORS, rate limiting, and error handling
middleware for the FastAPI application.
"""

from .auth_middleware import AuthMiddleware
from .cors_middleware import setup_cors
from .rate_limiting import RateLimitMiddleware
from .error_handling import ErrorHandlingMiddleware

__all__ = [
    "AuthMiddleware",
    "setup_cors",
    "RateLimitMiddleware", 
    "ErrorHandlingMiddleware",
]