"""
Base models and mixins - EMERGENCY FIX for production circular imports
"""

from sqlalchemy import Column, DateTime, Boolean, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from uuid import uuid4

# Create base directly - avoid importing from src.core.database
Base = declarative_base()

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UUIDMixin:
    """Mixin for UUID primary key"""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

class BaseModel(Base, UUIDMixin, TimestampMixin):
    """Base model with common fields"""
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

# EMERGENCY FIX: Don't import ANY models in __init__.py
# This prevents circular imports completely
# Models will be imported directly where needed

__all__ = [
    "BaseModel", 
    "Base",
    "TimestampMixin", 
    "UUIDMixin",
]