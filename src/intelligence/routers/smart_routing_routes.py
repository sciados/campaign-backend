# src/intelligence/routers/smart_routing_routes.py
"""
SMART ROUTING API ROUTES
✅ Integrates with your existing FastAPI app
✅ Provides monitoring and analytics endpoints
✅ Real-time cost tracking and optimization
"""

import os
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from ..generators.email_generator import EmailSequenceGenerator
from ..generators.factory import get_global_factory

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances for monitoring
_email_generator = None
_factory = None

def get_email_generator():
    """Get or create email generator instance"""
    global _email_generator
    if _email_generator is None:
        _email_generator = EmailSequenceGenerator()
    return _email_generator

def get_global_factory():
    """Get or create factory instance"""
    global _factory
    if _factory is None:
        _factory = get_global_factory()
    return _factory

@router.get("/api/smart-routing/status")
async def get_smart_routing_status():
    """Get smart routing system status"""
    try:
        generator = get_email_generator()
        
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
            "system_status": "operational",
            "ultra_cheap_providers": len(generator.ultra_cheap_providers) if hasattr(generator, 'ultra_cheap_providers') else 0,
            "fallback_providers": len(generator.fallback_providers) if hasattr(generator, 'fallback_providers') else 0,
            "smart_routing_stats": generator.get_smart_routing_stats()
        }
    except Exception as e:
        logger.error(f"❌ Smart routing status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/smart-routing/analytics")
async def get_smart_routing_analytics():
    """Get smart routing analytics and cost data"""
    try:
        generator = get_email_generator()
        factory = get_global_factory()
        
        # Get enhanced cost summary
        cost_summary = generator.get_enhanced_cost_summary()
        
        # Get factory status
        factory_status = factory.get_factory_status()
        
        return {
            "smart_routing_analytics": {
                "email_generator": cost_summary.get("smart_routing", {}),
                "factory_performance": factory_status.get("cost_performance", {}),
                "provider_distribution": factory_status.get("provider_distribution", {}),
                "projections": factory_status.get("projections", {}),
                "ultra_cheap_system": cost_summary.get("ultra_cheap_system", {}),
                "enhanced_features": cost_summary.get("enhanced_features", {})
            },
            "real_time_stats": {
                "total_generations": factory_status.get("cost_performance", {}).get("total_generations", 0),
                "average_cost_per_generation": factory_status.get("cost_performance", {}).get("average_cost_per_generation", 0),
                "total_savings": factory_status.get("cost_performance", {}).get("total_savings", 0),
                "savings_percentage": factory_status.get("cost_performance", {}).get("savings_percentage", 0)
            },
            "system_health": {
                "all_systems_operational": True,
                "last_updated": datetime.utcnow().isoformat(),
                "monitoring_active": True
            }
        }
    except Exception as e:
        logger.error(f"❌ Smart routing analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/smart-routing/provider-performance")
async def get_provider_performance():
    """Get detailed provider performance data"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise HTTPException(status_code=500, detail="Database not configured")
        
        conn = psycopg2.connect(database_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get recent provider performance
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
            ORDER BY total_requests DESC
        """)
        
        performance_data = cur.fetchall()
        
        # Get cost totals
        cur.execute("""
            SELECT 
                SUM(cost_per_1k_tokens) as total_cost,
                COUNT(*) as total_requests
            FROM ai_provider_usage 
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """)
        
        cost_data = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return {
            "provider_performance": [dict(row) for row in performance_data],
            "cost_summary": {
                "total_cost_24h": float(cost_data['total_cost'] or 0),
                "total_requests_24h": int(cost_data['total_requests'] or 0),
                "average_cost_per_request": float(cost_data['total_cost'] or 0) / max(1, int(cost_data['total_requests'] or 1))
            },
            "data_freshness": "24_hours",
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Provider performance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/smart-routing/test-generation")
async def test_smart_generation():
    """Test smart routing with sample generation"""
    try:
        generator = get_email_generator()
        
        # Test data
        test_intelligence = {
            "offer_intelligence": {
                "insights": ["Product called SMARTTEST helps with optimization"],
                "benefits": ["cost savings", "performance improvement"],
                "products": ["SMARTTEST"]
            }
        }
        
        # Generate test content
        result = await generator.generate_email_sequence(
            test_intelligence, 
            {"length": "2"}
        )
        
        return {
            "test_successful": True,
            "content_generated": bool(result.get("content")),
            "provider_used": result.get("metadata", {}).get("ai_provider_used"),
            "generation_cost": result.get("metadata", {}).get("generation_cost", 0),
            "smart_routing_enabled": result.get("metadata", {}).get("smart_routing_enabled", False),
            "response_summary": {
                "emails_generated": len(result.get("content", {}).get("emails", [])),
                "total_cost": result.get("metadata", {}).get("generation_cost", 0),
                "generation_time": result.get("metadata", {}).get("generation_time", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Test generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/smart-routing/cost-projections")
async def get_cost_projections():
    """Get cost projections and savings estimates"""
    try:
        factory = get_global_factory()
        factory_status = factory.get_factory_status()
        
        # Current performance
        cost_perf = factory_status.get("cost_performance", {})
        projections = factory_status.get("projections", {})
        
        # Calculate detailed projections
        current_cost = cost_perf.get("total_cost", 0)
        current_savings = cost_perf.get("total_savings", 0)
        total_requests = cost_perf.get("total_generations", 1)
        
        # OpenAI baseline cost (estimated)
        openai_baseline = 0.030  # $0.030 per 1K tokens
        current_avg_cost = current_cost / max(1, total_requests)
        
        return {
            "current_performance": {
                "total_requests": total_requests,
                "total_cost": current_cost,
                "average_cost_per_request": current_avg_cost,
                "total_savings": current_savings,
                "savings_percentage": cost_perf.get("savings_percentage", 0)
            },
            "projections": {
                "daily_1000_users": {
                    "ultra_cheap_cost": current_avg_cost * 1000,
                    "openai_cost": openai_baseline * 1000,
                    "daily_savings": (openai_baseline - current_avg_cost) * 1000
                },
                "monthly_1000_users": {
                    "ultra_cheap_cost": projections.get("monthly_cost_1000_users", 0),
                    "openai_cost": openai_baseline * 1000 * 30,
                    "monthly_savings": projections.get("monthly_savings_1000_users", 0)
                },
                "annual_1000_users": {
                    "ultra_cheap_cost": projections.get("monthly_cost_1000_users", 0) * 12,
                    "openai_cost": openai_baseline * 1000 * 365,
                    "annual_savings": projections.get("annual_savings_1000_users", 0)
                }
            },
            "roi_analysis": {
                "cost_reduction_percentage": ((openai_baseline - current_avg_cost) / openai_baseline) * 100,
                "break_even_requests": 1,  # Immediate savings
                "payback_period": "immediate"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Cost projections error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/api/smart-routing/health")
async def health_check():
    """Health check for smart routing system"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "smart_routing": "operational",
            "database": "connected" if os.getenv("DATABASE_URL") else "not_configured",
            "monitoring": "enabled" if os.getenv("AI_MONITORING_ENABLED", "true").lower() == "true" else "disabled"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Add these routes to your main FastAPI app
def include_smart_routing_routes(app):
    """Include smart routing routes in your FastAPI app"""
    app.include_router(router, prefix="", tags=["smart-routing"])
    logger.info("🚀 Smart Routing Routes: Added to FastAPI app")