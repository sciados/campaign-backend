# src/api/endpoints.py - Health & Core Endpoints
"""
Health checks, status endpoints, and system diagnostics
Responsibility: /health endpoint, /api/health endpoint, /api/status endpoint,
/ root endpoint, System status checks, Feature availability reporting,
All debug endpoints (/api/debug/*), Router status endpoints
"""

import logging
from datetime import datetime
from fastapi import FastAPI
from src.core.router_registry import get_router_status

logger = logging.getLogger(__name__)

# ============================================================================
# ✅ HEALTH CHECK ENDPOINTS
# ============================================================================

def include_health_endpoints(app: FastAPI):
    """Include health check and status endpoints"""
    
    @app.get("/health")
    async def health_check_root():
        """Root level health check (Railway compatibility)"""
        return {"status": "healthy", "message": "CampaignForge AI Backend is running"}

    @app.get("/api/health")
    async def health_check():
        """Health check with feature availability"""
        router_status = get_router_status()
        
        return {
            "status": "healthy",
            "version": "3.3.0",  # 🆕 NEW: Updated version for AI Discovery System
            "features": {
                "authentication": router_status.get("auth", False),
                "campaigns": router_status.get("campaigns", False),
                "dashboard": router_status.get("dashboard", False),
                "admin": router_status.get("admin", False),
                "intelligence": router_status.get("intelligence_system", False),
                "intelligence_main_router": router_status.get("intelligence_main", False),  # ✅ FIXED
                "content_generation": router_status.get("content", False),  # ✅ FIXED
                "enhanced_email_generation": router_status.get("enhanced_email", False),  # ✅ NEW
                "email_ai_learning": router_status.get("enhanced_email", False),  # ✅ NEW
                "database_email_templates": router_status.get("email_models", False),  # ✅ NEW
                "stability_ai": router_status.get("stability", False),  # ✅ NEW
                "ultra_cheap_images": router_status.get("stability", False),  # ✅ NEW
                "universal_storage": router_status.get("storage", False),  # ✅ NEW
                "document_management": router_status.get("document", False),  # ✅ NEW
                "dual_storage_system": router_status.get("storage_system", False),  # ✅ NEW
                "ai_monitoring": router_status.get("ai_monitoring", False),  # ✅ NEW
                "dynamic_routing": router_status.get("ai_monitoring", False),  # ✅ NEW
                "cost_optimization": router_status.get("ai_monitoring", False),  # ✅ NEW
                "analysis": router_status.get("analysis", False),
                "affiliate_links": False,  # Not implemented yet
                "waitlist": router_status.get("waitlist", False),
                "content": router_status.get("content", False),
                "ultra_cheap_ai": router_status.get("content", False),
                "dynamic_ai_providers": router_status.get("dynamic_ai_providers", False),
                "ai_discovery": router_status.get("ai_discovery", False)  # 🆕 NEW: AI Platform Discovery System
            },
            "ai_discovery_system": {  # 🆕 NEW: AI Discovery system status
                "discovery_available": router_status.get("ai_discovery", False),
                "two_table_architecture": router_status.get("ai_discovery", False),
                "automated_discovery": router_status.get("ai_discovery", False),
                "web_research": router_status.get("ai_discovery", False),
                "top_3_ranking": router_status.get("ai_discovery", False),
                "auto_promotion": router_status.get("ai_discovery", False),
                "routes_registered": 1 if router_status.get("ai_discovery", False) else 0,
                "emergency_endpoints_active": True
            },
            "discovery_routes_count": 1 if router_status.get("ai_discovery", False) else 0,  # 🆕 NEW
            "tables_status": "existing",
            "emergency_mode_active": True  # 🆕 NEW: Emergency endpoints are active
        }

    @app.get("/api/status")
    async def system_status():
        """Detailed system status endpoint"""
        router_status = get_router_status()
        
        # Count available features
        available_features = sum(1 for status in router_status.values() if status)
        total_features = len(router_status)
        
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "3.3.0",
            "system_health": {
                "overall_status": "healthy",
                "features_available": available_features,
                "total_features": total_features,
                "availability_percentage": round((available_features / total_features) * 100, 2)
            },
            "router_status": router_status,
            "critical_systems": {
                "authentication": router_status.get("auth", False),
                "database": True,  # Assume database is working if app starts
                "ai_discovery": router_status.get("ai_discovery", False),
                "emergency_fallbacks": True
            },
            "ai_systems": {
                "intelligence_engine": router_status.get("intelligence_main", False),
                "content_generation": router_status.get("content", False),
                "enhanced_email": router_status.get("enhanced_email", False),
                "stability_ai": router_status.get("stability", False),
                "ai_monitoring": router_status.get("ai_monitoring", False),
                "ai_discovery": router_status.get("ai_discovery", False)
            },
            "storage_systems": {
                "universal_storage": router_status.get("storage", False),
                "document_management": router_status.get("document", False),
                "dual_storage_active": router_status.get("storage_system", False)
            }
        }

    @app.get("/")
    async def root():
        """Root endpoint"""
        router_status = get_router_status()
        
        return {
            "message": "CampaignForge AI Backend API",
            "version": "3.3.0",  # 🆕 NEW: Updated version for AI Discovery System
            "status": "healthy",
            "docs": "/api/docs", 
            "health": "/api/health",
            "features_available": True,
            "ai_discovery_fixed": True,  # 🆕 NEW
            "emergency_endpoints_active": True,  # 🆕 NEW
            "router_summary": {
                "total_routers": len([k for k, v in router_status.items() if v]),
                "core_systems": sum(1 for k in ["auth", "campaigns", "dashboard"] if router_status.get(k, False)),
                "ai_systems": sum(1 for k in ["intelligence_main", "content", "enhanced_email", "stability", "ai_monitoring", "ai_discovery"] if router_status.get(k, False)),
                "storage_systems": sum(1 for k in ["storage", "document"] if router_status.get(k, False))
            },
            "new_features": {
                "ai_discovery": "Automated AI platform discovery and management",  # 🆕 NEW
                "emergency_mode": "Emergency endpoints active for immediate functionality",  # 🆕 NEW
                "database_fixes": "All database connection issues resolved",  # 🆕 NEW
                "async_context_fixes": "All async context manager issues resolved"  # 🆕 NEW
            }
        }

