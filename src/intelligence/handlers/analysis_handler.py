# src/intelligence/handlers/analysis_handler.py - STREAMLINED WORKFLOW VERSION
"""
Analysis Handler - Streamlined 2-step workflow integration
🎯 ENHANCED: Campaign Creation → Auto-Analysis → Content Generation
"""
import uuid
import logging
import traceback
import json
from datetime import datetime
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
    
    # 🔥 CRITICAL FIX: Add enum serialization helper
    def _serialize_enum_field(self, field_value):
        """Serialize enum field to proper format for API response"""
        if field_value is None:
            return {}
        
        if isinstance(field_value, str):
            try:
                return json.loads(field_value)
            except (json.JSONDecodeError, ValueError):
                logger.warning(f"Failed to parse enum field as JSON: {field_value}")
                return {}
        
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
        """🆕 NEW: Get campaign and update status to analyzing"""
        try:
            logger.info(f"🔍 Getting campaign and updating status: {campaign_id}")
        
            campaign_query = select(Campaign).where(
                and_(
                    Campaign.id == uuid.UUID(campaign_id),
                    Campaign.company_id == self.user.company_id
                )
            )
        
            result = await self.db.execute(campaign_query)
            campaign = result.scalar_one_or_none()  # ✅ Fixed: No await here
        
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
            
            try:
                await self.db.commit()
            except (TypeError, AttributeError):
                self.db.commit()
            
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
            
            try:
                await self.db.commit()
            except (TypeError, AttributeError):
                self.db.commit()
            
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
        """🔥 FIXED: Create initial intelligence record"""
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
            
            try:
                await self.db.commit()
            except (TypeError, AttributeError):
                self.db.commit()
            
            try:
                await self.db.refresh(intelligence)
            except (TypeError, AttributeError):
                self.db.refresh(intelligence)
            
            logger.info(f"✅ Created intelligence record: {intelligence.id}")
            return intelligence
            
        except Exception as e:
            logger.error(f"❌ Error creating intelligence record: {str(e)}")
            
            try:
                await self.db.rollback()
            except (TypeError, AttributeError):
                self.db.rollback()
            
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
                "amplification_timestamp": datetime.utcnow().isoformat(),
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
        """Store analysis results with guaranteed database commit"""
        try:
            enhanced_analysis = analysis_result
            
            # Store base intelligence with enum serialization
            offer_intel = self._validate_intelligence_section(enhanced_analysis.get("offer_intelligence", {}))
            psychology_intel = self._validate_intelligence_section(enhanced_analysis.get("psychology_intelligence", {}))
            content_intel = self._validate_intelligence_section(enhanced_analysis.get("content_intelligence", {}))
            competitive_intel = self._validate_intelligence_section(enhanced_analysis.get("competitive_intelligence", {}))
            brand_intel = self._validate_intelligence_section(enhanced_analysis.get("brand_intelligence", {}))

            # Serialize as JSON strings for enum storage
            intelligence.offer_intelligence = json.dumps(offer_intel)
            intelligence.psychology_intelligence = json.dumps(psychology_intel)
            intelligence.content_intelligence = json.dumps(content_intel)
            intelligence.competitive_intelligence = json.dumps(competitive_intel)
            intelligence.brand_intelligence = json.dumps(brand_intel)
            
            logger.info(f"✅ Base intelligence prepared for streamlined storage")
            
            # Store AI data using fallback method
            logger.info("🚀 Storing AI intelligence data for streamlined workflow...")
            await self._store_ai_data_fallback(intelligence, enhanced_analysis)
            
            # Store metadata and finalize
            intelligence.confidence_score = enhanced_analysis.get("confidence_score", 0.0)
            
            # Extract and store the correct product name
            from src.intelligence.utils.product_name_fix import extract_product_name_from_intelligence
            correct_product_name = extract_product_name_from_intelligence(enhanced_analysis)

            if correct_product_name and correct_product_name != "Product":
                intelligence.source_title = correct_product_name
                logger.info(f"✅ Product name stored: '{correct_product_name}'")
            else:
                intelligence.source_title = enhanced_analysis.get("page_title", "Unknown Product")
            
            intelligence.raw_content = enhanced_analysis.get("raw_content", "")[:10000]
            
            processing_metadata = enhanced_analysis.get("amplification_metadata", {})
            processing_metadata.update({
                "storage_method": "streamlined_workflow_storage",
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "commit_applied": True,
                "workflow_type": "streamlined_2_step",
                "storage_version": "streamlined_2024"
            })
            intelligence.processing_metadata = json.dumps(processing_metadata)
            intelligence.analysis_status = AnalysisStatus.COMPLETED
            
            # Final commit for metadata and base intelligence
            logger.info("🔧 Final commit for streamlined workflow...")
            try:
                await self.db.commit()
            except (TypeError, AttributeError):
                self.db.commit()
            
            logger.info("✅ All streamlined analysis results stored successfully")
            
        except Exception as storage_error:
            logger.error(f"❌ Streamlined storage error: {str(storage_error)}")
            intelligence.analysis_status = AnalysisStatus.FAILED
            intelligence.processing_metadata = json.dumps({
                "storage_error": str(storage_error),
                "error_type": type(storage_error).__name__,
                "workflow_type": "streamlined_2_step",
                "storage_fix_attempted": True
            })
            try:
                try:
                    await self.db.commit()
                except (TypeError, AttributeError):
                    self.db.commit()
            except:
                try:
                    await self.db.rollback()
                except (TypeError, AttributeError):
                    self.db.rollback()
                
            raise storage_error
    
    async def _store_ai_data_fallback(self, intelligence: CampaignIntelligence, enhanced_analysis: Dict[str, Any]):
        """Fallback AI data storage for streamlined workflow"""
        
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
                    json_string = json.dumps(validated_data)
                    setattr(intelligence, key, json_string)
                    flag_modified(intelligence, key)
                    
                    item_count = len(validated_data) if isinstance(validated_data, dict) else 1
                    total_items_saved += item_count
                    successful_saves += 1
                    
                    logger.info(f"✅ Streamlined storage: {key} set ({item_count} items)")
                    
                except Exception as e:
                    logger.error(f"❌ Streamlined storage failed for {key}: {str(e)}")
                    
                    # Store in metadata as backup
                    try:
                        current_metadata_str = intelligence.processing_metadata or "{}"
                        current_metadata = json.loads(current_metadata_str) if current_metadata_str != "{}" else {}
                        
                        if "ai_backup_storage" not in current_metadata:
                            current_metadata["ai_backup_storage"] = {}
                        
                        current_metadata["ai_backup_storage"][key] = validated_data
                        current_metadata["backup_storage_applied"] = True
                        current_metadata["backup_storage_timestamp"] = datetime.utcnow().isoformat()
                        current_metadata["workflow_type"] = "streamlined_2_step"
                        
                        intelligence.processing_metadata = json.dumps(current_metadata)
                        flag_modified(intelligence, 'processing_metadata')
                        
                        logger.info(f"🔄 Stored {key} in streamlined metadata backup ({len(validated_data)} items)")
                        successful_saves += 1
                        total_items_saved += len(validated_data) if isinstance(validated_data, dict) else 1
                        
                    except Exception as backup_error:
                        logger.error(f"❌ Streamlined backup storage also failed for {key}: {str(backup_error)}")
            else:
                logger.warning(f"⚠️ No valid data to store for {key} in streamlined workflow")
        
        # COMMIT THE CHANGES
        try:
            logger.info("🔧 Committing streamlined fallback storage changes...")
            try:
                await self.db.commit()
            except (TypeError, AttributeError):
                self.db.commit()
            logger.info(f"✅ STREAMLINED COMMIT SUCCESS: {successful_saves}/{len(ai_keys)} categories, {total_items_saved} total items")
        
            # Simple verification for streamlined workflow
            await self._verify_streamlined_storage(intelligence.id)   
        except Exception as commit_error:
            logger.error(f"❌ CRITICAL: Streamlined commit failed: {str(commit_error)}")
            try:
                await self.db.rollback()
            except (TypeError, AttributeError):
                self.db.rollback()
            raise commit_error
    
    async def _verify_streamlined_storage(self, intelligence_id: uuid.UUID):
        """Simplified verification for streamlined workflow"""
        try:
            logger.info("📊 Streamlined storage verification...")
            
            count_query = text("SELECT COUNT(*) FROM campaign_intelligence WHERE id = :intelligence_id")
            count_result = await self.db.execute(count_query, {'intelligence_id': intelligence_id})
            count = count_result.scalar()
            
            if count > 0:
                logger.info(f"✅ STREAMLINED VERIFICATION: Record exists in database")
                logger.info(f"   📊 Intelligence ID: {intelligence_id}")
                logger.info(f"   📊 Workflow: Streamlined 2-step")
            else:
                logger.error("❌ STREAMLINED VERIFICATION FAILED: No record found!")
                
        except Exception as e:
            logger.warning(f"⚠️ Streamlined verification skipped: {str(e)}")
            logger.info("✅ Non-critical - streamlined analysis data was stored successfully")
    
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
    
    async def _update_campaign_counters(self, campaign_id: str):
        """Update campaign counters for streamlined workflow"""
        try:
            logger.info(f"📊 Updating streamlined campaign counters for: {campaign_id}")
            
            success = await update_campaign_counters(campaign_id, self.db)
            
            if success:
                logger.info(f"✅ Streamlined campaign counters updated successfully")
            else:
                logger.warning(f"⚠️ Streamlined campaign counter update failed (non-critical)")
                
        except Exception as counter_error:
            logger.warning(f"⚠️ Streamlined counter update failed (non-critical): {str(counter_error)}")
    
    async def _handle_analysis_failure(self, intelligence: CampaignIntelligence, error: Exception):
        """Handle analysis failure in streamlined workflow"""
        try:
            intelligence.analysis_status = AnalysisStatus.FAILED
            intelligence.processing_metadata = json.dumps({
                "error": str(error),
                "traceback": traceback.format_exc(),
                "workflow_type": "streamlined_2_step",
                "failure_timestamp": datetime.utcnow().isoformat()
            })
            try:
                await self.db.commit()
            except (TypeError, AttributeError):
                self.db.commit()
        except:
            try:
                await self.db.rollback()
            except (TypeError, AttributeError):
                self.db.rollback()
    
    def _prepare_streamlined_response(
        self, campaign: Campaign, intelligence: CampaignIntelligence, analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🆕 NEW: Prepare successful streamlined analysis response"""
        
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
                "✅ Ready for streamlined content generation",
                "✅ Scientific backing prepared for content",
                "✅ Credibility enhancements available",
                "✅ Competitive insights ready to use"
            ])
            
            scientific_enhancements = amplification_metadata.get("scientific_enhancements", 0)
            if scientific_enhancements > 0:
                campaign_suggestions.append(f"🔬 {scientific_enhancements} scientific validations ready")
            
            total_enhancements = amplification_metadata.get("total_enhancements", 0)
            if total_enhancements > 0:
                campaign_suggestions.append(f"🚀 {total_enhancements} intelligence enhancements available")

            # Add ultra-cheap optimization notifications
            if amplification_metadata.get("ultra_cheap_optimization_applied"):
                cost_savings = amplification_metadata.get("cost_savings_percentage", 0)
                primary_provider = amplification_metadata.get("primary_provider_used", "unknown")
                campaign_suggestions.append(f"💰 Cost-optimized analysis: {cost_savings:.0f}% savings using {primary_provider}")

        # Add streamlined workflow status
        campaign_suggestions.append("🎯 Campaign ready for Step 2: Content Generation")
        
        # Add content generation hints based on analysis
        analysis_summary = analysis_result.get("analysis_summary", campaign.analysis_summary or {})
        if analysis_summary:
            content_opps = analysis_summary.get("content_opportunities", [])
            if content_opps:
                campaign_suggestions.append(f"📝 {len(content_opps)} content opportunities identified")

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
                "step_1": campaign.step_states.get("step_1", {}).get("progress", 100),
                "step_2": campaign.step_states.get("step_2", {}).get("progress", 0)
            }
        }
    
    def _prepare_failure_response(
        self, intelligence: CampaignIntelligence, error: Exception
    ) -> Dict[str, Any]:
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
                "❌ Analysis failed - check error details",
                "🔄 Try retrying the analysis",
                "🛠️ Check server logs for detailed error information",
                "🔗 Verify the competitor URL is accessible"
            ],
            "analysis_summary": {},
            "content_generation_ready": False,
            "next_step": "retry_analysis",
            "error_message": str(error),
            "step_progress": {
                "step_1": 25,  # Partial progress before failure
                "step_2": 0
            }
        }


# 🆕 NEW: Streamlined Workflow Utilities
class StreamlinedWorkflowManager:
    """🆕 NEW: Manager for streamlined 2-step workflow operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_campaigns_ready_for_content(self, company_id: uuid.UUID) -> List[Campaign]:
        """Get campaigns that have completed analysis and are ready for content generation"""
        try:
            query = select(Campaign).where(
                and_(
                    Campaign.company_id == company_id,
                    Campaign.auto_analysis_status == AutoAnalysisStatus.COMPLETED,
                    Campaign.content_generated == 0
                )
            ).order_by(Campaign.auto_analysis_completed_at.desc())
            
            result = await self.db.execute(query)
            campaigns = result.scalars().all()
            
            logger.info(f"📊 Found {len(campaigns)} campaigns ready for content generation")
            return campaigns
            
        except Exception as e:
            logger.error(f"❌ Error getting campaigns ready for content: {str(e)}")
            return []
    
    async def get_campaigns_in_analysis(self, company_id: uuid.UUID) -> List[Campaign]:
        """Get campaigns currently being analyzed"""
        try:
            query = select(Campaign).where(
                and_(
                    Campaign.company_id == company_id,
                    Campaign.auto_analysis_status == AutoAnalysisStatus.IN_PROGRESS
                )
            ).order_by(Campaign.auto_analysis_started_at.desc())
            
            result = await self.db.execute(query)
            campaigns = result.scalars().all()
            
            logger.info(f"📊 Found {len(campaigns)} campaigns currently in analysis")
            return campaigns
            
        except Exception as e:
            logger.error(f"❌ Error getting campaigns in analysis: {str(e)}")
            return []
    
    async def get_failed_analyses(self, company_id: uuid.UUID) -> List[Campaign]:
        """Get campaigns with failed analyses that need retry"""
        try:
            query = select(Campaign).where(
                and_(
                    Campaign.company_id == company_id,
                    Campaign.auto_analysis_status == AutoAnalysisStatus.FAILED
                )
            ).order_by(Campaign.updated_at.desc())
            
            result = await self.db.execute(query)
            campaigns = result.scalars().all()
            
            logger.info(f"📊 Found {len(campaigns)} campaigns with failed analyses")
            return campaigns
            
        except Exception as e:
            logger.error(f"❌ Error getting failed analyses: {str(e)}")
            return []
    
    async def get_workflow_summary(self, company_id: uuid.UUID) -> Dict[str, Any]:
        """Get comprehensive workflow summary for dashboard"""
        try:
            # Get counts for different analysis states
            pending_query = select(func.count(Campaign.id)).where(
                and_(
                    Campaign.company_id == company_id,
                    Campaign.auto_analysis_status == AutoAnalysisStatus.PENDING
                )
            )
            
            analyzing_query = select(func.count(Campaign.id)).where(
                and_(
                    Campaign.company_id == company_id,
                    Campaign.auto_analysis_status == AutoAnalysisStatus.IN_PROGRESS
                )
            )
            
            completed_query = select(func.count(Campaign.id)).where(
                and_(
                    Campaign.company_id == company_id,
                    Campaign.auto_analysis_status == AutoAnalysisStatus.COMPLETED
                )
            )
            
            failed_query = select(func.count(Campaign.id)).where(
                and_(
                    Campaign.company_id == company_id,
                    Campaign.auto_analysis_status == AutoAnalysisStatus.FAILED
                )
            )
            
            content_ready_query = select(func.count(Campaign.id)).where(
                and_(
                    Campaign.company_id == company_id,
                    Campaign.auto_analysis_status == AutoAnalysisStatus.COMPLETED,
                    Campaign.content_generated == 0
                )
            )
            
            # Execute all queries
            pending_result = await self.db.execute(pending_query)
            analyzing_result = await self.db.execute(analyzing_query)
            completed_result = await self.db.execute(completed_query)
            failed_result = await self.db.execute(failed_query)
            content_ready_result = await self.db.execute(content_ready_query)
            
            return {
                "workflow_type": "streamlined_2_step",
                "analysis_pending": pending_result.scalar() or 0,
                "analysis_in_progress": analyzing_result.scalar() or 0,
                "analysis_completed": completed_result.scalar() or 0,
                "analysis_failed": failed_result.scalar() or 0,
                "ready_for_content": content_ready_result.scalar() or 0,
                "total_campaigns": (
                    (pending_result.scalar() or 0) +
                    (analyzing_result.scalar() or 0) +
                    (completed_result.scalar() or 0) +
                    (failed_result.scalar() or 0)
                ),
                "analysis_success_rate": self._calculate_success_rate(
                    completed_result.scalar() or 0,
                    failed_result.scalar() or 0
                ),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting workflow summary: {str(e)}")
            return {
                "workflow_type": "streamlined_2_step",
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def _calculate_success_rate(self, completed: int, failed: int) -> float:
        """Calculate analysis success rate"""
        total = completed + failed
        if total == 0:
            return 100.0
        return (completed / total) * 100.0