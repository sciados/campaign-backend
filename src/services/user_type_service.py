# src/services/user_type_service.py
"""
User Type Management Service for CampaignForge Multi-User System
🎭 Handles user type detection, routing, and configuration
🎯 Provides user-specific recommendations / optimizations
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone, timedelta

from ..models.user import User, UserType, UserTier, OnboardingStatus
from ..models.campaign import Campaign
from ..core.database import get_db

class UserTypeService:
    """Service for managing user types and user-specific functionality"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    # 🎭 User Type Detection & Configuration
    
    def detect_user_type_from_data(self, user_data: dict) -> UserType:
        """
        Intelligent user type detection based on provided data
        🧠 Analyzes user inputs to suggest the best user type
        """
        # Keywords that indicate different user types
        affiliate_keywords = [
            "affiliate", "commission", "promote products", "earn money", 
            "traffic", "conversions", "epc", "cpa", "cpm", "clickbank",
            "amazon associate", "marketing funnels", "landing pages"
        ]
        
        creator_keywords = [
            "content", "social media", "influencer", "youtube", "tiktok", 
            "instagram", "viral", "followers", "engagement", "brand deals",
            "creator", "video", "podcast", "blog", "audience", "subscribers"
        ]
        
        business_keywords = [
            "business", "company", "leads", "customers", "sales", 
            "marketing", "roi", "growth", "market share", "b2b",
            "startup", "entrepreneur", "revenue", "profit", "enterprise"
        ]
        
        # Analyze user input text
        text_to_analyze = " ".join([
            user_data.get("goals", ""),
            user_data.get("description", ""),
            user_data.get("interests", ""),
            str(user_data.get("current_activities", []))
        ]).lower()
        
        # Score each user type
        affiliate_score = sum(1 for keyword in affiliate_keywords if keyword in text_to_analyze)
        creator_score = sum(1 for keyword in creator_keywords if keyword in text_to_analyze)
        business_score = sum(1 for keyword in business_keywords if keyword in text_to_analyze)
        
        # Return the highest scoring type (with ties going to business owner as default)
        if affiliate_score > creator_score and affiliate_score > business_score:
            return UserType.affiliate_marketer
        elif creator_score > business_score and creator_score >= affiliate_score:
            return UserType.content_creator
        else:
            return UserType.business_owner
    
    def set_user_type(self, user_id: str, user_type: UserType, type_data: dict = None) -> User:
        """Set user type and initialize type-specific configuration"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Set user type
        user.set_user_type(user_type, type_data or {})
        
        # Commit changes
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def complete_user_onboarding(self, user_id: str, goals: list, experience_level: str) -> User:
        """Complete user onboarding process"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        user.complete_onboarding(goals, experience_level)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    # 📊 User Type Analytics
    
    def get_user_type_stats(self) -> dict:
        """Get statistics about user types in the system"""
        total_users = self.db.query(User).count()
        
        affiliate_count = self.db.query(User).filter(User.user_type == UserType.affiliate_marketer).count()
        creator_count = self.db.query(User).filter(User.user_type == UserType.content_creator).count()
        business_count = self.db.query(User).filter(User.user_type == UserType.business_owner).count()
        no_type_count = self.db.query(User).filter(User.user_type.is_(None)).count()
        
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
    
    def get_users_by_type(self, user_type: UserType, limit: int = 100) -> List[User]:
        """Get users of a specific type"""
        return self.db.query(User).filter(User.user_type == user_type).limit(limit).all()
    
    # 🎯 User-Specific Recommendations
    
    def get_user_recommendations(self, user_id: str) -> dict:
        """Get personalized recommendations for a user based on their type and activity"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Get user's campaign history
        recent_campaigns = self.db.query(Campaign).filter(
            and_(Campaign.user_id == user_id)
        ).order_by(Campaign.created_at.desc()).limit(5).all()
        
        recommendations = {
            "next_actions": [],
            "suggested_features": [],
            "learning_resources": [],
            "optimization_tips": []
        }
        
        if user.user_type == UserType.affiliate_marketer:
            recommendations = self._get_affiliate_recommendations(user, recent_campaigns)
        elif user.user_type == UserType.content_creator:
            recommendations = self._get_creator_recommendations(user, recent_campaigns)
        elif user.user_type == UserType.business_owner:
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
    
    def get_dashboard_config(self, user_id: str) -> dict:
        """Get user-type specific dashboard configuration"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        base_config = {
            "user_profile": user.get_user_profile(),
            "available_features": user.get_available_features(),
            "usage_summary": user.get_usage_summary(),
            "dashboard_route": user.get_dashboard_route()
        }
        
        # Add user-type specific dashboard widgets and layout
        if user.user_type == UserType.affiliate_marketer:
            base_config.update({
                "primary_widgets": [
                    "commission_tracker", "competitor_intel", "campaign_performance",
                    "compliance_center", "traffic_analytics"
                ],
                "dashboard_title": "Commission Command Center",
                "main_cta": "Track Competitors",
                "theme_color": "green"
            })
        elif user.user_type == UserType.content_creator:
            base_config.update({
                "primary_widgets": [
                    "viral_opportunities", "content_studio", "audience_insights",
                    "brand_partnerships", "cross_platform_analytics"
                ],
                "dashboard_title": "Creator Studio Pro",
                "main_cta": "Analyze Viral Content",
                "theme_color": "purple"
            })
        elif user.user_type == UserType.business_owner:
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
    
    def get_user_type_display_info(self, user_type: UserType) -> dict:
        """Get display information for a user type"""
        type_info = {
            UserType.affiliate_marketer: {
                "emoji": "💰",
                "title": "Affiliate Marketer",
                "description": "Promote products and earn commissions",
                "features": ["Competitor tracking", "Commission analysis", "Compliance monitoring"],
                "pricing_start": "$149/month"
            },
            UserType.content_creator: {
                "emoji": "🎬",
                "title": "Content Creator",
                "description": "Create viral content and grow your audience",
                "features": ["Viral analysis", "Trend detection", "Brand partnerships"],
                "pricing_start": "$99/month"
            },
            UserType.business_owner: {
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
            user_type.value: self.get_user_type_display_info(user_type)
            for user_type in UserType
        }
    
    def can_user_upgrade_tier(self, user_id: str) -> dict:
        """Check if user can/should upgrade their tier"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        usage = user.get_usage_summary()
        
        # Check if user is approaching limits
        campaign_usage_percent = usage["campaigns"]["percentage"]
        analysis_usage_percent = usage["analysis"]["percentage"]
        
        should_upgrade = campaign_usage_percent > 80 or analysis_usage_percent > 80
        
        # Suggest appropriate tier
        if user.user_tier == UserTier.free and should_upgrade:
            suggested_tier = UserTier.starter
        elif user.user_tier == UserTier.starter and should_upgrade:
            suggested_tier = UserTier.pro
        elif user.user_tier == UserTier.pro and should_upgrade:
            suggested_tier = UserTier.elite
        else:
            suggested_tier = None
        
        return {
            "can_upgrade": suggested_tier is not None,
            "should_upgrade": should_upgrade,
            "current_tier": user.user_tier.value,
            "suggested_tier": suggested_tier.value if suggested_tier else None,
            "reasons": [
                f"Campaign usage: {campaign_usage_percent:.1f}%" if campaign_usage_percent > 80 else None,
                f"Analysis usage: {analysis_usage_percent:.1f}%" if analysis_usage_percent > 80 else None
            ],
            "usage_summary": usage
        }
    
    # 🔍 User Search and Filtering
    
    def search_users(self, filters: dict) -> List[User]:
        """Search users with various filters"""
        query = self.db.query(User)
        
        if filters.get("user_type"):
            query = query.filter(User.user_type == UserType(filters["user_type"]))
        
        if filters.get("user_tier"):
            query = query.filter(User.user_tier == UserTier(filters["user_tier"]))
        
        if filters.get("onboarding_status"):
            query = query.filter(User.onboarding_status == OnboardingStatus(filters["onboarding_status"]))
        
        if filters.get("experience_level"):
            query = query.filter(User.experience_level == filters["experience_level"])
        
        if filters.get("is_active") is not None:
            query = query.filter(User.is_active == filters["is_active"])
        
        limit = filters.get("limit", 50)
        return query.limit(limit).all()
    
    # 📈 Usage Analytics
    
    def get_user_activity_summary(self, user_id: str, days: int = 30) -> dict:
        """Get user activity summary for the last N days"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get recent campaigns
        recent_campaigns = self.db.query(Campaign).filter(
            and_(
                Campaign.user_id == user_id,
                Campaign.created_at >= start_date
            )
        ).count()
        
        return {
            "user_id": user_id,
            "user_type": user.user_type.value if user.user_type else None,
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
    
    def migrate_user_type(self, user_id: str, new_user_type: UserType, reason: str = None) -> User:
        """Migrate user from one type to another"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        old_type = user.user_type
        
        # Update user type
        user.set_user_type(new_user_type)
        
        # Log the migration (you could add a migration log table)
        migration_log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "old_type": old_type.value if old_type else None,
            "new_type": new_user_type.value,
            "reason": reason
        }
        
        # Add to user's settings for audit trail
        if not user.settings:
            user.settings = {}
        if "type_migrations" not in user.settings:
            user.settings["type_migrations"] = []
        user.settings["type_migrations"].append(migration_log)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    # 🎨 Personalization
    
    def get_personalized_welcome_message(self, user_id: str) -> str:
        """Get personalized welcome message based on user type and progress"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return "Welcome to CampaignForge!"
        
        if user.user_type == UserType.affiliate_marketer:
            if user.total_campaigns_created == 0:
                return "💰 Ready to optimize your affiliate campaigns? Let's start by analyzing your top competitor!"
            else:
                return f"💰 Welcome back! You've created {user.total_campaigns_created} campaigns. Time to discover new opportunities!"
        
        elif user.user_type == UserType.content_creator:
            if user.total_campaigns_created == 0:
                return "🎬 Ready to create viral content? Let's analyze what's trending in your niche!"
            else:
                return f"🎬 Welcome back, creator! You've analyzed {user.total_campaigns_created} pieces of content. Let's find your next viral hit!"
        
        elif user.user_type == UserType.business_owner:
            if user.total_campaigns_created == 0:
                return "🏢 Ready to grow your business? Let's start with market research and competitor analysis!"
            else:
                return f"🏢 Welcome back! You've run {user.total_campaigns_created} analyses. Time to generate more qualified leads!"
        
        else:
            return "Welcome to CampaignForge! Let's set up your user type to get started."
    
    # 🔄 Advanced User Type Analytics
    
    def get_user_type_performance_metrics(self, user_type: UserType, days: int = 30) -> dict:
        """Get performance metrics for a specific user type"""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        users = self.db.query(User).filter(User.user_type == user_type).all()
        
        if not users:
            return {"error": f"No users found for type {user_type.value}"}
        
        total_users = len(users)
        active_users = len([u for u in users if u.last_active_at and u.last_active_at >= start_date])
        total_campaigns = sum(u.total_campaigns_created for u in users)
        total_intelligence = sum(u.total_intelligence_generated for u in users)
        total_content = sum(u.total_content_generated for u in users)
        
        # Calculate averages
        avg_campaigns = total_campaigns / total_users if total_users > 0 else 0
        avg_intelligence = total_intelligence / total_users if total_users > 0 else 0
        avg_content = total_content / total_users if total_users > 0 else 0
        
        return {
            "user_type": user_type.value,
            "period_days": days,
            "metrics": {
                "total_users": total_users,
                "active_users": active_users,
                "activity_rate": (active_users / total_users * 100) if total_users > 0 else 0,
                "total_campaigns": total_campaigns,
                "total_intelligence": total_intelligence,
                "total_content": total_content,
                "avg_campaigns_per_user": round(avg_campaigns, 1),
                "avg_intelligence_per_user": round(avg_intelligence, 1),
                "avg_content_per_user": round(avg_content, 1)
            }
        }
    
    def get_user_engagement_insights(self, user_id: str) -> dict:
        """Get detailed engagement insights for a specific user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Calculate engagement metrics
        usage = user.get_usage_summary()
        
        # Determine engagement level
        campaign_usage = usage["campaigns"]["percentage"]
        analysis_usage = usage["analysis"]["percentage"]
        
        engagement_score = (campaign_usage + analysis_usage) / 2
        
        if engagement_score >= 80:
            engagement_level = "high"
            engagement_message = "🔥 Power user! You're getting maximum value from CampaignForge."
        elif engagement_score >= 50:
            engagement_level = "medium"
            engagement_message = "📈 Great progress! Consider exploring more features to unlock additional value."
        elif engagement_score >= 20:
            engagement_level = "low"
            engagement_message = "🌱 Getting started! Try creating more campaigns to see better results."
        else:
            engagement_level = "minimal"
            engagement_message = "👋 Welcome! Let's help you get started with your first campaign."
        
        # Get recommendations based on usage patterns
        recommendations = []
        
        if campaign_usage < 30:
            recommendations.append({
                "type": "action",
                "title": "Create more campaigns",
                "description": "You're only using 30% of your campaign limit. Create more to get better insights!",
                "cta": "Create Campaign",
                "priority": "high"
            })
        
        if analysis_usage < 30:
            recommendations.append({
                "type": "feature",
                "title": "Try auto-analysis",
                "description": "Enable auto-analysis to get insights without manual work.",
                "cta": "Enable Auto-Analysis",
                "priority": "medium"
            })
        
        if user.last_active_at:
            days_since_active = (datetime.now(timezone.utc) - user.last_active_at).days
            if days_since_active > 7:
                recommendations.append({
                    "type": "retention",
                    "title": "Welcome back!",
                    "description": f"It's been {days_since_active} days since your last visit. Check out what's new!",
                    "cta": "See Updates",
                    "priority": "high"
                })
        
        return {
            "user_id": user_id,
            "user_type": user.user_type.value if user.user_type else None,
            "engagement": {
                "level": engagement_level,
                "score": round(engagement_score, 1),
                "message": engagement_message
            },
            "usage": usage,
            "recommendations": recommendations,
            "insights": {
                "most_used_feature": "campaigns" if campaign_usage > analysis_usage else "analysis",
                "underutilized_features": [
                    "campaigns" if campaign_usage < 50 else None,
                    "analysis" if analysis_usage < 50 else None
                ],
                "tier_recommendation": self.can_user_upgrade_tier(user_id)
            }
        }
    
    # 🎯 User Type Optimization
    
    def optimize_user_limits(self, user_id: str) -> dict:
        """Optimize user limits based on usage patterns"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        usage = user.get_usage_summary()
        
        # Calculate optimal limits
        current_campaign_usage = usage["campaigns"]["used"]
        current_analysis_usage = usage["analysis"]["used"]
        
        # Suggest limits with 20% buffer
        optimal_campaign_limit = max(user.monthly_campaign_limit, int(current_campaign_usage * 1.2))
        optimal_analysis_limit = max(user.monthly_analysis_limit, int(current_analysis_usage * 1.2))
        
        return {
            "user_id": user_id,
            "current_limits": {
                "campaigns": user.monthly_campaign_limit,
                "analysis": user.monthly_analysis_limit
            },
            "usage": {
                "campaigns": current_campaign_usage,
                "analysis": current_analysis_usage
            },
            "recommended_limits": {
                "campaigns": optimal_campaign_limit,
                "analysis": optimal_analysis_limit
            },
            "optimization_potential": {
                "campaign_increase": optimal_campaign_limit - user.monthly_campaign_limit,
                "analysis_increase": optimal_analysis_limit - user.monthly_analysis_limit
            }
        }
    
    def get_user_success_metrics(self, user_id: str) -> dict:
        """Get user success metrics and milestones"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Define success milestones by user type
        milestones = {
            UserType.affiliate_marketer: [
                {"name": "First Campaign", "threshold": 1, "metric": "campaigns"},
                {"name": "Campaign Master", "threshold": 10, "metric": "campaigns"},
                {"name": "Intelligence Expert", "threshold": 25, "metric": "intelligence"},
                {"name": "Content Creator", "threshold": 50, "metric": "content"},
                {"name": "Power User", "threshold": 100, "metric": "campaigns"}
            ],
            UserType.content_creator: [
                {"name": "Content Analyzer", "threshold": 1, "metric": "campaigns"},
                {"name": "Trend Spotter", "threshold": 5, "metric": "intelligence"},
                {"name": "Viral Hunter", "threshold": 15, "metric": "campaigns"},
                {"name": "Content Machine", "threshold": 100, "metric": "content"},
                {"name": "Influence Master", "threshold": 50, "metric": "campaigns"}
            ],
            UserType.business_owner: [
                {"name": "Market Researcher", "threshold": 1, "metric": "campaigns"},
                {"name": "Lead Generator", "threshold": 5, "metric": "campaigns"},
                {"name": "Business Intelligence", "threshold": 20, "metric": "intelligence"},
                {"name": "Growth Hacker", "threshold": 25, "metric": "campaigns"},
                {"name": "Market Leader", "threshold": 100, "metric": "intelligence"}
            ]
        }
        
        user_milestones = milestones.get(user.user_type, [])
        
        # Calculate achievement status
        achievements = []
        for milestone in user_milestones:
            if milestone["metric"] == "campaigns":
                current_value = user.total_campaigns_created
            elif milestone["metric"] == "intelligence":
                current_value = user.total_intelligence_generated
            elif milestone["metric"] == "content":
                current_value = user.total_content_generated
            else:
                current_value = 0
            
            achieved = current_value >= milestone["threshold"]
            progress = min(100, (current_value / milestone["threshold"]) * 100)
            
            achievements.append({
                "name": milestone["name"],
                "threshold": milestone["threshold"],
                "current": current_value,
                "achieved": achieved,
                "progress": round(progress, 1)
            })
        
        # Calculate overall success score
        achieved_count = sum(1 for a in achievements if a["achieved"])
        success_score = (achieved_count / len(achievements) * 100) if achievements else 0
        
        return {
            "user_id": user_id,
            "user_type": user.user_type.value if user.user_type else None,
            "success_score": round(success_score, 1),
            "achievements": achievements,
            "next_milestone": next((a for a in achievements if not a["achieved"]), None),
            "total_achievements": achieved_count,
            "lifetime_stats": {
                "campaigns": user.total_campaigns_created,
                "intelligence": user.total_intelligence_generated,
                "content": user.total_content_generated
            }
        }