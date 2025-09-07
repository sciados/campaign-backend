# =====================================
# File: src/core/interfaces/repository_interfaces.py
# =====================================

"""
Repository pattern interfaces for CampaignForge data access layer.

Defines standard data access patterns that all repository classes
should implement for consistent database operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generic, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.models import Base

T = TypeVar('T', bound=Base)


class RepositoryInterface(Generic[T], ABC):
    """
    Base repository interface for data access operations.
    
    Provides standard CRUD operations and query patterns
    that all repository classes should implement.
    """
    
    @abstractmethod
    async def save(self, entity: T, session: AsyncSession) -> T:
        """
        Save an entity to the database.
        
        Args:
            entity: Entity to save
            session: Database session
            
        Returns:
            T: Saved entity
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, entity_id: str, session: AsyncSession) -> Optional[T]:
        """
        Find entity by ID.
        
        Args:
            entity_id: ID of the entity to find
            session: Database session
            
        Returns:
            Optional[T]: Entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def find_all(
        self, 
        session: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[T]:
        """
        Find all entities with optional filtering.
        
        Args:
            session: Database session
            filters: Optional filtering criteria
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List[T]: List of entities
        """
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, data: Dict[str, Any], session: AsyncSession) -> Optional[T]:
        """
        Update an entity.
        
        Args:
            entity_id: ID of the entity to update
            data: Update data
            session: Database session
            
        Returns:
            Optional[T]: Updated entity if successful, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete_by_id(self, entity_id: str, session: AsyncSession) -> bool:
        """
        Delete entity by ID.
        
        Args:
            entity_id: ID of the entity to delete
            session: Database session
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        pass
    
    async def count(
        self, 
        session: AsyncSession,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count entities with optional filtering.
        
        Args:
            session: Database session
            filters: Optional filtering criteria
            
        Returns:
            int: Number of entities
        """
        return 0
    
    async def exists(self, entity_id: str, session: AsyncSession) -> bool:
        """
        Check if entity exists.
        
        Args:
            entity_id: ID of the entity to check
            session: Database session
            
        Returns:
            bool: True if entity exists
        """
        entity = await self.find_by_id(entity_id, session)
        return entity is not None