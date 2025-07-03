# Shared Intelligence Cache System
# File: src/intelligence/cache/shared_intelligence.py

import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, text
from sqlalchemy.orm import selectinload

from src.models.intelligence import CampaignIntelligence, AnalysisStatus
from src.models.campaign import Campaign

logger = logging.getLogger(__name__)

class SharedIntelligenceCache:
    """
    Cache and share intelligence analysis across all users for the same URLs
    One analysis → Multiple users benefit
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache_duration_days = 30  # How long to keep cached intelligence
        self.min_confidence_threshold = 0.7  # Only cache high-quality analyses
    
    def generate_url_hash(self, url: str) -> str:
        """Generate consistent hash for URL normalization"""
        # Normalize URL (remove trailing slashes, convert to lowercase, etc.)
        normalized_url = url.lower().rstrip('/')
        
        # Remove common tracking parameters
        tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'fbclid', 'gclid']
        # You might want to implement URL cleaning here
        
        return hashlib.sha256(normalized_url.encode()).hexdigest()
    
    async def check_existing_intelligence(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Check if we already have high-quality intelligence for this URL
        Returns the cached intelligence data if available
        """
        try:
            url_hash = self.generate_url_hash(url)
            
            # Look for existing high-quality analysis
            query = select(CampaignIntelligence).where(
                and_(
                    CampaignIntelligence.source_url == url,
                    CampaignIntelligence.analysis_status == AnalysisStatus.COMPLETED,
                    CampaignIntelligence.confidence_score >= self.min_confidence_threshold,
                    CampaignIntelligence.created_at >= datetime.utcnow() - timedelta(days=self.cache_duration_days)
                )
            ).order_by(CampaignIntelligence.confidence_score.desc()).limit(1)
            
            result = await self.db.execute(query)
            existing_intelligence = result.scalar_one_or_none()
            
            if existing_intelligence:
                logger.info(f"🎯 CACHE HIT: Found existing intelligence for {url}")
                logger.info(f"   Confidence: {existing_intelligence.confidence_score:.2f}")
                logger.info(f"   Age: {(datetime.utcnow() - existing_intelligence.created_at).days} days")
                
                # Return the cached intelligence data
                cached_data = {
                    "cache_hit": True,
                    "source_intelligence_id": str(existing_intelligence.id),
                    "confidence_score": existing_intelligence.confidence_score,
                    "page_title": existing_intelligence.source_title,
                    "source_url": existing_intelligence.source_url,
                    
                    # Base intelligence
                    "offer_intelligence": existing_intelligence.offer_intelligence,
                    "psychology_intelligence": existing_intelligence.psychology_intelligence,
                    "content_intelligence": existing_intelligence.content_intelligence,
                    "competitive_intelligence": existing_intelligence.competitive_intelligence,
                    "brand_intelligence": existing_intelligence.brand_intelligence,
                    
                    # AI-enhanced intelligence
                    "scientific_intelligence": existing_intelligence.scientific_intelligence,
                    "credibility_intelligence": existing_intelligence.credibility_intelligence,
                    "market_intelligence": existing_intelligence.market_intelligence,
                    "emotional_transformation_intelligence": existing_intelligence.emotional_transformation_intelligence,
                    "scientific_authority_intelligence": existing_intelligence.scientific_authority_intelligence,
                    
                    # Metadata
                    "processing_metadata": existing_intelligence.processing_metadata,
                    "raw_content": existing_intelligence.raw_content,
                    "cached_at": datetime.utcnow().isoformat(),
                    "original_analysis_date": existing_intelligence.created_at.isoformat()
                }
                
                return cached_data
            
            else:
                logger.info(f"🔍 CACHE MISS: No existing intelligence found for {url}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error checking existing intelligence: {str(e)}")
            return None
    
    async def create_user_intelligence_reference(
        self, 
        user_campaign_id: str,
        user_id: str,
        company_id: str,
        source_intelligence_id: str,
        cached_data: Dict[str, Any]
    ) -> str:
        """
        Create a new intelligence record for the user that references the cached data
        This allows each user to have their own record while sharing the underlying analysis
        """
        try:
            from src.models.intelligence import IntelligenceSourceType
            
            # Create new intelligence record for this user
            user_intelligence = CampaignIntelligence(
                source_url=cached_data["source_url"],
                source_type=IntelligenceSourceType.SALES_PAGE,
                source_title=cached_data["page_title"],
                campaign_id=user_campaign_id,
                user_id=user_id,
                company_id=company_id,
                analysis_status=AnalysisStatus.COMPLETED,
                
                # Copy all the intelligence data
                offer_intelligence=cached_data["offer_intelligence"],
                psychology_intelligence=cached_data["psychology_intelligence"],
                content_intelligence=cached_data["content_intelligence"],
                competitive_intelligence=cached_data["competitive_intelligence"],
                brand_intelligence=cached_data["brand_intelligence"],
                
                # Copy AI-enhanced intelligence
                scientific_intelligence=cached_data["scientific_intelligence"],
                credibility_intelligence=cached_data["credibility_intelligence"],
                market_intelligence=cached_data["market_intelligence"],
                emotional_transformation_intelligence=cached_data["emotional_transformation_intelligence"],
                scientific_authority_intelligence=cached_data["scientific_authority_intelligence"],
                
                # Metadata
                confidence_score=cached_data["confidence_score"],
                raw_content=cached_data["raw_content"],
                processing_metadata={
                    **cached_data["processing_metadata"],
                    "shared_from_cache": True,
                    "source_intelligence_id": source_intelligence_id,
                    "cache_utilized_at": datetime.utcnow().isoformat(),
                    "cost_savings": "90%+",
                    "analysis_method": "shared_cache"
                }
            )
            
            self.db.add(user_intelligence)
            await self.db.commit()
            await self.db.refresh(user_intelligence)
            
            logger.info(f"✅ Created user intelligence reference: {user_intelligence.id}")
            logger.info(f"💰 Cost savings: 90%+ (used cached analysis)")
            
            return str(user_intelligence.id)
            
        except Exception as e:
            logger.error(f"❌ Error creating user intelligence reference: {str(e)}")
            raise
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get statistics about cache usage and savings"""
        try:
            # Total intelligence records
            total_query = select(func.count(CampaignIntelligence.id))
            total_result = await self.db.execute(total_query)
            total_analyses = total_result.scalar()
            
            # Cached/shared analyses
            cached_query = select(func.count(CampaignIntelligence.id)).where(
                CampaignIntelligence.processing_metadata.op('?')('shared_from_cache')
            )
            cached_result = await self.db.execute(cached_query)
            cached_analyses = cached_result.scalar()
            
            # Unique URLs analyzed
            unique_urls_query = select(func.count(func.distinct(CampaignIntelligence.source_url)))
            unique_result = await self.db.execute(unique_urls_query)
            unique_urls = unique_result.scalar()
            
            # Calculate savings
            cache_hit_rate = (cached_analyses / total_analyses * 100) if total_analyses > 0 else 0
            estimated_cost_savings = cached_analyses * 5  # Assume $5 saved per cached analysis
            
            return {
                "total_analyses": total_analyses,
                "cached_analyses": cached_analyses,
                "unique_urls": unique_urls,
                "cache_hit_rate_percent": round(cache_hit_rate, 2),
                "estimated_cost_savings": estimated_cost_savings,
                "analysis_reuse_ratio": round(total_analyses / unique_urls, 2) if unique_urls > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting cache statistics: {str(e)}")
            return {}
    
    async def cleanup_old_cache(self):
        """Clean up old cached intelligence data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.cache_duration_days)
            
            # Find old intelligence records that are not referenced by recent campaigns
            cleanup_query = text("""
                DELETE FROM campaign_intelligence 
                WHERE created_at < :cutoff_date 
                AND confidence_score < :min_confidence
                AND id NOT IN (
                    SELECT DISTINCT source_intelligence_id::uuid 
                    FROM campaign_intelligence 
                    WHERE processing_metadata->>'source_intelligence_id' IS NOT NULL
                    AND created_at > :recent_cutoff
                )
            """)
            
            result = await self.db.execute(cleanup_query, {
                "cutoff_date": cutoff_date,
                "min_confidence": self.min_confidence_threshold,
                "recent_cutoff": datetime.utcnow() - timedelta(days=7)
            })
            
            await self.db.commit()
            
            deleted_count = result.rowcount
            logger.info(f"🧹 Cleaned up {deleted_count} old cache entries")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up cache: {str(e)}")
            return 0


