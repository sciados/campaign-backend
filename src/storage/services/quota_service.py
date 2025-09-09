# ============================================================================
# src/storage/services/quota_service.py
# ============================================================================

"""
Storage Quota Management Service

Handles storage quotas, usage tracking, and tier management.
"""

import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from src.users.services.user_storage_crud import UserStorageCRUD
from src.core.config.storage_config import storage_config

logger = logging.getLogger(__name__)

class QuotaService:
    """Storage quota management service"""
    
    def __init__(self):
        self.storage_crud = UserStorageCRUD()
        
        # Storage tier limits (bytes)
        self.tier_limits = {
            "free": 1024 * 1024 * 100,      # 100 MB
            "pro": 1024 * 1024 * 1024 * 5,  # 5 GB
            "enterprise": 1024 * 1024 * 1024 * 50  # 50 GB
        }
        
        # File size limits per tier (bytes)
        self.file_size_limits = {
            "free": 1024 * 1024 * 10,       # 10 MB per file
            "pro": 1024 * 1024 * 100,       # 100 MB per file
            "enterprise": 1024 * 1024 * 500  # 500 MB per file
        }
    
    async def check_quota(
        self,
        db: AsyncSession,
        user_id: str,
        file_size: int,
        user_tier: str = "free"
    ) -> Dict[str, Any]:
        """Check if user has sufficient quota for file upload"""
        try:
            # Get current usage
            usage = await self.storage_crud.calculate_user_storage_usage(
                db=db,
                user_id=user_id
            )
            
            current_usage = usage["active_size_bytes"]
            tier_limit = self.tier_limits.get(user_tier, self.tier_limits["free"])
            file_limit = self.file_size_limits.get(user_tier, self.file_size_limits["free"])
            
            # Check file size limit
            if file_size > file_limit:
                return {
                    "success": False,
                    "error": "file_too_large",
                    "message": f"File size exceeds {file_limit // 1024 // 1024}MB limit for {user_tier} tier",
                    "file_size": file_size,
                    "file_limit": file_limit
                }
            
            # Check total quota
            if current_usage + file_size > tier_limit:
                return {
                    "success": False,
                    "error": "quota_exceeded",
                    "message": f"Upload would exceed {tier_limit // 1024 // 1024}MB quota for {user_tier} tier",
                    "current_usage": current_usage,
                    "file_size": file_size,
                    "tier_limit": tier_limit,
                    "available_space": tier_limit - current_usage
                }
            
            # Calculate usage percentage
            usage_percentage = ((current_usage + file_size) / tier_limit) * 100
            
            return {
                "success": True,
                "current_usage": current_usage,
                "file_size": file_size,
                "new_usage": current_usage + file_size,
                "tier_limit": tier_limit,
                "usage_percentage": round(usage_percentage, 2),
                "available_space": tier_limit - current_usage - file_size,
                "is_near_limit": usage_percentage > 80
            }
            
        except Exception as e:
            logger.error(f"Quota check failed: {e}")
            return {
                "success": False,
                "error": "quota_check_failed",
                "message": str(e)
            }
    
    async def get_quota_status(
        self,
        db: AsyncSession,
        user_id: str,
        user_tier: str = "free"
    ) -> Dict[str, Any]:
        """Get current quota status for user"""
        try:
            usage = await self.storage_crud.calculate_user_storage_usage(
                db=db,
                user_id=user_id
            )
            
            tier_limit = self.tier_limits.get(user_tier, self.tier_limits["free"])
            current_usage = usage["active_size_bytes"]
            usage_percentage = (current_usage / tier_limit) * 100
            
            return {
                "user_id": user_id,
                "tier": user_tier,
                "current_usage_bytes": current_usage,
                "current_usage_mb": round(current_usage / 1024 / 1024, 2),
                "tier_limit_bytes": tier_limit,
                "tier_limit_mb": round(tier_limit / 1024 / 1024, 2),
                "available_bytes": tier_limit - current_usage,
                "available_mb": round((tier_limit - current_usage) / 1024 / 1024, 2),
                "usage_percentage": round(usage_percentage, 2),
                "status": "full" if usage_percentage >= 100 else "near_full" if usage_percentage >= 80 else "normal",
                "file_count": usage["active_files"],
                "deleted_files": usage["deleted_files"]
            }
            
        except Exception as e:
            logger.error(f"Failed to get quota status: {e}")
            return {
                "error": str(e),
                "user_id": user_id,
                "status": "error"
            }
    
    async def cleanup_deleted_files(
        self,
        db: AsyncSession,
        user_id: str,
        older_than_days: int = 30
    ) -> Dict[str, Any]:
        """Clean up old deleted files to free space"""
        try:
            result = await self.storage_crud.cleanup_deleted_files(
                db=db,
                user_id=user_id,
                older_than_days=older_than_days
            )
            
            return {
                "success": True,
                "files_cleaned": result["cleaned_up"],
                "space_freed_bytes": result["bytes_freed"],
                "space_freed_mb": result["mb_freed"],
                "cleanup_age_days": older_than_days
            }
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_tier_info(self, tier: str = "free") -> Dict[str, Any]:
        """Get information about storage tier limits"""
        limit_bytes = self.tier_limits.get(tier, self.tier_limits["free"])
        file_limit_bytes = self.file_size_limits.get(tier, self.file_size_limits["free"])
        
        return {
            "tier": tier,
            "storage_limit_bytes": limit_bytes,
            "storage_limit_mb": round(limit_bytes / 1024 / 1024, 2),
            "storage_limit_gb": round(limit_bytes / 1024 / 1024 / 1024, 2),
            "file_size_limit_bytes": file_limit_bytes,
            "file_size_limit_mb": round(file_limit_bytes / 1024 / 1024, 2),
            "features": self._get_tier_features(tier)
        }
    
    def _get_tier_features(self, tier: str) -> list:
        """Get features available for tier"""
        features = {
            "free": [
                "Basic file upload/download",
                "100MB total storage",
                "10MB max file size",
                "Standard support"
            ],
            "pro": [
                "Advanced file management",
                "5GB total storage", 
                "100MB max file size",
                "Priority support",
                "Media generation",
                "Advanced analytics"
            ],
            "enterprise": [
                "Unlimited file management",
                "50GB total storage",
                "500MB max file size", 
                "Dedicated support",
                "Advanced media generation",
                "Custom integrations",
                "API access",
                "Advanced analytics"
            ]
        }
        
        return features.get(tier, features["free"])