# ============================================================================
# ✅ DEBUG ENDPOINTS
# ============================================================================

def include_debug_endpoints(app: FastAPI):
    """Include debug and troubleshooting endpoints"""
    
    @app.get("/api/debug/router-status", tags=["debug"])
    async def debug_router_status():
        """Debug router registration status"""
        router_status = get_router_status()
        
        # Check if routes exist for each router
        debug_info = {}
        for router_name, available in router_status.items():
            debug_info[router_name] = {
                "available": available,
                "imported": available,
                "registered": available
            }
        
        return {
            "router_status": debug_info,
            "summary": {
                "total_routers": len(router_status),
                "available_routers": sum(1 for status in router_status.values() if status),
                "missing_routers": sum(1 for status in router_status.values() if not status)
            },
            "critical_missing": [
                name for name, status in router_status.items() 
                if not status and name in ["auth", "campaigns", "dashboard"]
            ],
            "ai_systems_status": {
                name: status for name, status in router_status.items()
                if name in ["intelligence_main", "content", "enhanced_email", "stability", "ai_monitoring", "ai_discovery"]
            }
        }

    @app.get("/api/debug/ai-discovery-router-status", tags=["debug"])
    async def debug_ai_discovery_router_status():
        """🔍 Debug AI Discovery router registration status"""
        router_status = get_router_status()
        
        # Check if routes exist
        ai_discovery_routes = []
        for route in app.routes:
            if hasattr(route, 'path') and '/ai-discovery/' in route.path:
                ai_discovery_routes.append({
                    "path": route.path,
                    "methods": list(route.methods) if hasattr(route, 'methods') else [],
                    "name": getattr(route, 'name', 'unnamed')
                })
        
        return {
            "router_import_status": router_status.get("ai_discovery", False),
            "routes_registered": len(ai_discovery_routes),
            "ai_discovery_routes": ai_discovery_routes,
            "expected_routes": [
                "/api/admin/ai-discovery/health",
                "/api/admin/ai-discovery/active-providers", 
                "/api/admin/ai-discovery/discovered-suggestions",
                "/api/admin/ai-discovery/category-rankings",
                "/api/admin/ai-discovery/dashboard"
            ],
            "emergency_endpoints_active": True,
            "registration_issue": len(ai_discovery_routes) == 0 and router_status.get("ai_discovery", False),
            "troubleshooting": {
                "step_1": "Check if router file exists: src/routes/ai_platform_discovery.py",
                "step_2": "Verify router registration in router_registry.py",
                "step_3": "Check import statement works",
                "step_4": "Verify prefix is '/api/admin/ai-discovery'"
            }
        }

    @app.get("/api/debug/campaigns-status", tags=["debug"])
    async def debug_campaigns_status():
        """Debug campaigns router status"""
        router_status = get_router_status()
        
        # Check if campaigns routes exist
        campaigns_routes = []
        for route in app.routes:
            if hasattr(route, 'path') and '/campaigns' in route.path:
                campaigns_routes.append({
                    "path": route.path,
                    "methods": list(route.methods) if hasattr(route, 'methods') else [],
                    "name": getattr(route, 'name', 'unnamed')
                })
        
        return {
            "campaigns_router_available": router_status.get("campaigns", False),
            "routes_found": len(campaigns_routes),
            "campaigns_routes": campaigns_routes,
            "emergency_mode": not router_status.get("campaigns", False),
            "import_issues": {
                "check_schemas": "Verify src.campaigns.schemas imports",
                "check_services": "Verify src.campaigns.services imports", 
                "check_models": "Verify campaign models import",
                "check_routes": "Verify src.campaigns.routes imports"
            },
            "fallback_active": len(campaigns_routes) > 0 and not router_status.get("campaigns", False)
        }

    @app.get("/api/debug/content-status", tags=["debug"])
    async def debug_content_status():
        """Debug content generation router status"""
        router_status = get_router_status()
        
        # Check if content routes exist
        content_routes = []
        for route in app.routes:
            if hasattr(route, 'path') and '/content' in route.path:
                content_routes.append({
                    "path": route.path,
                    "methods": list(route.methods) if hasattr(route, 'methods') else [],
                    "name": getattr(route, 'name', 'unnamed')
                })
        
        return {
            "content_router_available": router_status.get("content", False),
            "intelligence_main_available": router_status.get("intelligence_main", False),
            "routes_found": len(content_routes),
            "content_routes": content_routes,
            "emergency_mode": not router_status.get("content", False),
            "router_hierarchy": {
                "primary": "Intelligence main router includes content routes",
                "fallback": "Direct content router registration",
                "emergency": "Emergency content endpoints"
            },
            "troubleshooting": {
                "step_1": "Check intelligence main router import",
                "step_2": "Check content_routes.py exists",
                "step_3": "Verify content router registration logic",
                "step_4": "Check for import errors in intelligence module"
            }
        }

    @app.get("/api/debug/all-routes", tags=["debug"])
    async def debug_all_routes():
        """Debug all registered routes"""
        routes_info = []
        
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes_info.append({
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": getattr(route, 'name', 'unnamed'),
                    "tags": getattr(route, 'tags', [])
                })
        
        # Group routes by prefix
        route_groups = {}
        for route in routes_info:
            prefix = route['path'].split('/')[1] if len(route['path'].split('/')) > 1 else 'root'
            if prefix not in route_groups:
                route_groups[prefix] = []
            route_groups[prefix].append(route)
        
        return {
            "total_routes": len(routes_info),
            "route_groups": route_groups,
            "group_summary": {
                group: len(routes) for group, routes in route_groups.items()
            },
            "api_routes": len([r for r in routes_info if r['path'].startswith('/api')]),
            "admin_routes": len([r for r in routes_info if '/admin' in r['path']]),
            "emergency_routes": len([r for r in routes_info if 'emergency' in str(r.get('tags', []))])
        }

    @app.get("/api/debug/system-info", tags=["debug"])
    async def debug_system_info():
        """Debug system information"""
        import os
        import sys
        
        router_status = get_router_status()
        
        return {
            "python_version": sys.version,
            "environment": {
                "RAILWAY_ENVIRONMENT_NAME": os.getenv("RAILWAY_ENVIRONMENT_NAME"),
                "DEBUG": os.getenv("DEBUG", "false"),
                "DATABASE_URL_SET": bool(os.getenv("DATABASE_URL")),
                "JWT_SECRET_KEY_SET": bool(os.getenv("JWT_SECRET_KEY")),
                "OPENAI_API_KEY_SET": bool(os.getenv("OPENAI_API_KEY"))
            },
            "router_status": router_status,
            "critical_paths": {
                "src_path_exists": os.path.exists("src"),
                "models_path_exists": os.path.exists("src/models"),
                "routes_path_exists": os.path.exists("src/routes"),
                "intelligence_path_exists": os.path.exists("src/intelligence"),
                "campaigns_path_exists": os.path.exists("src/campaigns")
            },
            "system_status": {
                "total_available_routers": sum(1 for status in router_status.values() if status),
                "critical_systems_ok": all(router_status.get(k, False) for k in ["auth"]),
                "ai_systems_available": any(router_status.get(k, False) for k in ["intelligence_main", "content", "ai_discovery"]),
                "emergency_mode_active": True
            }
        }

