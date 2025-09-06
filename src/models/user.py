# File: src/models/user.py

# User and Company models to match existing database tables

from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import bcrypt
import uuid

from src.core.database.models import Base, TimestampMixin

class Company(Base, TimestampMixin):
    """Company model matching existing database table"""
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False)
    company_slug = Column(String(255), unique=True, nullable=False)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    website_url = Column(String(255), nullable=True)
    
    # Subscription info
    subscription_tier = Column(String(50), default="free")
    subscription_status = Column(String(50), default="active")
    monthly_credits_used = Column(Integer, default=0)
    monthly_credits_limit = Column(Integer, default=1000)
    
    # Relationships
    users = relationship("User", back_populates="company")
    campaigns = relationship("Campaign", back_populates="company")  # Added missing relationship

class User(Base, TimestampMixin):
    """User model matching existing database table"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User type and role
    role = Column(String(50), default="user")  # user, admin
    user_type = Column(String(50), nullable=True)  # affiliate_marketer, content_creator, business_owner
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Company relationship
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Profile information
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    timezone = Column(String(100), default="UTC")
    
    # Onboarding status
    onboarding_completed = Column(Boolean, default=False)
    onboarding_step = Column(Integer, default=0)
    
    # Usage tracking
    monthly_campaigns_used = Column(Integer, default=0)
    monthly_analysis_used = Column(Integer, default=0)
    total_campaigns_created = Column(Integer, default=0)
    total_intelligence_generated = Column(Integer, default=0)
    total_content_generated = Column(Integer, default=0)
    
    # Timestamps
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="users")
    campaigns = relationship("Campaign", back_populates="user")  # Added missing relationship
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                self.hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storage"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def set_password(self, password: str) -> None:
        """Set and hash a new password"""
        self.hashed_password = self.hash_password(password)
    
    def set_user_type(self, user_type: str, type_data: Optional[Dict[str, Any]] = None) -> None:
        """Set user type and handle type-specific data"""
        self.user_type = user_type
        self.updated_at = datetime.now(timezone.utc)
        
        # Handle type-specific logic if needed
        if type_data:
            # Store type-specific data in bio or other fields as needed
            pass
    
    def complete_onboarding(
        self, 
        goals: Optional[List[str]] = None, 
        experience_level: str = "beginner"
    ) -> None:
        """Mark onboarding as complete"""
        self.onboarding_completed = True
        self.onboarding_step = 100  # Completed
        self.updated_at = datetime.now(timezone.utc)
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get user usage statistics"""
        return {
            "user_id": self.id,
            "monthly_campaigns_used": self.monthly_campaigns_used or 0,
            "monthly_analysis_used": self.monthly_analysis_used or 0,
            "total_campaigns_created": self.total_campaigns_created or 0,
            "total_intelligence_generated": self.total_intelligence_generated or 0,
            "total_content_generated": self.total_content_generated or 0,
            "subscription_tier": self.company.subscription_tier if self.company else "free",
            "monthly_credits_limit": self.company.monthly_credits_limit if self.company else 1000,
            "monthly_credits_used": self.company.monthly_credits_used if self.company else 0
        }
    
    def __repr__(self):
        return f"<User(email='{self.email}', full_name='{self.full_name}')>"