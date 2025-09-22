# =====================================
# File: src/intelligence/services/intelligence_service.py
# =====================================

"""
Core intelligence service for orchestrating analysis operations.

Provides the main service interface for intelligence analysis,
coordinating between analysis, enhancement, and storage systems.
"""

import time
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.core.interfaces.service_interfaces import ServiceInterface
from src.core.shared.decorators import log_execution_time, cache_result
from src.core.shared.exceptions import NotFoundError, ValidationError
from src.intelligence.models.intelligence_models import (
    IntelligenceRequest, 
    IntelligenceResponse, 
    AnalysisResult,
    AnalysisMethod
)
from src.intelligence.repositories.intelligence_repository import IntelligenceRepository
from src.intelligence.repositories.research_repository import ResearchRepository
from src.intelligence.services.analysis_service import AnalysisService

logger = logging.getLogger(__name__)


class IntelligenceService:
    """Core service for intelligence operations."""
    
    def __init__(self):
        self.intelligence_repo = IntelligenceRepository()
        self.research_repo = ResearchRepository()
        self.analysis_service = AnalysisService()
    
    @log_execution_time()
    async def analyze_url(
        self,
        request: IntelligenceRequest,
        user_id: str,
        company_id: Optional[str] = None,
        session: AsyncSession = None
    ) -> IntelligenceResponse:
        """
        Analyze a URL and return intelligence results.
        
        Args:
            request: Intelligence analysis request
            user_id: ID of requesting user
            company_id: Optional company ID
            session: Database session
            
        Returns:
            IntelligenceResponse: Analysis results
        """
        start_time = time.time()
        
        try:
            # 🎯 AFFILIATE OPTIMIZATION: Global URL Caching System
            #
            # This system enables affiliate marketers to share intelligence analysis for common URLs
            # without duplicating expensive AI processing. Key benefits:
            #
            # 💰 COST SAVINGS: Process each URL only once, share across all users
            # ⚡ SPEED: Instant results for subsequent users (no AI processing delay)
            # 📊 DATA QUALITY: Users get the highest quality analysis (best confidence score)
            # 🔒 PRIVACY: Users get their own intelligence records, sharing is transparent
            #
            # How it works:
            # 1. Check if ANY user has analyzed this URL before (global_existing)
            # 2. If found, clone the complete analysis for the current user
            # 3. User gets full intelligence data instantly without knowing it was cached
            # 4. System saves 95%+ on AI processing costs for common affiliate URLs
            if not request.force_refresh:
                # First check for GLOBAL analysis (any user who analyzed this URL)
                global_existing = await self.intelligence_repo.find_by_url_global(
                    request.salespage_url, session
                )

                if global_existing:
                    logger.info(f"🎯 AFFILIATE CACHE HIT: Returning shared intelligence for {request.salespage_url}")
                    logger.info(f"   📊 Original analysis by user: {global_existing.user_id}")
                    logger.info(f"   👤 Cloning for current user: {user_id}")
                    logger.info(f"   💾 Analysis method: {global_existing.analysis_method}")
                    logger.info(f"   📈 Confidence score: {global_existing.confidence_score}")
                    logger.info(f"   🔬 Full analysis data available: {bool(global_existing.full_analysis_data)}")

                    # Clone the analysis for this user (preserve original data)
                    cloned_analysis = await self._clone_analysis_for_user(
                        global_existing, user_id, company_id, session
                    )

                    analysis_result = await self._build_analysis_result(cloned_analysis, session)

                    return IntelligenceResponse(
                        intelligence_id=cloned_analysis.id,
                        analysis_result=analysis_result,
                        cached=True,
                        processing_time_ms=int((time.time() - start_time) * 1000)
                    )

                # Fallback: Check user-specific analysis
                user_existing = await self.intelligence_repo.find_by_url(
                    request.salespage_url, user_id, session
                )

                if user_existing:
                    logger.info(f"Returning user-specific cached intelligence for {request.salespage_url}")
                    analysis_result = await self._build_analysis_result(user_existing, session)

                    return IntelligenceResponse(
                        intelligence_id=user_existing.id,
                        analysis_result=analysis_result,
                        cached=True,
                        processing_time_ms=int((time.time() - start_time) * 1000)
                    )
            
            # Perform new analysis
            logger.info(f"Starting {request.analysis_method} analysis for {request.salespage_url}")
            
            analysis_result = await self.analysis_service.analyze_content(
                salespage_url=request.salespage_url,
                analysis_method=request.analysis_method,
                user_id=user_id,
                company_id=company_id,
                session=session
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return IntelligenceResponse(
                intelligence_id=analysis_result.intelligence_id,
                analysis_result=analysis_result,
                cached=False,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Intelligence analysis failed for {request.salespage_url}: {e}")
            raise
    
    async def get_intelligence(
        self,
        intelligence_id: str,
        user_id: str,
        session: AsyncSession
    ) -> AnalysisResult:
        """
        Get existing intelligence by ID.
        
        Args:
            intelligence_id: Intelligence record ID
            user_id: Requesting user ID
            session: Database session
            
        Returns:
            AnalysisResult: Intelligence data
            
        Raises:
            NotFoundError: If intelligence not found or not accessible
        """
        intelligence = await self.intelligence_repo.find_by_id(intelligence_id, session)
        
        if not intelligence or intelligence.user_id != user_id:
            raise NotFoundError(
                f"Intelligence {intelligence_id} not found",
                resource_type="intelligence",
                resource_id=intelligence_id
            )
        
        return await self._build_analysis_result(intelligence, session)
    
    async def list_intelligence(
        self,
        user_id: str,
        company_id: Optional[str] = None,
        analysis_method: Optional[AnalysisMethod] = None,
        limit: int = 100,
        offset: int = 0,
        session: AsyncSession = None
    ) -> List[AnalysisResult]:
        """
        List intelligence records for a user.
        
        Args:
            user_id: User ID to filter by
            company_id: Optional company ID filter
            analysis_method: Optional analysis method filter
            limit: Maximum results to return
            offset: Number of results to skip
            session: Database session
            
        Returns:
            List[AnalysisResult]: List of intelligence results
        """
        filters = {"user_id": user_id}
        if company_id:
            filters["company_id"] = company_id
        if analysis_method:
            filters["analysis_method"] = analysis_method.value
        
        intelligence_records = await self.intelligence_repo.find_all(
            session=session,
            filters=filters,
            limit=limit,
            offset=offset
        )
        
        results = []
        for intelligence in intelligence_records:
            analysis_result = await self._build_analysis_result(intelligence, session)
            results.append(analysis_result)
        
        return results
    
    async def delete_intelligence(
        self,
        intelligence_id: str,
        user_id: str,
        session: AsyncSession
    ) -> bool:
        """
        Delete intelligence record.
        
        Args:
            intelligence_id: Intelligence record ID
            user_id: Requesting user ID
            session: Database session
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            NotFoundError: If intelligence not found or not accessible
        """
        # Verify ownership
        intelligence = await self.intelligence_repo.find_by_id(intelligence_id, session)
        
        if not intelligence or intelligence.user_id != user_id:
            raise NotFoundError(
                f"Intelligence {intelligence_id} not found",
                resource_type="intelligence",
                resource_id=intelligence_id
            )
        
        return await self.intelligence_repo.delete_by_id(intelligence_id, session)

    async def _clone_analysis_for_user(
        self,
        original_intelligence: Any,  # IntelligenceCore with loaded relationships
        user_id: str,
        company_id: Optional[str],
        session: AsyncSession
    ) -> Any:  # IntelligenceCore
        """
        Clone existing intelligence analysis for a new user.

        This enables sharing comprehensive analysis data across affiliate marketers
        without duplicating the expensive AI processing. Only creates a reference
        to the shared intelligence data while maintaining user-specific tracking.

        Args:
            original_intelligence: The existing intelligence record to clone
            user_id: ID of the user requesting the analysis
            company_id: Optional company ID
            session: Database session

        Returns:
            IntelligenceCore: Cloned intelligence record for the new user
        """
        from src.intelligence.models.intelligence_models import ProductInfo, MarketInfo

        # Extract the original analysis data
        original_product_info = ProductInfo()
        if original_intelligence.product_data:
            for product_data in original_intelligence.product_data:
                original_product_info = ProductInfo(
                    features=product_data.features or [],
                    benefits=product_data.benefits or [],
                    ingredients=product_data.ingredients or [],
                    conditions=product_data.conditions or [],
                    usage_instructions=product_data.usage_instructions or []
                )
                break

        original_market_info = MarketInfo()
        if original_intelligence.market_data:
            for market_data in original_intelligence.market_data:
                original_market_info = MarketInfo(
                    category=market_data.category,
                    positioning=market_data.positioning,
                    competitive_advantages=market_data.competitive_advantages or [],
                    target_audience=market_data.target_audience
                )
                break

        # Create a complete intelligence record for this user using the shared analysis
        cloned_intelligence = await self.intelligence_repo.create_complete_intelligence(
            salespage_url=original_intelligence.salespage_url,
            product_name=original_intelligence.product_name,
            user_id=user_id,
            company_id=company_id,
            analysis_method=original_intelligence.analysis_method,
            confidence_score=original_intelligence.confidence_score,
            product_info=original_product_info,
            market_info=original_market_info,
            full_analysis_data=original_intelligence.full_analysis_data,  # Share the complete 3-stage analysis
            session=session
        )

        # Copy research links if they exist
        if original_intelligence.research_links:
            for original_link in original_intelligence.research_links:
                if original_link.research:
                    try:
                        # Link the same research to the new intelligence record
                        await self.research_repo.link_research_to_intelligence(
                            intelligence_id=cloned_intelligence.id,
                            research_id=original_link.research.id,
                            relevance_score=original_link.relevance_score,
                            session=session
                        )
                    except Exception as e:
                        logger.warning(f"Failed to link research to cloned intelligence: {e}")
                        continue

        await session.commit()

        logger.info(f"✅ AFFILIATE CLONE: Created intelligence {cloned_intelligence.id} for user {user_id} from shared analysis {original_intelligence.id}")

        return cloned_intelligence

    async def _build_analysis_result(
        self,
        intelligence: Any,  # IntelligenceCore with loaded relationships
        session: AsyncSession
    ) -> AnalysisResult:
        """Build AnalysisResult from database intelligence record."""
        from src.intelligence.models.intelligence_models import ProductInfo, MarketInfo, ResearchInfo
        
        # Extract product info
        product_info = ProductInfo()
        if intelligence.product_data:
            for product_data in intelligence.product_data:
                product_info = ProductInfo(
                    features=product_data.features or [],
                    benefits=product_data.benefits or [],
                    ingredients=product_data.ingredients or [],
                    conditions=product_data.conditions or [],
                    usage_instructions=product_data.usage_instructions or []
                )
                break  # Take first product data record
        
        # Extract market info
        market_info = MarketInfo()
        if intelligence.market_data:
            for market_data in intelligence.market_data:
                market_info = MarketInfo(
                    category=market_data.category,
                    positioning=market_data.positioning,
                    competitive_advantages=market_data.competitive_advantages or [],
                    target_audience=market_data.target_audience
                )
                break  # Take first market data record
        
        # Extract research info
        research_info = []
        if intelligence.research_links:
            for link in intelligence.research_links:
                if link.research:
                    research_info.append(ResearchInfo(
                        research_id=link.research.id,
                        content=link.research.content,
                        research_type=link.research.research_type,
                        relevance_score=link.relevance_score,
                        source_metadata=link.research.source_metadata or {}
                    ))
        
        return AnalysisResult(
            intelligence_id=intelligence.id,
            product_name=intelligence.product_name,
            confidence_score=intelligence.confidence_score,
            product_info=product_info,
            market_info=market_info,
            research=research_info,
            created_at=intelligence.created_at
        )

    async def get_campaign_intelligence(
        self,
        campaign_id: str,
        user_id: str,
        session: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """Get intelligence data linked to a specific campaign"""
        try:
            # For now, get all intelligence for the user
            # Later this can be enhanced to link intelligence to specific campaigns
            intelligence_results = await self.get_intelligence_results(
                user_id=user_id,
                session=session,
                limit=50
            )

            # Convert to the format expected by frontend
            intelligence_data = []
            for result in intelligence_results:
                intelligence_data.append({
                    "id": str(result.intelligence_id),
                    "product_name": result.product_name,
                    "confidence_score": result.confidence_score,
                    "created_at": result.created_at.isoformat() if result.created_at else None,
                    "product_info": result.product_info,
                    "market_info": result.market_info,
                    "research": result.research
                })

            return intelligence_data

        except Exception as e:
            logger.error(f"Failed to get campaign intelligence: {e}")
            return []