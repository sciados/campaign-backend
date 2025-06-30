"""
File: src/intelligence/utils/campaign_helpers.py
Campaign Helpers - Utility functions for campaign operations
Extracted from main routes.py for better organization
"""
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from src.models.campaign import Campaign
from src.models.intelligence import CampaignIntelligence, GeneratedContent

logger = logging.getLogger(__name__)


async def update_campaign_counters(campaign_id: str, db: AsyncSession) -> bool:
    """Update campaign counter fields based on actual data"""
    try:
        # Count intelligence sources
        intelligence_count = await db.execute(
            select(func.count(CampaignIntelligence.id)).where(
                CampaignIntelligence.campaign_id == campaign_id
            )
        )
        sources_count = intelligence_count.scalar() or 0

        # Count generated content
        content_count = await db.execute(
            select(func.count(GeneratedContent.id)).where(
                GeneratedContent.campaign_id == campaign_id
            )
        )
        generated_content_count = content_count.scalar() or 0

        # Update campaign record
        await db.execute(
            update(Campaign).where(Campaign.id == campaign_id).values(
                sources_count=sources_count,
                intelligence_extracted=sources_count,
                intelligence_count=sources_count,
                content_generated=generated_content_count,
                generated_content_count=generated_content_count,
                updated_at=datetime.utcnow()
            )
        )

        logger.info(f"📊 Updated campaign counters: {sources_count} sources, {generated_content_count} content")
        return True

    except Exception as e:
        logger.error(f"❌ Error updating campaign counters: {str(e)}")
        return False


async def get_campaign_with_verification(
    campaign_id: str, company_id: str, db: AsyncSession
) -> Optional[Campaign]:
    """Get campaign with company verification"""
    try:
        campaign_result = await db.execute(
            select(Campaign).where(
                Campaign.id == campaign_id,
                Campaign.company_id == company_id
            )
        )
        return campaign_result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"❌ Error getting campaign: {str(e)}")
        return None


