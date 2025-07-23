# File: src/intelligence/routers/stability_routes.py
"""
Stability AI Image Generation Routes - Integrated with YOUR existing files
✅ Uses YOUR StabilityAIGenerator from src/intelligence/generators/stability_ai_generator.py
✅ Uses YOUR SocialMediaGenerator from src/intelligence/generators/social_media_generator.py
✅ Uses YOUR CampaignAsset model from src/models/campaign_assets.py
✅ Uses YOUR GeneratedContent model from src/models/intelligence.py
✅ Follows YOUR existing router patterns
"""
from fastapi import APIRouter, Depends, HTTPException, status as http_status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import uuid
import logging
import base64

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.campaign import Campaign
from src.models.intelligence import CampaignIntelligence, GeneratedContent
from src.models.campaign_assets import CampaignAsset, AssetType
from src.storage.universal_dual_storage import get_storage_manager

# Import YOUR existing generators
from ..generators.stability_ai_generator import StabilityAIGenerator
from ..generators.social_media_generator import SocialMediaGenerator
from ..generators.slideshow_video_generator import SlideshowVideoGenerator

router = APIRouter()
logger = logging.getLogger(__name__)

# Import ultra-cheap generator if available
try:
    from ..generators.ultra_cheap_image_generator import UltraCheapImageGenerator
    ULTRA_CHEAP_AVAILABLE = True
except ImportError:
    ULTRA_CHEAP_AVAILABLE = False
    logger.warning("UltraCheapImageGenerator not available")

# Check credits availability (matching your existing pattern)
try:
    from src.core.credits import check_and_consume_credits
    CREDITS_AVAILABLE = True
except ImportError:
    CREDITS_AVAILABLE = False
    async def check_and_consume_credits(*args, **kwargs):
        pass

