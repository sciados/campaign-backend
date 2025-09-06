# src/utils/json_utils.py - JSON Serialization Utilities
"""
JSON Utilities for handling datetime serialization
🔧 CRITICAL FIX: Centralized solution for "datetime is not JSON serializable" errors
"""
import json
from datetime import datetime, date, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

def json_serial(obj: Any) -> str:
    """
    JSON serializer for objects not serializable by default json code
    
    🔧 CRITICAL FIX: Handles datetime, date, timedelta, Decimal, and Enum objects
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, timedelta):
        return str(obj)
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, '__dict__'):
        # For objects with __dict__, convert to dict
        return obj.__dict__
    
    raise TypeError(f"Type {type(obj)} not serializable")

def safe_json_dumps(data: Any, **kwargs) -> str:
    """
    Safely serialize data to JSON string with datetime support
    
    Args:
        data: Data to serialize
        **kwargs: Additional arguments for json.dumps
    
    Returns:
        JSON string
    """
    try:
        # 🔧 FIXED: Removed circular import - use json_serial directly
        return json.dumps(data, default=json_serial, **kwargs)
    except Exception as e:
        logger.error(f"❌ JSON serialization failed: {str(e)}")
        # Fallback to string representation
        return json.dumps({"error": "Serialization failed", "data": str(data)})

def safe_json_loads(json_str: str) -> Any:
    """
    Safely deserialize JSON string to Python object
    
    Args:
        json_str: JSON string to deserialize
    
    Returns:
        Python object or None if parsing fails
    """
    try:
        if not json_str or json_str == "{}":
            return {}
        return json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"⚠️ JSON deserialization failed: {str(e)}")
        return {}

def serialize_for_api(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize data for API response, ensuring all datetime objects are strings
    
    Args:
        data: Dictionary to serialize
    
    Returns:
        Serialized dictionary safe for JSON
    """
    try:
        # Convert the entire dict to JSON and back to handle nested datetime objects
        json_str = safe_json_dumps(data)
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"❌ API serialization failed: {str(e)}")
        return {"error": "Serialization failed"}

def serialize_metadata(metadata: Dict[str, Any]) -> str:
    """
    Serialize metadata dictionary to JSON string for database storage
    
    Args:
        metadata: Metadata dictionary
    
    Returns:
        JSON string safe for database storage
    """
    if not metadata:
        return "{}"
    
    # Add timestamp if not present
    if "serialized_at" not in metadata:
        metadata["serialized_at"] = datetime.now().isoformat()
    
    return safe_json_dumps(metadata)

def deserialize_metadata(metadata_str: str) -> Dict[str, Any]:
    """
    Deserialize metadata JSON string from database
    
    Args:
        metadata_str: JSON string from database
    
    Returns:
        Metadata dictionary
    """
    return safe_json_loads(metadata_str)

# 🔧 CRITICAL FIX: Custom JSON encoder class for use with FastAPI
class DateTimeJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles datetime objects
    Can be used with FastAPI's jsonable_encoder or directly with json.dumps
    """
    
    def default(self, obj: Any) -> Any:
        try:
            return json_serial(obj)
        except TypeError:
            return super().default(obj)

# 🔧 CRITICAL FIX: FastAPI compatible encoder function
def jsonable_encoder_with_datetime(obj: Any) -> Any:
    """
    FastAPI compatible encoder that handles datetime objects
    
    This can be used as a drop-in replacement for FastAPI's jsonable_encoder
    when you need datetime support
    """
    try:
        from fastapi.encoders import jsonable_encoder
        # Convert datetime objects first, then use FastAPI's encoder
        json_str = safe_json_dumps(obj)
        parsed_obj = json.loads(json_str)
        return jsonable_encoder(parsed_obj)
    except ImportError:
        # Fallback if FastAPI not available
        return serialize_for_api(obj)

# 🔧 CRITICAL FIX: SQLAlchemy model serialization helper
def serialize_sqlalchemy_model(model_instance: Any, exclude_fields: list = None) -> Dict[str, Any]:
    """
    Serialize SQLAlchemy model instance to dictionary
    
    Args:
        model_instance: SQLAlchemy model instance
        exclude_fields: List of field names to exclude
    
    Returns:
        Dictionary representation of the model
    """
    if exclude_fields is None:
        exclude_fields = []
    
    try:
        result = {}
        
        # Get all columns from the model
        for column in model_instance.__table__.columns:
            field_name = column.name
            if field_name not in exclude_fields:
                field_value = getattr(model_instance, field_name)
                
                # Handle different types
                if isinstance(field_value, (datetime, date)):
                    result[field_name] = field_value.isoformat()
                elif isinstance(field_value, timedelta):
                    result[field_name] = str(field_value)
                elif isinstance(field_value, Decimal):
                    result[field_name] = float(field_value)
                elif isinstance(field_value, Enum):
                    result[field_name] = field_value.value
                else:
                    result[field_name] = field_value
        
        return result
        
    except Exception as e:
        logger.error(f"❌ SQLAlchemy model serialization failed: {str(e)}")
        return {"error": "Model serialization failed", "model": str(model_instance)}

# 🔧 CRITICAL FIX: Error response helper
def create_error_response(error_message: str, error_code: str = "SERIALIZATION_ERROR") -> Dict[str, Any]:
    """
    Create standardized error response with proper datetime serialization
    
    Args:
        error_message: Human readable error message
        error_code: Machine readable error code
    
    Returns:
        Error response dictionary
    """
    return {
        "error": True,
        "error_code": error_code,
        "error_message": error_message,
        "timestamp": datetime.now().isoformat(),
        "success": False
    }

# 🔧 CRITICAL FIX: Success response helper
def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """
    Create standardized success response with proper datetime serialization
    
    Args:
        data: Response data
        message: Success message
    
    Returns:
        Success response dictionary
    """
    response = {
        "success": True,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    # Ensure the entire response is JSON serializable
    return serialize_for_api(response)