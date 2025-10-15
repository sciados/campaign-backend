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
        # Get user's subscription tier directly from user
        if hasattr(current_user, 'subscription_tier'):
            user_tier = current_user.subscription_tier or "FREE"
        elif isinstance(current_user, dict):
            user_tier = current_user.get('subscription_tier', 'FREE')
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
        # Get user's subscription tier directly from user (now denormalized)
        if hasattr(current_user, 'subscription_tier'):
            user_tier = current_user.subscription_tier or "FREE"
            logger.info(f"🔍 User tier (direct): user_id={getattr(current_user, 'id', 'unknown')}, tier={user_tier}")
        elif isinstance(current_user, dict):
            user_tier = current_user.get('subscription_tier', 'FREE')
            logger.info(f"🔍 User tier (dict): user_id={current_user.get('id', 'unknown')}, tier={user_tier}")
        else:
            user_tier = "FREE"
            logger.info(f"🔍 User tier (fallback): type={type(current_user)}, tier={user_tier}")

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
        # Get user's subscription tier directly from user
        if hasattr(current_user, 'subscription_tier'):
            user_tier = current_user.subscription_tier or "FREE"
        elif isinstance(current_user, dict):
            user_tier = current_user.get('subscription_tier', 'FREE')
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


@router.get("/debug-api-connection")
async def debug_dynamic_mockups_api(
    current_user: User = Depends(get_current_user)
):
    """
    Debug endpoint to test Dynamic Mockups API connection
    Shows what templates are available in your account

    **Usage:**
    Visit: https://campaign-backend-production-e2db.up.railway.app/api/content/mockups/debug-api-connection

    This will show:
    - Whether API key is configured
    - API connection status
    - Number of templates in your account
    - Sample of available templates
    - Next steps if no templates found
    """

    try:
        import os
        import aiohttp

        api_key = os.getenv("DYNAMIC_MOCKUPS_API_KEY")

        if not api_key:
            return {
                "success": False,
                "error": "DYNAMIC_MOCKUPS_API_KEY not configured",
                "message": "Please add your Dynamic Mockups API key to Railway environment variables"
            }

        # Test API connection
        api_url = "https://app.dynamicmockups.com/api/v1"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{api_url}/mockups",
                headers={
                    "x-api-key": api_key,
                    "Accept": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                status_code = response.status
                response_text = await response.text()

                if status_code == 200:
                    try:
                        result = await response.json()
                    except:
                        result = {"data": []}

                    mockups = result.get("data", [])

                    # Extract useful info
                    template_info = []
                    for mockup in mockups[:10]:  # First 10 templates
                        template_info.append({
                            "uuid": mockup.get("uuid"),
                            "name": mockup.get("name"),
                            "thumbnail": mockup.get("thumbnail"),
                            "collections": [c.get("name") for c in mockup.get("collections", [])],
                            "smart_objects_count": len(mockup.get("smart_objects", []))
                        })

                    return {
                        "success": True,
                        "api_key_configured": True,
                        "api_key_preview": f"{api_key[:20]}...",
                        "api_connection": "✅ Working",
                        "status_code": status_code,
                        "templates_count": len(mockups),
                        "templates_preview": template_info,
                        "message": f"Found {len(mockups)} templates in your Dynamic Mockups account" if len(mockups) > 0 else "No templates found in your account",
                        "next_steps": [
                            "⚠️ No templates found in your Dynamic Mockups account",
                            "1. Visit https://app.dynamicmockups.com/",
                            "2. Click 'Upload Template' or 'New Template'",
                            "3. Upload your PSD files (supplement bottles, ebook covers, etc.)",
                            "4. Configure smart object layers (the editable areas)",
                            "5. Organize templates into collections",
                            "6. Templates will automatically appear in CampaignForge"
                        ] if len(mockups) == 0 else [
                            f"✅ Found {len(mockups)} templates ready to use!",
                            "Templates are automatically fetched from your Dynamic Mockups account",
                            "You can now generate mockups in CampaignForge"
                        ]
                    }
                elif status_code == 401:
                    return {
                        "success": False,
                        "api_key_configured": True,
                        "api_key_preview": f"{api_key[:20]}...",
                        "api_connection": "❌ Authentication Failed",
                        "status_code": status_code,
                        "error": "Invalid API key",
                        "message": "API key authentication failed",
                        "next_steps": [
                            "1. Check your API key in Dynamic Mockups dashboard",
                            "2. Go to https://app.dynamicmockups.com/settings/api",
                            "3. Generate a new API key if needed",
                            "4. Update DYNAMIC_MOCKUPS_API_KEY in Railway variables",
                            "5. Redeploy the backend service"
                        ]
                    }
                else:
                    return {
                        "success": False,
                        "api_key_configured": True,
                        "api_connection": "❌ Failed",
                        "status_code": status_code,
                        "error_response": response_text[:500],  # First 500 chars
                        "message": f"API returned error status code {status_code}",
                        "next_steps": [
                            "Check the error_response for details",
                            "Verify your API key has proper permissions",
                            "Make sure you're using the production API key (not a test key)",
                            "Contact Dynamic Mockups support if issue persists"
                        ]
                    }

    except aiohttp.ClientTimeout:
        logger.error("Dynamic Mockups API timeout")
        return {
            "success": False,
            "error": "API request timeout",
            "message": "Connection to Dynamic Mockups timed out after 30 seconds",
            "next_steps": [
                "Check your network connection",
                "Dynamic Mockups service might be experiencing issues",
                "Try again in a few minutes"
            ]
        }
    except Exception as e:
        logger.error(f"Debug API connection error: {e}")
        import traceback
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "message": "Failed to connect to Dynamic Mockups API"
        }
