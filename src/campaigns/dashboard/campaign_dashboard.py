# src/campaigns/dashboard/campaign_dashboard.py

from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from datetime import datetime, timezone, timedelta
from intelligence.generators.landing_page.database.models import GeneratedContent
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
import logging

from src.campaigns.models.campaign import Campaign, CampaignStatusEnum, CampaignTypeEnum
from src.campaigns.services.campaign_service import CampaignService
from src.campaigns.workflows.campaign_workflows import CampaignWorkflowEngine

logger = logging.getLogger(__name__)

class CampaignDashboardService:
    """Campaign dashboard analytics and metrics service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.campaign_service = CampaignService(db)
        self.workflow_engine = CampaignWorkflowEngine(db)
    
    # ============================================================================
    # DASHBOARD OVERVIEW METHODS
    # ============================================================================
    
    async def _count_generated_content(
        self,
        user_id: Union[str, UUID],
        company_id: Union[str, UUID]
    ) -> int:
        """Count generated content for the user and company"""
        try:
            # Convert to UUID if necessary
            user_uuid = UUID(str(user_id))
            company_uuid = UUID(str(company_id))
        
            # Query the GeneratedContent table
            async with self.db() as session:
                query = select(func.count(GeneratedContent.content_id)) \
                    .join(Campaign, GeneratedContent.campaign_id == Campaign.id) \
                    .where(
                        and_(
                            Campaign.user_id == user_uuid,
                            Campaign.company_id == company_uuid
                        )
                    )
            
                result = await session.execute(query)
                return result.scalar_one()
    
        except Exception as e:
            logger.error(f"Error counting generated content: {e}")
            return 0

    async def get_dashboard_overview(
        self,
        user_id: Union[str, UUID],
        company_id: Union[str, UUID],
        time_period: str = "30d"
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard overview"""
        try:
            logger.info(f"Getting dashboard overview for user {user_id}")
        
            # Get basic campaign stats
            stats = await self.campaign_service.get_campaign_stats(user_id, company_id)
        
            # Get workflow status
            workflow_status = await self.workflow_engine.monitor_active_workflows()
        
            # Get recent activity
            recent_activity = await self._get_recent_activity(user_id, company_id, time_period)
        
            # Get performance metrics
            performance_metrics = await self._get_performance_overview(user_id, company_id, time_period)
        
            # Get campaign health score
            health_score = await self._calculate_campaign_health_score(user_id, company_id)
        
            # Get upcoming deadlines
            upcoming_deadlines = await self._get_upcoming_deadlines(user_id, company_id)
        
            # ✅ ADD THIS LINE: Count generated content
            generated_content_count = await self._count_generated_content(user_id, company_id)
        
            return {
                "overview": {
                    "total_campaigns": stats.get("total_campaigns", 0),
                    "active_campaigns": stats.get("active_campaigns", 0),
                    "completed_campaigns": stats.get("completed_campaigns", 0),
                    "completion_rate": stats.get("completion_rate", 0),
                    "health_score": health_score,
                    "generated_content_count": generated_content_count  # 👈 This is the fix
                },
                "workflow_status": {
                    "active_workflows": workflow_status.get("active_workflows", 0),
                    "paused_workflows": workflow_status.get("paused_workflows", 0),
                    "error_workflows": workflow_status.get("error_workflows", 0)
                },
                "performance_metrics": performance_metrics,
                "recent_activity": recent_activity,
                "upcoming_deadlines": upcoming_deadlines,
                "time_period": time_period,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting dashboard overview: {e}")
            return {"error": str(e)}
    
    async def get_campaign_analytics(
        self,
        user_id: Union[str, UUID],
        company_id: Union[str, UUID],
        time_period: str = "30d"
    ) -> Dict[str, Any]:
        """Get detailed campaign analytics"""
        try:
            logger.info(f"Getting campaign analytics for user {user_id}")
            
            # Parse time period
            days = self._parse_time_period(time_period)
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            user_uuid = UUID(str(user_id))
            company_uuid = UUID(str(company_id))
            
            # Get campaigns in time period
            query = select(Campaign).where(
                and_(
                    Campaign.user_id == user_uuid,
                    Campaign.company_id == company_uuid,
                    Campaign.created_at >= start_date
                )
            )
            
            result = await self.db.execute(query)
            campaigns = list(result.scalars().all())
            
            # Calculate analytics
            analytics = {
                "time_period": time_period,
                "total_campaigns": len(campaigns),
                "campaign_creation_trend": await self._calculate_creation_trend(campaigns, days),
                "status_distribution": await self._calculate_status_distribution(campaigns),
                "type_distribution": await self._calculate_type_distribution(campaigns),
                "performance_metrics": await self._calculate_performance_metrics(campaigns),
                "workflow_analytics": await self._calculate_workflow_analytics(campaigns),
                "top_performing_campaigns": await self._get_top_performing_campaigns(campaigns),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting campaign analytics: {e}")
            return {"error": str(e)}
    
    async def get_workflow_dashboard(
        self,
        user_id: Union[str, UUID],
        company_id: Union[str, UUID]
    ) -> Dict[str, Any]:
        """Get workflow-specific dashboard data"""
        try:
            logger.info(f"Getting workflow dashboard for user {user_id}")
            
            # Get active workflows
            workflow_status = await self.workflow_engine.monitor_active_workflows()
            
            # Get workflow performance data
            user_uuid = UUID(str(user_id))
            company_uuid = UUID(str(company_id))
            
            query = select(Campaign).where(
                and_(
                    Campaign.user_id == user_uuid,
                    Campaign.company_id == company_uuid,
                    Campaign.workflow_data.isnot(None)
                )
            )
            
            result = await self.db.execute(query)
            campaigns_with_workflows = list(result.scalars().all())
            
            # Calculate workflow metrics
            workflow_metrics = {
                "active_workflows": workflow_status.get("active_workflows", 0),
                "paused_workflows": workflow_status.get("paused_workflows", 0),
                "error_workflows": workflow_status.get("error_workflows", 0),
                "completed_workflows": workflow_status.get("completed_workflows", 0),
                "workflow_completion_rate": await self._calculate_workflow_completion_rate(campaigns_with_workflows),
                "average_workflow_duration": await self._calculate_average_workflow_duration(campaigns_with_workflows),
                "workflow_bottlenecks": await self._identify_workflow_bottlenecks(campaigns_with_workflows),
                "workflow_success_rate": await self._calculate_workflow_success_rate(campaigns_with_workflows),
                "workflows_by_type": await self._get_workflows_by_type(campaigns_with_workflows),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return workflow_metrics
            
        except Exception as e:
            logger.error(f"Error getting workflow dashboard: {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # PRIVATE ANALYTICS METHODS
    # ============================================================================
    
    async def _get_recent_activity(
        self,
        user_id: Union[str, UUID],
        company_id: Union[str, UUID],
        time_period: str
    ) -> List[Dict[str, Any]]:
        """Get recent campaign activity"""
        try:
            days = self._parse_time_period(time_period)
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            user_uuid = UUID(str(user_id))
            company_uuid = UUID(str(company_id))
            
            query = select(Campaign).where(
                and_(
                    Campaign.user_id == user_uuid,
                    Campaign.company_id == company_uuid,
                    Campaign.updated_at >= start_date
                )
            ).order_by(desc(Campaign.updated_at)).limit(10)
            
            result = await self.db.execute(query)
            recent_campaigns = list(result.scalars().all())
            
            activity = []
            for campaign in recent_campaigns:
                activity.append({
                    "campaign_id": str(campaign.id),
                    "campaign_name": campaign.name,
                    "action": self._determine_recent_action(campaign),
                    "status": campaign.status if campaign.status else "unknown",
                    "timestamp": campaign.updated_at.isoformat() if campaign.updated_at else None
                })
            
            return activity
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
    
    async def _get_performance_overview(
        self,
        user_id: Union[str, UUID],
        company_id: Union[str, UUID],
        time_period: str
    ) -> Dict[str, Any]:
        """Get performance metrics overview"""
        try:
            performance_metrics = await self.campaign_service.get_campaign_performance_metrics(
                company_id, user_id
            )
            
            return {
                "total_impressions": performance_metrics.get("campaign_metrics", {}).get("total_impressions", 0),
                "total_clicks": performance_metrics.get("campaign_metrics", {}).get("total_clicks", 0),
                "total_conversions": performance_metrics.get("campaign_metrics", {}).get("total_conversions", 0),
                "total_revenue": performance_metrics.get("campaign_metrics", {}).get("total_revenue", 0),
                "average_ctr": performance_metrics.get("campaign_metrics", {}).get("average_ctr", 0),
                "average_conversion_rate": performance_metrics.get("campaign_metrics", {}).get("average_conversion_rate", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting performance overview: {e}")
            return {}
    
    async def _calculate_campaign_health_score(
        self,
        user_id: Union[str, UUID],
        company_id: Union[str, UUID]
    ) -> float:
        """Calculate overall campaign health score (0-100)"""
        try:
            stats = await self.campaign_service.get_campaign_stats(user_id, company_id)
            
            total_campaigns = stats.get("total_campaigns", 0)
            if total_campaigns == 0:
                return 0.0
            
            completed_campaigns = stats.get("completed_campaigns", 0)
            active_campaigns = stats.get("active_campaigns", 0)
            draft_campaigns = stats.get("draft_campaigns", 0)
            
            # Calculate health components
            completion_score = (completed_campaigns / total_campaigns) * 40  # 40% weight
            activity_score = (active_campaigns / total_campaigns) * 30  # 30% weight
            efficiency_score = max(0, (total_campaigns - draft_campaigns) / total_campaigns) * 30  # 30% weight
            
            health_score = completion_score + activity_score + efficiency_score
            
            return round(min(100, max(0, health_score)), 1)
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return 0.0
    
    async def _get_upcoming_deadlines(
        self,
        user_id: Union[str, UUID],
        company_id: Union[str, UUID]
    ) -> List[Dict[str, Any]]:
        """Get upcoming campaign deadlines"""
        try:
            # This would integrate with actual deadline tracking
            # For now, return mock data based on workflow states
            
            user_uuid = UUID(str(user_id))
            company_uuid = UUID(str(company_id))
            
            query = select(Campaign).where(
                and_(
                    Campaign.user_id == user_uuid,
                    Campaign.company_id == company_uuid,
                    Campaign.is_workflow_complete == False
                )
            )
            
            result = await self.db.execute(query)
            active_campaigns = list(result.scalars().all())
            
            deadlines = []
            for campaign in active_campaigns:
                # Mock deadline calculation based on workflow progress
                if campaign.workflow_data:
                    estimated_completion = campaign.workflow_data.get("estimated_completion")
                    if estimated_completion:
                        deadlines.append({
                            "campaign_id": str(campaign.id),
                            "campaign_name": campaign.name,
                            "deadline": estimated_completion,
                            "status": "pending",
                            "urgency": "medium"
                        })
            
            # Sort by deadline
            deadlines.sort(key=lambda x: x["deadline"])
            
            return deadlines[:5]  # Return top 5 upcoming deadlines
            
        except Exception as e:
            logger.error(f"Error getting upcoming deadlines: {e}")
            return []
    
    def _parse_time_period(self, time_period: str) -> int:
        """Parse time period string to days"""
        period_map = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "1y": 365
        }
        return period_map.get(time_period, 30)
    
    def _determine_recent_action(self, campaign: Campaign) -> str:
        """Determine the most recent action for a campaign"""
        if campaign.status == "draft":
            return "created"
        elif campaign.status == "active":
            return "launched"
        elif campaign.status == "completed":
            return "completed"
        elif campaign.status == "paused":
            return "paused"
        else:
            return "updated"
    
    async def _calculate_creation_trend(
        self,
        campaigns: List[Campaign],
        days: int
    ) -> List[Dict[str, Any]]:
        """Calculate campaign creation trend over time"""
        try:
            # Group campaigns by day
            daily_counts = {}
            for campaign in campaigns:
                if campaign.created_at:
                    day_key = campaign.created_at.date().isoformat()
                    daily_counts[day_key] = daily_counts.get(day_key, 0) + 1
            
            # Fill in missing days with 0
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            trend_data = []
            
            for i in range(days):
                current_date = start_date + timedelta(days=i)
                day_key = current_date.date().isoformat()
                trend_data.append({
                    "date": day_key,
                    "count": daily_counts.get(day_key, 0)
                })
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error calculating creation trend: {e}")
            return []
    
    async def _calculate_status_distribution(
        self,
        campaigns: List[Campaign]
    ) -> Dict[str, int]:
        """Calculate campaign status distribution"""
        # Initialize with known status values as strings
        distribution = {
            "draft": 0,
            "active": 0,
            "completed": 0,
            "paused": 0,
            "archived": 0
        }
        
        for campaign in campaigns:
            if campaign.status and campaign.status in distribution:
                distribution[campaign.status] += 1
        
        return distribution
    
    async def _calculate_type_distribution(
        self,
        campaigns: List[Campaign]
    ) -> Dict[str, int]:
        """Calculate campaign type distribution"""
        # Initialize with known campaign type values as strings
        distribution = {
            "social_media": 0,
            "email_marketing": 0,
            "content_marketing": 0,
            "affiliate_promotion": 0,
            "product_launch": 0
        }
        
        for campaign in campaigns:
            if campaign.campaign_type and campaign.campaign_type in distribution:
                distribution[campaign.campaign_type] += 1
        
        return distribution
    
    async def _calculate_performance_metrics(
        self,
        campaigns: List[Campaign]
    ) -> Dict[str, Any]:
        """Calculate aggregated performance metrics"""
        total_impressions = sum(c.impressions or 0 for c in campaigns)
        total_clicks = sum(c.clicks or 0 for c in campaigns)
        total_conversions = sum(c.conversions or 0 for c in campaigns)
        total_revenue = sum(c.revenue or 0 for c in campaigns) / 100
        
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        
        return {
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "total_revenue": round(total_revenue, 2),
            "average_ctr": round(avg_ctr, 2),
            "average_conversion_rate": round(avg_conversion_rate, 2)
        }
    
    async def _calculate_workflow_analytics(
        self,
        campaigns: List[Campaign]
    ) -> Dict[str, Any]:
        """Calculate workflow analytics"""
        workflows_with_data = [c for c in campaigns if c.workflow_data]
        
        if not workflows_with_data:
            return {
                "total_workflows": 0,
                "completed_workflows": 0,
                "average_completion_time": 0,
                "success_rate": 0
            }
        
        completed_workflows = [c for c in workflows_with_data if c.is_workflow_complete]
        
        # Calculate average completion time
        completion_times = []
        for campaign in completed_workflows:
            workflow_data = campaign.workflow_data or {}
            started_at = workflow_data.get("started_at")
            completed_at = workflow_data.get("completed_at")
            
            if started_at and completed_at:
                try:
                    start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                    end_time = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                    duration = (end_time - start_time).total_seconds() / 3600  # hours
                    completion_times.append(duration)
                except:
                    continue
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        success_rate = (len(completed_workflows) / len(workflows_with_data) * 100) if workflows_with_data else 0
        
        return {
            "total_workflows": len(workflows_with_data),
            "completed_workflows": len(completed_workflows),
            "average_completion_time": round(avg_completion_time, 2),
            "success_rate": round(success_rate, 1)
        }
    
    async def _get_top_performing_campaigns(
        self,
        campaigns: List[Campaign],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top performing campaigns"""
        # Sort by a performance score (revenue + conversions)
        scored_campaigns = []
        for campaign in campaigns:
            revenue = (campaign.revenue or 0) / 100
            conversions = campaign.conversions or 0
            score = revenue + (conversions * 10)  # Weight conversions
            
            scored_campaigns.append({
                "campaign_id": str(campaign.id),
                "campaign_name": campaign.name,
                "performance_score": score,
                "revenue": revenue,
                "conversions": conversions,
                "impressions": campaign.impressions or 0,
                "clicks": campaign.clicks or 0
            })
        
        # Sort by performance score
        scored_campaigns.sort(key=lambda x: x["performance_score"], reverse=True)
        
        return scored_campaigns[:limit]
    
    async def _calculate_workflow_completion_rate(
        self,
        campaigns: List[Campaign]
    ) -> float:
        """Calculate workflow completion rate"""
        workflows_with_data = [c for c in campaigns if c.workflow_data]
        if not workflows_with_data:
            return 0.0
        
        completed = len([c for c in workflows_with_data if c.is_workflow_complete])
        return round((completed / len(workflows_with_data)) * 100, 1)
    
    async def _calculate_average_workflow_duration(
        self,
        campaigns: List[Campaign]
    ) -> float:
        """Calculate average workflow duration in hours"""
        durations = []
        
        for campaign in campaigns:
            if not campaign.workflow_data or not campaign.is_workflow_complete:
                continue
            
            workflow_data = campaign.workflow_data
            started_at = workflow_data.get("started_at")
            completed_at = workflow_data.get("completed_at")
            
            if started_at and completed_at:
                try:
                    start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                    end_time = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                    duration = (end_time - start_time).total_seconds() / 3600
                    durations.append(duration)
                except:
                    continue
        
        return round(sum(durations) / len(durations), 2) if durations else 0.0
    
    async def _identify_workflow_bottlenecks(
        self,
        campaigns: List[Campaign]
    ) -> List[Dict[str, Any]]:
        """Identify workflow bottlenecks"""
        step_durations = {}
        
        for campaign in campaigns:
            if not campaign.workflow_data:
                continue
            
            step_history = campaign.workflow_data.get("step_history", [])
            
            for step_record in step_history:
                step_number = step_record.get("step_number")
                started_at = step_record.get("started_at")
                completed_at = step_record.get("completed_at")
                
                if step_number and started_at and completed_at:
                    try:
                        start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                        end_time = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                        duration = (end_time - start_time).total_seconds() / 60  # minutes
                        
                        if step_number not in step_durations:
                            step_durations[step_number] = []
                        step_durations[step_number].append(duration)
                    except:
                        continue
        
        # Calculate average durations and identify bottlenecks
        bottlenecks = []
        for step_number, durations in step_durations.items():
            avg_duration = sum(durations) / len(durations)
            if avg_duration > 300:  # More than 5 minutes average
                bottlenecks.append({
                    "step_number": step_number,
                    "average_duration_minutes": round(avg_duration, 2),
                    "occurrences": len(durations)
                })
        
        return sorted(bottlenecks, key=lambda x: x["average_duration_minutes"], reverse=True)
    
    async def _calculate_workflow_success_rate(
        self,
        campaigns: List[Campaign]
    ) -> float:
        """Calculate workflow success rate"""
        workflows_started = len([c for c in campaigns if c.workflow_data])
        if workflows_started == 0:
            return 0.0
        
        workflows_completed_successfully = len([
            c for c in campaigns 
            if c.workflow_data and c.is_workflow_complete and 
            c.workflow_state != "ERROR"
        ])
        
        return round((workflows_completed_successfully / workflows_started) * 100, 1)
    
    async def _get_workflows_by_type(
        self,
        campaigns: List[Campaign]
    ) -> Dict[str, int]:
        """Get workflow distribution by campaign type"""
        workflow_types = {}
        
        for campaign in campaigns:
            if campaign.workflow_data and campaign.campaign_type:
                campaign_type = campaign.campaign_type
                workflow_types[campaign_type] = workflow_types.get(campaign_type, 0) + 1
        
        return workflow_types