# src/models/user_storage.py - FINAL FIXED VERSION - Remove back references
"""
User storage usage tracking model - FIXED: No circular imports + no back references
"""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

from src.utils.json_utils import safe_json_dumps, serialize_metadata

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

# Only import for type hints to avoid circular imports
if TYPE_CHECKING:
    from .campaign import Campaign
    from .user import User

from .base import BaseModel

class UserStorageUsage(BaseModel):
    """Track individual file storage usage per user"""
    __tablename__ = "user_storage_usage"
    
    # User relationship
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # File information
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)  # R2 object key
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # Size in bytes
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)  # MIME type
    
    # Organization
    content_category: Mapped[str] = mapped_column(String(50), nullable=False)  # image, document, video
    campaign_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    
    # Metadata
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_accessed: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    access_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Status
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Additional file metadata (JSON for extensibility) - RENAMED TO AVOID CONFLICT
    file_metadata: Mapped[Optional[str]] = mapped_column("file_metadata", Text, nullable=True)  # JSON string storage
    
    # RELATIONSHIPS REMOVED - No back references to avoid relationship errors
    user: Mapped["User"] = relationship("User", back_populates="storage_usage")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="storage_files")
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        return round(self.file_size / 1024 / 1024, 2)
    
    @property
    def file_size_kb(self) -> float:
        """Get file size in KB"""
        return round(self.file_size / 1024, 2)
    
    @property
    def is_image(self) -> bool:
        """Check if file is an image"""
        return self.content_category == "image" or self.content_type.startswith("image/")
    
    @property
    def is_document(self) -> bool:
        """Check if file is a document"""
        return self.content_category == "document" or self.content_type in [
            "application/pdf", "application/msword", 
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
    
    @property
    def is_video(self) -> bool:
        """Check if file is a video"""
        return self.content_category == "video" or self.content_type.startswith("video/")
    
    # ==============================================================================
# 🔧 UPDATED METHODS: Using centralized JSON utilities
# ==============================================================================

def get_file_metadata(self) -> dict:
    """
    Get file metadata as dict using centralized JSON utilities
    
    🔧 IMPROVEMENT: Uses safe_json_loads for better error handling
    """
    if not self.file_metadata:
        return {}
    
    if isinstance(self.file_metadata, dict):
        return self.file_metadata
    elif isinstance(self.file_metadata, str):
        return safe_json_dumps(self.file_metadata)
    else:
        return {}

def set_file_metadata(self, metadata_dict: dict):
    """
    Set file metadata from dict using centralized JSON utilities
    
    🔧 IMPROVEMENT: Uses safe_json_dumps for datetime support and better error handling
    """
    if not metadata_dict:
        self.file_metadata = None
    else:
        # Use the centralized serialize_metadata function which adds timestamp
        self.file_metadata = serialize_metadata(metadata_dict)
    
    def mark_accessed(self):
        """Mark file as accessed (update access count and timestamp)"""
        self.last_accessed = datetime.now(timezone.utc)
        self.access_count += 1
    
    def soft_delete(self):
        """Soft delete the file record"""
        self.is_deleted = True
        self.deleted_date = datetime.now(timezone.utc)
    
    def __repr__(self):
        return f"<UserStorageUsage(id={self.id}, user_id={self.user_id}, filename='{self.original_filename}', size={self.file_size_mb}MB)>"
    
# ============================================================================
# Pydantic Schemas for CRUD Operations
# ============================================================================

class UserStorageBase(BaseModel):
    """Base schema for user storage"""
    original_filename: str = Field(..., min_length=1, max_length=255)
    file_size: int = Field(..., gt=0, description="File size in bytes")
    content_type: str = Field(..., min_length=1, max_length=100)
    content_category: str = Field(..., regex="^(image|document|video)$")
    campaign_id: Optional[str] = Field(None, description="Associated campaign ID")
    file_metadata: Optional[str] = Field(None, description="JSON metadata string")
    
    @validator('file_size')
    def validate_file_size(cls, v):
        """Validate file size is reasonable"""
        if v <= 0:
            raise ValueError('File size must be positive')
        if v > 500 * 1024 * 1024:  # 500MB max
            raise ValueError('File size exceeds maximum allowed (500MB)')
        return v
    
    @validator('content_category')
    def validate_content_category(cls, v):
        """Validate content category"""
        allowed_categories = ['image', 'document', 'video']
        if v not in allowed_categories:
            raise ValueError(f'Content category must be one of: {allowed_categories}')
        return v
    
    @validator('original_filename')
    def validate_filename(cls, v):
        """Validate filename"""
        if not v or v.strip() == '':
            raise ValueError('Filename cannot be empty')
        
        # Remove path traversal attempts
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError('Filename contains invalid characters')
        
        return v.strip()

class UserStorageCreate(UserStorageBase):
    """Schema for creating storage records"""
    user_id: str = Field(..., description="User ID who owns the file")
    file_path: str = Field(..., min_length=1, max_length=500, description="Storage path")
    upload_date: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('file_path')
    def validate_file_path(cls, v):
        """Validate file path"""
        if not v or v.strip() == '':
            raise ValueError('File path cannot be empty')
        return v.strip()

class UserStorageUpdate(BaseModel):
    """Schema for updating storage records"""
    original_filename: Optional[str] = Field(None, min_length=1, max_length=255)
    last_accessed: Optional[datetime] = None
    access_count: Optional[int] = Field(None, ge=0)
    is_deleted: Optional[bool] = None
    deleted_date: Optional[datetime] = None
    file_metadata: Optional[str] = None
    
    @validator('original_filename')
    def validate_filename(cls, v):
        """Validate filename if provided"""
        if v is not None:
            if not v or v.strip() == '':
                raise ValueError('Filename cannot be empty')
            if '..' in v or '/' in v or '\\' in v:
                raise ValueError('Filename contains invalid characters')
            return v.strip()
        return v

class UserStorageResponse(UserStorageBase):
    """Schema for storage record responses"""
    id: str
    user_id: str
    file_path: str
    upload_date: datetime
    last_accessed: Optional[datetime] = None
    deleted_date: Optional[datetime] = None
    access_count: int
    is_deleted: bool
    file_size_mb: float
    file_size_kb: float
    
class Config:
    from_attributes = True  # For Pydantic v2 compatibility