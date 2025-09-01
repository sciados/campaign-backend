# src/intelligence/handlers/analysis_handler.py
"""
Analysis Handler - Complete CRUD integration with zero ChunkedIteratorResult risk
FIXED: All database operations now use centralized CRUD system
FIXED: Direct SQLAlchemy queries replaced with CRUD methods
FIXED: Manual session management replaced with CRUD patterns
FIXED: ChunkedIteratorResult elimination across all methods
FIXED: Proper async/sync handling for auth compatibility
FIXED: Syntax errors and orphaned code blocks removed
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
    CampaignIntelligence,
    IntelligenceSourceType,
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


def diagnose_amplification_output(enhanced_analysis: Dict[str, Any]):
    """Diagnostic function to understand amplification output"""
    logger.info("AMPLIFICATION OUTPUT DIAGNOSIS")
    logger.info("=" * 50)
    
    # Check top-level structure
    logger.info(f"Top-level keys: {list(enhanced_analysis.keys())}")
    
    # Look for AI intelligence data
    ai_keys = [
        'scientific_intelligence', 'credibility_intelligence', 'market_intelligence', 
        'emotional_transformation_intelligence', 'scientific_authority_intelligence'
    ]
    
    logger.info("AI Intelligence Categories:")
    for key in ai_keys:
        if key in enhanced_analysis:
            data = enhanced_analysis[key]
            logger.info(f"  {key}: {type(data)} - {len(data) if isinstance(data, dict) else 'Not a dict'}")
            if isinstance(data, dict) and data:
                sample_key = list(data.keys())[0]
                sample_value = data[sample_key]
                logger.info(f"     Sample: {sample_key} = {str(sample_value)[:80]}...")
        else:
            logger.info(f"  {key}: MISSING")
    
    # Check amplification metadata
    if 'amplification_metadata' in enhanced_analysis:
        amp_meta = enhanced_analysis['amplification_metadata']
        logger.info(f"Amplification Metadata:")
        logger.info(f"  Applied: {amp_meta.get('amplification_applied', 'Unknown')}")
        logger.info(f"  Total enhancements: {amp_meta.get('total_enhancements', 'Unknown')}")
        logger.info(f"  Confidence boost: {amp_meta.get('confidence_boost', 'Unknown')}")
    
    logger.info("=" * 50)


class AnalysisHandler:
    """Handle URL analysis operations for streamlined workflow - FIXED CRUD MIGRATED"""
    
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
        """Main URL analysis with streamlined workflow integration - FIXED CRUD MIGRATED"""
        logger.info(f"Starting STREAMLINED URL analysis for: {request_data.get('url')}")
        
        url = str(request_data.get('url'))
        campaign_id = request_data.get('campaign_id')
        analysis_type = request_data.get('analysis_type', 'sales_page')
        
        intelligence = None
        campaign = None
        
        try:
            # FIXED: Get campaign and update status - CRUD MIGRATED
            campaign = await self._get_and_update_campaign(campaign_id)
            
            # FIXED: Create intelligence record - CRUD MIGRATED
            intelligence = await self._create_intelligence_record(url, campaign_id, analysis_type)
            
            # STEP 1: Base Analysis
            base_analysis_result = await self._perform_base_analysis(url, analysis_type)
            
            # STEP 2: Amplification (if available)
            final_analysis_result = await self._perform_amplification(url, base_analysis_result)
            
            # STEP 3: Store results - CRUD MIGRATED
            logger.info("Storing analysis results for streamlined workflow...")
            await self._store_analysis_results(intelligence, final_analysis_result)
            
            # STEP 4: Complete campaign - CRUD MIGRATED
            await self._complete_campaign_analysis(campaign, intelligence, final_analysis_result)
            
            logger.info("Successfully stored analysis results and updated campaign")
            
            # STEP 5: Update counters (if available)
            if CAMPAIGN_HELPERS_AVAILABLE:
                await self._update_campaign_counters(campaign_id)
            
            # STEP 6: Prepare response
            return self._prepare_streamlined_response(campaign, intelligence, final_analysis_result)
            
        except Exception as e:
            logger.error(f"Analysis failed for {url}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # FIXED: Handle failures with proper error handling
            if intelligence:
                try:
                    await self._handle_analysis_failure(intelligence, e)
                except Exception as failure_error:
                    logger.error(f"Failed to handle intelligence failure: {str(failure_error)}")
            
            if campaign:
                try:
                    await self._fail_campaign_analysis(campaign, e)
                except Exception as campaign_error:
                    logger.error(f"Failed to handle campaign failure: {str(campaign_error)}")
                
            # Return failure response
            if intelligence:
                return self._prepare_failure_response(intelligence, e)
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
                    "amplification_metadata": {
                        "amplification_applied": False,
                        "amplification_error": "Analysis failed before amplification",
                        "workflow_type": "streamlined_2_step"
                    },
                    "analysis_summary": {},
                    "content_generation_ready": False,
                    "next_step": "retry_analysis",
                    "error_message": str(e),
                    "step_progress": {
                        "step_1": 0,
                        "step_2": 0
                    }
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
        
            # DEBUG: Check campaign status before updating
            logger.info(f"Campaign current status: {campaign.auto_analysis_status}")
            
            # Check if analysis is already in progress or completed
            if hasattr(campaign, 'auto_analysis_status') and campaign.auto_analysis_status:
                if campaign.auto_analysis_status.value in ['in_progress', 'completed']:
                    logger.warning(f"Campaign {campaign_id} analysis already {campaign.auto_analysis_status.value}")
                    if campaign.auto_analysis_status.value == 'completed':
                        raise ValueError(f"Campaign {campaign_id} analysis already completed")
                    elif campaign.auto_analysis_status.value == 'in_progress':
                        raise ValueError(f"Campaign {campaign_id} analysis already in progress")
            
            # Update campaign to analyzing status
            campaign.start_auto_analysis()  # This is synchronous - no await
            
            # FIXED: CRUD MIGRATION - Use CRUD update method instead of direct db.commit()
            updated_campaign = await campaign_crud.update(
               db=self.db,
                db_obj=campaign,  # Pass the object instance
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
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception args: {e.args}")
            raise ValueError(f"Campaign update failed: {str(e)}")
    
    async def _create_intelligence_record(self, url: str, campaign_id: str, analysis_type: str) -> CampaignIntelligence:
        """Create initial intelligence record - FIXED CRUD MIGRATED"""
        try:
            logger.info(f"Creating intelligence record for: {url}")
            
            # FIXED: CRUD MIGRATION - Use intelligence_crud.create instead of direct model creation
            intelligence_data = {
                "source_url": url,
                "source_type": IntelligenceSourceType.SALES_PAGE,
                "campaign_id": uuid.UUID(campaign_id),
                "user_id": self.user.id,
                "company_id": self.user.company_id,
                "analysis_status": AnalysisStatus.PROCESSING
            }
            
            intelligence = await intelligence_crud.create(
                db=self.db,
                obj_in=intelligence_data
            )
            
            logger.info(f"Created intelligence record via CRUD: {intelligence.id}")
            return intelligence
            
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
            
        try:
            logger.info("Starting intelligence amplification for streamlined workflow...")
            
            # Get AI providers
            ai_providers = self._get_ai_providers_from_analyzer()
            provider_names = [p.get('name', 'unknown') for p in ai_providers]
            logger.info(f"AMPLIFICATION using providers: {provider_names}")
            
            # Set up preferences
            preferences = {
                "enhance_scientific_backing": True,
                "boost_credibility": True,
                "competitive_analysis": True,
                "psychological_depth": "medium",
                "content_optimization": True,
                "cost_optimization": True,
                "preferred_provider": provider_names[0] if provider_names else "groq"
            }
            
            # STEP 1: Identify opportunities
            logger.info("Identifying enhancement opportunities...")
            opportunities = await identify_opportunities(
                base_intel=base_analysis,
                preferences=preferences,
                providers=ai_providers
            )
            
            opportunities_count = opportunities.get("opportunity_metadata", {}).get("total_opportunities", 0)
            logger.info(f"Identified {opportunities_count} enhancement opportunities")
            
            # STEP 2: Generate enhancements
            logger.info("Generating AI-powered enhancements...")
            enhancements = await generate_enhancements(
                base_intel=base_analysis,
                opportunities=opportunities,
                providers=ai_providers
            )
            
            enhancement_metadata = enhancements.get("enhancement_metadata", {})
            total_enhancements = enhancement_metadata.get("total_enhancements", 0)
            confidence_boost = enhancement_metadata.get("confidence_boost", 0.0)
            
            logger.info(f"Generated {total_enhancements} enhancements with {confidence_boost:.1%} confidence boost")
            
            # STEP 3: Create enriched intelligence
            logger.info("Creating enriched intelligence...")
            enriched_intelligence = create_enriched_intelligence(
                base_intel=base_analysis,
                enhancements=enhancements
            )
            
            # Diagnose the amplification output
            diagnose_amplification_output(enriched_intelligence)
            
            # Add amplification metadata
            try:
                from src.intelligence.utils.tiered_ai_provider import get_cost_summary
                cost_summary = get_cost_summary()
            except:
                cost_summary = {"error": "Cost tracking not available"}
            
            enriched_intelligence["amplification_metadata"] = {
                "amplification_applied": True,
                "amplification_method": "streamlined_workflow_enhancement",
                "opportunities_identified": opportunities_count,
                "total_enhancements": total_enhancements,
                "confidence_boost": confidence_boost,
                "base_confidence": base_analysis.get("confidence_score", 0.0),
                "amplified_confidence": enriched_intelligence.get("confidence_score", 0.0),
                "credibility_score": enhancement_metadata.get("credibility_score", 0.0),
                "enhancement_quality": enhancement_metadata.get("enhancement_quality", "unknown"),
                "modules_successful": enhancement_metadata.get("modules_successful", []),
                "scientific_enhancements": len(enhancements.get("scientific_validation", {})) if enhancements.get("scientific_validation") else 0,
                "system_architecture": "streamlined_modular_enhancement",
                "amplification_timestamp": datetime.now(timezone.utc),
                "ultra_cheap_optimization_applied": True,
                "primary_provider_used": provider_names[0] if provider_names else "unknown",
                "provider_priority": provider_names,
                "cost_tracking": cost_summary,
                "estimated_cost_savings": cost_summary.get("estimated_savings", 0.0),
                "cost_savings_percentage": cost_summary.get("savings_percentage", 0.0),
                "workflow_type": "streamlined_2_step"
            }
            
            logger.info(f"Streamlined amplification completed - Final confidence: {enriched_intelligence.get('confidence_score', 0.0):.2f}")
            return enriched_intelligence
            
        except Exception as amp_error:
            logger.warning(f"Amplification failed, using base analysis: {str(amp_error)}")
            base_analysis["amplification_metadata"] = {
                "amplification_applied": False,
                "amplification_error": str(amp_error),
                "fallback_to_base": True,
                "error_type": type(amp_error).__name__,
                "workflow_type": "streamlined_2_step"
            }
            return base_analysis
    
    def _get_ai_providers_from_analyzer(self) -> List[Dict[str, Any]]:
        """Get AI providers using tiered system or fallback"""
        try:
            from src.intelligence.utils.tiered_ai_provider import get_tiered_ai_provider, ServiceTier
            
            tiered_manager = get_tiered_ai_provider(ServiceTier.free)
            providers = tiered_manager.get_available_providers(ServiceTier.free)
            
            if providers:
                primary_provider = providers[0]
                provider_name = primary_provider.get('name', 'unknown')
                cost_per_1k = primary_provider.get('cost_per_1k_tokens', 0)
                
                logger.info(f"STREAMLINED AI: Primary provider: {provider_name}, Cost: ${cost_per_1k:.5f}/1K tokens")
                return providers
            else:
                logger.warning("No providers available")
                return self._create_emergency_fallback_providers()
                
        except ImportError as e:
            logger.error(f"Tiered AI provider system not available: {str(e)}")
            return self._create_emergency_fallback_providers()
        except Exception as e:
            logger.error(f"Failed to get tiered AI providers: {str(e)}")
            return self._create_emergency_fallback_providers()
    
    def _create_emergency_fallback_providers(self) -> List[Dict[str, Any]]:
        """Emergency fallback if tiered system fails"""
        import os
        providers = []
        
        logger.warning("Using emergency fallback providers")
        
        emergency_configs = [
            {
                "name": "groq",
                "api_key_env": "GROQ_API_KEY",
                "cost_per_1k_tokens": 0.0002,
                "quality_score": 78,
                "priority": 1
            },
            {
                "name": "together", 
                "api_key_env": "TOGETHER_API_KEY",
                "cost_per_1k_tokens": 0.0008,
                "quality_score": 82,
                "priority": 2
            }
        ]
        
        for config in emergency_configs:
            api_key = os.getenv(config["api_key_env"])
            if api_key:
                try:
                    if config["name"] == "groq":
                        import groq
                        client = groq.AsyncGroq(api_key=api_key)
                    elif config["name"] == "together":
                        import openai
                        client = openai.AsyncOpenAI(
                            api_key=api_key,
                            base_url="https://api.together.xyz/v1"
                        )
                    
                    providers.append({
                        "name": config["name"],
                        "available": True,
                        "client": client,
                        "priority": config["priority"],
                        "cost_per_1k_tokens": config["cost_per_1k_tokens"],
                        "quality_score": config["quality_score"],
                        "provider_tier": "emergency_streamlined"
                    })
                    
                    logger.info(f"Emergency provider: {config['name']} initialized")
                    
                except Exception as e:
                    logger.error(f"Emergency provider failed for {config['name']}: {str(e)}")
        
        if providers:
            providers.sort(key=lambda x: x["priority"])
            logger.info(f"Emergency providers: {[p['name'] for p in providers]}")
        
        return providers
    
    async def _store_analysis_results(self, intelligence: CampaignIntelligence, analysis_result: Dict[str, Any]):
        """Store analysis results using centralized JSON utilities - FIXED CRUD MIGRATED"""
        try:
            enhanced_analysis = analysis_result
            
            # Store base intelligence sections using centralized utilities
            offer_intel = self._validate_intelligence_section(enhanced_analysis.get("offer_intelligence", {}))
            psychology_intel = self._validate_intelligence_section(enhanced_analysis.get("psychology_intelligence", {}))
            content_intel = self._validate_intelligence_section(enhanced_analysis.get("content_intelligence", {}))
            competitive_intel = self._validate_intelligence_section(enhanced_analysis.get("competitive_intelligence", {}))
            brand_intel = self._validate_intelligence_section(enhanced_analysis.get("brand_intelligence", {}))
            
            logger.info("Base intelligence prepared for streamlined storage")
            
            # Store AI data using fallback method
            ai_intelligence_data = await self._prepare_ai_intelligence_data(enhanced_analysis)
            
            # Store metadata and finalize
            confidence_score = enhanced_analysis.get("confidence_score", 0.0)
            
            # FIXED: Always use campaign product name as primary source
            source_title = await self._get_campaign_product_name(intelligence.campaign_id, enhanced_analysis)
            
            # FIXED: Also update the analysis results to use correct product name
            enhanced_analysis = self._fix_product_names_in_analysis(enhanced_analysis, source_title)
            
            raw_content = enhanced_analysis.get("raw_content", "")[:10000]
            
            processing_metadata = enhanced_analysis.get("amplification_metadata", {})
            processing_metadata.update({
                "storage_method": "streamlined_workflow_storage",
                "analysis_timestamp": datetime.now(timezone.utc),
                "commit_applied": True,
                "workflow_type": "streamlined_2_step",
                "storage_version": "streamlined_2024",
                "product_name_source": "campaign_user_input"
            })
            
            # FIXED: CRUD MIGRATION - Use intelligence_crud.update instead of direct db operations
            update_data = {
                "offer_intelligence": safe_json_dumps(offer_intel),
                "psychology_intelligence": safe_json_dumps(psychology_intel),
                "content_intelligence": safe_json_dumps(content_intel),
                "competitive_intelligence": safe_json_dumps(competitive_intel),
                "brand_intelligence": safe_json_dumps(brand_intel),
                "confidence_score": confidence_score,
                "source_title": source_title,
                "raw_content": raw_content,
                "processing_metadata": serialize_metadata(processing_metadata),
                "analysis_status": AnalysisStatus.COMPLETED
            }
            
            # Add AI intelligence data
            update_data.update(ai_intelligence_data)
            
            updated_intelligence = await intelligence_crud.update(
                db=self.db,
                # id=intelligence.id,
                db_obj=intelligence,
                obj_in=update_data
            )
            
            logger.info("All streamlined analysis results stored successfully via CRUD")
            
        except Exception as storage_error:
            logger.error(f"Streamlined storage error: {str(storage_error)}")
            
            error_metadata = {
                "storage_error": str(storage_error),
                "error_type": type(storage_error).__name__,
                "workflow_type": "streamlined_2_step",
                "storage_fix_attempted": True,
                "failure_timestamp": datetime.now(timezone.utc)
            }
            
            # FIXED: CRUD MIGRATION - Use CRUD update for error handling
            try:
                await intelligence_crud.update(
                    db=self.db,
                    # id=intelligence.id,
                    db_obj=intelligence,
                    obj_in={
                        "analysis_status": AnalysisStatus.FAILED,
                        "processing_metadata": serialize_metadata(error_metadata)
                    }
                )
            except Exception as update_error:
                logger.error(f"Failed to update error metadata via CRUD: {str(update_error)}")
                
            raise storage_error

    async def _get_campaign_product_name(self, campaign_id: uuid.UUID, enhanced_analysis: Dict[str, Any]) -> str:
        """Get campaign product name using CRUD - FIXED"""
        try:
            # FIXED: CRUD MIGRATION - Use campaign_crud instead of direct query
            campaign = await campaign_crud.get(db=self.db, id=campaign_id)
            
            if campaign and hasattr(campaign, 'product_name') and campaign.product_name:
                # PRIORITY 1: Use the user-provided product name from campaign setup
                logger.info(f"Using campaign product name: '{campaign.product_name}'")
                return campaign.product_name.strip()
                
            elif campaign and hasattr(campaign, 'title') and campaign.title:
                # PRIORITY 2: Use campaign title as fallback
                logger.info(f"Using campaign title as product name: '{campaign.title}'")
                return campaign.title.strip()
            else:
                # PRIORITY 3: Extraction fallback (should rarely be needed now)
                logger.warning("No campaign product name found, using extraction fallback")
                return enhanced_analysis.get("page_title", "Unknown Product")
                
        except Exception as name_error:
            logger.error(f"Failed to get campaign product name via CRUD: {str(name_error)}")
            return enhanced_analysis.get("page_title", "Unknown Product")

    async def _prepare_ai_intelligence_data(self, enhanced_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Prepare AI intelligence data for CRUD update"""
        ai_intelligence_data = {}
        
        ai_keys = [
            'scientific_intelligence', 'credibility_intelligence', 'market_intelligence', 
            'emotional_transformation_intelligence', 'scientific_authority_intelligence'
        ]
        
        for key in ai_keys:
            source_data = enhanced_analysis.get(key, {})
            validated_data = self._validate_intelligence_section(source_data)
            
            if validated_data and validated_data != {}:
                try:
                    ai_intelligence_data[key] = safe_json_dumps(validated_data)
                    item_count = len(validated_data) if isinstance(validated_data, dict) else 1
                    logger.info(f"Prepared {key} for CRUD storage ({item_count} items)")
                except Exception as e:
                    logger.error(f"Failed to prepare {key} for CRUD storage: {str(e)}")
                    # Create fallback data
                    fallback_data = {
                        "fallback_data": True,
                        "original_error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    ai_intelligence_data[key] = safe_json_dumps(fallback_data)
        
        return ai_intelligence_data

    def _fix_product_names_in_analysis(self, analysis_result: Dict[str, Any], correct_product_name: str) -> Dict[str, Any]:
        """FIXED: Fix product names throughout analysis results"""
        
        logger.info(f"Applied product name fix: {correct_product_name}")
        
        # Create a copy to avoid modifying original
        fixed_analysis = analysis_result.copy()
        
        # Fix offer intelligence products
        if "offer_intelligence" in fixed_analysis:
            offer_intel = fixed_analysis["offer_intelligence"]
            if isinstance(offer_intel, dict) and "products" in offer_intel:
                # Replace any extracted/hallucinated product names with correct one
                offer_intel["products"] = [correct_product_name]
                logger.info(f"Fixed offer_intelligence products: [{correct_product_name}]")
        
        # Add metadata about the fix
        if "amplification_metadata" not in fixed_analysis:
            fixed_analysis["amplification_metadata"] = {}
        
        fixed_analysis["amplification_metadata"].update({
            "product_name_fix_applied": True,
            "correct_product_name": correct_product_name,
            "product_name_source": "campaign_user_input",
            "fix_timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return fixed_analysis
    
    def _validate_intelligence_section(self, data: Any) -> Dict[str, Any]:
        """Validate and clean intelligence data section"""
        if isinstance(data, dict):
            return data
        elif isinstance(data, list):
            return {"items": data}
        elif isinstance(data, str):
            return {"content": data}
        else:
            return {"value": str(data) if data is not None else ""}
    
    async def _complete_campaign_analysis(self, campaign: Campaign, intelligence: CampaignIntelligence, analysis_result: Dict[str, Any]):
        """Complete campaign analysis and prepare for content generation - FIXED CRUD MIGRATED"""
        try:
            logger.info(f"Completing campaign analysis for {campaign.id}")
            
            # Extract key insights for content generation
            analysis_summary = self._extract_analysis_summary(analysis_result)
            
            # Update campaign with completion
            campaign.complete_auto_analysis(
                str(intelligence.id),
                analysis_result.get("confidence_score", 0.0),
                analysis_summary
            )
            
            # If auto-generate content is enabled, trigger content generation
            if getattr(campaign, 'generate_content_after_analysis', False):
                logger.info("Auto-generating content after analysis...")
                campaign.start_content_generation()
                logger.info("Content generation would be triggered here")
            
            # FIXED: CRUD MIGRATION - Use campaign_crud.update instead of direct db.commit()
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
        
        # Extract psychology intelligence
        psychology_intel = analysis_result.get("psychology_intelligence", {})
        if psychology_intel:
            summary["audience_insights"] = {
                "target_audience": psychology_intel.get("target_audience", "Unknown"),
                "pain_points": psychology_intel.get("pain_points", [])[:5],
                "emotional_triggers": psychology_intel.get("emotional_triggers", [])[:5],
                "persuasion_techniques": psychology_intel.get("persuasion_techniques", [])[:3]
            }
        
        # Extract competitive opportunities
        competitive_opps = analysis_result.get("competitive_opportunities", [])
        summary["competitive_advantages"] = [
            opp.get("description", str(opp)) for opp in competitive_opps[:5]
        ]
        
        # Extract content opportunities
        campaign_suggestions = analysis_result.get("campaign_suggestions", [])
        summary["content_opportunities"] = campaign_suggestions[:8]
        
        # Extract amplification data
        amp_metadata = analysis_result.get("amplification_metadata", {})
        if amp_metadata.get("amplification_applied"):
            summary["amplification_data"] = {
                "scientific_backing_available": amp_metadata.get("scientific_enhancements", 0) > 0,
                "credibility_enhancements": amp_metadata.get("credibility_score", 0.0),
                "total_enhancements": amp_metadata.get("total_enhancements", 0),
                "confidence_boost": amp_metadata.get("confidence_boost", 0.0),
                "enhancement_quality": amp_metadata.get("enhancement_quality", "unknown")
            }
        
        logger.info(f"Extracted analysis summary with {len(summary['content_opportunities'])} content opportunities")
        return summary
    
    async def _fail_campaign_analysis(self, campaign: Campaign, error: Exception):
        """Handle campaign analysis failure - FIXED CRUD MIGRATED"""
        try:
            logger.info(f"Failing campaign analysis for {campaign.id}")
            
            # This method call is synchronous - no await needed
            campaign.fail_auto_analysis(str(error))
            
            # FIXED: CRUD MIGRATION - Use campaign_crud.update instead of direct db operations
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
            logger.error(f"Failed to update campaign failure status via CRUD: {str(update_error)}")
    
    async def _update_campaign_counters(self, campaign_id: str):
        """Update campaign counters for streamlined workflow"""
        if not CAMPAIGN_HELPERS_AVAILABLE:
            logger.info("Campaign helpers not available, skipping counter update")
            return
            
        try:
            logger.info(f"Updating streamlined campaign counters for: {campaign_id}")
            success = await update_campaign_counters(campaign_id, self.db)
            if success:
                logger.info("Streamlined campaign counters updated successfully")
            else:
                logger.warning("Streamlined campaign counter update failed (non-critical)")
        except Exception as counter_error:
            logger.warning(f"Streamlined counter update failed (non-critical): {str(counter_error)}")
    
    async def _handle_analysis_failure(self, intelligence: CampaignIntelligence, error: Exception):
        """Handle analysis failure in streamlined workflow - FIXED CRUD MIGRATED"""
        try:
            error_metadata = {
                "error": str(error),
                "traceback": traceback.format_exc(),
                "workflow_type": "streamlined_2_step",
                "failure_timestamp": datetime.now(timezone.utc)
            }
            
            # FIXED: CRUD MIGRATION - Use intelligence_crud.update instead of direct db operations
            await intelligence_crud.update(
                db=self.db,
                # id=intelligence.id
                db_obj=intelligence,
                obj_in={
                    "analysis_status": AnalysisStatus.FAILED,
                    "processing_metadata": serialize_metadata(error_metadata)
                }
            )
        except Exception as update_error:
            logger.error(f"Failed to update failure metadata via CRUD: {str(update_error)}")
    
    def _prepare_streamlined_response(self, campaign: Campaign, intelligence: CampaignIntelligence, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare successful streamlined analysis response"""
        # Extract competitive opportunities
        competitive_intel = analysis_result.get("competitive_intelligence", {})
        competitive_opportunities = []
        if isinstance(competitive_intel.get("opportunities"), list):
            for opp in competitive_intel["opportunities"]:
                competitive_opportunities.append({"description": str(opp), "priority": "medium"})

        campaign_suggestions = analysis_result.get("campaign_suggestions", [])

        # Add streamlined workflow-specific suggestions
        amplification_metadata = analysis_result.get("amplification_metadata", {})
        if amplification_metadata.get("amplification_applied"):
            campaign_suggestions.extend([
                "Ready for streamlined content generation",
                "Scientific backing prepared for content",
                "Credibility enhancements available",
                "Competitive insights ready to use"
            ])
            
            scientific_enhancements = amplification_metadata.get("scientific_enhancements", 0)
            if scientific_enhancements > 0:
                campaign_suggestions.append(f"Scientific validations ready: {scientific_enhancements}")
            
            total_enhancements = amplification_metadata.get("total_enhancements", 0)
            if total_enhancements > 0:
                campaign_suggestions.append(f"Intelligence enhancements available: {total_enhancements}")

            # Add ultra-cheap optimization notifications
            if amplification_metadata.get("ultra_cheap_optimization_applied"):
                cost_savings = amplification_metadata.get("cost_savings_percentage", 0)
                primary_provider = amplification_metadata.get("primary_provider_used", "unknown")
                campaign_suggestions.append(f"Cost-optimized analysis: {cost_savings:.0f}% savings using {primary_provider}")

        # Add streamlined workflow status
        campaign_suggestions.append("Campaign ready for Step 2: Content Generation")
        
        # Add content generation hints based on analysis
        analysis_summary = analysis_result.get("analysis_summary", campaign.analysis_summary or {})
        if analysis_summary:
            content_opps = analysis_summary.get("content_opportunities", [])
            if content_opps:
                campaign_suggestions.append(f"Content opportunities identified: {len(content_opps)}")

        return {
            "intelligence_id": str(intelligence.id),
            "campaign_id": str(campaign.id),
            "analysis_status": intelligence.analysis_status.value,
            "campaign_analysis_status": campaign.auto_analysis_status.value if campaign.auto_analysis_status else "completed",
            "confidence_score": intelligence.confidence_score,
            "campaign_confidence_score": campaign.analysis_confidence_score or 0.0,
            "workflow_type": "streamlined_2_step",
            "workflow_state": campaign.workflow_state.value if campaign.workflow_state else "analysis_complete",
            "can_proceed_to_content": campaign.auto_analysis_status == AutoAnalysisStatus.COMPLETED,
            "offer_intelligence": self._serialize_enum_field(intelligence.offer_intelligence),
            "psychology_intelligence": self._serialize_enum_field(intelligence.psychology_intelligence),
            "competitive_opportunities": competitive_opportunities,
            "campaign_suggestions": campaign_suggestions,
            "amplification_metadata": amplification_metadata,
            "analysis_summary": analysis_summary,
            "content_generation_ready": True,
            "next_step": "content_generation",
            "step_progress": {
                "step_1": campaign.step_states.get("step_1", {}).get("progress", 100) if hasattr(campaign, 'step_states') and campaign.step_states else 100,
                "step_2": campaign.step_states.get("step_2", {}).get("progress", 0) if hasattr(campaign, 'step_states') and campaign.step_states else 0
            }
        }
    
    def _prepare_failure_response(self, intelligence: CampaignIntelligence, error: Exception) -> Dict[str, Any]:
        """Prepare failure response for streamlined workflow"""
        return {
            "intelligence_id": str(intelligence.id),
            "analysis_status": "failed",
            "campaign_analysis_status": "failed",
            "confidence_score": 0.0,
            "campaign_confidence_score": 0.0,
            "workflow_type": "streamlined_2_step",
            "workflow_state": "analysis_failed",
            "can_proceed_to_content": False,
            "offer_intelligence": {"products": [], "pricing": [], "bonuses": [], "guarantees": [], "value_propositions": []},
            "psychology_intelligence": {"emotional_triggers": [], "pain_points": [], "target_audience": "Unknown", "persuasion_techniques": []},
            "competitive_opportunities": [{"description": f"Analysis failed: {str(error)}", "priority": "high"}],
            "campaign_suggestions": [
                "Analysis failed - check error details",
                "Try retrying the analysis",
                "Check server logs for detailed error information",
                "Verify the competitor URL is accessible"
            ],
            "analysis_summary": {},
            "content_generation_ready": False,
            "next_step": "retry_analysis",
            "error_message": str(error),
            "step_progress": {
                "step_1": 25,
                "step_2": 0
            }
        }


class StreamlinedWorkflowManager:
    """Manager for streamlined 2-step workflow operations - FIXED CRUD MIGRATED"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_campaigns_ready_for_content(self, company_id: uuid.UUID) -> List[Campaign]:
        """Get campaigns ready for content generation - FIXED CRUD MIGRATED"""
        try:
            # FIXED: CRUD MIGRATION - Use campaign_crud instead of direct queries
            filters = {
                "company_id": company_id,
                "auto_analysis_status": AutoAnalysisStatus.COMPLETED,
                "content_generated": 0
            }
            
            campaigns = await campaign_crud.get_multi(
                db=self.db,
                filters=filters,
                order_by="auto_analysis_completed_at DESC"
            )
            
            logger.info(f"Found {len(campaigns)} campaigns ready for content generation via CRUD")
            return campaigns
            
        except Exception as e:
            logger.error(f"Error getting campaigns ready for content via CRUD: {str(e)}")
            return []
    
    async def get_campaigns_in_analysis(self, company_id: uuid.UUID) -> List[Campaign]:
        """Get campaigns currently being analyzed - FIXED CRUD MIGRATED"""
        try:
            # FIXED: CRUD MIGRATION - Use campaign_crud instead of direct queries
            filters = {
                "company_id": company_id,
                "auto_analysis_status": AutoAnalysisStatus.IN_PROGRESS
            }
            
            campaigns = await campaign_crud.get_multi(
                db=self.db,
                filters=filters,
                order_by="auto_analysis_started_at DESC"
            )
            
            logger.info(f"Found {len(campaigns)} campaigns currently in analysis via CRUD")
            return campaigns
            
        except Exception as e:
            logger.error(f"Error getting campaigns in analysis via CRUD: {str(e)}")
            return []
    
    async def get_failed_analyses(self, company_id: uuid.UUID) -> List[Campaign]:
        """Get campaigns with failed analyses that need retry - FIXED CRUD MIGRATED"""
        try:
            # FIXED: CRUD MIGRATION - Use campaign_crud instead of direct queries
            filters = {
                "company_id": company_id,
                "auto_analysis_status": AutoAnalysisStatus.FAILED
            }
            
            campaigns = await campaign_crud.get_multi(
                db=self.db,
                filters=filters,
                order_by="updated_at DESC"
            )
            
            logger.info(f"Found {len(campaigns)} campaigns with failed analyses via CRUD")
            return campaigns
            
        except Exception as e:
            logger.error(f"Error getting failed analyses via CRUD: {str(e)}")
            return []
    
    async def get_workflow_summary(self, company_id: uuid.UUID) -> Dict[str, Any]:
        """Get comprehensive workflow summary for dashboard - FIXED CRUD MIGRATED"""
        try:
            # FIXED: CRUD MIGRATION - Use campaign_crud for aggregation instead of direct queries
            
            # Get counts for different analysis states
            pending_count = await campaign_crud.count_by_filters(
                db=self.db,
                filters={
                    "company_id": company_id,
                    "auto_analysis_status": AutoAnalysisStatus.PENDING
                }
            )
            
            analyzing_count = await campaign_crud.count_by_filters(
                db=self.db,
                filters={
                    "company_id": company_id,
                    "auto_analysis_status": AutoAnalysisStatus.IN_PROGRESS
                }
            )
            
            completed_count = await campaign_crud.count_by_filters(
                db=self.db,
                filters={
                    "company_id": company_id,
                    "auto_analysis_status": AutoAnalysisStatus.COMPLETED
                }
            )
            
            failed_count = await campaign_crud.count_by_filters(
                db=self.db,
                filters={
                    "company_id": company_id,
                    "auto_analysis_status": AutoAnalysisStatus.FAILED
                }
            )
            
            content_ready_count = await campaign_crud.count_by_filters(
                db=self.db,
                filters={
                    "company_id": company_id,
                    "auto_analysis_status": AutoAnalysisStatus.COMPLETED,
                    "content_generated": 0
                }
            )
            
            return {
                "workflow_type": "streamlined_2_step",
                "analysis_pending": pending_count,
                "analysis_in_progress": analyzing_count,
                "analysis_completed": completed_count,
                "analysis_failed": failed_count,
                "ready_for_content": content_ready_count,
                "total_campaigns": pending_count + analyzing_count + completed_count + failed_count,
                "analysis_success_rate": self._calculate_success_rate(completed_count, failed_count),
                "generated_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow summary via CRUD: {str(e)}")
            return {
                "workflow_type": "streamlined_2_step",
                "error": str(e),
                "generated_at": datetime.now(timezone.utc)
            }
    
    def _calculate_success_rate(self, completed: int, failed: int) -> float:
        """Calculate analysis success rate"""
        total = completed + failed
        if total == 0:
            return 100.0
        return (completed / total) * 100.0