# ==============================================================================
# 6. STORAGE API ROUTES
# ==============================================================================

# src/storage/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database.session import get_async_db
from src.users.middleware.auth_middleware import get_current_user
from src.core.factories.service_factory import ServiceFactory
from typing import List, Optional
import io

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    campaign_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user)
):
    """Upload file to storage"""
    
    file_service = ServiceFactory().get_service("file_manager")
    if not file_service:
        raise HTTPException(status_code=500, detail="File service not available")
    
    # Read file data
    file_data = await file.read()
    
    # Upload file
    result = await file_service.upload_file(
        db=db,
        user_id=str(current_user.id),
        file_data=file_data,
        original_filename=file.filename,
        content_type=file.content_type,
        campaign_id=campaign_id
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user)
):
    """Download file from storage"""
    
    file_service = ServiceFactory().get_service("file_manager")
    if not file_service:
        raise HTTPException(status_code=500, detail="File service not available")
    
    result = await file_service.download_file(
        db=db,
        user_id=str(current_user.id),
        file_id=file_id
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return StreamingResponse(
        io.BytesIO(result["file_data"]),
        media_type=result["content_type"]
    )

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user)
):
    """Delete file from storage"""
    
    file_service = ServiceFactory().get_service("file_manager")
    if not file_service:
        raise HTTPException(status_code=500, detail="File service not available")
    
    result = await file_service.delete_file(
        db=db,
        user_id=str(current_user.id),
        file_id=file_id
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/generate/images")
async def generate_campaign_images(
    campaign_id: str = Form(...),
    platforms: List[str] = Form(["instagram", "facebook"]),
    images_per_platform: int = Form(2),
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user)
):
    """Generate campaign images"""
    
    media_service = ServiceFactory().get_service("media_generator")
    if not media_service:
        raise HTTPException(status_code=500, detail="Media service not available")
    
    # Get campaign intelligence data (would integrate with campaigns module)
    intelligence_data = {
        "source_title": "Sample Product",
        "offer_intelligence": {
            "benefits": ["Health optimization", "Natural wellness"]
        }
    }
    
    result = await media_service.generate_campaign_images(
        db=db,
        user_id=str(current_user.id),
        campaign_id=campaign_id,
        intelligence_data=intelligence_data,
        platforms=platforms,
        images_per_platform=images_per_platform
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/generate/video")
async def generate_slideshow_video(
    campaign_id: str = Form(...),
    image_file_ids: Optional[List[str]] = Form(None),
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user)
):
    """Generate slideshow video"""
    
    media_service = ServiceFactory().get_service("media_generator")
    if not media_service:
        raise HTTPException(status_code=500, detail="Media service not available")
    
    # Get campaign intelligence data (would integrate with campaigns module)
    intelligence_data = {
        "source_title": "Sample Product",
        "offer_intelligence": {
            "benefits": ["Health optimization", "Natural wellness"]
        }
    }
    
    result = await media_service.generate_slideshow_video(
        db=db,
        user_id=str(current_user.id),
        campaign_id=campaign_id,
        intelligence_data=intelligence_data,
        image_file_ids=image_file_ids
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result