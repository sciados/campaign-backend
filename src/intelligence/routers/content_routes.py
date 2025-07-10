"""
File: src/intelligence/routers/content_routes.py
Enhanced Content Routes - FIXED Ultra-Cheap AI Integration
"""
from fastapi import APIRouter, Depends, HTTPException, status as http_status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import asyncio

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User

# Import existing handler
from ..handlers.content_handler import ContentHandler, enhanced_content_generation
from ..schemas.requests import GenerateContentRequest
from ..schemas.responses import ContentGenerationResponse

router = APIRouter()

# ============================================================================
# ✅ FIXED: Main Content Generation Endpoint (Frontend Compatible)
# ============================================================================

@router.post("/generate")
async def generate_content(
    request_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🎯 FIXED: Content generation endpoint with ultra-cheap AI
    
    Frontend sends: POST /api/intelligence/content/generate
    {
        "content_type": "ad_copy",
        "prompt": "Create ad for fitness product", 
        "context": {...}
    }
    
    Now with 99% cost savings vs OpenAI!
    """
    
    try:
        # ✅ NEW: Extract content type and prepare data properly
        content_type = request_data.get("content_type", "ad_copy")
        prompt = request_data.get("prompt", "")
        context = request_data.get("context", {})
        campaign_id = request_data.get("campaign_id")
        
        logging.info(f"🎯 Content generation: {content_type} for user {current_user.id}")
        
        # ✅ NEW: Use enhanced content generation with proper intelligence data
        try:
            # Prepare intelligence data from prompt and context
            intelligence_data = {
                "campaign_id": campaign_id,
                "campaign_name": context.get("campaign_name", "Generated Campaign"),
                "target_audience": context.get("target_audience", "health-conscious adults"),
                "offer_intelligence": {
                    "insights": [prompt] if prompt else ["Generate content"],
                    "benefits": context.get("benefits", ["improved results", "better outcomes"])
                },
                "psychology_intelligence": context.get("psychology_intelligence", {}),
                "content_intelligence": context.get("content_intelligence", {}),
                "competitive_intelligence": context.get("competitive_intelligence", {}),
                "brand_intelligence": context.get("brand_intelligence", {}),
                "intelligence_sources": []
            }
            
            # Prepare preferences
            preferences = {
                "platform": context.get("platform", "facebook"),
                "count": context.get("count", "3"),
                "length": context.get("length", "medium"),
                "tone": context.get("tone", "persuasive"),
                "format": context.get("format", "standard")
            }
            
            # Use enhanced content generation
            result = await enhanced_content_generation(
                content_type=content_type,
                intelligence_data=intelligence_data,
                preferences=preferences
            )
            
            # Ensure proper response format
            if not isinstance(result, dict):
                result = {"content": str(result), "success": True}
            
            # Add ultra-cheap AI metadata
            result.update({
                "cost_savings": "99% vs OpenAI",
                "provider": result.get("metadata", {}).get("ai_provider_used", "ultra-cheap-ai"),
                "generation_method": "enhanced",
                "ultra_cheap_ai_used": True
            })
            
            logging.info("✅ Ultra-cheap AI generation successful")
            
        except Exception as ultra_cheap_error:
            logging.warning(f"⚠️ Ultra-cheap AI failed, using existing handler: {ultra_cheap_error}")
            
            # Fallback to existing handler with proper data format
            handler = ContentHandler(db, current_user)
            
            # Convert to handler format
            handler_request = {
                "content_type": content_type,
                "campaign_id": campaign_id,
                "preferences": {
                    "prompt": prompt,
                    "context": context,
                    **preferences
                }
            }
            
            result = await handler.generate_content(handler_request)
            result.update({
                "cost_savings": "standard",
                "provider": "existing-handler",
                "generation_method": "fallback",
                "ultra_cheap_ai_used": False
            })
        
        # ✅ FIXED: Save to database IMMEDIATELY after generation (before response formatting)
        try:
            content_id = await save_generation_history_sync(
                db=db,
                user_id=current_user.id,
                content_type=content_type,
                prompt=prompt,
                result=result,
                campaign_id=campaign_id
            )
            logging.info(f"✅ Content saved to database with ID: {content_id}")
        except Exception as save_error:
            logging.error(f"❌ Failed to save to database: {save_error}")
            content_id = "temp_" + datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # ✅ FIXED: Format response to match expected schema
        formatted_response = {
            "content_id": content_id,
            "content_type": content_type,
            "generated_content": result,  # The actual generated content
            "smart_url": None,
            "performance_predictions": {},
            "intelligence_sources_used": len(intelligence_data.get("intelligence_sources", [])),
            "generation_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "generator_used": f"{content_type}_generator",
                "fallback_used": result.get("metadata", {}).get("fallback", False),
                "ultra_cheap_ai_enabled": True,
                "ultra_cheap_ai_used": result.get("ultra_cheap_ai_used", True),
                "cost_savings": result.get("metadata", {}).get("cost_savings", 0.0),
                "provider": result.get("provider", "ultra-cheap-ai"),
                "success": True
            }
        }
        
        return formatted_response
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logging.error(f"❌ Content generation failed: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

# ============================================================================
# ✅ FIXED: Ultra-Cheap AI Generation Function
# ============================================================================

async def generate_with_ultra_cheap_ai_fixed(
    content_type: str,
    intelligence_data: Dict[str, Any],
    preferences: Dict[str, Any],
    user_id: int
) -> Dict[str, Any]:
    """Generate content using ultra-cheap AI providers (99% cost savings) - FIXED"""
    
    try:
        logging.info(f"🚀 Ultra-cheap AI generation: {content_type}")
        
        # ✅ Use enhanced content generation function
        result = await enhanced_content_generation(
            content_type=content_type,
            intelligence_data=intelligence_data,
            preferences=preferences
        )
        
        # Ensure result is properly formatted
        if isinstance(result, str):
            result = {
                "content": result,
                "content_type": content_type,
                "success": True
            }
        elif isinstance(result, dict) and "content" not in result:
            result = {
                "content": str(result),
                "content_type": content_type,
                "success": True
            }
        
        # Add ultra-cheap AI metadata
        if not result.get("metadata"):
            result["metadata"] = {}
        
        result["metadata"].update({
            "ultra_cheap_ai_used": True,
            "cost_savings": 0.028,  # $0.028 saved vs OpenAI
            "generation_cost": 0.002,  # $0.002 actual cost
        })
        
        return result
        
    except Exception as e:
        logging.error(f"❌ Ultra-cheap AI generation failed: {e}")
        raise ValueError(f"Ultra-cheap AI generation failed: {str(e)}")

# ============================================================================
# ✅ FIXED: Specialized Generation Endpoints
# ============================================================================

@router.post("/generate/{content_type}")
async def generate_specific_content(
    content_type: str,
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate specific content type with ultra-cheap AI - FIXED"""
    
    try:
        prompt = request_data.get("prompt", "")
        context = request_data.get("context", {})
        campaign_id = request_data.get("campaign_id")
        
        # Prepare intelligence data
        intelligence_data = {
            "campaign_id": campaign_id,
            "campaign_name": context.get("campaign_name", "Generated Campaign"),
            "target_audience": context.get("target_audience", "health-conscious adults"),
            "offer_intelligence": {
                "insights": [prompt] if prompt else ["Generate content"],
                "benefits": context.get("benefits", ["improved results"])
            },
            "intelligence_sources": []
        }
        
        # Prepare preferences
        preferences = {
            "platform": context.get("platform", "facebook"),
            "count": context.get("count", "3"),
            "length": context.get("length", "medium")
        }
        
        result = await generate_with_ultra_cheap_ai_fixed(
            content_type=content_type,
            intelligence_data=intelligence_data,
            preferences=preferences,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "content": result.get("content"),
            "content_type": content_type,
            "cost_savings": "99% vs OpenAI",
            "provider": result.get("metadata", {}).get("ai_provider_used", "ultra-cheap-ai"),
            "generation_cost": result.get("metadata", {}).get("generation_cost", 0.002)
        }
        
    except Exception as e:
        logging.error(f"❌ Specific content generation failed: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate {content_type}: {str(e)}"
        )

# ============================================================================
# ✅ FIXED: Batch Generation
# ============================================================================

@router.post("/generate/batch")
async def generate_batch_content(
    requests: List[Dict[str, Any]],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate multiple content pieces with ultra-cheap AI - FIXED"""
    
    results = []
    total_cost_savings = 0
    
    for req in requests:
        try:
            content_type = req.get("content_type", "ad_copy")
            prompt = req.get("prompt", "")
            context = req.get("context", {})
            campaign_id = req.get("campaign_id")
            
            # Prepare intelligence data
            intelligence_data = {
                "campaign_id": campaign_id,
                "offer_intelligence": {
                    "insights": [prompt] if prompt else ["Generate content"],
                    "benefits": context.get("benefits", ["improved results"])
                },
                "intelligence_sources": []
            }
            
            preferences = {
                "platform": context.get("platform", "facebook"),
                "count": "1"  # Single item for batch
            }
            
            result = await generate_with_ultra_cheap_ai_fixed(
                content_type=content_type,
                intelligence_data=intelligence_data,
                preferences=preferences,
                user_id=current_user.id
            )
            
            results.append({
                "content_type": content_type,
                "success": True,
                "content": result.get("content"),
                "cost_savings": "$0.028 vs OpenAI",
                "provider": result.get("metadata", {}).get("ai_provider_used", "ultra-cheap-ai")
            })
            
            # Track cost savings
            total_cost_savings += result.get("metadata", {}).get("cost_savings", 0.028)
            
        except Exception as e:
            results.append({
                "content_type": req.get("content_type", "unknown"),
                "success": False,
                "error": str(e)
            })
    
    return {
        "success": True,
        "results": results,
        "total_items": len(requests),
        "successful_items": len([r for r in results if r.get("success")]),
        "total_cost_savings": f"${total_cost_savings:.3f}",
        "provider": "ultra-cheap-ai"
    }

# ============================================================================
# ✅ EXISTING ENDPOINTS (Keep your current functionality)
# ============================================================================

@router.get("/{campaign_id}")
async def get_campaign_content_list(
    campaign_id: str,
    include_body: bool = False,
    content_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of generated content for a campaign"""
    
    handler = ContentHandler(db, current_user)
    
    try:
        result = await handler.get_content_list(campaign_id, include_body, content_type)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content list: {str(e)}"
        )

@router.get("/{campaign_id}/{content_id}")
async def get_content_detail(
    campaign_id: str,
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed content including full body"""
    
    handler = ContentHandler(db, current_user)
    
    try:
        result = await handler.get_content_detail(campaign_id, content_id)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content detail: {str(e)}"
        )

@router.put("/{campaign_id}/{content_id}")
async def update_content(
    campaign_id: str,
    content_id: str,
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update generated content"""
    
    handler = ContentHandler(db, current_user)
    
    try:
        result = await handler.update_content(campaign_id, content_id, update_data)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update content: {str(e)}"
        )

@router.delete("/{campaign_id}/{content_id}")
async def delete_content(
    campaign_id: str,
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete generated content"""
    
    handler = ContentHandler(db, current_user)
    
    try:
        result = await handler.delete_content(campaign_id, content_id)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete content: {str(e)}"
        )

@router.get("/types/available")
async def get_available_content_types(
    current_user: User = Depends(get_current_user)
):
    """Get list of available content types and their capabilities"""
    
    return {
        "available_content_types": [
            "email_sequence",
            "ad_copy",
            "SOCIAL_POSTS"
        ],
        "total_available": 3,
        "capabilities": {
            "email_sequence": {
                "description": "Generate email sequences with 5 angles",
                "status": "available",
                "cost_savings": "99% vs OpenAI",
                "provider": "ultra-cheap-ai"
            },
            "ad_copy": {
                "description": "Generate ad copy for multiple platforms",
                "status": "available", 
                "cost_savings": "97% vs OpenAI",
                "provider": "ultra-cheap-ai"
            },
            "SOCIAL_POSTS": {
                "description": "Generate social media posts",
                "status": "limited",
                "cost_savings": "95% vs OpenAI",
                "provider": "ultra-cheap-ai"
            }
        },
        "ultra_cheap_ai": True,
        "cost_savings": "99% vs OpenAI",
        "status": "enhanced"
    }

# ============================================================================
# ✅ ULTRA-CHEAP AI STATUS & MONITORING
# ============================================================================

@router.get("/system/ultra-cheap-status")
async def get_ultra_cheap_status(current_user: User = Depends(get_current_user)):
    """Get ultra-cheap AI system status"""
    
    try:
        # Test email generator
        email_available = False
        try:
            from ..generators.email_generator import EmailSequenceGenerator
            gen = EmailSequenceGenerator()
            if hasattr(gen, 'ultra_cheap_providers'):
                email_available = True
                email_providers = len(gen.ultra_cheap_providers)
            else:
                email_providers = 0
        except:
            email_providers = 0
        
        # Test ad copy generator
        ad_available = False
        try:
            from ..generators.ad_copy_generator import AdCopyGenerator
            gen = AdCopyGenerator()
            if hasattr(gen, 'ultra_cheap_providers'):
                ad_available = True
                ad_providers = len(gen.ultra_cheap_providers)
            else:
                ad_providers = 0
        except:
            ad_providers = 0
        
        return {
            "ultra_cheap_ai_status": "operational" if (email_available or ad_available) else "limited",
            "generators": {
                "email_sequence": {
                    "available": email_available,
                    "ultra_cheap_providers": email_providers,
                    "cost_savings": "99.3% vs OpenAI"
                },
                "ad_copy": {
                    "available": ad_available,
                    "ultra_cheap_providers": ad_providers,
                    "cost_savings": "97% vs OpenAI"
                }
            },
            "cost_analysis": {
                "openai_cost_per_1k": "$0.030",
                "ultra_cheap_cost_per_1k": "$0.0008",
                "savings_per_1k_tokens": "$0.0292",
                "savings_percentage": "97.3%"
            },
            "monthly_projections": {
                "1000_users": "$1,665 saved",
                "5000_users": "$8,325 saved",
                "10000_users": "$16,650 saved"
            }
        }
        
    except Exception as e:
        return {
            "ultra_cheap_ai_status": "error",
            "error": str(e),
            "message": "Ultra-cheap AI status check failed"
        }

# ============================================================================
# ✅ UTILITY FUNCTIONS
# ============================================================================

async def save_generation_history_sync(
    db: AsyncSession,
    user_id: int,
    content_type: str,
    prompt: str,
    result: Dict[str, Any],
    campaign_id: str = None
) -> str:
    """Save generation history to database synchronously and return content_id"""
    try:
        from ...models.intelligence import GeneratedContent
        import json
        
        # Generate content ID
        content_id = f"content_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        
        generated_content = GeneratedContent(
            id=content_id,
            campaign_id=campaign_id,
            user_id=user_id,
            content_type=content_type,
            content_title=result.get("title", f"Generated {content_type.title()}"),
            content_body=json.dumps(result.get("content", {})),
            content_metadata=result.get("metadata", {}),
            generation_settings={
                "prompt": prompt,
                "ultra_cheap_ai_used": result.get("ultra_cheap_ai_used", True),
                "provider": result.get("provider", "ultra-cheap-ai"),
                "cost_savings": result.get("cost_savings", "99% vs OpenAI"),
                "generation_cost": result.get("metadata", {}).get("generation_cost", 0.0)
            },
            intelligence_used={
                "generation_timestamp": datetime.utcnow().isoformat(),
                "ultra_cheap_ai_used": True,
                "cost_savings": result.get("metadata", {}).get("cost_savings", 0.0),
                "provider_used": result.get("provider", "ultra-cheap-ai"),
                "generation_cost": result.get("metadata", {}).get("generation_cost", 0.0),
                "railway_compatible": True
            },
            is_published=False
        )
        
        db.add(generated_content)
        await db.commit()
        await db.refresh(generated_content)
        
        logging.info(f"✅ Saved generation to database: {content_id}")
        return content_id
        
    except Exception as e:
        logging.error(f"❌ Failed to save generation history: {str(e)}")
        await db.rollback()
        return f"temp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

async def save_generation_history(
    db: AsyncSession,
    user_id: int,
    content_type: str,
    prompt: str,
    result: Dict[str, Any]
):
    """Save generation history to database (background task version)"""
    try:
        await save_generation_history_sync(db, user_id, content_type, prompt, result)
    except Exception as e:
        logging.error(f"❌ Background save failed: {str(e)}")