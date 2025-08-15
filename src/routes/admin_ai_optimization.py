import datetime
from fastapi import APIRouter, Depends, HTTPException
from src.plugins.ai_discovery_client import AiDiscoveryPlugin
# Adjust this import based on your auth setup
try:
    from src.auth.dependencies import get_current_user
except ImportError:
    # Fallback if auth structure is different
    def get_current_user():
        return {"id": "admin", "is_admin": True}

import os

router = APIRouter(prefix="/admin/ai-optimization", tags=["admin", "ai-optimization"])

@router.get("/dashboard-data")
async def get_ai_optimization_dashboard():
    """Main admin endpoint that aggregates plugin data with main app data"""
    
    async with AiDiscoveryPlugin() as plugin:
        # Get data from AI Discovery Service
        plugin_data = await plugin.get_aggregated_dashboard_data()
        
        # Get main app AI usage data (placeholder for now)
        main_app_data = {
            "current_providers": {
                "image_generation": os.getenv("CURRENT_IMAGE_PROVIDER", "stability_ai"),
                "text_generation": os.getenv("CURRENT_TEXT_PROVIDER", "openai"),
                "video_generation": os.getenv("CURRENT_VIDEO_PROVIDER", "runway_ml")
            },
            "daily_usage": {
                "images_generated": 45,
                "texts_generated": 123,
                "videos_generated": 8
            },
            "monthly_costs": {
                "total": 245.67,
                "image": 89.23,
                "text": 134.44,
                "video": 22.00
            },
            "performance_metrics": {
                "avg_response_time": 2.3,
                "success_rate": 98.5,
                "error_rate": 1.5
            }
        }
        
        return {
            "main_app": main_app_data,
            "discovery_service": plugin_data,
            "integration_status": {
                "plugin_connected": plugin_data["is_connected"],
                "last_sync": plugin_data["last_updated"],
                "features_available": [
                    "ai_discovery",
                    "cost_optimization", 
                    "provider_switching",
                    "market_intelligence"
                ] if plugin_data["is_connected"] else ["basic_monitoring"],
                "service_url": os.getenv("AI_DISCOVERY_SERVICE_URL", "not_configured")
            }
        }

@router.get("/test-connection")
async def test_ai_discovery_connection():
    """Test endpoint to verify AI Discovery Service integration"""
    
    async with AiDiscoveryPlugin() as plugin:
        try:
            health = await plugin.check_service_health()
            discoveries = await plugin.get_discoveries_widget_data()
            recommendations = await plugin.get_provider_recommendations()
            
            return {
                "integration_status": "success",
                "discovery_service_health": health,
                "sample_discoveries": discoveries,
                "sample_recommendations": recommendations,
                "message": "🎉 AI Discovery Service integration working perfectly!",
                "service_url": os.getenv("AI_DISCOVERY_SERVICE_URL"),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "integration_status": "failed",
                "error": str(e),
                "message": "❌ Unable to connect to AI Discovery Service",
                "service_url": os.getenv("AI_DISCOVERY_SERVICE_URL", "not_configured"),
                "timestamp": datetime.utcnow().isoformat()
            }

@router.get("/provider-status")
async def get_provider_status():
    """Get detailed status of all AI providers"""
    
    async with AiDiscoveryPlugin() as plugin:
        recommendations = await plugin.get_provider_recommendations()
        
        return {
            "providers": recommendations,
            "last_updated": datetime.utcnow().isoformat(),
            "integration_active": not recommendations.get("error")
        }