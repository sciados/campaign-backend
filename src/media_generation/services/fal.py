import httpx

from typing import Optional, Dict, Any
from .util import with_retries
from ..config import settings

# NOTE: Endpoints may evolve. Keep these as easy-to-edit constants.
FAL_BASE = "https://fal.run"  # Fal proxy base; some deployments use api.fal.ai

# Example model routes (adjust if needed)
FLUX_IMAGE_ROUTE = "/fal-ai/flux/schnell"
TEXT2VIDEO_ROUTE = "/fal-ai/fast-svd-lcm/text-to-video"
IMG2VIDEO_ROUTE = "/fal-ai/minimax/video-from-image"

async def _post_json(route: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not settings.FAL_API_KEY:
        raise RuntimeError("FAL_API_KEY is not configured")
    headers = {"Authorization": f"Key {settings.FAL_API_KEY}", "Content-Type": "application/json"}
    url = FAL_BASE + route
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()

async def generate_image(prompt: str, size: Optional[str] = None) -> str:
    size = size or settings.DEFAULT_IMAGE_SIZE
    payload = {"prompt": prompt, "image_size": size}
    data = await with_retries(lambda: _post_json(FLUX_IMAGE_ROUTE, payload))
    # Normalize likely outputs
    url = None
    if isinstance(data, dict):
        url = (
            data.get("image", {}).get("url")
            or (data.get("images") or [{}])[0].get("url")
            or data.get("url")
        )
    if not url:
        raise RuntimeError(f"Fal image response missing url: {data}")
    return url

async def text_to_video(prompt: str, duration: Optional[int] = None, aspect_ratio: Optional[str] = None) -> str:
    duration = duration or settings.DEFAULT_VIDEO_DURATION
    aspect_ratio = aspect_ratio or settings.DEFAULT_ASPECT_RATIO
    payload = {"prompt": prompt, "duration": duration, "aspect_ratio": aspect_ratio}
    data = await with_retries(lambda: _post_json(TEXT2VIDEO_ROUTE, payload))
    url = data.get("video_url") or data.get("url")
    if not url:
        # Fal often returns a task URL to poll; support both patterns
        url = data.get("output", {}).get("video", {}).get("url") or data.get("request", {}).get("result_url")
    if not url:
        raise RuntimeError(f"Fal text-to-video response missing url: {data}")
    return url

async def image_to_video(image_url: str, motion_prompt: str = "", duration: Optional[int] = None, aspect_ratio: Optional[str] = None) -> str:
    duration = duration or settings.DEFAULT_VIDEO_DURATION
    aspect_ratio = aspect_ratio or settings.DEFAULT_ASPECT_RATIO
    payload = {
        "image_url": image_url,
        "prompt": motion_prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio
    }
    data = await with_retries(lambda: _post_json(IMG2VIDEO_ROUTE, payload))
    url = data.get("video_url") or data.get("url")
    if not url:
        url = data.get("output", {}).get("video", {}).get("url")
    if not url:
        raise RuntimeError(f"Fal image-to-video response missing url: {data}")
    return url