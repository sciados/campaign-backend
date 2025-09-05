# =====================================
# File: src/intelligence/repositories/research_repository.py
# =====================================

"""
Research repository for knowledge base operations.

Handles research content storage, deduplication, and retrieval
from the knowledge_base and related tables.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import hashlib
import uuid

from src.core.database.models import KnowledgeBase, IntelligenceResearch
from src.core.interfaces.repository_interfaces import RepositoryInterface


class ResearchRepository(RepositoryInterface[KnowledgeBase]):
    """Repository for research and knowledge base operations."""
    
    async def save(self, entity: KnowledgeBase, session: AsyncSession) -> KnowledgeBase:
        """Save research entity to database."""
        session.add(entity)
        await session.flush()
        return entity
    
    async def find_by_id(self, research_id: str, session: AsyncSession) -> Optional[KnowledgeBase]:
        """Find research by ID."""
        stmt = select(KnowledgeBase).where(KnowledgeBase.id == research_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_by_content_hash(self, content_hash: str, session: AsyncSession) -> Optional[KnowledgeBase]:
        """Find research by content hash for deduplication."""
        stmt = select(KnowledgeBase).where(KnowledgeBase.content_hash == content_hash)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_all(
        self,
        session: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[KnowledgeBase]:
        """Find all research records with optional filtering."""
        stmt = select(KnowledgeBase)
        
        if filters:
            if "research_type" in filters:
                stmt = stmt.where(KnowledgeBase.research_type == filters["research_type"])
        
        stmt = stmt.offset(offset).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()
    
    async def update(
        self, 
        research_id: str, 
        data: Dict[str, Any], 
        session: AsyncSession
    ) -> Optional[KnowledgeBase]:
        """Update research record."""
        research = await self.find_by_id(research_id, session)
        if not research:
            return None
        
        for key, value in data.items():
            if hasattr(research, key):
                setattr(research, key, value)
        
        await session.flush()
        return research
    
    async def delete_by_id(self, research_id: str, session: AsyncSession) -> bool:
        """Delete research record."""
        research = await self.find_by_id(research_id, session)
        if not research:
            return False
        
        await session.delete(research)
        return True
    
    async def create_or_get_research(
        self,
        content: str,
        research_type: str,
        source_metadata: Dict[str, Any],
        session: AsyncSession
    ) -> KnowledgeBase:
        """Create new research or return existing if content already exists."""
        
        # Generate content hash for deduplication
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Check if research already exists
        existing = await self.find_by_content_hash(content_hash, session)
        if existing:
            return existing
        
        # Create new research record
        research = KnowledgeBase(
            id=str(uuid.uuid4()),
            content_hash=content_hash,
            content=content,
            research_type=research_type,
            source_metadata=source_metadata
        )
        
        session.add(research)
        await session.flush()
        return research
    
    async def link_research_to_intelligence(
        self,
        intelligence_id: str,
        research_id: str,
        relevance_score: float,
        session: AsyncSession
    ) -> IntelligenceResearch:
        """Create link between intelligence and research."""
        
        link = IntelligenceResearch(
            id=str(uuid.uuid4()),
            intelligence_id=intelligence_id,
            research_id=research_id,
            relevance_score=relevance_score
        )
        
        session.add(link)
        await session.flush()
        return link
    
    async def get_research_for_intelligence(
        self,
        intelligence_id: str,
        session: AsyncSession,
        min_relevance: float = 0.0
    ) -> List[KnowledgeBase]:
        """Get all research linked to an intelligence record."""
        stmt = select(KnowledgeBase).join(
            IntelligenceResearch,
            KnowledgeBase.id == IntelligenceResearch.research_id
        ).where(
            IntelligenceResearch.intelligence_id == intelligence_id,
            IntelligenceResearch.relevance_score >= min_relevance
        ).order_by(IntelligenceResearch.relevance_score.desc())
        
        result = await session.execute(stmt)
        return result.scalars().all()