"""
File: src/intelligence/handlers/analysis_handler.py
Analysis Handler - Contains URL analysis business logic
Extracted from routes.py to improve maintainability
"""
import uuid
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Dict, Any, Optional, List  # ← Add List here
from src.models.user import User
from src.models.campaign import Campaign
from src.models.intelligence import (
    CampaignIntelligence,
    IntelligenceSourceType,
    AnalysisStatus
)
from ..utils.intelligence_validation import ensure_intelligence_structure, validate_intelligence_section
from ..utils.analyzer_factory import get_analyzer

# NEW - using enhancement.py directly  
from src.intelligence.amplifier.enhancement import (
    identify_opportunities,
    generate_enhancements, 
    create_enriched_intelligence
)
from ..utils.campaign_helpers import update_campaign_counters


logger = logging.getLogger(__name__)

class AnalysisHandler:
    """Handle URL analysis operations"""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
    
    async def analyze_url(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced URL analysis with direct amplifier integration
        Main business logic extracted from routes.py
        """
        logger.info(f"🎯 Starting AMPLIFIED URL analysis for: {request_data.get('url')}")
        
        url = str(request_data.get('url'))
        campaign_id = request_data.get('campaign_id')
        analysis_type = request_data.get('analysis_type', 'sales_page')
        
        # Verify campaign ownership
        campaign = await self._verify_campaign_access(campaign_id)
        
        # Create intelligence record
        intelligence = await self._create_intelligence_record(url, campaign_id, analysis_type)
        
        try:
            # STEP 1: Base Analysis
            base_analysis_result = await self._perform_base_analysis(url, analysis_type)
            
            # STEP 2: Amplification (if available)
            final_analysis_result = await self._perform_amplification(
                url, base_analysis_result
            )
            
            # STEP 3: Store results
            await self._store_analysis_results(intelligence, final_analysis_result)
            
            # STEP 4: Update campaign counters
            await self._update_campaign_counters(campaign_id)
            
            # STEP 5: Prepare response
            return self._prepare_analysis_response(intelligence, final_analysis_result)
            
        except Exception as e:
            logger.error(f"❌ Analysis failed for {url}: {str(e)}")
            await self._handle_analysis_failure(intelligence, e)
            return self._prepare_failure_response(intelligence, e)
    
    async def _verify_campaign_access(self, campaign_id: str) -> Campaign:
        """Verify user has access to the campaign"""
        campaign_result = await self.db.execute(
            select(Campaign).where(
                and_(
                    Campaign.id == campaign_id,
                    Campaign.company_id == self.user.company_id
                )
            )
        )
        campaign = campaign_result.scalar_one_or_none()
        if not campaign:
            raise ValueError("Campaign not found or access denied")
        return campaign
    
    async def _create_intelligence_record(
        self, url: str, campaign_id: str, analysis_type: str
    ) -> CampaignIntelligence:
        """Create initial intelligence record"""
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
        """Perform intelligence amplification using direct enhancement functions"""
        
        try:
            logger.info("🚀 Starting intelligence amplification...")
            
            # ✅ FIX: Set up AI providers properly from your analyzer
            ai_providers = self._get_ai_providers_from_analyzer()
            
            # Set up preferences
            preferences = {
                "enhance_scientific_backing": True,
                "boost_credibility": True,
                "competitive_analysis": True,
                "psychological_depth": "medium",
                "content_optimization": True
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
            
            # Add amplification metadata for backward compatibility
            enrichment_metadata = enriched_intelligence.get("enrichment_metadata", {})
            
            enriched_intelligence["amplification_metadata"] = {
                "amplification_applied": True,
                "amplification_method": "direct_enhancement_functions",
                "opportunities_identified": opportunities_count,
                "total_enhancements": total_enhancements,
                "confidence_boost": confidence_boost,
                "base_confidence": base_analysis.get("confidence_score", 0.0),
                "amplified_confidence": enriched_intelligence.get("confidence_score", 0.0),
                "credibility_score": enhancement_metadata.get("credibility_score", 0.0),
                "enhancement_quality": enhancement_metadata.get("enhancement_quality", "unknown"),
                "modules_successful": enhancement_metadata.get("modules_successful", []),
                "scientific_enhancements": len(enhancements.get("scientific_validation", {})) if enhancements.get("scientific_validation") else 0,
                "system_architecture": "direct_modular_enhancement",
                "amplification_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Amplification completed successfully - Final confidence: {enriched_intelligence.get('confidence_score', 0.0):.2f}")
            
            return enriched_intelligence
            
        except ImportError as import_error:
            logger.warning(f"⚠️ Enhancement modules not available: {str(import_error)}")
            base_analysis["amplification_metadata"] = {
                "amplification_applied": False,
                "amplification_available": False,
                "amplification_error": f"Enhancement modules not installed: {str(import_error)}",
                "note": "Install amplifier dependencies for enhanced analysis",
                "fallback_to_base": True
            }
            return base_analysis
            
        except Exception as amp_error:
            logger.warning(f"⚠️ Amplification failed, using base analysis: {str(amp_error)}")
            logger.debug(f"Amplification error details: {traceback.format_exc()}")
            
            base_analysis["amplification_metadata"] = {
                "amplification_applied": False,
                "amplification_error": str(amp_error),
                "fallback_to_base": True,
                "error_type": type(amp_error).__name__
            }
            return base_analysis
    
    def _get_ai_providers_from_analyzer(self) -> List[Dict[str, Any]]:
        """Extract AI providers from analyzer in the format expected by enhancement modules"""
        
        from ..utils.analyzer_factory import get_analyzer
        import os
        
        providers = []
        
        try:
            # Get analyzer instance to access AI clients
            analyzer = get_analyzer("sales_page")
            
            # OpenAI provider
            if hasattr(analyzer, 'openai_client') and analyzer.openai_client:
                providers.append({
                    "name": "openai",
                    "available": True,
                    "client": analyzer.openai_client
                })
                logger.info("✅ OpenAI provider added to enhancement system")
            
            # Claude provider
            if hasattr(analyzer, 'claude_client') and analyzer.claude_client:
                providers.append({
                    "name": "anthropic", 
                    "available": True,
                    "client": analyzer.claude_client
                })
                logger.info("✅ Claude provider added to enhancement system")
            
            # Cohere provider
            if hasattr(analyzer, 'cohere_client') and analyzer.cohere_client:
                providers.append({
                    "name": "cohere",
                    "available": True, 
                    "client": analyzer.cohere_client
                })
                logger.info("✅ Cohere provider added to enhancement system")
            
            logger.info(f"🔧 Prepared {len(providers)} AI providers for enhancement modules")
            return providers
            
        except Exception as e:
            logger.error(f"❌ Failed to get AI providers from analyzer: {str(e)}")
            
            # Fallback: Try to create providers directly
            return self._create_ai_providers_fallback()
    
    def _create_ai_providers_fallback(self) -> List[Dict[str, Any]]:
        """Fallback method to create AI providers directly"""
        
        import os
        providers = []
        
        try:
            # OpenAI
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                import openai
                openai_client = openai.AsyncOpenAI(api_key=openai_key)
                providers.append({
                    "name": "openai",
                    "available": True,
                    "client": openai_client
                })
                logger.info("✅ Created OpenAI provider directly")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create OpenAI provider: {str(e)}")
        
        try:
            # Claude
            claude_key = os.getenv("ANTHROPIC_API_KEY")
            if claude_key:
                import anthropic
                claude_client = anthropic.AsyncAnthropic(api_key=claude_key)
                providers.append({
                    "name": "anthropic",
                    "available": True,
                    "client": claude_client
                })
                logger.info("✅ Created Claude provider directly")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create Claude provider: {str(e)}")
        
        try:
            # Cohere
            cohere_key = os.getenv("COHERE_API_KEY")
            if cohere_key:
                import cohere
                cohere_client = cohere.AsyncClient(api_key=cohere_key)
                providers.append({
                    "name": "cohere",
                    "available": True,
                    "client": cohere_client
                })
                logger.info("✅ Created Cohere provider directly")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create Cohere provider: {str(e)}")
        
        logger.info(f"🔧 Created {len(providers)} AI providers via fallback method")
        return providers
    
    async def _store_analysis_results(
        self, intelligence: CampaignIntelligence, analysis_result: Dict[str, Any]
    ):
        """Store analysis results with proper validation"""
        try:
            # ✅ CRITICAL: Ensure intelligence structure is complete
            enhanced_analysis = ensure_intelligence_structure(analysis_result)
            
            # Validate and clean intelligence data before storage
            offer_intel = validate_intelligence_section(enhanced_analysis.get("offer_intelligence", {}))
            psychology_intel = validate_intelligence_section(enhanced_analysis.get("psychology_intelligence", {}))
            content_intel = validate_intelligence_section(enhanced_analysis.get("content_intelligence", {}))
            competitive_intel = validate_intelligence_section(enhanced_analysis.get("competitive_intelligence", {}))
            brand_intel = validate_intelligence_section(enhanced_analysis.get("brand_intelligence", {}))

            # ✅ CRITICAL: Log what we're storing
            logger.info(f"📊 Storing intelligence data:")
            logger.info(f"   - offer_intelligence: {len(offer_intel)} keys")
            logger.info(f"   - psychology_intelligence: {len(psychology_intel)} keys") 
            logger.info(f"   - content_intelligence: {len(content_intel)} keys")
            logger.info(f"   - competitive_intelligence: {len(competitive_intel)} keys")
            logger.info(f"   - brand_intelligence: {len(brand_intel)} keys")

            # Store validated base intelligence data
            intelligence.offer_intelligence = offer_intel
            intelligence.psychology_intelligence = psychology_intel
            intelligence.content_intelligence = content_intel
            intelligence.competitive_intelligence = competitive_intel
            intelligence.brand_intelligence = brand_intel
            
            # 🔥 CRITICAL FIX: Store AI-enhanced intelligence in dedicated columns with detailed error handling
            try:
                logger.info("🔍 DEBUG: Starting AI data storage...")
                
                ai_scientific = enhanced_analysis.get("scientific_intelligence", {})
                ai_credibility = enhanced_analysis.get("credibility_intelligence", {})
                ai_market = enhanced_analysis.get("market_intelligence", {})
                ai_emotional = enhanced_analysis.get("emotional_transformation_intelligence", {})
                ai_authority = enhanced_analysis.get("scientific_authority_intelligence", {})
                
                logger.info(f"🔍 AI data extracted - scientific: {len(ai_scientific) if ai_scientific else 0} items")
                
                # Store each AI column individually with error handling
                try:
                    intelligence.scientific_intelligence = ai_scientific
                    logger.info(f"✅ Set scientific_intelligence: {len(ai_scientific)} items")
                except Exception as e:
                    logger.error(f"❌ Failed to set scientific_intelligence: {str(e)}")
                
                try:
                    intelligence.credibility_intelligence = ai_credibility
                    logger.info(f"✅ Set credibility_intelligence: {len(ai_credibility)} items")
                except Exception as e:
                    logger.error(f"❌ Failed to set credibility_intelligence: {str(e)}")
                
                try:
                    intelligence.market_intelligence = ai_market
                    logger.info(f"✅ Set market_intelligence: {len(ai_market)} items")
                except Exception as e:
                    logger.error(f"❌ Failed to set market_intelligence: {str(e)}")
                
                try:
                    intelligence.emotional_transformation_intelligence = ai_emotional
                    logger.info(f"✅ Set emotional_transformation_intelligence: {len(ai_emotional)} items")
                except Exception as e:
                    logger.error(f"❌ Failed to set emotional_transformation_intelligence: {str(e)}")
                
                try:
                    intelligence.scientific_authority_intelligence = ai_authority
                    logger.info(f"✅ Set scientific_authority_intelligence: {len(ai_authority)} items")
                except Exception as e:
                    logger.error(f"❌ Failed to set scientific_authority_intelligence: {str(e)}")
                
                # Try to flag modified for SQLAlchemy tracking
                try:
                    from sqlalchemy.orm.attributes import flag_modified
                    flag_modified(intelligence, 'scientific_intelligence')
                    flag_modified(intelligence, 'credibility_intelligence')
                    flag_modified(intelligence, 'market_intelligence')
                    flag_modified(intelligence, 'emotional_transformation_intelligence')
                    flag_modified(intelligence, 'scientific_authority_intelligence')
                    logger.info("✅ Successfully flagged AI columns as modified")
                except Exception as flag_error:
                    logger.error(f"❌ Failed to flag columns as modified: {str(flag_error)}")
                
            except Exception as ai_storage_error:
                logger.error(f"❌ Critical error in AI data storage: {str(ai_storage_error)}")
                logger.error(f"❌ Error type: {type(ai_storage_error).__name__}")
                import traceback
                logger.error(f"❌ Full traceback: {traceback.format_exc()}")
                # Continue with base intelligence only
            
            # Log what AI data we're storing (integrated above)
            ai_data_stored = {
                "scientific_intelligence": len(ai_scientific) if 'ai_scientific' in locals() and ai_scientific else 0,
                "credibility_intelligence": len(ai_credibility) if 'ai_credibility' in locals() and ai_credibility else 0,
                "market_intelligence": len(ai_market) if 'ai_market' in locals() and ai_market else 0,
                "emotional_transformation_intelligence": len(ai_emotional) if 'ai_emotional' in locals() and ai_emotional else 0,
                "scientific_authority_intelligence": len(ai_authority) if 'ai_authority' in locals() and ai_authority else 0
            }
            
            total_ai_categories = sum(1 for size in ai_data_stored.values() if size > 0)
            logger.info(f"🎯 TOTAL AI CATEGORIES WITH DATA: {total_ai_categories}/5")
            
            # Store metadata
            intelligence.confidence_score = enhanced_analysis.get("confidence_score", 0.0)
            intelligence.source_title = enhanced_analysis.get("page_title", "Analyzed Page")
            intelligence.raw_content = enhanced_analysis.get("raw_content", "")[:10000]  # Limit size
            
            # Store processing metadata (including amplification info)
            processing_metadata = enhanced_analysis.get("amplification_metadata", {})
            
            # Add base processing metadata
            processing_metadata.update({
                "base_confidence": enhanced_analysis.get("confidence_score", 0.0),
                "total_enhancements": len(offer_intel) + len(psychology_intel) + len(content_intel) + len(competitive_intel) + len(brand_intel),
                "extraction_successful": True,
                "product_name": enhanced_analysis.get("product_name", "Unknown"),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "storage_validation_applied": True,
                "intelligence_categories_stored": {
                    "offer_intelligence": len(offer_intel),
                    "psychology_intelligence": len(psychology_intel),
                    "content_intelligence": len(content_intel),
                    "competitive_intelligence": len(competitive_intel), 
                    "brand_intelligence": len(brand_intel)
                },
                "ai_intelligence_categories_stored": ai_data_stored,
                "total_ai_categories_stored": total_ai_categories
            })
            
            intelligence.processing_metadata = processing_metadata

            # Set analysis status
            if enhanced_analysis.get("confidence_score", 0.0) > 0:
                intelligence.analysis_status = AnalysisStatus.COMPLETED
                logger.info(f"✅ Analysis completed successfully with {total_ai_categories}/5 AI categories populated")
            else:
                intelligence.analysis_status = AnalysisStatus.FAILED
                logger.warning(f"⚠️ Analysis completed with zero confidence")

            # Commit to database
            await self.db.commit()
            logger.info(f"💾 Intelligence data saved to database with {total_ai_categories}/5 AI categories populated")

        except Exception as storage_error:
            logger.error(f"❌ Error storing intelligence data: {str(storage_error)}")
            # Set failed status but continue
            intelligence.analysis_status = AnalysisStatus.FAILED
            intelligence.processing_metadata = {
                "storage_error": str(storage_error),
                "partial_analysis": True
            }
            await self.db.commit()
    
    async def _update_campaign_counters(self, campaign_id: str):
        """Update campaign counters (non-critical)"""
        try:
            await update_campaign_counters(campaign_id, self.db)
            await self.db.commit()
            logger.info(f"📊 Campaign counters updated")
        except Exception as counter_error:
            logger.warning(f"⚠️ Campaign counter update failed (non-critical): {str(counter_error)}")
    
    async def _handle_analysis_failure(self, intelligence: CampaignIntelligence, error: Exception):
        """Handle analysis failure"""
        try:
            intelligence.analysis_status = AnalysisStatus.FAILED
            intelligence.processing_metadata = {
                "error": str(error),
                "traceback": traceback.format_exc()
            }
            await self.db.commit()
        except:
            await self.db.rollback()
    
    def _prepare_analysis_response(
        self, intelligence: CampaignIntelligence, analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare successful analysis response"""
        # Extract competitive opportunities
        competitive_intel = analysis_result.get("competitive_intelligence", {})
        competitive_opportunities = []
        if isinstance(competitive_intel.get("opportunities"), list):
            for opp in competitive_intel["opportunities"]:
                competitive_opportunities.append({"description": str(opp), "priority": "medium"})

        campaign_suggestions = analysis_result.get("campaign_suggestions", [])

        # Add amplification-specific suggestions
        amplification_metadata = analysis_result.get("amplification_metadata", {})
        if amplification_metadata.get("amplification_applied"):
            campaign_suggestions.extend([
                "✅ Leverage scientific backing in content creation",
                "✅ Use enhanced credibility positioning",
                "✅ Apply competitive intelligence insights"
            ])
            
            scientific_enhancements = amplification_metadata.get("scientific_enhancements", 0)
            if scientific_enhancements > 0:
                campaign_suggestions.append(f"✅ {scientific_enhancements} scientific enhancements available")
            
            total_enhancements = amplification_metadata.get("total_enhancements", 0)
            if total_enhancements > 0:
                campaign_suggestions.append(f"✅ {total_enhancements} total intelligence enhancements applied")
                
            enhancement_quality = amplification_metadata.get("enhancement_quality", "unknown")
            if enhancement_quality in ["excellent", "good"]:
                campaign_suggestions.append(f"✅ High-quality enhancement achieved ({enhancement_quality})")

        return {
            "intelligence_id": str(intelligence.id),
            "analysis_status": intelligence.analysis_status.value,
            "confidence_score": intelligence.confidence_score,
            "offer_intelligence": intelligence.offer_intelligence,
            "psychology_intelligence": intelligence.psychology_intelligence,
            "competitive_opportunities": competitive_opportunities,
            "campaign_suggestions": campaign_suggestions
        }
    
    def _prepare_failure_response(
        self, intelligence: CampaignIntelligence, error: Exception
    ) -> Dict[str, Any]:
        """Prepare failure response"""
        return {
            "intelligence_id": str(intelligence.id),
            "analysis_status": "failed",
            "confidence_score": 0.0,
            "offer_intelligence": {"products": [], "pricing": [], "bonuses": [], "guarantees": [], "value_propositions": []},
            "psychology_intelligence": {"emotional_triggers": [], "pain_points": [], "target_audience": "Unknown", "persuasion_techniques": []},
            "competitive_opportunities": [{"description": f"Analysis failed: {str(error)}", "priority": "high"}],
            "campaign_suggestions": [
                "Check server logs for detailed error information",
                "Verify all dependencies are installed",
                "Try with a different URL"
            ]
        }