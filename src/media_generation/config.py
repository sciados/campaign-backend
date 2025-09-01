from pydantic import BaseSettings
from typing import Dict, List, Optional

class Settings(BaseSettings):
    # Providers
    FAL_API_KEY: Optional[str]
    STABILITY_API_KEY: Optional[str]
    REPLICATE_API_TOKEN: Optional[str]

    # R2
    CLOUDFLARE_ACCOUNT_ID: Optional[str]
    CLOUDFLARE_R2_ACCESS_KEY_ID: Optional[str]
    CLOUDFLARE_R2_SECRET_ACCESS_KEY: Optional[str]
    CLOUDFLARE_R2_BUCKET_NAME: Optional[str]
    CLOUDFLARE_R2_PUBLIC_BASE_URL: Optional[str]

    # Defaults
    DEFAULT_IMAGE_SIZE: str = "1024x1024"
    DEFAULT_VIDEO_DURATION: int = 15
    DEFAULT_ASPECT_RATIO: str = "9:16"

    # Model selection per provider/task
    MODEL_CONFIG: Dict[str, Dict[str, List[str]]] = {
        "fal": {
            "image": ["flux-schnell", "sdxl-turbo"],
            "video": ["fast-svd-lcm", "fast-svd-lite"],
            "img2video": ["minimax", "animate-lite"]
        },
        "stability": {"image": ["stable-diffusion-xl-v2-2", "stable-diffusion-v1-6"]},
        "replicate": {"img2video": ["animate-diff-v2", "animate-diff-v1"]}
    }

    SOCIAL_MEDIA_SIZES = {
    "tiktok": {"image": "1080x1920", "video": "1080x1920"},
    "instagram_reel": {"image": "1080x1920", "video": "1080x1920"},
    "instagram_post": {"image": "1080x1080", "video": "1080x1080"},
    "facebook_story": {"image": "1080x1920", "video": "1080x1920"},
    "linkedin_post": {"image": "1200x627", "video": "1080x1080"},
    "youtube_short": {"image": "1080x1920", "video": "1080x1920"}
    }

settings = Settings()