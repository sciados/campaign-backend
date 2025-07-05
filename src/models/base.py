# src/models/base.py - Permanent base models and utilities
"""
Base models and utilities for all model classes
"""

import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4

# Create the declarative base
Base = declarative_base()

class BaseModel(Base):
    """Base model with common fields for all tables"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class EnumSerializerMixin:
    """Mixin for proper enum field serialization"""
    
    def _serialize_enum_field(self, field_value):
        """Serialize enum field to proper format"""
        if field_value is None:
            return {}
        
        if isinstance(field_value, dict):
            return field_value
        
        if isinstance(field_value, str):
            try:
                return json.loads(field_value)
            except (json.JSONDecodeError, ValueError):
                return {}
        
        return {}