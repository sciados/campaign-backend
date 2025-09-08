# =====================================
# File: src/core/config/storage_config.py
# =====================================

"""
Storage configuration for CampaignForge multi-cloud setup.

Manages Cloudflare R2 and Backblaze B2 configurations with tiered storage.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

from src.core.config.settings import settings


class StorageTier(Enum):
    """Storage tiers for different access patterns."""
    HOT = "hot"          # Frequently accessed (Cloudflare R2)
    WARM = "warm"        # Occasionally accessed
    COLD = "cold"        # Rarely accessed (Backblaze B2)
    ARCHIVE = "archive"  # Long-term storage


@dataclass
class CloudflareR2Config:
    """Cloudflare R2 storage configuration."""
    
    account_id: str
    access_key_id: str
    secret_access_key: str
    bucket_name: str
    region: str = "auto"
    endpoint_url: str = None
    
    def __post_init__(self):
        if not self.endpoint_url:
            self.endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"
    
    @property
    def boto3_config(self) -> Dict[str, Any]:
        """Get boto3 configuration for Cloudflare R2."""
        return {
            "aws_access_key_id": self.access_key_id,
            "aws_secret_access_key": self.secret_access_key,
            "endpoint_url": self.endpoint_url,
            "region_name": self.region,
        }


class StorageConfig:
    """Main storage configuration manager."""
    
    def __init__(self):
        self.cloudflare_r2 = CloudflareR2Config(
            account_id=settings.CLOUDFLARE_ACCOUNT_ID,
            access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
            secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
            bucket_name=settings.CLOUDFLARE_R2_BUCKET_NAME,
        )
    
    def get_storage_config_by_tier(self, tier: StorageTier) -> Dict[str, Any]:
        """Get storage configuration for specific tier."""
        configs = {
            StorageTier.HOT: {
                "provider": "cloudflare_r2",
                "config": self.cloudflare_r2.boto3_config,
                "bucket": self.cloudflare_r2.bucket_name,
                "prefix": "hot/",
            },
            StorageTier.WARM: {
                "provider": "cloudflare_r2",
                "config": self.cloudflare_r2.boto3_config,
                "bucket": self.cloudflare_r2.bucket_name,
                "prefix": "warm/",
            },
            StorageTier.COLD: {
                "provider": "cloudflare_r2",
                "config": self.cloudflare_r2.boto3_config,
                "bucket": self.cloudflare_r2.bucket_name,
                "prefix": "cold/",
            },
            StorageTier.ARCHIVE: {
                "provider": "cloudflare_r2",
                "config": self.cloudflare_r2.boto3_config,
                "bucket": self.cloudflare_r2.bucket_name,
                "prefix": "archive/",
            },
        }
        return configs.get(tier, configs[StorageTier.HOT])
    
    def get_media_generation_config(self) -> Dict[str, str]:
        """Get media generation service configurations."""
        return {
            "stability_api_key": settings.STABILITY_API_KEY,
            "replicate_api_token": settings.REPLICATE_API_TOKEN,
            "fal_api_key": settings.FAL_API_KEY,
        }
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return settings.MAX_FILE_SIZE_MB * 1024 * 1024


# Global storage configuration
storage_config = StorageConfig()