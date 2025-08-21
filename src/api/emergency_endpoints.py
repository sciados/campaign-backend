# src/api/emergency_endpoints.py - Emergency & Fallback Routes
"""
All emergency endpoints and fallback functionality with LIVE DATABASE QUERIES
Responsibility: Emergency AI Discovery endpoints (live data versions),
Emergency campaign endpoints, Emergency dashboard endpoints, Emergency content endpoints,
Fallback route handlers, Live database queries replacing mock data
"""

import logging
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ============================================================================
# 🚨 EMERGENCY AI DISCOVERY ENDPOINTS (LIVE DATABASE)
# ============================================================================

def include_emergency_ai_discovery_endpoints(app: FastAPI):
    """🧪 Emergency AI Discovery endpoints with LIVE database queries"""
    
    @app.get("/api/admin/ai-discovery/test", tags=["emergency-ai-discovery"])
    async def emergency_ai_discovery_test():
        """🧪 Emergency test endpoint for AI Discovery"""
        return {
            "success": True,
            "message": "✅ AI Discovery emergency endpoint working!",
            "router_status": "emergency mode",
            "timestamp": datetime.utcnow().isoformat(),
            "next_step": "Check if router registration worked",
            "live_data": "Emergency endpoints use live database queries"
        }

    @app.get("/api/admin/ai-discovery/health", tags=["emergency-ai-discovery"])
    async def emergency_ai_discovery_health():
        """✅ Emergency health check for AI Discovery with database connection test"""
        try:
            # Test AI Discovery database connection
            from src.core.ai_discovery_database import test_ai_discovery_connection
            db_connected = test_ai_discovery_connection()
            
            return {
                "status": "healthy" if db_connected else "degraded",
                "service": "AI Platform Discovery System (Emergency Mode)",
                "version": "1.0.0-emergency",
                "database_connected": db_connected,
                "endpoints_active": True,
                "mode": "emergency_fallback_with_live_data",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Emergency AI Discovery health check failed: {e}")
            return {
                "status": "error",
                "service": "AI Platform Discovery System (Emergency Mode)",
                "error": str(e),
                "database_connected": False,
                "endpoints_active": True,
                "mode": "mock_data_fallback"
            }

    @app.get("/api/admin/ai-discovery/active-providers", tags=["emergency-ai-discovery"])
    async def emergency_active_providers():
        """📋 Emergency active providers endpoint with LIVE DATABASE QUERY"""
        try:
            # Try to get live data from AI Discovery database
            from src.core.ai_discovery_database import get_ai_discovery_session
            
            async with get_ai_discovery_session() as db:
                # Import models
                from src.core.ai_discovery_database import ActiveAIProvider
                
                # Query live active providers
                result = await db.execute(
                    select(ActiveAIProvider)
                    .where(ActiveAIProvider.is_active == True)
                    .order_by(ActiveAIProvider.category, ActiveAIProvider.category_rank)
                )
                active_providers = result.scalars().all()
                
                # Convert to response format
                providers_data = []
                for provider in active_providers:
                    providers_data.append({
                        "id": provider.id,
                        "provider_name": provider.provider_name,
                        "env_var_name": provider.env_var_name,
                        "category": provider.category,
                        "is_active": provider.is_active,
                        "is_top_3": provider.is_top_3,
                        "quality_score": float(provider.quality_score) if provider.quality_score else 0.0,
                        "cost_per_1k_tokens": float(provider.cost_per_1k_tokens) if provider.cost_per_1k_tokens else 0.0,
                        "category_rank": provider.category_rank,
                        "last_tested": provider.last_tested.isoformat() if provider.last_tested else None
                    })
                
                return {
                    "success": True,
                    "providers": providers_data,
                    "total_count": len(providers_data),
                    "data_source": "live_database",
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "✅ Live data from AI Discovery database"
                }
                
        except Exception as e:
            logger.error(f"Live data query failed, using fallback: {e}")
            
            # Fallback to enhanced mock data
            return {
                "success": True,
                "providers": [
                    {
                        "id": 1,
                        "provider_name": "OpenAI",
                        "env_var_name": "OPENAI_API_KEY",
                        "category": "text_generation",
                        "is_active": True,
                        "is_top_3": True,
                        "quality_score": 4.8,
                        "cost_per_1k_tokens": 0.020,
                        "category_rank": 2
                    },
                    {
                        "id": 2,
                        "provider_name": "Anthropic",
                        "env_var_name": "ANTHROPIC_API_KEY", 
                        "category": "text_generation",
                        "is_active": True,
                        "is_top_3": True,
                        "quality_score": 4.9,
                        "cost_per_1k_tokens": 0.008,
                        "category_rank": 1
                    },
                    {
                        "id": 3,
                        "provider_name": "Groq",
                        "env_var_name": "GROQ_API_KEY",
                        "category": "text_generation", 
                        "is_active": True,
                        "is_top_3": True,
                        "quality_score": 4.3,
                        "cost_per_1k_tokens": 0.00027,
                        "category_rank": 3
                    },
                    {
                        "id": 4,
                        "provider_name": "Stability AI",
                        "env_var_name": "STABILITY_API_KEY",
                        "category": "image_generation",
                        "is_active": True,
                        "is_top_3": True,
                        "quality_score": 4.5,
                        "cost_per_1k_tokens": 0.002  # Per image equivalent
                    }
                ],
                "total_count": 4,
                "data_source": "emergency_mock",
                "message": "⚠️ Database unavailable - using enhanced mock data",
                "timestamp": datetime.utcnow().isoformat()
            }

    @app.get("/api/admin/ai-discovery/discovered-suggestions", tags=["emergency-ai-discovery"])
    async def emergency_discovered_suggestions():
        """🔍 Emergency discovered suggestions endpoint with LIVE DATABASE QUERY"""
        try:
            # Try to get live data from AI Discovery database
            from src.core.ai_discovery_database import get_ai_discovery_session
            
            async with get_ai_discovery_session() as db:
                # Import models
                from src.core.ai_discovery_database import DiscoveredAIProvider
                
                # Query live discovered suggestions
                result = await db.execute(
                    select(DiscoveredAIProvider)
                    .where(DiscoveredAIProvider.review_status == 'pending')
                    .order_by(DiscoveredAIProvider.recommendation_priority.desc(), DiscoveredAIProvider.discovered_at.desc())
                )
                suggestions = result.scalars().all()
                
                # Convert to response format
                suggestions_data = []
                for suggestion in suggestions:
                    suggestions_data.append({
                        "id": suggestion.id,
                        "provider_name": suggestion.provider_name,
                        "suggested_env_var_name": f"{suggestion.provider_name.upper().replace(' ', '_')}_API_KEY",
                        "category": suggestion.category,
                        "recommendation_priority": suggestion.recommendation_priority,
                        "estimated_quality_score": float(suggestion.estimated_quality) if suggestion.estimated_quality else 0.0,
                        "estimated_cost_per_1k": float(suggestion.estimated_cost_per_1k) if suggestion.estimated_cost_per_1k else 0.0,
                        "unique_features": suggestion.unique_features,
                        "market_positioning": suggestion.market_positioning,
                        "competitive_advantages": suggestion.competitive_advantages,
                        "integration_complexity": suggestion.integration_complexity,
                        "discovered_at": suggestion.discovered_at.isoformat() if suggestion.discovered_at else None
                    })
                
                return {
                    "success": True,
                    "suggestions": suggestions_data,
                    "total_count": len(suggestions_data),
                    "data_source": "live_database",
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "✅ Live suggestions from AI Discovery database"
                }
                
        except Exception as e:
            logger.error(f"Live suggestions query failed, using fallback: {e}")
            
            # Fallback to enhanced mock data
            return {
                "success": True,
                "suggestions": [
                    {
                        "id": 1,
                        "provider_name": "Mistral AI",
                        "suggested_env_var_name": "MISTRAL_API_KEY",
                        "category": "text_generation",
                        "recommendation_priority": "high",
                        "estimated_quality_score": 4.2,
                        "estimated_cost_per_1k": 0.0006,
                        "unique_features": ["European-based", "GDPR compliant", "Multilingual"],
                        "market_positioning": "Privacy-focused AI with strong European presence",
                        "competitive_advantages": ["Data privacy", "Cost efficiency", "Multi-language support"],
                        "integration_complexity": "easy",
                        "website_url": "https://mistral.ai"
                    },
                    {
                        "id": 2,
                        "provider_name": "Cohere",
                        "suggested_env_var_name": "COHERE_API_KEY",
                        "category": "text_generation",
                        "recommendation_priority": "medium",
                        "estimated_quality_score": 4.0,
                        "estimated_cost_per_1k": 0.0015,
                        "unique_features": ["Enterprise-focused", "Fine-tuning capabilities"],
                        "market_positioning": "Enterprise AI solutions provider",
                        "competitive_advantages": ["Business optimization", "Custom model training"],
                        "integration_complexity": "medium"
                    }
                ],
                "total_count": 2,
                "data_source": "emergency_mock",
                "message": "⚠️ Database unavailable - using enhanced mock suggestions",
                "timestamp": datetime.utcnow().isoformat()
            }

    @app.get("/api/admin/ai-discovery/category-rankings", tags=["emergency-ai-discovery"])
    async def emergency_category_rankings():
        """🏆 Emergency category rankings endpoint with LIVE DATABASE QUERY"""
        try:
            # Try to get live data from AI Discovery database
            from src.core.ai_discovery_database import get_ai_discovery_session
            
            async with get_ai_discovery_session() as db:
                # Import models
                from src.core.ai_discovery_database import ActiveAIProvider
                
                # Query rankings by category
                categories = ["text_generation", "image_generation", "video_generation", "audio_generation", "multimodal"]
                category_rankings = {}
                
                for category in categories:
                    result = await db.execute(
                        select(ActiveAIProvider)
                        .where(ActiveAIProvider.category == category)
                        .where(ActiveAIProvider.is_active == True)
                        .where(ActiveAIProvider.is_top_3 == True)
                        .order_by(ActiveAIProvider.category_rank)
                    )
                    providers = result.scalars().all()
                    
                    if providers:
                        category_rankings[category] = []
                        for provider in providers:
                            category_rankings[category].append({
                                "rank": provider.category_rank,
                                "provider_name": provider.provider_name,
                                "quality_score": float(provider.quality_score) if provider.quality_score else 0.0,
                                "cost_per_1k_tokens": float(provider.cost_per_1k_tokens) if provider.cost_per_1k_tokens else 0.0,
                                "is_active": provider.is_active,
                                "response_time_ms": provider.response_time_ms
                            })
                
                return {
                    "success": True,
                    "category_rankings": category_rankings,
                    "total_categories": len(category_rankings),
                    "data_source": "live_database",
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "✅ Live rankings from AI Discovery database"
                }
                
        except Exception as e:
            logger.error(f"Live rankings query failed, using fallback: {e}")
            
            # Fallback to enhanced mock data
            return {
                "success": True,
                "category_rankings": {
                    "text_generation": [
                        {
                            "rank": 1,
                            "provider_name": "Anthropic",
                            "quality_score": 4.9,
                            "cost_per_1k_tokens": 0.008,
                            "is_active": True,
                            "response_time_ms": 850
                        },
                        {
                            "rank": 2,
                            "provider_name": "OpenAI",
                            "quality_score": 4.8,
                            "cost_per_1k_tokens": 0.020,
                            "is_active": True,
                            "response_time_ms": 1200
                        },
                        {
                            "rank": 3,
                            "provider_name": "Groq",
                            "quality_score": 4.3,
                            "cost_per_1k_tokens": 0.00027,
                            "is_active": True,
                            "response_time_ms": 300
                        }
                    ],
                    "image_generation": [
                        {
                            "rank": 1,
                            "provider_name": "Stability AI",
                            "quality_score": 4.5,
                            "cost_per_image": 0.002,
                            "is_active": True,
                            "response_time_ms": 3000
                        },
                        {
                            "rank": 2,
                            "provider_name": "DALL-E 3",
                            "quality_score": 4.7,
                            "cost_per_image": 0.040,
                            "is_active": True,
                            "response_time_ms": 8000
                        }
                    ]
                },
                "total_categories": 2,
                "data_source": "emergency_mock",
                "message": "⚠️ Database unavailable - using enhanced mock rankings",
                "timestamp": datetime.utcnow().isoformat()
            }

    @app.get("/api/admin/ai-discovery/dashboard", tags=["emergency-ai-discovery"])
    async def emergency_ai_discovery_dashboard():
        """🎯 Emergency AI Discovery dashboard with LIVE DATABASE QUERY"""
        try:
            # Try to get live data from AI Discovery database
            from src.core.ai_discovery_database import get_ai_discovery_session
            
            async with get_ai_discovery_session() as db:
                # Import models
                from src.core.ai_discovery_database import ActiveAIProvider, DiscoveredAIProvider
                
                # Get active providers stats
                active_result = await db.execute(
                    select(func.count(ActiveAIProvider.id))
                    .where(ActiveAIProvider.is_active == True)
                )
                total_active = active_result.scalar() or 0
                
                # Get discovered suggestions stats
                discovered_result = await db.execute(
                    select(func.count(DiscoveredAIProvider.id))
                    .where(DiscoveredAIProvider.review_status == 'pending')
                )
                total_discovered = discovered_result.scalar() or 0
                
                # Get recent discoveries
                recent_result = await db.execute(
                    select(DiscoveredAIProvider)
                    .where(DiscoveredAIProvider.review_status == 'pending')
                    .order_by(DiscoveredAIProvider.discovered_at.desc())
                    .limit(5)
                )
                recent_discoveries = recent_result.scalars().all()
                
                recent_data = []
                for discovery in recent_discoveries:
                    recent_data.append({
                        "id": discovery.id,
                        "provider_name": discovery.provider_name,
                        "category": discovery.category,
                        "recommendation_priority": discovery.recommendation_priority,
                        "discovered_date": discovery.discovered_at.isoformat() if discovery.discovered_at else None
                    })
                
                return {
                    "success": True,
                    "dashboard": {
                        "active_providers": {
                            "total": total_active,
                            "by_category": []  # Would need additional queries for full breakdown
                        },
                        "discovered_providers": {
                            "total": total_discovered,
                            "by_category": []  # Would need additional queries for full breakdown
                        },
                        "recent_discoveries": recent_data,
                        "system_status": "operational",
                        "last_discovery_cycle": datetime.utcnow().isoformat(),
                        "database_connected": True
                    },
                    "data_source": "live_database",
                    "message": "✅ Live dashboard data from AI Discovery database",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Live dashboard query failed, using fallback: {e}")
            
            # Fallback to enhanced mock data
            return {
                "success": True,
                "dashboard": {
                    "active_providers": {
                        "total": 4,
                        "by_category": [
                            {"category": "text_generation", "total": 3, "active": 3, "top_3": 3},
                            {"category": "image_generation", "total": 1, "active": 1, "top_3": 1}
                        ]
                    },
                    "discovered_providers": {
                        "total": 2,
                        "by_category": [
                            {"category": "text_generation", "total": 2, "high_priority": 1}
                        ]
                    },
                    "recent_discoveries": [
                        {
                            "id": 1,
                            "provider_name": "Mistral AI",
                            "category": "text_generation",
                            "recommendation_priority": "high",
                            "discovered_date": datetime.utcnow().isoformat()
                        },
                        {
                            "id": 2,
                            "provider_name": "Cohere",
                            "category": "text_generation",
                            "recommendation_priority": "medium",
                            "discovered_date": datetime.utcnow().isoformat()
                        }
                    ],
                    "system_status": "operational",
                    "last_discovery_cycle": datetime.utcnow().isoformat(),
                    "database_connected": False
                },
                "data_source": "emergency_mock",
                "message": "⚠️ Database unavailable - using enhanced mock dashboard",
                "timestamp": datetime.utcnow().isoformat()
            }

    @app.post("/api/admin/ai-discovery/run-discovery", tags=["emergency-ai-discovery"])
    async def emergency_run_discovery():
        """🔄 Emergency run discovery endpoint with LIVE DATABASE OPERATIONS"""
        try:
            # Try to perform live discovery operations
            from src.services.ai_platform_discovery import get_discovery_service
            
            discovery_service = get_discovery_service()
            
            # Run environment scan
            env_results = await discovery_service.scan_environment_variables()
            
            # Run web research (simplified for emergency mode)
            web_results = {"new_discoveries": 0, "status": "emergency_mode_limited"}
            
            # Try to save results to database
            try:
                from src.core.ai_discovery_database import get_ai_discovery_session
                
                async with get_ai_discovery_session() as db:
                    # Simple database operation test
                    await db.execute(text("SELECT 1"))
                    database_operational = True
                    
            except Exception:
                database_operational = False
            
            return {
                "success": True,
                "message": "🔄 AI discovery cycle completed (emergency mode)",
                "status": "completed",
                "database_operational": database_operational,
                "results": {
                    "environment_scan": env_results if env_results else {"providers_found": 0},
                    "web_research": web_results,
                    "database_updated": database_operational,
                    "mode": "emergency_with_live_scanning"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Emergency discovery run failed: {e}")
            
            return {
                "success": False,
                "message": "🔄 AI discovery cycle failed (emergency mode)",
                "status": "failed",
                "error": str(e),
                "fallback_results": {
                    "environment_scan": {"providers_found": 0},
                    "web_research": {"new_discoveries": 0},
                    "status": "emergency_mock_mode"
                },
                "timestamp": datetime.utcnow().isoformat()
            }

# ============================================================================
# 🚨 EMERGENCY CAMPAIGN ENDPOINTS (LIVE DATABASE)
# ============================================================================

def include_emergency_campaign_endpoints(app: FastAPI):
    """🚨 Emergency campaign endpoints with LIVE DATABASE QUERIES"""
    
    @app.get("/api/campaigns/emergency-health", tags=["emergency-campaigns"])
    async def emergency_campaign_health():
        """Check campaign system health with database connectivity"""
        try:
            from src.core.database import get_async_db
            
            # Test database connection
            db = None
            async for session in get_async_db():
                db = session
                break
            
            if db:
                # Test campaign table access
                from src.models.campaign import Campaign
                result = await db.execute(select(func.count(Campaign.id)))
                campaign_count = result.scalar()
                
                return {
                    "success": True,
                    "status": "operational",
                    "database_connected": True,
                    "total_campaigns": campaign_count,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "✅ Campaign system operational with live database"
                }
            else:
                return {
                    "success": False,
                    "status": "database_error",
                    "database_connected": False,
                    "message": "❌ Database connection failed"
                }
                
        except Exception as e:
            logger.error(f"Emergency campaign health check failed: {e}")
            return {
                "success": False,
                "status": "error",
                "error": str(e),
                "database_connected": False,
                "timestamp": datetime.utcnow().isoformat()
            }

    @app.get("/api/campaigns/emergency-list", tags=["emergency-campaigns"])
    async def emergency_campaign_list():
        """Emergency campaign list with LIVE DATABASE QUERY"""
        try:
            from src.core.database import get_async_db
            from src.models.campaign import Campaign
            
            # Get live campaign data
            db = None
            async for session in get_async_db():
                db = session
                break
            
            if db:
                result = await db.execute(
                    select(Campaign)
                    .order_by(Campaign.created_at.desc())
                    .limit(10)
                )
                campaigns = result.scalars().all()
                
                campaigns_data = []
                for campaign in campaigns:
                    campaigns_data.append({
                        "id": str(campaign.id),
                        "name": campaign.name,
                        "description": campaign.description,
                        "status": campaign.status,
                        "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
                        "updated_at": campaign.updated_at.isoformat() if campaign.updated_at else None,
                        "data_source": "live_database"
                    })
                
                return {
                    "success": True,
                    "campaigns": campaigns_data,
                    "total_count": len(campaigns_data),
                    "data_source": "live_database",
                    "message": "✅ Live campaigns from database",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                raise Exception("Database connection failed")
                
        except Exception as e:
            logger.error(f"Live campaign query failed, using fallback: {e}")
            
            # Fallback to mock data
            return {
                "success": True,
                "campaigns": [
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Emergency Campaign Sample",
                        "description": "Sample campaign data - database unavailable",
                        "status": "emergency",
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                        "data_source": "emergency_mock"
                    }
                ],
                "total_count": 1,
                "data_source": "emergency_mock",
                "message": "⚠️ Database unavailable - using mock campaign data",
                "timestamp": datetime.utcnow().isoformat()
            }

# ============================================================================
# 🚨 EMERGENCY DASHBOARD ENDPOINTS (LIVE DATABASE)
# ============================================================================

def include_emergency_dashboard_endpoints(app: FastAPI):
    """🚨 Emergency dashboard endpoints with LIVE DATABASE QUERIES"""
    
    @app.get("/api/dashboard/emergency-stats", tags=["emergency-dashboard"])
    async def emergency_dashboard_stats():
        """Emergency dashboard stats with LIVE DATABASE QUERY"""
        try:
            from src.core.database import get_async_db
            from src.models.campaign import Campaign
            from src.models.user import User
            from src.models.company import Company
            
            # Get live dashboard data
            db = None
            async for session in get_async_db():
                db = session
                break
            
            if db:
                # Get campaign count
                campaign_result = await db.execute(select(func.count(Campaign.id)))
                total_campaigns = campaign_result.scalar() or 0
                
                # Get user count
                user_result = await db.execute(select(func.count(User.id)))
                total_users = user_result.scalar() or 0
                
                # Get company count  
                company_result = await db.execute(select(func.count(Company.id)))
                total_companies = company_result.scalar() or 0
                
                return {
                    "success": True,
                    "stats": {
                        "total_campaigns_created": total_campaigns,
                        "active_campaigns": total_campaigns,  # Simplified
                        "total_users": total_users,
                        "total_companies": total_companies,
                        "subscription_tier": "free",
                        "monthly_credits_used": 0,
                        "monthly_credits_limit": 5000,
                        "credits_remaining": 5000,
                        "usage_percentage": 0.0
                    },
                    "data_source": "live_database",
                    "message": "✅ Live dashboard stats from database",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                raise Exception("Database connection failed")
                
        except Exception as e:
            logger.error(f"Live dashboard query failed, using fallback: {e}")
            
            # Fallback to mock data
            return {
                "success": True,
                "stats": {
                    "company_name": "CampaignForge",
                    "subscription_tier": "free",
                    "monthly_credits_used": 0,
                    "monthly_credits_limit": 5000,
                    "credits_remaining": 5000,
                    "total_campaigns_created": 0,
                    "active_campaigns": 0,
                    "team_members": 1,
                    "campaigns_this_month": 0,
                    "usage_percentage": 0.0
                },
                "data_source": "emergency_mock",
                "message": "⚠️ Database unavailable - using mock dashboard data",
                "timestamp": datetime.utcnow().isoformat()
            }

# ============================================================================
# 🚨 EMERGENCY CONTENT ENDPOINTS (LIVE AI SERVICES)
# ============================================================================

def include_emergency_content_endpoints(app: FastAPI):
    """🚨 Emergency content endpoints with LIVE AI SERVICE CALLS"""
    
    @app.post("/api/intelligence/content/emergency-generate", tags=["emergency-content"])
    async def emergency_generate_content(request_data: dict):
        """Emergency content generation with LIVE AI SERVICE CALLS"""
        try:
            # Try to use live AI services
            from src.intelligence.utils.ultra_cheap_ai_provider import get_ultra_cheap_provider
            
            provider = get_ultra_cheap_provider()
            
            # Simple content generation
            prompt = request_data.get("prompt", "Generate a sample marketing campaign")
            
            try:
                # Attempt live AI generation
                generated_content = await provider.generate_text(
                    prompt=prompt,
                    max_tokens=500
                )
                
                return {
                    "success": True,
                    "content_id": str(uuid.uuid4()),
                    "content_type": "ai_generated",
                    "generated_content": {
                        "title": "Emergency AI Generated Content",
                        "content": generated_content,
                        "metadata": {
                            "ai_provider": provider.provider_name,
                            "generation_method": "live_ai_service",
                            "emergency_mode": True
                        }
                    },
                    "ai_service_used": True,
                    "data_source": "live_ai_generation",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as ai_error:
                logger.error(f"Live AI generation failed: {ai_error}")
                raise ai_error
                
        except Exception as e:
            logger.error(f"Emergency content generation failed, using fallback: {e}")
            
            # Fallback to template content
            return {
                "success": True,
                "content_id": str(uuid.uuid4()),
                "content_type": "template",
                "generated_content": {
                    "title": "Emergency Template Content",
                    "content": {
                        "headline": "Your Campaign Headline Here",
                        "description": "Campaign description based on your input",
                        "call_to_action": "Take Action Now",
                        "body": "This is emergency template content. AI services are temporarily unavailable."
                    },
                    "metadata": {
                        "generation_method": "emergency_template",
                        "ai_service_used": False,
                        "emergency_mode": True
                    }
                },
                "ai_service_used": False,
                "data_source": "emergency_template",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    @app.get("/api/intelligence/content/emergency-health", tags=["emergency-content"])
    async def emergency_content_health():
        """Check content generation system health"""
        try:
            # Test AI service availability
            from src.intelligence.utils.ultra_cheap_ai_provider import get_ultra_cheap_provider
            
            provider = get_ultra_cheap_provider()
            
            # Simple health check
            test_response = await provider.generate_text(
                prompt="Test health check",
                max_tokens=10
            )
            
            return {
                "success": True,
                "status": "operational",
                "ai_services_available": True,
                "provider_name": provider.provider_name,
                "test_response": test_response[:50] + "..." if test_response else "No response",
                "message": "✅ Content generation services operational",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Content health check failed: {e}")
            
            return {
                "success": False,
                "status": "degraded",
                "ai_services_available": False,
                "error": str(e),
                "message": "⚠️ Content generation services unavailable - template mode active",
                "timestamp": datetime.utcnow().isoformat()
            }

# ============================================================================
# ✅ MAIN INCLUDE FUNCTION
# ============================================================================

def include_emergency_endpoints(app: FastAPI):
    """Include all emergency endpoints with LIVE DATABASE QUERIES"""
    
    # Include all emergency endpoint groups
    include_emergency_ai_discovery_endpoints(app)
    include_emergency_campaign_endpoints(app)
    include_emergency_dashboard_endpoints(app)
    include_emergency_content_endpoints(app)
    
    # Add general emergency status endpoint
    @app.get("/api/emergency/status", tags=["emergency"])
    async def emergency_system_status():
        """Overall emergency system status"""
        
        # Test each subsystem
        subsystems = {
            "ai_discovery": False,
            "campaigns": False, 
            "dashboard": False,
            "content": False,
            "database": False
        }
        
        # Test database
        try:
            from src.core.database import get_async_db
            db = None
            async for session in get_async_db():
                db = session
                break
            if db:
                await db.execute(text("SELECT 1"))
                subsystems["database"] = True
        except:
            pass
        
        # Test AI Discovery database
        try:
            from src.core.ai_discovery_database import test_ai_discovery_connection
            subsystems["ai_discovery"] = test_ai_discovery_connection()
        except:
            pass
        
        # Test campaigns
        try:
            from src.models.campaign import Campaign
            subsystems["campaigns"] = True
        except:
            pass
        
        # Test content generation
        try:
            from src.intelligence.utils.ultra_cheap_ai_provider import get_ultra_cheap_provider
            get_ultra_cheap_provider()
            subsystems["content"] = True
        except:
            pass
        
        # Set dashboard based on database
        subsystems["dashboard"] = subsystems["database"]
        
        operational_count = sum(1 for status in subsystems.values() if status)
        total_systems = len(subsystems)
        
        return {
            "success": True,
            "emergency_mode": True,
            "system_status": "operational" if operational_count >= 3 else "degraded",
            "subsystems": subsystems,
            "operational_percentage": round((operational_count / total_systems) * 100, 1),
            "operational_systems": operational_count,
            "total_systems": total_systems,
            "live_data_available": subsystems["database"] or subsystems["ai_discovery"],
            "ai_services_available": subsystems["content"],
            "critical_systems_ok": subsystems["database"],
            "message": f"✅ {operational_count}/{total_systems} emergency systems operational",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    logger.info("✅ Emergency endpoints included with live database query capabilities")

# ============================================================================
# ✅ EXPORTS
# ============================================================================

__all__ = [
    'include_emergency_endpoints',
    'include_emergency_ai_discovery_endpoints',
    'include_emergency_campaign_endpoints', 
    'include_emergency_dashboard_endpoints',
    'include_emergency_content_endpoints'
]