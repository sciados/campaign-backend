# src/content/api/video_generation_routes.py
"""
Video Generation API Routes
Handles AI video creation from scripts using generated visuals and voiceovers
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import logging

from src.core.database.session import get_async_db
from src.users.services.auth_service import AuthService
from src.content.services.video_generation_orchestrator import (
    create_video_generation_orchestrator,
    VideoGenerationRequest,
    VideoType,
    VisualStyle,
    VoiceType
)
from src.intelligence.repositories.intelligence_repository import IntelligenceRepository
from src.core.crud.campaign_crud import CampaignCRUD
from src.users.services.user_crud import UserCRUD

router = APIRouter(prefix="/api/video", tags=["video-generation"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
) -> str:
    """Get current user ID from token"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return str(user.id)

@router.post("/generate/{campaign_id}")
async def generate_video_from_script(
    campaign_id: str,
    request_data: Dict[str, Any],
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Generate a complete video from a script using AI
    
    Body should contain:
    {
        "script_content": "Your video script text...",
        "video_type": "youtube_short|tiktok|instagram_reel|youtube_standard|facebook_ad",
        "visual_style": "realistic|animated|minimalist|infographic|product_focus|lifestyle",
        "voice_type": "male_professional|female_professional|young_energetic|authoritative",
        "brand_colors": ["#FF0000", "#00FF00"],
        "logo_url": "https://...",
        "music_style": "upbeat|calm|energetic|corporate"
    }
    """
    
    try:
        # Validate required fields
        script_content = request_data.get("script_content")
        if not script_content or len(script_content.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="script_content is required and must be at least 10 characters"
            )
        
        # Parse video type
        video_type_str = request_data.get("video_type", "youtube_short")
        try:
            video_type = VideoType(video_type_str)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid video_type. Must be one of: {[vt.value for vt in VideoType]}"
            )
        
        # Parse visual style
        visual_style_str = request_data.get("visual_style", "realistic")
        try:
            visual_style = VisualStyle(visual_style_str)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid visual_style. Must be one of: {[vs.value for vs in VisualStyle]}"
            )
        
        # Parse voice type
        voice_type_str = request_data.get("voice_type", "female_professional")
        try:
            voice_type = VoiceType(voice_type_str)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid voice_type. Must be one of: {[vt.value for vt in VoiceType]}"
            )
        
        # Get intelligence data for this campaign
        intelligence_repository = IntelligenceRepository()
        campaign_crud = CampaignCRUD()

        try:
            # Get campaign information
            campaign = await campaign_crud.get(db=db, id=campaign_id)
            if not campaign:
                raise HTTPException(
                    status_code=404,
                    detail="Campaign not found"
                )

            # Verify campaign belongs to user
            if campaign.user_id != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied to this campaign"
                )

            # Get intelligence data for this campaign
            intelligence_data = {}
            if campaign.intelligence_id:
                intelligence = await intelligence_repository.find_by_id(
                    campaign.intelligence_id, db
                )
                if intelligence:
                    # Convert intelligence entity to dictionary format
                    intelligence_data = {
                        "id": intelligence.id,
                        "source_url": intelligence.salespage_url,
                        "product_analysis": intelligence.product_data[0].__dict__ if intelligence.product_data else {},
                        "audience_analysis": intelligence.market_data[0].__dict__ if intelligence.market_data else {},
                        "brand_analysis": {
                            "colors": request_data.get("brand_colors", ["#007BFF"]),
                            "name": intelligence.source_title or "Product"
                        },
                        "offer_intelligence": {
                            "price_point": intelligence.price_point,
                            "benefits": intelligence.key_benefits or [],
                            "target_audience": intelligence.target_audience
                        }
                    }
                else:
                    logger.warning(f"Intelligence data not found for campaign {campaign_id}")

            # Fallback if no intelligence data available
            if not intelligence_data:
                intelligence_data = {
                    "product_analysis": {"name": campaign.name or "Product"},
                    "audience_analysis": {"demographics": {}},
                    "brand_analysis": {"colors": request_data.get("brand_colors", ["#007BFF"])},
                    "offer_intelligence": {"benefits": ["Enhanced performance", "Better results"]}
                }
                logger.info(f"Using fallback intelligence data for campaign {campaign_id}")

        except Exception as e:
            logger.error(f"Failed to retrieve intelligence data for campaign {campaign_id}: {e}")
            # Use fallback data if intelligence retrieval fails
            intelligence_data = {
                "product_analysis": {"name": "Product"},
                "audience_analysis": {"demographics": {}},
                "brand_analysis": {"colors": request_data.get("brand_colors", ["#007BFF"])},
                "offer_intelligence": {"benefits": ["Enhanced performance", "Better results"]}
            }
        
        # Create video generation request
        video_request = VideoGenerationRequest(
            campaign_id=campaign_id,
            user_id=user_id,
            script_content=script_content,
            video_type=video_type,
            visual_style=visual_style,
            voice_type=voice_type,
            intelligence_data=intelligence_data,
            brand_colors=request_data.get("brand_colors"),
            logo_url=request_data.get("logo_url"),
            music_style=request_data.get("music_style", "upbeat")
        )
        
        # Initialize video generation orchestrator
        orchestrator = create_video_generation_orchestrator()
        
        # Generate video (this will be async in production)
        result = await orchestrator.generate_video(video_request)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Video generation failed: {result.get('error')}"
            )
        
        logger.info(f"Video generation completed for campaign {campaign_id}")
        
        return {
            "success": True,
            "message": "Video generated successfully",
            "campaign_id": campaign_id,
            "video_url": result["video_url"],
            "duration_seconds": result["duration_seconds"],
            "scenes_count": result["scenes_count"],
            "generation_details": {
                "video_type": video_type.value,
                "visual_style": visual_style.value,
                "voice_type": voice_type.value,
                "visual_assets_created": result["visual_assets"],
                "generation_time": result["generation_time"]
            },
            "video_specs": result["video_specs"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation failed for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video: {str(e)}"
        )

@router.get("/status/{job_id}")
async def get_video_generation_status(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get status of video generation job"""
    
    try:
        orchestrator = create_video_generation_orchestrator()
        status = await orchestrator.get_generation_status(job_id)
        
        return {
            "job_id": job_id,
            "status": status["status"],
            "progress": status["progress"],
            "current_step": status["current_step"],
            "estimated_completion_minutes": status["estimated_completion_minutes"],
            "steps": [
                {"name": "script_analysis", "status": "completed", "duration": "30s"},
                {"name": "visual_generation", "status": "in_progress", "duration": "5-8min"},
                {"name": "voice_synthesis", "status": "pending", "duration": "2-3min"},
                {"name": "video_assembly", "status": "pending", "duration": "3-5min"},
                {"name": "final_processing", "status": "pending", "duration": "1-2min"}
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get video generation status for job {job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get status: {str(e)}"
        )

@router.post("/regenerate-scene/{job_id}")
async def regenerate_video_scene(
    job_id: str,
    request_data: Dict[str, Any],
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Regenerate specific scene in a video
    
    Body should contain:
    {
        "scene_id": "scene_1",
        "modifications": {
            "visual_style": "animated",
            "script_text": "New script for this scene...",
            "visual_description": "New visual description..."
        }
    }
    """
    
    try:
        scene_id = request_data.get("scene_id")
        modifications = request_data.get("modifications", {})
        
        if not scene_id:
            raise HTTPException(
                status_code=400,
                detail="scene_id is required"
            )
        
        orchestrator = create_video_generation_orchestrator()
        result = await orchestrator.regenerate_scene(job_id, scene_id, modifications)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Scene regeneration failed: {result.get('error')}"
            )
        
        return {
            "success": True,
            "message": f"Scene {scene_id} regeneration started",
            "job_id": job_id,
            "scene_id": scene_id,
            "estimated_completion_minutes": result["estimated_completion_minutes"],
            "regenerated_assets": result["regenerated_assets"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scene regeneration failed for job {job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate scene: {str(e)}"
        )

@router.get("/templates")
async def get_video_templates(
    video_type: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get available video templates and presets"""
    
    try:
        templates = {
            "youtube_short": [
                {
                    "template_id": "hook_benefit_cta",
                    "name": "Hook → Benefit → CTA",
                    "description": "Attention-grabbing opener, key benefit, strong call-to-action",
                    "duration": "45-60s",
                    "scenes": 3,
                    "visual_style": "dynamic"
                },
                {
                    "template_id": "problem_solution_proof",
                    "name": "Problem → Solution → Proof",
                    "description": "Identify problem, present solution, show social proof",
                    "duration": "50-60s", 
                    "scenes": 3,
                    "visual_style": "professional"
                }
            ],
            "tiktok": [
                {
                    "template_id": "trending_hook",
                    "name": "Trending Hook Format",
                    "description": "Uses current trending audio/effects with product integration",
                    "duration": "15-30s",
                    "scenes": 2,
                    "visual_style": "energetic"
                },
                {
                    "template_id": "transformation",
                    "name": "Before/After Transformation",
                    "description": "Shows dramatic before/after results",
                    "duration": "30-45s",
                    "scenes": 4,
                    "visual_style": "realistic"
                }
            ],
            "instagram_reel": [
                {
                    "template_id": "lifestyle_showcase",
                    "name": "Lifestyle Integration",
                    "description": "Product seamlessly integrated into lifestyle content",
                    "duration": "60-90s",
                    "scenes": 5,
                    "visual_style": "lifestyle"
                }
            ],
            "facebook_ad": [
                {
                    "template_id": "direct_response",
                    "name": "Direct Response Ad",
                    "description": "Clear value proposition with immediate CTA",
                    "duration": "15-30s",
                    "scenes": 2,
                    "visual_style": "product_focus"
                }
            ]
        }
        
        if video_type:
            return templates.get(video_type, [])
        
        return templates
        
    except Exception as e:
        logger.error(f"Failed to get video templates: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get templates: {str(e)}"
        )

@router.get("/capabilities")
async def get_video_generation_capabilities(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get available video generation capabilities and options"""
    
    return {
        "video_types": [
            {"value": vt.value, "label": vt.value.replace("_", " ").title()}
            for vt in VideoType
        ],
        "visual_styles": [
            {"value": vs.value, "label": vs.value.replace("_", " ").title()}
            for vs in VisualStyle
        ],
        "voice_types": [
            {"value": vt.value, "label": vt.value.replace("_", " ").title()}
            for vt in VoiceType
        ],
        "supported_languages": ["english", "spanish", "french", "german"],
        "max_durations": {
            "youtube_short": 60,
            "tiktok": 60,
            "instagram_reel": 90,
            "youtube_standard": 600,
            "facebook_ad": 30
        },
        "ai_providers": {
            "image_generation": ["dall-e-3", "midjourney", "stable-diffusion"],
            "text_to_speech": ["elevenlabs", "aws-polly", "google-tts"],
            "video_assembly": ["ffmpeg", "after-effects-templates"]
        }
    }

@router.get("/user-limits")
async def get_user_video_limits(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user's video generation limits and usage"""
    
    try:
        # Get actual user limits from database
        user_crud = UserCRUD()
        user = await user_crud.get(db=db, id=user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Determine limits based on user tier/subscription
        # Default limits for basic users
        monthly_limit = 5
        max_duration = 60
        premium_features = False
        max_concurrent = 1
        priority_queue = False

        # Adjust limits based on user type or subscription
        if hasattr(user, 'subscription_tier'):
            if user.subscription_tier == "premium":
                monthly_limit = 20
                max_duration = 300
                premium_features = True
                max_concurrent = 3
                priority_queue = True
            elif user.subscription_tier == "pro":
                monthly_limit = 50
                max_duration = 600
                premium_features = True
                max_concurrent = 5
                priority_queue = True

        # TODO: Count actual videos generated this month from database
        # For now, using placeholder count
        videos_generated = 0  # This should query actual generation count

        return {
            "monthly_video_limit": monthly_limit,
            "videos_generated_this_month": videos_generated,
            "remaining_videos": max(0, monthly_limit - videos_generated),
            "max_video_duration": max_duration,
            "premium_features_enabled": premium_features,
            "supported_formats": ["mp4", "mov", "webm"],
            "max_concurrent_generations": max_concurrent,
            "priority_queue": priority_queue,
            "user_tier": getattr(user, 'subscription_tier', 'basic')
        }
        
    except Exception as e:
        logger.error(f"Failed to get user video limits: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get limits: {str(e)}"
        )