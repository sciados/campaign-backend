# src/campaigns/services/intelligence_service.py
"""
Intelligence Service - FIXED VERSION using Centralized CRUD
🔧 FIXED: Uses centralized CRUD to eliminate ChunkedIteratorResult issues
🔧 FIXED: Proper async session management via CRUD layer
✅ No more direct database queries - all through CRUD
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

# ✅ NEW: Import centralized CRUD
from src.core.crud import campaign_crud, intelligence_crud

from src.models import Campaign, User
from src.models.intelligence import CampaignIntelligence

logger = logging.getLogger(__name__)


class IntelligenceService:
    """
    Intelligence service using centralized CRUD - NO MORE ChunkedIteratorResult!
    🔧 FIXED: All database operations through proven CRUD patterns
    ✅ Eliminates async session issues completely
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_campaign_intelligence_for_content(
        self, 
        campaign_id: UUID, 
        company_id: UUID
    ) -> Dict[str, Any]:
        """
        Get real intelligence data - FIXED VERSION using CRUD
        🔧 FIXED: No more direct database queries
        ✅ Uses proven CRUD patterns that work reliably
        """
        try:
            logger.info(f"Getting intelligence for content generation: campaign {campaign_id}")
            
            # ✅ FIXED: Use CRUD instead of direct database query
            campaign = await campaign_crud.get_campaign_with_access_check(
                db=self.db,
                campaign_id=campaign_id,
                company_id=company_id
            )
            
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found or access denied")
            
            logger.info(f"✅ Found campaign: {campaign.title}")
            
            # ✅ FIXED: Use intelligence CRUD instead of problematic direct query
            intelligence_sources = await intelligence_crud.get_campaign_intelligence(
                db=self.db,
                campaign_id=campaign_id,
                limit=100  # Get all sources for content generation
            )
            
            logger.info(f"📊 Found {len(intelligence_sources)} intelligence sources via CRUD")
            
            if not intelligence_sources:
                logger.warning(f"⚠️ No intelligence sources found for campaign {campaign_id}")
                raise ValueError("No analysis data found for this campaign. Please run analysis first.")
            
            logger.info(f"✅ Found {len(intelligence_sources)} intelligence sources for campaign {campaign_id}")
            
            # Use the highest confidence source as primary (CRUD returns ordered by confidence)
            primary_source = intelligence_sources[0]
            logger.info(f"🎯 Using primary source: {primary_source.source_title} (confidence: {primary_source.confidence_score})")
            
            # Build intelligence data using existing _parse_json_field logic
            intelligence_data = {
                "campaign_id": str(campaign_id),
                "campaign_name": campaign.title,
                "target_audience": campaign.target_audience or "health-conscious adults",
                
                # 🔥 CRITICAL: Include source_title for product name extraction
                "source_title": primary_source.source_title,
                "source_url": primary_source.source_url,
                
                # Real intelligence data from analysis using existing parsing
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
                "intelligence_sources": []
            }
            
            # Process all sources using existing logic
            for source in intelligence_sources:
                try:
                    source_data = {
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
                    intelligence_data["intelligence_sources"].append(source_data)
                except Exception as source_error:
                    logger.warning(f"⚠️ Error processing source {source.id}: {source_error}")
                    continue
            
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