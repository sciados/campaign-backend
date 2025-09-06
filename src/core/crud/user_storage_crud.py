# src/core/crud/user_storage_crud.py - FIXED: Generic Type Parameters
"""
User Storage CRUD Operations - FIXED Generic Type Definition
🎯 Complete CRUD implementation for UserStorageUsage model
📊 Storage analytics and quota management
🔧 File management and tier operations
🔧 FIXED: BaseCRUD generic type parameters
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc, update, delete
from sqlalchemy.orm import selectinload, joinedload
from src.utils.json_utils import safe_json_dumps, safe_json_loads

# ✅ FIXED: Import only what we need for CRUD
from .base_crud import BaseCRUD
from src.models.user_storage import UserStorageUsage  # Only the model class
from src.models.user import User
from src.models.campaign import Campaign

import logging
logger = logging.getLogger(__name__)

# ✅ FIXED: Use only the model type parameter, not the Pydantic schemas
class UserStorageCRUD(BaseCRUD[UserStorageUsage]):
    """Enhanced CRUD operations for user storage management"""
    
    def __init__(self):
        super().__init__(UserStorageUsage)
    
    # ============================================================================
    # FILE MANAGEMENT OPERATIONS
    # ============================================================================
    
    async def create_storage_record(
        self,
        db: AsyncSession,
        *,
        user_id: Union[str, UUID],
        file_path: str,
        original_filename: str,
        file_size: int,
        content_type: str,
        content_category: str,
        campaign_id: Optional[Union[str, UUID]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UserStorageUsage:
        """Create a new storage usage record"""
        
        storage_data = {
            "user_id": str(user_id),
            "file_path": file_path,
            "original_filename": original_filename,
            "file_size": file_size,
            "content_type": content_type,
            "content_category": content_category,
            "campaign_id": str(campaign_id) if campaign_id else None,
            "file_metadata": safe_json_dumps(metadata) if metadata else None,
            "upload_date": datetime.now(timezone.utc)
        }
        
        storage_record = await self.create(db=db, obj_in=storage_data)
        
        logger.info(
            f"Created storage record for user {user_id}: {original_filename} ({file_size} bytes)"
        )
        
        return storage_record
    
    async def get_user_files(
        self,
        db: AsyncSession,
        *,
        user_id: Union[str, UUID],
        content_category: Optional[str] = None,
        campaign_id: Optional[Union[str, UUID]] = None,
        include_deleted: bool = False,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "upload_date",
        order_desc: bool = True
    ) -> Dict[str, Any]:
        """Get user files with filtering and pagination"""
        
        # Build base query
        query = select(UserStorageUsage).where(UserStorageUsage.user_id == str(user_id))
        
        # Apply filters
        if not include_deleted:
            query = query.where(UserStorageUsage.is_deleted == False)
        
        if content_category:
            query = query.where(UserStorageUsage.content_category == content_category)
        
        if campaign_id:
            query = query.where(UserStorageUsage.campaign_id == str(campaign_id))
        
        # Count total for pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total_files = total_result.scalar()
        
        # Apply ordering
        order_column = getattr(UserStorageUsage, order_by, UserStorageUsage.upload_date)
        if order_desc:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        files = result.scalars().all()
        
        # Prepare response
        files_data = []
        for file in files:
            files_data.append({
                "id": str(file.id),
                "file_path": file.file_path,
                "original_filename": file.original_filename,
                "file_size": file.file_size,
                "file_size_mb": file.file_size_mb,
                "content_type": file.content_type,
                "content_category": file.content_category,
                "campaign_id": file.campaign_id,
                "upload_date": file.upload_date.isoformat(),
                "last_accessed": file.last_accessed.isoformat() if file.last_accessed else None,
                "access_count": file.access_count,
                "is_deleted": file.is_deleted,
                "metadata": safe_json_loads(file.file_metadata) if file.file_metadata else {}
            })
        
        return {
            "success": True,
            "files": files_data,
            "pagination": {
                "total": total_files,
                "limit": limit,
                "offset": offset,
                "has_more": total_files > (offset + limit)
            },
            "filters": {
                "content_category": content_category,
                "campaign_id": str(campaign_id) if campaign_id else None,
                "include_deleted": include_deleted
            }
        }
    
    async def get_file_by_path(
        self,
        db: AsyncSession,
        *,
        user_id: Union[str, UUID],
        file_path: str
    ) -> Optional[UserStorageUsage]:
        """Get file by path for a specific user"""
        
        result = await db.execute(
            select(UserStorageUsage)
            .where(
                and_(
                    UserStorageUsage.user_id == str(user_id),
                    UserStorageUsage.file_path == file_path,
                    UserStorageUsage.is_deleted == False
                )
            )
        )
        
        return result.scalar_one_or_none()
    
    async def mark_file_deleted(
        self,
        db: AsyncSession,
        *,
        file_id: Union[str, UUID],
        user_id: Union[str, UUID]
    ) -> Dict[str, Any]:
        """Mark file as deleted and return size for quota update"""
        
        # Get file record
        file_record = await self.get(db=db, id=file_id)
        
        if not file_record:
            raise ValueError(f"File {file_id} not found")
        
        if file_record.user_id != str(user_id):
            raise ValueError(f"File {file_id} does not belong to user {user_id}")
        
        if file_record.is_deleted:
            raise ValueError(f"File {file_id} is already deleted")
        
        # Mark as deleted using CRUD update
        update_data = {
            "is_deleted": True,
            "deleted_date": datetime.now(timezone.utc)
        }
        
        updated_file = await self.update(db=db, db_obj=file_record, obj_in=update_data)
        
        logger.info(f"Marked file {file_id} as deleted for user {user_id}")
        
        return {
            "file_id": str(file_id),
            "file_size": file_record.file_size,
            "original_filename": file_record.original_filename,
            "deleted_date": updated_file.deleted_date.isoformat()
        }
    
    async def update_file_access(
        self,
        db: AsyncSession,
        *,
        file_id: Union[str, UUID],
        user_id: Union[str, UUID]
    ) -> bool:
        """Update file access count and timestamp"""
        
        try:
            # Update access tracking
            await db.execute(
                update(UserStorageUsage)
                .where(
                    and_(
                        UserStorageUsage.id == file_id,
                        UserStorageUsage.user_id == str(user_id),
                        UserStorageUsage.is_deleted == False
                    )
                )
                .values(
                    access_count=UserStorageUsage.access_count + 1,
                    last_accessed=datetime.now(timezone.utc)
                )
            )
            
            await db.commit()
            return True
            
        except Exception as e:
            logger.warning(f"Failed to update file access for {file_id}: {str(e)}")
            await db.rollback()
            return False
    
    # ============================================================================
    # STORAGE ANALYTICS OPERATIONS
    # ============================================================================
    
    async def get_storage_usage_by_category(
        self,
        db: AsyncSession,
        *,
        user_id: Union[str, UUID]
    ) -> Dict[str, Any]:
        """Get storage usage breakdown by content category"""
        
        result = await db.execute(
            select(
                UserStorageUsage.content_category,
                func.count(UserStorageUsage.id).label('file_count'),
                func.sum(UserStorageUsage.file_size).label('total_size'),
                func.avg(UserStorageUsage.file_size).label('avg_size'),
                func.max(UserStorageUsage.upload_date).label('last_upload')
            )
            .where(
                and_(
                    UserStorageUsage.user_id == str(user_id),
                    UserStorageUsage.is_deleted == False
                )
            )
            .group_by(UserStorageUsage.content_category)
        )
        
        category_stats = {}
        total_files = 0
        total_size = 0
        
        for row in result:
            category_stats[row.content_category] = {
                "file_count": row.file_count,
                "total_size_bytes": row.total_size or 0,
                "total_size_mb": round((row.total_size or 0) / 1024 / 1024, 2),
                "avg_size_mb": round((row.avg_size or 0) / 1024 / 1024, 2),
                "last_upload": row.last_upload.isoformat() if row.last_upload else None
            }
            total_files += row.file_count
            total_size += (row.total_size or 0)
        
        return {
            "by_category": category_stats,
            "totals": {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "total_size_gb": round(total_size / 1024 / 1024 / 1024, 3)
            }
        }
    
    async def get_storage_analytics(
        self,
        db: AsyncSession,
        *,
        user_id: Union[str, UUID],
        days: int = 30
    ) -> Dict[str, Any]:
        """Get detailed storage analytics for specified period"""
        
        # Date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Upload trends over time
        upload_trends_result = await db.execute(
            select(
                func.date(UserStorageUsage.upload_date).label('date'),
                func.count(UserStorageUsage.id).label('uploads'),
                func.sum(UserStorageUsage.file_size).label('bytes_uploaded')
            )
            .where(
                and_(
                    UserStorageUsage.user_id == str(user_id),
                    UserStorageUsage.upload_date >= start_date,
                    UserStorageUsage.is_deleted == False
                )
            )
            .group_by(func.date(UserStorageUsage.upload_date))
            .order_by(func.date(UserStorageUsage.upload_date))
        )
        
        daily_stats = []
        total_uploads = 0
        total_bytes = 0
        
        for row in upload_trends_result:
            daily_stats.append({
                "date": row.date.isoformat(),
                "uploads": row.uploads,
                "bytes_uploaded": row.bytes_uploaded,
                "mb_uploaded": round(row.bytes_uploaded / 1024 / 1024, 2)
            })
            total_uploads += row.uploads
            total_bytes += row.bytes_uploaded
        
        # Most accessed files
        popular_files_result = await db.execute(
            select(UserStorageUsage)
            .where(
                and_(
                    UserStorageUsage.user_id == str(user_id),
                    UserStorageUsage.is_deleted == False,
                    UserStorageUsage.access_count > 0
                )
            )
            .order_by(desc(UserStorageUsage.access_count))
            .limit(10)
        )
        
        popular_files = []
        for file in popular_files_result.scalars():
            popular_files.append({
                "id": str(file.id),
                "filename": file.original_filename,
                "content_category": file.content_category,
                "access_count": file.access_count,
                "file_size_mb": file.file_size_mb,
                "last_accessed": file.last_accessed.isoformat() if file.last_accessed else None
            })
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "summary": {
                "total_uploads": total_uploads,
                "total_bytes_uploaded": total_bytes,
                "total_mb_uploaded": round(total_bytes / 1024 / 1024, 2),
                "avg_daily_uploads": round(total_uploads / days, 1) if days > 0 else 0,
                "avg_daily_mb": round((total_bytes / 1024 / 1024) / days, 2) if days > 0 else 0
            },
            "daily_trends": daily_stats,
            "popular_files": popular_files
        }
    
    async def get_campaign_storage_usage(
        self,
        db: AsyncSession,
        *,
        user_id: Union[str, UUID],
        campaign_id: Union[str, UUID]
    ) -> Dict[str, Any]:
        """Get storage usage for a specific campaign"""
        
        result = await db.execute(
            select(
                func.count(UserStorageUsage.id).label('file_count'),
                func.sum(UserStorageUsage.file_size).label('total_size'),
                UserStorageUsage.content_category
            )
            .where(
                and_(
                    UserStorageUsage.user_id == str(user_id),
                    UserStorageUsage.campaign_id == str(campaign_id),
                    UserStorageUsage.is_deleted == False
                )
            )
            .group_by(UserStorageUsage.content_category)
        )
        
        campaign_usage = {
            "campaign_id": str(campaign_id),
            "by_category": {},
            "totals": {
                "total_files": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0
            }
        }
        
        for row in result:
            category_data = {
                "file_count": row.file_count,
                "total_size_bytes": row.total_size or 0,
                "total_size_mb": round((row.total_size or 0) / 1024 / 1024, 2)
            }
            
            campaign_usage["by_category"][row.content_category] = category_data
            campaign_usage["totals"]["total_files"] += row.file_count
            campaign_usage["totals"]["total_size_bytes"] += (row.total_size or 0)
        
        campaign_usage["totals"]["total_size_mb"] = round(
            campaign_usage["totals"]["total_size_bytes"] / 1024 / 1024, 2
        )
        
        return campaign_usage
    
    # ============================================================================
    # QUOTA MANAGEMENT OPERATIONS
    # ============================================================================
    
    async def calculate_user_storage_usage(
        self,
        db: AsyncSession,
        *,
        user_id: Union[str, UUID]
    ) -> Dict[str, Any]:
        """Calculate actual storage usage for quota verification"""
        
        result = await db.execute(
            select(
                func.count(UserStorageUsage.id).label('total_files'),
                func.sum(UserStorageUsage.file_size).label('total_size'),
                func.sum(
                    func.case(
                        (UserStorageUsage.is_deleted == True, UserStorageUsage.file_size),
                        else_=0
                    )
                ).label('deleted_size')
            )
            .where(UserStorageUsage.user_id == str(user_id))
        )
        
        row = result.first()
        
        if not row:
            return {
                "total_files": 0,
                "active_files": 0,
                "deleted_files": 0,
                "total_size_bytes": 0,
                "active_size_bytes": 0,
                "deleted_size_bytes": 0,
                "total_size_mb": 0,
                "active_size_mb": 0,
                "deleted_size_mb": 0
            }
        
        total_size = row.total_size or 0
        deleted_size = row.deleted_size or 0
        active_size = total_size - deleted_size
        
        # Get active file count
        active_result = await db.execute(
            select(func.count(UserStorageUsage.id))
            .where(
                and_(
                    UserStorageUsage.user_id == str(user_id),
                    UserStorageUsage.is_deleted == False
                )
            )
        )
        active_files = active_result.scalar()
        
        return {
            "total_files": row.total_files,
            "active_files": active_files,
            "deleted_files": row.total_files - active_files,
            "total_size_bytes": total_size,
            "active_size_bytes": active_size,
            "deleted_size_bytes": deleted_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "active_size_mb": round(active_size / 1024 / 1024, 2),
            "deleted_size_mb": round(deleted_size / 1024 / 1024, 2)
        }
    
    async def cleanup_deleted_files(
        self,
        db: AsyncSession,
        *,
        user_id: Union[str, UUID],
        older_than_days: int = 30
    ) -> Dict[str, Any]:
        """Permanently remove old deleted files from tracking"""
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
        
        # Get files to be cleaned up
        files_to_cleanup = await db.execute(
            select(UserStorageUsage)
            .where(
                and_(
                    UserStorageUsage.user_id == str(user_id),
                    UserStorageUsage.is_deleted == True,
                    UserStorageUsage.deleted_date <= cutoff_date
                )
            )
        )
        
        cleanup_files = files_to_cleanup.scalars().all()
        
        if not cleanup_files:
            return {
                "cleaned_up": 0,
                "bytes_freed": 0,
                "mb_freed": 0
            }
        
        # Calculate freed space
        total_freed = sum(file.file_size for file in cleanup_files)
        
        # Delete the records
        await db.execute(
            delete(UserStorageUsage)
            .where(
                and_(
                    UserStorageUsage.user_id == str(user_id),
                    UserStorageUsage.is_deleted == True,
                    UserStorageUsage.deleted_date <= cutoff_date
                )
            )
        )
        
        await db.commit()
        
        logger.info(
            f"Cleaned up {len(cleanup_files)} deleted files for user {user_id}, "
            f"freed {round(total_freed / 1024 / 1024, 2)}MB"
        )
        
        return {
            "cleaned_up": len(cleanup_files),
            "bytes_freed": total_freed,
            "mb_freed": round(total_freed / 1024 / 1024, 2)
        }
    
    # ============================================================================
    # ADMIN OPERATIONS
    # ============================================================================
    
    async def get_storage_overview(
        self,
        db: AsyncSession,
        *,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get system-wide storage overview for admins"""
        
        # Get user storage summaries
        result = await db.execute(
            select(
                UserStorageUsage.user_id,
                func.count(UserStorageUsage.id).label('file_count'),
                func.sum(UserStorageUsage.file_size).label('total_size'),
                func.max(UserStorageUsage.upload_date).label('last_upload')
            )
            .where(UserStorageUsage.is_deleted == False)
            .group_by(UserStorageUsage.user_id)
            .order_by(desc(func.sum(UserStorageUsage.file_size)))
            .offset(offset)
            .limit(limit)
        )
        
        user_summaries = []
        total_system_size = 0
        total_system_files = 0
        
        for row in result:
            user_size = row.total_size or 0
            user_summaries.append({
                "user_id": row.user_id,
                "file_count": row.file_count,
                "total_size_bytes": user_size,
                "total_size_mb": round(user_size / 1024 / 1024, 2),
                "last_upload": row.last_upload.isoformat() if row.last_upload else None
            })
            total_system_size += user_size
            total_system_files += row.file_count
        
        # Get system totals
        system_totals_result = await db.execute(
            select(
                func.count(UserStorageUsage.id).label('total_files'),
                func.sum(UserStorageUsage.file_size).label('total_size'),
                func.count(func.distinct(UserStorageUsage.user_id)).label('total_users')
            )
            .where(UserStorageUsage.is_deleted == False)
        )
        
        system_totals = system_totals_result.first()
        
        return {
            "system_totals": {
                "total_files": system_totals.total_files,
                "total_size_bytes": system_totals.total_size or 0,
                "total_size_mb": round((system_totals.total_size or 0) / 1024 / 1024, 2),
                "total_size_gb": round((system_totals.total_size or 0) / 1024 / 1024 / 1024, 3),
                "total_users": system_totals.total_users
            },
            "user_summaries": user_summaries,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "returned": len(user_summaries)
            }
        }

# ✅ FIXED: Create singleton instance with correct typing
user_storage_crud = UserStorageCRUD()