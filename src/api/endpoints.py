# src/api/endpoints.py - Health & Core Endpoints
"""
Health checks, status endpoints, and system diagnostics
Responsibility: /health endpoint, /api/health endpoint, /api/status endpoint,
/ root endpoint, System status checks, Feature availability reporting,
All debug endpoints (/api/debug/*), Router status endpoints
ENHANCED: AI Category support and Dynamic Analysis features
"""

import logging
from datetime import datetime
from fastapi import FastAPI
from src.core.router_registry import get_router_status

logger = logging.getLogger(__name__)

# ============================================================================
# ✅ HEALTH CHECK ENDPOINTS - ENHANCED
# ============================================================================

def include_health_endpoints(app: FastAPI):
    """Include health check and status endpoints with AI category support"""
    
    @app.get("/health")
    async def health_check_root():
        """Root level health check (Railway compatibility)"""
        return {"status": "healthy", "message": "CampaignForge AI Backend is running"}

    @app.get("/api/health")
    async def health_check():
        """Health check with feature availability and AI category support"""
        router_status = get_router_status()
        
        # Test AI category features
        ai_categories_available = False
        dynamic_analysis_available = False
        video_detection_ready = False
        
        try:
            from src.services.ai_provider_analyzer import get_dynamic_ai_provider_analyzer
            analyzer = get_dynamic_ai_provider_analyzer()
            ai_categories_available = True
            dynamic_analysis_available = True
            video_detection_ready = True
        except:
            pass
        
        return {
            "status": "healthy",
            "version": "3.3.1",  # 🆕 NEW: Updated version for Dynamic AI Analysis
            "features": {
                "authentication": router_status.get("auth", False),
                "campaigns": router_status.get("campaigns", False),
                "dashboard": router_status.get("dashboard", False),
                "admin": router_status.get("admin", False),
                "intelligence": router_status.get("intelligence_system", False),
                "intelligence_main_router": router_status.get("intelligence_main", False),
                "content_generation": router_status.get("content", False),
                "enhanced_email_generation": router_status.get("enhanced_email", False),
                "email_ai_learning": router_status.get("enhanced_email", False),
                "database_email_templates": router_status.get("email_models", False),
                "stability_ai": router_status.get("stability", False),
                "ultra_cheap_images": router_status.get("stability", False),
                "universal_storage": router_status.get("storage", False),
                "document_management": router_status.get("document", False),
                "dual_storage_system": router_status.get("storage_system", False),
                "ai_monitoring": router_status.get("ai_monitoring", False),
                "dynamic_routing": router_status.get("ai_monitoring", False),
                "cost_optimization": router_status.get("ai_monitoring", False),
                "analysis": router_status.get("analysis", False),
                "affiliate_links": False,  # Not implemented yet
                "waitlist": router_status.get("waitlist", False),
                "content": router_status.get("content", False),
                "ultra_cheap_ai": router_status.get("content", False),
                "dynamic_ai_providers": router_status.get("dynamic_ai_providers", False),
                "ai_discovery": router_status.get("ai_discovery", False),
                
                # 🆕 NEW: AI Category Features
                "ai_categories": ai_categories_available,
                "dynamic_ai_analysis": dynamic_analysis_available,
                "video_provider_detection": video_detection_ready,
                "multimodal_support": ai_categories_available,
                "cost_per_minute_analysis": ai_categories_available,
                "confidence_scoring": dynamic_analysis_available
            },
            "ai_discovery_system": {
                "discovery_available": router_status.get("ai_discovery", False),
                "two_table_architecture": router_status.get("ai_discovery", False),
                "automated_discovery": router_status.get("ai_discovery", False),
                "web_research": router_status.get("ai_discovery", False),
                "top_3_ranking": router_status.get("ai_discovery", False),
                "auto_promotion": router_status.get("ai_discovery", False),
                "routes_registered": 1 if router_status.get("ai_discovery", False) else 0,
                "emergency_endpoints_active": True,
                
                # 🆕 NEW: AI Category System
                "ai_category_system": {
                    "dynamic_categorization": dynamic_analysis_available,
                    "video_detection": video_detection_ready,
                    "replicate_video_support": ai_categories_available,
                    "cost_analysis": ai_categories_available,
                    "confidence_scoring": dynamic_analysis_available,
                    "emergency_ai_endpoints": True
                }
            },
            "video_generation": {  # 🆕 NEW: Video generation status
                "supported": video_detection_ready,
                "replicate_configured": video_detection_ready,
                "cost_optimization": ai_categories_available,
                "providers_detected": video_detection_ready,
                "emergency_fallback": True
            },
            "discovery_routes_count": 1 if router_status.get("ai_discovery", False) else 0,
            "tables_status": "existing",
            "emergency_mode_active": True,
            "ai_enhanced_emergency_mode": ai_categories_available  # 🆕 NEW
        }

    @app.get("/api/status")
    async def system_status():
        """Detailed system status endpoint with AI category information"""
        router_status = get_router_status()
        
        # Test AI category features
        ai_features = {
            "ai_categories_available": False,
            "dynamic_analysis_available": False,
            "video_detection_ready": False,
            "replicate_video_support": False
        }
        
        try:
            from src.services.ai_provider_analyzer import get_dynamic_ai_provider_analyzer
            analyzer = get_dynamic_ai_provider_analyzer()
            ai_features.update({
                "ai_categories_available": True,
                "dynamic_analysis_available": True,
                "video_detection_ready": True,
                "replicate_video_support": True
            })
        except Exception as e:
            logger.info(f"AI category features not available: {e}")
        
        # Count available features
        available_features = sum(1 for status in router_status.values() if status)
        total_features = len(router_status)
        
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "3.3.1-dynamic-ai",  # 🆕 Updated version
            "system_health": {
                "overall_status": "healthy",
                "features_available": available_features,
                "total_features": total_features,
                "availability_percentage": round((available_features / total_features) * 100, 2),
                "ai_enhanced": ai_features["ai_categories_available"]  # 🆕 NEW
            },
            "router_status": router_status,
            "critical_systems": {
                "authentication": router_status.get("auth", False),
                "database": True,  # Assume database is working if app starts
                "ai_discovery": router_status.get("ai_discovery", False),
                "emergency_fallbacks": True,
                "ai_categories": ai_features["ai_categories_available"]  # 🆕 NEW
            },
            "ai_systems": {
                "intelligence_engine": router_status.get("intelligence_main", False),
                "content_generation": router_status.get("content", False),
                "enhanced_email": router_status.get("enhanced_email", False),
                "stability_ai": router_status.get("stability", False),
                "ai_monitoring": router_status.get("ai_monitoring", False),
                "ai_discovery": router_status.get("ai_discovery", False),
                
                # 🆕 NEW: AI Category Systems
                "dynamic_ai_analysis": ai_features["dynamic_analysis_available"],
                "video_provider_detection": ai_features["video_detection_ready"],
                "multimodal_categorization": ai_features["ai_categories_available"],
                "cost_per_minute_analysis": ai_features["ai_categories_available"],
                "confidence_scoring": ai_features["dynamic_analysis_available"]
            },
            "storage_systems": {
                "universal_storage": router_status.get("storage", False),
                "document_management": router_status.get("document", False),
                "dual_storage_active": router_status.get("storage_system", False)
            },
            "video_generation": {  # 🆕 NEW: Video generation status
                "system_ready": ai_features["video_detection_ready"],
                "replicate_support": ai_features["replicate_video_support"],
                "providers_available": ai_features["ai_categories_available"],
                "cost_analysis_available": ai_features["ai_categories_available"]
            }
        }

    @app.get("/")
    async def root():
        """Root endpoint with AI category information"""
        router_status = get_router_status()
        
        # Check AI category features
        ai_category_features = False
        try:
            from src.services.ai_provider_analyzer import get_dynamic_ai_provider_analyzer
            get_dynamic_ai_provider_analyzer()
            ai_category_features = True
        except:
            pass
        
        return {
            "message": "CampaignForge AI Backend API",
            "version": "3.3.1-dynamic-ai",  # 🆕 NEW: Updated version
            "status": "healthy",
            "docs": "/api/docs", 
            "health": "/api/health",
            "features_available": True,
            "ai_discovery_fixed": True,
            "emergency_endpoints_active": True,
            "ai_categories_available": ai_category_features,  # 🆕 NEW
            "video_generation_ready": ai_category_features,  # 🆕 NEW
            "router_summary": {
                "total_routers": len([k for k, v in router_status.items() if v]),
                "core_systems": sum(1 for k in ["auth", "campaigns", "dashboard"] if router_status.get(k, False)),
                "ai_systems": sum(1 for k in ["intelligence_main", "content", "enhanced_email", "stability", "ai_monitoring", "ai_discovery"] if router_status.get(k, False)),
                "storage_systems": sum(1 for k in ["storage", "document"] if router_status.get(k, False)),
                "ai_category_systems": 1 if ai_category_features else 0  # 🆕 NEW
            },
            "new_features": {
                "ai_discovery": "Automated AI platform discovery and management",
                "emergency_mode": "Emergency endpoints active for immediate functionality",
                "database_fixes": "All database connection issues resolved",
                "async_context_fixes": "All async context manager issues resolved",
                
                # 🆕 NEW: AI Category Features
                "dynamic_ai_analysis": "AI-powered provider categorization and analysis" if ai_category_features else "Not available",
                "video_provider_detection": "Automatic video generation provider detection" if ai_category_features else "Not available", 
                "replicate_video_support": "Replicate multimodal and video capabilities" if ai_category_features else "Not available",
                "cost_optimization": "Video generation cost analysis and optimization" if ai_category_features else "Not available"
            }
        }

