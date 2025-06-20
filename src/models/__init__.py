"""
Base models and mixins - FIXED VERSION
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

# Import all models in correct order to avoid circular imports
from .user import User
from .company import (
    Company, 
    CompanyMembership, 
    CompanyInvitation,
    CompanySize,
    CompanySubscriptionTier,
    MembershipRole,
    MembershipStatus,
    InvitationStatus
)
from .campaign import Campaign, CampaignType, CampaignStatus, CampaignWorkflowState, WorkflowPreference
from .intelligence import (
    CampaignIntelligence,
    GeneratedContent,
    SmartURL,
    IntelligenceSourceType,
    AnalysisStatus
)

__all__ = [
    # Base classes
    "BaseModel", 
    "TimestampMixin", 
    "UUIDMixin",
    
    # User models
    "User",
    
    # Company models
    "Company",
    "CompanyMembership",
    "CompanyInvitation",
    
    # Company enums
    "CompanySize",
    "CompanySubscriptionTier", 
    "MembershipRole",
    "MembershipStatus",
    "InvitationStatus",
    
    # Campaign models
    "Campaign", 
    "CampaignType", 
    "CampaignStatus",
    "CampaignWorkflowState",
    "WorkflowPreference",
    
    # Intelligence models
    "CampaignIntelligence",
    "GeneratedContent", 
    "SmartURL",
    "IntelligenceSourceType",
    "AnalysisStatus"
]