# src/intelligence/routes.py - ENHANCED WITH AMPLIFIER INTEGRATION AND FIXED CONTENT ROUTING
"""
Intelligence analysis routes - Enhanced with Intelligence Amplifier and Fixed Content Type Routing
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import uuid
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

# ✅ ENHANCED: Safe import handling for analyzers
try:
    from src.intelligence.analyzers import SalesPageAnalyzer, DocumentAnalyzer, WebAnalyzer, EnhancedSalesPageAnalyzer, VSLAnalyzer
    ANALYZERS_AVAILABLE = True
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

logger = logging.getLogger(__name__)
router = APIRouter(tags=["intelligence"])

# ============================================================================
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error verifying campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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

# ============================================================================
# ✅ FIXED: CONTENT GENERATION WITH PROPER CONTENT TYPE ROUTING
# ============================================================================

@router.post("/generate-content", response_model=ContentGenerationResponse)
async def generate_content_from_intelligence(
    request: GenerateContentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """✅ FIXED: Generate content using appropriate generator based on content_type"""
    
    logger.info(f"🎯 Starting content generation: {request.content_type}")
    
    if not GENERATORS_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Content generation is currently unavailable due to missing dependencies"
        )
    
    # Get intelligence data
    try:
        intelligence_result = await db.execute(
            select(CampaignIntelligence).where(
                and_(
                    CampaignIntelligence.id == request.intelligence_id,
                    CampaignIntelligence.company_id == current_user.company_id
                )
            )
        )
        intelligence = intelligence_result.scalar_one_or_none()
        
        if not intelligence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Intelligence source not found"
            )
        
        logger.info(f"✅ Found intelligence source: {intelligence.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error finding intelligence: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find intelligence source"
        )
    
    # Check credits
    if CREDITS_AVAILABLE:
        try:
            await check_and_consume_credits(
                user=current_user,
                operation="content_generation",
                credits_required=2,
                db=db
            )
            logger.info(f"✅ Credits checked successfully")
        except Exception as e:
            logger.warning(f"⚠️ Credits check failed but continuing: {str(e)}")
    
    try:
        # ✅ Build intelligence data (same as before)
        intelligence_data = {
            "offer_intelligence": intelligence.offer_intelligence or {},
            "psychology_intelligence": intelligence.psychology_intelligence or {},
            "content_intelligence": intelligence.content_intelligence or {},
            "competitive_intelligence": intelligence.competitive_intelligence or {},
            "brand_intelligence": intelligence.brand_intelligence or {},
            "confidence_score": intelligence.confidence_score or 0.0
        }
        
        # Check if this intelligence was amplified
        amplification_metadata = intelligence.processing_metadata or {}
        is_amplified = amplification_metadata.get("amplification_applied", False)
        
        if is_amplified:
            logger.info("🚀 Using AMPLIFIED intelligence for content generation")
            
            # Add amplification context to preferences
            enhanced_preferences = request.preferences.copy() if request.preferences else {}
            enhanced_preferences.update({
                "amplified_intelligence": True,
                "confidence_boost": amplification_metadata.get("confidence_boost", 0.0),
                "scientific_enhancements": amplification_metadata.get("scientific_enhancements", 0),
                "credibility_score": amplification_metadata.get("credibility_score", 0.0),
                "amplification_advantages": [
                    "Scientific backing integration",
                    "Enhanced credibility positioning", 
                    "Competitive intelligence insights",
                    "Research-backed content approach"
                ]
            })
        else:
            logger.info("📝 Using base intelligence for content generation")
            enhanced_preferences = request.preferences.copy() if request.preferences else {}
        
        # ✅ NEW: Route to appropriate generator based on content_type
        content_result = None
        
        if request.content_type == "email_sequence":
            logger.info("📧 Generating email sequence")
            generator = EmailSequenceGenerator()
            content_result = await generator.generate_email_sequence(intelligence_data, enhanced_preferences)
            
        elif request.content_type in ["social_posts", "social_media_posts"]:
            logger.info("📱 Generating social media posts")
            try:
                generator = SocialMediaGenerator()
                content_result = await generator.generate_social_posts(intelligence_data, enhanced_preferences)
            except (ImportError, AttributeError):
                # Fallback to email generator with adapted response
                logger.warning("⚠️ SocialMediaGenerator not available, using email fallback")
                generator = EmailSequenceGenerator()
                email_result = await generator.generate_email_sequence(intelligence_data, enhanced_preferences)
                # Transform email result to social posts format
                emails = email_result.get("content", {}).get("emails", [])
                content_result = {
                    "content_type": "social_media_posts",
                    "title": "Social Media Posts (Generated from Email Content)",
                    "content": {
                        "posts": [
                            {
                                "platform": "facebook",
                                "content": f"🚀 {email['subject']}\n\n{email['body'][:200]}...\n\n#marketing #business #growth",
                                "hashtags": ["#marketing", "#business", "#growth"],
                                "character_count": len(f"{email['subject']}\n\n{email['body'][:200]}...")
                            } for email in emails[:3]
                        ]
                    },
                    "metadata": email_result.get("metadata", {})
                }
                
        elif request.content_type == "ad_copy":
            logger.info("📢 Generating ad copy")
            try:
                generator = AdCopyGenerator()
                content_result = await generator.generate_ad_copy(intelligence_data, enhanced_preferences)
            except (ImportError, AttributeError):
                # Fallback - transform email to ad copy
                logger.warning("⚠️ AdCopyGenerator not available, using email fallback")
                generator = EmailSequenceGenerator()
                email_result = await generator.generate_email_sequence(intelligence_data, enhanced_preferences)
                emails = email_result.get("content", {}).get("emails", [])
                content_result = {
                    "content_type": "ad_copy",
                    "title": "Advertisement Copy (Generated from Email Content)",
                    "content": {
                        "ads": [
                            {
                                "platform": "facebook",
                                "headline": email["subject"],
                                "body": email["body"][:150] + "...",
                                "cta": "Learn More",
                                "target_audience": enhanced_preferences.get("target_audience", "General audience")
                            } for email in emails[:2]
                        ]
                    },
                    "metadata": email_result.get("metadata", {})
                }
                
        elif request.content_type == "blog_post":
            logger.info("📝 Generating blog post")
            try:
                generator = BlogPostGenerator()
                content_result = await generator.generate_blog_post(intelligence_data, enhanced_preferences)
            except (ImportError, AttributeError):
                # Fallback - transform email to blog post
                logger.warning("⚠️ BlogPostGenerator not available, using email fallback")
                generator = EmailSequenceGenerator()
                email_result = await generator.generate_email_sequence(intelligence_data, enhanced_preferences)
                emails = email_result.get("content", {}).get("emails", [])
                blog_content = "\n\n".join([f"## {email['subject']}\n\n{email['body']}" for email in emails])
                content_result = {
                    "content_type": "blog_post",
                    "title": "Blog Post (Generated from Email Series)",
                    "content": {
                        "title": f"Complete Guide: {emails[0]['subject'] if emails else 'Marketing Insights'}",
                        "body": blog_content,
                        "meta_description": f"Comprehensive guide based on {len(emails)} key insights",
                        "tags": ["marketing", "business", "strategy"],
                        "word_count": len(blog_content.split())
                    },
                    "metadata": email_result.get("metadata", {})
                }
                
        elif request.content_type == "landing_page":
            logger.info("🎯 Generating landing page")
            try:
                generator = LandingPageGenerator()
                content_result = await generator.generate_landing_page(intelligence_data, enhanced_preferences)
            except (ImportError, AttributeError):
                # Fallback - create landing page from email content
                logger.warning("⚠️ LandingPageGenerator not available, using email fallback")
                generator = EmailSequenceGenerator()
                email_result = await generator.generate_email_sequence(intelligence_data, enhanced_preferences)
                emails = email_result.get("content", {}).get("emails", [])
                
                content_result = {
                    "content_type": "landing_page",
                    "title": "Landing Page (Generated from Email Content)",
                    "content": {
                        "html": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{emails[0]['subject'] if emails else 'Landing Page'}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .hero {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 20px; text-align: center; border-radius: 10px; }}
        .section {{ margin: 40px 0; padding: 20px; }}
        .cta {{ background: #28a745; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 18px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="hero">
        <h1>{emails[0]['subject'] if emails else 'Welcome'}</h1>
        <p>Discover the power of our solution</p>
    </div>
    {''.join([f'<div class="section"><h2>{email["subject"]}</h2><p>{email["body"][:300]}...</p></div>' for email in emails[:3]])}
    <div style="text-align: center; margin: 40px 0;">
        <button class="cta">Get Started Now</button>
    </div>
</body>
</html>""",
                        "sections": [{"title": email["subject"], "content": email["body"]} for email in emails],
                        "page_type": "lead_generation"
                    },
                    "metadata": email_result.get("metadata", {})
                }
                
        elif request.content_type == "video_script":
            logger.info("🎬 Generating video script")
            try:
                generator = VideoScriptGenerator()
                content_result = await generator.generate_video_script(intelligence_data, enhanced_preferences)
            except (ImportError, AttributeError):
                # Fallback - create video script from email content
                logger.warning("⚠️ VideoScriptGenerator not available, using email fallback")
                generator = EmailSequenceGenerator()
                email_result = await generator.generate_email_sequence(intelligence_data, enhanced_preferences)
                emails = email_result.get("content", {}).get("emails", [])
                
                content_result = {
                    "content_type": "video_script",
                    "title": "Video Script (Generated from Email Content)",
                    "content": {
                        "title": emails[0]['subject'] if emails else 'Video Script',
                        "duration": "3-5 minutes",
                        "scenes": [
                            {
                                "scene": i + 1,
                                "title": email["subject"],
                                "script": email["body"][:300] + "...",
                                "duration": "60-90 seconds",
                                "visual_notes": "Show relevant graphics and text overlays"
                            } for i, email in enumerate(emails[:3])
                        ],
                        "call_to_action": "Subscribe for more insights!"
                    },
                    "metadata": email_result.get("metadata", {})
                }
        else:
            # Default to email sequence for unknown types
            logger.info(f"❓ Unknown content type '{request.content_type}', defaulting to email sequence")
            generator = EmailSequenceGenerator()
            content_result = await generator.generate_email_sequence(intelligence_data, enhanced_preferences)
        
        # ✅ ENHANCED: Add amplification context to content result
        if is_amplified:
            content_result["amplification_context"] = {
                "amplified_intelligence_used": True,
                "confidence_boost": amplification_metadata.get("confidence_boost", 0.0),
                "scientific_enhancements": amplification_metadata.get("scientific_enhancements", 0),
                "credibility_score": amplification_metadata.get("credibility_score", 0.0),
                "amplification_advantages": enhanced_preferences.get("amplification_advantages", []),
                "content_quality_boost": "Enhanced through intelligence amplification"
            }
            
            # Enhance performance predictions with amplification data
            existing_predictions = content_result.get("performance_predictions", {})
            confidence_boost = amplification_metadata.get("confidence_boost", 0.0)
            scientific_enhancements = amplification_metadata.get("scientific_enhancements", 0)
            
            existing_predictions["amplification_boost"] = f"+{confidence_boost * 100:.0f}% from intelligence amplification"
            existing_predictions["scientific_credibility"] = "High" if scientific_enhancements > 0 else "Standard"
            existing_predictions["competitive_advantage"] = "Intelligence-amplified positioning"
            existing_predictions["content_quality"] = "Premium - Amplified Intelligence" if is_amplified else "Standard"
            
            content_result["performance_predictions"] = existing_predictions
        
        logger.info(f"✅ Content generated successfully: {request.content_type} ({'AMPLIFIED' if is_amplified else 'STANDARD'})")
        
        # Prepare content data safely for database storage
        content_body = content_result.get("content", {})
        if isinstance(content_body, dict):
            content_body_str = json.dumps(content_body)
        else:
            content_body_str = str(content_body)
        
        metadata = content_result.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        
        preferences = enhanced_preferences or {}
        if not isinstance(preferences, dict):
            preferences = {}
        
        intelligence_used_data = {
            "intelligence_id": str(intelligence.id),
            "source_url": str(intelligence.source_url or ""),
            "confidence_score": float(intelligence.confidence_score or 0.0),
            "amplified": is_amplified,
            "amplification_metadata": amplification_metadata if is_amplified else {}
        }
        
        # Create and save content record
        generated_content = GeneratedContent(
            content_type=str(request.content_type),
            content_title=str(content_result.get("title", f"Generated {request.content_type}")),
            content_body=content_body_str,
            content_metadata=metadata,
            generation_settings=preferences,
            intelligence_used=intelligence_used_data,
            campaign_id=uuid.UUID(request.campaign_id),
            intelligence_source_id=intelligence.id,
            user_id=current_user.id,
            company_id=current_user.company_id
        )
        
        db.add(generated_content)
        await db.commit()
        await db.refresh(generated_content)
        
        logger.info(f"✅ Content saved to database: {generated_content.id}")
        
        # Handle optional features (non-critical)
        smart_url = None
        if content_result.get("needs_tracking"):
            try:
                smart_url_record = SmartURL(
                    short_code=f"cf{uuid.uuid4().hex[:8]}",
                    original_url=content_result.get("target_url", ""),
                    tracking_url=f"https://track.campaignforge.co/cf{uuid.uuid4().hex[:8]}",
                    campaign_id=uuid.UUID(request.campaign_id),
                    generated_content_id=generated_content.id,
                    user_id=current_user.id,
                    company_id=current_user.company_id
                )
                
                db.add(smart_url_record)
                await db.commit()
                smart_url = smart_url_record.tracking_url
                logger.info(f"✅ Smart URL created: {smart_url}")
                
            except Exception as smart_url_error:
                logger.warning(f"⚠️ Smart URL creation failed (non-critical): {str(smart_url_error)}")
        
        # Update usage count (non-critical)
        try:
            intelligence.usage_count = (intelligence.usage_count or 0) + 1
            await db.commit()
            logger.info(f"✅ Intelligence usage count updated")
        except Exception as usage_error:
            logger.warning(f"⚠️ Usage count update failed (non-critical): {str(usage_error)}")
        
        # Update campaign counters (non-critical)
        try:
            await update_campaign_counters(request.campaign_id, db)
            await db.commit()
            logger.info(f"✅ Campaign counters updated")
        except Exception as counter_error:
            logger.warning(f"⚠️ Campaign counter update failed (non-critical): {str(counter_error)}")
        
        logger.info(f"🎉 Content generation completed successfully: {request.content_type}")
        
        return ContentGenerationResponse(
            content_id=str(generated_content.id),
            content_type=request.content_type,
            generated_content=content_result,
            smart_url=smart_url,
            performance_predictions=content_result.get("performance_predictions", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Content generation failed: {str(e)}")
        logger.error(f"📍 Full traceback: {traceback.format_exc()}")
        
        try:
            await db.rollback()
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

# ============================================================================
# ✅ NEW: AMPLIFIER-SPECIFIC ENDPOINTS
# ============================================================================

@router.post("/amplify-intelligence")
async def amplify_existing_intelligence(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """NEW: Amplify existing intelligence sources"""
    
    if not AMPLIFIER_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Intelligence amplification not available - install amplifier dependencies"
        )
    
    intelligence_ids = request.get("intelligence_ids", [])
    amplification_preferences = request.get("preferences", {})
    
    if not intelligence_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No intelligence sources provided"
        )
    
    try:
        # Get intelligence sources
        intelligence_sources = []
        for intel_id in intelligence_ids:
            intel_result = await db.execute(
                select(CampaignIntelligence).where(
                    and_(
                        CampaignIntelligence.id == intel_id,
                        CampaignIntelligence.company_id == current_user.company_id
                    )
                )
            )
            intel = intel_result.scalar_one_or_none()
            if intel:
                intelligence_sources.append({
                    "type": "intelligence",
                    "id": str(intel.id),
                    "url": intel.source_url,
                    "data": {
                        "offer_intelligence": intel.offer_intelligence or {},
                        "psychology_intelligence": intel.psychology_intelligence or {},
                        "competitive_intelligence": intel.competitive_intelligence or {},
                        "confidence_score": intel.confidence_score or 0.0
                    }
                })
        
        if not intelligence_sources:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid intelligence sources found"
            )
        
        # Run amplification
        amplifier = IntelligenceAmplificationService()
        amplification_result = await amplifier.process_sources(
            sources=intelligence_sources,
            preferences=amplification_preferences
        )
        
        # Update intelligence records with amplified data
        enriched_intelligence = amplification_result.get("intelligence_data", {})
        amplification_summary = amplification_result.get("summary", {})
        
        for intel_id in intelligence_ids:
            try:
                intel_result = await db.execute(
                    select(CampaignIntelligence).where(
                        CampaignIntelligence.id == intel_id
                    )
                )
                intel = intel_result.scalar_one_or_none()
                if intel:
                    # Update with enriched data
                    if enriched_intelligence.get("offer_intelligence"):
                        intel.offer_intelligence = enriched_intelligence["offer_intelligence"]
                    if enriched_intelligence.get("psychology_intelligence"):
                        intel.psychology_intelligence = enriched_intelligence["psychology_intelligence"]
                    if enriched_intelligence.get("competitive_intelligence"):
                        intel.competitive_intelligence = enriched_intelligence["competitive_intelligence"]
                    
                    # Update confidence score
                    intel.confidence_score = enriched_intelligence.get("confidence_score", intel.confidence_score)
                    
                    # Add amplification metadata
                    enrichment_metadata = enriched_intelligence.get("enrichment_metadata", {})
                    intel.processing_metadata = {
                        "amplification_applied": True,
                        "confidence_boost": enrichment_metadata.get("confidence_boost", 0.0),
                        "scientific_enhancements": len(enriched_intelligence.get("offer_intelligence", {}).get("scientific_support", [])),
                        "credibility_score": enrichment_metadata.get("credibility_score", 0.0),
                        "total_enhancements": enrichment_metadata.get("total_enhancements", 0),
                        "amplified_at": datetime.utcnow().isoformat()
                    }
                    
            except Exception as update_error:
                logger.warning(f"⚠️ Failed to update intelligence {intel_id}: {str(update_error)}")
        
        await db.commit()
        
        return {
            "amplification_applied": True,
            "sources_processed": len(intelligence_sources),
            "enriched_intelligence": enriched_intelligence,
            "amplification_summary": amplification_summary,
            "confidence_improvement": enriched_intelligence.get("enrichment_metadata", {}).get("confidence_boost", 0.0),
            "scientific_enhancements": len(enriched_intelligence.get("offer_intelligence", {}).get("scientific_support", [])),
            "updated_intelligence_ids": intelligence_ids
        }
        
    except Exception as e:
        logger.error(f"❌ Intelligence amplification failed: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Amplification failed: {str(e)}"
        )

