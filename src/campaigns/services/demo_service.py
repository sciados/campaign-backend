# src/campaigns/services/demo_service.py
"""
Demo Service - Complete demo functionality management
🎯 SMART: Auto-adapts based on user experience level  
🎯 COMPLETE: User preference management with protective logic
Following intelligence/handlers/ pattern for demo functionality
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm.attributes import flag_modified

from src.models import Campaign, User
from src.campaigns.schemas.demo_schemas import DemoPreferenceUpdate, DemoPreferenceResponse
from src.utils.demo_campaign_seeder import DemoCampaignSeeder, is_demo_campaign

logger = logging.getLogger(__name__)


class DemoService:
    """
    Demo service handling all demo campaign functionality
    🎯 INCLUDES: User preference management, demo creation, and smart defaults
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ========================================================================
    # USER PREFERENCE MANAGEMENT
    # ========================================================================
    
    async def get_user_demo_preference(self, user_id: UUID) -> Dict[str, Any]:
        """Get user's demo campaign preference with smart defaults"""
        try:
            # Get user with their stored preferences
            user_query = select(User).where(User.id == user_id)
            result = await self.db.execute(user_query)
            user = result.scalar_one_or_none()
            
            if not user:
                return {"show_demo_campaigns": True}  # Default for new users
            
            # Check if user has demo preference in their settings
            user_settings = self._parse_user_settings(user)
            
            if 'demo_campaign_preferences' in user_settings:
                stored_pref = user_settings['demo_campaign_preferences'].get('show_demo_campaigns')
                if stored_pref is not None:
                    return {"show_demo_campaigns": stored_pref}
            
            # 🎯 SMART DEFAULT based on user experience
            try:
                real_campaigns_query = select(func.count(Campaign.id)).where(
                    Campaign.company_id == user.company_id,
                    Campaign.settings.op('->>')('demo_campaign') != 'true'
                )
                real_count_result = await self.db.execute(real_campaigns_query)
                real_campaigns_count = real_count_result.scalar() or 0
                
                # Smart default: Show demo for new users, hide for experienced users
                smart_default = real_campaigns_count < 3
                
                logger.info(f"Smart default for user {user_id}: show_demo={smart_default} (real campaigns: {real_campaigns_count})")
                return {"show_demo_campaigns": smart_default}
                
            except Exception as query_error:
                logger.warning(f"Error querying campaigns for smart default: {query_error}")
                return {"show_demo_campaigns": True}  # Safe default
        
        except Exception as e:
            logger.error(f"Error getting user demo preference: {e}")
            return {"show_demo_campaigns": True}  # Safe default
    
    async def set_user_demo_preference(
        self, 
        user_id: UUID, 
        show_demo: bool, 
        store_as_smart_default: bool = False
    ) -> bool:
        """Set user's demo campaign preference"""
        try:
            # Get user
            user_query = select(User).where(User.id == user_id)
            result = await self.db.execute(user_query)
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error(f"User {user_id} not found for demo preference update")
                return False
            
            # Handle settings attribute safely
            current_settings = self._parse_user_settings(user)
            
            # Update demo preference
            if 'demo_campaign_preferences' not in current_settings:
                current_settings['demo_campaign_preferences'] = {}
            
            current_settings['demo_campaign_preferences']['show_demo_campaigns'] = show_demo
            current_settings['demo_campaign_preferences']['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            if store_as_smart_default:
                current_settings['demo_campaign_preferences']['set_by'] = 'smart_default'
            else:
                current_settings['demo_campaign_preferences']['set_by'] = 'user_choice'
            
            # Update user settings
            try:
                if hasattr(user, 'settings'):
                    user.settings = current_settings
                    # Mark the field as modified for SQLAlchemy
                    flag_modified(user, 'settings')
                else:
                    logger.warning(f"User model doesn't have settings attribute")
                    return True  # Return success for now
            
                await self.db.commit()
                logger.info(f"✅ Updated demo preference for user {user_id}: show_demo={show_demo}")
                return True
                
            except Exception as commit_error:
                logger.error(f"Error committing user settings: {commit_error}")
                await self.db.rollback()
                return False
        
        except Exception as e:
            logger.error(f"Error setting user demo preference: {e}")
            try:
                await self.db.rollback()
            except:
                pass
            return False
    
    # ========================================================================
    # DEMO CAMPAIGN MANAGEMENT
    # ========================================================================
    
    async def get_demo_status(self, company_id: UUID) -> Dict[str, Any]:
        """Get demo campaign status for the company"""
        try:
            # Check if demo campaign exists
            demo_query = select(Campaign).where(
                Campaign.company_id == company_id,
                Campaign.settings.op('->>')('demo_campaign') == 'true'
            )
            
            result = await self.db.execute(demo_query)
            demo_campaign = result.scalar_one_or_none()
            
            if demo_campaign:
                return {
                    "has_demo": True,
                    "demo_campaign_id": str(demo_campaign.id),
                    "demo_title": demo_campaign.title,
                    "demo_status": demo_campaign.status.value if demo_campaign.status else "unknown",
                    "demo_completion": demo_campaign.calculate_completion_percentage() if hasattr(demo_campaign, 'calculate_completion_percentage') else 0,
                    "content_count": demo_campaign.content_generated or 0
                }
            else:
                return {
                    "has_demo": False,
                    "demo_campaign_id": None
                }
                
        except Exception as e:
            logger.error(f"Error getting demo status: {e}")
            raise e
    
    async def create_demo_campaign(self, company_id: UUID, user_id: UUID) -> Optional[Campaign]:
        """Create a demo campaign using the demo seeder"""
        try:
            logger.info(f"🎭 Creating demo campaign for company {company_id}")
            
            seeder = DemoCampaignSeeder(self.db)
            demo_campaign = await seeder.create_demo_campaign(company_id, user_id)
            
            if demo_campaign:
                logger.info(f"✅ Demo campaign created: {demo_campaign.id}")
                return demo_campaign
            else:
                logger.error("❌ Demo creation returned None")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating demo campaign: {e}")
            raise e
    
    async def ensure_demo_exists(self, company_id: UUID, user_id: UUID) -> Optional[Campaign]:
        """Ensure demo campaign exists, create if missing"""
        try:
            # Check if demo already exists
            demo_status = await self.get_demo_status(company_id)
            
            if demo_status["has_demo"]:
                # Get existing demo
                demo_query = select(Campaign).where(
                    Campaign.company_id == company_id,
                    Campaign.settings.op('->>')('demo_campaign') == 'true'
                )
                result = await self.db.execute(demo_query)
                return result.scalar_one_or_none()
            else:
                # Create new demo
                return await self.create_demo_campaign(company_id, user_id)
                
        except Exception as e:
            logger.error(f"Error ensuring demo exists: {e}")
            return None
    
    async def get_demo_preferences(self, user_id: UUID, company_id: UUID) -> DemoPreferenceResponse:
        """Get complete demo preference response"""
        try:
            # Get user's current preference
            user_demo_preference = await self.get_user_demo_preference(user_id)
            
            # Get campaign counts
            demo_query = select(func.count(Campaign.id)).where(
                Campaign.company_id == company_id,
                Campaign.settings.op('->>')('demo_campaign') == 'true'
            )
            real_query = select(func.count(Campaign.id)).where(
                Campaign.company_id == company_id,
                Campaign.settings.op('->>')('demo_campaign') != 'true'
            )
            
            demo_result = await self.db.execute(demo_query)
            real_result = await self.db.execute(real_query)
            
            demo_count = demo_result.scalar() or 0
            real_count = real_result.scalar() or 0
            
            return DemoPreferenceResponse(
                show_demo_campaigns=user_demo_preference["show_demo_campaigns"],
                demo_available=demo_count > 0,
                real_campaigns_count=real_count,
                demo_campaigns_count=demo_count
            )
            
        except Exception as e:
            logger.error(f"Error getting demo preferences: {e}")
            raise e
    
    async def can_delete_demo(self, company_id: UUID) -> Dict[str, Any]:
        """Check if demo campaign can be safely deleted"""
        try:
            # Get count of real campaigns
            real_campaigns_query = select(func.count(Campaign.id)).where(
                Campaign.company_id == company_id,
                Campaign.settings.op('->>')('demo_campaign') != 'true'
            )
            real_count_result = await self.db.execute(real_campaigns_query)
            real_campaigns_count = real_count_result.scalar() or 0
            
            can_delete = real_campaigns_count > 0
            
            return {
                "can_delete": can_delete,
                "real_campaigns_count": real_campaigns_count,
                "reason": "User has real campaigns" if can_delete else "No real campaigns - demo needed for onboarding"
            }
            
        except Exception as e:
            logger.error(f"Error checking if demo can be deleted: {e}")
            return {"can_delete": False, "error": str(e)}
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _parse_user_settings(self, user: User) -> Dict[str, Any]:
        """Parse user settings safely"""
        user_settings = {}
        if hasattr(user, 'settings') and user.settings is not None:
            if isinstance(user.settings, dict):
                user_settings = user.settings.copy()
            elif isinstance(user.settings, str):
                try:
                    user_settings = json.loads(user.settings) if user.settings else {}
                except (json.JSONDecodeError, TypeError):
                    user_settings = {}
        return user_settings
    
    def is_demo_campaign(self, campaign: Campaign) -> bool:
        """Check if campaign is a demo campaign"""
        return is_demo_campaign(campaign)