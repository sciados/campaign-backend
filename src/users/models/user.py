# src/users/models/user.py
"""
User and Company models for the Users module
Consolidated from original models with enhanced functionality
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
import bcrypt
import uuid
import enum

from src.core.database.base import Base

class UserTypeEnum(str, enum.Enum):
    """User type enumeration for different user categories"""
    AFFILIATE_MARKETER = "affiliate_marketer"
    CONTENT_CREATOR = "content_creator"
    BUSINESS_OWNER = "business_owner"

class UserRoleEnum(str, enum.Enum):
    """User role enumeration for permissions"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class SubscriptionTierEnum(str, enum.Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class Company(Base):
    """Company model for user organizations"""
    __tablename__ = "companies"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False)
    company_slug = Column(String(255), unique=True, nullable=False, index=True)
    
    # Company details
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    website_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Subscription and billing
    subscription_tier = Column(Enum(SubscriptionTierEnum), default=SubscriptionTierEnum.FREE, nullable=False)
    subscription_status = Column(String(50), default="active")
    monthly_credits_used = Column(Integer, default=0)
    monthly_credits_limit = Column(Integer, default=1000)
    
    # Contact information
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    billing_address = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    
    def get_usage_percentage(self) -> float:
        """Get percentage of monthly credits used"""
        if self.monthly_credits_limit <= 0:
            return 0.0
        return min((self.monthly_credits_used / self.monthly_credits_limit) * 100, 100.0)
    
    def can_use_credits(self, amount: int = 1) -> bool:
        """Check if company can use specified amount of credits"""
        return (self.monthly_credits_used + amount) <= self.monthly_credits_limit
    
    def use_credits(self, amount: int = 1) -> bool:
        """Use credits if available"""
        if self.can_use_credits(amount):
            self.monthly_credits_used = (self.monthly_credits_used or 0) + amount
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def reset_monthly_credits(self) -> None:
        """Reset monthly credit usage (called by cron job)"""
        self.monthly_credits_used = 0
        self.updated_at = datetime.now(timezone.utc)
    
    def __repr__(self):
        return f"<Company(name='{self.company_name}', tier='{self.subscription_tier}')>"

