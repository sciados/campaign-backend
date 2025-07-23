# src/intelligence/generators/slideshow_video_generator.py
import os
import asyncio
import subprocess
import tempfile
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json
import aiohttp
import aiofiles

from src.models.base import EnumSerializerMixin
from src.storage.universal_dual_storage import get_storage_manager
# 🔥 ADD PRODUCT NAME FIX IMPORTS
from ..utils.product_name_fix import (
    extract_product_name_from_intelligence
)

logger = logging.getLogger(__name__)

class SlideshowVideoGenerator(EnumSerializerMixin):
    """Generate slideshow videos from campaign content"""
    
    def __init__(self):
        self.storage_manager = get_storage_manager()
        self.video_providers = self._initialize_video_providers()
        self.default_settings = {
            "duration_per_slide": 3,
            "transition_type": "fade",
            "resolution": "1920x1080",
            "fps": 30,
            "format": "mp4",
            "quality": "high"
        }
    
    def _initialize_video_providers(self) -> List[Dict[str, Any]]:
        """Initialize video generation providers"""
        providers = []
        
        # Local FFmpeg (always available)
        providers.append({
            "name": "ffmpeg_local",
            "priority": 1,
            "cost_per_video": 0.00,
            "available": self._check_ffmpeg_availability(),
            "capabilities": ["slideshow", "transitions", "audio"]
        })
        
        # RunwayML (AI video generation)
        if os.getenv("RUNWAYML_API_KEY"):
            providers.append({
                "name": "runwayml",
                "priority": 2,
                "cost_per_video": 0.50,
                "available": True,
                "capabilities": ["ai_enhancement", "advanced_effects"]
            })
        
        # Pika Labs (Text-to-video)
        if os.getenv("PIKA_LABS_API_KEY"):
            providers.append({
                "name": "pika_labs",
                "priority": 3,
                "cost_per_video": 0.25,
                "available": True,
                "capabilities": ["text_to_video", "ai_effects"]
            })
        
        return sorted(providers, key=lambda x: x["priority"])
    
    def _check_ffmpeg_availability(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    async def generate_slideshow_video(
        self,
        intelligence_data: Dict[str, Any],
        images: List[str],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate slideshow video from campaign images"""
        
        if not images:
            raise ValueError("No images provided for slideshow generation")
        
        if preferences is None:
            preferences = {}
        
        # Merge settings
        settings = {**self.default_settings, **preferences}
        
        # Extract product information
        product_name = extract_product_name_from_intelligence(intelligence_data)
        
        # Generate video script/storyboard
        storyboard = await self._generate_storyboard(intelligence_data, images, settings)
        
        # Generate video with best available provider
        video_result = None
        
        for provider in self.video_providers:
            if not provider["available"]:
                continue
            
            try:
                logger.info(f"🎬 Generating video with {provider['name']}")
                
                if provider["name"] == "ffmpeg_local":
                    video_result = await self._generate_with_ffmpeg(
                        images, storyboard, settings
                    )
                elif provider["name"] == "runwayml":
                    video_result = await self._generate_with_runwayml(
                        images, storyboard, settings
                    )
                elif provider["name"] == "pika_labs":
                    video_result = await self._generate_with_pika_labs(
                        images, storyboard, settings
                    )
                
                if video_result and video_result["success"]:
                    video_result["provider_used"] = provider["name"]
                    video_result["cost"] = provider["cost_per_video"]
                    break
                    
            except Exception as e:
                logger.error(f"Video generation failed with {provider['name']}: {str(e)}")
                continue
        
        if not video_result or not video_result["success"]:
            raise Exception("All video generation providers failed")
        
        # 🔥 APPLY FIX BEFORE RETURNING
        result_data = {
            "success": True,
            "video_data": video_result["video_data"],
            "duration": video_result["duration"],
            "provider_used": video_result["provider_used"],
            "cost": video_result["cost"],
            "storyboard": storyboard,
            "settings": settings,
            "product_name": product_name,
            "generation_timestamp": datetime.datetime.now()
        }
        
        fixed_result = fix_slideshow_video_placeholders(result_data, intelligence_data)
        fixed_result["placeholders_fixed"] = True
        
        return fixed_result
    
    async def generate_slideshow_video_with_image_generation(
        self,
        intelligence_data: Dict[str, Any],
        campaign_id: str,
        current_user: Any,
        image_assets: List[Dict[str, Any]] = None,
        video_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate slideshow video with automatic image generation if needed"""
        
        # Import Stability AI generator here to avoid circular imports
        try:
            from .stability_ai_generator import StabilityAIGenerator
        except ImportError:
            logger.warning("StabilityAIGenerator not available, using placeholder images")
            stability_generator = None
        else:
            stability_generator = StabilityAIGenerator()
        
        # Define preferences with defaults
        preferences = video_preferences or {
            "duration_per_slide": 3,
            "transition_type": "fade",
            "resolution": "1920x1080",
            "fps": 30,
            "format": "mp4",
            "quality": "high"
        }
        
        # Extract image URLs from assets or generate them
        image_urls = []
        image_asset_ids = []
        
        if image_assets:
            # Use provided image assets
            for asset in image_assets:
                if "url" in asset:
                    image_urls.append(asset["url"])
                if "id" in asset:
                    image_asset_ids.append(asset["id"])
        else:
            # Generate images if none provided and Stability AI is available
            if stability_generator:
                # Extract product name for better prompts
                product_name = extract_product_name_from_intelligence(intelligence_data)
                
                # Generate 3-5 marketing images
                image_prompts = [
                    f"Professional marketing image for {product_name}, health supplement photography",
                    f"Lifestyle image showing wellness transformation with {product_name}", 
                    f"{product_name} benefits visualization, clean modern design",
                    f"Call-to-action marketing visual featuring {product_name}"
                ]
                
                for i, prompt in enumerate(image_prompts):
                    try:
                        image_result = await stability_generator.generate_social_media_image(
                            prompt=prompt,
                            platform="general",
                            style="marketing"
                        )
                        
                        if image_result.get("success") and "image_data" in image_result:
                            # Save image to storage
                            image_filename = f"slideshow_{campaign_id}_{i}.png"
                            storage_result = await self.storage_manager.save_content_dual_storage(
                                content_data=image_result["image_data"]["image_base64"],
                                content_type="image",
                                filename=image_filename,
                                user_id=str(current_user.id),
                                campaign_id=campaign_id,
                                metadata={
                                    "content_type": "slideshow_image",
                                    "prompt": prompt,
                                    "generation_method": "stability_ai"
                                }
                            )
                            
                            if storage_result.get("success"):
                                image_urls.append(storage_result["public_url"])
                                image_asset_ids.append(storage_result.get("asset_id"))
                                
                    except Exception as e:
                        logger.error(f"Failed to generate slideshow image {i}: {str(e)}")
                        continue
            else:
                # Fallback: use placeholder images
                placeholder_urls = [
                    "https://via.placeholder.com/1920x1080/4CAF50/white?text=Health+Benefits",
                    "https://via.placeholder.com/1920x1080/2196F3/white?text=Natural+Wellness",
                    "https://via.placeholder.com/1920x1080/FF9800/white?text=Transform+Your+Health",
                    "https://via.placeholder.com/1920x1080/9C27B0/white?text=Call+to+Action"
                ]
                image_urls = placeholder_urls
                image_asset_ids = [f"placeholder_{i}" for i in range(len(placeholder_urls))]
        
        # Ensure we have at least some images
        if not image_urls:
            return {
                "success": False,
                "error": "No images available for slideshow generation",
                "suggestion": "Please provide image assets or ensure image generation is working"
            }
        
        try:
            # Generate slideshow video
            video_result = await self.generate_slideshow_video(
                intelligence_data=intelligence_data,
                images=image_urls,
                preferences=preferences
            )
            
            if not video_result.get("success"):
                return {
                    "success": False,
                    "error": "Slideshow video generation failed",
                    "details": video_result.get("error")
                }
            
            # Save video to dual storage
            video_filename = f"slideshow_{campaign_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            
            storage_result = await self.storage_manager.save_content_dual_storage(
                content_data=video_result["video_data"],
                content_type="video",
                filename=video_filename,
                user_id=str(current_user.id),
                campaign_id=campaign_id,
                metadata={
                    "video_type": "slideshow",
                    "source_images": image_asset_ids,
                    "duration": video_result["duration"],
                    "provider_used": video_result["provider_used"],
                    "generation_cost": video_result["cost"]
                }
            )
            
            return {
                "success": True,
                "video_url": storage_result["public_url"],
                "video_id": storage_result.get("asset_id"),
                "duration": video_result["duration"],
                "provider_used": video_result["provider_used"],
                "cost": video_result["cost"],
                "source_images": image_asset_ids,
                "preferences_used": preferences,
                "generation_timestamp": video_result["generation_timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Slideshow video generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback_suggestion": "Try with fewer images or different settings"
            }
    
    async def _generate_storyboard(
        self,
        intelligence_data: Dict[str, Any],
        images: List[str],
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate video storyboard from intelligence data"""
        
        # Extract key messaging with proper enum serialization
        offer_intel = self._serialize_enum_field(intelligence_data.get("offer_intelligence", {}))
        key_benefits = offer_intel.get("benefits", ["Health optimization", "Natural wellness"])
        
        # Get actual product name
        product_name = extract_product_name_from_intelligence(intelligence_data)
        
        # Create storyboard
        storyboard = {
            "title": f"{product_name} Campaign Video",
            "total_duration": len(images) * settings["duration_per_slide"],
            "scenes": []
        }
        
        # Generate scenes for each image
        for i, image_url in enumerate(images):
            scene = {
                "scene_number": i + 1,
                "image_url": image_url,
                "start_time": i * settings["duration_per_slide"],
                "end_time": (i + 1) * settings["duration_per_slide"],
                "duration": settings["duration_per_slide"],
                "transition": settings["transition_type"],
                "text_overlay": self._generate_text_overlay(i, key_benefits, product_name),
                "effects": ["fade_in", "fade_out"] if i == 0 or i == len(images) - 1 else []
            }
            storyboard["scenes"].append(scene)
        
        return storyboard
    
    def _generate_text_overlay(self, scene_index: int, key_benefits: List[str], product_name: str) -> str:
        """Generate text overlay for scene"""
        
        if scene_index == 0:
            return f"Transform Your Health with {product_name}"
        elif scene_index < len(key_benefits):
            return key_benefits[scene_index]
        else:
            return f"Experience the {product_name} Difference"
    
    async def _generate_with_ffmpeg(
        self,
        images: List[str],
        storyboard: Dict[str, Any],
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate video using FFmpeg"""
        
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download images to temp directory
                image_paths = await self._download_images_to_temp(images, temp_dir)
                
                if not image_paths:
                    raise Exception("No images were successfully downloaded")
                
                # Generate video with FFmpeg
                output_path = os.path.join(temp_dir, "slideshow.mp4")
                
                # Build FFmpeg command
                cmd = [
                    "ffmpeg",
                    "-y",  # Overwrite output file
                    "-f", "image2",
                    "-framerate", f"1/{settings['duration_per_slide']}",
                    "-i", os.path.join(temp_dir, "image_%03d.jpg"),
                    "-vf", f"scale={settings['resolution']},format=yuv420p",
                    "-r", str(settings['fps']),
                    "-c:v", "libx264",
                    "-preset", "medium",
                    "-crf", "23",
                    "-t", str(storyboard["total_duration"]),
                    output_path
                ]
                
                # Execute FFmpeg
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                
                if result.returncode != 0:
                    raise Exception(f"FFmpeg failed: {result.stderr}")
                
                # Read generated video
                with open(output_path, "rb") as f:
                    video_data = f.read()
                
                return {
                    "success": True,
                    "video_data": video_data,
                    "duration": storyboard["total_duration"],
                    "file_size": len(video_data),
                    "format": "mp4"
                }
                
        except Exception as e:
            logger.error(f"FFmpeg video generation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _download_images_to_temp(self, images: List[str], temp_dir: str) -> List[str]:
        """Download images to temporary directory"""
        
        image_paths = []
        
        async with aiohttp.ClientSession() as session:
            for i, image_url in enumerate(images):
                try:
                    async with session.get(image_url) as response:
                        if response.status == 200:
                            image_data = await response.read()
                            
                            # Save to temp directory
                            image_path = os.path.join(temp_dir, f"image_{i:03d}.jpg")
                            async with aiofiles.open(image_path, "wb") as f:
                                await f.write(image_data)
                            
                            image_paths.append(image_path)
                        else:
                            logger.warning(f"Failed to download image: {image_url}")
                            
                except Exception as e:
                    logger.error(f"Error downloading image {image_url}: {str(e)}")
        
        return image_paths
    
    async def _generate_with_runwayml(
        self,
        images: List[str],
        storyboard: Dict[str, Any],
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate video using RunwayML API"""
        
        # Placeholder for RunwayML integration
        # In production, you'd implement the actual API calls
        
        return {
            "success": False,
            "error": "RunwayML integration not implemented yet"
        }
    
    async def _generate_with_pika_labs(
        self,
        images: List[str],
        storyboard: Dict[str, Any],
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate video using Pika Labs API"""
        
        # Placeholder for Pika Labs integration
        # In production, you'd implement the actual API calls
        
        return {
            "success": False,
            "error": "Pika Labs integration not implemented yet"
        }
    
    async def generate_batch_videos(
        self,
        campaigns: List[Dict[str, Any]],
        batch_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate multiple slideshow videos efficiently"""
        
        results = []
        total_cost = 0
        
        for i, campaign in enumerate(campaigns):
            try:
                result = await self.generate_slideshow_video_with_image_generation(
                    intelligence_data=campaign["intelligence_data"],
                    campaign_id=campaign["campaign_id"],
                    current_user=campaign["current_user"],
                    image_assets=campaign.get("image_assets"),
                    video_preferences=batch_preferences
                )
                results.append(result)
                
                if result.get("success"):
                    total_cost += result.get("cost", 0)
                
                # Small delay to avoid overwhelming the system
                await asyncio.sleep(1)
                
                logger.info(f"Generated slideshow video {i+1}/{len(campaigns)}")
                
            except Exception as e:
                logger.error(f"Batch video generation failed for campaign {i+1}: {str(e)}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "campaign_id": campaign.get("campaign_id")
                })
        
        return {
            "total_videos": len(campaigns),
            "successful_generations": len([r for r in results if r.get("success")]),
            "failed_generations": len([r for r in results if not r.get("success")]),
            "total_cost": total_cost,
            "cost_per_video": total_cost / len(campaigns) if campaigns else 0,
            "results": results
        }
    
    def get_video_statistics(self) -> Dict[str, Any]:
        """Get video generation statistics"""
        
        return {
            "available_providers": [p["name"] for p in self.video_providers if p["available"]],
            "provider_costs": {p["name"]: p["cost_per_video"] for p in self.video_providers},
            "default_settings": self.default_settings,
            "supported_formats": ["mp4", "avi", "mov"],
            "supported_resolutions": ["1920x1080", "1280x720", "3840x2160"],
            "ffmpeg_available": self._check_ffmpeg_availability()
        }