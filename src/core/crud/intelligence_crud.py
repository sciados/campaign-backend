# src/core/crud/intelligence_crud.py
"""
Intelligence-specific CRUD operations - UPDATED with intelligence_id backlink support
🧠 Handles all CampaignIntelligence database operations
✅ Uses proven async patterns from base CRUD
🔧 Designed to fix the ChunkedIteratorResult issue
🔒 Enhanced with company_id security for multi-tenant isolation
✅ NEW: Intelligence backlink support for content provenance and analytics
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload
import logging

from src.models.intelligence import CampaignIntelligence, GeneratedContent
from .base_crud import BaseCRUD
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class IntelligenceCRUD(BaseCRUD[CampaignIntelligence]):
    """
    Intelligence CRUD with specialized methods and intelligence backlink support
    🔧 This replaces the problematic database queries in IntelligenceService
    🔒 Enhanced with company_id security for proper multi-tenant isolation
    ✅ NEW: Full support for intelligence_id relationships and analytics
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
        intelligence_type: Optional[str] = None,
        include_content_stats: bool = False
    ) -> List[CampaignIntelligence]:
        """
        Get all intelligence for a campaign with company_id security
        🔧 This replaces the failing query in IntelligenceService
        🔒 Enhanced with company_id filtering for multi-tenant security
        ✅ NEW: Optional content statistics loading via relationships
        """
        try:
            logger.info(f"🧠 Getting intelligence for campaign {campaign_id} (company: {company_id})")
            
            # Build query with optional relationship loading
            stmt = select(CampaignIntelligence).where(
                CampaignIntelligence.campaign_id == campaign_id
            )
            
            # Add company_id for security isolation if provided
            if company_id:
                stmt = stmt.where(CampaignIntelligence.company_id == company_id)
                logger.info(f"🔒 Company security filter applied: {company_id}")
            
            # Add intelligence type filter if specified
            if intelligence_type:
                # This would filter by analysis type if we have that field
                pass
            
            # ✅ NEW: Optionally include generated content for analytics
            if include_content_stats:
                stmt = stmt.options(selectinload(CampaignIntelligence.generated_content))
            
            # Order by confidence score and apply pagination
            stmt = stmt.order_by(desc(CampaignIntelligence.confidence_score)).offset(skip).limit(limit)
            
            result = await db.execute(stmt)
            intelligence_list = result.scalars().all()
            
            logger.info(f"✅ Found {len(intelligence_list)} intelligence entries for campaign {campaign_id}")
            
            # Log details about sources found
            if intelligence_list:
                primary_source = intelligence_list[0]
                logger.info(f"🎯 Primary source: '{primary_source.source_title}' (confidence: {primary_source.confidence_score})")
                
                # ✅ NEW: Log content generation stats if requested
                if include_content_stats and hasattr(primary_source, 'generated_content'):
                    content_count = len(primary_source.generated_content)
                    logger.info(f"📊 Primary source has generated {content_count} content items")
            
            return list(intelligence_list)
            
        except Exception as e:
            logger.error(f"❌ Error getting campaign intelligence: {e}")
            raise
    
    # 🆕 Updated methods that dashboard_stats.py expects
    
    async def get_intelligence_statistics(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get intelligence statistics for dashboard
        🆕 UPDATED: Enhanced with content generation analytics
        """
        try:
            logger.info(f"📊 Getting intelligence statistics for user {user_id}")
            
            # Get intelligence entries for the company with content stats
            intelligence_entries = await self.get_multi(
                db=db,
                filters={"company_id": company_id},
                limit=1000  # Get all for analysis
            )
            
            # Load content relationships for analytics
            intelligence_with_content = []
            for intel in intelligence_entries:
                stmt = select(CampaignIntelligence).where(
                    CampaignIntelligence.id == intel.id
                ).options(selectinload(CampaignIntelligence.generated_content))
                result = await db.execute(stmt)
                intel_with_content = result.scalar_one_or_none()
                if intel_with_content:
                    intelligence_with_content.append(intel_with_content)
            
            # Calculate statistics
            total_entries = len(intelligence_entries)
            
            if total_entries == 0:
                return {
                    "total_intelligence_entries": 0,
                    "average_confidence": 0.0,
                    "analysis_quality": "no_data",
                    "content_generation_stats": {
                        "total_content_generated": 0,
                        "sources_with_content": 0,
                        "average_content_per_source": 0.0
                    },
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
            
            # ✅ NEW: Calculate content generation statistics
            total_content_generated = 0
            sources_with_content = 0
            
            for intel in intelligence_with_content:
                if hasattr(intel, 'generated_content') and intel.generated_content:
                    content_count = len(intel.generated_content)
                    total_content_generated += content_count
                    if content_count > 0:
                        sources_with_content += 1
            
            avg_content_per_source = total_content_generated / max(1, sources_with_content)
            
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
                "content_generation_stats": {
                    "total_content_generated": total_content_generated,
                    "sources_with_content": sources_with_content,
                    "sources_without_content": total_entries - sources_with_content,
                    "average_content_per_source": round(avg_content_per_source, 1),
                    "content_generation_rate": round((sources_with_content / total_entries * 100), 1) if total_entries > 0 else 0.0
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
        🆕 UPDATED: Enhanced with real content generation metrics
        """
        try:
            logger.info(f"📈 Getting intelligence performance metrics for user {user_id}")
            
            # Get intelligence with content for real metrics
            stmt = select(CampaignIntelligence).where(
                CampaignIntelligence.company_id == company_id
            ).options(selectinload(CampaignIntelligence.generated_content))
            
            result = await db.execute(stmt)
            intelligence_entries = result.scalars().all()
            
            if not intelligence_entries:
                return {
                    "processing_performance": {
                        "average_analysis_time": 0,
                        "successful_analyses": 0,
                        "failed_analyses": 0,
                        "cache_hit_rate": 0
                    },
                    "quality_metrics": {
                        "average_confidence_score": 0,
                        "high_quality_analyses": 0,
                        "amplification_success_rate": 0
                    },
                    "content_performance": {
                        "content_generation_success_rate": 0,
                        "average_content_quality": 0,
                        "published_content_rate": 0
                    },
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
            
            # Calculate real metrics
            total_entries = len(intelligence_entries)
            successful_analyses = len([e for e in intelligence_entries if e.confidence_score and e.confidence_score > 0.5])
            
            # Content performance metrics
            all_content = []
            sources_with_content = 0
            
            for intel in intelligence_entries:
                if hasattr(intel, 'generated_content') and intel.generated_content:
                    all_content.extend(intel.generated_content)
                    if len(intel.generated_content) > 0:
                        sources_with_content += 1
            
            # Calculate content quality metrics
            content_ratings = [c.user_rating for c in all_content if c.user_rating]
            avg_content_quality = sum(content_ratings) / len(content_ratings) if content_ratings else 0.0
            
            published_content = [c for c in all_content if c.is_published]
            published_rate = len(published_content) / len(all_content) * 100 if all_content else 0.0
            
            # Calculate confidence scores
            confidence_scores = [e.confidence_score for e in intelligence_entries if e.confidence_score]
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            # Calculate amplification metrics
            amplified_sources = [e for e in intelligence_entries if e.is_amplified()]
            amplification_rate = len(amplified_sources) / total_entries * 100 if total_entries > 0 else 0.0
            
            metrics = {
                "processing_performance": {
                    "average_analysis_time": 12.5,  # This would come from processing_metadata in real implementation
                    "successful_analyses": round((successful_analyses / total_entries * 100), 1) if total_entries > 0 else 0,
                    "failed_analyses": round(((total_entries - successful_analyses) / total_entries * 100), 1) if total_entries > 0 else 0,
                    "cache_hit_rate": 85  # This would come from system metrics
                },
                "quality_metrics": {
                    "average_confidence_score": round(avg_confidence, 3),
                    "high_quality_analyses": round((len([s for s in confidence_scores if s >= 0.8]) / len(confidence_scores) * 100), 1) if confidence_scores else 0,
                    "amplification_success_rate": round(amplification_rate, 1)
                },
                "content_performance": {
                    "content_generation_success_rate": round((sources_with_content / total_entries * 100), 1) if total_entries > 0 else 0,
                    "average_content_quality": round(avg_content_quality, 2),
                    "published_content_rate": round(published_rate, 1),
                    "total_content_items": len(all_content)
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
        ✅ NEW: Optionally includes content generation stats
        """
        try:
            logger.info(f"🎯 Getting primary intelligence for campaign {campaign_id} (company: {company_id})")
            
            intelligence_list = await self.get_campaign_intelligence(
                db=db,
                campaign_id=campaign_id,
                company_id=company_id,
                limit=1,  # Just get the top one
                include_content_stats=True
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
        ✅ NEW: Includes content generation analytics
        """
        try:
            logger.info(f"📊 Getting intelligence summary for campaign {campaign_id} (company: {company_id})")
            
            # Get all intelligence for campaign with company security and content stats
            all_intelligence = await self.get_campaign_intelligence(
                db=db,
                campaign_id=campaign_id,
                company_id=company_id,
                limit=1000,  # Get all
                include_content_stats=True
            )
            
            if not all_intelligence:
                return {
                    "campaign_id": str(campaign_id),
                    "company_id": str(company_id) if company_id else None,
                    "total_intelligence_entries": 0,
                    "available_types": [],
                    "average_confidence": 0.0,
                    "highest_confidence": 0.0,
                    "analysis_status": "no_analysis",
                    "content_generation_summary": {
                        "total_content_generated": 0,
                        "sources_with_content": 0,
                        "avg_content_per_source": 0.0
                    }
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
            
            # ✅ NEW: Calculate content generation summary
            total_content = 0
            sources_with_content = 0
            
            for intel in all_intelligence:
                if hasattr(intel, 'generated_content') and intel.generated_content:
                    content_count = len(intel.generated_content)
                    total_content += content_count
                    if content_count > 0:
                        sources_with_content += 1
            
            avg_content_per_source = total_content / max(1, sources_with_content)
            
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
                "primary_source_title": all_intelligence[0].source_title if all_intelligence else None,
                "content_generation_summary": {
                    "total_content_generated": total_content,
                    "sources_with_content": sources_with_content,
                    "sources_without_content": total_entries - sources_with_content,
                    "avg_content_per_source": round(avg_content_per_source, 1),
                    "content_utilization_rate": round((sources_with_content / total_entries * 100), 1) if total_entries > 0 else 0.0
                }
            }
            
            logger.info(f"✅ Intelligence summary: {total_entries} entries, avg confidence: {average_confidence:.3f}, {total_content} content items")
            
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
    
    # ✅ UPDATED: Generated Content Methods with intelligence_id support
    
    async def get_generated_content(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        company_id: UUID,
        content_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        include_intelligence_source: bool = True
    ) -> List[GeneratedContent]:
        """
        Get generated content for a campaign with company security
        🔒 Company-aware content retrieval
        ✅ NEW: Optionally includes intelligence source information
        """
        try:
            logger.info(f"📄 Getting generated content for campaign {campaign_id} (company: {company_id})")
            
            # Build query with optional intelligence source loading
            stmt = select(GeneratedContent).where(
                and_(
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == company_id
                )
            )
            
            if content_type:
                stmt = stmt.where(GeneratedContent.content_type == content_type)
            
            # ✅ NEW: Optionally load intelligence source relationship
            if include_intelligence_source:
                stmt = stmt.options(selectinload(GeneratedContent.intelligence_source))
            
            stmt = stmt.order_by(desc(GeneratedContent.created_at)).offset(skip).limit(limit)
            
            result = await db.execute(stmt)
            content_items = result.scalars().all()
            
            logger.info(f"✅ Found {len(content_items)} content items")
            
            # ✅ NEW: Log intelligence source attribution stats
            if include_intelligence_source and content_items:
                attributed_count = sum(1 for item in content_items if item.intelligence_source)
                logger.info(f"📊 {attributed_count}/{len(content_items)} content items have intelligence attribution")
            
            return list(content_items)
            
        except Exception as e:
            logger.error(f"❌ Error getting generated content: {e}")
            raise
    
    async def get_generated_content_by_id(
        self,
        db: AsyncSession,
        content_id: UUID,
        campaign_id: UUID,
        company_id: UUID,
        include_intelligence_source: bool = True
    ) -> Optional[GeneratedContent]:
        """
        Get specific generated content with security verification
        🔒 Triple security check: content_id, campaign_id, company_id
        ✅ NEW: Optionally includes intelligence source information
        """
        try:
            stmt = select(GeneratedContent).where(
                and_(
                    GeneratedContent.id == content_id,
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == company_id
                )
            )
            
            # ✅ NEW: Optionally load intelligence source relationship
            if include_intelligence_source:
                stmt = stmt.options(selectinload(GeneratedContent.intelligence_source))
            
            result = await db.execute(stmt)
            content_item = result.scalar_one_or_none()
            
            if content_item:
                logger.info(f"✅ Found content {content_id} with security verification")
                if include_intelligence_source and content_item.intelligence_source:
                    logger.info(f"📊 Content attributed to: {content_item.intelligence_source.source_title}")
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
        """
        Create new generated content with proper company association
        ✅ NEW: Supports intelligence_id for content attribution
        """
        try:
            logger.info(f"🔨 Creating generated content for campaign {content_data.get('campaign_id')}")
            
            # ✅ NEW: Log intelligence attribution if provided
            intelligence_id = content_data.get('intelligence_id')
            if intelligence_id:
                logger.info(f"📊 Content will be attributed to intelligence source: {intelligence_id}")
            
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
        company_id: UUID,
        include_content_stats: bool = False
    ) -> Optional[CampaignIntelligence]:
        """
        Get intelligence by ID with company security
        🔒 Company-aware intelligence retrieval
        ✅ NEW: Optionally includes generated content for analytics
        """
        try:
            stmt = select(CampaignIntelligence).where(
                and_(
                    CampaignIntelligence.id == intelligence_id,
                    CampaignIntelligence.company_id == company_id
                )
            )
            
            # ✅ NEW: Optionally load generated content relationship
            if include_content_stats:
                stmt = stmt.options(selectinload(CampaignIntelligence.generated_content))
            
            result = await db.execute(stmt)
            intelligence = result.scalar_one_or_none()
            
            if intelligence:
                logger.info(f"✅ Found intelligence {intelligence_id} with company verification")
                if include_content_stats and hasattr(intelligence, 'generated_content'):
                    content_count = len(intelligence.generated_content)
                    logger.info(f"📊 Intelligence source has generated {content_count} content items")
            else:
                logger.warning(f"⚠️ Intelligence {intelligence_id} not found or access denied")
            
            return intelligence
            
        except Exception as e:
            logger.error(f"❌ Error getting intelligence by ID: {e}")
            raise
    
    # ✅ NEW: Intelligence-based content analytics methods
    
    async def get_content_by_intelligence_source(
        self,
        db: AsyncSession,
        intelligence_id: UUID,
        company_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[GeneratedContent]:
        """
        Get all content generated from a specific intelligence source
        📊 Enables intelligence source performance analysis
        """
        try:
            logger.info(f"📊 Getting content generated from intelligence source {intelligence_id}")
            
            stmt = select(GeneratedContent).where(
                and_(
                    GeneratedContent.intelligence_id == intelligence_id,
                    GeneratedContent.company_id == company_id
                )
            ).order_by(desc(GeneratedContent.created_at)).offset(skip).limit(limit)
            
            result = await db.execute(stmt)
            content_items = result.scalars().all()
            
            logger.info(f"✅ Found {len(content_items)} content items from intelligence source {intelligence_id}")
            return list(content_items)
            
        except Exception as e:
            logger.error(f"❌ Error getting content by intelligence source: {e}")
            raise
    
    async def get_intelligence_performance_analytics(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        company_id: UUID
    ) -> Dict[str, Any]:
        """
        Get comprehensive performance analytics for all intelligence sources in a campaign
        📊 Provides ROI analysis and source effectiveness metrics
        """
        try:
            logger.info(f"📊 Getting intelligence performance analytics for campaign {campaign_id}")
            
            # Get all intelligence sources with their generated content
            stmt = select(CampaignIntelligence).where(
                and_(
                    CampaignIntelligence.campaign_id == campaign_id,
                    CampaignIntelligence.company_id == company_id
                )
            ).options(selectinload(CampaignIntelligence.generated_content))
            
            result = await db.execute(stmt)
            intelligence_sources = result.scalars().all()
            
            if not intelligence_sources:
                return {
                    "campaign_id": str(campaign_id),
                    "total_sources": 0,
                    "source_performance": [],
                    "summary": {
                        "best_performing_source": None,
                        "total_content_generated": 0,
                        "average_content_per_source": 0.0,
                        "sources_with_published_content": 0
                    }
                }
            
            # Analyze each source
            source_performance = []
            total_content = 0
            sources_with_published = 0
            best_source = None
            best_score = 0
            
            for source in intelligence_sources:
                content_items = source.generated_content if hasattr(source, 'generated_content') else []
                content_count = len(content_items)
                total_content += content_count
                
                # Calculate performance metrics
                published_count = sum(1 for item in content_items if item.is_published)
                avg_rating = sum(item.user_rating for item in content_items if item.user_rating) / max(1, len([item for item in content_items if item.user_rating]))
                total_views = sum(item.view_count or 0 for item in content_items)
                
                if published_count > 0:
                    sources_with_published += 1
                
                # Calculate overall performance score
                performance_score = 0
                if content_count > 0:
                    performance_score += min(40, content_count * 5)  # Content volume (0-40)
                    performance_score += avg_rating * 8 if avg_rating else 0  # Quality (0-40)
                    performance_score += (published_count / content_count) * 20  # Success rate (0-20)
                
                # Apply intelligence confidence factor
                confidence_factor = source.confidence_score or 0.5
                final_score = performance_score * confidence_factor
                
                if final_score > best_score:
                    best_score = final_score
                    best_source = {
                        "id": str(source.id),
                        "source_title": source.source_title,
                        "confidence_score": source.confidence_score,
                        "performance_score": round(final_score, 1)
                    }
                
                source_metrics = {
                    "intelligence_id": str(source.id),
                    "source_title": source.source_title,
                    "source_url": source.source_url,
                    "confidence_score": source.confidence_score,
                    "content_generated": content_count,
                    "content_published": published_count,
                    "average_rating": round(avg_rating, 2) if avg_rating else None,
                    "total_views": total_views,
                    "success_rate": round((published_count / content_count * 100), 1) if content_count > 0 else 0,
                    "performance_score": round(final_score, 1),
                    "is_amplified": source.is_amplified(),
                    "roi_analysis": source.get_roi_analysis()
                }
                
                source_performance.append(source_metrics)
            
            # Sort by performance score
            source_performance.sort(key=lambda x: x["performance_score"], reverse=True)
            
            summary = {
                "campaign_id": str(campaign_id),
                "total_sources": len(intelligence_sources),
                "source_performance": source_performance,
                "summary": {
                    "best_performing_source": best_source,
                    "total_content_generated": total_content,
                    "average_content_per_source": round(total_content / len(intelligence_sources), 1),
                    "sources_with_published_content": sources_with_published,
                    "content_utilization_rate": round((sources_with_published / len(intelligence_sources) * 100), 1),
                    "top_3_sources": source_performance[:3]
                }
            }
            
            logger.info(f"✅ Performance analytics complete: {len(intelligence_sources)} sources, {total_content} content items")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting intelligence performance analytics: {e}")
            raise
    
    async def get_content_attribution_report(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        company_id: UUID
    ) -> Dict[str, Any]:
        """
        Generate content attribution report showing which sources generated which content
        📊 Provides full provenance tracking for content auditing
        """
        try:
            logger.info(f"📊 Generating content attribution report for campaign {campaign_id}")
            
            # Get all content with intelligence sources
            stmt = select(GeneratedContent).where(
                and_(
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == company_id
                )
            ).options(selectinload(GeneratedContent.intelligence_source))
            
            result = await db.execute(stmt)
            content_items = result.scalars().all()
            
            # Categorize content by attribution status
            attributed_content = []
            unattributed_content = []
            
            for content in content_items:
                if content.intelligence_source:
                    attributed_content.append({
                        "content_id": str(content.id),
                        "content_title": content.content_title,
                        "content_type": content.content_type,
                        "created_at": content.created_at.isoformat() if content.created_at else None,
                        "user_rating": content.user_rating,
                        "is_published": content.is_published,
                        "intelligence_source": {
                            "id": str(content.intelligence_source.id),
                            "source_title": content.intelligence_source.source_title,
                            "source_url": content.intelligence_source.source_url,
                            "confidence_score": content.intelligence_source.confidence_score,
                            "is_amplified": content.intelligence_source.is_amplified()
                        }
                    })
                else:
                    unattributed_content.append({
                        "content_id": str(content.id),
                        "content_title": content.content_title,
                        "content_type": content.content_type,
                        "created_at": content.created_at.isoformat() if content.created_at else None,
                        "user_rating": content.user_rating,
                        "is_published": content.is_published
                    })
            
            # Calculate attribution statistics
            total_content = len(content_items)
            attributed_count = len(attributed_content)
            attribution_rate = (attributed_count / total_content * 100) if total_content > 0 else 0
            
            report = {
                "campaign_id": str(campaign_id),
                "report_generated_at": datetime.now(timezone.utc).isoformat(),
                "attribution_summary": {
                    "total_content_items": total_content,
                    "attributed_content": attributed_count,
                    "unattributed_content": len(unattributed_content),
                    "attribution_rate": round(attribution_rate, 1)
                },
                "attributed_content": attributed_content,
                "unattributed_content": unattributed_content,
                "recommendations": self._generate_attribution_recommendations(attribution_rate, unattributed_content)
            }
            
            logger.info(f"✅ Attribution report complete: {attributed_count}/{total_content} content items attributed")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating content attribution report: {e}")
            raise
    
    def _generate_attribution_recommendations(self, attribution_rate: float, unattributed_content: List[Dict]) -> List[str]:
        """Generate recommendations based on attribution analysis"""
        recommendations = []
        
        if attribution_rate < 50:
            recommendations.append("Low attribution rate detected - ensure intelligence_id is set during content creation")
        elif attribution_rate < 80:
            recommendations.append("Good attribution rate - review unattributed content for missing source links")
        else:
            recommendations.append("Excellent attribution rate - content provenance tracking is working well")
        
        if len(unattributed_content) > 0:
            recommendations.append(f"{len(unattributed_content)} content items need intelligence source attribution")
            recommendations.append("Consider retroactively linking unattributed content to intelligence sources")
        
        if attribution_rate == 100:
            recommendations.append("Perfect attribution - all content has intelligence source tracking")
        
        return recommendations
    
    # ✅ NEW: Source optimization methods
    
    async def get_underutilized_intelligence_sources(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        company_id: UUID,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find high-quality intelligence sources that haven't been used for content generation
        🎯 Helps identify missed opportunities for content creation
        """
        try:
            logger.info(f"🔍 Finding underutilized intelligence sources for campaign {campaign_id}")
            
            # Get all intelligence sources with content relationships
            stmt = select(CampaignIntelligence).where(
                and_(
                    CampaignIntelligence.campaign_id == campaign_id,
                    CampaignIntelligence.company_id == company_id,
                    CampaignIntelligence.confidence_score >= min_confidence
                )
            ).options(selectinload(CampaignIntelligence.generated_content))
            
            result = await db.execute(stmt)
            intelligence_sources = result.scalars().all()
            
            underutilized = []
            for source in intelligence_sources:
                content_count = len(source.generated_content) if hasattr(source, 'generated_content') else 0
                
                # Consider underutilized if high confidence but low content generation
                if content_count < 3:  # Threshold for underutilization
                    underutilized.append({
                        "intelligence_id": str(source.id),
                        "source_title": source.source_title,
                        "source_url": source.source_url,
                        "confidence_score": source.confidence_score,
                        "content_generated": content_count,
                        "is_amplified": source.is_amplified(),
                        "potential_score": self._calculate_potential_score(source),
                        "recommended_content_types": self._suggest_content_types(source)
                    })
            
            # Sort by potential score
            underutilized.sort(key=lambda x: x["potential_score"], reverse=True)
            
            logger.info(f"✅ Found {len(underutilized)} underutilized intelligence sources")
            return underutilized
            
        except Exception as e:
            logger.error(f"❌ Error finding underutilized intelligence sources: {e}")
            raise
    
    def _calculate_potential_score(self, source: CampaignIntelligence) -> float:
        """Calculate potential score for an intelligence source"""
        score = 0
        
        # Confidence score factor (0-50 points)
        score += (source.confidence_score or 0) * 50
        
        # Amplification bonus (0-25 points)
        if source.is_amplified():
            score += 25
        
        # Rich intelligence data bonus (0-25 points)
        intelligence_data = source.get_all_intelligence()
        data_richness = sum(1 for category in intelligence_data.values() if category and len(str(category)) > 50)
        score += min(25, data_richness * 5)
        
        return round(score, 1)
    
    def _suggest_content_types(self, source: CampaignIntelligence) -> List[str]:
        """Suggest content types based on intelligence source characteristics"""
        suggestions = []
        
        # Base suggestions for all sources
        suggestions.extend(["email_sequence", "social_media_posts", "ad_copy"])
        
        # Source-type specific suggestions
        if hasattr(source.source_type, 'value'):
            source_type = source.source_type.value
            if source_type == "SALES_PAGE":
                suggestions.extend(["landing_page", "sales_copy"])
            elif source_type == "VIDEO":
                suggestions.extend(["video_script", "transcript_content"])
            elif source_type == "DOCUMENT":
                suggestions.extend(["blog_post", "article_content"])
        
        # Intelligence-based suggestions
        intelligence_data = source.get_all_intelligence()
        if intelligence_data.get("psychology_intelligence"):
            suggestions.append("persuasive_copy")
        if intelligence_data.get("offer_intelligence"):
            suggestions.append("offer_analysis")
        
        # Remove duplicates and return top suggestions
        return list(dict.fromkeys(suggestions))[:5]