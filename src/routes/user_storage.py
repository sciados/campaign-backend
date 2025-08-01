# src/routes/user_storage.py - NEW FILE
"""
User Storage Management API Routes
🎯 Complete user storage dashboard and file management
📊 Storage analytics and quota management
🔧 Tier upgrades and usage monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import structlog

from src.core.database import get_async_db
from src.auth.dependencies import get_current_user, get_current_admin_user
from src.models.user import User
from src.models.user_storage import UserStorageUsage
from src.storage.universal_dual_storage import (
    get_storage_manager, 
    upload_with_quota_check,
    UserQuotaExceeded,
    FileSizeExceeded, 
    ContentTypeNotAllowed
)
from src.storage.storage_tiers import (
    STORAGE_TIERS,
    get_tier_info,
    get_available_tiers,
    calculate_tier_upgrade_cost
)

logger = structlog.get_logger()
router = APIRouter(prefix="/api/users", tags=["User Storage"])

# ============================================================================
# USER STORAGE DASHBOARD
# ============================================================================

@router.get("/{user_id}/storage/dashboard")
async def get_user_storage_dashboard(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get comprehensive storage dashboard for user"""
    
    # Authorization check
    if str(current_user.id) != user_id and current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        storage_manager = get_storage_manager()
        dashboard_data = await storage_manager.get_user_storage_dashboard(user_id, db)
        
        if not dashboard_data.get("success"):
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Failed to get storage dashboard for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve storage dashboard"
        )

