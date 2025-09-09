# ============================================================================
# src/storage/schemas/storage_schemas.py
# ============================================================================

"""
Storage API Schemas

Pydantic schemas for storage API requests and responses.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class FileUploadRequest(BaseModel):
    """Schema for file upload request"""
    model_config = ConfigDict(from_attributes=True)
    
    campaign_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    model_config = ConfigDict(from_attributes=True)
    
    success: bool
    file_id: Optional[str] = None
    file_path: Optional[str] = None
    public_url: Optional[str] = None
    size: Optional[int] = None
    content_category: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

class FileDownloadResponse(BaseModel):
    """Schema for file download response"""
    model_config = ConfigDict(from_attributes=True)
    
    success: bool
    file_data: Optional[bytes] = None
    content_type: Optional[str] = None
    filename: Optional[str] = None
    size: Optional[int] = None
    error: Optional[str] = None

class MediaGenerationType(str, Enum):
    """Media generation types"""
    IMAGES = "images"
    VIDEO = "video"
    SLIDESHOW = "slideshow"

class MediaGenerationRequest(BaseModel):
    """Schema for media generation request"""
    model_config = ConfigDict(from_attributes=True)
    
    campaign_id: str
    generation_type: MediaGenerationType
    platforms: Optional[List[str]] = ["instagram", "facebook"]
    items_per_platform: Optional[int] = 2
    video_preferences: Optional[Dict[str, Any]] = None
    image_file_ids: Optional[List[str]] = None

class MediaGenerationResponse(BaseModel):
    """Schema for media generation response"""
    model_config = ConfigDict(from_attributes=True)
    
    success: bool
    generation_type: str
    items_generated: Optional[int] = None
    items_stored: Optional[int] = None
    stored_files: Optional[List[Dict[str, Any]]] = None
    total_cost: Optional[float] = None
    generation_stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class StorageQuotaResponse(BaseModel):
    """Schema for storage quota response"""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str
    tier: str
    current_usage_bytes: int
    current_usage_mb: float
    tier_limit_bytes: int
    tier_limit_mb: float
    available_bytes: int
    available_mb: float
    usage_percentage: float
    status: str
    file_count: int
    deleted_files: int

class FileMetadata(BaseModel):
    """Schema for file metadata"""
    model_config = ConfigDict(from_attributes=True)
    
    file_id: str
    original_filename: str
    file_size: int
    file_size_mb: float
    content_type: str
    content_category: str
    upload_date: datetime
    last_accessed: Optional[datetime] = None
    access_count: int
    campaign_id: Optional[str] = None
    public_url: Optional[str] = None
    is_deleted: bool = False

class FileListResponse(BaseModel):
    """Schema for file list response"""
    model_config = ConfigDict(from_attributes=True)
    
    success: bool
    files: List[FileMetadata]
    pagination: Dict[str, Any]
    filters: Dict[str, Any]
    total_size_mb: Optional[float] = None

class StorageAnalyticsResponse(BaseModel):
    """Schema for storage analytics response"""
    model_config = ConfigDict(from_attributes=True)
    
    period: Dict[str, Any]
    summary: Dict[str, Any]
    daily_trends: List[Dict[str, Any]]
    popular_files: List[Dict[str, Any]]
    category_breakdown: Dict[str, Dict[str, Any]]