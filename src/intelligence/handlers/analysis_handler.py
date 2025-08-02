# src/intelligence/handlers/analysis_handler.py - CRITICAL FIXES APPLIED
"""
Analysis Handler - CRITICAL FIXES for JSON serialization and async/sync issues
🔧 FIXED: JSON serialization error with datetime objects
🔧 FIXED: SQLAlchemy async/sync confusion (removed incorrect await calls)
🔧 FIXED: Background task compatibility for FastAPI
🔧 UPDATED: Now uses centralized JSON utilities from json_utils.py
"""
import uuid
import logging
import traceback
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text, update
from sqlalchemy.orm.attributes import flag_modified

from src.models.user import User
from src.models.campaign import Campaign, AutoAnalysisStatus, CampaignStatus, CampaignWorkflowState
from src.models.intelligence import (
    CampaignIntelligence,
    IntelligenceSourceType,
    AnalysisStatus
)
from ..utils.analyzer_factory import get_analyzer

# 🔧 CRITICAL FIX: Use centralized JSON utilities
from src.utils.json_utils import (
    json_serial, 
    safe_json_dumps, 
    safe_json_loads,
    serialize_metadata,
    deserialize_metadata,
    create_error_response,
    create_success_response
)

# Enhancement modules - using enhancement.py directly  
from src.intelligence.amplifier.enhancement import (
    identify_opportunities,
    generate_enhancements, 
    create_enriched_intelligence
)
from ..utils.campaign_helpers import update_campaign_counters

logger = logging.getLogger(__name__)

def diagnose_amplification_output(enhanced_analysis: Dict[str, Any]):
    """Diagnostic function to understand what's happening to your AI data"""
    
    logger.info("🔍 AMPLIFICATION OUTPUT DIAGNOSIS")
    logger.info("=" * 50)
    
    # Check top-level structure
    logger.info(f"Top-level keys: {list(enhanced_analysis.keys())}")
    
    # Look for AI intelligence data
    ai_keys = [
        'scientific_intelligence',
        'credibility_intelligence',
        'market_intelligence', 
        'emotional_transformation_intelligence',
        'scientific_authority_intelligence'
    ]
    
    logger.info("📊 AI Intelligence Categories:")
    for key in ai_keys:
        if key in enhanced_analysis:
            data = enhanced_analysis[key]
            logger.info(f"  ✅ {key}: {type(data)} - {len(data) if isinstance(data, dict) else 'Not a dict'}")
            
            if isinstance(data, dict) and data:
                sample_key = list(data.keys())[0]
                sample_value = data[sample_key]
                logger.info(f"     Sample: {sample_key} = {str(sample_value)[:80]}...")
        else:
            logger.info(f"  ❌ {key}: MISSING")
    
    # Check amplification metadata
    if 'amplification_metadata' in enhanced_analysis:
        amp_meta = enhanced_analysis['amplification_metadata']
        logger.info(f"🚀 Amplification Metadata:")
        logger.info(f"  Applied: {amp_meta.get('amplification_applied', 'Unknown')}")
        logger.info(f"  Total enhancements: {amp_meta.get('total_enhancements', 'Unknown')}")
        logger.info(f"  Confidence boost: {amp_meta.get('confidence_boost', 'Unknown')}")
    
    logger.info("=" * 50)


