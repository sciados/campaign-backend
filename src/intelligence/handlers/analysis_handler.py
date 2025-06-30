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

from src.models.user import User
from src.models.campaign import Campaign
from src.models.intelligence import (
    CampaignIntelligence,
    IntelligenceSourceType,
    AnalysisStatus
)
from ..utils.intelligence_validation import ensure_intelligence_structure, validate_intelligence_section
from ..utils.analyzer_factory import get_analyzer
from ..utils.amplifier_service import get_amplifier_service
from ..utils.campaign_helpers import update_campaign_counters

logger = logging.getLogger(__name__)

class AnalysisHandler:
    """Handle URL analysis operations"""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
    
    async def analyze_url(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced URL analysis with amplifier integration
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
        """Perform intelligence amplification if available"""
        amplifier = get_amplifier_service()
        
        if not amplifier:
            logger.info("📝 Amplifier not available, using base analysis")
            base_analysis["amplification_metadata"] = {
                "amplification_applied": False,
                "amplification_available": False,
                "note": "Install amplifier dependencies for enhanced analysis"
            }
            return base_analysis
        
        try:
            logger.info("🚀 Starting intelligence amplification...")
            
            # Prepare sources for amplification
            user_sources = [{
                "type": "url",
                "url": url,
                "analysis_result": base_analysis
            }]
            
            # Run amplification
            amplification_result = await amplifier.process_sources(
                sources=user_sources,
                preferences={
                    "enhance_scientific_backing": True,
                    "boost_credibility": True,
                    "competitive_analysis": True
                }
            )
            
            # Get enriched intelligence
            enriched_intelligence = amplification_result.get("intelligence_data", base_analysis)
            amplification_summary = amplification_result.get("summary", {})
            
            # Calculate amplification metrics
            enrichment_metadata = enriched_intelligence.get("enrichment_metadata", {})
            confidence_boost = enrichment_metadata.get("confidence_boost", 0.0)
            scientific_support = enriched_intelligence.get("offer_intelligence", {}).get("scientific_support", [])
            scientific_enhancements = len(scientific_support) if scientific_support else 0
            
            logger.info(f"✅ Amplification completed - Confidence boost: {confidence_boost:.1%}, Scientific enhancements: {scientific_enhancements}")
            
            # Add amplification metadata
            enriched_intelligence["amplification_metadata"] = {
                "amplification_applied": True,
                "confidence_boost": confidence_boost,
                "scientific_enhancements": scientific_enhancements,
                "amplification_summary": amplification_summary,
                "base_confidence": base_analysis.get("confidence_score", 0.0),
                "amplified_confidence": enriched_intelligence.get("confidence_score", 0.0),
                "credibility_score": enrichment_metadata.get("credibility_score", 0.0),
                "total_enhancements": enrichment_metadata.get("total_enhancements", 0)
            }
            
            return enriched_intelligence
            
        except Exception as amp_error:
            logger.warning(f"⚠️ Amplification failed, using base analysis: {str(amp_error)}")
            base_analysis["amplification_metadata"] = {
                "amplification_applied": False,
                "amplification_error": str(amp_error),
                "fallback_to_base": True
            }
            return base_analysis
    
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

            # Store validated intelligence data
            intelligence.offer_intelligence = offer_intel
            intelligence.psychology_intelligence = psychology_intel
            intelligence.content_intelligence = content_intel
            intelligence.competitive_intelligence = competitive_intel
            intelligence.brand_intelligence = brand_intel
            
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
                }
            })
            
            intelligence.processing_metadata = processing_metadata

            # Set analysis status
            if enhanced_analysis.get("confidence_score", 0.0) > 0:
                intelligence.analysis_status = AnalysisStatus.COMPLETED
                logger.info(f"✅ Analysis completed successfully with all intelligence categories")
            else:
                intelligence.analysis_status = AnalysisStatus.FAILED
                logger.warning(f"⚠️ Analysis completed with zero confidence")

            # Commit to database
            await self.db.commit()
            logger.info(f"💾 Intelligence data saved to database with all categories populated")

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
            if amplification_metadata.get("scientific_enhancements", 0) > 0:
                campaign_suggestions.append(f"✅ {amplification_metadata['scientific_enhancements']} scientific enhancements available")

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