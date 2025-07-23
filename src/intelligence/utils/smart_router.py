# src/intelligence/utils/smart_router.py
"""
COMPLETE SMART AI ROUTER - PRODUCTION READY
🤖 Automatically selects optimal AI providers based on real-time monitoring
💰 Maximizes cost savings while maintaining quality
🔄 Adapts to provider availability and performance
📊 Comprehensive monitoring and analytics
"""

import os
import logging
import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

@dataclass
class ProviderConfig:
    """Provider configuration with performance metrics"""
    name: str
    env_key: str
    base_cost: float
    models: Dict[str, str]
    strengths: List[str]
    performance_score: float = 0.0
    success_rate: float = 100.0
    avg_response_time: float = 0.0
    last_used: Optional[datetime] = None
    is_available: bool = True

class CompleteSmartRouter:
    """Complete smart routing system with real-time optimization"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.monitoring_enabled = os.getenv("AI_MONITORING_ENABLED", "true").lower() == "true"
        self.cache_ttl = int(os.getenv("AI_CACHE_TTL_SECONDS", "300"))
        
        # Provider configurations
        self.providers = self._initialize_provider_configs()
        
        # Performance tracking
        self.performance_cache = {}
        self.last_cache_update = datetime.now(timezone.utc).astimezone().isoformat()
        
        # Session statistics
        self.session_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "total_cost": 0.0,
            "total_savings": 0.0,
            "provider_usage": {},
            "content_type_usage": {},
            "session_start": datetime.now(timezone.utc).astimezone().isoformat()
        }
        
        # Initialize monitoring
        if self.monitoring_enabled:
            asyncio.create_task(self._start_monitoring())
        
        logger.info(f"🤖 Complete Smart Router: {len(self.providers)} providers configured")
    
    def _initialize_provider_configs(self) -> Dict[str, ProviderConfig]:
        """Initialize provider configurations"""
        configs = {}
        
        # Text providers
        text_providers = [
            ProviderConfig(
                name="groq",
                env_key="GROQ_API_KEY",
                base_cost=0.00013,  # Updated 2025 pricing
                models={"text": "llama-3.3-70b-versatile"},
                strengths=["speed", "cost", "conversational"]
            ),
            ProviderConfig(
                name="deepseek",
                env_key="DEEPSEEK_API_KEY", 
                base_cost=0.00055,
                models={"text": "deepseek-chat"},
                strengths=["reasoning", "math", "analysis"]
            ),
            ProviderConfig(
                name="together",
                env_key="TOGETHER_API_KEY",
                base_cost=0.0008,
                models={"text": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"},
                strengths=["creativity", "long_form", "versatility"]
            ),
            ProviderConfig(
                name="anthropic",
                env_key="ANTHROPIC_API_KEY",
                base_cost=0.009,  # Claude Sonnet 4 pricing
                models={"text": "claude-sonnet-4-20250514"},
                strengths=["quality", "safety", "complex_reasoning"]
            )
        ]
        
        # Image providers
        image_providers = [
            ProviderConfig(
                name="stability",
                env_key="STABILITY_API_KEY",
                base_cost=0.002,
                models={"image": "stable-diffusion-xl"},
                strengths=["cost", "quality", "speed"]
            ),
            ProviderConfig(
                name="replicate",
                env_key="REPLICATE_API_TOKEN",
                base_cost=0.004,
                models={"image": "various"},
                strengths=["variety", "specialized_models"]
            ),
            ProviderConfig(
                name="fal",
                env_key="FAL_API_KEY",
                base_cost=0.005,
                models={"image": "various"},
                strengths=["speed", "modern_models"]
            )
        ]
        
        # Check availability and add to configs
        for provider in text_providers + image_providers:
            if os.getenv(provider.env_key):
                provider.is_available = True
                configs[provider.name] = provider
                logger.info(f"✅ {provider.name}: Available (${provider.base_cost:.5f})")
            else:
                logger.warning(f"⚠️ {provider.name}: API key not found")
        
        return configs
    
    async def _start_monitoring(self):
        """Start continuous monitoring of provider performance"""
        logger.info("📊 Smart Router: Starting performance monitoring")
        
        while True:
            try:
                await self._update_performance_cache()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(30)  # Retry after 30 seconds
    
    async def _update_performance_cache(self):
        """Update provider performance cache from database"""
        if not self.database_url:
            return
        
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get performance data from last 24 hours
            cur.execute("""
                SELECT 
                    provider_name,
                    content_type,
                    COUNT(*) as total_requests,
                    AVG(response_time_seconds) as avg_response_time,
                    AVG(cost_per_1k_tokens) as avg_cost,
                    SUM(CASE WHEN is_successful THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate,
                    MAX(created_at) as last_used
                FROM ai_provider_usage 
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                GROUP BY provider_name, content_type
            """)
            
            results = cur.fetchall()
            
            # Update provider performance
            for row in results:
                provider_name = row['provider_name']
                if provider_name in self.providers:
                    provider = self.providers[provider_name]
                    provider.success_rate = float(row['success_rate'] or 100)
                    provider.avg_response_time = float(row['avg_response_time'] or 0)
                    provider.last_used = row['last_used']
                    
                    # Calculate performance score
                    provider.performance_score = self._calculate_performance_score(
                        provider.success_rate,
                        provider.avg_response_time,
                        provider.base_cost
                    )
            
            cur.close()
            conn.close()
            
            self.last_cache_update = datetime.now(timezone.utc).astimezone().isoformat()
            logger.debug("📊 Performance cache updated")
            
        except Exception as e:
            logger.error(f"❌ Performance cache update failed: {e}")
    
    def _calculate_performance_score(self, success_rate: float, response_time: float, cost: float) -> float:
        """Calculate comprehensive performance score"""
        # Normalize metrics (0-100 scale)
        success_score = success_rate  # Already 0-100
        
        # Speed score (penalize slow responses)
        speed_score = max(0, 100 - (response_time * 20))
        
        # Cost score (reward lower costs)
        cost_score = max(0, 100 - (cost * 10000))
        
        # Weighted combination: 50% success, 30% speed, 20% cost
        return (success_score * 0.5) + (speed_score * 0.3) + (cost_score * 0.2)
    
    def get_optimal_provider(self, content_type: str, required_strength: str = None) -> Optional[ProviderConfig]:
        """Get optimal provider based on real-time performance"""
        
        # Filter providers by content type
        if content_type in ["text", "email_sequence", "social_posts", "ad_copy", "blog_post"]:
            content_providers = [p for p in self.providers.values() if "text" in p.models]
        elif content_type == "image":
            content_providers = [p for p in self.providers.values() if "image" in p.models]
        else:
            content_providers = list(self.providers.values())
        
        # Filter by required strength if specified
        if required_strength:
            content_providers = [p for p in content_providers if required_strength in p.strengths]
        
        # Filter available providers
        available_providers = [p for p in content_providers if p.is_available]
        
        if not available_providers:
            logger.warning(f"⚠️ No available providers for {content_type}")
            return None
        
        # Sort by performance score (highest first)
        optimal_providers = sorted(available_providers, key=lambda p: p.performance_score, reverse=True)
        
        # Log selection
        selected = optimal_providers[0]
        logger.info(f"🎯 Optimal provider for {content_type}: {selected.name} (score: {selected.performance_score:.1f})")
        
        return selected
    
    def get_provider_hierarchy(self, content_type: str) -> List[ProviderConfig]:
        """Get optimized provider hierarchy for failover"""
        
        # Get all suitable providers
        if content_type in ["text", "email_sequence", "social_posts", "ad_copy", "blog_post"]:
            suitable_providers = [p for p in self.providers.values() if "text" in p.models and p.is_available]
        elif content_type == "image":
            suitable_providers = [p for p in self.providers.values() if "image" in p.models and p.is_available]
        else:
            suitable_providers = [p for p in self.providers.values() if p.is_available]
        
        # Sort by performance score, then by cost
        return sorted(suitable_providers, key=lambda p: (p.performance_score, -p.base_cost), reverse=True)
    
    async def log_provider_usage(self, provider_name: str, content_type: str, response_time: float, 
                               cost: float, success: bool, tokens_used: int = 0):
        """Log provider usage to database"""
        
        # Update session stats
        self.session_stats["total_requests"] += 1
        if success:
            self.session_stats["successful_requests"] += 1
        
        self.session_stats["total_cost"] += cost
        
        # Calculate savings vs most expensive provider
        if content_type in ["text", "email_sequence", "social_posts"]:
            expensive_cost = 0.030  # OpenAI GPT-4 baseline
        else:
            expensive_cost = 0.040  # DALL-E baseline
        
        savings = expensive_cost - cost
        self.session_stats["total_savings"] += savings
        
        # Update provider usage
        if provider_name not in self.session_stats["provider_usage"]:
            self.session_stats["provider_usage"][provider_name] = {
                "requests": 0, "successes": 0, "total_cost": 0.0, "total_savings": 0.0
            }
        
        usage = self.session_stats["provider_usage"][provider_name]
        usage["requests"] += 1
        if success:
            usage["successes"] += 1
        usage["total_cost"] += cost
        usage["total_savings"] += savings
        
        # Update content type usage
        if content_type not in self.session_stats["content_type_usage"]:
            self.session_stats["content_type_usage"][content_type] = {"requests": 0, "cost": 0.0}
        
        self.session_stats["content_type_usage"][content_type]["requests"] += 1
        self.session_stats["content_type_usage"][content_type]["cost"] += cost
        
        # Log to database
        if self.monitoring_enabled and self.database_url:
            await self._log_to_database(provider_name, content_type, response_time, cost, success, tokens_used)
    
    async def _log_to_database(self, provider_name: str, content_type: str, response_time: float,
                             cost: float, success: bool, tokens_used: int):
        """Log usage to database"""
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO ai_provider_usage 
                (provider_name, content_type, response_time_seconds, cost_per_1k_tokens, 
                 is_successful, tokens_used, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (provider_name, content_type, response_time, cost, success, tokens_used, datetime.now(timezone.utc).astimezone().isoformat()))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Database logging failed: {e}")
    
    def get_routing_decision(self, content_type: str, required_strength: str = None) -> Dict[str, Any]:
        """Get routing decision with full context"""
        
        optimal_provider = self.get_optimal_provider(content_type, required_strength)
        hierarchy = self.get_provider_hierarchy(content_type)
        
        if not optimal_provider:
            return {
                "success": False,
                "error": "No available providers",
                "alternatives": []
            }
        
        return {
            "success": True,
            "primary_provider": {
                "name": optimal_provider.name,
                "cost": optimal_provider.base_cost,
                "performance_score": optimal_provider.performance_score,
                "success_rate": optimal_provider.success_rate,
                "strengths": optimal_provider.strengths
            },
            "fallback_providers": [
                {
                    "name": p.name,
                    "cost": p.base_cost,
                    "performance_score": p.performance_score
                } for p in hierarchy[1:4]  # Next 3 providers
            ],
            "routing_strategy": "performance_optimized",
            "content_type": content_type,
            "required_strength": required_strength,
            "decision_time": datetime.now(timezone.utc).astimezone().isoformat()
        }
    
    def get_system_analytics(self) -> Dict[str, Any]:
        """Get comprehensive system analytics"""
        
        session_duration = (datetime.now(timezone.utc).astimezone().isoformat() - self.session_stats["session_start"]).total_seconds()
        
        return {
            "system_status": {
                "monitoring_enabled": self.monitoring_enabled,
                "providers_configured": len(self.providers),
                "providers_available": len([p for p in self.providers.values() if p.is_available]),
                "last_performance_update": self.last_cache_update.isoformat(),
                "session_duration_hours": session_duration / 3600
            },
            "performance_metrics": {
                "total_requests": self.session_stats["total_requests"],
                "successful_requests": self.session_stats["successful_requests"],
                "success_rate": (self.session_stats["successful_requests"] / max(1, self.session_stats["total_requests"])) * 100,
                "total_cost": self.session_stats["total_cost"],
                "total_savings": self.session_stats["total_savings"],
                "average_cost_per_request": self.session_stats["total_cost"] / max(1, self.session_stats["total_requests"]),
                "cost_savings_percentage": (self.session_stats["total_savings"] / max(0.001, self.session_stats["total_savings"] + self.session_stats["total_cost"])) * 100
            },
            "provider_performance": {
                name: {
                    "performance_score": provider.performance_score,
                    "success_rate": provider.success_rate,
                    "avg_response_time": provider.avg_response_time,
                    "base_cost": provider.base_cost,
                    "is_available": provider.is_available,
                    "usage_stats": self.session_stats["provider_usage"].get(name, {})
                }
                for name, provider in self.providers.items()
            },
            "content_type_usage": self.session_stats["content_type_usage"],
            "projections": {
                "daily_cost_1000_users": self.session_stats["total_cost"] * 1000,
                "daily_savings_1000_users": self.session_stats["total_savings"] * 1000,
                "monthly_cost_1000_users": self.session_stats["total_cost"] * 1000 * 30,
                "monthly_savings_1000_users": self.session_stats["total_savings"] * 1000 * 30,
                "annual_savings_1000_users": self.session_stats["total_savings"] * 1000 * 365
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        
        health_status = {
            "overall_health": "healthy",
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
            "components": {}
        }
        
        # Check database connectivity
        try:
            if self.database_url:
                conn = psycopg2.connect(self.database_url)
                conn.close()
                health_status["components"]["database"] = "healthy"
            else:
                health_status["components"]["database"] = "not_configured"
        except Exception as e:
            health_status["components"]["database"] = f"error: {e}"
            health_status["overall_health"] = "degraded"
        
        # Check provider availability
        available_providers = [p for p in self.providers.values() if p.is_available]
        if len(available_providers) == 0:
            health_status["components"]["providers"] = "critical"
            health_status["overall_health"] = "critical"
        elif len(available_providers) < len(self.providers) * 0.5:
            health_status["components"]["providers"] = "degraded"
            health_status["overall_health"] = "degraded"
        else:
            health_status["components"]["providers"] = "healthy"
        
        # Check monitoring
        if self.monitoring_enabled:
            cache_age = (datetime.now(timezone.utc).astimezone().isoformat() - self.last_cache_update).total_seconds()
            if cache_age > 300:  # 5 minutes
                health_status["components"]["monitoring"] = "stale"
                health_status["overall_health"] = "degraded"
            else:
                health_status["components"]["monitoring"] = "healthy"
        else:
            health_status["components"]["monitoring"] = "disabled"
        
        return health_status

# Global instance
_global_smart_router = None

def get_smart_router() -> CompleteSmartRouter:
    """Get or create global smart router instance"""
    global _global_smart_router
    
    if _global_smart_router is None:
        _global_smart_router = CompleteSmartRouter()
    
    return _global_smart_router

# Convenience functions
async def get_optimal_provider_for_content(content_type: str, required_strength: str = None) -> Optional[ProviderConfig]:
    """Get optimal provider for content type"""
    router = get_smart_router()
    return router.get_optimal_provider(content_type, required_strength)

async def log_ai_usage(provider_name: str, content_type: str, response_time: float, 
                      cost: float, success: bool, tokens_used: int = 0):
    """Log AI usage for optimization"""
    router = get_smart_router()
    await router.log_provider_usage(provider_name, content_type, response_time, cost, success, tokens_used)

def get_routing_analytics() -> Dict[str, Any]:
    """Get routing analytics"""
    router = get_smart_router()
    return router.get_system_analytics()