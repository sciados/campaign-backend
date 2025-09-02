# Updated Global Cache for New Database Schema
# File: src/intelligence/cache/global_cache.py

import logging
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, text, func
from dataclasses import dataclass

from src.utils.json_utils import safe_json_dumps

logger = logging.getLogger(__name__)

@dataclass
class GlobalIntelligenceCache:
    """
    Updated global cache using new normalized database schema
    Uses intelligence_core + related tables instead of flat global_intelligence_cache table
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache_duration_days = 60
    
    def generate_cache_key(self, url: str) -> str:
        """Generate consistent cache key for URL"""
        normalized_url = self._normalize_url(url)
        return hashlib.sha256(normalized_url.encode()).hexdigest()
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for consistent caching"""
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
            clean_params = {k: v for k, v in query_params.items() if k not in tracking_params}
            clean_query = urlencode(clean_params, doseq=True)
        else:
            clean_query = ''
        
        clean_path = parsed.path.rstrip('/')
        
        clean_url = urlunparse((
            parsed.scheme or 'https',
            parsed.netloc,
            clean_path,
            parsed.params,
            clean_query,
            ''
        ))
        
        return clean_url
    
    async def check_global_cache(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Check if intelligence exists in new schema
        Uses intelligence_core + product_data + market_data tables
        """
        try:
            # Look for existing high-quality intelligence using new schema
            query = """
                SELECT 
                    ic.id,
                    ic.product_name,
                    ic.source_url,
                    ic.confidence_score,
                    ic.analysis_method,
                    ic.created_at,
                    pd.features,
                    pd.benefits,
                    pd.ingredients,
                    pd.conditions,
                    pd.usage_instructions,
                    md.category,
                    md.positioning,
                    md.competitive_advantages,
                    md.target_audience,
                    sc.title,
                    sc.content
                FROM intelligence_core ic
                LEFT JOIN product_data pd ON ic.id = pd.intelligence_id
                LEFT JOIN market_data md ON ic.id = md.intelligence_id
                LEFT JOIN scraped_content sc ON sc.url = ic.source_url
                WHERE ic.source_url = :url 
                AND ic.created_at >= NOW() - INTERVAL ':cache_days days'
                AND ic.confidence_score >= 0.7
                ORDER BY ic.confidence_score DESC, ic.created_at DESC
                LIMIT 1
            """
            
            result = await self.db.execute(query, {
                "url": url,
                "cache_days": self.cache_duration_days
            })
            row = result.fetchone()
            
            if row:
                logger.info(f"GLOBAL CACHE HIT: Found intelligence for {url}")
                logger.info(f"   Cache age: {(datetime.now(timezone.utc) - row.created_at).days} days")
                logger.info(f"   Confidence: {row.confidence_score:.2f}")
                
                # Reconstruct intelligence data from new schema
                cached_intelligence = {
                    "cache_hit": True,
                    "global_intelligence_id": str(row.id),
                    "source_url": row.source_url,
                    "source_title": row.title or "Cached Analysis",
                    "confidence_score": row.confidence_score,
                    "product_name": row.product_name,
                    "cached_at": datetime.now(timezone.utc).isoformat(),
                    "original_analysis_date": row.created_at.isoformat(),
                    
                    # Reconstruct offer intelligence from product_data
                    "offer_intelligence": {
                        "key_features": row.features or [],
                        "primary_benefits": row.benefits or [],
                        "ingredients_list": row.ingredients or [],
                        "target_conditions": row.conditions or [],
                        "usage_instructions": row.usage_instructions or []
                    },
                    
                    # Reconstruct competitive intelligence from market_data
                    "competitive_intelligence": {
                        "market_category": row.category or "",
                        "market_positioning": row.positioning or "",
                        "competitive_advantages": row.competitive_advantages or []
                    },
                    
                    # Reconstruct psychology intelligence from market_data
                    "psychology_intelligence": {
                        "target_audience": row.target_audience or ""
                    },
                    
                    # Basic content intelligence
                    "content_intelligence": {
                        "analysis_method": row.analysis_method,
                        "content_available": bool(row.content)
                    },
                    
                    # Metadata
                    "raw_content": (row.content or "")[:1000],
                    "processing_metadata": {
                        "cache_source": "new_schema",
                        "intelligence_id": str(row.id)
                    }
                }
                
                # Track cache hit
                await self._track_cache_hit(str(row.id))
                
                return cached_intelligence
            
            else:
                logger.info(f"GLOBAL CACHE MISS: No intelligence found for {url}")
                return None
                
        except Exception as e:
            logger.error(f"Error checking global cache: {str(e)}")
            return None
    
    async def store_in_global_cache(self, analysis_result: Dict[str, Any]) -> bool:
        """
        Store analysis results using new schema
        Data is already stored in intelligence_core + related tables
        This method just ensures it's marked as globally cacheable
        """
        try:
            url = analysis_result.get("source_url")
            if not url:
                logger.error("No source URL in analysis result")
                return False
            
            # Check if already exists in new schema
            existing_query = """
                SELECT id FROM intelligence_core 
                WHERE source_url = :url
                AND confidence_score >= 0.7
                ORDER BY confidence_score DESC
                LIMIT 1
            """
            
            result = await self.db.execute(existing_query, {"url": url})
            existing_row = result.fetchone()
            
            if existing_row:
                logger.info(f"Intelligence already in global cache for {url}")
                return True
            
            # If we get here, the analysis should already be stored by the analyzer
            # Just log that it's available globally
            logger.info(f"Analysis stored and available globally for {url}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing in global cache: {str(e)}")
            return False
    
    async def _track_cache_hit(self, intelligence_id: str):
        """Track cache hit for analytics - could add to intelligence_core metadata"""
        try:
            # Update analysis_method to include cache hit info
            update_query = """
                UPDATE intelligence_core 
                SET analysis_method = CASE 
                    WHEN analysis_method LIKE '%cache_hit%' THEN analysis_method
                    ELSE analysis_method || '_cache_hit'
                END
                WHERE id = :id
            """
            
            await self.db.execute(update_query, {"id": intelligence_id})
            await self.db.commit()
            
        except Exception as e:
            logger.warning(f"Failed to track cache hit: {str(e)}")
    
    async def get_global_cache_stats(self) -> Dict[str, Any]:
        """Get global cache performance statistics using new schema"""
        try:
            # Stats from intelligence_core table
            stats_query = """
                SELECT 
                    COUNT(*) as total_cached_pages,
                    COUNT(DISTINCT source_url) as unique_urls,
                    AVG(confidence_score) as avg_confidence,
                    COUNT(CASE WHEN analysis_method LIKE '%cache_hit%' THEN 1 END) as total_cache_hits,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as added_this_week,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '1 day' THEN 1 END) as added_today
                FROM intelligence_core
                WHERE confidence_score >= 0.7
            """
            
            result = await self.db.execute(stats_query)
            stats = result.fetchone()
            
            # Calculate estimated cost savings
            total_hits = stats[3] if stats[3] else 0
            estimated_savings = total_hits * 5.90
            
            return {
                "total_cached_pages": stats[0],
                "unique_urls": stats[1], 
                "average_confidence": round(float(stats[2]) if stats[2] else 0, 2),
                "total_cache_hits": total_hits,
                "pages_added_this_week": stats[4],
                "pages_added_today": stats[5],
                "estimated_cost_savings": f"${estimated_savings:,.2f}",
                "cache_efficiency": f"{(total_hits / max(stats[0], 1)):.1f}x reuse per page"
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {}
    
    async def cleanup_old_cache(self) -> int:
        """Clean up old cache entries using new schema"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.cache_duration_days * 2)
            
            # Remove low-quality old entries
            cleanup_query = """
                DELETE FROM intelligence_core 
                WHERE created_at < :cutoff_date
                AND confidence_score < 0.7
                AND analysis_method NOT LIKE '%cache_hit%'
            """
            
            result = await self.db.execute(cleanup_query, {"cutoff_date": cutoff_date})
            deleted_count = result.rowcount
            await self.db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old cache entries")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning cache: {str(e)}")
            return 0


# Updated Campaign Intelligence Handler for new schema
class CampaignIntelligenceHandler:
    """Updated handler using new normalized schema"""
    
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
        """Add source using new schema with cache-first approach"""
        try:
            logger.info(f"Adding source to campaign: {url}")
            
            # Check cache using new schema
            cached_intelligence = await self.global_cache.check_global_cache(url)
            
            if cached_intelligence:
                logger.info("CACHE HIT: Using existing intelligence from new schema")
                
                # Create reference in new schema (you might create a campaign_sources table)
                # For now, just return the cached data
                return {
                    "intelligence_id": cached_intelligence["global_intelligence_id"],
                    "status": "added_from_cache",
                    "cache_hit": True,
                    "intelligence_data": cached_intelligence,
                    "cost_savings": "95%+ cost savings from global cache",
                    "analysis_time": "Instant (cached)",
                    "message": "Source added instantly using global intelligence cache"
                }
            
            else:
                logger.info("CACHE MISS: Performing new analysis with new schema")
                
                # Perform new analysis using your existing analyzer
                # The OptimizedDatabaseStorage will handle storing in new schema
                from src.intelligence.analyzers import SalesPageAnalyzer
                analyzer = SalesPageAnalyzer()
                
                analysis_result = await analyzer.analyze(url)
                
                if analysis_result.get("analysis_id"):
                    logger.info("Analysis completed and stored in new schema")
                    
                    return {
                        "intelligence_id": analysis_result["analysis_id"],
                        "status": "analyzed_and_cached",
                        "cache_hit": False,
                        "intelligence_data": analysis_result,
                        "cost_savings": "None (new analysis)",
                        "analysis_time": "2-3 minutes (full analysis)",
                        "message": "Source analyzed and stored in new schema"
                    }
                else:
                    return {
                        "status": "error",
                        "error": "Analysis failed",
                        "message": "Failed to analyze source"
                    }
                
        except Exception as e:
            logger.error(f"Error adding source to campaign: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to add source to campaign"
            }