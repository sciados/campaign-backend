# src/intelligence/handlers/analysis_handler.py - FIXED FOR NEW SCHEMA
"""
Analysis Handler - Complete CRUD integration with NEW OPTIMIZED SCHEMA
FIXED: Updated to use IntelligenceCore with correct field names
FIXED: All database operations now use new normalized schema via intelligence_crud
FIXED: Removed analysis_method field that doesn't exist in new schema
FIXED: Single class definition with all methods properly organized
"""
import asyncio
import time
import uuid
import logging
import traceback
# import time
# from datetime import time
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.campaign import Campaign, AutoAnalysisStatus, CampaignStatus, CampaignWorkflowState

# FIXED: Import centralized CRUD system only
from src.core.crud import campaign_crud, intelligence_crud

# FIXED: Simplified JSON utilities - only import what exists
try:
    from src.utils.json_utils import safe_json_dumps, safe_json_loads
except ImportError:
    # Fallback JSON functions
    import json
    def safe_json_dumps(data):
        return json.dumps(data, default=str)
    def safe_json_loads(data):
        return json.loads(data) if isinstance(data, str) else data

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
            
            # FIXED: Only include fields that exist in new intelligence_core schema  
            analysis_data = {
                "product_name": f"Analysis for {url}",
                "source_url": url,
                "confidence_score": 0.0  # Will be updated after analysis
                # REMOVED: "analysis_method" - field doesn't exist in new schema
            }
            
            logger.info(f"Creating intelligence with data: {analysis_data}")
            
            intelligence_id = await intelligence_crud.create_intelligence(
                db=self.db,
                analysis_data=analysis_data
            )
            
            logger.info(f"Created intelligence record via NEW SCHEMA: {intelligence_id}")
            return intelligence_id
            
        except Exception as e:
            logger.error(f"Error creating intelligence record: {str(e)}")
            logger.error(f"Analysis data that failed: {analysis_data}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise
    
    async def _perform_base_analysis(self, url: str, analysis_type: str) -> Dict[str, Any]:
        """Perform base analysis using appropriate analyzer"""
        try:
            logger.info(f"DEBUG: About to perform base analysis...")
            analyzer = get_analyzer(analysis_type)
            logger.info(f"Using analyzer: {type(analyzer).__name__}")
            
            analysis_result = await analyzer.analyze(url)
            logger.info(f"Base analysis completed with confidence: {analysis_result.get('confidence_score', 0.0)}")
            logger.info(f"DEBUG: Base analysis completed successfully")
            
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
    
    def _get_ai_providers_from_analyzer(self) -> List[Dict[str, Any]]:
        """Get AI providers for amplification"""
        try:
            from ..utils.tiered_ai_provider import get_tiered_ai_provider, ServiceTier
            provider_manager = get_tiered_ai_provider(ServiceTier.free)
            providers = provider_manager.get_available_providers()
            logger.info(f"Retrieved {len(providers)} AI providers for amplification")
            return providers
        except Exception as e:
            logger.warning(f"Could not get AI providers: {e}")
            # Return mock provider to prevent total failure
            return [{
                "name": "mock_provider",
                "available": False,
                "priority": 999,
                "cost_per_1k_tokens": 0.0,
                "quality_score": 50.0
            }]

    async def _perform_amplification(self, url: str, base_analysis: Dict[str, Any]) -> Dict[str, Any]:
        import time as time_module  # Local import
    
        logger.info("=== AMPLIFICATION DEBUG START ===")
        total_start = time_module.time()

        try:
            # Log each step with precise timing
            logger.info("STEP 1: Getting AI providers...")
            step_start = time.time()
            ai_providers = self._get_ai_providers_from_analyzer()
            logger.info(f"STEP 1 COMPLETE: {time.time() - step_start:.2f}s - Found {len(ai_providers)} providers")

            logger.info("STEP 2: Identifying opportunities...")
            step_start = time.time()
            # Use empty preferences if not defined
            preferences = {}
            opportunities = await asyncio.wait_for(
                identify_opportunities(base_intel=base_analysis, preferences=preferences, providers=ai_providers),
                timeout=60
            )
            logger.info(f"STEP 2 COMPLETE: {time.time() - step_start:.2f}s")

            logger.info("STEP 3: Generating enhancements (THIS IS WHERE TIMEOUT LIKELY OCCURS)...")
            step_start = time.time()
            enhancements = await asyncio.wait_for(
                generate_enhancements(base_intel=base_analysis, opportunities=opportunities, providers=ai_providers),
                timeout=300  # Increase timeout and log it
            )
            enhancement_time = time.time() - step_start
            logger.info(f"STEP 3 COMPLETE: {enhancement_time:.2f}s")

            # Check if we're close to timeout
            if enhancement_time > 240:
                logger.error(f"TIMEOUT WARNING: Enhancement took {enhancement_time:.2f}s - very close to timeout!")

            logger.info("STEP 4: Creating enriched intelligence...")
            step_start = time.time()
            enriched_intelligence = await asyncio.wait_for(
                create_enriched_intelligence(base_intel=base_analysis, enhancements=enhancements),
                timeout=30
            )
            logger.info(f"STEP 4 COMPLETE: {time.time() - step_start:.2f}s")

            total_time = time.time() - total_start
            logger.info(f"=== AMPLIFICATION DEBUG END: {total_time:.2f}s total ===")

            return enriched_intelligence

        except asyncio.TimeoutError as e:
            timeout_time = time.time() - total_start
            logger.error(f"TIMEOUT DEBUG: Failed after {timeout_time:.2f}s - {str(e)}")
            base_analysis["amplification_metadata"] = {
                "amplification_applied": False,
                "amplification_error": "Amplification timed out",
                "fallback_to_base": True,
                "workflow_type": "streamlined_2_step",
                "timeout": True
            }
            return base_analysis

        except Exception as amp_error:
            error_time = time.time() - total_start
            logger.error(f"Amplification failed after {error_time:.2f}s: {str(amp_error)}")
            logger.error(f"DEBUG: Amplification failed with error: {str(amp_error)}")
            base_analysis["amplification_metadata"] = {
                "amplification_applied": False,
                "amplification_error": str(amp_error),
                "fallback_to_base": True,
                "error_type": type(amp_error).__name__,
                "workflow_type": "streamlined_2_step"
            }
            return base_analysis

    async def _store_analysis_results(self, intelligence_id: str, analysis_result: Dict[str, Any]):
        logger.info("STORAGE DEBUG: Starting storage operation")
        storage_start = time.time()
    
        try:
            data_size = len(str(analysis_result))
            logger.info(f"STORAGE DEBUG: Data size to store: {data_size} characters")
        
            await intelligence_crud.update_intelligence(
                db=self.db,
                intelligence_id=uuid.UUID(intelligence_id),
                update_data=analysis_result
            )
        
            storage_time = time.time() - storage_start
            logger.info(f"STORAGE DEBUG: Completed in {storage_time:.2f}s")
        
            if storage_time > 30:
                logger.error(f"SLOW STORAGE: Database update took {storage_time:.2f}s - this is too slow!")
            
        except Exception as e:
            storage_time = time.time() - storage_start
            logger.error(f"STORAGE DEBUG: Failed after {storage_time:.2f}s - {str(e)}")
            raise
    
    async def _complete_campaign_analysis(self, campaign: Campaign, intelligence_id: str, analysis_result: Dict[str, Any]):
        """Complete campaign analysis - FIXED FOR NEW SCHEMA"""
        try:
            logger.info(f"DEBUG: About to complete campaign analysis...")
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
            logger.info(f"DEBUG: Campaign completion successful")
            
        except Exception as e:
            logger.error(f"Failed to complete campaign analysis: {str(e)}")
            logger.error(f"DEBUG: Campaign completion failed: {str(e)}")
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
            # FIXED: Only update fields that exist in new schema
            await intelligence_crud.update_intelligence(
                db=self.db,
                intelligence_id=uuid.UUID(intelligence_id),
                update_data={
                    "confidence_score": 0.0
                    # REMOVED: analysis_method and other fields that don't exist
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

    async def debug_new_schema_compatibility(self):
        """Debug method to test new schema compatibility"""
        try:
            # Test creating a simple intelligence record
            test_data = {
                "product_name": "Test Product",
                "source_url": "https://test.com",
                "confidence_score": 0.5
            }
            
            logger.info(f"Testing intelligence creation with: {test_data}")
            
            intelligence_id = await intelligence_crud.create_intelligence(
                db=self.db,
                analysis_data=test_data
            )
            
            logger.info(f"Test intelligence created: {intelligence_id}")
            
            # Test updating it
            update_data = {"confidence_score": 0.7}
            await intelligence_crud.update_intelligence(
                db=self.db,
                intelligence_id=uuid.UUID(intelligence_id),
                update_data=update_data
            )
            
            logger.info("Test intelligence updated successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Schema compatibility test failed: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False

    async def debug_storage_only(self, url: str = "https://debug-test.com"):
        """Debug method to test just storage operations"""
        import time as time_module  # Local import avoids global conflicts
    
        logger.info("=== STORAGE DEBUG TEST START ===")
    
        try:
            # Test 1: Create intelligence record
            create_start = time_module.time()
            intelligence_id = await self._create_intelligence_record(url, "debug_test", "sales_page")
            create_time = time_module.time() - create_start
            logger.info(f"STORAGE DEBUG: Create took {create_time:.2f}s - ID: {intelligence_id}")
        
            # Test 2: Minimal update
            minimal_start = time_module.time()
            minimal_data = {"confidence_score": 0.8}
            await intelligence_crud.update_intelligence(
                db=self.db,
                intelligence_id=uuid.UUID(intelligence_id),
                update_data=minimal_data
            )
            minimal_time = time_module.time() - minimal_start
            logger.info(f"STORAGE DEBUG: Minimal update took {minimal_time:.2f}s")
        
            # Test 3: Complex update
            complex_start = time_module.time()
            complex_data = {
                "confidence_score": 0.9,
                "offer_intelligence": {
                    "key_features": ["test1", "test2"],
                    "primary_benefits": ["benefit1", "benefit2"]
                },
                "competitive_intelligence": {"market_category": "test"},
                "psychology_intelligence": {"target_audience": "test audience"}
            }
            await intelligence_crud.update_intelligence(
                db=self.db,
                intelligence_id=uuid.UUID(intelligence_id),
                update_data=complex_data
            )
            complex_time = time_module.time() - complex_start
            logger.info(f"STORAGE DEBUG: Complex update took {complex_time:.2f}s")
        
            total_time = create_time + minimal_time + complex_time
            logger.info(f"=== STORAGE DEBUG COMPLETE: {total_time:.2f}s total ===")
        
            return {
                "status": "success",
                "create_time": create_time,
                "minimal_update_time": minimal_time,
                "complex_update_time": complex_time,
                "total_time": total_time,
                "intelligence_id": intelligence_id
            }
        
        except Exception as e:
            logger.error(f"STORAGE DEBUG FAILED: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {"status": "failed", "error": str(e)}