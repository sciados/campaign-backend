# ============================================================================
# API ROUTES FOR INTEGRATED CONTENT GENERATION
# ============================================================================

# src/content/api/routes.py (Updated for integration)

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from uuid import UUID

from src.core.factories.service_factory import ServiceFactory
from src.content.services.integrated_content_service import IntegratedContentService

router = APIRouter(prefix="/api/content", tags=["content"])

@router.post("/generate")
async def generate_content_integrated(
    request: Dict[str, Any]
):
    """Generate content using integrated existing generator system"""
    try:
        campaign_id = request.get("campaign_id")
        content_type = request.get("content_type")
        user_id = request.get("user_id")
        company_id = request.get("company_id")
        preferences = request.get("preferences", {})
        
        if not all([campaign_id, content_type, user_id, company_id]):
            raise HTTPException(
                status_code=400,
                detail="campaign_id, content_type, user_id, and company_id are required"
            )
        
        # Use ServiceFactory for proper session management
        async with ServiceFactory.create_service(IntegratedContentService) as content_service:
            result = await content_service.generate_content(
                campaign_id=campaign_id,
                content_type=content_type,
                user_id=user_id,
                company_id=company_id,
                preferences=preferences
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generators/status")
async def get_generator_status():
    """Get status of available content generators"""
    try:
        async with ServiceFactory.create_service(IntegratedContentService) as content_service:
            status = content_service.get_generator_status()
        
        return {
            "success": True,
            "generator_status": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns/{campaign_id}/content")
async def get_campaign_content_integrated(
    campaign_id: UUID,
    content_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get generated content for a campaign"""
    try:
        async with ServiceFactory.create_service(IntegratedContentService) as content_service:
            content = await content_service.get_campaign_content(
                campaign_id=campaign_id,
                content_type=content_type,
                limit=limit,
                offset=offset
            )
        
        return {
            "success": True,
            "campaign_id": str(campaign_id),
            "content": content,
            "total_items": len(content),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))