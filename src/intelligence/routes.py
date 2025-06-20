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
import traceback

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.campaign import Campaign
from src.models.intelligence import (
    CampaignIntelligence, 
    GeneratedContent, 
    SmartURL, 
    IntelligenceSourceType,
    AnalysisStatus,
    # Enhanced request/response models
    EnhancedAnalysisRequest,
    VSLAnalysisRequest,
    CampaignAngleRequest,
    BatchAnalysisRequest,
    URLValidationRequest,
    EnhancedSalesPageIntelligence,
    VSLTranscriptionResult,
    CampaignAngleResponse,
    MultiSourceIntelligence,
    BatchAnalysisResponse,
    URLValidationResponse
)
from src.intelligence.analyzers import SalesPageAnalyzer, DocumentAnalyzer, WebAnalyzer, EnhancedSalesPageAnalyzer, VSLAnalyzer
from src.intelligence.generators import ContentGenerator, CampaignAngleGenerator
from src.core.credits import check_and_consume_credits

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])

# ============================================================================
# EXISTING ROUTES (Keep all your current routes)
# ============================================================================

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
            analysis_status=AnalysisStatus.PROCESSING
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
        intelligence.analysis_status = AnalysisStatus.COMPLETED
        
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
            intelligence.analysis_status = AnalysisStatus.FAILED
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
# ENHANCED INTELLIGENCE METHODS (NEW)
# ============================================================================

