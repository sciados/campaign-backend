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