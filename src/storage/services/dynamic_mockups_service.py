"""
Dynamic Mockups API Integration for Professional Mockup Generation
Tier-gated feature for PRO and ENTERPRISE users
"""

import os
import logging
import aiohttp
from typing import Dict, Any, Optional, List
from uuid import UUID

logger = logging.getLogger(__name__)


class DynamicMockupsService:
    """
    Professional mockup generation using Dynamic Mockups API

    Features:
    - Realistic product mockups (bottles, boxes, labels, t-shirts, mugs, etc.)
    - Fast rendering (1 second average)
    - Bulk mockup generation support
    - Custom Photoshop template support
    - Photo-realistic results

    Tier Access:
    - FREE/BASIC: Not available
    - PRO: Available (5 mockups/month included)
    - ENTERPRISE: Available (unlimited)

    API Docs: https://docs.dynamicmockups.com/
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.api_key = os.getenv("DYNAMIC_MOCKUPS_API_KEY")
        self.api_url = "https://app.dynamicmockups.com/api/v1"

        # Pricing - check Dynamic Mockups dashboard for current rates
        # Free tier available, paid plans start at $19/month
        self.cost_per_mockup = 0.10  # Approximate cost per mockup

        logger.info(f"✅ DynamicMockupsService v{self.VERSION} initialized")

    async def generate_mockup(
        self,
        image_url: str,
        mockup_uuid: str,
        smart_object_uuid: Optional[str] = None,
        product_name: Optional[str] = None,
        label_text: Optional[str] = None,
        user_tier: str = "FREE",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate professional mockup using Dynamic Mockups API

        Args:
            image_url: URL of base image to apply to mockup
            mockup_uuid: Dynamic Mockups template UUID
            smart_object_uuid: UUID of smart object layer to replace (optional)
            product_name: Product name for label (optional, for future text overlay)
            label_text: Additional label text (optional)
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
            logger.error("DYNAMIC_MOCKUPS_API_KEY not configured")
            return {
                "success": False,
                "error": "Mockup service not configured",
            }

        try:
            logger.info(f"🎨 Generating Dynamic Mockups mockup: {mockup_uuid}")

            # Build Dynamic Mockups API request
            payload = {
                "mockup_uuid": mockup_uuid,
                "smart_objects": [
                    {
                        "uuid": smart_object_uuid or "default",  # Will be template-specific
                        "asset": {
                            "url": image_url
                        }
                    }
                ]
            }

            # Add any additional parameters
            payload.update(kwargs)

            # Call Dynamic Mockups Render API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/renders",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                ) as response:

                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Dynamic Mockups API error: {error_text}")
                        return {
                            "success": False,
                            "error": f"Mockup generation failed: {error_text}"
                        }

                    result = await response.json()

                    # Extract mockup URL from response
                    mockup_url = result.get("url") or result.get("mockup_url")

                    logger.info(f"✅ Mockup generated successfully")

                    return {
                        "success": True,
                        "mockup_url": mockup_url,
                        "template_id": mockup_uuid,
                        "cost": self.cost_per_mockup,
                        "metadata": {
                            "provider": "dynamic_mockups",
                            "template": mockup_uuid,
                            "product_name": product_name,
                            "label_text": label_text,
                            "render_time": result.get("render_time", "~1s")
                        }
                    }

        except Exception as e:
            logger.error(f"Mockup generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_available_mockups(
        self,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch available mockup templates from Dynamic Mockups API

        Args:
            category: Optional category filter

        Returns:
            List of mockup template info dicts
        """

        if not self.api_key:
            logger.error("DYNAMIC_MOCKUPS_API_KEY not configured")
            return []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/mockups",
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    }
                ) as response:

                    if response.status != 200:
                        logger.error(f"Failed to fetch mockups: {response.status}")
                        return self._get_fallback_templates(category)

                    result = await response.json()
                    mockups = result.get("mockups", [])

                    # Filter by category if specified
                    if category:
                        mockups = [m for m in mockups if m.get("category") == category]

                    return mockups

        except Exception as e:
            logger.error(f"Error fetching mockups: {e}")
            return self._get_fallback_templates(category)

    def _get_fallback_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fallback template library when API is unavailable
        These are examples - real UUIDs come from Dynamic Mockups dashboard
        """

        templates = {
            "supplement": [
                {
                    "uuid": "supplement-bottle-3d-front",
                    "name": "3D Supplement Bottle - Front View",
                    "description": "Photo-realistic supplement bottle with custom label",
                    "category": "supplement",
                    "preview_url": "https://dynamicmockups.com/preview/supplement-bottle.jpg",
                    "smart_objects": [
                        {
                            "uuid": "front-label",
                            "name": "Front Label"
                        }
                    ]
                },
                {
                    "uuid": "supplement-bottle-angled",
                    "name": "Supplement Bottle - Angled View",
                    "description": "Angled view showing bottle depth and dimension",
                    "category": "supplement",
                    "preview_url": "https://dynamicmockups.com/preview/supplement-angled.jpg",
                    "smart_objects": [
                        {
                            "uuid": "label-layer",
                            "name": "Label"
                        }
                    ]
                },
                {
                    "uuid": "supplement-flat-lay",
                    "name": "Flat Lay Supplement Scene",
                    "description": "Top-down view with natural elements",
                    "category": "supplement",
                    "preview_url": "https://dynamicmockups.com/preview/supplement-flat.jpg",
                    "smart_objects": [
                        {
                            "uuid": "bottle-label",
                            "name": "Bottle Label"
                        }
                    ]
                }
            ],
            "lifestyle": [
                {
                    "uuid": "hand-holding-bottle",
                    "name": "Hand Holding Bottle",
                    "description": "Person holding supplement bottle",
                    "category": "lifestyle",
                    "preview_url": "https://dynamicmockups.com/preview/hand-holding.jpg",
                    "smart_objects": [
                        {
                            "uuid": "bottle-design",
                            "name": "Bottle Design"
                        }
                    ]
                },
                {
                    "uuid": "gym-scene",
                    "name": "Gym/Fitness Scene",
                    "description": "Product in athletic setting",
                    "category": "lifestyle",
                    "preview_url": "https://dynamicmockups.com/preview/gym-scene.jpg",
                    "smart_objects": [
                        {
                            "uuid": "product-label",
                            "name": "Product Label"
                        }
                    ]
                }
            ],
            "packaging": [
                {
                    "uuid": "box-mockup-3d",
                    "name": "3D Box Mockup",
                    "description": "Product box with custom design",
                    "category": "packaging",
                    "preview_url": "https://dynamicmockups.com/preview/box-3d.jpg",
                    "smart_objects": [
                        {
                            "uuid": "box-front",
                            "name": "Box Front"
                        }
                    ]
                }
            ]
        }

        if category:
            return templates.get(category, [])

        # Return all templates
        all_templates = []
        for cat_templates in templates.values():
            all_templates.extend(cat_templates)
        return all_templates

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
                "cost_per_additional": 0.10,
                "message": "5 mockups included, $0.10 each additional"
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
_dynamic_mockups_service = None

def get_dynamic_mockups_service() -> DynamicMockupsService:
    """Get or create DynamicMockupsService singleton"""
    global _dynamic_mockups_service
    if _dynamic_mockups_service is None:
        _dynamic_mockups_service = DynamicMockupsService()
    return _dynamic_mockups_service
