# src/content/utils/content_utils.py
"""
Content utility functions
"""

from typing import Optional
from src.content.models import ContentType

def extract_content_type(content_type: Optional[str]) -> Optional[str]:
    """
    Extract content type from request
    
    Args:
        content_type: Raw content type string
        
    Returns:
        Normalized content type or None if invalid
    """
    if not content_type:
        return None
        
    # Clean up the content type
    cleaned_type = content_type.strip().lower()
    
    # Map to our content type enum
    content_type_mapping = {
        "blog": "blog",
        "social": "social",
        "image": "image",
        "video": "video",
        "long_form": "long_form",
        "multi_platform_image": "multi_platform_image"
    }
    
    return content_type_mapping.get(cleaned_type, None)

def validate_content_type(content_type: Optional[str]) -> bool:
    """
    Validate if content type is supported
    
    Args:
        content_type: Content type string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not content_type:
        return False
        
    # Get normalized content type
    normalized_type = extract_content_type(content_type)
    
    # Check if it's in our supported types
    return normalized_type in [
        "blog", "social", "image", "video", 
        "long_form", "multi_platform_image"
    ]

def determine_content_type(
    requested_type: Optional[str],
    content_spec: Optional[str]
) -> str:
    """
    Determine content type based on request data
    
    Args:
        requested_type: Requested content type
        content_spec: Content specification
        
    Returns:
        str: Determined content type
    """
    # If type is already specified, use it
    if requested_type:
        return requested_type
    
    # If content_spec contains image-related terms, use image
    if content_spec and any(term in content_spec.lower() for term in ["image", "photo", "graphic", "visual"]):
        return "image"
    
    # If content_spec contains video-related terms, use video
    if content_spec and any(term in content_spec.lower() for term in ["video", "clip", "film", "youtube"]):
        return "video"
    
    # If content_spec contains social media terms, use social
    if content_spec and any(term in content_spec.lower() for term in ["social", "post", "twitter", "instagram"]):
        return "social"
    
    # Default to blog
    return "blog"