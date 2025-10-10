# src/content/generators/enhanced_platform_image_generator.py
"""
Enhanced Platform-Specific Image Generator
Integrates with existing intelligence and prompt generation system
"""

import logging
import os
import asyncio
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timezone
from uuid import UUID
from dataclasses import dataclass

from src.content.services.prompt_generation_service import PromptGenerationService
from src.content.services.ai_provider_service import AIProviderService, TaskComplexity
from src.content.services.smart_provider_router import SmartProviderRouter
from src.storage.services.cloudflare_service import CloudflareService

logger = logging.getLogger(__name__)

@dataclass
class PlatformImageSpec:
    """Platform-specific image specifications"""
    platform: str
    width: int
    height: int
    aspect_ratio: str
    format: str
    max_file_size_mb: float
    recommended_style: str
    optimal_text_zones: List[Dict[str, Any]]
    color_profile: str
    use_case: str

class EnhancedPlatformImageGenerator:
    """
    Enhanced Image Generator with Platform-Specific Optimization
    Integrates with existing intelligence → prompt → AI pipeline
    """

    # Platform specifications for 2024 social media requirements
    PLATFORM_SPECS = {
        # Instagram Formats
        "instagram_feed": PlatformImageSpec(
            platform="Instagram Feed", width=1080, height=1080, aspect_ratio="1:1",
            format="JPG", max_file_size_mb=30, recommended_style="modern, clean, mobile-optimized",
            optimal_text_zones=[{"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.2}],
            color_profile="sRGB", use_case="Feed posts, brand content"
        ),
        "instagram_story": PlatformImageSpec(
            platform="Instagram Story", width=1080, height=1920, aspect_ratio="9:16",
            format="JPG", max_file_size_mb=30, recommended_style="vertical, immersive, engaging",
            optimal_text_zones=[{"x": 0.1, "y": 0.2, "width": 0.8, "height": 0.6}],
            color_profile="sRGB", use_case="Stories, behind-the-scenes"
        ),
        "instagram_reel_cover": PlatformImageSpec(
            platform="Instagram Reel Cover", width=1080, height=1920, aspect_ratio="9:16",
            format="JPG", max_file_size_mb=30, recommended_style="eye-catching, thumbnail-optimized",
            optimal_text_zones=[{"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.3}],
            color_profile="sRGB", use_case="Reel thumbnails, video covers"
        ),

        # Facebook Formats
        "facebook_feed": PlatformImageSpec(
            platform="Facebook Feed", width=1200, height=630, aspect_ratio="1.91:1",
            format="JPG", max_file_size_mb=8, recommended_style="engaging, social-friendly",
            optimal_text_zones=[{"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.3}],
            color_profile="sRGB", use_case="News feed posts, link shares"
        ),
        "facebook_story": PlatformImageSpec(
            platform="Facebook Story", width=1080, height=1920, aspect_ratio="9:16",
            format="JPG", max_file_size_mb=30, recommended_style="vertical, immersive",
            optimal_text_zones=[{"x": 0.1, "y": 0.2, "width": 0.8, "height": 0.6}],
            color_profile="sRGB", use_case="Facebook Stories"
        ),

        # LinkedIn Formats
        "linkedin_feed": PlatformImageSpec(
            platform="LinkedIn Feed", width=1200, height=627, aspect_ratio="1.91:1",
            format="JPG", max_file_size_mb=5, recommended_style="professional, business-focused",
            optimal_text_zones=[{"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.3}],
            color_profile="sRGB", use_case="Professional posts, articles"
        ),
        "linkedin_article": PlatformImageSpec(
            platform="LinkedIn Article Header", width=1200, height=627, aspect_ratio="1.91:1",
            format="JPG", max_file_size_mb=5, recommended_style="editorial, professional",
            optimal_text_zones=[{"x": 0.1, "y": 0.6, "width": 0.8, "height": 0.3}],
            color_profile="sRGB", use_case="Article headers, long-form content"
        ),

        # Twitter/X Formats
        "twitter_feed": PlatformImageSpec(
            platform="Twitter/X Feed", width=1200, height=675, aspect_ratio="16:9",
            format="JPG", max_file_size_mb=5, recommended_style="concise, attention-grabbing",
            optimal_text_zones=[{"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.25}],
            color_profile="sRGB", use_case="Tweet images, link previews"
        ),

        # TikTok Formats
        "tiktok_cover": PlatformImageSpec(
            platform="TikTok Cover", width=1080, height=1920, aspect_ratio="9:16",
            format="JPG", max_file_size_mb=10, recommended_style="trendy, eye-catching, mobile-first",
            optimal_text_zones=[{"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.3}],
            color_profile="sRGB", use_case="Video thumbnails, profile content"
        ),

        # YouTube Formats
        "youtube_thumbnail": PlatformImageSpec(
            platform="YouTube Thumbnail", width=1280, height=720, aspect_ratio="16:9",
            format="JPG", max_file_size_mb=2, recommended_style="clickable, thumbnail-optimized",
            optimal_text_zones=[{"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.35}],
            color_profile="sRGB", use_case="Video thumbnails, channel art"
        ),

        # Pinterest Formats
        "pinterest_pin": PlatformImageSpec(
            platform="Pinterest Pin", width=1000, height=1500, aspect_ratio="2:3",
            format="JPG", max_file_size_mb=10, recommended_style="vertical, pin-optimized, inspiring",
            optimal_text_zones=[{"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.3}],
            color_profile="sRGB", use_case="Pinterest pins, idea boards"
        ),

        # General Formats
        "square": PlatformImageSpec(
            platform="Square (General)", width=1080, height=1080, aspect_ratio="1:1",
            format="JPG", max_file_size_mb=10, recommended_style="versatile, square format",
            optimal_text_zones=[{"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.8}],
            color_profile="sRGB", use_case="Versatile square content"
        ),
        "landscape": PlatformImageSpec(
            platform="Landscape (General)", width=1200, height=630, aspect_ratio="1.91:1",
            format="JPG", max_file_size_mb=10, recommended_style="versatile, landscape format",
            optimal_text_zones=[{"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.8}],
            color_profile="sRGB", use_case="Versatile landscape content"
        )
    }

    def __init__(self, db_session=None):
        self.name = "enhanced_platform_image_generator"
        self.version = "2.0.0"
        
        # Initialize existing services
        self.prompt_service = PromptGenerationService()
        self.ai_provider_service = AIProviderService()
        self.smart_router = SmartProviderRouter()
        self.storage_service = CloudflareService()
        
        # Image generation API keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
        
        # Database session for prompt storage
        self.db_session = db_session
        if db_session:
            from src.content.services.prompt_storage_service import PromptStorageService
            self.prompt_storage = PromptStorageService(db_session)
        else:
            self.prompt_storage = None

        # Generation statistics
        self._stats = {
            "total_generated": 0,
            "platform_breakdown": {},
            "total_cost": 0.0,
            "batch_generations": 0,
            "avg_generation_time": 0.0
        }

        logger.info(f"✅ {self.name} v{self.version} initialized with {len(self.PLATFORM_SPECS)} platform specs")

    async def generate_platform_image(
        self,
        campaign_id: Union[str, UUID],
        intelligence_data: Dict[str, Any],
        platform_format: str,
        image_type: str = "marketing",
        style_preferences: Optional[Dict[str, Any]] = None,
        user_id: Optional[Union[str, UUID]] = None,
        user_tier: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate single platform-optimized image using intelligence → prompt → AI pipeline
        Integrates with existing content generation architecture
        """
        
        try:
            # Get platform specifications
            platform_spec = self.PLATFORM_SPECS.get(platform_format)
            if not platform_spec:
                raise ValueError(f"Unsupported platform format: {platform_format}")

            logger.info(f"🎨 Generating {platform_spec.platform} image ({platform_spec.width}x{platform_spec.height})")

            # Step 1: Generate intelligence-driven prompt using existing prompt service
            prompt_data = await self._generate_image_prompt(
                intelligence_data=intelligence_data,
                platform_spec=platform_spec,
                image_type=image_type,
                style_preferences=style_preferences or {}
            )

            # Step 2: Select optimal image AI provider using smart router
            image_provider_info = self.smart_router.select_image_provider(
                user_tier=user_tier,
                image_type=image_type,
                credits_remaining=1000  # TODO: Get from user service
            )

            # Step 3: Generate image using selected provider
            image_result = await self._generate_with_provider(
                provider=image_provider_info["provider"],
                prompt=prompt_data["prompt"],
                platform_spec=platform_spec
            )

            if not image_result["success"]:
                raise Exception(f"Image generation failed: {image_result.get('error')}")

            # Step 4: Save to permanent storage with platform metadata
            storage_result = await self._save_to_storage(
                image_url=image_result["url"],
                campaign_id=campaign_id,
                platform_spec=platform_spec,
                image_type=image_type,
                user_id=user_id
            )

            # Step 5: Save prompt for reuse (if enabled)
            if self.prompt_storage and user_id:
                try:
                    await self.prompt_storage.save_prompt(
                        campaign_id=str(campaign_id),
                        user_id=str(user_id),
                        content_type="platform_image",
                        user_prompt=prompt_data["prompt"],
                        system_message=prompt_data.get("system_message", ""),
                        intelligence_variables=prompt_data["variables"],
                        prompt_result=prompt_data,
                        ai_result=image_result
                    )
                except Exception as e:
                    logger.warning(f"Failed to save prompt (non-critical): {e}")

            # Step 6: Update statistics
            self._update_stats(platform_format, image_result.get("cost", 0), image_result.get("generation_time", 0))

            return {
                "success": True,
                "campaign_id": str(campaign_id),
                "platform": platform_spec.platform,
                "image": {
                    "url": storage_result["permanent_url"],
                    "temporary_url": image_result["url"],
                    "platform_format": platform_format,
                    "dimensions": f"{platform_spec.width}x{platform_spec.height}",
                    "aspect_ratio": platform_spec.aspect_ratio,
                    "file_size_mb": storage_result.get("size_mb", 0),
                    "format": platform_spec.format.lower(),
                    "optimized_for": platform_spec.platform,
                    "use_case": platform_spec.use_case
                },
                "prompt": prompt_data["prompt"],
                "provider_info": image_provider_info,
                "platform_metadata": {
                    "platform": platform_spec.platform,
                    "optimal_text_zones": platform_spec.optimal_text_zones,
                    "recommended_style": platform_spec.recommended_style,
                    "max_file_size_mb": platform_spec.max_file_size_mb,
                    "color_profile": platform_spec.color_profile
                },
                "generation_metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "provider": image_provider_info["provider"],
                    "cost": image_result.get("cost", 0),
                    "generation_time": image_result.get("generation_time", 0),
                    "platform_optimized": True,
                    "intelligence_enhanced": True
                }
            }

        except Exception as e:
            logger.error(f"❌ Platform image generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform_format": platform_format,
                "campaign_id": str(campaign_id)
            }

    async def generate_multi_platform_batch(
        self,
        campaign_id: Union[str, UUID],
        intelligence_data: Dict[str, Any],
        platforms: List[str],
        image_type: str = "marketing",
        batch_style: Optional[Dict[str, Any]] = None,
        user_id: Optional[Union[str, UUID]] = None,
        user_tier: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate complete multi-platform image batch
        Uses intelligent rate limiting and concurrent generation
        """
        
        logger.info(f"🎨 Generating multi-platform batch for {len(platforms)} platforms")
        
        # Validate platforms
        invalid_platforms = [p for p in platforms if p not in self.PLATFORM_SPECS]
        if invalid_platforms:
            return {
                "success": False,
                "error": f"Invalid platforms: {invalid_platforms}",
                "valid_platforms": list(self.PLATFORM_SPECS.keys())
            }

        # Calculate estimated cost
        cost_estimate = self.smart_router.calculate_batch_cost(platforms, "dall-e-3")

        # Generate images with rate limiting
        semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
        tasks = []
        
        for platform_format in platforms:
            task = self._generate_platform_with_semaphore(
                semaphore=semaphore,
                campaign_id=campaign_id,
                intelligence_data=intelligence_data,
                platform_format=platform_format,
                image_type=image_type,
                style_preferences=batch_style,
                user_id=user_id,
                user_tier=user_tier
            )
            tasks.append(task)

        # Execute all generations
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_images = []
        failed_generations = []
        total_cost = 0.0
        total_time = 0.0
        
        for i, result in enumerate(results):
            platform_format = platforms[i]
            
            if isinstance(result, Exception):
                failed_generations.append({
                    "platform": platform_format,
                    "error": str(result)
                })
            elif result.get("success"):
                successful_images.append(result)
                total_cost += result["generation_metadata"]["cost"]
                total_time += result["generation_metadata"]["generation_time"]
            else:
                failed_generations.append({
                    "platform": platform_format,
                    "error": result.get("error", "Unknown error")
                })

        # Update batch statistics
        self._stats["batch_generations"] += 1
        
        # Calculate savings vs individual generations
        estimated_individual_cost = len(platforms) * 0.080  # DALL-E 3 HD cost
        cost_savings = estimated_individual_cost - total_cost
        
        return {
            "success": len(successful_images) > 0,
            "campaign_id": str(campaign_id),
            "batch_summary": {
                "total_platforms": len(platforms),
                "successful_generations": len(successful_images),
                "failed_generations": len(failed_generations),
                "success_rate": (len(successful_images) / len(platforms)) * 100,
                "total_cost": total_cost,
                "estimated_cost": cost_estimate["total_cost"],
                "cost_savings": cost_savings,
                "total_generation_time": total_time,
                "avg_generation_time": total_time / len(successful_images) if successful_images else 0
            },
            "generated_images": successful_images,
            "failed_generations": failed_generations,
            "platform_coverage": [img["platform"] for img in successful_images],
            "generation_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "image_type": image_type,
                "batch_style_applied": batch_style is not None,
                "user_tier": user_tier
            }
        }

    async def _generate_platform_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        campaign_id: Union[str, UUID],
        intelligence_data: Dict[str, Any],
        platform_format: str,
        image_type: str,
        style_preferences: Optional[Dict[str, Any]],
        user_id: Optional[Union[str, UUID]],
        user_tier: str
    ) -> Dict[str, Any]:
        """Generate single platform image with rate limiting"""
        async with semaphore:
            return await self.generate_platform_image(
                campaign_id=campaign_id,
                intelligence_data=intelligence_data,
                platform_format=platform_format,
                image_type=image_type,
                style_preferences=style_preferences,
                user_id=user_id,
                user_tier=user_tier
            )

    async def _generate_image_prompt(
        self,
        intelligence_data: Dict[str, Any],
        platform_spec: PlatformImageSpec,
        image_type: str,
        style_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate platform-optimized image prompt using intelligence data"""
        
        # Extract intelligence variables using existing service patterns
        product_name = intelligence_data.get("product_name", "Product")
        
        # Extract from intelligence (similar to existing prompt service)
        offer_intel = intelligence_data.get("offer_intelligence", {})
        psychology_intel = intelligence_data.get("psychology_intelligence", {})
        brand_intel = intelligence_data.get("brand_intelligence", {})
        
        # Get primary benefit and target audience
        primary_benefit = ""
        if offer_intel.get("benefits"):
            primary_benefit = offer_intel["benefits"][0] if isinstance(offer_intel["benefits"], list) else str(offer_intel["benefits"])
        elif intelligence_data.get("benefits"):
            benefits = intelligence_data["benefits"]
            primary_benefit = benefits[0] if isinstance(benefits, list) and benefits else str(benefits)
        
        target_audience = (psychology_intel.get("target_audience") or 
                          intelligence_data.get("target_audience", "customers"))
        
        # Build platform-specific prompt
        base_prompt = f"Create a {image_type} image for {product_name}"
        
        # Add platform specifications
        platform_style = platform_spec.recommended_style
        if style_preferences.get("style"):
            platform_style = f"{platform_style}, {style_preferences['style']}"
        
        # Add dimension-specific optimizations
        if platform_spec.aspect_ratio == "9:16":  # Vertical
            base_prompt += ", vertical composition optimized for mobile viewing"
        elif platform_spec.aspect_ratio == "16:9":  # Horizontal
            base_prompt += ", horizontal landscape composition"
        elif platform_spec.aspect_ratio == "1:1":  # Square
            base_prompt += ", centered square composition"
        
        # Add platform-specific enhancements
        if "instagram" in platform_spec.platform.lower():
            base_prompt += ", Instagram-style aesthetic, social media optimized"
        elif "linkedin" in platform_spec.platform.lower():
            base_prompt += ", professional business style, corporate aesthetic"
        elif "tiktok" in platform_spec.platform.lower():
            base_prompt += ", trendy, eye-catching, Gen-Z appealing"
        elif "youtube" in platform_spec.platform.lower():
            base_prompt += ", thumbnail-optimized, clickable design"
        
        # Add intelligence-driven context
        if primary_benefit:
            base_prompt += f", highlighting {primary_benefit}"
        
        if target_audience:
            base_prompt += f", appealing to {target_audience}"
        
        # Add style requirements
        full_prompt = f"{base_prompt}, {platform_style}, high resolution, professional quality, {platform_spec.format} optimized"
        
        # Add technical specifications
        full_prompt += f", {platform_spec.width}x{platform_spec.height} dimensions, {platform_spec.color_profile} color space"
        
        # Add style overrides
        if style_preferences.get("color_palette"):
            full_prompt += f", color palette: {style_preferences['color_palette']}"
        
        if style_preferences.get("mood"):
            full_prompt += f", mood: {style_preferences['mood']}"
        
        return {
            "prompt": full_prompt,
            "variables": {
                "product_name": product_name,
                "primary_benefit": primary_benefit,
                "target_audience": target_audience,
                "platform": platform_spec.platform,
                "image_type": image_type
            },
            "platform_spec": platform_spec,
            "quality_score": self._calculate_prompt_quality(full_prompt)
        }

    async def _generate_with_provider(
        self,
        provider: str,
        prompt: str,
        platform_spec: PlatformImageSpec
    ) -> Dict[str, Any]:
        """Generate image with specified provider"""
        
        dimensions = f"{platform_spec.width}x{platform_spec.height}"
        
        if provider == "dall-e-3-hd":
            return await self._generate_with_dalle3(prompt, dimensions, quality="hd")
        elif provider == "dall-e-3-standard":
            return await self._generate_with_dalle3(prompt, dimensions, quality="standard")
        elif provider == "flux-schnell":
            return await self._generate_with_flux(prompt, dimensions)
        elif provider == "sdxl":
            return await self._generate_with_sdxl(prompt, dimensions)
        else:
            # Default to DALL-E 3 standard
            return await self._generate_with_dalle3(prompt, dimensions, quality="standard")

    async def _generate_with_dalle3(self, prompt: str, dimensions: str, quality: str = "standard") -> Dict[str, Any]:
        """Generate with DALL-E 3"""
        import aiohttp
        import time

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        start_time = time.time()

        try:
            # Map to DALL-E 3 supported sizes
            width, height = map(int, dimensions.split('x'))
            if width == height:
                size = "1024x1024"
            elif width > height:
                size = "1792x1024"
            else:
                size = "1024x1792"

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
                        "size": size,
                        "quality": quality,
                        "style": "natural"
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        generation_time = time.time() - start_time
                        cost = 0.080 if quality == "hd" else 0.040

                        return {
                            "success": True,
                            "url": result["data"][0]["url"],
                            "cost": cost,
                            "generation_time": generation_time,
                            "provider": f"dall-e-3-{quality}"
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"DALL-E 3 API error: {error_text}")

        except Exception as e:
            logger.error(f"DALL-E 3 generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_with_flux(self, prompt: str, dimensions: str) -> Dict[str, Any]:
        """Generate with Flux Schnell (fast & cheap)"""
        import aiohttp
        import time
        import asyncio

        if not self.replicate_api_token:
            raise ValueError("REPLICATE_API_TOKEN not configured")

        start_time = time.time()
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
                        "version": "f2ab8a5bfe79f02f0789a146cf5e73d2a4ff2684a98c2b303d1e1ff3814271db",
                        "input": {
                            "prompt": prompt,
                            "width": width,
                            "height": height,
                            "num_outputs": 1
                        }
                    }
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        prediction_id = result["id"]

                        # Poll for completion
                        for _ in range(30):  # 30 second timeout
                            await asyncio.sleep(1)

                            async with session.get(
                                f"https://api.replicate.com/v1/predictions/{prediction_id}",
                                headers={"Authorization": f"Token {self.replicate_api_token}"}
                            ) as status_response:
                                if status_response.status == 200:
                                    status_result = await status_response.json()

                                    if status_result["status"] == "succeeded":
                                        generation_time = time.time() - start_time
                                        return {
                                            "success": True,
                                            "url": status_result["output"][0],
                                            "cost": 0.003,
                                            "generation_time": generation_time,
                                            "provider": "flux-schnell"
                                        }
                                    elif status_result["status"] == "failed":
                                        raise Exception(f"Flux generation failed: {status_result.get('error')}")

                        raise Exception("Flux generation timeout")
                    else:
                        error_text = await response.text()
                        raise Exception(f"Replicate API error: {error_text}")

        except Exception as e:
            logger.error(f"Flux generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_with_sdxl(self, prompt: str, dimensions: str) -> Dict[str, Any]:
        """Generate with Stable Diffusion XL"""
        # Placeholder - implement SDXL provider
        logger.warning("SDXL generation not implemented, falling back to Flux")
        return await self._generate_with_flux(prompt, dimensions)

    async def _save_to_storage(
        self,
        image_url: str,
        campaign_id: Union[str, UUID],
        platform_spec: PlatformImageSpec,
        image_type: str,
        user_id: Optional[Union[str, UUID]]
    ) -> Dict[str, Any]:
        """Save image to permanent storage with platform metadata"""
        
        try:
            # Download image from temporary URL
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to download image: HTTP {response.status}")
                    
                    image_data = await response.read()
                    content_type = f"image/{platform_spec.format.lower()}"

            # Generate storage path
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            platform_key = platform_spec.platform.lower().replace(" ", "_").replace("/", "_")
            filename = f"{platform_key}_{image_type}_{timestamp}.{platform_spec.format.lower()}"
            r2_path = f"images/campaigns/{campaign_id}/platforms/{platform_key}/{filename}"

            # Upload to Cloudflare R2 with enhanced metadata
            upload_result = await self.storage_service.upload_file(
                file_data=image_data,
                file_path=r2_path,
                content_type=content_type,
                metadata={
                    'campaign_id': str(campaign_id),
                    'platform': platform_spec.platform,
                    'platform_format': platform_key,
                    'width': platform_spec.width,
                    'height': platform_spec.height,
                    'aspect_ratio': platform_spec.aspect_ratio,
                    'image_type': image_type,
                    'format': platform_spec.format,
                    'max_file_size_mb': platform_spec.max_file_size_mb,
                    'color_profile': platform_spec.color_profile,
                    'use_case': platform_spec.use_case,
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'user_id': str(user_id) if user_id else None
                }
            )

            if not upload_result["success"]:
                raise Exception(f"Storage upload failed: {upload_result.get('error')}")

            return {
                "success": True,
                "permanent_url": upload_result["public_url"],
                "r2_path": r2_path,
                "size_mb": upload_result["size"] / (1024 * 1024),
                "filename": filename
            }

        except Exception as e:
            logger.error(f"❌ Failed to save image to storage: {e}")
            return {
                "success": False,
                "permanent_url": image_url,  # Fallback to temporary URL
                "error": str(e)
            }

    def _calculate_prompt_quality(self, prompt: str) -> int:
        """Calculate prompt quality score"""
        score = 0
        
        # Length check
        if len(prompt) > 100:
            score += 20
        
        # Platform-specific terms
        if any(term in prompt.lower() for term in ["optimized", "professional", "high resolution"]):
            score += 20
        
        # Product context
        if "product" in prompt.lower():
            score += 20
        
        # Style elements
        if any(term in prompt.lower() for term in ["style", "aesthetic", "composition"]):
            score += 20
        
        # Technical specifications
        if any(term in prompt.lower() for term in ["dimensions", "format", "color"]):
            score += 20
        
        return min(score, 100)

    def _update_stats(self, platform_format: str, cost: float, generation_time: float):
        """Update generation statistics"""
        self._stats["total_generated"] += 1
        self._stats["total_cost"] += cost
        
        # Update average generation time
        total = self._stats["total_generated"]
        current_avg = self._stats["avg_generation_time"]
        self._stats["avg_generation_time"] = (current_avg * (total - 1) + generation_time) / total
        
        # Update platform breakdown
        if platform_format not in self._stats["platform_breakdown"]:
            self._stats["platform_breakdown"][platform_format] = 0
        self._stats["platform_breakdown"][platform_format] += 1

    def get_platform_specs(self) -> Dict[str, Dict[str, Any]]:
        """Get all platform specifications for frontend"""
        return {
            key: {
                "platform": spec.platform,
                "dimensions": f"{spec.width}x{spec.height}",
                "aspect_ratio": spec.aspect_ratio,
                "format": spec.format,
                "max_file_size_mb": spec.max_file_size_mb,
                "recommended_style": spec.recommended_style,
                "optimal_text_zones": spec.optimal_text_zones,
                "color_profile": spec.color_profile,
                "use_case": spec.use_case
            }
            for key, spec in self.PLATFORM_SPECS.items()
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get generator statistics"""
        return {
            "generator": self.name,
            "version": self.version,
            "platform_specs_count": len(self.PLATFORM_SPECS),
            "stats": self._stats
        }

    def calculate_batch_cost(self, platforms: List[str], user_tier: str = "professional") -> Dict[str, Any]:
        """Calculate cost for multi-platform generation"""
        return self.smart_router.calculate_batch_cost(platforms, "dall-e-3")


# Factory function for integration with existing service
def create_enhanced_platform_image_generator(db_session=None) -> EnhancedPlatformImageGenerator:
    """Create enhanced platform image generator instance"""
    return EnhancedPlatformImageGenerator(db_session)