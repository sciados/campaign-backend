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
import base64

# ✅ CRUD MIGRATION IMPORTS
from src.intelligence.repositories.intelligence_repository import IntelligenceRepository
from src.core.crud.campaign_crud import CampaignCRUD
# from src.core.crud.intelligence_crud import intelligence_crud, GeneratedContent  # DEPRECATED - Legacy file

# ✅ STORAGE SYSTEM INTEGRATION
from src.storage.services.file_service import FileService
from src.storage.services.media_service import MediaService

# ✅ VIDEO ASSEMBLY PIPELINE INTEGRATION
from src.content.services.video_assembly_pipeline import (
    create_video_assembly_pipeline,
    VideoScene as AssemblyVideoScene,
    VideoSpec
)

# ✅ DATABASE SESSION
from src.core.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

from src.intelligence.utils.enum_serializer import EnumSerializerMixin
# 🔥 ADD PRODUCT NAME FIX IMPORTS
from ..utils.product_name_fix import (
    extract_product_name_from_intelligence
)

logger = logging.getLogger(__name__)

# ✅ MISSING FUNCTION IMPLEMENTATION
def fix_slideshow_video_placeholders(result_data: Dict[str, Any], intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fix placeholders in slideshow video data using intelligence context"""
    
    # Extract product information for placeholder replacement
    product_name = extract_product_name_from_intelligence(intelligence_data)
    offer_intel = intelligence_data.get("offer_intelligence", {})
    
    # Get primary benefit for context
    benefits = offer_intel.get("benefits", ["Health optimization", "Natural wellness"]) if offer_intel else ["Health optimization"]
    primary_benefit = benefits[0] if benefits else "Health optimization"
    
    # Process storyboard if present
    if "storyboard" in result_data:
        storyboard = result_data["storyboard"]
        
        # Fix title
        if "title" in storyboard:
            storyboard["title"] = storyboard["title"].replace("[PRODUCT]", product_name)
            storyboard["title"] = storyboard["title"].replace("PRODUCT", product_name)
        
        # Fix scenes
        if "scenes" in storyboard:
            for scene in storyboard["scenes"]:
                # Fix text overlays
                if "text_overlay" in scene:
                    scene["text_overlay"] = scene["text_overlay"].replace("[PRODUCT]", product_name)
                    scene["text_overlay"] = scene["text_overlay"].replace("PRODUCT", product_name)
                    scene["text_overlay"] = scene["text_overlay"].replace("[BENEFIT]", primary_benefit)
    
    # Add metadata about placeholder fixes
    result_data["intelligence_context"] = {
        "product_name": product_name,
        "primary_benefit": primary_benefit,
        "placeholders_processed": True,
        "enhancement_timestamp": datetime.now().isoformat()
    }
    
    return result_data

class SlideshowVideoGenerator(EnumSerializerMixin):
    """Generate slideshow videos from campaign content with CRUD and storage integration"""
    
    def __init__(self):
        # ✅ INITIALIZE CRUD INSTANCES
        self.intelligence_repository = IntelligenceRepository()
        self.campaign_crud = CampaignCRUD()
        
        # ✅ INITIALIZE STORAGE SYSTEM
        self.file_service = FileService()
        self.media_service = MediaService()

        # ✅ INITIALIZE VIDEO ASSEMBLY PIPELINE
        self.video_assembler = create_video_assembly_pipeline()
        
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
        """Check if FFmpeg is available with graceful fallback"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            available = result.returncode == 0
            if available:
                logger.info("✅ FFmpeg available for video generation")
            else:
                logger.warning("⚠️ FFmpeg not properly configured")
            return available
        except Exception as e:
            logger.warning(f"⚠️ FFmpeg not available: {e}")
            return False
    
    # ✅ STORAGE QUOTA CHECKING
    async def _check_storage_quota(self, user_id: str, estimated_file_size: int) -> bool:
        """Check if user has sufficient storage quota"""
        try:
            return await self.storage.check_quota(user_id, estimated_file_size)
        except Exception as e:
            logger.error(f"Storage quota check failed: {e}")
            return False
    
    # ✅ SAVE GENERATED VIDEO TO STORAGE
    async def _save_video_to_storage(
        self, 
        user_id: str, 
        video_data: bytes, 
        metadata: Dict[str, Any]
    ) -> Optional[str]:
        """Save generated video to storage system"""
        try:
            file_size = len(video_data)
            
            # Check quota before saving
            if not await self._check_storage_quota(user_id, file_size):
                raise Exception("Storage quota exceeded")
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"slideshow_video_{timestamp}.mp4"
            
            # Save to storage
            file_url = await self.storage.upload(
                user_id=user_id,
                file_data=video_data,
                file_type="video",
                filename=filename,
                metadata=metadata
            )
            
            # Update storage usage
            await self.storage.update_usage(user_id, file_size)
            
            return file_url
            
        except Exception as e:
            logger.error(f"Failed to save video to storage: {e}")
            return None
    
    async def generate_slideshow_video(
        self,
        intelligence_data: Dict[str, Any],
        images: List[str],
        preferences: Dict[str, Any] = None,
        user_id: Optional[str] = None,
        campaign_id: Optional[int] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """Generate slideshow video from campaign images with storage and CRUD integration"""
        
        if not images:
            raise ValueError("No images provided for slideshow generation")
        
        if preferences is None:
            preferences = {}
        
        # Merge settings
        settings = {**self.default_settings, **preferences}
        
        # Extract product information
        product_name = extract_product_name_from_intelligence(intelligence_data)
        
        # Estimate video file size (roughly 10MB for 60-second slideshow)
        estimated_duration = len(images) * settings["duration_per_slide"]
        estimated_size = estimated_duration * 170000  # ~170KB per second
        
        # Check storage quota if user_id provided
        if user_id and not await self._check_storage_quota(user_id, estimated_size):
            raise Exception("Storage quota exceeded. Please upgrade your plan.")
        
        # Generate video script/storyboard
        storyboard = await self._generate_storyboard(intelligence_data, images, settings)
        
        # Generate video with best available provider
        video_result = None
        provider_used = None
        generation_cost = 0
        
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
                    provider_used = provider["name"]
                    generation_cost = provider["cost_per_video"]
                    break
                    
            except Exception as e:
                logger.error(f"Video generation failed with {provider['name']}: {str(e)}")
                continue
        
        if not video_result or not video_result["success"]:
            raise Exception("All video generation providers failed")
        
        # ✅ SAVE TO STORAGE IF USER PROVIDED
        file_url = None
        if user_id and isinstance(video_result["video_data"], bytes):
            metadata = {
                "video_type": "slideshow",
                "provider": provider_used,
                "cost": generation_cost,
                "duration": video_result["duration"],
                "campaign_id": campaign_id,
                "generation_timestamp": datetime.now().isoformat(),
                "product_name": product_name
            }
            
            file_url = await self._save_video_to_storage(
                user_id, 
                video_result["video_data"], 
                metadata
            )
        
        # ✅ SAVE TO DATABASE IF DB SESSION PROVIDED
        if db and campaign_id:
            try:
                # Convert video data to base64 for database storage
                video_base64 = None
                if isinstance(video_result["video_data"], bytes):
                    video_base64 = base64.b64encode(video_result["video_data"]).decode()
                
                content_data = {
                    "campaign_id": campaign_id,
                    "content_type": "video",
                    "content_format": "mp4",
                    "content_data": {
                        "video_base64": video_base64,
                        "duration": video_result["duration"],
                        "storyboard": storyboard,
                        "provider": provider_used,
                        "cost": generation_cost,
                        "file_url": file_url,
                        "settings": settings
                    },
                    "generation_metadata": {
                        "provider_used": provider_used,
                        "video_type": "slideshow",
                        "source_images_count": len(images),
                        "generation_timestamp": datetime.now().isoformat(),
                        "product_name": product_name
                    }
                }
                
                # Save generated video content using file service
                if video_file_path and os.path.exists(video_file_path):
                    with open(video_file_path, 'rb') as video_file:
                        video_data = video_file.read()

                    # Upload video file to storage
                    upload_result = await self.file_service.upload_file(
                        db=db,
                        user_id=user_id,
                        file_data=video_data,
                        original_filename=f"slideshow_video_{campaign_id}.mp4",
                        content_type="video/mp4",
                        campaign_id=campaign_id,
                        metadata={
                            "content_type": "slideshow_video",
                            "generation_provider": provider,
                            "video_specs": video_specs,
                            "generation_cost": total_generation_cost,
                            "intelligence_id": intelligence_data.get("id"),
                            "created_via": "slideshow_video_generator"
                        }
                    )

                    if upload_result.get("success"):
                        logger.info(f"Video file uploaded successfully: {upload_result.get('file_id')}")
                    else:
                        logger.error(f"Failed to upload video file: {upload_result.get('error')}")
                
            except Exception as e:
                logger.error(f"Failed to save generated video to database: {e}")
                # Don't fail the entire generation if DB save fails
        
        # 🔥 APPLY FIX BEFORE RETURNING
        result_data = {
            "success": True,
            "video_data": video_result["video_data"],
            "file_url": file_url,
            "duration": video_result["duration"],
            "provider_used": provider_used,
            "cost": generation_cost,
            "storyboard": storyboard,
            "settings": settings,
            "product_name": product_name,
            "generation_timestamp": datetime.now(timezone.utc),
            "storage_saved": file_url is not None
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
        video_preferences: Dict[str, Any] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """Generate slideshow video with automatic image generation if needed"""
        
        # Import image generator to avoid circular imports
        try:
            from .image_generator import UltraCheapImageGenerator
        except ImportError:
            logger.warning("UltraCheapImageGenerator not available, using placeholder images")
            image_generator = None
        else:
            image_generator = UltraCheapImageGenerator()
        
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
        total_generation_cost = 0
        
        if image_assets:
            # Use provided image assets
            for asset in image_assets:
                if "url" in asset:
                    image_urls.append(asset["url"])
                if "id" in asset:
                    image_asset_ids.append(asset["id"])
        else:
            # Generate images if none provided and image generator is available
            if image_generator:
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
                        image_result = await image_generator.generate_single_image(
                            prompt=prompt,
                            platform="general",
                            user_id=str(current_user.id),
                            campaign_id=int(campaign_id),
                            db=db
                        )
                        
                        if image_result.get("success") and image_result.get("file_url"):
                            image_urls.append(image_result["file_url"])
                            image_asset_ids.append(f"generated_{i}")
                            total_generation_cost += image_result.get("cost", 0)
                                
                    except Exception as e:
                        logger.error(f"Failed to generate slideshow image {i}: {str(e)}")
                        continue
            else:
                # Fallback: Generate simple text-based scenes from script content if no image generator available
                try:
                    # Extract key points from script to create scenes
                    script_sentences = script_content.split('. ')
                    key_points = script_sentences[:4] if len(script_sentences) >= 4 else script_sentences

                    # Create text-based scene descriptions
                    image_urls = []
                    image_asset_ids = []

                    for i, point in enumerate(key_points):
                        # Create a meaningful scene description from the script content
                        scene_description = point.strip()[:50] + "..." if len(point) > 50 else point.strip()
                        image_asset_ids.append(f"text_scene_{i}")
                        # Note: In production, this should integrate with a text-to-image service
                        logger.warning(f"No image generator available. Scene {i}: {scene_description}")

                    if not image_urls:
                        return {
                            "success": False,
                            "error": "No image generation capability available and no fallback images configured"
                        }

                except Exception as e:
                    logger.error(f"Failed to create fallback scenes: {str(e)}")
                    return {
                        "success": False,
                        "error": "Unable to generate video content without image generation capability"
                    }
        
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
                preferences=preferences,
                user_id=str(current_user.id),
                campaign_id=int(campaign_id),
                db=db
            )
            
            if not video_result.get("success"):
                return {
                    "success": False,
                    "error": "Slideshow video generation failed",
                    "details": video_result.get("error")
                }
            
            total_cost = total_generation_cost + video_result.get("cost", 0)
            
            return {
                "success": True,
                "video_url": video_result.get("file_url"),
                "video_id": f"slideshow_{campaign_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "duration": video_result["duration"],
                "provider_used": video_result["provider_used"],
                "cost": total_cost,
                "image_generation_cost": total_generation_cost,
                "video_generation_cost": video_result.get("cost", 0),
                "source_images": image_asset_ids,
                "preferences_used": preferences,
                "generation_timestamp": video_result["generation_timestamp"],
                "storage_saved": video_result.get("storage_saved", False)
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
        """Generate video using centralized video assembly pipeline"""

        try:
            # Create temporary directory for downloaded images
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download images to temp directory
                image_paths = await self._download_images_to_temp(images, temp_dir)

                if not image_paths:
                    raise Exception("No images were successfully downloaded")

                # Convert storyboard to video scenes for assembly pipeline
                assembly_scenes = []
                duration_per_slide = settings.get("duration_per_slide", 3)

                for i, image_path in enumerate(image_paths):
                    scene = AssemblyVideoScene(
                        scene_id=f"slide_{i+1}",
                        image_path=image_path,
                        audio_path=None,  # No audio for basic slideshow
                        duration=float(duration_per_slide),
                        transition_type=settings.get("transition_type", "fade"),
                        effects=None
                    )
                    assembly_scenes.append(scene)

                # Create video specification
                resolution_parts = settings.get("resolution", "1920x1080").split("x")
                video_spec = VideoSpec(
                    width=int(resolution_parts[0]),
                    height=int(resolution_parts[1]),
                    fps=settings.get("fps", 30),
                    bitrate=settings.get("bitrate", "2M"),
                    codec="libx264",
                    format="mp4"
                )

                # Generate unique output filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"slideshow_{timestamp}.mp4"

                # Use video assembly pipeline to create video
                assembled_video = await self.video_assembler.assemble_video(
                    scenes=assembly_scenes,
                    video_type="slideshow",
                    brand_config=None,  # No branding for basic slideshow
                    music_path=None,   # No music for basic slideshow
                    output_filename=output_filename
                )

                logger.info(f"Video assembled using pipeline: {assembled_video.video_path}")

                # Read generated video file
                with open(assembled_video.video_path, "rb") as f:
                    video_data = f.read()

                return {
                    "success": True,
                    "video_data": video_data,
                    "video_path": assembled_video.video_path,
                    "duration": assembled_video.duration_seconds,
                    "file_size": assembled_video.file_size_mb * 1024 * 1024,  # Convert MB to bytes
                    "format": "mp4",
                    "specs": assembled_video.specs,
                    "scenes_count": assembled_video.scenes_count,
                    "assembly_time": assembled_video.assembly_time
                }
                
        except Exception as e:
            logger.error(f"FFmpeg video generation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Note: _create_ffmpeg_input_file method removed - now using centralized video assembly pipeline
    
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
        """Generate video using RunwayML API (placeholder for future implementation)"""
        
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
        """Generate video using Pika Labs API (placeholder for future implementation)"""
        
        # Placeholder for Pika Labs integration
        # In production, you'd implement the actual API calls
        
        return {
            "success": False,
            "error": "Pika Labs integration not implemented yet"
        }
    
    async def generate_batch_videos(
        self,
        campaigns: List[Dict[str, Any]],
        batch_preferences: Dict[str, Any] = None,
        db: Optional[AsyncSession] = None
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
                    video_preferences=batch_preferences,
                    db=db
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
            "ffmpeg_available": self._check_ffmpeg_availability(),
            "crud_integrated": True,
            "storage_integrated": True
        }
    
    # ✅ ENHANCED TESTING WITH STORAGE INTEGRATION
    async def test_video_generation(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Test video generation capabilities"""
        
        test_results = {}
        
        for provider in self.video_providers:
            try:
                if provider["name"] == "ffmpeg_local" and provider["available"]:
                    # Test basic slideshow generation - using real content validation
                    # Note: In production testing, use actual generated content or sample campaign data
                    logger.info("Testing slideshow generation with minimal content validation")
                    test_images = []  # Will be populated by actual image generation during test
                    
                    test_intelligence = {
                        "source_title": "Test Product",
                        "offer_intelligence": {
                            "benefits": ["Test Benefit 1", "Test Benefit 2"]
                        }
                    }
                    
                    result = await self.generate_slideshow_video(
                        intelligence_data=test_intelligence,
                        images=test_images,
                        preferences={"duration_per_slide": 2},
                        user_id=user_id
                    )
                    
                    test_results[provider["name"]] = {
                        "available": True,
                        "cost": provider["cost_per_video"],
                        "test_successful": result.get("success", False),
                        "storage_integration": result.get("storage_saved", False)
                    }
                else:
                    test_results[provider["name"]] = {
                        "available": provider["available"],
                        "cost": provider["cost_per_video"],
                        "test_successful": False,
                        "reason": "Provider not available or not implemented"
                    }
            except Exception as e:
                test_results[provider["name"]] = {
                    "available": False,
                    "error": str(e),
                    "cost": provider["cost_per_video"]
                }
        
        return test_results