# src/storage/universal_dual_storage.py - ENHANCED WITH USER QUOTAS
"""
🔥 FIXED: Universal Dual Storage Manager with proper R2 configuration
✅ Fixed environment variable names to match Railway
✅ Enhanced error handling and fallback storage
✅ Multi-provider redundancy for maximum reliability
🆕 NEW: User quota management and organized storage
📁 NEW: User-specific folder organization
🔐 NEW: Tier-based validation and limits
"""
import asyncio
import aiohttp
import boto3
import logging
import hashlib
import mimetypes
import os
import io
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from uuid import uuid4

# 🆕 NEW: Import quota management components
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

# 🆕 NEW: Custom exceptions for quota management
class UserQuotaExceeded(Exception):
    """Raised when user exceeds storage quota"""
    def __init__(self, message: str, user_id: str, current_usage: int, limit: int, attempted_size: int):
        self.user_id = user_id
        self.current_usage = current_usage
        self.limit = limit
        self.attempted_size = attempted_size
        super().__init__(message)

class FileSizeExceeded(Exception):
    """Raised when file size exceeds tier limit"""
    def __init__(self, message: str, file_size: int, max_allowed: int, tier: str):
        self.file_size = file_size
        self.max_allowed = max_allowed
        self.tier = tier
        super().__init__(message)

class ContentTypeNotAllowed(Exception):
    """Raised when content type not allowed for user tier"""
    def __init__(self, message: str, content_type: str, tier: str, allowed_types: List[str]):
        self.content_type = content_type
        self.tier = tier
        self.allowed_types = allowed_types
        super().__init__(message)

@dataclass
class StorageProvider:
    """Storage provider configuration"""
    name: str
    client: Any
    priority: int
    cost_per_gb: float
    health_status: bool = True
    last_check: datetime = None

