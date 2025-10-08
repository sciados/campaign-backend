# src/content/generators/image_generator.py
"""
AI-Powered Image Generator with Intelligence Integration
Uses modular architecture: Intelligence → Prompt → AI → Image
Supports multiple providers: OpenAI DALL-E 3, Replicate (Flux, SDXL)
"""

import logging
import os
import base64
import aiohttp
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timezone
from uuid import UUID
from io import BytesIO
from PIL import Image as PILImage

from src.content.services.prompt_generation_service import (
    PromptGenerationService,
    ContentType,
    SalesPsychologyStage
)

logger = logging.getLogger(__name__)


class ImageGenerator:
    """
    AI-powered Image Generator integrating with Intelligence Engine
    Implements modular architecture for marketing image generation
    """

    def __init__(self, db_session=None):
        self.name = "image_generator"
        self.version = "3.0.0"

        # Initialize modular services
        self.prompt_service = PromptGenerationService()

        # API keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.replicate_api_token = os.getenv("REPLICATE_API_TOKEN")

        # Optional: Prompt storage service
        self.db_session = db_session
        self.prompt_storage = None
        if db_session:
            from src.content.services.prompt_storage_service import PromptStorageService
            self.prompt_storage = PromptStorageService(db_session)

        self._generation_stats = {
            "images_generated": 0,
            "total_cost": 0.0,
            "prompts_saved": 0
        }

        logger.info(f"✅ ImageGenerator v{self.version} - Modular architecture with AI")

    async def generate_marketing_image(
        self,
        campaign_id: Union[str, UUID],
        intelligence_data: Dict[str, Any],
        image_type: str = "product_hero",
        style: str = "professional",
        dimensions: str = "1024x1024",
        provider: str = "dall-e-3",
        target_audience: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        user_id: Optional[Union[str, UUID]] = None
    ) -> Dict[str, Any]:
        """
        Generate marketing image using AI
        Implements Intelligence → Prompt → AI → Image pipeline

        Args:
            campaign_id: Campaign identifier
            intelligence_data: Campaign intelligence from analysis
            image_type: Type of image (product_hero, lifestyle, comparison, infographic, social_post)
            style: Visual style (professional, modern, vibrant, minimalist, dramatic)
            dimensions: Image size (1024x1024, 1792x1024, 1024x1792)
            provider: AI provider (dall-e-3, flux-schnell, sdxl)
            target_audience: Optional audience description
            preferences: Additional generation preferences

        Returns:
            Dictionary with generated image data
        """

        if preferences is None:
            preferences = {}

        try:
            logger.info(f"🎨 Generating {image_type} image ({dimensions}) for campaign {campaign_id}")

            # Enhance intelligence data with preferences
            if target_audience:
                if "psychology_intelligence" not in intelligence_data:
                    intelligence_data["psychology_intelligence"] = {}
                intelligence_data["psychology_intelligence"]["target_audience"] = target_audience

            if style:
                if "brand_intelligence" not in intelligence_data:
                    intelligence_data["brand_intelligence"] = {}
                intelligence_data["brand_intelligence"]["visual_style"] = style

            # Add image-specific preferences
            preferences["image_type"] = image_type
            preferences["style"] = style
            preferences["dimensions"] = dimensions

            # Step 1: Generate optimized image prompt from intelligence
            image_prompt = await self._generate_image_prompt(
                intelligence_data=intelligence_data,
                image_type=image_type,
                style=style,
                preferences=preferences
            )

            logger.info(f"✅ Generated image prompt: {image_prompt[:100]}...")

            # Step 2: Generate image using AI provider
            if provider == "dall-e-3":
                image_result = await self._generate_with_dalle3(
                    prompt=image_prompt,
                    dimensions=dimensions
                )
            elif provider == "flux-schnell":
                image_result = await self._generate_with_flux(
                    prompt=image_prompt,
                    dimensions=dimensions
                )
            elif provider == "sdxl":
                image_result = await self._generate_with_sdxl(
                    prompt=image_prompt,
                    dimensions=dimensions
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            if not image_result["success"]:
                raise Exception(f"Image generation failed: {image_result.get('error')}")

            logger.info(f"✅ AI generated image using {provider} (cost: ${image_result.get('cost', 0):.4f})")

            # Update stats
            self._generation_stats["images_generated"] += 1
            self._generation_stats["total_cost"] += image_result.get("cost", 0)

            return {
                "success": True,
                "campaign_id": str(campaign_id),
                "image": {
                    "url": image_result["url"],
                    "local_path": image_result.get("local_path"),
                    "dimensions": dimensions,
                    "image_type": image_type,
                    "style": style,
                    "provider": provider
                },
                "prompt": image_prompt,
                "generation_metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "generator_version": self.version,
                    "provider": provider,
                    "cost": image_result.get("cost", 0),
                    "generation_time": image_result.get("generation_time", 0),
                    "intelligence_enhanced": True
                }
            }

        except Exception as e:
            logger.error(f"❌ Image generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "campaign_id": str(campaign_id)
            }

    async def _generate_image_prompt(
        self,
        intelligence_data: Dict[str, Any],
        image_type: str,
        style: str,
        preferences: Dict[str, Any]
    ) -> str:
        """Generate detailed image prompt from intelligence data"""

        product_name = intelligence_data.get("product_name", "Product")
        primary_benefit = intelligence_data.get("offer_intelligence", {}).get("benefits", ["quality"])[0] if intelligence_data.get("offer_intelligence", {}).get("benefits") else "quality"
        target_audience = intelligence_data.get("psychology_intelligence", {}).get("target_audience", "consumers")

        # Base prompt templates by image type
        prompts = {
            "product_hero": f"Professional product photography of {product_name}, hero shot, {style} style, studio lighting, high-end commercial quality, focus on {primary_benefit}, appealing to {target_audience}",
            "lifestyle": f"Lifestyle photography featuring {product_name} in use, {style} aesthetic, real-world setting, happy {target_audience} using the product, natural lighting, authentic moment",
            "comparison": f"Before and after comparison image for {product_name}, split-screen layout, {style} design, showing transformation and {primary_benefit}, clean professional presentation",
            "infographic": f"Modern infographic design explaining {primary_benefit} of {product_name}, {style} color scheme, clean layout, data visualization, professional business graphics",
            "social_post": f"Eye-catching social media image for {product_name}, {style} aesthetic, bold colors, text-friendly composition, attention-grabbing for {target_audience}"
        }

        base_prompt = prompts.get(image_type, prompts["product_hero"])

        # Enhance with style details
        style_enhancements = {
            "professional": "corporate aesthetic, clean lines, sophisticated color palette, high-end presentation",
            "modern": "contemporary design, minimalist, trendy, sleek composition",
            "vibrant": "bold colors, energetic, eye-catching, dynamic composition",
            "minimalist": "simple, clean, white space, elegant, understated",
            "dramatic": "high contrast, dramatic lighting, bold shadows, cinematic"
        }

        enhancement = style_enhancements.get(style, style_enhancements["professional"])
        full_prompt = f"{base_prompt}, {enhancement}"

        # Add technical quality requirements
        full_prompt += ", ultra high quality, 8k resolution, professional commercial photography, sharp focus, perfect composition"

        return full_prompt

    async def _generate_with_dalle3(
        self,
        prompt: str,
        dimensions: str
    ) -> Dict[str, Any]:
        """Generate image using OpenAI DALL-E 3"""

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        import time
        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "dall-e-3",
                        "prompt": prompt,
                        "n": 1,
                        "size": dimensions,
                        "quality": "hd",
                        "style": "vivid"
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"DALL-E 3 API error: {error_text}")

                    result = await response.json()
                    image_url = result["data"][0]["url"]

                    generation_time = time.time() - start_time

                    # DALL-E 3 pricing: $0.040 per image (1024x1024 standard), $0.080 (HD)
                    cost = 0.080  # HD quality

                    return {
                        "success": True,
                        "url": image_url,
                        "cost": cost,
                        "generation_time": generation_time
                    }

        except Exception as e:
            logger.error(f"DALL-E 3 generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_with_flux(
        self,
        prompt: str,
        dimensions: str
    ) -> Dict[str, Any]:
        """Generate image using Replicate Flux Schnell (fast & cheap)"""

        if not self.replicate_api_token:
            raise ValueError("REPLICATE_API_TOKEN not configured")

        import time
        start_time = time.time()

        # Parse dimensions
        width, height = map(int, dimensions.split('x'))

        try:
            async with aiohttp.ClientSession() as session:
                # Create prediction
                async with session.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {self.replicate_api_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "version": "f2ab8a5bfe79f02f0789a146cf5e73d2a4ff2684a98c2b303d1e1ff3814271db",  # flux-schnell
                        "input": {
                            "prompt": prompt,
                            "width": width,
                            "height": height,
                            "num_outputs": 1
                        }
                    }
                ) as response:
                    if response.status != 201:
                        error_text = await response.text()
                        raise Exception(f"Replicate API error: {error_text}")

                    prediction = await response.json()
                    prediction_id = prediction["id"]

                # Poll for completion (Flux Schnell is fast, ~1-3 seconds)
                import asyncio
                for _ in range(30):  # 30 second timeout
                    await asyncio.sleep(1)

                    async with session.get(
                        f"https://api.replicate.com/v1/predictions/{prediction_id}",
                        headers={"Authorization": f"Token {self.replicate_api_token}"}
                    ) as response:
                        prediction = await response.json()

                        if prediction["status"] == "succeeded":
                            image_url = prediction["output"][0]
                            generation_time = time.time() - start_time

                            # Flux Schnell pricing: ~$0.003 per image
                            cost = 0.003

                            return {
                                "success": True,
                                "url": image_url,
                                "cost": cost,
                                "generation_time": generation_time
                            }
                        elif prediction["status"] == "failed":
                            raise Exception(f"Flux generation failed: {prediction.get('error')}")

                raise Exception("Flux generation timeout")

        except Exception as e:
            logger.error(f"Flux generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_with_sdxl(
        self,
        prompt: str,
        dimensions: str
    ) -> Dict[str, Any]:
        """Generate image using Stable Diffusion XL (balanced quality/cost)"""

        if not self.replicate_api_token:
            raise ValueError("REPLICATE_API_TOKEN not configured")

        # Similar implementation to Flux but with SDXL model
        # SDXL pricing: ~$0.0055 per image
        logger.warning("SDXL generation not yet implemented, falling back to Flux")
        return await self._generate_with_flux(prompt, dimensions)

    def get_stats(self) -> Dict[str, Any]:
        """Get image generator statistics"""
        return {
            "generator": self.name,
            "version": self.version,
            "stats": self._generation_stats
        }
