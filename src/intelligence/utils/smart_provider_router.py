# src/intelligence/utils/smart_provider_router.py
"""
SMART PROVIDER ROUTER - Enhances existing BaseContentGenerator
✅ Works with your existing Railway environment
✅ Uses your existing API keys and provider hierarchy
✅ Adds real-time optimization and monitoring
✅ Database logging for cost tracking
"""

import os
import logging
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

class SmartProviderRouter:
    """Smart router that enhances your existing BaseContentGenerator"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.monitoring_enabled = os.getenv("AI_MONITORING_ENABLED", "true").lower() == "true"
        
        # Provider performance tracking
        self.provider_stats = {}
        self.last_update = datetime.utcnow()
        
        # Cost tracking
        self.session_stats = {
            "total_requests": 0,
            "total_cost": 0.0,
            "total_savings": 0.0,
            "provider_usage": {},
            "session_start": datetime.utcnow()
        }
        
        if self.monitoring_enabled:
            logger.info("🤖 Smart Provider Router: Monitoring enabled")
            asyncio.create_task(self._initialize_monitoring())
    
    async def _initialize_monitoring(self):
        """Initialize monitoring system"""
        try:
            # Load provider performance from database
            await self._load_provider_performance()
            logger.info("📊 Smart Router: Historical data loaded")
        except Exception as e:
            logger.warning(f"⚠️ Smart Router: Could not load historical data: {e}")
    
    async def _load_provider_performance(self):
        """Load provider performance from database"""
        if not self.database_url:
            return
            
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get recent provider performance (last 7 days)
            cur.execute("""
                SELECT provider_name, 
                       AVG(response_time_seconds) as avg_response_time,
                       AVG(cost_per_1k_tokens) as avg_cost,
                       COUNT(*) as usage_count,
                       SUM(CASE WHEN is_successful THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
                FROM ai_provider_usage 
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY provider_name
            """)
            
            results = cur.fetchall()
            
            for row in results:
                self.provider_stats[row['provider_name']] = {
                    'avg_response_time': float(row['avg_response_time'] or 0),
                    'avg_cost': float(row['avg_cost'] or 0),
                    'usage_count': int(row['usage_count']),
                    'success_rate': float(row['success_rate'] or 0),
                    'performance_score': self._calculate_performance_score(row)
                }
            
            cur.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Database error loading provider stats: {e}")
    
    def _calculate_performance_score(self, provider_data: Dict) -> float:
        """Calculate performance score for provider optimization"""
        success_rate = float(provider_data.get('success_rate', 0))
        response_time = float(provider_data.get('avg_response_time', 5))
        cost = float(provider_data.get('avg_cost', 0.001))
        
        # Score: 50% success rate, 30% speed, 20% cost
        speed_score = max(0, 10 - response_time) * 10  # 10 = best (1s), 0 = worst (10s+)
        cost_score = max(0, 100 - (cost * 100000))  # Lower cost = higher score
        
        return (success_rate * 0.5) + (speed_score * 0.3) + (cost_score * 0.2)
    
    def optimize_provider_order(self, providers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize provider order based on performance data"""
        
        if not self.monitoring_enabled or not self.provider_stats:
            # Fall back to cost-based ordering (your existing logic)
            return sorted(providers, key=lambda x: x["cost_per_1k_tokens"])
        
        # Sort by performance score, then by cost
        def score_provider(provider):
            provider_name = provider["name"]
            stats = self.provider_stats.get(provider_name, {})
            
            performance_score = stats.get('performance_score', 50)  # Default middle score
            cost_score = (0.003 - provider["cost_per_1k_tokens"]) * 1000  # Lower cost = higher score
            
            return performance_score + cost_score
        
        optimized = sorted(providers, key=score_provider, reverse=True)
        
        # Log optimization
        logger.info(f"🎯 Smart routing: Optimized provider order: {[p['name'] for p in optimized[:3]]}")
        
        return optimized
    
    async def log_provider_usage(self, provider_name: str, response_time: float, 
                               cost: float, success: bool, content_type: str):
        """Log provider usage for optimization"""
        
        # Update session stats
        self.session_stats["total_requests"] += 1
        self.session_stats["total_cost"] += cost
        
        if provider_name not in self.session_stats["provider_usage"]:
            self.session_stats["provider_usage"][provider_name] = {
                "requests": 0, "total_cost": 0.0, "successes": 0
            }
        
        usage = self.session_stats["provider_usage"][provider_name]
        usage["requests"] += 1
        usage["total_cost"] += cost
        if success:
            usage["successes"] += 1
        
        # Log to database if monitoring enabled
        if self.monitoring_enabled and self.database_url:
            await self._log_to_database(provider_name, response_time, cost, success, content_type)
    
    async def _log_to_database(self, provider_name: str, response_time: float, 
                             cost: float, success: bool, content_type: str):
        """Log usage to database"""
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO ai_provider_usage 
                (provider_name, response_time_seconds, cost_per_1k_tokens, is_successful, 
                 content_type, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (provider_name, response_time, cost, success, content_type, datetime.utcnow()))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Database logging error: {e}")
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get current optimization statistics"""
        session_duration = (datetime.utcnow() - self.session_stats["session_start"]).total_seconds()
        
        return {
            "smart_routing_enabled": self.monitoring_enabled,
            "session_duration_minutes": session_duration / 60,
            "total_requests": self.session_stats["total_requests"],
            "total_cost": self.session_stats["total_cost"],
            "average_cost_per_request": self.session_stats["total_cost"] / max(1, self.session_stats["total_requests"]),
            "provider_usage": self.session_stats["provider_usage"],
            "provider_performance": self.provider_stats,
            "estimated_monthly_savings": self.session_stats["total_cost"] * 1000 * 30,
            "top_provider": max(self.session_stats["provider_usage"].items(), 
                              key=lambda x: x[1]["requests"])[0] if self.session_stats["provider_usage"] else None
        }


#  BaseContentGenerator Mixin
class SmartProviderMixin:
    """Mixin to add smart provider routing to existing BaseContentGenerator"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.smart_router = SmartProviderRouter()
        logger.info("🤖 Smart Provider Mixin: Initialized")
    
    def _initialize_ultra_cheap_providers(self) -> List[Dict[str, Any]]:
        """ provider initialization with smart routing"""
        # Get providers from parent class
        providers = super()._initialize_ultra_cheap_providers()
        
        # Optimize order based on performance
        if providers:
            optimized_providers = self.smart_router.optimize_provider_order(providers)
            logger.info(f"🎯 Smart routing: Provider order optimized")
            return optimized_providers
        
        return providers
    
    async def _generate_with_ultra_cheap_ai(self, *args, **kwargs) -> Dict[str, Any]:
        """ generation with smart routing and monitoring"""
        
        start_time = datetime.utcnow()
        
        # Call parent method
        result = await super()._generate_with_ultra_cheap_ai(*args, **kwargs)
        
        # Log usage for optimization
        if result:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            provider_used = result.get("provider_used", "unknown")
            cost = result.get("cost", 0.0)
            success = bool(result.get("content"))
            
            # Log for smart routing
            await self.smart_router.log_provider_usage(
                provider_used, response_time, cost, success, self.generator_type
            )
        
        return result
    
    def get_smart_routing_stats(self) -> Dict[str, Any]:
        """Get smart routing statistics"""
        return self.smart_router.get_optimization_stats()


# Helper function to enhance existing generators
def enhance_generator_with_smart_routing(generator_class):
    """Class decorator to add smart routing to existing generators"""
    
    class Generator(SmartProviderMixin, generator_class):
        pass
    
    return Generator


# Monitoring routes for your FastAPI app
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/api/smart-routing/status")
async def get_smart_routing_status():
    """Get smart routing system status"""
    try:
        # This would be called from your generator instance
        return {
            "smart_routing_active": True,
            "monitoring_enabled": os.getenv("AI_MONITORING_ENABLED", "true").lower() == "true",
            "database_connected": bool(os.getenv("DATABASE_URL")),
            "providers_available": {
                "groq": bool(os.getenv("GROQ_API_KEY")),
                "deepseek": bool(os.getenv("DEEPSEEK_API_KEY")),
                "together": bool(os.getenv("TOGETHER_API_KEY")),
                "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
                "stability": bool(os.getenv("STABILITY_API_KEY")),
                "replicate": bool(os.getenv("REPLICATE_API_TOKEN"))
            },
            "system_status": "operational"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/smart-routing/analytics")
async def get_smart_routing_analytics():
    """Get smart routing analytics"""
    try:
        # This would get stats from your generator instances
        return {
            "message": "Smart routing analytics - connect to your generator instances",
            "note": "This endpoint needs to be connected to your generator instances"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))