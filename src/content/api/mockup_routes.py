"""
API routes for professional mockup generation (PRO/ENTERPRISE tier)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from src.core.database.session import get_db
from src.core.auth.dependencies import get_current_user
from src.users.models.user import User
from src.storage.services.dynamic_mockups_service import get_dynamic_mockups_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/mockups",
    tags=["mockups"]
)


class MockupGenerationRequest(BaseModel):
    """Request to generate professional mockup"""
    image_url: str = Field(..., description="URL of base image to apply to mockup")
    mockup_uuid: str = Field(..., description="Dynamic Mockups template UUID")
    smart_object_uuid: Optional[str] = Field(None, description="Smart object layer UUID")
    product_name: Optional[str] = Field(None, description="Product name for label")
    label_text: Optional[str] = Field(None, description="Additional label text")
    additional_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional template parameters")


class MockupGenerationResponse(BaseModel):
    """Response from mockup generation"""
    success: bool
    mockup_url: Optional[str] = None
    cost: Optional[float] = None
    mockup_uuid: Optional[str] = None
    error: Optional[str] = None
    upgrade_required: Optional[bool] = None
    feature: Optional[str] = None


class MockupTemplatesResponse(BaseModel):
    """List of available mockup templates"""
    success: bool
    templates: List[Dict[str, Any]]
    user_tier: str
    tier_limits: Dict[str, Any]


@router.post("/generate", response_model=MockupGenerationResponse)
async def generate_mockup(
    request: MockupGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate professional mockup using Dynamic Mockups API

    **Tier Requirements:**
    - FREE/BASIC: Not available
    - PRO: 5 mockups/month included, $0.10 each additional
    - ENTERPRISE: Unlimited mockups

    **Features:**
    - Realistic product mockups (bottles, boxes, labels, apparel, mugs)
    - Fast rendering (~1 second)
    - Custom Photoshop template support
    - Photo-realistic results
    """

    try:
        # Get user's subscription tier (handle both dict and object)
        if hasattr(current_user, 'company'):
            user_tier = current_user.company.subscription_tier if current_user.company else "FREE"
        elif isinstance(current_user, dict):
            user_tier = current_user.get('company', {}).get('subscription_tier', 'FREE') if current_user.get('company') else "FREE"
        else:
            user_tier = "FREE"

        user_id = current_user.id if hasattr(current_user, 'id') else current_user.get('id', 'unknown')
        logger.info(f"🎨 Mockup generation requested by user {user_id} (tier: {user_tier})")

        # Get Dynamic Mockups service
        mockup_service = get_dynamic_mockups_service()

        # Generate mockup (tier check happens inside service)
        result = await mockup_service.generate_mockup(
            image_url=request.image_url,
            mockup_uuid=request.mockup_uuid,
            smart_object_uuid=request.smart_object_uuid,
            product_name=request.product_name,
            label_text=request.label_text,
            user_tier=user_tier,
            **request.additional_params
        )

        if not result["success"]:
            # Check if upgrade required
            if result.get("upgrade_required"):
                return MockupGenerationResponse(
                    success=False,
                    error=result["error"],
                    upgrade_required=True,
                    feature=result.get("feature")
                )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )

        logger.info(f"✅ Mockup generated successfully (cost: ${result['cost']:.2f})")

        return MockupGenerationResponse(
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


@router.get("/templates", response_model=MockupTemplatesResponse)
async def get_mockup_templates(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get available mockup templates from Dynamic Mockups

    **Categories:**
    - supplement: Bottle and box mockups for supplements
    - lifestyle: Hand-holding, gym scenes, lifestyle shots
    - packaging: Product packaging variations
    - apparel: T-shirts, hoodies, etc.
    - drinkware: Mugs, tumblers, bottles
    """

    try:
        # Get user's subscription tier (handle both dict and object)
        if hasattr(current_user, 'company'):
            user_tier = current_user.company.subscription_tier if current_user.company else "FREE"
            logger.info(f"🔍 User tier detection (object): user_id={getattr(current_user, 'id', 'unknown')}, company={current_user.company}, tier={user_tier}")
        elif isinstance(current_user, dict):
            user_tier = current_user.get('company', {}).get('subscription_tier', 'FREE') if current_user.get('company') else "FREE"
            logger.info(f"🔍 User tier detection (dict): user_id={current_user.get('id', 'unknown')}, company={current_user.get('company')}, tier={user_tier}")
        else:
            user_tier = "FREE"
            logger.info(f"🔍 User tier detection (fallback): user_type={type(current_user)}, tier={user_tier}")

        # Get Dynamic Mockups service
        mockup_service = get_dynamic_mockups_service()

        # Get templates (will fetch from API or use fallback)
        templates = await mockup_service.get_available_mockups(category)

        # Get tier limits
        tier_limits = mockup_service.get_tier_limits(user_tier)

        return MockupTemplatesResponse(
            success=True,
            templates=templates,
            user_tier=user_tier,
            tier_limits=tier_limits
        )

    except Exception as e:
        logger.error(f"Error fetching mockup templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch templates: {str(e)}"
        )


@router.get("/tier-info")
async def get_tier_info(
    current_user: User = Depends(get_current_user)
):
    """Get mockup generation limits and pricing for user's tier"""

    try:
        # Get user's subscription tier (handle both dict and object)
        if hasattr(current_user, 'company'):
            user_tier = current_user.company.subscription_tier if current_user.company else "FREE"
        elif isinstance(current_user, dict):
            user_tier = current_user.get('company', {}).get('subscription_tier', 'FREE') if current_user.get('company') else "FREE"
        else:
            user_tier = "FREE"

        mockup_service = get_dynamic_mockups_service()
        tier_limits = mockup_service.get_tier_limits(user_tier)

        return {
            "success": True,
            "user_tier": user_tier,
            "limits": tier_limits,
            "feature": "professional_mockups"
        }

    except Exception as e:
        logger.error(f"Error fetching tier info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
