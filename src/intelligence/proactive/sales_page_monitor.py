# Proactive Sales Page Analysis System
# File: src/intelligence/proactive/sales_page_monitor.py

import json
import logging
import asyncio
import aiohttp
# from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from core.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, text
from dataclasses import dataclass

from src.utils.json_utils import safe_json_dumps

logger = logging.getLogger(__name__)

@dataclass
class SalesPageSource:
    """Configuration for monitoring sales page sources"""
    name: str
    base_url: str
    monitoring_enabled: bool
    check_frequency_hours: int
    priority: int  # 1=highest, 5=lowest
    api_endpoint: Optional[str] = None
    rss_feed: Optional[str] = None
    requires_auth: bool = False

class ProactiveSalesPageMonitor:
    """
    Monitor affiliate networks and product sources for new sales pages
    Automatically analyze and enhance them before users request them
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sources = self._initialize_monitoring_sources()
        self.analysis_queue = []
        self.processed_urls = set()
    
    def _initialize_monitoring_sources(self) -> List[SalesPageSource]:
        """Initialize sources to monitor for new sales pages"""
        return [
            # Major affiliate networks
            SalesPageSource(
                name="WarriorPlus",
                base_url="https://warriorplus.com",
                monitoring_enabled=True,
                check_frequency_hours=6,
                priority=1
            ),
            SalesPageSource(
                name="JVZoo",
                base_url="https://www.jvzoo.com",
                monitoring_enabled=True,
                check_frequency_hours=6,
                priority=1
            ),
            # Product discovery sources
            SalesPageSource(
                name="Product Hunt",
                base_url="https://www.producthunt.com",
                monitoring_enabled=True,
                check_frequency_hours=12,
                priority=2,
                rss_feed="https://www.producthunt.com/feed"
            ),
            # E-commerce platforms
            SalesPageSource(
                name="Shopify Apps",
                base_url="https://apps.shopify.com",
                monitoring_enabled=True,
                check_frequency_hours=24,
                priority=3
            ),
            # Custom sources (your manual additions)
            SalesPageSource(
                name="Manual Queue",
                base_url="internal",
                monitoring_enabled=True,
                check_frequency_hours=1,
                priority=1
            )
        ]
    
    async def discover_new_sales_pages(self, source: SalesPageSource, limit: int = 50) -> List[str]:
        """Discover new sales pages from a specific source"""
        try:
            logger.info(f"🔍 Discovering new sales pages from {source.name}")
            
            if source.name == "Product Hunt":
                return await self._discover_producthunt_pages(source, limit)
            elif source.name == "Manual Queue":
                return await self._get_manual_queue_pages(limit)
            else:
                return await self._discover_generic_pages(source, limit)
                
        except Exception as e:
            logger.error(f"❌ Error discovering pages from {source.name}: {str(e)}")
            return []
    
    async def _discover_producthunt_pages(self, source: SalesPageSource, limit: int) -> List[str]:
        """Discover trending products from Product Hunt"""
        try:
            # Use Product Hunt API or RSS feed
            # Focus on products with landing pages suitable for affiliate promotion
            
            async with aiohttp.ClientSession() as session:
                # Example RSS parsing (simplified)
                if source.rss_feed:
                    async with session.get(source.rss_feed) as response:
                        if response.status == 200:
                            # Parse RSS and extract product URLs
                            # Filter for products with affiliate potential
                            pass
            
            # Mock data for demonstration
            new_urls = [
                "https://newproduct1.com",
                "https://trendingapp2.com",
                "https://hotservice3.com"
            ]
            
            return new_urls[:limit]
            
        except Exception as e:
            logger.error(f"❌ Product Hunt discovery error: {str(e)}")
            return []
    
    async def _discover_generic_pages(self, source: SalesPageSource, limit: int) -> List[str]:
        """Discover pages from generic sources"""
        try:
            # Generic discovery logic for other sources
            logger.info(f"🔍 Generic discovery for {source.name}")
            
            # This would be customized based on each source's API/structure
            # For now, returning empty list as placeholder
            return []
            
        except Exception as e:
            logger.error(f"❌ Generic discovery error for {source.name}: {str(e)}")
            return []
    
    async def _get_manual_queue_pages(self, limit: int) -> List[str]:
        """Get manually queued pages for analysis"""
        try:
            # FIXED: Use PostgreSQL positional parameters
            query = text("""
                SELECT url FROM proactive_analysis_queue 
                WHERE status = 'pending' 
                AND priority >= 1
                ORDER BY priority ASC, created_at ASC
                LIMIT $1
            """)
            
            result = await self.db.execute(query, [limit])
            rows = result.fetchall()
            
            urls = [row[0] for row in rows]
            logger.info(f"✅ Retrieved {len(urls)} URLs from manual queue")
            
            return urls
            
        except Exception as e:
            logger.error(f"❌ Manual queue error: {str(e)}")
            return []
    
async def queue_url_for_proactive_analysis(
    self, 
    url: str, 
    priority: int = 3,
    source: str = "manual",
    metadata: Optional[Dict] = None
) -> bool:
    """Queue a URL for proactive analysis - Updated for new schema"""
    try:
        # UPDATED: Check new intelligence_core table instead of campaignintelligence
        existing_check = text("""
            SELECT id FROM intelligence_core 
            WHERE source_url = $1 
            AND created_at >= NOW() - INTERVAL '7 days'
            AND confidence_score >= 0.7
            LIMIT 1
        """)
        
        result = await self.db.execute(existing_check, [url])
        if result.fetchone():
            logger.info(f"URL already analyzed recently: {url}")
            return False
        
        # Add to proactive queue (this table structure remains the same)
        insert_query = text("""
            INSERT INTO proactive_analysis_queue 
            (url, priority, source, metadata, status, created_at)
            VALUES ($1, $2, $3, $4, 'pending', NOW())
            ON CONFLICT (url) DO UPDATE SET
                priority = GREATEST(proactive_analysis_queue.priority, $2),
                updated_at = NOW()
        """)
        
        await self.db.execute(insert_query, [
            url,
            priority,
            source,
            safe_json_dumps(metadata or {})
        ])
        
        await self.db.commit()
        
        logger.info(f"Queued URL for proactive analysis: {url} (priority: {priority})")
        return True
        
    except Exception as e:
        logger.error(f"Error queuing URL: {str(e)}")
        return False

async def get_proactive_analysis_stats(self) -> Dict[str, Any]:
    """Get statistics about proactive analysis performance - Updated for new schema"""
    try:
        # Queue stats remain the same
        stats_query = text("""
            SELECT 
                COUNT(*) as total_queued,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as added_today,
                COUNT(CASE WHEN updated_at >= NOW() - INTERVAL '24 hours' AND status = 'completed' THEN 1 END) as completed_today
            FROM proactive_analysis_queue
        """)
        
        result = await self.db.execute(stats_query)
        stats = result.fetchone()
        
        if not stats:
            return {}
        
        # UPDATED: Get cache hit rate using new schema
        cache_stats_query = text("""
            SELECT 
                COUNT(*) as total_user_requests,
                COUNT(CASE WHEN analysis_method LIKE '%cache%' OR analysis_method LIKE '%shared%' THEN 1 END) as cache_hits
            FROM intelligence_core ic
            WHERE EXISTS (
                SELECT 1 FROM proactive_analysis_queue paq 
                WHERE paq.url = ic.source_url AND paq.status = 'completed'
            )
            AND ic.created_at >= NOW() - INTERVAL '30 days'
        """)
        
        cache_result = await self.db.execute(cache_stats_query)
        cache_stats = cache_result.fetchone()
        
        cache_hit_rate = 0
        if cache_stats and cache_stats[0] > 0:
            cache_hit_rate = (cache_stats[1] / cache_stats[0]) * 100
        
        return {
            "queue_status": {
                "total_queued": stats[0],
                "pending": stats[1],
                "processing": stats[2],
                "completed": stats[3],
                "failed": stats[4]
            },
            "daily_activity": {
                "added_today": stats[5],
                "completed_today": stats[6]
            },
            "cache_performance": {
                "total_user_requests": cache_stats[0] if cache_stats else 0,
                "cache_hits": cache_stats[1] if cache_stats else 0,
                "cache_hit_rate": round(cache_hit_rate, 1)
            },
            "efficiency_metrics": {
                "success_rate": round((stats[3] / max(stats[0], 1)) * 100, 1),
                "processing_speed": "Real-time" if stats[2] == 0 else f"{stats[2]} in queue"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting proactive analysis stats: {str(e)}")
        return {}

async def _perform_proactive_analysis(self, url: str) -> bool:
    """Perform full analysis and enhancement for a URL - Updated for new schema"""
    try:
        # Use the new OptimizedDatabaseStorage and analyzers
        from src.intelligence.analyzers import SalesPageAnalyzer
        
        # Initialize the analyzer with new schema support
        analyzer = SalesPageAnalyzer()
        
        # Perform analysis using new schema
        result = await analyzer.analyze(url)
        
        # Check if analysis was successful using new response structure
        if result.get("analysis_id") and result.get("confidence_score", 0) > 0.5:
            logger.info(f"Proactive analysis completed for: {url}")
            return True
        else:
            logger.error(f"Proactive analysis failed for: {url}")
            return False
            
    except Exception as e:
        logger.error(f"Error in proactive analysis: {str(e)}")
        return False
    
    async def _get_or_create_system_user(self):
        """Get or create system user for proactive analysis"""
        try:
            # Check if system user exists
            # FIXED: Use PostgreSQL positional parameters
            query = text("SELECT * FROM users WHERE email = $1 LIMIT 1")
            result = await self.db.execute(query, ["system@proactive.internal"])
            user_row = result.fetchone()
            
            if user_row:
                # Convert row to user object (simplified)
                return user_row
            
            # Create system user if doesn't exist
            # This would use your actual User model
            # For now, returning a mock structure
            return {
                "id": "system-user-id",
                "company_id": "system-company-id",
                "email": "system@proactive.internal"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting system user: {str(e)}")
            raise
    
    async def _get_or_create_system_campaign(self, system_user):
        """Get or create system campaign for proactive analysis"""
        try:
            # Similar to system user, get or create system campaign
            return {
                "id": "system-campaign-id",
                "title": "Proactive Analysis Campaign",
                "user_id": system_user["id"],
                "company_id": system_user["company_id"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting system campaign: {str(e)}")
            raise
    
    async def _update_queue_status(self, url: str, status: str):
        """Update the status of a URL in the queue"""
        try:
            # FIXED: Use PostgreSQL positional parameters
            update_query = text("""
                UPDATE proactive_analysis_queue 
                SET status = $2, updated_at = NOW()
                WHERE url = $1
            """)
            
            await self.db.execute(update_query, [url, status])
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"❌ Error updating queue status: {str(e)}")
    
    async def get_proactive_analysis_stats(self) -> Dict[str, Any]:
        """Get statistics about proactive analysis performance"""
        try:
            stats_query = text("""
                SELECT 
                    COUNT(*) as total_queued,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                    COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as added_today,
                    COUNT(CASE WHEN updated_at >= NOW() - INTERVAL '24 hours' AND status = 'completed' THEN 1 END) as completed_today
                FROM proactive_analysis_queue
            """)
            
            result = await self.db.execute(stats_query)
            stats = result.fetchone()
            
            if not stats:
                return {}
            
            # Get cache hit rate for proactively analyzed URLs
            cache_stats_query = text("""
                SELECT 
                    COUNT(*) as total_user_requests,
                    COUNT(CASE WHEN processing_metadata->>'shared_from_cache' = 'true' THEN 1 END) as cache_hits
                FROM intelligence_core ci
                WHERE EXISTS (
                    SELECT 1 FROM proactive_analysis_queue paq 
                    WHERE paq.url = ci.source_url AND paq.status = 'completed'
                )
                AND ci.created_at >= NOW() - INTERVAL '30 days'
            """)
            
            cache_result = await self.db.execute(cache_stats_query)
            cache_stats = cache_result.fetchone()
            
            cache_hit_rate = 0
            if cache_stats and cache_stats[0] > 0:
                cache_hit_rate = (cache_stats[1] / cache_stats[0]) * 100
            
            return {
                "queue_status": {
                    "total_queued": stats[0],
                    "pending": stats[1],
                    "processing": stats[2],
                    "completed": stats[3],
                    "failed": stats[4]
                },
                "daily_activity": {
                    "added_today": stats[5],
                    "completed_today": stats[6]
                },
                "cache_performance": {
                    "total_user_requests": cache_stats[0] if cache_stats else 0,
                    "cache_hits": cache_stats[1] if cache_stats else 0,
                    "cache_hit_rate": round(cache_hit_rate, 1)
                },
                "efficiency_metrics": {
                    "success_rate": round((stats[3] / max(stats[0], 1)) * 100, 1),
                    "processing_speed": "Real-time" if stats[2] == 0 else f"{stats[2]} in queue"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting proactive analysis stats: {str(e)}")
            return {}