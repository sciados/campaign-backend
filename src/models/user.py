"""
User model and related schemas - FIXED VERSION
"""

import json
from intelligence.amplifier import sources
from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from src.intelligence.utils.enum_serializer import EnumSerializerMixin

from src.models import BaseModel

class User(BaseModel):
    """User model"""
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
    json.loads(sources.preferences).get("research_data")
    
    # Relationships - Use string references to avoid circular imports
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
    uploaded_assets = relationship("CampaignAsset", back_populates="uploader")
    
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