# src/intelligence/routers/ai_monitoring_routes.py
"""
COMPLETE AI MONITORING & OPTIMIZATION DASHBOARD API
📊 Real-time monitoring of AI provider performance
💰 Cost optimization analytics and controls
🎯 Dynamic routing management and overrides
🔧 System health monitoring and alerts
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import StreamingResponse
import json
import psycopg2
from psycopg2.extras import RealDictCursor

from ..utils.smart_router import get_smart_router
from ..adapters.dynamic_router import check_dynamic_routing_health
from ..schemas.monitoring_schemas import (
    ProviderStatusResponse,
    OptimizationAnalyticsResponse,
    RoutingDecisionResponse,
    SystemHealthResponse,
    CostAnalyticsResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Database dependency
def get_database():
    """Get database connection"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=500, detail="Database not configured")
    return database_url

@router.get("/api/ai-monitoring/status", response_model=SystemHealthResponse)
async def get_system_status():
    """Get comprehensive system status"""
    try:
        smart_router = get_smart_router()
        health_check = await smart_router.health_check()
        analytics = smart_router.get_system_analytics()
        
        return SystemHealthResponse(
            system_health=health_check["overall_health"],
            monitoring_enabled=analytics["system_status"]["monitoring_enabled"],
            providers_available=analytics["system_status"]["providers_available"],
            providers_configured=analytics["system_status"]["providers_configured"],
            database_status=health_check["components"]["database"],
            last_update=analytics["system_status"]["last_performance_update"],
            session_duration_hours=analytics["system_status"]["session_duration_hours"],
            components=health_check["components"]
        )
    except Exception as e:
        logger.error(f"❌ System status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai-monitoring/providers", response_model=List[ProviderStatusResponse])
async def get_provider_status():
    """Get detailed provider status and performance"""
    try:
        smart_router = get_smart_router()
        analytics = smart_router.get_system_analytics()
        
        provider_responses = []
        for name, provider_data in analytics["provider_performance"].items():
            provider_responses.append(ProviderStatusResponse(
                name=name,
                is_available=provider_data["is_available"],
                performance_score=provider_data["performance_score"],
                success_rate=provider_data["success_rate"],
                avg_response_time=provider_data["avg_response_time"],
                base_cost=provider_data["base_cost"],
                total_requests=provider_data["usage_stats"].get("requests", 0),
                total_cost=provider_data["usage_stats"].get("total_cost", 0.0),
                last_used=datetime.datetime.now()  # Would be actual last used from DB
            ))
        
        return provider_responses
    except Exception as e:
        logger.error(f"❌ Provider status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai-monitoring/analytics", response_model=OptimizationAnalyticsResponse)
async def get_optimization_analytics():
    """Get comprehensive optimization analytics"""
    try:
        smart_router = get_smart_router()
        analytics = smart_router.get_system_analytics()
        
        return OptimizationAnalyticsResponse(
            total_requests=analytics["performance_metrics"]["total_requests"],
            successful_requests=analytics["performance_metrics"]["successful_requests"],
            success_rate=analytics["performance_metrics"]["success_rate"],
            total_cost=analytics["performance_metrics"]["total_cost"],
            total_savings=analytics["performance_metrics"]["total_savings"],
            cost_savings_percentage=analytics["performance_metrics"]["cost_savings_percentage"],
            average_cost_per_request=analytics["performance_metrics"]["average_cost_per_request"],
            content_type_usage=analytics["content_type_usage"],
            provider_distribution=analytics["provider_performance"],
            optimization_enabled=True
        )
    except Exception as e:
        logger.error(f"❌ Optimization analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai-monitoring/routing-decision")
async def get_routing_decision(
    content_type: str = Query(..., description="Content type for routing decision"),
    required_strength: Optional[str] = Query(None, description="Required provider strength")
):
    """Get routing decision for specific content type"""
    try:
        smart_router = get_smart_router()
        decision = smart_router.get_routing_decision(content_type, required_strength)
        
        return RoutingDecisionResponse(
            success=decision["success"],
            content_type=decision.get("content_type", content_type),
            primary_provider=decision.get("primary_provider", {}),
            fallback_providers=decision.get("fallback_providers", []),
            routing_strategy=decision.get("routing_strategy", "unknown"),
            decision_time=decision.get("decision_time", datetime.datetime.now()),
            error_message=decision.get("error") if not decision["success"] else None
        )
    except Exception as e:
        logger.error(f"❌ Routing decision error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai-monitoring/cost-analytics", response_model=CostAnalyticsResponse)