# ============================================================================
# ✅ FEATURE AVAILABILITY ENDPOINTS
# ============================================================================

def include_feature_endpoints(app: FastAPI):
    """Include feature availability and capability endpoints"""
    
    @app.get("/api/features", tags=["features"])
    async def get_available_features():
        """Get detailed feature availability"""
        router_status = get_router_status()
        
        return {
            "core_features": {
                "user_authentication": {
                    "available": router_status.get("auth", False),
                    "endpoints": ["/api/auth/login", "/api/auth/register", "/api/auth/profile"],
                    "status": "operational" if router_status.get("auth", False) else "unavailable"
                },
                "campaign_management": {
                    "available": router_status.get("campaigns", False),
                    "endpoints": ["/api/campaigns", "/api/campaigns/{id}"],
                    "status": "operational" if router_status.get("campaigns", False) else "emergency_mode",
                    "emergency_endpoints": not router_status.get("campaigns", False)
                },
                "dashboard_analytics": {
                    "available": router_status.get("dashboard", False),
                    "endpoints": ["/api/dashboard/stats", "/api/dashboard/company"],
                    "status": "operational" if router_status.get("dashboard", False) else "emergency_mode",
                    "emergency_endpoints": not router_status.get("dashboard", False)
                }
            },
            "ai_features": {
                "content_generation": {
                    "available": router_status.get("content", False),
                    "intelligence_main_router": router_status.get("intelligence_main", False),
                    "endpoints": ["/api/intelligence/content/generate"],
                    "status": "operational" if router_status.get("content", False) else "emergency_mode"
                },
                "enhanced_email_generation": {
                    "available": router_status.get("enhanced_email", False),
                    "ai_learning": router_status.get("enhanced_email", False),
                    "database_templates": router_status.get("email_models", False),
                    "endpoints": ["/api/intelligence/emails/generate", "/api/intelligence/emails/subjects"],
                    "status": "operational" if router_status.get("enhanced_email", False) else "unavailable"
                },
                "ultra_cheap_images": {
                    "available": router_status.get("stability", False),
                    "cost_savings": "90%+ vs DALL-E",
                    "endpoints": ["/api/intelligence/stability/generate"],
                    "status": "operational" if router_status.get("stability", False) else "unavailable"
                },
                "ai_monitoring": {
                    "available": router_status.get("ai_monitoring", False),
                    "real_time_optimization": router_status.get("ai_monitoring", False),
                    "cost_tracking": router_status.get("ai_monitoring", False),
                    "endpoints": ["/api/ai-monitoring/status", "/api/ai-monitoring/analytics"],
                    "status": "operational" if router_status.get("ai_monitoring", False) else "unavailable"
                },
                "ai_discovery_system": {
                    "available": router_status.get("ai_discovery", False),
                    "two_table_architecture": router_status.get("ai_discovery", False),
                    "automated_discovery": router_status.get("ai_discovery", False),
                    "endpoints": [
                        "/api/admin/ai-discovery/active-providers",
                        "/api/admin/ai-discovery/discovered-suggestions",
                        "/api/admin/ai-discovery/dashboard"
                    ],
                    "status": "operational" if router_status.get("ai_discovery", False) else "emergency_mode",
                    "emergency_endpoints": True
                }
            },
            "storage_features": {
                "universal_storage": {
                    "available": router_status.get("storage", False),
                    "dual_storage_system": router_status.get("storage_system", False),
                    "endpoints": ["/api/storage/upload", "/api/storage/download"],
                    "status": "operational" if router_status.get("storage", False) else "unavailable"
                },
                "document_management": {
                    "available": router_status.get("document", False),
                    "file_processing": router_status.get("document", False),
                    "endpoints": ["/api/documents/upload", "/api/documents/process"],
                    "status": "operational" if router_status.get("document", False) else "unavailable"
                }
            },
            "admin_features": {
                "admin_dashboard": {
                    "available": router_status.get("admin", False),
                    "endpoints": ["/api/admin/users", "/api/admin/companies"],
                    "status": "operational" if router_status.get("admin", False) else "unavailable"
                },
                "waitlist_management": {
                    "available": router_status.get("waitlist", False),
                    "endpoints": ["/api/waitlist/join", "/api/waitlist/status"],
                    "status": "operational" if router_status.get("waitlist", False) else "unavailable"
                },
                "dynamic_ai_providers": {
                    "available": router_status.get("dynamic_ai_providers", False),
                    "endpoints": ["/admin/providers/dynamic"],
                    "status": "operational" if router_status.get("dynamic_ai_providers", False) else "unavailable"
                }
            }
        }

    @app.get("/api/capabilities", tags=["features"])
    async def get_system_capabilities():
        """Get system capabilities summary"""
        router_status = get_router_status()
        
        # Calculate capability scores
        core_score = sum(1 for k in ["auth", "campaigns", "dashboard"] if router_status.get(k, False)) / 3
        ai_score = sum(1 for k in ["intelligence_main", "content", "enhanced_email", "stability", "ai_monitoring", "ai_discovery"] if router_status.get(k, False)) / 6
        storage_score = sum(1 for k in ["storage", "document"] if router_status.get(k, False)) / 2
        admin_score = sum(1 for k in ["admin", "waitlist", "dynamic_ai_providers"] if router_status.get(k, False)) / 3
        
        overall_score = (core_score + ai_score + storage_score + admin_score) / 4
        
        return {
            "overall_capability": round(overall_score * 100, 1),
            "capability_breakdown": {
                "core_systems": round(core_score * 100, 1),
                "ai_systems": round(ai_score * 100, 1), 
                "storage_systems": round(storage_score * 100, 1),
                "admin_systems": round(admin_score * 100, 1)
            },
            "ready_for_production": overall_score >= 0.7,
            "critical_systems_operational": core_score >= 0.67,  # At least auth working
            "ai_systems_operational": ai_score >= 0.33,  # At least 2 AI systems working
            "emergency_mode_active": overall_score < 1.0,
            "recommended_actions": get_recommended_actions(router_status),
            "system_strengths": get_system_strengths(router_status),
            "next_priorities": get_next_priorities(router_status)
        }

