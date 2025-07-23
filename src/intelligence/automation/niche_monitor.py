# Automated Niche Monitoring System
# File: src/intelligence/automation/niche_monitor.py

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
import aiohttp
import json

logger = logging.getLogger(__name__)

class AutomatedNicheMonitor:
    """
    Automated monitoring system for high-volume affiliate niches
    Continuously discovers and prioritizes new products for analysis
    """
    
    def __init__(self, db):
        self.db = db
        self.monitoring_active = False
        self.niche_schedules = self._initialize_monitoring_schedules()
        
    def _initialize_monitoring_schedules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize monitoring schedules for each niche"""
        return {
            "Health & Weight Loss": {
                "check_interval_minutes": 60,  # Every hour
                "sources": ["amazon_supplements", "health_trends"],
                "max_daily_analyses": 20,
                "priority_score": 100
            },
            "Make Money Online": {
                "check_interval_minutes": 30,  # Every 30 minutes
                "sources": ["warriorplus", "jvzoo", "product_hunt_biz"],
                "max_daily_analyses": 25,
                "priority_score": 100
            },
            "Beauty & Anti-Aging": {
                "check_interval_minutes": 180,  # Every 3 hours
                "sources": ["amazon_beauty", "sephora_new", "beauty_trends"],
                "max_daily_analyses": 15,
                "priority_score": 80
            },
            "Fitness & Muscle Building": {
                "check_interval_minutes": 240,  # Every 4 hours
                "sources": ["amazon_fitness", "bodybuilding_new", "fitness_trends"],
                "max_daily_analyses": 12,
                "priority_score": 80
            },
            "Dating & Relationships": {
                "check_interval_minutes": 360,  # Every 6 hours
                "sources": ["relationship_blogs"],
                "max_daily_analyses": 8,
                "priority_score": 70
            }
        }
    
    async def start_continuous_monitoring(self):
        """Start continuous monitoring of all high-value niches"""
        self.monitoring_active = True
        logger.info("🚀 Starting continuous niche monitoring...")
        
        # Create monitoring tasks for each niche
        monitoring_tasks = []
        for niche_name, schedule in self.niche_schedules.items():
            task = asyncio.create_task(
                self._monitor_niche_continuously(niche_name, schedule)
            )
            monitoring_tasks.append(task)
        
        # Also start the priority processor
        processor_task = asyncio.create_task(self._process_high_priority_queue())
        monitoring_tasks.append(processor_task)
        
        try:
            await asyncio.gather(*monitoring_tasks)
        except Exception as e:
            logger.error(f"❌ Error in continuous monitoring: {str(e)}")
        finally:
            self.monitoring_active = False
    
    async def _monitor_niche_continuously(self, niche_name: str, schedule: Dict[str, Any]):
        """Continuously monitor a specific niche"""
        logger.info(f"🎯 Starting continuous monitoring for: {niche_name}")
        
        daily_analysis_count = 0
        last_reset_date = datetime.now().date()
        
        while self.monitoring_active:
            try:
                # Reset daily counter if new day
                current_date = datetime.now().date()
                if current_date > last_reset_date:
                    daily_analysis_count = 0
                    last_reset_date = current_date
                    logger.info(f"🔄 Reset daily counter for {niche_name}")
                
                # Check if we've hit daily limit
                if daily_analysis_count >= schedule["max_daily_analyses"]:
                    logger.info(f"📊 Daily analysis limit reached for {niche_name} ({daily_analysis_count})")
                    await asyncio.sleep(schedule["check_interval_minutes"] * 60)
                    continue
                
                # Discover new products for this niche
                new_products = await self._discover_niche_products(niche_name, schedule["sources"])
                
                # Queue high-priority products for analysis
                queued_count = 0
                for product in new_products:
                    if daily_analysis_count + queued_count < schedule["max_daily_analyses"]:
                        success = await self._queue_product_for_analysis(product, niche_name, schedule["priority_score"])
                        if success:
                            queued_count += 1
                
                daily_analysis_count += queued_count
                
                if queued_count > 0:
                    logger.info(f"✅ {niche_name}: Queued {queued_count} products for analysis (daily total: {daily_analysis_count})")
                
                # Wait until next check
                await asyncio.sleep(schedule["check_interval_minutes"] * 60)
                
            except Exception as e:
                logger.error(f"❌ Error monitoring {niche_name}: {str(e)}")
                await asyncio.sleep(300)  # 5 minute error delay
    
    async def _discover_niche_products(self, niche_name: str, sources: List[str]) -> List[Dict[str, Any]]:
        """Discover new products for a specific niche"""
        try:
            all_products = []
            
            for source in sources:
                try:
                    products = await self._discover_from_source(source, niche_name)
                    all_products.extend(products)
                except Exception as e:
                    logger.error(f"❌ Error discovering from {source}: {str(e)}")
            
            # Filter out already analyzed products
            new_products = await self._filter_new_products(all_products)
            
            # Sort by estimated value/popularity
            new_products.sort(key=lambda x: x.get("estimated_affiliates", 0), reverse=True)
            
            return new_products[:10]  # Top 10 most promising
            
        except Exception as e:
            logger.error(f"❌ Error discovering products for {niche_name}: {str(e)}")
            return []
    
    async def _discover_from_source(self, source: str, niche_name: str) -> List[Dict[str, Any]]:
        """Discover products from a specific source"""
        
        if  source == "amazon_supplements":
            return await self._discover_amazon_supplements()
        elif source == "warriorplus":
            return await self._discover_warriorplus()
        elif source == "health_trends":
            return await self._discover_health_trends()
        else:
            return []
    
    async def _discover_warriorplus(self) -> List[Dict[str, Any]]:
        """Discover new launches from WarriorPlus"""
        try:
            # Mock WarriorPlus new launches
            new_launches = [
                {
                    "url": "https://email-marketing-empire.warriorplus.com",
                    "title": "Email Marketing Empire",
                    "niche": "Make Money Online",
                    "estimated_affiliates": 200,
                    "trending_score": 85,
                    "source": "WarriorPlus Launch"
                },
                {
                    "url": "https://social-media-profits.warriorplus.com",
                    "title": "Social Media Profits 2024",
                    "niche": "Make Money Online", 
                    "estimated_affiliates": 150,
                    "trending_score": 78,
                    "source": "WarriorPlus Launch"
                }
            ]
            
            logger.info(f"🔍 Discovered {len(new_launches)} new launches from WarriorPlus")
            return new_launches
            
        except Exception as e:
            logger.error(f"❌ WarriorPlus discovery error: {str(e)}")
            return []
    
    async def _discover_amazon_supplements(self) -> List[Dict[str, Any]]:
        """Discover trending supplements from Amazon"""
        try:
            # Mock Amazon bestsellers discovery
            bestsellers = [
                {
                    "url": "https://amazon.com/trending-probiotic-supplement/dp/B123456789",
                    "title": "Advanced Probiotic Complex",
                    "niche": "Health & Weight Loss",
                    "estimated_affiliates": 120,
                    "trending_score": 75,
                    "source": "Amazon Bestsellers"
                },
                {
                    "url": "https://amazon.com/collagen-peptides-powder/dp/B987654321",
                    "title": "Premium Collagen Peptides",
                    "niche": "Beauty & Anti-Aging",
                    "estimated_affiliates": 90,
                    "trending_score": 72,
                    "source": "Amazon Bestsellers"
                }
            ]
            
            logger.info(f"🔍 Discovered {len(bestsellers)} trending supplements from Amazon")
            return bestsellers
            
        except Exception as e:
            logger.error(f"❌ Amazon supplements discovery error: {str(e)}")
            return []
    
    async def _discover_health_trends(self) -> List[Dict[str, Any]]:
        """Discover trending health topics that could become products"""
        try:
            # This could integrate with Google Trends, social media APIs, etc.
            trending_topics = [
                {
                    "url": "https://new-liver-detox-trend.com",
                    "title": "Liver Detox Trending Solution",
                    "niche": "Health & Weight Loss",
                    "estimated_affiliates": 80,
                    "trending_score": 68,
                    "source": "Health Trends"
                }
            ]
            
            return trending_topics
            
        except Exception as e:
            logger.error(f"❌ Health trends discovery error: {str(e)}")
            return []
    
    async def _filter_new_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out products that have already been analyzed recently"""
        try:
            new_products = []
            
            for product in products:
                url = product["url"]
                
                # Check if URL was analyzed in last 7 days
                query = """
                    SELECT id FROM campaign_intelligence 
                    WHERE source_url = :url 
                    AND created_at >= NOW() - INTERVAL '7 days'
                    LIMIT 1
                """
                
                result = await self.db.execute(query, {"url": url})
                
                if not result.fetchone():
                    new_products.append(product)
                else:
                    logger.debug(f"⏭️ Skipping recently analyzed: {url}")
            
            return new_products
            
        except Exception as e:
            logger.error(f"❌ Error filtering new products: {str(e)}")
            return products  # Return all if filtering fails
    
    async def _queue_product_for_analysis(self, product: Dict[str, Any], niche_name: str, priority_score: int) -> bool:
        """Queue a discovered product for proactive analysis"""
        try:
            # Calculate final priority based on multiple factors
            base_priority = 1 if priority_score >= 100 else 2 if priority_score >= 80 else 3
            
            estimated_affiliates = product.get("estimated_affiliates", 0)
            trending_score = product.get("trending_score", 0)
            
            # Boost priority for high-potential products
            if estimated_affiliates > 200 and trending_score > 90:
                final_priority = 1
            elif estimated_affiliates > 100 and trending_score > 80:
                final_priority = min(base_priority, 2)
            else:
                final_priority = base_priority
            
            # Queue for analysis
            from src.intelligence.proactive.sales_page_monitor import ProactiveSalesPageMonitor
            monitor = ProactiveSalesPageMonitor(self.db)
            
            metadata = {
                "niche": niche_name,
                "estimated_affiliates": estimated_affiliates,
                "trending_score": trending_score,
                "source": product.get("source", "unknown"),
                "discovery_timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
                "auto_discovered": True
            }
            
            success = await monitor.queue_url_for_proactive_analysis(
                url=product["url"],
                priority=final_priority,
                source=f"auto_{niche_name.lower().replace(' ', '_')}",
                metadata=metadata
            )
            
            if success:
                logger.info(f"✅ Queued {product['title']} (priority: {final_priority}, affiliates: {estimated_affiliates})")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error queueing product: {str(e)}")
            return False
    
    async def _process_high_priority_queue(self):
        """Continuously process high-priority analysis queue"""
        logger.info("🚀 Starting high-priority queue processor...")
        
        while self.monitoring_active:
            try:
                from src.intelligence.proactive.sales_page_monitor import ProactiveSalesPageMonitor
                monitor = ProactiveSalesPageMonitor(self.db)
                
                # Process priority 1 and 2 items more frequently
                result = await monitor.process_proactive_analysis_queue(batch_size=5)
                
                if result["processed"] > 0:
                    logger.info(f"🎯 Processed {result['processed']} high-priority analyses")
                
                # Wait 5 minutes before next processing cycle
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"❌ Error in priority queue processor: {str(e)}")
                await asyncio.sleep(600)  # 10 minute error delay
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        logger.info("⏹️ Stopping continuous niche monitoring...")


