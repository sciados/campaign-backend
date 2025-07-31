"""
Campaign Service - Business Logic Layer
🔧 CRITICAL FIX: Proper async session management for background tasks
🎯 Following intelligence/handlers/analysis_handler.py pattern
"""
import uuid
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from src.core.database import AsyncSessionLocal  # 🔧 CRITICAL FIX: Import at module level
from src.models import Campaign, User, CampaignStatus
# from src.models.campaign import AutoAnalysisStatus, CampaignWorkflowState
from src.utils.demo_campaign_seeder import is_demo_campaign

logger = logging.getLogger(__name__)

class CampaignService:
    """
    Campaign business logic service
    🔧 FIXED: Proper async session management for background tasks
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_campaign(
        self, 
        campaign_data: Dict[str, Any], 
        user: User,
        background_tasks
    ) -> Campaign:
        """Create new campaign with optional auto-analysis trigger"""
        try:
            logger.info(f"🎯 Creating streamlined campaign for user {user.id}")
            
            new_campaign = Campaign(
                title=campaign_data.get("title"),
                description=campaign_data.get("description"),
                keywords=campaign_data.get("keywords", []),
                target_audience=campaign_data.get("target_audience"),
                tone=campaign_data.get("tone", "conversational"),
                style=campaign_data.get("style", "modern"),
                user_id=user.id,
                company_id=user.company_id,
                status=CampaignStatus.DRAFT,
                settings=campaign_data.get("settings", {}),
                
                # Auto-analysis fields
                salespage_url=campaign_data.get("salespage_url"),
                auto_analysis_enabled=campaign_data.get("auto_analysis_enabled", True),
                content_types=campaign_data.get("content_types", ["email", "social_post", "ad_copy"]),
                content_tone=campaign_data.get("content_tone", "conversational"),
                content_style=campaign_data.get("content_style", "modern"),
                generate_content_after_analysis=campaign_data.get("generate_content_after_analysis", False)
            )
            
            self.db.add(new_campaign)
            await self.db.commit()
            await self.db.refresh(new_campaign)
            
            logger.info(f"✅ Created campaign {new_campaign.id}")
            
            # 🔧 CRITICAL FIX: Trigger auto-analysis if enabled and URL provided
            if (campaign_data.get("auto_analysis_enabled") and 
                campaign_data.get("salespage_url") and 
                campaign_data.get("salespage_url").strip()):
                
                logger.info(f"🚀 Triggering auto-analysis for {campaign_data.get('salespage_url')}")
                
                # 🔧 FIXED: Add background task with proper parameters
                background_tasks.add_task(
                    self.trigger_auto_analysis_task_fixed,  # 🔧 NEW: Fixed version
                    str(new_campaign.id),
                    campaign_data.get("salespage_url").strip(),
                    str(user.id),
                    str(user.company_id)
                )
            
            return new_campaign
            
        except Exception as e:
            logger.error(f"❌ Error creating campaign: {e}")
            await self.db.rollback()
            raise e
    
    # 🔧 CRITICAL FIX: NEW WORKING BACKGROUND TASK
    @staticmethod
    async def trigger_auto_analysis_task_fixed(
        campaign_id: str, 
        salespage_url: str, 
        user_id: str, 
        company_id: str
    ):
        """
        🔧 CRITICAL FIX: Background task with proper async session management
        This replaces the broken version in routes.py
        """
        try:
            logger.info(f"🚀 Starting FIXED auto-analysis background task for campaign {campaign_id}")
            
            # 🔧 CRITICAL FIX: Create new async session within background task
            async with AsyncSessionLocal() as db:
                # Get user for analysis handler
                user_result = await db.execute(select(User).where(User.id == user_id))
                user = user_result.scalar_one_or_none()
                
                if not user:
                    logger.error(f"❌ User {user_id} not found for auto-analysis")
                    return
                
                # Get campaign
                campaign_result = await db.execute(
                    select(Campaign).where(
                        and_(Campaign.id == campaign_id, Campaign.company_id == company_id)
                    )
                )
                campaign = campaign_result.scalar_one_or_none()
                
                if not campaign:
                    logger.error(f"❌ Campaign {campaign_id} not found for auto-analysis")
                    return
                
                # Start analysis using campaign's method
                campaign.start_auto_analysis()
                await db.commit()
                
                # Create analysis handler and run analysis
                from src.intelligence.handlers.analysis_handler import AnalysisHandler
                handler = AnalysisHandler(db, user)
                
                analysis_request = {
                    "url": salespage_url,
                    "campaign_id": str(campaign_id),
                    "analysis_type": "sales_page"
                }
                
                try:
                    analysis_result = await handler.analyze_url(analysis_request)
                    
                    # Update campaign with results
                    if analysis_result.get("intelligence_id"):
                        intelligence_id = analysis_result["intelligence_id"]
                        confidence_score = analysis_result.get("confidence_score", 0.0)
                        
                        # Create analysis summary using campaign method
                        analysis_summary = {
                            "offer_intelligence": analysis_result.get("offer_intelligence", {}),
                            "psychology_intelligence": analysis_result.get("psychology_intelligence", {}),
                            "competitive_opportunities": analysis_result.get("competitive_opportunities", []),
                            "campaign_suggestions": analysis_result.get("campaign_suggestions", []),
                            "amplification_applied": analysis_result.get("amplification_metadata", {}).get("amplification_applied", False)
                        }
                        
                        campaign.complete_auto_analysis(intelligence_id, confidence_score, analysis_summary)
                        logger.info(f"✅ FIXED auto-analysis completed for campaign {campaign_id}")
                        
                    else:
                        raise Exception("Analysis failed - no intelligence ID returned")
                        
                except Exception as analysis_error:
                    logger.error(f"❌ Auto-analysis failed: {str(analysis_error)}")
                    campaign.fail_auto_analysis(str(analysis_error))
                
                await db.commit()
                
        except Exception as task_error:
            logger.error(f"❌ FIXED auto-analysis background task failed: {str(task_error)}")
    
    async def get_campaigns_by_company(
        self, 
        company_id: str, 
        skip: int = 0, 
        limit: int = 100, 
        status: Optional[str] = None
    ) -> List[Campaign]:
        """Get campaigns by company ID"""
        try:
            from sqlalchemy import select
            # from ...models import Campaign
        
            # Build query
            query = select(Campaign).where(Campaign.company_id == company_id)
        
            if status:
                query = query.where(Campaign.status == status)
        
            # Apply pagination
            query = query.offset(skip).limit(limit)
        
            # Execute query
            result = await self.db.execute(query)
            campaigns = result.scalars().all()
        
            return campaigns
        
        except Exception as e:
            logger.error(f"Error getting campaigns by company: {e}")
            return []
    
    async def get_campaigns_paginated(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        company_id: str = None
    ) -> List[Campaign]:
        """Get campaigns with pagination and filtering"""
        try:
            query = select(Campaign).where(Campaign.company_id == company_id)
            
            if status:
                try:
                    status_enum = CampaignStatus(status.upper())
                    query = query.where(Campaign.status == status_enum)
                except ValueError:
                    logger.warning(f"Invalid status filter '{status}'")
            
            query = query.offset(skip).limit(limit).order_by(Campaign.updated_at.desc())
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting campaigns: {e}")
            raise e
    
    async def get_campaign_by_id(self, campaign_id: str, company_id: str) -> Optional[Campaign]:
        """Get campaign by ID with company verification"""
        try:
            query = select(Campaign).where(
                Campaign.id == campaign_id,
                Campaign.company_id == company_id
            )
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting campaign {campaign_id}: {e}")
            return None
    
    async def get_campaign_by_id_and_company(self, campaign_id: str, company_id: str) -> Optional[Campaign]:
        """
        Get campaign by ID with company verification (alias for get_campaign_by_id)
        🔧 CRITICAL FIX: Missing method being called from workflow_operations.py
        """
        return await self.get_campaign_by_id(campaign_id, company_id)
    
    async def update_campaign(
        self, 
        campaign_id: str, 
        update_data: Dict[str, Any], 
        company_id: str
    ) -> Optional[Campaign]:
        """Update campaign with validation"""
        try:
            campaign = await self.get_campaign_by_id(campaign_id, company_id)
            if not campaign:
                return None
            
            # Update fields that were provided
            for field, value in update_data.items():
                if field == "status" and value:
                    try:
                        campaign.status = CampaignStatus(value.upper())
                    except ValueError:
                        logger.warning(f"Invalid status value: {value}")
                else:
                    setattr(campaign, field, value)
            
            # Update timestamp
            campaign.updated_at = datetime.now(timezone.utc)
            
            await self.db.commit()
            await self.db.refresh(campaign)
            
            return campaign
            
        except Exception as e:
            logger.error(f"Error updating campaign {campaign_id}: {e}")
            await self.db.rollback()
            raise e
    
    async def delete_campaign(self, campaign_id: str, company_id: str) -> bool:
        """Delete campaign with demo protection"""
        try:
            campaign = await self.get_campaign_by_id(campaign_id, company_id)
            if not campaign:
                return False
            
            # Check if this is a demo campaign - protect if it's the last one
            if is_demo_campaign(campaign):
                # Get count of real campaigns
                real_campaigns_query = select(func.count(Campaign.id)).where(
                    Campaign.company_id == company_id,
                    Campaign.settings.op('->>')('demo_campaign') != 'true'
                )
                real_count_result = await self.db.execute(real_campaigns_query)
                real_campaigns_count = real_count_result.scalar() or 0
                
                if real_campaigns_count == 0:
                    logger.warning(f"Prevented deletion of demo campaign - user has no real campaigns")
                    return False
            
            await self.db.delete(campaign)
            await self.db.commit()
            
            logger.info(f"✅ Campaign {campaign_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting campaign {campaign_id}: {e}")
            await self.db.rollback()
            return False
    
    async def get_dashboard_stats(self, company_id: str) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            total_query = select(func.count(Campaign.id)).where(Campaign.company_id == company_id)
            demo_query = select(func.count(Campaign.id)).where(
                Campaign.company_id == company_id,
                Campaign.settings.op('->>')('demo_campaign') == 'true'
            )
            real_query = select(func.count(Campaign.id)).where(
                Campaign.company_id == company_id,
                Campaign.settings.op('->>')('demo_campaign') != 'true'
            )
            
            total_result = await self.db.execute(total_query)
            demo_result = await self.db.execute(demo_query)
            real_result = await self.db.execute(real_query)
            
            total_campaigns = total_result.scalar() or 0
            demo_campaigns = demo_result.scalar() or 0
            real_campaigns = real_result.scalar() or 0
            
            return {
                "total_campaigns_created": total_campaigns,
                "real_campaigns": real_campaigns,
                "demo_campaigns": demo_campaigns,
                "workflow_type": "streamlined_2_step",
                "user_experience": {
                    "is_new_user": real_campaigns == 0,
                    "demo_recommended": real_campaigns < 3,
                    "onboarding_complete": real_campaigns >= 1
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {"error": str(e)}
        
    # Add this method to campaign_service.py - CampaignService class

    def to_response(self, campaign: Campaign) -> Dict[str, Any]:
        """
        Convert Campaign model to API response format
        🔧 CRITICAL FIX: Missing method causing 'CampaignService' object has no attribute 'to_response'
        """
        try:
            return {
                "id": str(campaign.id),
                "title": campaign.title,
                "description": campaign.description,
                "keywords": campaign.keywords or [],
                "target_audience": campaign.target_audience,
                "campaign_type": getattr(campaign, 'campaign_type', 'universal'),
                "status": campaign.status.value if campaign.status else 'DRAFT',
                "tone": campaign.tone,
                "style": campaign.style,
                "settings": campaign.settings or {},
                "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
                "updated_at": campaign.updated_at.isoformat() if campaign.updated_at else None,
                "user_id": str(campaign.user_id),
                "company_id": str(campaign.company_id),
                
                # Auto-Analysis Fields
                "salespage_url": campaign.salespage_url,
                "auto_analysis_enabled": campaign.auto_analysis_enabled,
                "auto_analysis_status": campaign.auto_analysis_status.value if campaign.auto_analysis_status else None,
                "analysis_confidence_score": campaign.analysis_confidence_score,
                
                # Workflow Fields
                "workflow_state": campaign.workflow_state.value if campaign.workflow_state else None,
                "completion_percentage": self._calculate_completion_percentage(campaign),
                "sources_count": campaign.sources_count or 0,
                "intelligence_count": campaign.intelligence_count or 0,
                "content_count": campaign.generated_content_count or 0,
                "total_steps": 2,  # 2-step workflow
                
                # Content preferences
                "content_types": campaign.content_types or [],
                "content_tone": campaign.content_tone,
                "content_style": campaign.content_style,
                "generate_content_after_analysis": campaign.generate_content_after_analysis,
                
                # Demo campaign fields
                "is_demo": is_demo_campaign(campaign),
                
                # Legacy fields for backward compatibility
                "confidence_score": campaign.analysis_confidence_score,
                "last_activity": campaign.updated_at.isoformat() if campaign.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error converting campaign to response: {str(e)}")
            # Return minimal response on error
            return {
                "id": str(campaign.id) if campaign.id else "unknown",
                "title": campaign.title or "Unknown Campaign",
                "status": "ERROR",
                "error": "Failed to convert campaign data"
            }
    
    def _calculate_completion_percentage(self, campaign: Campaign) -> int:
        """Calculate campaign completion percentage based on workflow state"""
        try:
            if not campaign.workflow_state:
                return 0
            
            # Map workflow states to completion percentages
            completion_map = {
                "SETUP": 25,
                "ANALYSIS_STARTED": 50,
                "ANALYSIS_COMPLETE": 75,
                "CONTENT_GENERATION": 90,
                "COMPLETED": 100
            }
            
            state_value = campaign.workflow_state.value if hasattr(campaign.workflow_state, 'value') else str(campaign.workflow_state)
            return completion_map.get(state_value, 0)
            
        except Exception as e:
            logger.error(f"Error calculating completion percentage: {e}")
            return 0