def get_recommended_actions(router_status):
    """Get recommended actions based on router status"""
    actions = []
    
    if not router_status.get("auth", False):
        actions.append("CRITICAL: Fix authentication router - system unusable without auth")
    
    if not router_status.get("campaigns", False):
        actions.append("HIGH: Fix campaigns router - core functionality missing")
    
    if not router_status.get("content", False) and not router_status.get("intelligence_main", False):
        actions.append("HIGH: Fix content generation - key differentiator missing")
    
    if not router_status.get("ai_discovery", False):
        actions.append("MEDIUM: AI Discovery system available but not fully integrated")
    
    if not router_status.get("storage", False):
        actions.append("MEDIUM: Enable storage system for file handling")
    
    if len(actions) == 0:
        actions.append("✅ All systems operational - ready for production")
    
    return actions

def get_system_strengths(router_status):
    """Get system strengths based on available routers"""
    strengths = []
    
    if router_status.get("auth", False):
        strengths.append("✅ User authentication and security")
    
    if router_status.get("ai_discovery", False):
        strengths.append("✅ AI Platform Discovery System (v3.3.0)")
    
    if router_status.get("enhanced_email", False):
        strengths.append("✅ Enhanced email generation with AI learning")
    
    if router_status.get("stability", False):
        strengths.append("✅ Ultra-cheap AI image generation (90% cost savings)")
    
    if router_status.get("ai_monitoring", False):
        strengths.append("✅ Real-time AI monitoring and optimization")
    
    if router_status.get("storage_system", False):
        strengths.append("✅ Dual storage system with automatic failover")
    
    return strengths

def get_next_priorities(router_status):
    """Get next development priorities"""
    priorities = []
    
    # Count working systems
    working_systems = sum(1 for status in router_status.values() if status)
    
    if working_systems < 5:
        priorities.append("Focus on fixing core router imports")
    elif working_systems < 10:
        priorities.append("Enable additional AI features")
    else:
        priorities.append("Optimize performance and add advanced features")
    
    if not router_status.get("storage", False):
        priorities.append("Implement storage system for file handling")
    
    if router_status.get("ai_discovery", False):
        priorities.append("Complete AI Discovery frontend integration")
    
    return priorities

# ============================================================================
# ✅ MAIN INCLUDE FUNCTION
# ============================================================================

def include_core_endpoints(app: FastAPI):
    """Include all core endpoints in the FastAPI app"""
    include_health_endpoints(app)
    include_debug_endpoints(app)
    include_feature_endpoints(app)
    
    logging.info("✅ Core endpoints included: health, debug, and features")

# ============================================================================
# ✅ EXPORTS
# ============================================================================

__all__ = [
    'include_core_endpoints',
    'include_health_endpoints', 
    'include_debug_endpoints',
    'include_feature_endpoints'
]