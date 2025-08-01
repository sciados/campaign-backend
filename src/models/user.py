# src/models/user.py - TEMPORARILY DISABLE STORAGE RELATIONSHIP
"""
User model and related schemas - Updated with storage tracking
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

# Import from our clean base module
from .base import BaseModel

class User(BaseModel):
    """User model - Updated with storage tracking fields"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    avatar_url = Column(Text)
    
    # Company Relationship
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    role = Column(String(50), default="owner")  # owner, admin, member, viewer
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # User Preferences (personal, not company-wide)
    preferences = Column(JSONB, default={})
    settings = Column(JSONB, default={})
    
    # 🆕 STORAGE TRACKING FIELDS
    storage_used_bytes = Column(Integer, default=0, nullable=False)
    storage_limit_bytes = Column(Integer, default=1073741824, nullable=False)  # 1GB default (free tier)
    storage_tier = Column(String(20), default="free", nullable=False)  # free, pro, enterprise
    last_storage_check = Column(DateTime, nullable=True)
    
    # Clean relationships (will work once all models use proper imports)
    company = relationship("Company", back_populates="users")
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    
    # Intelligence relationships
    intelligence_sources = relationship("CampaignIntelligence", back_populates="user")
    generated_content = relationship("GeneratedContent", back_populates="user")
    smart_urls = relationship("SmartURL", back_populates="user")
    
    # Company membership relationships
    company_memberships = relationship(
        "CompanyMembership", 
        foreign_keys="CompanyMembership.user_id",
        back_populates="user"
    )
    
    # Asset relationships
    # uploaded_assets = relationship("src.models.campaign_assets.CampaignAsset", back_populates="uploader")
    
    # Invitations sent by this user (as inviter)
    sent_invitations = relationship(
        "CompanyInvitation",
        foreign_keys="CompanyInvitation.invited_by", 
        back_populates="inviter"
    )
    
    # Invitations accepted by this user (as accepter)
    accepted_invitations = relationship(
        "CompanyInvitation",
        foreign_keys="CompanyInvitation.accepted_by",
        back_populates="accepter"
    )
    
    # Memberships where this user was the inviter
    invited_memberships = relationship(
        "CompanyMembership",
        foreign_keys="CompanyMembership.invited_by",
        back_populates="inviter"
    )
    
    # 🆕 STORAGE RELATIONSHIP - TEMPORARILY DISABLED TO FIX REGISTRATION
    storage_usage = relationship("UserStorageUsage", back_populates="user", cascade="all, delete-orphan")
    
    def get_preferences(self) -> dict:
        """Get user preferences with proper handling"""
        if isinstance(self.preferences, dict):
            return self.preferences
        elif isinstance(self.preferences, str):
            try:
                import json
                return json.loads(self.preferences)
            except (json.JSONDecodeError, ValueError):
                return {}
        return {}
    
    # 🆕 STORAGE UTILITY METHODS
    def get_storage_used_mb(self) -> float:
        """Get storage used in MB"""
        return round(self.storage_used_bytes / 1024 / 1024, 2)
    
    def get_storage_limit_mb(self) -> float:
        """Get storage limit in MB"""
        return round(self.storage_limit_bytes / 1024 / 1024, 2)
    
    def get_storage_used_gb(self) -> float:
        """Get storage used in GB"""
        return round(self.storage_used_bytes / 1024 / 1024 / 1024, 2)
    
    def get_storage_limit_gb(self) -> float:
        """Get storage limit in GB"""
        return round(self.storage_limit_bytes / 1024 / 1024 / 1024, 2)
    
    def get_storage_usage_percentage(self) -> float:
        """Get storage usage as percentage"""
        if self.storage_limit_bytes == 0:
            return 0.0
        return round((self.storage_used_bytes / self.storage_limit_bytes) * 100, 1)
    
    def has_storage_available(self, bytes_needed: int) -> bool:
        """Check if user has enough storage available"""
        return (self.storage_used_bytes + bytes_needed) <= self.storage_limit_bytes
    
    def get_storage_available_bytes(self) -> int:
        """Get available storage in bytes"""
        return max(0, self.storage_limit_bytes - self.storage_used_bytes)
    
    def get_storage_tier_info(self) -> dict:
        """Get storage tier information"""
        try:
            from ..storage.storage_tiers import STORAGE_TIERS
            return STORAGE_TIERS.get(self.storage_tier, STORAGE_TIERS["free"])
        except ImportError:
            # Return default if storage_tiers not available
            return {
                "limit_gb": 1,
                "limit_bytes": 1073741824,
                "max_file_size_mb": 10,
                "price_monthly": 0
            }
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}', storage_tier='{self.storage_tier}')>"