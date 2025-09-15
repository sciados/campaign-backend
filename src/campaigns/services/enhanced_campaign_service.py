# ============================================================================
# ENHANCED CAMPAIGN SERVICE INTEGRATION (Session 5)
# ============================================================================

# src/campaigns/services/enhanced_campaign_service.py

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.campaigns.services.campaign_service import CampaignService
from src.core.factories.service_factory import ServiceFactory

logger = logging.getLogger(__name__)

class EnhancedCampaignService(CampaignService):
    """Enhanced Campaign Service with Content Generation integration"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.content_service = None  # Will be created when needed
    
    async def create_campaign_with_content_generation(
        self,
        user_id: Union[str, UUID],
        name: str,
        campaign_type: str,
        description: Optional[str] = None,
        target_audience: Optional[str] = None,
        goals: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        auto_generate_content: bool = False,
        content_types: Optional[List[str]] = None,
        company_id: Optional[Union[str, UUID]] = None
    ) -> Dict[str, Any]:
        """Create campaign with optional automatic content generation"""
        try:
            # Create the campaign
            campaign = await self.create_campaign(
                user_id=user_id,
                name=name,
                campaign_type=campaign_type,
                description=description,
                target_audience=target_audience,
                goals=goals,
                keywords=keywords,
                company_id=company_id
            )
            
            result = {
                "campaign": {
                    "id": str(campaign.id),
                    "name": campaign.name,
                    "title": campaign.name,
                    "status": campaign.status,
                    "created_at": campaign.created_at.isoformat()
                },
                "content_generated": False,
                "content_items": []
            }
            
            # Generate content if requested
            if auto_generate_content and content_types:
                logger.info(f"Auto-generating content for campaign {campaign.id}")
                
                # Use ServiceFactory to create ContentService
                try:
                    from src.content.services.content_service import ContentService
                    
                    async with ServiceFactory.create_service(ContentService) as content_service:
                        for content_type in content_types:
                            content_result = await content_service.generate_content(
                                campaign_id=campaign.id,
                                content_type=content_type,
                                preferences={
                                    "product_name": name,
                                    "tone": "conversational",
                                    "auto_generated": True
                                }
                            )
                            
                            if content_result.get("success"):
                                result["content_items"].append({
                                    "content_type": content_type,
                                    "content_id": content_result.get("content_id"),
                                    "status": "generated"
                                })
                    
                    result["content_generated"] = True
                    logger.info(f"Generated {len(result['content_items'])} content items")
                    
                except ImportError:
                    logger.warning("Content service not available for auto-generation")
                except Exception as e:
                    logger.error(f"Content auto-generation failed: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced campaign creation failed: {e}")
            raise
    
    async def get_campaign_with_content(
        self,
        campaign_id: Union[str, UUID],
        company_id: Union[str, UUID],
        include_content: bool = True
    ) -> Dict[str, Any]:
        """Get campaign with associated content"""
        try:
            # Get the campaign
            campaign = await self.get_campaign_with_access_check(
                campaign_id=campaign_id,
                company_id=company_id
            )
            
            if not campaign:
                return {"error": "Campaign not found"}
            
            result = {
                "campaign": {
                    "id": str(campaign.id),
                    "name": campaign.name,
                    "title": campaign.name,
                    "description": campaign.description,
                    "status": campaign.status,
                    "campaign_type": campaign.campaign_type,
                    "created_at": campaign.created_at.isoformat(),
                    "updated_at": campaign.updated_at.isoformat()
                },
                "content": []
            }
            
            # Get associated content if requested
            if include_content:
                try:
                    from src.content.services.content_service import ContentService
                    
                    async with ServiceFactory.create_service(ContentService) as content_service:
                        content_items = await content_service.get_campaign_content(
                            campaign_id=campaign_id
                        )
                        result["content"] = content_items
                        
                except ImportError:
                    logger.warning("Content service not available")
                except Exception as e:
                    logger.error(f"Failed to get campaign content: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Get campaign with content failed: {e}")
            raise