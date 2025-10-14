"""
API routes for image variation generation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import logging

from src.core.auth.dependencies import get_current_user
from src.users.models.user import User
from src.content.generators.image_variation_service import get_variation_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/variations",
    tags=["variations"]
)


class VariationRequest(BaseModel):
    """Request to generate image variation"""
    source_image_url: str = Field(..., description="URL of source image to vary")
    variation_strength: float = Field(
        0.3,
        ge=0.1,
        le=0.9,
        description="Variation strength: 0.1=subtle, 0.5=moderate, 0.9=strong"
    )
    provider: str = Field("dall-e", description="AI provider: dall-e, stability, flux")
    style_guidance: Optional[str] = Field(None, description="Optional style guidance text")


class VariationResponse(BaseModel):
    """Response from variation generation"""
    success: bool
    variation_url: Optional[str] = None
    cost: Optional[float] = None
    provider: Optional[str] = None
    variation_strength: Optional[float] = None
    error: Optional[str] = None


@router.post("/generate", response_model=VariationResponse)
async def generate_variation(
    request: VariationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a unique variation of an existing background scene

    **Use Cases:**
    - Create multiple unique versions of a successful scene
    - A/B test different scene variations
    - Avoid repetition across thousands of campaigns
    - Maintain style consistency with subtle differences

    **Variation Strength Guide:**
    - 0.1-0.3: Subtle changes (lighting, color adjustments)
    - 0.4-0.6: Moderate changes (some composition differences)
    - 0.7-0.9: Strong changes (significant variation)

    **Providers:**
    - dall-e: Best quality, automatic variations ($0.02)
    - stability: Most control over strength ($0.01)
    - flux: Fastest generation ($0.003)
    """

    try:
        logger.info(f"🎨 Variation requested by user {current_user.id}")

        # Get variation service
        variation_service = get_variation_service()

        # Generate variation
        result = await variation_service.generate_variation(
            source_image_url=request.source_image_url,
            variation_strength=request.variation_strength,
            provider=request.provider,
            style_guidance=request.style_guidance
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )

        logger.info(f"✅ Variation generated successfully (cost: ${result['cost']:.3f})")

        return VariationResponse(
            success=True,
            variation_url=result["url"],
            cost=result["cost"],
            provider=result["provider"],
            variation_strength=result.get("variation_strength")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Variation generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Variation generation failed: {str(e)}"
        )


@router.get("/pricing")
async def get_variation_pricing(
    current_user: User = Depends(get_current_user)
):
    """Get pricing information for image variations"""

    return {
        "success": True,
        "pricing": {
            "dall-e": {
                "cost_per_variation": 0.02,
                "quality": "Best",
                "speed": "Moderate",
                "description": "OpenAI DALL-E variations - highest quality"
            },
            "stability": {
                "cost_per_variation": 0.01,
                "quality": "High",
                "speed": "Fast",
                "description": "Stability AI img2img - most control over strength"
            },
            "flux": {
                "cost_per_variation": 0.003,
                "quality": "Good",
                "speed": "Fastest",
                "description": "Flux Schnell img2img - fastest generation"
            }
        },
        "use_cases": [
            "Create 10 unique versions of one successful scene",
            "A/B test variations to find best performer",
            "Generate library of similar but unique backgrounds",
            "Avoid scene repetition across campaigns"
        ]
    }
