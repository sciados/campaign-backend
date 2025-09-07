# =====================================
# File: src/core/middleware/rate_limiting.py
# =====================================

"""
Rate limiting middleware for CampaignForge.

Provides basic rate limiting functionality to prevent abuse
and protect against excessive API usage.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from typing import Dict, List
import logging

from src.core.config import deployment_config

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    
    Note: In production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, List[float]] = {}
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request with rate limiting.
        
        Args:
            request: HTTP request
            call_next: Next middleware/endpoint
            
        Returns:
            Response: HTTP response
        """
        # Get client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        # Check rate limit
        now = time.time()
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        
        # Remove old requests outside the period
        cutoff = now - self.period
        self.clients[client_ip] = [t for t in self.clients[client_ip] if t > cutoff]
        
        # Check if rate limit exceeded
        if len(self.clients[client_ip]) >= self.calls:
            logger.warning(f"Rate limit exceeded for client {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.calls} requests per {self.period} seconds",
                headers={"Retry-After": str(self.period)}
            )
        
        # Record this request
        self.clients[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, self.calls - len(self.clients[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + self.period))
        
        return response