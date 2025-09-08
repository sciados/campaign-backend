"""
Standardized API response models for CampaignForge.

Provides consistent response structures across all API endpoints
with proper typing and serialization.
"""

from typing import Any, Dict, List, Optional, Generic, TypeVar, Literal
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')


class StandardResponse(BaseModel, Generic[T]):
    """
    Standard API response format for all CampaignForge endpoints.
    
    Provides consistent structure with success status, data,
    and optional metadata.
    """
    
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[T] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Human-readable message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SuccessResponse(StandardResponse[T]):
    """Success response with data."""
    
    success: Literal[True] = Field(True, description="Success status")
    
    def __init__(self, data: T, message: Optional[str] = None, **kwargs):
        super().__init__(success=True, data=data, message=message, **kwargs)


class ErrorResponse(StandardResponse[None]):
    """Error response with error details."""
    
    success: Literal[False] = Field(False, description="Error status")
    error_code: str = Field(..., description="Machine-readable error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "GENERAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            success=False,
            data=None,
            message=message,
            error_code=error_code,
            details=details,
            **kwargs
        )


class PaginatedResponse(StandardResponse[List[T]]):
    """Paginated response for list endpoints."""
    
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")
    
    def __init__(
        self,
        data: List[T],
        total: int,
        page: int,
        size: int,
        message: Optional[str] = None,
        **kwargs
    ):
        pages = (total + size - 1) // size if size > 0 else 0
        has_next = page < pages
        has_previous = page > 1
        
        super().__init__(
            success=True,
            data=data,
            message=message,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=has_next,
            has_previous=has_previous,
            **kwargs
        )


# Response factory functions for common use cases
def success_response(data: T, message: Optional[str] = None) -> SuccessResponse[T]:
    """Create a success response."""
    return SuccessResponse(data=data, message=message)


def error_response(
    message: str,
    error_code: str = "GENERAL_ERROR",
    details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """Create an error response."""
    return ErrorResponse(message=message, error_code=error_code, details=details)


def paginated_response(
    data: List[T],
    total: int,
    page: int,
    size: int,
    message: Optional[str] = None
) -> PaginatedResponse[T]:
    """Create a paginated response."""
    return PaginatedResponse(
        data=data,
        total=total,
        page=page,
        size=size,
        message=message
    )


# ===== UTILITY FUNCTIONS FOR BACKWARD COMPATIBILITY =====

def create_success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a success response dictionary for backward compatibility.
    
    This function provides compatibility with existing code that expects
    dict responses rather than Pydantic models.
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code (for compatibility, not used in dict)
        meta: Additional metadata
        
    Returns:
        Dictionary response for compatibility with existing endpoints
    """
    response = {
        "success": True,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    if meta:
        response["meta"] = meta
    
    return response

def create_error_response(
    message: str = "An error occurred",
    status_code: int = 400,
    error_code: str = "GENERAL_ERROR",
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create an error response dictionary for backward compatibility.
    
    Args:
        message: Error message
        status_code: HTTP status code (for compatibility)
        error_code: Specific error code
        details: Additional error details
        
    Returns:
        Dictionary response for compatibility with existing endpoints
    """
    response = {
        "success": False,
        "message": message,
        "error_code": error_code,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        response["details"] = details
    
    return response