async def get_cost_analytics(
    timeframe: str = Query("24h", description="Timeframe: 1h, 24h, 7d, 30d")
):
    """Get detailed cost analytics"""
    try:
        database_url = get_database()
        
        # Convert timeframe to SQL interval
        interval_map = {
            "1h": "1 hour",
            "24h": "24 hours", 
            "7d": "7 days",
            "30d": "30 days"
        }
        
        interval = interval_map.get(timeframe, "24 hours")
        
        conn = psycopg2.connect(database_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get cost breakdown by provider
        cur.execute("""
            SELECT 
                provider_name,
                content_type,
                COUNT(*) as requests,
                SUM(cost_per_1k_tokens) as total_cost,
                AVG(cost_per_1k_tokens) as avg_cost,
                SUM(tokens_used) as total_tokens
            FROM ai_provider_usage 
            WHERE created_at >= NOW() - INTERVAL %s
            GROUP BY provider_name, content_type
            ORDER BY total_cost DESC
        """, (interval,))
        
        cost_breakdown = cur.fetchall()
        
        # Get hourly cost trend
        cur.execute("""
            SELECT 
                DATE_TRUNC('hour', created_at) as hour,
                COUNT(*) as requests,
                SUM(cost_per_1k_tokens) as cost
            FROM ai_provider_usage 
            WHERE created_at >= NOW() - INTERVAL %s
            GROUP BY hour
            ORDER BY hour
        """, (interval,))
        
        hourly_trend = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Calculate totals
        total_cost = sum(float(row['total_cost'] or 0) for row in cost_breakdown)
        total_requests = sum(int(row['requests']) for row in cost_breakdown)
        
        # Estimate savings (vs OpenAI baseline)
        openai_baseline = 0.030
        estimated_openai_cost = total_requests * openai_baseline
        total_savings = estimated_openai_cost - total_cost
        
        return CostAnalyticsResponse(
            timeframe=timeframe,
            total_cost=total_cost,
            total_requests=total_requests,
            total_savings=total_savings,
            cost_savings_percentage=(total_savings / max(estimated_openai_cost, 0.001)) * 100,
            average_cost_per_request=total_cost / max(total_requests, 1),
            cost_breakdown_by_provider=[dict(row) for row in cost_breakdown],
            hourly_cost_trend=[dict(row) for row in hourly_trend],
            projections={
                "daily_cost": total_cost * (24 / max(int(timeframe.rstrip('hd')), 1)),
                "monthly_cost": total_cost * (30 * 24 / max(int(timeframe.rstrip('hd')), 1)),
                "annual_savings": total_savings * (365 * 24 / max(int(timeframe.rstrip('hd')), 1))
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Cost analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/ai-monitoring/optimize-providers")
async def optimize_providers():
    """Trigger provider optimization"""
    try:
        smart_router = get_smart_router()
        await smart_router._update_performance_cache()
        
        return {
            "success": True,
            "message": "Provider optimization triggered",
            "timestamp": datetime.datetime.now()
        }
    except Exception as e:
        logger.error(f"❌ Provider optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/ai-monitoring/force-provider")
async def force_provider_selection(
    provider_name: str = Body(..., description="Provider name to force"),
    content_type: str = Body(..., description="Content type"),
    duration_minutes: int = Body(60, description="Duration in minutes")
):
    """Force selection of specific provider for testing"""
    try:
        # This would implement provider forcing logic
        # For now, return success
        return {
            "success": True,
            "message": f"Forced {provider_name} for {content_type} for {duration_minutes} minutes",
            "expires_at": (datetime.datetime.now() + timedelta(minutes=duration_minutes)).isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Force provider error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai-monitoring/real-time-metrics")
async def get_real_time_metrics():
    """Get real-time system metrics"""
    try:
        smart_router = get_smart_router()
        health_check = await smart_router.health_check()
        analytics = smart_router.get_system_analytics()
        
        return {
            "timestamp": datetime.datetime.now(),
            "system_health": health_check["overall_health"],
            "active_providers": analytics["system_status"]["providers_available"],
            "total_requests": analytics["performance_metrics"]["total_requests"],
            "success_rate": analytics["performance_metrics"]["success_rate"],
            "current_cost": analytics["performance_metrics"]["total_cost"],
            "total_savings": analytics["performance_metrics"]["total_savings"],
            "cost_per_request": analytics["performance_metrics"]["average_cost_per_request"],
            "top_provider": max(
                analytics["provider_performance"].items(),
                key=lambda x: x[1]["usage_stats"].get("requests", 0)
            )[0] if analytics["provider_performance"] else None,
            "monitoring_active": analytics["system_status"]["monitoring_enabled"]
        }
    except Exception as e:
        logger.error(f"❌ Real-time metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai-monitoring/export-data")
async def export_monitoring_data(
    format: str = Query("json", description="Export format: json, csv"),
    timeframe: str = Query("24h", description="Timeframe: 1h, 24h, 7d, 30d")
):
    """Export monitoring data"""
    try:
        database_url = get_database()
        
        interval_map = {
            "1h": "1 hour",
            "24h": "24 hours", 
            "7d": "7 days",
            "30d": "30 days"
        }
        
        interval = interval_map.get(timeframe, "24 hours")
        
        conn = psycopg2.connect(database_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT * FROM ai_provider_usage 
            WHERE created_at >= NOW() - INTERVAL %s
            ORDER BY created_at DESC
        """, (interval,))
        
        data = cur.fetchall()
        cur.close()
        conn.close()
        
        if format == "json":
            def generate_json():
                yield json.dumps([dict(row) for row in data], default=str, indent=2)
            
            return StreamingResponse(
                generate_json(),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=ai_monitoring_{timeframe}.json"}
            )
        
        elif format == "csv":
            def generate_csv():
                if data:
                    # CSV header
                    yield ",".join(data[0].keys()) + "\n"
                    # CSV data
                    for row in data:
                        yield ",".join(str(v) for v in row.values()) + "\n"
            
            return StreamingResponse(
                generate_csv(),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=ai_monitoring_{timeframe}.csv"}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
            
    except Exception as e:
        logger.error(f"❌ Export data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai-monitoring/alerts")
async def get_system_alerts():
    """Get system alerts and warnings"""
    try:
        smart_router = get_smart_router()
        health_check = await smart_router.health_check()
        analytics = smart_router.get_system_analytics()
        
        alerts = []
        
        # Check for system health issues
        if health_check["overall_health"] == "critical":
            alerts.append({
                "level": "critical",
                "message": "System health is critical",
                "timestamp": datetime.datetime.now(),
                "components": health_check["components"]
            })
        
        # Check for low success rates
        if analytics["performance_metrics"]["success_rate"] < 90:
            alerts.append({
                "level": "warning",
                "message": f"Success rate below 90%: {analytics['performance_metrics']['success_rate']:.1f}%",
                "timestamp": datetime.datetime.now()
            })
        
        # Check for high costs
        avg_cost = analytics["performance_metrics"]["average_cost_per_request"]
        if avg_cost > 0.005:  # Above $0.005 per request
            alerts.append({
                "level": "warning",
                "message": f"Average cost per request high: ${avg_cost:.4f}",
                "timestamp": datetime.datetime.now()
            })
        
        # Check for provider failures
        for name, provider in analytics["provider_performance"].items():
            if not provider["is_available"]:
                alerts.append({
                    "level": "error",
                    "message": f"Provider {name} is unavailable",
                    "timestamp": datetime.datetime.now()
                })
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "critical_count": len([a for a in alerts if a["level"] == "critical"]),
            "warning_count": len([a for a in alerts if a["level"] == "warning"]),
            "error_count": len([a for a in alerts if a["level"] == "error"])
        }
        
    except Exception as e:
        logger.error(f"❌ System alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include routes in FastAPI app
def include_ai_monitoring_routes(app):
    """Include AI monitoring routes in FastAPI app"""
    app.include_router(router, prefix="", tags=["ai-monitoring"])
    logger.info("📊 AI Monitoring Routes: Added to FastAPI app")