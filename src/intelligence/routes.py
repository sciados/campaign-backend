"""
Intelligence analysis routes - Enhanced with Intelligence Amplifier and Fixed Content Type Routing
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy import update
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl
from datetime import datetime
import traceback
import logging
import json

# ✅ ENHANCED: Import and setup logger
logger = logging.getLogger(__name__)

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.campaign import Campaign
from src.models.intelligence import (
    CampaignIntelligence,
    GeneratedContent,
    SmartURL,
    IntelligenceSourceType,
    AnalysisStatus
)

# ✅ FIXED: Import analyzers using proper package structure
try:
    from src.intelligence import SalesPageAnalyzer, DocumentAnalyzer, WebAnalyzer, EnhancedSalesPageAnalyzer, VSLAnalyzer, INTELLIGENCE_AVAILABLE
    ANALYZERS_AVAILABLE = INTELLIGENCE_AVAILABLE
    logger.info("✅ SUCCESS: All intelligence analyzers imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ IMPORT WARNING: Analyzers not available: {str(e)}")
    ANALYZERS_AVAILABLE = False

# ✅ FIXED: Import generators with proper routing capability
try:
    from src.intelligence.generators import (
        EmailSequenceGenerator,
        CampaignAngleGenerator,
        SocialMediaGenerator,
        AdCopyGenerator,
        BlogPostGenerator,
        LandingPageGenerator,
        VideoScriptGenerator
    )
    GENERATORS_AVAILABLE = True
    logger.info("✅ All generators imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ IMPORT WARNING: Some generators not available: {str(e)}")
    GENERATORS_AVAILABLE = False

    # Create fallback classes
    class EmailSequenceGenerator:
        async def generate_email_sequence(self, *args, **kwargs):
            return {"error": "Email generator not available", "fallback": True}

    class SocialMediaGenerator:
        async def generate_social_posts(self, *args, **kwargs):
            return {"error": "Social media generator not available", "fallback": True}

    class AdCopyGenerator:
        async def generate_ad_copy(self, *args, **kwargs):
            return {"error": "Ad copy generator not available", "fallback": True}

    class BlogPostGenerator:
        async def generate_blog_post(self, *args, **kwargs):
            return {"error": "Blog post generator not available", "fallback": True}

    class LandingPageGenerator:
        async def generate_landing_page(self, *args, **kwargs):
            return {"error": "Landing page generator not available", "fallback": True}

    class VideoScriptGenerator:
        async def generate_video_script(self, *args, **kwargs):
            return {"error": "Video script generator not available", "fallback": True}

    class CampaignAngleGenerator:
        async def generate_angles(self, *args, **kwargs):
            return {"error": "Campaign angle generator not available", "fallback": True}

# ✅ CLEAN: Import Intelligence Amplifier from package
try:
    from src.intelligence.amplifier import IntelligenceAmplificationService, is_amplifier_available, get_amplifier_status
    AMPLIFIER_AVAILABLE = is_amplifier_available()
    amplifier_status = get_amplifier_status()
    logger.info(f"✅ SUCCESS: Intelligence Amplifier imported - Status: {amplifier_status['status']}")
except ImportError as e:
    logger.warning(f"⚠️ AMPLIFIER WARNING: Intelligence Amplifier package not available: {str(e)}")
    logger.warning("⚠️ Check amplifier folder structure and dependencies")
    AMPLIFIER_AVAILABLE = False

    # Fallback class if package import fails completely
    class IntelligenceAmplificationService:
        async def process_sources(self, sources, preferences=None):
            return {
                "intelligence_data": sources[0] if sources else {},
                "summary": {
                    "total": len(sources) if sources else 0,
                    "successful": 0,
                    "note": "Amplifier package not available"
                }
            }

try:
    from src.core.credits import check_and_consume_credits
    CREDITS_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ WARNING: Credits system not available")
    CREDITS_AVAILABLE = False
    async def check_and_consume_credits(*args, **kwargs):
        pass

router = APIRouter(tags=["intelligence"])

# ============================================================================
# CONTENT MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/{campaign_id}/content")
async def get_campaign_content_list(
    campaign_id: str,
    include_body: bool = False,
    content_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """✅ NEW: Get list of generated content for a campaign"""
    try:
        logger.info(f"Getting content list for campaign {campaign_id}")

        # Verify campaign ownership
        campaign_result = await db.execute(
            select(Campaign).where(
                and_(
                    Campaign.id == campaign_id,
                    Campaign.company_id == current_user.company_id
                )
            )
        )
        campaign = campaign_result.scalar_one_or_none()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Build query for generated content
        query = select(GeneratedContent).where(
            GeneratedContent.campaign_id == campaign_id
        ).order_by(GeneratedContent.created_at.desc())

        # Add content type filter if specified
        if content_type:
            query = query.where(GeneratedContent.content_type == content_type)

        result = await db.execute(query)
        content_items = result.scalars().all()

        # Format response
        content_list = []
        for item in content_items:
            content_data = {
                "id": str(item.id),
                "content_type": item.content_type,
                "content_title": item.content_title,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                "user_rating": item.user_rating,
                "is_published": item.is_published,
                "published_at": item.published_at,
                "performance_data": item.performance_data or {},
                "content_metadata": item.content_metadata or {},
                "generation_settings": item.generation_settings or {},
                "intelligence_used": item.intelligence_used or {}
            }

            # Include full content body if requested
            if include_body:
                content_data["content_body"] = item.content_body
            else:
                # Just include a preview
                try:
                    parsed_body = json.loads(item.content_body) if item.content_body else {}
                    if isinstance(parsed_body, dict):
                        # Extract preview from different content types
                        preview = ""
                        if "emails" in parsed_body and parsed_body["emails"]:
                            preview = f"{len(parsed_body['emails'])} emails"
                        elif "posts" in parsed_body and parsed_body["posts"]:
                            preview = f"{len(parsed_body['posts'])} posts"
                        elif "ads" in parsed_body and parsed_body["ads"]:
                            preview = f"{len(parsed_body['ads'])} ads"
                        elif "title" in parsed_body:
                            preview = parsed_body["title"][:100] + "..."
                        else:
                            preview = "Generated content"
                        content_data["content_preview"] = preview
                    else:
                        content_data["content_preview"] = str(parsed_body)[:100] + "..."
                except:
                    content_data["content_preview"] = "Content available"

            content_list.append(content_data)

        return {
            "campaign_id": campaign_id,
            "total_content": len(content_list),
            "content_items": content_list
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign content: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign content: {str(e)}"
        )

@router.get("/{campaign_id}/content/{content_id}")
async def get_content_detail(
    campaign_id: str,
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """✅ NEW: Get detailed content including full body"""
    try:
        logger.info(f"Getting content detail for {content_id} in campaign {campaign_id}")

        # Get the content item with campaign verification
        content_result = await db.execute(
            select(GeneratedContent).where(
                and_(
                    GeneratedContent.id == content_id,
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == current_user.company_id
                )
            )
        )
        content_item = content_result.scalar_one_or_none()

        if not content_item:
            raise HTTPException(status_code=404, detail="Content not found")

        # Parse content body
        parsed_content = {}
        try:
            if content_item.content_body:
                parsed_content = json.loads(content_item.content_body)
        except json.JSONDecodeError:
            parsed_content = {"raw_content": content_item.content_body}

        # Get intelligence source info if available
        intelligence_info = None
        if content_item.intelligence_source_id:
            intel_result = await db.execute(
                select(CampaignIntelligence).where(
                    CampaignIntelligence.id == content_item.intelligence_source_id
                )
            )
            intelligence_source = intel_result.scalar_one_or_none()
            if intelligence_source:
                intelligence_info = {
                    "id": str(intelligence_source.id),
                    "source_title": intelligence_source.source_title,
                    "source_url": intelligence_source.source_url,
                    "confidence_score": intelligence_source.confidence_score,
                    "source_type": intelligence_source.source_type.value if intelligence_source.source_type else None
                }

        return {
            "id": str(content_item.id),
            "campaign_id": campaign_id,
            "content_type": content_item.content_type,
            "content_title": content_item.content_title,
            "content_body": content_item.content_body,
            "parsed_content": parsed_content,
            "content_metadata": content_item.content_metadata or {},
            "generation_settings": content_item.generation_settings or {},
            "intelligence_used": content_item.intelligence_used or {},
            "performance_data": content_item.performance_data or {},
            "user_rating": content_item.user_rating,
            "is_published": content_item.is_published,
            "published_at": content_item.published_at,
            "created_at": content_item.created_at.isoformat() if content_item.created_at else None,
            "updated_at": content_item.updated_at.isoformat() if content_item.updated_at else None,
            "intelligence_source": intelligence_info
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content detail: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content detail: {str(e)}"
        )

@router.put("/{campaign_id}/content/{content_id}")
async def update_content(
    campaign_id: str,
    content_id: str,
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """✅ NEW: Update generated content"""
    try:
        logger.info(f"Updating content {content_id} in campaign {campaign_id}")

        # Get the content item with verification
        content_result = await db.execute(
            select(GeneratedContent).where(
                and_(
                    GeneratedContent.id == content_id,
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == current_user.company_id
                )
            )
        )
        content_item = content_result.scalar_one_or_none()

        if not content_item:
            raise HTTPException(status_code=404, detail="Content not found")

        # Update allowed fields
        allowed_fields = [
            'content_title', 'content_body', 'content_metadata',
            'user_rating', 'is_published', 'published_at', 'performance_data'
        ]

        for field, value in update_data.items():
            if field in allowed_fields and hasattr(content_item, field):
                setattr(content_item, field, value)

        # Update timestamp
        content_item.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(content_item)

        logger.info(f"Content {content_id} updated successfully")

        return {
            "id": str(content_item.id),
            "message": "Content updated successfully",
            "updated_at": content_item.updated_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating content: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update content: {str(e)}"
        )

@router.delete("/{campaign_id}/content/{content_id}")
async def delete_content(
    campaign_id: str,
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """✅ NEW: Delete generated content"""
    try:
        logger.info(f"Deleting content {content_id} from campaign {campaign_id}")

        # Get the content item with verification
        content_result = await db.execute(
            select(GeneratedContent).where(
                and_(
                    GeneratedContent.id == content_id,
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == current_user.company_id
                )
            )
        )
        content_item = content_result.scalar_one_or_none()

        if not content_item:
            raise HTTPException(status_code=404, detail="Content not found")

        # Delete the content
        await db.delete(content_item)
        await db.commit()

        # Update campaign counters
        try:
            await update_campaign_counters(campaign_id, db)
            await db.commit()
        except Exception as counter_error:
            logger.warning(f"Failed to update campaign counters: {str(counter_error)}")

        logger.info(f"Content {content_id} deleted successfully")

        return {"message": "Content deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting content: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete content: {str(e)}"
        )

# ============================================================================
# ✅ FIXED: CONTENT GENERATION ENDPOINT (SINGLE VERSION)
# ============================================================================

@router.post("/generate-content")
async def generate_content_endpoint(
    request_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """✅ FIXED: Generate content using intelligence data"""

    logger.info(f"🎯 Content generation request received")
    logger.info(f"📝 Request data: {request_data}")

    try:
        content_type = request_data.get("content_type", "email_sequence")
        campaign_id = request_data.get("campaign_id")
        preferences = request_data.get("preferences", {})
        intelligence_id = request_data.get("intelligence_id")

        logger.info(f"🎯 Generating {content_type} for campaign {campaign_id}")

        if not campaign_id:
            raise HTTPException(status_code=400, detail="campaign_id is required")

        # Get campaign and verify ownership
        campaign_result = await db.execute(
            select(Campaign).where(
                and_(
                    Campaign.id == campaign_id,
                    Campaign.company_id == current_user.company_id
                )
            )
        )
        campaign = campaign_result.scalar_one_or_none()

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        logger.info(f"✅ Campaign verified: {campaign.title}")

        # Get intelligence data for the campaign
        intelligence_result = await db.execute(
            select(CampaignIntelligence).where(
                CampaignIntelligence.campaign_id == campaign_id
            )
        )
        intelligence_sources = intelligence_result.scalars().all()

        logger.info(f"📊 Found {len(intelligence_sources)} intelligence sources")

        # Prepare intelligence data for generator
        intelligence_data = {
            "campaign_id": campaign_id,
            "campaign_name": campaign.title,
            "target_audience": campaign.target_audience or "health-conscious adults",
            "offer_intelligence": {},
            "psychology_intelligence": {},
            "content_intelligence": {},
            "competitive_intelligence": {},
            "brand_intelligence": {},
            "intelligence_sources": []
        }

        # Aggregate intelligence data from all sources
        for source in intelligence_sources:
            try:
                source_data = {
                    "id": str(source.id),
                    "source_type": source.source_type.value if source.source_type else "unknown",
                    "source_url": source.source_url,
                    "confidence_score": source.confidence_score or 0.0,
                    "offer_intelligence": source.offer_intelligence or {},
                    "psychology_intelligence": source.psychology_intelligence or {},
                    "content_intelligence": source.content_intelligence or {},
                    "competitive_intelligence": source.competitive_intelligence or {},
                    "brand_intelligence": source.brand_intelligence or {}
                }
                intelligence_data["intelligence_sources"].append(source_data)

                # Merge into aggregate intelligence
                for intel_type in ["offer_intelligence", "psychology_intelligence", "content_intelligence", "competitive_intelligence", "brand_intelligence"]:
                    source_intel = source_data.get(intel_type, {})
                    if source_intel:
                        current_intel = intelligence_data.get(intel_type, {})

                        # Merge lists and strings intelligently
                        for key, value in source_intel.items():
                            if key in current_intel:
                                if isinstance(value, list) and isinstance(current_intel[key], list):
                                    current_intel[key].extend(value)
                                elif isinstance(value, str) and isinstance(current_intel[key], str):
                                    if value not in current_intel[key]:
                                        current_intel[key] += f" {value}"
                            else:
                                current_intel[key] = value

                        intelligence_data[intel_type] = current_intel

            except Exception as source_error:
                logger.warning(f"⚠️ Error processing source {source.id}: {str(source_error)}")
                continue

        logger.info(f"🧠 Intelligence data prepared for {content_type} generation")

        # Generate content using the appropriate generator
        if content_type == "email_sequence":
            try:
                from src.intelligence.generators.email_generator import EmailSequenceGenerator
                generator = EmailSequenceGenerator()
                result = await generator.generate_email_sequence(intelligence_data, preferences)
                logger.info(f"✅ Email sequence generated successfully")
            except ImportError as e:
                logger.error(f"❌ Email generator import failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Email generator not available")

        elif content_type == "SOCIAL_POSTS":
            try:
                from src.intelligence.generators.social_media_generator import SocialMediaGenerator
                generator = SocialMediaGenerator()
                result = await generator.generate_social_posts(intelligence_data, preferences)
                logger.info(f"✅ Social media posts generated successfully")
            except ImportError as e:
                logger.error(f"❌ Social media generator import failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Social media generator not available")

        elif content_type == "ad_copy":
            try:
                from src.intelligence.generators.ad_copy_generator import AdCopyGenerator
                generator = AdCopyGenerator()
                result = await generator.generate_ad_copy(intelligence_data, preferences)
                logger.info(f"✅ Ad copy generated successfully")
            except ImportError as e:
                logger.error(f"❌ Ad copy generator import failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Ad copy generator not available")

        elif content_type == "blog_post":
            try:
                from src.intelligence.generators.blog_post_generator import BlogPostGenerator
                generator = BlogPostGenerator()
                result = await generator.generate_blog_post(intelligence_data, preferences)
                logger.info(f"✅ Blog post generated successfully")
            except ImportError as e:
                logger.error(f"❌ Blog post generator import failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Blog post generator not available")

        elif content_type == "LANDING_PAGE":
            try:
                from src.intelligence.generators.landing_page.core.generator import EnhancedLandingPageGenerator
                generator = EnhancedLandingPageGenerator()
                result = await generator.generate_landing_page(intelligence_data, preferences)
                logger.info(f"✅ Landing page generated successfully")
            except ImportError as e:
                logger.error(f"❌ Landing page generator import failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Landing page generator not available")

        elif content_type == "video_script":
            try:
                from src.intelligence.generators.video_script_generator import VideoScriptGenerator
                generator = VideoScriptGenerator()
                result = await generator.generate_video_script(intelligence_data, preferences)
                logger.info(f"✅ Video script generated successfully")
            except ImportError as e:
                logger.error(f"❌ Video script generator import failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Video script generator not available")

        else:
            logger.error(f"❌ Unknown content type: {content_type}")
            raise HTTPException(status_code=400, detail=f"Unknown content type: {content_type}")

        # Check if generation was successful
        if not result or result.get("error") or result.get("fallback"):
            logger.error(f"❌ Generation failed or returned fallback: {result}")
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Content generation failed")
            )

        # Save generated content to database - FIXED VERSION
        generated_content = GeneratedContent(
            campaign_id=campaign_id,
            company_id=current_user.company_id,
            user_id=current_user.id,
            content_type=content_type,
            content_title=result.get("title", f"Generated {content_type.title()}"),
            content_body=json.dumps(result.get("content", {})),
            content_metadata=result.get("metadata", {}),
            generation_settings=preferences,
            intelligence_used={
                "sources_count": len(intelligence_sources),
                "primary_source_id": str(intelligence_sources[0].id) if intelligence_sources else None,
                "generation_timestamp": datetime.utcnow().isoformat(),
                "amplified": any(
                    source.processing_metadata and source.processing_metadata.get("amplification_applied", False)
                    for source in intelligence_sources
                )
            },
            intelligence_source_id=intelligence_sources[0].id if intelligence_sources else None,
            # ✅ PROPER: Don't set timestamp fields, let them default to NULL
            is_published=False  # Only set the boolean, not the timestamp
        )

        db.add(generated_content)
        await db.commit()
        await db.refresh(generated_content)

        # Update campaign counters
        try:
            await update_campaign_counters(campaign_id, db)
            await db.commit()
            logger.info(f"📊 Campaign counters updated")
        except Exception as counter_error:
            logger.warning(f"⚠️ Campaign counter update failed (non-critical): {str(counter_error)}")

        logger.info(f"✅ Content generation completed successfully - ID: {generated_content.id}")

        return {
            "content_id": str(generated_content.id),
            "content_type": content_type,
            "generated_content": result,
            "smart_url": None,  # Can be implemented later
            "performance_predictions": {},  # Can be implemented later
            "intelligence_sources_used": len(intelligence_sources),
            "generation_metadata": {
                "generated_at": generated_content.created_at.isoformat(),
                "generator_used": f"{content_type}_generator",
                "fallback_used": False,
                "success": True
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Content generation failed: {str(e)}")
        logger.error(f"📍 Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Content generation failed: {str(e)}"
        )

# ============================================================================
# CONTENT TYPE DISCOVERY ENDPOINT
# ============================================================================

@router.get("/content-types")
async def get_available_content_types(
    current_user: User = Depends(get_current_user)
):
    """Get list of available content types and their capabilities"""

    try:
        # Try to use the factory if available
        try:
            from src.intelligence.generators.factory import ContentGeneratorFactory
            factory = ContentGeneratorFactory()
            capabilities = factory.get_generator_capabilities()
            available_types = factory.get_available_generators()
            factory_available = True
        except ImportError:
            factory_available = False
            capabilities = {}
            available_types = []

        # Fallback to manual detection
        if not factory_available:
            available_types = []
            capabilities = {}

            # Check each generator individually
            generators_to_check = [
                ("email_sequence", "EmailSequenceGenerator", "src.intelligence.generators.email_generator"),
                ("SOCIAL_POSTS", "SocialMediaGenerator", "src.intelligence.generators.social_media_generator"),
                ("ad_copy", "AdCopyGenerator", "src.intelligence.generators.ad_copy_generator"),
                ("blog_post", "BlogPostGenerator", "src.intelligence.generators.blog_post_generator"),
                ("landing_page", "EnhancedLandingPageGenerator", "src.intelligence.generators.landing_page.core.generator"),
                ("video_script", "VideoScriptGenerator", "src.intelligence.generators.video_script_generator"),
            ]

            for content_type, class_name, module_path in generators_to_check:
                try:
                    module = __import__(module_path, fromlist=[class_name])
                    getattr(module, class_name)
                    available_types.append(content_type)
                    capabilities[content_type] = {
                        "description": f"Generate {content_type.replace('_', ' ')}",
                        "status": "available"
                    }
                except (ImportError, AttributeError):
                    capabilities[content_type] = {
                        "description": f"Generate {content_type.replace('_', ' ')}",
                        "status": "unavailable"
                    }

        return {
            "available_content_types": available_types,
            "total_available": len(available_types),
            "capabilities": capabilities,
            "factory_available": factory_available,
            "status": "operational" if available_types else "limited"
        }

    except Exception as e:
        logger.error(f"❌ Error getting content types: {str(e)}")
        return {
            "available_content_types": ["email_sequence"],  # Fallback
            "total_available": 1,
            "capabilities": {
                "email_sequence": {
                    "description": "Generate email sequences",
                    "status": "fallback"
                }
            },
            "factory_available": False,
            "status": "fallback",
            "error": str(e)
        }
# FALLBACK CLASSES FOR MISSING DEPENDENCIES
# ============================================================================

class FallbackAnalyzer:
    async def analyze(self, url: str) -> Dict[str, Any]:
        return {
            "offer_intelligence": {
                "products": ["Analysis requires missing dependencies"],
                "pricing": [],
                "bonuses": [],
                "guarantees": [],
                "value_propositions": ["Install aiohttp, beautifulsoup4, lxml to enable analysis"]
            },
            "psychology_intelligence": {
                "emotional_triggers": [],
                "pain_points": ["Dependency error - cannot analyze"],
                "target_audience": "Unknown",
                "persuasion_techniques": []
            },
            "competitive_intelligence": {
                "opportunities": ["Fix import dependencies to enable analysis"],
                "gaps": [],
                "positioning": "Analysis disabled",
                "advantages": [],
                "weaknesses": []
            },
            "content_intelligence": {
                "key_messages": [f"URL: {url}"],
                "success_stories": [],
                "social_proof": [],
                "content_structure": "Cannot analyze without dependencies"
            },
            "brand_intelligence": {
                "tone_voice": "Unknown",
                "messaging_style": "Unknown",
                "brand_positioning": "Unknown"
            },
            "campaign_suggestions": [
                "Install missing dependencies: pip install aiohttp beautifulsoup4 lxml",
                "Check Railway deployment logs for import errors",
                "Verify requirements.txt contains all dependencies"
            ],
            "source_url": url,
            "page_title": "Analysis Failed - Missing Dependencies",
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "confidence_score": 0.0,
            "raw_content": "",
            "error_message": "Missing dependencies: aiohttp, beautifulsoup4, lxml",
            "analysis_note": "Install required dependencies to enable URL analysis"
        }

# Use fallback if imports failed
if not ANALYZERS_AVAILABLE:
    SalesPageAnalyzer = FallbackAnalyzer
    DocumentAnalyzer = FallbackAnalyzer
    WebAnalyzer = FallbackAnalyzer
    EnhancedSalesPageAnalyzer = FallbackAnalyzer
    VSLAnalyzer = FallbackAnalyzer

if not AMPLIFIER_AVAILABLE:
    IntelligenceAmplificationService = IntelligenceAmplificationService

# ============================================================================
# HELPER FUNCTIONS - CAMPAIGN COUNTER UPDATES
# ============================================================================

async def update_campaign_counters(campaign_id: str, db: AsyncSession):
    """Update campaign counter fields based on actual data"""
    try:
        # Count intelligence sources
        intelligence_count = await db.execute(
            select(func.count(CampaignIntelligence.id)).where(
                CampaignIntelligence.campaign_id == campaign_id
            )
        )
        sources_count = intelligence_count.scalar() or 0

        # Count generated content
        content_count = await db.execute(
            select(func.count(GeneratedContent.id)).where(
                GeneratedContent.campaign_id == campaign_id
            )
        )
        generated_content_count = content_count.scalar() or 0

        # Update campaign record
        from sqlalchemy import update
        await db.execute(
            update(Campaign).where(Campaign.id == campaign_id).values(
                sources_count=sources_count,
                intelligence_extracted=sources_count,
                intelligence_count=sources_count,
                content_generated=generated_content_count,
                generated_content_count=generated_content_count,
                updated_at=datetime.utcnow()
            )
        )

        logger.info(f"📊 Updated campaign counters: {sources_count} sources, {generated_content_count} content")
        return True

    except Exception as e:
        logger.error(f"❌ Error updating campaign counters: {str(e)}")
        return False

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AnalyzeURLRequest(BaseModel):
    url: HttpUrl
    campaign_id: str
    analysis_type: str = "sales_page"

class AnalysisResponse(BaseModel):
    intelligence_id: str
    analysis_status: str
    confidence_score: float
    offer_intelligence: Dict[str, Any]
    psychology_intelligence: Dict[str, Any]
    competitive_opportunities: List[Dict[str, Any]]
    campaign_suggestions: List[str]

class GenerateContentRequest(BaseModel):
    intelligence_id: str
    content_type: str
    preferences: Dict[str, Any] = {}
    campaign_id: str

class ContentGenerationResponse(BaseModel):
    content_id: str
    content_type: str
    generated_content: Dict[str, Any]
    smart_url: Optional[str] = None
    performance_predictions: Dict[str, Any]

# ============================================================================
# ✅ FIXED: MAIN INTELLIGENCE ENDPOINT WITH PROPER ERROR HANDLING
# ============================================================================

@router.get("/campaign/{campaign_id}/intelligence")
async def get_campaign_intelligence(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """✅ FIXED: Get all intelligence sources for a campaign with proper error handling"""

    logger.info(f"🔍 Getting ENHANCED intelligence for campaign: {campaign_id}")

    try:
        # ✅ STEP 1: Verify campaign access (simple query, no joins)
        campaign_result = await db.execute(
            select(Campaign).where(
                and_(
                    Campaign.id == campaign_id,
                    Campaign.company_id == current_user.company_id
                )
            )
        )
        campaign = campaign_result.scalar_one_or_none()

        if not campaign:
            logger.error(f"❌ Campaign {campaign_id} not found for user {current_user.id}")
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )

        logger.info(f"✅ Campaign access verified: {campaign.title}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error verifying campaign access: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify campaign access"
        )

    try:
        # ✅ STEP 2: Get intelligence sources (FIXED QUERY)
        intelligence_query = select(CampaignIntelligence).where(
            CampaignIntelligence.campaign_id == campaign_id
        ).order_by(CampaignIntelligence.created_at.desc())

        intelligence_result = await db.execute(intelligence_query)
        intelligence_sources = intelligence_result.scalars().all()

        logger.info(f"✅ Found {len(intelligence_sources)} intelligence sources")

    except Exception as e:
        logger.error(f"❌ Error getting intelligence sources: {str(e)}")
        # Return empty instead of failing
        intelligence_sources = []

    try:
        # ✅ STEP 3: Get generated content (FIXED QUERY)
        content_query = select(GeneratedContent).where(
            GeneratedContent.campaign_id == campaign_id
        ).order_by(GeneratedContent.created_at.desc())

        content_result = await db.execute(content_query)
        generated_content = content_result.scalars().all()

        logger.info(f"✅ Found {len(generated_content)} generated content items")

    except Exception as e:
        logger.error(f"❌ Error getting generated content: {str(e)}")
        # Return empty instead of failing
        generated_content = []

    # ✅ STEP 4: Build response safely (no database operations)
    try:
        # Calculate summary statistics
        total_intelligence = len(intelligence_sources)
        total_content = len(generated_content)
        avg_confidence = 0.0
        amplified_sources = 0
        total_scientific_enhancements = 0

        if intelligence_sources:
            confidence_scores = []
            for source in intelligence_sources:
                if source.confidence_score is not None:
                    confidence_scores.append(source.confidence_score)

                # Check amplification status
                amplification_metadata = source.processing_metadata or {}
                if amplification_metadata.get("amplification_applied", False):
                    amplified_sources += 1
                    total_scientific_enhancements += amplification_metadata.get("scientific_enhancements", 0)

            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        # Convert to response format safely
        intelligence_data = []
        for source in intelligence_sources:
            try:
                amplification_metadata = source.processing_metadata or {}

                intelligence_data.append({
                    "id": str(source.id),
                    "source_title": source.source_title or "Untitled Source",
                    "source_url": source.source_url or "",
                    "source_type": source.source_type.value if source.source_type else "unknown",
                    "confidence_score": source.confidence_score or 0.0,
                    "usage_count": source.usage_count or 0,
                    "analysis_status": source.analysis_status.value if source.analysis_status else "unknown",
                    "created_at": source.created_at.isoformat() if source.created_at else None,
                    "updated_at": source.updated_at.isoformat() if source.updated_at else None,
                    # Include intelligence data for frontend use
                    "offer_intelligence": source.offer_intelligence or {},
                    "psychology_intelligence": source.psychology_intelligence or {},
                    "content_intelligence": source.content_intelligence or {},
                    "competitive_intelligence": source.competitive_intelligence or {},
                    "brand_intelligence": source.brand_intelligence or {},
                    # ✅ Amplification status
                    "amplification_status": {
                        "is_amplified": amplification_metadata.get("amplification_applied", False),
                        "confidence_boost": amplification_metadata.get("confidence_boost", 0.0),
                        "scientific_enhancements": amplification_metadata.get("scientific_enhancements", 0),
                        "credibility_score": amplification_metadata.get("credibility_score", 0.0),
                        "total_enhancements": amplification_metadata.get("total_enhancements", 0),
                        "amplified_at": amplification_metadata.get("amplified_at"),
                        "amplification_available": AMPLIFIER_AVAILABLE
                    }
                })
            except Exception as source_error:
                logger.warning(f"⚠️ Error processing intelligence source {source.id}: {str(source_error)}")
                # Skip problematic sources instead of failing
                continue

        content_data = []
        for content in generated_content:
            try:
                # Check if content was generated from amplified intelligence
                intelligence_used = content.intelligence_used or {}
                is_amplified_content = intelligence_used.get("amplified", False)

                content_data.append({
                    "id": str(content.id),
                    "content_type": content.content_type or "unknown",
                    "content_title": content.content_title or "Untitled Content",
                    "created_at": content.created_at.isoformat() if content.created_at else None,
                    "user_rating": content.user_rating,
                    "is_published": content.is_published or False,
                    "performance_data": content.performance_data or {},
                    # ✅ Amplification context
                    "amplification_context": {
                        "generated_from_amplified_intelligence": is_amplified_content,
                        "amplification_metadata": intelligence_used.get("amplification_metadata", {})
                    }
                })
            except Exception as content_error:
                logger.warning(f"⚠️ Error processing content {content.id}: {str(content_error)}")
                # Skip problematic content instead of failing
                continue

        # ✅ Build final response
        response = {
            "campaign_id": campaign_id,
            "intelligence_sources": intelligence_data,
            "generated_content": content_data,
            "summary": {
                "total_intelligence_sources": total_intelligence,
                "total_generated_content": total_content,
                "avg_confidence_score": round(avg_confidence, 3),
                # ✅ Amplification summary
                "amplification_summary": {
                    "sources_amplified": amplified_sources,
                    "sources_available_for_amplification": total_intelligence - amplified_sources,
                    "total_scientific_enhancements": total_scientific_enhancements,
                    "amplification_available": AMPLIFIER_AVAILABLE,
                    "amplification_coverage": f"{amplified_sources}/{total_intelligence}" if total_intelligence > 0 else "0/0"
                }
            }
        }

        logger.info(f"✅ Enhanced intelligence response prepared successfully")

        return response

    except Exception as e:
        logger.error(f"❌ Error building response: {str(e)}")
        logger.error(f"📍 Response building traceback: {traceback.format_exc()}")

        # Return minimal response instead of failing
        return {
            "campaign_id": campaign_id,
            "intelligence_sources": [],
            "generated_content": [],
            "summary": {
                "total_intelligence_sources": 0,
                "total_generated_content": 0,
                "avg_confidence_score": 0.0,
                "amplification_summary": {
                    "sources_amplified": 0,
                    "sources_available_for_amplification": 0,
                    "total_scientific_enhancements": 0,
                    "amplification_available": AMPLIFIER_AVAILABLE,
                    "amplification_coverage": "0/0"
                }
            },
            "error": "Partial response - some data may be missing",
            "partial_data": True
        }

    except Exception as e:
        logger.error(f"❌ Critical error in get_campaign_intelligence: {str(e)}")
        logger.error(f"📍 Full traceback: {traceback.format_exc()}")

        # Always return a valid response to prevent infinite loading
        return {
            "campaign_id": campaign_id,
            "intelligence_sources": [],
            "generated_content": [],
            "summary": {
                "total_intelligence_sources": 0,
                "total_generated_content": 0,
                "avg_confidence_score": 0.0,
                "amplification_summary": {
                    "sources_amplified": 0,
                    "sources_available_for_amplification": 0,
                    "total_scientific_enhancements": 0,
                    "amplification_available": AMPLIFIER_AVAILABLE,
                    "amplification_coverage": "0/0"
                }
            },
            "error": "Failed to load intelligence data",
            "fallback_response": True
        }

# ============================================================================
# ENHANCED MAIN ANALYSIS ENDPOINT - WITH AMPLIFIER INTEGRATION
# ============================================================================

@router.post("/analyze-url", response_model=AnalysisResponse)
async def analyze_sales_page(
    request: AnalyzeURLRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """✅ ENHANCED: Analyze competitor sales page with AMPLIFIER INTEGRATION"""

    logger.info(f"🎯 Starting AMPLIFIED URL analysis for: {str(request.url)}")

    # Check credits if system is available
    if CREDITS_AVAILABLE:
        try:
            await check_and_consume_credits(
                user=current_user,
                operation="intelligence_analysis",
                credits_required=5,
                db=db
            )
        except Exception as e:
            logger.warning(f"⚠️ Credits check failed but continuing: {str(e)}")

    # Verify campaign ownership
    try:
        campaign_result = await db.execute(
            select(Campaign).where(
                and_(
                    Campaign.id == request.campaign_id,
                    Campaign.company_id == current_user.company_id
                )
            )
        )
        campaign = campaign_result.scalar_one_or_none()
        if not campaign:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error verifying campaign: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify campaign access"
        )

    # Create intelligence record
    try:
        intelligence = CampaignIntelligence(
            source_url=str(request.url),
            source_type=IntelligenceSourceType.SALES_PAGE,
            campaign_id=uuid.UUID(request.campaign_id),
            user_id=current_user.id,
            company_id=current_user.company_id,
            analysis_status=AnalysisStatus.PROCESSING
        )

        db.add(intelligence)
        await db.commit()
        await db.refresh(intelligence)

        logger.info(f"✅ Created intelligence record: {intelligence.id}")

    except Exception as e:
        logger.error(f"❌ Error creating intelligence record: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create intelligence record"
        )

    # ✅ ENHANCED: AMPLIFIED ANALYSIS SECTION
    try:
        # STEP 1: Basic Analysis (your existing analyzer)
        if request.analysis_type == "sales_page":
            analyzer = SalesPageAnalyzer()
        elif request.analysis_type == "website":
            analyzer = WebAnalyzer()
        else:
            analyzer = SalesPageAnalyzer()

        logger.info(f"🔧 Using analyzer: {type(analyzer).__name__}")
        base_analysis_result = await analyzer.analyze(str(request.url))

        logger.info(f"📊 Base analysis completed with confidence: {base_analysis_result.get('confidence_score', 0.0)}")

        # STEP 2: AMPLIFICATION (if available)
        if AMPLIFIER_AVAILABLE:
            try:
                logger.info("🚀 Starting intelligence amplification...")

                # Initialize amplifier
                amplifier = IntelligenceAmplificationService()

                # Prepare sources for amplification
                user_sources = [{
                    "type": "url",
                    "url": str(request.url),
                    "analysis_result": base_analysis_result
                }]

                # Run amplification
                amplification_result = await amplifier.process_sources(
                    sources=user_sources,
                    preferences={
                        "enhance_scientific_backing": True,
                        "boost_credibility": True,
                        "competitive_analysis": True
                    }
                )

                # Get enriched intelligence
                enriched_intelligence = amplification_result.get("intelligence_data", base_analysis_result)
                amplification_summary = amplification_result.get("summary", {})

                # Calculate amplification boost
                enrichment_metadata = enriched_intelligence.get("enrichment_metadata", {})
                confidence_boost = enrichment_metadata.get("confidence_boost", 0.0)
                scientific_support = enriched_intelligence.get("offer_intelligence", {}).get("scientific_support", [])
                scientific_enhancements = len(scientific_support) if scientific_support else 0

                logger.info(f"✅ Amplification completed - Confidence boost: {confidence_boost:.1%}, Scientific enhancements: {scientific_enhancements}")

                # Use enriched intelligence as final result
                final_analysis_result = enriched_intelligence

                # Add amplification metadata
                final_analysis_result["amplification_metadata"] = {
                    "amplification_applied": True,
                    "confidence_boost": confidence_boost,
                    "scientific_enhancements": scientific_enhancements,
                    "amplification_summary": amplification_summary,
                    "base_confidence": base_analysis_result.get("confidence_score", 0.0),
                    "amplified_confidence": enriched_intelligence.get("confidence_score", 0.0),
                    "credibility_score": enrichment_metadata.get("credibility_score", 0.0),
                    "total_enhancements": enrichment_metadata.get("total_enhancements", 0)
                }

            except Exception as amp_error:
                logger.warning(f"⚠️ Amplification failed, using base analysis: {str(amp_error)}")
                final_analysis_result = base_analysis_result
                final_analysis_result["amplification_metadata"] = {
                    "amplification_applied": False,
                    "amplification_error": str(amp_error),
                    "fallback_to_base": True
                }
        else:
            logger.info("📝 Amplifier not available, using base analysis")
            final_analysis_result = base_analysis_result
            final_analysis_result["amplification_metadata"] = {
                "amplification_applied": False,
                "amplification_available": False,
                "note": "Install amplifier dependencies for enhanced analysis"
            }

        # STEP 3: Update intelligence record with final results
        intelligence.offer_intelligence = final_analysis_result.get("offer_intelligence", {})
        intelligence.psychology_intelligence = final_analysis_result.get("psychology_intelligence", {})
        intelligence.content_intelligence = final_analysis_result.get("content_intelligence", {})
        intelligence.competitive_intelligence = final_analysis_result.get("competitive_intelligence", {})
        intelligence.brand_intelligence = final_analysis_result.get("brand_intelligence", {})
        intelligence.confidence_score = final_analysis_result.get("confidence_score", 0.0)
        intelligence.source_title = final_analysis_result.get("page_title", "Analyzed Page")
        intelligence.raw_content = final_analysis_result.get("raw_content", "")

        # Store amplification metadata
        intelligence.processing_metadata = final_analysis_result.get("amplification_metadata", {})

        # Set status based on results
        if ANALYZERS_AVAILABLE and final_analysis_result.get("confidence_score", 0.0) > 0:
            intelligence.analysis_status = AnalysisStatus.COMPLETED
        else:
            intelligence.analysis_status = AnalysisStatus.FAILED
            intelligence.processing_metadata = {
                "error": final_analysis_result.get("error_message", "Dependencies missing"),
                "note": final_analysis_result.get("analysis_note", "Install aiohttp, beautifulsoup4, lxml")
            }

        await db.commit()

        # Update campaign counters (non-critical)
        try:
            await update_campaign_counters(request.campaign_id, db)
            await db.commit()
            logger.info(f"📊 Campaign counters updated")
        except Exception as counter_error:
            logger.warning(f"⚠️ Campaign counter update failed (non-critical): {str(counter_error)}")

        # Extract competitive opportunities (enhanced by amplification)
        competitive_intel = final_analysis_result.get("competitive_intelligence", {})
        competitive_opportunities = []
        if isinstance(competitive_intel.get("opportunities"), list):
            for opp in competitive_intel["opportunities"]:
                competitive_opportunities.append({"description": str(opp), "priority": "medium"})

        campaign_suggestions = final_analysis_result.get("campaign_suggestions", [])

        # Add amplification-specific suggestions
        amplification_metadata = final_analysis_result.get("amplification_metadata", {})
        if amplification_metadata.get("amplification_applied"):
            campaign_suggestions.extend([
                "✅ Leverage scientific backing in content creation",
                "✅ Use enhanced credibility positioning",
                "✅ Apply competitive intelligence insights"
            ])
            if amplification_metadata.get("scientific_enhancements", 0) > 0:
                campaign_suggestions.append(f"✅ {amplification_metadata['scientific_enhancements']} scientific enhancements available")

        logger.info(f"✅ AMPLIFIED analysis completed successfully for: {str(request.url)}")

        return AnalysisResponse(
            intelligence_id=str(intelligence.id),
            analysis_status=intelligence.analysis_status.value,
            confidence_score=intelligence.confidence_score,
            offer_intelligence=intelligence.offer_intelligence,
            psychology_intelligence=intelligence.psychology_intelligence,
            competitive_opportunities=competitive_opportunities,
            campaign_suggestions=campaign_suggestions
        )

    except Exception as e:
        logger.error(f"❌ Analysis failed for {str(request.url)}: {str(e)}")

        # Update status to failed
        try:
            intelligence.analysis_status = AnalysisStatus.FAILED
            intelligence.processing_metadata = {
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            await db.commit()
        except:
            await db.rollback()

        # Return a failed analysis instead of raising exception
        return AnalysisResponse(
            intelligence_id=str(intelligence.id),
            analysis_status="failed",
            confidence_score=0.0,
            offer_intelligence={"products": [], "pricing": [], "bonuses": [], "guarantees": [], "value_propositions": []},
            psychology_intelligence={"emotional_triggers": [], "pain_points": [], "target_audience": "Unknown", "persuasion_techniques": []},
            competitive_opportunities=[{"description": f"Analysis failed: {str(e)}", "priority": "high"}],
            campaign_suggestions=[
                "Check server logs for detailed error information",
                "Verify all dependencies are installed",
                "Try with a different URL"
            ]
        )