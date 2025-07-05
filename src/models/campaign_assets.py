# src/models/campaign_assets.py - FIXED VERSION
"""
Campaign Assets models for file uploads and asset management - FIXED VERSION
"""

import json
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

# EMERGENCY FIX: Create BaseModel locally to avoid circular imports
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4

Base = declarative_base()

class BaseModel(Base):
    """Emergency base model to avoid circular imports"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class AssetType(str, enum.Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    PDF = "pdf"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    ARCHIVE = "archive"
    OTHER = "other"

class AssetStatus(str, enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    DELETED = "deleted"

class CampaignAsset(BaseModel):
    """Campaign asset model for file uploads and asset management"""
    __tablename__ = "campaign_assets"
    
    # Basic Asset Information
    asset_name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    asset_type = Column(String(50), nullable=False, default=AssetType.OTHER.value)
    mime_type = Column(String(100))
    
    # File Details
    file_url = Column(Text, nullable=False)  # Storage URL (S3, etc.)
    file_path = Column(Text)  # Internal file path
    file_size = Column(Integer)  # Size in bytes
    file_hash = Column(String(255))  # File hash for deduplication
    
    # Asset Status and Processing
    status = Column(String(50), default=AssetStatus.READY.value)
    processing_status = Column(String(50))  # upload progress, processing state
    error_message = Column(Text)  # Error details if processing failed
    
    # Metadata and Properties - FIXED: Proper JSONB column definitions
    asset_metadata = Column(JSONB, default={})  # AI analysis metadata
    tags = Column(JSONB, default={})  # User-defined tags
    description = Column(Text)  # Asset description
    
    # Usage and Analytics
    download_count = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True))
    is_public = Column(Boolean, default=False)
    
    # Organization
    folder_path = Column(String(500))  # Virtual folder organization
    sort_order = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    
    # Processing Results (for AI analysis)
    extracted_text = Column(Text)  # OCR or document text extraction
    ai_analysis = Column(JSONB, default={})  # AI-generated insights about the asset
    thumbnail_url = Column(Text)  # Generated thumbnail URL
    
    # Foreign Keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # EMERGENCY FIX: Remove relationships to avoid circular imports
    # Relationships will be defined elsewhere if needed
    
    def __repr__(self):
        return f"<CampaignAsset(id={self.id}, name='{self.asset_name}', type='{self.asset_type}')>"
    
    @property
    def file_size_mb(self):
        """Return file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    @property
    def is_image(self):
        """Check if asset is an image"""
        return self.asset_type == AssetType.IMAGE.value
    
    @property
    def is_document(self):
        """Check if asset is a document"""
        return self.asset_type in [AssetType.DOCUMENT.value, AssetType.PDF.value, 
                                  AssetType.SPREADSHEET.value, AssetType.PRESENTATION.value]
    
    @property
    def is_media(self):
        """Check if asset is video or audio"""
        return self.asset_type in [AssetType.VIDEO.value, AssetType.AUDIO.value]
    
    def get_asset_metadata(self) -> dict:
        """Get asset metadata with proper handling"""
        if isinstance(self.asset_metadata, dict):
            return self.asset_metadata
        elif isinstance(self.asset_metadata, str):
            try:
                return json.loads(self.asset_metadata)
            except (json.JSONDecodeError, ValueError):
                return {}
        return {}
    
    def get_tags(self) -> dict:
        """Get tags with proper handling"""
        if isinstance(self.tags, dict):
            return self.tags
        elif isinstance(self.tags, str):
            try:
                return json.loads(self.tags)
            except (json.JSONDecodeError, ValueError):
                return {}
        return {}
    
    def get_ai_analysis(self) -> dict:
        """Get AI analysis with proper handling"""
        if isinstance(self.ai_analysis, dict):
            return self.ai_analysis
        elif isinstance(self.ai_analysis, str):
            try:
                return json.loads(self.ai_analysis)
            except (json.JSONDecodeError, ValueError):
                return {}
        return {}

# Utility functions for asset management
def get_asset_type_from_extension(filename: str) -> AssetType:
    """Determine asset type from file extension"""
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'tiff']
    video_extensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv']
    audio_extensions = ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg']
    document_extensions = ['txt', 'rtf', 'doc', 'docx']
    pdf_extensions = ['pdf']
    spreadsheet_extensions = ['xls', 'xlsx', 'csv']
    presentation_extensions = ['ppt', 'pptx']
    archive_extensions = ['zip', 'rar', '7z', 'tar', 'gz']
    
    if extension in image_extensions:
        return AssetType.IMAGE
    elif extension in video_extensions:
        return AssetType.VIDEO
    elif extension in audio_extensions:
        return AssetType.AUDIO
    elif extension in document_extensions:
        return AssetType.DOCUMENT
    elif extension in pdf_extensions:
        return AssetType.PDF
    elif extension in spreadsheet_extensions:
        return AssetType.SPREADSHEET
    elif extension in presentation_extensions:
        return AssetType.PRESENTATION
    elif extension in archive_extensions:
        return AssetType.ARCHIVE
    else:
        return AssetType.OTHER

def validate_file_size(file_size: int, max_size_mb: int = 100) -> bool:
    """Validate file size against maximum allowed size"""
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes

def generate_file_hash(file_content: bytes) -> str:
    """Generate SHA-256 hash of file content for deduplication"""
    import hashlib
    return hashlib.sha256(file_content).hexdigest()

def get_allowed_extensions() -> dict:
    """Get dictionary of allowed file extensions by category"""
    return {
        'images': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp'],
        'documents': ['pdf', 'doc', 'docx', 'txt', 'rtf'],
        'spreadsheets': ['xls', 'xlsx', 'csv'],
        'presentations': ['ppt', 'pptx'],
        'videos': ['mp4', 'avi', 'mov', 'wmv', 'webm'],
        'audio': ['mp3', 'wav', 'flac', 'aac', 'm4a'],
        'archives': ['zip', 'rar', '7z', 'tar']
    }