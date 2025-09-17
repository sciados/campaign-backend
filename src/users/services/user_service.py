# src/users/services/user_service.py
"""
User Service - Business logic layer for user management
Migrated from src/core/crud/user_crud.py with enhancements
"""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
import logging
import json

from src.users.models.user import User, Company, UserTypeEnum, UserRoleEnum, SubscriptionTierEnum
from src.core.shared.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

class UserService:
    """
    User Service with authentication and multi-user type support
    Provides business logic layer for user management
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Core user management methods
    async def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        company_name: str = "Default Company",
        role: Union[str, UserRoleEnum] = UserRoleEnum.USER,
        user_type: Optional[Union[str, UserTypeEnum]] = None
    ) -> User:
        """Create a new user with company"""
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_email(email)
            if existing_user:
                raise ValidationError(f"User with email {email} already exists", field="email")
            
            # Create company first
            company_slug = company_name.lower().replace(" ", "-").replace(".", "")
            
            # Ensure unique company slug
            base_slug = company_slug
            counter = 1
            while await self._company_slug_exists(company_slug):
                company_slug = f"{base_slug}-{counter}"
                counter += 1
            
            company = Company(
                company_name=company_name,
                company_slug=company_slug,
                subscription_tier=SubscriptionTierEnum.FREE,
                monthly_credits_limit=1000,
                monthly_credits_used=0
            )
            self.db.add(company)
            await self.db.flush()  # Get the company ID
            
            # Create user
            user = User(
                email=email,
                full_name=full_name,
                company_id=company.id,
                is_active=True,
                is_verified=False,
                onboarding_completed=False,
                onboarding_step=0
            )
            
            # Set role
            user.set_role(role)
            
            # Set user type if provided
            if user_type:
                user.set_user_type(user_type)
            
            # Set password using the User model's method
            user.set_password(password)
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            await self.db.refresh(company)
            
            # Load the company relationship
            user.company = company
            
            logger.info(f"Created user {user.id} with company {company.id}")
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    async def _company_slug_exists(self, slug: str) -> bool:
        """Check if company slug already exists"""
        result = await self.db.execute(
            select(Company).where(Company.company_slug == slug)
        )
        return result.scalar_one_or_none() is not None
    
    async def get_user_by_email(
        self,
        email: str,
        include_company: bool = True
    ) -> Optional[User]:
        """Get user by email address with optional company info"""
        try:
            query = select(User).where(User.email == email)
            
            if include_company:
                query = query.options(selectinload(User.company))
            
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
            
            return user
            
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise
    
    async def get_user_by_id(
        self,
        user_id: Union[str, UUID],
        include_company: bool = True
    ) -> Optional[User]:
        """Get user by ID with optional company info"""
        try:
            query = select(User).where(User.id == user_id)

            if include_company:
                query = query.options(selectinload(User.company))

            # Execute query without creating a new transaction
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()

            return user
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            raise
    
    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = await self.get_user_by_email(email=email, include_company=True)
            
            if not user:
                logger.warning(f"User not found for email: {email}")
                return None
            
            if not user.verify_password(password):
                logger.warning(f"Invalid password for user: {email}")
                return None
            
            if not user.is_active:
                logger.warning(f"User account is deactivated: {email}")
                return None
            
            # Update last login using the User model method
            user.record_login()
            await self.db.commit()
            
            logger.info(f"User authenticated successfully: {user.id}")
            return user
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise
    
    async def update_user(
        self,
        user_id: Union[str, UUID],
        **kwargs
    ) -> Optional[User]:
        """Update user information"""
        try:
            user = await self.get_user_by_id(user_id=user_id)
            if not user:
                raise NotFoundError(f"User {user_id} not found", resource_type="user", resource_id=str(user_id))
            
            # Update allowed fields
            allowed_fields = [
                'full_name', 'first_name', 'last_name', 'bio', 'timezone',
                'phone_number', 'avatar_url', 'profile_image_url', 'language', 'theme'
            ]
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            user.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Updated user {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            await self.db.rollback()
            raise
    
    async def delete_user(self, user_id: Union[str, UUID]) -> bool:
        """Soft delete user (deactivate)"""
        return await self.deactivate_user(user_id)
    
    # Dashboard-specific methods
    async def get_dashboard_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        company_id: Optional[Union[str, UUID]] = None,
        user_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """Get users for admin dashboard"""
        try:
            query = select(User).options(selectinload(User.company))
            
            if company_id:
                query = query.where(User.company_id == str(company_id))
            
            if user_type:
                query = query.where(User.user_type == user_type)
            
            if is_active is not None:
                query = query.where(User.is_active == is_active)
            
            query = query.offset(skip).limit(limit).order_by(desc(User.created_at))
            
            result = await self.db.execute(query)
            users = result.scalars().all()
            
            return list(users)
            
        except Exception as e:
            logger.error(f"Error getting dashboard users: {e}")
            raise
    
    async def get_user_stats(self, company_id: Optional[Union[str, UUID]] = None) -> Dict[str, Any]:
        """Get user statistics for dashboard"""
        try:
            base_query = select(func.count(User.id))
            
            if company_id:
                base_query = base_query.where(User.company_id == str(company_id))
            
            # Total users
            total_result = await self.db.execute(base_query)
            total_users = total_result.scalar()
            
            # Active users
            active_result = await self.db.execute(
                base_query.where(User.is_active == True)
            )
            active_users = active_result.scalar()
            
            # Admin users
            admin_result = await self.db.execute(
                base_query.where(User.role == UserRoleEnum.ADMIN)
            )
            admin_users = admin_result.scalar()
            
            # Users by type
            user_types = {}
            for user_type in UserTypeEnum:
                type_result = await self.db.execute(
                    base_query.where(User.user_type == user_type)
                )
                user_types[user_type.value] = type_result.scalar()
            
            # Recent signups (last 30 days)
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent_result = await self.db.execute(
                base_query.where(User.created_at >= thirty_days_ago)
            )
            recent_signups = recent_result.scalar()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "admin_users": admin_users,
                "user_types": user_types,
                "recent_signups": recent_signups,
                "onboarded_users": await self._count_onboarded_users(company_id),
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            raise
    
    async def _count_onboarded_users(self, company_id: Optional[Union[str, UUID]] = None) -> int:
        """Count users who completed onboarding"""
        query = select(func.count(User.id)).where(User.onboarding_completed == True)
        
        if company_id:
            query = query.where(User.company_id == str(company_id))
        
        result = await self.db.execute(query)
        return result.scalar()
    
    async def update_dashboard_preferences(
        self, 
        user_id: Union[str, UUID], 
        preferences: Dict[str, Any]
    ) -> User:
        """Update user dashboard preferences"""
        try:
            user = await self.get_user_by_id(user_id=user_id)
            if not user:
                raise NotFoundError(f"User {user_id} not found", resource_type="user", resource_id=str(user_id))
            
            user.update_dashboard_preferences(preferences)
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Updated dashboard preferences for user {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating dashboard preferences: {e}")
            await self.db.rollback()
            raise
    
    async def get_dashboard_preferences(self, user_id: Union[str, UUID]) -> Dict[str, Any]:
        """Get user dashboard preferences"""
        try:
            user = await self.get_user_by_id(user_id=user_id)
            if not user:
                raise NotFoundError(f"User {user_id} not found", resource_type="user", resource_id=str(user_id))
            
            return user.get_dashboard_preferences()
            
        except Exception as e:
            logger.error(f"Error getting dashboard preferences: {e}")
            raise
    
    # User type and onboarding management
    async def get_users_by_company(
        self,
        company_id: Union[str, UUID],
        skip: int = 0,
        limit: int = 100,
        user_type: Optional[str] = None,
        is_active: Optional[bool] = True
    ) -> List[User]:
        """Get all users for a company with optional filtering"""
        try:
            query = select(User).where(User.company_id == str(company_id))
            
            if user_type:
                query = query.where(User.user_type == user_type)
            
            if is_active is not None:
                query = query.where(User.is_active == is_active)
            
            query = query.offset(skip).limit(limit).order_by(desc(User.created_at))
            
            result = await self.db.execute(query)
            users = result.scalars().all()
            
            return list(users)
            
        except Exception as e:
            logger.error(f"Error getting users by company: {e}")
            raise
    
    async def update_user_type(
        self,
        user_id: Union[str, UUID],
        user_type: Union[str, UserTypeEnum],
        type_data: Optional[Dict[str, Any]] = None
    ) -> Optional[User]:
        """Update user type and related data"""
        try:
            user = await self.get_user_by_id(user_id=user_id)
            if not user:
                raise NotFoundError(f"User {user_id} not found", resource_type="user", resource_id=str(user_id))
            
            user.set_user_type(user_type, type_data)
            
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Updated user {user_id} to type {user_type}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user type: {e}")
            await self.db.rollback()
            raise
    
    async def complete_onboarding(
        self,
        user_id: Union[str, UUID],
        goals: Optional[List[str]] = None,
        experience_level: str = "beginner"
    ) -> Optional[User]:
        """Complete user onboarding process"""
        try:
            user = await self.get_user_by_id(user_id=user_id)
            if not user:
                raise NotFoundError(f"User {user_id} not found", resource_type="user", resource_id=str(user_id))
            
            user.complete_onboarding(goals, experience_level)
            
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Completed onboarding for user {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error completing onboarding: {e}")
            await self.db.rollback()
            raise
    
    async def update_onboarding_step(
        self,
        user_id: Union[str, UUID],
        step: int,
        step_data: Optional[Dict[str, Any]] = None
    ) -> Optional[User]:
        """Update onboarding step"""
        try:
            user = await self.get_user_by_id(user_id=user_id)
            if not user:
                raise NotFoundError(f"User {user_id} not found", resource_type="user", resource_id=str(user_id))
            
            user.update_onboarding_step(step, step_data)
            
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Updated onboarding step for user {user_id} to step {step}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating onboarding step: {e}")
            await self.db.rollback()
            raise
    
    # Password and security management
    async def update_password(
        self,
        user_id: Union[str, UUID],
        new_password: str
    ) -> bool:
        """Update user password"""
        try:
            user = await self.get_user_by_id(user_id=user_id)
            if not user:
                raise NotFoundError(f"User {user_id} not found", resource_type="user", resource_id=str(user_id))
            
            user.set_password(new_password)
            await self.db.commit()
            
            logger.info(f"Updated password for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating password: {e}")
            await self.db.rollback()
            return False
    
    async def change_password(
        self,
        user_id: Union[str, UUID],
        current_password: str,
        new_password: str
    ) -> bool:
        """Change user password with current password verification"""
        try:
            user = await self.get_user_by_id(user_id=user_id)
            if not user:
                raise NotFoundError(f"User {user_id} not found", resource_type="user", resource_id=str(user_id))
            
            if not user.verify_password(current_password):
                logger.warning(f"Invalid current password for user {user_id}")
                return False
            
            user.set_password(new_password)
            await self.db.commit()
            
            logger.info(f"Password changed for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            await self.db.rollback()
            return False
    
    async def deactivate_user(
        self,
        user_id: Union[str, UUID]
    ) -> bool:
        """Deactivate a user account"""
        try:
            user = await self.get_user_by_id(user_id=user_id)
            if not user:
                raise NotFoundError(f"User {user_id} not found", resource_type="user", resource_id=str(user_id))
            
            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)
            
            await self.db.commit()
            
            logger.info(f"Deactivated user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            await self.db.rollback()
            return False
    
    async def activate_user(
        self,
        user_id: Union[str, UUID]
    ) -> bool:
        """Activate a user account"""
        try:
            user = await self.get_user_by_id(user_id=user_id)
            if not user:
                raise NotFoundError(f"User {user_id} not found", resource_type="user", resource_id=str(user_id))
            
            user.is_active = True
            user.updated_at = datetime.now(timezone.utc)
            
            await self.db.commit()
            
            logger.info(f"Activated user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error activating user: {e}")
            await self.db.rollback()
            return False
    
    # Usage tracking
    async def update_usage_stats(
        self,
        user_id: Union[str, UUID],
        campaigns_increment: int = 0,
        analysis_increment: int = 0,
        intelligence_increment: int = 0,
        content_increment: int = 0
    ) -> Optional[User]:
        """Update user usage statistics"""
        try:
            user = await self.get_user_by_id(user_id=user_id)
            if not user:
                raise NotFoundError(f"User {user_id} not found", resource_type="user", resource_id=str(user_id))
            
            user.increment_usage(
                campaigns=campaigns_increment,
                analysis=analysis_increment,
                intelligence=intelligence_increment,
                content=content_increment
            )
            
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Updated usage stats for user {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating usage stats: {e}")
            await self.db.rollback()
            raise
    
    async def record_user_activity(
        self,
        user_id: Union[str, UUID]
    ) -> None:
        """Record user activity"""
        try:
            user = await self.get_user_by_id(user_id=user_id)
            if user:
                user.record_activity()
                await self.db.commit()
                
        except Exception as e:
            logger.error(f"Error recording user activity: {e}")
    
    # Utility methods
    async def get_user_usage_summary(
        self,
        user_id: Union[str, UUID]
    ) -> Dict[str, Any]:
        """Get comprehensive user usage summary"""
        try:
            user = await self.get_user_by_id(user_id=user_id, include_company=True)
            if not user:
                raise NotFoundError(f"User {user_id} not found", resource_type="user", resource_id=str(user_id))
            
            return user.get_usage_summary()
            
        except Exception as e:
            logger.error(f"Error getting usage summary: {e}")
            raise
    
    async def search_users(
        self,
        query: str,
        company_id: Optional[Union[str, UUID]] = None,
        limit: int = 50
    ) -> List[User]:
        """Search users by email or name"""
        try:
            search_query = select(User).options(selectinload(User.company))
            
            # Add search conditions
            search_conditions = [
                User.email.ilike(f"%{query}%"),
                User.full_name.ilike(f"%{query}%")
            ]
            
            search_query = search_query.where(or_(*search_conditions))
            
            if company_id:
                search_query = search_query.where(User.company_id == str(company_id))
            
            search_query = search_query.limit(limit)
            
            result = await self.db.execute(search_query)
            users = result.scalars().all()
            
            return list(users)
            
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            raise

    async def get_all_users(self) -> List[User]:
        """Get all users (admin only)"""
        try:
            result = await self.db.execute(
                select(User).options(selectinload(User.company))
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise

    # Demo campaign creation
    async def create_demo_campaign(self, user: User) -> bool:
        """Create a demo campaign for new users to showcase platform capabilities"""
        try:
            # Import Campaign models here to avoid circular imports
            from src.campaigns.models.campaign import Campaign, CampaignTypeEnum, CampaignStatusEnum
            
            # Check if user already has campaigns
            existing_campaigns = await self.db.execute(
                select(func.count(Campaign.id)).where(Campaign.user_id == user.id)
            )
            campaign_count = existing_campaigns.scalar() or 0
            
            if campaign_count > 0:
                logger.info(f"User {user.id} already has {campaign_count} campaigns, skipping demo")
                return False
            
            # Create a comprehensive demo campaign
            demo_campaign = Campaign(
                name="🌟 Welcome to CampaignForge - Demo Campaign",
                description="This is your demo campaign showcasing CampaignForge's powerful AI-driven marketing capabilities. Explore features like intelligent product analysis, automated content generation, and multi-channel campaign orchestration.",
                campaign_type=CampaignTypeEnum.PRODUCT_LAUNCH,
                status=CampaignStatusEnum.ACTIVE,
                user_id=user.id,
                company_id=user.company_id,
                target_audience="Health-conscious consumers seeking natural wellness solutions",
                goals=[
                    "Demonstrate AI-powered product intelligence",
                    "Showcase multi-channel content generation",
                    "Highlight campaign optimization features",
                    "Provide onboarding experience for new users"
                ],
                settings={
                    "is_demo": True,
                    "demo_hidden": False,  # Show demo by default
                    "demo_created_at": datetime.now(timezone.utc).isoformat(),
                    "ai_analysis_enabled": True,
                    "content_generation_enabled": True,
                    "optimization_enabled": True,
                    "channels": ["email", "social_media", "landing_page"],
                    "demo_product": {
                        "name": "VitalBoost Pro - Premium Health Supplement",
                        "category": "Health & Wellness",
                        "price": "$49.99",
                        "key_benefits": [
                            "Boosts energy naturally with organic ingredients",
                            "Supports immune system function",
                            "Enhances mental clarity and focus",
                            "Made with clinically-tested compounds"
                        ],
                        "target_market": "Active adults 25-55 seeking natural wellness",
                        "unique_selling_points": [
                            "Third-party tested for purity",
                            "90-day money-back guarantee", 
                            "Formulated by certified nutritionists",
                            "Sustainable packaging"
                        ]
                    },
                    "demo_intelligence": {
                        "confidence_score": 0.94,
                        "market_analysis": "High-growth health supplement market with strong online presence",
                        "competitive_advantages": [
                            "Premium organic ingredient sourcing",
                            "Transparent third-party testing",
                            "Strong customer testimonial portfolio"
                        ],
                        "campaign_angles": [
                            "Natural energy without crashes",
                            "Science-backed wellness solution",
                            "Transform your daily vitality"
                        ]
                    }
                }
            )
            
            self.db.add(demo_campaign)
            await self.db.commit()
            await self.db.refresh(demo_campaign)
            
            logger.info(f"Created demo campaign for user {user.id}: {demo_campaign.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating demo campaign for user {user.id}: {e}")
            await self.db.rollback()
            return False

    async def create_global_demo_campaign(self) -> bool:
        """Create a single global demo campaign that will be shown to all users"""
        try:
            # Import Campaign models here to avoid circular imports
            from src.campaigns.models.campaign import Campaign, CampaignTypeEnum, CampaignStatusEnum
            
            # Check if global demo already exists
            existing_demo = await self.db.execute(
                select(Campaign).where(Campaign.user_id == None, 
                                     Campaign.settings['is_demo'] == True)
            )
            if existing_demo.scalar():
                logger.info("Global demo campaign already exists, skipping creation")
                return True
            
            # Create the global demo campaign
            global_demo = Campaign(
                name="🌟 Welcome to CampaignForge - Global Demo",
                description="This is a shared demo campaign showcasing CampaignForge's AI-driven marketing capabilities. This campaign demonstrates intelligent product analysis, automated content generation, multi-channel orchestration, and conversion optimization for all new users.",
                campaign_type=CampaignTypeEnum.PRODUCT_LAUNCH,
                status=CampaignStatusEnum.ACTIVE,
                user_id=None,  # Global campaign - no specific user
                company_id=None,  # Global campaign - no specific company
                target_audience="Health-conscious consumers seeking premium wellness solutions",
                goals=[
                    "Showcase AI-powered product intelligence across industries",
                    "Demonstrate multi-channel content generation capabilities",
                    "Highlight advanced campaign optimization features",
                    "Provide comprehensive onboarding experience for all users"
                ],
                settings={
                    "is_demo": True,
                    "is_global_demo": True,  # Special flag for global demos
                    "demo_created_at": datetime.now(timezone.utc).isoformat(),
                    "ai_analysis_enabled": True,
                    "content_generation_enabled": True,
                    "optimization_enabled": True,
                    "multi_platform_enabled": True,
                    "channels": ["email", "social_media", "landing_page", "ads", "video"],
                    "demo_product": {
                        "name": "VitalBoost Pro - Premium Health Supplement",
                        "category": "Health & Wellness",
                        "price": "$49.99",
                        "key_benefits": [
                            "Boosts energy naturally with organic ingredients",
                            "Supports immune system and cognitive function",
                            "Enhances mental clarity and physical performance",
                            "Made with clinically-tested, third-party verified compounds"
                        ],
                        "target_market": "Active professionals 25-55 seeking natural wellness optimization",
                        "unique_selling_points": [
                            "Third-party tested for purity and potency",
                            "90-day money-back satisfaction guarantee", 
                            "Formulated by certified nutritionists and researchers",
                            "Sustainable packaging and ethical sourcing"
                        ]
                    },
                    "demo_intelligence": {
                        "confidence_score": 0.96,
                        "market_analysis": "High-growth $50B+ health supplement market with strong online presence and recurring purchase patterns",
                        "competitive_advantages": [
                            "Premium organic ingredient sourcing with full traceability",
                            "Transparent third-party testing and batch verification",
                            "Strong customer testimonial portfolio and retention rates",
                            "Multi-channel marketing integration and optimization"
                        ],
                        "campaign_angles": [
                            "Natural energy without crashes or jitters",
                            "Science-backed wellness solution for peak performance",
                            "Transform your daily vitality and mental clarity",
                            "Premium ingredients for professionals who demand results"
                        ],
                        "estimated_metrics": {
                            "conversion_rate": "4.2%",
                            "customer_lifetime_value": "$180",
                            "market_penetration": "High growth potential",
                            "recommended_budget": "$2,500/month"
                        }
                    }
                }
            )
            
            self.db.add(global_demo)
            await self.db.commit()
            await self.db.refresh(global_demo)
            
            logger.info(f"Created global demo campaign: {global_demo.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating global demo campaign: {e}")
            await self.db.rollback()
            return False

    async def ensure_user_has_demo_campaign(self, user_id: Union[str, UUID]) -> bool:
        """Ensure user has a demo campaign, create one if they don't"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            return await self.create_demo_campaign(user)
            
        except Exception as e:
            logger.error(f"Error ensuring demo campaign for user {user_id}: {e}")
            return False

    async def toggle_demo_campaign_visibility(self, user_id: Union[str, UUID], hidden: bool = True) -> bool:
        """Toggle demo campaign visibility for a user"""
        try:
            # Import Campaign models here to avoid circular imports
            from src.campaigns.models.campaign import Campaign, CampaignTypeEnum, CampaignStatusEnum
            from sqlalchemy import text
            
            # Find the demo campaign for this user
            result = await self.db.execute(
                text("""
                    UPDATE campaigns 
                    SET settings = jsonb_set(settings, '{demo_hidden}', :hidden::jsonb)
                    WHERE user_id = :user_id 
                    AND settings->>'is_demo' = 'true'
                    RETURNING id
                """),
                {"user_id": str(user_id), "hidden": str(hidden).lower()}
            )
            
            updated_campaign = result.fetchone()
            
            if updated_campaign:
                await self.db.commit()
                action = "hidden" if hidden else "shown"
                logger.info(f"Demo campaign {action} for user {user_id}")
                return True
            else:
                logger.warning(f"No demo campaign found for user {user_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error toggling demo campaign visibility for user {user_id}: {e}")
            await self.db.rollback()
            return False

    async def get_user_campaigns(self, user_id: Union[str, UUID], include_hidden_demos: bool = False) -> List:
        """Get user campaigns with option to exclude hidden demo campaigns, plus global demo"""
        try:
            # Import Campaign models here to avoid circular imports
            from src.campaigns.models.campaign import Campaign
            from sqlalchemy import text, or_
            
            # Check if user has hidden the global demo
            user_settings = await self.get_user_demo_settings(user_id)
            global_demo_hidden = user_settings.get("global_demo_hidden", False)
            
            if include_hidden_demos:
                # Include all user campaigns + global demo (even if hidden)
                query = text("""
                    SELECT * FROM campaigns 
                    WHERE user_id = :user_id 
                       OR (user_id IS NULL AND settings->>'is_global_demo' = 'true')
                    ORDER BY created_at DESC
                """)
                result = await self.db.execute(query, {"user_id": str(user_id)})
                campaigns = result.fetchall()
                return list(campaigns)
            else:
                # Build query to exclude hidden demos but include global demo if not hidden by user
                if global_demo_hidden:
                    # User has hidden global demo, exclude it
                    query = text("""
                        SELECT * FROM campaigns 
                        WHERE user_id = :user_id 
                        AND NOT (
                            settings->>'is_demo' = 'true' 
                            AND settings->>'demo_hidden' = 'true'
                        )
                        ORDER BY created_at DESC
                    """)
                else:
                    # Include global demo since user hasn't hidden it
                    query = text("""
                        SELECT * FROM campaigns 
                        WHERE (
                            user_id = :user_id 
                            AND NOT (
                                settings->>'is_demo' = 'true' 
                                AND settings->>'demo_hidden' = 'true'
                            )
                        ) OR (
                            user_id IS NULL 
                            AND settings->>'is_global_demo' = 'true'
                        )
                        ORDER BY created_at DESC
                    """)
                
                result = await self.db.execute(query, {"user_id": str(user_id)})
                campaigns = result.fetchall()
                return list(campaigns)
            
        except Exception as e:
            logger.error(f"Error getting campaigns for user {user_id}: {e}")
            return []

    async def get_user_demo_settings(self, user_id: Union[str, UUID]) -> Dict[str, Any]:
        """Get user's demo campaign visibility settings"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user or not user.settings:
                return {}
            return user.settings.get("demo_settings", {})
        except Exception as e:
            logger.error(f"Error getting demo settings for user {user_id}: {e}")
            return {}
    
    async def set_user_demo_settings(self, user_id: Union[str, UUID], settings: Dict[str, Any]) -> bool:
        """Set user's demo campaign visibility settings"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            if not user.settings:
                user.settings = {}
            
            user.settings["demo_settings"] = settings
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting demo settings for user {user_id}: {e}")
            await self.db.rollback()
            return False