# src/core/crud/base_crud.py
"""
Centralized CRUD Operations - Base Repository Pattern
🏗️ Single source of truth for all database operations
✅ Consistent async handling across all services
✅ Unified error handling and logging
"""

from typing import Generic, TypeVar, Type, List, Optional, Dict, Any, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
import logging

from src.models.base import BaseModel

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseCRUD(Generic[ModelType]):
    """
    Base CRUD repository with consistent database access patterns
    🔧 Designed to eliminate ChunkedIteratorResult and other async issues
    ✅ Proven async patterns that work reliably
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.model_name = model.__name__
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        """Get single record by ID with consistent async handling"""
        try:
            logger.debug(f"🔍 Getting {self.model_name} by ID: {id}")
            
            query = select(self.model).where(self.model.id == id)
            result = await db.execute(query)
            record = result.scalar_one_or_none()
            
            if record:
                logger.debug(f"✅ Found {self.model_name}: {id}")
            else:
                logger.debug(f"❌ {self.model_name} not found: {id}")
                
            return record
            
        except Exception as e:
            logger.error(f"❌ Error getting {self.model_name} {id}: {e}")
            raise
    
    async def get_by_field(
        self, 
        db: AsyncSession, 
        field_name: str, 
        field_value: Any
    ) -> Optional[ModelType]:
        """Get single record by any field"""
        try:
            logger.debug(f"🔍 Getting {self.model_name} by {field_name}: {field_value}")
            
            if not hasattr(self.model, field_name):
                raise ValueError(f"Field {field_name} does not exist on {self.model_name}")
            
            field = getattr(self.model, field_name)
            query = select(self.model).where(field == field_value)
            result = await db.execute(query)
            record = result.scalar_one_or_none()
            
            if record:
                logger.debug(f"✅ Found {self.model_name} by {field_name}")
            else:
                logger.debug(f"❌ {self.model_name} not found by {field_name}: {field_value}")
                
            return record
            
        except Exception as e:
            logger.error(f"❌ Error getting {self.model_name} by {field_name}: {e}")
            raise
    
    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = True
    ) -> List[ModelType]:
        """
        Get multiple records with filters and ordering
        🔧 Uses proven async patterns to avoid ChunkedIteratorResult
        """
        try:
            logger.debug(f"🔍 Getting multiple {self.model_name} records")
            
            query = select(self.model)
            
            # Apply filters
            if filters:
                for field_name, field_value in filters.items():
                    if hasattr(self.model, field_name):
                        field = getattr(self.model, field_name)
                        if isinstance(field_value, list):
                            query = query.where(field.in_(field_value))
                        else:
                            query = query.where(field == field_value)
                    else:
                        logger.warning(f"⚠️ Field {field_name} does not exist on {self.model_name}")
            
            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                order_field = getattr(self.model, order_by)
                if order_desc:
                    query = query.order_by(desc(order_field))
                else:
                    query = query.order_by(asc(order_field))
            elif hasattr(self.model, 'created_at'):
                # Default ordering by created_at if available
                query = query.order_by(desc(self.model.created_at))
            elif hasattr(self.model, 'updated_at'):
                # Fallback to updated_at
                query = query.order_by(desc(self.model.updated_at))
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            # Execute query with proven async pattern
            result = await db.execute(query)
            records = result.scalars().all()
            
            logger.debug(f"✅ Found {len(records)} {self.model_name} records")
            return records
            
        except Exception as e:
            logger.error(f"❌ Error getting multiple {self.model_name}: {e}")
            raise
    
    async def get_multi_by_field(
        self,
        db: AsyncSession,
        field_name: str,
        field_values: List[Any],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records where field is in a list of values"""
        try:
            if not hasattr(self.model, field_name):
                raise ValueError(f"Field {field_name} does not exist on {self.model_name}")
            
            field = getattr(self.model, field_name)
            query = select(self.model).where(field.in_(field_values))
            query = query.offset(skip).limit(limit)
            
            result = await db.execute(query)
            records = result.scalars().all()
            
            logger.debug(f"✅ Found {len(records)} {self.model_name} records by {field_name}")
            return records
            
        except Exception as e:
            logger.error(f"❌ Error getting {self.model_name} by {field_name} list: {e}")
            raise
    
    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> ModelType:
        """Create new record with proper error handling"""
        try:
            logger.debug(f"🔨 Creating {self.model_name}")
            
            # Create new instance
            db_obj = self.model(**obj_in)
            db.add(db_obj)
            
            # Commit and refresh
            await db.commit()
            await db.refresh(db_obj)
            
            # Handle models that don't have an 'id' attribute
            if hasattr(db_obj, 'id'):
                logger.info(f"✅ Created {self.model_name}: {db_obj.id}")
            else:
                # For models like ProductData that use composite/foreign keys as primary key
                logger.info(f"✅ Created {self.model_name}: {type(db_obj).__name__}")
            return db_obj
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error creating {self.model_name}: {e}")
            raise
    
    async def update(
        self, 
        db: AsyncSession, 
        db_obj: ModelType, 
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """Update existing record"""
        try:
            logger.debug(f"🔧 Updating {self.model_name}: {db_obj.id}")
            
            # Update fields
            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
                else:
                    logger.warning(f"⚠️ Field {field} does not exist on {self.model_name}")
            
            # Update timestamp if available
            if hasattr(db_obj, 'updated_at'):
                from datetime import datetime, timezone
                db_obj.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(db_obj)
            
            logger.info(f"✅ Updated {self.model_name}: {db_obj.id}")
            return db_obj
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error updating {self.model_name}: {e}")
            raise
    
    async def update_by_id(
        self,
        db: AsyncSession,
        id: UUID,
        obj_in: Dict[str, Any]
    ) -> Optional[ModelType]:
        """Update record by ID (convenience method)"""
        db_obj = await self.get(db=db, id=id)
        if not db_obj:
            return None
        
        return await self.update(db=db, db_obj=db_obj, obj_in=obj_in)
    
    async def delete(self, db: AsyncSession, id: UUID) -> bool:
        """Delete record by ID"""
        try:
            logger.debug(f"🗑️ Deleting {self.model_name}: {id}")
            
            # Check if record exists first
            existing = await self.get(db=db, id=id)
            if not existing:
                logger.warning(f"⚠️ {self.model_name} not found for deletion: {id}")
                return False
            
            # Delete the record
            query = delete(self.model).where(self.model.id == id)
            result = await db.execute(query)
            await db.commit()
            
            success = result.rowcount > 0
            if success:
                logger.info(f"✅ Deleted {self.model_name}: {id}")
            else:
                logger.warning(f"⚠️ No rows deleted for {self.model_name}: {id}")
                
            return success
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error deleting {self.model_name} {id}: {e}")
            raise
    
    async def count(
        self,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count records with optional filters"""
        try:
            from sqlalchemy import func
            
            query = select(func.count(self.model.id))
            
            # Apply filters
            if filters:
                for field_name, field_value in filters.items():
                    if hasattr(self.model, field_name):
                        field = getattr(self.model, field_name)
                        query = query.where(field == field_value)
            
            result = await db.execute(query)
            count = result.scalar()
            
            logger.debug(f"📊 Count {self.model_name}: {count}")
            return count or 0
            
        except Exception as e:
            logger.error(f"❌ Error counting {self.model_name}: {e}")
            raise
    
    async def exists(
        self,
        db: AsyncSession,
        filters: Dict[str, Any]
    ) -> bool:
        """Check if record exists with given filters"""
        try:
            query = select(self.model.id)
            
            for field_name, field_value in filters.items():
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    query = query.where(field == field_value)
            
            query = query.limit(1)
            result = await db.execute(query)
            exists = result.scalar_one_or_none() is not None
            
            logger.debug(f"🔍 Exists {self.model_name}: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"❌ Error checking {self.model_name} existence: {e}")
            raise