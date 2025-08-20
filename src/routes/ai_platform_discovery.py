# Add these endpoints to src/routes/ai_platform_discovery.py

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from campaigns.routes import router
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from src.core.ai_discovery_database import get_ai_discovery_db
from src.core.database import get_db
from src.services.ai_platform_discovery import (
    get_discovery_service, 
    ActiveAIProvider, 
    DiscoveredAIProvider
)

# 🆕 NEW REQUEST MODELS FOR TOGGLE FUNCTIONALITY
class ToggleProviderRequest(BaseModel):
    enabled: bool

class BulkToggleRequest(BaseModel):
    provider_ids: List[str]
    enabled: bool

# 🎛️ Toggle Individual Provider Status
@router.post("/toggle-provider/{provider_id}")
async def toggle_provider_status(
    provider_id: int,
    request: ToggleProviderRequest,
    db: Session = Depends(get_ai_discovery_db)
):
    """
    🎛️ Enable/Disable individual AI provider
    Updates is_active status and logs the change
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
    
        # Add to admin notes/log if available
        status_change = "enabled" if request.enabled else "disabled"
        action_log = f"Provider {status_change} on {datetime.utcnow().isoformat()}"
    
        # Update admin notes if the field exists
        if hasattr(provider, 'admin_notes'):
            existing_notes = provider.admin_notes or ""
            provider.admin_notes = f"{existing_notes}\n{action_log}".strip()
    
        db.commit()
    
        # Recalculate category rankings if this affects top 3
        if provider.is_top_3:
            discovery_service = get_discovery_service(db)
            await discovery_service.update_rankings()
    
        return {
            'success': True,
            'message': f'✅ {provider.provider_name} {status_change} successfully',
            'provider': {
                'id': provider.id,
                'provider_name': provider.provider_name,
                'category': provider.category,
                'is_active': provider.is_active,
                'was_active': old_status,
                'status_changed': old_status != request.enabled
            },
            'impact': {
                'affects_top_3': provider.is_top_3,
                'category_rankings_updated': provider.is_top_3,
                'usage_will_stop': not request.enabled and old_status,
                'usage_will_resume': request.enabled and not old_status
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Toggle failed: {str(e)}")

# 🔄 Bulk Toggle Multiple Providers
@router.post("/bulk-toggle-providers")
async def bulk_toggle_providers(
    request: BulkToggleRequest,
    db: Session = Depends(get_ai_discovery_db)
):
    """
    🔄 Bulk enable/disable multiple AI providers
    Efficient for managing multiple providers at once
    """
    try:
        updated_count = 0
        failed_count = 0
        results = []
        
        for provider_id_str in request.provider_ids:
            try:
                provider_id = int(provider_id_str)
                provider = db.query(ActiveAIProvider).filter(
                    ActiveAIProvider.id == provider_id
                ).first()
                
                if not provider:
                    results.append({
                        'provider_id': provider_id_str,
                        'success': False,
                        'message': 'Provider not found'
                    })
                    failed_count += 1
                    continue
                
                old_status = provider.is_active
                provider.is_active = request.enabled
                provider.updated_at = datetime.utcnow()
                
                # Add bulk action log
                status_change = "enabled" if request.enabled else "disabled"
                action_log = f"Bulk {status_change} on {datetime.utcnow().isoformat()}"
                
                if hasattr(provider, 'admin_notes'):
                    existing_notes = provider.admin_notes or ""
                    provider.admin_notes = f"{existing_notes}\n{action_log}".strip()
                
                results.append({
                    'provider_id': provider_id_str,
                    'success': True,
                    'message': f'{provider.provider_name} {status_change}',
                    'provider_name': provider.provider_name,
                    'category': provider.category,
                    'status_changed': old_status != request.enabled
                })
                updated_count += 1
                
            except Exception as e:
                results.append({
                    'provider_id': provider_id_str,
                    'success': False,
                    'message': f'Error: {str(e)}'
                })
                failed_count += 1
        
        db.commit()
        
        # Update rankings if any top 3 providers were affected
        top_3_affected = any(
            result['success'] and 
            db.query(ActiveAIProvider).filter(
                ActiveAIProvider.id == int(result['provider_id']),
                ActiveAIProvider.is_top_3 == True
            ).first()
            for result in results
        )
        
        if top_3_affected:
            try:
                discovery_service = get_discovery_service(db)
                await discovery_service.update_rankings()
            except Exception as e:
                print(f"Warning: Failed to update rankings after bulk toggle: {e}")
        
        action = "enabled" if request.enabled else "disabled"
        
        return {
            'success': True,
            'message': f'✅ Bulk toggle completed: {updated_count} providers {action}',
            'updated_count': updated_count,
            'failed_count': failed_count,
            'results': results,
            'summary': {
                'total_requested': len(request.provider_ids),
                'successful_updates': updated_count,
                'failed_updates': failed_count,
                'action_performed': action,
                'rankings_updated': top_3_affected
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk toggle failed: {str(e)}")

# 📊 Get Provider Status Summary  
@router.get("/provider-status-summary")
async def get_provider_status_summary(db: Session = Depends(get_ai_discovery_db)):
    """
    📊 Get summary of enabled/disabled providers by category
    Useful for dashboard overview and bulk operations
    """
    try:
        status_query = text('''
        SELECT 
            category,
            COUNT(*) as total_providers,
            COUNT(CASE WHEN is_active = true THEN 1 END) as enabled_providers,
            COUNT(CASE WHEN is_active = false THEN 1 END) as disabled_providers,
            COUNT(CASE WHEN is_active = true AND is_top_3 = true THEN 1 END) as enabled_top_3,
            AVG(CASE WHEN is_active = true THEN quality_score END) as avg_quality_enabled,
            SUM(CASE WHEN is_active = true THEN monthly_usage * cost_per_1k_tokens / 1000 END) as monthly_cost_enabled
        FROM active_ai_providers
        GROUP BY category
        ORDER BY category
        ''')
        
        category_stats = db.execute(status_query).fetchall()
        
        # Overall totals
        overall_query = text('''
        SELECT 
            COUNT(*) as total_providers,
            COUNT(CASE WHEN is_active = true THEN 1 END) as enabled_providers,
            COUNT(CASE WHEN is_active = false THEN 1 END) as disabled_providers
        FROM active_ai_providers
        ''')
        
        overall_stats = db.execute(overall_query).fetchone()
        
        return {
            'overall': {
                'total_providers': overall_stats.total_providers or 0,
                'enabled_providers': overall_stats.enabled_providers or 0,
                'disabled_providers': overall_stats.disabled_providers or 0,
                'enabled_percentage': round(
                    (overall_stats.enabled_providers or 0) / max(overall_stats.total_providers or 1, 1) * 100, 1
                )
            },
            'by_category': [
                {
                    'category': row.category,
                    'total_providers': row.total_providers or 0,
                    'enabled_providers': row.enabled_providers or 0,
                    'disabled_providers': row.disabled_providers or 0,
                    'enabled_top_3': row.enabled_top_3 or 0,
                    'avg_quality_enabled': round(float(row.avg_quality_enabled or 0), 1),
                    'monthly_cost_enabled': round(float(row.monthly_cost_enabled or 0), 2),
                    'enabled_percentage': round(
                        (row.enabled_providers or 0) / max(row.total_providers or 1, 1) * 100, 1
                    )
                }
                for row in category_stats
            ],
            'recommendations': {
                'categories_with_no_active': [
                    row.category for row in category_stats 
                    if (row.enabled_providers or 0) == 0
                ],
                'categories_fully_enabled': [
                    row.category for row in category_stats 
                    if (row.enabled_providers or 0) == (row.total_providers or 0) and (row.total_providers or 0) > 0
                ],
                'suggested_actions': []
            },
            'last_updated': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status summary failed: {str(e)}")

# 🔄 Quick Enable/Disable All in Category
@router.post("/toggle-category/{category}")
async def toggle_category_providers(
    category: str,
    enabled: bool,
    db: Session = Depends(get_ai_discovery_db)
):
    """
    🔄 Enable/disable all providers in a specific category
    Useful for quickly managing entire categories
    """
    try:
        valid_categories = ['text_generation', 'image_generation', 'video_generation', 'audio_generation', 'multimodal']
        if category not in valid_categories:
            raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {valid_categories}")
        
        # Get all providers in category
        providers = db.query(ActiveAIProvider).filter(
            ActiveAIProvider.category == category
        ).all()
        
        if not providers:
            raise HTTPException(status_code=404, detail=f"No providers found in category: {category}")
        
        updated_count = 0
        action = "enabled" if enabled else "disabled"
        
        for provider in providers:
            if provider.is_active != enabled:  # Only update if status is changing
                provider.is_active = enabled
                provider.updated_at = datetime.utcnow()
                
                # Add category action log
                action_log = f"Category bulk {action} on {datetime.utcnow().isoformat()}"
                if hasattr(provider, 'admin_notes'):
                    existing_notes = provider.admin_notes or ""
                    provider.admin_notes = f"{existing_notes}\n{action_log}".strip()
                
                updated_count += 1
        
        db.commit()
        
        # Update rankings for this category
        try:
            discovery_service = get_discovery_service(db)
            await discovery_service.update_rankings()
        except Exception as e:
            print(f"Warning: Failed to update rankings after category toggle: {e}")
        
        return {
            'success': True,
            'message': f'✅ All {category} providers {action} ({updated_count} providers)',
            'category': category,
            'total_providers': len(providers),
            'updated_count': updated_count,
            'action_performed': action,
            'providers_affected': [
                {
                    'id': p.id,
                    'provider_name': p.provider_name,
                    'is_active': p.is_active
                }
                for p in providers
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Category toggle failed: {str(e)}")

# 🎛️ Quick Toggle All Providers (System-wide)
@router.post("/toggle-all-providers")
async def toggle_all_providers(
    enabled: bool,
    confirm: bool = False,
    db: Session = Depends(get_ai_discovery_db)
):
    """
    🎛️ Enable/disable ALL AI providers in the system
    Requires confirmation parameter for safety
    """
    try:
        if not confirm:
            raise HTTPException(
                status_code=400, 
                detail="This action requires confirmation. Add ?confirm=true to proceed."
            )
        
        providers = db.query(ActiveAIProvider).all()
        
        if not providers:
            return {
                'success': True,
                'message': 'No providers found to toggle',
                'updated_count': 0
            }
        
        updated_count = 0
        action = "enabled" if enabled else "disabled"
        
        for provider in providers:
            if provider.is_active != enabled:  # Only update if status is changing
                provider.is_active = enabled
                provider.updated_at = datetime.utcnow()
                
                # Add system-wide action log
                action_log = f"System-wide bulk {action} on {datetime.utcnow().isoformat()}"
                if hasattr(provider, 'admin_notes'):
                    existing_notes = provider.admin_notes or ""
                    provider.admin_notes = f"{existing_notes}\n{action_log}".strip()
                
                updated_count += 1
        
        db.commit()
        
        # Update all rankings
        try:
            discovery_service = get_discovery_service(db)
            await discovery_service.update_rankings()
        except Exception as e:
            print(f"Warning: Failed to update rankings after system-wide toggle: {e}")
        
        return {
            'success': True,
            'message': f'🎛️ System-wide toggle completed: {updated_count} providers {action}',
            'total_providers': len(providers),
            'updated_count': updated_count,
            'action_performed': action,
            'warning': f'All AI providers are now {action}. This affects all AI routing decisions.',
            'next_steps': [
                'Monitor system performance after this change',
                'Consider enabling critical providers if all were disabled',
                'Check individual provider performance in next 24 hours'
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"System-wide toggle failed: {str(e)}")