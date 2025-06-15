"""
User model and related schemas
"""

from sqlalchemy import Column, String, Boolean, Integer, Enum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from src.models import BaseModel

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    AGENCY = "agency"
    ENTERPRISE = "enterprise"

class User(BaseModel):
    """User model"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    avatar_url = Column(Text)
    
    # Subscription
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_status = Column(String(50), default="active")
    credits_remaining = Column(Integer, default=1000)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Preferences
    preferences = Column(JSONB)
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    brand_settings = relationship("BrandSetting", back_populates="user")