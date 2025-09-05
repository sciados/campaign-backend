# =====================================
# File: src/core/middleware/error_handling.py
# =====================================

"""
Global error handling middleware for CampaignForge.

Provides consistent error responses and logging across
all API endpoints.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging
from typing import Union

from ..shared.exceptions import CampaignForgeException
from ..shared.responses import ErrorResponse

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request with global error handling.
        
        Args:
            request: HTTP request
            call_next: Next middleware/endpoint
            
        Returns:
            Response: HTTP response
        """
        try:
            return await call_next(request)
        except HTTPException as e:
            # FastAPI HTTP exceptions - pass through
            logger.info(f"HTTP {e.status_code}: {e.detail} - {request.method} {request.url}")
            raise
        except CampaignForgeException as e:
            # Custom application exceptions
            logger.error(f"Application error: {e.error_code} - {e.message}")
            return JSONResponse(
                status_code=e.status_code,
                content=ErrorResponse(
                    message=e.message,
                    error_code=e.error_code,
                    details=e.details
                ).dict()
            )
        except Exception as e:
            # Unexpected exceptions
            logger.exception(f"Unexpected error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    message="An unexpected error occurred",
                    error_code="INTERNAL_SERVER_ERROR",
                    details={"error_type": type(e).__name__}
                ).dict()
            )