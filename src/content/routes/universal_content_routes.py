# src/content/routes/universal_content_routes.py
"""
Universal Content Generation API Routes
Exposes the Universal Sales Engine for all content types
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from enum import Enum

from src.core.database.session import get_async_db
from src.users.services.auth_service import AuthService
from src.content.services.universal_sales_engine import (
    UniversalSalesEngine,
    ContentRequest,
    ContentFormat,
    SalesPsychologyStage
)

router = APIRouter(prefix="/api/content", tags=["Universal Content Generation"])
security = HTTPBearer()

async def get_current_user_and_company(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
) -> tuple[str, str]:
    """Get current user ID and company ID from token"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return str(user.id), str(user.company_id)

class ContentGenerationRequest(BaseModel):
    """Universal content generation request model"""
    campaign_id: str
    content_format: str  # Will be converted to ContentFormat enum
    psychology_stage: str = "solution_reveal"  # Will be converted to SalesPsychologyStage enum
    preferences: Dict[str, Any] = {}
    specific_requirements: Dict[str, Any] = {}

    @validator('content_format')
    def validate_content_format(cls, v):
        """Validate content format"""
        try:
            return ContentFormat(v.lower())
        except ValueError:
            valid_formats = [f.value for f in ContentFormat]
            raise ValueError(f"Invalid content format. Must be one of: {valid_formats}")

    @validator('psychology_stage')
    def validate_psychology_stage(cls, v):
        """Validate psychology stage"""
        try:
            return SalesPsychologyStage(v.lower())
        except ValueError:
            valid_stages = [s.value for s in SalesPsychologyStage]
            raise ValueError(f"Invalid psychology stage. Must be one of: {valid_stages}")

class ContentFormatsResponse(BaseModel):
    """Response model for available content formats"""
    success: bool
    data: Dict[str, Any]

class PsychologyStagesResponse(BaseModel):
    """Response model for available psychology stages"""
    success: bool
    data: Dict[str, Any]

@router.get("/formats", response_model=ContentFormatsResponse)
async def get_available_content_formats():
    """Get all available content formats and their requirements"""

    formats_info = {}

    for content_format in ContentFormat:
        formats_info[content_format.value] = {
            "name": content_format.value.replace("_", " ").title(),
            "description": _get_format_description(content_format),
            "category": _get_format_category(content_format),
            "typical_use_cases": _get_format_use_cases(content_format),
            "estimated_generation_time": _get_format_generation_time(content_format)
        }

    return {
        "success": True,
        "data": {
            "formats": formats_info,
            "total_formats": len(ContentFormat),
            "categories": {
                "text": ["email", "email_sequence", "blog_article", "ad_copy", "sales_page", "landing_page"],
                "visual": ["image", "infographic"],
                "video": ["video_slideshow", "video_talking_head", "video_animated", "video_kinetic_text"],
                "multimedia": ["video_script", "webinar_script", "podcast_script"],
                "social": ["social_post"],
                "documents": ["case_study", "white_paper", "press_release"]
            }
        }
    }

@router.get("/psychology-stages", response_model=PsychologyStagesResponse)
async def get_psychology_stages():
    """Get all available sales psychology stages"""

    stages_info = {}

    for stage in SalesPsychologyStage:
        stages_info[stage.value] = {
            "name": stage.value.replace("_", " ").title(),
            "description": _get_stage_description(stage),
            "purpose": _get_stage_purpose(stage),
            "typical_content_types": _get_stage_content_types(stage),
            "conversion_intent": _get_stage_conversion_intent(stage)
        }

    return {
        "success": True,
        "data": {
            "stages": stages_info,
            "total_stages": len(SalesPsychologyStage),
            "sequence_flow": [
                "problem_awareness",
                "problem_agitation",
                "solution_reveal",
                "benefit_proof",
                "social_validation",
                "urgency_creation",
                "objection_handling",
                "call_to_action"
            ]
        }
    }

