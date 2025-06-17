# src/intelligence/routes.py
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

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.campaign import Campaign
from src.models.intelligence import CampaignIntelligence, GeneratedContent, SmartURL, IntelligenceSourceType
from src.intelligence.analyzers import SalesPageAnalyzer, DocumentAnalyzer, WebAnalyzer
from src.intelligence.generators import ContentGenerator
from src.core.credits import check_and_consume_credits

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])

# Request/Response Models
class AnalyzeURLRequest(BaseModel):
    url: HttpUrl
    campaign_id: str
    analysis_type: str = "sales_page"  # sales_page, website, competitor

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
    content_type: str  # email_sequence, social_posts, ad_copy, blog_post
    preferences: Dict[str, Any] = {}
    campaign_id: str

class ContentGenerationResponse(BaseModel):
    content_id: str
    content_type: str
    generated_content: Dict[str, Any]
    smart_url: Optional[str] = None
    performance_predictions: Dict[str, Any]

@router.post("/analyze-url", response_model=AnalysisResponse)
async def analyze_sales_page(
    request: AnalyzeURLRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze competitor sales page or website - Our killer feature!"""
    
    # Check credits and tier limits
    await check_and_consume_credits(
        user=current_user,
        operation="intelligence_analysis",
        credits_required=5,  # 5 credits per analysis
        db=db
    )
    
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
    
    try:
        # Create intelligence record
        intelligence = CampaignIntelligence(
            source_url=str(request.url),
            source_type=IntelligenceSourceType.SALES_PAGE,
            campaign_id=uuid.UUID(request.campaign_id),
            user_id=current_user.id,
            company_id=current_user.company_id,
            analysis_status="processing"
        )
        
        db.add(intelligence)
        await db.commit()
        await db.refresh(intelligence)
        
        # Perform analysis based on type
        if request.analysis_type == "sales_page":
            analyzer = SalesPageAnalyzer()
        elif request.analysis_type == "website":
            analyzer = WebAnalyzer()
        else:
            analyzer = SalesPageAnalyzer()  # Default
        
        # Run the analysis
        analysis_result = await analyzer.analyze(str(request.url))
        
        # Update intelligence record with results
        intelligence.offer_intelligence = analysis_result.get("offer_intelligence", {})
        intelligence.psychology_intelligence = analysis_result.get("psychology_intelligence", {})
        intelligence.content_intelligence = analysis_result.get("content_intelligence", {})
        intelligence.competitive_intelligence = analysis_result.get("competitive_intelligence", {})
        intelligence.brand_intelligence = analysis_result.get("brand_intelligence", {})
        intelligence.confidence_score = analysis_result.get("confidence_score", 0.8)
        intelligence.source_title = analysis_result.get("page_title", "Analyzed Page")
        intelligence.raw_content = analysis_result.get("raw_content", "")
        intelligence.analysis_status = "completed"
        
        await db.commit()
        
        # Extract competitive opportunities
        competitive_opportunities = analysis_result.get("competitive_intelligence", {}).get("opportunities", [])
        campaign_suggestions = analysis_result.get("campaign_suggestions", [])
        
        return AnalysisResponse(
            intelligence_id=str(intelligence.id),
            analysis_status="completed",
            confidence_score=intelligence.confidence_score,
            offer_intelligence=intelligence.offer_intelligence,
            psychology_intelligence=intelligence.psychology_intelligence,
            competitive_opportunities=competitive_opportunities,
            campaign_suggestions=campaign_suggestions
        )
        
    except Exception as e:
        # Update status to failed
        if 'intelligence' in locals():
            intelligence.analysis_status = "failed"
            intelligence.processing_metadata = {"error": str(e)}
            await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/upload-document")
async def upload_document_for_analysis(
    file: UploadFile = File(...),
    campaign_id: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and analyze documents (PDF, Word, PowerPoint, etc.)"""
    
    # Check file type and size limits based on tier
    allowed_types = {
        "free": ["pdf"],
        "growth": ["pdf", "docx", "pptx", "txt"],
        "professional": ["pdf", "docx", "pptx", "txt", "xlsx", "csv"],
        "agency": ["pdf", "docx", "pptx", "txt", "xlsx", "csv", "mp3", "mp4"]
    }
    
    user_tier = current_user.company.subscription_tier
    file_extension = file.filename.split('.')[-1].lower()
    
    if file_extension not in allowed_types.get(user_tier, ["pdf"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported for {user_tier} tier"
        )
    
    # Check credits
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
            analysis_status="processing"
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
        intelligence.analysis_status = "completed"
        
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
    """Generate marketing content from analyzed intelligence"""
    
    # Get intelligence data
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
    
    # Check credits for content generation
    await check_and_consume_credits(
        user=current_user,
        operation="content_generation",
        credits_required=2,
        db=db
    )
    
    try:
        # Generate content using intelligence
        generator = ContentGenerator()
        
        content_result = await generator.generate_content(
            intelligence_data={
                "offer_intelligence": intelligence.offer_intelligence,
                "psychology_intelligence": intelligence.psychology_intelligence,
                "content_intelligence": intelligence.content_intelligence,
                "competitive_intelligence": intelligence.competitive_intelligence,
                "brand_intelligence": intelligence.brand_intelligence
            },
            content_type=request.content_type,
            preferences=request.preferences
        )
        
        # Create generated content record
        generated_content = GeneratedContent(
            content_type=request.content_type,
            content_title=content_result.get("title", f"Generated {request.content_type}"),
            content_body=content_result.get("content", ""),
            content_metadata=content_result.get("metadata", {}),
            generation_settings=request.preferences,
            intelligence_used={
                "intelligence_id": str(intelligence.id),
                "source_url": intelligence.source_url,
                "confidence_score": intelligence.confidence_score
            },
            campaign_id=uuid.UUID(request.campaign_id),
            intelligence_source_id=intelligence.id,
            user_id=current_user.id,
            company_id=current_user.company_id
        )
        
        db.add(generated_content)
        await db.commit()
        await db.refresh(generated_content)
        
        # Create smart URL if content includes links
        smart_url = None
        if content_result.get("needs_tracking"):
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
        
        # Update intelligence usage stats
        intelligence.usage_count += 1
        await db.commit()
        
        return ContentGenerationResponse(
            content_id=str(generated_content.id),
            content_type=request.content_type,
            generated_content=content_result,
            smart_url=smart_url,
            performance_predictions=content_result.get("performance_predictions", {})
        )
        
    except Exception as e:
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
    
    # Get intelligence sources
    intelligence_result = await db.execute(
        select(CampaignIntelligence).where(
            CampaignIntelligence.campaign_id == campaign_id
        ).order_by(CampaignIntelligence.created_at.desc())
    )
    intelligence_sources = intelligence_result.scalars().all()
    
    # Get generated content
    content_result = await db.execute(
        select(GeneratedContent).where(
            GeneratedContent.campaign_id == campaign_id
        ).order_by(GeneratedContent.created_at.desc())
    )
    generated_content = content_result.scalars().all()
    
    return {
        "campaign_id": campaign_id,
        "intelligence_sources": [
            {
                "id": str(intel.id),
                "source_type": intel.source_type,
                "source_title": intel.source_title,
                "source_url": intel.source_url,
                "confidence_score": intel.confidence_score,
                "usage_count": intel.usage_count,
                "created_at": intel.created_at,
                "key_insights": len(intel.offer_intelligence.get("products", [])) + 
                              len(intel.psychology_intelligence.get("emotional_triggers", [])) +
                              len(intel.competitive_intelligence.get("opportunities", []))
            }
            for intel in intelligence_sources
        ],
        "generated_content": [
            {
                "id": str(content.id),
                "content_type": content.content_type,
                "content_title": content.content_title,
                "user_rating": content.user_rating,
                "is_published": content.is_published,
                "created_at": content.created_at
            }
            for content in generated_content
        ],
        "summary": {
            "total_intelligence_sources": len(intelligence_sources),
            "total_generated_content": len(generated_content),
            "avg_confidence_score": sum(i.confidence_score for i in intelligence_sources) / len(intelligence_sources) if intelligence_sources else 0
        }
    }

@router.get("/usage-stats")
async def get_intelligence_usage_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get intelligence usage statistics for current user's company"""
    
    # Get current month's usage
    now = datetime.utcnow()
    first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Intelligence analyses this month
    analyses_this_month = await db.scalar(
        select(func.count(CampaignIntelligence.id)).where(
            and_(
                CampaignIntelligence.company_id == current_user.company_id,
                CampaignIntelligence.created_at >= first_of_month
            )
        )
    ) or 0
    
    # Content generations this month
    generations_this_month = await db.scalar(
        select(func.count(GeneratedContent.id)).where(
            and_(
                GeneratedContent.company_id == current_user.company_id,
                GeneratedContent.created_at >= first_of_month
            )
        )
    ) or 0
    
    # Get tier limits
    tier_limits = {
        "free": {"analyses": 5, "generations": 10},
        "growth": {"analyses": 50, "generations": 100},
        "professional": {"analyses": 200, "generations": 500},
        "agency": {"analyses": -1, "generations": -1}  # Unlimited
    }
    
    user_tier = current_user.company.subscription_tier
    limits = tier_limits.get(user_tier, tier_limits["free"])
    
    return {
        "current_usage": {
            "analyses_this_month": analyses_this_month,
            "generations_this_month": generations_this_month,
            "credits_used": current_user.company.monthly_credits_used,
            "credits_limit": current_user.company.monthly_credits_limit
        },
        "tier_limits": {
            "tier": user_tier,
            "analysis_limit": limits["analyses"],
            "generation_limit": limits["generations"],
            "analyses_remaining": max(0, limits["analyses"] - analyses_this_month) if limits["analyses"] != -1 else -1,
            "generations_remaining": max(0, limits["generations"] - generations_this_month) if limits["generations"] != -1 else -1
        },
        "upgrade_suggestions": {
            "should_upgrade": (
                (limits["analyses"] != -1 and analyses_this_month >= limits["analyses"] * 0.8) or
                (limits["generations"] != -1 and generations_this_month >= limits["generations"] * 0.8)
            ),
            "next_tier": "growth" if user_tier == "free" else "professional" if user_tier == "growth" else "agency",
            "upgrade_benefits": [
                "More intelligence analyses per month",
                "Unlimited content generation",
                "Advanced psychology insights",
                "Priority processing"
            ]
        }
    }