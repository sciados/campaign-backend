"""
File: src/intelligence/routers/content_routes.py
Content Routes - Content generation and management endpoints
Extracted from main routes.py for better organization
"""
from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from ..handlers.content_handler import ContentHandler
from ..schemas.requests import GenerateContentRequest
from ..schemas.responses import ContentGenerationResponse

router = APIRouter()

@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate content using intelligence data"""
    
    handler = ContentHandler(db, current_user)
    
    try:
        result = await handler.generate_content(request_data)
        return ContentGenerationResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

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
    
    try:
        # Try to use the factory if available
        try:
            from src.intelligence.generators.factory import ContentGeneratorFactory
            factory = ContentGeneratorFactory()
            capabilities = factory.get_generator_capabilities()
            available_types = factory.get_available_generators()
            factory_available = True
        except ImportError:
            factory_available = False
            capabilities = {}
            available_types = []

        # Fallback to manual detection
        if not factory_available:
            available_types = []
            capabilities = {}

            # Check each generator individually
            generators_to_check = [
                ("email_sequence", "EmailSequenceGenerator", "src.intelligence.generators.email_generator"),
                ("SOCIAL_POSTS", "SocialMediaGenerator", "src.intelligence.generators.social_media_generator"),
                ("ad_copy", "AdCopyGenerator", "src.intelligence.generators.ad_copy_generator"),
                ("blog_post", "BlogPostGenerator", "src.intelligence.generators.blog_post_generator"),
                ("landing_page", "EnhancedLandingPageGenerator", "src.intelligence.generators.landing_page.core.generator"),
                ("video_script", "VideoScriptGenerator", "src.intelligence.generators.video_script_generator"),
            ]

            for content_type, class_name, module_path in generators_to_check:
                try:
                    module = __import__(module_path, fromlist=[class_name])
                    getattr(module, class_name)
                    available_types.append(content_type)
                    capabilities[content_type] = {
                        "description": f"Generate {content_type.replace('_', ' ')}",
                        "status": "available"
                    }
                except (ImportError, AttributeError):
                    capabilities[content_type] = {
                        "description": f"Generate {content_type.replace('_', ' ')}",
                        "status": "unavailable"
                    }

        return {
            "available_content_types": available_types,
            "total_available": len(available_types),
            "capabilities": capabilities,
            "factory_available": factory_available,
            "status": "operational" if available_types else "limited"
        }

    except Exception as e:
        return {
            "available_content_types": ["email_sequence"],  # Fallback
            "total_available": 1,
            "capabilities": {
                "email_sequence": {
                    "description": "Generate email sequences",
                    "status": "fallback"
                }
            },
            "factory_available": False,
            "status": "fallback",
            "error": str(e)
        }