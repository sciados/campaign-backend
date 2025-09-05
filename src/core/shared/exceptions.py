# =====================================
# File: src/core/shared/exceptions.py
# =====================================

"""
Custom exceptions for CampaignForge application.

Provides a comprehensive exception hierarchy for proper error handling
and user feedback across all modules.
"""

from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CampaignForgeException(Exception):
    """
    Base exception for all CampaignForge-specific errors.
    
    Provides structured error information with proper logging
    and user-friendly error messages.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "GENERAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)
        
        # Log the exception
        logger.error(
            f"CampaignForge Exception: {error_code} - {message}",
            extra={"error_code": error_code, "details": details}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(CampaignForgeException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            status_code=422,
            **kwargs
        )


class AuthenticationError(CampaignForgeException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            **kwargs
        )


class AuthorizationError(CampaignForgeException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied", resource: Optional[str] = None, **kwargs):
        details = {"resource": resource} if resource else {}
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details,
            status_code=403,
            **kwargs
        )


class NotFoundError(CampaignForgeException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None, **kwargs):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
            
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            details=details,
            status_code=404,
            **kwargs
        )


class ServiceUnavailableError(CampaignForgeException):
    """Raised when an external service is unavailable."""
    
    def __init__(self, message: str, service_name: Optional[str] = None, **kwargs):
        details = {"service_name": service_name} if service_name else {}
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE_ERROR",
            details=details,
            status_code=503,
            **kwargs
        )


class RateLimitError(CampaignForgeException):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None, **kwargs):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details,
            status_code=429,
            **kwargs
        )


class StorageError(CampaignForgeException):
    """Raised when storage operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        details = {"operation": operation} if operation else {}
        super().__init__(
            message=message,
            error_code="STORAGE_ERROR",
            details=details,
            status_code=500,
            **kwargs
        )


class AIProviderError(CampaignForgeException):
    """Raised when AI provider operations fail."""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        details = {"provider": provider} if provider else {}
        super().__init__(
            message=message,
            error_code="AI_PROVIDER_ERROR",
            details=details,
            status_code=502,
            **kwargs
        )