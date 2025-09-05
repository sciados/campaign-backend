# src/models/user.py - FIXED Enhanced User model for existing CampaignForge database
"""
Enhanced User model with multi-user type system for existing CampaignForge database
🎭 Adds user type functionality while preserving all existing relationships
🔧 FIXED: Correct string handling and removed enum dependencies
🔧 FIXED: Removed problematic intelligence relationships for new schema
"""

from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

# Import from your existing base module
from .base import BaseModel

# 🎭 User Type Enums (kept for reference, but using strings in database)
class UserType(str, enum.Enum):
    AFFILIATE_MARKETER = "affiliate_marketer"
    CONTENT_CREATOR = "content_creator" 
    BUSINESS_OWNER = "business_owner"

class UserTier(str, enum.Enum):
    FREE = "free"
    STARTER = "starter" 
    PRO = "pro"
    ELITE = "elite"

class OnboardingStatus(str, enum.Enum):
    INCOMPLETE = "incomplete"
    TYPE_SELECTED = "type_selected"
    PREFERENCES_SET = "preferences_set" 
    COMPLETED = "completed"

class User(BaseModel):
    """Enhanced User model with multi-user type support - preserves all existing fields"""
    __tablename__ = "users"
    
    # 🔧 EXISTING FIELDS (preserved as-is from your current model)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    avatar_url = Column(Text)
    
    # Company Relationship (existing)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    role = Column(String(50), default="owner")  # owner, admin, member, viewer
    
    # Status (existing)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Preferences (existing)
    preferences = Column(JSONB, default={})
    settings = Column(JSONB, default={})
    
    # Storage tracking (existing)
    storage_used_bytes = Column(Integer, default=0, nullable=False)
    storage_limit_bytes = Column(Integer, default=1073741824, nullable=False)  # 1GB default
    storage_tier = Column(String(20), default="free", nullable=False)
    last_storage_check = Column(DateTime(timezone=True), nullable=True)
    
    # 🆕 NEW: Multi-User Type System (using strings for consistency)
    user_type = Column(String(50), nullable=True)
    user_tier = Column(String(20), default="free", nullable=False)
    onboarding_status = Column(String(30), default="incomplete", nullable=False)
    onboarding_completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 🎯 NEW: User Goals & Experience (minimal additions)
    user_goals = Column(JSONB, default=[])  # User's stated goals
    experience_level = Column(String(50), default="beginner")  # beginner, intermediate, advanced
    
    # 📊 NEW: Usage Tracking (essential for multi-user limits)
    monthly_campaign_limit = Column(Integer, default=5)  # Based on user type/tier
    monthly_campaigns_used = Column(Integer, default=0)
    monthly_analysis_limit = Column(Integer, default=10)
    monthly_analysis_used = Column(Integer, default=0)
    
    # 📈 NEW: Lifetime Stats (for gamification and analytics)
    total_campaigns_created = Column(Integer, default=0)
    total_intelligence_generated = Column(Integer, default=0)
    total_content_generated = Column(Integer, default=0)
    
    # 🔧 ALL EXISTING RELATIONSHIPS (preserved exactly as-is, FIXED for new schema)
    company = relationship("Company", back_populates="users")
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    
    # FIXED: Updated relationships for new intelligence schema
    # Only keep GeneratedContent if it has user_id column
    generated_content = relationship("GeneratedContent", back_populates="user")
    
    # REMOVED: These relationships referenced non-existent columns
    # intelligence_sources = relationship("IntelligenceSourceType", back_populates="user")  # REMOVED - IntelligenceSourceType is now an enum
    # smart_urls = relationship("SmartURL", back_populates="user")  # REMOVED - SmartURL doesn't exist
    
    # Company membership relationships (existing)
    company_memberships = relationship(
        "CompanyMembership", 
        foreign_keys="CompanyMembership.user_id",
        back_populates="user"
    )
    
    # Invitations (existing)
    sent_invitations = relationship(
        "CompanyInvitation",
        foreign_keys="CompanyInvitation.invited_by", 
        back_populates="inviter"
    )
    
    accepted_invitations = relationship(
        "CompanyInvitation",
        foreign_keys="CompanyInvitation.accepted_by",
        back_populates="accepter"
    )
    
    invited_memberships = relationship(
        "CompanyMembership",
        foreign_keys="CompanyMembership.invited_by",
        back_populates="inviter"
    )
    
    # Storage relationship (existing)
    storage_usage = relationship("UserStorageUsage", back_populates="user", cascade="all, delete-orphan")
    
    # 🆕 NEW: Method to get user's intelligence through campaigns (correct approach for new schema)
    def get_intelligence_data(self, db_session):
        """Get user's intelligence data through campaigns (new schema approach)"""
        from sqlalchemy.orm import selectinload
        try:
            campaigns_with_intelligence = db_session.query(type(self.campaigns[0]))\
                .filter_by(user_id=self.id)\
                .filter(type(self.campaigns[0]).analysis_intelligence_id.isnot(None))\
                .options(selectinload('intelligence_data'))\
                .all()
            return campaigns_with_intelligence
        except (IndexError, AttributeError):
            return []
    
    # 🆕 NEW: Multi-User Type Methods (FIXED to use strings)
    
    def set_user_type(self, user_type: str, type_data: dict = None):
        """Set user type and initialize type-specific data"""
        self.user_type = user_type
        self.onboarding_status = "type_selected"
        
        # Store type-specific data in existing settings field to avoid new column
        if not self.settings:
            self.settings = {}
        self.settings['user_type_data'] = type_data or {}
        
        # Set default limits based on user type
        self._set_default_limits_by_type()
        
        # Set default preferences in existing preferences field
        self._set_default_intelligence_preferences()
    
    def _set_default_limits_by_type(self):
        """Set default limits based on user type"""
        if self.user_type == "affiliate_marketer":
            self.monthly_campaign_limit = 10  # Affiliates create more campaigns
            self.monthly_analysis_limit = 25
        elif self.user_type == "content_creator":
            self.monthly_campaign_limit = 15  # Creators need lots of content
            self.monthly_analysis_limit = 20
        elif self.user_type == "business_owner":
            self.monthly_campaign_limit = 8   # Businesses focus on quality
            self.monthly_analysis_limit = 15
    
    def _set_default_intelligence_preferences(self):
        """Set default intelligence preferences in existing preferences field"""
        if not self.preferences:
            self.preferences = {}
            
        if self.user_type == "affiliate_marketer":
            self.preferences['intelligence'] = {
                "focus_areas": ["competitor_analysis", "conversion_optimization", "commission_tracking"],
                "auto_track_competitors": True,
                "monitor_compliance": True,
                "track_epc": True,
                "preferred_sources": ["competitor_pages", "affiliate_networks", "commission_data"]
            }
            
        elif self.user_type == "content_creator":
            self.preferences['intelligence'] = {
                "focus_areas": ["viral_analysis", "trend_detection", "audience_insights"],
                "auto_track_trends": True,
                "monitor_viral_content": True,
                "cross_platform_analysis": True,
                "preferred_sources": ["social_media", "viral_content", "trend_data"]
            }
            
        elif self.user_type == "business_owner":
            self.preferences['intelligence'] = {
                "focus_areas": ["market_research", "lead_generation", "competitor_monitoring"],
                "auto_market_analysis": True,
                "track_lead_sources": True,
                "monitor_industry_trends": True,
                "preferred_sources": ["market_data", "competitor_sites", "industry_reports"]
            }
    
    def complete_onboarding(self, goals: list = None, experience_level: str = "beginner"):
        """Complete user onboarding process"""
        self.user_goals = goals or []
        self.experience_level = experience_level
        self.onboarding_status = "completed"
        self.onboarding_completed_at = datetime.now(timezone.utc)
    
    def get_dashboard_route(self) -> str:
        """Get the appropriate dashboard route for this user type"""
        if self.user_type == "affiliate_marketer":
            return "/dashboard/affiliate"
        elif self.user_type == "content_creator":
            return "/dashboard/creator"
        elif self.user_type == "business_owner":
            return "/dashboard/business"
        else:
            return "/user-selection"  # Not set yet
    
    def get_user_type_display(self) -> str:
        """Get display name for user type"""
        if self.user_type == "affiliate_marketer":
            return "💰 Affiliate Marketer"
        elif self.user_type == "content_creator":
            return "🎬 Content Creator"
        elif self.user_type == "business_owner":
            return "🏢 Business Owner"
        else:
            return "User"
    
    def get_available_features(self) -> list:
        """Get list of available features for this user type"""
        if self.user_type == "affiliate_marketer":
            return [
                'competitor_tracking', 'commission_analysis', 'compliance_check',
                'ad_creative_generator', 'email_sequences', 'traffic_analysis'
            ]
        elif self.user_type == "content_creator":
            return [
                'viral_analysis', 'trend_detection', 'content_optimization', 
                'audience_insights', 'brand_partnerships', 'cross_platform'
            ]
        elif self.user_type == "business_owner":
            return [
                'market_research', 'lead_generation', 'competitor_analysis',
                'customer_insights', 'sales_optimization', 'roi_tracking'  
            ]
        else:
            return []
    
    # 📊 NEW: Usage Tracking Methods
    def can_create_campaign(self) -> bool:
        """Check if user can create another campaign this month"""
        return self.monthly_campaigns_used < self.monthly_campaign_limit
    
    def can_run_analysis(self) -> bool:
        """Check if user can run another analysis this month"""
        return self.monthly_analysis_used < self.monthly_analysis_limit
    
    def increment_campaign_usage(self):
        """Increment monthly campaign usage - will be handled by DB trigger"""
        pass  # Database trigger handles this automatically
    
    def increment_analysis_usage(self):
        """Increment monthly analysis usage - will be handled by DB trigger"""
        pass  # Database trigger handles this automatically
    
    def get_usage_summary(self) -> dict:
        """Get comprehensive usage summary"""
        return {
            "campaigns": {
                "used": self.monthly_campaigns_used,
                "limit": self.monthly_campaign_limit,
                "available": max(0, self.monthly_campaign_limit - self.monthly_campaigns_used),
                "percentage": (self.monthly_campaigns_used / self.monthly_campaign_limit * 100) if self.monthly_campaign_limit > 0 else 0
            },
            "analysis": {
                "used": self.monthly_analysis_used,
                "limit": self.monthly_analysis_limit,
                "available": max(0, self.monthly_analysis_limit - self.monthly_analysis_used),
                "percentage": (self.monthly_analysis_used / self.monthly_analysis_limit * 100) if self.monthly_analysis_limit > 0 else 0
            },
            "lifetime_stats": {
                "total_campaigns": self.total_campaigns_created,
                "total_intelligence": self.total_intelligence_generated,
                "total_content": self.total_content_generated
            }
        }
    
    def get_user_profile(self) -> dict:
        """Get comprehensive user profile for dashboard"""
        return {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "user_type": self.user_type,  # Already a string
            "user_type_display": self.get_user_type_display(),
            "user_tier": self.user_tier,  # Already a string
            "onboarding_status": self.onboarding_status,  # Already a string
            "experience_level": self.experience_level,
            "dashboard_route": self.get_dashboard_route(),
            "available_features": self.get_available_features(),
            "usage_summary": self.get_usage_summary(),
            "user_goals": self.user_goals,
            "user_type_data": self.settings.get('user_type_data', {}) if self.settings else {},
            "intelligence_preferences": self.preferences.get('intelligence', {}) if self.preferences else {},
            "onboarding_completed": self.onboarding_status == "completed"
        }
    
    # 🔧 EXISTING METHODS (preserved exactly as-is)
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
    
    # Storage utility methods (existing - unchanged)
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
            return {
                "limit_gb": 1,
                "limit_bytes": 1073741824,
                "max_file_size_mb": 10,
                "price_monthly": 0
            }
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', type='{self.user_type}', tier='{self.user_tier}', onboarding='{self.onboarding_status}')>"