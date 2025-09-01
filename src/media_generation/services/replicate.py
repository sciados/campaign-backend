import httpx, asyncio
from typing import Dict, Any
from ..config import settings
from .util import with_retries

REPLICATE_BASE = "https://api.replicate.com/v1"

async def _post_predictions(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not settings.REPLICATE_API_TOKEN:
        raise RuntimeError("REPLICATE_API_TOKEN is not configured")
    headers = {
        "Authorization": f"Token {settings.REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(f"{REPLICATE_BASE}/predictions", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()

async def image_to_video_animatediff(image_url: str, prompt: str, num_frames: int = 64) -> str:
    payload = {
        "version": "animate-diff-version-id",  # replace with a specific model version you prefer
        "input": {"image": image_url, "prompt": prompt, "num_frames": num_frames}
    }
    data = await _post_predictions(payload)
    # Poll until completed
    status_url = data["urls"]["get"]
    async with httpx.AsyncClient(timeout=120) as client:
        while True:
            res = await client.get(status_url, headers={"Authorization": f"Token {settings.REPLICATE_API_TOKEN}"})
            res.raise_for_status()
            j = res.json()
            if j["status"] in ("succeeded", "failed", "canceled"):
                if j["status"] == "succeeded":
                    # Replicate returns an array of output URLs
                    out = j.get("output")
                    return out[-1] if isinstance(out, list) and out else out
                raise RuntimeError(f"Replicate job failed: {j}")
            await asyncio.sleep(1.2)