"""
Image Variation Generation Service
Creates unique variations from existing background scenes
Supports: OpenAI DALL-E variations, Stability AI img2img, Flux img2img
"""

import logging
import os
import aiohttp
import base64
from typing import Dict, Any, Optional
from io import BytesIO

logger = logging.getLogger(__name__)


class ImageVariationService:
    """
    Generate variations of existing background scenes

    Features:
    - Create unique versions of successful scenes
    - Maintain overall composition and style
    - Subtle variations in lighting, color, elements
    - A/B testing capability
    - Avoid scene repetition across campaigns

    Providers:
    - OpenAI DALL-E variations (best quality)
    - Stability AI img2img (most control)
    - Flux Schnell img2img (fastest)
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
        self.replicate_api_token = os.getenv("REPLICATE_API_TOKEN")

        # Pricing
        self.variation_cost = {
            "dall-e": 0.02,      # $0.02 per variation
            "stability": 0.01,   # ~$0.01 per variation
            "flux": 0.003        # ~$0.003 per variation
        }

        logger.info(f"✅ ImageVariationService v{self.VERSION} initialized")

    async def generate_variation(
        self,
        source_image_url: str,
        variation_strength: float = 0.3,
        provider: str = "dall-e",
        style_guidance: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a unique variation of an existing scene

        Args:
            source_image_url: URL of the base scene image
            variation_strength: How different the variation should be (0.1-0.9)
                - 0.1-0.3: Subtle (lighting, color adjustments)
                - 0.4-0.6: Moderate (some composition changes)
                - 0.7-0.9: Strong (significant differences)
            provider: AI provider to use (dall-e, stability, flux)
            style_guidance: Optional text to guide variation style

        Returns:
            Dict with variation image URL, cost, and metadata
        """

        try:
            logger.info(f"🎨 Generating image variation (strength: {variation_strength}, provider: {provider})")

            # Download source image
            image_data = await self._download_image(source_image_url)

            # Generate variation based on provider
            if provider == "dall-e" and self.openai_api_key:
                result = await self._generate_dalle_variation(image_data, style_guidance)
            elif provider == "stability" and self.stability_api_key:
                result = await self._generate_stability_variation(
                    image_data,
                    variation_strength,
                    style_guidance
                )
            elif provider == "flux" and self.replicate_api_token:
                result = await self._generate_flux_variation(
                    image_data,
                    variation_strength,
                    style_guidance
                )
            else:
                return {
                    "success": False,
                    "error": f"Provider {provider} not configured or not available"
                }

            if result["success"]:
                logger.info(f"✅ Variation generated successfully (cost: ${result['cost']:.3f})")

            return result

        except Exception as e:
            logger.error(f"Variation generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _download_image(self, url: str) -> bytes:
        """Download image from URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download image: {response.status}")
                return await response.read()

    async def _generate_dalle_variation(
        self,
        image_data: bytes,
        style_guidance: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate variation using OpenAI DALL-E

        Uses DALL-E's edit mode with minimal mask to create variations
        """

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        try:
            # OpenAI variations endpoint
            url = "https://api.openai.com/v1/images/variations"

            # Prepare image for DALL-E (must be PNG, square, <4MB)
            from PIL import Image
            img = Image.open(BytesIO(image_data))

            # Ensure square and reasonable size
            size = min(img.size[0], img.size[1])
            size = min(size, 1024)  # Max 1024x1024 for variations

            img = img.resize((size, size), Image.Resampling.LANCZOS)

            # Convert to PNG
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            async with aiohttp.ClientSession() as session:
                form = aiohttp.FormData()
                form.add_field('image', img_buffer, filename='image.png', content_type='image/png')
                form.add_field('n', '1')  # Number of variations
                form.add_field('size', f'{size}x{size}')

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
                        raise Exception(f"DALL-E variation failed: {error_text}")

                    result = await response.json()
                    variation_url = result['data'][0]['url']

                    return {
                        "success": True,
                        "url": variation_url,
                        "provider": "dall-e",
                        "cost": self.variation_cost["dall-e"],
                        "variation_strength": "automatic",
                        "metadata": {
                            "size": f"{size}x{size}",
                            "style_guidance": style_guidance
                        }
                    }

        except Exception as e:
            logger.error(f"DALL-E variation failed: {e}")
            raise

    async def _generate_stability_variation(
        self,
        image_data: bytes,
        strength: float,
        style_guidance: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate variation using Stability AI img2img

        Provides most control over variation strength
        """

        if not self.stability_api_key:
            raise ValueError("STABILITY_API_KEY not configured")

        try:
            # Stability AI img2img endpoint
            url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

            # Prepare prompt for variation
            prompt = style_guidance or "Create a unique variation of this scene, maintaining overall composition but varying lighting, colors, and subtle details, professional background scene ready for product placement"

            async with aiohttp.ClientSession() as session:
                form = aiohttp.FormData()
                form.add_field('image', image_data, content_type='image/png')
                form.add_field('prompt', prompt)
                form.add_field('strength', str(strength))  # 0.0-1.0
                form.add_field('mode', 'image-to-image')
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
                        raise Exception(f"Stability variation failed: {error_text}")

                    # Get variation image
                    variation_data = await response.read()

                    # Convert to data URL
                    import base64
                    image_base64 = base64.b64encode(variation_data).decode('utf-8')
                    data_url = f"data:image/png;base64,{image_base64}"

                    return {
                        "success": True,
                        "url": data_url,
                        "provider": "stability",
                        "cost": self.variation_cost["stability"],
                        "variation_strength": strength,
                        "variation_data": variation_data,
                        "metadata": {
                            "prompt": prompt,
                            "style_guidance": style_guidance
                        }
                    }

        except Exception as e:
            logger.error(f"Stability variation failed: {e}")
            raise

    async def _generate_flux_variation(
        self,
        image_data: bytes,
        strength: float,
        style_guidance: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate variation using Flux Schnell img2img

        Fastest option for variations
        """

        if not self.replicate_api_token:
            raise ValueError("REPLICATE_API_TOKEN not configured")

        try:
            # Flux img2img via Replicate
            url = "https://api.replicate.com/v1/predictions"

            # Convert image to data URI
            import base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            data_uri = f"data:image/png;base64,{image_base64}"

            # Prepare prompt
            prompt = style_guidance or "Create a unique variation of this scene, maintaining composition but varying lighting and colors, professional background scene"

            payload = {
                "version": "black-forest-labs/flux-schnell",  # Fast model
                "input": {
                    "image": data_uri,
                    "prompt": prompt,
                    "strength": strength,
                    "num_outputs": 1
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.replicate_api_token}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                ) as response:

                    if response.status != 201:
                        error_text = await response.text()
                        logger.error(f"Flux error: {error_text}")
                        raise Exception(f"Flux variation failed: {error_text}")

                    result = await response.json()
                    prediction_url = result.get("urls", {}).get("get")

                    # Poll for completion
                    variation_url = await self._poll_replicate_result(prediction_url)

                    return {
                        "success": True,
                        "url": variation_url,
                        "provider": "flux",
                        "cost": self.variation_cost["flux"],
                        "variation_strength": strength,
                        "metadata": {
                            "prompt": prompt,
                            "style_guidance": style_guidance
                        }
                    }

        except Exception as e:
            logger.error(f"Flux variation failed: {e}")
            raise

    async def _poll_replicate_result(self, prediction_url: str, max_attempts: int = 30) -> str:
        """Poll Replicate for prediction result"""
        import asyncio

        async with aiohttp.ClientSession() as session:
            for attempt in range(max_attempts):
                async with session.get(
                    prediction_url,
                    headers={"Authorization": f"Bearer {self.replicate_api_token}"}
                ) as response:
                    result = await response.json()

                    if result.get("status") == "succeeded":
                        return result["output"][0]
                    elif result.get("status") == "failed":
                        raise Exception(f"Prediction failed: {result.get('error')}")

                    await asyncio.sleep(1)

        raise Exception("Prediction timed out")


# Singleton instance
_variation_service = None

def get_variation_service() -> ImageVariationService:
    """Get or create ImageVariationService singleton"""
    global _variation_service
    if _variation_service is None:
        _variation_service = ImageVariationService()
    return _variation_service
