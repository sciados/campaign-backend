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
        self.version = "3.2.0"

        # Initialize modular services
        self.prompt_service = PromptGenerationService()

        # Initialize prompt storage (optional)
        self.prompt_storage = None
        if db_session:
            from src.content.services.prompt_storage_service import PromptStorageService
            self.prompt_storage = PromptStorageService(db_session)

        # API keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.replicate_api_token = os.getenv("REPLICATE_API_TOKEN")

        # Initialize Cloudflare R2 storage
        from src.storage.services.cloudflare_service import CloudflareService
        self.storage_service = CloudflareService()

        self._generation_stats = {
            "images_generated": 0,
            "total_cost": 0.0,
            "prompts_saved": 0,
            "images_uploaded": 0
        }

        logger.info(f"✅ ImageGenerator v{self.version} - Modular architecture with AI + R2 storage")

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

            # Step 2: Generate image using AI provider with automatic fallback
            # Try providers in order until one succeeds (handle insufficient credits)
            providers_to_try = [provider]  # Start with requested provider

            # Add fallback providers (cheapest first for cost optimization)
            all_providers = ["flux-schnell", "sdxl", "dall-e-3"]
            for p in all_providers:
                if p not in providers_to_try:
                    providers_to_try.append(p)

            image_result = None
            last_error = None

            for attempt_provider in providers_to_try:
                try:
                    logger.info(f"🔄 Attempting image generation with {attempt_provider}...")

                    if attempt_provider == "dall-e-3":
                        image_result = await self._generate_with_dalle3(
                            prompt=image_prompt,
                            dimensions=dimensions
                        )
                    elif attempt_provider == "flux-schnell":
                        image_result = await self._generate_with_flux(
                            prompt=image_prompt,
                            dimensions=dimensions
                        )
                    elif attempt_provider == "sdxl":
                        image_result = await self._generate_with_sdxl(
                            prompt=image_prompt,
                            dimensions=dimensions
                        )
                    else:
                        logger.warning(f"⚠️ Unsupported provider: {attempt_provider}, skipping...")
                        continue

                    if image_result["success"]:
                        logger.info(f"✅ Image generation succeeded with {attempt_provider}")
                        provider = attempt_provider  # Update provider to the one that worked
                        break
                    else:
                        last_error = image_result.get('error')
                        logger.warning(f"⚠️ {attempt_provider} failed: {last_error}")

                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"⚠️ {attempt_provider} error: {last_error}")
                    # Check if it's an insufficient credit error
                    if "insufficient" in last_error.lower() or "quota" in last_error.lower() or "credit" in last_error.lower():
                        logger.info(f"💳 Insufficient credits for {attempt_provider}, trying next provider...")
                        continue
                    # For other errors, also try next provider
                    continue

            # If all providers failed
            if not image_result or not image_result["success"]:
                raise Exception(f"Image generation failed with all providers. Last error: {last_error}")

            logger.info(f"✅ AI generated image using {provider} (cost: ${image_result.get('cost', 0):.4f})")

            # Save prompt to database for future reuse (if storage available)
            prompt_id = None
            if self.prompt_storage:
                try:
                    # Use provided user_id or fallback to system UUID if not provided
                    storage_user_id = str(user_id) if user_id else "00000000-0000-0000-0000-000000000000"

                    # Create mock prompt_result and ai_result structures for storage
                    mock_prompt_result = {
                        "success": True,
                        "prompt": image_prompt,
                        "system_message": f"Generate {image_type} image in {style} style",
                        "variables": {
                            "PRODUCT_NAME": intelligence_data.get("product_name", "Product"),
                            "PRIMARY_BENEFIT": intelligence_data.get("offer_intelligence", {}).get("benefits", ["quality"])[0] if intelligence_data.get("offer_intelligence", {}).get("benefits") else "quality",
                            "TARGET_AUDIENCE": intelligence_data.get("psychology_intelligence", {}).get("target_audience", "consumers"),
                            "IMAGE_TYPE": image_type,
                            "STYLE": style,
                            "DIMENSIONS": dimensions
                        },
                        "quality_score": 85,  # Default quality score for images
                        "psychology_stage": "visual_appeal",
                        "metadata": {"template_used": f"image_{image_type}"}
                    }

                    mock_ai_result = {
                        "success": True,
                        "content": image_result["url"],
                        "provider": provider,
                        "provider_name": provider,
                        "cost": image_result.get("cost", 0),
                        "generation_time": image_result.get("generation_time", 0),
                        "estimated_tokens": 0
                    }

                    prompt_id = await self.prompt_storage.save_prompt(
                        campaign_id=str(campaign_id),
                        user_id=storage_user_id,
                        content_type="image",
                        user_prompt=image_prompt,
                        system_message=mock_prompt_result["system_message"],
                        intelligence_variables=mock_prompt_result["variables"],
                        prompt_result=mock_prompt_result,
                        ai_result=mock_ai_result,
                        content_id=None
                    )
                    self._generation_stats["prompts_saved"] += 1
                    logger.info(f"✅ Saved image prompt {prompt_id} for future reuse")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to save image prompt (non-critical): {e}")

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

    async def _upload_image_to_r2(
        self,
        image_url: str,
        campaign_id: Union[str, UUID],
        image_type: str,
        provider: str
    ) -> Dict[str, Any]:
        """
        Download image from temporary URL and upload to Cloudflare R2 for permanent storage
        
        Args:
            image_url: Temporary URL from AI provider
            campaign_id: Campaign identifier
            image_type: Type of image generated
            provider: AI provider used
            
        Returns:
            Dict with permanent R2 URL and metadata
        """
        try:
            logger.info(f"📥 Downloading image from {provider} temporary URL...")
            
            # Download image from temporary URL
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to download image: HTTP {response.status}")
                    
                    image_data = await response.read()
                    content_type = response.headers.get('Content-Type', 'image/png')
            
            # Generate R2 path: images/campaigns/{campaign_id}/{timestamp}_{image_type}.png
            from datetime import datetime
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            file_extension = 'png' if 'png' in content_type else 'jpg'
            r2_path = f"images/campaigns/{campaign_id}/{timestamp}_{image_type}.{file_extension}"
            
            # Upload to Cloudflare R2
            logger.info(f"☁️ Uploading to Cloudflare R2: {r2_path}")
            upload_result = await self.storage_service.upload_file(
                file_data=image_data,
                file_path=r2_path,
                content_type=content_type,
                metadata={
                    'campaign_id': str(campaign_id),
                    'image_type': image_type,
                    'provider': provider,
                    'generated_at': datetime.now(timezone.utc).isoformat()
                }
            )
            
            if not upload_result["success"]:
                raise Exception(f"R2 upload failed: {upload_result.get('error')}")
            
            self._generation_stats["images_uploaded"] += 1
            logger.info(f"✅ Image uploaded to R2: {upload_result['public_url']}")
            
            return {
                "success": True,
                "permanent_url": upload_result["public_url"],
                "r2_path": r2_path,
                "size_bytes": upload_result["size"],
                "temporary_url": image_url
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to upload image to R2: {e}")
            # Return temporary URL as fallback
            return {
                "success": False,
                "permanent_url": image_url,  # Fallback to temporary URL
                "error": str(e),
                "temporary_url": image_url
            }


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
