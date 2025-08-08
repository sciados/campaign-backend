# src/campaigns/services/intelligence_service.py
"""
Intelligence Service - WORKING VERSION based on WorkflowService pattern
🔧 FIXED: Uses exact same database query pattern as WorkflowService
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.models import Campaign, User
from src.models.intelligence import CampaignIntelligence

logger = logging.getLogger(__name__)


class IntelligenceService:
    """
    Intelligence service using exact same pattern as WorkflowService
    🔧 FIXED: Database queries match working WorkflowService
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_campaign_intelligence_for_content(
        self, 
        campaign_id: UUID, 
        company_id: UUID
    ) -> Dict[str, Any]:
        """
        Get real intelligence data - EXACT PATTERN FROM WorkflowService
        """
        try:
            logger.info(f"Getting intelligence for content generation: campaign {campaign_id}")
            
            # 🔧 EXACT PATTERN FROM WorkflowService.get_workflow_state()
            query = select(Campaign).where(
                Campaign.id == campaign_id,
                Campaign.company_id == company_id
            )
            
            result = await self.db.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found or access denied")
            
            # 🔧 EXACT PATTERN FROM WorkflowService.get_campaign_intelligence()
            intelligence_query = select(CampaignIntelligence).where(
                CampaignIntelligence.campaign_id == campaign_id
            ).order_by(CampaignIntelligence.confidence_score.desc())
            
            intelligence_result = await self.db.execute(intelligence_query)
            intelligence_sources = intelligence_result.scalars().all()
            
            if not intelligence_sources:
                logger.warning(f"⚠️ No intelligence sources found for campaign {campaign_id}")
                raise ValueError("No analysis data found for this campaign. Please run analysis first.")
            
            logger.info(f"✅ Found {len(intelligence_sources)} intelligence sources for campaign {campaign_id}")
            
            # Use the highest confidence source as primary
            primary_source = intelligence_sources[0]
            
            # Build intelligence data using WorkflowService._parse_json_field pattern
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
    
    def _parse_json_field(self, field_value):
        """Helper to parse JSON fields safely - EXACT COPY from WorkflowService"""
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