@router.post("/generate-campaign-with-images")
async def generate_campaign_with_images(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate complete social media campaign with AI images using YOUR existing generators
    
    Works with your HepatoBurn campaign data:
    {
        "campaign_id": "f4116b74-f47f-4fd2-8ee5-ff5315930104",
        "platforms": ["instagram", "facebook", "tiktok"],
        "content_count": 5,
        "image_style": "health",
        "generate_images": true
    }
    """
    
    campaign_id = request_data.get("campaign_id")
    platforms = request_data.get("platforms", ["instagram", "facebook"])
    content_count = request_data.get("content_count", 3)
    image_style = request_data.get("image_style", "health")
    generate_images = request_data.get("generate_images", True)
    
    if not campaign_id:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="campaign_id is required"
        )
    
    # Check credits using YOUR credit system
    estimated_images = len(platforms) * content_count if generate_images else 0
    if CREDITS_AVAILABLE and estimated_images > 0:
        try:
            await check_and_consume_credits(
                user=current_user,
                operation="stability_ai_generation",
                credits_required=estimated_images,
                db=db
            )
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Need {estimated_images} credits for {estimated_images} images: {str(e)}"
            )
    
    try:
        # 1. Get campaign intelligence data using YOUR CampaignIntelligence model
        intelligence_query = select(CampaignIntelligence).where(
            and_(
                CampaignIntelligence.campaign_id == campaign_id,
                CampaignIntelligence.user_id == current_user.id
            )
        )
        intelligence_result = await db.execute(intelligence_query)
        intelligence_record = intelligence_result.scalar_one_or_none()
        
        if not intelligence_record:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="No intelligence data found for this campaign. Please analyze a URL first."
            )
        
        # 2. Extract intelligence data (using your HepatoBurn structure)
        intelligence_data = {
            "product_name": _extract_product_name(intelligence_record),
            "offer_intelligence": intelligence_record.offer_intelligence or {},
            "psychology_intelligence": intelligence_record.psychology_intelligence or {},
            "content_intelligence": intelligence_record.content_intelligence or {},
            "scientific_intelligence": intelligence_record.scientific_intelligence or {},
            "credibility_intelligence": intelligence_record.credibility_intelligence or {},
            "emotional_transformation_intelligence": intelligence_record.emotional_transformation_intelligence or {}
        }
        
        logger.info(f"🎯 Generating campaign for {intelligence_data['product_name']}")
        
        # 3. Generate social media content using YOUR SocialMediaGenerator
        social_generator = SocialMediaGenerator()
        
        campaign_preferences = {
            "platforms": platforms,
            "content_count": content_count,
            "theme": "product_benefits",
            "generate_images": generate_images,
            "image_style": image_style
        }
        
        social_campaign = await social_generator.generate_social_campaign(
            intelligence_data, 
            campaign_preferences
        )
        
        logger.info(f"📱 Generated {social_campaign['content']['total_pieces']} social media posts")
        
        # 4. Generate actual images using YOUR StabilityAIGenerator
        generated_images = []
        stability_generator = StabilityAIGenerator() if generate_images else None
        total_cost = 0.0
        
        if generate_images and stability_generator:
            logger.info(f"🖼️ Starting image generation for {estimated_images} images")
            
            for platform, platform_data in social_campaign["content"]["platforms"].items():
                for post in platform_data["posts"]:
                    if post.get("image_prompt"):
                        try:
                            logger.info(f"🎨 Generating image for {platform} post {post['post_number']}")
                            
                            # Generate image using YOUR Stability AI generator
                            image_result = await stability_generator.generate_social_media_image(
                                prompt=post["image_prompt"],
                                platform=platform,
                                style=image_style
                            )
                            
                            if image_result.get("success"):
                                # Save image to YOUR campaign_assets table
                                asset_id = await _save_image_to_your_assets_table(
                                    db=db,
                                    campaign_id=campaign_id,
                                    user_id=current_user.id,
                                    company_id=current_user.company_id,
                                    image_data=image_result["image_data"],
                                    platform=platform,
                                    prompt=post["image_prompt"],
                                    post_number=post["post_number"]
                                )
                                
                                post["generated_image"] = {
                                    "asset_id": asset_id,
                                    "cost": image_result["estimated_cost"],
                                    "platform": platform,
                                    "dimensions": image_result["dimensions"],
                                    "status": "generated",
                                    "download_ready": True
                                }
                                
                                generated_images.append({
                                    "asset_id": asset_id,
                                    "platform": platform,
                                    "post_number": post["post_number"],
                                    "cost": image_result["estimated_cost"]
                                })
                                
                                total_cost += image_result["estimated_cost"]
                                logger.info(f"✅ Image saved with asset_id: {asset_id}")
                                
                            else:
                                logger.error(f"❌ Image generation failed: {image_result.get('error')}")
                                post["generated_image"] = {
                                    "status": "failed",
                                    "error": image_result.get("error", "Unknown error")
                                }
                        
                        except Exception as e:
                            logger.error(f"Image generation failed for {platform} post {post['post_number']}: {str(e)}")
                            post["generated_image"] = {
                                "status": "failed", 
                                "error": str(e)
                            }
        
        # 5. Save social media content to YOUR generated_content table
        content_id = str(uuid.uuid4())
        
        generated_content = GeneratedContent(
            id=content_id,
            campaign_id=campaign_id,
            user_id=current_user.id,
            company_id=current_user.company_id,
            content_type="social_media_campaign_with_images",
            content_title=social_campaign["title"],
            content_body=str(social_campaign["content"]),  # JSON as string
            content_metadata={
                "platforms_covered": platforms,
                "total_posts": social_campaign["content"]["total_pieces"],
                "images_generated": len(generated_images),
                "total_image_cost": total_cost,
                "cost_savings_vs_dalle": (len(generated_images) * 0.040) - total_cost,
                "generation_timestamp": datetime.now(timezone.utc),
                "intelligence_source_id": str(intelligence_record.id),
                "ready_to_publish": True,
                "product_name": intelligence_data["product_name"]
            },
            generation_settings={
                "platforms": platforms,
                "content_count": content_count,
                "image_style": image_style,
                "generate_images": generate_images
            },
            intelligence_used={
                "intelligence_id": str(intelligence_record.id),
                "confidence_score": intelligence_record.confidence_score,
                "source_url": intelligence_record.source_url
            },
            intelligence_source_id=intelligence_record.id
        )
        
        db.add(generated_content)
        await db.commit()
        
        logger.info(f"💾 Saved content with ID: {content_id}")
        
        return {
            "success": True,
            "content_id": content_id,
            "campaign_id": campaign_id,
            "product_name": intelligence_data["product_name"],
            "platforms_generated": platforms,
            "total_posts": social_campaign["content"]["total_pieces"],
            "images_generated": len(generated_images),
            "total_cost": round(total_cost, 3),
            "cost_savings_vs_dalle": f"${round((len(generated_images) * 0.040) - total_cost, 3)}",
            "generated_images": generated_images,
            "social_campaign": social_campaign,
            "ready_for_download": True,
            "message": f"✅ Generated {social_campaign['content']['total_pieces']} social media posts with {len(generated_images)} AI images for ${round(total_cost, 3)}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Campaign generation failed: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Campaign generation failed: {str(e)}"
        )

@router.post("/generate-single-image")
async def generate_single_image(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a single AI image using YOUR StabilityAIGenerator"""
    
    campaign_id = request_data.get("campaign_id")
    prompt = request_data.get("prompt")
    platform = request_data.get("platform", "instagram")
    style = request_data.get("style", "health")
    
    if not campaign_id or not prompt:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="campaign_id and prompt are required"
        )
    
    # Check credits using YOUR credit system
    if CREDITS_AVAILABLE:
        try:
            await check_and_consume_credits(
                user=current_user,
                operation="stability_ai_generation",
                credits_required=1,
                db=db
            )
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits: {str(e)}"
            )
    
    try:
        # Generate image using YOUR StabilityAIGenerator
        stability_generator = StabilityAIGenerator()
        
        image_result = await stability_generator.generate_social_media_image(
            prompt=prompt,
            platform=platform,
            style=style
        )
        
        if not image_result.get("success"):
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Image generation failed: {image_result.get('error', 'Unknown error')}"
            )
        
        # Save to YOUR campaign_assets table
        asset_id = await _save_image_to_your_assets_table(
            db=db,
            campaign_id=campaign_id,
            user_id=current_user.id,
            company_id=current_user.company_id,
            image_data=image_result["image_data"],
            platform=platform,
            prompt=prompt,
            post_number=1
        )
        
        return {
            "success": True,
            "asset_id": asset_id,
            "campaign_id": campaign_id,
            "platform": platform,
            "dimensions": image_result["dimensions"],
            "cost": image_result["estimated_cost"],
            "savings_vs_dalle": image_result["savings_vs_dalle"],
            "model_used": image_result["model_used"],
            "prompt_used": image_result["enhanced_prompt"],
            "ready_for_download": True,
            "message": f"✅ Image generated successfully for ${image_result['estimated_cost']:.3f}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Single image generation failed: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}"
        )

