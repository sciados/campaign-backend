# ============================================================================
# src/storage/utils/file_helpers.py
# ============================================================================

"""
File Processing Utilities

Helper functions for file validation, processing, and metadata extraction.
"""

import hashlib
import mimetypes
import re
import os
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

def validate_file_type(
    filename: str, 
    content_type: str,
    allowed_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Validate file type and extension"""
    
    if allowed_types is None:
        allowed_types = [
            # Images
            "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml",
            # Videos
            "video/mp4", "video/avi", "video/mov", "video/wmv", "video/webm",
            # Documents
            "application/pdf", "application/msword", "text/plain", "text/csv",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            # Audio
            "audio/mpeg", "audio/wav", "audio/ogg"
        ]
    
    # Get file extension
    file_ext = get_file_extension(filename).lower()
    
    # Check content type
    is_allowed_type = content_type in allowed_types
    
    # Get expected content type from extension
    expected_type, _ = mimetypes.guess_type(filename)
    
    # Check if content type matches extension
    type_matches_extension = content_type == expected_type
    
    return {
        "is_valid": is_allowed_type and type_matches_extension,
        "filename": filename,
        "content_type": content_type,
        "file_extension": file_ext,
        "expected_content_type": expected_type,
        "is_allowed_type": is_allowed_type,
        "type_matches_extension": type_matches_extension,
        "validation_errors": _get_validation_errors(
            is_allowed_type, type_matches_extension, content_type, expected_type
        )
    }

def _get_validation_errors(
    is_allowed_type: bool,
    type_matches_extension: bool, 
    content_type: str,
    expected_type: str
) -> List[str]:
    """Get validation error messages"""
    errors = []
    
    if not is_allowed_type:
        errors.append(f"File type '{content_type}' is not allowed")
    
    if not type_matches_extension:
        errors.append(f"Content type '{content_type}' does not match expected type '{expected_type}'")
    
    return errors

def calculate_file_hash(file_data: bytes, algorithm: str = "sha256") -> str:
    """Calculate hash of file data"""
    
    if algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    elif algorithm == "sha256":
        hasher = hashlib.sha256()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    hasher.update(file_data)
    return hasher.hexdigest()

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix

def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """Sanitize filename for safe storage"""
    
    # Remove/replace unsafe characters
    sanitized = re.sub(r'[^\w\s.-]', '_', filename)
    
    # Replace spaces with underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Trim length if necessary
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        max_name_length = max_length - len(ext)
        sanitized = name[:max_name_length] + ext
    
    return sanitized.strip('_')

def get_content_type(filename: str) -> str:
    """Get content type from filename"""
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or "application/octet-stream"

def extract_file_info(filename: str, file_data: bytes) -> Dict[str, Any]:
    """Extract comprehensive file information"""
    
    file_size = len(file_data)
    file_hash = calculate_file_hash(file_data)
    content_type = get_content_type(filename)
    extension = get_file_extension(filename)
    sanitized_name = sanitize_filename(filename)
    
    return {
        "original_filename": filename,
        "sanitized_filename": sanitized_name,
        "file_size": file_size,
        "file_size_mb": round(file_size / 1024 / 1024, 2),
        "content_type": content_type,
        "file_extension": extension,
        "file_hash": file_hash,
        "content_category": _determine_content_category(content_type)
    }

def _determine_content_category(content_type: str) -> str:
    """Determine content category from MIME type"""
    if content_type.startswith('image/'):
        return 'image'
    elif content_type.startswith('video/'):
        return 'video'
    elif content_type.startswith('audio/'):
        return 'audio'
    elif content_type in ['application/pdf', 'application/msword', 'text/plain', 'text/csv']:
        return 'document'
    else:
        return 'other'

def validate_file_upload(
    filename: str,
    file_data: bytes,
    max_size: int = 100 * 1024 * 1024,  # 100MB default
    allowed_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Comprehensive file upload validation"""
    
    file_info = extract_file_info(filename, file_data)
    type_validation = validate_file_type(filename, file_info["content_type"], allowed_types)
    
    # Size validation
    size_valid = file_info["file_size"] <= max_size
    
    # Overall validation
    is_valid = type_validation["is_valid"] and size_valid
    
    validation_errors = type_validation["validation_errors"].copy()
    if not size_valid:
        validation_errors.append(f"File size {file_info['file_size_mb']}MB exceeds limit of {max_size / 1024 / 1024}MB")
    
    return {
        "is_valid": is_valid,
        "file_info": file_info,
        "type_validation": type_validation,
        "size_valid": size_valid,
        "validation_errors": validation_errors
    }