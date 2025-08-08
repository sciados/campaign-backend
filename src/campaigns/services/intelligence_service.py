# src/campaigns/services/intelligence_service.py
"""
Intelligence Service - Central CRUD for intelligence operations
🎯 HANDLES: Intelligence data access, content generation coordination
Following the same pattern as CampaignService and WorkflowService
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from src.models import Campaign, User
from src.models.intelligence import CampaignIntelligence

logger = logging.getLogger(__name__)


class IntelligenceService:
    """
    Central Intelligence service for database operations
    🎯 REPLACES: Direct database queries in content_routes.py
    🎯 FOLLOWS: Same pattern as existing services
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ========================================================================
    # CAMPAIGN INTELLIGENCE ACCESS
    # ========================================================================
    
    async def get_campaign_intelligence_for_content(
        self, 
        campaign_id: UUID, 
        company_id: UUID
    ) -> Dict[str, Any]:
        """
        Get real intelligence data from campaign analysis
        🔧 FIXED: Proper async database handling using service pattern
        """
        try:
            logger.info(f"Getting intelligence for content generation: campaign {campaign_id}")
            
            # 1. Verify campaign exists and user has access
            campaign_query = select(Campaign).where(
                Campaign.id == campaign_id,
                Campaign.company_id == company_id
            )
            
            campaign_result = await self.db.execute(campaign_query)
            campaign = campaign_result.scalar_one_or_none()
            
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found or access denied")
            
            # 2. Get all intelligence sources for this campaign
            intelligence_query = select(CampaignIntelligence).where(
                CampaignIntelligence.campaign_id == campaign_id
            ).order_by(CampaignIntelligence.confidence_score.desc())
            
            intelligence_result = await self.db.execute(intelligence_query)
            intelligence_sources = intelligence_result.scalars().all()
            
            if not intelligence_sources:
                logger.warning(f"⚠️ No intelligence sources found for campaign {campaign_id}")
                raise ValueError("No analysis data found for this campaign. Please run analysis first.")
            
            logger.info(f"✅ Found {len(intelligence_sources)} intelligence sources for campaign {campaign_id}")
            
            # 3. Use the highest confidence source as primary
            primary_source = intelligence_sources[0]
            
            # 4. Build comprehensive intelligence data
            intelligence_data = {
                "campaign_id": str(campaign_id),
                "campaign_name": campaign.title,
                "target_audience": campaign.target_audience or "health-conscious adults",
                
                # 🔥 CRITICAL: Include source_title for product name extraction
                "source_title": primary_source.source_title,
                "source_url": primary_source.source_url,
                
                # Real intelligence data from analysis
                "offer_intelligence": self._parse_json_field(primary_source.offer_intelligence),
                "psychology_intelligence": self._parse_json_field(primary_source.psychology_intelligence),
                "content_intelligence": self._parse_json_field(getattr(primary_source, 'content_intelligence', None)),
                "competitive_intelligence": self._parse_json_field(getattr(primary_source, 'competitive_intelligence', None)),
                "brand_intelligence": self._parse_json_field(getattr(primary_source, 'brand_intelligence', None)),
                
                # Additional intelligence if available
                "scientific_intelligence": self._parse_json_field(getattr(primary_source, 'scientific_intelligence', None)),
                "credibility_intelligence": self._parse_json_field(getattr(primary_source, 'credibility_intelligence', None)),
                "market_intelligence": self._parse_json_field(getattr(primary_source, 'market_intelligence', None)),
                "emotional_transformation_intelligence": self._parse_json_field(getattr(primary_source, 'emotional_transformation_intelligence', None)),
                "scientific_authority_intelligence": self._parse_json_field(getattr(primary_source, 'scientific_authority_intelligence', None)),
                
                # All sources for comprehensive content
                "intelligence_sources": [
                    {
                        "id": str(source.id),
                        "source_title": source.source_title,
                        "source_url": source.source_url,
                        "source_type": source.source_type.value if hasattr(source, 'source_type') and source.source_type else "url",
                        "confidence_score": source.confidence_score or 0.0,
                        "offer_intelligence": self._parse_json_field(source.offer_intelligence),
                        "psychology_intelligence": self._parse_json_field(source.psychology_intelligence),
                        "content_intelligence": self._parse_json_field(getattr(source, 'content_intelligence', None)),
                        "competitive_intelligence": self._parse_json_field(getattr(source, 'competitive_intelligence', None)),
                        "brand_intelligence": self._parse_json_field(getattr(source, 'brand_intelligence', None))
                    }
                    for source in intelligence_sources
                ]
            }
            
            # Extract product name from source_title for logging
            product_name = primary_source.source_title or "Unknown Product"
            logger.info(f"🎯 Using intelligence for product: '{product_name}' from {len(intelligence_sources)} sources")
            
            return intelligence_data
            
        except ValueError:
            # Re-raise ValueError as-is (these are expected errors)
            raise
        except Exception as e:
            logger.error(f"❌ Failed to get campaign intelligence: {e}")
            logger.error(f"❌ Error type: {type(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise ValueError(f"Failed to load campaign analysis data: {str(e)}")
    
    async def get_intelligence_source_by_id(
        self, 
        intelligence_id: str, 
        company_id: UUID
    ) -> Optional[CampaignIntelligence]:
        """Get specific intelligence source by ID"""
        try:
            query = select(CampaignIntelligence).where(
                and_(
                    CampaignIntelligence.id == intelligence_id,
                    CampaignIntelligence.company_id == company_id
                )
            )
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting intelligence source {intelligence_id}: {e}")
            return None
    
    async def get_intelligence_summary(
        self, 
        campaign_id: UUID, 
        company_id: UUID
    ) -> Dict[str, Any]:
        """Get intelligence summary for a campaign"""
        try:
            # Get intelligence count
            count_query = select(func.count(CampaignIntelligence.id)).where(
                and_(
                    CampaignIntelligence.campaign_id == campaign_id,
                    CampaignIntelligence.company_id == company_id
                )
            )
            count_result = await self.db.execute(count_query)
            intelligence_count = count_result.scalar() or 0
            
            # Get highest confidence score
            confidence_query = select(func.max(CampaignIntelligence.confidence_score)).where(
                and_(
                    CampaignIntelligence.campaign_id == campaign_id,
                    CampaignIntelligence.company_id == company_id
                )
            )
            confidence_result = await self.db.execute(confidence_query)
            max_confidence = confidence_result.scalar() or 0.0
            
            return {
                "intelligence_count": intelligence_count,
                "max_confidence_score": max_confidence,
                "has_intelligence": intelligence_count > 0
            }
            
        except Exception as e:
            logger.error(f"Error getting intelligence summary: {e}")
            return {"intelligence_count": 0, "max_confidence_score": 0.0, "has_intelligence": False}
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _parse_json_field(self, field_value):
        """Helper to parse JSON fields safely - same as WorkflowService"""
        if field_value is None:
            return {}
        
        if isinstance(field_value, str):
            try:
                return json.loads(field_value)
            except (json.JSONDecodeError, ValueError):
                return {"raw_value": field_value}
        
        if isinstance(field_value, dict):
            return field_value
        
        return {"value": str(field_value)}