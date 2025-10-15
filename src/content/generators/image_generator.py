# src/content/generators/image_generator.py
"""
AI-Powered Image Generator with Intelligence Integration
Uses modular architecture: Intelligence → Prompt → AI → Image
Supports multiple providers: OpenAI DALL-E 3, Google Imagen 3, Replicate (Flux, SDXL)
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
        self.version = "4.0.0"  # Standardized provider contracts - all return binary data

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
        self.google_api_key = os.getenv("GOOGLE_API_KEY")  # For Imagen 3

        # Initialize Cloudflare R2 storage
        from src.storage.services.cloudflare_service import CloudflareService
        self.storage_service = CloudflareService()

        # Initialize AI Inpainting service for automatic text removal
        from src.storage.services.inpainting_service import get_inpainting_service
        self.inpainting_service = get_inpainting_service()

        self._generation_stats = {
            "images_generated": 0,
            "total_cost": 0.0,
            "prompts_saved": 0,
            "images_uploaded": 0,
            "images_cleaned": 0
        }

        logger.info(f"✅ ImageGenerator v{self.version} - Modular architecture with AI + R2 storage + Auto text removal")

    async def generate_marketing_image(
        self,
        campaign_id: Union[str, UUID],
        intelligence_data: Dict[str, Any],
        image_type: str = "product_hero",
        style: str = "professional",
        dimensions: str = "1024x1024",
        provider: str = "imagen-3",  # Imagen 3 recommended (best value: $0.03)
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
            provider: AI provider (imagen-3, dall-e-3, flux-schnell, sdxl)
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

            # Add fallback providers (Imagen 3 first for best value, then DALL-E 3, then cheaper options)
            all_providers = ["imagen-3", "dall-e-3", "flux-schnell", "sdxl"]
            for p in all_providers:
                if p not in providers_to_try:
                    providers_to_try.append(p)

            image_result = None
            last_error = None

            for attempt_provider in providers_to_try:
                try:
                    logger.info(f"🔄 Attempting image generation with {attempt_provider}...")

                    if attempt_provider == "imagen-3":
                        image_result = await self._generate_with_imagen3(
                            prompt=image_prompt,
                            dimensions=dimensions
                        )
                    elif attempt_provider == "dall-e-3":
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

            # Step 2.5: Automatic text removal using AI inpainting (ensures clean images)
            # Skip if provider doesn't return a temporary URL (like Imagen 3 which returns binary data directly)
            temporary_url = image_result.get("url")
            cleaning_cost = 0.0

            if temporary_url:
                try:
                    logger.info(f"🧹 Attempting automatic text removal...")
                    cleaning_result = await self.inpainting_service.remove_text_from_image(
                        image_url=temporary_url,
                        provider="stability"  # Stability AI for inpainting
                    )

                    if cleaning_result["success"]:
                        # Use cleaned image instead of original
                        temporary_url = cleaning_result["cleaned_url"]
                        cleaning_cost = cleaning_result.get("cost", 0.01)
                        self._generation_stats["images_cleaned"] += 1
                        logger.info(f"✅ Text removed successfully (cost: ${cleaning_cost:.3f})")
                    else:
                        logger.warning(f"⚠️ Text removal failed, using original image: {cleaning_result.get('error')}")

                except Exception as e:
                    logger.warning(f"⚠️ Text removal error (continuing with original): {e}")
            else:
                logger.info(f"⏭️  Skipping text removal (provider returned binary data directly)")

            # Step 3: Upload image to Cloudflare R2 for permanent storage
            # If provider returned raw image_data (like Imagen 3), pass it directly to avoid re-download
            image_data_direct = image_result.get("image_data") if image_result else None

            r2_upload_result = await self._upload_image_to_r2(
                image_url=temporary_url if temporary_url else "",  # Empty string if no URL
                campaign_id=campaign_id,
                image_type=image_type,
                provider=provider,
                image_data=image_data_direct
            )

            # Use permanent R2 URL if upload succeeded, otherwise fallback to temporary URL or raise error
            if r2_upload_result["success"]:
                permanent_url = r2_upload_result["permanent_url"]
                logger.info(f"✅ Image uploaded to R2: {permanent_url}")
            else:
                # If R2 upload failed and we have no temporary URL, this is a critical failure
                if not temporary_url:
                    raise Exception(f"R2 upload failed and no fallback URL available: {r2_upload_result.get('error')}")
                permanent_url = temporary_url
                logger.warning(f"⚠️ R2 upload failed, using temporary URL: {r2_upload_result.get('error')}")

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
                        "content": permanent_url,  # Use permanent R2 URL
                        "temporary_url": temporary_url,
                        "r2_path": r2_upload_result.get("r2_path"),
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

            # Update stats (including cleaning cost if text removal was performed)
            self._generation_stats["images_generated"] += 1
            self._generation_stats["total_cost"] += image_result.get("cost", 0) + cleaning_cost

            return {
                "success": True,
                "campaign_id": str(campaign_id),
                "image": {
                    "url": permanent_url,  # R2 permanent URL or temporary fallback
                    "temporary_url": temporary_url,  # Original temporary URL from AI provider
                    "r2_path": r2_upload_result.get("r2_path"),  # Path in R2 storage
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
                    "intelligence_enhanced": True,
                    "r2_uploaded": r2_upload_result["success"],
                    "storage_location": "cloudflare_r2" if r2_upload_result["success"] else "temporary"
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

        # Extract rich intelligence data
        product_name = intelligence_data.get("product_name", "Product")

        # Get offer intelligence
        offer_intel = intelligence_data.get("offer_intelligence", {})
        primary_benefits = offer_intel.get("primary_benefits", [])
        key_features = offer_intel.get("key_features", [])
        products = offer_intel.get("products", [])

        # Get psychology intelligence
        psych_intel = intelligence_data.get("psychology_intelligence", {})
        target_audience = psych_intel.get("target_audience", "consumers")
        pain_points = psych_intel.get("pain_points", [])
        desire_states = psych_intel.get("desire_states", [])

        # Get brand intelligence
        brand_intel = intelligence_data.get("brand_intelligence", {})
        brand_personality = brand_intel.get("brand_personality", [])
        brand_values = brand_intel.get("brand_values", [])

        # Build context-aware descriptions
        benefit_desc = ", ".join(primary_benefits[:2]) if primary_benefits else "quality results"
        feature_desc = ", ".join(key_features[:2]) if key_features else ""
        personality_desc = ", ".join(brand_personality[:2]) if brand_personality else "trustworthy"
        pain_desc = " and ".join(pain_points[:2]) if pain_points else ""
        desire_desc = ", ".join(desire_states[:2]) if desire_states else "better health"

        # Base prompt templates by image type - GENERIC REUSABLE SCENES
        # IMPORTANT: Generate scenes WITHOUT products - products will be added later via mockups
        # This creates a reusable library of backgrounds that work across thousands of products
        prompts = {
            "product_hero": f"Professional studio product photography setup with perfect lighting and backdrop, clean minimalist background for product placement, {style} aesthetic with {personality_desc} mood, empty pedestal or clean surface ready for product, premium commercial photography studio quality, natural health and wellness elements in background, soft diffused lighting, high-end marketing backdrop, absolutely no products or text in scene",

            "lifestyle": f"Authentic lifestyle photography scene of {target_audience} in daily wellness routine, natural environment perfect for product placement, {style} aesthetic, real-world setting showing {desire_desc} lifestyle, natural lighting, genuine moment with empty space for product mockup, warm inviting atmosphere, hands visible ready to hold product, no products or text in scene",

            "comparison": f"Split-screen layout showing transformation concept, before and after visual framework for {pain_desc if pain_desc else 'wellness'} to {desire_desc}, {style} design with {personality_desc} presentation, clean professional layout with designated spaces for product placement, no products or text overlays, empty frames ready for mockup",

            "infographic": f"Clean modern visual composition with geometric shapes and abstract wellness icons representing {benefit_desc}, {style} color scheme reflecting {', '.join(brand_values[:2]) if brand_values else 'health and wellness'}, professional marketing graphics with designated spaces for product placement, minimalist background elements, no products or text labels, ready for overlay",

            "social_post": f"Eye-catching social media background scene targeting {target_audience} seeking {desire_desc}, {style} aesthetic with wellness-focused color palette, clean uncluttered composition with empty focal area perfect for product mockup, attention-grabbing backdrop with natural or lifestyle elements, no products or text in image, ideal for product overlay"
        }

        base_prompt = prompts.get(image_type, prompts["product_hero"])

        # Enhance with style details - focus on background scene, not products
        style_enhancements = {
            "professional": "corporate backdrop, clean lines, sophisticated color palette, medical-grade environment, trust-building setting, empty space for product placement",
            "modern": "contemporary design, minimalist background, trendy marketing backdrop, sleek and approachable scene, clear product placement area",
            "vibrant": "energetic colors, vitality-focused environment, eye-catching background, dynamic and motivating setting, designated product space",
            "minimalist": "simple clean design, generous white space, elegant aesthetic, understated premium backdrop, perfect for product overlay",
            "dramatic": "high contrast lighting, dramatic shadows, bold atmospheric setting, cinematic background, empty focal point for product",
            "funny": "playful and humorous scene, lighthearted setting, entertaining and relatable environment, fun unexpected elements, approachable atmosphere with space for product",
            "animated": "3D rendered cartoon style background, Pixar-quality animation, vibrant animated scene, friendly animated environment, colorful digital art backdrop with clear product placement area"
        }

        enhancement = style_enhancements.get(style, style_enhancements["professional"])
        full_prompt = f"{base_prompt}, {enhancement}"

        # Add technical quality requirements based on style
        if style == "animated":
            full_prompt += ", ultra high quality 3D rendering, professional commercial animation, Pixar-style lighting, cinema-quality CGI background scene, no products in frame"
        else:
            full_prompt += ", ultra high quality, 8k resolution, professional commercial photography background, sharp focus, perfect composition, premium backdrop ready for product mockup, no products in frame"

        return full_prompt

    async def _upload_image_to_r2(
        self,
        image_url: str,
        campaign_id: Union[str, UUID],
        image_type: str,
        provider: str,
        image_data: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Download image from temporary URL and upload to Cloudflare R2 for permanent storage

        Args:
            image_url: Temporary URL from AI provider (or data URL)
            campaign_id: Campaign identifier
            image_type: Type of image generated
            provider: AI provider used
            image_data: Optional pre-downloaded image data (avoids re-download)

        Returns:
            Dict with permanent R2 URL and metadata
        """
        try:
            # If image_data provided (e.g., from Imagen 3), skip download
            if image_data:
                logger.info(f"📥 Using pre-downloaded image data from {provider}...")
                content_type = 'image/png'
            # Check if image_url is a data URL (data:image/png;base64,...)
            elif image_url.startswith('data:'):
                logger.info(f"📥 Extracting image from data URL...")
                # Parse data URL format: data:image/png;base64,<base64_data>
                if ';base64,' in image_url:
                    base64_data = image_url.split(';base64,')[1]
                    image_data = base64.b64decode(base64_data)
                    content_type = image_url.split(';')[0].replace('data:', '')
                    logger.info(f"✅ Extracted {len(image_data)} bytes from data URL")
                else:
                    raise Exception("Data URL is not in base64 format")
            else:
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
        """
        Generate image using OpenAI DALL-E 3

        Returns standardized format with raw binary data for consistent R2 upload
        """

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        import time
        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                # Generate image
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
                        "quality": "standard",  # Standard quality: excellent for marketing, 50% cheaper than HD
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
                    cost = 0.040  # Standard quality (excellent for marketing)

                    # Download image immediately (DALL-E URLs expire after 1 hour)
                    logger.info(f"📥 Downloading DALL-E 3 image from temporary URL...")
                    async with session.get(image_url) as img_response:
                        if img_response.status != 200:
                            raise Exception(f"Failed to download DALL-E image: HTTP {img_response.status}")

                        image_data = await img_response.read()
                        content_type = img_response.headers.get('Content-Type', 'image/png')

                    logger.info(f"✅ DALL-E 3 image downloaded ({len(image_data)} bytes)")

                    # Return standardized format with raw binary data
                    return {
                        "success": True,
                        "image_data": image_data,          # Raw binary data (primary)
                        "url": image_url,                  # Original temporary URL (reference only)
                        "content_type": content_type,      # Content type for R2 upload
                        "cost": cost,
                        "generation_time": generation_time
                    }

        except Exception as e:
            logger.error(f"DALL-E 3 generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_with_imagen3(
        self,
        prompt: str,
        dimensions: str
    ) -> Dict[str, Any]:
        """
        Generate image using Google Imagen 3

        Returns standardized format with raw binary data for consistent R2 upload
        """

        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY not configured")

        try:
            import time
            start_time = time.time()

            # Convert dimensions to aspect ratio for Imagen 3
            aspect_ratio_map = {
                "1024x1024": "1:1",
                "1792x1024": "16:9",
                "1024x1792": "9:16"
            }
            aspect_ratio = aspect_ratio_map.get(dimensions, "1:1")

            # Imagen 3 API endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:generateImages"

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": self.google_api_key
                    },
                    json={
                        "prompt": prompt,
                        "config": {
                            "numberOfImages": 1,
                            "aspectRatio": aspect_ratio
                        }
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Imagen 3 API error: {error_text}")

                    result = await response.json()

                    # Extract image from response
                    if "generatedImages" not in result or not result["generatedImages"]:
                        raise Exception("No images generated by Imagen 3")

                    # Get first generated image
                    generated_image = result["generatedImages"][0]

                    # Extract binary data from base64
                    if "imageBytes" not in generated_image:
                        raise Exception("No image data in Imagen 3 response")

                    image_base64 = generated_image["imageBytes"]
                    image_data = base64.b64decode(image_base64)

                    generation_time = time.time() - start_time

                    # Imagen 3 pricing: $0.03 per image (40% cheaper than DALL-E 3)
                    cost = 0.030

                    logger.info(f"✅ Imagen 3 generated image in {generation_time:.2f}s (cost: ${cost})")

                    # Return standardized format with raw binary data
                    # No URL needed - R2 upload will handle storage and generate CDN URL
                    return {
                        "success": True,
                        "image_data": image_data,      # Raw binary data (primary)
                        "url": None,                    # No temporary URL (not needed)
                        "content_type": "image/png",   # Content type for R2 upload
                        "cost": cost,
                        "generation_time": generation_time
                    }

        except Exception as e:
            logger.error(f"Imagen 3 generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_with_flux(
        self,
        prompt: str,
        dimensions: str
    ) -> Dict[str, Any]:
        """
        Generate image using Replicate Flux Schnell (fast & cheap)

        Returns standardized format with raw binary data for consistent R2 upload
        """

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

                            # Download image immediately for consistent handling
                            logger.info(f"📥 Downloading Flux image from Replicate...")
                            async with session.get(image_url) as img_response:
                                if img_response.status != 200:
                                    raise Exception(f"Failed to download Flux image: HTTP {img_response.status}")

                                image_data = await img_response.read()
                                content_type = img_response.headers.get('Content-Type', 'image/png')

                            logger.info(f"✅ Flux image downloaded ({len(image_data)} bytes)")

                            # Return standardized format with raw binary data
                            return {
                                "success": True,
                                "image_data": image_data,       # Raw binary data (primary)
                                "url": image_url,               # Original temporary URL (reference only)
                                "content_type": content_type,   # Content type for R2 upload
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
