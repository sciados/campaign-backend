# src/models/campaign_assets.py - FIXED VERSION to resolve registry conflicts
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
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

class AssetStatus(Enum):
    READY = "ready"
    PROCESSING = "processing"
    FAILED = "failed"
    ARCHIVED = "archived"

class CampaignAsset(BaseModel):
    """Enhanced campaign asset model with dual storage support"""
    
    # ✅ FIXED: Remove conflicting parameters
    __tablename__ = "campaign_assets"
    __table_args__ = {
        'extend_existing': True,  # Allow extending existing table definition
        # ❌ REMOVED: 'keep_existing': True - this conflicts with extend_existing
    }
    
    # campaign = relationship("src.models.campaign.Campaign", back_populates="assets")
    # uploader = relationship("src.models.user.User", back_populates="uploaded_assets")
    # company = relationship("src.models.company.Company", back_populates="assets")

    # Basic asset information
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # File information
    asset_name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    asset_type = Column(String(20), nullable=False)  # AssetType enum
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Legacy single storage (for backward compatibility)
    file_url = Column(Text, nullable=True)
    
    # ✅ NEW: Enhanced dual storage URLs
    file_url_primary = Column(Text, nullable=True)      # Cloudflare R2
    file_url_backup = Column(Text, nullable=True)       # Backblaze B2
    
    # ✅ NEW: Storage management fields
    storage_status = Column(String(20), default=StorageStatus.PENDING.value)    # StorageStatus enum
    active_provider = Column(String(50), default="cloudflare_r2")               # Current serving provider
    content_category = Column(String(20), default=ContentCategory.USER_UPLOADED.value)  # ContentCategory enum
    failover_count = Column(Integer, default=0)                                 # Track failover events
    
    # Metadata and tags
    asset_metadata = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    description = Column(Text, nullable=True)
    
    # Status and timestamps
    status = Column(String(20), default=AssetStatus.READY.value)  # Use enum value
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
        return self.storage_status == StorageStatus.FULLY_SYNCED.value
    
    def is_ai_generated(self) -> bool:
        """Check if asset is AI generated"""
        return self.content_category == ContentCategory.AI_GENERATED.value
    
    def update_access_stats(self):
        """Update access statistics"""
        self.access_count += 1
        self.last_accessed = func.now()

    def set_status(self, new_status: str):
        """Safely set status if valid"""
        if new_status in [status.value for status in AssetStatus]:
            self.status = new_status
        else:
            raise ValueError(f"Invalid status: {new_status}. Valid options: {[s.value for s in AssetStatus]}")
    
    def set_storage_status(self, new_status: str):
        """Safely set storage status if valid"""
        if new_status in [status.value for status in StorageStatus]:
            self.storage_status = new_status
        else:
            raise ValueError(f"Invalid storage status: {new_status}. Valid options: {[s.value for s in StorageStatus]}")
    
    def set_content_category(self, new_category: str):
        """Safely set content category if valid"""
        if new_category in [cat.value for cat in ContentCategory]:
            self.content_category = new_category
        else:
            raise ValueError(f"Invalid content category: {new_category}. Valid options: {[c.value for c in ContentCategory]}")

# Utility functions for asset management
def get_asset_type_from_extension(filename: str) -> str:
    """Get asset type from file extension"""
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp']
    video_extensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv']
    audio_extensions = ['mp3', 'wav', 'aac', 'ogg', 'flac', 'wma']
    document_extensions = ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx']
    
    if extension in image_extensions:
        return AssetType.IMAGE.value
    elif extension in video_extensions:
        return AssetType.VIDEO.value
    elif extension in audio_extensions:
        return AssetType.AUDIO.value
    elif extension in document_extensions:
        return AssetType.DOCUMENT.value
    else:
        return AssetType.DOCUMENT.value  # Default fallback

def validate_file_size(file_size: int, asset_type: str) -> bool:
    """Validate file size based on asset type"""
    max_sizes = {
        AssetType.IMAGE.value: 10 * 1024 * 1024,      # 10MB
        AssetType.DOCUMENT.value: 50 * 1024 * 1024,   # 50MB
        AssetType.VIDEO.value: 200 * 1024 * 1024,     # 200MB
        AssetType.AUDIO.value: 100 * 1024 * 1024,     # 100MB
    }
    
    max_size = max_sizes.get(asset_type, 10 * 1024 * 1024)  # Default 10MB
    return file_size <= max_size

def generate_file_hash(content: bytes) -> str:
    """Generate MD5 hash for file content"""
    import hashlib
    return hashlib.md5(content).hexdigest()

def get_allowed_extensions() -> dict:
    """Get allowed file extensions by type"""
    return {
        AssetType.IMAGE.value: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp'],
        AssetType.VIDEO.value: ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'],
        AssetType.AUDIO.value: ['mp3', 'wav', 'aac', 'ogg', 'flac', 'wma'],
        AssetType.DOCUMENT.value: ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx', 'md']
    }

# Export all the necessary components
__all__ = [
    'CampaignAsset',
    'AssetType',
    'StorageStatus', 
    'ContentCategory',
    'AssetStatus',
    'get_asset_type_from_extension',
    'validate_file_size',
    'generate_file_hash',
    'get_allowed_extensions'
]