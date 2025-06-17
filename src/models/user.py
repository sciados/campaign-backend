"""
User model and related schemas
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

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
    preferences = Column(JSONB, default={})
    
    # Relationships
    company = relationship("Company", back_populates="users")
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    company_memberships = relationship("CompanyMembership", foreign_keys="CompanyMembership.user_id")