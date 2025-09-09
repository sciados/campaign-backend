# ==============================================================================
# 4. FILE SERVICE
# ==============================================================================

# src/storage/services/file_service.py
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from src.users.services.user_storage_crud import UserStorageCRUD
from .cloudflare_service import CloudflareService
import logging

logger = logging.getLogger(__name__)

class FileService:
    """File management service"""
    
    def __init__(self):
        self.storage_crud = UserStorageCRUD()
        self.cloudflare_service = CloudflareService()
    
    async def upload_file(
        self,
        db: AsyncSession,
        user_id: str,
        file_data: bytes,
        original_filename: str,
        content_type: str,
        campaign_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Upload file with database tracking"""
        try:
            # Generate unique file path
            file_extension = original_filename.split('.')[-1] if '.' in original_filename else 'bin'
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = f"user_{user_id}/{datetime.now().strftime('%Y/%m')}/{unique_filename}"
            
            # Determine content category
            content_category = self._determine_content_category(content_type)
            
            # Upload to Cloudflare R2
            upload_result = await self.cloudflare_service.upload_file(
                file_data=file_data,
                file_path=file_path,
                content_type=content_type,
                metadata=metadata
            )
            
            if not upload_result["success"]:
                return upload_result
            
            # Create database record
            storage_record = await self.storage_crud.create_storage_record(
                db=db,
                user_id=user_id,
                file_path=file_path,
                original_filename=original_filename,
                file_size=len(file_data),
                content_type=content_type,
                content_category=content_category,
                campaign_id=campaign_id,
                metadata=metadata
            )
            
            return {
                "success": True,
                "file_id": str(storage_record.id),
                "file_path": file_path,
                "public_url": upload_result["public_url"],
                "size": len(file_data),
                "content_category": content_category
            }
            
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def download_file(
        self,
        db: AsyncSession,
        user_id: str,
        file_id: str
    ) -> Dict[str, Any]:
        """Download file with access tracking"""
        try:
            # Get file record
            file_record = await self.storage_crud.get(db=db, id=file_id)
            
            if not file_record or file_record.user_id != user_id:
                return {
                    "success": False,
                    "error": "File not found or access denied"
                }
            
            if file_record.is_deleted:
                return {
                    "success": False,
                    "error": "File has been deleted"
                }
            
            # Download from R2
            download_result = await self.cloudflare_service.download_file(file_record.file_path)
            
            if download_result["success"]:
                # Update access tracking
                await self.storage_crud.update_file_access(
                    db=db,
                    file_id=file_id,
                    user_id=user_id
                )
            
            return download_result
            
        except Exception as e:
            logger.error(f"File download failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_file(
        self,
        db: AsyncSession,
        user_id: str,
        file_id: str
    ) -> Dict[str, Any]:
        """Delete file (mark as deleted)"""
        try:
            # Mark as deleted in database
            delete_result = await self.storage_crud.mark_file_deleted(
                db=db,
                file_id=file_id,
                user_id=user_id
            )
            
            return {
                "success": True,
                "file_id": file_id,
                "size_freed": delete_result["file_size"]
            }
            
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _determine_content_category(self, content_type: str) -> str:
        """Determine content category from MIME type"""
        if content_type.startswith('image/'):
            return 'image'
        elif content_type.startswith('video/'):
            return 'video'
        elif content_type.startswith('audio/'):
            return 'audio'
        elif content_type in ['application/pdf', 'application/msword', 'text/plain']:
            return 'document'
        else:
            return 'other'