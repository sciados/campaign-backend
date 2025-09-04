"""
File: src/intelligence/handlers/intelligence_handler.py
Intelligence Handler - UPDATED FOR NEW OPTIMIZED SCHEMA
Handles intelligence data operations using the new 6-table normalized structure
"""
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models.base import EnumSerializerMixin
from src.models.user import User
from src.models.campaign import Campaign

# Import NEW CRUD for optimized schema
from src.core.crud.intelligence_crud import intelligence_crud
from src.core.crud import campaign_crud

from ..utils.campaign_helpers import (
    get_campaign_with_verification,
    calculate_campaign_statistics,
    update_campaign_counters
)

# JSON serialization helper
from src.utils.json_utils import json_serial, safe_json_dumps

logger = logging.getLogger(__name__)


class IntelligenceHandler(EnumSerializerMixin):
    """Handle intelligence data management operations - UPDATED FOR NEW SCHEMA"""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
    
    async def get_campaign_intelligence(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get intelligence for a campaign - FIXED FOR NEW SHARED ARCHITECTURE
        Now uses the campaign's analysis_intelligence_id to get the specific linked intelligence
        """
        logger.info(f"Getting intelligence data for campaign: {campaign_id}")
        
        try:
            # Verify campaign access (still needed for permissions)
            campaign = await campaign_crud.get_campaign_with_access_check(
                db=self.db,
                campaign_id=campaign_id,
                company_id=str(self.user.company_id)
            )
            
            if not campaign:
                raise ValueError("Campaign not found or access denied")
            
            logger.info(f"Campaign access verified: {campaign.title}")
            
            # NEW: Get intelligence via campaign's analysis_intelligence_id
            intelligence_sources = await self._get_intelligence_sources(campaign)
            
            # Get generated content (still works with campaign_id)
            generated_content = await self._get_generated_content(campaign_id)
            
            # Build response adapted for new schema
            return self._build_intelligence_response(
                campaign_id, intelligence_sources, generated_content
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Critical error in get_campaign_intelligence: {str(e)}")
            return self._build_fallback_response(campaign_id)
    
    async def _get_intelligence_sources(self, campaign: Campaign) -> List[Dict[str, Any]]:
        """Get intelligence sources for specific campaign - FIXED FOR NEW ARCHITECTURE"""
        try:
            # Check if campaign has linked intelligence
            if not campaign.analysis_intelligence_id:
                logger.info(f"Campaign {campaign.id} has no linked intelligence")
                return []
            
            # Get the specific intelligence record linked to this campaign
            intelligence_data = await intelligence_crud.get_intelligence_by_id(
                db=self.db,
                intelligence_id=campaign.analysis_intelligence_id,
                include_content_stats=True
            )
            
            if not intelligence_data:
                logger.warning(f"Intelligence {campaign.analysis_intelligence_id} not found for campaign {campaign.id}")
                return []
            
            logger.info(f"Retrieved linked intelligence for campaign: {intelligence_data.get('analysis_id', 'unknown')}")
            return [intelligence_data]  # Single intelligence source per campaign
            
        except Exception as e:
            logger.error(f"Error getting intelligence sources for campaign: {str(e)}")
            return []

    async def _get_generated_content(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get generated content for campaign - UPDATED"""
        try:
            # This still works with campaign_id since content belongs to campaigns
            from src.core.crud.base_crud import BaseCRUD
            from src.core.crud.intelligence_crud import GeneratedContent
            
            content_crud = BaseCRUD(GeneratedContent)
            content_items = await content_crud.get_multi(
                db=self.db,
                filters={"campaign_id": campaign_id},
                limit=100
            )
            
            # Convert to dictionary format
            formatted_content = []
            for item in content_items:
                formatted_content.append({
                    "id": str(item.id),
                    "content_type": item.content_type,
                    "title": item.content_title,
                    "content": item.content_body,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "is_published": item.is_published,
                    "user_rating": item.user_rating
                })
            
            logger.info(f"Retrieved {len(formatted_content)} content items for campaign")
            return formatted_content
            
        except Exception as e:
            logger.error(f"Error getting generated content: {str(e)}")
            return []
    def _build_intelligence_response(
        self, 
        campaign_id: str, 
        intelligence_sources: List[Dict[str, Any]], 
        generated_content: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build intelligence response - ADAPTED FOR NEW SCHEMA"""
        try:
            # NEW: Format intelligence sources from new schema structure
            formatted_sources = []
            for source in intelligence_sources:
                # NEW: Intelligence data is already reconstructed from normalized tables
                formatted_source = {
                    "id": source.get("analysis_id", "unknown"),
                    "source_url": source.get("source_url", ""),
                    "source_title": source.get("product_name", "Unknown Product"),
                    "confidence_score": source.get("confidence_score", 0.0),
                    "created_at": source.get("analysis_timestamp", ""),
                    
                    # NEW: Intelligence categories from reconstructed data
                    "offer_intelligence": source.get("offer_intelligence", {}),
                    "psychology_intelligence": source.get("psychology_intelligence", {}),
                    "content_intelligence": source.get("content_intelligence", {}),
                    "competitive_intelligence": source.get("competitive_intelligence", {}),
                    "brand_intelligence": source.get("brand_intelligence", {}),
                    
                    # NEW: Enhanced categories from reconstructed data  
                    "scientific_intelligence": source.get("scientific_intelligence", {}),
                    "credibility_intelligence": source.get("credibility_intelligence", {}),
                    "market_intelligence": source.get("market_intelligence", {}),
                    "emotional_transformation_intelligence": source.get("emotional_transformation_intelligence", {}),
                    "scientific_authority_intelligence": source.get("scientific_authority_intelligence", {}),
                    
                    # NEW: Schema metadata
                    "schema_version": "optimized_normalized",
                    "rag_enhanced": source.get("rag_enhanced", False),
                    "research_chunks_used": source.get("research_chunks_used", 0)
                }
                formatted_sources.append(formatted_source)
            
            # Format generated content (simplified)
            formatted_content = []
            for content in generated_content:
                formatted_content_item = {
                    "id": content.get("id", "unknown"),
                    "content_type": content.get("content_type", "unknown"),
                    "title": content.get("title", ""),
                    "content": content.get("content", ""),
                    "created_at": content.get("created_at", "")
                }
                formatted_content.append(formatted_content_item)
            
            # Calculate statistics
            total_sources = len(intelligence_sources)
            avg_confidence = (
                sum(source.get("confidence_score", 0.0) for source in intelligence_sources) / total_sources
                if total_sources > 0 else 0.0
            )
            
            # NEW: Count RAG-enhanced sources
            rag_enhanced_count = sum(1 for source in intelligence_sources if source.get("rag_enhanced", False))
            
            logger.info(f"Intelligence Response Stats:")
            logger.info(f"   Total sources: {total_sources}")
            logger.info(f"   RAG enhanced: {rag_enhanced_count}")
            logger.info(f"   Average confidence: {avg_confidence:.2f}")
            
            return {
                "campaign_id": campaign_id,
                "intelligence_sources": formatted_sources,
                "generated_content": formatted_content,
                "statistics": {
                    "total_sources": total_sources,
                    "rag_enhanced_sources": rag_enhanced_count,
                    "total_content": len(generated_content),
                    "average_confidence": round(avg_confidence, 2),
                    "enhancement_rate": round(rag_enhanced_count / total_sources * 100, 1) if total_sources > 0 else 0.0
                },
                "schema_info": {
                    "version": "optimized_normalized",
                    "storage_reduction": "90%",
                    "tables_used": 6,
                    "campaign_relationship": "time_based_context"
                },
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error building intelligence response: {str(e)}")
            return self._build_fallback_response(campaign_id)

    def _build_fallback_response(self, campaign_id: str) -> Dict[str, Any]:
        """Build fallback response for errors"""
        return {
            "campaign_id": campaign_id,
            "intelligence_sources": [],
            "generated_content": [],
            "statistics": {
                "total_sources": 0,
                "rag_enhanced_sources": 0,
                "total_content": 0,
                "average_confidence": 0.0,
                "enhancement_rate": 0.0
            },
            "schema_info": {
                "version": "optimized_normalized",
                "status": "error"
            },
            "success": False,
            "error": "Failed to load intelligence data",
            "message": "There was an error loading intelligence data. Please try again."
        }
    
    async def delete_intelligence_source(self, campaign_id: str, intelligence_id: str) -> Dict[str, Any]:
        """Delete intelligence source - UPDATED FOR NEW SCHEMA"""
        
        # Verify campaign access
        campaign = await campaign_crud.get_campaign_with_access_check(
            db=self.db,
            campaign_id=campaign_id,
            company_id=str(self.user.company_id)
        )
        if not campaign:
            raise ValueError("Campaign not found or access denied")
        
        # NEW: Delete using new CRUD method
        try:
            intelligence_uuid = UUID(intelligence_id)
            success = await intelligence_crud.delete_intelligence(
                db=self.db,
                intelligence_id=intelligence_uuid
            )
            
            if not success:
                raise ValueError("Intelligence source not found")
            
            # Update campaign counters
            await update_campaign_counters(campaign_id, self.db)
            
            return {"message": "Intelligence source deleted successfully"}
            
        except ValueError as e:
            if "not found" in str(e):
                raise ValueError("Intelligence source not found")
            raise
        except Exception as e:
            logger.error(f"Error deleting intelligence source: {e}")
            raise ValueError("Failed to delete intelligence source")

    async def create_intelligence_source(
        self,
        campaign_id: str,
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create new intelligence source - NEW METHOD FOR NEW SCHEMA"""
        
        # Verify campaign access
        campaign = await campaign_crud.get_campaign_with_access_check(
            db=self.db,
            campaign_id=campaign_id,
            company_id=str(self.user.company_id)
        )
        if not campaign:
            raise ValueError("Campaign not found or access denied")
        
        try:
            # Create intelligence using new CRUD
            intelligence_id = await intelligence_crud.create_intelligence(
                db=self.db,
                analysis_data=analysis_data
            )
            
            # Update campaign counters
            await update_campaign_counters(campaign_id, self.db)
            
            logger.info(f"Created intelligence source: {intelligence_id}")
            return {
                "intelligence_id": intelligence_id,
                "message": "Intelligence source created successfully",
                "schema_version": "optimized_normalized"
            }
            
        except Exception as e:
            logger.error(f"Error creating intelligence source: {e}")
            raise ValueError("Failed to create intelligence source")

    async def update_intelligence_source(
        self,
        campaign_id: str,
        intelligence_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update intelligence source - NEW METHOD FOR NEW SCHEMA"""
        
        # Verify campaign access
        campaign = await campaign_crud.get_campaign_with_access_check(
            db=self.db,
            campaign_id=campaign_id,
            company_id=str(self.user.company_id)
        )
        if not campaign:
            raise ValueError("Campaign not found or access denied")
        
        try:
            intelligence_uuid = UUID(intelligence_id)
            
            # Update using new CRUD
            updated_intelligence = await intelligence_crud.update_intelligence(
                db=self.db,
                intelligence_id=intelligence_uuid,
                update_data=update_data
            )
            
            if not updated_intelligence:
                raise ValueError("Intelligence source not found")
            
            logger.info(f"Updated intelligence source: {intelligence_id}")
            return {
                "intelligence_id": intelligence_id,
                "message": "Intelligence source updated successfully",
                "updated_data": updated_intelligence
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating intelligence source: {e}")
            raise ValueError("Failed to update intelligence source")

    async def search_intelligence_by_product(
        self,
        product_name: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search intelligence by product name - NEW METHOD FOR NEW SCHEMA"""
        
        try:
            intelligence_results = await intelligence_crud.search_intelligence_by_product(
                db=self.db,
                product_name=product_name,
                limit=limit
            )
            
            return {
                "search_term": product_name,
                "results_found": len(intelligence_results),
                "intelligence_sources": intelligence_results,
                "search_type": "product_name",
                "schema_version": "optimized_normalized"
            }
            
        except Exception as e:
            logger.error(f"Error searching intelligence by product: {e}")
            return {
                "search_term": product_name,
                "results_found": 0,
                "intelligence_sources": [],
                "error": str(e)
            }

    async def search_intelligence_by_url(
        self,
        source_url: str,
        exact_match: bool = True
    ) -> Dict[str, Any]:
        """Search intelligence by URL - NEW METHOD FOR NEW SCHEMA"""
        
        try:
            intelligence_results = await intelligence_crud.search_intelligence_by_url(
                db=self.db,
                source_url=source_url,
                exact_match=exact_match
            )
            
            return {
                "search_url": source_url,
                "results_found": len(intelligence_results),
                "intelligence_sources": intelligence_results,
                "exact_match": exact_match,
                "schema_version": "optimized_normalized"
            }
            
        except Exception as e:
            logger.error(f"Error searching intelligence by URL: {e}")
            return {
                "search_url": source_url,
                "results_found": 0,
                "intelligence_sources": [],
                "error": str(e)
            }

    async def get_intelligence_statistics(self) -> Dict[str, Any]:
        """Get intelligence statistics - UPDATED FOR NEW SCHEMA"""
        
        try:
            statistics = await intelligence_crud.get_intelligence_statistics(db=self.db)
            
            # Add handler-level context
            statistics.update({
                "handler_context": {
                    "user_id": str(self.user.id),
                    "company_id": str(self.user.company_id),
                    "schema_version": "optimized_normalized"
                },
                "data_source": "normalized_6_table_schema"
            })
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting intelligence statistics: {e}")
            return {
                "error": str(e),
                "schema_version": "optimized_normalized"
            }

    # REMOVED: amplify_intelligence_source method
    # This would need significant rework to work with the new schema
    # The amplification logic assumed the old JSONB column structure
    
    async def get_intelligence_by_id(self, intelligence_id: str) -> Dict[str, Any]:
        """Get specific intelligence by ID - NEW METHOD FOR NEW SCHEMA"""
        
        try:
            intelligence_uuid = UUID(intelligence_id)
            
            intelligence_data = await intelligence_crud.get_intelligence_by_id(
                db=self.db,
                intelligence_id=intelligence_uuid,
                include_content_stats=True
            )
            
            if not intelligence_data:
                return {
                    "intelligence_id": intelligence_id,
                    "found": False,
                    "error": "Intelligence not found"
                }
            
            return {
                "intelligence_id": intelligence_id,
                "found": True,
                "intelligence_data": intelligence_data,
                "schema_version": "optimized_normalized"
            }
            
        except Exception as e:
            logger.error(f"Error getting intelligence by ID: {e}")
            return {
                "intelligence_id": intelligence_id,
                "found": False,
                "error": str(e)
            }