# Niche Performance Analytics
# File: src/intelligence/analytics/niche_analytics.py

class NichePerformanceAnalytics:
    """Analytics for niche performance and ROI optimization"""
    
    def __init__(self, db):
        self.db = db
    
    async def generate_niche_roi_report(self) -> Dict[str, Any]:
        """Generate comprehensive ROI report for niche targeting"""
        try:
            # Get performance data for each niche
            niche_performance = {}
            
            niches = [
                "Health & Weight Loss",
                "Make Money Online", 
                "Beauty & Anti-Aging",
                "Fitness & Muscle Building",
                "Dating & Relationships"
            ]
            
            total_savings = 0
            total_analyses = 0
            
            for niche in niches:
                performance = await self._calculate_niche_roi(niche)
                niche_performance[niche] = performance
                total_savings += performance["estimated_savings"]
                total_analyses += performance["total_analyses"]
            
            # Calculate overall metrics
            overall_metrics = {
                "total_cost_savings": total_savings,
                "total_analyses_served": total_analyses,
                "average_cost_per_analysis": total_savings / max(total_analyses, 1),
                "roi_percentage": (total_savings / (total_analyses * 6.0)) * 100 if total_analyses > 0 else 0
            }
            
            return {
                "report_type": "niche_roi_analysis",
                "generated_at": datetime.now(timezone.utc).astimezone().isoformat(),
                "period": "Last 30 days",
                "overall_metrics": overall_metrics,
                "niche_breakdown": niche_performance,
                "strategic_insights": self._generate_strategic_insights(niche_performance),
                "optimization_recommendations": self._generate_optimization_recommendations(niche_performance)
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating niche ROI report: {str(e)}")
            return {}
    
    async def _calculate_niche_roi(self, niche_name: str) -> Dict[str, Any]:
        """Calculate ROI metrics for a specific niche"""
        try:
            # Mock calculation - replace with actual database queries
            
            # Simulate realistic data based on niche characteristics
            niche_data = {
                "Health & Weight Loss": {
                    "total_analyses": 450,
                    "unique_urls": 25, 
                    "cache_hits": 425,
                    "avg_affiliates_per_url": 18
                },
                "Make Money Online": {
                    "total_analyses": 680,
                    "unique_urls": 22,
                    "cache_hits": 658,
                    "avg_affiliates_per_url": 31
                },
                "Beauty & Anti-Aging": {
                    "total_analyses": 320,
                    "unique_urls": 18,
                    "cache_hits": 302,
                    "avg_affiliates_per_url": 18
                },
                "Fitness & Muscle Building": {
                    "total_analyses": 280,
                    "unique_urls": 20,
                    "cache_hits": 260,
                    "avg_affiliates_per_url": 14
                },
                "Dating & Relationships": {
                    "total_analyses": 150,
                    "unique_urls": 12,
                    "cache_hits": 138,
                    "avg_affiliates_per_url": 12
                }
            }
            
            data = niche_data.get(niche_name, {
                "total_analyses": 100,
                "unique_urls": 10,
                "cache_hits": 90,
                "avg_affiliates_per_url": 10
            })
            
            # Calculate metrics
            cache_hit_rate = (data["cache_hits"] / data["total_analyses"]) * 100
            cost_without_cache = data["total_analyses"] * 6.0
            cost_with_cache = (data["unique_urls"] * 6.0) + (data["cache_hits"] * 0.10)
            estimated_savings = cost_without_cache - cost_with_cache
            roi_percentage = (estimated_savings / cost_without_cache) * 100
            
            return {
                "niche": niche_name,
                "total_analyses": data["total_analyses"],
                "unique_urls": data["unique_urls"],
                "cache_hits": data["cache_hits"],
                "cache_hit_rate": round(cache_hit_rate, 1),
                "avg_affiliates_per_url": data["avg_affiliates_per_url"],
                "cost_without_cache": cost_without_cache,
                "cost_with_cache": cost_with_cache,
                "estimated_savings": estimated_savings,
                "roi_percentage": round(roi_percentage, 1),
                "value_rating": "EXCELLENT" if roi_percentage > 90 else "GOOD" if roi_percentage > 80 else "FAIR"
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating ROI for {niche_name}: {str(e)}")
            return {}
    
    def _generate_strategic_insights(self, niche_performance: Dict[str, Any]) -> List[str]:
        """Generate strategic insights from niche performance data"""
        insights = []
        
        # Find top performing niches
        top_niches = sorted(
            niche_performance.items(),
            key=lambda x: x[1].get("roi_percentage", 0),
            reverse=True
        )[:3]
        
        if top_niches:
            best_niche = top_niches[0]
            insights.append(f"🏆 {best_niche[0]} is your highest ROI niche at {best_niche[1].get('roi_percentage', 0):.1f}%")
        
        # Identify high-reuse niches
        high_reuse = [
            niche for niche, data in niche_performance.items()
            if data.get("avg_affiliates_per_url", 0) > 20
        ]
        
        if high_reuse:
            insights.append(f"🎯 {len(high_reuse)} niches show excellent URL reuse (20+ affiliates per product)")
        
        # Cache efficiency insights
        high_cache = [
            niche for niche, data in niche_performance.items()
            if data.get("cache_hit_rate", 0) > 90
        ]
        
        if high_cache:
            insights.append(f"⚡ {len(high_cache)} niches achieve 90%+ cache hit rates")
        
        return insights
    
    def _generate_optimization_recommendations(self, niche_performance: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Recommend focusing on top ROI niches
        excellent_niches = [
            niche for niche, data in niche_performance.items()
            if data.get("value_rating") == "EXCELLENT"
        ]
        
        if excellent_niches:
            recommendations.append(f"🚀 Focus 80% of proactive analysis on {len(excellent_niches)} excellent-ROI niches")
        
        # Recommend scaling successful niches
        high_volume_niches = [
            niche for niche, data in niche_performance.items()
            if data.get("total_analyses", 0) > 400
        ]
        
        if high_volume_niches:
            recommendations.append(f"📈 Scale analysis frequency for {len(high_volume_niches)} high-volume niches")
        
        # Recommend monitoring frequency adjustments
        recommendations.append("⏰ Increase monitoring frequency for niches with >95% cache hit rates")
        recommendations.append("💡 Consider expanding to sub-niches within top-performing categories")
        
        return recommendations


# Main Automation Controller
# File: src/intelligence/automation/automation_controller.py

class NicheAutomationController:
    """Main controller for automated niche targeting and monitoring"""
    
    def __init__(self, db):
        self.db = db
        self.monitor = AutomatedNicheMonitor(db)
        self.analytics = NichePerformanceAnalytics(db)
        self.running = False
    
    async def start_full_automation(self):
        """Start complete automation system"""
        self.running = True
        logger.info("🚀 Starting full niche automation system...")
        
        try:
            # Start continuous monitoring
            monitoring_task = asyncio.create_task(
                self.monitor.start_continuous_monitoring()
            )
            
            # Start periodic analytics
            analytics_task = asyncio.create_task(
                self._run_periodic_analytics()
            )
            
            await asyncio.gather(monitoring_task, analytics_task)
            
        except Exception as e:
            logger.error(f"❌ Error in full automation: {str(e)}")
        finally:
            self.running = False
    
    async def _run_periodic_analytics(self):
        """Run analytics and optimization checks periodically"""
        while self.running:
            try:
                # Generate ROI report every 6 hours
                roi_report = await self.analytics.generate_niche_roi_report()
                
                if roi_report:
                    logger.info("📊 Generated niche ROI report")
                    
                    # Log key insights
                    insights = roi_report.get("strategic_insights", [])
                    for insight in insights[:3]:  # Top 3 insights
                        logger.info(f"💡 {insight}")
                
                # Wait 6 hours before next analytics run
                await asyncio.sleep(21600)
                
            except Exception as e:
                logger.error(f"❌ Error in periodic analytics: {str(e)}")
                await asyncio.sleep(3600)  # 1 hour error delay
    
    def stop_automation(self):
        """Stop all automation"""
        self.running = False
        self.monitor.stop_monitoring()
        logger.info("⏹️ Stopped full niche automation system")


# CLI Commands for Manual Control
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "start":
            print("🚀 Starting niche automation...")
            # Start automation system
            
        elif command == "status":
            print("📊 Niche automation status...")
            # Show current status
            
        elif command == "report":
            print("📈 Generating niche performance report...")
            # Generate and display report
            
        else:
            print("Available commands: start, status, report")
    else:
        print("Usage: python niche_monitoring_automation.py [start|status|report]")