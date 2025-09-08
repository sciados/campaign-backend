# ============================================================================
# API ROUTES FOR DATABASE-DRIVEN CONTENT GENERATION
# ============================================================================

# src/content/api/database_driven_routes.py

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from uuid import UUID

from src.core.factories.service_factory import ServiceFactory
from src.content.services.database_driven_content_service import DatabaseDrivenContentService, ContentValidationService

router = APIRouter(prefix="/api/content/database-driven", tags=["database-content"])

@router.post("/generate")
async def generate_content_from_database(
    request: Dict[str, Any]
):
    """
    Generate content using only real database intelligence data
    NO mock data - requires actual campaign intelligence
    """
    try:
        content_type = request.get("content_type")
        campaign_id = request.get("campaign_id")
        user_id = request.get("user_id")
        company_id = request.get("company_id")
        preferences = request.get("preferences", {})
        
        if not all([content_type, campaign_id, user_id, company_id]):
            raise HTTPException(
                status_code=400,
                detail="content_type, campaign_id, user_id, and company_id are required"
            )
        
        async with ServiceFactory.create_service(DatabaseDrivenContentService) as service:
            result = await service.generate_content_from_intelligence(
                content_type=content_type,
                campaign_id=campaign_id,
                user_id=user_id,
                company_id=company_id,
                preferences=preferences
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns/{campaign_id}/readiness")
async def check_campaign_readiness(campaign_id: UUID):
    """Check if campaign has sufficient data for content generation"""
    try:
        async with ServiceFactory.create_service(ContentValidationService) as service:
            readiness = await service.validate_campaign_readiness(campaign_id)
        
        return {
            "success": True,
            "readiness": readiness
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/requirements")
async def get_content_generation_requirements():
    """Get requirements for database-driven content generation"""
    return {
        "requirements": {
            "intelligence_data": {
                "required": True,
                "source": "intelligence_core, product_data, market_data tables",
                "minimum_records": 1,
                "description": "Campaign must have intelligence analysis completed"
            },
            "email_templates": {
                "required_for": ["email", "email_sequence"],
                "source": "email_subject_templates table",
                "minimum_records": 1,
                "description": "Email generation requires templates in database"
            }
        },
        "supported_content_types": ["email", "email_sequence", "social_post", "blog_article", "ad_copy"],
        "no_mock_data": True,
        "database_driven_only": True
    }