@router.post("/generate-slideshow-video")
async def generate_slideshow_video(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate slideshow video from campaign images"""
    
    campaign_id = request_data.get("campaign_id")
    video_preferences = request_data.get("video_preferences", {})
    image_assets = request_data.get("image_assets", [])  # List of asset IDs or URLs
    
    if not campaign_id:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="campaign_id is required"
        )
    
    # Check credits using YOUR credit system
    if CREDITS_AVAILABLE:
        try:
            await check_and_consume_credits(
                user=current_user,
                operation="slideshow_video_generation",
                credits_required=1,
                db=db
            )
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits: {str(e)}"
            )
    
    try:
        # 1. Get campaign intelligence data
        intelligence_query = select(CampaignIntelligence).where(
            and_(
                CampaignIntelligence.campaign_id == campaign_id,
                CampaignIntelligence.user_id == current_user.id
            )
        )
        intelligence_result = await db.execute(intelligence_query)
        intelligence_record = intelligence_result.scalar_one_or_none()
        
        if not intelligence_record:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="No intelligence data found for this campaign"
            )
        
        # 2. Extract intelligence data
        intelligence_data = {
            "product_name": _extract_product_name(intelligence_record),
            "offer_intelligence": intelligence_record.offer_intelligence or {},
            "psychology_intelligence": intelligence_record.psychology_intelligence or {},
            "content_intelligence": intelligence_record.content_intelligence or {}
        }
        
        # 3. Prepare image assets
        prepared_image_assets = []
        
        if image_assets:
            # Use provided image assets
            for asset_info in image_assets:
                if isinstance(asset_info, str):
                    # Asset ID provided
                    asset_query = select(CampaignAsset).where(
                        and_(
                            CampaignAsset.id == asset_info,
                            CampaignAsset.campaign_id == campaign_id,
                            CampaignAsset.uploaded_by == current_user.id
                        )
                    )
                    asset_result = await db.execute(asset_query)
                    asset = asset_result.scalar_one_or_none()
                    
                    if asset:
                        prepared_image_assets.append({
                            "id": str(asset.id),
                            "url": asset.file_url or asset.file_url_primary,
                            "metadata": asset.asset_metadata or {}
                        })
                elif isinstance(asset_info, dict):
                    # Asset info dict provided
                    prepared_image_assets.append(asset_info)
        
        # 4. Generate slideshow video
        slideshow_generator = SlideshowVideoGenerator()
        
        video_result = await slideshow_generator.generate_slideshow_video_with_image_generation(
            intelligence_data=intelligence_data,
            campaign_id=campaign_id,
            current_user=current_user,
            image_assets=prepared_image_assets,
            video_preferences=video_preferences
        )
        
        if not video_result.get("success"):
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Video generation failed: {video_result.get('error', 'Unknown error')}"
            )
        
        # 5. Save video to YOUR campaign_assets table
        video_asset_id = str(uuid.uuid4())
        
        video_asset = CampaignAsset(
            id=video_asset_id,
            campaign_id=campaign_id,
            uploaded_by=current_user.id,
            company_id=current_user.company_id,
            asset_name=f"slideshow_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            original_filename="slideshow_video.mp4",
            asset_type=AssetType.VIDEO.value,
            mime_type="video/mp4",
            file_url=video_result.get("video_url"),
            file_size_mb=0,  # Will be calculated by storage system
            status="ready",
            asset_metadata={
                "video_type": "slideshow",
                "duration": video_result.get("duration"),
                "provider_used": video_result.get("provider_used"),
                "generation_cost": video_result.get("cost"),
                "source_images": [img.get("id") for img in prepared_image_assets],
                "ai_generated": True,
                "preferences_used": video_preferences
            },
            tags=["ai_generated", "slideshow", "video"],
            description=f"AI-generated slideshow video for {intelligence_data['product_name']}"
        )
        
        db.add(video_asset)
        await db.commit()
        
        return {
            "success": True,
            "video_asset_id": video_asset_id,
            "campaign_id": campaign_id,
            "video_url": video_result.get("video_url"),
            "duration": video_result.get("duration"),
            "provider_used": video_result.get("provider_used"),
            "cost": video_result.get("cost"),
            "source_images": len(prepared_image_assets),
            "ready_for_download": True,
            "message": f"✅ Slideshow video generated successfully for ${video_result.get('cost', 0):.3f}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Slideshow video generation failed: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video generation failed: {str(e)}"
        )

@router.post("/ultra-cheap/generate-single")
async def generate_single_ultra_cheap_image(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate single image with ultra-cheap providers"""
    
    if not ULTRA_CHEAP_AVAILABLE:
        raise HTTPException(
            status_code=http_status.HTTP_501_NOT_IMPLEMENTED,
            detail="Ultra-cheap image generator not available"
        )
    
    try:
        generator = UltraCheapImageGenerator()
        
        result = await generator.generate_single_image(
            prompt=request_data.get("prompt", "Professional product photography"),
            platform=request_data.get("platform", "instagram"),
            negative_prompt=request_data.get("negative_prompt", ""),
            style_preset=request_data.get("style_preset", "photographic")
        )
        
        # Save to dual storage if campaign_id provided
        if request_data.get("campaign_id"):
            storage_manager = get_storage_manager()
            
            storage_result = await storage_manager.save_content_dual_storage(
                content_data=result["image_data"]["image_base64"],
                content_type="image",
                filename=f"ai_image_{result['platform']}.png",
                user_id=str(current_user.id),
                campaign_id=request_data["campaign_id"],
                metadata={
                    "ai_generated": True,
                    "provider_used": result["provider_used"],
                    "generation_cost": result["cost"],
                    "prompt": result["prompt"]
                }
            )
            
            result["storage_result"] = storage_result
        
        return {
            "success": True,
            "image_result": result,
            "user_id": str(current_user.id)
        }
        
    except Exception as e:
        logger.error(f"Ultra-cheap image generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.post("/ultra-cheap/generate-campaign")
async def generate_campaign_ultra_cheap_images(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate complete campaign with ultra-cheap images"""
    
    if not ULTRA_CHEAP_AVAILABLE:
        raise HTTPException(
            status_code=http_status.HTTP_501_NOT_IMPLEMENTED,
            detail="Ultra-cheap image generator not available"
        )
    
    try:
        # Get campaign intelligence
        campaign_id = request_data.get("campaign_id")
        
        if not campaign_id:
            raise HTTPException(status_code=400, detail="campaign_id is required")
        
        # Get intelligence data from database
        intelligence_query = select(CampaignIntelligence).where(
            and_(
                CampaignIntelligence.campaign_id == campaign_id,
                CampaignIntelligence.user_id == current_user.id
            )
        )
        intelligence_result = await db.execute(intelligence_query)
        intelligence_record = intelligence_result.scalar_one_or_none()
        
        if not intelligence_record:
            raise HTTPException(status_code=404, detail="Campaign intelligence not found")
        
        # Extract intelligence data
        intelligence_data = {
            "product_name": intelligence_record.source_title or "PRODUCT",
            "offer_intelligence": intelligence_record.offer_intelligence or {},
            "psychology_intelligence": intelligence_record.psychology_intelligence or {},
            "content_intelligence": intelligence_record.content_intelligence or {}
        }
        
        # Generate ultra-cheap images
        generator = UltraCheapImageGenerator()
        
        campaign_result = await generator.generate_campaign_images(
            intelligence_data=intelligence_data,
            campaign_id=campaign_id,
            platforms=request_data.get("platforms", ["instagram", "facebook"]),
            image_count=request_data.get("image_count", 4)
        )
        
        return {
            "success": True,
            "campaign_result": campaign_result,
            "campaign_id": campaign_id,
            "product_name": intelligence_data["product_name"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ultra-cheap campaign generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Campaign generation failed: {str(e)}")

@router.get("/test-connection")
async def test_stability_connection(
    current_user: User = Depends(get_current_user)
):
    """Test YOUR StabilityAIGenerator connection and setup"""
    
    try:
        # Test YOUR StabilityAIGenerator
        stability_generator = StabilityAIGenerator()
        test_result = await stability_generator.test_generation()
        
        # Test slideshow generator
        slideshow_generator = SlideshowVideoGenerator()
        slideshow_stats = slideshow_generator.get_video_statistics()
        
        return {
            "stability_ai_status": test_result,
            "slideshow_generator_status": slideshow_stats,
            "integration_ready": test_result.get("api_working", False),
            "cost_benefits": {
                "stability_ai_cost": "$0.004 per image",
                "dalle_cost": "$0.040 per image", 
                "savings_per_image": "$0.036 (90% savings)",
                "cost_for_10_images": "Stability: $0.04 vs DALL-E: $0.40"
            },
            "setup_instructions": {
                "get_api_key": "https://platform.stability.ai/",
                "environment_variable": "STABILITY_API_KEY",
                "current_setup": "✅ Ready" if test_result.get("api_working") else "❌ Setup Required"
            },
            "your_system_status": {
                "generators_available": "✅ Using YOUR existing generators",
                "database_models": "✅ Using YOUR CampaignAsset model",
                "credit_system": "✅ Using YOUR credits system" if CREDITS_AVAILABLE else "⚠️ Credits system not found",
                "ultra_cheap_available": "✅ Available" if ULTRA_CHEAP_AVAILABLE else "❌ Not available"
            }
        }
        
    except Exception as e:
        return {
            "stability_ai_status": {
                "test_status": "❌ FAILED",
                "error": str(e)
            },
            "integration_ready": False,
            "setup_help": "Check STABILITY_API_KEY environment variable in Railway"
        }

@router.get("/{campaign_id}/download-package")
async def download_campaign_package(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download all campaign assets using YOUR CampaignAsset model"""
    
    try:
        # Get campaign assets using YOUR CampaignAsset model
        assets_query = select(CampaignAsset).where(
            and_(
                CampaignAsset.campaign_id == campaign_id,
                CampaignAsset.uploaded_by == current_user.id,
                CampaignAsset.asset_type.in_([AssetType.IMAGE.value, AssetType.VIDEO.value])
            )
        )
        assets_result = await db.execute(assets_query)
        assets = assets_result.scalars().all()
        
        # Get generated content using YOUR GeneratedContent model
        content_query = select(GeneratedContent).where(
            and_(
                GeneratedContent.campaign_id == campaign_id,
                GeneratedContent.user_id == current_user.id,
                GeneratedContent.content_type.like("%social_media%")
            )
        )
        content_result = await db.execute(content_query)
        content_items = content_result.scalars().all()
        
        # Separate images and videos
        images = [asset for asset in assets if asset.asset_type == AssetType.IMAGE.value]
        videos = [asset for asset in assets if asset.asset_type == AssetType.VIDEO.value]
        
        package_data = {
            "campaign_id": campaign_id,
            "package_created": datetime.now(timezone.utc),
            "total_images": len(images),
            "total_videos": len(videos),
            "total_content_pieces": len(content_items),
            "expires_in_days": 14,  # 14-day campaign storage
            "download_instructions": "Use the asset_ids to download individual images via YOUR assets API",
            "content_summary": [
                {
                    "content_id": item.id,
                    "content_type": item.content_type,
                    "title": item.content_title,
                    "platforms": item.content_metadata.get("platforms_covered", []),
                    "posts_count": item.content_metadata.get("total_posts", 0),
                    "images_count": item.content_metadata.get("images_generated", 0),
                    "created_at": item.created_at.isoformat()
                }
                for item in content_items
            ],
            "image_summary": [
                {
                    "asset_id": str(asset.id),
                    "asset_name": asset.asset_name,
                    "file_url": asset.file_url or asset.file_url_primary,
                    "platform": asset.asset_metadata.get("platform", "unknown"),
                    "file_size_mb": asset.file_size_mb,
                    "created_at": asset.created_at.isoformat()
                }
                for asset in images
            ],
            "video_summary": [
                {
                    "asset_id": str(asset.id),
                    "asset_name": asset.asset_name,
                    "file_url": asset.file_url or asset.file_url_primary,
                    "duration": asset.asset_metadata.get("duration", "unknown"),
                    "provider_used": asset.asset_metadata.get("provider_used", "unknown"),
                    "file_size_mb": asset.file_size_mb,
                    "created_at": asset.created_at.isoformat()
                }
                for asset in videos
            ]
        }
        
        return package_data
        
    except Exception as e:
        logger.error(f"Package download failed: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Package creation failed: {str(e)}"
        )

@router.get("/cost-calculator")
async def cost_calculator(
    platforms: str = "instagram,facebook",
    posts_per_platform: int = 3,
    include_video: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Calculate costs for image generation campaign"""
    
    platform_list = [p.strip() for p in platforms.split(",")]
    total_images = len(platform_list) * posts_per_platform
    stability_cost = total_images * 0.004
    dalle_cost = total_images * 0.040
    savings = dalle_cost - stability_cost
    
    # Add video cost if requested
    video_cost = 0.0
    if include_video:
        video_cost = 0.25  # Estimated slideshow video cost
        stability_cost += video_cost
    
    return {
        "cost_calculation": {
            "platforms": platform_list,
            "posts_per_platform": posts_per_platform,
            "total_images": total_images,
            "include_video": include_video,
            "stability_ai_cost": f"${stability_cost:.3f}",
            "dalle_cost": f"${dalle_cost:.3f}",
            "video_cost": f"${video_cost:.3f}" if include_video else "$0.000",
            "total_savings": f"${savings:.3f}",
            "savings_percentage": f"{(savings/dalle_cost)*100:.1f}%"
        },
        "credits_required": total_images + (1 if include_video else 0),
        "cost_breakdown": {
            "cost_per_image_stability": "$0.004",
            "cost_per_image_dalle": "$0.040", 
            "savings_per_image": "$0.036",
            "slideshow_video_cost": "$0.25"
        },
        "affiliate_marketing_benefits": {
            "campaign_duration": "14 days (perfect for affiliate campaigns)",
            "storage_method": "Uses YOUR existing file storage system",
            "scalability": "Handles 1000+ users efficiently"
        }
    }

@router.get("/{campaign_id}/analytics")
async def get_campaign_analytics(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for campaign generation"""
    
    try:
        # Get all assets for this campaign
        assets_query = select(CampaignAsset).where(
            and_(
                CampaignAsset.campaign_id == campaign_id,
                CampaignAsset.uploaded_by == current_user.id
            )
        )
        assets_result = await db.execute(assets_query)
        assets = assets_result.scalars().all()
        
        # Get all generated content
        content_query = select(GeneratedContent).where(
            and_(
                GeneratedContent.campaign_id == campaign_id,
                GeneratedContent.user_id == current_user.id
            )
        )
        content_result = await db.execute(content_query)
        content_items = content_result.scalars().all()
        
        # Calculate analytics
        total_images = len([a for a in assets if a.asset_type == AssetType.IMAGE.value])
        total_videos = len([a for a in assets if a.asset_type == AssetType.VIDEO.value])
        total_cost = 0.0
        
        # Extract costs from metadata
        for asset in assets:
            if asset.asset_metadata and "generation_cost" in asset.asset_metadata:
                total_cost += float(asset.asset_metadata["generation_cost"])
        
        for content in content_items:
            if content.content_metadata and "total_image_cost" in content.content_metadata:
                total_cost += float(content.content_metadata["total_image_cost"])
        
        return {
            "campaign_id": campaign_id,
            "analytics": {
                "total_assets": len(assets),
                "total_images": total_images,
                "total_videos": total_videos,
                "total_content_pieces": len(content_items),
                "total_generation_cost": round(total_cost, 3),
                "estimated_dalle_cost": round((total_images * 0.040) + (total_videos * 1.0), 3),
                "total_savings": round((total_images * 0.036) + (total_videos * 0.75), 3),
                "average_cost_per_asset": round(total_cost / len(assets), 3) if assets else 0
            },
            "generation_breakdown": {
                "stability_ai_images": total_images,
                "slideshow_videos": total_videos,
                "social_media_campaigns": len([c for c in content_items if "social_media" in c.content_type])
            },
            "cost_comparison": {
                "your_cost": f"${total_cost:.3f}",
                "traditional_cost": f"${(total_images * 0.040) + (total_videos * 1.0):.3f}",
                "savings_percentage": f"{((total_images * 0.036) + (total_videos * 0.75)) / ((total_images * 0.040) + (total_videos * 1.0)) * 100:.1f}%" if (total_images + total_videos) > 0 else "0%"
            }
        }
        
    except Exception as e:
        logger.error(f"Analytics retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics retrieval failed: {str(e)}"
        )

@router.delete("/{campaign_id}/cleanup")
async def cleanup_campaign_assets(
    campaign_id: str,
    asset_types: Optional[str] = "images,videos",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Clean up campaign assets (useful for testing and storage management)"""
    
    try:
        asset_type_list = [t.strip() for t in asset_types.split(",")]
        
        # Map string types to enum values
        type_mapping = {
            "images": AssetType.IMAGE.value,
            "videos": AssetType.VIDEO.value,
            "documents": AssetType.DOCUMENT.value
        }
        
        asset_type_values = [type_mapping.get(t) for t in asset_type_list if type_mapping.get(t)]
        
        # Delete assets
        assets_query = select(CampaignAsset).where(
            and_(
                CampaignAsset.campaign_id == campaign_id,
                CampaignAsset.uploaded_by == current_user.id,
                CampaignAsset.asset_type.in_(asset_type_values)
            )
        )
        assets_result = await db.execute(assets_query)
        assets_to_delete = assets_result.scalars().all()
        
        deleted_count = 0
        for asset in assets_to_delete:
            await db.delete(asset)
            deleted_count += 1
        
        await db.commit()
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "deleted_assets": deleted_count,
            "asset_types_deleted": asset_type_list,
            "message": f"✅ Deleted {deleted_count} assets from campaign {campaign_id}"
        }
        
    except Exception as e:
        logger.error(f"Asset cleanup failed: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Asset cleanup failed: {str(e)}"
        )

# ============================================================================
# UTILITY FUNCTIONS FOR YOUR EXISTING MODELS
# ============================================================================

async def _save_image_to_your_assets_table(
    db: AsyncSession,
    campaign_id: str,
    user_id: str,
    company_id: str,
    image_data: Dict[str, Any],
    platform: str,
    prompt: str,
    post_number: int
) -> str:
    """Save generated image to YOUR campaign_assets table using YOUR CampaignAsset model"""
    
    asset_id = str(uuid.uuid4())
    
    # For now, we'll store the base64 data in metadata and create a data URL
    # In production, you'd upload to your storage system and get a real file_url
    base64_data = image_data.get("image_base64", "")
    file_size = len(base64_data) if base64_data else 0
    
    # Convert base64 size to MB (rough estimate)
    file_size_mb = file_size / (1024 * 1024) if file_size > 0 else 0
    
    # Create asset using YOUR CampaignAsset model
    asset = CampaignAsset(
        id=asset_id,
        campaign_id=campaign_id,
        uploaded_by=user_id,
        company_id=company_id,
        asset_name=f"{platform}_post_{post_number}_image",
        original_filename=f"{platform}_image_{post_number}.png",
        asset_type=AssetType.IMAGE.value,  # Using YOUR AssetType enum
        mime_type="image/png",
        file_url=f"data:image/png;base64,{base64_data}",  # Data URL for immediate use
        file_size_mb=file_size_mb,
        status="ready",  # Using YOUR asset status
        asset_metadata={
            "platform": platform,
            "post_number": post_number,
            "prompt": prompt,
            "generation_source": "stability_ai",
            "image_data": image_data,
            "ai_generated": True,
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=14)).isoformat(),
            "dimensions": image_data.get("dimensions", "1024x1024"),
            "generation_cost": image_data.get("estimated_cost", 0.004)
        },
        tags=["ai_generated", "social_media", platform],
        description=f"AI-generated image for {platform} post {post_number}",
        content_category="ai_generated"
    )
    
    db.add(asset)
    await db.commit()
    
    logger.info(f"💾 Saved image asset {asset_id} to YOUR campaign_assets table")
    return asset_id

def _extract_product_name(intelligence_record) -> str:
    """Extract product name from YOUR intelligence data (HepatoBurn example)"""
    
    # Using YOUR intelligence data structure
    content_intel = intelligence_record.content_intelligence or {}
    key_messages = content_intel.get("key_messages", [])
    
    # From your HepatoBurn data: key_messages: ["HEPATOBURN"]
    if key_messages and isinstance(key_messages, list) and len(key_messages) > 0:
        return key_messages[0]
    
    # From your HepatoBurn data: source_title: "HEPATOBURN"
    if intelligence_record.source_title:
        return intelligence_record.source_title
    
    # Try offer intelligence
    offer_intel = intelligence_record.offer_intelligence or {}
    if offer_intel.get("product_name"):
        return offer_intel["product_name"]
    
    # Fallback
    return "PRODUCT"

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    
    try:
        # Test basic functionality
        stability_generator = StabilityAIGenerator()
        slideshow_generator = SlideshowVideoGenerator()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc),
            "components": {
                "stability_ai_generator": "✅ Available",
                "slideshow_generator": "✅ Available",
                "ultra_cheap_generator": "✅ Available" if ULTRA_CHEAP_AVAILABLE else "❌ Not available",
                "credits_system": "✅ Available" if CREDITS_AVAILABLE else "❌ Not available"
            },
            "version": "1.0.0",
            "integration_status": "Fully integrated with YOUR existing system"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc)
        }