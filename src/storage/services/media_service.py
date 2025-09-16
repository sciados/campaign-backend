# ==============================================================================
# 5. MEDIA SERVICE (Integrating Old Generators)
# ==============================================================================

# src/storage/services/media_service.py
import base64
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from .file_service import FileService
import logging

logger = logging.getLogger(__name__)

class MediaService:
    """Media generation service integrating old generators"""
    
    def __init__(self):
        self.file_service = FileService()
        self._image_generator = None
        self._video_generator = None
    
    def _get_image_generator(self):
        """Lazy load image generator"""
        if self._image_generator is None:
            try:
                # Import from old intelligence generators
                from src.intelligence.generators.image_generator import UltraCheapImageGenerator
                self._image_generator = UltraCheapImageGenerator()
            except ImportError:
                logger.warning("Image generator not available")
        return self._image_generator
    
    def _get_video_generator(self):
        """Lazy load video generator"""
        if self._video_generator is None:
            try:
                # Import from old intelligence generators - DISABLED FOR RAILWAY DEPLOYMENT
                # from src.intelligence.generators.slideshow_video_generator import SlideshowVideoGenerator
                # self._video_generator = SlideshowVideoGenerator()
                logger.warning("Video generator disabled - legacy dependency")
                self._video_generator = None
            except ImportError:
                logger.warning("Video generator not available")
        return self._video_generator
    
    async def generate_campaign_images(
        self,
        db: AsyncSession,
        user_id: str,
        campaign_id: str,
        intelligence_data: Dict[str, Any],
        platforms: List[str] = ["instagram", "facebook", "linkedin"],
        images_per_platform: int = 2
    ) -> Dict[str, Any]:
        """Generate campaign images and store them"""
        
        image_generator = self._get_image_generator()
        if not image_generator:
            return {
                "success": False,
                "error": "Image generator not available"
            }
        
        try:
            # Generate images using old generator
            generation_result = await image_generator.generate_campaign_images(
                intelligence_data=intelligence_data,
                platforms=platforms,
                posts_per_platform=images_per_platform,
                user_id=user_id,
                campaign_id=int(campaign_id) if campaign_id.isdigit() else None,
                db=db
            )
            
            if not generation_result.get("success"):
                return generation_result
            
            # Store generated images
            stored_images = []
            for image_data in generation_result.get("generated_images", []):
                if image_data.get("image_data", {}).get("image_base64"):
                    # Decode and store
                    image_bytes = base64.b64decode(image_data["image_data"]["image_base64"])
                    
                    filename = f"campaign_{campaign_id}_{image_data['platform']}_post_{image_data['post_number']}.png"
                    
                    upload_result = await self.file_service.upload_file(
                        db=db,
                        user_id=user_id,
                        file_data=image_bytes,
                        original_filename=filename,
                        content_type="image/png",
                        campaign_id=campaign_id,
                        metadata={
                            "generated": True,
                            "platform": image_data["platform"],
                            "post_number": image_data["post_number"],
                            "provider": image_data.get("provider_used"),
                            "cost": image_data.get("cost", 0)
                        }
                    )
                    
                    if upload_result["success"]:
                        stored_images.append({
                            "file_id": upload_result["file_id"],
                            "public_url": upload_result["public_url"],
                            "platform": image_data["platform"],
                            "post_number": image_data["post_number"]
                        })
            
            return {
                "success": True,
                "images_generated": len(generation_result.get("generated_images", [])),
                "images_stored": len(stored_images),
                "stored_images": stored_images,
                "total_cost": generation_result.get("total_cost", 0),
                "generation_stats": generation_result.get("generation_stats", {})
            }
            
        except Exception as e:
            logger.error(f"Campaign image generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_slideshow_video(
        self,
        db: AsyncSession,
        user_id: str,
        campaign_id: str,
        intelligence_data: Dict[str, Any],
        image_file_ids: Optional[List[str]] = None,
        video_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate slideshow video and store it"""
        
        video_generator = self._get_video_generator()
        if not video_generator:
            return {
                "success": False,
                "error": "Video generator not available"
            }
        
        try:
            # If no image IDs provided, generate images first
            image_urls = []
            if image_file_ids:
                # Get image URLs from file IDs
                for file_id in image_file_ids:
                    download_result = await self.file_service.download_file(
                        db=db,
                        user_id=user_id,
                        file_id=file_id
                    )
                    if download_result["success"]:
                        # Convert to data URL for video generator
                        file_data = download_result["file_data"]
                        data_url = f"data:{download_result['content_type']};base64,{base64.b64encode(file_data).decode()}"
                        image_urls.append(data_url)
            else:
                # Generate images first
                image_result = await self.generate_campaign_images(
                    db=db,
                    user_id=user_id,
                    campaign_id=campaign_id,
                    intelligence_data=intelligence_data,
                    platforms=["general"],
                    images_per_platform=4
                )
                
                if image_result["success"]:
                    for stored_image in image_result["stored_images"]:
                        image_urls.append(stored_image["public_url"])
            
            if not image_urls:
                return {
                    "success": False,
                    "error": "No images available for video generation"
                }
            
            # Generate video
            video_result = await video_generator.generate_slideshow_video(
                intelligence_data=intelligence_data,
                images=image_urls,
                preferences=video_preferences,
                user_id=user_id,
                campaign_id=int(campaign_id) if campaign_id.isdigit() else None,
                db=db
            )
            
            if not video_result.get("success"):
                return video_result
            
            # Store video if not already stored
            if isinstance(video_result.get("video_data"), bytes) and not video_result.get("file_url"):
                filename = f"campaign_{campaign_id}_slideshow_video.mp4"
                
                upload_result = await self.file_service.upload_file(
                    db=db,
                    user_id=user_id,
                    file_data=video_result["video_data"],
                    original_filename=filename,
                    content_type="video/mp4",
                    campaign_id=campaign_id,
                    metadata={
                        "generated": True,
                        "video_type": "slideshow",
                        "duration": video_result.get("duration"),
                        "provider": video_result.get("provider_used"),
                        "cost": video_result.get("cost", 0)
                    }
                )
                
                if upload_result["success"]:
                    video_result["file_url"] = upload_result["public_url"]
                    video_result["file_id"] = upload_result["file_id"]
            
            return video_result
            
        except Exception as e:
            logger.error(f"Slideshow video generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }