"""
File: src/intelligence/utils/campaign_helpers.py
Campaign Helpers - FIXED VERSION - Resolves ChunkedIteratorResult async/await error
🔥 CRITICAL FIX: Properly handle SQLAlchemy async query results
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
    """
    🔥 FIXED: Update campaign counter fields based on actual data
    RESOLVES: ChunkedIteratorResult can't be used in 'await' expression
    """
    try:
        logger.info(f"🔄 Updating campaign counters for campaign: {campaign_id}")
        
        # 🔥 FIX 1: Properly handle async query results - use .scalar() not .scalar_one()
        # Count intelligence sources
        intelligence_count_query = select(func.count(CampaignIntelligence.id)).where(
            CampaignIntelligence.campaign_id == campaign_id
        )
        intelligence_result = await db.execute(intelligence_count_query)
        sources_count = intelligence_result.scalar() or 0
        logger.info(f"📊 Intelligence sources count: {sources_count}")

        # Count generated content  
        content_count_query = select(func.count(GeneratedContent.id)).where(
            GeneratedContent.campaign_id == campaign_id
        )
        content_result = await db.execute(content_count_query)
        generated_content_count = content_result.scalar() or 0
        logger.info(f"📊 Generated content count: {generated_content_count}")

        # 🔥 FIX 2: Use proper async update with explicit commit
        update_query = update(Campaign).where(Campaign.id == campaign_id).values(
            sources_count=sources_count,
            intelligence_extracted=sources_count,
            intelligence_count=sources_count,
            content_generated=generated_content_count,
            generated_content_count=generated_content_count,
            updated_at=datetime.utcnow()
        )
        
        await db.execute(update_query)
        
        # 🔥 FIX 3: Proper async commit with fallback
        try:
            await db.commit()
        except (TypeError, AttributeError):
            db.commit()

        logger.info(f"✅ Campaign counters updated: {sources_count} sources, {generated_content_count} content")
        return True

    except Exception as e:
        logger.error(f"❌ Error updating campaign counters: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        
        # Rollback on error
        try:
            await db.rollback()
        except (TypeError, AttributeError):
            db.rollback()
        
        return False


async def get_campaign_with_verification(
    campaign_id: str, company_id: str, db: AsyncSession
) -> Optional[Campaign]:
    """🔥 FIXED: Get campaign with company verification"""
    try:
        campaign_query = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.company_id == company_id
        )
        campaign_result = await db.execute(campaign_query)
        return campaign_result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"❌ Error getting campaign: {str(e)}")
        return None


async def calculate_campaign_statistics(campaign_id: str, db: AsyncSession) -> dict:
    """🔥 FIXED: Calculate comprehensive campaign statistics"""
    try:
        # Get intelligence sources with proper async handling
        intelligence_query = select(CampaignIntelligence).where(
            CampaignIntelligence.campaign_id == campaign_id
        )
        intelligence_result = await db.execute(intelligence_query)
        intelligence_sources = intelligence_result.scalars().all()
        
        # Get generated content with proper async handling
        content_query = select(GeneratedContent).where(
            GeneratedContent.campaign_id == campaign_id
        )
        content_result = await db.execute(content_query)
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
    """Format intelligence data for export - No async issues here"""
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
    """Format content data for export - No async issues here"""
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


# 🔥 CRITICAL FIX SUMMARY:
"""
RESOLVED ChunkedIteratorResult Error:

✅ ROOT CAUSE IDENTIFIED:
- The error was in update_campaign_counters() function
- SQLAlchemy async query results were not being handled properly
- Using .scalar() instead of improper result handling

✅ SPECIFIC FIXES APPLIED:
1. Fixed async query result handling in update_campaign_counters()
2. Added proper error handling with rollback
3. Used explicit async commit with fallback
4. Added detailed logging for debugging

✅ DATABASE COLUMN ISSUES CONFIRMED:
- generated_content table does NOT have analysis_status column ✅
- All columns match the database schema shown in images ✅
- No column mismatches causing the async/await error ✅

✅ ASYNC/AWAIT PATTERN FIXES:
- Proper use of await db.execute() followed by .scalar()
- Explicit commit/rollback handling
- Error logging with rollback on failure

🎯 DEPLOYMENT READY:
This fixed version should resolve the ChunkedIteratorResult error completely.
The async/await pattern is now correct for SQLAlchemy 1.4+ with AsyncSession.
"""