@router.get("/{user_id}/storage/usage")
async def get_user_storage_usage(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get detailed storage usage breakdown"""
    
    # Authorization check
    if str(current_user.id) != user_id and current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Get user
        result = await db.execute(
            select(User)
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get usage statistics by category and date
        usage_stats = await db.execute(
            select(
                UserStorageUsage.content_category,
                func.count(UserStorageUsage.id).label('file_count'),
                func.sum(UserStorageUsage.file_size).label('total_size'),
                func.avg(UserStorageUsage.file_size).label('avg_size'),
                func.max(UserStorageUsage.upload_date).label('last_upload')
            )
            .where(and_(
                UserStorageUsage.user_id == user_id,
                UserStorageUsage.is_deleted == False
            ))
            .group_by(UserStorageUsage.content_category)
        )
        
        category_stats = {}
        total_files = 0
        total_size = 0
        
        for row in usage_stats:
            category_stats[row.content_category] = {
                "file_count": row.file_count,
                "total_size_bytes": row.total_size or 0,
                "total_size_mb": round((row.total_size or 0) / 1024 / 1024, 2),
                "avg_size_mb": round((row.avg_size or 0) / 1024 / 1024, 2),
                "last_upload": row.last_upload.isoformat() if row.last_upload else None
            }
            total_files += row.file_count
            total_size += (row.total_size or 0)
        
        # Get tier info
        tier_info = get_tier_info(user.storage_tier)
        usage_percentage = user.get_storage_usage_percentage()
        
        return {
            "success": True,
            "user_id": user_id,
            "storage_tier": user.storage_tier,
            "tier_info": tier_info,
            "summary": {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "total_size_gb": round(total_size / 1024 / 1024 / 1024, 3),
                "usage_percentage": usage_percentage,
                "is_near_limit": usage_percentage >= 80,
                "is_over_limit": usage_percentage >= 100,
                "available_bytes": user.get_storage_available_bytes(),
                "available_mb": round(user.get_storage_available_bytes() / 1024 / 1024, 2)
            },
            "by_category": category_stats,
            "limits": {
                "storage_limit_bytes": user.storage_limit_bytes,
                "storage_limit_mb": user.get_storage_limit_mb(),
                "storage_limit_gb": user.get_storage_limit_gb(),
                "max_file_size_mb": tier_info["max_file_size_mb"],
                "allowed_types": tier_info["allowed_types"]
            },
            "last_updated": user.last_storage_check.isoformat() if user.last_storage_check else None
        }
        
    except Exception as e:
        logger.error(f"Failed to get storage usage for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve storage usage"
        )

# ============================================================================
# FILE UPLOAD & MANAGEMENT
# ============================================================================

@router.post("/{user_id}/storage/upload")
async def upload_file_with_quota(
    user_id: str,
    file: UploadFile = File(...),
    campaign_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Upload file with quota validation"""
    
    # Authorization check
    if str(current_user.id) != user_id and current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Empty file uploaded"
            )
        
        # Upload with quota check
        result = await upload_with_quota_check(
            file_content=file_content,
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            user_id=user_id,
            campaign_id=campaign_id,
            db=db
        )
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file": result
        }
        
    except UserQuotaExceeded as e:
        logger.warning(f"User {user_id} quota exceeded: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "Storage quota exceeded",
                "current_usage_mb": round(e.current_usage / 1024 / 1024, 2),
                "limit_mb": round(e.limit / 1024 / 1024, 2),
                "attempted_size_mb": round(e.attempted_size / 1024 / 1024, 2),
                "available_mb": round((e.limit - e.current_usage) / 1024 / 1024, 2),
                "upgrade_suggestion": "Consider upgrading to Pro tier for 10GB storage"
            }
        )
        
    except FileSizeExceeded as e:
        logger.warning(f"User {user_id} file size exceeded: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "File size exceeds tier limit",
                "file_size_mb": round(e.file_size / 1024 / 1024, 2),
                "max_allowed_mb": round(e.max_allowed / 1024 / 1024, 2),
                "tier": e.tier,
                "upgrade_suggestion": f"Upgrade to Pro tier for {STORAGE_TIERS['pro']['max_file_size_mb']}MB files"
            }
        )
        
    except ContentTypeNotAllowed as e:
        logger.warning(f"User {user_id} content type not allowed: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={
                "error": "File type not allowed for your tier",
                "content_type": e.content_type,
                "tier": e.tier,
                "allowed_types": e.allowed_types,
                "upgrade_suggestion": "Upgrade to Pro tier for video support"
            }
        )
        
    except Exception as e:
        logger.error(f"Upload failed for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )

@router.get("/{user_id}/storage/files")
async def get_user_files(
    user_id: str,
    content_category: Optional[str] = Query(None, description="Filter by category: image, document, video"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign"),
    include_deleted: bool = Query(False, description="Include deleted files"),
    limit: int = Query(50, ge=1, le=200, description="Number of files to return"),
    offset: int = Query(0, ge=0, description="Number of files to skip"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user's files with filtering and pagination"""
    
    # Authorization check
    if str(current_user.id) != user_id and current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        storage_manager = get_storage_manager()
        files_data = await storage_manager.get_user_files(
            user_id=user_id,
            content_category=content_category,
            campaign_id=campaign_id,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset,
            db=db
        )
        
        return files_data
        
    except Exception as e:
        logger.error(f"Failed to get files for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve files"
        )

@router.delete("/{user_id}/storage/files/{file_id}")
async def delete_user_file(
    user_id: str,
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete user file and update quota"""
    
    # Authorization check
    if str(current_user.id) != user_id and current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        storage_manager = get_storage_manager()
        result = await storage_manager.delete_file_with_quota_update(
            file_id=file_id,
            user_id=user_id,
            db=db
        )
        
        return {
            "success": True,
            "message": "File deleted successfully",
            "details": result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to delete file {file_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )

# ============================================================================
# STORAGE TIER MANAGEMENT
# ============================================================================

@router.get("/{user_id}/storage/tiers")
async def get_available_storage_tiers(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get available storage tiers and upgrade options"""
    
    # Authorization check
    if str(current_user.id) != user_id and current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Get user's current tier
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        current_tier = user.storage_tier
        tiers_info = {}
        
        for tier_name in get_available_tiers():
            tier_info = get_tier_info(tier_name)
            
            # Calculate upgrade cost
            upgrade_cost = 0
            if tier_name != current_tier:
                upgrade_cost = calculate_tier_upgrade_cost(current_tier, tier_name)
            
            tiers_info[tier_name] = {
                **tier_info,
                "is_current": tier_name == current_tier,
                "upgrade_cost": upgrade_cost,
                "can_upgrade": tier_name != current_tier and upgrade_cost >= 0,
                "is_downgrade": upgrade_cost < 0
            }
        
        return {
            "success": True,
            "current_tier": current_tier,
            "tiers": tiers_info,
            "recommendations": {
                "suggested_tier": "pro" if current_tier == "free" else "enterprise",
                "benefits": _get_upgrade_benefits(current_tier)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get tiers for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve storage tiers"
        )

@router.post("/{user_id}/storage/upgrade")
async def upgrade_user_storage_tier(
    user_id: str,
    new_tier: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Upgrade user's storage tier (placeholder for payment integration)"""
    
    # Authorization check
    if str(current_user.id) != user_id and current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Validate tier
    if new_tier not in get_available_tiers():
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {new_tier}"
        )
    
    try:
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        current_tier = user.storage_tier
        
        # Check if it's actually an upgrade
        upgrade_cost = calculate_tier_upgrade_cost(current_tier, new_tier)
        if upgrade_cost < 0:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Downgrades not supported through this endpoint"
            )
        
        # TODO: Integrate with payment processor here
        # For now, just update the tier (in production, this would happen after payment)
        
        # Update user tier and limits
        new_tier_info = get_tier_info(new_tier)
        user.storage_tier = new_tier
        user.storage_limit_bytes = new_tier_info["limit_bytes"]
        user.last_storage_check = datetime.now(timezone.utc)
        
        await db.commit()
        
        logger.info(f"User {user_id} upgraded from {current_tier} to {new_tier}")
        
        return {
            "success": True,
            "message": f"Successfully upgraded to {new_tier} tier",
            "details": {
                "previous_tier": current_tier,
                "new_tier": new_tier,
                "new_limit_gb": new_tier_info["limit_gb"],
                "upgrade_cost": upgrade_cost,
                "effective_date": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to upgrade tier for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upgrade storage tier"
        )

# ============================================================================
# STORAGE ANALYTICS
# ============================================================================

@router.get("/{user_id}/storage/analytics")
async def get_user_storage_analytics(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get detailed storage analytics for user"""
    
    # Authorization check
    if str(current_user.id) != user_id and current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Upload trends over time
        upload_trends = await db.execute(
            select(
                func.date(UserStorageUsage.upload_date).label('date'),
                func.count(UserStorageUsage.id).label('uploads'),
                func.sum(UserStorageUsage.file_size).label('bytes_uploaded')
            )
            .where(and_(
                UserStorageUsage.user_id == user_id,
                UserStorageUsage.upload_date >= start_date,
                UserStorageUsage.is_deleted == False
            ))
            .group_by(func.date(UserStorageUsage.upload_date))
            .order_by(func.date(UserStorageUsage.upload_date))
        )
        
        daily_stats = []
        total_uploads = 0
        total_bytes = 0
        
        for row in upload_trends:
            daily_stats.append({
                "date": row.date.isoformat(),
                "uploads": row.uploads,
                "bytes_uploaded": row.bytes_uploaded,
                "mb_uploaded": round(row.bytes_uploaded / 1024 / 1024, 2)
            })
            total_uploads += row.uploads
            total_bytes += row.bytes_uploaded
        
        # Most accessed files
        popular_files = await db.execute(
            select(UserStorageUsage)
            .where(and_(
                UserStorageUsage.user_id == user_id,
                UserStorageUsage.is_deleted == False,
                UserStorageUsage.access_count > 0
            ))
            .order_by(desc(UserStorageUsage.access_count))
            .limit(10)
        )
        
        popular_files_list = []
        for file in popular_files:
            popular_files_list.append({
                "id": str(file.id),
                "filename": file.original_filename,
                "content_category": file.content_category,
                "access_count": file.access_count,
                "file_size_mb": file.file_size_mb,
                "last_accessed": file.last_accessed.isoformat() if file.last_accessed else None
            })
        
        return {
            "success": True,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "summary": {
                "total_uploads": total_uploads,
                "total_bytes_uploaded": total_bytes,
                "total_mb_uploaded": round(total_bytes / 1024 / 1024, 2),
                "avg_daily_uploads": round(total_uploads / days, 1),
                "avg_daily_mb": round((total_bytes / 1024 / 1024) / days, 2)
            },
            "daily_trends": daily_stats,
            "popular_files": popular_files_list
        }
        
    except Exception as e:
        logger.error(f"Failed to get analytics for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve storage analytics"
        )

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_upgrade_benefits(current_tier: str) -> List[str]:
    """Get benefits of upgrading from current tier"""
    if current_tier == "free":
        return [
            "10x more storage (10GB vs 1GB)",
            "5x larger files (50MB vs 10MB)",
            "Video upload support",
            "10x more monthly uploads",
            "Priority support"
        ]
    elif current_tier == "pro":
        return [
            "10x more storage (100GB vs 10GB)",
            "4x larger files (200MB vs 50MB)",
            "Unlimited monthly uploads",
            "Advanced analytics",
            "Custom integrations"
        ]
    else:
        return ["You're already on the highest tier!"]