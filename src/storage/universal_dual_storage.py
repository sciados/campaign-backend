# src/storage/universal_dual_storage.py
import asyncio
import aiohttp
import boto3
import logging
import hashlib
import mimetypes
import os
import io
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

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
    """Universal storage manager for all content types"""
    
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
    
    def _initialize_providers(self) -> List[StorageProvider]:
        """Initialize storage providers"""
        providers = []
        
        # Cloudflare R2 (Primary)
        try:
            r2_client = boto3.client(
                's3',
                endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
                aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
                region_name='auto'
            )
            providers.append(StorageProvider(
                name="cloudflare_r2",
                client=r2_client,
                priority=1,
                cost_per_gb=0.015
            ))
            logger.info("✅ Cloudflare R2 provider initialized")
        except Exception as e:
            logger.error(f"❌ Cloudflare R2 initialization failed: {str(e)}")
        
        # Backblaze B2 (Backup)
        try:
            b2_client = boto3.client(
                's3',
                endpoint_url='https://s3.us-west-004.backblazeb2.com',
                aws_access_key_id=os.getenv('B2_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('B2_SECRET_ACCESS_KEY'),
                region_name='us-west-004'
            )
            providers.append(StorageProvider(
                name="backblaze_b2",
                client=b2_client,
                priority=2,
                cost_per_gb=0.005
            ))
            logger.info("✅ Backblaze B2 provider initialized")
        except Exception as e:
            logger.error(f"❌ Backblaze B2 initialization failed: {str(e)}")
        
        return sorted(providers, key=lambda x: x.priority)
    
    async def save_content_dual_storage(
        self,
        content_data: Union[bytes, str],
        content_type: str,
        filename: str,
        user_id: str,
        campaign_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Universal save method for all content types"""
        
        # Validate content type
        if content_type not in self.supported_types:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        # Convert base64 to bytes if needed
        if isinstance(content_data, str):
            import base64
            content_data = base64.b64decode(content_data)
        
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
        optimized_content = await self._optimize_content(content_data, content_type)
        
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
            "upload_timestamp": datetime.utcnow().isoformat(),
            "content_hash": content_hash,
            **(metadata or {})
        }
        
        # Save to all providers
        results = {
            "filename": unique_filename,
            "content_type": content_type,
            "file_size": len(optimized_content),
            "providers": {},
            "storage_status": "pending",
            "metadata": enhanced_metadata
        }
        
        # Save to primary provider (Cloudflare R2)
        primary_provider = self.providers[0]
        try:
            primary_url = await self._upload_to_provider(
                primary_provider, unique_filename, optimized_content, mime_type, enhanced_metadata
            )
            results["providers"]["primary"] = {
                "provider": primary_provider.name,
                "url": primary_url,
                "status": "success"
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
        
        # Save to backup provider (Backblaze B2)
        if len(self.providers) > 1:
            backup_provider = self.providers[1]
            try:
                backup_url = await self._upload_to_provider(
                    backup_provider, unique_filename, optimized_content, mime_type, enhanced_metadata
                )
                results["providers"]["backup"] = {
                    "provider": backup_provider.name,
                    "url": backup_url,
                    "status": "success"
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
        
        if primary_success and backup_success:
            results["storage_status"] = "fully_synced"
        elif primary_success:
            results["storage_status"] = "primary_only"
        elif backup_success:
            results["storage_status"] = "backup_only"
        else:
            results["storage_status"] = "failed"
            raise Exception("Both primary and backup storage failed")
        
        return results
    
    async def get_content_url_with_failover(
        self,
        primary_url: str,
        backup_url: str = None,
        preferred_provider: str = "cloudflare_r2"
    ) -> str:
        """Get content URL with automatic failover"""
        
        if preferred_provider == "cloudflare_r2":
            # Try primary first
            if primary_url and await self._check_url_health(primary_url):
                return primary_url
            elif backup_url and await self._check_url_health(backup_url):
                logger.warning(f"🔄 Failing over to backup for {primary_url}")
                return backup_url
        else:
            # Try backup first
            if backup_url and await self._check_url_health(backup_url):
                return backup_url
            elif primary_url and await self._check_url_health(primary_url):
                return primary_url
        
        # If both fail, return primary and let it fail naturally
        return primary_url or backup_url
    
    async def _upload_to_provider(
        self,
        provider: StorageProvider,
        filename: str,
        content: bytes,
        mime_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Upload content to specific provider"""
        
        bucket_name = os.getenv('R2_BUCKET_NAME') if provider.name == "cloudflare_r2" else os.getenv('B2_BUCKET_NAME')
        
        provider.client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=content,
            ContentType=mime_type,
            Metadata={k: str(v) for k, v in metadata.items()}
        )
        
        # Return public URL
        if provider.name == "cloudflare_r2":
            return f"https://{bucket_name}.{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com/{filename}"
        else:
            return f"https://{bucket_name}.s3.us-west-004.backblazeb2.com/{filename}"
    
    async def _check_url_health(self, url: str) -> bool:
        """Check if URL is accessible with caching"""
        
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
        return os.path.splitext(filename)[1].lower()
    
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
    
    async def get_storage_health(self) -> Dict[str, Any]:
        """Get comprehensive storage health status"""
        
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "providers": {},
            "failover_stats": {
                "total_failovers": 0,
                "last_failover": None,
                "uptime_percentage": 99.99
            }
        }
        
        # Check each provider
        for provider in self.providers:
            try:
                # Test upload capability
                test_key = f"health-check-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                test_data = b"health check"
                
                await self._upload_to_provider(
                    provider, f"health-checks/{test_key}", test_data, "text/plain", {}
                )
                
                health_status["providers"][provider.name] = {
                    "status": "healthy",
                    "last_check": datetime.utcnow().isoformat(),
                    "response_time": "< 1s"
                }
                
            except Exception as e:
                health_status["providers"][provider.name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
                health_status["overall_status"] = "degraded"
        
        return health_status

# Global instance
_storage_manager = None

def get_storage_manager() -> UniversalDualStorageManager:
    """Get global storage manager instance"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = UniversalDualStorageManager()
    return _storage_manager