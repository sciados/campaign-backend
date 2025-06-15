"""
Base models and mixins
"""

from sqlalchemy import Column, DateTime, Boolean, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from uuid import uuid4

from src.core.database import Base

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

# Import all models to make them available
from .user import User, SubscriptionTier
from .campaign import Campaign, CampaignAsset, CampaignType, CampaignStatus, AssetType

__all__ = [
    "BaseModel", 
    "TimestampMixin", 
    "UUIDMixin",
    "User", 
    "SubscriptionTier",
    "Campaign", 
    "CampaignAsset", 
    "CampaignType", 
    "CampaignStatus", 
    "AssetType"
]