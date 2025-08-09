# src/core/crud/intelligence_crud.py
"""
Intelligence-specific CRUD operations
🧠 Handles all CampaignIntelligence database operations
✅ Uses proven async patterns from base CRUD
🔧 Designed to fix the ChunkedIteratorResult issue
🔒 Enhanced with company_id security for multi-tenant isolation
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
import logging

from src.models.intelligence import CampaignIntelligence, GeneratedContent
from .base_crud import BaseCRUD

logger = logging.getLogger(__name__)

class IntelligenceCRUD(BaseCRUD[CampaignIntelligence]):
    """
    Intelligence CRUD with specialized methods
    🔧 This replaces the problematic database queries in IntelligenceService
    🔒 Enhanced with company_id security for proper multi-tenant isolation
    """
    
    def __init__(self):
        super().__init__(CampaignIntelligence)
    
    async def get_campaign_intelligence(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        company_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50,
        intelligence_type: Optional[str] = None
    ) -> List[CampaignIntelligence]:
        """
        Get all intelligence for a campaign with company_id security
        🔧 This replaces the failing query in IntelligenceService
        🔒 Enhanced with company_id filtering for multi-tenant security
        """
        try:
            logger.info(f"🧠 Getting intelligence for campaign {campaign_id} (company: {company_id})")
            
            # Build filters with campaign_id
            filters = {"campaign_id": campaign_id}
            
            # Add company_id for security isolation if provided
            if company_id:
                filters["company_id"] = company_id
                logger.info(f"🔒 Company security filter applied: {company_id}")
            
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
    
    # 🆕 Missing methods that dashboard_stats.py expects
    
    async def get_intelligence_statistics(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get intelligence statistics for dashboard
        🆕 NEW: Method that dashboard_stats.py expects
        """
        try:
            logger.info(f"📊 Getting intelligence statistics for user {user_id}")
            
            # Get intelligence entries for the company
            intelligence_entries = await self.get_multi(
                db=db,
                filters={"company_id": company_id},
                limit=1000  # Get all for analysis
            )
            
            # Calculate statistics
            total_entries = len(intelligence_entries)
            
            if total_entries == 0:
                return {
                    "total_intelligence_entries": 0,
                    "average_confidence": 0.0,
                    "analysis_quality": "no_data",
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
            
            # Calculate confidence metrics
            confidence_scores = [
                entry.confidence_score or 0.0 
                for entry in intelligence_entries 
                if entry.confidence_score is not None
            ]
            
            average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            max_confidence = max(confidence_scores) if confidence_scores else 0.0
            
            # Determine analysis quality
            if average_confidence >= 0.8:
                quality = "excellent"
            elif average_confidence >= 0.6:
                quality = "good"
            elif average_confidence >= 0.4:
                quality = "fair"
            else:
                quality = "needs_improvement"
            
            statistics = {
                "total_intelligence_entries": total_entries,
                "average_confidence": round(average_confidence, 3),
                "max_confidence": round(max_confidence, 3),
                "analysis_quality": quality,
                "entries_with_high_confidence": len([s for s in confidence_scores if s >= 0.8]),
                "company_analysis_coverage": {
                    "campaigns_analyzed": len(set(entry.campaign_id for entry in intelligence_entries)),
                    "unique_sources": len(set(entry.source_url for entry in intelligence_entries if entry.source_url)),
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"❌ Error getting intelligence statistics: {e}")
            return {"error": str(e)}
    
    async def get_intelligence_performance_metrics(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get intelligence performance metrics for dashboard
        🆕 NEW: Method that dashboard_stats.py expects
        """
        try:
            logger.info(f"📈 Getting intelligence performance metrics for user {user_id}")
            
            # Mock performance metrics - replace with real metrics as needed
            metrics = {
                "processing_performance": {
                    "average_analysis_time": 12.5,  # seconds
                    "successful_analyses": 95,  # percentage
                    "failed_analyses": 5,  # percentage
                    "cache_hit_rate": 85  # percentage
                },
                "quality_metrics": {
                    "average_confidence_score": 0.82,
                    "high_quality_analyses": 78,  # percentage
                    "amplification_success_rate": 92  # percentage
                },
                "resource_usage": {
                    "memory_usage": 40,  # percentage
                    "api_calls_per_hour": 150,
                    "cost_efficiency": 88  # percentage
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error getting intelligence performance metrics: {e}")
            return {"error": str(e)}
    
    async def get_primary_intelligence(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        company_id: Optional[UUID] = None
    ) -> Optional[CampaignIntelligence]:
        """
        Get highest confidence intelligence for a campaign with company security
        🎯 Returns the best intelligence source for content generation
        🔒 Enhanced with company_id filtering for security
        """
        try:
            logger.info(f"🎯 Getting primary intelligence for campaign {campaign_id} (company: {company_id})")
            
            intelligence_list = await self.get_campaign_intelligence(
                db=db,
                campaign_id=campaign_id,
                company_id=company_id,
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
        source_type: str,
        company_id: Optional[UUID] = None
    ) -> List[CampaignIntelligence]:
        """
        Get intelligence by source type (url, document, etc.) with company security
        🔒 Enhanced with company_id filtering for security
        """
        try:
            # Build base filters
            filters = {
                "campaign_id": campaign_id
            }
            
            # Add company_id for security if provided
            if company_id:
                filters["company_id"] = company_id
            
            intelligence_list = await self.get_multi(
                db=db,
                filters=filters,
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
        campaign_id: UUID,
        company_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get intelligence summary for a campaign with company security
        📊 Provides overview stats about intelligence sources
        🔒 Enhanced with company_id filtering for security
        """
        try:
            logger.info(f"📊 Getting intelligence summary for campaign {campaign_id} (company: {company_id})")
            
            # Get all intelligence for campaign with company security
            all_intelligence = await self.get_campaign_intelligence(
                db=db,
                campaign_id=campaign_id,
                company_id=company_id,
                limit=1000  # Get all
            )
            
            if not all_intelligence:
                return {
                    "campaign_id": str(campaign_id),
                    "company_id": str(company_id) if company_id else None,
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
                "company_id": str(company_id) if company_id else None,
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
        """Create new intelligence entry with proper company association"""
        try:
            logger.info(f"🔨 Creating intelligence for campaign {campaign_id} (company: {company_id})")
            
            # Prepare intelligence data with company_id
            intelligence_data = {
                "campaign_id": campaign_id,
                "user_id": user_id,
                "company_id": company_id,
                **source_data
            }
            
            # Use base CRUD create method
            intelligence = await self.create(db=db, obj_in=intelligence_data)
            
            logger.info(f"✅ Created intelligence: {intelligence.id} for company {company_id}")
            return intelligence
            
        except Exception as e:
            logger.error(f"❌ Error creating intelligence: {e}")
            raise
    
    # 🆕 Generated Content Methods with company_id support
    
    async def get_generated_content(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        company_id: UUID,
        content_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[GeneratedContent]:
        """
        Get generated content for a campaign with company security
        🔒 Company-aware content retrieval
        """
        try:
            logger.info(f"📄 Getting generated content for campaign {campaign_id} (company: {company_id})")
            
            # Build filters with security
            filters = {
                "campaign_id": campaign_id,
                "company_id": company_id
            }
            
            if content_type:
                filters["content_type"] = content_type
            
            # Use direct query for GeneratedContent model
            stmt = select(GeneratedContent).where(
                and_(
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == company_id
                )
            )
            
            if content_type:
                stmt = stmt.where(GeneratedContent.content_type == content_type)
            
            stmt = stmt.order_by(desc(GeneratedContent.created_at)).offset(skip).limit(limit)
            
            result = await db.execute(stmt)
            content_items = result.scalars().all()
            
            logger.info(f"✅ Found {len(content_items)} content items")
            return list(content_items)
            
        except Exception as e:
            logger.error(f"❌ Error getting generated content: {e}")
            raise
    
    async def get_generated_content_by_id(
        self,
        db: AsyncSession,
        content_id: UUID,
        campaign_id: UUID,
        company_id: UUID
    ) -> Optional[GeneratedContent]:
        """
        Get specific generated content with security verification
        🔒 Triple security check: content_id, campaign_id, company_id
        """
        try:
            stmt = select(GeneratedContent).where(
                and_(
                    GeneratedContent.id == content_id,
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == company_id
                )
            )
            
            result = await db.execute(stmt)
            content_item = result.scalar_one_or_none()
            
            if content_item:
                logger.info(f"✅ Found content {content_id} with security verification")
            else:
                logger.warning(f"⚠️ Content {content_id} not found or access denied")
            
            return content_item
            
        except Exception as e:
            logger.error(f"❌ Error getting content by ID: {e}")
            raise
    
    async def create_generated_content(
        self,
        db: AsyncSession,
        content_data: Dict[str, Any]
    ) -> GeneratedContent:
        """Create new generated content with proper company association"""
        try:
            logger.info(f"🔨 Creating generated content for campaign {content_data.get('campaign_id')}")
            
            # 🔧 FIXED: Handle JSON serialization for datetime objects
            processed_data = {}
            for key, value in content_data.items():
                if isinstance(value, datetime):
                    processed_data[key] = value  # SQLAlchemy handles datetime directly
                elif isinstance(value, dict):
                    # Serialize dict fields that might contain datetime objects
                    processed_data[key] = self._serialize_json_field(value)
                else:
                    processed_data[key] = value
            
            # Create GeneratedContent instance
            content = GeneratedContent(**processed_data)
            db.add(content)
            await db.commit()
            await db.refresh(content)
            
            logger.info(f"✅ Created generated content: {content.id}")
            return content
            
        except Exception as e:
            logger.error(f"❌ Error creating generated content: {e}")
            await db.rollback()
            raise
    
    def _serialize_json_field(self, data: Any) -> Any:
        """
        Serialize JSON field with proper datetime handling
        🔧 FIXED: Handle datetime objects in JSON fields
        """
        import json
        from datetime import datetime, date
        
        def json_serial(obj):
            """JSON serializer for objects not serializable by default"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        try:
            if isinstance(data, dict):
                # Convert to JSON string and back to ensure serialization
                json_str = json.dumps(data, default=json_serial)
                return json.loads(json_str)
            else:
                return data
        except Exception as e:
            logger.warning(f"JSON serialization warning: {e}")
            return data
    
    async def update_generated_content(
        self,
        db: AsyncSession,
        content_id: UUID,
        update_data: Dict[str, Any]
    ) -> GeneratedContent:
        """Update generated content"""
        try:
            # Get existing content
            stmt = select(GeneratedContent).where(GeneratedContent.id == content_id)
            result = await db.execute(stmt)
            content = result.scalar_one_or_none()
            
            if not content:
                raise ValueError(f"Content {content_id} not found")
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(content, field):
                    setattr(content, field, value)
            
            await db.commit()
            await db.refresh(content)
            
            logger.info(f"✅ Updated generated content: {content_id}")
            return content
            
        except Exception as e:
            logger.error(f"❌ Error updating generated content: {e}")
            await db.rollback()
            raise
    
    async def delete_generated_content(
        self,
        db: AsyncSession,
        content_id: UUID
    ) -> bool:
        """Delete generated content"""
        try:
            stmt = select(GeneratedContent).where(GeneratedContent.id == content_id)
            result = await db.execute(stmt)
            content = result.scalar_one_or_none()
            
            if not content:
                return False
            
            await db.delete(content)
            await db.commit()
            
            logger.info(f"✅ Deleted generated content: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting generated content: {e}")
            await db.rollback()
            raise
    
    async def get_intelligence_by_id(
        self,
        db: AsyncSession,
        intelligence_id: UUID,
        company_id: UUID
    ) -> Optional[CampaignIntelligence]:
        """
        Get intelligence by ID with company security
        🔒 Company-aware intelligence retrieval
        """
        try:
            stmt = select(CampaignIntelligence).where(
                and_(
                    CampaignIntelligence.id == intelligence_id,
                    CampaignIntelligence.company_id == company_id
                )
            )
            
            result = await db.execute(stmt)
            intelligence = result.scalar_one_or_none()
            
            if intelligence:
                logger.info(f"✅ Found intelligence {intelligence_id} with company verification")
            else:
                logger.warning(f"⚠️ Intelligence {intelligence_id} not found or access denied")
            
            return intelligence
            
        except Exception as e:
            logger.error(f"❌ Error getting intelligence by ID: {e}")
            raise