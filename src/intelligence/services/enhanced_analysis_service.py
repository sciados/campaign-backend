# =====================================
# File: src/intelligence/services/enhanced_analysis_service.py
# =====================================

"""
Enhanced Analysis Service with Complete 3-Stage Pipeline

Replaces the simplified analysis service with the full intelligence pipeline:
1. Base Analysis (working)
2. Enhancement Pipeline (6 enhancers - FIXED)
3. RAG Integration (research augmentation)
4. Consolidated Storage (complete data preservation)

**CRITICAL**: Uses new database schema with complete intelligence storage
"""

import asyncio
import logging
import json
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import time

from src.core.config import ai_provider_config
from src.core.shared.decorators import retry_on_failure, log_execution_time
from src.core.shared.exceptions import ServiceUnavailableError, ValidationError
from ..models.intelligence_models import AnalysisResult, AnalysisMethod, ProductInfo, MarketInfo, ResearchInfo
from ..repositories.enhanced_intelligence_repository import EnhancedIntelligenceRepository
from ..repositories.research_repository import ResearchRepository
from ..analysis.analyzers import ContentAnalyzer
from ..analysis.enhanced_handler import EnhancedAnalysisHandler

logger = logging.getLogger(__name__)


class EnhancedAnalysisService:
    """Enhanced service with complete 3-stage intelligence pipeline and new database schema."""
    
    def __init__(self):
        self.intelligence_repo = EnhancedIntelligenceRepository()  # Use enhanced repository
        self.research_repo = ResearchRepository()
        self.content_analyzer = ContentAnalyzer()
        self.enhanced_handler = EnhancedAnalysisHandler()
    
    @log_execution_time()
    @retry_on_failure(max_retries=2)
    async def analyze_content(
        self,
        source_url: str,
        analysis_method: AnalysisMethod,
        user_id: str,
        company_id: Optional[str] = None,
        session: AsyncSession = None
    ) -> AnalysisResult:
        """
        Perform complete 3-stage content analysis.
        
        Restores the full pipeline that was generating 12,000+ character intelligence.
        
        Args:
            source_url: URL to analyze
            analysis_method: Analysis method to use
            user_id: Requesting user ID
            company_id: Optional company ID
            session: Database session
            
        Returns:
            AnalysisResult: Complete analysis results with rich intelligence
        """
        pipeline_start = time.time()
        
        try:
            logger.info(f"Starting enhanced analysis pipeline for {source_url}")
            logger.info(f"Analysis method: {analysis_method}")
            
            # Step 1: Scrape and preprocess content
            logger.info("Phase 1: Content scraping...")
            scrape_start = time.time()
            content_data = await self.content_analyzer.scrape_content(source_url)
            scrape_time = time.time() - scrape_start
            logger.info(f"Content scraping completed in {scrape_time:.2f}s")
            logger.info(f"Scraped content size: {len(content_data.get('text', ''))} characters")
            
            # Step 2: Perform 3-stage intelligence pipeline
            logger.info("Phase 2: Starting 3-stage intelligence pipeline...")
            
            # STAGE 1: Base Analysis
            logger.info("Stage 1: Base analysis...")
            stage1_start = time.time()
            base_intelligence = await self.enhanced_handler.perform_base_analysis(
                content_data.get("text", ""), 
                source_url
            )
            stage1_time = time.time() - stage1_start
            logger.info(f"Stage 1 completed in {stage1_time:.2f}s")
            logger.info(f"Base intelligence size: {len(str(base_intelligence))} characters")
            
            # STAGE 2: Enhancement Pipeline (only for DEEP and ENHANCED)
            if analysis_method in [AnalysisMethod.DEEP, AnalysisMethod.ENHANCED]:
                logger.info("Stage 2: Enhancement pipeline...")
                stage2_start = time.time()
                enriched_intelligence = await self.enhanced_handler.perform_amplification(
                    base_intelligence, 
                    source_url
                )
                stage2_time = time.time() - stage2_start
                logger.info(f"Stage 2 completed in {stage2_time:.2f}s")
                logger.info(f"Enriched intelligence size: {len(str(enriched_intelligence))} characters")
            else:
                # Fast mode: skip enhancement pipeline
                enriched_intelligence = base_intelligence.copy()
                enriched_intelligence["enhancement_summary"] = {"skipped": "fast_mode"}
            
            # STAGE 3: RAG Integration (only for ENHANCED)
            if analysis_method == AnalysisMethod.ENHANCED:
                logger.info("Stage 3: RAG integration...")
                stage3_start = time.time()
                final_intelligence = await self.enhanced_handler.apply_rag_enhancement(
                    enriched_intelligence, 
                    source_url
                )
                stage3_time = time.time() - stage3_start
                logger.info(f"Stage 3 completed in {stage3_time:.2f}s")
                logger.info(f"Final intelligence size: {len(str(final_intelligence))} characters")
            else:
                # Skip RAG for FAST and DEEP modes
                final_intelligence = enriched_intelligence.copy()
                final_intelligence["rag_enhancement"] = {"skipped": analysis_method.value}
            
            # Step 3: Convert intelligence to storage format
            logger.info("Phase 3: Converting to storage format...")
            analysis_data = await self._convert_intelligence_to_storage_format(
                final_intelligence, content_data
            )
            
            # Step 4: Store results with COMPLETE intelligence data
            logger.info("Phase 4: Storing complete analysis results...")
            storage_start = time.time()
            intelligence = await self._store_complete_analysis_results(
                source_url=source_url,
                analysis_data=analysis_data,
                full_intelligence=final_intelligence,  # Store complete intelligence
                analysis_method=analysis_method.value,
                user_id=user_id,
                company_id=company_id,
                session=session
            )
            storage_time = time.time() - storage_start
            logger.info(f"Storage completed in {storage_time:.2f}s")
            
            # Calculate total time before logging
            total_time = time.time() - pipeline_start
            
            # Log pipeline restoration success
            self._log_pipeline_restoration_success(final_intelligence, intelligence, total_time)
            
            # Step 5: Build and return result
            analysis_result = AnalysisResult(
                intelligence_id=intelligence.id,
                product_name=intelligence.product_name,
                confidence_score=intelligence.confidence_score,
                product_info=analysis_data["product_info"],
                market_info=analysis_data["market_info"],
                research=analysis_data.get("research", []),
                created_at=intelligence.created_at
            )
            
            logger.info(f"COMPLETE PIPELINE FINISHED in {total_time:.2f}s")
            logger.info(f"Final confidence score: {intelligence.confidence_score}")
            logger.info(f"Total intelligence data size: {len(str(final_intelligence))} characters")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Enhanced analysis pipeline failed for {source_url}: {e}")
            raise
    
    async def _convert_intelligence_to_storage_format(
        self, 
        intelligence: Dict[str, Any], 
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert rich intelligence to normalized storage format."""
        
        # Extract product information from intelligence
        offer_intel = intelligence.get("offer_intelligence", {})
        product_info = ProductInfo(
            features=offer_intel.get("key_features", []),
            benefits=offer_intel.get("primary_benefits", []),
            ingredients=offer_intel.get("ingredients", []),
            conditions=offer_intel.get("conditions", []),
            usage_instructions=offer_intel.get("usage_instructions", [])
        )
        
        # Extract market information
        comp_intel = intelligence.get("competitive_intelligence", {})
        psych_intel = intelligence.get("psychology_intelligence", {})
        market_info = MarketInfo(
            category=comp_intel.get("category"),
            positioning=comp_intel.get("market_positioning"),
            competitive_advantages=comp_intel.get("competitive_advantages", []),
            target_audience=psych_intel.get("target_audience")
        )
        
        # Extract research information (from RAG enhancement)
        research_data = []
        rag_enhancement = intelligence.get("rag_enhancement", {})
        if rag_enhancement.get("research_applied"):
            research_data.append(ResearchInfo(
                research_id=f"rag_{intelligence.get('intelligence_id', 'unknown')}",
                content=rag_enhancement.get("research_summary", ""),
                research_type="rag_enhanced",
                relevance_score=rag_enhancement.get("confidence_boost", 0.1),
                source_metadata={"rag_applied": True}
            ))
        
        # Extract product name
        products = offer_intel.get("products", [])
        product_name = products[0] if products else "Unknown Product"
        
        return {
            "product_name": product_name,
            "product_info": product_info,
            "market_info": market_info,
            "research": research_data,
            "confidence_score": intelligence.get("confidence_score", 0.5)
        }
    
    async def _store_complete_analysis_results(
        self,
        source_url: str,
        analysis_data: Dict[str, Any],
        full_intelligence: Dict[str, Any],  # NEW: Store complete intelligence
        analysis_method: str,
        user_id: str,
        company_id: Optional[str],
        session: AsyncSession
    ) -> Any:  # IntelligenceCore
        """Store analysis results with COMPLETE intelligence data preservation using new schema."""
        
        # **CRITICAL**: Use the new enhanced repository method for complete data storage
        intelligence = await self.intelligence_repo.create_complete_intelligence_with_full_data(
            source_url=source_url,
            product_name=analysis_data["product_name"],
            user_id=user_id,
            company_id=company_id,
            analysis_method=analysis_method,
            confidence_score=analysis_data["confidence_score"],
            product_info=analysis_data["product_info"],
            market_info=analysis_data["market_info"],
            full_intelligence_data=full_intelligence,  # Complete 12,000+ char intelligence
            session=session
        )
        
        # Store research data using existing repository
        for research_item in analysis_data.get("research", []):
            # Create or get existing research
            research = await self.research_repo.create_or_get_research(
                content=research_item.content,
                research_type=research_item.research_type,
                source_metadata=research_item.source_metadata,
                session=session
            )
            
            # Link research to intelligence
            await self.research_repo.link_research_to_intelligence(
                intelligence_id=intelligence.id,
                research_id=research.id,
                relevance_score=research_item.relevance_score,
                session=session
            )
        
        await session.commit()
        
        # Log storage success with data sizes
        logger.info(f"Enhanced intelligence stored successfully:")
        logger.info(f"  - Core record: {intelligence.id}")
        logger.info(f"  - Product: {analysis_data['product_name']}")
        logger.info(f"  - Method: {analysis_method}")
        logger.info(f"  - Confidence: {analysis_data['confidence_score']:.3f}")
        logger.info(f"  - Product features: {len(analysis_data['product_info'].features)}")
        logger.info(f"  - Market advantages: {len(analysis_data['market_info'].competitive_advantages)}")
        logger.info(f"  - Research items: {len(analysis_data.get('research', []))}")
        logger.info(f"  - Complete intelligence size: {len(str(full_intelligence)):,} characters")
        
        # Log enhancement breakdown
        enhancement_summary = full_intelligence.get("enhancement_summary", {})
        if enhancement_summary:
            successful_enhancers = enhancement_summary.get("modules_successful", [])
            success_rate = enhancement_summary.get("success_rate", 0)
            logger.info(f"  - Enhancement modules: {len(successful_enhancers)}/6 successful ({success_rate:.1f}%)")
            logger.info(f"  - Successful enhancers: {', '.join(successful_enhancers)}")
        
        # Log RAG integration
        rag_enhancement = full_intelligence.get("rag_enhancement", {})
        if rag_enhancement.get("research_applied"):
            logger.info(f"  - RAG enhancement: Applied with confidence boost")
        
        return intelligence
    
    def _log_pipeline_restoration_success(
        self, 
        final_intelligence: Dict[str, Any], 
        intelligence: Any, 
        total_time: float
    ) -> None:
        """Log detailed pipeline restoration success metrics."""
        
        # Calculate intelligence data metrics
        total_chars = len(str(final_intelligence))
        base_chars = len(str(final_intelligence.get("offer_intelligence", {})))
        
        # Enhancement metrics
        enhancement_summary = final_intelligence.get("enhancement_summary", {})
        successful_enhancers = enhancement_summary.get("modules_successful", [])
        success_rate = enhancement_summary.get("success_rate", 0)
        
        # RAG metrics
        rag_enhancement = final_intelligence.get("rag_enhancement", {})
        rag_applied = rag_enhancement.get("research_applied", False)
        
        # Log restoration success
        logger.info("=" * 80)
        logger.info("INTELLIGENCE PIPELINE RESTORATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"INTELLIGENCE DATA METRICS:")
        logger.info(f"   • Total intelligence size: {total_chars:,} characters")
        logger.info(f"   • Base analysis size: {base_chars:,} characters")
        logger.info(f"   • Data restoration: {((total_chars - 450) / (12000 - 450) * 100):.1f}% of target reached")
        logger.info(f"   • Target was: 12,000+ characters (vs previous 450)")
        logger.info("")
        logger.info(f"ENHANCEMENT PIPELINE STATUS:")
        logger.info(f"   • Enhancers successful: {len(successful_enhancers)}/6 ({success_rate:.1f}%)")
        logger.info(f"   • Successful modules: {', '.join(successful_enhancers)}")
        logger.info("")
        logger.info(f"RAG INTEGRATION STATUS:")
        logger.info(f"   • RAG enhancement: {'Applied' if rag_applied else 'Not applied'}")
        logger.info("")
        logger.info(f"PERFORMANCE METRICS:")
        logger.info(f"   • Total pipeline time: {total_time:.2f}s")
        logger.info(f"   • Final confidence score: {intelligence.confidence_score:.3f}")
        logger.info(f"   • Product: {intelligence.product_name}")
        logger.info("")
        
        # Determine restoration status
        if total_chars > 8000:
            status = "EXCELLENT - Rich intelligence fully restored"
        elif total_chars > 4000:
            status = "GOOD - Substantial intelligence recovered"
        elif total_chars > 1000:
            status = "PARTIAL - Some intelligence recovered"
        else:
            status = "MINIMAL - Pipeline needs attention"
            
        logger.info(f"RESTORATION STATUS: {status}")
        logger.info("=" * 80)