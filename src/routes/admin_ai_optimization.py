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
    
    try:
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
            
            service_url = os.getenv("AI_DISCOVERY_SERVICE_URL", "")
            is_configured = bool(service_url.strip())
            
            return {
                "main_app": main_app_data,
                "discovery_service": plugin_data,
                "integration_status": {
                    "plugin_connected": plugin_data["is_connected"],
                    "last_sync": plugin_data["last_updated"],
                    "service_configured": is_configured,
                    "service_url": service_url if is_configured else "not_configured",
                    "features_available": [
                        "ai_discovery",
                        "cost_optimization", 
                        "provider_switching",
                        "market_intelligence"
                    ] if plugin_data["is_connected"] else [],
                    "status": "connected" if plugin_data["is_connected"] else "not_configured" if not is_configured else "configured_but_offline"
                }
            }
    except Exception as e:
        return {
            "error": str(e),
            "integration_status": {
                "plugin_connected": False,
                "service_configured": bool(os.getenv("AI_DISCOVERY_SERVICE_URL", "").strip()),
                "service_url": os.getenv("AI_DISCOVERY_SERVICE_URL", "not_configured"),
                "status": "error"
            },
            "troubleshooting": [
                "Check AI_DISCOVERY_SERVICE_URL environment variable",
                "Verify AI Discovery Service is deployed and running",
                "Check Railway deployment logs",
                "Ensure httpx is in requirements.txt"
            ]
        }

@router.get("/test-connection")
async def test_ai_discovery_connection():
    """Test endpoint to verify AI Discovery Service integration"""
    
    service_url = os.getenv("AI_DISCOVERY_SERVICE_URL", "")
    
    if not service_url.strip():
        return {
            "integration_status": "not_configured",
            "message": "⚙️ AI Discovery Service not configured",
            "service_url": "not_set",
            "configuration": {
                "ai_discovery_service_url": "not_set",
                "url_configured": False,
                "environment": os.getenv("RAILWAY_ENVIRONMENT_NAME", "development")
            },
            "next_steps": [
                "Set AI_DISCOVERY_SERVICE_URL in Railway environment variables",
                "Deploy AI Discovery Service from handover document", 
                "Update environment variable to live service URL",
                "Restart backend service"
            ],
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    
    try:
        async with AiDiscoveryPlugin() as plugin:
            health = await plugin.check_service_health()
            
            # Test if we can get data
            discoveries = await plugin.get_discoveries_widget_data()
            recommendations = await plugin.get_provider_recommendations()
            
            # Check if service responded successfully
            service_healthy = (
                "error" not in health and 
                health.get("status") not in ["disconnected", "not_configured", "unknown"]
            )
            
            return {
                "integration_status": "success" if service_healthy else "service_offline",
                "discovery_service_health": health,
                "discoveries_available": "error" not in discoveries,
                "recommendations_available": "error" not in recommendations,
                "message": "🎉 AI Discovery Service integration working!" if service_healthy else "⚠️ Service configured but not responding",
                "service_url": service_url,
                "configuration": {
                    "ai_discovery_service_url": service_url,
                    "url_configured": True,
                    "url_valid": service_url.startswith("http"),
                    "environment": os.getenv("RAILWAY_ENVIRONMENT_NAME", "development")
                },
                "next_steps": [
                    "AI Discovery Service is working!",
                    "Check admin dashboard for live data",
                    "Monitor provider recommendations",
                    "Review cost optimization suggestions"
                ] if service_healthy else [
                    "Check if AI Discovery Service is deployed and running",
                    "Verify the service URL is correct",
                    "Check service logs for errors",
                    "Test the service URL directly in browser"
                ],
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {
            "integration_status": "failed",
            "error": str(e),
            "message": "❌ AI Discovery Service connection failed",
            "service_url": service_url,
            "debug_info": {
                "ai_discovery_service_url": service_url,
                "url_configured": True,
                "error_type": type(e).__name__,
                "environment": os.getenv("RAILWAY_ENVIRONMENT_NAME", "development")
            },
            "troubleshooting": [
                "Verify AI Discovery Service is deployed and running",
                "Check if service URL is accessible",
                "Review service deployment logs",
                "Test service health endpoint directly"
            ],
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

@router.get("/provider-status")
async def get_provider_status():
    """Get detailed status of all AI providers"""
    
    try:
        async with AiDiscoveryPlugin() as plugin:
            recommendations = await plugin.get_provider_recommendations()
            
            return {
                "providers": recommendations,
                "last_updated": datetime.datetime.utcnow().isoformat(),
                "integration_active": "error" not in recommendations,
                "service_configured": bool(os.getenv("AI_DISCOVERY_SERVICE_URL", "").strip())
            }
    except Exception as e:
        return {
            "error": str(e),
            "providers": {},
            "last_updated": datetime.datetime.utcnow().isoformat(),
            "integration_active": False,
            "service_configured": bool(os.getenv("AI_DISCOVERY_SERVICE_URL", "").strip())
        }

@router.get("/setup-status")
async def get_setup_status():
    """Get detailed setup and configuration status"""
    
    service_url = os.getenv("AI_DISCOVERY_SERVICE_URL", "")
    is_configured = bool(service_url.strip())
    
    # Test connection if configured
    service_responding = False
    if is_configured:
        try:
            async with AiDiscoveryPlugin() as plugin:
                health = await plugin.check_service_health()
                service_responding = "error" not in health and health.get("status") != "disconnected"
        except:
            service_responding = False
    
    return {
        "configuration": {
            "ai_discovery_service_url": service_url if is_configured else "not_set",
            "url_configured": is_configured,
            "url_valid": service_url.startswith("http") if service_url else False,
            "environment": os.getenv("RAILWAY_ENVIRONMENT_NAME", "development")
        },
        "setup_progress": {
            "step_1_env_var": is_configured,
            "step_2_service_responding": service_responding,
            "step_3_integration_working": service_responding,
            "overall_status": "ready" if service_responding else "configured" if is_configured else "not_configured"
        },
        "next_actions": [
            "✅ Environment variable configured" if is_configured else "⚠️ Set AI_DISCOVERY_SERVICE_URL environment variable",
            "✅ Service responding" if service_responding else "🔄 Deploy/start AI Discovery Service",
            "✅ Integration working" if service_responding else "🔗 Test integration",
            "🚀 Monitor live AI discovery" if service_responding else "📋 Follow setup documentation"
        ],
        "timestamp": datetime.datetime.utcnow().isoformat()
    }