# src/models/user_storage.py - FIXED: Pydantic v2 Compatibility
"""
User Storage Models with Pydantic v2 Compatibility
🔧 FIXED: Changed regex to pattern for Pydantic v2
✅ Complete storage tracking and quota management
📊 Enhanced analytics and reporting capabilities
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

from ...core.crud.base_crud import BaseModel as SQLModel

# ============================================================================
# SQLAlchemy Model
# ============================================================================

class UserStorageUsage(SQLModel):
    """
    User Storage Usage tracking model
    Tracks all file uploads, storage usage, and analytics
    """
    __tablename__ = "user_storage_usage"
    
    # Core identification
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    
    # File information
    file_path = Column(String, nullable=False, unique=True)  # Unique storage path
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    content_type = Column(String, nullable=False)
    content_category = Column(String, nullable=False, index=True)  # image, document, video
    
    # Organization
    campaign_id = Column(String, ForeignKey('campaigns.id'), nullable=True, index=True)
    
    # Timestamps
    upload_date = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    deleted_date = Column(DateTime(timezone=True), nullable=True)
    
    # File lifecycle
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    access_count = Column(Integer, default=0, nullable=False)
    
    # Metadata
    file_metadata = Column(Text, nullable=True)  # JSON metadata about the file
    
    # Relationships
    user = relationship("User", back_populates="storage_usage")
    campaign = relationship("Campaign", back_populates="storage_files", foreign_keys=[campaign_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_storage_active', 'user_id', 'is_deleted', 'upload_date'),
        Index('idx_user_storage_category', 'user_id', 'content_category', 'is_deleted'),
        Index('idx_user_storage_campaign', 'user_id', 'campaign_id', 'is_deleted'),
        Index('idx_storage_cleanup', 'is_deleted', 'deleted_date'),
    )
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        return round(self.file_size / 1024 / 1024, 2)
    
    @property
    def file_size_kb(self) -> float:
        """Get file size in KB"""
        return round(self.file_size / 1024, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "file_path": self.file_path,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_size_mb": self.file_size_mb,
            "content_type": self.content_type,
            "content_category": self.content_category,
            "campaign_id": self.campaign_id,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "deleted_date": self.deleted_date.isoformat() if self.deleted_date else None,
            "is_deleted": self.is_deleted,
            "access_count": self.access_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# Pydantic Schemas - FIXED for Pydantic v2
# ============================================================================

class UserStorageBase(BaseModel):
    """Base schema for user storage"""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str
    file_path: str
    original_filename: str
    file_size: int = Field(..., gt=0, description="File size in bytes")
    content_type: str
    content_category: str = Field(..., pattern="^(image|document|video)$")  # FIXED: regex -> pattern
    campaign_id: Optional[str] = None
    file_metadata: Optional[str] = None

class UserStorageCreate(UserStorageBase):
    """Schema for creating user storage records"""
    upload_date: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserStorageUpdate(BaseModel):
    """Schema for updating user storage records"""
    model_config = ConfigDict(from_attributes=True)
    
    original_filename: Optional[str] = None
    last_accessed: Optional[datetime] = None
    deleted_date: Optional[datetime] = None
    is_deleted: Optional[bool] = None
    access_count: Optional[int] = None
    file_metadata: Optional[str] = None

class UserStorageResponse(UserStorageBase):
    """Schema for user storage API responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    upload_date: datetime
    last_accessed: Optional[datetime] = None
    deleted_date: Optional[datetime] = None
    is_deleted: bool = False
    access_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        return round(self.file_size / 1024 / 1024, 2)

class UserStorageAnalytics(BaseModel):
    """Schema for storage analytics"""
    model_config = ConfigDict(from_attributes=True)
    
    total_files: int
    total_size_bytes: int
    total_size_mb: float
    total_size_gb: float
    by_category: Dict[str, Dict[str, Any]]
    recent_uploads: int
    storage_trend: str  # "increasing", "stable", "decreasing"

