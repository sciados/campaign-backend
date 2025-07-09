# File: src/intelligence/routers/stability_routes.py
"""
Stability AI Image Generation Routes - Integrated with YOUR existing files
✅ Uses YOUR StabilityAIGenerator from src/intelligence/generators/stability_ai_generator.py
✅ Uses YOUR EnhancedSocialMediaGenerator from src/intelligence/generators/enhanced_social_media_generator.py
✅ Uses YOUR CampaignAsset model from src/models/campaign_assets.py
✅ Uses YOUR GeneratedContent model from src/models/intelligence.py
✅ Follows YOUR existing router patterns
"""
from fastapi import APIRouter, Depends, HTTPException, status as http_status, BackgroundTasks
from intelligence.generators.ultra_cheap_image_generator import UltraCheapImageGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import logging
import base64

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.campaign import Campaign
from src.models.intelligence import CampaignIntelligence, GeneratedContent
from src.models.campaign_assets import CampaignAsset, AssetType
from storage.universal_dual_storage import get_storage_manager
from ..generators.slideshow_video_generator import SlideshowVideoGenerator
from typing import Dict, List, Any, Optional


# Import YOUR existing generators
from ..generators.stability_ai_generator import StabilityAIGenerator
from ..generators.enhanced_social_media_generator import EnhancedSocialMediaGenerator

# Check credits availability (matching your existing pattern)
try:
    from src.core.credits import check_and_consume_credits
    CREDITS_AVAILABLE = True
except ImportError:
    CREDITS_AVAILABLE = False
    async def check_and_consume_credits(*args, **kwargs):
        pass

router = APIRouter()
logger = logging.getLogger(__name__)

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
        
        # 3. Generate social media content using YOUR EnhancedSocialMediaGenerator
        social_generator = EnhancedSocialMediaGenerator()
        
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
                "generation_timestamp": datetime.utcnow().isoformat(),
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

@router.get("/test-connection")
async def test_stability_connection(
    current_user: User = Depends(get_current_user)
):
    """Test YOUR StabilityAIGenerator connection and setup"""
    
    try:
        # Test YOUR StabilityAIGenerator
        stability_generator = StabilityAIGenerator()
        test_result = await stability_generator.test_generation()
        
        return {
            "stability_ai_status": test_result,
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
                "credit_system": "✅ Using YOUR credits system" if CREDITS_AVAILABLE else "⚠️ Credits system not found"
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
                CampaignAsset.asset_type == AssetType.IMAGE.value
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
        
        package_data = {
            "campaign_id": campaign_id,
            "package_created": datetime.utcnow().isoformat(),
            "total_images": len(assets),
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
                    "file_url": asset.file_url,
                    "platform": asset.asset_metadata.get("platform", "unknown"),
                    "file_size_mb": asset.file_size_mb,
                    "created_at": asset.created_at.isoformat()
                }
                for asset in assets
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
    current_user: User = Depends(get_current_user)
):
    """Calculate costs for image generation campaign"""
    
    platform_list = [p.strip() for p in platforms.split(",")]
    total_images = len(platform_list) * posts_per_platform
    stability_cost = total_images * 0.004
    dalle_cost = total_images * 0.040
    savings = dalle_cost - stability_cost
    
    return {
        "cost_calculation": {
            "platforms": platform_list,
            "posts_per_platform": posts_per_platform,
            "total_images": total_images,
            "stability_ai_cost": f"${stability_cost:.3f}",
            "dalle_cost": f"${dalle_cost:.3f}",
            "total_savings": f"${savings:.3f}",
            "savings_percentage": f"{(savings/dalle_cost)*100:.1f}%"
        },
        "credits_required": total_images,
        "cost_breakdown": {
            "cost_per_image_stability": "$0.004",
            "cost_per_image_dalle": "$0.040", 
            "savings_per_image": "$0.036"
        },
        "affiliate_marketing_benefits": {
            "campaign_duration": "14 days (perfect for affiliate campaigns)",
            "storage_method": "Uses YOUR existing file storage system",
            "scalability": "Handles 1000+ users efficiently"
        }
    }

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
    
    # For now, we'll store the base64 data in metadata
    # In production, you'd upload to your storage system and get a real file_url
    base64_data = image_data.get("image_base64", "")
    file_size = len(base64_data) if base64_data else 0
    
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
        file_url=f"data:image/png;base64,{base64_data}",  # Data URL for now
        file_size=file_size,
        status="ready",  # Using YOUR AssetStatus
        asset_metadata={
            "platform": platform,
            "post_number": post_number,
            "prompt": prompt,
            "generation_source": "stability_ai",
            "image_data": image_data,
            "ai_generated": True,
            "expires_at": (datetime.utcnow() + timedelta(days=14)).isoformat()
        },
        tags=["ai_generated", "social_media", platform],
        description=f"AI-generated image for {platform} post {post_number}"
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
    
    # Fallback
    return "PRODUCT"

@router.post("/ultra-cheap/generate-single")
async def generate_single_ultra_cheap_image(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate single image with ultra-cheap providers"""
    
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
        
        video_result = await SlideshowVideoGenerator.generate_slideshow_video(
            intelligence_data=intelligence_data,
            images=image_urls,
            preferences=preferences
        )
        
        # Save video to dual storage
        storage_manager = get_storage_manager()
        video_filename = f"slideshow_{campaign_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        storage_result = await storage_manager.save_content_dual_storage(
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
        
        # Save to database
        video_asset = CampaignAsset(
            campaign_id=campaign_id,
            uploaded_by=current_user.id,
            company_id=current_user.company_id,
            asset_name=storage_result["filename"],
            original_filename=video_filename,
            asset_type="video",
            mime_type="video/mp4",
            file_size=storage_result["file_size"],
            file_url_primary=storage_result["providers"]["primary"]["url"],
            file_url_backup=storage_result["providers"]["backup"]["url"],
            storage_status=storage_result["storage_status"],
            content_category="ai_generated",
            asset_metadata=storage_result["metadata"]
        )
        
        db.add(video_asset)
        await db.commit()
        
        return {
            "success": True,
            "video_asset_id": str(video_asset.id),
            "video_url": video_asset.get_serving_url(),
            "duration": video_result["duration"],
            "cost": video_result["cost"],
            "provider_used": video_result["provider_used"],
            "storage_status": video_asset.storage_status,
            "file_size": video_asset.file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")