class User(Base):
    """User model with comprehensive profile and usage tracking"""
    __tablename__ = "users"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User classification
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.USER, nullable=False)
    user_type = Column(Enum(UserTypeEnum), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)  # For backwards compatibility and dashboard access
    
    # Company relationship
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Profile information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    profile_image_url = Column(String(500), nullable=True)  # Alternative field name
    bio = Column(Text, nullable=True)
    timezone = Column(String(100), default="UTC")
    phone_number = Column(String(50), nullable=True)
    
    # Preferences
    dashboard_preferences = Column(Text, nullable=True)  # JSON string for dashboard settings
    notification_preferences = Column(Text, nullable=True)  # JSON string for notification settings
    language = Column(String(10), default="en")
    theme = Column(String(20), default="light")
    
    # Onboarding workflow
    onboarding_completed = Column(Boolean, default=False)
    onboarding_step = Column(Integer, default=0)
    onboarding_data = Column(Text, nullable=True)  # JSON string for onboarding progress
    
    # Usage tracking - Monthly limits
    monthly_campaigns_used = Column(Integer, default=0)
    monthly_analysis_used = Column(Integer, default=0)
    monthly_content_generated = Column(Integer, default=0)
    monthly_intelligence_generated = Column(Integer, default=0)
    
    # Usage tracking - Lifetime totals
    total_campaigns_created = Column(Integer, default=0)
    total_analysis_performed = Column(Integer, default=0)
    total_intelligence_generated = Column(Integer, default=0)
    total_content_generated = Column(Integer, default=0)
    total_logins = Column(Integer, default=0)
    
    # User experience and goals
    experience_level = Column(String(50), default="beginner")  # beginner, intermediate, advanced
    primary_goals = Column(Text, nullable=True)  # JSON array of goals
    
    # Activity tracking
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="users")
    
    # Password management
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
        self.updated_at = datetime.now(timezone.utc)
    
    # User type management
    def set_user_type(self, user_type: Union[UserTypeEnum, str], type_data: Optional[Dict[str, Any]] = None) -> None:
        """Set user type and handle type-specific data"""
        # Accept either enum or string
        if isinstance(user_type, UserTypeEnum):
            self.user_type = user_type
        elif isinstance(user_type, str):
            # Validate string against enum values
            try:
                self.user_type = UserTypeEnum(user_type)
            except ValueError:
                valid_values = [e.value for e in UserTypeEnum]
                raise ValueError(f"Invalid user_type: {user_type}. Must be one of: {valid_values}")
        else:
            raise TypeError(f"user_type must be UserTypeEnum or str, got {type(user_type)}")
        
        self.updated_at = datetime.now(timezone.utc)
        
        # Store type-specific data in onboarding_data if provided
        if type_data:
            import json
            existing_data = {}
            if self.onboarding_data:
                try:
                    existing_data = json.loads(self.onboarding_data)
                except json.JSONDecodeError:
                    existing_data = {}
            
            existing_data.update({"type_data": type_data})
            self.onboarding_data = json.dumps(existing_data)
    
    # Role management
    def set_role(self, role: Union[UserRoleEnum, str]) -> None:
        """Set user role"""
        if isinstance(role, UserRoleEnum):
            self.role = role
        elif isinstance(role, str):
            try:
                self.role = UserRoleEnum(role)
            except ValueError:
                valid_values = [e.value for e in UserRoleEnum]
                raise ValueError(f"Invalid role: {role}. Must be one of: {valid_values}")
        else:
            raise TypeError(f"role must be UserRoleEnum or str, got {type(role)}")
        
        # Update is_admin for backwards compatibility
        self.is_admin = (self.role == UserRoleEnum.ADMIN)
        self.updated_at = datetime.now(timezone.utc)
    
    # Onboarding management
    def complete_onboarding(
        self, 
        goals: Optional[List[str]] = None, 
        experience_level: str = "beginner"
    ) -> None:
        """Mark onboarding as complete"""
        self.onboarding_completed = True
        self.onboarding_step = 100  # Completed
        self.experience_level = experience_level
        
        if goals:
            import json
            self.primary_goals = json.dumps(goals)
        
        self.updated_at = datetime.now(timezone.utc)
    
    def update_onboarding_step(self, step: int, step_data: Optional[Dict[str, Any]] = None) -> None:
        """Update onboarding progress"""
        self.onboarding_step = step
        
        if step_data:
            import json
            existing_data = {}
            if self.onboarding_data:
                try:
                    existing_data = json.loads(self.onboarding_data)
                except json.JSONDecodeError:
                    existing_data = {}
            
            existing_data.update({f"step_{step}": step_data})
            self.onboarding_data = json.dumps(existing_data)
        
        self.updated_at = datetime.now(timezone.utc)
    
    # Activity tracking
    def record_login(self) -> None:
        """Record a login event"""
        self.last_login_at = datetime.now(timezone.utc)
        self.last_activity_at = datetime.now(timezone.utc)
        self.login_count = (self.login_count or 0) + 1
        self.total_logins = (self.total_logins or 0) + 1
    
    def record_activity(self) -> None:
        """Record user activity"""
        self.last_activity_at = datetime.now(timezone.utc)
    
    # Usage tracking
    def increment_usage(
        self,
        campaigns: int = 0,
        analysis: int = 0,
        intelligence: int = 0,
        content: int = 0
    ) -> None:
        """Increment usage counters"""
        if campaigns > 0:
            self.monthly_campaigns_used = (self.monthly_campaigns_used or 0) + campaigns
            self.total_campaigns_created = (self.total_campaigns_created or 0) + campaigns
        
        if analysis > 0:
            self.monthly_analysis_used = (self.monthly_analysis_used or 0) + analysis
            self.total_analysis_performed = (self.total_analysis_performed or 0) + analysis
        
        if intelligence > 0:
            self.monthly_intelligence_generated = (self.monthly_intelligence_generated or 0) + intelligence
            self.total_intelligence_generated = (self.total_intelligence_generated or 0) + intelligence
        
        if content > 0:
            self.monthly_content_generated = (self.monthly_content_generated or 0) + content
            self.total_content_generated = (self.total_content_generated or 0) + content
        
        self.updated_at = datetime.now(timezone.utc)
    
    def reset_monthly_usage(self) -> None:
        """Reset monthly usage counters (called by cron job)"""
        self.monthly_campaigns_used = 0
        self.monthly_analysis_used = 0
        self.monthly_content_generated = 0
        self.monthly_intelligence_generated = 0
        self.updated_at = datetime.now(timezone.utc)
    
    # Usage summary and statistics
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get comprehensive user usage statistics"""
        return {
            "user_id": str(self.id),
            "monthly_usage": {
                "campaigns_used": self.monthly_campaigns_used or 0,
                "analysis_used": self.monthly_analysis_used or 0,
                "intelligence_generated": self.monthly_intelligence_generated or 0,
                "content_generated": self.monthly_content_generated or 0,
            },
            "lifetime_totals": {
                "campaigns_created": self.total_campaigns_created or 0,
                "analysis_performed": self.total_analysis_performed or 0,
                "intelligence_generated": self.total_intelligence_generated or 0,
                "content_generated": self.total_content_generated or 0,
                "total_logins": self.total_logins or 0,
            },
            "subscription_info": {
                "tier": self.company.subscription_tier.value if self.company else "free",
                "monthly_credits_limit": self.company.monthly_credits_limit if self.company else 1000,
                "monthly_credits_used": self.company.monthly_credits_used if self.company else 0,
                "credits_remaining": (self.company.monthly_credits_limit or 1000) - (self.company.monthly_credits_used or 0) if self.company else 1000,
            },
            "account_info": {
                "member_since": self.created_at.isoformat() if self.created_at else None,
                "last_login": self.last_login_at.isoformat() if self.last_login_at else None,
                "last_activity": self.last_activity_at.isoformat() if self.last_activity_at else None,
                "login_count": self.login_count or 0,
            }
        }
    
    # Preferences management
    def update_dashboard_preferences(self, preferences: Dict[str, Any]) -> None:
        """Update dashboard preferences"""
        import json
        self.dashboard_preferences = json.dumps(preferences)
        self.updated_at = datetime.now(timezone.utc)
    
    def get_dashboard_preferences(self) -> Dict[str, Any]:
        """Get dashboard preferences"""
        if not self.dashboard_preferences:
            return {}
        
        try:
            import json
            return json.loads(self.dashboard_preferences)
        except json.JSONDecodeError:
            return {}
    
    def update_notification_preferences(self, preferences: Dict[str, Any]) -> None:
        """Update notification preferences"""
        import json
        self.notification_preferences = json.dumps(preferences)
        self.updated_at = datetime.now(timezone.utc)
    
    def get_notification_preferences(self) -> Dict[str, Any]:
        """Get notification preferences"""
        if not self.notification_preferences:
            return {
                "email_notifications": True,
                "marketing_emails": True,
                "product_updates": True,
                "security_alerts": True,
            }
        
        try:
            import json
            return json.loads(self.notification_preferences)
        except json.JSONDecodeError:
            return {}
    
    # Utility methods
    def is_onboarding_complete(self) -> bool:
        """Check if user has completed onboarding"""
        return self.onboarding_completed and self.onboarding_step >= 100
    
    def can_access_feature(self, feature: str) -> bool:
        """Check if user can access a specific feature based on subscription"""
        if not self.company:
            return False
        
        tier = self.company.subscription_tier
        
        # Define feature access by tier
        feature_access = {
            SubscriptionTierEnum.FREE: ["basic_campaigns", "basic_analysis"],
            SubscriptionTierEnum.BASIC: ["basic_campaigns", "basic_analysis", "advanced_campaigns"],
            SubscriptionTierEnum.PRO: ["basic_campaigns", "basic_analysis", "advanced_campaigns", "ai_intelligence", "content_generation"],
            SubscriptionTierEnum.ENTERPRISE: ["all_features"]
        }
        
        if tier == SubscriptionTierEnum.ENTERPRISE:
            return True
        
        return feature in feature_access.get(tier, [])
    
    def get_display_name(self) -> str:
        """Get user's display name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.full_name:
            return self.full_name
        else:
            return self.email.split("@")[0]
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary"""
        data = {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "display_name": self.get_display_name(),
            "role": self.role.value if self.role else "user",
            "user_type": self.user_type.value if self.user_type else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_admin": self.is_admin,
            "avatar_url": self.avatar_url or self.profile_image_url,
            "timezone": self.timezone,
            "experience_level": self.experience_level,
            "onboarding_completed": self.onboarding_completed,
            "onboarding_step": self.onboarding_step,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
        }
        
        if include_sensitive:
            data.update({
                "phone_number": self.phone_number,
                "bio": self.bio,
                "dashboard_preferences": self.get_dashboard_preferences(),
                "notification_preferences": self.get_notification_preferences(),
                "usage_summary": self.get_usage_summary(),
            })
        
        return data
    
    def __repr__(self):
        return f"<User(email='{self.email}', full_name='{self.full_name}', role='{self.role}')>"