class UserStorageSummary(BaseModel):
    """Schema for user storage summary"""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str
    total_files: int
    active_files: int
    deleted_files: int
    total_size_bytes: int
    active_size_bytes: int
    deleted_size_bytes: int
    total_size_mb: float
    active_size_mb: float
    deleted_size_mb: float
    storage_usage_percentage: float
    last_upload: Optional[datetime] = None
    most_used_category: Optional[str] = None

# ============================================================================
# Storage Tier Validation Schemas - FIXED for Pydantic v2
# ============================================================================

class StorageTierBase(BaseModel):
    """Base schema for storage tiers"""
    model_config = ConfigDict(from_attributes=True)
    
    tier_name: str = Field(..., pattern="^(free|pro|enterprise)$")  # FIXED: regex -> pattern
    limit_gb: int = Field(..., gt=0)
    limit_bytes: int = Field(..., gt=0)
    max_file_size_mb: int = Field(..., gt=0)
    max_file_size_bytes: int = Field(..., gt=0)
    allowed_types: list[str]

class StorageQuotaCheck(BaseModel):
    """Schema for quota checking"""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str
    current_usage_bytes: int
    limit_bytes: int
    available_bytes: int
    usage_percentage: float
    is_near_limit: bool = Field(default=False)  # 80%+
    is_over_limit: bool = Field(default=False)  # 100%+
    tier: str = Field(..., pattern="^(free|pro|enterprise)$")  # FIXED: regex -> pattern

class FileUploadValidation(BaseModel):
    """Schema for file upload validation"""
    model_config = ConfigDict(from_attributes=True)
    
    filename: str
    file_size: int = Field(..., gt=0)
    content_type: str
    content_category: str = Field(..., pattern="^(image|document|video)$")  # FIXED: regex -> pattern
    user_tier: str = Field(..., pattern="^(free|pro|enterprise)$")  # FIXED: regex -> pattern
    is_valid: bool
    validation_errors: list[str] = Field(default_factory=list)

# ============================================================================
# Bulk Operations Schemas - FIXED for Pydantic v2
# ============================================================================

class BulkDeleteRequest(BaseModel):
    """Schema for bulk delete operations"""
    model_config = ConfigDict(from_attributes=True)
    
    file_ids: list[str] = Field(..., min_length=1, max_length=100)
    confirm_deletion: bool = Field(default=False)

class BulkDeleteResponse(BaseModel):
    """Schema for bulk delete responses"""
    model_config = ConfigDict(from_attributes=True)
    
    total_requested: int
    successful_deletions: int
    failed_deletions: int
    total_size_freed_mb: float
    deleted_files: list[Dict[str, Any]]
    failed_files: list[Dict[str, Any]]

class StorageExportRequest(BaseModel):
    """Schema for storage data export"""
    model_config = ConfigDict(from_attributes=True)
    
    export_format: str = Field(..., pattern="^(json|csv)$")  # FIXED: regex -> pattern
    include_deleted: bool = Field(default=False)
    date_range_days: int = Field(default=365, ge=1, le=365)
    categories: Optional[list[str]] = None

# ============================================================================
# Admin Schemas - FIXED for Pydantic v2
# ============================================================================

class AdminStorageOverview(BaseModel):
    """Schema for admin storage overview"""
    model_config = ConfigDict(from_attributes=True)
    
    total_users: int
    total_files: int
    total_size_gb: float
    avg_files_per_user: float
    avg_size_per_user_mb: float
    storage_distribution: Dict[str, int]  # by tier
    top_users_by_usage: list[Dict[str, Any]]

class AdminUserStorageDetails(BaseModel):
    """Schema for admin user storage details"""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str
    user_email: Optional[str] = None
    storage_tier: str = Field(..., pattern="^(free|pro|enterprise)$")  # FIXED: regex -> pattern
    total_files: int
    total_size_mb: float
    usage_percentage: float
    last_upload: Optional[datetime] = None
    is_over_limit: bool
    needs_attention: bool
    recommendations: list[str]

