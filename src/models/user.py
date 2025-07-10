# src/models/user.py - PERMANENT CLEAN VERSION
"""
User model and related schemas - Clean permanent version
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

# Import from our clean base module
from .base import BaseModel

class User(BaseModel):
    """User model - Clean permanent version"""
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
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"