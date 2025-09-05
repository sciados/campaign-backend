# =====================================
# File: src/core/shared/validators.py
# =====================================

"""
Common validation utilities for CampaignForge.

Provides input validation, sanitization, and type checking
functions used across all modules.
"""

import re
import uuid
from typing import Any, Optional
from urllib.parse import urlparse
import bleach
from email_validator import validate_email as _validate_email, EmailNotValidError

from .exceptions import ValidationError


def validate_uuid(value: Any, field_name: str = "id") -> str:
    """
    Validate and return a UUID string.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error reporting
        
    Returns:
        str: Valid UUID string
        
    Raises:
        ValidationError: If value is not a valid UUID
    """
    if not value:
        raise ValidationError(f"{field_name} is required", field=field_name)
    
    try:
        # Convert to string and validate
        uuid_str = str(value)
        uuid.UUID(uuid_str)
        return uuid_str
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid UUID", field=field_name)


def validate_email(email: Any, field_name: str = "email") -> str:
    """
    Validate and return a normalized email address.
    
    Args:
        email: Email to validate
        field_name: Name of the field for error reporting
        
    Returns:
        str: Valid, normalized email address
        
    Raises:
        ValidationError: If email is not valid
    """
    if not email:
        raise ValidationError(f"{field_name} is required", field=field_name)
    
    try:
        # Use email-validator library for comprehensive validation
        validation_result = _validate_email(str(email))
        return validation_result.email
    except EmailNotValidError as e:
        raise ValidationError(f"Invalid {field_name}: {str(e)}", field=field_name)


def validate_url(url: Any, field_name: str = "url", schemes: tuple = ("http", "https")) -> str:
    """
    Validate and return a URL.
    
    Args:
        url: URL to validate
        field_name: Name of the field for error reporting
        schemes: Allowed URL schemes
        
    Returns:
        str: Valid URL
        
    Raises:
        ValidationError: If URL is not valid
    """
    if not url:
        raise ValidationError(f"{field_name} is required", field=field_name)
    
    try:
        url_str = str(url).strip()
        parsed = urlparse(url_str)
        
        if not parsed.scheme:
            raise ValidationError(f"{field_name} must include a scheme (http/https)", field=field_name)
        
        if parsed.scheme.lower() not in schemes:
            raise ValidationError(f"{field_name} must use one of: {', '.join(schemes)}", field=field_name)
        
        if not parsed.netloc:
            raise ValidationError(f"{field_name} must include a domain", field=field_name)
        
        return url_str
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid {field_name}: {str(e)}", field=field_name)


def sanitize_string(
    value: Any,
    field_name: str = "text",
    max_length: Optional[int] = None,
    allow_html: bool = False,
    allowed_tags: Optional[list] = None
) -> str:
    """
    Sanitize and validate a string input.
    
    Args:
        value: String to sanitize
        field_name: Name of the field for error reporting
        max_length: Maximum allowed length
        allow_html: Whether to allow HTML tags
        allowed_tags: List of allowed HTML tags if allow_html is True
        
    Returns:
        str: Sanitized string
        
    Raises:
        ValidationError: If string is invalid
    """
    if value is None:
        return ""
    
    try:
        text = str(value).strip()
        
        # Check length
        if max_length and len(text) > max_length:
            raise ValidationError(
                f"{field_name} must be {max_length} characters or less",
                field=field_name
            )
        
        # Handle HTML
        if not allow_html:
            # Strip all HTML tags
            text = bleach.clean(text, tags=[], strip=True)
        elif allowed_tags:
            # Allow only specified tags
            text = bleach.clean(text, tags=allowed_tags, strip=True)
        
        return text
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid {field_name}: {str(e)}", field=field_name)


def validate_positive_integer(value: Any, field_name: str = "number") -> int:
    """
    Validate and return a positive integer.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error reporting
        
    Returns:
        int: Valid positive integer
        
    Raises:
        ValidationError: If value is not a positive integer
    """
    try:
        num = int(value)
        if num <= 0:
            raise ValidationError(f"{field_name} must be a positive integer", field=field_name)
        return num
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid integer", field=field_name)


def validate_json_data(value: Any, field_name: str = "data") -> dict:
    """
    Validate and return JSON data as a dictionary.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error reporting
        
    Returns:
        dict: Valid JSON data
        
    Raises:
        ValidationError: If value is not valid JSON data
    """
    if isinstance(value, dict):
        return value
    
    try:
        import json
        if isinstance(value, str):
            return json.loads(value)
        else:
            raise ValidationError(f"{field_name} must be a JSON object or dict", field=field_name)
    except (json.JSONDecodeError, TypeError) as e:
        raise ValidationError(f"Invalid {field_name}: {str(e)}", field=field_name)