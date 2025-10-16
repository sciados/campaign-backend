"""
AI Inpainting Service for Automatic Text Removal
Ensures clean images without gibberish text
"""

import os
import logging
import aiohttp
import base64
from typing import Dict, Any, Optional
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)


class InpaintingService:
    """
    Automatic text detection and removal using AI inpainting

    Features:
    - Detects text regions in images
    - Removes text using AI inpainting
    - Returns clean images ready
    - Minimal cost (~$0.01 per image)

    Providers:
    - Stability AI Inpainting (primary)
    - DALL-E Edit Mode (fallback)
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Pricing
        self.inpainting_cost = 0.01  # ~$0.01 per inpaint operation

        logger.info(f"✅ InpaintingService v{self.VERSION} initialized")

    async def remove_text_from_image(
        self,
        image_url: str,
        provider: str = "stability"
    ) -> Dict[str, Any]:
        """
        Automatically detect and remove text from image

        Args:
            image_url: URL of image to process
            provider: AI provider (stability, dall-e)

        Returns:
            Dict with cleaned image URL and metadata
        """

        try:
            logger.info(f"🧹 Removing text from image using {provider}")

            # Download image
            image_data = await self._download_image(image_url)

            if provider == "stability" and self.stability_api_key:
                result = await self._inpaint_with_stability(image_data)
            elif provider == "dall-e" and self.openai_api_key:
                result = await self._inpaint_with_dalle(image_data)
            else:
                return {
                    "success": False,
                    "error": "No inpainting provider configured",
                    "original_url": image_url
                }

            if result["success"]:
                logger.info(f"✅ Text removed successfully (cost: ${self.inpainting_cost:.3f})")

            return result

        except Exception as e:
            logger.error(f"Inpainting error: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_url": image_url  # Return original if cleanup fails
            }

    async def _download_image(self, url: str) -> bytes:
        """Download image from URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download image: {response.status}")
                return await response.read()

    async def _inpaint_with_stability(self, image_data: bytes) -> Dict[str, Any]:
        """
        Remove text using Stability AI Inpainting

        Uses automatic text detection + inpainting to clean the image
        """

        if not self.stability_api_key:
            raise ValueError("STABILITY_API_KEY not configured")

        try:
            # Stability AI Inpaint endpoint
            url = "https://api.stability.ai/v2beta/stable-image/edit/inpaint"

            # Create mask for text regions (we'll use a prompt-based approach)
            # Stability can auto-detect text regions with the right prompt

            async with aiohttp.ClientSession() as session:
                # Prepare multipart form data
                form = aiohttp.FormData()
                form.add_field('image', image_data, content_type='image/png')
                form.add_field('prompt', 'clean product photography, no text, no labels, pristine surface')
                form.add_field('search_prompt', 'text, letters, writing, labels, words')  # What to remove
                form.add_field('output_format', 'png')

                async with session.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.stability_api_key}",
                        "Accept": "image/*"
                    },
                    data=form
                ) as response:

                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Stability AI error: {error_text}")
                        raise Exception(f"Inpainting failed: {error_text}")

                    # Get cleaned image
                    cleaned_image_data = await response.read()

                    # Convert to base64 or upload to storage
                    # For now, return as data URL
                    import base64
                    image_base64 = base64.b64encode(cleaned_image_data).decode('utf-8')
                    data_url = f"data:image/png;base64,{image_base64}"

                    return {
                        "success": True,
                        "cleaned_url": data_url,
                        "provider": "stability",
                        "cost": self.inpainting_cost,
                        "cleaned_image_data": cleaned_image_data
                    }

        except Exception as e:
            logger.error(f"Stability inpainting failed: {e}")
            raise

    async def _inpaint_with_dalle(self, image_data: bytes) -> Dict[str, Any]:
        """
        Remove text using DALL-E Edit Mode

        Uses DALL-E's image editing capability with a mask
        """

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        try:
            # DALL-E Edit endpoint
            url = "https://api.openai.com/v1/images/edits"

            # For DALL-E, we need to create a mask highlighting text areas
            # For simplicity, we'll use a prompt-based approach

            async with aiohttp.ClientSession() as session:
                form = aiohttp.FormData()
                form.add_field('image', image_data, filename='image.png', content_type='image/png')
                form.add_field('prompt', 'remove all text and labels, clean blank surface')
                form.add_field('n', '1')
                form.add_field('size', '1024x1024')

                async with session.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}"
                    },
                    data=form
                ) as response:

                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"DALL-E error: {error_text}")
                        raise Exception(f"DALL-E inpainting failed: {error_text}")

                    result = await response.json()
                    cleaned_url = result['data'][0]['url']

                    return {
                        "success": True,
                        "cleaned_url": cleaned_url,
                        "provider": "dall-e",
                        "cost": self.inpainting_cost
                    }

        except Exception as e:
            logger.error(f"DALL-E inpainting failed: {e}")
            raise

    async def detect_text_in_image(self, image_url: str) -> Dict[str, Any]:
        """
        Detect if image contains text (optional pre-check)

        Uses OCR to detect text before deciding if inpainting is needed
        Can save costs by only inpainting when text is detected
        """

        try:
            # Download image
            image_data = await self._download_image(image_url)

            # Use Tesseract OCR or Google Vision API
            # For now, simplified version - always assume text exists
            # TODO: Add OCR detection to save costs

            return {
                "has_text": True,  # Assume text exists for now
                "confidence": 0.9,
                "text_detected": ["placeholder"]
            }

        except Exception as e:
            logger.error(f"Text detection error: {e}")
            return {
                "has_text": True,  # Safe default - clean the image
                "error": str(e)
            }


# Singleton instance
_inpainting_service = None

def get_inpainting_service() -> InpaintingService:
    """Get or create InpaintingService singleton"""
    global _inpainting_service
    if _inpainting_service is None:
        _inpainting_service = InpaintingService()
    return _inpainting_service
