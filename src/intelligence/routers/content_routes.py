# src/intelligence/routers/content_routes.py
"""
Fixed Content Routes - Parameter and Data Type Corrections
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from src.core.database import get_db
from src.core.crud.intelligence_crud import IntelligenceCRUD
from src.intelligence.schemas.requests import ContentGenerationRequest
from src.intelligence.schemas.responses import ContentResponse, GeneratedContentResponse
from src.intelligence.handlers.content_handler import ContentHandler

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize CRUD and handler
intelligence_crud = IntelligenceCRUD()
content_handler = ContentHandler()

@router.get("/content/{campaign_id}", response_model=List[GeneratedContentResponse])
async def get_generated_content(
    campaign_id: str,
    skip: int = Query(0, ge=0),  # Note: using 'skip' not 'offset'
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get generated content for a campaign - FIXED parameter names"""
    try:
        logger.info(f"🔍 Getting content for campaign {campaign_id}")
        
        # FIXED: Use 'skip' parameter name instead of 'offset'
        content_items = await intelligence_crud.get_generated_content(
            db=db,
            campaign_id=campaign_id,
            skip=skip,  # Changed from 'offset' to 'skip'
            limit=limit
        )
        
        logger.info(f"✅ Retrieved {len(content_items)} content items")
        return content_items
        
    except Exception as e:
        logger.error(f"❌ Error getting content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get content: {str(e)}")

@router.post("/content/generate", response_model=ContentResponse)
async def generate_content(
    request: ContentGenerationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate content for a campaign - FIXED data type handling"""
    try:
        logger.info("🎯 Content generation request received")
        
        # FIXED: Handle preference values that might be strings instead of integers
        preferences = request.preferences.copy() if request.preferences else {}
        
        # Convert string preference values to appropriate types
        for key, value in preferences.items():
            if isinstance(value, str):
                # Handle specific preference keys that should be integers
                if key in ['length', 'word_count', 'email_count', 'sequence_length']:
                    try:
                        # Map common string values to integers
                        if value.lower() == 'short':
                            preferences[key] = 1
                        elif value.lower() == 'medium':
                            preferences[key] = 2
                        elif value.lower() == 'long':
                            preferences[key] = 3
                        else:
                            # Try to convert directly to int
                            preferences[key] = int(value)
                    except ValueError:
                        logger.warning(f"⚠️ Could not convert preference {key}='{value}' to integer, using default")
                        preferences[key] = 2  # Default to medium
                elif key in ['tone', 'style', 'format']:
                    # Keep string values for tone/style/format preferences
                    continue
                elif key.endswith('_enabled') or key.startswith('include_'):
                    # Convert boolean-like strings
                    preferences[key] = value.lower() in ['true', '1', 'yes', 'on']
        
        # Create the fixed request object
        fixed_request = ContentGenerationRequest(
            campaign_id=request.campaign_id,
            content_type=request.content_type,
            preferences=preferences,
            prompt=request.prompt,
            intelligence_source_id=getattr(request, 'intelligence_source_id', None)
        )
        
        # Generate content using the handler
        result = await content_handler.generate_content(
            db=db,
            request=fixed_request
        )
        
        logger.info(f"✅ Content generated successfully: {result.content_type}")
        return result
        
    except ValueError as e:
        if "invalid literal for int()" in str(e):
            logger.error(f"❌ Data type conversion error: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid data format in preferences. Please check numeric values: {str(e)}"
            )
        else:
            raise
    except Exception as e:
        logger.error(f"❌ Content generation failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Content generation failed: {str(e)}"
        )

@router.get("/content/{campaign_id}/types")
async def get_available_content_types(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get available content types for a campaign"""
    try:
        # Get campaign intelligence to determine available content types
        intelligence_data = await intelligence_crud.get_campaign_intelligence(
            db=db,
            campaign_id=campaign_id
        )
        
        if not intelligence_data:
            raise HTTPException(status_code=404, detail="No intelligence data found for campaign")
        
        # Return standard content types (could be made dynamic based on intelligence)
        content_types = [
            {"id": "email_sequence", "name": "Email Sequence", "description": "Multi-email marketing sequence"},
            {"id": "ad_copy", "name": "Ad Copy", "description": "Social media and search ads"},
            {"id": "blog_post", "name": "Blog Post", "description": "SEO-optimized blog content"},
            {"id": "social_media", "name": "Social Media", "description": "Social platform posts"},
            {"id": "landing_page", "name": "Landing Page", "description": "Conversion-focused landing page"},
            {"id": "video_script", "name": "Video Script", "description": "Video marketing script"}
        ]
        
        return {"content_types": content_types}
        
    except Exception as e:
        logger.error(f"❌ Error getting content types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get content types: {str(e)}")

@router.delete("/content/{content_id}")
async def delete_generated_content(
    content_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a specific piece of generated content"""
    try:
        await intelligence_crud.delete_generated_content(
            db=db,
            content_id=content_id
        )
        
        logger.info(f"✅ Deleted content {content_id}")
        return {"message": "Content deleted successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error deleting content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete content: {str(e)}")