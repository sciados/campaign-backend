# src/models/user_storage.py - FINAL FIXED VERSION - Remove back references
"""
User storage usage tracking model - FIXED: No circular imports + no back references
"""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import Optional, TYPE_CHECKING

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
    
    def get_file_metadata(self) -> dict:
        """Get file metadata as dict"""
        if not self.file_metadata:
            return {}
        try:
            import json
            return json.loads(self.file_metadata) if isinstance(self.file_metadata, str) else {}
        except (json.JSONDecodeError, ValueError):
            return {}
    
    def set_file_metadata(self, metadata_dict: dict):
        """Set file metadata from dict"""
        import json
        self.file_metadata = json.dumps(metadata_dict) if metadata_dict else None
    
    def mark_accessed(self):
        """Mark file as accessed (update access count and timestamp)"""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
    
    def soft_delete(self):
        """Soft delete the file record"""
        self.is_deleted = True
        self.deleted_date = datetime.utcnow()
    
    def __repr__(self):
        return f"<UserStorageUsage(id={self.id}, user_id={self.user_id}, filename='{self.original_filename}', size={self.file_size_mb}MB)>"