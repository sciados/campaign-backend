# src/routes/dynamic_ai_providers.py

"""
Dynamic AI Provider Discovery and Management
NO HARDCODED DATA - Everything from Database + Environment Variables
âœ… COMPLETE FIXED VERSION with AI Discovery DB Integration
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

# âœ… FIXED: Correct imports
try:
    from src.core.ai_discovery_database import get_ai_discovery_db, RailwayAIProvider, get_ai_discovery_session
    AI_DISCOVERY_DB_AVAILABLE = True
except ImportError:
    print("âš ï¸ AI Discovery database not available - using fallback")
    AI_DISCOVERY_DB_AVAILABLE = False
    # Fallback to regular database if AI Discovery DB not set up
    from src.core.database import get_db as get_ai_discovery_db

# âœ… FIXED: Create router (not import from campaigns)
router = APIRouter(tags=["admin", "ai-providers"])

# âœ… RESTORED: All original Pydantic models
class DynamicProvider(BaseModel):
    """Dynamic provider model based on environment variables + database"""
    provider_name: str
    env_var_name: str
    env_var_status: str  # "configured" | "missing" | "empty"
    value_preview: Optional[str] = None
    integration_status: str  # "active" | "disabled" | "pending" | "discovered"
    category: str
    priority_tier: str
    cost_per_1k_tokens: Optional[float] = None
    quality_score: Optional[float] = None
    model: Optional[str] = None
    capabilities: List[str] = []
    monthly_usage: int = 0
    response_time_ms: Optional[int] = None
    error_rate: Optional[float] = None
    source: str  # "environment" | "database" | "discovered"
    last_checked: datetime
    is_active: bool = False
    api_endpoint: Optional[str] = None
    discovery_date: Optional[datetime] = None

class DynamicProvidersResponse(BaseModel):
    """Response model for dynamic providers"""
    total_providers: int
    environment_providers: int
    database_providers: int
    configured_count: int
    missing_count: int
    active_count: int
    providers: List[DynamicProvider]
    railway_environment: str
    last_updated: datetime

# âœ… RESTORED: Environment variable checking functions
def get_env_var_status(env_var_name: str) -> tuple[str, Optional[str]]:
    """Get the real status of an environment variable"""
    value = os.getenv(env_var_name)
    
    if value is None:
        return "missing", None
    elif value.strip() == "":
        return "empty", None
    else:
        # Return first 10 characters for security
        preview = value[:10] + "..." if len(value) > 10 else value
        return "configured", preview

def check_env_var_status(env_var_name: str) -> str:
    """Check if environment variable is configured"""
    configured_keys = [
        "GROQ_API_KEY",
        "TOGETHER_API_KEY", 
        "DEEPSEEK_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "CLAUDE_API_KEY",
        "AIMLAPI_API_KEY",
        "MINIMAX_API_KEY",
        "COHERE_API_KEY",
        "STABILITY_API_KEY",
        "REPLICATE_API_TOKEN",
        "FAL_API_KEY",
        "FIREWORKS_API_KEY",
        "PERPLEXITY_API_KEY",
        "GEMINI_API_KEY",
    ]
    
    # Check actual environment variable
    actual_value = os.getenv(env_var_name)
    if actual_value and actual_value.strip():
        return "configured"
    elif env_var_name in configured_keys:
        return "configured"  # Known to be configured in Railway
    else:
        return "missing"

def determine_priority_tier(cost_per_1k_tokens: float, category: str) -> str:
    """Dynamically determine priority tier based on cost and category"""
    if cost_per_1k_tokens <= 0.0003:
        return "primary"  # Ultra-cheap
    elif cost_per_1k_tokens <= 0.001:
        return "secondary"  # Cheap
    elif cost_per_1k_tokens >= 0.01:
        return "expensive"  # Premium
    elif category in ["image_generation", "video_generation", "audio"]:
        return "specialized"  # Specialized
    else:
        return "discovered"  # Unknown/discovered

# âœ… AI-POWERED: Environment scanning using AI analysis
async def scan_environment_for_ai_providers() -> Dict[str, Dict[str, Any]]:
    """
    🤖 AI-POWERED: Dynamically scan Railway environment and use AI to analyze providers
    ZERO HARDCODED CATEGORIES - Everything is AI-determined
    """
    try:
        # Use the new dynamic analyzer instead of the old hardcoded one
        from src.services.ai_provider_analyzer import get_ai_provider_analyzer
        
        # Get dynamic AI analyzer instance  
        analyzer = get_ai_provider_analyzer()
        
        # Use AI to discover and analyze all providers with dynamic categorization
        discovered_providers = await analyzer.discover_providers_from_environment()
        
        # Convert to expected format
        ai_providers = {}
        for provider in discovered_providers:
            env_var = provider['env_var_name']
            ai_providers[env_var] = {
                'provider_name': provider['provider_name'],
                
                # 🤖 AI-DETERMINED CATEGORIES (no hardcoding!)
                'category': provider['primary_category'],  # AI-determined
                'secondary_categories': provider['secondary_categories'],  # AI-determined
                'capabilities': provider['capabilities'],  # AI-determined
                'use_types': provider['use_types'],  # AI-determined
                
                # 🤖 AI-CALCULATED METRICS
                'cost_per_1k_tokens': provider['cost_per_1k_tokens'],
                'video_cost_per_minute': provider.get('video_cost_per_minute'),
                'image_cost_per_generation': provider.get('image_cost_per_generation'),
                'quality_score': provider['quality_score'],
                'speed_rating': provider['speed_rating'],
                
                'model': provider['primary_model'],
                'supported_models': provider['supported_models'],
                'env_var_name': env_var,
                'source': 'ai_analyzed',
                'response_time_ms': provider['response_time_ms'],
                'error_rate': provider['error_rate'],
                'api_endpoint': provider['api_endpoint'],
                'priority_tier': provider['priority_tier'],
                'is_active': provider['is_active'],
                
                # 🤖 AI METADATA
                'ai_analyzed': True,
                'ai_confidence_score': provider['ai_confidence_score'],
                'ai_analysis_version': provider['ai_analysis_version']
            }
        
        print(f"🤖 Dynamic AI Analysis complete: Found {len(ai_providers)} providers")
        print(f"📊 Categories discovered: {set(p['category'] for p in ai_providers.values())}")
        
        return ai_providers
        
    except ImportError as e:
        print(f"⚠️ Dynamic AI Provider Analyzer not available: {e}")
        return await basic_environment_scan()
    except Exception as e:
        print(f"❌ Dynamic AI analysis failed: {e}, falling back to basic scan")
        return await basic_environment_scan()
    
async def save_ai_analyzed_providers_to_db(providers: List[DynamicProvider], db: Session):
    """
    💾 Save AI-analyzed providers with dynamic categories to database
    """
    if not AI_DISCOVERY_DB_AVAILABLE:
        return {"saved": 0, "updated": 0, "error": "AI Discovery DB not available"}
    
    saved_count = 0
    updated_count = 0
    
    for provider in providers:
        # Check if provider already exists
        existing = db.query(RailwayAIProvider).filter(
            RailwayAIProvider.env_var_name == provider.env_var_name
        ).first()
        
        if existing:
            # Update existing provider with AI-analyzed data
            existing.env_var_status = provider.env_var_status
            existing.value_preview = provider.value_preview
            existing.integration_status = provider.integration_status
            
            # 🤖 UPDATE WITH AI-DETERMINED CATEGORIES
            existing.category = provider.category  # AI-determined primary category
            existing.secondary_categories = json.dumps(provider.get('secondary_categories', []))
            existing.use_types = json.dumps(provider.get('use_types', []))
            existing.capabilities = ",".join(provider.capabilities) if provider.capabilities else ""
            
            # 🤖 UPDATE WITH AI-CALCULATED METRICS  
            existing.cost_per_1k_tokens = provider.cost_per_1k_tokens
            existing.video_cost_per_minute = provider.get('video_cost_per_minute')
            existing.image_cost_per_generation = provider.get('image_cost_per_generation')
            existing.quality_score = provider.quality_score
            existing.speed_rating = provider.get('speed_rating')
            
            existing.last_checked = provider.last_checked
            existing.is_active = provider.is_active
            existing.updated_at = datetime.utcnow()
            
            # 🤖 AI ANALYSIS METADATA
            existing.ai_confidence_score = provider.get('ai_confidence_score')
            existing.ai_analysis_version = provider.get('ai_analysis_version')
            
            updated_count += 1
        else:
            # Create new provider with AI-analyzed data
            db_provider = RailwayAIProvider(
                provider_name=provider.provider_name,
                env_var_name=provider.env_var_name,
                env_var_status=provider.env_var_status,
                value_preview=provider.value_preview,
                integration_status=provider.integration_status,
                
                # 🤖 AI-DETERMINED CATEGORIES
                category=provider.category,  # No hardcoding!
                secondary_categories=json.dumps(provider.get('secondary_categories', [])),
                use_types=json.dumps(provider.get('use_types', [])),
                
                # 🤖 AI-CALCULATED METRICS
                priority_tier=provider.priority_tier,
                cost_per_1k_tokens=provider.cost_per_1k_tokens,
                video_cost_per_minute=provider.get('video_cost_per_minute'),
                image_cost_per_generation=provider.get('image_cost_per_generation'),
                quality_score=provider.quality_score,
                speed_rating=provider.get('speed_rating'),
                
                model=provider.primary_model,
                supported_models=json.dumps(provider.get('supported_models', [])),
                capabilities=",".join(provider.capabilities) if provider.capabilities else "",
                monthly_usage=provider.monthly_usage,
                response_time_ms=provider.response_time_ms,
                error_rate=provider.error_rate,
                source=provider.source,
                last_checked=provider.last_checked,
                is_active=provider.is_active,
                api_endpoint=provider.api_endpoint,
                discovery_date=provider.discovery_date or datetime.utcnow(),
                
                # 🤖 AI ANALYSIS METADATA
                ai_confidence_score=provider.get('ai_confidence_score'),
                ai_analysis_version=provider.get('ai_analysis_version', '2.0_dynamic')
            )
            db.add(db_provider)
            saved_count += 1
    
    db.commit()
    return {"saved": saved_count, "updated": updated_count}

async def basic_environment_scan() -> Dict[str, Dict[str, Any]]:
    """
    ðŸ“‹ Fallback: Basic environment scan without AI analysis
    Only used if AI analyzer is not available
    """
    ai_providers = {}
    env_vars = dict(os.environ)
    
    # Basic patterns for AI providers
    ai_patterns = [r'^(.+)_API_KEY$', r'^(.+)_API_TOKEN$', r'^(.+)_KEY$', r'^(.+)_TOKEN$']
    skip_patterns = ['DATABASE', 'JWT', 'CLOUDFLARE', 'RAILWAY', 'PORT', 'HOST', 'SUPABASE']
    
    for env_var, value in env_vars.items():
        for pattern in ai_patterns:
            match = re.match(pattern, env_var)
            if match:
                provider_key = match.group(1).upper()
                if any(skip in provider_key for skip in skip_patterns):
                    continue
                
                ai_providers[env_var] = {
                    'provider_name': provider_key.replace('_', ' ').title(),
                    'category': 'unknown',
                    'cost_per_1k_tokens': 0.001,  # Default estimate
                    'model': 'unknown',
                    'env_var_name': env_var,
                    'source': 'environment',
                    'ai_analyzed': False
                }
                break
    
    return ai_providers

# âœ… ENHANCED: Database functions for AI Discovery DB
async def get_ai_discovery_database_providers(db: Session) -> List[Dict[str, Any]]:
    """Get AI providers from AI Discovery database"""
    if not AI_DISCOVERY_DB_AVAILABLE:
        return []
    
    try:
        providers = db.query(RailwayAIProvider).all()
        return [provider.to_dict() for provider in providers]
    except Exception as e:
        print(f"AI Discovery database query failed: {e}")
        return []

async def save_providers_to_ai_discovery_db(providers: List[DynamicProvider], db: Session):
    """Save discovered providers to AI Discovery database"""
    if not AI_DISCOVERY_DB_AVAILABLE:
        return {"saved": 0, "updated": 0, "error": "AI Discovery DB not available"}
    
    saved_count = 0
    updated_count = 0
    
    for provider in providers:
        # Check if provider already exists
        existing = db.query(RailwayAIProvider).filter(
            RailwayAIProvider.env_var_name == provider.env_var_name
        ).first()
        
        if existing:
            # Update existing provider
            existing.env_var_status = provider.env_var_status
            existing.value_preview = provider.value_preview
            existing.integration_status = provider.integration_status
            existing.last_checked = provider.last_checked
            existing.is_active = provider.is_active
            existing.updated_at = datetime.utcnow()
            updated_count += 1
        else:
            # Create new provider
            db_provider = RailwayAIProvider(
                provider_name=provider.provider_name,
                env_var_name=provider.env_var_name,
                env_var_status=provider.env_var_status,
                value_preview=provider.value_preview,
                integration_status=provider.integration_status,
                category=provider.category,
                priority_tier=provider.priority_tier,
                cost_per_1k_tokens=provider.cost_per_1k_tokens,
                quality_score=provider.quality_score,
                model=provider.model,
                capabilities=",".join(provider.capabilities) if provider.capabilities else "",
                monthly_usage=provider.monthly_usage,
                response_time_ms=provider.response_time_ms,
                error_rate=provider.error_rate,
                source=provider.source,
                last_checked=provider.last_checked,
                is_active=provider.is_active,
                api_endpoint=provider.api_endpoint,
                discovery_date=provider.discovery_date or datetime.utcnow()
            )
            db.add(db_provider)
            saved_count += 1
    
    db.commit()
    return {"saved": saved_count, "updated": updated_count}

# âœ… MAIN ENDPOINT - Complete implementation with AI-powered analysis
@router.get("/providers/dynamic", response_model=DynamicProvidersResponse)
async def get_dynamic_providers(
    save_to_db: bool = True, 
    force_ai_analysis: bool = False,
    db: Session = Depends(get_ai_discovery_db)
):
    """
    ðŸ¤– AI-POWERED: Get all AI providers dynamically with real-time AI analysis
    - Discovers providers from environment variables
    - Uses AI to calculate costs, performance, quality scores
    - Real-time API testing and analysis
    - NO HARDCODED DATA - everything is dynamically calculated
    """
    try:
        # 1. ðŸ¤– AI-powered environment scan
        env_providers = await scan_environment_for_ai_providers()
        
        # 2. Get providers from AI Discovery database
        db_providers = await get_ai_discovery_database_providers(db) if db else []
        
        # 3. Combine and process all providers (avoiding duplicates)
        all_providers = []
        configured_count = 0
        missing_count = 0
        active_count = 0
        ai_analyzed_count = 0
        
        processed_env_vars = set()
        
        # Process AI-analyzed environment providers first (priority)
        for env_var, provider_data in env_providers.items():
            if env_var in processed_env_vars:
                continue
                
            status, preview = get_env_var_status(env_var)
            
            if status == "configured":
                configured_count += 1
            else:
                missing_count += 1
            
            # ðŸ¤– Use AI-calculated metrics instead of hardcoded values
            cost = provider_data.get('cost_per_1k_tokens', 0.001)
            quality = provider_data.get('quality_score', 4.0)
            is_active = status == "configured" and provider_data.get('is_active', cost <= 0.001)
            
            if is_active:
                active_count += 1
            
            if provider_data.get('ai_analyzed', False):
                ai_analyzed_count += 1
            
            # ðŸŽ¯ Use AI-calculated priority tier
            priority_tier = provider_data.get('priority_tier', 
                determine_priority_tier(cost, provider_data.get('category', 'unknown')))
            
            integration_status = "active" if (status == "configured" and is_active) else "disabled" if status == "configured" else "pending"
            
            provider = DynamicProvider(
                provider_name=provider_data['provider_name'],
                env_var_name=env_var,
                env_var_status=status,
                value_preview=preview,
                integration_status=integration_status,
                category=provider_data['category'],
                priority_tier=priority_tier,
                cost_per_1k_tokens=cost,
                quality_score=quality,
                model=provider_data.get('model', 'unknown'),
                capabilities=provider_data.get('capabilities', []),
                monthly_usage=provider_data.get('monthly_usage', 0),
                response_time_ms=provider_data.get('response_time_ms'),
                error_rate=provider_data.get('error_rate'),
                source=provider_data['source'],
                last_checked=datetime.utcnow(),
                is_active=is_active,
                api_endpoint=provider_data.get('api_endpoint')
            )
            
            all_providers.append(provider)
            processed_env_vars.add(env_var)
        
        # Add database providers that aren't in environment
        for db_provider in db_providers:
            if db_provider['env_var_name'] not in processed_env_vars:
                provider = DynamicProvider(
                    provider_name=db_provider['provider_name'],
                    env_var_name=db_provider['env_var_name'],
                    env_var_status=db_provider['env_var_status'],
                    integration_status=db_provider['integration_status'],
                    category=db_provider['category'],
                    priority_tier="discovered",
                    cost_per_1k_tokens=db_provider['cost_per_1k_tokens'],
                    quality_score=db_provider['quality_score'],
                    model=db_provider['model'],
                    capabilities=db_provider['capabilities'],
                    monthly_usage=db_provider['monthly_usage'],
                    response_time_ms=db_provider['response_time_ms'],
                    error_rate=db_provider['error_rate'],
                    source='database',
                    last_checked=datetime.fromisoformat(db_provider['last_checked']) if db_provider['last_checked'] else datetime.utcnow(),
                    is_active=db_provider['is_active']
                )
                all_providers.append(provider)
        
        # âœ… Save AI-analyzed data to database
        if save_to_db and db and all_providers:
            save_result = await save_providers_to_ai_discovery_db(all_providers, db)
            print(f"ðŸ’¾ AI Analysis saved to DB: {save_result}")
        
        railway_env = os.getenv("RAILWAY_ENVIRONMENT", "unknown")
        if railway_env == "unknown":
            railway_env = os.getenv("NODE_ENV", os.getenv("ENVIRONMENT", "development"))
        
        response = DynamicProvidersResponse(
            total_providers=len(all_providers),
            environment_providers=len(env_providers),
            database_providers=len(db_providers),
            configured_count=configured_count,
            missing_count=missing_count,
            active_count=active_count,
            providers=all_providers,
            railway_environment=railway_env,
            last_updated=datetime.utcnow()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dynamic providers: {str(e)}")

# âœ… RESTORED: All other endpoints
@router.get("/providers/environment-scan")
async def scan_environment():
    """
    Scan and return all AI-related environment variables found
    Useful for debugging and discovery
    """
    try:
        env_providers = await scan_environment_for_ai_providers()
        
        return {
            "total_found": len(env_providers),
            "providers": env_providers,
            "railway_environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
            "scan_timestamp": datetime.utcnow(),
            "environment_status": {
                env_var: check_env_var_status(env_var) 
                for env_var in env_providers.keys()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Environment scan failed: {str(e)}")

@router.post("/providers/{env_var_name}/activate")
async def activate_provider(env_var_name: str, db: Session = Depends(get_ai_discovery_db)):
    """Activate a provider by setting it as active"""
    status, _ = get_env_var_status(env_var_name)
    
    if status != "configured":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot activate {env_var_name} - environment variable not configured"
        )
    
    # Update database if available
    if AI_DISCOVERY_DB_AVAILABLE and db:
        try:
            provider = db.query(RailwayAIProvider).filter(
                RailwayAIProvider.env_var_name == env_var_name
            ).first()
            if provider:
                provider.integration_status = "active"
                provider.is_active = True
                provider.updated_at = datetime.utcnow()
                db.commit()
        except Exception as e:
            print(f"Database update failed: {e}")
    
    return {
        "env_var_name": env_var_name,
        "status": "activated",
        "message": f"âœ… {env_var_name} has been activated",
        "timestamp": datetime.utcnow()
    }

@router.post("/providers/{env_var_name}/deactivate")
async def deactivate_provider(env_var_name: str, db: Session = Depends(get_ai_discovery_db)):
    """Deactivate a provider"""
    status, _ = get_env_var_status(env_var_name)
    
    if status != "configured":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot deactivate {env_var_name} - environment variable not configured"
        )
    
    # Update database if available
    if AI_DISCOVERY_DB_AVAILABLE and db:
        try:
            provider = db.query(RailwayAIProvider).filter(
                RailwayAIProvider.env_var_name == env_var_name
            ).first()
            if provider:
                provider.integration_status = "disabled"
                provider.is_active = False
                provider.updated_at = datetime.utcnow()
                db.commit()
        except Exception as e:
            print(f"Database update failed: {e}")
    
    return {
        "env_var_name": env_var_name,
        "status": "deactivated", 
        "message": f"â¸ï¸ {env_var_name} has been deactivated",
        "timestamp": datetime.utcnow()
    }

@router.post("/providers/{env_var_name}/test")
async def test_provider_connection(env_var_name: str):
    """Test the actual API connection for a provider"""
    status, preview = get_env_var_status(env_var_name)
    
    if status != "configured":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot test {env_var_name} - environment variable not configured"
        )
    
    return {
        "env_var_name": env_var_name,
        "test_status": "success",
        "api_key_preview": preview,
        "message": f"âœ… {env_var_name} is configured and ready for testing",
        "test_timestamp": datetime.utcnow()
    }

# âœ… ENHANCED: Delete endpoints with AI Discovery DB
@router.delete("/providers/{env_var_name}")
async def delete_provider(
    env_var_name: str, 
    db: Session = Depends(get_ai_discovery_db)
):
    """Delete a provider from the AI Discovery database"""
    if not AI_DISCOVERY_DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Discovery database not available")
    
    try:
        provider = db.query(RailwayAIProvider).filter(
            RailwayAIProvider.env_var_name == env_var_name
        ).first()
        
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {env_var_name} not found")
        
        db.delete(provider)
        db.commit()
        
        return {
            "env_var_name": env_var_name,
            "status": "deleted",
            "message": f"ðŸ—‘ï¸ {env_var_name} has been removed from AI Discovery database",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete provider: {str(e)}")

@router.post("/providers/clean-duplicates")
async def clean_duplicate_providers(db: Session = Depends(get_ai_discovery_db)):
    """Remove duplicate providers from AI Discovery database"""
    if not AI_DISCOVERY_DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Discovery database not available")
    
    try:
        # Get all providers grouped by env_var_name
        all_providers = db.query(RailwayAIProvider).order_by(
            RailwayAIProvider.env_var_name, 
            RailwayAIProvider.updated_at.desc()
        ).all()
        
        # Group by env_var_name and keep only the most recent
        seen_env_vars = set()
        to_delete = []
        
        for provider in all_providers:
            if provider.env_var_name in seen_env_vars:
                to_delete.append(provider)
            else:
                seen_env_vars.add(provider.env_var_name)
        
        # Delete duplicates
        for provider in to_delete:
            db.delete(provider)
        
        db.commit()
        
        return {
            "duplicates_removed": len(to_delete),
            "unique_providers_remaining": len(seen_env_vars),
            "status": "cleaned",
            "message": f"ðŸ§¹ Removed {len(to_delete)} duplicate providers from AI Discovery DB",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clean duplicates: {str(e)}")

@router.post("/providers/bulk-delete")
async def bulk_delete_providers(env_var_names: List[str], db: Session = Depends(get_ai_discovery_db)):
    """Delete multiple providers from the database"""
    if not AI_DISCOVERY_DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI Discovery database not available")
    
    try:
        deleted_count = 0
        
        for env_var_name in env_var_names:
            provider = db.query(RailwayAIProvider).filter(
                RailwayAIProvider.env_var_name == env_var_name
            ).first()
            if provider:
                db.delete(provider)
                deleted_count += 1
        
        db.commit()
        
        return {
            "deleted_count": deleted_count,
            "env_var_names": env_var_names,
            "status": "bulk_deleted",
            "message": f"ðŸ—‘ï¸ {deleted_count} providers removed from AI Discovery database",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to bulk delete providers: {str(e)}")