@router.post("/generate")
async def generate_universal_content(
    request: ContentGenerationRequest,
    user_company: tuple[str, str] = Depends(get_current_user_and_company),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Generate content using the Universal Sales Engine

    This single endpoint can generate ANY type of content:
    - Emails, Images, Videos (script + actual video files), Articles, Posts, etc.
    - All driven by the same sales-focused engine
    - Outputs exactly what the user demands

    VIDEO FORMATS NOW INCLUDE ACTUAL VIDEO FILES:
    - video_slideshow: Script + slideshow-style video file
    - video_talking_head: Script + AI avatar video file
    - video_animated: Script + animated video file
    - video_kinetic_text: Script + kinetic typography video file
    """

    user_id, company_id = user_company

    try:
        # Initialize the Universal Sales Engine
        engine = UniversalSalesEngine(db)

        # Create the content request
        content_request = ContentRequest(
            format=request.content_format,
            psychology_stage=request.psychology_stage,
            campaign_id=request.campaign_id,
            user_id=user_id,
            company_id=company_id,
            preferences=request.preferences,
            specific_requirements=request.specific_requirements
        )

        # Generate content using the universal engine
        result = await engine.generate_sales_content(content_request)

        if result.get("success"):
            return {
                "success": True,
                "data": result,
                "message": f"Successfully generated {request.content_format.value} content using Universal Sales Engine"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Content generation failed")
            )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

class VideoGenerationRequest(BaseModel):
    """Specialized video generation request with video-specific options"""
    campaign_id: str
    video_style: str = "slideshow"  # slideshow, talking_head, animated, kinetic_text
    psychology_stage: str = "solution_reveal"
    duration: int = 60  # seconds
    aspect_ratio: str = "16:9"  # 16:9, 9:16, 1:1
    resolution: str = "1080p"   # 1080p, 720p, 4K
    voice_style: str = "professional"  # professional, casual, energetic, warm
    include_captions: bool = True
    include_music: bool = True
    music_style: str = "corporate"  # corporate, energetic, calm, dramatic
    brand_colors: List[str] = []
    logo_url: str = ""

@router.post("/generate/video")
async def generate_video_content(
    request: VideoGenerationRequest,
    user_company: tuple[str, str] = Depends(get_current_user_and_company),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Specialized endpoint for video generation with enhanced options

    Creates both script AND actual video file:
    - Analyzes sales intelligence
    - Generates sales-focused script
    - Converts script to actual video file
    - Returns both script and video URL

    Supported styles:
    - slideshow: Text slides + background images + transitions
    - talking_head: AI avatar speaking the script
    - animated: Animated graphics and characters
    - kinetic_text: Animated typography and text effects
    """

    user_id, company_id = user_company

    try:
        # Map video style to content format
        video_format_map = {
            "slideshow": "video_slideshow",
            "talking_head": "video_talking_head",
            "animated": "video_animated",
            "kinetic_text": "video_kinetic_text"
        }

        content_format = video_format_map.get(request.video_style, "video_slideshow")

        # Create universal content request with video-specific requirements
        content_request = ContentRequest(
            format=ContentFormat(content_format),
            psychology_stage=SalesPsychologyStage(request.psychology_stage),
            campaign_id=request.campaign_id,
            user_id=user_id,
            company_id=company_id,
            preferences={},
            specific_requirements={
                "video_style": request.video_style,
                "duration": request.duration,
                "aspect_ratio": request.aspect_ratio,
                "resolution": request.resolution,
                "voice_style": request.voice_style,
                "include_captions": request.include_captions,
                "include_music": request.include_music,
                "music_style": request.music_style,
                "brand_colors": request.brand_colors,
                "logo_url": request.logo_url,
                "format": "mp4"  # Default video format
            }
        )

        # Generate video using universal engine
        engine = UniversalSalesEngine(db)
        result = await engine.generate_sales_content(content_request)

        if result.get("success"):
            generated_content = result["generated_content"]["content"]

            return {
                "success": True,
                "data": {
                    "content_id": result["content_id"],
                    "script": generated_content.get("script"),
                    "video_url": generated_content.get("video_url"),
                    "video_id": generated_content.get("video_id"),
                    "thumbnail_url": generated_content.get("thumbnail_url"),
                    "duration": generated_content.get("duration"),
                    "scenes_count": generated_content.get("scenes_count"),
                    "video_style": request.video_style,
                    "includes_script_and_video": generated_content.get("includes_script_and_video", True),
                    "generation_metadata": result.get("generation_metadata", {}),
                    "sales_psychology_applied": request.psychology_stage
                },
                "message": f"Successfully generated {request.video_style} video with sales psychology: {request.psychology_stage}"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Video generation failed")
            )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation error: {str(e)}")

@router.post("/generate/batch")
async def generate_batch_content(
    requests: List[ContentGenerationRequest],
    user_company: tuple[str, str] = Depends(get_current_user_and_company),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Generate multiple pieces of content in a single request
    Useful for generating complete campaigns (email sequence + images + videos)
    """

    user_id, company_id = user_company

    if len(requests) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 content pieces per batch request"
        )

    try:
        engine = UniversalSalesEngine(db)
        results = []

        for i, request in enumerate(requests):
            try:
                content_request = ContentRequest(
                    format=request.content_format,
                    psychology_stage=request.psychology_stage,
                    campaign_id=request.campaign_id,
                    user_id=user_id,
                    company_id=company_id,
                    preferences=request.preferences,
                    specific_requirements=request.specific_requirements
                )

                result = await engine.generate_sales_content(content_request)

                results.append({
                    "index": i,
                    "content_format": request.content_format.value,
                    "psychology_stage": request.psychology_stage.value,
                    "result": result
                })

            except Exception as e:
                results.append({
                    "index": i,
                    "content_format": request.content_format.value,
                    "psychology_stage": request.psychology_stage.value,
                    "result": {
                        "success": False,
                        "error": str(e)
                    }
                })

        # Calculate success rate
        successful_results = [r for r in results if r["result"].get("success")]
        success_rate = len(successful_results) / len(results)

        return {
            "success": True,
            "data": {
                "results": results,
                "summary": {
                    "total_requested": len(requests),
                    "successful": len(successful_results),
                    "failed": len(results) - len(successful_results),
                    "success_rate": success_rate
                }
            },
            "message": f"Batch generation completed: {len(successful_results)}/{len(requests)} successful"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")

@router.get("/campaigns/{campaign_id}/generated")
async def get_campaign_generated_content(
    campaign_id: str,
    content_format: Optional[str] = None,
    user_company: tuple[str, str] = Depends(get_current_user_and_company),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all generated content for a campaign, optionally filtered by format"""

    user_id, company_id = user_company

    try:
        engine = UniversalSalesEngine(db)

        # Get generated content from database
        from sqlalchemy import text
        from uuid import UUID

        query = text("""
            SELECT
                id,
                content_type,
                content_title,
                content_body,
                content_metadata,
                generation_method,
                created_at
            FROM generated_content
            WHERE campaign_id = :campaign_id
            AND user_id = :user_id
            AND company_id = :company_id
            AND (:content_format IS NULL OR content_type = :content_format)
            ORDER BY created_at DESC
        """)

        result = await db.execute(query, {
            "campaign_id": UUID(campaign_id),
            "user_id": UUID(user_id),
            "company_id": UUID(company_id),
            "content_format": content_format
        })

        rows = result.fetchall()

        content_items = []
        for row in rows:
            import json

            metadata = json.loads(row.content_metadata) if row.content_metadata else {}

            content_items.append({
                "id": str(row.id),
                "content_type": row.content_type,
                "title": row.content_title,
                "content": json.loads(row.content_body) if row.content_body else {},
                "metadata": metadata,
                "generation_method": row.generation_method,
                "created_at": row.created_at.isoformat(),
                "engine_generated": metadata.get("engine") == "universal_sales_engine",
                "ai_generated": metadata.get("ai_generated", False),
                "sales_optimized": metadata.get("conversion_optimized", False)
            })

        return {
            "success": True,
            "data": {
                "campaign_id": campaign_id,
                "content_items": content_items,
                "total_items": len(content_items),
                "content_types": list(set(item["content_type"] for item in content_items)),
                "ai_generated_count": len([item for item in content_items if item["ai_generated"]]),
                "engine_generated_count": len([item for item in content_items if item["engine_generated"]])
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve content: {str(e)}")

@router.delete("/content/{content_id}")
async def delete_generated_content(
    content_id: str,
    user_company: tuple[str, str] = Depends(get_current_user_and_company),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a specific piece of generated content"""

    user_id, company_id = user_company

    try:
        from sqlalchemy import text
        from uuid import UUID

        # Verify ownership and delete
        query = text("""
            DELETE FROM generated_content
            WHERE id = :content_id
            AND user_id = :user_id
            AND company_id = :company_id
            RETURNING id
        """)

        result = await db.execute(query, {
            "content_id": UUID(content_id),
            "user_id": UUID(user_id),
            "company_id": UUID(company_id)
        })

        deleted_row = result.fetchone()

        if not deleted_row:
            raise HTTPException(
                status_code=404,
                detail="Content not found or access denied"
            )

        await db.commit()

        return {
            "success": True,
            "message": f"Content {content_id} deleted successfully"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete content: {str(e)}")

# Helper functions for format and stage information
def _get_format_description(content_format: ContentFormat) -> str:
    descriptions = {
        ContentFormat.EMAIL: "Single persuasive email for direct communication",
        ContentFormat.EMAIL_SEQUENCE: "Multi-email sales sequence (3-7 emails)",
        ContentFormat.SOCIAL_POST: "Social media post optimized for engagement and conversion",
        ContentFormat.BLOG_ARTICLE: "Long-form article combining SEO and sales",
        ContentFormat.VIDEO_SCRIPT: "Video script for promotional or educational content",
        ContentFormat.VIDEO_SLIDESHOW: "Script + slideshow-style video file with transitions",
        ContentFormat.VIDEO_TALKING_HEAD: "Script + AI avatar video file with speaking presenter",
        ContentFormat.VIDEO_ANIMATED: "Script + animated video file with motion graphics",
        ContentFormat.VIDEO_KINETIC_TEXT: "Script + kinetic typography video file with animated text",
        ContentFormat.AD_COPY: "Advertisement copy for paid campaigns",
        ContentFormat.IMAGE: "Sales-focused promotional image",
        ContentFormat.INFOGRAPHIC: "Data visualization with sales messaging",
        ContentFormat.LANDING_PAGE: "Conversion-optimized landing page",
        ContentFormat.SALES_PAGE: "Long-form sales page for product promotion",
        ContentFormat.WEBINAR_SCRIPT: "Interactive webinar presentation script",
        ContentFormat.PODCAST_SCRIPT: "Podcast episode script with sales integration",
        ContentFormat.PRESS_RELEASE: "News announcement with promotional elements",
        ContentFormat.CASE_STUDY: "Customer success story for social proof",
        ContentFormat.WHITE_PAPER: "Authoritative document establishing expertise"
    }
    return descriptions.get(content_format, "Professional content optimized for sales")

def _get_format_category(content_format: ContentFormat) -> str:
    categories = {
        ContentFormat.EMAIL: "text",
        ContentFormat.EMAIL_SEQUENCE: "text",
        ContentFormat.SOCIAL_POST: "social",
        ContentFormat.BLOG_ARTICLE: "text",
        ContentFormat.VIDEO_SCRIPT: "multimedia",
        ContentFormat.VIDEO_SLIDESHOW: "video",     # New video category
        ContentFormat.VIDEO_TALKING_HEAD: "video",
        ContentFormat.VIDEO_ANIMATED: "video",
        ContentFormat.VIDEO_KINETIC_TEXT: "video",
        ContentFormat.AD_COPY: "text",
        ContentFormat.IMAGE: "visual",
        ContentFormat.INFOGRAPHIC: "visual",
        ContentFormat.LANDING_PAGE: "text",
        ContentFormat.SALES_PAGE: "text",
        ContentFormat.WEBINAR_SCRIPT: "multimedia",
        ContentFormat.PODCAST_SCRIPT: "multimedia",
        ContentFormat.PRESS_RELEASE: "documents",
        ContentFormat.CASE_STUDY: "documents",
        ContentFormat.WHITE_PAPER: "documents"
    }
    return categories.get(content_format, "text")

def _get_format_use_cases(content_format: ContentFormat) -> List[str]:
    use_cases = {
        ContentFormat.EMAIL: ["Direct sales", "Nurture campaigns", "Product launches"],
        ContentFormat.EMAIL_SEQUENCE: ["Lead nurturing", "Product education", "Sales funnel"],
        ContentFormat.SOCIAL_POST: ["Brand awareness", "Engagement", "Traffic driving"],
        ContentFormat.BLOG_ARTICLE: ["SEO content", "Thought leadership", "Product education"],
        ContentFormat.VIDEO_SCRIPT: ["Product demos", "Testimonials", "Educational content"],
        ContentFormat.VIDEO_SLIDESHOW: ["Social media videos", "Product presentations", "Educational content"],
        ContentFormat.VIDEO_TALKING_HEAD: ["Personal branding", "Product testimonials", "Expert presentations"],
        ContentFormat.VIDEO_ANIMATED: ["Explainer videos", "Product demos", "Complex concept visualization"],
        ContentFormat.VIDEO_KINETIC_TEXT: ["Social media ads", "Quote videos", "Text-heavy presentations"],
        ContentFormat.AD_COPY: ["Paid advertising", "PPC campaigns", "Social ads"],
        ContentFormat.IMAGE: ["Social media", "Advertisements", "Website graphics"],
        ContentFormat.INFOGRAPHIC: ["Data presentation", "Educational content", "Social sharing"],
        ContentFormat.LANDING_PAGE: ["Campaign destinations", "Lead capture", "Product promotion"],
        ContentFormat.SALES_PAGE: ["Product sales", "Course promotion", "High-ticket offers"],
        ContentFormat.WEBINAR_SCRIPT: ["Live presentations", "Product demos", "Educational seminars"],
        ContentFormat.PODCAST_SCRIPT: ["Thought leadership", "Interview preparation", "Educational content"],
        ContentFormat.PRESS_RELEASE: ["Product launches", "Company news", "Media outreach"],
        ContentFormat.CASE_STUDY: ["Social proof", "Success stories", "B2B sales materials"],
        ContentFormat.WHITE_PAPER: ["Lead magnets", "Authority building", "B2B marketing"]
    }
    return use_cases.get(content_format, ["General marketing", "Brand promotion"])

def _get_format_generation_time(content_format: ContentFormat) -> str:
    times = {
        ContentFormat.EMAIL: "30-60 seconds",
        ContentFormat.EMAIL_SEQUENCE: "2-5 minutes",
        ContentFormat.SOCIAL_POST: "15-30 seconds",
        ContentFormat.BLOG_ARTICLE: "3-8 minutes",
        ContentFormat.VIDEO_SCRIPT: "2-4 minutes",
        ContentFormat.VIDEO_SLIDESHOW: "3-8 minutes",      # Script + video generation
        ContentFormat.VIDEO_TALKING_HEAD: "5-15 minutes",  # Script + AI avatar processing
        ContentFormat.VIDEO_ANIMATED: "8-20 minutes",      # Script + animation rendering
        ContentFormat.VIDEO_KINETIC_TEXT: "2-6 minutes",   # Script + text animation
        ContentFormat.AD_COPY: "30-90 seconds",
        ContentFormat.IMAGE: "1-3 minutes",
        ContentFormat.INFOGRAPHIC: "3-6 minutes",
        ContentFormat.LANDING_PAGE: "5-10 minutes",
        ContentFormat.SALES_PAGE: "8-15 minutes",
        ContentFormat.WEBINAR_SCRIPT: "10-20 minutes",
        ContentFormat.PODCAST_SCRIPT: "5-10 minutes",
        ContentFormat.PRESS_RELEASE: "2-4 minutes",
        ContentFormat.CASE_STUDY: "4-8 minutes",
        ContentFormat.WHITE_PAPER: "15-30 minutes"
    }
    return times.get(content_format, "1-5 minutes")

def _get_stage_description(stage: SalesPsychologyStage) -> str:
    descriptions = {
        SalesPsychologyStage.PROBLEM_AWARENESS: "Make prospects aware of their problem",
        SalesPsychologyStage.PROBLEM_AGITATION: "Intensify the pain and urgency of the problem",
        SalesPsychologyStage.SOLUTION_REVEAL: "Introduce your solution as the answer",
        SalesPsychologyStage.BENEFIT_PROOF: "Prove the solution works with evidence",
        SalesPsychologyStage.SOCIAL_VALIDATION: "Show others succeeding with the solution",
        SalesPsychologyStage.URGENCY_CREATION: "Create time pressure to act now",
        SalesPsychologyStage.OBJECTION_HANDLING: "Address concerns and remove barriers",
        SalesPsychologyStage.CALL_TO_ACTION: "Direct prospects to take immediate action"
    }
    return descriptions.get(stage, "Drive prospects toward conversion")

def _get_stage_purpose(stage: SalesPsychologyStage) -> str:
    purposes = {
        SalesPsychologyStage.PROBLEM_AWARENESS: "Education and problem identification",
        SalesPsychologyStage.PROBLEM_AGITATION: "Emotional engagement and urgency creation",
        SalesPsychologyStage.SOLUTION_REVEAL: "Hope and possibility introduction",
        SalesPsychologyStage.BENEFIT_PROOF: "Trust building through evidence",
        SalesPsychologyStage.SOCIAL_VALIDATION: "Risk reduction through social proof",
        SalesPsychologyStage.URGENCY_CREATION: "Action motivation through scarcity",
        SalesPsychologyStage.OBJECTION_HANDLING: "Barrier removal and reassurance",
        SalesPsychologyStage.CALL_TO_ACTION: "Conversion and immediate action"
    }
    return purposes.get(stage, "Conversion optimization")

def _get_stage_content_types(stage: SalesPsychologyStage) -> List[str]:
    content_types = {
        SalesPsychologyStage.PROBLEM_AWARENESS: ["blog_article", "social_post", "video_script"],
        SalesPsychologyStage.PROBLEM_AGITATION: ["email", "ad_copy", "video_script"],
        SalesPsychologyStage.SOLUTION_REVEAL: ["email", "landing_page", "video_script"],
        SalesPsychologyStage.BENEFIT_PROOF: ["case_study", "white_paper", "video_script"],
        SalesPsychologyStage.SOCIAL_VALIDATION: ["case_study", "social_post", "testimonial_video"],
        SalesPsychologyStage.URGENCY_CREATION: ["email", "ad_copy", "social_post"],
        SalesPsychologyStage.OBJECTION_HANDLING: ["email", "landing_page", "sales_page"],
        SalesPsychologyStage.CALL_TO_ACTION: ["sales_page", "email", "ad_copy"]
    }
    return content_types.get(stage, ["email", "social_post"])

def _get_stage_conversion_intent(stage: SalesPsychologyStage) -> str:
    intents = {
        SalesPsychologyStage.PROBLEM_AWARENESS: "awareness",
        SalesPsychologyStage.PROBLEM_AGITATION: "interest",
        SalesPsychologyStage.SOLUTION_REVEAL: "consideration",
        SalesPsychologyStage.BENEFIT_PROOF: "evaluation",
        SalesPsychologyStage.SOCIAL_VALIDATION: "evaluation",
        SalesPsychologyStage.URGENCY_CREATION: "conversion",
        SalesPsychologyStage.OBJECTION_HANDLING: "conversion",
        SalesPsychologyStage.CALL_TO_ACTION: "conversion"
    }
    return intents.get(stage, "engagement")