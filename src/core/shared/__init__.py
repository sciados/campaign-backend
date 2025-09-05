# =====================================
# File: src/core/shared/__init__.py
# =====================================

"""
Shared utilities and common components for CampaignForge Core Infrastructure.

Provides exceptions, response models, decorators, and other utilities
used across all modules.
"""

from .exceptions import (
    CampaignForgeException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ServiceUnavailableError,
    RateLimitError,
    StorageError,
    AIProviderError,
)
from .responses import (
    StandardResponse,
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
)
from .decorators import (
    retry_on_failure,
    rate_limit,
    cache_result,
    log_execution_time,
)
from .validators import (
    validate_uuid,
    validate_email,
    validate_url,
    sanitize_string,
)

__all__ = [
    # Exceptions
    "CampaignForgeException",
    "ValidationError",
    "AuthenticationError", 
    "AuthorizationError",
    "NotFoundError",
    "ServiceUnavailableError",
    "RateLimitError",
    "StorageError",
    "AIProviderError",
    
    # Responses
    "StandardResponse",
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
    
    # Decorators
    "retry_on_failure",
    "rate_limit",
    "cache_result",
    "log_execution_time",
    
    # Validators
    "validate_uuid",
    "validate_email",
    "validate_url",
    "sanitize_string",
]