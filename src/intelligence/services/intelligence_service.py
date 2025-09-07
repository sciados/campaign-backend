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
from src.intelligence.services.analysis_service import AnalysisService

logger = logging.getLogger(__name__)


class IntelligenceService:
    """Core service for intelligence operations."""
    
    def __init__(self):
        self.intelligence_repo = IntelligenceRepository()
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
            # Check for existing analysis if not forcing refresh
            if not request.force_refresh:
                existing = await self.intelligence_repo.find_by_url(
                    request.source_url, user_id, session
                )
                
                if existing:
                    logger.info(f"Returning cached intelligence for {request.source_url}")
                    analysis_result = await self._build_analysis_result(existing, session)
                    
                    return IntelligenceResponse(
                        intelligence_id=existing.id,
                        analysis_result=analysis_result,
                        cached=True,
                        processing_time_ms=int((time.time() - start_time) * 1000)
                    )
            
            # Perform new analysis
            logger.info(f"Starting {request.analysis_method} analysis for {request.source_url}")
            
            analysis_result = await self.analysis_service.analyze_content(
                source_url=request.source_url,
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
            logger.error(f"Intelligence analysis failed for {request.source_url}: {e}")
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