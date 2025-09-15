# src/campaigns/services/campaign_service.py

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func, text
from sqlalchemy.orm import selectinload
import logging

from src.campaigns.models.campaign import Campaign, CampaignStatusEnum, CampaignTypeEnum
from src.core.shared.exceptions import NotFoundError

logger = logging.getLogger(__name__)

class CampaignService:
    """Complete Campaign business logic service with all legacy CRUD functionality"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============================================================================
    # CORE CRUD OPERATIONS
    # ============================================================================
    
    async def create_campaign(
        self,
        user_id: Union[str, UUID],
        name: str,
        campaign_type: Union[str, CampaignTypeEnum],
        description: Optional[str] = None,
        target_audience: Optional[str] = None,
        goals: Optional[List[str]] = None,
        company_id: Optional[Union[str, UUID]] = None
    ) -> Campaign:
        """Create a new campaign"""
        try:
            logger.info(f"Creating campaign '{name}' for user {user_id}")
            
            # Convert campaign type to valid string value for database
            if isinstance(campaign_type, str):
                try:
                    # First try the string value directly (e.g., "content_marketing")
                    campaign_type_enum = CampaignTypeEnum(campaign_type)
                    final_campaign_type = campaign_type_enum.value  # Extract string value
                except ValueError:
                    try:
                        # If that fails, try uppercase key (e.g., "CONTENT_MARKETING") and get its value
                        enum_obj = getattr(CampaignTypeEnum, campaign_type.upper())
                        final_campaign_type = enum_obj.value  # Extract string value
                    except (ValueError, AttributeError):
                        # If all else fails, pass the string as-is (should be a valid enum value)
                        final_campaign_type = campaign_type.lower()
                        logger.warning(f"Using campaign type as-is: {final_campaign_type}")
            else:
                # Already a CampaignTypeEnum object
                final_campaign_type = campaign_type.value if hasattr(campaign_type, 'value') else str(campaign_type)
            
            # Debug logging for enum conversion  
            logger.info(f"🔧 Input campaign_type: {campaign_type} (type: {type(campaign_type)})")
            logger.info(f"🔧 Final campaign_type: {final_campaign_type} (type: {type(final_campaign_type)})")
            
            # Convert UUIDs if strings
            user_uuid = UUID(str(user_id)) if isinstance(user_id, str) else user_id
            
            # Handle company_id - for now require it to be provided
            if not company_id:
                raise ValueError("company_id is required for campaign creation")
            
            company_uuid = UUID(str(company_id)) if isinstance(company_id, str) else company_id
            
            # Pass string values directly to avoid enum conversion issues
            final_status = CampaignStatusEnum.DRAFT.value
            logger.info(f"🔧 Final string values to DB: campaign_type='{final_campaign_type}', status='{final_status}'")
            
            campaign = Campaign(
                name=name,   # Campaign name
                description=description,
                campaign_type=final_campaign_type,  # Use string value
                user_id=user_uuid,
                company_id=company_uuid,
                target_audience=target_audience,
                goals=goals,
                status=final_status  # Use string value
            )
            
            self.db.add(campaign)
            await self.db.commit()
            await self.db.refresh(campaign)
            
            logger.info(f"Campaign created successfully: {campaign.id}")
            return campaign
            
        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            await self.db.rollback()
            raise
    
    async def get_campaign_by_id(
        self,
        campaign_id: Union[str, UUID],
        user_id: Optional[Union[str, UUID]] = None
    ) -> Optional[Campaign]:
        """Get campaign by ID with optional user verification"""
        try:
            campaign_uuid = UUID(str(campaign_id))
            query = select(Campaign).where(Campaign.id == campaign_uuid)
            
            if user_id:
                user_uuid = UUID(str(user_id))
                query = query.where(Campaign.user_id == user_uuid)
            
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting campaign by ID: {e}")
            return None
    
    async def get_campaign_with_access_check(
        self,
        campaign_id: Union[str, UUID],
        company_id: Union[str, UUID],
        user_id: Optional[Union[str, UUID]] = None
    ) -> Optional[Campaign]:
        """Get campaign with access verification"""
        try:
            logger.info(f"Getting campaign {campaign_id} with access check")
            
            campaign_uuid = UUID(str(campaign_id))
            company_uuid = UUID(str(company_id))
            
            query = select(Campaign).where(
                and_(
                    Campaign.id == campaign_uuid,
                    Campaign.company_id == company_uuid
                )
            )
            
            if user_id:
                user_uuid = UUID(str(user_id))
                query = query.where(Campaign.user_id == user_uuid)
            
            result = await self.db.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                logger.warning(f"Campaign {campaign_id} not found or access denied")
                return None
            
            logger.info(f"Campaign access granted: {campaign.name}")
            return campaign
            
        except Exception as e:
            logger.error(f"Error getting campaign with access check: {e}")
            return None
    
    async def get_user_campaigns(
        self,
        user_id: Union[str, UUID],
        status: Optional[Union[str, CampaignStatusEnum]] = None,
        campaign_type: Optional[Union[str, CampaignTypeEnum]] = None,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[Union[str, UUID]] = None
    ) -> List[Campaign]:
        """Get campaigns for a user"""
        try:
            logger.info(f"Getting campaigns for user {user_id}")
            
            user_uuid = UUID(str(user_id))
            query = select(Campaign).where(Campaign.user_id == user_uuid)
            
            # Add company filter if provided
            if company_id:
                company_uuid = UUID(str(company_id))
                query = query.where(Campaign.company_id == company_uuid)
            
            # Add status filter
            if status:
                if isinstance(status, str):
                    try:
                        status_enum = CampaignStatusEnum(status.upper())
                        query = query.where(Campaign.status == status_enum)
                    except ValueError:
                        logger.warning(f"Invalid status filter: {status}")
                else:
                    query = query.where(Campaign.status == status)
            
            # Add campaign type filter
            if campaign_type:
                if isinstance(campaign_type, str):
                    try:
                        type_enum = CampaignTypeEnum(campaign_type.upper())
                        query = query.where(Campaign.campaign_type == type_enum)
                    except ValueError:
                        logger.warning(f"Invalid campaign type filter: {campaign_type}")
                else:
                    query = query.where(Campaign.campaign_type == campaign_type)
            
            query = query.offset(skip).limit(limit).order_by(desc(Campaign.created_at))
            
            result = await self.db.execute(query)
            campaigns = list(result.scalars().all())
            
            logger.info(f"Found {len(campaigns)} campaigns for user")
            return campaigns
            
        except Exception as e:
            logger.error(f"Error getting user campaigns: {e}")
            return []
    
    async def get_campaigns_by_status(
        self,
        status: Union[str, CampaignStatusEnum],
        company_id: Optional[Union[str, UUID]] = None,
        user_id: Optional[Union[str, UUID]] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Campaign]:
        """Get campaigns by status"""
        try:
            # Convert status to enum if string
            if isinstance(status, str):
                try:
                    status_enum = CampaignStatusEnum(status.upper())
                except ValueError:
                    logger.error(f"Invalid status: {status}")
                    return []
            else:
                status_enum = status
            
            query = select(Campaign).where(Campaign.status == status_enum)
            
            if company_id:
                company_uuid = UUID(str(company_id))
                query = query.where(Campaign.company_id == company_uuid)
            
            if user_id:
                user_uuid = UUID(str(user_id))
                query = query.where(Campaign.user_id == user_uuid)
            
            query = query.offset(skip).limit(limit).order_by(desc(Campaign.updated_at))
            
            result = await self.db.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error getting campaigns by status: {e}")
            return []
    
    async def get_recent_campaigns(
        self,
        user_id: Union[str, UUID],
        company_id: Union[str, UUID],
        limit: int = 5
    ) -> List[Campaign]:
        """Get most recently updated campaigns"""
        try:
            logger.info(f"Getting recent campaigns for user {user_id}")
            
            campaigns = await self.get_user_campaigns(
                user_id=user_id,
                company_id=company_id,
                skip=0,
                limit=limit
            )
            
            logger.info(f"Found {len(campaigns)} recent campaigns")
            return campaigns
            
        except Exception as e:
            logger.error(f"Error getting recent campaigns: {e}")
            return []
    
    async def search_campaigns(
        self,
        user_id: Union[str, UUID],
        company_id: Union[str, UUID],
        search_term: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Campaign]:
        """Search campaigns by title or description"""
        try:
            logger.info(f"Searching campaigns for term: {search_term}")
            
            user_uuid = UUID(str(user_id))
            company_uuid = UUID(str(company_id))
            
            # Use PostgreSQL ILIKE for case-insensitive search
            search_pattern = f"%{search_term}%"
            
            query = select(Campaign).where(
                and_(
                    Campaign.user_id == user_uuid,
                    Campaign.company_id == company_uuid,
                    or_(
                        Campaign.name.ilike(search_pattern),
                        Campaign.description.ilike(search_pattern)
                    )
                )
            ).offset(skip).limit(limit).order_by(desc(Campaign.updated_at))
            
            result = await self.db.execute(query)
            campaigns = list(result.scalars().all())
            
            logger.info(f"Found {len(campaigns)} campaigns matching '{search_term}'")
            return campaigns
            
        except Exception as e:
            logger.error(f"Error searching campaigns: {e}")
            return []
    
    # ============================================================================
    # UPDATE OPERATIONS
    # ============================================================================
    
    async def update_campaign(
        self,
        campaign_id: Union[str, UUID],
        user_id: Union[str, UUID],
        **updates
    ) -> Optional[Campaign]:
        """Update campaign information"""
        try:
            campaign = await self.get_campaign_by_id(campaign_id, user_id)
            if not campaign:
                raise NotFoundError(f"Campaign {campaign_id} not found")
            
            # Update allowed fields
            allowed_fields = [
                'title', 'name', 'description', 'target_audience', 'goals', 'settings'
            ]
            
            for field, value in updates.items():
                if field in allowed_fields and hasattr(campaign, field):
                    setattr(campaign, field, value)
            
            campaign.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(campaign)
            
            return campaign
            
        except Exception as e:
            logger.error(f"Error updating campaign: {e}")
            await self.db.rollback()
            raise
    
    async def update_campaign_status(
        self,
        campaign_id: Union[str, UUID],
        new_status: Union[str, CampaignStatusEnum],
        company_id: Union[str, UUID]
    ) -> Optional[Campaign]:
        """Update campaign status with access check"""
        try:
            logger.info(f"Updating campaign {campaign_id} status to {new_status}")
            
            # Convert string to enum if needed
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
                campaign_id=campaign_id,
                company_id=company_id
            )
            
            if not campaign:
                return None
            
            # Update status
            campaign.status = status_enum
            campaign.updated_at = datetime.now(timezone.utc)
            
            # Update timestamps based on status
            if status_enum == CampaignStatusEnum.ACTIVE:
                campaign.launched_at = datetime.now(timezone.utc)
            elif status_enum == CampaignStatusEnum.COMPLETED:
                campaign.completed_at = datetime.now(timezone.utc)
            
            await self.db.commit()
            await self.db.refresh(campaign)
            
            logger.info(f"Updated campaign {campaign_id} status to {status_enum.value if hasattr(status_enum, 'value') else status_enum}")
            return campaign
            
        except Exception as e:
            logger.error(f"Error updating campaign status: {e}")
            await self.db.rollback()
            return None
    
    async def update_workflow_state(
        self,
        campaign_id: Union[str, UUID],
        new_state: str,
        completion_percentage: Optional[int] = None
    ) -> Optional[Campaign]:
        """Update campaign workflow state"""
        try:
            campaign_uuid = UUID(str(campaign_id))
            
            campaign = await self.get_campaign_by_id(campaign_uuid)
            if not campaign:
                return None
            
            # Update workflow state (stored as string in workflow_data)
            workflow_data = campaign.workflow_data or {}
            workflow_data["current_state"] = new_state
            workflow_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            if completion_percentage is not None:
                campaign.completion_percentage = min(100, max(0, completion_percentage))
                workflow_data["completion_percentage"] = campaign.completion_percentage
            
            campaign.workflow_data = workflow_data
            campaign.updated_at = datetime.now(timezone.utc)
            
            await self.db.commit()
            await self.db.refresh(campaign)
            
            logger.info(f"Updated workflow state for campaign {campaign_id} to {new_state}")
            return campaign
            
        except Exception as e:
            logger.error(f"Error updating workflow state: {e}")
            await self.db.rollback()
            return None
    
    async def increment_counters(
        self,
        campaign_id: Union[str, UUID],
        counter_type: str,
        increment: int = 1
    ) -> bool:
        """Increment campaign counters"""
        try:
            campaign_uuid = UUID(str(campaign_id))
            campaign = await self.get_campaign_by_id(campaign_uuid)
            if not campaign:
                return False
            
            # Update appropriate counter
            if counter_type == "sources":
                current_count = getattr(campaign, 'sources_count', 0) or 0
                campaign.sources_count = current_count + increment
            elif counter_type == "intelligence":
                current_count = getattr(campaign, 'intelligence_count', 0) or 0
                campaign.intelligence_count = current_count + increment
            elif counter_type == "content":
                current_count = getattr(campaign, 'generated_content_count', 0) or 0
                campaign.generated_content_count = current_count + increment
            else:
                logger.warning(f"Unknown counter type: {counter_type}")
                return False
            
            campaign.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            
            logger.info(f"Incremented {counter_type} counter for campaign {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing counter: {e}")
            await self.db.rollback()
            return False
    
    async def delete_campaign(
        self,
        campaign_id: Union[str, UUID],
        user_id: Union[str, UUID]
    ) -> bool:
        """Delete (archive) a campaign"""
        try:
            campaign = await self.get_campaign_by_id(campaign_id, user_id)
            if not campaign:
                return False
            
            campaign.status = CampaignStatusEnum.ARCHIVED
            campaign.updated_at = datetime.now(timezone.utc)
            
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting campaign: {e}")
            await self.db.rollback()
            return False
    
    # ============================================================================
    # STATISTICS AND ANALYTICS
    # ============================================================================
    
    async def get_campaign_stats(
        self,
        user_id: Union[str, UUID],
        company_id: Optional[Union[str, UUID]] = None
    ) -> Dict[str, Any]:
        """Get campaign statistics"""
        try:
            logger.info(f"Getting campaign stats for user {user_id}")
            
            user_uuid = UUID(str(user_id))
            base_query = select(func.count(Campaign.id)).where(Campaign.user_id == user_uuid)
            
            if company_id:
                company_uuid = UUID(str(company_id))
                base_query = base_query.where(Campaign.company_id == company_uuid)
            
            # Total campaigns
            total_result = await self.db.execute(base_query)
            total_campaigns = total_result.scalar() or 0
            
            # Status counts
            status_counts = {}
            for status in CampaignStatusEnum:
                status_result = await self.db.execute(
                    base_query.where(Campaign.status == status)
                )
                status_counts[status.value.lower()] = status_result.scalar() or 0
            
            # Recent campaigns (last 30 days)
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent_query = base_query.where(Campaign.created_at >= thirty_days_ago)
            recent_result = await self.db.execute(recent_query)
            recent_campaigns = recent_result.scalar() or 0
            
            # Campaign types breakdown
            campaign_types = {}
            for campaign_type in CampaignTypeEnum:
                type_result = await self.db.execute(
                    base_query.where(Campaign.campaign_type == campaign_type)
                )
                campaign_types[campaign_type.value.lower()] = type_result.scalar() or 0
            
            # Calculate completion rate
            active_campaigns = status_counts.get("active", 0)
            completed_campaigns = status_counts.get("completed", 0)
            draft_campaigns = status_counts.get("draft", 0)
            
            completion_rate = 0.0
            if total_campaigns > 0:
                completion_rate = (completed_campaigns / total_campaigns) * 100
            
            return {
                "total_campaigns": total_campaigns,
                "active_campaigns": active_campaigns,
                "completed_campaigns": completed_campaigns,
                "draft_campaigns": draft_campaigns,
                "recent_campaigns": recent_campaigns,
                "status_breakdown": status_counts,
                "campaign_types": campaign_types,
                "completion_rate": round(completion_rate, 1),
                "user_id": str(user_id),
                "company_id": str(company_id) if company_id else None,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign stats: {e}")
            return {
                "total_campaigns": 0,
                "active_campaigns": 0,
                "completed_campaigns": 0,
                "draft_campaigns": 0,
                "recent_campaigns": 0,
                "status_breakdown": {},
                "campaign_types": {},
                "completion_rate": 0.0,
                "error": str(e),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def get_campaign_insights(
        self,
        company_id: Union[str, UUID],
        user_id: Union[str, UUID]
    ) -> Dict[str, Any]:
        """Get campaign insights for dashboard"""
        try:
            logger.info(f"Getting campaign insights for user {user_id}")
            
            # Get basic stats
            stats = await self.get_campaign_stats(
                user_id=user_id,
                company_id=company_id
            )
            
            # Generate recommendations
            recommendations = []
            total_campaigns = stats.get("total_campaigns", 0)
            draft_campaigns = stats.get("draft_campaigns", 0)
            completed_campaigns = stats.get("completed_campaigns", 0)
            
            if total_campaigns == 0:
                recommendations.append("Create your first campaign to get started")
            elif draft_campaigns > completed_campaigns:
                recommendations.append("Complete your draft campaigns for better results")
            else:
                recommendations.append("Great progress! Consider creating new campaigns")
            
            # Calculate user engagement
            recent_campaigns = stats.get("recent_campaigns", 0)
            user_engagement = "active" if recent_campaigns > 0 else "low"
            
            insights = {
                "basic_stats": stats,
                "user_activity": {
                    "total_campaigns_created": total_campaigns,
                    "completion_rate": self._calculate_completion_rate(stats),
                    "most_active_period": "recent",
                    "user_engagement": user_engagement
                },
                "recommendations": recommendations,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting campaign insights: {e}")
            return {"error": str(e)}
    
    async def get_campaign_performance_metrics(
        self,
        company_id: Union[str, UUID],
        user_id: Union[str, UUID]
    ) -> Dict[str, Any]:
        """Get campaign performance metrics for dashboard"""
        try:
            logger.info(f"Getting performance metrics for user {user_id}")
            
            # Get performance data from campaigns
            user_uuid = UUID(str(user_id))
            company_uuid = UUID(str(company_id))
            
            query = select(Campaign).where(
                and_(
                    Campaign.user_id == user_uuid,
                    Campaign.company_id == company_uuid
                )
            )
            
            result = await self.db.execute(query)
            campaigns = list(result.scalars().all())
            
            # Calculate aggregated metrics
            total_impressions = sum(c.impressions or 0 for c in campaigns)
            total_clicks = sum(c.clicks or 0 for c in campaigns)
            total_conversions = sum(c.conversions or 0 for c in campaigns)
            total_revenue = sum(c.revenue or 0 for c in campaigns) / 100  # Convert to dollars
            
            # Calculate rates
            avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            avg_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            
            metrics = {
                "campaign_metrics": {
                    "total_campaigns": len(campaigns),
                    "total_impressions": total_impressions,
                    "total_clicks": total_clicks,
                    "total_conversions": total_conversions,
                    "total_revenue": round(total_revenue, 2),
                    "average_ctr": round(avg_ctr, 2),
                    "average_conversion_rate": round(avg_conversion_rate, 2),
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
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
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