@router.post("/analyze-sales-page-enhanced", response_model=EnhancedSalesPageIntelligence)
async def analyze_sales_page_enhanced(
    request: EnhancedAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enhanced sales page analysis with comprehensive intelligence extraction"""
    
    # Check credits
    await check_and_consume_credits(
        user=current_user,
        operation="enhanced_analysis",
        credits_required=8,
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
            source_url=request.url,
            source_type=IntelligenceSourceType.SALES_PAGE,
            campaign_id=uuid.UUID(request.campaign_id),
            user_id=current_user.id,
            company_id=current_user.company_id,
            analysis_status=AnalysisStatus.PROCESSING
        )
        
        db.add(intelligence)
        await db.commit()
        await db.refresh(intelligence)
        
        # Run enhanced analysis
        analyzer = EnhancedSalesPageAnalyzer()
        analysis_result = await analyzer.analyze_enhanced(
            url=request.url,
            analysis_depth=request.analysis_depth,
            include_vsl_detection=request.include_vsl_detection,
            custom_analysis_points=request.custom_analysis_points or []
        )
        
        # Update intelligence record
        intelligence.offer_intelligence = analysis_result.get("offer_analysis", {})
        intelligence.psychology_intelligence = analysis_result.get("psychology_analysis", {})
        intelligence.content_intelligence = analysis_result.get("content_strategy", {})
        intelligence.competitive_intelligence = analysis_result.get("competitive_intelligence", {})
        intelligence.confidence_score = analysis_result.get("confidence_score", 0.85)
        intelligence.source_title = analysis_result.get("source_title", "Enhanced Analysis")
        intelligence.analysis_status = AnalysisStatus.COMPLETED
        
        await db.commit()
        
        # Return enhanced response
        return EnhancedSalesPageIntelligence(
            intelligence_id=str(intelligence.id),
            confidence_score=intelligence.confidence_score,
            source_url=request.url,
            source_title=intelligence.source_title,
            analysis_timestamp=intelligence.created_at.isoformat(),
            **analysis_result
        )
        
    except Exception as e:
        if 'intelligence' in locals():
            intelligence.analysis_status = AnalysisStatus.FAILED
            intelligence.processing_metadata = {"error": str(e)}
            await db.commit()
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced analysis failed: {str(e)}"
        )

@router.post("/vsl-analysis", response_model=VSLTranscriptionResult)
async def detect_and_analyze_vsl(
    request: VSLAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Detect and analyze Video Sales Letters"""
    
    # Check credits
    await check_and_consume_credits(
        user=current_user,
        operation="vsl_analysis",
        credits_required=10,
        db=db
    )
    
    try:
        analyzer = VSLAnalyzer()
        vsl_result = await analyzer.analyze_vsl(
            url=request.url,
            extract_transcript=request.extract_transcript,
            analyze_psychological_hooks=request.analyze_psychological_hooks
        )
        
        # Create intelligence record for VSL
        intelligence = CampaignIntelligence(
            source_url=request.url,
            source_type=IntelligenceSourceType.VIDEO,
            campaign_id=uuid.UUID(request.campaign_id),
            user_id=current_user.id,
            company_id=current_user.company_id,
            analysis_status=AnalysisStatus.COMPLETED,
            content_intelligence={"vsl_analysis": vsl_result},
            confidence_score=0.9,
            source_title="VSL Analysis"
        )
        
        db.add(intelligence)
        await db.commit()
        
        return VSLTranscriptionResult(**vsl_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"VSL analysis failed: {str(e)}"
        )

@router.post("/generate-campaign-angles", response_model=CampaignAngleResponse)
async def generate_campaign_angles(
    request: CampaignAngleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate unique campaign angles based on intelligence"""
    
    # Check credits
    await check_and_consume_credits(
        user=current_user,
        operation="campaign_angles",
        credits_required=5,
        db=db
    )
    
    try:
        # Get intelligence sources
        intelligence_sources = []
        for source_id in request.intelligence_sources:
            result = await db.execute(
                select(CampaignIntelligence).where(
                    and_(
                        CampaignIntelligence.id == source_id,
                        CampaignIntelligence.company_id == current_user.company_id
                    )
                )
            )
            source = result.scalar_one_or_none()
            if source:
                intelligence_sources.append(source)
        
        if not intelligence_sources:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid intelligence sources found"
            )
        
        # Generate campaign angles
        generator = CampaignAngleGenerator()
        angles_result = await generator.generate_angles(
            intelligence_sources=intelligence_sources,
            target_audience=request.target_audience,
            industry=request.industry,
            tone_preferences=request.tone_preferences or [],
            unique_value_props=request.unique_value_props or [],
            avoid_angles=request.avoid_angles or []
        )
        
        return CampaignAngleResponse(**angles_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Campaign angle generation failed: {str(e)}"
        )

@router.post("/consolidate/{campaign_id}", response_model=MultiSourceIntelligence)
async def consolidate_multi_source_intelligence(
    campaign_id: str,
    options: Dict[str, Any] = {},
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Consolidate intelligence from multiple sources"""
    
    # Check credits
    await check_and_consume_credits(
        user=current_user,
        operation="intelligence_consolidation",
        credits_required=7,
        db=db
    )
    
    try:
        # Get all intelligence for campaign
        intelligence_result = await db.execute(
            select(CampaignIntelligence).where(
                and_(
                    CampaignIntelligence.campaign_id == campaign_id,
                    CampaignIntelligence.company_id == current_user.company_id,
                    CampaignIntelligence.analysis_status == AnalysisStatus.COMPLETED
                )
            )
        )
        intelligence_sources = intelligence_result.scalars().all()
        
        if not intelligence_sources:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No completed intelligence sources found for this campaign"
            )
        
        # Consolidate intelligence
        from src.intelligence.analyzers import IntelligenceConsolidator
        consolidator = IntelligenceConsolidator()
        
        consolidated_result = await consolidator.consolidate_sources(
            intelligence_sources=intelligence_sources,
            weight_by_confidence=options.get("weight_by_confidence", True),
            include_conflicting_insights=options.get("include_conflicting_insights", True),
            generate_unified_strategy=options.get("generate_unified_strategy", True)
        )
        
        return MultiSourceIntelligence(**consolidated_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intelligence consolidation failed: {str(e)}"
        )

@router.post("/batch-analyze", response_model=BatchAnalysisResponse)
async def batch_analyze_competitors(
    request: BatchAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Batch analyze multiple competitor URLs"""
    
    # Check credits (more for batch operations)
    credits_required = len(request.urls) * 5
    await check_and_consume_credits(
        user=current_user,
        operation="batch_analysis",
        credits_required=credits_required,
        db=db
    )
    
    try:
        analyzer = EnhancedSalesPageAnalyzer()
        batch_results = []
        
        for url in request.urls:
            try:
                # Create intelligence record
                intelligence = CampaignIntelligence(
                    source_url=url,
                    source_type=IntelligenceSourceType.COMPETITOR_ANALYSIS,
                    campaign_id=uuid.UUID(request.campaign_id),
                    user_id=current_user.id,
                    company_id=current_user.company_id,
                    analysis_status=AnalysisStatus.PROCESSING
                )
                
                db.add(intelligence)
                await db.commit()
                await db.refresh(intelligence)
                
                # Analyze URL
                analysis_result = await analyzer.analyze_enhanced(
                    url=url,
                    analysis_depth=request.analysis_type,
                    include_vsl_detection=True
                )
                
                # Update intelligence
                intelligence.offer_intelligence = analysis_result.get("offer_analysis", {})
                intelligence.psychology_intelligence = analysis_result.get("psychology_analysis", {})
                intelligence.competitive_intelligence = analysis_result.get("competitive_intelligence", {})
                intelligence.confidence_score = analysis_result.get("confidence_score", 0.8)
                intelligence.analysis_status = AnalysisStatus.COMPLETED
                
                await db.commit()
                
                # Add to batch results
                enhanced_intelligence = EnhancedSalesPageIntelligence(
                    intelligence_id=str(intelligence.id),
                    confidence_score=intelligence.confidence_score,
                    source_url=url,
                    source_title=analysis_result.get("source_title", url),
                    analysis_timestamp=intelligence.created_at.isoformat(),
                    **analysis_result
                )
                
                batch_results.append(enhanced_intelligence)
                
            except Exception as url_error:
                print(f"Failed to analyze {url}: {url_error}")
                continue
        
        # Generate comparative analysis
        if request.compare_results and len(batch_results) > 1:
            from src.intelligence.analyzers import ComparativeAnalyzer
            comparative_analyzer = ComparativeAnalyzer()
            comparative_analysis = await comparative_analyzer.compare_analyses(batch_results)
        else:
            comparative_analysis = {
                "common_strategies": [],
                "unique_approaches": [],
                "market_gaps": [],
                "opportunity_matrix": []
            }
        
        return BatchAnalysisResponse(
            analyses=batch_results,
            comparative_analysis=comparative_analysis
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis failed: {str(e)}"
        )

@router.post("/validate-url", response_model=URLValidationResponse)
async def validate_and_pre_analyze_url(
    request: URLValidationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Smart URL validation and pre-analysis"""
    
    try:
        from src.intelligence.analyzers import URLValidator
        validator = URLValidator()
        
        validation_result = await validator.validate_url(request.url)
        
        return URLValidationResponse(**validation_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"URL validation failed: {str(e)}"
        )