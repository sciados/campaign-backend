# src/intelligence/routers/enhanced_intelligence_routes.py
"""
Enhanced Intelligence Routes - Missing API endpoints for workflow integration
Fills Gap 1: Intelligence Storage and Auto-Enhancement API
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timezone

from src.core.database import get_async_db
from src.models.user import User
from src.core.crud.intelligence_crud import intelligence_crud, AnalysisStatus, IntelligenceSourceType
from src.models.campaign import Campaign, AutoAnalysisStatus
from src.auth.dependencies import get_current_user
from src.intelligence.handlers.intelligence_handler import IntelligenceHandler
from src.core.crud import intelligence_crud, campaign_crud
from src.utils.json_utils import safe_json_dumps, safe_json_loads

# Import analyzers for analysis
from src.intelligence.analyzers import SalesPageAnalyzer, EnhancedSalesPageAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Enhanced Intelligence"])


@router.post("/campaigns/{campaign_id}/analyze-and-store")
async def analyze_and_store_intelligence(
    campaign_id: str,
    analysis_request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    MISSING ENDPOINT: Analyze URL, store intelligence, and trigger auto-enhancement
    This fills the gap between Step 2 (analysis) and Steps 3-4 (enhancement + storage)
    """
    try:
        logger.info(f"Starting analyze-and-store for campaign {campaign_id}")
        
        # Verify campaign access
        campaign = await campaign_crud.get_campaign_with_access_check(
            db=db,
            campaign_id=campaign_id,
            company_id=str(current_user.company_id)
        )
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found or access denied")
        
        # Extract analysis parameters
        salespage_url = analysis_request.get("salespage_url")
        product_name = analysis_request.get("product_name", campaign.product_name or "Product")
        auto_enhance = analysis_request.get("auto_enhance", True)
        
        if not salespage_url:
            raise HTTPException(status_code=400, detail="salespage_url is required")
        
        # Update campaign status to analyzing
        campaign.start_auto_analysis()
        await campaign_crud.update(db=db, id=campaign.id, obj_in={
            "auto_analysis_status": campaign.auto_analysis_status,
            "auto_analysis_started_at": campaign.auto_analysis_started_at,
            "status": campaign.status,
            "workflow_state": campaign.workflow_state,
            "step_states": campaign.step_states
        })
        
        # Step 1: Perform analysis using existing analyzer
        analyzer = EnhancedSalesPageAnalyzer()
        analysis_result = await analyzer.analyze(salespage_url)
        
        logger.info(f"Analysis completed with confidence: {analysis_result.get('confidence_score', 0)}")
        
        # Step 2: Create intelligence record in database
        intelligence_data = {
            "campaign_id": campaign_id,
            "user_id": str(current_user.id),
            "company_id": str(current_user.company_id),
            "source_url": salespage_url,
            "source_type": IntelligenceSourceType.SALES_PAGE,
            "source_title": analysis_result.get("page_title", f"{product_name} Analysis"),
            "analysis_status": AnalysisStatus.COMPLETED,
            "confidence_score": analysis_result.get("confidence_score", 0.0),
            "raw_content": analysis_result.get("raw_content", ""),
            
            # Core intelligence data
            "offer_intelligence": safe_json_dumps(analysis_result.get("offer_intelligence", {})),
            "psychology_intelligence": safe_json_dumps(analysis_result.get("psychology_intelligence", {})),
            "content_intelligence": safe_json_dumps(analysis_result.get("content_intelligence", {})),
            "competitive_intelligence": safe_json_dumps(analysis_result.get("competitive_intelligence", {})),
            "brand_intelligence": safe_json_dumps(analysis_result.get("brand_intelligence", {})),
            
            # Processing metadata
            "processing_metadata": safe_json_dumps({
                "analysis_method": analysis_result.get("analysis_method", "standard"),
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
                "product_name_extracted": analysis_result.get("product_name", product_name),
                "auto_enhancement_requested": auto_enhance,
                "workflow_integration": True
            })
        }
        
        # Create intelligence record
        intelligence_record = await intelligence_crud.create(db=db, obj_in=intelligence_data)
        
        logger.info(f"Intelligence record created: {intelligence_record.id}")
        
        # Step 3: Update campaign with intelligence reference
        analysis_summary = {
            "intelligence_id": str(intelligence_record.id),
            "confidence_score": intelligence_record.confidence_score,
            "product_name": product_name,
            "key_insights": {
                "offers_identified": len(analysis_result.get("offer_intelligence", {}).get("products", [])),
                "psychology_triggers": len(analysis_result.get("psychology_intelligence", {}).get("emotional_triggers", [])),
                "competitive_opportunities": len(analysis_result.get("competitive_intelligence", {}).get("opportunities", []))
            },
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Complete campaign analysis
        campaign.complete_auto_analysis(
            intelligence_id=str(intelligence_record.id),
            confidence_score=intelligence_record.confidence_score,
            analysis_summary=analysis_summary
        )
        
        await campaign_crud.update(db=db, id=campaign.id, obj_in={
            "auto_analysis_status": campaign.auto_analysis_status,
            "auto_analysis_completed_at": campaign.auto_analysis_completed_at,
            "analysis_intelligence_id": campaign.analysis_intelligence_id,
            "analysis_confidence_score": campaign.analysis_confidence_score,
            "analysis_summary": campaign.analysis_summary,
            "status": campaign.status,
            "workflow_state": campaign.workflow_state,
            "step_states": campaign.step_states,
            "completed_steps": campaign.completed_steps,
            "sources_count": campaign.sources_count,
            "sources_processed": campaign.sources_processed,
            "intelligence_extracted": campaign.intelligence_extracted,
            "intelligence_count": campaign.intelligence_count
        })
        
        # Step 4: Schedule auto-enhancement if requested
        if auto_enhance:
            background_tasks.add_task(
                auto_enhance_intelligence_background,
                campaign_id,
                str(intelligence_record.id),
                str(current_user.id),
                db
            )
            
            logger.info(f"Auto-enhancement scheduled for intelligence {intelligence_record.id}")
        
        return {
            "success": True,
            "intelligence_id": str(intelligence_record.id),
            "campaign_id": campaign_id,
            "confidence_score": intelligence_record.confidence_score,
            "analysis_method": analysis_result.get("analysis_method", "standard"),
            "auto_enhancement_scheduled": auto_enhance,
            "workflow_state": campaign.workflow_state.value,
            "ready_for_content_generation": True,
            "analysis_summary": analysis_summary
        }
        
    except Exception as e:
        logger.error(f"Analyze-and-store failed for campaign {campaign_id}: {str(e)}")
        
        # Update campaign with error
        try:
            campaign = await campaign_crud.get(db=db, id=campaign_id)
            if campaign:
                campaign.fail_auto_analysis(str(e))
                await campaign_crud.update(db=db, id=campaign.id, obj_in={
                    "auto_analysis_status": campaign.auto_analysis_status,
                    "auto_analysis_error": campaign.auto_analysis_error,
                    "status": campaign.status,
                    "step_states": campaign.step_states
                })
        except Exception as update_error:
            logger.error(f"Failed to update campaign error state: {update_error}")
        
        raise HTTPException(status_code=500, detail=f"Analysis and storage failed: {str(e)}")



async def auto_enhance_intelligence_background(
    campaign_id: str,
    intelligence_id: str,
    user_id: str,
    db: AsyncSession
):
    """
    Background task for automatic intelligence enhancement
    This fills Gap 3: Auto-Enhancement Trigger
    """
    try:
        logger.info(f"Starting auto-enhancement for intelligence {intelligence_id}")
        
        # Get user for intelligence handler
        from src.core.crud import user_crud
        user = await user_crud.get(db=db, id=user_id)
        if not user:
            logger.error(f"User {user_id} not found for auto-enhancement")
            return
        
        # Create intelligence handler
        handler = IntelligenceHandler(db=db, user=user)
        
        # Default enhancement preferences for auto-enhancement
        enhancement_preferences = {
            "enhance_scientific_backing": True,
            "boost_credibility": True,
            "competitive_analysis": True,
            "psychological_depth": "medium",
            "content_optimization": True,
            "auto_enhancement": True,
            "enhancement_source": "workflow_integration"
        }
        
        # Perform amplification
        result = await handler.amplify_intelligence_source(
            campaign_id=campaign_id,
            intelligence_id=intelligence_id,
            preferences=enhancement_preferences
        )
        
        if result.get("amplification_applied"):
            logger.info(f"Auto-enhancement completed successfully for {intelligence_id}")
            logger.info(f"AI categories populated: {result.get('ai_categories_populated', 0)}/5")
        else:
            logger.warning(f"Auto-enhancement failed for {intelligence_id}: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"Auto-enhancement background task failed: {str(e)}")


@router.get("/campaigns/{campaign_id}/enhanced-intelligence")
async def get_enhanced_intelligence(
    campaign_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    MISSING ENDPOINT: Retrieve enhanced intelligence for content generation
    This fills Gap 2: Intelligence Retrieval for Content Generation
    """
    try:
        # Create intelligence handler
        handler = IntelligenceHandler(db=db, user=current_user)
        
        # Get campaign intelligence using existing handler method
        intelligence_data = await handler.get_campaign_intelligence(campaign_id)
        
        if not intelligence_data.get("success"):
            raise HTTPException(
                status_code=404, 
                detail=intelligence_data.get("error", "Intelligence data not found")
            )
        
        # Format for content generation
        formatted_intelligence = {
            "campaign_id": campaign_id,
            "intelligence_ready": len(intelligence_data.get("intelligence_sources", [])) > 0,
            "enhancement_applied": intelligence_data.get("statistics", {}).get("amplified_sources", 0) > 0,
            "confidence_score": intelligence_data.get("statistics", {}).get("average_confidence", 0.0),
            "intelligence_sources": intelligence_data.get("intelligence_sources", []),
            "statistics": intelligence_data.get("statistics", {}),
            "content_generation_ready": True,
            "enhancement_summary": {
                "total_sources": intelligence_data.get("statistics", {}).get("total_sources", 0),
                "enhanced_sources": intelligence_data.get("statistics", {}).get("amplified_sources", 0),
                "enhancement_rate": intelligence_data.get("statistics", {}).get("enhancement_rate", 0.0)
            }
        }
        
        return formatted_intelligence
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve enhanced intelligence for campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve enhanced intelligence: {str(e)}"
        )


@router.post("/campaigns/{campaign_id}/intelligence/{intelligence_id}/manual-enhance")
async def manual_enhance_intelligence(
    campaign_id: str,
    intelligence_id: str,
    enhancement_request: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manual intelligence enhancement endpoint (for user-triggered enhancement)
    """
    try:
        # Create intelligence handler
        handler = IntelligenceHandler(db=db, user=current_user)
        
        # Extract preferences or use defaults
        preferences = enhancement_request or {
            "enhance_scientific_backing": True,
            "boost_credibility": True,
            "competitive_analysis": True,
            "psychological_depth": "high",
            "content_optimization": True,
            "manual_enhancement": True
        }
        
        # Perform manual amplification
        result = await handler.amplify_intelligence_source(
            campaign_id=campaign_id,
            intelligence_id=intelligence_id,
            preferences=preferences
        )
        
        return {
            "success": result.get("amplification_applied", False),
            "intelligence_id": intelligence_id,
            "campaign_id": campaign_id,
            "enhancement_result": result,
            "message": result.get("message", "Enhancement completed")
        }
        
    except Exception as e:
        logger.error(f"Manual enhancement failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")


@router.get("/campaigns/{campaign_id}/workflow-status")
async def get_workflow_status(
    campaign_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive workflow status for frontend integration
    """
    try:
        # Get campaign with access check
        campaign = await campaign_crud.get_campaign_with_access_check(
            db=db,
            campaign_id=campaign_id,
            company_id=str(current_user.company_id)
        )
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get intelligence data if available
        intelligence_data = None
        if campaign.analysis_intelligence_id:
            try:
                handler = IntelligenceHandler(db=db, user=current_user)
                intelligence_response = await handler.get_campaign_intelligence(campaign_id)
                if intelligence_response.get("success"):
                    intelligence_data = intelligence_response
            except Exception as e:
                logger.warning(f"Could not load intelligence data: {e}")
        
        # Build comprehensive status
        workflow_status = {
            "campaign_id": campaign_id,
            "campaign_title": campaign.title,
            "product_name": campaign.product_name,
            "salespage_url": campaign.salespage_url,
            
            # Analysis status
            "auto_analysis_status": campaign.get_auto_analysis_status(),
            "workflow_summary": campaign.get_workflow_summary(),
            
            # Intelligence status
            "intelligence_available": intelligence_data is not None,
            "intelligence_enhanced": False,
            "intelligence_confidence": campaign.analysis_confidence_score or 0.0,
            
            # Content generation readiness
            "ready_for_content_generation": (
                campaign.auto_analysis_status == AutoAnalysisStatus.COMPLETED and
                campaign.analysis_intelligence_id is not None
            ),
            
            # Step states
            "current_step": campaign.get_workflow_summary().get("current_step", 1),
            "step_states": campaign.step_states or {},
            "completed_steps": campaign.completed_steps or [],
            
            # Enhancement data
            "enhancement_summary": {}
        }
        
        # Add intelligence enhancement details if available
        if intelligence_data and intelligence_data.get("intelligence_sources"):
            sources = intelligence_data["intelligence_sources"]
            enhanced_sources = [s for s in sources if s.get("amplification_applied", False)]
            
            workflow_status.update({
                "intelligence_enhanced": len(enhanced_sources) > 0,
                "enhancement_summary": {
                    "total_sources": len(sources),
                    "enhanced_sources": len(enhanced_sources),
                    "enhancement_rate": len(enhanced_sources) / len(sources) * 100 if sources else 0,
                    "ai_categories_available": any(
                        s.get("scientific_intelligence") or s.get("credibility_intelligence")
                        for s in sources
                    )
                }
            })
        
        return workflow_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")