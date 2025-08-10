# ============================================================================
# FILE 1: src/core/responses.py (NEW FILE)
# ============================================================================

"""
Response utilities for standardized API responses
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ResponseBuilder:
    """Builder for creating standardized responses"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation completed successfully",
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a standardized success response"""
        return {
            "success": True,
            "status": "success",
            "message": message,
            "data": data,
            "error": None,
            "error_code": None,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id or str(uuid.uuid4())
        }
    
    @staticmethod
    def error(
        error: str,
        error_code: Optional[str] = None,
        data: Any = None,
        status_code: int = 500,
        suggestions: List[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a standardized error response"""
        return {
            "success": False,
            "status": "error",
            "message": error,
            "data": data,
            "error": error,
            "error_code": error_code or f"HTTP_{status_code}",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id or str(uuid.uuid4()),
            "error_details": {
                "error_type": error_code or "UnknownError",
                "description": error,
                "suggestions": suggestions or [],
                "debug_info": {
                    "status_code": status_code,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        }