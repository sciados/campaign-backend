# src/media_generation/routes.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import SOCIAL_MEDIA_SIZES
from .services import fal, r2
from .repository.repo import insert_generated_media
from ..db import get_session  # your async DB session provider

router = APIRouter()

class MediaReq(BaseModel):
    prompt: str
    user_id: str
    platform: str
    media_type: str  # "image" or "video"
    salespage_url: str = None

@router.post("/generate/media")
async def generate_media(req: MediaReq, session: AsyncSession = Depends(get_session)):
    platform_sizes = SOCIAL_MEDIA_SIZES.get(req.platform.lower())
    if not platform_sizes:
        return {"error": "Unsupported platform"}

    # generate media based on type
    if req.media_type == "image":
        image_url = await fal.generate_image(req.prompt, size=platform_sizes["image"])
        final_url = await r2.upload_from_url(image_url)
    elif req.media_type == "video":
        video_url = await fal.generate_video(req.prompt, resolution=platform_sizes["video"])
        final_url = await r2.upload_from_url(video_url)
    else:
        return {"error": "Unsupported media type"}

    # store in DB
    await insert_generated_media(session, {
        "user_id": req.user_id,
        "salespage_url": req.salespage_url,
        "media_type": req.media_type,
        "platform": req.platform,
        "prompt": req.prompt,
        "provider": "fal",
        "output_url": final_url,
        "cost_usd": 0.0
    })

    return {"url": final_url, "platform": req.platform, "media_type": req.media_type}