# =====================================
# File: src/intelligence/repositories/intelligence_repository.py
# =====================================

"""
Intelligence repository for consolidated schema operations.

Handles CRUD operations for the consolidated intelligence schema
including intelligence_core, product_data, and market_data tables.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import uuid

from src.core.database.models import IntelligenceCore, ProductData, MarketData
from src.core.interfaces.repository_interfaces import RepositoryInterface
from src.intelligence.models.intelligence_models import ProductInfo, MarketInfo


class IntelligenceRepository(RepositoryInterface[IntelligenceCore]):
    """Repository for intelligence operations using consolidated schema."""
    
    async def save(self, entity: IntelligenceCore, session: AsyncSession) -> IntelligenceCore:
        """Save intelligence entity to database."""
        session.add(entity)
        await session.flush()
        return entity
    
    async def find_by_id(self, intelligence_id: str, session: AsyncSession) -> Optional[IntelligenceCore]:
        """Find intelligence by ID with related data."""
        stmt = select(IntelligenceCore).options(
            selectinload(IntelligenceCore.product_data),
            selectinload(IntelligenceCore.market_data),
            selectinload(IntelligenceCore.research_links)
        ).where(IntelligenceCore.id == intelligence_id)
        
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_by_url(self, salespage_url: str, user_id: str, session: AsyncSession) -> Optional[IntelligenceCore]:
        """Find intelligence by source URL and user."""
        stmt = select(IntelligenceCore).options(
            selectinload(IntelligenceCore.product_data),
            selectinload(IntelligenceCore.market_data),
            selectinload(IntelligenceCore.research_links)
        ).where(
            IntelligenceCore.salespage_url == salespage_url,
            IntelligenceCore.user_id == user_id
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_url_global(self, salespage_url: str, session: AsyncSession) -> Optional[IntelligenceCore]:
        """
        Find intelligence by source URL from ANY user (global cache for affiliate marketers).

        This method enables the affiliate optimization strategy where the same URLs
        are analyzed once and shared across all users. Returns the highest quality
        analysis (best confidence score + most recent) for maximum value.

        Args:
            salespage_url: The URL to look up
            session: Database session

        Returns:
            IntelligenceCore with full analysis data, or None if not found

        Benefits:
            - 95%+ cost savings on common affiliate URLs
            - Instant results for subsequent users
            - Users get the best available analysis quality
            - Transparent sharing (users don't know it's cached)
        """
        stmt = select(IntelligenceCore).options(
            selectinload(IntelligenceCore.product_data),
            selectinload(IntelligenceCore.market_data),
            selectinload(IntelligenceCore.research_links)
        ).where(
            IntelligenceCore.salespage_url == salespage_url
        ).order_by(
            IntelligenceCore.confidence_score.desc(),  # Get highest quality analysis first
            IntelligenceCore.created_at.desc()  # Then most recent
        ).limit(1)

        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_all(
        self,
        session: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[IntelligenceCore]:
        """Find all intelligence records with optional filtering."""
        stmt = select(IntelligenceCore).options(
            selectinload(IntelligenceCore.product_data),
            selectinload(IntelligenceCore.market_data),
            selectinload(IntelligenceCore.research_links)
        )
        
        if filters:
            if "user_id" in filters:
                stmt = stmt.where(IntelligenceCore.user_id == filters["user_id"])
            if "company_id" in filters:
                stmt = stmt.where(IntelligenceCore.company_id == filters["company_id"])
            if "analysis_method" in filters:
                stmt = stmt.where(IntelligenceCore.analysis_method == filters["analysis_method"])
            if "min_confidence" in filters:
                stmt = stmt.where(IntelligenceCore.confidence_score >= filters["min_confidence"])
        
        stmt = stmt.offset(offset).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().unique())
    
    async def update(
        self, 
        intelligence_id: str, 
        data: Dict[str, Any], 
        session: AsyncSession
    ) -> Optional[IntelligenceCore]:
        """Update intelligence record."""
        stmt = update(IntelligenceCore).where(
            IntelligenceCore.id == intelligence_id
        ).values(**data).returning(IntelligenceCore)
        
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def delete_by_id(self, intelligence_id: str, session: AsyncSession) -> bool:
        """Delete intelligence record and related data."""
        stmt = delete(IntelligenceCore).where(IntelligenceCore.id == intelligence_id)
        result = await session.execute(stmt)
        return result.rowcount > 0
    
    async def create_complete_intelligence(
        self,
        salespage_url: str,
        product_name: str,
        user_id: str,
        analysis_method: str,
        confidence_score: float,
        product_info: ProductInfo,
        market_info: MarketInfo,
        company_id: Optional[str] = None,
        full_analysis_data: Optional[Dict[str, Any]] = None,
        session: AsyncSession = None
    ) -> IntelligenceCore:
        """Create complete intelligence record with product and market data."""
        
        # Create core intelligence record
        intelligence = IntelligenceCore(
            id=str(uuid.uuid4()),
            product_name=product_name,
            salespage_url=salespage_url,
            user_id=user_id,
            company_id=company_id,
            analysis_method=analysis_method,
            confidence_score=confidence_score,
            full_analysis_data=full_analysis_data  # Store the complete 3-stage analysis
        )
        
        # Create product data
        product_data = ProductData(
            intelligence_id=intelligence.id,
            features=product_info.features,
            benefits=product_info.benefits,
            ingredients=product_info.ingredients,
            conditions=product_info.conditions,
            usage_instructions=product_info.usage_instructions
        )
        
        # Create market data
        market_data = MarketData(
            intelligence_id=intelligence.id,
            category=market_info.category,
            positioning=market_info.positioning,
            competitive_advantages=market_info.competitive_advantages,
            target_audience=market_info.target_audience
        )
        
        # Add to session
        session.add(intelligence)
        session.add(product_data)
        session.add(market_data)
        
        await session.flush()
        return intelligence