@router.get("/amplification-status/{intelligence_id}")
async def get_amplification_status(
    intelligence_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """NEW: Check if intelligence source has been amplified"""
    
    try:
        intel_result = await db.execute(
            select(CampaignIntelligence).where(
                and_(
                    CampaignIntelligence.id == intelligence_id,
                    CampaignIntelligence.company_id == current_user.company_id
                )
            )
        )
        intel = intel_result.scalar_one_or_none()
        
        if not intel:
            raise HTTPException(status_code=404, detail="Intelligence source not found")
        
        amplification_metadata = intel.processing_metadata or {}
        
        return {
            "intelligence_id": intelligence_id,
            "is_amplified": amplification_metadata.get("amplification_applied", False),
            "confidence_boost": amplification_metadata.get("confidence_boost", 0.0),
            "scientific_enhancements": amplification_metadata.get("scientific_enhancements", 0),
            "credibility_score": amplification_metadata.get("credibility_score", 0.0),
            "total_enhancements": amplification_metadata.get("total_enhancements", 0),
            "base_confidence": intel.confidence_score,
            "amplified_at": amplification_metadata.get("amplified_at"),
            "amplification_available": AMPLIFIER_AVAILABLE,
            "amplification_status": "enhanced" if amplification_metadata.get("amplification_applied") else "available" if AMPLIFIER_AVAILABLE else "unavailable"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting amplification status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get amplification status"
        )

# ============================================================================
# EXISTING ENDPOINTS (UNCHANGED)
# ============================================================================

@router.post("/upload-document")
async def upload_document_for_analysis(
    file: UploadFile = File(...),
    campaign_id: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and analyze documents"""
    
    if not ANALYZERS_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document analysis is currently unavailable due to missing dependencies"
        )
    
    # Basic file validation
    allowed_extensions = ["pdf", "docx", "txt", "pptx"]
    file_extension = file.filename.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type .{file_extension} not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Create intelligence record
        intelligence = CampaignIntelligence(
            source_type=IntelligenceSourceType.DOCUMENT,
            source_title=file.filename,
            campaign_id=uuid.UUID(campaign_id),
            user_id=current_user.id,
            company_id=current_user.company_id,
            analysis_status=AnalysisStatus.PROCESSING
        )
        
        db.add(intelligence)
        await db.commit()
        await db.refresh(intelligence)
        
        # Analyze document
        analyzer = DocumentAnalyzer()
        analysis_result = await analyzer.analyze_document(file_content, file_extension)
        
        # Update intelligence with results
        intelligence.content_intelligence = analysis_result.get("content_intelligence", {})
        intelligence.competitive_intelligence = analysis_result.get("competitive_intelligence", {})
        intelligence.confidence_score = analysis_result.get("confidence_score", 0.7)
        intelligence.raw_content = analysis_result.get("extracted_text", "")
        intelligence.analysis_status = AnalysisStatus.COMPLETED
        
        await db.commit()
        
        # Update campaign counters (non-critical)
        try:
            await update_campaign_counters(campaign_id, db)
            await db.commit()
        except Exception as counter_error:
            logger.warning(f"⚠️ Campaign counter update failed: {str(counter_error)}")
        
        return {
            "intelligence_id": str(intelligence.id),
            "status": "completed",
            "insights_extracted": len(analysis_result.get("key_insights", [])),
            "content_opportunities": analysis_result.get("content_opportunities", [])
        }
        
    except Exception as e:
        logger.error(f"❌ Document analysis failed: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document analysis failed: {str(e)}"
        )

# ============================================================================
# ✅ ENHANCED: EXISTING CAMPAIGN INTELLIGENCE ENDPOINT
# ============================================================================

@router.get("/campaign/{campaign_id}/intelligence")
async def get_campaign_intelligence(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """✅ ENHANCED: Get all intelligence sources for a campaign with amplification status"""
    
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        logger.info(f"✅ Campaign access verified: {campaign.title}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error verifying campaign access: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify campaign access"
        )
    
    try:
        # ✅ STEP 2: Get intelligence sources (safe query)
        intelligence_query = select(CampaignIntelligence).where(
            CampaignIntelligence.campaign_id == campaign_id
        ).order_by(CampaignIntelligence.created_at.desc())
        
        intelligence_result = await db.execute(intelligence_query)
        intelligence_sources = intelligence_result.scalars().all()
        
        logger.info(f"✅ Found {len(intelligence_sources)} intelligence sources")
        
    except Exception as e:
        logger.error(f"❌ Error getting intelligence sources: {str(e)}")
        await db.rollback()
        # Return empty instead of failing
        intelligence_sources = []
    
    try:
        # ✅ STEP 3: Get generated content (safe query)
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
    
    # ✅ STEP 4: Build enhanced response safely (no database operations)
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
        
        # Convert to enhanced response format safely
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
                    # ✅ NEW: Amplification status
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
                    # ✅ NEW: Amplification context
                    "amplification_context": {
                        "generated_from_amplified_intelligence": is_amplified_content,
                        "amplification_metadata": intelligence_used.get("amplification_metadata", {})
                    }
                })
            except Exception as content_error:
                logger.warning(f"⚠️ Error processing content {content.id}: {str(content_error)}")
                # Skip problematic content instead of failing
                continue
        
        # ✅ ENHANCED: Response with amplification insights
        response = {
            "campaign_id": campaign_id,
            "intelligence_sources": intelligence_data,
            "generated_content": content_data,
            "summary": {
                "total_intelligence_sources": total_intelligence,
                "total_generated_content": total_content,
                "avg_confidence_score": round(avg_confidence, 3),
                # ✅ NEW: Amplification summary
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
        logger.error(f"❌ Error building enhanced response: {str(e)}")
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
            "error": "Failed to build complete response",
            "partial_data": True
        }

# ============================================================================
# ALL OTHER EXISTING ENDPOINTS (UNCHANGED)
# ============================================================================

@router.post("/campaigns/{campaign_id}/sync-counters")
async def sync_campaign_counters(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Manually sync campaign counters with actual data"""
    
    try:
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
        
        # Update counters
        success = await update_campaign_counters(campaign_id, db)
        if success:
            await db.commit()
        
        # Get updated campaign data
        updated_campaign_result = await db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        updated_campaign = updated_campaign_result.scalar_one()
        
        return {
            "campaign_id": campaign_id,
            "sources_count": getattr(updated_campaign, 'sources_count', 0),
            "intelligence_count": getattr(updated_campaign, 'intelligence_count', 0),
            "content_count": getattr(updated_campaign, 'content_generated', 0),
            "message": "Campaign counters synchronized successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error syncing campaign counters: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync campaign counters: {str(e)}"
        )

# Add more existing endpoints here as needed...