class AnalysisHandler:
    """🆕 ENHANCED: Handle URL analysis operations for streamlined workflow"""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
    
    # 🔥 CRITICAL FIX: Add enum serialization helper using centralized utilities
    def _serialize_enum_field(self, field_value):
        """Serialize enum field to proper format for API response using centralized JSON utilities"""
        if field_value is None:
            return {}
        
        if isinstance(field_value, str):
            return safe_json_loads(field_value)
        
        if isinstance(field_value, dict):
            return field_value
        
        logger.warning(f"Unexpected enum field type: {type(field_value)}")
        return {}
    
    async def analyze_url(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🆕 ENHANCED: URL analysis with streamlined workflow integration
        Main business logic for auto-analysis in 2-step workflow
        """
        logger.info(f"🎯 Starting STREAMLINED URL analysis for: {request_data.get('url')}")
        
        url = str(request_data.get('url'))
        campaign_id = request_data.get('campaign_id')
        analysis_type = request_data.get('analysis_type', 'sales_page')
        
        # Get campaign and update status to analyzing
        campaign = await self._get_and_update_campaign(campaign_id)
        
        # Create intelligence record
        intelligence = await self._create_intelligence_record(url, campaign_id, analysis_type)
        
        try:
            # STEP 1: Base Analysis
            base_analysis_result = await self._perform_base_analysis(url, analysis_type)
            
            # STEP 2: Amplification (if available)
            final_analysis_result = await self._perform_amplification(
                url, base_analysis_result
            )
            
            # STEP 3: Store results with campaign integration
            try:
                logger.info("🔄 Storing analysis results for streamlined workflow...")
                await self._store_analysis_results(intelligence, final_analysis_result)
                
                # 🆕 NEW: Update campaign with analysis completion
                await self._complete_campaign_analysis(campaign, intelligence, final_analysis_result)
                
                logger.info("✅ Successfully stored analysis results and updated campaign")
            except Exception as storage_error:
                logger.error(f"❌ Failed to store analysis results: {str(storage_error)}")
                await self._fail_campaign_analysis(campaign, storage_error)
                raise storage_error
            
            # STEP 4: Update campaign counters
            await self._update_campaign_counters(campaign_id)
            
            # STEP 5: Prepare response with campaign context
            return self._prepare_streamlined_response(campaign, intelligence, final_analysis_result)
            
        except Exception as e:
            logger.error(f"❌ Analysis failed for {url}: {str(e)}")
            await self._handle_analysis_failure(intelligence, e)
            await self._fail_campaign_analysis(campaign, e)
            return self._prepare_failure_response(intelligence, e)
    
    async def _get_and_update_campaign(self, campaign_id: str) -> Campaign:
        """🔧 FIXED: Get campaign and update status to analyzing"""
        try:
            logger.info(f"🔍 Getting campaign and updating status: {campaign_id}")
        
            campaign_query = select(Campaign).where(
                and_(
                    Campaign.id == uuid.UUID(campaign_id),
                    Campaign.company_id == self.user.company_id
                )
            )
        
            result = await self.db.execute(campaign_query)
            campaign = result.scalar_one_or_none()  # 🔧 FIXED: No await here - this is synchronous
        
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found or access denied")
        
            # Update campaign to analyzing status - method exists in your model
            campaign.start_auto_analysis()  # ✅ This method exists
        
            await self.db.commit()
        
            logger.info(f"✅ Campaign {campaign_id} updated to analyzing status")
            return campaign
        
        except Exception as e:
            logger.error(f"❌ Failed to get/update campaign: {str(e)}")
            await self.db.rollback()
            raise ValueError(f"Campaign update failed: {str(e)}")
    
    async def _complete_campaign_analysis(
        self, campaign: Campaign, intelligence: CampaignIntelligence, analysis_result: Dict[str, Any]
    ):
        """🆕 NEW: Complete campaign analysis and prepare for content generation"""
        try:
            logger.info(f"🎯 Completing campaign analysis for {campaign.id}")
            
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
                logger.info("🚀 Auto-generating content after analysis...")
                campaign.start_content_generation()
                
                # TODO: Trigger content generation background task here
                # This would call your content generation system
                logger.info("📝 Content generation would be triggered here")
            
            await self.db.commit()
            
            logger.info(f"✅ Campaign analysis completed - Status: {campaign.status}")
            
        except Exception as e:
            logger.error(f"❌ Failed to complete campaign analysis: {str(e)}")
            await self._fail_campaign_analysis(campaign, e)
            raise
    
    async def _fail_campaign_analysis(self, campaign: Campaign, error: Exception):
        """🆕 NEW: Handle campaign analysis failure"""
        try:
            logger.info(f"❌ Failing campaign analysis for {campaign.id}")
            
            campaign.fail_auto_analysis(str(error))
            
            await self.db.commit()
            
            logger.info(f"✅ Campaign analysis failed - Status updated")
            
        except Exception as update_error:
            logger.error(f"❌ Failed to update campaign failure status: {str(update_error)}")
    
    def _extract_analysis_summary(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """🆕 NEW: Extract key insights for content generation"""
        
        # Extract the most important insights for content generation
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
                "products": offer_intel.get("products", [])[:3],  # Top 3 products
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
        
        # Extract content opportunities from campaign suggestions
        campaign_suggestions = analysis_result.get("campaign_suggestions", [])
        summary["content_opportunities"] = campaign_suggestions[:8]
        
        # Extract amplification data if available
        amp_metadata = analysis_result.get("amplification_metadata", {})
        if amp_metadata.get("amplification_applied"):
            summary["amplification_data"] = {
                "scientific_backing_available": amp_metadata.get("scientific_enhancements", 0) > 0,
                "credibility_enhancements": amp_metadata.get("credibility_score", 0.0),
                "total_enhancements": amp_metadata.get("total_enhancements", 0),
                "confidence_boost": amp_metadata.get("confidence_boost", 0.0),
                "enhancement_quality": amp_metadata.get("enhancement_quality", "unknown")
            }
        
        logger.info(f"📊 Extracted analysis summary with {len(summary['content_opportunities'])} content opportunities")
        return summary
    
    async def _create_intelligence_record(
        self, url: str, campaign_id: str, analysis_type: str
    ) -> CampaignIntelligence:
        """🔧 FIXED: Create initial intelligence record"""
        try:
            logger.info(f"📝 Creating intelligence record for: {url}")
            
            intelligence = CampaignIntelligence(
                source_url=url,
                source_type=IntelligenceSourceType.SALES_PAGE,
                campaign_id=uuid.UUID(campaign_id),
                user_id=self.user.id,
                company_id=self.user.company_id,
                analysis_status=AnalysisStatus.PROCESSING
            )
            
            self.db.add(intelligence)
            
            await self.db.commit()
            await self.db.refresh(intelligence)
            
            logger.info(f"✅ Created intelligence record: {intelligence.id}")
            return intelligence
            
        except Exception as e:
            logger.error(f"❌ Error creating intelligence record: {str(e)}")
            await self.db.rollback()
            raise
    
    async def _perform_base_analysis(self, url: str, analysis_type: str) -> Dict[str, Any]:
        """Perform base analysis using appropriate analyzer"""
        analyzer = get_analyzer(analysis_type)
        logger.info(f"🔧 Using analyzer: {type(analyzer).__name__}")
        
        analysis_result = await analyzer.analyze(url)
        logger.info(f"📊 Base analysis completed with confidence: {analysis_result.get('confidence_score', 0.0)}")
        
        return analysis_result
    
    async def _perform_amplification(
        self, url: str, base_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform intelligence amplification using direct enhancement functions with ULTRA-CHEAP providers"""
        
        try:
            logger.info("🚀 Starting intelligence amplification for streamlined workflow...")
            
            # Get AI providers with ULTRA-CHEAP optimization
            ai_providers = self._get_ai_providers_from_analyzer()
            
            # CRITICAL: Log the provider priority to verify cost optimization
            provider_names = [p.get('name', 'unknown') for p in ai_providers]
            logger.info(f"💰 AMPLIFICATION using ULTRA-CHEAP providers: {provider_names}")
            
            # Set up preferences with cost optimization
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
            logger.info("🔍 Identifying enhancement opportunities...")
            opportunities = await identify_opportunities(
                base_intel=base_analysis,
                preferences=preferences,
                providers=ai_providers
            )
            
            opportunities_count = opportunities.get("opportunity_metadata", {}).get("total_opportunities", 0)
            logger.info(f"✅ Identified {opportunities_count} enhancement opportunities")
            
            # STEP 2: Generate enhancements
            logger.info("🚀 Generating AI-powered enhancements...")
            enhancements = await generate_enhancements(
                base_intel=base_analysis,
                opportunities=opportunities,
                providers=ai_providers
            )
            
            enhancement_metadata = enhancements.get("enhancement_metadata", {})
            total_enhancements = enhancement_metadata.get("total_enhancements", 0)
            confidence_boost = enhancement_metadata.get("confidence_boost", 0.0)
            
            logger.info(f"✅ Generated {total_enhancements} enhancements with {confidence_boost:.1%} confidence boost")
            
            # STEP 3: Create enriched intelligence
            logger.info("✨ Creating enriched intelligence...")
            enriched_intelligence = create_enriched_intelligence(
                base_intel=base_analysis,
                enhancements=enhancements
            )
            
            # Diagnose the amplification output
            logger.info("🔍 POST-AMPLIFICATION DIAGNOSIS")
            diagnose_amplification_output(enriched_intelligence)
            
            # Add amplification metadata
            enrichment_metadata = enriched_intelligence.get("enrichment_metadata", {})

            # Get cost optimization summary
            try:
                from src.intelligence.utils.tiered_ai_provider import get_cost_summary
                cost_summary = get_cost_summary()
            except:
                cost_summary = {"error": "Cost tracking not available"}
            
            # 🔧 CRITICAL FIX: Use centralized datetime handling
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
                "amplification_timestamp": datetime.now(timezone.utc),  # 🔧 Keep as datetime object for now
                "ultra_cheap_optimization_applied": True,
                "primary_provider_used": provider_names[0] if provider_names else "unknown",
                "provider_priority": provider_names,
                "cost_tracking": cost_summary,
                "estimated_cost_savings": cost_summary.get("estimated_savings", 0.0),
                "cost_savings_percentage": cost_summary.get("savings_percentage", 0.0),
                "workflow_type": "streamlined_2_step"  # 🆕 NEW: Mark as streamlined workflow
            }
            
            logger.info(f"✅ Streamlined amplification completed - Final confidence: {enriched_intelligence.get('confidence_score', 0.0):.2f}")
            
            return enriched_intelligence
            
        except ImportError as import_error:
            logger.warning(f"⚠️ Enhancement modules not available: {str(import_error)}")
            base_analysis["amplification_metadata"] = {
                "amplification_applied": False,
                "amplification_available": False,
                "amplification_error": f"Enhancement modules not installed: {str(import_error)}",
                "note": "Install amplifier dependencies for enhanced analysis",
                "fallback_to_base": True,
                "workflow_type": "streamlined_2_step"
            }
            return base_analysis
            
        except Exception as amp_error:
            logger.warning(f"⚠️ Amplification failed, using base analysis: {str(amp_error)}")
            
            base_analysis["amplification_metadata"] = {
                "amplification_applied": False,
                "amplification_error": str(amp_error),
                "fallback_to_base": True,
                "error_type": type(amp_error).__name__,
                "workflow_type": "streamlined_2_step"
            }
            return base_analysis
    
    def _get_ai_providers_from_analyzer(self) -> List[Dict[str, Any]]:
        """Get ultra-cheap AI providers using tiered system"""
        
        try:
            from src.intelligence.utils.tiered_ai_provider import get_tiered_ai_provider, ServiceTier
            
            tiered_manager = get_tiered_ai_provider(ServiceTier.FREE)
            providers = tiered_manager.get_available_providers(ServiceTier.FREE)
            
            if providers:
                primary_provider = providers[0]
                provider_name = primary_provider.get('name', 'unknown')
                cost_per_1k = primary_provider.get('cost_per_1k_tokens', 0)
                
                logger.info(f"💰 STREAMLINED ULTRA-CHEAP AI:")
                logger.info(f"   Primary provider: {provider_name}")
                logger.info(f"   Cost: ${cost_per_1k:.5f}/1K tokens")
                
                return providers
            else:
                logger.warning("⚠️ No ultra-cheap providers available")
                return self._create_emergency_fallback_providers()
                
        except ImportError as e:
            logger.error(f"❌ Tiered AI provider system not available: {str(e)}")
            return self._create_emergency_fallback_providers()
        except Exception as e:
            logger.error(f"❌ Failed to get tiered AI providers: {str(e)}")
            return self._create_emergency_fallback_providers()
    
    def _create_emergency_fallback_providers(self) -> List[Dict[str, Any]]:
        """Emergency fallback if tiered system fails"""
        
        import os
        providers = []
        
        logger.warning("🚨 Using emergency fallback providers for streamlined workflow")
        
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
                    
                    logger.info(f"✅ Emergency streamlined provider: {config['name']} initialized")
                    
                except Exception as e:
                    logger.error(f"❌ Emergency provider failed for {config['name']}: {str(e)}")
        
        if providers:
            providers.sort(key=lambda x: x["priority"])
            logger.info(f"🚨 Emergency streamlined providers: {[p['name'] for p in providers]}")
        
        return providers
    
    async def _store_analysis_results(
        self, intelligence: CampaignIntelligence, analysis_result: Dict[str, Any]
    ):
        """Store analysis results with guaranteed database commit using centralized JSON utilities"""
        try:
            enhanced_analysis = analysis_result
            
            # Store base intelligence with enum serialization using centralized utilities
            offer_intel = self._validate_intelligence_section(enhanced_analysis.get("offer_intelligence", {}))
            psychology_intel = self._validate_intelligence_section(enhanced_analysis.get("psychology_intelligence", {}))
            content_intel = self._validate_intelligence_section(enhanced_analysis.get("content_intelligence", {}))
            competitive_intel = self._validate_intelligence_section(enhanced_analysis.get("competitive_intelligence", {}))
            brand_intel = self._validate_intelligence_section(enhanced_analysis.get("brand_intelligence", {}))

            # 🔧 UPDATED: Use centralized JSON utilities for serialization
            intelligence.offer_intelligence = safe_json_dumps(offer_intel)
            intelligence.psychology_intelligence = safe_json_dumps(psychology_intel)
            intelligence.content_intelligence = safe_json_dumps(content_intel)
            intelligence.competitive_intelligence = safe_json_dumps(competitive_intel)
            intelligence.brand_intelligence = safe_json_dumps(brand_intel)
            
            logger.info(f"✅ Base intelligence prepared for streamlined storage")
            
            # Store AI data using fallback method
            logger.info("🚀 Storing AI intelligence data for streamlined workflow...")
            await self._store_ai_data_fallback(intelligence, enhanced_analysis)
            
            # Store metadata and finalize
            intelligence.confidence_score = enhanced_analysis.get("confidence_score", 0.0)
            
            # Extract and store the correct product name
            try:
                from src.intelligence.utils.product_name_fix import extract_product_name_from_intelligence
                correct_product_name = extract_product_name_from_intelligence(enhanced_analysis)

                if correct_product_name and correct_product_name != "Product":
                    intelligence.source_title = correct_product_name
                    logger.info(f"✅ Product name stored: '{correct_product_name}'")
                else:
                    intelligence.source_title = enhanced_analysis.get("page_title", "Unknown Product")
            except ImportError:
                intelligence.source_title = enhanced_analysis.get("page_title", "Unknown Product")
            
            intelligence.raw_content = enhanced_analysis.get("raw_content", "")[:10000]
            
            processing_metadata = enhanced_analysis.get("amplification_metadata", {})
            processing_metadata.update({
                "storage_method": "streamlined_workflow_storage",
                "analysis_timestamp": datetime.now(timezone.utc),
                "commit_applied": True,
                "workflow_type": "streamlined_2_step",
                "storage_version": "streamlined_2024"  
            })
            
            # 🔧 UPDATED: Use centralized serialize_metadata function
            intelligence.processing_metadata = serialize_metadata(processing_metadata)
            intelligence.analysis_status = AnalysisStatus.COMPLETED
            
            # Final commit for metadata and base intelligence
            logger.info("🔧 Final commit for streamlined workflow...")
            await self.db.commit()
            
            logger.info("✅ All streamlined analysis results stored successfully")
            
        except Exception as storage_error:
            logger.error(f"❌ Streamlined storage error: {str(storage_error)}")
            intelligence.analysis_status = AnalysisStatus.FAILED
            
            # 🔧 UPDATED: Use centralized error handling
            error_metadata = {
                "storage_error": str(storage_error),
                "error_type": type(storage_error).__name__,
                "workflow_type": "streamlined_2_step",
                "storage_fix_attempted": True,
                "failure_timestamp": datetime.now(timezone.utc)
            }
            intelligence.processing_metadata = serialize_metadata(error_metadata)
            
            try:
                await self.db.commit()
            except:
                await self.db.rollback()
                
            raise storage_error
    
    async def _store_ai_data_fallback(self, intelligence: CampaignIntelligence, enhanced_analysis: Dict[str, Any]):
        """Fallback AI data storage for streamlined workflow using centralized JSON utilities"""
        
        ai_keys = ['scientific_intelligence', 'credibility_intelligence', 'market_intelligence', 
                  'emotional_transformation_intelligence', 'scientific_authority_intelligence']
        
        logger.info("🔧 Using streamlined ORM fallback for AI data storage")
        
        successful_saves = 0
        total_items_saved = 0
        
        for key in ai_keys:
            source_data = enhanced_analysis.get(key, {})
            validated_data = self._validate_intelligence_section(source_data)
            
            if validated_data and validated_data != {}:
                try:
                    # 🔧 UPDATED: Use centralized JSON utilities
                    json_string = safe_json_dumps(validated_data)
                    setattr(intelligence, key, json_string)
                    flag_modified(intelligence, key)
                    
                    item_count = len(validated_data) if isinstance(validated_data, dict) else 1
                    total_items_saved += item_count
                    successful_saves += 1
                    
                    logger.info(f"✅ Streamlined storage: {key} set ({item_count} items)")
                    
                except Exception as e:
                    logger.error(f"❌ Streamlined storage failed for {key}: {str(e)}")
                    
                    # Store in metadata as backup using centralized utilities
                    try:
                        current_metadata = deserialize_metadata(intelligence.processing_metadata or "{}")
                        
                        if "ai_backup_storage" not in current_metadata:
                            current_metadata["ai_backup_storage"] = {}
                        
                        current_metadata["ai_backup_storage"][key] = validated_data
                        current_metadata["backup_storage_applied"] = True
                        current_metadata["backup_storage_timestamp"] = datetime.now(timezone.utc)
                        current_metadata["workflow_type"] = "streamlined_2_step"
                        
                        # 🔧 UPDATED: Use centralized metadata serialization
                        intelligence.processing_metadata = serialize_metadata(current_metadata)
                        flag_modified(intelligence, 'processing_metadata')
                        
                        logger.info(f"🔄 Stored {key} in streamlined metadata backup ({len(validated_data)} items)")
                        successful_saves += 1
                        total_items_saved += len(validated_data) if isinstance(validated_data, dict) else 1
                        
                    except Exception as backup_error:
                        logger.error(f"❌ Streamlined backup storage also failed for {key}: {str(backup_error)}")
            else:
                logger.warning(f"⚠️ No valid data to store for {key} in streamlined workflow")