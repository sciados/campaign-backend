"""
Background Removal Service for Product Images
Automatically removes backgrounds to create transparent PNG images
"""

import os
import logging
import aiohttp
from typing import Dict, Any, Optional
from io import BytesIO

logger = logging.getLogger(__name__)


class BackgroundRemovalService:
    """
    Automatic background removal for product images

    Features:
    - AI-powered background removal
    - Returns transparent PNG
    - High-quality edge detection
    - Perfect for composites

    Providers:
    - remove.bg API (primary) - Best quality
    - BFL API (fallback) - Good for complex products

    Pricing:
    - remove.bg: ~$0.20 per image (or free tier: 50/month)
    - BFL: ~$0.10 per image
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.removebg_api_key = os.getenv("REMOVE_BG_API_KEY")
        self.bfl_api_key = os.getenv("BFL_API_KEY")

        # Pricing
        self.removebg_cost = 0.20  # $0.20 per image
        self.bfl_cost = 0.10  # $0.10 per image

        logger.info(f"✅ BackgroundRemovalService v{self.VERSION} initialized")

    async def remove_background(
        self,
        image_url: str,
        provider: str = "remove.bg",
        size: str = "auto"
    ) -> Dict[str, Any]:
        """
        Remove background from image

        Args:
            image_url: URL of image to process
            provider: Service provider (remove.bg, bfl)
            size: Output size (auto, hd, full)

        Returns:
            Dict with transparent PNG URL and metadata
        """

        try:
            logger.info(f"🎨 Removing background using {provider}")

            if provider == "remove.bg" and self.removebg_api_key:
                result = await self._remove_bg_with_removebg(image_url, size)
            elif provider == "bfl" and self.bfl_api_key:
                result = await self._remove_bg_with_bfl(image_url)
            else:
                # Try both in order
                if self.removebg_api_key:
                    result = await self._remove_bg_with_removebg(image_url, size)
                elif self.bfl_api_key:
                    result = await self._remove_bg_with_bfl(image_url)
                else:
                    return {
                        "success": False,
                        "error": "No background removal provider configured. Set REMOVE_BG_API_KEY or BFL_API_KEY."
                    }

            if result["success"]:
                logger.info(f"✅ Background removed successfully (cost: ${result.get('cost', 0):.3f})")

            return result

        except Exception as e:
            logger.error(f"Background removal error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _remove_bg_with_removebg(
        self,
        image_url: str,
        size: str = "auto"
    ) -> Dict[str, Any]:
        """
        Remove background using remove.bg API

        Best quality, great edge detection
        """

        if not self.removebg_api_key:
            raise ValueError("REMOVE_BG_API_KEY not configured")

        try:
            url = "https://api.remove.bg/v1.0/removebg"

            async with aiohttp.ClientSession() as session:
                # Prepare request
                data = aiohttp.FormData()
                data.add_field('image_url', image_url)
                data.add_field('size', size)  # auto, hd, full
                data.add_field('format', 'png')  # Return PNG with transparency

                async with session.post(
                    url,
                    headers={
                        "X-Api-Key": self.removebg_api_key
                    },
                    data=data
                ) as response:

                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"remove.bg API error: {error_text}")
                        raise Exception(f"Background removal failed: {error_text}")

                    # Get transparent PNG
                    png_data = await response.read()

                    # Convert to base64 data URL for immediate use
                    import base64
                    image_base64 = base64.b64encode(png_data).decode('utf-8')
                    data_url = f"data:image/png;base64,{image_base64}"

                    # Get API credits info from headers
                    credits_remaining = response.headers.get('X-Credits-Remaining', 'unknown')

                    return {
                        "success": True,
                        "transparent_url": data_url,
                        "transparent_image_data": png_data,
                        "provider": "remove.bg",
                        "cost": self.removebg_cost,
                        "format": "png",
                        "has_transparency": True,
                        "credits_remaining": credits_remaining
                    }

        except Exception as e:
            logger.error(f"remove.bg failed: {e}")
            raise

    async def _remove_bg_with_bfl(self, image_url: str) -> Dict[str, Any]:
        """
        Remove background using BFL API

        Good alternative with competitive pricing
        """

        if not self.bfl_api_key:
            raise ValueError("BFL_API_KEY not configured")

        try:
            # BFL background removal endpoint
            url = "https://api.bfl.ml/v1/background-removal"

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers={
                        "x-key": self.bfl_api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "image_url": image_url,
                        "output_format": "png"
                    }
                ) as response:

                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"BFL API error: {error_text}")
                        raise Exception(f"Background removal failed: {error_text}")

                    result = await response.json()
                    transparent_url = result.get("sample") or result.get("result_url")

                    if not transparent_url:
                        raise Exception("BFL API did not return image URL")

                    return {
                        "success": True,
                        "transparent_url": transparent_url,
                        "provider": "bfl",
                        "cost": self.bfl_cost,
                        "format": "png",
                        "has_transparency": True,
                        "task_id": result.get("id")
                    }

        except Exception as e:
            logger.error(f"BFL background removal failed: {e}")
            raise

    def get_provider_info(self) -> Dict[str, Any]:
        """Get available providers and their status"""

        providers = {
            "remove.bg": {
                "available": bool(self.removebg_api_key),
                "cost_per_image": self.removebg_cost,
                "quality": "excellent",
                "features": ["AI edge detection", "Hair/fur quality", "Fast processing"]
            },
            "bfl": {
                "available": bool(self.bfl_api_key),
                "cost_per_image": self.bfl_cost,
                "quality": "good",
                "features": ["Complex objects", "Competitive pricing"]
            }
        }

        return {
            "providers": providers,
            "recommended": "remove.bg" if self.removebg_api_key else "bfl",
            "configured_count": sum(1 for p in providers.values() if p["available"])
        }


# Singleton instance
_background_removal_service = None

def get_background_removal_service() -> BackgroundRemovalService:
    """Get or create BackgroundRemovalService singleton"""
    global _background_removal_service
    if _background_removal_service is None:
        _background_removal_service = BackgroundRemovalService()
    return _background_removal_service
