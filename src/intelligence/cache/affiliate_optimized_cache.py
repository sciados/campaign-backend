# Affiliate Marketing Optimized Cache Strategy
# File: src/intelligence/cache/affiliate_optimized_cache.py

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, and_, or_
from collections import defaultdict

logger = logging.getLogger(__name__)

class AffiliateOptimizedCache:
    """
    Cache system specifically optimized for affiliate marketers
    who frequently analyze the same sales pages for different campaigns
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.popular_domains = [
            # Major affiliate networks
            'warriorplus.com', 'jvzoo.com',
            # Popular product categories
            'amazon.com', 'ebay.com', 'etsy.com',
            # Health & wellness (popular in affiliate marketing)
            'supplementscam.com', 'healthline.com',
            # Digital products
            'gumroad.com', 'teachable.com', 'udemy.com',
            # Software/SaaS
            'software.com', 'saas-products.com'
        ]
        
        # Extended cache for affiliate products (60 days vs 30 for regular)
        self.affiliate_cache_duration = 60
        self.regular_cache_duration = 30
    
    def is_popular_affiliate_domain(self, url: str) -> bool:
        """Check if URL is from a popular affiliate marketing domain"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.lower()
            
            # Check exact matches
            if any(affiliate_domain in domain for affiliate_domain in self.popular_domains):
                return True
            
            # Check for common affiliate URL patterns
            affiliate_patterns = [                
                'warriorplus.com/o2/',
                'jvz',
                'affiliate',
                'promo',
                'special',
                'discount'
            ]
            
            return any(pattern in url.lower() for pattern in affiliate_patterns)
            
        except Exception:
            return False
    
    async def get_affiliate_cache_duration(self, url: str) -> int:
        """Get cache duration based on URL type"""
        if self.is_popular_affiliate_domain(url):
            return self.affiliate_cache_duration
        return self.regular_cache_duration
    
    async def get_popular_affiliate_urls(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get most frequently analyzed URLs by affiliate marketers"""
        try:
            query = text("""
                SELECT 
                    source_url,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(DISTINCT company_id) as unique_companies,
                    COUNT(*) as total_analyses,
                    AVG(confidence_score) as avg_confidence,
                    MAX(created_at) as last_analyzed,
                    EXTRACT(DAYS FROM (NOW() - MIN(created_at))) as days_since_first
                FROM campaign_intelligence 
                WHERE analysis_status = 'COMPLETED'
                AND created_at >= NOW() - INTERVAL '90 days'
                GROUP BY source_url
                HAVING COUNT(DISTINCT user_id) >= 3  -- At least 3 different users
                ORDER BY unique_users DESC, total_analyses DESC
                LIMIT :limit
            """)
            
            result = await self.db.execute(query, {"limit": limit})
            rows = result.fetchall()
            
            popular_urls = []
            for row in rows:
                url_data = {
                    "url": row[0],
                    "unique_users": row[1],
                    "unique_companies": row[2], 
                    "total_analyses": row[3],
                    "avg_confidence": round(float(row[4]), 2),
                    "last_analyzed": row[5].isoformat() if row[5] else None,
                    "days_active": int(row[6]) if row[6] else 0,
                    "is_affiliate_domain": self.is_popular_affiliate_domain(row[0]),
                    "reuse_factor": round(row[3] / row[1], 1)  # Analyses per user
                }
                popular_urls.append(url_data)
            
            logger.info(f"📊 Found {len(popular_urls)} popular affiliate URLs")
            return popular_urls
            
        except Exception as e:
            logger.error(f"❌ Error getting popular affiliate URLs: {str(e)}")
            return []
    
    async def get_affiliate_savings_report(self) -> Dict[str, Any]:
        """Generate detailed savings report for affiliate marketing usage"""
        try:
            # Get cache statistics
            cache_stats_query = text("""
                SELECT 
                    COUNT(*) as total_analyses,
                    COUNT(CASE WHEN processing_metadata->>'shared_from_cache' = 'true' THEN 1 END) as cached_analyses,
                    COUNT(DISTINCT source_url) as unique_urls,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(DISTINCT company_id) as unique_companies,
                    AVG(confidence_score) as avg_confidence
                FROM campaign_intelligence
                WHERE created_at >= NOW() - INTERVAL '30 days'
                AND analysis_status = 'COMPLETED'
            """)
            
            result = await self.db.execute(cache_stats_query)
            stats = result.fetchone()
            
            if not stats:
                return {}
            
            total_analyses = stats[0]
            cached_analyses = stats[1] 
            unique_urls = stats[2]
            unique_users = stats[3]
            unique_companies = stats[4]
            avg_confidence = float(stats[5]) if stats[5] else 0
            
            # Calculate affiliate marketing specific metrics
            cache_hit_rate = (cached_analyses / total_analyses * 100) if total_analyses > 0 else 0
            reuse_ratio = total_analyses / unique_urls if unique_urls > 0 else 0
            
            # Cost calculations (based on your original $6+ per analysis)
            full_analysis_cost = 6.00  # Cost without cache
            cached_analysis_cost = 0.10  # Just database operations
            
            total_cost_without_cache = total_analyses * full_analysis_cost
            actual_cost_with_cache = (unique_urls * full_analysis_cost) + (cached_analyses * cached_analysis_cost)
            total_savings = total_cost_without_cache - actual_cost_with_cache
            
            # Affiliate-specific insights
            affiliate_insights = []
            if reuse_ratio > 5:
                affiliate_insights.append("🎯 Excellent URL reuse - typical affiliate marketing pattern")
            if cache_hit_rate > 70:
                affiliate_insights.append("💰 Outstanding cache efficiency - major cost savings achieved")
            if unique_companies < unique_users * 0.3:
                affiliate_insights.append("👥 High user density per company - affiliate teams detected")
            
            return {
                "period": "Last 30 days",
                "affiliate_metrics": {
                    "total_analyses": total_analyses,
                    "unique_products_analyzed": unique_urls,
                    "unique_affiliate_marketers": unique_users,
                    "companies_agencies": unique_companies,
                    "average_quality_score": round(avg_confidence, 2)
                },
                "cache_performance": {
                    "cache_hit_rate": round(cache_hit_rate, 1),
                    "url_reuse_ratio": round(reuse_ratio, 1),
                    "cached_analyses": cached_analyses,
                    "fresh_analyses": total_analyses - cached_analyses
                },
                "cost_analysis": {
                    "total_cost_without_cache": f"${total_cost_without_cache:,.2f}",
                    "actual_cost_with_cache": f"${actual_cost_with_cache:,.2f}",
                    "total_savings": f"${total_savings:,.2f}",
                    "savings_percentage": f"{(total_savings/total_cost_without_cache*100):.1f}%" if total_cost_without_cache > 0 else "0%",
                    "cost_per_analysis_average": f"${actual_cost_with_cache/total_analyses:.2f}" if total_analyses > 0 else "$0.00"
                },
                "affiliate_insights": affiliate_insights,
                "top_products": await self.get_top_affiliate_products()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating affiliate savings report: {str(e)}")
            return {}
    
    async def get_top_affiliate_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top products being promoted by affiliate marketers"""
        try:
            query = text("""
                SELECT 
                    source_title,
                    source_url,
                    COUNT(DISTINCT user_id) as affiliate_count,
                    COUNT(*) as total_promotions,
                    AVG(confidence_score) as avg_quality,
                    MAX(created_at) as last_promotion
                FROM campaign_intelligence
                WHERE created_at >= NOW() - INTERVAL '30 days'
                AND analysis_status = 'COMPLETED'
                AND source_title IS NOT NULL
                AND source_title != ''
                GROUP BY source_title, source_url
                HAVING COUNT(DISTINCT user_id) >= 2
                ORDER BY affiliate_count DESC, total_promotions DESC
                LIMIT :limit
            """)
            
            result = await self.db.execute(query, {"limit": limit})
            rows = result.fetchall()
            
            top_products = []
            for row in rows:
                product = {
                    "product_name": row[0],
                    "product_url": row[1],
                    "affiliate_marketers": row[2],
                    "total_analyses": row[3],
                    "quality_score": round(float(row[4]), 2),
                    "last_analyzed": row[5].isoformat() if row[5] else None,
                    "promotion_intensity": round(row[3] / row[2], 1)  # Analyses per affiliate
                }
                top_products.append(product)
            
            return top_products
            
        except Exception as e:
            logger.error(f"❌ Error getting top affiliate products: {str(e)}")
            return []
    
    async def predict_cache_value(self, url: str) -> Dict[str, Any]:
        """Predict the cache value of analyzing a specific URL"""
        try:
            # Check if similar URLs have been popular
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            
            similar_urls_query = text("""
                SELECT 
                    COUNT(DISTINCT user_id) as potential_users,
                    COUNT(*) as similar_analyses,
                    AVG(confidence_score) as expected_quality
                FROM campaign_intelligence
                WHERE source_url LIKE :domain_pattern
                AND created_at >= NOW() - INTERVAL '90 days'
                AND analysis_status = 'COMPLETED'
            """)
            
            result = await self.db.execute(similar_urls_query, {"domain_pattern": f"%{domain}%"})
            stats = result.fetchone()
            
            if stats and stats[0]:
                potential_users = stats[0]
                similar_analyses = stats[1] 
                expected_quality = float(stats[2])
                
                # Estimate cache value
                estimated_reuse = min(potential_users * 2, 50)  # Conservative estimate
                cost_savings = estimated_reuse * 5.90  # $5.90 saved per cached use
                
                return {
                    "cache_prediction": "high_value" if estimated_reuse > 10 else "medium_value" if estimated_reuse > 3 else "low_value",
                    "estimated_reuse_count": estimated_reuse,
                    "potential_cost_savings": f"${cost_savings:.2f}",
                    "expected_quality": round(expected_quality, 2),
                    "recommendation": "Prioritize for analysis" if estimated_reuse > 10 else "Standard analysis" if estimated_reuse > 3 else "Low priority",
                    "similar_domain_popularity": similar_analyses,
                    "is_affiliate_domain": self.is_popular_affiliate_domain(url)
                }
            
            return {
                "cache_prediction": "unknown",
                "estimated_reuse_count": 0,
                "potential_cost_savings": "$0.00",
                "recommendation": "New domain - analyze to establish baseline"
            }
            
        except Exception as e:
            logger.error(f"❌ Error predicting cache value: {str(e)}")
            return {}


# Affiliate Marketing Dashboard
# File: src/intelligence/dashboard/affiliate_dashboard.py

class AffiliateDashboard:
    """Dashboard specifically designed for affiliate marketing insights"""
    
    def __init__(self, db: AsyncSession):
        self.cache = AffiliateOptimizedCache(db)
    
    async def get_affiliate_overview(self) -> Dict[str, Any]:
        """Get comprehensive affiliate marketing overview"""
        try:
            # Get savings report
            savings_report = await self.cache.get_affiliate_savings_report()
            
            # Get popular products
            popular_products = await self.cache.get_top_affiliate_products(15)
            
            # Get trending URLs
            popular_urls = await self.cache.get_popular_affiliate_urls(20)
            
            return {
                "dashboard_type": "affiliate_marketing",
                "generated_at": datetime.utcnow().isoformat(),
                "savings_summary": savings_report,
                "trending_products": popular_products,
                "popular_urls": popular_urls,
                "affiliate_insights": self._generate_affiliate_insights(savings_report, popular_products),
                "recommendations": self._generate_recommendations(savings_report)
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating affiliate overview: {str(e)}")
            return {}
    
    def _generate_affiliate_insights(self, savings_report: Dict, products: List[Dict]) -> List[str]:
        """Generate insights specific to affiliate marketing patterns"""
        insights = []
        
        if savings_report:
            cache_hit_rate = float(savings_report.get("cache_performance", {}).get("cache_hit_rate", 0))
            reuse_ratio = float(savings_report.get("cache_performance", {}).get("url_reuse_ratio", 0))
            
            if cache_hit_rate > 80:
                insights.append("🎯 Exceptional cache efficiency - affiliate marketers are analyzing similar products")
            
            if reuse_ratio > 8:
                insights.append("📈 High URL reuse detected - strong affiliate marketing activity")
            
            if len(products) > 5:
                insights.append(f"🔥 {len(products)} hot products being promoted by multiple affiliates")
        
        # Product-specific insights
        if products:
            top_product = products[0]
            if top_product["affiliate_marketers"] > 10:
                insights.append(f"⭐ '{top_product['product_name']}' is being promoted by {top_product['affiliate_marketers']} affiliates")
        
        return insights
    
    def _generate_recommendations(self, savings_report: Dict) -> List[str]:
        """Generate actionable recommendations for affiliate marketers"""
        recommendations = []
        
        if savings_report:
            cache_hit_rate = float(savings_report.get("cache_performance", {}).get("cache_hit_rate", 0))
            
            if cache_hit_rate < 50:
                recommendations.append("Consider focusing on popular affiliate products to maximize cache benefits")
            
            recommendations.append("Analyze competitor sales pages to find trending products")
            recommendations.append("Use cached intelligence to create unique content angles")
            recommendations.append("Monitor top products for seasonal promotion opportunities")
        
        return recommendations


# Example Usage and Benefits
def demonstrate_affiliate_cache_benefits():
    """Show the massive benefits for affiliate marketers"""
    
    scenarios = {
        "amazon_electronics": {
            "product": "Trending Electronics Product on Amazon", 
            "affiliates_analyzing": 75,
            "analysis_cost_each": 6.00,
            "cache_cost_each": 0.10
        },
        "digital_course": {
            "product": "Popular Digital Marketing Course",
            "affiliates_analyzing": 200,
            "analysis_cost_each": 6.00, 
            "cache_cost_each": 0.10
        }
    }
    
    total_savings = 0
    
    print("💰 AFFILIATE MARKETING CACHE BENEFITS")
    print("=" * 60)
    
    for scenario_name, data in scenarios.items():
        affiliates = data["affiliates_analyzing"]
        cost_without_cache = affiliates * data["analysis_cost_each"]
        cost_with_cache = data["analysis_cost_each"] + ((affiliates - 1) * data["cache_cost_each"])
        savings = cost_without_cache - cost_with_cache
        savings_percent = (savings / cost_without_cache) * 100
        
        total_savings += savings
        
        print(f"\n{scenario_name.upper().replace('_', ' ')}")
        print(f"  Affiliates: {affiliates}")
        print(f"  Without Cache: ${cost_without_cache:,.2f}")
        print(f"  With Cache: ${cost_with_cache:,.2f}")
        print(f"  Savings: ${savings:,.2f} ({savings_percent:.1f}%)")
    
    print("=" * 60)
    print(f"TOTAL MONTHLY SAVINGS: ${total_savings:,.2f}")
    print(f"ANNUAL SAVINGS: ${total_savings * 12:,.2f}")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_affiliate_cache_benefits()