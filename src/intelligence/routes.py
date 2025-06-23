# src/intelligence/routes.py - FIXED VERSION with Import Error Handling
"""
Intelligence analysis routes - The killer feature that sets us apart
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

# ✅ FIXED: Add import error handling for analyzers
try:
    from src.intelligence.analyzers import SalesPageAnalyzer, DocumentAnalyzer, WebAnalyzer, EnhancedSalesPageAnalyzer, VSLAnalyzer
    ANALYZERS_AVAILABLE = True
    print("✅ SUCCESS: All intelligence analyzers imported successfully")
except ImportError as e:
    print(f"❌ IMPORT ERROR: Failed to import analyzers: {str(e)}")
    print("This is likely due to missing dependencies: aiohttp, beautifulsoup4, lxml")
    ANALYZERS_AVAILABLE = False
    # Create fallback analyzer class
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
    
    # Use fallback analyzer
    SalesPageAnalyzer = FallbackAnalyzer
    DocumentAnalyzer = FallbackAnalyzer
    WebAnalyzer = FallbackAnalyzer
    EnhancedSalesPageAnalyzer = FallbackAnalyzer
    VSLAnalyzer = FallbackAnalyzer

# Similarly handle other imports
try:
    from src.intelligence.generators import ContentGenerator, CampaignAngleGenerator
    GENERATORS_AVAILABLE = True
except ImportError as e:
    print(f"❌ IMPORT ERROR: Failed to import generators: {str(e)}")
    GENERATORS_AVAILABLE = False
    
    class FallbackGenerator:
        async def generate_content(self, *args, **kwargs):
            return {
                "title": "Content Generation Disabled",
                "content": "Install missing dependencies to enable content generation",
                "metadata": {"error": "Missing dependencies"},
                "performance_predictions": {}
            }
    
    ContentGenerator = FallbackGenerator
    CampaignAngleGenerator = FallbackGenerator

try:
    from src.core.credits import check_and_consume_credits
    CREDITS_AVAILABLE = True
except ImportError:
    print("❌ WARNING: Credits system not available")
    CREDITS_AVAILABLE = False
    
    async def check_and_consume_credits(*args, **kwargs):
        print("⚠️ Credits system not available - skipping credit check")
        pass

logger = logging.getLogger(__name__)
router = APIRouter(tags=["intelligence"])

# ============================================================================
# HELPER FUNCTIONS - CAMPAIGN COUNTER UPDATES
# ============================================================================

async def update_campaign_counters(campaign_id: str, db: AsyncSession):
    """Update campaign counter fields based on actual data"""
    
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
            intelligence_extracted=sources_count,  # For compatibility
            intelligence_count=sources_count,      # For compatibility
            content_generated=generated_content_count,
            generated_content_count=generated_content_count,
            updated_at=datetime.utcnow()
        )
    )
    
    print(f"📊 Updated campaign counters: {sources_count} sources, {generated_content_count} content")

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
# MAIN ANALYSIS ENDPOINT - FIXED
# ============================================================================

@router.post("/analyze-url", response_model=AnalysisResponse)
async def analyze_sales_page(
    request: AnalyzeURLRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """✅ FIXED: Analyze competitor sales page with proper error handling"""
    
    print(f"🎯 Starting URL analysis for: {str(request.url)}")
    print(f"📊 Analyzers available: {ANALYZERS_AVAILABLE}")
    
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
            print(f"⚠️ Credits check failed but continuing: {str(e)}")
    
    # Verify campaign ownership
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
    
    # Create intelligence record first
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
    
    print(f"✅ Created intelligence record: {intelligence.id}")
    
    try:
        # ✅ FIXED: Always create analyzer, even if it's the fallback
        if request.analysis_type == "sales_page":
            analyzer = SalesPageAnalyzer()
        elif request.analysis_type == "website":
            analyzer = WebAnalyzer()
        else:
            analyzer = SalesPageAnalyzer()
        
        print(f"🔧 Using analyzer: {type(analyzer).__name__}")
        
        # Run the analysis
        analysis_result = await analyzer.analyze(str(request.url))
        
        print(f"📈 Analysis completed with confidence: {analysis_result.get('confidence_score', 0.0)}")
        
        # Update intelligence record with results
        intelligence.offer_intelligence = analysis_result.get("offer_intelligence", {})
        intelligence.psychology_intelligence = analysis_result.get("psychology_intelligence", {})
        intelligence.content_intelligence = analysis_result.get("content_intelligence", {})
        intelligence.competitive_intelligence = analysis_result.get("competitive_intelligence", {})
        intelligence.brand_intelligence = analysis_result.get("brand_intelligence", {})
        intelligence.confidence_score = analysis_result.get("confidence_score", 0.0)
        intelligence.source_title = analysis_result.get("page_title", "Analyzed Page")
        intelligence.raw_content = analysis_result.get("raw_content", "")
        
        # ✅ FIXED: Set status based on whether we have real results or fallback
        if ANALYZERS_AVAILABLE and analysis_result.get("confidence_score", 0.0) > 0:
            intelligence.analysis_status = AnalysisStatus.COMPLETED
        else:
            intelligence.analysis_status = AnalysisStatus.FAILED
            intelligence.processing_metadata = {
                "error": analysis_result.get("error_message", "Dependencies missing"),
                "note": analysis_result.get("analysis_note", "Install aiohttp, beautifulsoup4, lxml")
            }
        
        await db.commit()
        
        # ✅ NEW: Update campaign counters
        await update_campaign_counters(request.campaign_id, db)
        await db.commit()
        
        print(f"💾 Intelligence record updated: {intelligence.analysis_status}")
        print(f"📊 Campaign counters updated")
        
        # Extract competitive opportunities
        competitive_intel = analysis_result.get("competitive_intelligence", {})
        competitive_opportunities = []
        if isinstance(competitive_intel.get("opportunities"), list):
            for opp in competitive_intel["opportunities"]:
                competitive_opportunities.append({"description": str(opp), "priority": "medium"})
        
        campaign_suggestions = analysis_result.get("campaign_suggestions", [])
        
        print(f"✅ Analysis completed successfully for: {str(request.url)}")
        
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
        print(f"❌ Analysis failed for {str(request.url)}: {str(e)}")
        print(f"📍 Error traceback: {traceback.format_exc()}")
        
        # Update status to failed
        intelligence.analysis_status = AnalysisStatus.FAILED
        intelligence.processing_metadata = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        await db.commit()
        
        # Don't raise HTTP exception - return a failed analysis instead
        return AnalysisResponse(
            intelligence_id=str(intelligence.id),
            analysis_status="failed",
            confidence_score=0.0,
            offer_intelligence={"products": [], "pricing": [], "bonuses": [], "guarantees": [], "value_propositions": []},
            psychology_intelligence={"emotional_triggers": [], "pain_points": [], "target_audience": "Unknown", "persuasion_techniques": []},
            competitive_opportunities=[{"description": f"Analysis failed: {str(e)}", "priority": "high"}],
            campaign_suggestions=[
                "Check server logs for detailed error information",
                "Verify all dependencies are installed on Railway",
                "Try with a different URL"
            ]
        )

# ============================================================================
# KEEP ALL OTHER EXISTING ENDPOINTS
# ============================================================================

@router.post("/upload-document")
async def upload_document_for_analysis(
    file: UploadFile = File(...),
    campaign_id: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and analyze documents (PDF, Word, PowerPoint, etc.)"""
    
    if not ANALYZERS_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document analysis is currently unavailable due to missing dependencies"
        )
    
    # Check file type and size limits based on tier
    allowed_types = {
        "free": ["pdf"],
        "growth": ["pdf", "docx", "pptx", "txt"],
        "professional": ["pdf", "docx", "pptx", "txt", "xlsx", "csv"],
        "agency": ["pdf", "docx", "pptx", "txt", "xlsx", "csv", "mp3", "mp4"]
    }
    
    user_tier = getattr(current_user.company, 'subscription_tier', 'free')
    file_extension = file.filename.split('.')[-1].lower()
    
    if file_extension not in allowed_types.get(user_tier, ["pdf"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported for {user_tier} tier"
        )
    
    # Check credits
    if CREDITS_AVAILABLE:
        await check_and_consume_credits(
            user=current_user,
            operation="document_analysis",
            credits_required=3,
            db=db
        )
    
    try:
        # Save file and process
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
        
        # ✅ NEW: Update campaign counters
        await update_campaign_counters(campaign_id, db)
        await db.commit()
        
        return {
            "intelligence_id": str(intelligence.id),
            "status": "completed",
            "insights_extracted": len(analysis_result.get("key_insights", [])),
            "content_opportunities": analysis_result.get("content_opportunities", [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document analysis failed: {str(e)}"
        )

@router.post("/generate-content", response_model=ContentGenerationResponse)
async def generate_content_from_intelligence(
    request: GenerateContentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """✅ FIXED: Generate marketing content from analyzed intelligence - Transaction Safe"""
    
    print(f"🎯 Starting content generation: {request.content_type}")
    
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
        
        print(f"✅ Found intelligence source: {intelligence.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error finding intelligence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find intelligence source"
        )
    
    # Check credits for content generation
    if CREDITS_AVAILABLE:
        try:
            await check_and_consume_credits(
                user=current_user,
                operation="content_generation",
                credits_required=2,
                db=db
            )
            print(f"✅ Credits checked successfully")
        except Exception as e:
            print(f"⚠️ Credits check failed but continuing: {str(e)}")
    
    try:
        # ✅ STEP 1: Generate content using intelligence
        print(f"🔧 Starting content generation...")
        
        generator = ContentGenerator()
        
        content_result = await generator.generate_content(
            intelligence_data={
                "offer_intelligence": intelligence.offer_intelligence or {},
                "psychology_intelligence": intelligence.psychology_intelligence or {},
                "content_intelligence": intelligence.content_intelligence or {},
                "competitive_intelligence": intelligence.competitive_intelligence or {},
                "brand_intelligence": intelligence.brand_intelligence or {}
            },
            content_type=request.content_type,
            preferences=request.preferences or {}
        )
        
        print(f"✅ Content generated: {content_result.get('title', 'Untitled')}")
        
        # ✅ STEP 2: Prepare content data with safe formatting
        print(f"💾 Preparing content for database...")
        
        # Ensure content_body is properly formatted
        content_body = content_result.get("content", {})
        if isinstance(content_body, dict):
            content_body_str = json.dumps(content_body)
        else:
            content_body_str = str(content_body)
        
        # Safe metadata handling
        metadata = content_result.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        
        # Safe preferences handling
        preferences = request.preferences or {}
        if not isinstance(preferences, dict):
            preferences = {}
        
        # ✅ FIXED: Safe intelligence_used data (no extra semicolons)
        intelligence_used_data = {
            "intelligence_id": str(intelligence.id),
            "source_url": str(intelligence.source_url or ""),  # Remove any trailing semicolons
            "confidence_score": float(intelligence.confidence_score or 0.0)
        }
        
        # ✅ STEP 3: Create and save content record
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
        
        # ✅ CRITICAL: Commit content first before anything else
        await db.commit()
        await db.refresh(generated_content)
        
        print(f"✅ Content saved to database: {generated_content.id}")
        
        # ✅ STEP 4: Handle optional features in separate transactions
        smart_url = None
        
        # Smart URL creation (non-critical)
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
                print(f"✅ Smart URL created: {smart_url}")
                
            except Exception as smart_url_error:
                print(f"⚠️ Smart URL creation failed (non-critical): {str(smart_url_error)}")
                # Don't rollback - content is already saved
        
        # Usage count update (non-critical)
        try:
            intelligence.usage_count = (intelligence.usage_count or 0) + 1
            await db.commit()
            print(f"✅ Intelligence usage count updated")
        except Exception as usage_error:
            print(f"⚠️ Usage count update failed (non-critical): {str(usage_error)}")
            # Don't rollback - content is already saved
        
        # Campaign counters update (non-critical)
        try:
            await update_campaign_counters(request.campaign_id, db)
            await db.commit()
            print(f"✅ Campaign counters updated")
        except Exception as counter_error:
            print(f"⚠️ Campaign counter update failed (non-critical): {str(counter_error)}")
            # Don't rollback - content is already saved
        
        print(f"🎉 Content generation completed successfully!")
        
        # ✅ STEP 5: Return successful response
        return ContentGenerationResponse(
            content_id=str(generated_content.id),
            content_type=request.content_type,
            generated_content=content_result,
            smart_url=smart_url,
            performance_predictions=content_result.get("performance_predictions", {})
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        print(f"❌ Content generation failed: {str(e)}")
        import traceback
        print(f"📍 Full traceback: {traceback.format_exc()}")
        
        # Rollback any pending transaction
        try:
            await db.rollback()
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@router.get("/campaign/{campaign_id}/intelligence")
async def get_campaign_intelligence(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all intelligence sources for a campaign"""
    
    # Verify campaign access
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
    
    try:
        # Get all intelligence sources for this campaign
        intelligence_query = select(CampaignIntelligence).where(
            CampaignIntelligence.campaign_id == campaign_id
        ).order_by(CampaignIntelligence.created_at.desc())
        
        intelligence_result = await db.execute(intelligence_query)
        intelligence_sources = intelligence_result.scalars().all()
        
        # Get all generated content for this campaign
        content_query = select(GeneratedContent).where(
            GeneratedContent.campaign_id == campaign_id
        ).order_by(GeneratedContent.created_at.desc())
        
        content_result = await db.execute(content_query)
        generated_content = content_result.scalars().all()
        
        # Calculate summary statistics
        total_intelligence = len(intelligence_sources)
        total_content = len(generated_content)
        avg_confidence = 0.0
        
        if intelligence_sources:
            confidence_scores = [source.confidence_score for source in intelligence_sources if source.confidence_score]
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Convert to response format
        intelligence_data = []
        for source in intelligence_sources:
            intelligence_data.append({
                "id": str(source.id),
                "source_title": source.source_title or "Untitled Source",
                "source_url": source.source_url,
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
                "brand_intelligence": source.brand_intelligence or {}
            })
        
        content_data = []
        for content in generated_content:
            content_data.append({
                "id": str(content.id),
                "content_type": content.content_type,
                "content_title": content.content_title,
                "created_at": content.created_at.isoformat() if content.created_at else None,
                "user_rating": content.user_rating,
                "is_published": content.is_published or False,
                "performance_data": content.performance_data or {}
            })
        
        return {
            "campaign_id": campaign_id,
            "intelligence_sources": intelligence_data,
            "generated_content": content_data,
            "summary": {
                "total_intelligence_sources": total_intelligence,
                "total_generated_content": total_content,
                "avg_confidence_score": round(avg_confidence, 3)
            }
        }
        
    except Exception as e:
        print(f"❌ DEBUG: Error getting campaign intelligence: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign intelligence: {str(e)}"
        )

# ============================================================================
# CAMPAIGN COUNTER SYNC ENDPOINT
# ============================================================================

@router.post("/campaigns/{campaign_id}/sync-counters")
async def sync_campaign_counters(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Manually sync campaign counters with actual data"""
    
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
    await update_campaign_counters(campaign_id, db)
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