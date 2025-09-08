# src/core/crud/campaign_crud.py
"""
Campaign-specific CRUD operations
🎯 Extends base CRUD with campaign-specific methods
✅ Provides consistent database access for campaigns
🔧 CRITICAL FIXES: Added proper enum handling, transaction safety, and missing methods
"""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime, timezone, timedelta
from campaigns.schemas.campaign import CampaignWorkflowUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
import logging

from src.campaigns.models.campaign import Campaign, CampaignStatusEnum, CampaignTypeEnum
from src.core.crud.base_crud import BaseCRUD

logger = logging.getLogger(__name__)

class CampaignCRUD(BaseCRUD[Campaign]):
    """
    Campaign CRUD with specialized methods
    🔧 FIXED: Proper enum handling and transaction management
    """
    
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
            
            # 🔧 FIXED: Add status filter with proper enum handling
            if status_filter:
                try:
                    # Convert string to enum if needed
                    if isinstance(status_filter, str):
                        status_enum = CampaignStatusEnum(status_filter.upper())
                        filters["status"] = status_enum
                    else:
                        filters["status"] = status_filter
                except ValueError:
                    logger.warning(f"Invalid status filter: {status_filter}")
                    # Continue without status filter if invalid
            
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
            # 🔧 FIXED: Add transaction rollback on error
            await db.rollback()
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
            return None  # Don't raise on access check failures
    
    async def get_campaign_stats(
        self,
        db: AsyncSession,
        user_id: Optional[UUID] = None,  # 🔧 FIXED: Make user_id optional for company-wide stats
        company_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get campaign statistics with proper enum handling
        🔧 FIXED: Status enum conversion and transaction safety
        """
        try:
            logger.info(f"📊 Getting campaign stats for user {user_id}")
            
            # Build base filters
            filters = {}
            if company_id:
                filters["company_id"] = company_id
            if user_id:
                filters["user_id"] = user_id
            
            # 🔧 FIXED: Get total campaigns safely
            try:
                total_campaigns = await self.count(db=db, filters=filters)
            except Exception as count_error:
                logger.warning(f"Error counting total campaigns: {count_error}")
                total_campaigns = 0
            
            # 🔧 FIXED: Count by status with proper enum handling
            status_counts = {}
            for status_name in ["DRAFT", "IN_PROGRESS", "COMPLETED", "ARCHIVED"]:
                try:
                    # Convert string to proper enum
                    status_enum = CampaignStatusEnum(status_name)
                    status_filters = {**filters, "status": status_enum}
                    count = await self.count(db=db, filters=status_filters)
                    status_counts[status_name.lower()] = count
                except ValueError:
                    logger.warning(f"Status enum {status_name} not found")
                    status_counts[status_name.lower()] = 0
                except Exception as status_error:
                    logger.warning(f"Error counting {status_name} campaigns: {status_error}")
                    status_counts[status_name.lower()] = 0
            
            # 🔧 FIXED: Safe active campaigns count (use non-draft campaigns)
            active_campaigns = status_counts.get("in_progress", 0) + status_counts.get("completed", 0)
            
            # Calculate additional metrics safely
            try:
                # Get recent campaigns (last 30 days)
                thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
                
                recent_campaigns_stmt = select(func.count(Campaign.id)).where(
                    and_(
                        Campaign.company_id == company_id if company_id else True,
                        Campaign.user_id == user_id if user_id else True,
                        Campaign.created_at >= thirty_days_ago
                    )
                )
                
                result = await db.execute(recent_campaigns_stmt)
                recent_campaigns = result.scalar() or 0
                
            except Exception as recent_error:
                logger.warning(f"Error counting recent campaigns: {recent_error}")
                recent_campaigns = 0
            
            stats = {
                "total_campaigns_created": total_campaigns,  # Keep existing field name
                "total_campaigns": total_campaigns,
                "active_campaigns": active_campaigns,
                "draft_campaigns": status_counts.get("draft", 0),
                "completed_campaigns": status_counts.get("completed", 0),
                "recent_campaigns": recent_campaigns,
                "status_breakdown": status_counts,
                "user_id": str(user_id) if user_id else None,
                "company_id": str(company_id) if company_id else None,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Retrieved campaign stats: {total_campaigns} total campaigns")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting campaign stats: {e}")
            # 🔧 FIXED: Rollback on error to prevent transaction issues
            await db.rollback()
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
        new_status: Union[str, CampaignStatusEnum],  # 🔧 FIXED: Accept both string and enum
        company_id: UUID
    ) -> Optional[Campaign]:
        """Update campaign status with access check and proper enum handling"""
        try:
            logger.info(f"🔄 Updating campaign {campaign_id} status to {new_status}")
            
            # 🔧 FIXED: Convert string to enum if needed
            if isinstance(new_status, str):
                try:
                    status_enum = CampaignStatusEnum(new_status.upper())
                except ValueError:
                    logger.error(f"Invalid status: {new_status}")
                    return None
            else:
                status_enum = new_status
            
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
                obj_in={"status": status_enum}
            )
            
            logger.info(f"✅ Updated campaign {campaign_id} status to {status_enum.value}")
            return updated_campaign
            
        except Exception as e:
            logger.error(f"❌ Error updating campaign status: {e}")
            await db.rollback()
            raise
    
    # 🆕 NEW METHODS: Missing methods that dashboard_stats.py expects
    
    async def get_campaigns_by_status(
        self,
        db: AsyncSession,
        status: Union[str, CampaignStatusEnum],
        company_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Campaign]:
        """
        Get campaigns by status with proper enum handling
        🔧 FIXED: Status enum conversion
        """
        try:
            # 🔧 FIXED: Convert string status to enum if needed
            if isinstance(status, str):
                try:
                    status_enum = CampaignStatusEnum(status.upper())
                except ValueError:
                    logger.error(f"Invalid status: {status}")
                    return []
            else:
                status_enum = status
            
            # Build filters
            filters = {"status": status_enum}
            if company_id:
                filters["company_id"] = company_id
            if user_id:
                filters["user_id"] = user_id
            
            campaigns = await self.get_multi(
                db=db,
                skip=skip,
                limit=limit,
                filters=filters,
                order_by="updated_at",
                order_desc=True
            )
            
            return campaigns
            
        except Exception as e:
            logger.error(f"❌ Error getting campaigns by status: {e}")
            return []
    
    async def update_workflow_state(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        new_state: Union[str, CampaignWorkflowUpdate],
        completion_percentage: Optional[int] = None
    ) -> Optional[Campaign]:
        """
        Update campaign workflow state
        🔧 FIXED: Enum handling and transaction safety
        """
        try:
            # Get campaign
            campaign = await self.get(db=db, id=campaign_id)
            if not campaign:
                return None
            
            # 🔧 FIXED: Convert string to enum if needed
            # Use the actual model methods instead
            campaign.update_workflow_step(int(new_state) if isinstance(new_state, str) else new_state)
            if completion_percentage == 100:
                campaign.mark_workflow_complete()
            
            if isinstance(new_state, str):
                workflow_step = int(new_state) if new_state.isdigit() else 0
            else:
                workflow_step = new_state

            # Use the actual model method
            campaign.update_workflow_step(workflow_step)

            if completion_percentage == 100:
                campaign.mark_workflow_complete()

            # Commit the changes
            await db.commit()
            await db.refresh(campaign)
            updated_campaign = campaign
            
            # logger.info(f"✅ Updated workflow state for campaign {campaign_id} to {state_enum.value}")
            return updated_campaign
            
        except Exception as e:
            logger.error(f"❌ Error updating workflow state: {e}")
            await db.rollback()
            return None
    
    async def increment_counters(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        counter_type: str,
        increment: int = 1
    ) -> bool:
        """
        Increment campaign counters safely
        🔧 FIXED: Safe counter updates with transaction handling
        """
        try:
            campaign = await self.get(db=db, id=campaign_id)
            if not campaign:
                return False
            
            # Update appropriate counter
            update_data = {"updated_at": datetime.now(timezone.utc)}
            
            if counter_type == "sources":
                current_count = getattr(campaign, 'sources_count', 0) or 0
                update_data["sources_count"] = current_count + increment
            elif counter_type == "intelligence":
                current_count = getattr(campaign, 'intelligence_count', 0) or 0
                update_data["intelligence_count"] = current_count + increment
            elif counter_type == "content":
                current_count = getattr(campaign, 'generated_content_count', 0) or 0
                update_data["generated_content_count"] = current_count + increment
            else:
                logger.warning(f"Unknown counter type: {counter_type}")
                return False
            
            # Update campaign
            await self.update(db=db, db_obj=campaign, obj_in=update_data)
            
            logger.info(f"✅ Incremented {counter_type} counter for campaign {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error incrementing counter: {e}")
            await db.rollback()
            return False
    
    async def get_campaign_insights(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get campaign insights for dashboard
        🆕 NEW: Method that dashboard_stats.py expects
        """
        try:
            logger.info(f"📊 Getting campaign insights for user {user_id}")
            
            # Get basic stats
            stats = await self.get_campaign_stats(
                db=db,
                user_id=user_id,
                company_id=company_id
            )
            
            # Get additional insights
            insights = {
                "basic_stats": stats,
                "user_activity": {
                    "total_campaigns_created": stats.get("total_campaigns", 0),
                    "completion_rate": self._calculate_completion_rate(stats),
                    "most_active_period": "recent",
                    "user_engagement": "active" if stats.get("recent_campaigns", 0) > 0 else "low"
                },
                "recommendations": [],
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Add recommendations based on stats
            if stats.get("total_campaigns", 0) == 0:
                insights["recommendations"].append("Create your first campaign to get started")
            elif stats.get("draft_campaigns", 0) > stats.get("completed_campaigns", 0):
                insights["recommendations"].append("Complete your draft campaigns for better results")
            else:
                insights["recommendations"].append("Great progress! Consider creating new campaigns")
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error getting campaign insights: {e}")
            return {"error": str(e)}
    
    async def get_campaign_performance_metrics(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get campaign performance metrics for dashboard
        🆕 NEW: Method that dashboard_stats.py expects
        """
        try:
            logger.info(f"📈 Getting performance metrics for user {user_id}")
            
            # Get basic metrics
            metrics = {
                "query_performance": {
                    "average_response_time": 0.15,  # Mock data - replace with real metrics
                    "slow_queries": 0,
                    "successful_queries": 100,
                    "failed_queries": 0
                },
                "campaign_metrics": {
                    "creation_success_rate": 100.0,
                    "analysis_completion_rate": 85.0,
                    "content_generation_rate": 90.0
                },
                "system_health": {
                    "memory_usage": 45,
                    "cpu_usage": 30,
                    "database_connections": 5
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_completion_rate(self, stats: Dict[str, Any]) -> float:
        """Calculate campaign completion rate from stats"""
        try:
            total = stats.get("total_campaigns", 0)
            completed = stats.get("completed_campaigns", 0)
            
            if total == 0:
                return 0.0
            
            return round((completed / total) * 100, 1)
            
        except Exception:
            return 0.0