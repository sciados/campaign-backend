"""
File: src/intelligence/handlers/intelligence_handler.py
Intelligence Handler - Intelligence data management operations
Supporting the management routes
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.models.user import User
from src.models.campaign import Campaign
from src.models.intelligence import CampaignIntelligence, GeneratedContent
from ..utils.campaign_helpers import (
    get_campaign_with_verification,
    calculate_campaign_statistics,
    format_intelligence_for_export,
    format_content_for_export,
    merge_export_data,
    get_intelligence_summary,
    get_content_summary,
    update_campaign_counters
)

# NEW - using enhancement.py directly  
try:
    from ..amplifier.enhancement import (
        identify_opportunities,
        generate_enhancements,
        create_enriched_intelligence
    )
    ENHANCEMENT_FUNCTIONS_AVAILABLE = True
except ImportError:
    ENHANCEMENT_FUNCTIONS_AVAILABLE = False


logger = logging.getLogger(__name__)


class IntelligenceHandler:
    """Handle intelligence data management operations"""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
        self.enhancement_available = ENHANCEMENT_FUNCTIONS_AVAILABLE
    
    async def get_campaign_intelligence(self, campaign_id: str) -> Dict[str, Any]:
        """Get all intelligence sources for a campaign with proper error handling"""
        
        logger.info(f"🔍 Getting ENHANCED intelligence for campaign: {campaign_id}")
        
        try:
            # Verify campaign access
            campaign = await get_campaign_with_verification(
                campaign_id, str(self.user.company_id), self.db
            )
            
            if not campaign:
                raise ValueError("Campaign not found or access denied")
            
            logger.info(f"✅ Campaign access verified: {campaign.title}")
            
            # Get intelligence sources
            intelligence_sources = await self._get_intelligence_sources(campaign_id)
            
            # Get generated content
            generated_content = await self._get_generated_content(campaign_id)
            
            # Build enhanced response
            return self._build_intelligence_response(
                campaign_id, intelligence_sources, generated_content
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"❌ Critical error in get_campaign_intelligence: {str(e)}")
            return self._build_fallback_response(campaign_id)
    
    async def delete_intelligence_source(self, campaign_id: str, intelligence_id: str) -> Dict[str, Any]:
        """Delete an intelligence source"""
        
        # Verify campaign access
        campaign = await get_campaign_with_verification(
            campaign_id, str(self.user.company_id), self.db
        )
        if not campaign:
            raise ValueError("Campaign not found or access denied")
        
        # Get intelligence source
        intelligence_result = await self.db.execute(
            select(CampaignIntelligence).where(
                and_(
                    CampaignIntelligence.id == intelligence_id,
                    CampaignIntelligence.campaign_id == campaign_id,
                    CampaignIntelligence.company_id == self.user.company_id
                )
            )
        )
        intelligence_source = intelligence_result.scalar_one_or_none()
        
        if not intelligence_source:
            raise ValueError("Intelligence source not found")
        
        # Delete the source
        await self.db.delete(intelligence_source)
        await self.db.commit()
        
        # Update campaign counters
        await update_campaign_counters(campaign_id, self.db)
        
        return {"message": "Intelligence source deleted successfully"}
    
    async def amplify_intelligence_source(
        self, campaign_id: str, intelligence_id: str, preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Amplify an existing intelligence source using direct enhancement functions"""
        
        if not self.enhancement_available:
            raise ValueError("Enhancement functions not available. Install amplifier dependencies.")
        
        # Verify campaign access
        campaign = await get_campaign_with_verification(
            campaign_id, str(self.user.company_id), self.db
        )
        if not campaign:
            raise ValueError("Campaign not found or access denied")
        
        # Get intelligence source
        intelligence_result = await self.db.execute(
            select(CampaignIntelligence).where(
                and_(
                    CampaignIntelligence.id == intelligence_id,
                    CampaignIntelligence.campaign_id == campaign_id,
                    CampaignIntelligence.company_id == self.user.company_id
                )
            )
        )
        intelligence_source = intelligence_result.scalar_one_or_none()
        
        if not intelligence_source:
            raise ValueError("Intelligence source not found")
        
        try:
            # Prepare data for amplification
            base_intel = {
                "offer_intelligence": intelligence_source.offer_intelligence or {},
                "psychology_intelligence": intelligence_source.psychology_intelligence or {},
                "content_intelligence": intelligence_source.content_intelligence or {},
                "competitive_intelligence": intelligence_source.competitive_intelligence or {},
                "brand_intelligence": intelligence_source.brand_intelligence or {},
                "source_url": intelligence_source.source_url,
                "confidence_score": intelligence_source.confidence_score or 0.0,
                "page_title": intelligence_source.source_title or "",
                "product_name": intelligence_source.source_title or "Unknown Product"
            }
            
            # Set up AI providers (you may need to adjust this based on your config)
            ai_providers = []  # This should be populated from your AI service configuration
            
            # Set default preferences if not provided
            if not preferences:
                preferences = {
                    "enhance_scientific_backing": True,
                    "boost_credibility": True,
                    "competitive_analysis": True,
                    "psychological_depth": "medium",
                    "content_optimization": True
                }
            
            logger.info(f"🚀 Starting amplification for intelligence source: {intelligence_id}")
            
            # STEP 1: Identify opportunities
            opportunities = await identify_opportunities(
                base_intel=base_intel,
                preferences=preferences,
                providers=ai_providers
            )
            
            opportunities_count = opportunities.get("opportunity_metadata", {}).get("total_opportunities", 0)
            logger.info(f"🔍 Identified {opportunities_count} enhancement opportunities")
            
            # STEP 2: Generate enhancements
            enhancements = await generate_enhancements(
                base_intel=base_intel,
                opportunities=opportunities,
                providers=ai_providers
            )
            
            enhancement_metadata = enhancements.get("enhancement_metadata", {})
            total_enhancements = enhancement_metadata.get("total_enhancements", 0)
            confidence_boost = enhancement_metadata.get("confidence_boost", 0.0)
            
            logger.info(f"✨ Generated {total_enhancements} enhancements with {confidence_boost:.1%} confidence boost")
            
            # STEP 3: Create enriched intelligence
            enriched_intelligence = create_enriched_intelligence(
                base_intel=base_intel,
                enhancements=enhancements
            )
            
            # Update the intelligence source with enriched data
            intelligence_source.offer_intelligence = enriched_intelligence.get("offer_intelligence", {})
            intelligence_source.psychology_intelligence = enriched_intelligence.get("psychology_intelligence", {})
            intelligence_source.content_intelligence = enriched_intelligence.get("content_intelligence", {})
            intelligence_source.competitive_intelligence = enriched_intelligence.get("competitive_intelligence", {})
            intelligence_source.brand_intelligence = enriched_intelligence.get("brand_intelligence", {})
            
            # Update confidence score if improved
            new_confidence = enriched_intelligence.get("confidence_score", intelligence_source.confidence_score)
            if new_confidence > intelligence_source.confidence_score:
                intelligence_source.confidence_score = new_confidence
            
            # Update processing metadata
            enrichment_metadata = enriched_intelligence.get("enrichment_metadata", {})
            
            amplification_metadata = {
                "amplification_applied": True,
                "amplification_method": "direct_enhancement_functions",
                "opportunities_identified": opportunities_count,
                "total_enhancements": total_enhancements,
                "confidence_boost": confidence_boost,
                "base_confidence": base_intel.get("confidence_score", 0.0),
                "amplified_confidence": new_confidence,
                "credibility_score": enhancement_metadata.get("credibility_score", 0.0),
                "enhancement_quality": enhancement_metadata.get("enhancement_quality", "unknown"),
                "modules_successful": enhancement_metadata.get("modules_successful", []),
                "scientific_enhancements": len(enhancements.get("scientific_validation", {})) if enhancements.get("scientific_validation") else 0,
                "amplified_at": datetime.utcnow().isoformat(),
                "amplification_preferences": preferences,
                "system_architecture": "direct_modular_enhancement"
            }
            
            intelligence_source.processing_metadata = {
                **(intelligence_source.processing_metadata or {}),
                **amplification_metadata
            }
            
            await self.db.commit()
            await self.db.refresh(intelligence_source)
            
            logger.info(f"✅ Intelligence source amplified successfully - Final confidence: {new_confidence:.2f}")
            
            return {
                "intelligence_id": str(intelligence_source.id),
                "amplification_applied": True,
                "confidence_boost": confidence_boost,
                "opportunities_identified": opportunities_count,
                "total_enhancements": total_enhancements,
                "scientific_enhancements": amplification_metadata["scientific_enhancements"],
                "enhancement_quality": enhancement_metadata.get("enhancement_quality", "unknown"),
                "message": "Intelligence source amplified successfully using direct enhancement functions"
            }
            
        except Exception as e:
            logger.error(f"❌ Amplification failed for intelligence source {intelligence_id}: {str(e)}")
            
            # Update processing metadata with error info
            error_metadata = {
                "amplification_applied": False,
                "amplification_error": str(e),
                "amplification_attempted_at": datetime.utcnow().isoformat(),
                "fallback_to_base": True
            }
            
            intelligence_source.processing_metadata = {
                **(intelligence_source.processing_metadata or {}),
                **error_metadata
            }
            
            await self.db.commit()
            
            return {
                "intelligence_id": str(intelligence_source.id),
                "amplification_applied": False,
                "error": str(e),
                "message": "Amplification failed, but intelligence source preserved"
            }
    
    async def get_campaign_statistics(self, campaign_id: str) -> Dict[str, Any]:
        """Get detailed statistics for a campaign"""
        
        # Verify campaign access
        campaign = await get_campaign_with_verification(
            campaign_id, str(self.user.company_id), self.db
        )
        if not campaign:
            raise ValueError("Campaign not found or access denied")
        
        # Calculate statistics
        statistics = await calculate_campaign_statistics(campaign_id, self.db)
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.title,
            **statistics
        }
    
    async def export_campaign_data(
        self, campaign_id: str, export_format: str, include_content: bool
    ) -> Dict[str, Any]:
        """Export campaign intelligence and content data"""
        
        # Verify campaign access
        campaign = await get_campaign_with_verification(
            campaign_id, str(self.user.company_id), self.db
        )
        if not campaign:
            raise ValueError("Campaign not found or access denied")
        
        # Get intelligence sources
        intelligence_sources = await self._get_intelligence_sources(campaign_id)
        intelligence_data = format_intelligence_for_export(intelligence_sources)
        
        # Get content data if requested
        content_data = {}
        if include_content:
            content_items = await self._get_generated_content(campaign_id)
            content_data = format_content_for_export(content_items)
        
        # Prepare campaign info
        campaign_info = {
            "id": str(campaign.id),
            "title": campaign.title,
            "description": campaign.description,
            "target_audience": campaign.target_audience,
            "created_at": campaign.created_at.isoformat() if campaign.created_at else None
        }
        
        # Merge all data
        export_data = merge_export_data(intelligence_data, content_data, campaign_info)
        
        # For Railway/PostgreSQL deployment, we'll return the data directly
        # In a production setup, you might want to store this in cloud storage
        return {
            "export_id": f"export_{campaign_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "export_format": export_format,
            "data": export_data if export_format == "json" else str(export_data),
            "file_size": len(json.dumps(export_data)),
            "exported_at": datetime.utcnow().isoformat(),
            "includes": {
                "intelligence": True,
                "content": include_content,
                "metadata": True
            }
        }
    
    # Private helper methods
    
    async def _get_intelligence_sources(self, campaign_id: str) -> list:
        """Get intelligence sources for campaign"""
        try:
            intelligence_query = select(CampaignIntelligence).where(
                CampaignIntelligence.campaign_id == campaign_id
            ).order_by(CampaignIntelligence.created_at.desc())
            
            result = await self.db.execute(intelligence_query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"❌ Error getting intelligence sources: {str(e)}")
            return []
    
    async def _get_generated_content(self, campaign_id: str) -> list:
        """Get generated content for campaign"""
        try:
            content_query = select(GeneratedContent).where(
                GeneratedContent.campaign_id == campaign_id
            ).order_by(GeneratedContent.created_at.desc())
            
            result = await self.db.execute(content_query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"❌ Error getting generated content: {str(e)}")
            return []
    
    def _build_intelligence_response(
        self, campaign_id: str, intelligence_sources: list, generated_content: list
    ) -> Dict[str, Any]:
        """Build enhanced intelligence response"""
        
        try:
            # Format intelligence sources
            intelligence_data = []
            amplified_sources = 0
            total_scientific_enhancements = 0
            
            for source in intelligence_sources:
                try:
                    amplification_metadata = source.processing_metadata or {}
                    
                    if amplification_metadata.get("amplification_applied", False):
                        amplified_sources += 1
                        total_scientific_enhancements += amplification_metadata.get("scientific_enhancements", 0)
                    
                    intelligence_data.append({
                        "id": str(source.id),
                        "source_title": source.source_title or "Untitled Source",
                        "source_url": source.source_url or "",
                        "source_type": source.source_type.value if source.source_type else "unknown",
                        "confidence_score": source.confidence_score or 0.0,
                        "usage_count": source.usage_count or 0,
                        "analysis_status": source.analysis_status.value if source.analysis_status else "unknown",
                        "created_at": source.created_at.isoformat() if source.created_at else None,
                        "updated_at": source.updated_at.isoformat() if source.updated_at else None,
                        "offer_intelligence": source.offer_intelligence or {},
                        "psychology_intelligence": source.psychology_intelligence or {},
                        "content_intelligence": source.content_intelligence or {},
                        "competitive_intelligence": source.competitive_intelligence or {},
                        "brand_intelligence": source.brand_intelligence or {},
                        "amplification_status": {
                            "is_amplified": amplification_metadata.get("amplification_applied", False),
                            "confidence_boost": amplification_metadata.get("confidence_boost", 0.0),
                            "scientific_enhancements": amplification_metadata.get("scientific_enhancements", 0),
                            "credibility_score": amplification_metadata.get("credibility_score", 0.0),
                            "amplified_at": amplification_metadata.get("amplified_at"),
                            "amplification_available": self.enhancement_available,
                            "enhancement_quality": amplification_metadata.get("enhancement_quality", "unknown"),
                            "amplification_method": amplification_metadata.get("amplification_method", "unknown")
                        }
                    })
                except Exception as source_error:
                    logger.warning(f"⚠️ Error processing intelligence source {source.id}: {str(source_error)}")
                    continue
            
            # Format content data
            content_data = []
            for content in generated_content:
                try:
                    intelligence_used = content.intelligence_used or {}
                    is_amplified_content = intelligence_used.get("amplified", False)
                    
                    content_data.append({
                        "id": str(content.id),
                        "content_type": content.content_type or "unknown",
                        "content_title": content.content_title or "Untitled Content",
                        "created_at": content.created_at.isoformat() if content.created_at else None,
                        "user_rating": content.user_rating,
                        "is_published": content.is_published or False,
                        "performance_data": content.performance_data or {},
                        "amplification_context": {
                            "generated_from_amplified_intelligence": is_amplified_content,
                            "amplification_metadata": intelligence_used.get("amplification_metadata", {})
                        }
                    })
                except Exception as content_error:
                    logger.warning(f"⚠️ Error processing content {content.id}: {str(content_error)}")
                    continue
            
            # Calculate summary statistics
            total_intelligence = len(intelligence_sources)
            total_content = len(generated_content)
            avg_confidence = 0.0
            
            if intelligence_sources:
                confidence_scores = [s.confidence_score for s in intelligence_sources if s.confidence_score is not None]
                avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            return {
                "campaign_id": campaign_id,
                "intelligence_sources": intelligence_data,
                "generated_content": content_data,
                "summary": {
                    "total_intelligence_sources": total_intelligence,
                    "total_generated_content": total_content,
                    "avg_confidence_score": round(avg_confidence, 3),
                    "amplification_summary": {
                        "sources_amplified": amplified_sources,
                        "sources_available_for_amplification": total_intelligence - amplified_sources,
                        "total_scientific_enhancements": total_scientific_enhancements,
                        "amplification_available": self.enhancement_available,
                        "amplification_coverage": f"{amplified_sources}/{total_intelligence}" if total_intelligence > 0 else "0/0",
                        "system_architecture": "direct_modular_enhancement"
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error building intelligence response: {str(e)}")
            return self._build_fallback_response(campaign_id)
    
    def _build_fallback_response(self, campaign_id: str) -> Dict[str, Any]:
        """Build fallback response when errors occur"""
        return {
            "campaign_id": campaign_id,
            "intelligence_sources": [],
            "generated_content": [],
            "summary": {
                "total_intelligence_sources": 0,
                "total_generated_content": 0,
                "avg_confidence_score": 0.0,
                "amplification_summary": {
                    "sources_amplified": 0,
                    "sources_available_for_amplification": 0,
                    "total_scientific_enhancements": 0,
                    "amplification_available": self.enhancement_available,
                    "amplification_coverage": "0/0",
                    "system_architecture": "direct_modular_enhancement"
                }
            },
            "error": "Failed to load intelligence data",
            "fallback_response": True
        }