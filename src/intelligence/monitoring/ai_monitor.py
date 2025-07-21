# src/intelligence/monitoring/ai_monitor.py
"""
AI MONITORING SERVICE - AUTOMATIC OPTIMIZATION SYSTEM
🤖 Monitors pricing, performance, and capabilities in real-time
🎯 Auto-selects optimal providers for each content type
💰 Maximizes cost savings while maintaining quality
🔄 Adapts to new models and pricing changes automatically
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import aiohttp
import os

logger = logging.getLogger(__name__)

@dataclass
class ProviderMetrics:
    """Provider performance and cost metrics"""
    provider_name: str
    model_name: str
    content_type: str
    cost_per_unit: float
    quality_score: float
    speed_score: float
    reliability_score: float
    value_score: float  # quality/cost ratio
    last_updated: datetime

@dataclass
class OptimizationRecommendation:
    """AI provider recommendation for content type"""
    content_type: str
    primary_provider: str
    backup_providers: List[str]
    reasoning: str
    cost_savings: float
    quality_impact: str

class AIMonitorService:
    """Main AI monitoring and optimization service"""
    
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.engine = create_async_engine(self.db_url)
        
        # Provider API endpoints for pricing monitoring
        self.pricing_sources = {
            "groq": "https://api.groq.com/v1/models",
            "deepseek": "https://api.deepseek.com/pricing",
            "together": "https://api.together.xyz/v1/models",
            "anthropic": "https://api.anthropic.com/v1/pricing",
            "stability": "https://api.stability.ai/v1/pricing",
            "replicate": "https://api.replicate.com/v1/pricing"
        }
        
        # Content type configurations
        self.content_types = {
            "email_sequence": {"primary_metric": "cost", "quality_threshold": 0.7},
            "ad_copy": {"primary_metric": "quality", "quality_threshold": 0.8},
            "social_media": {"primary_metric": "speed", "quality_threshold": 0.75},
            "blog_post": {"primary_metric": "quality", "quality_threshold": 0.85},
            "landing_page": {"primary_metric": "quality", "quality_threshold": 0.9},
            "image": {"primary_metric": "cost", "quality_threshold": 0.8},
            "video": {"primary_metric": "cost", "quality_threshold": 0.7}
        }
        
        logger.info("🤖 AI Monitor Service initialized")
    
    async def start_monitoring(self, interval_minutes: int = 60):
        """Start continuous monitoring of AI providers"""
        logger.info(f"🔄 Starting AI monitoring (every {interval_minutes} minutes)")
        
        while True:
            try:
                # Run all monitoring tasks concurrently
                await asyncio.gather(
                    self.update_pricing_data(),
                    self.assess_provider_health(),
                    self.benchmark_performance(),
                    self.calculate_optimizations(),
                    self.update_routing_decisions()
                )
                
                logger.info("✅ Monitoring cycle completed successfully")
                
            except Exception as e:
                logger.error(f"❌ Monitoring cycle failed: {str(e)}")
            
            # Wait for next cycle
            await asyncio.sleep(interval_minutes * 60)
    
    async def update_pricing_data(self):
        """Fetch and update latest pricing from all providers"""
        logger.info("💰 Updating pricing data...")
        
        pricing_updates = []
        
        async with aiohttp.ClientSession() as session:
            for provider, endpoint in self.pricing_sources.items():
                try:
                    # Check if we have API key for this provider
                    api_key = self._get_provider_api_key(provider)
                    if not api_key:
                        continue
                    
                    pricing_data = await self._fetch_provider_pricing(session, provider, endpoint, api_key)
                    if pricing_data:
                        pricing_updates.extend(pricing_data)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to fetch pricing for {provider}: {str(e)}")
        
        # Update database with new pricing
        if pricing_updates:
            await self._save_pricing_updates(pricing_updates)
            logger.info(f"📊 Updated pricing for {len(pricing_updates)} provider-model combinations")
    
    async def assess_provider_health(self):
        """Check health and availability of all providers"""
        logger.info("🏥 Assessing provider health...")
        
        health_checks = []
        
        async with aiohttp.ClientSession() as session:
            for provider in self.pricing_sources.keys():
                try:
                    api_key = self._get_provider_api_key(provider)
                    if not api_key:
                        continue
                    
                    health_data = await self._check_provider_health(session, provider, api_key)
                    if health_data:
                        health_checks.append(health_data)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Health check failed for {provider}: {str(e)}")
        
        if health_checks:
            await self._save_health_data(health_checks)
            logger.info(f"🔍 Health checked {len(health_checks)} providers")
    
    async def benchmark_performance(self):
        """Run performance benchmarks on active providers"""
        logger.info("⚡ Running performance benchmarks...")
        
        # Sample prompts for testing
        test_prompts = {
            "text": [
                "Write a compelling email subject line for a health supplement",
                "Create a 50-word product description for a fitness app",
                "Generate 3 social media hashtags for a nutrition brand"
            ],
            "image": [
                "Professional product photo of a health supplement bottle",
                "Social media image for a fitness app announcement",
                "Marketing banner for a nutrition brand"
            ]
        }
        
        performance_results = []
        
        for content_type, prompts in test_prompts.items():
            for prompt in prompts:
                try:
                    # Test each available provider for this content type
                    providers = await self._get_active_providers(content_type)
                    
                    for provider in providers:
                        try:
                            result = await self._benchmark_provider(provider, content_type, prompt)
                            if result:
                                performance_results.append(result)
                                
                        except Exception as e:
                            logger.warning(f"⚠️ Benchmark failed for {provider}: {str(e)}")
                            
                except Exception as e:
                    logger.error(f"❌ Benchmark error for {content_type}: {str(e)}")
        
        if performance_results:
            await self._save_performance_data(performance_results)
            logger.info(f"📈 Completed {len(performance_results)} performance benchmarks")
    
    async def calculate_optimizations(self):
        """Calculate optimal provider selections for each content type"""
        logger.info("🧮 Calculating optimization recommendations...")
        
        recommendations = []
        
        for content_type, config in self.content_types.items():
            try:
                # Get latest metrics for all providers
                metrics = await self._get_provider_metrics(content_type)
                
                if not metrics:
                    continue
                
                # Calculate optimal selection
                recommendation = self._calculate_optimal_provider(content_type, metrics, config)
                if recommendation:
                    recommendations.append(recommendation)
                    
            except Exception as e:
                logger.error(f"❌ Optimization calculation failed for {content_type}: {str(e)}")
        
        if recommendations:
            await self._save_optimization_recommendations(recommendations)
            logger.info(f"🎯 Generated {len(recommendations)} optimization recommendations")
    
    async def update_routing_decisions(self):
        """Update active routing decisions based on latest optimizations"""
        logger.info("🛣️ Updating routing decisions...")
        
        try:
            # Get latest recommendations
            recommendations = await self._get_latest_recommendations()
            
            routing_updates = []
            for rec in recommendations:
                routing_decision = {
                    "content_type": rec.content_type,
                    "selected_provider": rec.primary_provider,
                    "backup_providers": rec.backup_providers,
                    "decision_factors": {
                        "reasoning": rec.reasoning,
                        "cost_savings": rec.cost_savings,
                        "quality_impact": rec.quality_impact,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
                routing_updates.append(routing_decision)
            
            if routing_updates:
                await self._update_active_routing(routing_updates)
                logger.info(f"✅ Updated routing for {len(routing_updates)} content types")
                
        except Exception as e:
            logger.error(f"❌ Routing update failed: {str(e)}")
    
    async def get_optimal_provider(self, content_type: str) -> Dict[str, Any]:
        """Get current optimal provider for content type"""
        async with AsyncSession(self.engine) as session:
            query = text("""
                SELECT rd.selected_provider_id, ap.provider_name, ap.model_name,
                       rd.alternative_providers, rd.decision_factors
                FROM routing_decisions rd
                JOIN ai_providers ap ON rd.selected_provider_id = ap.id
                WHERE rd.content_type = :content_type
                AND rd.effective_from <= NOW()
                AND (rd.expires_at IS NULL OR rd.expires_at > NOW())
                ORDER BY rd.effective_from DESC
                LIMIT 1
            """)
            
            result = await session.execute(query, {"content_type": content_type})
            row = result.fetchone()
            
            if row:
                return {
                    "provider_name": row.provider_name,
                    "model_name": row.model_name,
                    "backup_providers": row.alternative_providers,
                    "decision_factors": row.decision_factors,
                    "api_key_env": f"{row.provider_name.upper()}_API_KEY"
                }
            
            # Fallback to default if no routing decision found
            return await self._get_fallback_provider(content_type)
    
    async def _fetch_provider_pricing(self, session: aiohttp.ClientSession, provider: str, endpoint: str, api_key: str) -> List[Dict]:
        """Fetch pricing data from provider API"""
        headers = self._get_auth_headers(provider, api_key)
        
        async with session.get(endpoint, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_pricing_data(provider, data)
            else:
                logger.warning(f"⚠️ Pricing fetch failed for {provider}: HTTP {response.status}")
                return []
    
    async def _check_provider_health(self, session: aiohttp.ClientSession, provider: str, api_key: str) -> Optional[Dict]:
        """Check health of provider API"""
        test_endpoint = self._get_health_check_endpoint(provider)
        headers = self._get_auth_headers(provider, api_key)
        
        start_time = datetime.utcnow()
        
        try:
            async with session.get(test_endpoint, headers=headers, timeout=10) as response:
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                return {
                    "provider": provider,
                    "status": "healthy" if response.status == 200 else "degraded",
                    "response_time_ms": int(response_time),
                    "status_code": response.status,
                    "checked_at": datetime.utcnow()
                }
        except asyncio.TimeoutError:
            return {
                "provider": provider,
                "status": "down",
                "response_time_ms": 10000,
                "error": "timeout",
                "checked_at": datetime.utcnow()
            }
        except Exception as e:
            return {
                "provider": provider,
                "status": "down",
                "error": str(e),
                "checked_at": datetime.utcnow()
            }
    
    def _get_provider_api_key(self, provider: str) -> Optional[str]:
        """Get API key for provider from environment"""
        key_map = {
            "groq": "GROQ_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY", 
            "together": "TOGETHER_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "stability": "STABILITY_API_KEY",
            "replicate": "REPLICATE_API_TOKEN",
            "fal": "FAL_API_KEY"
        }
        
        env_key = key_map.get(provider)
        return os.getenv(env_key) if env_key else None
    
    def _calculate_optimal_provider(self, content_type: str, metrics: List[ProviderMetrics], config: Dict) -> OptimizationRecommendation:
        """Calculate optimal provider based on metrics and configuration"""
        if not metrics:
            return None
        
        # Filter providers that meet quality threshold
        qualified_providers = [
            m for m in metrics 
            if m.quality_score >= config.get("quality_threshold", 0.7)
        ]
        
        if not qualified_providers:
            # Fallback to best quality available
            qualified_providers = sorted(metrics, key=lambda x: x.quality_score, reverse=True)[:3]
        
        # Sort by optimization criteria
        primary_metric = config.get("primary_metric", "cost")
        
        if primary_metric == "cost":
            # Optimize for cost (lowest cost first)
            sorted_providers = sorted(qualified_providers, key=lambda x: x.cost_per_unit)
        elif primary_metric == "quality":
            # Optimize for quality (highest quality first)
            sorted_providers = sorted(qualified_providers, key=lambda x: x.quality_score, reverse=True)
        elif primary_metric == "speed":
            # Optimize for speed (highest speed first)
            sorted_providers = sorted(qualified_providers, key=lambda x: x.speed_score, reverse=True)
        else:
            # Default to value score (quality/cost ratio)
            sorted_providers = sorted(qualified_providers, key=lambda x: x.value_score, reverse=True)
        
        if not sorted_providers:
            return None
        
        primary = sorted_providers[0]
        backups = [p.provider_name for p in sorted_providers[1:4]]  # Top 3 backups
        
        # Calculate cost savings vs most expensive option
        most_expensive = max(metrics, key=lambda x: x.cost_per_unit)
        cost_savings = most_expensive.cost_per_unit - primary.cost_per_unit
        
        return OptimizationRecommendation(
            content_type=content_type,
            primary_provider=primary.provider_name,
            backup_providers=backups,
            reasoning=f"Selected {primary.provider_name} for {primary_metric} optimization. Quality: {primary.quality_score:.2f}, Cost: ${primary.cost_per_unit:.4f}",
            cost_savings=cost_savings,
            quality_impact="maintained" if primary.quality_score >= config["quality_threshold"] else "reduced"
        )
    
    def _get_auth_headers(self, provider: str, api_key: str) -> Dict[str, str]:
        """Get authentication headers for provider"""
        header_map = {
            "groq": {"Authorization": f"Bearer {api_key}"},
            "deepseek": {"Authorization": f"Bearer {api_key}"},
            "together": {"Authorization": f"Bearer {api_key}"},
            "anthropic": {"x-api-key": api_key, "anthropic-version": "2025-05-22"},
            "stability": {"Authorization": f"Bearer {api_key}"},
            "replicate": {"Authorization": f"Token {api_key}"},
            "fal": {"Authorization": f"Key {api_key}"}
        }
        
        return header_map.get(provider, {"Authorization": f"Bearer {api_key}"})
    
    def _get_health_check_endpoint(self, provider: str) -> str:
        """Get health check endpoint for provider"""
        endpoints = {
            "groq": "https://api.groq.com/openai/v1/models",
            "deepseek": "https://api.deepseek.com/v1/models",
            "together": "https://api.together.xyz/v1/models",
            "anthropic": "https://api.anthropic.com/v1/models",
            "stability": "https://api.stability.ai/v1/engines/list",
            "replicate": "https://api.replicate.com/v1/predictions",
            "fal": "https://fal.run/models"
        }
        
        return endpoints.get(provider, f"https://api.{provider}.com/v1/models")
    
    # Additional helper methods for database operations...
    async def _save_pricing_updates(self, pricing_updates: List[Dict]):
        """Save pricing updates to database"""
        # Implementation for saving pricing data
        pass
    
    async def _save_health_data(self, health_checks: List[Dict]):
        """Save health check data to database"""
        # Implementation for saving health data
        pass
    
    async def _save_performance_data(self, performance_results: List[Dict]):
        """Save performance benchmark data to database"""
        # Implementation for saving performance data
        pass

# Global monitor instance
_monitor_instance = None

async def get_ai_monitor() -> AIMonitorService:
    """Get global AI monitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = AIMonitorService()
    return _monitor_instance

async def start_ai_monitoring():
    """Start AI monitoring service"""
    monitor = await get_ai_monitor()
    await monitor.start_monitoring()

# CLI command for Railway deployment
if __name__ == "__main__":
    asyncio.run(start_ai_monitoring())