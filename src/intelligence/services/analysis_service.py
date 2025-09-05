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
from ..models.intelligence_models import AnalysisResult, AnalysisMethod, ProductInfo, MarketInfo
from ..repositories.intelligence_repository import IntelligenceRepository
from ..repositories.research_repository import ResearchRepository
from ..analysis.analyzers import ContentAnalyzer
from ..analysis.handler import AnalysisHandler

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for content analysis and intelligence extraction."""
    
    def __init__(self):
        self.intelligence_repo = IntelligenceRepository()
        self.research_repo = ResearchRepository()
        self.content_analyzer = ContentAnalyzer()
        self.analysis_handler = AnalysisHandler()
    
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
        Perform content analysis and return intelligence results.
        
        Args:
            source_url: URL to analyze
            analysis_method: Analysis method to use
            user_id: Requesting user ID
            company_id: Optional company ID
            session: Database session
            
        Returns:
            AnalysisResult: Complete analysis results
        """
        try:
            # Step 1: Scrape and preprocess content
            logger.info(f"Scraping content from {source_url}")
            content_data = await self.content_analyzer.scrape_content(source_url)
            
            # Step 2: Perform AI analysis based on method
            logger.info(f"Performing {analysis_method} analysis")
            if analysis_method == AnalysisMethod.FAST:
                analysis_data = await self._fast_analysis(content_data)
            elif analysis_method == AnalysisMethod.DEEP:
                analysis_data = await self._deep_analysis(content_data)
            elif analysis_method == AnalysisMethod.ENHANCED:
                analysis_data = await self._enhanced_analysis(content_data)
            else:
                raise ValidationError(f"Unsupported analysis method: {analysis_method}")
            
            # Step 3: Store results in consolidated schema
            logger.info("Storing analysis results")
            intelligence = await self._store_analysis_results(
                source_url=source_url,
                analysis_data=analysis_data,
                analysis_method=analysis_method.value,
                user_id=user_id,
                company_id=company_id,
                session=session
            )
            
            # Step 4: Build and return result
            analysis_result = AnalysisResult(
                intelligence_id=intelligence.id,
                product_name=intelligence.product_name,
                confidence_score=intelligence.confidence_score,
                product_info=analysis_data["product_info"],
                market_info=analysis_data["market_info"],
                research=analysis_data.get("research", []),
                created_at=intelligence.created_at
            )
            
            logger.info(f"Analysis completed for {source_url} with confidence {intelligence.confidence_score}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Analysis failed for {source_url}: {e}")
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
        """Perform enhanced analysis using premium AI providers and research."""
        logger.info("Running enhanced analysis pipeline")
        
        # Get premium providers for highest quality analysis
        providers = ai_provider_config.get_providers_by_tier("premium")
        if not providers:
            # Fallback to standard providers
            providers = ai_provider_config.get_providers_by_tier("standard")
        
        if not providers:
            raise ServiceUnavailableError("No suitable AI providers available")
        
        primary_provider = providers[0]
        
        # Premium product extraction with multiple passes
        product_info = await self.analysis_handler.extract_comprehensive_product_info(
            content_data["text"],
            provider_name=primary_provider.name
        )
        
        # Premium market analysis with competitor research
        market_info = await self.analysis_handler.extract_comprehensive_market_info(
            content_data["text"],
            provider_name=primary_provider.name
        )
        
        # Comprehensive research gathering
        research_data = await self.analysis_handler.gather_comprehensive_research(
            product_info.get("name", ""),
            content_data["text"],
            market_info.get("category", "")
        )
        
        confidence_score = self._calculate_confidence_score(content_data, "enhanced")
        
        return {
            "product_name": product_info.get("name", "Unknown Product"),
            "product_info": ProductInfo(**product_info),
            "market_info": MarketInfo(**market_info),
            "confidence_score": confidence_score,
            "research": research_data
        }
    
    async def _store_analysis_results(
        self,
        source_url: str,
        analysis_data: Dict[str, Any],
        analysis_method: str,
        user_id: str,
        company_id: Optional[str],
        session: AsyncSession
    ) -> Any:  # IntelligenceCore
        """Store analysis results in consolidated schema."""
        
        # Create complete intelligence record
        intelligence = await self.intelligence_repo.create_complete_intelligence(
            source_url=source_url,
            product_name=analysis_data["product_name"],
            user_id=user_id,
            company_id=company_id,
            analysis_method=analysis_method,
            confidence_score=analysis_data["confidence_score"],
            product_info=analysis_data["product_info"],
            market_info=analysis_data["market_info"],
            session=session
        )
        
        # Store research data if available
        for research_item in analysis_data.get("research", []):
            # Create or get existing research
            research = await self.research_repo.create_or_get_research(
                content=research_item["content"],
                research_type=research_item["type"],
                source_metadata=research_item.get("metadata", {}),
                session=session
            )
            
            # Link research to intelligence
            await self.research_repo.link_research_to_intelligence(
                intelligence_id=intelligence.id,
                research_id=research.id,
                relevance_score=research_item.get("relevance", 0.5),
                session=session
            )
        
        await session.commit()
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