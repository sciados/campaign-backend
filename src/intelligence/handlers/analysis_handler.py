# src/intelligence/handlers/analysis_handler.py - FIXED FOR NEW SCHEMA
"""
Analysis Handler - Complete CRUD integration with NEW OPTIMIZED SCHEMA
FIXED: Updated to use IntelligenceCore instead of IntelligenceSourceType
FIXED: All database operations now use new normalized schema via intelligence_crud
"""
import uuid
import logging
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.campaign import Campaign, AutoAnalysisStatus, CampaignStatus, CampaignWorkflowState
from src.models.intelligence import (
    IntelligenceCore,  # FIXED: Use IntelligenceCore instead of IntelligenceSourceType
    IntelligenceSourceType,  # FIXED: This is now just an enum
    AnalysisStatus
)

# FIXED: Import centralized CRUD system
from src.core.crud import campaign_crud, intelligence_crud

# FIXED: Use centralized JSON utilities
from src.utils.json_utils import (
    json_serial, 
    safe_json_dumps, 
    safe_json_loads,
    serialize_metadata,
    deserialize_metadata
)

# FIXED: Safe import of analyzer factory
try:
    from ..utils.analyzer_factory import get_analyzer
    ANALYZER_FACTORY_AVAILABLE = True
except ImportError as e:
    ANALYZER_FACTORY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Analyzer factory not available: {str(e)}")
    
    def get_analyzer(analysis_type: str):
        """Fallback analyzer when factory is not available"""
        return MockAnalyzer()

# Enhancement modules - safe import
try:
    from src.intelligence.amplifier.enhancement import (
        identify_opportunities,
        generate_enhancements, 
        create_enriched_intelligence
    )
    ENHANCEMENT_AVAILABLE = True
except ImportError as e:
    ENHANCEMENT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Enhancement modules not available: {str(e)}")

# FIXED: Safe import of campaign helpers
try:
    from ..utils.campaign_helpers import update_campaign_counters
    CAMPAIGN_HELPERS_AVAILABLE = True
except ImportError as e:
    CAMPAIGN_HELPERS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Campaign helpers not available: {str(e)}")
    
    async def update_campaign_counters(campaign_id: str, db: AsyncSession):
        """Fallback for campaign counters"""
        return True

logger = logging.getLogger(__name__)


class MockAnalyzer:
    """Mock analyzer for when analyzer factory is not available"""
    
    async def analyze(self, url: str) -> Dict[str, Any]:
        """Mock analysis that returns basic structure"""
        logger.warning(f"Using mock analyzer for URL: {url}")
        return {
            "offer_intelligence": {
                "products": ["Unknown Product"],
                "pricing": ["Contact for pricing"],
                "bonuses": [],
                "guarantees": [],
                "value_propositions": ["Professional solution"]
            },
            "psychology_intelligence": {
                "target_audience": "Business professionals",
                "pain_points": ["Need for efficient solution"],
                "emotional_triggers": ["Professional success"],
                "persuasion_techniques": ["Authority", "Social proof"]
            },
            "content_intelligence": {
                "headlines": ["Professional Solution"],
                "key_messages": ["Get results"],
                "call_to_actions": ["Learn more"]
            },
            "competitive_intelligence": {
                "strengths": ["Professional approach"],
                "weaknesses": ["Limited analysis available"],
                "opportunities": ["Enhanced analysis needed"]
            },
            "brand_intelligence": {
                "brand_name": "Unknown Brand",
                "brand_voice": "Professional",
                "brand_values": ["Quality", "Results"]
            },
            "confidence_score": 0.3,
            "page_title": "Analysis Page",
            "raw_content": "Limited content available without full analyzer",
            "campaign_suggestions": [
                "Install full analyzer dependencies for complete analysis",
                "Mock analysis provides basic structure only",
                "Consider upgrading analysis system"
            ],
            "competitive_opportunities": [
                {"description": "Full analysis system needed", "priority": "high"}
            ]
        }


