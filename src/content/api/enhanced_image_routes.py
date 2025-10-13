# src/content/api/enhanced_image_routes.py
"""
Enhanced Platform-Specific Image Generation API Routes
Integrates with existing content generation system
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from src.core.database.session import get_async_db
from src.users.services.auth_service import AuthService
from src.content.services.integrated_content_service import IntegratedContentService

router = APIRouter(prefix="/api/content/enhanced-images", tags=["enhanced-images"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Request models
class PlatformImageRequest(BaseModel):
    campaign_id: str
    platform_format: str
    image_type: str = "marketing"
    style_preferences: Optional[Dict[str, Any]] = None
    user_tier: str = "professional"

class MultiPlatformImageRequest(BaseModel):
    campaign_id: str
    platforms: List[str]
    image_type: str = "marketing"
    batch_style: Optional[Dict[str, Any]] = None
    user_tier: str = "professional"

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
) -> str:
    """Get current user ID from token"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return str(user.id)

@router.get("/platform-specs")
async def get_platform_specifications():
    """Get all available platform specifications"""
    from src.content.generators.enhanced_platform_image_generator import create_enhanced_platform_image_generator
    
    generator = create_enhanced_platform_image_generator()
    
    return {
        "success": True,
        "platform_specs": generator.get_platform_specs(),
        "total_platforms": len(generator.PLATFORM_SPECS),
        "categories": {
            "Instagram": ["instagram_feed", "instagram_story", "instagram_reel_cover"],
            "Facebook": ["facebook_feed", "facebook_story"],
            "LinkedIn": ["linkedin_feed", "linkedin_article"],
            "Twitter/X": ["twitter_feed"],
            "TikTok": ["tiktok_cover"],
            "YouTube": ["youtube_thumbnail"],
            "Pinterest": ["pinterest_pin"],
            "General": ["square", "landscape"]
        }
    }

@router.post("/generate-platform")
async def generate_platform_image(
    request: PlatformImageRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Generate single platform-optimized image using existing content service"""
    
    try:
        # Use existing IntegratedContentService
        content_service = IntegratedContentService(db)
        
        # Get user and company info from campaign
        from src.core.crud.campaign_crud import CampaignCRUD
        campaign_crud = CampaignCRUD()
        campaign = await campaign_crud.get_campaign(db, request.campaign_id)
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Generate using existing service with enhanced image generator
        result = await content_service.generate_content(
            campaign_id=request.campaign_id,
            content_type="platform_image",
            user_id=user_id,
            company_id=campaign.company_id,
            preferences={
                "platform_format": request.platform_format,
                "image_type": request.image_type,
                "style_preferences": request.style_preferences or {},
                "user_tier": request.user_tier
            }
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Image generation failed: {result.get('error')}"
            )
        
        return {
            "success": True,
            "message": f"Generated platform image successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Platform image generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate platform image: {str(e)}"
        )

@router.post("/generate-batch")
async def generate_multi_platform_batch(
    request: MultiPlatformImageRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Generate multi-platform image batch using existing content service"""
    
    try:
        # Use existing IntegratedContentService
        content_service = IntegratedContentService(db)
        
        # Get user and company info from campaign
        from src.core.crud.campaign_crud import CampaignCRUD
        campaign_crud = CampaignCRUD()
        campaign = await campaign_crud.get_campaign(db, request.campaign_id)
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Generate using existing service
        result = await content_service.generate_content(
            campaign_id=request.campaign_id,
            content_type="multi_platform_image",
            user_id=user_id,
            company_id=campaign.company_id,
            preferences={
                "platforms": request.platforms,
                "image_type": request.image_type,
                "batch_style": request.batch_style or {},
                "user_tier": request.user_tier
            }
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Batch generation failed: {result.get('error')}"
            )
        
        return {
            "success": True,
            "message": f"Generated batch for {len(request.platforms)} platforms",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multi-platform generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate multi-platform batch: {str(e)}"
        )

@router.get("/cost-calculator")
async def calculate_generation_cost(
    platforms: str,  # Comma-separated platform list
    user_tier: str = "professional"
):
    """Calculate cost for multi-platform generation"""
    
    try:
        platform_list = [p.strip() for p in platforms.split(",")]
        
        from src.content.generators.enhanced_platform_image_generator import create_enhanced_platform_image_generator
        generator = create_enhanced_platform_image_generator()
        
        cost_calculation = generator.calculate_batch_cost(platform_list, user_tier)
        
        return {
            "success": True,
            "cost_calculation": cost_calculation
        }
        
    except Exception as e:
        logger.error(f"Cost calculation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate cost: {str(e)}"
        )

@router.get("/generator-stats")
async def get_generator_statistics(
    user_id: str = Depends(get_current_user_id)
):
    """Get image generator statistics"""
    
    try:
        from src.content.generators.enhanced_platform_image_generator import create_enhanced_platform_image_generator
        generator = create_enhanced_platform_image_generator()
        
        stats = generator.get_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )