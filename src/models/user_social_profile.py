# src/models/user_social_profile.py
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import BaseModel

class UserSocialProfile(BaseModel):
    __tablename__ = "user_social_profiles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    platform = Column(String(50), nullable=False)  # instagram, linkedin, tiktok, etc
    username = Column(String(100))
    display_name = Column(String(200))
    
    # Core metrics (all platforms)
    followers = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    avg_monthly_reach = Column(Integer, default=0)
    
    # Connection status
    is_primary_platform = Column(Boolean, default=False)
    is_connected_via_api = Column(Boolean, default=False)
    manual_input = Column(Boolean, default=True)
    
    # Platform-specific data storage
    platform_metrics = Column(JSONB, default={})
    
    # API integration
    api_token_encrypted = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="social_profiles")

# Add to User model
class User(BaseModel):
    # ... existing fields ...
    
    # Add relationship
    social_profiles = relationship("UserSocialProfile", back_populates="user", cascade="all, delete-orphan")