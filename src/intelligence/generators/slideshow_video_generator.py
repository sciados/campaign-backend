# src/intelligence/generators/slideshow_video_generator.py
import os
import asyncio
import subprocess
import tempfile
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from src.models.base import EnumSerializerMixin
from src.storage.universal_dual_storage import get_storage_manager
# 🔥 ADD PRODUCT NAME FIX IMPORTS
from ..utils.product_name_fix import (
    fix_slideshow_video_placeholders,
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
            "generation_timestamp": datetime.utcnow().isoformat()
        }
        
        fixed_result = fix_slideshow_video_placeholders(result_data, intelligence_data)
        fixed_result["placeholders_fixed"] = True
        
        return fixed_result
    
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
        
        import aiohttp
        import aiofiles
        
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