# src/api/emergency_endpoints.py - Emergency & Fallback Routes
"""
All emergency endpoints and fallback functionality with LIVE DATABASE QUERIES
Responsibility: Emergency AI Discovery endpoints (live data versions),
Emergency campaign endpoints, Emergency dashboard endpoints, Emergency content endpoints,
Fallback route handlers, Live database queries replacing mock data,
NEW: AI Category Emergency Endpoints with Dynamic Analysis
"""

import logging
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, or_

logger = logging.getLogger(__name__)

# ============================================================================
# 🆕 EMERGENCY AI CATEGORY ENDPOINTS (DYNAMIC AI ANALYSIS)
# ============================================================================

def include_emergency_ai_category_endpoints(app: FastAPI):
    """🎥 NEW: Emergency AI category endpoints with dynamic analysis"""

    @app.get("/api/emergency/ai-categories", tags=["emergency-ai-categories"])
    async def emergency_ai_categories():
        """🚨 Emergency endpoint - AI categories with dynamic analysis fallback"""
        try:
            from src.core.ai_discovery_database import get_ai_discovery_session, ActiveAIProvider

            async with get_ai_discovery_session() as db:
                result = await db.execute(
                    select(ActiveAIProvider.category, func.count(ActiveAIProvider.id).label('count'))
                    .where(ActiveAIProvider.is_active == True)
                    .group_by(ActiveAIProvider.category)
                )
                category_data = result.all()

                categories = {}
                for category, count in category_data:
                    providers_result = await db.execute(
                        select(ActiveAIProvider)
                        .where(ActiveAIProvider.category == category)
                        .where(ActiveAIProvider.is_active == True)
                        .order_by(ActiveAIProvider.category_rank.asc().nulls_last())
                    )
                    providers = providers_result.scalars().all()

                    categories[category] = [
                        {
                            "provider_name": p.provider_name,
                            "env_var_name": p.env_var_name,
                            "is_active": p.is_active,
                            "quality_score": float(p.quality_score) if p.quality_score else None,
                            "cost_per_1k_tokens": float(p.cost_per_1k_tokens) if p.cost_per_1k_tokens else None,
                            "video_cost_per_minute": float(p.video_cost_per_minute) if p.video_cost_per_minute else None,
                            "capabilities": p.capabilities,
                            "ai_confidence_score": float(p.ai_confidence_score) if p.ai_confidence_score else None
                        }
                        for p in providers
                    ]

                return {
                    "success": True,
                    "status": "operational",
                    "database_connected": True,
                    "categories": categories,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "✅ AI categories retrieved with live database"
                }

        except Exception as e:
            logger.error(f"Emergency AI category check failed: {e}")
            return {
                "success": False,
                "status": "error",
                "error": str(e),
                "database_connected": False,
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
            from src.models.campaign import Campaign

            db = None
            async for session in get_async_db():
                db = session
                break

            if db:
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

                campaigns_data = [
                    {
                        "id": str(campaign.id),
                        "name": campaign.name,
                        "description": campaign.description,
                        "status": campaign.status,
                        "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
                        "updated_at": campaign.updated_at.isoformat() if campaign.updated_at else None,
                        "data_source": "live_database"
                    }
                    for campaign in campaigns
                ]

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

            db = None
            async for session in get_async_db():
                db = session
                break

            if db:
                campaign_result = await db.execute(select(func.count(Campaign.id)))
                total_campaigns = campaign_result.scalar() or 0

                user_result = await db.execute(select(func.count(User.id)))
                total_users = user_result.scalar() or 0

                company_result = await db.execute(select(func.count(Company.id)))
                total_companies = company_result.scalar() or 0

                return {
                    "success": True,
                    "stats": {
                        "total_campaigns_created": total_campaigns,
                        "active_campaigns": total_campaigns,
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
            from src.intelligence.utils.ultra_cheap_ai_provider import get_ultra_cheap_provider

            provider = get_ultra_cheap_provider()
            prompt = request_data.get("prompt", "Generate a sample marketing campaign")

            try:
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
            from src.intelligence.utils.ultra_cheap_ai_provider import get_ultra_cheap_provider
            provider = get_ultra_cheap_provider()

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

    include_emergency_ai_category_endpoints(app)
    include_emergency_campaign_endpoints(app)
    include_emergency_dashboard_endpoints(app)
    include_emergency_content_endpoints(app)

    @app.get("/api/emergency/status", tags=["emergency"])
    async def emergency_system_status():
        subsystems = {
            "ai_discovery": False,
            "campaigns": False,
            "dashboard": False,
            "content": False,
            "database": False
        }

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

        try:
            from src.core.ai_discovery_database import test_ai_discovery_connection
            subsystems["ai_discovery"] = test_ai_discovery_connection()
        except:
            pass

        try:
            from src.models.campaign import Campaign
            subsystems["campaigns"] = True
        except:
            pass

        try:
            from src.intelligence.utils.ultra_cheap_ai_provider import get_ultra_cheap_provider
            get_ultra_cheap_provider()
            subsystems["content"] = True
        except:
            pass

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

__all__ = [
    'include_emergency_endpoints',
    'include_emergency_ai_category_endpoints',
    'include_emergency_campaign_endpoints',
    'include_emergency_dashboard_endpoints',
    'include_emergency_content_endpoints'
]