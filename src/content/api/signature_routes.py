# ============================================================================
# USER SIGNATURE MANAGEMENT API
# ============================================================================

# src/content/api/signature_routes.py

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from uuid import UUID

from src.core.factories.service_factory import ServiceFactory
from src.content.services.truly_dynamic_content_service import TrulyDynamicContentService

signature_router = APIRouter(prefix="/api/content/signature", tags=["user-signature"])

@signature_router.get("/users/{user_id}")
async def get_user_signature(user_id: UUID):
    """Get user's saved content signature"""
    try:
        async with ServiceFactory.create_service(TrulyDynamicContentService) as service:
            signature = await service._get_user_signature(user_id)
        
        return {
            "success": True,
            "signature": signature
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@signature_router.post("/users/{user_id}")
async def save_user_signature(user_id: UUID, signature_data: Dict[str, str]):
    """Save user's content signature preferences"""
    try:
        async with ServiceFactory.create_service(TrulyDynamicContentService) as service:
            success = await service._save_user_signature(user_id, signature_data)
        
        if success:
            return {
                "success": True,
                "message": "Signature saved successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to save signature"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@signature_router.get("/styles")
async def get_signature_styles():
    """Get available signature styles"""
    return {
        "styles": {
            "professional": {
                "description": "Best regards format with title and company",
                "example": "Best regards,\nJohn Smith\nMarketing Director, ABC Company"
            },
            "casual": {
                "description": "Simple best format",
                "example": "Best,\nJohn\nABC Company"
            },
            "formal": {
                "description": "Sincerely format with full credentials",
                "example": "Sincerely,\nJohn Smith\nMarketing Director\nABC Company"
            }
        }
    }