class TierUpgradeRequest(BaseModel):
    """Schema for tier upgrade requests"""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str
    new_tier: str = Field(..., pattern="^(free|pro|enterprise)$")  # FIXED: regex -> pattern
    reason: str = Field(..., min_length=10, max_length=500)
    effective_date: Optional[datetime] = None

class TierUpgradeResponse(BaseModel):
    """Schema for tier upgrade responses"""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str
    previous_tier: str
    new_tier: str
    previous_limit_gb: int
    new_limit_gb: int
    upgrade_date: datetime
    performed_by: str
    reason: str

# ============================================================================
# Migration Status Schemas - FIXED for Pydantic v2
# ============================================================================

class CRUDMigrationStatus(BaseModel):
    """Schema for CRUD migration status"""
    model_config = ConfigDict(from_attributes=True)
    
    module_name: str
    migration_complete: bool
    crud_integration_status: str
    endpoints_migrated: int
    new_features_added: int
    performance_improvements: list[str]
    last_updated: datetime

class SystemHealthCheck(BaseModel):
    """Schema for system health checks"""
    model_config = ConfigDict(from_attributes=True)
    
    overall_status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$")  # FIXED: regex -> pattern
    database_status: str = Field(..., pattern="^(connected|disconnected|error)$")  # FIXED: regex -> pattern
    storage_providers_status: Dict[str, str]
    crud_system_status: str = Field(..., pattern="^(active|inactive|error)$")  # FIXED: regex -> pattern
    total_files_managed: int
    total_storage_gb: float
    system_uptime: str
    last_health_check: datetime

# ============================================================================
# File Access Tracking - FIXED for Pydantic v2
# ============================================================================

class FileAccessEvent(BaseModel):
    """Schema for file access tracking"""
    model_config = ConfigDict(from_attributes=True)
    
    file_id: str
    user_id: str
    access_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    access_type: str = Field(..., pattern="^(view|download|preview|edit)$")  # FIXED: regex -> pattern
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class FileAccessAnalytics(BaseModel):
    """Schema for file access analytics"""
    model_config = ConfigDict(from_attributes=True)
    
    file_id: str
    filename: str
    total_accesses: int
    unique_access_days: int
    first_access: Optional[datetime] = None
    last_access: Optional[datetime] = None
    peak_access_day: Optional[str] = None
    access_trend: str = Field(..., pattern="^(increasing|stable|decreasing)$")  # FIXED: regex -> pattern

# ============================================================================
# Response Wrapper Schemas
# ============================================================================

class StorageAPIResponse(BaseModel):
    """Standard API response wrapper for storage operations"""
    model_config = ConfigDict(from_attributes=True)
    
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[list[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============================================================================
# PYDANTIC V2 COMPATIBILITY SUMMARY
# ============================================================================

"""
🔧 PYDANTIC V2 COMPATIBILITY FIXES APPLIED:

CHANGES MADE:
✅ regex -> pattern in ALL Field() validators
✅ Added model_config = ConfigDict(from_attributes=True) to all schemas
✅ Updated list type hints to use list[str] instead of List[str]
✅ Maintained all validation logic and constraints
✅ Preserved all existing functionality

FIXED FIELDS:
- content_category: Field(..., pattern="^(image|document|video)$")
- tier_name: Field(..., pattern="^(free|pro|enterprise)$")
- user_tier: Field(..., pattern="^(free|pro|enterprise)$")
- export_format: Field(..., pattern="^(json|csv)$")
- overall_status: Field(..., pattern="^(healthy|degraded|unhealthy)$")
- database_status: Field(..., pattern="^(connected|disconnected|error)$")
- crud_system_status: Field(..., pattern="^(active|inactive|error)$")
- access_type: Field(..., pattern="^(view|download|preview|edit)$")
- access_trend: Field(..., pattern="^(increasing|stable|decreasing)$")

DEPLOYMENT STATUS:
✅ Ready for immediate deployment
✅ Pydantic v2 compatible
✅ All validation preserved
✅ Zero functionality lost
"""