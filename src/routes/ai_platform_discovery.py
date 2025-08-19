# src/routes/ai_platform_discovery.py

"""
🔍 AI Platform Discovery & Management Routes

Table 1: active_ai_providers (Top 3 per category with API keys)
Table 2: discovered_ai_providers (Research suggestions)
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from src.core.ai_discovery_database import get_ai_discovery_db
from src.services.ai_platform_discovery import (
    get_discovery_service, 
    ActiveAIProvider, 
    DiscoveredAIProvider
)

router = APIRouter(prefix="/admin/ai-discovery", tags=["admin", "ai-discovery"])

# ✅ Response Models
class ActiveProviderResponse(BaseModel):
    id: int
    provider_name: str
    env_var_name: str
    category: str
    use_type: str
    cost_per_1k_tokens: Optional[float]
    quality_score: float
    category_rank: int
    is_top_3: bool
    is_active: bool
    
class DiscoveredProviderResponse(BaseModel):
    id: int
    provider_name: str
    suggested_env_var_name: Optional[str]
    category: str
    use_type: str
    estimated_cost_per_1k_tokens: Optional[float]
    estimated_quality_score: float
    recommendation_priority: str
    unique_features: Optional[str]
    website_url: Optional[str]
    
class CategorySummary(BaseModel):
    category: str
    active_providers: List[ActiveProviderResponse]
    discovered_suggestions: List[DiscoveredProviderResponse]
    total_active: int
    total_suggestions: int

# ✅ Main Dashboard Endpoint
@router.get("/dashboard")
async def get_ai_discovery_dashboard(db: Session = Depends(get_ai_discovery_db)):
    """
    📊 Main AI Platform Discovery Dashboard
    Shows Table 1 (Active) and Table 2 (Discovered) organized by categories
    """
    try:
        categories = ['text_generation', 'image_generation', 'video_generation', 'audio_generation', 'multimodal']
        dashboard_data = {}
        
        for category in categories:
            # Get active providers (Table 1) - Top 3 only
            active_providers = db.query(ActiveAIProvider).filter(
                ActiveAIProvider.category == category,
                ActiveAIProvider.is_active == True
            ).order_by(ActiveAIProvider.category_rank).limit(3).all()
            
            # Get discovered suggestions (Table 2) - Top 5 recommendations
            discovered_providers = db.query(DiscoveredAIProvider).filter(
                DiscoveredAIProvider.category == category,
                DiscoveredAIProvider.promotion_status == 'pending'
            ).order_by(
                DiscoveredAIProvider.recommendation_priority.desc(),
                DiscoveredAIProvider.estimated_quality_score.desc()
            ).limit(5).all()
            
            dashboard_data[category] = {
                'active_providers': [
                    {
                        'id': p.id,
                        'provider_name': p.provider_name,
                        'env_var_name': p.env_var_name,
                        'category_rank': p.category_rank,
                        'cost_per_1k_tokens': float(p.cost_per_1k_tokens) if p.cost_per_1k_tokens else None,
                        'quality_score': float(p.quality_score),
                        'is_top_3': p.is_top_3,
                        'primary_model': p.primary_model
                    } for p in active_providers
                ],
                'discovered_suggestions': [
                    {
                        'id': p.id,
                        'provider_name': p.provider_name,
                        'suggested_env_var_name': p.suggested_env_var_name,
                        'estimated_cost_per_1k_tokens': float(p.estimated_cost_per_1k_tokens) if p.estimated_cost_per_1k_tokens else None,
                        'estimated_quality_score': float(p.estimated_quality_score),
                        'recommendation_priority': p.recommendation_priority,
                        'unique_features': p.unique_features,
                        'website_url': p.website_url
                    } for p in discovered_providers
                ],
                'summary': {
                    'active_count': len(active_providers),
                    'suggestions_count': len(discovered_providers)
                }
            }
        
        # Overall summary
        total_active = db.query(ActiveAIProvider).filter(ActiveAIProvider.is_active == True).count()
        total_discovered = db.query(DiscoveredAIProvider).filter(
            DiscoveredAIProvider.promotion_status == 'pending'
        ).count()
        
        return {
            'success': True,
            'categories': dashboard_data,
            'overall_summary': {
                'total_active_providers': total_active,
                'total_discovery_suggestions': total_discovered,
                'last_updated': datetime.utcnow().isoformat(),
                'system_status': 'operational'
            },
            'quick_actions': [
                'Run Full Discovery Scan',
                'Review Pending Suggestions', 
                'Update Provider Rankings',
                'Check for New API Keys'
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard load failed: {str(e)}")

# ✅ Full Discovery Cycle
@router.post("/run-discovery")
async def run_full_discovery_cycle(
    background_tasks: BackgroundTasks,
    force_web_research: bool = False,
    db: Session = Depends(get_ai_discovery_db)
):
    """
    🔄 Run complete AI platform discovery cycle
    1. Scan environment variables → Table 1
    2. Research web for new platforms → Table 2  
    3. Update rankings (top 3 per category)
    4. Check for promotions (Table 2 → Table 1)
    """
    try:
        discovery_service = get_discovery_service(db)
        
        # Run in background to avoid timeout
        background_tasks.add_task(
            run_discovery_background,
            discovery_service,
            force_web_research
        )
        
        return {
            'success': True,
            'message': '🔍 Full discovery cycle started in background',
            'estimated_duration': '2-5 minutes',
            'stages': [
                '1. Environment variable scan',
                '2. Web research for new platforms', 
                '3. Ranking update (top 3 per category)',
                '4. Promotion check (move to active if API keys found)'
            ],
            'check_status_url': '/admin/ai-discovery/status'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery cycle failed: {str(e)}")

async def run_discovery_background(discovery_service, force_web_research: bool):
    """Background task for discovery cycle"""
    try:
        results = await discovery_service.full_discovery_cycle()
        print(f"✅ Discovery cycle complete: {results}")
    except Exception as e:
        print(f"❌ Discovery cycle failed: {e}")

# ✅ Table 1: Active Providers (Environment-based)
@router.get("/active-providers")
async def get_active_providers(
    category: Optional[str] = None,
    top_3_only: bool = True,
    db: Session = Depends(get_ai_discovery_db)
):
    """
    📋 Get active providers (Table 1) - Only providers with API keys
    Optionally filter by category and show only top 3 performers
    """
    try:
        query = db.query(ActiveAIProvider).filter(ActiveAIProvider.is_active == True)
        
        if category:
            query = query.filter(ActiveAIProvider.category == category)
        
        if top_3_only:
            query = query.filter(ActiveAIProvider.is_top_3 == True)
        
        providers = query.order_by(
            ActiveAIProvider.category,
            ActiveAIProvider.category_rank
        ).all()
        
        # Group by category
        by_category = {}
        for provider in providers:
            cat = provider.category
            if cat not in by_category:
                by_category[cat] = []
            
            by_category[cat].append({
                'id': provider.id,
                'provider_name': provider.provider_name,
                'env_var_name': provider.env_var_name,
                'category_rank': provider.category_rank,
                'cost_per_1k_tokens': float(provider.cost_per_1k_tokens) if provider.cost_per_1k_tokens else None,
                'quality_score': float(provider.quality_score),
                'speed_score': float(provider.speed_score),
                'primary_model': provider.primary_model,
                'api_endpoint': provider.api_endpoint,
                'last_performance_check': provider.last_performance_check.isoformat() if provider.last_performance_check else None
            })
        
        return {
            'success': True,
            'active_providers_by_category': by_category,
            'total_providers': len(providers),
            'filter_applied': {
                'category': category,
                'top_3_only': top_3_only
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active providers: {str(e)}")

# ✅ Table 2: Discovered Providers (Research suggestions)
@router.get("/discovered-suggestions")
async def get_discovered_suggestions(
    category: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_ai_discovery_db)
):
    """
    🔍 Get discovered AI platform suggestions (Table 2)
    Research-based recommendations for new platforms to consider
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
            DiscoveredAIProvider.estimated_quality_score.desc()
        ).limit(limit).all()
        
        # Group by category and priority
        by_category = {}
        priority_stats = {'high': 0, 'medium': 0, 'low': 0}
        
        for suggestion in suggestions:
            cat = suggestion.category
            if cat not in by_category:
                by_category[cat] = []
            
            priority_stats[suggestion.recommendation_priority] += 1
            
            by_category[cat].append({
                'id': suggestion.id,
                'provider_name': suggestion.provider_name,
                'suggested_env_var_name': suggestion.suggested_env_var_name,
                'use_type': suggestion.use_type,
                'estimated_cost_per_1k_tokens': float(suggestion.estimated_cost_per_1k_tokens) if suggestion.estimated_cost_per_1k_tokens else None,
                'estimated_quality_score': float(suggestion.estimated_quality_score),
                'recommendation_priority': suggestion.recommendation_priority,
                'unique_features': suggestion.unique_features,
                'website_url': suggestion.website_url,
                'pricing_url': suggestion.pricing_url,
                'discovery_source': suggestion.discovery_source,
                'discovered_date': suggestion.discovered_date.isoformat(),
                'research_notes': suggestion.research_notes
            })
        
        return {
            'success': True,
            'discovered_suggestions_by_category': by_category,
            'total_suggestions': len(suggestions),
            'priority_breakdown': priority_stats,
            'filter_applied': {
                'category': category,
                'priority': priority,
                'limit': limit
            },
            'next_steps': [
                'Review high priority suggestions',
                'Add API keys to environment for desired platforms',
                'Run discovery cycle to promote to active'
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

# ✅ Promote Suggestion to Active
@router.post("/promote-suggestion/{suggestion_id}")
async def promote_suggestion_to_active(
    suggestion_id: int,
    api_key: str,
    db: Session = Depends(get_ai_discovery_db)
):
    """
    ⬆️ Manually promote a suggestion from Table 2 to Table 1
    Used when admin adds API key and wants immediate promotion
    """
    try:
        # Get the suggestion
        suggestion = db.query(DiscoveredAIProvider).filter(
            DiscoveredAIProvider.id == suggestion_id
        ).first()
        
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        if suggestion.promotion_status != 'pending':
            raise HTTPException(status_code=400, detail=f"Suggestion already {suggestion.promotion_status}")
        
        # Create active provider
        active_provider = ActiveAIProvider(
            provider_name=suggestion.provider_name,
            env_var_name=suggestion.suggested_env_var_name,
            category=suggestion.category,
            use_type=suggestion.use_type,
            cost_per_1k_tokens=suggestion.estimated_cost_per_1k_tokens,
            cost_per_image=suggestion.estimated_cost_per_image,
            cost_per_minute_video=suggestion.estimated_cost_per_minute_video,
            quality_score=suggestion.estimated_quality_score,
            speed_score=suggestion.estimated_speed_score,
            api_endpoint=suggestion.api_endpoint,
            capabilities=suggestion.unique_features,
            promoted_date=datetime.utcnow(),
            is_active=True
        )
        
        # Add to Table 1
        db.add(active_provider)
        
        # Update suggestion status in Table 2
        suggestion.promotion_status = 'promoted'
        suggestion.admin_notes = f"Manually promoted with API key on {datetime.utcnow().isoformat()}"
        suggestion.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Trigger ranking update for this category
        discovery_service = get_discovery_service(db)
        await discovery_service.update_rankings()
        
        return {
            'success': True,
            'message': f'✅ {suggestion.provider_name} promoted to active providers',
            'promoted_provider': {
                'id': active_provider.id,
                'provider_name': active_provider.provider_name,
                'env_var_name': active_provider.env_var_name,
                'category': active_provider.category
            },
            'next_steps': [
                f'Add {suggestion.suggested_env_var_name}={api_key[:10]}... to environment variables',
                'Provider will be included in top 3 ranking for its category',
                'Performance monitoring will begin automatically'
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Promotion failed: {str(e)}")

# ✅ Update Rankings
@router.post("/update-rankings")
async def update_provider_rankings(db: Session = Depends(get_ai_discovery_db)):
    """
    🏆 Update provider rankings to show top 3 per category
    Recalculates cost-effectiveness and performance scores
    """
    try:
        discovery_service = get_discovery_service(db)
        ranking_results = await discovery_service.update_rankings()
        
        return {
            'success': True,
            'message': '🏆 Provider rankings updated successfully',
            'ranking_results': ranking_results,
            'categories_updated': list(ranking_results.keys()),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ranking update failed: {str(e)}")

# ✅ Review and Approve Suggestions
@router.post("/review-suggestion/{suggestion_id}")
async def review_suggestion(
    suggestion_id: int,
    action: str,  # 'approve', 'reject', 'needs_review'
    admin_notes: Optional[str] = None,
    db: Session = Depends(get_ai_discovery_db)
):
    """
    👥 Admin review of discovered suggestions
    Mark suggestions as approved, rejected, or needing more review
    """
    try:
        suggestion = db.query(DiscoveredAIProvider).filter(
            DiscoveredAIProvider.id == suggestion_id
        ).first()
        
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        valid_actions = ['approve', 'reject', 'needs_review']
        if action not in valid_actions:
            raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of: {valid_actions}")
        
        # Update suggestion
        suggestion.promotion_status = action
        suggestion.is_reviewed = True
        suggestion.admin_notes = admin_notes or f"Admin action: {action}"
        suggestion.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            'success': True,
            'message': f'✅ Suggestion {action}ed successfully',
            'suggestion': {
                'id': suggestion.id,
                'provider_name': suggestion.provider_name,
                'status': suggestion.promotion_status,
                'admin_notes': suggestion.admin_notes
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")

# ✅ System Status
@router.get("/status")
async def get_discovery_system_status(db: Session = Depends(get_ai_discovery_db)):
    """
    📊 Get overall system status and health metrics
    """
    try:
        discovery_service = get_discovery_service(db)
        summary = await discovery_service.generate_summary()
        
        # Check for recent discoveries
        recent_discoveries = db.query(DiscoveredAIProvider).filter(
            DiscoveredAIProvider.discovered_date >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Check for recent promotions
        recent_promotions = db.query(ActiveAIProvider).filter(
            ActiveAIProvider.promoted_date >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return {
            'success': True,
            'system_status': 'operational',
            'summary': summary,
            'recent_activity': {
                'discoveries_this_week': recent_discoveries,
                'promotions_this_week': recent_promotions,
                'last_discovery_scan': datetime.utcnow().isoformat()
            },
            'system_health': {
                'table_1_active': summary['total_active_providers'] > 0,
                'table_2_discoveries': summary['total_discovered_providers'] > 0,
                'auto_promotion_working': True,
                'web_research_enabled': True
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

# ✅ Delete/Remove Providers
@router.delete("/active-provider/{provider_id}")
async def remove_active_provider(provider_id: int, db: Session = Depends(get_ai_discovery_db)):
    """🗑️ Remove provider from active list (Table 1)"""
    try:
        provider = db.query(ActiveAIProvider).filter(ActiveAIProvider.id == provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        provider_name = provider.provider_name
        db.delete(provider)
        db.commit()
        
        return {
            'success': True,
            'message': f'🗑️ {provider_name} removed from active providers',
            'note': 'Provider can be re-discovered in next scan if API key still exists'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Removal failed: {str(e)}")

@router.delete("/suggestion/{suggestion_id}")
async def remove_suggestion(suggestion_id: int, db: Session = Depends(get_ai_discovery_db)):
    """🗑️ Remove suggestion from discoveries (Table 2)"""
    try:
        suggestion = db.query(DiscoveredAIProvider).filter(DiscoveredAIProvider.id == suggestion_id).first()
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        provider_name = suggestion.provider_name
        db.delete(suggestion)
        db.commit()
        
        return {
            'success': True,
            'message': f'🗑️ {provider_name} removed from suggestions',
            'note': 'Provider may be re-discovered in future web research'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Removal failed: {str(e)}")