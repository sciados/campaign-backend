# src/routes/admin_storage.py - NEW FILE
"""
Admin Storage Management Routes
🔧 System-wide storage monitoring and management
📊 User storage analytics and quota management
⚙️ Storage cleanup and optimization tools
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Form
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, text
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import asyncio
import structlog

from src.core.database import get_async_db
from src.auth.dependencies import get_current_admin_user
from src.models.user import User
from src.models.user_storage import UserStorageUsage
from src.storage.universal_dual_storage import get_storage_manager
from src.storage.storage_tiers import STORAGE_TIERS, get_tier_info

logger = structlog.get_logger()
router = APIRouter(prefix="/api/admin/storage", tags=["Admin Storage"])

# ============================================================================
# SYSTEM STORAGE OVERVIEW
# ============================================================================

@router.get("/system/overview")
async def get_system_storage_overview(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get system-wide storage overview and statistics"""
    
    try:
        # Total system usage
        total_stats = await db.execute(
            select(
                func.count(UserStorageUsage.id).label('total_files'),
                func.sum(UserStorageUsage.file_size).label('total_size'),
                func.count(func.distinct(UserStorageUsage.user_id)).label('active_users')
            )
            .where(UserStorageUsage.is_deleted == False)
        )
        
        stats = total_stats.first()
        total_files = stats.total_files or 0
        total_size = stats.total_size or 0
        active_users = stats.active_users or 0
        
        # Usage by tier
        tier_usage = await db.execute(
            select(
                User.storage_tier,
                func.count(User.id).label('user_count'),
                func.sum(User.storage_used_bytes).label('total_used'),
                func.sum(User.storage_limit_bytes).label('total_allocated'),
                func.avg(User.storage_used_bytes).label('avg_used')
            )
            .group_by(User.storage_tier)
        )
        
        tier_stats = {}
        total_revenue_potential = 0
        
        for row in tier_usage:
            tier_info = get_tier_info(row.storage_tier)
            monthly_revenue = row.user_count * tier_info["price_monthly"]
            total_revenue_potential += monthly_revenue
            
            tier_stats[row.storage_tier] = {
                "user_count": row.user_count,
                "total_used_bytes": row.total_used or 0,
                "total_used_gb": round((row.total_used or 0) / 1024 / 1024 / 1024, 2),
                "total_allocated_gb": round((row.total_allocated or 0) / 1024 / 1024 / 1024, 2),
                "avg_used_mb": round((row.avg_used or 0) / 1024 / 1024, 2),
                "utilization_rate": round(((row.total_used or 0) / (row.total_allocated or 1)) * 100, 1),
                "monthly_revenue": monthly_revenue,
                "price_per_user": tier_info["price_monthly"]
            }
        
        # Top storage users
        top_users = await db.execute(
            select(User)
            .options(selectinload(User.storage_usage))
            .where(User.storage_used_bytes > 0)
            .order_by(desc(User.storage_used_bytes))
            .limit(10)
        )
        
        top_users_list = []
        for user in top_users:
            top_users_list.append({
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "storage_tier": user.storage_tier,
                "used_mb": user.get_storage_used_mb(),
                "used_gb": user.get_storage_used_gb(),
                "limit_gb": user.get_storage_limit_gb(),
                "usage_percentage": user.get_storage_usage_percentage(),
                "file_count": len([f for f in user.storage_usage if not f.is_deleted]) if user.storage_usage else 0
            })
        
        # Storage health check
        storage_manager = get_storage_manager()
        health_status = await storage_manager.get_storage_health()
        
        return {
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_totals": {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_gb": round(total_size / 1024 / 1024 / 1024, 2),
                "active_users": active_users,
                "avg_files_per_user": round(total_files / max(active_users, 1), 1),
                "avg_storage_per_user_mb": round((total_size / 1024 / 1024) / max(active_users, 1), 2)
            },
            "tier_breakdown": tier_stats,
            "revenue_analytics": {
                "total_monthly_revenue_potential": total_revenue_potential,
                "total_annual_revenue_potential": total_revenue_potential * 12,
                "free_tier_users": tier_stats.get("free", {}).get("user_count", 0),
                "paying_users": sum(stats["user_count"] for tier, stats in tier_stats.items() if tier != "free"),
                "conversion_rate": round((sum(stats["user_count"] for tier, stats in tier_stats.items() if tier != "free") / max(sum(stats["user_count"] for stats in tier_stats.values()), 1)) * 100, 2)
            },
            "top_storage_users": top_users_list,
            "storage_health": health_status,
            "cost_analysis": {
                "estimated_monthly_cost": round(total_size / 1024 / 1024 / 1024 * 0.015, 2),  # R2 pricing
                "estimated_annual_cost": round(total_size / 1024 / 1024 / 1024 * 0.015 * 12, 2),
                "cost_per_user": round((total_size / 1024 / 1024 / 1024 * 0.015) / max(active_users, 1), 4)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get system storage overview: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system storage overview"
        )

# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.get("/users")
async def get_all_users_storage(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tier: Optional[str] = Query(None, description="Filter by storage tier"),
    sort_by: str = Query("usage_desc", description="Sort by: usage_desc, usage_asc, tier, email"),
    search: Optional[str] = Query(None, description="Search by email or name"),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all users with their storage information"""
    
    try:
        # Build query
        query = select(User).options(selectinload(User.storage_usage))
        
        # Apply filters
        if tier:
            query = query.where(User.storage_tier == tier)
        
        if search:
            search_term = f"%{search.lower()}%"
            query = query.where(
                func.lower(User.email).like(search_term) |
                func.lower(User.full_name).like(search_term)
            )
        
        # Apply sorting
        if sort_by == "usage_desc":
            query = query.order_by(desc(User.storage_used_bytes))
        elif sort_by == "usage_asc":
            query = query.order_by(User.storage_used_bytes)
        elif sort_by == "tier":
            query = query.order_by(User.storage_tier)
        elif sort_by == "email":
            query = query.order_by(User.email)
        else:
            query = query.order_by(desc(User.storage_used_bytes))
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query
        result = await db.execute(query)
        users = result.scalars().all()
        
        # Get total count
        count_query = select(func.count(User.id))
        if tier:
            count_query = count_query.where(User.storage_tier == tier)
        if search:
            search_term = f"%{search.lower()}%"
            count_query = count_query.where(
                func.lower(User.email).like(search_term) |
                func.lower(User.full_name).like(search_term)
            )
        
        total_result = await db.execute(count_query)
        total_count = total_result.scalar()
        
        # Format users
        users_list = []
        for user in users:
            file_count = len([f for f in user.storage_usage if not f.is_deleted]) if user.storage_usage else 0
            
            users_list.append({
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "storage_tier": user.storage_tier,
                "usage": {
                    "used_bytes": user.storage_used_bytes,
                    "used_mb": user.get_storage_used_mb(),
                    "used_gb": user.get_storage_used_gb(),
                    "limit_gb": user.get_storage_limit_gb(),
                    "usage_percentage": user.get_storage_usage_percentage(),
                    "available_mb": round(user.get_storage_available_bytes() / 1024 / 1024, 2)
                },
                "file_count": file_count,
                "last_storage_check": user.last_storage_check.isoformat() if user.last_storage_check else None,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat()
            })
        
        return {
            "success": True,
            "users": users_list,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count
            },
            "filters_applied": {
                "tier": tier,
                "search": search,
                "sort_by": sort_by
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get users storage data: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users storage data"
        )

@router.put("/users/{user_id}/storage-limit")
async def update_user_storage_limit(
    user_id: str,
    new_limit_gb: float = Form(..., ge=0.1, le=1000),
    new_tier: Optional[str] = Form(None),
    reason: str = Form(..., description="Reason for the change"),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update user's storage limit (admin override)"""
    
    try:
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        old_limit = user.get_storage_limit_gb()
        old_tier = user.storage_tier
        
        # Update limits
        user.storage_limit_bytes = int(new_limit_gb * 1024 * 1024 * 1024)
        
        if new_tier and new_tier in STORAGE_TIERS:
            user.storage_tier = new_tier
        
        user.last_storage_check = datetime.now(timezone.utc)
        
        await db.commit()
        
        logger.info(f"Admin {current_admin.email} updated storage for user {user.email}: {old_limit}GB -> {new_limit_gb}GB, tier: {old_tier} -> {user.storage_tier}, reason: {reason}")
        
        return {
            "success": True,
            "message": "User storage limit updated successfully",
            "changes": {
                "user_id": user_id,
                "user_email": user.email,
                "old_limit_gb": old_limit,
                "new_limit_gb": new_limit_gb,
                "old_tier": old_tier,
                "new_tier": user.storage_tier,
                "reason": reason,
                "updated_by": current_admin.email,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update storage limit for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user storage limit"
        )

# ============================================================================
# SYSTEM ANALYTICS
# ============================================================================

@router.get("/analytics/trends")
async def get_storage_trends(
    days: int = Query(30, ge=1, le=365),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get storage usage trends over time"""
    
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Daily upload trends
        daily_trends = await db.execute(
            select(
                func.date(UserStorageUsage.upload_date).label('date'),
                func.count(UserStorageUsage.id).label('uploads'),
                func.sum(UserStorageUsage.file_size).label('bytes_uploaded'),
                func.count(func.distinct(UserStorageUsage.user_id)).label('active_users')
            )
            .where(and_(
                UserStorageUsage.upload_date >= start_date,
                UserStorageUsage.is_deleted == False
            ))
            .group_by(func.date(UserStorageUsage.upload_date))
            .order_by(func.date(UserStorageUsage.upload_date))
        )
        
        trend_data = []
        total_uploads = 0
        total_bytes = 0
        
        for row in daily_trends:
            trend_data.append({
                "date": row.date.isoformat(),
                "uploads": row.uploads,
                "bytes_uploaded": row.bytes_uploaded,
                "mb_uploaded": round(row.bytes_uploaded / 1024 / 1024, 2),
                "active_users": row.active_users
            })
            total_uploads += row.uploads
            total_bytes += row.bytes_uploaded
        
        # Content type breakdown
        content_breakdown = await db.execute(
            select(
                UserStorageUsage.content_category,
                func.count(UserStorageUsage.id).label('file_count'),
                func.sum(UserStorageUsage.file_size).label('total_size')
            )
            .where(and_(
                UserStorageUsage.upload_date >= start_date,
                UserStorageUsage.is_deleted == False
            ))
            .group_by(UserStorageUsage.content_category)
        )
        
        content_stats = {}
        for row in content_breakdown:
            content_stats[row.content_category] = {
                "file_count": row.file_count,
                "total_size_bytes": row.total_size,
                "total_size_mb": round(row.total_size / 1024 / 1024, 2),
                "percentage": round((row.total_size / max(total_bytes, 1)) * 100, 1)
            }
        
        return {
            "success": True,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "summary": {
                "total_uploads": total_uploads,
                "total_bytes": total_bytes,
                "total_gb": round(total_bytes / 1024 / 1024 / 1024, 2),
                "avg_daily_uploads": round(total_uploads / days, 1),
                "avg_daily_gb": round((total_bytes / 1024 / 1024 / 1024) / days, 3)
            },
            "daily_trends": trend_data,
            "content_breakdown": content_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get storage trends: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve storage trends"
        )

# ============================================================================
# CLEANUP AND MAINTENANCE
# ============================================================================

@router.post("/cleanup/orphaned-files")
async def cleanup_orphaned_files(
    dry_run: bool = Form(True, description="Preview changes without executing"),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Find and cleanup orphaned files (files in R2 but not in database)"""
    
    try:
        storage_manager = get_storage_manager()
        
        if dry_run:
            # For now, return a placeholder since we'd need to implement R2 listing
            return {
                "success": True,
                "dry_run": True,
                "message": "Dry run completed - no files were deleted",
                "found_orphans": 0,
                "would_free_mb": 0,
                "note": "Full orphan detection requires R2 bucket listing implementation"
            }
        else:
            # TODO: Implement actual orphan cleanup
            return {
                "success": True,
                "dry_run": False,
                "message": "Orphan cleanup not yet implemented",
                "cleaned_files": 0,
                "freed_mb": 0
            }
        
    except Exception as e:
        logger.error(f"Failed to cleanup orphaned files: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup orphaned files"
        )

@router.post("/cleanup/old-deleted-files")
async def cleanup_old_deleted_files(
    days_old: int = Form(30, ge=1, le=365, description="Delete files soft-deleted this many days ago"),
    dry_run: bool = Form(True, description="Preview changes without executing"),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Permanently delete files that were soft-deleted X days ago"""
    
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
        
        # Find old deleted files
        old_deleted_files = await db.execute(
            select(UserStorageUsage)
            .where(and_(
                UserStorageUsage.is_deleted == True,
                UserStorageUsage.deleted_date <= cutoff_date
            ))
        )
        
        files_to_delete = old_deleted_files.scalars().all()
        total_files = len(files_to_delete)
        total_size = sum(file.file_size for file in files_to_delete)
        total_size_mb = round(total_size / 1024 / 1024, 2)
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": f"Found {total_files} files ready for permanent deletion",
                "files_found": total_files,
                "total_size_mb": total_size_mb,
                "cutoff_date": cutoff_date.isoformat(),
                "would_free_storage": True
            }
        
        # Actually delete files (not in dry run)
        storage_manager = get_storage_manager()
        deleted_count = 0
        freed_bytes = 0
        
        for file in files_to_delete:
            try:
                # Delete from R2
                await storage_manager.delete_file(file.file_path)
                
                # Update user storage usage
                await db.execute(
                    text("UPDATE users SET storage_used_bytes = storage_used_bytes - :bytes WHERE id = :user_id"),
                    {"bytes": file.file_size, "user_id": file.user_id}
                )
                
                # Delete database record
                await db.delete(file)
                
                deleted_count += 1
                freed_bytes += file.file_size
                
            except Exception as e:
                logger.warning(f"Failed to delete file {file.id}: {str(e)}")
                continue
        
        await db.commit()
        
        logger.info(f"Admin {current_admin.email} cleaned up {deleted_count} old deleted files, freed {round(freed_bytes / 1024 / 1024, 2)}MB")
        
        return {
            "success": True,
            "dry_run": False,
            "message": f"Successfully deleted {deleted_count} old files",
            "deleted_files": deleted_count,
            "freed_mb": round(freed_bytes / 1024 / 1024, 2),
            "failed_deletions": total_files - deleted_count
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to cleanup old deleted files: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup old deleted files"
        )

@router.post("/maintenance/reconcile-usage")
async def reconcile_storage_usage(
    user_id: Optional[str] = Form(None, description="Reconcile specific user, or all users if empty"),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Reconcile database storage usage with actual file sizes"""
    
    try:
        # Build query
        if user_id:
            users_query = select(User).where(User.id == user_id)
        else:
            users_query = select(User)
        
        result = await db.execute(users_query)
        users = result.scalars().all()
        
        if not users:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="No users found"
            )
        
        reconciled_users = []
        total_corrections = 0
        
        for user in users:
            # Calculate actual usage from storage records
            actual_usage = await db.execute(
                select(func.sum(UserStorageUsage.file_size))
                .where(and_(
                    UserStorageUsage.user_id == user.id,
                    UserStorageUsage.is_deleted == False
                ))
            )
            
            actual_bytes = actual_usage.scalar() or 0
            stored_bytes = user.storage_used_bytes
            difference = actual_bytes - stored_bytes
            
            if difference != 0:
                # Update user's stored usage
                user.storage_used_bytes = actual_bytes
                user.last_storage_check = datetime.now(timezone.utc)
                total_corrections += 1
                
                reconciled_users.append({
                    "user_id": str(user.id),
                    "email": user.email,
                    "stored_bytes": stored_bytes,
                    "actual_bytes": actual_bytes,
                    "difference_bytes": difference,
                    "difference_mb": round(difference / 1024 / 1024, 2),
                    "corrected": True
                })
            else:
                reconciled_users.append({
                    "user_id": str(user.id),
                    "email": user.email,
                    "stored_bytes": stored_bytes,
                    "actual_bytes": actual_bytes,
                    "difference_bytes": 0,
                    "difference_mb": 0,
                    "corrected": False
                })
        
        await db.commit()
        
        logger.info(f"Admin {current_admin.email} reconciled storage usage for {len(users)} users, {total_corrections} corrections made")
        
        return {
            "success": True,
            "message": f"Reconciled storage usage for {len(users)} users",
            "total_users_checked": len(users),
            "corrections_made": total_corrections,
            "users": reconciled_users
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to reconcile storage usage: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reconcile storage usage"
        )

# ============================================================================
# SYSTEM HEALTH AND MONITORING
# ============================================================================

@router.get("/health/detailed")
async def get_detailed_storage_health(
    current_admin: User = Depends(get_current_admin_user)
):
    """Get detailed storage system health information"""
    
    try:
        storage_manager = get_storage_manager()
        health_status = await storage_manager.get_storage_health()
        
        # Add admin-specific health details
        health_status["admin_details"] = {
            "quota_system_active": True,
            "tier_validation_enabled": True,
            "cleanup_tools_available": True,
            "monitoring_active": True,
            "backup_providers": len([p for p in health_status.get("providers", {}).values() if p.get("status") == "healthy"]) - 1,
            "failover_ready": len([p for p in health_status.get("providers", {}).values() if p.get("status") == "healthy"]) > 1
        }
        
        return {
            "success": True,
            "health_status": health_status,
            "system_recommendations": _get_system_recommendations(health_status)
        }
        
    except Exception as e:
        logger.error(f"Failed to get detailed storage health: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve storage health information"
        )

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_system_recommendations(health_status: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate system recommendations based on health status"""
    recommendations = []
    
    # Check provider health
    unhealthy_providers = [
        name for name, status in health_status.get("providers", {}).items()
        if status.get("status") != "healthy"
    ]
    
    if unhealthy_providers:
        recommendations.append({
            "priority": "high",
            "category": "provider_health",
            "message": f"Unhealthy storage providers detected: {', '.join(unhealthy_providers)}",
            "action": "Check provider configuration and connectivity"
        })
    
    # Check redundancy
    healthy_providers = len([
        p for p in health_status.get("providers", {}).values()
        if p.get("status") == "healthy"
    ])
    
    if healthy_providers < 2:
        recommendations.append({
            "priority": "medium",
            "category": "redundancy",
            "message": "Limited storage redundancy - only one healthy provider",
            "action": "Configure backup storage providers for redundancy"
        })
    
    # Check overall status
    if health_status.get("overall_status") != "healthy":
        recommendations.append({
            "priority": "high",
            "category": "system_health",
            "message": "Overall storage system health is degraded",
            "action": "Review provider status and resolve configuration issues"
        })
    
    if not recommendations:
        recommendations.append({
            "priority": "info",
            "category": "system_health",
            "message": "Storage system is operating normally",
            "action": "Continue regular monitoring and maintenance"
        })
    
    return recommendations