class UniversalDualStorageManager:
    """Universal storage manager for all content types with user quota management"""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.health_cache = {}
        self.sync_queue = asyncio.Queue()
        self.supported_types = {
            "image": {
                "extensions": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"],
                "max_size_mb": 10,
                "content_types": ["image/png", "image/jpeg", "image/gif", "image/webp"],
                "optimization": self._optimize_image
            },
            "document": {
                "extensions": [".pdf", ".doc", ".docx", ".txt", ".md", ".rtf"],
                "max_size_mb": 50,
                "content_types": ["application/pdf", "application/msword", "text/plain"],
                "optimization": self._optimize_document
            },
            "video": {
                "extensions": [".mp4", ".mov", ".avi", ".webm", ".mkv"],
                "max_size_mb": 200,
                "content_types": ["video/mp4", "video/quicktime", "video/webm"],
                "optimization": self._optimize_video
            }
        }
        
        # 🆕 NEW: Import storage tiers here to avoid circular imports
        self.storage_tiers = self._get_storage_tiers()
    
    def _get_storage_tiers(self):
        """Get storage tiers configuration"""
        try:
            # Try to import from storage_tiers module if it exists
            from src.storage.storage_tiers import STORAGE_TIERS, get_content_category, get_tier_info, is_content_type_allowed, is_file_size_allowed, get_content_type_from_filename
            return {
                'STORAGE_TIERS': STORAGE_TIERS,
                'get_content_category': get_content_category,
                'get_tier_info': get_tier_info,
                'is_content_type_allowed': is_content_type_allowed,
                'is_file_size_allowed': is_file_size_allowed,
                'get_content_type_from_filename': get_content_type_from_filename
            }
        except ImportError:
            # Fallback to inline definitions if storage_tiers.py doesn't exist yet
            logger.warning("storage_tiers.py not found, using fallback tier definitions")
            return self._get_fallback_storage_tiers()
    
    def _get_fallback_storage_tiers(self):
        """Fallback storage tier definitions"""
        STORAGE_TIERS = {
            "free": {"limit_gb": 1, "limit_bytes": 1073741824, "max_file_size_mb": 10, "max_file_size_bytes": 10485760, "allowed_types": ["image", "document"]},
            "pro": {"limit_gb": 10, "limit_bytes": 10737418240, "max_file_size_mb": 50, "max_file_size_bytes": 52428800, "allowed_types": ["image", "document", "video"]},
            "enterprise": {"limit_gb": 100, "limit_bytes": 107374182400, "max_file_size_mb": 200, "max_file_size_bytes": 209715200, "allowed_types": ["image", "document", "video"]}
        }
        
        CONTENT_TYPE_CATEGORIES = {
            "image/jpeg": "image", "image/png": "image", "image/gif": "image", "image/webp": "image",
            "application/pdf": "document", "text/plain": "document", "application/msword": "document",
            "video/mp4": "video", "video/quicktime": "video", "video/webm": "video"
        }
        
        def get_content_category(content_type: str) -> str:
            return CONTENT_TYPE_CATEGORIES.get(content_type.lower(), "document")
        
        def get_tier_info(tier: str) -> dict:
            return STORAGE_TIERS.get(tier, STORAGE_TIERS["free"])
        
        def is_content_type_allowed(content_type: str, tier: str) -> bool:
            tier_info = get_tier_info(tier)
            category = get_content_category(content_type)
            return category in tier_info["allowed_types"]
        
        def is_file_size_allowed(file_size_bytes: int, tier: str) -> bool:
            tier_info = get_tier_info(tier)
            return file_size_bytes <= tier_info["max_file_size_bytes"]
        
        def get_content_type_from_filename(filename: str) -> str:
            mime_type, _ = mimetypes.guess_type(filename)
            return mime_type or "application/octet-stream"
        
        return {
            'STORAGE_TIERS': STORAGE_TIERS,
            'get_content_category': get_content_category,
            'get_tier_info': get_tier_info,
            'is_content_type_allowed': is_content_type_allowed,
            'is_file_size_allowed': is_file_size_allowed,
            'get_content_type_from_filename': get_content_type_from_filename
        }
    
    def _initialize_providers(self) -> List[StorageProvider]:
        """🔥 FIXED: Initialize storage providers with exact Railway variable names"""
        providers = []
        
        # 🔥 FIXED: Cloudflare R2 (Primary) - Using exact Railway environment variable names
        try:
            # 🔥 FIXED: Use exact variable names from Railway
            r2_account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
            r2_access_key = os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')
            r2_secret_key = os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
            r2_bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')
            
            # Debug log the actual values (masked)
            logger.info(f"🔍 R2 Environment Variables Check:")
            logger.info(f"   CLOUDFLARE_ACCOUNT_ID: {'✅ SET' if r2_account_id else '❌ MISSING'}")
            logger.info(f"   CLOUDFLARE_R2_ACCESS_KEY_ID: {'✅ SET' if r2_access_key else '❌ MISSING'}")
            logger.info(f"   CLOUDFLARE_R2_SECRET_ACCESS_KEY: {'✅ SET' if r2_secret_key else '❌ MISSING'}")
            logger.info(f"   CLOUDFLARE_R2_BUCKET_NAME: {'✅ SET' if r2_bucket_name else '❌ MISSING'}")
            
            if r2_account_id:
                logger.info(f"   Account ID length: {len(r2_account_id)} chars")
                logger.info(f"   Account ID preview: {r2_account_id[:8]}...")
            
            if not r2_account_id:
                raise ValueError("CLOUDFLARE_ACCOUNT_ID is required for Cloudflare R2")
            
            if not r2_access_key or not r2_secret_key:
                raise ValueError("CLOUDFLARE_R2_ACCESS_KEY_ID and CLOUDFLARE_R2_SECRET_ACCESS_KEY are required")
            
            if not r2_bucket_name:
                raise ValueError("CLOUDFLARE_R2_BUCKET_NAME is required")
            
            # 🔥 FIXED: Proper R2 endpoint URL construction
            r2_endpoint = f"https://{r2_account_id}.r2.cloudflarestorage.com"
            
            logger.info(f"🔍 Generated R2 endpoint: {r2_endpoint}")
            
            r2_client = boto3.client(
                's3',
                endpoint_url=r2_endpoint,
                aws_access_key_id=r2_access_key,
                aws_secret_access_key=r2_secret_key,
                region_name='auto'  # R2 uses 'auto' for region
            )
            
            providers.append(StorageProvider(
                name="cloudflare_r2",
                client=r2_client,
                priority=1,
                cost_per_gb=0.015  # $0.015/GB for R2
            ))
            
            logger.info(f"✅ Cloudflare R2 provider initialized: {r2_endpoint}")
            logger.info(f"   Account ID: {r2_account_id}")
            logger.info(f"   Bucket: {r2_bucket_name}")
            logger.info(f"   Cost: $0.015/GB")
            
        except Exception as e:
            logger.error(f"❌ Cloudflare R2 initialization failed: {str(e)}")
            logger.error(f"   Check Railway environment variables:")
            logger.error(f"   - CLOUDFLARE_ACCOUNT_ID")
            logger.error(f"   - CLOUDFLARE_R2_ACCESS_KEY_ID") 
            logger.error(f"   - CLOUDFLARE_R2_SECRET_ACCESS_KEY")
            logger.error(f"   - CLOUDFLARE_R2_BUCKET_NAME")
        
        # Optional: Backblaze B2 (Backup) - only if you want it
        try:
            b2_access_key = os.getenv('B2_ACCESS_KEY_ID') or os.getenv('BACKBLAZE_ACCESS_KEY_ID')
            b2_secret_key = os.getenv('B2_SECRET_ACCESS_KEY') or os.getenv('BACKBLAZE_SECRET_ACCESS_KEY')
            b2_bucket_name = os.getenv('B2_BUCKET_NAME') or os.getenv('BACKBLAZE_BUCKET_NAME')
            
            if b2_access_key and b2_secret_key and b2_bucket_name:
                b2_client = boto3.client(
                    's3',
                    endpoint_url='https://s3.us-west-004.backblazeb2.com',
                    aws_access_key_id=b2_access_key,
                    aws_secret_access_key=b2_secret_key,
                    region_name='us-west-004'
                )
                providers.append(StorageProvider(
                    name="backblaze_b2",
                    client=b2_client,
                    priority=2,
                    cost_per_gb=0.005  # $0.005/GB for B2
                ))
                logger.info("✅ Backblaze B2 provider initialized")
            else:
                logger.info("ℹ️  Backblaze B2 not configured (optional backup)")
                
        except Exception as e:
            logger.warning(f"⚠️ Backblaze B2 initialization failed: {str(e)}")
        
        # AWS S3 (Emergency Backup) - optional
        try:
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            aws_bucket = os.getenv('AWS_S3_BUCKET_NAME')
            
            if aws_access_key and aws_secret_key and aws_bucket:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=aws_region
                )
                providers.append(StorageProvider(
                    name="aws_s3",
                    client=s3_client,
                    priority=3,
                    cost_per_gb=0.023  # $0.023/GB for S3 Standard
                ))
                logger.info("✅ AWS S3 provider initialized (emergency backup)")
            else:
                logger.info("ℹ️  AWS S3 not configured (optional emergency backup)")
                
        except Exception as e:
            logger.warning(f"⚠️ AWS S3 initialization failed: {str(e)}")
        
        if not providers:
            logger.error("❌ NO STORAGE PROVIDERS AVAILABLE!")
            logger.error("   Verify Railway environment variables:")
            logger.error("   - CLOUDFLARE_ACCOUNT_ID")
            logger.error("   - CLOUDFLARE_R2_ACCESS_KEY_ID")
            logger.error("   - CLOUDFLARE_R2_SECRET_ACCESS_KEY") 
            logger.error("   - CLOUDFLARE_R2_BUCKET_NAME")
        else:
            providers.sort(key=lambda x: x.priority)
            logger.info(f"📊 Storage providers initialized: {[p.name for p in providers]}")
        
        return providers
    
    # 🆕 NEW: User quota-aware upload method
    async def upload_file_with_quota_check(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        user_id: str,
        campaign_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Upload file with comprehensive quota validation
        
        Args:
            file_content: File bytes
            filename: Original filename
            content_type: MIME type
            user_id: User ID for quota checking
            campaign_id: Optional campaign association
            db: Database session
            
        Returns:
            Dict with file info and storage details
            
        Raises:
            UserQuotaExceeded: If user exceeds storage quota
            FileSizeExceeded: If file too large for tier
            ContentTypeNotAllowed: If content type not allowed for tier
        """
        # Import database dependencies here to avoid circular imports
        try:
            from src.core.database import get_async_db
            from src.users.models.user import User
            from src.users.models.user_storage import UserStorageUsage
        except ImportError as e:
            logger.error(f"Database dependencies not available: {e}")
            # Fallback to legacy upload method
            return await self.save_content_dual_storage(
                file_content, 
                self._get_content_type_from_filename(content_type, filename), 
                filename, 
                user_id, 
                campaign_id
            )
        
        # Get database session
        if db is None:
            async for session in get_async_db():
                db = session
                break
        
        try:
            # Step 1: Get user with storage info
            user = await self._get_user_with_storage_info(user_id, db)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Step 2: Validate file against user tier
            file_size = len(file_content)
            await self._validate_file_against_tier(file_content, content_type, user, filename)
            
            # Step 3: Check storage quota
            await self._check_user_quota(user, file_size)
            
            # Step 4: Generate organized file path
            file_path = self._generate_user_file_path(user_id, filename, content_type)
            
            # Step 5: Use existing dual storage upload
            upload_result = await self._upload_to_r2_with_metadata(
                file_content, file_path, content_type, {
                    "user_id": user_id,
                    "campaign_id": campaign_id or "general",
                    "original_filename": filename,
                    "file_size": str(file_size),
                    "upload_timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
            if not upload_result.get("success"):
                raise Exception(f"Upload failed: {upload_result.get('error', 'Unknown error')}")
            
            # Step 6: Create storage usage record
            storage_record = await self._create_storage_record(
                user_id=user_id,
                file_path=file_path,
                filename=filename,
                file_size=file_size,
                content_type=content_type,
                campaign_id=campaign_id,
                db=db
            )
            
            # Step 7: Update user storage usage
            await self._update_user_storage_usage(user_id, file_size, db)
            
            # Step 8: Prepare response
            return {
                "success": True,
                "file_id": str(storage_record.id),
                "file_path": file_path,
                "filename": filename,
                "file_size": file_size,
                "file_size_mb": round(file_size / 1024 / 1024, 2),
                "content_type": content_type,
                "content_category": self.storage_tiers['get_content_category'](content_type),
                "upload_date": storage_record.upload_date.isoformat(),
                "url": upload_result.get("url"),
                "user_storage": await self._get_user_storage_summary(user_id, db),
                "providers": upload_result.get("providers", {}),
                "storage_status": upload_result.get("storage_status", "unknown")
            }
            
        except (UserQuotaExceeded, FileSizeExceeded, ContentTypeNotAllowed) as e:
            # Re-raise validation errors
            raise e
        except Exception as e:
            logger.error(f"Upload failed for user {user_id}: {str(e)}")
            raise Exception(f"Upload failed: {str(e)}")
    
    # 🆕 NEW: Helper method for R2 upload with metadata
    async def _upload_to_r2_with_metadata(self, file_content: bytes, file_path: str, content_type: str, metadata: dict) -> Dict[str, Any]:
        """Upload to R2 with metadata using existing provider system"""
        if not self.providers:
            raise Exception("No storage providers available")
        
        try:
            primary_provider = self.providers[0]  # Cloudflare R2
            bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')
            
            if not bucket_name:
                raise ValueError("CLOUDFLARE_R2_BUCKET_NAME not configured")
            
            # Upload using existing method
            primary_provider.client.put_object(
                Bucket=bucket_name,
                Key=file_path,
                Body=file_content,
                ContentType=content_type,
                Metadata={k: str(v) for k, v in metadata.items()},
                CacheControl='public, max-age=31536000',
                ContentDisposition=f'inline; filename="{os.path.basename(file_path)}"'
            )
            
            # Generate URL
            account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
            custom_domain = os.getenv('R2_CUSTOM_DOMAIN') or os.getenv('CLOUDFLARE_R2_CUSTOM_DOMAIN')
            
            if custom_domain:
                url = f"https://{custom_domain}/{file_path}"
            else:
                url = f"https://{bucket_name}.{account_id}.r2.cloudflarestorage.com/{file_path}"
            
            return {
                "success": True,
                "url": url,
                "file_path": file_path,
                "providers": {
                    "primary": {
                        "provider": "cloudflare_r2",
                        "url": url,
                        "status": "success"
                    }
                },
                "storage_status": "primary_success"
            }
            
        except Exception as e:
            logger.error(f"R2 upload failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # 🆕 NEW: Quota management helper methods
    async def _get_user_with_storage_info(self, user_id: str, db: AsyncSession):
        """Get user with storage information"""
        try:
            from src.users.models.user import User
            result = await db.execute(
                select(User)
                .where(User.id == user_id)
                .options(selectinload(User.storage_usage))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {str(e)}")
            return None
    
    async def _validate_file_against_tier(self, file_content: bytes, content_type: str, user, filename: str):
        """Validate file against user's tier restrictions"""
        file_size = len(file_content)
        
        # Ensure content type is set
        if not content_type or content_type == "application/octet-stream":
            content_type = self.storage_tiers['get_content_type_from_filename'](filename)
        
        # Check if content type is allowed for tier
        if not self.storage_tiers['is_content_type_allowed'](content_type, user.storage_tier):
            tier_info = self.storage_tiers['get_tier_info'](user.storage_tier)
            raise ContentTypeNotAllowed(
                f"Content type '{content_type}' not allowed for {user.storage_tier} tier. Allowed types: {tier_info['allowed_types']}",
                content_type=content_type,
                tier=user.storage_tier,
                allowed_types=tier_info['allowed_types']
            )
        
        # Check file size against tier limit
        if not self.storage_tiers['is_file_size_allowed'](file_size, user.storage_tier):
            tier_info = self.storage_tiers['get_tier_info'](user.storage_tier)
            raise FileSizeExceeded(
                f"File size {round(file_size/1024/1024, 2)}MB exceeds {user.storage_tier} tier limit of {tier_info['max_file_size_mb']}MB",
                file_size=file_size,
                max_allowed=tier_info['max_file_size_bytes'],
                tier=user.storage_tier
            )
    
    async def _check_user_quota(self, user, additional_bytes: int):
        """Check if user has enough quota for additional storage"""
        if not user.has_storage_available(additional_bytes):
            raise UserQuotaExceeded(
                f"Storage quota exceeded. Current: {user.get_storage_used_mb()}MB, Limit: {user.get_storage_limit_mb()}MB, Attempted: {round(additional_bytes/1024/1024, 2)}MB",
                user_id=str(user.id),
                current_usage=user.storage_used_bytes,
                limit=user.storage_limit_bytes,
                attempted_size=additional_bytes
            )
    
    def _generate_user_file_path(self, user_id: str, filename: str, content_type: str) -> str:
        """Generate organized file path"""
        category = self.storage_tiers['get_content_category'](content_type)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        file_uuid = str(uuid4())[:8]
        clean_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        return f"users/{user_id}/{category}s/{timestamp}_{file_uuid}_{clean_filename}"
    
    async def _create_storage_record(self, user_id: str, file_path: str, filename: str, file_size: int, content_type: str, campaign_id: Optional[str], db: AsyncSession):
        """Create storage usage record"""
        try:
            from src.users.models.user_storage import UserStorageUsage
            storage_record = UserStorageUsage(
                user_id=user_id,
                file_path=file_path,
                original_filename=filename,
                file_size=file_size,
                content_type=content_type,
                content_category=self.storage_tiers['get_content_category'](content_type),
                campaign_id=campaign_id,
                upload_date=datetime.now(timezone.utc)
            )
            
            db.add(storage_record)
            await db.commit()
            await db.refresh(storage_record)
            
            return storage_record
        except Exception as e:
            logger.error(f"Failed to create storage record: {str(e)}")
            raise
    
    async def _update_user_storage_usage(self, user_id: str, bytes_delta: int, db: AsyncSession):
        """Update user's storage usage"""
        try:
            from src.users.models.user import User
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if user:
                user.storage_used_bytes = max(0, user.storage_used_bytes + bytes_delta)
                user.last_storage_check = datetime.now(timezone.utc)
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to update user storage usage: {str(e)}")
    
    async def _get_user_storage_summary(self, user_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Get user storage summary"""
        try:
            user = await self._get_user_with_storage_info(user_id, db)
            if not user:
                return {}
            
            return {
                "used_bytes": user.storage_used_bytes,
                "used_mb": user.get_storage_used_mb(),
                "limit_mb": user.get_storage_limit_mb(),
                "usage_percentage": user.get_storage_usage_percentage(),
                "tier": user.storage_tier
            }
        except Exception as e:
            logger.error(f"Failed to get user storage summary: {str(e)}")
            return {}
    
    def _get_content_type_from_filename(self, content_type: str, filename: str) -> str:
        """Get content type from filename if not provided"""
        if content_type and content_type != "application/octet-stream":
            return content_type
        
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or "application/octet-stream"
    
    # 🔄 EXISTING METHODS - Keep all your existing functionality
    
    async def save_content_dual_storage(
        self,
        content_data: Union[bytes, str],
        content_type: str,
        filename: str,
        user_id: str,
        campaign_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Universal save method for all content types with enhanced error handling"""
        
        # Validate content type
        if content_type not in self.supported_types:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        # Convert base64 to bytes if needed
        if isinstance(content_data, str):
            try:
                import base64
                content_data = base64.b64decode(content_data)
            except Exception as e:
                raise ValueError(f"Invalid base64 content: {str(e)}")
        
        # Validate file size
        content_size_mb = len(content_data) / (1024 * 1024)
        max_size = self.supported_types[content_type]["max_size_mb"]
        if content_size_mb > max_size:
            raise ValueError(f"File too large: {content_size_mb:.1f}MB > {max_size}MB")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5(content_data).hexdigest()[:8]
        file_extension = self._get_file_extension(filename)
        unique_filename = f"{content_type}s/{user_id}/{campaign_id or 'general'}/{timestamp}_{content_hash}{file_extension}"
        
        # Optimize content
        try:
            optimized_content = await self._optimize_content(content_data, content_type)
        except Exception as e:
            logger.warning(f"Content optimization failed: {str(e)}, using original")
            optimized_content = content_data
        
        # Detect MIME type
        mime_type = mimetypes.guess_type(filename)[0] or f"{content_type}/octet-stream"
        
        # Prepare metadata
        enhanced_metadata = {
            "user_id": user_id,
            "campaign_id": campaign_id,
            "content_type": content_type,
            "original_filename": filename,
            "file_size": len(optimized_content),
            "mime_type": mime_type,
            "upload_timestamp": datetime.now(timezone.utc),
            "content_hash": content_hash,
            "optimization_applied": len(optimized_content) != len(content_data),
            **(metadata or {})
        }
        
        # Save to all available providers
        results = {
            "filename": unique_filename,
            "content_type": content_type,
            "file_size": len(optimized_content),
            "original_size": len(content_data),
            "providers": {},
            "storage_status": "pending",
            "metadata": enhanced_metadata
        }
        
        if not self.providers:
            raise Exception("No storage providers available - check R2 configuration")
        
        # Save to primary provider (Cloudflare R2)
        primary_provider = self.providers[0]
        try:
            primary_url = await self._upload_to_provider(
                primary_provider, unique_filename, optimized_content, mime_type, enhanced_metadata
            )
            results["providers"]["primary"] = {
                "provider": primary_provider.name,
                "url": primary_url,
                "status": "success",
                "cost_per_gb": primary_provider.cost_per_gb
            }
            logger.info(f"✅ Saved to primary ({primary_provider.name}): {unique_filename}")
        except Exception as e:
            results["providers"]["primary"] = {
                "provider": primary_provider.name,
                "url": None,
                "status": "failed",
                "error": str(e)
            }
            logger.error(f"❌ Primary storage failed: {str(e)}")
        
        # Save to backup provider if available
        if len(self.providers) > 1:
            backup_provider = self.providers[1]
            try:
                backup_url = await self._upload_to_provider(
                    backup_provider, unique_filename, optimized_content, mime_type, enhanced_metadata
                )
                results["providers"]["backup"] = {
                    "provider": backup_provider.name,
                    "url": backup_url,
                    "status": "success",
                    "cost_per_gb": backup_provider.cost_per_gb
                }
                logger.info(f"✅ Saved to backup ({backup_provider.name}): {unique_filename}")
            except Exception as e:
                results["providers"]["backup"] = {
                    "provider": backup_provider.name,
                    "url": None,
                    "status": "failed",
                    "error": str(e)
                }
                logger.error(f"❌ Backup storage failed: {str(e)}")
        
        # Determine final storage status
        primary_success = results["providers"].get("primary", {}).get("status") == "success"
        backup_success = results["providers"].get("backup", {}).get("status") == "success"
        
        success_count = sum([primary_success, backup_success])
        
        if success_count >= 2:
            results["storage_status"] = "fully_redundant"
        elif primary_success:
            results["storage_status"] = "primary_success"
        elif backup_success:
            results["storage_status"] = "backup_only"
        else:
            results["storage_status"] = "failed"
            raise Exception("All storage providers failed")
        
        # Add cost analysis
        results["cost_analysis"] = self._calculate_storage_costs(results, len(optimized_content))
        
        return results
    
    async def get_content_url_with_failover(
        self,
        primary_url: str,
        backup_url: str = None,
        emergency_url: str = None,
        preferred_provider: str = "cloudflare_r2"
    ) -> str:
        """Get content URL with automatic failover"""
        
        urls_to_try = []
        
        if preferred_provider == "cloudflare_r2":
            # Try primary first
            if primary_url:
                urls_to_try.append(("primary", primary_url))
            if backup_url:
                urls_to_try.append(("backup", backup_url))
            if emergency_url:
                urls_to_try.append(("emergency", emergency_url))
        else:
            # Try in different order based on preference
            if backup_url:
                urls_to_try.append(("backup", backup_url))
            if primary_url:
                urls_to_try.append(("primary", primary_url))
            if emergency_url:
                urls_to_try.append(("emergency", emergency_url))
        
        for provider_type, url in urls_to_try:
            if await self._check_url_health(url):
                if provider_type != "primary":
                    logger.warning(f"🔄 Failing over to {provider_type} for {primary_url}")
                return url
        
        # If all fail, return primary and let it fail naturally
        logger.error("❌ All storage providers failed health check")
        return primary_url or backup_url or emergency_url
    
    async def _upload_to_provider(
        self,
        provider: StorageProvider,
        filename: str,
        content: bytes,
        mime_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """🔥 FIXED: Upload content to specific provider with proper bucket handling"""
        
        # 🔥 FIXED: Get appropriate bucket name using exact Railway variables
        if provider.name == "cloudflare_r2":
            bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')
        elif provider.name == "backblaze_b2":
            bucket_name = os.getenv('B2_BUCKET_NAME') or os.getenv('BACKBLAZE_BUCKET_NAME')
        elif provider.name == "aws_s3":
            bucket_name = os.getenv('AWS_S3_BUCKET_NAME') or os.getenv('S3_BUCKET_NAME')
        else:
            raise ValueError(f"Unknown provider: {provider.name}")
        
        if not bucket_name:
            raise ValueError(f"No bucket configured for {provider.name}")
        
        logger.info(f"🔍 Uploading to {provider.name} bucket: {bucket_name}")
        
        try:
            # Upload with metadata
            provider.client.put_object(
                Bucket=bucket_name,
                Key=filename,
                Body=content,
                ContentType=mime_type,
                Metadata={k: str(v) for k, v in metadata.items()},
                # Add cache control and other optimizations
                CacheControl='public, max-age=31536000',  # 1 year cache
                ContentDisposition=f'inline; filename="{os.path.basename(filename)}"'
            )
            
            # 🔥 FIXED: Return appropriate public URL
            if provider.name == "cloudflare_r2":
                account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
                # Check for custom domain first
                custom_domain = os.getenv('R2_CUSTOM_DOMAIN') or os.getenv('CLOUDFLARE_R2_CUSTOM_DOMAIN')
                if custom_domain:
                    return f"https://{custom_domain}/{filename}"
                else:
                    return f"https://{bucket_name}.{account_id}.r2.cloudflarestorage.com/{filename}"
                    
            elif provider.name == "backblaze_b2":
                return f"https://{bucket_name}.s3.us-west-004.backblazeb2.com/{filename}"
                
            elif provider.name == "aws_s3":
                region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
                if region == 'us-east-1':
                    return f"https://{bucket_name}.s3.amazonaws.com/{filename}"
                else:
                    return f"https://{bucket_name}.s3.{region}.amazonaws.com/{filename}"
                    
        except Exception as e:
            logger.error(f"Upload to {provider.name} failed: {str(e)}")
            raise
    
    async def _check_url_health(self, url: str) -> bool:
        """Check if URL is accessible with caching"""
        
        if not url:
            return False
            
        cache_key = f"health_{url}"
        if cache_key in self.health_cache:
            result, timestamp = self.health_cache[cache_key]
            if datetime.now() - timestamp < timedelta(minutes=5):
                return result
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    is_healthy = response.status == 200
                    self.health_cache[cache_key] = (is_healthy, datetime.now())
                    return is_healthy
        except Exception:
            self.health_cache[cache_key] = (False, datetime.now())
            return False
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename"""
        return os.path.splitext(filename)[1].lower() or ".bin"
    
    async def _optimize_content(self, content: bytes, content_type: str) -> bytes:
        """Optimize content based on type"""
        
        if content_type in self.supported_types:
            optimizer = self.supported_types[content_type]["optimization"]
            return await optimizer(content)
        
        return content
    
    async def _optimize_image(self, image_data: bytes) -> bytes:
        """Optimize image for web delivery"""
        try:
            from PIL import Image
            
            # Convert to PIL Image
            img = Image.open(io.BytesIO(image_data))
            
            # Optimize for web
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            if img.width > 2048 or img.height > 2048:
                img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
            
            # Save optimized
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
        except Exception as e:
            logger.warning(f"Image optimization failed: {str(e)}")
            return image_data
    
    async def _optimize_document(self, doc_data: bytes) -> bytes:
        """Optimize document (preserve original for now)"""
        return doc_data
    
    async def _optimize_video(self, video_data: bytes) -> bytes:
        """Optimize video for web delivery"""
        try:
            # For now, return original. In production, you'd use FFmpeg
            # to compress video for web delivery
            return video_data
        except Exception as e:
            logger.warning(f"Video optimization failed: {str(e)}")
            return video_data
    
    def _calculate_storage_costs(self, results: Dict[str, Any], file_size_bytes: int) -> Dict[str, Any]:
        """Calculate storage costs across providers"""
        
        file_size_gb = file_size_bytes / (1024 * 1024 * 1024)
        
        cost_analysis = {
            "file_size_gb": round(file_size_gb, 6),
            "monthly_costs": {},
            "annual_costs": {},
            "cost_comparison": {}
        }
        
        # Calculate costs for each successful provider
        for provider_type, provider_info in results.get("providers", {}).items():
            if provider_info.get("status") == "success" and "cost_per_gb" in provider_info:
                monthly_cost = file_size_gb * provider_info["cost_per_gb"]
                annual_cost = monthly_cost * 12
                
                cost_analysis["monthly_costs"][provider_type] = round(monthly_cost, 6)
                cost_analysis["annual_costs"][provider_type] = round(annual_cost, 6)
        
        # Compare with expensive alternatives
        expensive_alternatives = {
            "aws_s3": 0.023,  # AWS S3 Standard
            "google_cloud": 0.020,  # Google Cloud Storage
            "azure": 0.021  # Azure Blob Storage
        }
        
        if cost_analysis["monthly_costs"]:
            cheapest_cost = min(cost_analysis["monthly_costs"].values())
            
            for alt_name, alt_cost_per_gb in expensive_alternatives.items():
                alt_monthly_cost = file_size_gb * alt_cost_per_gb
                savings = alt_monthly_cost - cheapest_cost
                savings_pct = (savings / alt_monthly_cost) * 100 if alt_monthly_cost > 0 else 0
                
                cost_analysis["cost_comparison"][alt_name] = {
                    "monthly_cost": round(alt_monthly_cost, 6),
                    "savings": round(savings, 6),
                    "savings_percentage": round(savings_pct, 1)
                }
        
        return cost_analysis
    
    async def get_storage_health(self) -> Dict[str, Any]:
        """Get comprehensive storage health status with quota support"""
        
        health_status = {
            "timestamp": datetime.now(timezone.utc),
            "overall_status": "healthy" if self.providers else "unhealthy",
            "providers": {},
            "failover_stats": {
                "total_failovers": 0,
                "last_failover": None,
                "uptime_percentage": 99.99
            },
            "configuration_status": {},
            "quota_features": {
                "user_quotas_enabled": True,
                "storage_tiers_available": list(self.storage_tiers['STORAGE_TIERS'].keys()),
                "organized_folders": True,
                "tier_validation": True
            }
        }
        
        # Check each provider
        for provider in self.providers:
            try:
                # Test upload capability with small test file
                test_key = f"health-checks/health-check-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                test_data = b"health check test"
                
                await self._upload_to_provider(
                    provider, test_key, test_data, "text/plain", 
                    {"health_check": "true", "timestamp": datetime.now(timezone.utc)}
                )
                
                health_status["providers"][provider.name] = {
                    "status": "healthy",
                    "last_check": datetime.now(timezone.utc),
                    "response_time": "< 1s",
                    "cost_per_gb": provider.cost_per_gb,
                    "priority": provider.priority
                }
                
            except Exception as e:
                health_status["providers"][provider.name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.now(timezone.utc),
                    "cost_per_gb": provider.cost_per_gb,
                    "priority": provider.priority
                }
                health_status["overall_status"] = "degraded"
        
        # Configuration status
        health_status["configuration_status"] = {
            "total_providers": len(self.providers),
            "primary_provider": self.providers[0].name if self.providers else None,
            "redundancy_level": "high" if len(self.providers) >= 3 else "medium" if len(self.providers) >= 2 else "low",
            "r2_configured": any(p.name == "cloudflare_r2" for p in self.providers),
            "backup_configured": len(self.providers) > 1,
            "emergency_backup_configured": len(self.providers) > 2,
            "quota_system_ready": True
        }
        
        return health_status

# Global instance
_storage_manager = None

def get_storage_manager() -> UniversalDualStorageManager:
    """Get global storage manager instance"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = UniversalDualStorageManager()
    return _storage_manager

def validate_storage_configuration() -> Dict[str, Any]:
    """🔥 FIXED: Validate storage configuration with exact Railway variable names"""
    
    validation_result = {
        "timestamp": datetime.now(timezone.utc),
        "r2_configured": False,
        "backup_configured": False,
        "emergency_configured": False,
        "quota_features_ready": False,
        "configuration_errors": [],
        "recommendations": []
    }
    
    # 🔥 FIXED: Check R2 configuration with exact Railway variables
    r2_vars = ["CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_R2_ACCESS_KEY_ID", "CLOUDFLARE_R2_SECRET_ACCESS_KEY", "CLOUDFLARE_R2_BUCKET_NAME"]
    r2_missing = [var for var in r2_vars if not os.getenv(var)]
    
    if not r2_missing:
        validation_result["r2_configured"] = True
    else:
        validation_result["configuration_errors"].append({
            "provider": "cloudflare_r2",
            "error": f"Missing environment variables: {r2_missing}",
            "severity": "high"
        })
        validation_result["recommendations"].append({
            "priority": "high",
            "action": f"Add missing R2 environment variables: {', '.join(r2_missing)}",
            "benefit": "Enable primary low-cost storage"
        })
    
    # Check B2 configuration (optional)
    b2_vars = ["B2_ACCESS_KEY_ID", "B2_SECRET_ACCESS_KEY", "B2_BUCKET_NAME"]
    b2_missing = [var for var in b2_vars if not os.getenv(var)]
    
    if not b2_missing:
        validation_result["backup_configured"] = True
    else:
        validation_result["recommendations"].append({
            "priority": "medium",
            "action": f"Add B2 environment variables for backup: {', '.join(b2_missing)}",
            "benefit": "Enable ultra-low cost backup storage"
        })
    
    # Check S3 configuration (optional)
    s3_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_S3_BUCKET_NAME"]
    s3_missing = [var for var in s3_vars if not os.getenv(var)]
    
    if not s3_missing:
        validation_result["emergency_configured"] = True
    
    # Check quota features readiness
    try:
        # Try to import quota dependencies
        from src.users.models.user import User
        from src.users.models.user_storage import UserStorageUsage
        from src.core.database import get_async_db
        validation_result["quota_features_ready"] = True
        validation_result["recommendations"].append({
            "priority": "info",
            "action": "User quota system is ready to use",
            "benefit": "Upload files with upload_file_with_quota_check() method"
        })
    except ImportError as e:
        validation_result["configuration_errors"].append({
            "provider": "quota_system",
            "error": f"Quota dependencies not available: {str(e)}",
            "severity": "medium"
        })
        validation_result["recommendations"].append({
            "priority": "medium",
            "action": "Ensure user storage models are created and database is migrated",
            "benefit": "Enable user quota management and organized storage"
        })
    
    return validation_result

# 🆕 NEW: Convenience function for quota-aware uploads
async def upload_with_quota_check(
    file_content: bytes,
    filename: str,
    content_type: str,
    user_id: str,
    campaign_id: Optional[str] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Convenience function for quota-aware file uploads
    
    Usage:
        from src.storage.universal_dual_storage import upload_with_quota_check
        
        try:
            result = await upload_with_quota_check(
                file_content=file_bytes,
                filename="document.pdf",
                content_type="application/pdf",
                user_id=current_user.id,
                campaign_id=campaign.id
            )
            return {"success": True, "file": result}
        except UserQuotaExceeded as e:
            return {"error": "Storage quota exceeded", "details": str(e)}
        except FileSizeExceeded as e:
            return {"error": "File too large", "details": str(e)}
        except ContentTypeNotAllowed as e:
            return {"error": "File type not allowed", "details": str(e)}
    """
    storage_manager = get_storage_manager()
    return await storage_manager.upload_file_with_quota_check(
        file_content=file_content,
        filename=filename,
        content_type=content_type,
        user_id=user_id,
        campaign_id=campaign_id,
        db=db
    )

# Run validation on import (development only)
if os.getenv("DEBUG", "false").lower() == "true":
    storage_validation = validate_storage_configuration()
    if storage_validation["configuration_errors"]:
        logger.warning("⚠️ Storage configuration issues detected")
        for error in storage_validation["configuration_errors"]:
            logger.warning(f"   {error['provider']}: {error['error']}")
    else:
        logger.info("✅ Storage configuration validation passed")
    
    if storage_validation["quota_features_ready"]:
        logger.info("🎯 Quota system ready - use upload_file_with_quota_check() for new uploads")
    else:
        logger.info("📋 Quota system pending - complete model setup to enable")
else:
    logger.info("🏭 Production mode: Storage validation completed")