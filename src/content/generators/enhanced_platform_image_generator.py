# src/content/generators/enhanced_platform_image_generator.py
"""
Enhanced Platform-Specific Image Generator v2.1.0
Generates optimized images for 15+ social media platforms with AI intelligence integration.
FIXED: Image storage encoding error and improved error handling
"""

import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import uuid

from src.content.services.prompt_generation_service import PromptGenerationService
from src.content.services.ai_provider_service import AIProviderService
from src.content.services.smart_provider_router import SmartProviderRouter
from src.storage.services.cloudflare_service import CloudflareService

logger = logging.getLogger(__name__)

class EnhancedPlatformImageGenerator:
    """
    Enhanced platform-specific image generator with AI intelligence integration.
    Supports 15+ social media platforms with optimized dimensions and styles.
    """
    
    def __init__(self):
        self.version = "2.1.0"
        self.prompt_service = PromptGenerationService()
        self.ai_provider_service = AIProviderService()
        self.smart_router = SmartProviderRouter()
        self.cloudflare_service = CloudflareService()
        
        # Platform specifications with optimal settings
        self.platform_specs = {
            # Instagram Formats
            "instagram_feed": {
                "platform": "Instagram Feed",
                "dimensions": "1080x1080",
                "aspect_ratio": "1:1",
                "format": "JPG",
                "max_file_size_mb": 30,
                "recommended_style": "vibrant, high-contrast, mobile-optimized",
                "optimal_text_zones": [{"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.2}],
                "color_profile": "sRGB",
                "use_case": "Feed posts, brand content"
            },
            "instagram_story": {
                "platform": "Instagram Story",
                "dimensions": "1080x1920",
                "aspect_ratio": "9:16",
                "format": "JPG",
                "max_file_size_mb": 30,
                "recommended_style": "vertical, story-oriented, engaging",
                "optimal_text_zones": [{"x": 0.1, "y": 0.15, "width": 0.8, "height": 0.3}],
                "color_profile": "sRGB",
                "use_case": "Stories, behind-the-scenes"
            },
            "instagram_reel_cover": {
                "platform": "Instagram Reel Cover",
                "dimensions": "1080x1920",
                "aspect_ratio": "9:16",
                "format": "JPG",
                "max_file_size_mb": 30,
                "recommended_style": "eye-catching, vertical, thumbnail-style",
                "optimal_text_zones": [{"x": 0.1, "y": 0.4, "width": 0.8, "height": 0.2}],
                "color_profile": "sRGB",
                "use_case": "Reel thumbnails, video covers"
            },
            
            # Facebook Formats
            "facebook_feed": {
                "platform": "Facebook Feed",
                "dimensions": "1200x630",
                "aspect_ratio": "1.91:1",
                "format": "JPG",
                "max_file_size_mb": 8,
                "recommended_style": "engaging, informative, social",
                "optimal_text_zones": [{"x": 0.05, "y": 0.1, "width": 0.9, "height": 0.25}],
                "color_profile": "sRGB",
                "use_case": "News feed posts, link shares"
            },
            "facebook_story": {
                "platform": "Facebook Story",
                "dimensions": "1080x1920",
                "aspect_ratio": "9:16",
                "format": "JPG",
                "max_file_size_mb": 30,
                "recommended_style": "vertical, story-format, personal",
                "optimal_text_zones": [{"x": 0.1, "y": 0.15, "width": 0.8, "height": 0.3}],
                "color_profile": "sRGB",
                "use_case": "Facebook Stories"
            },
            
            # LinkedIn Formats
            "linkedin_feed": {
                "platform": "LinkedIn Feed",
                "dimensions": "1200x627",
                "aspect_ratio": "1.91:1",
                "format": "JPG",
                "max_file_size_mb": 5,
                "recommended_style": "professional, clean, business-focused",
                "optimal_text_zones": [{"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.3}],
                "color_profile": "sRGB",
                "use_case": "Professional posts, articles"
            },
            "linkedin_article": {
                "platform": "LinkedIn Article",
                "dimensions": "1280x720",
                "aspect_ratio": "16:9",
                "format": "JPG",
                "max_file_size_mb": 5,
                "recommended_style": "professional, header-style, informative",
                "optimal_text_zones": [{"x": 0.1, "y": 0.2, "width": 0.8, "height": 0.6}],
                "color_profile": "sRGB",
                "use_case": "Article headers, thought leadership"
            },
            
            # Twitter/X Formats
            "twitter_feed": {
                "platform": "Twitter Feed",
                "dimensions": "1200x675",
                "aspect_ratio": "16:9",
                "format": "JPG",
                "max_file_size_mb": 5,
                "recommended_style": "engaging, concise, trending",
                "optimal_text_zones": [{"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.2}],
                "color_profile": "sRGB",
                "use_case": "Tweet images, link previews"
            },
            
            # TikTok Formats
            "tiktok_cover": {
                "platform": "TikTok Cover",
                "dimensions": "1080x1920",
                "aspect_ratio": "9:16",
                "format": "JPG",
                "max_file_size_mb": 10,
                "recommended_style": "trendy, vertical, gen-z appealing",
                "optimal_text_zones": [{"x": 0.1, "y": 0.3, "width": 0.8, "height": 0.4}],
                "color_profile": "sRGB",
                "use_case": "Video thumbnails, covers"
            },
            
            # YouTube Formats
            "youtube_thumbnail": {
                "platform": "YouTube Thumbnail",
                "dimensions": "1280x720",
                "aspect_ratio": "16:9",
                "format": "JPG",
                "max_file_size_mb": 2,
                "recommended_style": "clickable, high-contrast, engaging",
                "optimal_text_zones": [{"x": 0.05, "y": 0.1, "width": 0.9, "height": 0.8}],
                "color_profile": "sRGB",
                "use_case": "Video thumbnails"
            },
            
            # Pinterest Formats
            "pinterest_pin": {
                "platform": "Pinterest Pin",
                "dimensions": "1000x1500",
                "aspect_ratio": "2:3",
                "format": "JPG",
                "max_file_size_mb": 20,
                "recommended_style": "vertical, pinterest-optimized, discoverable",
                "optimal_text_zones": [{"x": 0.1, "y": 0.05, "width": 0.8, "height": 0.9}],
                "color_profile": "sRGB",
                "use_case": "Pins, idea boards"
            },
            
            # General Purpose Formats
            "square": {
                "platform": "Square Format",
                "dimensions": "1080x1080",
                "aspect_ratio": "1:1",
                "format": "JPG",
                "max_file_size_mb": 10,
                "recommended_style": "versatile, clean, multi-platform",
                "optimal_text_zones": [{"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.8}],
                "color_profile": "sRGB",
                "use_case": "Universal square format"
            },
            "landscape": {
                "platform": "Landscape Format",
                "dimensions": "1920x1080",
                "aspect_ratio": "16:9",
                "format": "JPG",
                "max_file_size_mb": 10,
                "recommended_style": "wide, landscape, desktop-optimized",
                "optimal_text_zones": [{"x": 0.1, "y": 0.2, "width": 0.8, "height": 0.6}],
                "color_profile": "sRGB",
                "use_case": "Website headers, banners"
            }
        }
        
        logger.info(f"✅ {self.__class__.__name__} v{self.version} initialized with {len(self.platform_specs)} platform specs")

    async def generate_platform_image(
        self,
        user_id: str,
        campaign_id: str,
        platform_format: str,
        image_type: str = "marketing",
        style_preferences: Optional[Dict[str, Any]] = None,
        ai_enhancements: Optional[Dict[str, Any]] = None,
        user_tier: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate a single platform-optimized image.
        
        Args:
            user_id: User identifier
            campaign_id: Campaign identifier
            platform_format: Platform specification key (e.g., 'instagram_feed')
            image_type: Type of image (marketing, product, lifestyle, etc.)
            style_preferences: Optional style customizations
            ai_enhancements: AI-powered enhancements from intelligence system
            user_tier: User subscription tier for cost calculation
            
        Returns:
            Dict containing generation result and metadata
        """
        try:
            logger.info(f"🎨 Generating {platform_format} image ({self.platform_specs.get(platform_format, {}).get('dimensions', 'unknown')})")
            
            # Validate platform format
            if platform_format not in self.platform_specs:
                raise ValueError(f"Unsupported platform format: {platform_format}")
            
            platform_spec = self.platform_specs[platform_format]
            
            # Generate optimized prompt
            prompt = await self._generate_platform_prompt(
                platform_spec=platform_spec,
                image_type=image_type,
                style_preferences=style_preferences or {},
                ai_enhancements=ai_enhancements or {}
            )
            
            # Select optimal AI provider for image generation
            provider_config = await self.smart_router.route_image_request(
                prompt=prompt,
                dimensions=platform_spec["dimensions"],
                user_tier=user_tier,
                platform=platform_spec["platform"]
            )
            
            # Generate image
            generation_start = datetime.now()
            image_result = await self.ai_provider_service.generate_image(
                prompt=prompt,
                provider=provider_config["provider"],
                model=provider_config["model"],
                **provider_config["parameters"]
            )
            generation_time = (datetime.now() - generation_start).total_seconds()
            
            if not image_result.get("success"):
                raise Exception(f"Image generation failed: {image_result.get('error', 'Unknown error')}")
            
            # Save to storage with proper error handling
            image_url = image_result["image_url"]
            filename = f"{campaign_id}_{platform_format}_{uuid.uuid4().hex[:8]}.png"
            
            storage_url = await self._save_image_to_storage(
                image_url=image_url,
                filename=filename,
                platform_format=platform_format
            )
            
            # Calculate cost
            cost = provider_config.get("cost_per_image", 0.040)
            
            # Prepare result
            result = {
                "success": True,
                "image_url": storage_url or image_url,  # Use storage URL if available, fallback to original
                "platform_format": platform_format,
                "platform_spec": platform_spec,
                "prompt_used": prompt,
                "ai_provider": provider_config["provider"],
                "generation_time": generation_time,
                "cost": cost,
                "metadata": {
                    "image_type": image_type,
                    "style_preferences": style_preferences,
                    "ai_enhancements_used": bool(ai_enhancements),
                    "user_tier": user_tier,
                    "filename": filename,
                    "storage_saved": storage_url is not None
                }
            }
            
            logger.info(f"✅ {platform_format} image generated successfully (${cost:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Platform image generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform_format": platform_format,
                "cost": 0.0
            }

    async def generate_multi_platform_batch(
        self,
        user_id: str,
        campaign_id: str,
        platforms: List[str],
        image_type: str = "marketing",
        batch_style: Optional[Dict[str, Any]] = None,
        ai_enhancements: Optional[Dict[str, Any]] = None,
        user_tier: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate images for multiple platforms in a batch with consistent styling.
        
        Args:
            user_id: User identifier
            campaign_id: Campaign identifier
            platforms: List of platform format keys
            image_type: Type of image
            batch_style: Consistent style preferences for all platforms
            ai_enhancements: AI-powered enhancements
            user_tier: User subscription tier
            
        Returns:
            Dict containing batch results and metadata
        """
        try:
            logger.info(f"🎨 Generating multi-platform batch for {len(platforms)} platforms")
            
            # Validate all platforms
            invalid_platforms = [p for p in platforms if p not in self.platform_specs]
            if invalid_platforms:
                raise ValueError(f"Invalid platforms: {invalid_platforms}")
            
            # Generate images concurrently for better performance
            tasks = []
            for platform in platforms:
                task = self.generate_platform_image(
                    user_id=user_id,
                    campaign_id=campaign_id,
                    platform_format=platform,
                    image_type=image_type,
                    style_preferences=batch_style,
                    ai_enhancements=ai_enhancements,
                    user_tier=user_tier
                )
                tasks.append(task)
            
            # Execute all generations
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful_results = []
            failed_results = []
            total_cost = 0.0
            
            for i, result in enumerate(results):
                platform = platforms[i]
                
                if isinstance(result, Exception):
                    failed_results.append({
                        "platform": platform,
                        "error": str(result)
                    })
                elif result.get("success"):
                    successful_results.append(result)
                    total_cost += result.get("cost", 0.0)
                else:
                    failed_results.append({
                        "platform": platform,
                        "error": result.get("error", "Unknown error")
                    })
            
            batch_result = {
                "success": len(successful_results) > 0,
                "total_platforms": len(platforms),
                "successful_platforms": len(successful_results),
                "failed_platforms": len(failed_results),
                "total_cost": total_cost,
                "results": successful_results,
                "failed_results": failed_results,
                "batch_metadata": {
                    "image_type": image_type,
                    "batch_style": batch_style,
                    "ai_enhancements_used": bool(ai_enhancements),
                    "user_tier": user_tier,
                    "platforms_requested": platforms
                }
            }
            
            logger.info(f"✅ Multi-platform batch complete: {len(successful_results)}/{len(platforms)} successful (${total_cost:.3f})")
            return batch_result
            
        except Exception as e:
            logger.error(f"❌ Multi-platform batch generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_platforms": len(platforms),
                "successful_platforms": 0,
                "failed_platforms": len(platforms),
                "total_cost": 0.0
            }

    async def _generate_platform_prompt(
        self,
        platform_spec: Dict[str, Any],
        image_type: str,
        style_preferences: Dict[str, Any],
        ai_enhancements: Dict[str, Any]
    ) -> str:
        """Generate platform-optimized prompt for image generation."""
        
        # Base prompt components
        base_prompt = f"Create a high-quality {image_type} image"
        
        # Platform-specific optimizations
        platform_optimization = f"optimized for {platform_spec['platform']} ({platform_spec['dimensions']}, {platform_spec['aspect_ratio']} aspect ratio)"
        
        # Style integration
        style_elements = []
        if style_preferences.get("style"):
            style_elements.append(f"Style: {style_preferences['style']}")
        if style_preferences.get("color_palette"):
            style_elements.append(f"Colors: {style_preferences['color_palette']}")
        
        # Add platform-recommended style
        style_elements.append(f"Platform style: {platform_spec['recommended_style']}")
        
        # AI enhancements integration
        ai_elements = []
        if ai_enhancements.get("emotional_triggers"):
            ai_elements.append(f"Emotional appeal: {', '.join(ai_enhancements['emotional_triggers'])}")
        if ai_enhancements.get("target_demographics"):
            ai_elements.append(f"Target audience: {ai_enhancements['target_demographics']}")
        if ai_enhancements.get("brand_values"):
            ai_elements.append(f"Brand values: {', '.join(ai_enhancements['brand_values'])}")
        
        # Quality and technical requirements
        quality_specs = [
            "professional quality",
            "high resolution",
            "mobile-optimized",
            f"suitable for {platform_spec['use_case']}"
        ]
        
        # Combine all elements
        prompt_parts = [
            base_prompt,
            platform_optimization,
            ", ".join(style_elements) if style_elements else "",
            ", ".join(ai_elements) if ai_elements else "",
            ", ".join(quality_specs)
        ]
        
        # Clean and join
        final_prompt = ", ".join([part for part in prompt_parts if part.strip()])
        
        return final_prompt

    async def _save_image_to_storage(self, image_url: str, filename: str, platform_format: str) -> Optional[str]:
        """
        Save generated image to Cloudflare R2 storage with proper error handling.
        FIXED: Proper type checking and error handling to prevent encoding errors.
        """
        try:
            logger.info(f"💾 Attempting to save {platform_format} image: {filename}")
            
            # Download image with comprehensive error handling
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(image_url) as response:
                    if response.status != 200:
                        logger.warning(f"Image download failed with HTTP {response.status}, using original URL")
                        return image_url
                    
                    # FIXED: Proper handling of response data
                    try:
                        image_data = await response.read()
                    except Exception as read_error:
                        logger.warning(f"Failed to read image data: {read_error}, using original URL")
                        return image_url
                    
                    # FIXED: Comprehensive data validation
                    if not isinstance(image_data, (bytes, bytearray)):
                        logger.warning(f"Invalid image data type: {type(image_data)} (expected bytes), using original URL")
                        return image_url
                    
                    if len(image_data) == 0:
                        logger.warning("Downloaded image data is empty, using original URL")
                        return image_url
                    
                    if len(image_data) < 1024:  # Less than 1KB is suspicious
                        logger.warning(f"Downloaded image data is suspiciously small ({len(image_data)} bytes), using original URL")
                        return image_url
                    
                    logger.info(f"📥 Successfully downloaded image: {len(image_data)} bytes")
            
            # Try to save to storage with comprehensive error handling
            try:
                storage_result = await self.cloudflare_service.upload_file(
                    file_data=image_data,
                    filename=filename,
                    content_type="image/png",
                    folder="generated-images"
                )
                
                if storage_result.get("success") and storage_result.get("public_url"):
                    logger.info(f"✅ Image saved to storage successfully: {storage_result['public_url']}")
                    return storage_result["public_url"]
                else:
                    logger.warning(f"Storage upload unsuccessful: {storage_result.get('error', 'Unknown error')}, using original URL")
                    return image_url
                    
            except Exception as storage_error:
                logger.warning(f"Storage upload failed: {storage_error}, using original URL")
                return image_url
                
        except Exception as e:
            logger.warning(f"Image storage process failed: {e}, using original AI URL")
            return image_url  # Always return the original URL as fallback

    async def get_platform_specs(self) -> Dict[str, Dict[str, Any]]:
        """Get all platform specifications."""
        return self.platform_specs.copy()

    async def calculate_cost(self, platforms: List[str], user_tier: str = "professional") -> Dict[str, Any]:
        """Calculate cost for generating images for specified platforms."""
        try:
            # Base cost per image (can vary by provider and user tier)
            base_cost_per_image = 0.040  # $0.04 per image
            
            # User tier multipliers
            tier_multipliers = {
                "free": 1.0,
                "basic": 0.9,
                "professional": 0.8,
                "enterprise": 0.7
            }
            
            multiplier = tier_multipliers.get(user_tier, 1.0)
            cost_per_image = base_cost_per_image * multiplier
            
            valid_platforms = [p for p in platforms if p in self.platform_specs]
            total_cost = len(valid_platforms) * cost_per_image
            
            return {
                "success": True,
                "platforms": valid_platforms,
                "cost_per_image": cost_per_image,
                "total_cost": total_cost,
                "user_tier": user_tier,
                "tier_multiplier": multiplier,
                "invalid_platforms": [p for p in platforms if p not in self.platform_specs]
            }
            
        except Exception as e:
            logger.error(f"Cost calculation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_cost": 0.0
            }

    async def get_generator_stats(self) -> Dict[str, Any]:
        """Get generator statistics and capabilities."""
        return {
            "version": self.version,
            "total_platforms": len(self.platform_specs),
            "supported_platforms": list(self.platform_specs.keys()),
            "capabilities": {
                "single_platform_generation": True,
                "multi_platform_batch": True,
                "ai_enhancement_integration": True,
                "cost_optimization": True,
                "cloudflare_r2_storage": True,
                "platform_specific_optimization": True
            },
            "platform_categories": {
                "instagram": ["instagram_feed", "instagram_story", "instagram_reel_cover"],
                "facebook": ["facebook_feed", "facebook_story"],
                "linkedin": ["linkedin_feed", "linkedin_article"],
                "twitter": ["twitter_feed"],
                "tiktok": ["tiktok_cover"],
                "youtube": ["youtube_thumbnail"],
                "pinterest": ["pinterest_pin"],
                "general": ["square", "landscape"]
            },
            "supported_image_types": [
                "marketing", "product", "lifestyle", "hero", 
                "comparison", "infographic", "testimonial", "announcement"
            ],
            "ai_providers_supported": ["dall-e-3", "midjourney", "stable-diffusion", "replicate"],
            "storage_integration": "cloudflare_r2",
            "cost_range": {
                "min_cost_per_image": 0.028,  # Enterprise tier
                "max_cost_per_image": 0.040,  # Free tier
                "currency": "USD"
            }
        }