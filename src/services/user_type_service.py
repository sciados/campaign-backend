# src/services/user_type_service.py
"""
User Type Management Service for CampaignForge Multi-User System - ASYNC VERSION
🎭 Handles user type detection, routing, and configuration with async operations
🎯 Provides user-specific recommendations / optimizations
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timezone, timedelta

from ..models.user import User, UserType, UserTier, OnboardingStatus
from ..models.campaign import Campaign
from ..core.database import get_async_db

class UserTypeService:
    """Service for managing user types and user-specific functionality"""
    
    def __init__(self, db: AsyncSession = None):
        self.db = db
    
    # 🎭 User Type Detection & Configuration
    
    async def detect_user_type_from_data(self, user_data: dict) -> str:
        """
        Intelligent user type detection based on provided data
        """
        try:
            if not user_data or not isinstance(user_data, dict):
                return "business_owner"
        
            # Define keyword patterns
            affiliate_keywords = [
                'affiliate', 'commission', 'promote products', 'earn money online', 
                'clickbank', 'amazon associates', 'referral', 'conversion rate',
                'traffic', 'landing page', 'sales funnel', 'cpa', 'cpc', 'epc',
                'affiliate network', 'promote offers', 'email marketing'
            ]
            
            creator_keywords = [
                'content creator', 'influencer', 'youtube', 'tiktok', 'instagram',
                'followers', 'subscribers', 'viral', 'social media', 'brand deals',
                'sponsorship', 'creator fund', 'monetize content', 'audience',
                'engagement', 'views', 'likes', 'shares', 'content strategy'
            ]
            
            business_keywords = [
                'business owner', 'entrepreneur', 'startup', 'company', 'sales',
                'leads', 'customers', 'market research', 'revenue', 'growth',
                'b2b', 'b2c', 'roi', 'marketing', 'brand', 'product', 'service',
                'competition', 'market share', 'business development'
            ]
        
            # Handle different data types properly
            description = user_data.get("description") or ""
        
            goals = user_data.get("goals", [])
            if isinstance(goals, list):
                goals = " ".join(str(g) for g in goals if g)
            else:
                goals = str(goals) if goals else ""
        
            interests = user_data.get("interests", [])
            if isinstance(interests, list):
                interests = " ".join(str(i) for i in interests if i)
            else:
                interests = str(interests) if interests else ""
        
            current_activities = user_data.get("current_activities", [])
            if isinstance(current_activities, list):
                current_activities = " ".join(str(a) for a in current_activities if a)
            else:
                current_activities = str(current_activities) if current_activities else ""
        
            text_to_analyze = " ".join([
                description,
                goals,
                interests,
                current_activities
            ]).lower()
        
            # Score each user type
            affiliate_score = sum(1 for keyword in affiliate_keywords if keyword in text_to_analyze)
            creator_score = sum(1 for keyword in creator_keywords if keyword in text_to_analyze)
            business_score = sum(1 for keyword in business_keywords if keyword in text_to_analyze)
        
            # Return user type with highest score
            if affiliate_score > creator_score and affiliate_score > business_score:
                return "affiliate_marketer"
            elif creator_score > business_score:
                return "content_creator"
            else:
                return "business_owner"
        
        except Exception as e:
            print(f"Error in detect_user_type_from_data: {e}")
            return "business_owner"
    
    async def set_user_type(self, user_id: str, user_type: str, type_data: dict = None) -> User:
        """Set user type and initialize type-specific configuration"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Set user type (accepting string directly)
        user.user_type = user_type
        user.onboarding_status = "type_selected"
        
        # Store type-specific data
        if not user.settings:
            user.settings = {}
        user.settings['user_type_data'] = type_data or {}
        
        # Set default limits and preferences
        user._set_default_limits_by_type()
        user._set_default_intelligence_preferences()
        
        # Commit changes
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def complete_user_onboarding(self, user_id: str, goals: list, experience_level: str) -> User:
        """Complete user onboarding process"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        user.complete_onboarding(goals, experience_level)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    # 📊 User Type Analytics
    
    async def get_user_type_stats(self) -> dict:
        """Get statistics about user types in the system"""
        total_users_result = await self.db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar()
        
        affiliate_result = await self.db.execute(
            select(func.count(User.id)).where(User.user_type == "affiliate_marketer")
        )
        affiliate_count = affiliate_result.scalar()
        
        creator_result = await self.db.execute(
            select(func.count(User.id)).where(User.user_type == "content_creator")
        )
        creator_count = creator_result.scalar()
        
        business_result = await self.db.execute(
            select(func.count(User.id)).where(User.user_type == "business_owner")
        )
        business_count = business_result.scalar()
        
        no_type_result = await self.db.execute(
            select(func.count(User.id)).where(User.user_type.is_(None))
        )
        no_type_count = no_type_result.scalar()
        
        return {
            "total_users": total_users,
            "user_types": {
                "affiliate_marketers": {
                    "count": affiliate_count,
                    "percentage": (affiliate_count / total_users * 100) if total_users > 0 else 0
                },
                "content_creators": {
                    "count": creator_count,
                    "percentage": (creator_count / total_users * 100) if total_users > 0 else 0
                },
                "business_owners": {
                    "count": business_count,
                    "percentage": (business_count / total_users * 100) if total_users > 0 else 0
                },
                "not_set": {
                    "count": no_type_count,
                    "percentage": (no_type_count / total_users * 100) if total_users > 0 else 0
                }
            }
        }
    
    async def get_users_by_type(self, user_type: str, limit: int = 100) -> List[User]:
        """Get users of a specific type"""
        result = await self.db.execute(
            select(User).where(User.user_type == user_type).limit(limit)
        )
        return result.scalars().all()
    
    # 🎯 User-Specific Recommendations
    
    async def get_user_recommendations(self, user_id: str) -> dict:
        """Get personalized recommendations for a user based on their type and activity"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Get user's campaign history
        campaigns_result = await self.db.execute(
            select(Campaign).where(Campaign.user_id == user_id)
            .order_by(Campaign.created_at.desc()).limit(5)
        )
        recent_campaigns = campaigns_result.scalars().all()
        
        recommendations = {
            "next_actions": [],
            "suggested_features": [],
            "learning_resources": [],
            "optimization_tips": []
        }
        
        if user.user_type == "affiliate_marketer":
            recommendations = self._get_affiliate_recommendations(user, recent_campaigns)
        elif user.user_type == "content_creator":
            recommendations = self._get_creator_recommendations(user, recent_campaigns)
        elif user.user_type == "business_owner":
            recommendations = self._get_business_recommendations(user, recent_campaigns)
        
        return recommendations
    
    def _get_affiliate_recommendations(self, user: User, recent_campaigns: List[Campaign]) -> dict:
        """Get recommendations specific to affiliate marketers"""
        return {
            "next_actions": [
                "🔍 Set up competitor tracking for your top 3 competitors",
                "📊 Analyze your best-performing campaign for optimization insights",
                "📧 Create email sequences for your top-converting offers"
            ],
            "suggested_features": [
                "competitor_tracking",
                "commission_analysis", 
                "compliance_check",
                "traffic_analysis"
            ],
            "learning_resources": [
                "📖 Affiliate Marketing Best Practices Guide",
                "🎥 How to Track Competitors Effectively",
                "📊 Understanding EPC and Conversion Metrics"
            ],
            "optimization_tips": [
                "💡 Test different traffic sources to find your best-performing channels",
                "⚡ Use compliance checking to avoid account suspensions",
                "📈 Track competitor campaigns to identify new opportunities"
            ]
        }
    
    def _get_creator_recommendations(self, user: User, recent_campaigns: List[Campaign]) -> dict:
        """Get recommendations specific to content creators"""
        return {
            "next_actions": [
                "🔥 Analyze viral content in your niche for trends",
                "📱 Set up cross-platform content optimization",
                "💰 Explore brand partnership opportunities"
            ],
            "suggested_features": [
                "viral_analysis",
                "trend_detection",
                "content_optimization",
                "audience_insights"
            ],
            "learning_resources": [
                "📖 Content Creator's Guide to Going Viral",
                "🎥 Cross-Platform Content Strategy",
                "💰 Monetization Strategies for Creators"
            ],
            "optimization_tips": [
                "💡 Post consistently to build audience engagement",
                "🎯 Use trending hashtags and sounds to boost reach",
                "📊 Analyze your best-performing content for patterns"
            ]
        }
    
    def _get_business_recommendations(self, user: User, recent_campaigns: List[Campaign]) -> dict:
        """Get recommendations specific to business owners"""
        return {
            "next_actions": [
                "📊 Conduct market research for expansion opportunities", 
                "🎯 Set up lead generation campaigns",
                "🏆 Analyze competitor strategies in your industry"
            ],
            "suggested_features": [
                "market_research",
                "lead_generation", 
                "competitor_analysis",
                "roi_tracking"
            ],
            "learning_resources": [
                "📖 SME Marketing Strategy Guide",
                "🎥 Lead Generation Best Practices",
                "📊 ROI Tracking and Optimization"
            ],
            "optimization_tips": [
                "💡 Focus on high-quality leads over quantity",
                "⚡ Track ROI on all marketing channels",
                "📈 Use competitor analysis to identify market gaps"
            ]
        }
    
    # 🎨 User Interface Customization
    
    async def get_dashboard_config(self, user_id: str) -> dict:
        """Get user-type specific dashboard configuration"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        base_config = {
            "user_profile": user.get_user_profile(),
            "available_features": user.get_available_features(),
            "usage_summary": user.get_usage_summary(),
            "dashboard_route": user.get_dashboard_route()
        }
        
        # Add user-type specific dashboard widgets and layout
        if user.user_type == "affiliate_marketer":
            base_config.update({
                "primary_widgets": [
                    "commission_tracker", "competitor_intel", "campaign_performance",
                    "compliance_center", "traffic_analytics"
                ],
                "dashboard_title": "Commission Command Center",
                "main_cta": "Track Competitors",
                "theme_color": "green"
            })
        elif user.user_type == "content_creator":
            base_config.update({
                "primary_widgets": [
                    "viral_opportunities", "content_studio", "audience_insights",
                    "brand_partnerships", "cross_platform_analytics"
                ],
                "dashboard_title": "Creator Studio Pro",
                "main_cta": "Analyze Viral Content",
                "theme_color": "purple"
            })
        elif user.user_type == "business_owner":
            base_config.update({
                "primary_widgets": [
                    "market_intelligence", "lead_generation", "competitor_watch",
                    "sales_pipeline", "roi_tracker"
                ],
                "dashboard_title": "Business Growth Command",
                "main_cta": "Generate Leads",
                "theme_color": "blue"
            })
        
        return base_config
    
    # 🔧 User Type Utilities
    
    def get_user_type_display_info(self, user_type: str) -> dict:
        """Get display information for a user type"""
        type_info = {
            "affiliate_marketer": {
                "emoji": "💰",
                "title": "Affiliate Marketer",
                "description": "Promote products and earn commissions",
                "features": ["Competitor tracking", "Commission analysis", "Compliance monitoring"],
                "pricing_start": "$149/month"
            },
            "content_creator": {
                "emoji": "🎬",
                "title": "Content Creator",
                "description": "Create viral content and grow your audience",
                "features": ["Viral analysis", "Trend detection", "Brand partnerships"],
                "pricing_start": "$99/month"
            },
            "business_owner": {
                "emoji": "🏢",
                "title": "Business Owner",
                "description": "Generate leads and grow your business",
                "features": ["Market research", "Lead generation", "ROI tracking"],
                "pricing_start": "$199/month"
            }
        }
        
        return type_info.get(user_type, {})
    
    def get_all_user_types_info(self) -> dict:
        """Get display information for all user types"""
        return {
            user_type: self.get_user_type_display_info(user_type)
            for user_type in ["affiliate_marketer", "content_creator", "business_owner"]
        }
    
    async def can_user_upgrade_tier(self, user_id: str) -> dict:
        """Check if user can/should upgrade their tier"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        usage = user.get_usage_summary()
        
        # Check if user is approaching limits
        campaign_usage_percent = usage["campaigns"]["percentage"]
        analysis_usage_percent = usage["analysis"]["percentage"]
        
        should_upgrade = campaign_usage_percent > 80 or analysis_usage_percent > 80
        
        # Suggest appropriate tier
        if user.user_tier == "free" and should_upgrade:
            suggested_tier = "starter"
        elif user.user_tier == "starter" and should_upgrade:
            suggested_tier = "pro"
        elif user.user_tier == "pro" and should_upgrade:
            suggested_tier = "elite"
        else:
            suggested_tier = None
        
        return {
            "can_upgrade": suggested_tier is not None,
            "should_upgrade": should_upgrade,
            "current_tier": user.user_tier,
            "suggested_tier": suggested_tier,
            "reasons": [
                f"Campaign usage: {campaign_usage_percent:.1f}%" if campaign_usage_percent > 80 else None,
                f"Analysis usage: {analysis_usage_percent:.1f}%" if analysis_usage_percent > 80 else None
            ],
            "usage_summary": usage
        }
    
    # 🔍 User Search and Filtering
    
    async def search_users(self, filters: dict) -> List[User]:
        """Search users with various filters"""
        query = select(User)
        
        if filters.get("user_type"):
            query = query.where(User.user_type == filters["user_type"])
        
        if filters.get("user_tier"):
            query = query.where(User.user_tier == filters["user_tier"])
        
        if filters.get("onboarding_status"):
            query = query.where(User.onboarding_status == filters["onboarding_status"])
        
        if filters.get("experience_level"):
            query = query.where(User.experience_level == filters["experience_level"])
        
        if filters.get("is_active") is not None:
            query = query.where(User.is_active == filters["is_active"])
        
        limit = filters.get("limit", 50)
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    # 📈 Usage Analytics
    
    async def get_user_activity_summary(self, user_id: str, days: int = 30) -> dict:
        """Get user activity summary for the last N days"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get recent campaigns
        campaigns_result = await self.db.execute(
            select(func.count(Campaign.id)).where(
                and_(
                    Campaign.user_id == user_id,
                    Campaign.created_at >= start_date
                )
            )
        )
        recent_campaigns = campaigns_result.scalar()
        
        return {
            "user_id": user_id,
            "user_type": user.user_type,
            "period_days": days,
            "activity": {
                "campaigns_created": recent_campaigns,
                "total_campaigns": user.total_campaigns_created,
                "total_intelligence": user.total_intelligence_generated,
                "total_content": user.total_content_generated,
                "last_active": user.last_active_at.isoformat() if user.last_active_at else None
            },
            "usage_limits": {
                "monthly_campaigns_used": user.monthly_campaigns_used,
                "monthly_campaigns_limit": user.monthly_campaign_limit,
                "monthly_analysis_used": user.monthly_analysis_used,
                "monthly_analysis_limit": user.monthly_analysis_limit
            }
        }
    
    # 🎯 User Type Migration
    
    async def migrate_user_type(self, user_id: str, new_user_type: str, reason: str = None) -> User:
        """Migrate user from one type to another"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        old_type = user.user_type
        
        # Update user type
        user.user_type = new_user_type
        
        # Log the migration (you could add a migration log table)
        migration_log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "old_type": old_type,
            "new_type": new_user_type,
            "reason": reason
        }
        
        # Add to user's settings for audit trail
        if not user.settings:
            user.settings = {}
        if "type_migrations" not in user.settings:
            user.settings["type_migrations"] = []
        user.settings["type_migrations"].append(migration_log)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    # 🎨 Personalization
    
    def get_personalized_welcome_message(self, user: User) -> str:
        """Get personalized welcome message based on user type and progress"""
        if not user:
            return "Welcome to CampaignForge!"
        
        if user.user_type == "affiliate_marketer":
            if user.total_campaigns_created == 0:
                return "💰 Ready to optimize your affiliate campaigns? Let's start by analyzing your top competitor!"
            else:
                return f"💰 Welcome back! You've created {user.total_campaigns_created} campaigns. Time to discover new opportunities!"
        
        elif user.user_type == "content_creator":
            if user.total_campaigns_created == 0:
                return "🎬 Ready to create viral content? Let's analyze what's trending in your niche!"
            else:
                return f"🎬 Welcome back, creator! You've analyzed {user.total_campaigns_created} pieces of content. Let's find your next viral hit!"
        
        elif user.user_type == "business_owner":
            if user.total_campaigns_created == 0:
                return "🏢 Ready to grow your business? Let's start with market research and competitor analysis!"
            else:
                return f"🏢 Welcome back! You've run {user.total_campaigns_created} analyses. Time to generate more qualified leads!"
        
        else:
            return "Welcome to CampaignForge! Let's set up your user type to get started."