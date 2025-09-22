# =====================================
# File: src/intelligence/services/analysis_service.py
# =====================================

"""
Analysis service for content processing and intelligence extraction.

Handles the core analysis pipeline including content scraping,
AI-powered analysis, and result consolidation.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import time

from src.core.config import ai_provider_config
from src.core.shared.decorators import retry_on_failure, log_execution_time
from src.core.shared.exceptions import ServiceUnavailableError, ValidationError
from src.intelligence.models.intelligence_models import AnalysisResult, AnalysisMethod, ProductInfo, MarketInfo, ResearchInfo
from src.intelligence.repositories.intelligence_repository import IntelligenceRepository
from src.intelligence.repositories.research_repository import ResearchRepository
from src.intelligence.analysis.analyzers import ContentAnalyzer
from src.intelligence.analysis.handler import AnalysisHandler
from src.intelligence.analysis.enhanced_handler import EnhancedAnalysisHandler

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for content analysis and intelligence extraction."""

    def __init__(self):
        self.intelligence_repo = IntelligenceRepository()
        self.research_repo = ResearchRepository()
        self.content_analyzer = ContentAnalyzer()
        self.analysis_handler = AnalysisHandler()
        self.enhanced_handler = EnhancedAnalysisHandler()
        self.progress_callback = None

    def set_progress_callback(self, callback):
        """Set progress callback for real-time progress tracking."""
        self.progress_callback = callback
    
    @log_execution_time()
    @retry_on_failure(max_retries=2)
    async def analyze_content(
        self,
        salespage_url: str,
        analysis_method: AnalysisMethod,
        user_id: str,
        company_id: Optional[str] = None,
        session: AsyncSession = None
    ) -> AnalysisResult:
        """
        Perform content analysis and return intelligence results.
        
        Args:
            salespage_url: URL to analyze
            analysis_method: Analysis method to use
            user_id: Requesting user ID
            company_id: Optional company ID
            session: Database session
            
        Returns:
            AnalysisResult: Complete analysis results
        """
        try:
            # Progress callback helper
            def progress_update(stage: str, progress: int, message: str):
                if self.progress_callback:
                    self.progress_callback(stage, progress, message)

            # Step 1: Scrape and preprocess content
            progress_update("content_extraction", 5, "Extracting content from sales page...")
            logger.info(f"Scraping content from {salespage_url}")
            content_data = await self.content_analyzer.scrape_content(salespage_url)

            # Step 2: Perform AI analysis based on method
            logger.info(f"Performing {analysis_method} analysis")
            if analysis_method == AnalysisMethod.FAST:
                analysis_data = await self._fast_analysis(content_data)
            elif analysis_method == AnalysisMethod.DEEP:
                analysis_data = await self._deep_analysis(content_data)
            elif analysis_method == AnalysisMethod.ENHANCED:
                analysis_data = await self._enhanced_analysis(content_data)
            elif analysis_method == AnalysisMethod.MAXIMUM:
                analysis_data = await self._maximum_analysis(content_data)
            else:
                raise ValidationError(f"Unsupported analysis method: {analysis_method}")

            # Step 3: Store results in consolidated schema
            progress_update("data_storage", 95, "Storing intelligence data...")
            logger.info("Storing analysis results")
            intelligence = await self._store_analysis_results(
                salespage_url=salespage_url,
                analysis_data=analysis_data,
                analysis_method=analysis_method.value,
                user_id=user_id,
                company_id=company_id,
                session=session
            )
            
            # Step 4: Build and return result
            # Convert research data to ResearchInfo objects
            research_objects = []
            for research_item in analysis_data.get("research", []):
                try:
                    research_objects.append(ResearchInfo(**research_item))
                except Exception as e:
                    logger.warning(f"Failed to convert research item to ResearchInfo: {e}")
                    continue

            analysis_result = AnalysisResult(
                intelligence_id=intelligence.id,
                product_name=intelligence.product_name,
                confidence_score=intelligence.confidence_score,
                product_info=analysis_data["product_info"],
                market_info=analysis_data["market_info"],
                research=research_objects,
                created_at=intelligence.created_at
            )
            
            logger.info(f"Analysis completed for {salespage_url} with confidence {intelligence.confidence_score}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Analysis failed for {salespage_url}: {e}")
            raise
    
    async def _fast_analysis(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform fast analysis using budget AI providers."""
        logger.info("Running fast analysis pipeline")
        
        # Get cheapest AI provider for fast analysis
        provider = ai_provider_config.get_cheapest_provider()
        if not provider:
            raise ServiceUnavailableError("No AI providers available")
        
        # Extract basic product information
        product_info = await self.analysis_handler.extract_product_info(
            content_data["text"],
            provider_name=provider.name
        )
        
        # Extract basic market information
        market_info = await self.analysis_handler.extract_market_info(
            content_data["text"],
            provider_name=provider.name
        )
        
        # Calculate confidence score based on content quality
        confidence_score = self._calculate_confidence_score(content_data, "fast")
        
        return {
            "product_name": product_info.get("name", "Unknown Product"),
            "product_info": ProductInfo(**product_info),
            "market_info": MarketInfo(**market_info),
            "confidence_score": confidence_score,
            "research": []
        }
    
    async def _deep_analysis(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform deep analysis using standard AI providers."""
        logger.info("Running deep analysis pipeline")
        
        # Get standard tier providers for more thorough analysis
        providers = ai_provider_config.get_providers_by_tier("standard")
        if not providers:
            # Fallback to budget providers
            providers = ai_provider_config.get_providers_by_tier("budget")
        
        if not providers:
            raise ServiceUnavailableError("No suitable AI providers available")
        
        primary_provider = providers[0]
        
        # Enhanced product extraction
        product_info = await self.analysis_handler.extract_detailed_product_info(
            content_data["text"],
            provider_name=primary_provider.name
        )
        
        # Enhanced market analysis
        market_info = await self.analysis_handler.extract_detailed_market_info(
            content_data["text"],
            provider_name=primary_provider.name
        )
        
        # Basic research gathering
        research_data = await self.analysis_handler.gather_basic_research(
            product_info.get("name", ""),
            content_data["text"]
        )
        
        confidence_score = self._calculate_confidence_score(content_data, "deep")
        
        return {
            "product_name": product_info.get("name", "Unknown Product"),
            "product_info": ProductInfo(**product_info),
            "market_info": MarketInfo(**market_info),
            "confidence_score": confidence_score,
            "research": research_data
        }
    
    async def _enhanced_analysis(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform enhanced analysis using the complete 3-stage pipeline with ultra-cheap providers."""
        logger.info("Running enhanced analysis pipeline")

        try:
            # Use our working enhanced handler with all providers available
            content_text = content_data["text"]
            salespage_url = content_data.get("url", "unknown")

            # STAGE 1: Base Analysis
            base_intelligence = await self.enhanced_handler.perform_base_analysis(content_text, salespage_url)

            # Throttling between stages to prevent API overload
            logger.info("Throttling: waiting 3s before Stage 2 (Enhancement Pipeline)")
            await asyncio.sleep(3.0)

            # STAGE 2: Enhancement Pipeline (6 enhancers)
            enriched_intelligence = await self.enhanced_handler.perform_amplification(base_intelligence, salespage_url)

            # Throttling between stages
            logger.info("Throttling: waiting 2s before Stage 3 (RAG Integration)")
            await asyncio.sleep(2.0)

            # STAGE 3: RAG Integration
            final_intelligence = await self.enhanced_handler.apply_rag_enhancement(enriched_intelligence, salespage_url)

            # Extract the needed format for the service
            products_list = final_intelligence.get("offer_intelligence", {}).get("products", ["Unknown Product"])
            product_name = products_list[0] if products_list else "Unknown Product"

            # Build product info from base intelligence
            product_info_data = {
                "name": product_name,
                "category": final_intelligence.get("competitive_intelligence", {}).get("market_positioning", "Unknown"),
                "features": final_intelligence.get("offer_intelligence", {}).get("key_features", []),
                "benefits": final_intelligence.get("offer_intelligence", {}).get("primary_benefits", []),
                "pricing": str(final_intelligence.get("offer_intelligence", {}).get("pricing_info", "Unknown"))
            }

            # Build market info from competitive intelligence
            market_info_data = {
                "category": final_intelligence.get("competitive_intelligence", {}).get("market_positioning", "Unknown"),
                "target_audience": final_intelligence.get("psychology_intelligence", {}).get("target_audience", "Unknown"),
                "competitive_advantages": final_intelligence.get("competitive_intelligence", {}).get("competitive_advantages", []),
                "market_size": "Unknown",  # Would need additional research
                "trends": ["AI-enhanced analysis available"]
            }

            confidence_score = final_intelligence.get("confidence_score", 0.7)

            # Prepare research data from the comprehensive analysis
            research_data = [
                {
                    "research_id": f"enhanced_3stage_analysis_{int(time.time())}",
                    "content": f"Complete intelligence analysis for {product_name} with {len(str(final_intelligence))} characters of data",
                    "research_type": "enhanced_analysis",
                    "relevance_score": confidence_score,
                    "source_metadata": {"pipeline": "3-stage", "enhancers": 6, "stages": ["base", "amplification", "rag"]}
                }
            ]

            return {
                "product_name": product_name,
                "product_info": ProductInfo(**product_info_data),
                "market_info": MarketInfo(**market_info_data),
                "confidence_score": confidence_score,
                "research": research_data,
                "full_analysis_data": final_intelligence  # Store the complete analysis
            }

        except Exception as e:
            logger.error(f"Enhanced analysis failed: {e}")
            # Fallback to basic analysis if enhanced fails
            return await self._basic_fallback_analysis(content_data)

    async def _maximum_analysis(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform MAXIMUM analysis - library-quality extraction with zero throttling."""
        logger.info("Running MAXIMUM analysis pipeline for library-quality extraction")

        try:
            # Use our working enhanced handler with all providers available
            content_text = content_data["text"]
            salespage_url = content_data.get("url", "unknown")

            # Progress callback helper
            def progress_update(stage: str, progress: int, message: str):
                if self.progress_callback:
                    self.progress_callback(stage, progress, message)

            # STAGE 1: Base Analysis
            progress_update("base_analysis", 10, "Performing base content analysis...")
            logger.info("MAXIMUM: Stage 1 - Base Analysis")
            base_intelligence = await self.enhanced_handler.perform_base_analysis(content_text, salespage_url)

            # GENEROUS THROTTLING - Quality over speed for one-time library extraction
            progress_update("base_analysis", 20, "Base analysis complete, preparing for enhancement...")
            logger.info("MAXIMUM: Throttling 5s before Stage 2 for optimal API stability")
            await asyncio.sleep(5.0)

            # STAGE 2: Enhancement Pipeline (6 enhancers) with extra throttling
            progress_update("ai_enhancement", 25, "Starting AI enhancement pipeline (6 enhancers)...")
            logger.info("MAXIMUM: Stage 2 - Enhancement Pipeline (6 enhancers) - QUALITY FOCUSED")
            enriched_intelligence = await self.enhanced_handler.perform_amplification(base_intelligence, salespage_url)

            # Extra throttling between stages for maximum quality
            progress_update("ai_enhancement", 60, "Enhancement pipeline complete, preparing for RAG research...")
            logger.info("MAXIMUM: Throttling 4s before Stage 3 for comprehensive extraction")
            await asyncio.sleep(4.0)

            # STAGE 3: RAG Integration
            progress_update("rag_research", 65, "Performing business intelligence RAG research...")
            logger.info("MAXIMUM: Stage 3 - RAG Integration with enhanced processing")
            final_intelligence = await self.enhanced_handler.apply_rag_enhancement(enriched_intelligence, salespage_url)

            # Extra throttling before second pass
            progress_update("rag_research", 75, "RAG research complete, preparing for ultra-enhancement...")
            logger.info("MAXIMUM: Throttling 3s before Stage 4 for ultra-enhancement")
            await asyncio.sleep(3.0)

            # STAGE 4: MAXIMUM ONLY - Second pass enhancement for library quality
            progress_update("ai_enhancement", 80, "Performing second-pass enhancement for library quality...")
            logger.info("MAXIMUM: Stage 4 - Second Pass Enhancement (LIBRARY QUALITY)")
            ultra_enhanced = await self.enhanced_handler.perform_amplification(final_intelligence, salespage_url)

            progress_update("data_storage", 90, "Processing complete, preparing data storage...")

            # Extract the needed format for the service
            products_list = ultra_enhanced.get("offer_intelligence", {}).get("products", ["Unknown Product"])
            product_name = products_list[0] if products_list else "Unknown Product"

            # Build product info from enhanced intelligence
            offer_intel = ultra_enhanced.get("offer_intelligence", {})
            market_enhancement = ultra_enhanced.get("market_enhancement", {})
            competitive_intel = ultra_enhanced.get("competitive_intelligence", {})
            psychology_intel = ultra_enhanced.get("psychology_intelligence", {})

            # Map the actual data fields from our analysis results
            product_info = ProductInfo(
                name=product_name,
                features=offer_intel.get("key_features", []),
                benefits=offer_intel.get("primary_benefits", []),
                target_audience=psychology_intel.get("target_audience", ""),
                price_points=[offer_intel.get("pricing_info", "")],
                ingredients=[],  # Not extracted in current analysis
                usage_instructions=offer_intel.get("value_propositions", []),
                contraindications=[]  # Not available in current analysis
            )

            market_info = MarketInfo(
                category=competitive_intel.get("market_positioning", "Unknown"),
                competitive_advantages=competitive_intel.get("competitive_advantages", []),
                positioning=competitive_intel.get("market_positioning", "Unknown"),
                market_trends=market_enhancement.get("market_opportunities", [])
            )

            confidence_score = ultra_enhanced.get("confidence_score", 0.85)

            # Include maximum research data
            research_data = [
                {
                    "research_id": f"maximum_analysis_{int(time.time())}",
                    "content": "MAXIMUM analysis completed with 4-stage quality-focused pipeline",
                    "research_type": "library_quality",
                    "relevance_score": confidence_score,
                    "source_metadata": {
                        "pipeline": "4-stage",
                        "enhancers": 12,
                        "stages": ["base", "amplification", "rag", "ultra_enhanced"],
                        "throttling": "generous_quality_focused",
                        "total_processing_time": "~3-5 minutes",
                        "quality_priority": "maximum"
                    }
                }
            ]

            # Ensure full_analysis_data is JSON serializable
            import json
            try:
                # Convert to dict if it's a Pydantic object, then test JSON serialization
                if hasattr(ultra_enhanced, 'dict'):
                    full_analysis_data = ultra_enhanced.dict()
                else:
                    full_analysis_data = ultra_enhanced

                # Test JSON serialization to catch any non-serializable data
                json.dumps(full_analysis_data, default=str)
                logger.info(f"✅ Full analysis data is JSON serializable ({len(str(full_analysis_data))} chars)")

            except Exception as e:
                logger.error(f"❌ Full analysis data serialization failed: {e}")
                # Fallback to a safe serializable version
                full_analysis_data = {
                    "serialization_error": str(e),
                    "data_type": str(type(ultra_enhanced)),
                    "data_size": len(str(ultra_enhanced)),
                    "timestamp": time.time()
                }

            return {
                "product_name": product_name,
                "product_info": product_info,
                "market_info": market_info,
                "confidence_score": confidence_score,
                "research": research_data,
                "full_analysis_data": full_analysis_data  # Store the complete 4-stage analysis
            }

        except Exception as e:
            logger.error(f"Maximum analysis failed: {e}")
            # Fallback to enhanced analysis if maximum fails
            return await self._enhanced_analysis(content_data)

    async def _basic_fallback_analysis(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic fallback analysis when enhanced pipeline fails."""
        logger.warning("Using basic fallback analysis")

        # Extract basic product name from content
        text = content_data["text"][:1000]  # First 1000 chars
        product_name = "Unknown Product"

        # Simple extraction
        if "product" in text.lower():
            words = text.split()
            for i, word in enumerate(words):
                if word.lower() == "product" and i > 0:
                    product_name = words[i-1].title()
                    break

        return {
            "product_name": product_name,
            "product_info": ProductInfo(
                name=product_name,
                category="Unknown",
                features=[],
                benefits=[],
                pricing="Unknown"
            ),
            "market_info": MarketInfo(
                category="Unknown",
                target_audience="Unknown",
                competitive_advantages=[],
                market_size="Unknown",
                trends=[]
            ),
            "confidence_score": 0.3,
            "research": [{
                "research_id": f"fallback_analysis_{int(time.time())}",
                "content": "Basic fallback analysis - enhanced pipeline failed",
                "research_type": "fallback",
                "relevance_score": 0.1,
                "source_metadata": {"pipeline": "fallback", "reason": "enhanced_analysis_failed"}
            }],
            "full_analysis_data": {"error": "Enhanced analysis failed, using fallback"}
        }

    async def _store_analysis_results(
        self,
        salespage_url: str,
        analysis_data: Dict[str, Any],
        analysis_method: str,
        user_id: str,
        company_id: Optional[str],
        session: AsyncSession
    ) -> Any:  # IntelligenceCore
        """Store analysis results in consolidated schema."""
        
        # Create complete intelligence record
        logger.info(f"📊 Creating intelligence record for user {user_id}, product: {analysis_data['product_name']}")
        logger.info(f"🔍 Analysis data keys: {list(analysis_data.keys())}")
        logger.info(f"🔍 Product info type: {type(analysis_data.get('product_info'))}")
        logger.info(f"🔍 Market info type: {type(analysis_data.get('market_info'))}")
        if 'product_info' in analysis_data:
            logger.info(f"🔍 Product info content: {analysis_data['product_info']}")
        if 'market_info' in analysis_data:
            logger.info(f"🔍 Market info content: {analysis_data['market_info']}")
        if 'full_analysis_data' in analysis_data:
            full_data = analysis_data['full_analysis_data']
            logger.info(f"🔍 Full analysis data type: {type(full_data)}")
            logger.info(f"🔍 Full analysis data size: {len(str(full_data)) if full_data else 0} characters")
            if isinstance(full_data, dict):
                logger.info(f"🔍 Full analysis data keys: {list(full_data.keys())}")
        else:
            logger.error("❌ full_analysis_data is MISSING from analysis_data!")

        intelligence = await self.intelligence_repo.create_complete_intelligence(
            salespage_url=salespage_url,
            product_name=analysis_data["product_name"],
            user_id=user_id,
            company_id=company_id,
            analysis_method=analysis_method,
            confidence_score=analysis_data["confidence_score"],
            product_info=analysis_data["product_info"],
            market_info=analysis_data["market_info"],
            full_analysis_data=analysis_data.get("full_analysis_data"),  # Store complete 3-stage analysis
            session=session
        )
        logger.info(f"✅ Intelligence record created with ID: {intelligence.id}")
        
        # Store research data if available
        for research_item in analysis_data.get("research", []):
            try:
                # Create or get existing research
                research = await self.research_repo.create_or_get_research(
                    content=research_item.get("content", ""),
                    research_type=research_item.get("type", "enhanced_analysis"),
                    source_metadata=research_item.get("metadata", {}),
                    session=session
                )

                # Link research to intelligence
                await self.research_repo.link_research_to_intelligence(
                    intelligence_id=intelligence.id,
                    research_id=research.id,
                    relevance_score=research_item.get("relevance_score", 0.5),
                    session=session
                )
            except Exception as e:
                logger.warning(f"Failed to store research item: {e}")
                continue

        # Note: session.commit() is handled by background session manager
        return intelligence
    
    def _calculate_confidence_score(self, content_data: Dict[str, Any], analysis_type: str) -> float:
        """Calculate confidence score based on content quality and analysis type."""
        base_score = 0.5
        
        # Content quality factors
        text_length = len(content_data.get("text", ""))
        if text_length > 5000:
            base_score += 0.2
        elif text_length > 1000:
            base_score += 0.1
        
        # Structure factors
        if content_data.get("title"):
            base_score += 0.1
        if content_data.get("meta_description"):
            base_score += 0.05
        
        # Analysis type multiplier
        type_multipliers = {
            "fast": 0.8,
            "deep": 1.0,
            "enhanced": 1.2
        }
        
        final_score = base_score * type_multipliers.get(analysis_type, 1.0)
        return min(1.0, max(0.0, final_score))