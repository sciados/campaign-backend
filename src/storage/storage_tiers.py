# src/storage/storage_tiers.py - NEW FILE
"""
Storage tier configuration and constants
"""

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

def is_content_type_allowed(content_type: str, tier: str) -> bool:
    """Check if content type is allowed for the tier"""
    tier_info = get_tier_info(tier)
    category = get_content_category(content_type)
    return category in tier_info["allowed_types"]

def is_file_size_allowed(file_size_bytes: int, tier: str) -> bool:
    """Check if file size is allowed for the tier"""
    tier_info = get_tier_info(tier)
    return file_size_bytes <= tier_info["max_file_size_bytes"]

def get_available_tiers() -> list:
    """Get list of available tier names"""
    return list(STORAGE_TIERS.keys())

def calculate_tier_upgrade_cost(current_tier: str, target_tier: str) -> float:
    """Calculate pro-rated upgrade cost"""
    current_info = get_tier_info(current_tier)
    target_info = get_tier_info(target_tier)
    
    return target_info["price_monthly"] - current_info["price_monthly"]

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