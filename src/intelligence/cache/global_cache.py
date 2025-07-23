# Global Cache Architecture System
# File: src/intelligence/cache/global_cache.py

import logging
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, text, func
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GlobalIntelligenceCache:
    """
    Global cache for sales page intelligence that all users can access
    Separates shared intelligence from private user content
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache_duration_days = 60  # How long to keep global cache
    
    def generate_cache_key(self, url: str) -> str:
        """Generate consistent cache key for URL"""
        # Normalize URL for consistent caching
        normalized_url = self._normalize_url(url)
        return hashlib.sha256(normalized_url.encode()).hexdigest()
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for consistent caching"""
        # Remove tracking parameters and normalize
        import re
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        parsed = urlparse(url.lower().strip())
        
        # Remove common tracking parameters
        tracking_params = {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'fbclid', 'gclid', 'msclkid', 'ref', 'affiliate_id', 'partner_id'
        }
        
        if parsed.query:
            query_params = parse_qs(parsed.query)
            # Remove tracking parameters
            clean_params = {k: v for k, v in query_params.items() if k not in tracking_params}
            clean_query = urlencode(clean_params, doseq=True)
        else:
            clean_query = ''
        
        # Remove trailing slash, normalize path
        clean_path = parsed.path.rstrip('/')
        
        # Reconstruct clean URL
        clean_url = urlunparse((
            parsed.scheme or 'https',
            parsed.netloc,
            clean_path,
            parsed.params,
            clean_query,
            ''  # Remove fragment
        ))
        
        return clean_url
    
    async def check_global_cache(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Check if intelligence exists in global cache
        Returns cached intelligence if available
        """
        try:
            cache_key = self.generate_cache_key(url)
            
            # Look for existing global intelligence
            query = text("""
                SELECT 
                    id,
                    source_url,
                    source_title,
                    confidence_score,
                    offer_intelligence,
                    psychology_intelligence,
                    content_intelligence,
                    competitive_intelligence,
                    brand_intelligence,
                    scientific_intelligence,
                    credibility_intelligence,
                    market_intelligence,
                    emotional_transformation_intelligence,
                    scientific_authority_intelligence,
                    raw_content,
                    processing_metadata,
                    created_at
                FROM global_intelligence_cache 
                WHERE cache_key = :cache_key 
                AND created_at >= NOW() - INTERVAL ':cache_days days'
                AND confidence_score >= 0.7
                ORDER BY confidence_score DESC, created_at DESC
                LIMIT 1
            """)
            
            result = await self.db.execute(query, {
                "cache_key": cache_key,
                "cache_days": self.cache_duration_days
            })
            row = result.fetchone()
            
            if row:
                logger.info(f"🎯 GLOBAL CACHE HIT: Found intelligence for {url}")
                logger.info(f"   Cache age: {(datetime.now(timezone.utc) - row.created_at).days} days")
                logger.info(f"   Confidence: {row.confidence_score:.2f}")
                
                # Return structured cache data
                cached_intelligence = {
                    "cache_hit": True,
                    "global_intelligence_id": str(row.id),
                    "source_url": row.source_url,
                    "source_title": row.source_title,
                    "confidence_score": row.confidence_score,
                    "cached_at": datetime.now(timezone.utc),
                    "original_analysis_date": row.created_at.isoformat(),
                    
                    # Base intelligence
                    "offer_intelligence": row.offer_intelligence or {},
                    "psychology_intelligence": row.psychology_intelligence or {},
                    "content_intelligence": row.content_intelligence or {},
                    "competitive_intelligence": row.competitive_intelligence or {},
                    "brand_intelligence": row.brand_intelligence or {},
                    
                    # AI-enhanced intelligence
                    "scientific_intelligence": row.scientific_intelligence or {},
                    "credibility_intelligence": row.credibility_intelligence or {},
                    "market_intelligence": row.market_intelligence or {},
                    "emotional_transformation_intelligence": row.emotional_transformation_intelligence or {},
                    "scientific_authority_intelligence": row.scientific_authority_intelligence or {},
                    
                    # Metadata
                    "raw_content": row.raw_content or "",
                    "processing_metadata": row.processing_metadata or {}
                }
                
                # Track cache hit
                await self._track_cache_hit(str(row.id))
                
                return cached_intelligence
            
            else:
                logger.info(f"🔍 GLOBAL CACHE MISS: No intelligence found for {url}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error checking global cache: {str(e)}")
            return None
    
    async def store_in_global_cache(self, analysis_result: Dict[str, Any]) -> bool:
        """
        Store analysis results in global cache for all users to access
        """
        try:
            url = analysis_result.get("source_url")
            if not url:
                logger.error("❌ No source URL in analysis result")
                return False
            
            cache_key = self.generate_cache_key(url)
            
            # Check if already exists
            existing_query = text("""
                SELECT id FROM global_intelligence_cache 
                WHERE cache_key = :cache_key
                LIMIT 1
            """)
            
            existing_result = await self.db.execute(existing_query, {"cache_key": cache_key})
            if existing_result.fetchone():
                logger.info(f"⏭️ Intelligence already in global cache for {url}")
                return True
            
            # Store in global cache
            insert_query = text("""
                INSERT INTO global_intelligence_cache (
                    cache_key,
                    source_url,
                    source_title,
                    confidence_score,
                    offer_intelligence,
                    psychology_intelligence,
                    content_intelligence,
                    competitive_intelligence,
                    brand_intelligence,
                    scientific_intelligence,
                    credibility_intelligence,
                    market_intelligence,
                    emotional_transformation_intelligence,
                    scientific_authority_intelligence,
                    raw_content,
                    processing_metadata,
                    created_at,
                    updated_at
                ) VALUES (
                    :cache_key,
                    :source_url,
                    :source_title,
                    :confidence_score,
                    :offer_intelligence::jsonb,
                    :psychology_intelligence::jsonb,
                    :content_intelligence::jsonb,
                    :competitive_intelligence::jsonb,
                    :brand_intelligence::jsonb,
                    :scientific_intelligence::jsonb,
                    :credibility_intelligence::jsonb,
                    :market_intelligence::jsonb,
                    :emotional_transformation_intelligence::jsonb,
                    :scientific_authority_intelligence::jsonb,
                    :raw_content,
                    :processing_metadata::jsonb,
                    NOW(),
                    NOW()
                )
            """)
            
            import json
            await self.db.execute(insert_query, {
                "cache_key": cache_key,
                "source_url": url,
                "source_title": analysis_result.get("page_title", "Unknown"),
                "confidence_score": analysis_result.get("confidence_score", 0.0),
                "offer_intelligence": json.dumps(analysis_result.get("offer_intelligence", {})),
                "psychology_intelligence": json.dumps(analysis_result.get("psychology_intelligence", {})),
                "content_intelligence": json.dumps(analysis_result.get("content_intelligence", {})),
                "competitive_intelligence": json.dumps(analysis_result.get("competitive_intelligence", {})),
                "brand_intelligence": json.dumps(analysis_result.get("brand_intelligence", {})),
                "scientific_intelligence": json.dumps(analysis_result.get("scientific_intelligence", {})),
                "credibility_intelligence": json.dumps(analysis_result.get("credibility_intelligence", {})),
                "market_intelligence": json.dumps(analysis_result.get("market_intelligence", {})),
                "emotional_transformation_intelligence": json.dumps(analysis_result.get("emotional_transformation_intelligence", {})),
                "scientific_authority_intelligence": json.dumps(analysis_result.get("scientific_authority_intelligence", {})),
                "raw_content": analysis_result.get("raw_content", "")[:50000],  # Limit size
                "processing_metadata": json.dumps(analysis_result.get("amplification_metadata", {}))
            })
            
            await self.db.commit()
            
            logger.info(f"✅ Stored intelligence in global cache for {url}")
            logger.info(f"   Confidence: {analysis_result.get('confidence_score', 0.0):.2f}")
            logger.info(f"   Available for all users globally")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing in global cache: {str(e)}")
            return False
    
    async def create_campaign_source_reference(
        self,
        campaign_id: str,
        user_id: str,
        company_id: str,
        global_intelligence_id: str,
        cached_data: Dict[str, Any]
    ) -> str:
        """
        Create a lightweight reference in user's campaign to global intelligence
        This maintains separation between shared intelligence and private campaigns
        """
        try:
            # Create campaign source reference (not full intelligence record)
            insert_query = text("""
                INSERT INTO campaign_sources (
                    id,
                    campaign_id,
                    user_id,
                    company_id,
                    source_type,
                    source_url,
                    source_title,
                    global_intelligence_id,
                    confidence_score,
                    status,
                    created_at,
                    updated_at
                ) VALUES (
                    gen_random_uuid(),
                    :campaign_id::uuid,
                    :user_id::uuid,
                    :company_id::uuid,
                    'SALES_PAGE',
                    :source_url,
                    :source_title,
                    :global_intelligence_id::uuid,
                    :confidence_score,
                    'ANALYZED',
                    NOW(),
                    NOW()
                ) RETURNING id
            """)
            
            result = await self.db.execute(insert_query, {
                "campaign_id": campaign_id,
                "user_id": user_id,
                "company_id": company_id,
                "source_url": cached_data["source_url"],
                "source_title": cached_data["source_title"],
                "global_intelligence_id": global_intelligence_id,
                "confidence_score": cached_data["confidence_score"]
            })
            
            source_reference_id = result.fetchone()[0]
            await self.db.commit()
            
            logger.info(f"✅ Created campaign source reference: {source_reference_id}")
            logger.info(f"   Links to global intelligence: {global_intelligence_id}")
            logger.info(f"   Campaign: {campaign_id}")
            
            return str(source_reference_id)
            
        except Exception as e:
            logger.error(f"❌ Error creating campaign source reference: {str(e)}")
            raise
    
    async def _track_cache_hit(self, global_intelligence_id: str):
        """Track cache hit for analytics"""
        try:
            update_query = text("""
                UPDATE global_intelligence_cache 
                SET 
                    hit_count = COALESCE(hit_count, 0) + 1,
                    last_accessed = NOW()
                WHERE id = :id
            """)
            
            await self.db.execute(update_query, {"id": global_intelligence_id})
            await self.db.commit()
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to track cache hit: {str(e)}")
    
    async def get_global_cache_stats(self) -> Dict[str, Any]:
        """Get global cache performance statistics"""
        try:
            stats_query = text("""
                SELECT 
                    COUNT(*) as total_cached_pages,
                    COUNT(DISTINCT source_url) as unique_urls,
                    AVG(confidence_score) as avg_confidence,
                    SUM(COALESCE(hit_count, 0)) as total_cache_hits,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as added_this_week,
                    COUNT(CASE WHEN last_accessed >= NOW() - INTERVAL '24 hours' THEN 1 END) as accessed_today
                FROM global_intelligence_cache
            """)
            
            result = await self.db.execute(stats_query)
            stats = result.fetchone()
            
            # Calculate estimated cost savings
            total_hits = stats[3] if stats[3] else 0
            estimated_savings = total_hits * 5.90  # $5.90 saved per cache hit
            
            return {
                "total_cached_pages": stats[0],
                "unique_urls": stats[1], 
                "average_confidence": round(float(stats[2]) if stats[2] else 0, 2),
                "total_cache_hits": total_hits,
                "pages_added_this_week": stats[4],
                "pages_accessed_today": stats[5],
                "estimated_cost_savings": f"${estimated_savings:,.2f}",
                "cache_efficiency": f"{(total_hits / max(stats[0], 1)):.1f}x reuse per page"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting cache stats: {str(e)}")
            return {}
    
    async def cleanup_old_cache(self) -> int:
        """Clean up old cache entries"""
        try:
            # Remove entries older than cache duration with no recent hits
            cleanup_query = text("""
                DELETE FROM global_intelligence_cache 
                WHERE created_at < NOW() - INTERVAL ':cache_days days'
                AND (
                    last_accessed IS NULL 
                    OR last_accessed < NOW() - INTERVAL '30 days'
                )
                AND COALESCE(hit_count, 0) < 5
            """)
            
            result = await self.db.execute(cleanup_query, {
                "cache_days": self.cache_duration_days * 2  # More lenient for cleanup
            })
            
            deleted_count = result.rowcount
            await self.db.commit()
            
            logger.info(f"🧹 Cleaned up {deleted_count} old cache entries")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning cache: {str(e)}")
            return 0


# Updated Campaign Intelligence Handler
# File: src/intelligence/handlers/campaign_intelligence_handler.py

class CampaignIntelligenceHandler:
    """
    Handles campaign-specific intelligence with global cache integration
    Maintains separation between shared intelligence and private campaign data
    """
    
    def __init__(self, db: AsyncSession, user):
        self.db = db
        self.user = user
        self.global_cache = GlobalIntelligenceCache(db)
    
    async def add_source_to_campaign(
        self, 
        campaign_id: str, 
        url: str,
        analysis_type: str = "sales_page"
    ) -> Dict[str, Any]:
        """
        Add a source to campaign - checks global cache first
        This is the main entry point for the cache-first architecture
        """
        try:
            logger.info(f"🎯 Adding source to campaign: {url}")
            
            # STEP 1: Check global cache first
            cached_intelligence = await self.global_cache.check_global_cache(url)
            
            if cached_intelligence:
                # CACHE HIT: Use global intelligence
                logger.info("🎯 GLOBAL CACHE HIT: Using existing intelligence")
                
                # Create campaign source reference (not full analysis)
                source_reference_id = await self.global_cache.create_campaign_source_reference(
                    campaign_id=campaign_id,
                    user_id=self.user.id,
                    company_id=self.user.company_id,
                    global_intelligence_id=cached_intelligence["global_intelligence_id"],
                    cached_data=cached_intelligence
                )
                
                return {
                    "source_reference_id": source_reference_id,
                    "status": "added_from_cache",
                    "cache_hit": True,
                    "intelligence_data": cached_intelligence,
                    "cost_savings": "95%+ cost savings from global cache",
                    "analysis_time": "Instant (cached)",
                    "message": "Source added instantly using global intelligence cache"
                }
            
            else:
                # CACHE MISS: Perform new analysis
                logger.info("🔍 GLOBAL CACHE MISS: Performing new analysis")
                
                # Use existing analysis handler for new analysis
                from src.intelligence.handlers.analysis_handler import AnalysisHandler
                analysis_handler = AnalysisHandler(self.db, self.user)
                
                # Perform full analysis
                analysis_result = await analysis_handler.analyze_url({
                    "url": url,
                    "campaign_id": campaign_id,
                    "analysis_type": analysis_type
                })
                
                # Store in global cache for future users
                if analysis_result.get("analysis_status") == "completed":
                    # Get the full analysis data to cache globally
                    intelligence_id = analysis_result["intelligence_id"]
                    full_analysis_data = await self._get_full_analysis_data(intelligence_id)
                    
                    if full_analysis_data:
                        await self.global_cache.store_in_global_cache(full_analysis_data)
                        logger.info("✅ Analysis stored in global cache for future users")
                
                return {
                    "source_reference_id": analysis_result["intelligence_id"],
                    "status": "analyzed_and_cached",
                    "cache_hit": False,
                    "intelligence_data": analysis_result,
                    "cost_savings": "None (new analysis)",
                    "analysis_time": "2-3 minutes (full analysis)",
                    "message": "Source analyzed and added to global cache for future users"
                }
                
        except Exception as e:
            logger.error(f"❌ Error adding source to campaign: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to add source to campaign"
            }
    
    async def _get_full_analysis_data(self, intelligence_id: str) -> Optional[Dict[str, Any]]:
        """Get full analysis data for caching"""
        try:
            query = text("""
                SELECT 
                    source_url,
                    source_title,
                    confidence_score,
                    offer_intelligence,
                    psychology_intelligence,
                    content_intelligence,
                    competitive_intelligence,
                    brand_intelligence,
                    scientific_intelligence,
                    credibility_intelligence,
                    market_intelligence,
                    emotional_transformation_intelligence,
                    scientific_authority_intelligence,
                    raw_content,
                    processing_metadata
                FROM campaign_intelligence
                WHERE id = :intelligence_id
            """)
            
            result = await self.db.execute(query, {"intelligence_id": intelligence_id})
            row = result.fetchone()
            
            if row:
                return {
                    "source_url": row[0],
                    "page_title": row[1],
                    "confidence_score": row[2],
                    "offer_intelligence": row[3] or {},
                    "psychology_intelligence": row[4] or {},
                    "content_intelligence": row[5] or {},
                    "competitive_intelligence": row[6] or {},
                    "brand_intelligence": row[7] or {},
                    "scientific_intelligence": row[8] or {},
                    "credibility_intelligence": row[9] or {},
                    "market_intelligence": row[10] or {},
                    "emotional_transformation_intelligence": row[11] or {},
                    "scientific_authority_intelligence": row[12] or {},
                    "raw_content": row[13] or "",
                    "amplification_metadata": row[14] or {}
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting full analysis data: {str(e)}")
            return None
    
    async def get_campaign_sources(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get all sources for a campaign with their intelligence data"""
        try:
            query = text("""
                SELECT 
                    cs.id,
                    cs.source_url,
                    cs.source_title,
                    cs.confidence_score,
                    cs.status,
                    cs.created_at,
                    gic.offer_intelligence,
                    gic.psychology_intelligence,
                    gic.competitive_intelligence
                FROM campaign_sources cs
                LEFT JOIN global_intelligence_cache gic ON cs.global_intelligence_id = gic.id
                WHERE cs.campaign_id = :campaign_id
                ORDER BY cs.created_at DESC
            """)
            
            result = await self.db.execute(query, {"campaign_id": campaign_id})
            rows = result.fetchall()
            
            sources = []
            for row in rows:
                sources.append({
                    "source_id": str(row[0]),
                    "url": row[1],
                    "title": row[2],
                    "confidence_score": row[3],
                    "status": row[4],
                    "added_at": row[5].isoformat(),
                    "offer_intelligence": row[6] or {},
                    "psychology_intelligence": row[7] or {},
                    "competitive_intelligence": row[8] or {}
                })
            
            return sources
            
        except Exception as e:
            logger.error(f"❌ Error getting campaign sources: {str(e)}")
            return []


# Database Schema for Global Cache
# File: migrations/add_global_cache_tables.sql

"""
-- Global intelligence cache table
CREATE TABLE global_intelligence_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(64) UNIQUE NOT NULL,
    source_url TEXT NOT NULL,
    source_title VARCHAR(500),
    confidence_score FLOAT DEFAULT 0.0,
    
    -- Base intelligence data
    offer_intelligence JSONB DEFAULT '{}',
    psychology_intelligence JSONB DEFAULT '{}',
    content_intelligence JSONB DEFAULT '{}',
    competitive_intelligence JSONB DEFAULT '{}',
    brand_intelligence JSONB DEFAULT '{}',
    
    -- AI-enhanced intelligence data
    scientific_intelligence JSONB DEFAULT '{}',
    credibility_intelligence JSONB DEFAULT '{}',
    market_intelligence JSONB DEFAULT '{}',
    emotional_transformation_intelligence JSONB DEFAULT '{}',
    scientific_authority_intelligence JSONB DEFAULT '{}',
    
    -- Metadata
    raw_content TEXT,
    processing_metadata JSONB DEFAULT '{}',
    
    -- Cache metrics
    hit_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Campaign sources table (lightweight references)
CREATE TABLE campaign_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    company_id UUID NOT NULL REFERENCES companies(id),
    
    -- Source info
    source_type VARCHAR(50) NOT NULL DEFAULT 'SALES_PAGE',
    source_url TEXT NOT NULL,
    source_title VARCHAR(500),
    
    -- Reference to global cache
    global_intelligence_id UUID REFERENCES global_intelligence_cache(id),
    
    -- Status and metrics
    confidence_score FLOAT DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'PENDING',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_global_cache_key ON global_intelligence_cache(cache_key);
CREATE INDEX idx_global_cache_url ON global_intelligence_cache(source_url);
CREATE INDEX idx_global_cache_confidence ON global_intelligence_cache(confidence_score);
CREATE INDEX idx_global_cache_created ON global_intelligence_cache(created_at);
CREATE INDEX idx_global_cache_accessed ON global_intelligence_cache(last_accessed);

CREATE INDEX idx_campaign_sources_campaign ON campaign_sources(campaign_id);
CREATE INDEX idx_campaign_sources_user ON campaign_sources(user_id);
CREATE INDEX idx_campaign_sources_global ON campaign_sources(global_intelligence_id);
CREATE INDEX idx_campaign_sources_url ON campaign_sources(source_url);
"""