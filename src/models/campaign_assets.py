# src/models/campaign_assets.py - Enhanced version
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from enum import Enum
from uuid import uuid4

from src.models.base import BaseModel

class AssetType(Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"

class StorageStatus(Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    FULLY_SYNCED = "fully_synced"
    PRIMARY_ONLY = "primary_only"
    BACKUP_ONLY = "backup_only"
    FAILED = "failed"

class ContentCategory(Enum):
    AI_GENERATED = "ai_generated"
    USER_UPLOADED = "user_uploaded"
    SYSTEM_GENERATED = "system_generated"

class CampaignAsset(BaseModel):
    """Enhanced campaign asset model with dual storage support"""
    
    # Basic asset information
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id = Column(UUID(as_uuid=True), nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), nullable=False)
    company_id = Column(UUID(as_uuid=True), nullable=False)
    
    # File information
    asset_name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    asset_type = Column(String(20), nullable=False)  # AssetType enum
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Legacy single storage (for backward compatibility)
    file_url = Column(Text, nullable=True)
    
    # Enhanced dual storage URLs
    file_url_primary = Column(Text, nullable=True)      # Cloudflare R2
    file_url_backup = Column(Text, nullable=True)       # Backblaze B2
    
    # Storage management
    storage_status = Column(String(20), default="pending")           # StorageStatus enum
    active_provider = Column(String(50), default="cloudflare_r2")    # Current serving provider
    content_category = Column(String(20), default="user_uploaded")   # ContentCategory enum
    failover_count = Column(Integer, default=0)                      # Track failover events
    
    # Metadata and tags
    asset_metadata = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    description = Column(Text, nullable=True)
    
    # Status and timestamps
    status = Column(String(20), default="ready")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Additional tracking
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    access_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<CampaignAsset {self.asset_name} ({self.asset_type})>"
    
    def get_serving_url(self) -> str:
        """Get the appropriate serving URL based on active provider"""
        if self.active_provider == "cloudflare_r2" and self.file_url_primary:
            return self.file_url_primary
        elif self.active_provider == "backblaze_b2" and self.file_url_backup:
            return self.file_url_backup
        elif self.file_url_primary:
            return self.file_url_primary
        elif self.file_url_backup:
            return self.file_url_backup
        else:
            return self.file_url  # Legacy fallback
    
    def is_fully_synced(self) -> bool:
        """Check if asset is fully synced across both providers"""
        return self.storage_status == "fully_synced"
    
    def is_ai_generated(self) -> bool:
        """Check if asset is AI generated"""
        return self.content_category == "ai_generated"
    
    def update_access_stats(self):
        """Update access statistics"""
        self.access_count += 1
        self.last_accessed = func.now()