# ============================================================================
# ✅ DEBUG ENDPOINTS - ENHANCED
# ============================================================================

def include_debug_endpoints(app: FastAPI):
    """Include debug and troubleshooting endpoints with AI category debugging"""
    
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

    @app.get("/api/debug/ai-category-system", tags=["debug"])  # 🆕 NEW
    async def debug_ai_category_system():
        """🆕 Debug AI category system status"""
        try:
            from src.services.ai_provider_analyzer import get_dynamic_ai_provider_analyzer
            
            analyzer = get_dynamic_ai_provider_analyzer()
            
            # Test basic functionality
            test_results = {
                "analyzer_imported": True,
                "analyzer_initialized": analyzer is not None,
                "openai_client_available": hasattr(analyzer, 'openai_client') and analyzer.openai_client is not None,
                "anthropic_client_available": hasattr(analyzer, 'anthropic_client') and analyzer.anthropic_client is not None
            }
            
            # Test environment scanning
            try:
                import asyncio
                env_providers = asyncio.run(analyzer.scan_environment_for_ai_providers()) if hasattr(analyzer, 'scan_environment_for_ai_providers') else {}
                test_results["environment_scan_working"] = True
                test_results["providers_found"] = len(env_providers)
                test_results["replicate_detected"] = any('replicate' in k.lower() for k in env_providers.keys())
            except Exception as e:
                test_results["environment_scan_working"] = False
                test_results["environment_scan_error"] = str(e)
                test_results["providers_found"] = 0
                test_results["replicate_detected"] = False
            
            return {
                "success": True,
                "ai_category_system": "operational",
                "test_results": test_results,
                "features": {
                    "dynamic_categorization": test_results["analyzer_initialized"],
                    "video_detection": test_results["analyzer_initialized"],
                    "replicate_video_support": test_results["replicate_detected"],
                    "cost_analysis": test_results["analyzer_initialized"]
                },
                "recommendations": [
                    "✅ AI category system is working" if test_results["analyzer_initialized"] else "❌ Initialize AI analyzer",
                    "✅ Replicate detected for video generation" if test_results["replicate_detected"] else "⚠️ Replicate not detected - check REPLICATE_API_TOKEN",
                    "✅ Environment scanning operational" if test_results["environment_scan_working"] else "❌ Fix environment scanning"
                ]
            }
            
        except ImportError as e:
            return {
                "success": False,
                "ai_category_system": "unavailable",
                "error": f"Import failed: {str(e)}",
                "troubleshooting": {
                    "step_1": "Check if ai_provider_analyzer.py exists",
                    "step_2": "Verify dynamic analyzer implementation",
                    "step_3": "Check OpenAI/Anthropic API keys for analysis",
                    "step_4": "Ensure all dependencies are installed"
                }
            }
        except Exception as e:
            return {
                "success": False,
                "ai_category_system": "error",
                "error": str(e),
                "message": "AI category system encountered an error"
            }

    @app.get("/api/debug/video-provider-detection", tags=["debug"])  # 🆕 NEW
    async def debug_video_provider_detection():
        """🆕 Debug video provider detection specifically"""
        try:
            # Check environment variables for video providers
            import os
            video_env_vars = {}
            potential_video_providers = ['REPLICATE_API_TOKEN', 'FAL_API_KEY', 'MINIMAX_API_KEY', 'RUNWAY_API_KEY']
            
            for var in potential_video_providers:
                value = os.getenv(var)
                video_env_vars[var] = {
                    "configured": value is not None and value.strip() != "",
                    "preview": value[:10] + "..." if value and len(value) > 10 else value if value else None
                }
            
            # Test AI analysis of video providers
            video_analysis_results = {}
            try:
                from src.services.ai_provider_analyzer import get_dynamic_ai_provider_analyzer
                analyzer = get_dynamic_ai_provider_analyzer()
                
                # Test specifically with Replicate
                if video_env_vars["REPLICATE_API_TOKEN"]["configured"]:
                    import asyncio
                    replicate_analysis = asyncio.run(analyzer.ai_analyze_provider(
                        "REPLICATE_API_TOKEN", 
                        "replicate", 
                        os.getenv("REPLICATE_API_TOKEN")
                    )) if hasattr(analyzer, 'ai_analyze_provider') else None
                    
                    if replicate_analysis:
                        video_analysis_results["replicate"] = {
                            "category": replicate_analysis.get("primary_category"),
                            "video_capable": "video_generation" in replicate_analysis.get("capabilities", []),
                            "video_cost_per_minute": replicate_analysis.get("video_cost_per_minute"),
                            "confidence": replicate_analysis.get("ai_confidence_score")
                        }
                
            except Exception as analysis_error:
                video_analysis_results["error"] = str(analysis_error)
            
            return {
                "success": True,
                "video_provider_detection": {
                    "environment_variables": video_env_vars,
                    "ai_analysis_results": video_analysis_results,
                    "video_providers_detected": sum(1 for v in video_env_vars.values() if v["configured"]),
                    "replicate_ready": video_env_vars["REPLICATE_API_TOKEN"]["configured"],
                    "analysis_working": len(video_analysis_results) > 0 and "error" not in video_analysis_results
                },
                "recommendations": [
                    "✅ Replicate configured for video generation" if video_env_vars["REPLICATE_API_TOKEN"]["configured"] else "❌ Configure REPLICATE_API_TOKEN for video generation",
                    "✅ Video provider analysis working" if "error" not in video_analysis_results else f"❌ Fix analysis: {video_analysis_results.get('error', 'Unknown error')}",
                    "ℹ️ Consider adding FAL_API_KEY or MINIMAX_API_KEY for additional video options"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Video provider detection failed"
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
        
        # Check for AI category routes
        ai_category_routes = []
        for route in app.routes:
            if hasattr(route, 'path') and any(keyword in route.path for keyword in ['/ai-categories', '/video-providers', '/provider-capabilities']):
                ai_category_routes.append({
                    "path": route.path,
                    "methods": list(route.methods) if hasattr(route, 'methods') else [],
                    "name": getattr(route, 'name', 'unnamed')
                })
        
        return {
            "router_import_status": router_status.get("ai_discovery", False),
            "routes_registered": len(ai_discovery_routes),
            "ai_discovery_routes": ai_discovery_routes,
            "ai_category_routes": len(ai_category_routes),  # 🆕 NEW
            "ai_category_route_details": ai_category_routes,  # 🆕 NEW
            "expected_routes": [
                "/api/admin/ai-discovery/health",
                "/api/admin/ai-discovery/active-providers", 
                "/api/admin/ai-discovery/discovered-suggestions",
                "/api/admin/ai-discovery/category-rankings",
                "/api/admin/ai-discovery/dashboard"
            ],
            "expected_ai_category_routes": [  # 🆕 NEW
                "/api/emergency/ai-categories",
                "/api/emergency/video-providers",
                "/api/emergency/provider-capabilities",
                "/api/emergency/trigger-ai-analysis"
            ],
            "emergency_endpoints_active": True,
            "ai_categories_emergency_active": len(ai_category_routes) > 0,  # 🆕 NEW
            "registration_issue": len(ai_discovery_routes) == 0 and router_status.get("ai_discovery", False),
            "troubleshooting": {
                "step_1": "Check if router file exists: src/routes/ai_platform_discovery.py",
                "step_2": "Verify router registration in router_registry.py",
                "step_3": "Check import statement works",
                "step_4": "Verify prefix is '/api/admin/ai-discovery'",
                "step_5": "Check emergency AI category endpoints are included"  # 🆕 NEW
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
        
        # Count AI category routes
        ai_category_routes = [r for r in routes_info if any(
            keyword in r['path'] for keyword in ['ai-categories', 'video-providers', 'provider-capabilities']
        )]
        
        return {
            "total_routes": len(routes_info),
            "route_groups": route_groups,
            "group_summary": {
                group: len(routes) for group, routes in route_groups.items()
            },
            "api_routes": len([r for r in routes_info if r['path'].startswith('/api')]),
            "admin_routes": len([r for r in routes_info if '/admin' in r['path']]),
            "emergency_routes": len([r for r in routes_info if 'emergency' in str(r.get('tags', []))]),
            "ai_category_routes": len(ai_category_routes),  # 🆕 NEW
            "ai_category_route_details": ai_category_routes  # 🆕 NEW
        }

    @app.get("/api/debug/system-info", tags=["debug"])
    async def debug_system_info():
        """Debug system information with AI category details"""
        import os
        import sys
        
        router_status = get_router_status()
        
        # Check AI category system
        ai_category_info = {
            "analyzer_available": False,
            "video_env_vars": {},
            "ai_api_keys": {}
        }
        
        try:
            from src.services.ai_provider_analyzer import get_dynamic_ai_provider_analyzer
            get_dynamic_ai_provider_analyzer()
            ai_category_info["analyzer_available"] = True
        except:
            pass
        
        # Check video-related environment variables
        video_vars = ['REPLICATE_API_TOKEN', 'FAL_API_KEY', 'MINIMAX_API_KEY']
        for var in video_vars:
            ai_category_info["video_env_vars"][var] = bool(os.getenv(var))
        
        # Check AI API keys for analysis
        ai_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY']
        for var in ai_vars:
            ai_category_info["ai_api_keys"][var] = bool(os.getenv(var))
        
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
            "ai_category_system": ai_category_info,  # 🆕 NEW
            "critical_paths": {
                "src_path_exists": os.path.exists("src"),
                "models_path_exists": os.path.exists("src/models"),
                "routes_path_exists": os.path.exists("src/routes"),
                "intelligence_path_exists": os.path.exists("src/intelligence"),
                "campaigns_path_exists": os.path.exists("src/campaigns"),
                "ai_provider_analyzer_exists": os.path.exists("src/services/ai_provider_analyzer.py")  # 🆕 NEW
            },
            "system_status": {
                "total_available_routers": sum(1 for status in router_status.values() if status),
                "critical_systems_ok": all(router_status.get(k, False) for k in ["auth"]),
                "ai_systems_available": any(router_status.get(k, False) for k in ["intelligence_main", "content", "ai_discovery"]),
                "emergency_mode_active": True,
                "ai_categories_ready": ai_category_info["analyzer_available"],  # 🆕 NEW
                "video_generation_ready": ai_category_info["analyzer_available"] and any(ai_category_info["video_env_vars"].values())  # 🆕 NEW
            }
        }

# ============================================================================
# ✅ FEATURE AVAILABILITY ENDPOINTS - ENHANCED
# ============================================================================

def include_feature_endpoints(app: FastAPI):
    """Include feature availability and capability endpoints with AI categories"""
    
    @app.get("/api/features", tags=["features"])
    async def get_available_features():
        """Get detailed feature availability including AI categories"""
        router_status = get_router_status()
        
        # Check AI category features
        ai_category_features = {
            "available": False,
            "video_detection": False,
            "dynamic_analysis": False,
            "cost_analysis": False
        }
        
        try:
            from src.services.ai_provider_analyzer import get_dynamic_ai_provider_analyzer
            analyzer = get_dynamic_ai_provider_analyzer()
            ai_category_features.update({
                "available": True,
                "video_detection": True,
                "dynamic_analysis": True,
                "cost_analysis": True
            })
        except:
            pass
        
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
                },
                
                # 🆕 NEW: AI Category Features
                "ai_category_system": {
                    "available": ai_category_features["available"],
                    "dynamic_categorization": ai_category_features["dynamic_analysis"],
                    "video_detection": ai_category_features["video_detection"],
                    "cost_analysis": ai_category_features["cost_analysis"],
                    "endpoints": [
                        "/api/emergency/ai-categories",
                        "/api/emergency/video-providers",
                        "/api/emergency/provider-capabilities",
                        "/api/emergency/trigger-ai-analysis"
                    ],
                    "status": "operational" if ai_category_features["available"] else "unavailable",
                    "emergency_endpoints": True
                },
                "video_generation": {
                    "available": ai_category_features["video_detection"],
                    "replicate_support": ai_category_features["available"],
                    "cost_optimization": ai_category_features["cost_analysis"],
                    "endpoints": ["/api/emergency/video-providers"],
                    "status": "operational" if ai_category_features["video_detection"] else "unavailable",
                    "providers_supported": ["Replicate", "Fal AI", "MiniMax"] if ai_category_features["available"] else []
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
        """Get system capabilities summary with AI category support"""
        router_status = get_router_status()
        
        # Check AI category capabilities
        ai_category_score = 0
        try:
            from src.services.ai_provider_analyzer import get_dynamic_ai_provider_analyzer
            get_dynamic_ai_provider_analyzer()
            ai_category_score = 1
        except:
            pass
        
        # Calculate capability scores
        core_score = sum(1 for k in ["auth", "campaigns", "dashboard"] if router_status.get(k, False)) / 3
        ai_score = sum(1 for k in ["intelligence_main", "content", "enhanced_email", "stability", "ai_monitoring", "ai_discovery"] if router_status.get(k, False)) / 6
        storage_score = sum(1 for k in ["storage", "document"] if router_status.get(k, False)) / 2
        admin_score = sum(1 for k in ["admin", "waitlist", "dynamic_ai_providers"] if router_status.get(k, False)) / 3
        ai_category_capability = ai_category_score  # 0 or 1
        
        # Include AI category in overall calculation
        overall_score = (core_score + ai_score + storage_score + admin_score + ai_category_capability) / 5
        
        return {
            "overall_capability": round(overall_score * 100, 1),
            "capability_breakdown": {
                "core_systems": round(core_score * 100, 1),
                "ai_systems": round(ai_score * 100, 1), 
                "storage_systems": round(storage_score * 100, 1),
                "admin_systems": round(admin_score * 100, 1),
                "ai_category_system": round(ai_category_capability * 100, 1)  # 🆕 NEW
            },
            "ready_for_production": overall_score >= 0.7,
            "critical_systems_operational": core_score >= 0.67,
            "ai_systems_operational": ai_score >= 0.33,
            "video_generation_ready": ai_category_capability >= 1,  # 🆕 NEW
            "emergency_mode_active": overall_score < 1.0,
            "recommended_actions": get_recommended_actions(router_status, ai_category_capability),
            "system_strengths": get_system_strengths(router_status, ai_category_capability),
            "next_priorities": get_next_priorities(router_status, ai_category_capability)
        }

def get_recommended_actions(router_status, ai_category_capability):
    """Get recommended actions based on router status and AI capabilities"""
    actions = []
    
    if not router_status.get("auth", False):
        actions.append("CRITICAL: Fix authentication router - system unusable without auth")
    
    if not router_status.get("campaigns", False):
        actions.append("HIGH: Fix campaigns router - core functionality missing")
    
    if not router_status.get("content", False) and not router_status.get("intelligence_main", False):
        actions.append("HIGH: Fix content generation - key differentiator missing")
    
    if not router_status.get("ai_discovery", False):
        actions.append("MEDIUM: AI Discovery system available but not fully integrated")
    
    if ai_category_capability < 1:
        actions.append("MEDIUM: Enable AI category system for video generation support")  # 🆕 NEW
    
    if not router_status.get("storage", False):
        actions.append("MEDIUM: Enable storage system for file handling")
    
    if len(actions) == 0:
        actions.append("✅ All systems operational - ready for production with AI categories")  # 🆕 Enhanced
    
    return actions

def get_system_strengths(router_status, ai_category_capability):
    """Get system strengths based on available routers and AI capabilities"""
    strengths = []
    
    if router_status.get("auth", False):
        strengths.append("✅ User authentication and security")
    
    if router_status.get("ai_discovery", False):
        strengths.append("✅ AI Platform Discovery System (v3.3.0)")
    
    if ai_category_capability >= 1:
        strengths.append("✅ Dynamic AI categorization and video detection (v3.3.1)")  # 🆕 NEW
    
    if router_status.get("enhanced_email", False):
        strengths.append("✅ Enhanced email generation with AI learning")
    
    if router_status.get("stability", False):
        strengths.append("✅ Ultra-cheap AI image generation (90% cost savings)")
    
    if router_status.get("ai_monitoring", False):
        strengths.append("✅ Real-time AI monitoring and optimization")
    
    if router_status.get("storage_system", False):
        strengths.append("✅ Dual storage system with automatic failover")
    
    return strengths

def get_next_priorities(router_status, ai_category_capability):
    """Get next development priorities including AI category considerations"""
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
    
    if ai_category_capability >= 1:
        priorities.append("Integrate video generation into campaign creation workflow")  # 🆕 NEW
    else:
        priorities.append("Enable AI category system for video generation support")  # 🆕 NEW
    
    return priorities

# ============================================================================
# ✅ MAIN INCLUDE FUNCTION
# ============================================================================

def include_core_endpoints(app: FastAPI):
    """Include all core endpoints in the FastAPI app"""
    include_health_endpoints(app)
    include_debug_endpoints(app)
    include_feature_endpoints(app)
    
    logging.info("✅ Core endpoints included: health, debug, and features with AI category support")

# ============================================================================
# ✅ EXPORTS
# ============================================================================

__all__ = [
    'include_core_endpoints',
    'include_health_endpoints', 
    'include_debug_endpoints',
    'include_feature_endpoints'
]