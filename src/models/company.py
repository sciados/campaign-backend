# src/models/company.py - FIXED VERSION with missing field
"""
Company models and related schemas - FIXED VERSION
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from src.models import BaseModel

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

class Company(BaseModel):
    """Company model"""
    __tablename__ = "companies"
    
    # Company Information
    company_name = Column(String(255), nullable=False)
    company_slug = Column(String(100), unique=True, nullable=False, index=True)
    industry = Column(String(100))
    company_size = Column(String(50), default=CompanySize.STARTUP.value)
    website_url = Column(Text)
    
    # Branding & Settings
    logo_url = Column(Text)
    brand_colors = Column(JSONB, default={})
    brand_guidelines = Column(JSONB, default={})
    
    # Subscription & Billing
    subscription_tier = Column(String(50), default=CompanySubscriptionTier.FREE.value)
    subscription_status = Column(String(50), default="active")
    billing_email = Column(String(255))
    
    # Usage Tracking - ✅ FIXED: Added missing field
    monthly_credits_used = Column(Integer, default=0)
    monthly_credits_limit = Column(Integer, default=1000)
    total_campaigns_created = Column(Integer, default=0)
    total_campaigns_created = Column(Integer, default=0)  # ← CRITICAL FIX for registration
    
    # Company Settings
    settings = Column(JSONB, default={})
    
    # Relationships - Use string references to avoid circular imports
    users = relationship("User", back_populates="company")
    campaigns = relationship("Campaign", back_populates="company")
    memberships = relationship("CompanyMembership", back_populates="company", cascade="all, delete-orphan")
    invitations = relationship("CompanyInvitation", back_populates="company", cascade="all, delete-orphan")
    
    # Asset relationships
    assets = relationship("CampaignAsset", back_populates="company")
    
    # Intelligence relationships
    intelligence_sources = relationship("CampaignIntelligence", back_populates="company")
    generated_content = relationship("GeneratedContent", back_populates="company")
    smart_urls = relationship("SmartURL", back_populates="company")

class CompanyMembership(BaseModel):
    """Company membership model for team collaboration"""
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
    
    # Relationships - FIXED
    user = relationship("User", foreign_keys=[user_id], back_populates="company_memberships")
    company = relationship("Company", back_populates="memberships")
    inviter = relationship("User", foreign_keys=[invited_by], back_populates="invited_memberships")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'company_id', name='unique_user_company_membership'),
    )

class CompanyInvitation(BaseModel):
    """Company invitation model for team invites"""
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
    
    # Relationships
    company = relationship("Company", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[invited_by], back_populates="sent_invitations")
    accepter = relationship("User", foreign_keys=[accepted_by], back_populates="accepted_invitations")