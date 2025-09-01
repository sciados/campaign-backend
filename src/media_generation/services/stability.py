import httpx

from typing import Optional
from ..config import settings
from .util import with_retries

STABILITY_BASE = "https://api.stability.ai"

async def generate_image_sdxl(prompt: str, size: Optional[str] = None) -> str:
    if not settings.STABILITY_API_KEY:
        raise RuntimeError("STABILITY_API_KEY is not configured")
    size = size or settings.DEFAULT_IMAGE_SIZE
    # Stability can return base64 or image bytes; some endpoints return URLs if hosted.
    # We use an endpoint that returns an image as binary and expect the caller to upload to R2.
    url = f"{STABILITY_BASE}/v2beta/stable-image/generate/sd3"
    headers = {"Authorization": f"Bearer {settings.STABILITY_API_KEY}"}
    json = {"prompt": prompt, "output_format": "png", "aspect_ratio": "1:1" if size.startswith("1024") else "9:16"}
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await with_retries(lambda: client.post(url, headers=headers, json=json))
        resp.raise_for_status()
        # Return raw bytes to uploader
        return resp.content