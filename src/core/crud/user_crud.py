# File: src/core/crud/user_crud.py
# Updated User CRUD to work with your existing User model and authentication

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
import logging

from src.models.user import User, Company
from .base_crud import BaseCRUD

logger = logging.getLogger(__name__)

class UserCRUD(BaseCRUD[User]):
    """
    User CRUD with authentication and multi-user type support
    """
    
    def __init__(self):
        super().__init__(User)
    
    async def create_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        full_name: str,
        company_name: str = "Default Company",
        role: str = "user"
    ) -> User:
        """Create a new user with company"""
        try:
            # Create company first
            company_slug = company_name.lower().replace(" ", "-").replace(".", "")
            company = Company(
                company_name=company_name,
                company_slug=company_slug,
                subscription_tier="free",
                monthly_credits_limit=1000,
                monthly_credits_used=0
            )
            db.add(company)
            await db.flush()  # Get the company ID
            
            # Create user
            user = User(
                email=email,
                full_name=full_name,
                company_id=company.id,
                role=role,
                is_active=True,
                is_verified=False,
                onboarding_completed=False,
                onboarding_step=0
            )
            # Use the User model's set_password method to hash the password
            user.set_password(password)
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            await db.refresh(company)
            
            # Load the company relationship
            user.company = company
            
            logger.info(f"Created user {user.id} with company {company.id}")
            return user
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_by_email(
        self,
        db: AsyncSession,
        email: str,
        include_company: bool = True
    ) -> Optional[User]:
        """Get user by email address with optional company info"""
        try:
            query = select(User).where(User.email == email)
            
            if include_company:
                query = query.options(selectinload(User.company))
            
            result = await db.execute(query)
            user = result.scalar_one_or_none()
            
            return user
            
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise
    
    async def get_by_id(
        self,
        db: AsyncSession,
        user_id: Union[str, UUID],
        include_company: bool = True
    ) -> Optional[User]:
        """Get user by ID with optional company info"""
        try:
            query = select(User).where(User.id == user_id)
            
            if include_company:
                query = query.options(selectinload(User.company))
            
            result = await db.execute(query)
            user = result.scalar_one_or_none()
            
            return user
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            raise
    
    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = await self.get_by_email(db=db, email=email, include_company=True)
            
            if not user:
                logger.warning(f"User not found for email: {email}")
                return None
            
            if not user.verify_password(password):
                logger.warning(f"Invalid password for user: {email}")
                return None
            
            if not user.is_active:
                logger.warning(f"User account is deactivated: {email}")
                return None
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            await db.commit()
            
            logger.info(f"User authenticated successfully: {user.id}")
            return user
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise
    
    async def get_users_by_company(
        self,
        db: AsyncSession,
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
            
            result = await db.execute(query)
            users = result.scalars().all()
            
            return list(users)
            
        except Exception as e:
            logger.error(f"Error getting users by company: {e}")
            raise
    
    async def update_user_type(
        self,
        db: AsyncSession,
        user_id: Union[str, UUID],
        user_type: str,
        type_data: Optional[Dict[str, Any]] = None
    ) -> Optional[User]:
        """Update user type and related data"""
        try:
            user = await self.get_by_id(db=db, user_id=user_id)
            if not user:
                return None
            
            user.set_user_type(user_type, type_data)
            
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Updated user {user_id} to type {user_type}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user type: {e}")
            await db.rollback()
            raise
    
    async def complete_onboarding(
        self,
        db: AsyncSession,
        user_id: Union[str, UUID],
        goals: Optional[List[str]] = None,
        experience_level: str = "beginner"
    ) -> Optional[User]:
        """Complete user onboarding process"""
        try:
            user = await self.get_by_id(db=db, user_id=user_id)
            if not user:
                return None
            
            user.complete_onboarding(goals, experience_level)
            
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Completed onboarding for user {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error completing onboarding: {e}")
            await db.rollback()
            raise
    
    async def update_password(
        self,
        db: AsyncSession,
        user_id: Union[str, UUID],
        new_password: str
    ) -> bool:
        """Update user password"""
        try:
            user = await self.get_by_id(db=db, user_id=user_id)
            if not user:
                return False
            
            user.set_password(new_password)
            await db.commit()
            
            logger.info(f"Updated password for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating password: {e}")
            await db.rollback()
            return False
    
    async def deactivate_user(
        self,
        db: AsyncSession,
        user_id: Union[str, UUID]
    ) -> bool:
        """Deactivate a user account"""
        try:
            user = await self.get_by_id(db=db, user_id=user_id)
            if not user:
                return False
            
            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            
            logger.info(f"Deactivated user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            await db.rollback()
            return False
    
    async def update_usage_stats(
        self,
        db: AsyncSession,
        user_id: Union[str, UUID],
        campaigns_increment: int = 0,
        analysis_increment: int = 0,
        intelligence_increment: int = 0,
        content_increment: int = 0
    ) -> Optional[User]:
        """Update user usage statistics"""
        try:
            user = await self.get_by_id(db=db, user_id=user_id)
            if not user:
                return None
            
            # Update monthly usage
            if campaigns_increment > 0:
                user.monthly_campaigns_used = (user.monthly_campaigns_used or 0) + campaigns_increment
                user.total_campaigns_created = (user.total_campaigns_created or 0) + campaigns_increment
            
            if analysis_increment > 0:
                user.monthly_analysis_used = (user.monthly_analysis_used or 0) + analysis_increment
            
            if intelligence_increment > 0:
                user.total_intelligence_generated = (user.total_intelligence_generated or 0) + intelligence_increment
            
            if content_increment > 0:
                user.total_content_generated = (user.total_content_generated or 0) + content_increment
            
            user.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Updated usage stats for user {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating usage stats: {e}")
            await db.rollback()
            raise

# Create the global instance
user_crud = UserCRUD()