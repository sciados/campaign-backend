# src/storage/storage_tiers.py - FIXED VERSION with StorageTier class
"""
Storage tier configuration and constants
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any

# 🔧 CRITICAL FIX: Add StorageTier enum class that generators expect
class StorageTier(Enum):
    """Storage tier enumeration"""
    free = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

# 🔧 ADDITIONAL: Add StorageTierInfo dataclass for structured tier information
@dataclass
class StorageTierInfo:
    """Structured storage tier information"""
    name: str
    limit_gb: int
    limit_bytes: int
    max_file_size_mb: int
    max_file_size_bytes: int
    allowed_types: List[str]
    monthly_uploads: int
    price_monthly: float
    features: List[str]
    
    @property
    def tier_enum(self) -> StorageTier:
        """Get the corresponding StorageTier enum"""
        tier_name = self.name.lower().replace(" tier", "").replace(" ", "_")
        for tier in StorageTier:
            if tier.value == tier_name or tier_name in tier.value:
                return tier
        return StorageTier.free

# Storage tier definitions
STORAGE_TIERS = {
    "free": {
        "name": "Free Tier",
        "limit_gb": 1,
        "limit_bytes": 1073741824,  # 1 GB
        "max_file_size_mb": 10,
        "max_file_size_bytes": 10485760,  # 10 MB
        "allowed_types": ["image", "document"],
        "monthly_uploads": 100,
        "price_monthly": 0,
        "features": [
            "1GB total storage",
            "Up to 10MB per file",
            "Images and documents only",
            "100 uploads per month"
        ]
    },
    "pro": {
        "name": "Pro Tier",
        "limit_gb": 10,
        "limit_bytes": 10737418240,  # 10 GB
        "max_file_size_mb": 50,
        "max_file_size_bytes": 52428800,  # 50 MB
        "allowed_types": ["image", "document", "video"],
        "monthly_uploads": 1000,
        "price_monthly": 9.99,
        "features": [
            "10GB total storage",
            "Up to 50MB per file",
            "Images, documents, and videos",
            "1,000 uploads per month",
            "Priority support"
        ]
    },
    "enterprise": {
        "name": "Enterprise Tier",
        "limit_gb": 100,
        "limit_bytes": 107374182400,  # 100 GB
        "max_file_size_mb": 200,
        "max_file_size_bytes": 209715200,  # 200 MB
        "allowed_types": ["image", "document", "video"],
        "monthly_uploads": -1,  # unlimited
        "price_monthly": 49.99,
        "features": [
            "100GB total storage",
            "Up to 200MB per file",
            "All file types supported",
            "Unlimited uploads",
            "Priority support",
            "Advanced analytics",
            "Custom integrations"
        ]
    }
}

# Content type mappings
CONTENT_TYPE_CATEGORIES = {
    # Images
    "image/jpeg": "image",
    "image/jpg": "image", 
    "image/png": "image",
    "image/gif": "image",
    "image/webp": "image",
    "image/svg+xml": "image",
    "image/bmp": "image",
    "image/tiff": "image",
    
    # Documents
    "application/pdf": "document",
    "application/msword": "document",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
    "application/vnd.ms-excel": "document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "document",
    "application/vnd.ms-powerpoint": "document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "document",
    "text/plain": "document",
    "text/csv": "document",
    "application/rtf": "document",
    
    # Videos
    "video/mp4": "video",
    "video/mpeg": "video",
    "video/quicktime": "video",
    "video/x-msvideo": "video",  # .avi
    "video/webm": "video",
    "video/ogg": "video"
}

def get_content_category(content_type: str) -> str:
    """Get content category from MIME type"""
    return CONTENT_TYPE_CATEGORIES.get(content_type.lower(), "document")

def get_tier_info(tier: str) -> dict:
    """Get tier information with fallback to free tier"""
    return STORAGE_TIERS.get(tier, STORAGE_TIERS["free"])

def get_tier_info_structured(tier: str) -> StorageTierInfo:
    """Get structured tier information"""
    tier_data = get_tier_info(tier)
    return StorageTierInfo(**tier_data)

def get_tier_info_by_enum(tier: StorageTier) -> dict:
    """Get tier information by StorageTier enum"""
    return get_tier_info(tier.value)

def get_tier_info_by_enum_structured(tier: StorageTier) -> StorageTierInfo:
    """Get structured tier information by StorageTier enum"""
    return get_tier_info_structured(tier.value)

def is_content_type_allowed(content_type: str, tier: str) -> bool:
    """Check if content type is allowed for the tier"""
    tier_info = get_tier_info(tier)
    category = get_content_category(content_type)
    return category in tier_info["allowed_types"]

def is_content_type_allowed_by_enum(content_type: str, tier: StorageTier) -> bool:
    """Check if content type is allowed for the tier by enum"""
    return is_content_type_allowed(content_type, tier.value)

def is_file_size_allowed(file_size_bytes: int, tier: str) -> bool:
    """Check if file size is allowed for the tier"""
    tier_info = get_tier_info(tier)
    return file_size_bytes <= tier_info["max_file_size_bytes"]

def is_file_size_allowed_by_enum(file_size_bytes: int, tier: StorageTier) -> bool:
    """Check if file size is allowed for the tier by enum"""
    return is_file_size_allowed(file_size_bytes, tier.value)

def get_available_tiers() -> list:
    """Get list of available tier names"""
    return list(STORAGE_TIERS.keys())

def get_available_tier_enums() -> List[StorageTier]:
    """Get list of available StorageTier enums"""
    return list(StorageTier)

def calculate_tier_upgrade_cost(current_tier: str, target_tier: str) -> float:
    """Calculate pro-rated upgrade cost"""
    current_info = get_tier_info(current_tier)
    target_info = get_tier_info(target_tier)
    
    return target_info["price_monthly"] - current_info["price_monthly"]

def calculate_tier_upgrade_cost_by_enum(current_tier: StorageTier, target_tier: StorageTier) -> float:
    """Calculate pro-rated upgrade cost by enum"""
    return calculate_tier_upgrade_cost(current_tier.value, target_tier.value)

# File extension to content type mapping (for fallback)
EXTENSION_TO_CONTENT_TYPE = {
    # Images
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
    
    # Documents
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".txt": "text/plain",
    ".csv": "text/csv",
    ".rtf": "application/rtf",
    
    # Videos
    ".mp4": "video/mp4",
    ".mpeg": "video/mpeg",
    ".mpg": "video/mpeg",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
    ".webm": "video/webm",
    ".ogg": "video/ogg"
}

def get_content_type_from_filename(filename: str) -> str:
    """Get content type from filename extension"""
    import os
    ext = os.path.splitext(filename.lower())[1]
    return EXTENSION_TO_CONTENT_TYPE.get(ext, "application/octet-stream")

# 🔧 UTILITY FUNCTIONS for storage tier management

def parse_tier_from_string(tier_string: str) -> StorageTier:
    """Parse StorageTier enum from string with fallback"""
    if not tier_string:
        return StorageTier.free
    
    tier_string = tier_string.lower().strip()
    
    for tier in StorageTier:
        if tier.value == tier_string or tier.name.lower() == tier_string:
            return tier
    
    # Fallback to free tier if not found
    return StorageTier.free

def get_user_tier_limits(tier: StorageTier) -> Dict[str, Any]:
    """Get comprehensive tier limits for a user"""
    tier_info = get_tier_info_by_enum(tier)
    
    return {
        "tier": tier.value,
        "tier_name": tier_info["name"],
        "storage_limit_bytes": tier_info["limit_bytes"],
        "storage_limit_gb": tier_info["limit_gb"],
        "max_file_size_bytes": tier_info["max_file_size_bytes"],
        "max_file_size_mb": tier_info["max_file_size_mb"],
        "allowed_content_types": tier_info["allowed_types"],
        "monthly_upload_limit": tier_info["monthly_uploads"],
        "unlimited_uploads": tier_info["monthly_uploads"] == -1,
        "monthly_cost": tier_info["price_monthly"],
        "features": tier_info["features"]
    }

def can_upload_file(
    tier: StorageTier,
    file_size_bytes: int,
    content_type: str,
    current_usage_bytes: int = 0,
    monthly_uploads_used: int = 0
) -> Dict[str, Any]:
    """Comprehensive check if a file can be uploaded"""
    
    tier_info = get_tier_info_by_enum(tier)
    
    # Check file size
    size_allowed = is_file_size_allowed_by_enum(file_size_bytes, tier)
    
    # Check content type
    content_allowed = is_content_type_allowed_by_enum(content_type, tier)
    
    # Check storage quota
    new_usage = current_usage_bytes + file_size_bytes
    storage_available = new_usage <= tier_info["limit_bytes"]
    
    # Check monthly upload limit
    monthly_limit = tier_info["monthly_uploads"]
    monthly_allowed = monthly_limit == -1 or monthly_uploads_used < monthly_limit
    
    can_upload = size_allowed and content_allowed and storage_available and monthly_allowed
    
    result = {
        "can_upload": can_upload,
        "tier": tier.value,
        "checks": {
            "file_size_allowed": size_allowed,
            "content_type_allowed": content_allowed,
            "storage_quota_available": storage_available,
            "monthly_uploads_available": monthly_allowed
        },
        "limits": {
            "max_file_size_bytes": tier_info["max_file_size_bytes"],
            "max_file_size_mb": tier_info["max_file_size_mb"],
            "storage_limit_bytes": tier_info["limit_bytes"],
            "storage_limit_gb": tier_info["limit_gb"],
            "monthly_upload_limit": monthly_limit,
            "allowed_content_types": tier_info["allowed_types"]
        },
        "usage": {
            "current_storage_bytes": current_usage_bytes,
            "file_size_bytes": file_size_bytes,
            "new_total_bytes": new_usage,
            "monthly_uploads_used": monthly_uploads_used
        }
    }
    
    # Add specific error messages if upload not allowed
    if not can_upload:
        errors = []
        if not size_allowed:
            errors.append(f"File size ({file_size_bytes / 1024 / 1024:.1f}MB) exceeds limit ({tier_info['max_file_size_mb']}MB)")
        if not content_allowed:
            errors.append(f"Content type '{get_content_category(content_type)}' not allowed for {tier.value} tier")
        if not storage_available:
            remaining_gb = (tier_info["limit_bytes"] - current_usage_bytes) / 1024 / 1024 / 1024
            errors.append(f"Storage quota exceeded. Only {remaining_gb:.2f}GB remaining")
        if not monthly_allowed:
            errors.append(f"Monthly upload limit reached ({monthly_uploads_used}/{monthly_limit})")
        
        result["errors"] = errors
    
    return result

# 🔧 COMPATIBILITY FUNCTIONS for existing code

def get_tier_by_name(tier_name: str) -> StorageTier:
    """Get StorageTier enum by name (alias for parse_tier_from_string)"""
    return parse_tier_from_string(tier_name)

def get_default_tier() -> StorageTier:
    """Get default tier for new users"""
    return StorageTier.free

def get_tier_features(tier: StorageTier) -> List[str]:
    """Get features list for a tier"""
    tier_info = get_tier_info_by_enum(tier)
    return tier_info["features"]

def get_tier_price(tier: StorageTier) -> float:
    """Get monthly price for a tier"""
    tier_info = get_tier_info_by_enum(tier)
    return tier_info["price_monthly"]

# 🔧 EXPORT ALL for convenience
__all__ = [
    'StorageTier',
    'StorageTierInfo', 
    'STORAGE_TIERS',
    'CONTENT_TYPE_CATEGORIES',
    'EXTENSION_TO_CONTENT_TYPE',
    'get_content_category',
    'get_tier_info',
    'get_tier_info_structured',
    'get_tier_info_by_enum',
    'get_tier_info_by_enum_structured',
    'is_content_type_allowed',
    'is_content_type_allowed_by_enum',
    'is_file_size_allowed',
    'is_file_size_allowed_by_enum',
    'get_available_tiers',
    'get_available_tier_enums',
    'calculate_tier_upgrade_cost',
    'calculate_tier_upgrade_cost_by_enum',
    'get_content_type_from_filename',
    'parse_tier_from_string',
    'get_user_tier_limits',
    'can_upload_file',
    'get_tier_by_name',
    'get_default_tier',
    'get_tier_features',
    'get_tier_price'
]