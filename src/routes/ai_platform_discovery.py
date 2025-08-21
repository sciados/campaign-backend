# src/routes/ai_platform_discovery.py - FIXED VERSION

import os
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from src.core.ai_discovery_database import get_ai_discovery_db
from src.services.ai_platform_discovery import (
    get_discovery_service, 
    ActiveAIProvider, 
    DiscoveredAIProvider,
    AIPlatformDiscoveryService
)

# ✅ FIX: Create the router properly
router = APIRouter(tags=["admin", "ai-discovery"])

# ✅ REQUEST MODELS
class ToggleProviderRequest(BaseModel):
    enabled: bool

class BulkToggleRequest(BaseModel):
    provider_ids: List[str]
    enabled: bool

# ✅ CORE ENDPOINTS THAT FRONTEND NEEDS

@router.get("/dashboard")
async def get_ai_discovery_dashboard(db: Session = Depends(get_ai_discovery_db)):
    """
    🎯 Main dashboard endpoint - Overview of AI platform discovery system
    """
    try:
        discovery_service = get_discovery_service(db)
        
        # Get active providers count by category
        active_stats = db.execute(text("""
            SELECT category, 
                   COUNT(*) as total,
                   COUNT(CASE WHEN is_active = true THEN 1 END) as active,
                   COUNT(CASE WHEN is_top_3 = true THEN 1 END) as top_3
            FROM active_ai_providers 
            GROUP BY category
        """)).fetchall()
        
        # Get discovered providers waiting for review
        discovered_stats = db.execute(text("""
            SELECT category,
                   COUNT(*) as total,
                   COUNT(CASE WHEN recommendation_priority = 'high' THEN 1 END) as high_priority
            FROM discovered_ai_providers 
            WHERE promotion_status = 'pending'
            GROUP BY category
        """)).fetchall()
        
        # Recent discoveries
        recent_discoveries = db.query(DiscoveredAIProvider).filter(
            DiscoveredAIProvider.discovered_date >= datetime.utcnow() - timedelta(days=7)
        ).order_by(DiscoveredAIProvider.discovered_date.desc()).limit(5).all()
        
        return {
            "success": True,
            "dashboard": {
                "active_providers": {
                    "by_category": [
                        {
                            "category": row.category,
                            "total": row.total,
                            "active": row.active,
                            "top_3": row.top_3
                        }
                        for row in active_stats
                    ],
                    "total": sum(row.total for row in active_stats)
                },
                "discovered_providers": {
                    "by_category": [
                        {
                            "category": row.category,
                            "total": row.total,
                            "high_priority": row.high_priority
                        }
                        for row in discovered_stats
                    ],
                    "total": sum(row.total for row in discovered_stats)
                },
                "recent_discoveries": [
                    {
                        "id": d.id,
                        "provider_name": d.provider_name,
                        "category": d.category,
                        "recommendation_priority": d.recommendation_priority,
                        "discovered_date": d.discovered_date.isoformat() if d.discovered_date else None
                    }
                    for d in recent_discoveries
                ],
                "system_status": "operational",
                "last_discovery_cycle": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard failed: {str(e)}")

@router.get("/active-providers")
async def get_active_providers(
    top_3_only: bool = Query(False, description="Only show top 3 per category"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_ai_discovery_db)
):
    """
    📋 Get list of active AI providers (Table 1)
    """
    try:
        query = db.query(ActiveAIProvider)
        
        if category:
            query = query.filter(ActiveAIProvider.category == category)
        
        if top_3_only:
            query = query.filter(ActiveAIProvider.is_top_3 == True)
        
        providers = query.order_by(
            ActiveAIProvider.category, 
            ActiveAIProvider.category_rank
        ).all()
        
        return {
            "success": True,
            "providers": [
                {
                    "id": p.id,
                    "provider_name": p.provider_name,
                    "env_var_name": p.env_var_name,
                    "category": p.category,
                    "use_type": p.use_type,
                    "cost_per_1k_tokens": float(p.cost_per_1k_tokens) if p.cost_per_1k_tokens else None,
                    "quality_score": float(p.quality_score) if p.quality_score else None,
                    "category_rank": p.category_rank,
                    "is_top_3": p.is_top_3,
                    "is_active": p.is_active,
                    "primary_model": p.primary_model,
                    "discovered_date": p.discovered_date.isoformat() if p.discovered_date else None
                }
                for p in providers
            ],
            "total_count": len(providers),
            "filter": {
                "top_3_only": top_3_only,
                "category": category
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active providers: {str(e)}")

@router.get("/discovered-suggestions")
async def get_discovered_suggestions(
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_ai_discovery_db)
):
    """
    🔍 Get discovered AI providers awaiting review (Table 2)
    """
    try:
        query = db.query(DiscoveredAIProvider).filter(
            DiscoveredAIProvider.promotion_status == 'pending'
        )
        
        if category:
            query = query.filter(DiscoveredAIProvider.category == category)
        
        if priority:
            query = query.filter(DiscoveredAIProvider.recommendation_priority == priority)
        
        suggestions = query.order_by(
            DiscoveredAIProvider.recommendation_priority.desc(),
            DiscoveredAIProvider.discovered_date.desc()
        ).all()
        
        return {
            "success": True,
            "suggestions": [
                {
                    "id": s.id,
                    "provider_name": s.provider_name,
                    "suggested_env_var_name": s.suggested_env_var_name,
                    "category": s.category,
                    "use_type": s.use_type,
                    "estimated_cost_per_1k_tokens": float(s.estimated_cost_per_1k_tokens) if s.estimated_cost_per_1k_tokens else None,
                    "estimated_quality_score": float(s.estimated_quality_score) if s.estimated_quality_score else None,
                    "website_url": s.website_url,
                    "recommendation_priority": s.recommendation_priority,
                    "unique_features": s.unique_features,
                    "research_notes": s.research_notes,
                    "discovered_date": s.discovered_date.isoformat() if s.discovered_date else None
                }
                for s in suggestions
            ],
            "total_count": len(suggestions),
            "filter": {
                "category": category,
                "priority": priority
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@router.get("/category-rankings")
async def get_category_rankings(db: Session = Depends(get_ai_discovery_db)):
    """
    🏆 Get top 3 providers per category with rankings
    """
    try:
        rankings = {}
        categories = ['text_generation', 'image_generation', 'video_generation', 'audio_generation', 'multimodal']
        
        for category in categories:
            top_providers = db.query(ActiveAIProvider).filter(
                ActiveAIProvider.category == category,
                ActiveAIProvider.is_top_3 == True,
                ActiveAIProvider.is_active == True
            ).order_by(ActiveAIProvider.category_rank).all()
            
            rankings[category] = [
                {
                    "rank": p.category_rank,
                    "provider_name": p.provider_name,
                    "quality_score": float(p.quality_score) if p.quality_score else None,
                    "cost_per_1k_tokens": float(p.cost_per_1k_tokens) if p.cost_per_1k_tokens else None,
                    "primary_model": p.primary_model,
                    "is_active": p.is_active
                }
                for p in top_providers
            ]
        
        return {
            "success": True,
            "category_rankings": rankings,
            "total_categories": len(categories),
            "total_top_providers": sum(len(providers) for providers in rankings.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get rankings: {str(e)}")

@router.post("/run-discovery")
async def run_discovery_cycle(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_ai_discovery_db)
):
    """
    🔄 Run full AI platform discovery cycle
    """
    try:
        discovery_service = get_discovery_service(db)
        
        # Run discovery in background
        background_tasks.add_task(discovery_service.full_discovery_cycle)
        
        return {
            "success": True,
            "message": "🔄 AI discovery cycle started",
            "status": "running",
            "estimated_completion": "2-5 minutes",
            "process": [
                "1. Scanning environment variables for new API keys",
                "2. Researching web for new AI platforms",
                "3. Updating provider rankings",
                "4. Checking for auto-promotions",
                "5. Generating updated summary"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery cycle failed: {str(e)}")

@router.post("/promote-suggestion/{suggestion_id}")
async def promote_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_ai_discovery_db)
):
    """
    ⬆️ Promote a suggestion from Table 2 to Table 1
    (Requires API key to be added to environment first)
    """
    try:
        suggestion = db.query(DiscoveredAIProvider).filter(
            DiscoveredAIProvider.id == suggestion_id
        ).first()
        
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        # Check if API key exists in environment
        env_var = suggestion.suggested_env_var_name
        if not env_var or env_var not in os.environ:
            return {
                "success": False,
                "message": f"❌ API key not found. Please add {env_var} to environment variables first.",
                "required_env_var": env_var,
                "instructions": f"Add {env_var}=your_api_key to your environment variables, then try again."
            }
        
        # Promote to active providers
        discovery_service = get_discovery_service(db)
        await discovery_service.promote_provider(suggestion, env_var, os.environ[env_var])
        
        return {
            "success": True,
            "message": f"✅ {suggestion.provider_name} promoted to active providers",
            "promoted_provider": {
                "provider_name": suggestion.provider_name,
                "env_var_name": env_var,
                "category": suggestion.category
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Promotion failed: {str(e)}")

# ✅ TOGGLE FUNCTIONALITY

@router.post("/toggle-provider/{provider_id}")
async def toggle_provider_status(
    provider_id: int,
    request: ToggleProviderRequest,
    db: Session = Depends(get_ai_discovery_db)
):
    """
    🎛️ Enable/Disable individual AI provider
    """
    try:
        provider = db.query(ActiveAIProvider).filter(
            ActiveAIProvider.id == provider_id
        ).first()
    
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
    
        old_status = provider.is_active
        provider.is_active = request.enabled
        provider.updated_at = datetime.utcnow()
        
        db.commit()
        
        status_change = "enabled" if request.enabled else "disabled"
        
        return {
            'success': True,
            'message': f'✅ {provider.provider_name} {status_change} successfully',
            'provider': {
                'id': provider.id,
                'provider_name': provider.provider_name,
                'category': provider.category,
                'is_active': provider.is_active,
                'status_changed': old_status != request.enabled
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Toggle failed: {str(e)}")

@router.get("/provider-status-summary")
async def get_provider_status_summary(db: Session = Depends(get_ai_discovery_db)):
    """
    📊 Get summary of enabled/disabled providers by category
    """
    try:
        status_query = text('''
        SELECT 
            category,
            COUNT(*) as total_providers,
            COUNT(CASE WHEN is_active = true THEN 1 END) as enabled_providers,
            COUNT(CASE WHEN is_active = false THEN 1 END) as disabled_providers,
            COUNT(CASE WHEN is_active = true AND is_top_3 = true THEN 1 END) as enabled_top_3
        FROM active_ai_providers
        GROUP BY category
        ORDER BY category
        ''')
        
        category_stats = db.execute(status_query).fetchall()
        
        return {
            'success': True,
            'by_category': [
                {
                    'category': row.category,
                    'total_providers': row.total_providers or 0,
                    'enabled_providers': row.enabled_providers or 0,
                    'disabled_providers': row.disabled_providers or 0,
                    'enabled_top_3': row.enabled_top_3 or 0
                }
                for row in category_stats
            ],
            'last_updated': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status summary failed: {str(e)}")

# ✅ HEALTH CHECK
@router.get("/health")
async def ai_discovery_health_check():
    """
    ✅ Health check for AI Discovery system
    """
    try:
        return {
            "status": "healthy",
            "service": "AI Platform Discovery System",
            "version": "1.0.0",
            "endpoints": {
                "dashboard": "/api/admin/ai-discovery/dashboard",
                "active_providers": "/api/admin/ai-discovery/active-providers",
                "discovered_suggestions": "/api/admin/ai-discovery/discovered-suggestions",
                "category_rankings": "/api/admin/ai-discovery/category-rankings",
                "run_discovery": "/api/admin/ai-discovery/run-discovery"
            },
            "features": [
                "Two-table architecture",
                "Environment scanning",
                "Web research",
                "Auto-promotion",
                "Provider toggle",
                "Category rankings"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")