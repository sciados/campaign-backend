# src/core/crud/user_crud.py
"""
User-specific CRUD operations
Handles all User model database operations with multi-user type support
Uses proven async patterns from base CRUD
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
import logging

from src.models.user import User
from .base_crud import BaseCRUD

logger = logging.getLogger(__name__)

class UserCRUD(BaseCRUD[User]):
    """
    User CRUD with specialized methods for multi-user type system
    Extends base CRUD with user-specific operations
    """
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> Optional[User]:
        """Get user by email address"""
        try:
            logger.debug(f"Getting user by email: {email}")
            
            return await self.get_by_field(
                db=db,
                field_name="email",
                field_value=email
            )
            
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise
    
    async def get_users_by_company(
        self,
        db: AsyncSession,
        company_id: UUID,
        skip: int = 0,
        limit: int = 100,
        user_type: Optional[str] = None,
        is_active: Optional[bool] = True
    ) -> List[User]:
        """Get all users for a company with optional filtering"""
        try:
            logger.info(f"Getting users for company {company_id}")
            
            filters = {"company_id": company_id}
            
            if user_type:
                filters["user_type"] = user_type
            
            if is_active is not None:
                filters["is_active"] = is_active
            
            users = await self.get_multi(
                db=db,
                skip=skip,
                limit=limit,
                filters=filters,
                order_by="created_at",
                order_desc=True
            )
            
            logger.info(f"Found {len(users)} users for company")
            return users
            
        except Exception as e:
            logger.error(f"Error getting users by company: {e}")
            raise
    
    async def get_users_by_type(
        self,
        db: AsyncSession,
        user_type: str,
        company_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get users by user type"""
        try:
            logger.info(f"Getting users of type: {user_type}")
            
            filters = {"user_type": user_type}
            
            if company_id:
                filters["company_id"] = company_id
            
            users = await self.get_multi(
                db=db,
                skip=skip,
                limit=limit,
                filters=filters,
                order_by="created_at",
                order_desc=True
            )
            
            logger.info(f"Found {len(users)} users of type {user_type}")
            return users
            
        except Exception as e:
            logger.error(f"Error getting users by type: {e}")
            raise
    
    async def update_user_type(
        self,
        db: AsyncSession,
        user_id: UUID,
        user_type: str,
        type_data: Optional[Dict[str, Any]] = None
    ) -> Optional[User]:
        """Update user type and related data"""
        try:
            logger.info(f"Updating user {user_id} to type: {user_type}")
            
            user = await self.get(db=db, id=user_id)
            if not user:
                return None
            
            # Use the user model's method to set type
            user.set_user_type(user_type, type_data)
            
            # Update in database
            updated_user = await self.update(
                db=db,
                db_obj=user,
                obj_in={}  # Changes already made to object
            )
            
            logger.info(f"Updated user {user_id} to type {user_type}")
            return updated_user
            
        except Exception as e:
            logger.error(f"Error updating user type: {e}")
            await db.rollback()
            raise
    
    async def complete_onboarding(
        self,
        db: AsyncSession,
        user_id: UUID,
        goals: Optional[List[str]] = None,
        experience_level: str = "beginner"
    ) -> Optional[User]:
        """Complete user onboarding process"""
        try:
            logger.info(f"Completing onboarding for user {user_id}")
            
            user = await self.get(db=db, id=user_id)
            if not user:
                return None
            
            # Use the user model's method
            user.complete_onboarding(goals, experience_level)
            
            # Update in database
            updated_user = await self.update(
                db=db,
                db_obj=user,
                obj_in={}  # Changes already made to object
            )
            
            logger.info(f"Completed onboarding for user {user_id}")
            return updated_user
            
        except Exception as e:
            logger.error(f"Error completing onboarding: {e}")
            await db.rollback()
            raise
    
    async def increment_usage_counters(
        self,
        db: AsyncSession,
        user_id: UUID,
        counter_type: str,
        increment: int = 1
    ) -> bool:
        """Increment user usage counters"""
        try:
            user = await self.get(db=db, id=user_id)
            if not user:
                return False
            
            update_data = {"updated_at": datetime.now(timezone.utc)}
            
            if counter_type == "campaigns":
                update_data["monthly_campaigns_used"] = (user.monthly_campaigns_used or 0) + increment
                update_data["total_campaigns_created"] = (user.total_campaigns_created or 0) + increment
            elif counter_type == "analysis":
                update_data["monthly_analysis_used"] = (user.monthly_analysis_used or 0) + increment
            elif counter_type == "intelligence":
                update_data["total_intelligence_generated"] = (user.total_intelligence_generated or 0) + increment
            elif counter_type == "content":
                update_data["total_content_generated"] = (user.total_content_generated or 0) + increment
            else:
                logger.warning(f"Unknown counter type: {counter_type}")
                return False
            
            await self.update(db=db, db_obj=user, obj_in=update_data)
            
            logger.info(f"Incremented {counter_type} counter for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing usage counter: {e}")
            await db.rollback()
            return False
    
    async def get_user_usage_stats(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Get user usage statistics"""
        try:
            user = await self.get(db=db, id=user_id)
            if not user:
                return {"error": "User not found"}
            
            return user.get_usage_summary()
            
        except Exception as e:
            logger.error(f"Error getting user usage stats: {e}")
            return {"error": str(e)}
    
    async def reset_monthly_usage(
        self,
        db: AsyncSession,
        user_id: Optional[UUID] = None,
        company_id: Optional[UUID] = None
    ) -> int:
        """Reset monthly usage counters"""
        try:
            logger.info("Resetting monthly usage counters")
            
            filters = {}
            if user_id:
                filters["id"] = user_id
            if company_id:
                filters["company_id"] = company_id
            
            users = await self.get_multi(
                db=db,
                filters=filters,
                limit=1000  # Get all matching users
            )
            
            reset_count = 0
            for user in users:
                await self.update(
                    db=db,
                    db_obj=user,
                    obj_in={
                        "monthly_campaigns_used": 0,
                        "monthly_analysis_used": 0
                    }
                )
                reset_count += 1
            
            logger.info(f"Reset monthly usage for {reset_count} users")
            return reset_count
            
        except Exception as e:
            logger.error(f"Error resetting monthly usage: {e}")
            await db.rollback()
            raise


# Create the global instance
user_crud = UserCRUD()