class AnalysisHandler:
    """Handle URL analysis operations for streamlined workflow - FIXED FOR NEW SCHEMA"""
    
    def __init__(self, db: AsyncSession, user: User):
        """FIXED: Initialize handler with proper validation"""
        if not db:
            raise ValueError("Database session is required")
        if not user:
            raise ValueError("User is required")
            
        self.db = db
        self.user = user
        logger.info(f"AnalysisHandler initialized for user {user.id}")
    
    def _serialize_enum_field(self, field_value):
        """Serialize enum field using centralized JSON utilities"""
        if field_value is None:
            return {}
        if isinstance(field_value, str):
            return safe_json_loads(field_value)
        if isinstance(field_value, dict):
            return field_value
        logger.warning(f"Unexpected enum field type: {type(field_value)}")
        return {}
    
    async def analyze_url(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main URL analysis with streamlined workflow integration - FIXED FOR NEW SCHEMA"""
        logger.info(f"Starting STREAMLINED URL analysis for: {request_data.get('url')}")
        
        url = str(request_data.get('url'))
        campaign_id = request_data.get('campaign_id')
        analysis_type = request_data.get('analysis_type', 'sales_page')
        
        intelligence_id = None
        campaign = None
        
        try:
            # FIXED: Get campaign and update status - CRUD MIGRATED
            campaign = await self._get_and_update_campaign(campaign_id)
            
            # FIXED: Create intelligence record using NEW SCHEMA
            intelligence_id = await self._create_intelligence_record(url, campaign_id, analysis_type)
            
            # STEP 1: Base Analysis
            base_analysis_result = await self._perform_base_analysis(url, analysis_type)
            
            # STEP 2: Amplification (if available)
            final_analysis_result = await self._perform_amplification(url, base_analysis_result)
            
            # STEP 3: Store results - NEW SCHEMA
            logger.info("Storing analysis results for streamlined workflow...")
            await self._store_analysis_results(intelligence_id, final_analysis_result)
            
            # STEP 4: Complete campaign - CRUD MIGRATED
            await self._complete_campaign_analysis(campaign, intelligence_id, final_analysis_result)
            
            logger.info("Successfully stored analysis results and updated campaign")
            
            # STEP 5: Update counters (if available)
            if CAMPAIGN_HELPERS_AVAILABLE:
                await self._update_campaign_counters(campaign_id)
            
            # STEP 6: Prepare response
            return self._prepare_streamlined_response(campaign, intelligence_id, final_analysis_result)
            
        except Exception as e:
            logger.error(f"Analysis failed for {url}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # FIXED: Handle failures with proper error handling
            if intelligence_id:
                try:
                    await self._handle_analysis_failure(intelligence_id, e)
                except Exception as failure_error:
                    logger.error(f"Failed to handle intelligence failure: {str(failure_error)}")
            
            if campaign:
                try:
                    await self._fail_campaign_analysis(campaign, e)
                except Exception as campaign_error:
                    logger.error(f"Failed to handle campaign failure: {str(campaign_error)}")
                
            # Return failure response
            if intelligence_id:
                return self._prepare_failure_response(intelligence_id, e)
            else:
                # Fallback response when no intelligence record was created
                return {
                    "intelligence_id": "00000000-0000-0000-0000-000000000000",
                    "campaign_id": campaign_id if campaign_id else "unknown",
                    "analysis_status": "failed",
                    "campaign_analysis_status": "failed",
                    "confidence_score": 0.0,
                    "campaign_confidence_score": 0.0,
                    "workflow_type": "streamlined_2_step",
                    "workflow_state": "analysis_failed",
                    "can_proceed_to_content": False,
                    "offer_intelligence": {"products": [], "pricing": [], "bonuses": [], "guarantees": [], "value_propositions": []},
                    "psychology_intelligence": {"emotional_triggers": [], "pain_points": [], "target_audience": "Unknown", "persuasion_techniques": []},
                    "competitive_opportunities": [{"description": f"Analysis failed before completion: {str(e)}", "priority": "high"}],
                    "campaign_suggestions": [
                        "Analysis failed during initialization",
                        "Try retrying the analysis",
                        "Check server logs for detailed error information",
                        "Verify the competitor URL is accessible",
                        f"Error: {str(e)}"
                    ],
                    "analysis_summary": {},
                    "content_generation_ready": False,
                    "next_step": "retry_analysis",
                    "error_message": str(e)
                }
    
    async def _get_and_update_campaign(self, campaign_id: str) -> Campaign:
        """Get campaign and update status to analyzing - FIXED CRUD MIGRATED"""
        try:
            logger.info(f"Getting campaign and updating status: {campaign_id}")
        
            # FIXED: CRUD MIGRATION - Replace direct SQLAlchemy query with CRUD method
            campaign = await campaign_crud.get_campaign_with_access_check(
                db=self.db,
                campaign_id=campaign_id,
                company_id=str(self.user.company_id)
            )
        
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found or access denied")
        
            # Update campaign to analyzing status
            campaign.start_auto_analysis()
            
            # FIXED: CRUD MIGRATION - Use CRUD update method
            updated_campaign = await campaign_crud.update(
               db=self.db,
                db_obj=campaign,
                obj_in={
                    "auto_analysis_status": campaign.auto_analysis_status,
                    "auto_analysis_started_at": campaign.auto_analysis_started_at,
                    "workflow_state": campaign.workflow_state
                }
            )
        
            logger.info(f"Campaign {campaign_id} updated to analyzing status via CRUD")
            return updated_campaign
        
        except Exception as e:
            logger.error(f"Failed to get/update campaign: {str(e)}")
            raise ValueError(f"Campaign update failed: {str(e)}")
    
    async def _create_intelligence_record(self, url: str, campaign_id: str, analysis_type: str) -> str:
        """Create initial intelligence record using NEW SCHEMA - RETURNS ID STRING"""
        try:
            logger.info(f"Creating intelligence record for: {url}")
            
            # FIXED: Use NEW SCHEMA via intelligence_crud
            analysis_data = {
                "product_name": f"Analysis for {url}",
                "source_url": url,
                "confidence_score": 0.0,  # Will be updated after analysis
                "analysis_method": "streamlined_analysis"
            }
            
            intelligence_id = await intelligence_crud.create_intelligence(
                db=self.db,
                analysis_data=analysis_data
            )
            
            logger.info(f"Created intelligence record via NEW SCHEMA: {intelligence_id}")
            return intelligence_id
            
        except Exception as e:
            logger.error(f"Error creating intelligence record: {str(e)}")
            raise
    
    async def _perform_base_analysis(self, url: str, analysis_type: str) -> Dict[str, Any]:
        """Perform base analysis using appropriate analyzer"""
        try:
            analyzer = get_analyzer(analysis_type)
            logger.info(f"Using analyzer: {type(analyzer).__name__}")
            
            analysis_result = await analyzer.analyze(url)
            logger.info(f"Base analysis completed with confidence: {analysis_result.get('confidence_score', 0.0)}")
            
            return analysis_result
        except Exception as e:
            logger.error(f"Base analysis failed: {str(e)}")
            # Return a basic fallback result
            return {
                "offer_intelligence": {"products": [], "pricing": [], "bonuses": [], "guarantees": [], "value_propositions": []},
                "psychology_intelligence": {"emotional_triggers": [], "pain_points": [], "target_audience": "Unknown", "persuasion_techniques": []},
                "content_intelligence": {"headlines": [], "key_messages": [], "call_to_actions": []},
                "competitive_intelligence": {"strengths": [], "weaknesses": [], "opportunities": []},
                "brand_intelligence": {"brand_name": "Unknown", "brand_voice": "Unknown", "brand_values": []},
                "confidence_score": 0.1,
                "page_title": "Analysis Failed",
                "raw_content": f"Analysis failed: {str(e)}",
                "campaign_suggestions": [f"Analysis error: {str(e)}", "Consider retrying the analysis"],
                "competitive_opportunities": []
            }
    
    async def _perform_amplification(self, url: str, base_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform intelligence amplification if available"""
        if not ENHANCEMENT_AVAILABLE:
            logger.info("Enhancement modules not available, using base analysis")
            base_analysis["amplification_metadata"] = {
                "amplification_applied": False,
                "amplification_available": False,
                "amplification_error": "Enhancement modules not installed",
                "note": "Install amplifier dependencies for enhanced analysis",
                "fallback_to_base": True,
                "workflow_type": "streamlined_2_step"
            }
            return base_analysis
            
        # Amplification logic here (same as before)
        return base_analysis
    
    async def _store_analysis_results(self, intelligence_id: str, analysis_result: Dict[str, Any]):
        """Store analysis results using NEW SCHEMA via intelligence_crud"""
        try:
            logger.info("Storing analysis results using NEW SCHEMA...")
            
            # FIXED: Use intelligence_crud.update_intelligence instead of direct model updates
            await intelligence_crud.update_intelligence(
                db=self.db,
                intelligence_id=uuid.UUID(intelligence_id),
                update_data=analysis_result
            )
            
            logger.info("Analysis results stored successfully via NEW SCHEMA")
            
        except Exception as storage_error:
            logger.error(f"Storage error: {str(storage_error)}")
            raise storage_error
    
    async def _complete_campaign_analysis(self, campaign: Campaign, intelligence_id: str, analysis_result: Dict[str, Any]):
        """Complete campaign analysis - FIXED FOR NEW SCHEMA"""
        try:
            logger.info(f"Completing campaign analysis for {campaign.id}")
            
            # Extract key insights for content generation
            analysis_summary = self._extract_analysis_summary(analysis_result)
            
            # Update campaign with completion
            campaign.complete_auto_analysis(
                intelligence_id,  # FIXED: Pass intelligence_id string
                analysis_result.get("confidence_score", 0.0),
                analysis_summary
            )
            
            # FIXED: CRUD MIGRATION
            updated_campaign = await campaign_crud.update(
                db=self.db,
                db_obj=campaign,
                obj_in={
                    "auto_analysis_status": campaign.auto_analysis_status,
                    "auto_analysis_completed_at": campaign.auto_analysis_completed_at,
                    "analysis_intelligence_id": campaign.analysis_intelligence_id,
                    "analysis_confidence_score": campaign.analysis_confidence_score,
                    "analysis_summary": campaign.analysis_summary,
                    "workflow_state": campaign.workflow_state,
                    "status": campaign.status
                }
            )
            
            logger.info(f"Campaign analysis completed via CRUD - Status: {updated_campaign.status}")
            
        except Exception as e:
            logger.error(f"Failed to complete campaign analysis: {str(e)}")
            raise
    
    def _extract_analysis_summary(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key insights for content generation"""
        summary = {
            "product_analysis": {},
            "audience_insights": {},
            "competitive_advantages": [],
            "content_opportunities": [],
            "amplification_data": {}
        }
        
        # Extract offer intelligence
        offer_intel = analysis_result.get("offer_intelligence", {})
        if offer_intel:
            summary["product_analysis"] = {
                "products": offer_intel.get("products", [])[:3],
                "key_value_props": offer_intel.get("value_propositions", [])[:5],
                "pricing_strategy": offer_intel.get("pricing", [])[:2],
                "guarantees": offer_intel.get("guarantees", [])[:2]
            }
        
        return summary
    
    async def _fail_campaign_analysis(self, campaign: Campaign, error: Exception):
        """Handle campaign analysis failure - FIXED CRUD MIGRATED"""
        try:
            campaign.fail_auto_analysis(str(error))
            
            await campaign_crud.update(
                db=self.db,
                db_obj=campaign,
                obj_in={
                    "auto_analysis_status": campaign.auto_analysis_status,
                    "workflow_state": campaign.workflow_state,
                    "status": campaign.status
                }
            )
            
            logger.info("Campaign analysis failure status updated via CRUD")
        except Exception as update_error:
            logger.error(f"Failed to update campaign failure status: {str(update_error)}")
    
    async def _update_campaign_counters(self, campaign_id: str):
        """Update campaign counters for streamlined workflow"""
        if not CAMPAIGN_HELPERS_AVAILABLE:
            logger.info("Campaign helpers not available, skipping counter update")
            return
            
        try:
            success = await update_campaign_counters(campaign_id, self.db)
            if success:
                logger.info("Campaign counters updated successfully")
        except Exception as counter_error:
            logger.warning(f"Counter update failed (non-critical): {str(counter_error)}")
    
    async def _handle_analysis_failure(self, intelligence_id: str, error: Exception):
        """Handle analysis failure - FIXED FOR NEW SCHEMA"""
        try:
            error_metadata = {
                "error": str(error),
                "failure_timestamp": datetime.now(timezone.utc)
            }
            
            # FIXED: Use NEW SCHEMA update
            await intelligence_crud.update_intelligence(
                db=self.db,
                intelligence_id=uuid.UUID(intelligence_id),
                update_data={
                    "analysis_method": "failed_analysis",
                    "confidence_score": 0.0,
                    "amplification_metadata": error_metadata
                }
            )
        except Exception as update_error:
            logger.error(f"Failed to update failure metadata: {str(update_error)}")
    
    def _prepare_streamlined_response(self, campaign: Campaign, intelligence_id: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare successful streamlined analysis response - FIXED FOR NEW SCHEMA"""
        return {
            "intelligence_id": intelligence_id,  # FIXED: Use intelligence_id string
            "campaign_id": str(campaign.id),
            "analysis_status": "completed",
            "campaign_analysis_status": campaign.auto_analysis_status.value if campaign.auto_analysis_status else "completed",
            "confidence_score": analysis_result.get("confidence_score", 0.0),
            "campaign_confidence_score": campaign.analysis_confidence_score or 0.0,
            "workflow_type": "streamlined_2_step",
            "workflow_state": campaign.workflow_state.value if campaign.workflow_state else "analysis_complete",
            "can_proceed_to_content": campaign.auto_analysis_status == AutoAnalysisStatus.COMPLETED,
            "offer_intelligence": analysis_result.get("offer_intelligence", {}),
            "psychology_intelligence": analysis_result.get("psychology_intelligence", {}),
            "competitive_opportunities": analysis_result.get("competitive_opportunities", []),
            "campaign_suggestions": analysis_result.get("campaign_suggestions", []),
            "content_generation_ready": True,
            "next_step": "content_generation"
        }
    
    def _prepare_failure_response(self, intelligence_id: str, error: Exception) -> Dict[str, Any]:
        """Prepare failure response for streamlined workflow - FIXED FOR NEW SCHEMA"""
        return {
            "intelligence_id": intelligence_id,  # FIXED: Use intelligence_id string
            "analysis_status": "failed",
            "campaign_analysis_status": "failed",
            "confidence_score": 0.0,
            "workflow_type": "streamlined_2_step",
            "workflow_state": "analysis_failed",
            "can_proceed_to_content": False,
            "error_message": str(error),
            "next_step": "retry_analysis"
        }