# Updated Analysis Handler with Shared Cache Integration
# File: src/intelligence/handlers/analysis_handler.py (add these methods)

class AnalysisHandler:
    """Analysis Handler with shared intelligence caching"""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
        self.shared_cache = SharedIntelligenceCache(db)
    
    async def analyze_url_with_cache(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced URL analysis with shared intelligence caching
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
                    user_id=self.user.id,
                    company_id=self.user.company_id,
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
                        "analysis_age_days": (datetime.utcnow() - datetime.fromisoformat(cached_intelligence["original_analysis_date"])).days
                    }
                }
                
            except Exception as cache_error:
                logger.error(f"❌ Cache utilization failed: {str(cache_error)}")
                # Fall through to new analysis
        
        # STEP 2: CACHE MISS - Perform new analysis
        logger.info("🔍 CACHE MISS: Performing new intelligence analysis...")
        
        # Create intelligence record
        intelligence = await self._create_intelligence_record(url, campaign_id, analysis_type)
        
        try:
            # Perform full analysis (base + amplification)
            base_analysis_result = await self._perform_base_analysis(url, analysis_type)
            final_analysis_result = await self._perform_amplification(url, base_analysis_result)
            
            # Store results
            await self._store_analysis_results(intelligence, final_analysis_result)
            
            # Update campaign counters
            await self._update_campaign_counters(campaign_id)
            
            logger.info("✅ NEW ANALYSIS: Created fresh intelligence (available for future caching)")
            
            # Prepare response
            return self._prepare_analysis_response_with_cache_info(
                intelligence, 
                final_analysis_result, 
                cache_hit=False
            )
            
        except Exception as e:
            logger.error(f"❌ Analysis failed for {url}: {str(e)}")
            await self._handle_analysis_failure(intelligence, e)
            return self._prepare_failure_response(intelligence, e)
    
    def _prepare_analysis_response_with_cache_info(
        self, 
        intelligence: CampaignIntelligence, 
        analysis_result: Dict[str, Any],
        cache_hit: bool = False
    ) -> Dict[str, Any]:
        """Prepare analysis response with cache information"""
        
        base_response = self._prepare_analysis_response(intelligence, analysis_result)
        
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


# Cache Management Commands
# File: src/intelligence/cache/cache_manager.py

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