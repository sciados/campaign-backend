"""
Placeit API Integration for Professional Mockup Generation
Tier-gated feature for PRO and ENTERPRISE users
"""

import os
import logging
import aiohttp
from typing import Dict, Any, Optional, List
from uuid import UUID

logger = logging.getLogger(__name__)


class PlaceitService:
    """
    Professional mockup generation using Placeit API

    Features:
    - Realistic product mockups (bottles, boxes, labels)
    - Automatic curved text with proper perspective
    - Photo-realistic results
    - Template library for different product types

    Tier Access:
    - FREE/BASIC: Not available
    - PRO: Available (5 mockups/month included)
    - ENTERPRISE: Available (unlimited)
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.api_key = os.getenv("PLACEIT_API_KEY")
        self.api_url = "https://api.placeit.net/v1"

        # Pricing (approximate - check Placeit for current rates)
        self.cost_per_mockup = 0.50  # $0.50 per mockup generation

        logger.info(f"✅ PlaceitService v{self.VERSION} initialized")

    async def generate_mockup(
        self,
        image_url: str,
        template_id: str,
        product_name: Optional[str] = None,
        label_text: Optional[str] = None,
        user_tier: str = "FREE",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate professional mockup using Placeit API

        Args:
            image_url: URL of base image to apply to mockup
            template_id: Placeit template ID (e.g., "supplement_bottle_3d")
            product_name: Product name for label
            label_text: Additional label text (benefits, tagline)
            user_tier: User subscription tier (FREE, BASIC, PRO, ENTERPRISE)
            **kwargs: Additional template parameters

        Returns:
            Dict with mockup URL, cost, and metadata
        """

        # Check tier access
        if user_tier not in ["PRO", "ENTERPRISE"]:
            return {
                "success": False,
                "error": "Mockup generation requires PRO or ENTERPRISE tier",
                "upgrade_required": True,
                "feature": "professional_mockups"
            }

        if not self.api_key:
            logger.error("PLACEIT_API_KEY not configured")
            return {
                "success": False,
                "error": "Mockup service not configured",
            }

        try:
            logger.info(f"🎨 Generating Placeit mockup with template: {template_id}")

            # Build Placeit API request
            payload = {
                "template": template_id,
                "image_url": image_url,
            }

            # Add optional text overlays
            if product_name:
                payload["product_name"] = product_name
            if label_text:
                payload["label_text"] = label_text

            # Add any additional template parameters
            payload.update(kwargs)

            # Call Placeit API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/mockups",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                ) as response:

                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Placeit API error: {error_text}")
                        return {
                            "success": False,
                            "error": f"Mockup generation failed: {error_text}"
                        }

                    result = await response.json()

                    logger.info(f"✅ Mockup generated successfully")

                    return {
                        "success": True,
                        "mockup_url": result.get("url"),
                        "template_id": template_id,
                        "cost": self.cost_per_mockup,
                        "metadata": {
                            "provider": "placeit",
                            "template": template_id,
                            "product_name": product_name,
                            "label_text": label_text,
                        }
                    }

        except Exception as e:
            logger.error(f"Mockup generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_available_templates(self, category: str = "supplement") -> List[Dict[str, Any]]:
        """
        Get list of available mockup templates

        Args:
            category: Template category (supplement, beauty, beverage, etc.)

        Returns:
            List of template info dicts
        """

        # Template library - these would come from Placeit API in production
        templates = {
            "supplement": [
                {
                    "id": "supplement_bottle_3d",
                    "name": "3D Supplement Bottle",
                    "description": "Photo-realistic supplement bottle with custom label",
                    "preview_url": "https://placeit.net/templates/supplement_bottle_3d.jpg"
                },
                {
                    "id": "supplement_bottle_flat",
                    "name": "Flat Lay Supplement Bottle",
                    "description": "Top-down flat lay with bottle and natural elements",
                    "preview_url": "https://placeit.net/templates/supplement_bottle_flat.jpg"
                },
                {
                    "id": "supplement_box_mockup",
                    "name": "Supplement Box Mockup",
                    "description": "Product box with custom label design",
                    "preview_url": "https://placeit.net/templates/supplement_box.jpg"
                },
                {
                    "id": "supplement_label_closeup",
                    "name": "Label Close-up",
                    "description": "Close-up of bottle label with depth",
                    "preview_url": "https://placeit.net/templates/supplement_label.jpg"
                }
            ],
            "lifestyle": [
                {
                    "id": "hand_holding_bottle",
                    "name": "Hand Holding Bottle",
                    "description": "Person holding supplement bottle",
                    "preview_url": "https://placeit.net/templates/hand_holding.jpg"
                },
                {
                    "id": "gym_scene_bottle",
                    "name": "Gym Scene",
                    "description": "Bottle in gym/fitness setting",
                    "preview_url": "https://placeit.net/templates/gym_scene.jpg"
                }
            ]
        }

        return templates.get(category, [])

    def get_tier_limits(self, user_tier: str) -> Dict[str, Any]:
        """Get mockup generation limits by tier"""

        limits = {
            "FREE": {
                "allowed": False,
                "monthly_limit": 0,
                "message": "Upgrade to PRO for professional mockups"
            },
            "BASIC": {
                "allowed": False,
                "monthly_limit": 0,
                "message": "Upgrade to PRO for professional mockups"
            },
            "PRO": {
                "allowed": True,
                "monthly_limit": 5,
                "cost_per_additional": 0.50,
                "message": "5 mockups included, $0.50 each additional"
            },
            "ENTERPRISE": {
                "allowed": True,
                "monthly_limit": -1,  # Unlimited
                "cost_per_additional": 0,
                "message": "Unlimited mockups included"
            }
        }

        return limits.get(user_tier, limits["FREE"])


# Singleton instance
_placeit_service = None

def get_placeit_service() -> PlaceitService:
    """Get or create PlaceitService singleton"""
    global _placeit_service
    if _placeit_service is None:
        _placeit_service = PlaceitService()
    return _placeit_service
