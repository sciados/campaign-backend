# src/models/company.py - FINAL FIX to remove circular import
"""
Company models and related schemas - FINAL FIX VERSION
"""

import json
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

# EMERGENCY FIX: Create enum serializer here to avoid circular import
class EnumSerializerMixin:
    """Simple enum serializer to avoid import issues"""
    
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

# EMERGENCY FIX: Import BaseModel directly to avoid circular import
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4

# Create base directly to avoid circular imports
Base = declarative_base()

class BaseModel(Base):
    """Emergency base model to avoid circular imports"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class CompanySize(str, enum.Enum):
    STARTUP = "startup"
    SMALL = "small" 
    MEDIUM = "medium"
    ENTERPRISE = "enterprise"

class CompanySubscriptionTier(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    AGENCY = "agency"
    ENTERPRISE = "enterprise"

class MembershipRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class MembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"

class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class Company(BaseModel, EnumSerializerMixin):
    """Company model - EMERGENCY FIX VERSION"""
    __tablename__ = "companies"
    
    # Company Information
    company_name = Column(String(255), nullable=False)
    company_slug = Column(String(100), unique=True, nullable=False, index=True)
    industry = Column(String(100))
    company_size = Column(String(50), default=CompanySize.STARTUP.value)
    website_url = Column(Text)
    
    # Branding & Settings - FIXED: Proper JSONB column definitions
    logo_url = Column(Text)
    brand_colors = Column(JSONB, default={})
    brand_guidelines = Column(JSONB, default={})
    
    # Subscription & Billing
    subscription_tier = Column(String(50), default=CompanySubscriptionTier.FREE.value)
    subscription_status = Column(String(50), default="active")
    billing_email = Column(String(255))
    
    # Usage Tracking
    monthly_credits_used = Column(Integer, default=0)
    monthly_credits_limit = Column(Integer, default=1000)
    total_campaigns_created = Column(Integer, default=0)
    
    # Company Settings - FIXED: Proper JSONB column definition
    settings = Column(JSONB, default={})
    
    # EMERGENCY FIX: Remove relationships to avoid circular imports
    # Relationships will be defined elsewhere if needed
    
    def get_branding_settings(self) -> dict:
        """Get branding settings with proper enum serialization"""
        return {
            "brand_colors": self._serialize_enum_field(self.brand_colors),
            "brand_guidelines": self._serialize_enum_field(self.brand_guidelines)
        }
    
    def get_company_settings(self) -> dict:
        """Get company settings with proper enum serialization"""
        return self._serialize_enum_field(self.settings)

class CompanyMembership(BaseModel, EnumSerializerMixin):
    """Company membership model for team collaboration - EMERGENCY FIX VERSION"""
    __tablename__ = "company_memberships"
    
    # Relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Role & Permissions
    role = Column(String(50), nullable=False, default=MembershipRole.MEMBER.value)
    permissions = Column(JSONB, default={})
    
    # Status
    status = Column(String(50), default=MembershipStatus.ACTIVE.value)
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    invited_at = Column(DateTime(timezone=True))
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # EMERGENCY FIX: Remove relationships to avoid circular imports
    
    __table_args__ = (
        UniqueConstraint('user_id', 'company_id', name='unique_user_company_membership'),
    )
    
    def get_permissions(self) -> dict:
        """Get permissions with proper enum serialization"""
        return self._serialize_enum_field(self.permissions)

class CompanyInvitation(BaseModel):
    """Company invitation model for team invites - EMERGENCY FIX VERSION"""
    __tablename__ = "company_invitations"
    
    # Invitation Details
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=MembershipRole.MEMBER.value)
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Status & Expiry
    status = Column(String(50), default=InvitationStatus.PENDING.value)
    expires_at = Column(DateTime(timezone=True), server_default=func.now() + func.make_interval(0, 0, 0, 7, 0, 0, 0))
    accepted_at = Column(DateTime(timezone=True))
    accepted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Security (will be populated by backend)
    invitation_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # EMERGENCY FIX: Remove relationships to avoid circular imports