async def calculate_campaign_statistics(campaign_id: str, db: AsyncSession) -> dict:
    """Calculate comprehensive campaign statistics"""
    try:
        # Get intelligence sources
        intelligence_result = await db.execute(
            select(CampaignIntelligence).where(
                CampaignIntelligence.campaign_id == campaign_id
            )
        )
        intelligence_sources = intelligence_result.scalars().all()
        
        # Get generated content
        content_result = await db.execute(
            select(GeneratedContent).where(
                GeneratedContent.campaign_id == campaign_id
            )
        )
        content_items = content_result.scalars().all()
        
        # Calculate intelligence statistics
        total_sources = len(intelligence_sources)
        confidence_scores = [s.confidence_score for s in intelligence_sources if s.confidence_score]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Count by source type
        source_types = {}
        amplified_sources = 0
        
        for source in intelligence_sources:
            source_type = source.source_type.value if source.source_type else "unknown"
            source_types[source_type] = source_types.get(source_type, 0) + 1
            
            # Check amplification
            if source.processing_metadata and source.processing_metadata.get("amplification_applied", False):
                amplified_sources += 1
        
        # Calculate content statistics
        total_content = len(content_items)
        content_types = {}
        published_content = 0
        
        for content in content_items:
            content_type = content.content_type or "unknown"
            content_types[content_type] = content_types.get(content_type, 0) + 1
            
            if content.is_published:
                published_content += 1
        
        return {
            "intelligence_statistics": {
                "total_sources": total_sources,
                "average_confidence": round(avg_confidence, 3),
                "source_types": source_types,
                "amplified_sources": amplified_sources,
                "amplification_coverage": f"{amplified_sources}/{total_sources}" if total_sources > 0 else "0/0"
            },
            "content_statistics": {
                "total_content": total_content,
                "content_types": content_types,
                "published_content": published_content,
                "draft_content": total_content - published_content,
                "publish_rate": round(published_content / total_content * 100, 1) if total_content > 0 else 0.0
            },
            "performance_metrics": {
                "content_per_source": round(total_content / total_sources, 2) if total_sources > 0 else 0.0,
                "avg_confidence_score": avg_confidence,
                "total_data_points": total_sources + total_content
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculating campaign statistics: {str(e)}")
        return {
            "intelligence_statistics": {"error": str(e)},
            "content_statistics": {"error": str(e)},
            "performance_metrics": {"error": str(e)}
        }


def format_intelligence_for_export(intelligence_sources: list) -> dict:
    """Format intelligence data for export"""
    formatted_data = {
        "intelligence_sources": [],
        "summary": {
            "total_sources": len(intelligence_sources),
            "export_timestamp": datetime.utcnow().isoformat()
        }
    }
    
    for source in intelligence_sources:
        try:
            formatted_source = {
                "id": str(source.id),
                "source_url": source.source_url,
                "source_title": source.source_title,
                "source_type": source.source_type.value if source.source_type else "unknown",
                "confidence_score": source.confidence_score,
                "analysis_status": source.analysis_status.value if source.analysis_status else "unknown",
                "created_at": source.created_at.isoformat() if source.created_at else None,
                "intelligence_data": {
                    "offer_intelligence": source.offer_intelligence or {},
                    "psychology_intelligence": source.psychology_intelligence or {},
                    "content_intelligence": source.content_intelligence or {},
                    "competitive_intelligence": source.competitive_intelligence or {},
                    "brand_intelligence": source.brand_intelligence or {}
                },
                "processing_metadata": source.processing_metadata or {}
            }
            formatted_data["intelligence_sources"].append(formatted_source)
        except Exception as e:
            logger.warning(f"⚠️ Error formatting source {source.id}: {str(e)}")
            continue
    
    return formatted_data


def format_content_for_export(content_items: list) -> dict:
    """Format content data for export"""
    formatted_data = {
        "generated_content": [],
        "summary": {
            "total_content": len(content_items),
            "export_timestamp": datetime.utcnow().isoformat()
        }
    }
    
    for content in content_items:
        try:
            formatted_content = {
                "id": str(content.id),
                "content_type": content.content_type,
                "content_title": content.content_title,
                "content_body": content.content_body,
                "content_metadata": content.content_metadata or {},
                "generation_settings": content.generation_settings or {},
                "intelligence_used": content.intelligence_used or {},
                "performance_data": content.performance_data or {},
                "is_published": content.is_published,
                "published_at": content.published_at.isoformat() if content.published_at else None,
                "created_at": content.created_at.isoformat() if content.created_at else None,
                "user_rating": content.user_rating
            }
            formatted_data["generated_content"].append(formatted_content)
        except Exception as e:
            logger.warning(f"⚠️ Error formatting content {content.id}: {str(e)}")
            continue
    
    return formatted_data


def merge_export_data(intelligence_data: dict, content_data: dict, campaign_info: dict) -> dict:
    """Merge intelligence and content data for complete export"""
    return {
        "campaign_info": campaign_info,
        "intelligence_data": intelligence_data,
        "content_data": content_data,
        "export_metadata": {
            "exported_at": datetime.utcnow().isoformat(),
            "export_version": "2.0.0",
            "total_intelligence_sources": intelligence_data["summary"]["total_sources"],
            "total_content_items": content_data["summary"]["total_content"]
        }
    }


def validate_campaign_access(campaign: Campaign, user_company_id: str) -> bool:
    """Validate user has access to campaign"""
    if not campaign:
        return False
    return str(campaign.company_id) == str(user_company_id)


def get_intelligence_summary(intelligence_sources: list) -> dict:
    """Get summary of intelligence sources"""
    if not intelligence_sources:
        return {
            "total_sources": 0,
            "avg_confidence": 0.0,
            "source_types": {},
            "amplified_sources": 0
        }
    
    confidence_scores = [s.confidence_score for s in intelligence_sources if s.confidence_score]
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    
    source_types = {}
    amplified_sources = 0
    
    for source in intelligence_sources:
        # Count source types
        source_type = source.source_type.value if source.source_type else "unknown"
        source_types[source_type] = source_types.get(source_type, 0) + 1
        
        # Count amplified sources
        if source.processing_metadata and source.processing_metadata.get("amplification_applied", False):
            amplified_sources += 1
    
    return {
        "total_sources": len(intelligence_sources),
        "avg_confidence": round(avg_confidence, 3),
        "source_types": source_types,
        "amplified_sources": amplified_sources,
        "amplification_coverage": f"{amplified_sources}/{len(intelligence_sources)}"
    }


def get_content_summary(content_items: list) -> dict:
    """Get summary of generated content"""
    if not content_items:
        return {
            "total_content": 0,
            "content_types": {},
            "published_content": 0,
            "publish_rate": 0.0
        }
    
    content_types = {}
    published_content = 0
    
    for content in content_items:
        # Count content types
        content_type = content.content_type or "unknown"
        content_types[content_type] = content_types.get(content_type, 0) + 1
        
        # Count published content
        if content.is_published:
            published_content += 1
    
    total_content = len(content_items)
    publish_rate = round(published_content / total_content * 100, 1) if total_content > 0 else 0.0
    
    return {
        "total_content": total_content,
        "content_types": content_types,
        "published_content": published_content,
        "draft_content": total_content - published_content,
        "publish_rate": publish_rate
    }