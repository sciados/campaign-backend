"""
API routes for image manipulation operations
Modular endpoints for background removal, mockup generation, and compositing
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

from src.core.database.session import get_db
from src.core.auth.dependencies import get_current_user
from src.users.models.user import User
from src.storage.services.background_removal_service import get_background_removal_service
from src.storage.services.dynamic_mockups_service import get_dynamic_mockups_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/image-manipulation",
    tags=["image-manipulation"]
)


# ============= REQUEST/RESPONSE MODELS =============

class RemoveBackgroundRequest(BaseModel):
    """Request to remove background from image"""
    image_url: str = Field(..., description="URL of image to process")
    provider: Optional[str] = Field("remove.bg", description="Service provider (remove.bg, bfl, auto)")
    size: Optional[str] = Field("auto", description="Output size (auto, hd, full)")


class RemoveBackgroundResponse(BaseModel):
    """Response from background removal"""
    success: bool
    transparent_url: Optional[str] = None
    cost: Optional[float] = None
    provider: Optional[str] = None
    format: Optional[str] = None
    has_transparency: Optional[bool] = None
    credits_remaining: Optional[str] = None
    error: Optional[str] = None


class GenerateMockupRequest(BaseModel):
    """Request to generate mockup"""
    image_url: str = Field(..., description="URL of image to apply to mockup")
    mockup_uuid: str = Field(..., description="Mockup template UUID")
    smart_object_uuid: Optional[str] = Field(None, description="Smart object layer UUID")
    product_name: Optional[str] = Field(None, description="Product name")
    additional_params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class GenerateMockupResponse(BaseModel):
    """Response from mockup generation"""
    success: bool
    mockup_url: Optional[str] = None
    cost: Optional[float] = None
    mockup_uuid: Optional[str] = None
    error: Optional[str] = None
    upgrade_required: Optional[bool] = None


class GetProvidersResponse(BaseModel):
    """Information about available image manipulation providers"""
    success: bool
    providers: Dict[str, Any]
    recommended_provider: Optional[str] = None
    configured_count: int


# ============= ENDPOINTS =============

@router.post("/remove-background", response_model=RemoveBackgroundResponse)
async def remove_background(
    request: RemoveBackgroundRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove background from image to create transparent PNG

    **Features:**
    - AI-powered edge detection
    - Perfect for product images
    - Returns transparent PNG
    - Great for mockups and composites

    **Pricing:**
    - remove.bg: ~$0.20/image (or 50 free/month)
    - BFL: ~$0.10/image
    """

    try:
        user_id = current_user.id if hasattr(current_user, 'id') else current_user.get('id', 'unknown')
        logger.info(f"🎨 Background removal requested by user {user_id}")

        # Get background removal service
        bg_service = get_background_removal_service()

        # Remove background
        result = await bg_service.remove_background(
            image_url=request.image_url,
            provider=request.provider,
            size=request.size
        )

        if not result["success"]:
            return RemoveBackgroundResponse(
                success=False,
                error=result.get("error", "Background removal failed")
            )

        logger.info(f"✅ Background removed successfully (cost: ${result['cost']:.2f})")

        return RemoveBackgroundResponse(
            success=True,
            transparent_url=result["transparent_url"],
            cost=result["cost"],
            provider=result["provider"],
            format=result.get("format"),
            has_transparency=result.get("has_transparency"),
            credits_remaining=result.get("credits_remaining")
        )

    except Exception as e:
        logger.error(f"Background removal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Background removal failed: {str(e)}"
        )


@router.post("/generate-mockup", response_model=GenerateMockupResponse)
async def generate_mockup(
    request: GenerateMockupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate professional mockup from image

    **Tier Requirements:**
    - FREE/BASIC: Not available
    - PRO: 5 mockups/month included
    - ENTERPRISE: Unlimited

    **Features:**
    - Photo-realistic mockups
    - Fast rendering (~1 second)
    - Various templates (bottles, boxes, apparel, mugs)
    """

    try:
        # Get user tier
        if hasattr(current_user, 'subscription_tier'):
            user_tier = current_user.subscription_tier or "FREE"
        elif isinstance(current_user, dict):
            user_tier = current_user.get('subscription_tier', 'FREE')
        else:
            user_tier = "FREE"

        user_id = current_user.id if hasattr(current_user, 'id') else current_user.get('id', 'unknown')
        logger.info(f"🎨 Mockup generation requested by user {user_id} (tier: {user_tier})")

        # Get mockup service
        mockup_service = get_dynamic_mockups_service()

        # Generate mockup
        result = await mockup_service.generate_mockup(
            image_url=request.image_url,
            mockup_uuid=request.mockup_uuid,
            smart_object_uuid=request.smart_object_uuid,
            product_name=request.product_name,
            user_tier=user_tier,
            **request.additional_params
        )

        if not result["success"]:
            if result.get("upgrade_required"):
                return GenerateMockupResponse(
                    success=False,
                    error=result["error"],
                    upgrade_required=True
                )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )

        logger.info(f"✅ Mockup generated successfully (cost: ${result['cost']:.2f})")

        return GenerateMockupResponse(
            success=True,
            mockup_url=result["mockup_url"],
            cost=result["cost"],
            mockup_uuid=result["template_id"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mockup generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mockup generation failed: {str(e)}"
        )


@router.get("/providers", response_model=GetProvidersResponse)
async def get_providers(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about available image manipulation providers
    """

    try:
        # Get background removal providers
        bg_service = get_background_removal_service()
        bg_info = bg_service.get_provider_info()

        # Get mockup providers
        mockup_service = get_dynamic_mockups_service()

        # Get user tier
        if hasattr(current_user, 'subscription_tier'):
            user_tier = current_user.subscription_tier or "FREE"
        elif isinstance(current_user, dict):
            user_tier = current_user.get('subscription_tier', 'FREE')
        else:
            user_tier = "FREE"

        mockup_limits = mockup_service.get_tier_limits(user_tier)

        providers = {
            "background_removal": bg_info["providers"],
            "mockup_generation": {
                "dynamic_mockups": {
                    "available": mockup_limits["allowed"],
                    "tier_requirement": "PRO or ENTERPRISE",
                    "monthly_limit": mockup_limits["monthly_limit"],
                    "cost_per_additional": mockup_limits.get("cost_per_additional", 0),
                    "user_tier": user_tier,
                    "message": mockup_limits["message"]
                }
            }
        }

        return GetProvidersResponse(
            success=True,
            providers=providers,
            recommended_provider=bg_info["recommended"],
            configured_count=bg_info["configured_count"]
        )

    except Exception as e:
        logger.error(f"Error fetching providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
