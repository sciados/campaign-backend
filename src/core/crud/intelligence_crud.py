# src/core/crud/intelligence_crud.py
"""
Intelligence-specific CRUD operations
🧠 Handles all CampaignIntelligence database operations
✅ Uses proven async patterns from base CRUD
🔧 Designed to fix the ChunkedIteratorResult issue
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
import logging

from src.models.intelligence import CampaignIntelligence
from .base_crud import BaseCRUD

logger = logging.getLogger(__name__)

class IntelligenceCRUD(BaseCRUD[CampaignIntelligence]):
    """
    Intelligence CRUD with specialized methods
    🔧 This replaces the problematic database queries in IntelligenceService
    """
    
    def __init__(self):
        super().__init__(CampaignIntelligence)
    
    async def get_campaign_intelligence(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        skip: int = 0,
        limit: int = 50,
        intelligence_type: Optional[str] = None
    ) -> List[CampaignIntelligence]:
        """
        Get all intelligence for a campaign
        🔧 This replaces the failing query in IntelligenceService
        """
        try:
            logger.info(f"🧠 Getting intelligence for campaign {campaign_id}")
            
            filters = {"campaign_id": campaign_id}
            
            # Add intelligence type filter if specified
            if intelligence_type:
                # This would filter by analysis type if we have that field
                pass
            
            # Use base CRUD with confidence score ordering
            intelligence_list = await self.get_multi(
                db=db,
                skip=skip,
                limit=limit,
                filters=filters,
                order_by="confidence_score",
                order_desc=True  # Highest confidence first
            )
            
            logger.info(f"✅ Found {len(intelligence_list)} intelligence entries for campaign {campaign_id}")
            
            # Log details about sources found
            if intelligence_list:
                primary_source = intelligence_list[0]
                logger.info(f"🎯 Primary source: '{primary_source.source_title}' (confidence: {primary_source.confidence_score})")
            
            return intelligence_list
            
        except Exception as e:
            logger.error(f"❌ Error getting campaign intelligence: {e}")
            raise
    
    async def get_primary_intelligence(
        self,
        db: AsyncSession,
        campaign_id: UUID
    ) -> Optional[CampaignIntelligence]:
        """
        Get highest confidence intelligence for a campaign
        🎯 Returns the best intelligence source for content generation
        """
        try:
            logger.info(f"🎯 Getting primary intelligence for campaign {campaign_id}")
            
            intelligence_list = await self.get_campaign_intelligence(
                db=db,
                campaign_id=campaign_id,
                limit=1  # Just get the top one
            )
            
            if not intelligence_list:
                logger.warning(f"⚠️ No intelligence found for campaign {campaign_id}")
                return None
            
            primary = intelligence_list[0]
            logger.info(f"✅ Primary intelligence: '{primary.source_title}' (confidence: {primary.confidence_score})")
            
            return primary
            
        except Exception as e:
            logger.error(f"❌ Error getting primary intelligence: {e}")
            raise
    
    async def get_intelligence_by_source_type(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        source_type: str
    ) -> List[CampaignIntelligence]:
        """Get intelligence by source type (url, document, etc.)"""
        try:
            # Note: We need to handle the enum properly
            intelligence_list = await self.get_multi(
                db=db,
                filters={
                    "campaign_id": campaign_id,
                    # "source_type": source_type  # Commented out due to enum handling
                },
                order_by="confidence_score",
                order_desc=True
            )
            
            # Filter by source type manually if needed
            if source_type:
                filtered_list = []
                for intel in intelligence_list:
                    try:
                        if hasattr(intel.source_type, 'value'):
                            type_value = intel.source_type.value
                        else:
                            type_value = str(intel.source_type)
                        
                        if type_value.lower() == source_type.lower():
                            filtered_list.append(intel)
                    except:
                        # Skip if we can't determine source type
                        continue
                
                intelligence_list = filtered_list
            
            logger.info(f"✅ Found {len(intelligence_list)} intelligence entries of type '{source_type}'")
            return intelligence_list
            
        except Exception as e:
            logger.error(f"❌ Error getting intelligence by source type: {e}")
            raise
    
    async def get_intelligence_summary(
        self,
        db: AsyncSession,
        campaign_id: UUID
    ) -> Dict[str, Any]:
        """
        Get intelligence summary for a campaign
        📊 Provides overview stats about intelligence sources
        """
        try:
            logger.info(f"📊 Getting intelligence summary for campaign {campaign_id}")
            
            # Get all intelligence for campaign
            all_intelligence = await self.get_campaign_intelligence(
                db=db,
                campaign_id=campaign_id,
                limit=1000  # Get all
            )
            
            if not all_intelligence:
                return {
                    "campaign_id": str(campaign_id),
                    "total_intelligence_entries": 0,
                    "available_types": [],
                    "average_confidence": 0.0,
                    "highest_confidence": 0.0,
                    "analysis_status": "no_analysis"
                }
            
            # Calculate summary statistics
            total_entries = len(all_intelligence)
            confidence_scores = [intel.confidence_score or 0.0 for intel in all_intelligence]
            average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            highest_confidence = max(confidence_scores) if confidence_scores else 0.0
            
            # Get available source types
            available_types = []
            for intel in all_intelligence:
                try:
                    if hasattr(intel.source_type, 'value'):
                        type_value = intel.source_type.value
                    else:
                        type_value = str(intel.source_type)
                    
                    if type_value not in available_types:
                        available_types.append(type_value)
                except:
                    continue
            
            # Determine analysis status
            if highest_confidence >= 0.8:
                analysis_status = "excellent"
            elif highest_confidence >= 0.6:
                analysis_status = "good"
            elif highest_confidence >= 0.4:
                analysis_status = "fair"
            else:
                analysis_status = "poor"
            
            summary = {
                "campaign_id": str(campaign_id),
                "total_intelligence_entries": total_entries,
                "available_types": available_types,
                "average_confidence": round(average_confidence, 3),
                "highest_confidence": round(highest_confidence, 3),
                "analysis_status": analysis_status,
                "primary_source_title": all_intelligence[0].source_title if all_intelligence else None
            }
            
            logger.info(f"✅ Intelligence summary: {total_entries} entries, avg confidence: {average_confidence:.3f}")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting intelligence summary: {e}")
            raise
    
    async def create_intelligence(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        user_id: UUID,
        company_id: UUID,
        source_data: Dict[str, Any]
    ) -> CampaignIntelligence:
        """Create new intelligence entry"""
        try:
            logger.info(f"🔨 Creating intelligence for campaign {campaign_id}")
            
            # Prepare intelligence data
            intelligence_data = {
                "campaign_id": campaign_id,
                "user_id": user_id,
                "company_id": company_id,
                **source_data
            }
            
            # Use base CRUD create method
            intelligence = await self.create(db=db, obj_in=intelligence_data)
            
            logger.info(f"✅ Created intelligence: {intelligence.id}")
            return intelligence
            
        except Exception as e:
            logger.error(f"❌ Error creating intelligence: {e}")
            raise