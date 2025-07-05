"""
Base models and mixins - SIMPLIFIED VERSION to fix circular imports
"""

from sqlalchemy import Column, DateTime, Boolean, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from uuid import uuid4

# Create base directly here to avoid circular imports
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

# SIMPLIFIED: Only import what we need for the migration
# This avoids the circular import issue with the async database engine
try:
    from .intelligence import (
        CampaignIntelligence,
        GeneratedContent,
        SmartURL,
        IntelligenceSourceType,
        AnalysisStatus
    )
    INTELLIGENCE_MODELS_AVAILABLE = True
except ImportError as e:
    INTELLIGENCE_MODELS_AVAILABLE = False
    print(f"Intelligence models not available: {e}")

# Minimal exports for migration
__all__ = [
    "BaseModel", 
    "Base",
    "TimestampMixin", 
    "UUIDMixin",
]

# Add intelligence models if available
if INTELLIGENCE_MODELS_AVAILABLE:
    __all__.extend([
        "CampaignIntelligence",
        "GeneratedContent", 
        "SmartURL",
        "IntelligenceSourceType",
        "AnalysisStatus"
    ])