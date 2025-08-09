# src/core/crud/campaign_crud.py
"""
Campaign-specific CRUD operations
🎯 Extends base CRUD with campaign-specific methods
✅ Provides consistent database access for campaigns
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
import logging

from src.models.campaign import Campaign
from .base_crud import BaseCRUD

logger = logging.getLogger(__name__)

class CampaignCRUD(BaseCRUD[Campaign]):
    """Campaign CRUD with specialized methods"""
    
    def __init__(self):
        super().__init__(Campaign)
    
    async def get_user_campaigns(
        self,
        db: AsyncSession,
        user_id: UUID,
        company_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None
    ) -> List[Campaign]:
        """
        Get campaigns for a specific user/company
        🔧 Replaces direct database queries in campaign routes
        """
        try:
            logger.info(f"📋 Getting campaigns for user {user_id}, company {company_id}")
            
            filters = {
                "user_id": user_id,
                "company_id": company_id
            }
            
            # Add status filter if provided
            if status_filter:
                filters["status"] = status_filter
            
            campaigns = await self.get_multi(
                db=db,
                skip=skip,
                limit=limit,
                filters=filters,
                order_by="updated_at",
                order_desc=True
            )
            
            logger.info(f"✅ Found {len(campaigns)} campaigns for user")
            return campaigns
            
        except Exception as e:
            logger.error(f"❌ Error getting user campaigns: {e}")
            raise
    
    async def get_campaign_with_access_check(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        company_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Optional[Campaign]:
        """
        Get campaign with access verification
        🔐 Ensures user has access to the campaign
        """
        try:
            logger.info(f"🔐 Getting campaign {campaign_id} with access check")
            
            filters = {
                "id": campaign_id,
                "company_id": company_id
            }
            
            # Add user filter if specified
            if user_id:
                filters["user_id"] = user_id
            
            campaigns = await self.get_multi(
                db=db,
                filters=filters,
                limit=1
            )
            
            if not campaigns:
                logger.warning(f"⚠️ Campaign {campaign_id} not found or access denied")
                return None
            
            campaign = campaigns[0]
            logger.info(f"✅ Campaign access granted: {campaign.title}")
            return campaign
            
        except Exception as e:
            logger.error(f"❌ Error getting campaign with access check: {e}")
            raise
    
    async def get_campaign_stats(
        self,
        db: AsyncSession,
        user_id: UUID,
        company_id: UUID
    ) -> Dict[str, Any]:
        """Get campaign statistics for user/company"""
        try:
            logger.info(f"📊 Getting campaign stats for user {user_id}")
            
            # Count campaigns by status
            filters_base = {
                "user_id": user_id,
                "company_id": company_id
            }
            
            # Total campaigns
            total_campaigns = await self.count(db=db, filters=filters_base)
            
            # Active campaigns (assuming 'active' status exists)
            active_filters = {**filters_base, "status": "active"}
            active_campaigns = await self.count(db=db, filters=active_filters)
            
            # Draft campaigns
            draft_filters = {**filters_base, "status": "draft"}
            draft_campaigns = await self.count(db=db, filters=draft_filters)
            
            # Completed campaigns
            completed_filters = {**filters_base, "status": "completed"}
            completed_campaigns = await self.count(db=db, filters=completed_filters)
            
            stats = {
                "total_campaigns_created": total_campaigns,
                "active_campaigns": active_campaigns,
                "draft_campaigns": draft_campaigns,
                "completed_campaigns": completed_campaigns,
                "user_id": str(user_id),
                "company_id": str(company_id)
            }
            
            logger.info(f"✅ Campaign stats: {total_campaigns} total, {active_campaigns} active")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting campaign stats: {e}")
            raise
    
    async def get_recent_campaigns(
        self,
        db: AsyncSession,
        user_id: UUID,
        company_id: UUID,
        limit: int = 5
    ) -> List[Campaign]:
        """Get most recently updated campaigns"""
        try:
            logger.info(f"🕒 Getting recent campaigns for user {user_id}")
            
            campaigns = await self.get_user_campaigns(
                db=db,
                user_id=user_id,
                company_id=company_id,
                skip=0,
                limit=limit
            )
            
            logger.info(f"✅ Found {len(campaigns)} recent campaigns")
            return campaigns
            
        except Exception as e:
            logger.error(f"❌ Error getting recent campaigns: {e}")
            raise
    
    async def search_campaigns(
        self,
        db: AsyncSession,
        user_id: UUID,
        company_id: UUID,
        search_term: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Campaign]:
        """Search campaigns by title or description"""
        try:
            logger.info(f"🔍 Searching campaigns for term: {search_term}")
            
            # For now, get all user campaigns and filter in Python
            # In a production system, you'd use SQL LIKE or full-text search
            all_campaigns = await self.get_user_campaigns(
                db=db,
                user_id=user_id,
                company_id=company_id,
                skip=0,
                limit=1000  # Get more to search through
            )
            
            # Filter by search term
            search_lower = search_term.lower()
            filtered_campaigns = []
            
            for campaign in all_campaigns:
                title_match = campaign.title and search_lower in campaign.title.lower()
                desc_match = campaign.description and search_lower in campaign.description.lower()
                
                if title_match or desc_match:
                    filtered_campaigns.append(campaign)
            
            # Apply pagination to filtered results
            paginated_campaigns = filtered_campaigns[skip:skip + limit]
            
            logger.info(f"✅ Found {len(paginated_campaigns)} campaigns matching '{search_term}'")
            return paginated_campaigns
            
        except Exception as e:
            logger.error(f"❌ Error searching campaigns: {e}")
            raise
    
    async def update_campaign_status(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        new_status: str,
        company_id: UUID
    ) -> Optional[Campaign]:
        """Update campaign status with access check"""
        try:
            logger.info(f"🔄 Updating campaign {campaign_id} status to {new_status}")
            
            # First verify access
            campaign = await self.get_campaign_with_access_check(
                db=db,
                campaign_id=campaign_id,
                company_id=company_id
            )
            
            if not campaign:
                return None
            
            # Update status
            updated_campaign = await self.update(
                db=db,
                db_obj=campaign,
                obj_in={"status": new_status}
            )
            
            logger.info(f"✅ Updated campaign {campaign_id} status to {new_status}")
            return updated_campaign
            
        except Exception as e:
            logger.error(f"❌ Error updating campaign status: {e}")
            raise