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
from src.models.campaign import AutoAnalysisStatus, CampaignWorkflowState
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