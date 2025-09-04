# Shared Intelligence Cache System - FIXED FOR NEW SCHEMA
# File: src/intelligence/cache/shared_intelligence.py

import logging
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, text
from sqlalchemy.orm import selectinload

# FIXED IMPORTS - Use new schema models
from src.models.intelligence import IntelligenceCore, AnalysisStatus  # FIXED: Use IntelligenceCore instead of CampaignIntelligence
from src.models.user import User
from src.models.campaign import Campaign
from src.core.crud.intelligence_crud import intelligence_crud

logger = logging.getLogger(__name__)

class SharedIntelligenceCache:
    """
    Cache and share intelligence analysis across all users for the same URLs
    Updated for new normalized database schema
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache_duration_days = 30
        self.min_confidence_threshold = 0.7
    
    def generate_url_hash(self, url: str) -> str:
        """Generate consistent hash for URL normalization"""
        normalized_url = url.lower().rstrip('/')
        return hashlib.sha256(normalized_url.encode()).hexdigest()
    
    async def check_existing_intelligence(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Check if we already have high-quality intelligence for this URL
        Updated to use new normalized schema
        """
        try:
            # Look for existing high-quality analysis in new schema
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
                AND ic.confidence_score >= :min_confidence
                AND ic.created_at >= :cutoff_date
                ORDER BY ic.confidence_score DESC
                LIMIT 1
            """
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.cache_duration_days)
            
            result = await self.db.execute(text(query), {
                "url": url,
                "min_confidence": self.min_confidence_threshold,
                "cutoff_date": cutoff_date
            })
            
            row = result.fetchone()
            
            if row:
                logger.info(f"CACHE HIT: Found existing intelligence for {url}")
                logger.info(f"   Confidence: {row.confidence_score:.2f}")
                
                # Reconstruct intelligence data from normalized schema
                cached_data = {
                    "cache_hit": True,
                    "source_intelligence_id": str(row.id),
                    "confidence_score": row.confidence_score,
                    "page_title": row.title or "Cached Analysis",
                    "source_url": row.source_url,
                    "product_name": row.product_name,
                    
                    # Reconstruct offer intelligence
                    "offer_intelligence": {
                        "key_features": row.features or [],
                        "primary_benefits": row.benefits or [],
                        "ingredients_list": row.ingredients or [],
                        "target_conditions": row.conditions or [],
                        "usage_instructions": row.usage_instructions or []
                    },
                    
                    # Reconstruct competitive intelligence
                    "competitive_intelligence": {
                        "market_category": row.category or "",
                        "market_positioning": row.positioning or "",
                        "competitive_advantages": row.competitive_advantages or []
                    },
                    
                    # Reconstruct psychology intelligence
                    "psychology_intelligence": {
                        "target_audience": row.target_audience or ""
                    },
                    
                    # Metadata
                    "analysis_method": row.analysis_method,
                    "raw_content": (row.content or "")[:1000],
                    "cached_at": datetime.now(timezone.utc),
                    "original_analysis_date": row.created_at.isoformat()
                }
                
                # Get linked research if available
                research_links = await self._get_research_links(str(row.id))
                if research_links:
                    cached_data["research_enhanced"] = True
                    cached_data["research_links"] = research_links
                
                return cached_data
            
            else:
                logger.info(f"CACHE MISS: No existing intelligence found for {url}")
                return None
                
        except Exception as e:
            logger.error(f"Error checking existing intelligence: {str(e)}")
            return None
    
    async def _get_research_links(self, intelligence_id: str) -> List[Dict[str, Any]]:
        """Get research links for an intelligence analysis"""
        try:
            query = """
                SELECT kb.id, kb.research_type, ir.relevance_score,
                       LEFT(kb.content, 200) as content_preview
                FROM knowledge_base kb
                JOIN intelligence_research ir ON kb.id = ir.research_id
                WHERE ir.intelligence_id = :intelligence_id
                ORDER BY ir.relevance_score DESC
                LIMIT 5
            """
            
            result = await self.db.execute(text(query), {"intelligence_id": intelligence_id})
            rows = result.fetchall()
            
            return [
                {
                    "research_id": str(row.id),
                    "research_type": row.research_type,
                    "relevance_score": row.relevance_score,
                    "preview": row.content_preview + "..."
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Error getting research links: {str(e)}")
            return []
    
    async def create_user_intelligence_reference(
        self, 
        user_campaign_id: str,
        user_id: str,
        company_id: str,
        source_intelligence_id: str,
        cached_data: Dict[str, Any]
    ) -> str:
        """
        Create new intelligence records for user that reference cached data
        Using new normalized schema
        """
        try:
            # Use the intelligence_crud to create the intelligence
            analysis_data = {
                "product_name": cached_data["product_name"],
                "source_url": cached_data["source_url"],
                "confidence_score": cached_data["confidence_score"],
                "analysis_method": f"shared_cache_from_{source_intelligence_id}",
                "offer_intelligence": cached_data.get("offer_intelligence", {}),
                "competitive_intelligence": cached_data.get("competitive_intelligence", {}),
                "psychology_intelligence": cached_data.get("psychology_intelligence", {})
            }
            
            # Copy research links if they exist
            if cached_data.get("research_links"):
                analysis_data["research_links"] = cached_data["research_links"]
            
            new_analysis_id = await intelligence_crud.create_intelligence(self.db, analysis_data)
            
            logger.info(f"Created user intelligence reference: {new_analysis_id}")
            logger.info(f"Cost savings: 90%+ (used cached analysis)")
            
            return new_analysis_id
            
        except Exception as e:
            logger.error(f"Error creating user intelligence reference: {str(e)}")
            await self.db.rollback()
            raise
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get statistics about cache usage and savings using new schema"""
        try:
            # Total intelligence records
            total_query = "SELECT COUNT(*) FROM intelligence_core"
            total_result = await self.db.execute(text(total_query))
            total_analyses = total_result.scalar()
            
            # Cached/shared analyses (those with shared_cache in analysis_method)
            cached_query = """
                SELECT COUNT(*) FROM intelligence_core 
                WHERE analysis_method LIKE '%shared_cache%'
            """
            cached_result = await self.db.execute(text(cached_query))
            cached_analyses = cached_result.scalar()
            
            # Unique URLs analyzed
            unique_urls_query = "SELECT COUNT(DISTINCT source_url) FROM intelligence_core"
            unique_result = await self.db.execute(text(unique_urls_query))
            unique_urls = unique_result.scalar()
            
            # Calculate savings
            cache_hit_rate = (cached_analyses / total_analyses * 100) if total_analyses > 0 else 0
            estimated_cost_savings = cached_analyses * 5
            
            return {
                "total_analyses": total_analyses,
                "cached_analyses": cached_analyses,
                "unique_urls": unique_urls,
                "cache_hit_rate_percent": round(cache_hit_rate, 2),
                "estimated_cost_savings": estimated_cost_savings,
                "analysis_reuse_ratio": round(total_analyses / unique_urls, 2) if unique_urls > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting cache statistics: {str(e)}")
            return {}
    
    async def cleanup_old_cache(self):
        """Clean up old cached intelligence data using new schema"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.cache_duration_days)
            
            # Clean up old intelligence that isn't referenced
            cleanup_query = """
                WITH referenced_intelligence AS (
                    SELECT DISTINCT ic2.id
                    FROM intelligence_core ic2
                    WHERE ic2.analysis_method LIKE '%shared_cache_from_%'
                    AND ic2.created_at > :recent_cutoff
                ),
                old_unreferenced AS (
                    SELECT ic.id
                    FROM intelligence_core ic
                    WHERE ic.created_at < :cutoff_date
                    AND ic.confidence_score < :min_confidence
                    AND ic.id NOT IN (SELECT id FROM referenced_intelligence)
                )
                DELETE FROM intelligence_core 
                WHERE id IN (SELECT id FROM old_unreferenced)
            """
            
            result = await self.db.execute(text(cleanup_query), {
                "cutoff_date": cutoff_date,
                "min_confidence": self.min_confidence_threshold,
                "recent_cutoff": datetime.now(timezone.utc) - timedelta(days=7)
            })
            
            await self.db.commit()
            
            deleted_count = result.rowcount
            logger.info(f"Cleaned up {deleted_count} old cache entries")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {str(e)}")
            await self.db.rollback()
            return 0

class AnalysisHandler:
    """Analysis Handler with shared intelligence caching - FIXED"""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
        self.shared_cache = SharedIntelligenceCache(db)
    
    async def analyze_url_with_cache(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        URL analysis with shared intelligence caching
        Main business logic with cache-first approach
        """
        url = str(request_data.get('url'))
        campaign_id = request_data.get('campaign_id')
        analysis_type = request_data.get('analysis_type', 'sales_page')
        
        logger.info(f"🎯 Starting analysis for: {url}")
        
        # Verify campaign ownership
        campaign = await self._verify_campaign_access(campaign_id)
        
        # STEP 1: Check for existing cached intelligence
        logger.info("🔍 Checking for cached intelligence...")
        cached_intelligence = await self.shared_cache.check_existing_intelligence(url)
        
        if cached_intelligence:
            # CACHE HIT: Use existing analysis
            logger.info("🎯 CACHE HIT: Using existing intelligence analysis")
            
            try:
                # Create user-specific intelligence record referencing cached data
                user_intelligence_id = await self.shared_cache.create_user_intelligence_reference(
                    user_campaign_id=campaign_id,
                    user_id=str(self.user.id),
                    company_id=str(self.user.company_id),
                    source_intelligence_id=cached_intelligence["source_intelligence_id"],
                    cached_data=cached_intelligence
                )
                
                # Update campaign counters
                await self._update_campaign_counters(campaign_id)
                
                # Return cached results
                return {
                    "intelligence_id": user_intelligence_id,
                    "analysis_status": "completed",
                    "confidence_score": cached_intelligence["confidence_score"],
                    "offer_intelligence": cached_intelligence["offer_intelligence"],
                    "psychology_intelligence": cached_intelligence["psychology_intelligence"],
                    "competitive_opportunities": self._extract_competitive_opportunities(cached_intelligence),
                    "campaign_suggestions": [
                        "✅ Used cached analysis (90%+ cost savings)",
                        "✅ High-quality intelligence data available",
                        "✅ Ready for content generation"
                    ],
                    "cache_info": {
                        "cache_hit": True,
                        "original_analysis_date": cached_intelligence["original_analysis_date"],
                        "cost_savings": "90%+",
                        "analysis_age_days": (datetime.now(timezone.utc) - datetime.fromisoformat(cached_intelligence["original_analysis_date"])).days
                    }
                }
                
            except Exception as cache_error:
                logger.error(f"❌ Cache utilization failed: {str(cache_error)}")
                # Fall through to new analysis
        
        # STEP 2: CACHE MISS - Perform new analysis
        logger.info("🔍 CACHE MISS: Performing new intelligence analysis...")
        
        # Create intelligence record using new schema
        try:
            analysis_data = {
                "product_name": f"Analysis for {url}",
                "source_url": url,
                "confidence_score": 0.0,  # Will be updated after analysis
                "analysis_method": "fresh_analysis"
            }
            
            intelligence_id = await intelligence_crud.create_intelligence(self.db, analysis_data)
            
            # Perform full analysis (base + amplification)
            base_analysis_result = await self._perform_base_analysis(url, analysis_type)
            final_analysis_result = await self._perform_amplification(url, base_analysis_result)
            
            # Update intelligence with results
            await intelligence_crud.update_intelligence(self.db, intelligence_id, final_analysis_result)
            
            # Update campaign counters
            await self._update_campaign_counters(campaign_id)
            
            logger.info("✅ NEW ANALYSIS: Created fresh intelligence (available for future caching)")
            
            # Prepare response
            return self._prepare_analysis_response_with_cache_info(
                intelligence_id, 
                final_analysis_result, 
                cache_hit=False
            )
            
        except Exception as e:
            logger.error(f"❌ Analysis failed for {url}: {str(e)}")
            return self._prepare_failure_response(url, e)
    
    def _prepare_analysis_response_with_cache_info(
        self, 
        intelligence_id: str,  # FIXED: Use intelligence_id string instead of CampaignIntelligence object
        analysis_result: Dict[str, Any],
        cache_hit: bool = False
    ) -> Dict[str, Any]:
        """Prepare analysis response with cache information - FIXED"""
        
        base_response = {
            "intelligence_id": intelligence_id,
            "analysis_status": "completed",
            "confidence_score": analysis_result.get("confidence_score", 0.0),
            "offer_intelligence": analysis_result.get("offer_intelligence", {}),
            "psychology_intelligence": analysis_result.get("psychology_intelligence", {}),
            "competitive_opportunities": analysis_result.get("competitive_intelligence", {}),
            "campaign_suggestions": []
        }
        
        # Add cache information
        base_response["cache_info"] = {
            "cache_hit": cache_hit,
            "analysis_method": "cached" if cache_hit else "fresh_analysis",
            "available_for_sharing": not cache_hit,  # Fresh analyses can be shared
            "cost_efficiency": "high" if cache_hit else "standard"
        }
        
        if cache_hit:
            base_response["campaign_suggestions"].append("✅ 90%+ cost savings from cached analysis")
        else:
            base_response["campaign_suggestions"].append("✅ Fresh analysis created (available for future users)")
        
        return base_response
    
    async def _verify_campaign_access(self, campaign_id: str) -> Campaign:
        """Verify user has access to campaign"""
        try:
            result = await self.db.execute(
                select(Campaign).where(
                    and_(
                        Campaign.id == campaign_id,
                        Campaign.user_id == self.user.id
                    )
                )
            )
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found or access denied")
            
            return campaign
            
        except Exception as e:
            logger.error(f"Campaign access verification failed: {e}")
            raise
    
    async def _update_campaign_counters(self, campaign_id: str):
        """Update campaign analysis counters"""
        try:
            await self.db.execute(
                text("""
                    UPDATE campaigns 
                    SET analysis_count = COALESCE(analysis_count, 0) + 1,
                        last_analysis_at = NOW()
                    WHERE id = :campaign_id
                """),
                {"campaign_id": campaign_id}
            )
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating campaign counters: {e}")
    
    def _extract_competitive_opportunities(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract competitive opportunities from intelligence data"""
        competitive_intel = intelligence_data.get("competitive_intelligence", {})
        
        return {
            "market_gaps": competitive_intel.get("competitive_advantages", []),
            "positioning_opportunities": [competitive_intel.get("market_positioning", "")],
            "differentiation_factors": competitive_intel.get("competitive_advantages", [])
        }
    
    async def _perform_base_analysis(self, url: str, analysis_type: str) -> Dict[str, Any]:
        """Placeholder for base analysis logic"""
        # This would contain the actual analysis logic
        return {
            "product_name": f"Product from {url}",
            "confidence_score": 0.8,
            "offer_intelligence": {
                "key_features": ["Feature 1", "Feature 2"],
                "primary_benefits": ["Benefit 1", "Benefit 2"]
            },
            "competitive_intelligence": {
                "market_category": "Health & Wellness",
                "competitive_advantages": ["Advantage 1"]
            },
            "psychology_intelligence": {
                "target_audience": "Health-conscious consumers"
            }
        }
    
    async def _perform_amplification(self, url: str, base_result: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for amplification logic"""
        # This would enhance the base analysis
        base_result["analysis_method"] = "base_plus_amplification"
        base_result["confidence_score"] = min(base_result["confidence_score"] + 0.1, 1.0)
        return base_result
    
    def _prepare_failure_response(self, url: str, error: Exception) -> Dict[str, Any]:
        """Prepare failure response"""
        return {
            "intelligence_id": None,
            "analysis_status": "failed",
            "error": str(error),
            "url": url,
            "cache_info": {
                "cache_hit": False,
                "analysis_method": "failed",
                "available_for_sharing": False,
                "cost_efficiency": "none"
            }
        }

# Cache Management Commands
class CacheManager:
    """Manage shared intelligence cache operations"""
    
    def __init__(self, db: AsyncSession):
        self.shared_cache = SharedIntelligenceCache(db)
    
    async def get_cache_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics for admin dashboard"""
        stats = await self.shared_cache.get_cache_statistics()
        
        return {
            "cache_performance": {
                "total_analyses": stats.get("total_analyses", 0),
                "cached_analyses": stats.get("cached_analyses", 0),
                "cache_hit_rate": f"{stats.get('cache_hit_rate_percent', 0):.1f}%",
                "unique_urls": stats.get("unique_urls", 0),
                "reuse_ratio": f"{stats.get('analysis_reuse_ratio', 0):.1f}x"
            },
            "cost_savings": {
                "estimated_monthly_savings": f"${stats.get('estimated_cost_savings', 0):.2f}",
                "efficiency_improvement": f"{stats.get('cache_hit_rate_percent', 0):.1f}%"
            },
            "recommendations": self._get_cache_recommendations(stats)
        }
    
    def _get_cache_recommendations(self, stats: Dict) -> List[str]:
        """Generate cache optimization recommendations"""
        recommendations = []
        
        hit_rate = stats.get('cache_hit_rate_percent', 0)
        
        if hit_rate < 20:
            recommendations.append("Consider promoting popular URLs to increase cache hit rate")
        elif hit_rate < 50:
            recommendations.append("Good cache performance - monitor for optimization opportunities")
        else:
            recommendations.append("Excellent cache performance - significant cost savings achieved")
        
        reuse_ratio = stats.get('analysis_reuse_ratio', 0)
        if reuse_ratio > 3:
            recommendations.append("High URL reuse detected - cache is providing excellent value")
        
        return recommendations
    
    async def cleanup_cache(self) -> Dict[str, Any]:
        """Clean up old cache entries"""
        deleted_count = await self.shared_cache.cleanup_old_cache()
        
        return {
            "cleanup_completed": True,
            "entries_removed": deleted_count,
            "status": "success"
        }