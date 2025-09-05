# =====================================
# File: src/core/interfaces/service_interfaces.py
# =====================================

"""
Service layer interfaces for CampaignForge business logic.

Defines standard CRUD and business logic interfaces that all
service classes should implement for consistency.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)


class ServiceInterface(Generic[T, CreateSchema, UpdateSchema], ABC):
    """
    Base service interface for business logic operations.
    
    Provides standard CRUD operations and business logic patterns
    that all service classes should implement.
    """
    
    @abstractmethod
    async def create(self, data: CreateSchema, user_id: str) -> T:
        """
        Create a new entity.
        
        Args:
            data: Creation data schema
            user_id: ID of the user creating the entity
            
        Returns:
            T: Created entity
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str, user_id: str) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: ID of the entity to retrieve
            user_id: ID of the requesting user
            
        Returns:
            Optional[T]: Entity if found and accessible, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        user_id: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[T]:
        """
        Get all entities for a user with optional filtering.
        
        Args:
            user_id: ID of the requesting user
            filters: Optional filtering criteria
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List[T]: List of entities
        """
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, data: UpdateSchema, user_id: str) -> Optional[T]:
        """
        Update an entity.
        
        Args:
            entity_id: ID of the entity to update
            data: Update data schema
            user_id: ID of the user updating the entity
            
        Returns:
            Optional[T]: Updated entity if successful, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str, user_id: str) -> bool:
        """
        Delete an entity.
        
        Args:
            entity_id: ID of the entity to delete
            user_id: ID of the user deleting the entity
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        pass
    
    async def count(self, user_id: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities for a user with optional filtering.
        
        Args:
            user_id: ID of the requesting user
            filters: Optional filtering criteria
            
        Returns:
            int: Number of entities
        """
        return 0
    
    async def exists(self, entity_id: str, user_id: str) -> bool:
        """
        Check if entity exists and is accessible to user.
        
        Args:
            entity_id: ID of the entity to check
            user_id: ID of the requesting user
            
        Returns:
            bool: True if entity exists and is accessible
        """
        entity = await self.get_by_id(entity_id, user_id)
        return entity is not None