# ==============================================================================
# 3. CLOUDFLARE R2 SERVICE
# ==============================================================================

# src/storage/services/cloudflare_service.py
import boto3
import asyncio
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
from src.core.config.storage_config import storage_config
import logging

logger = logging.getLogger(__name__)

class CloudflareService:
    """Cloudflare R2 storage service"""
    
    def __init__(self):
        self.config = storage_config.cloudflare_r2
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Cloudflare R2 client"""
        try:
            self.client = boto3.client(
                's3',
                **self.config.boto3_config
            )
            logger.info("✅ Cloudflare R2 client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize R2 client: {e}")
    
    async def upload_file(
        self,
        file_data: bytes,
        file_path: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Upload file to Cloudflare R2"""
        try:
            extra_args = {
                'ContentType': content_type,
                'Metadata': metadata or {}
            }
            
            # Use asyncio to run sync operation
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.put_object(
                    Bucket=self.config.bucket_name,
                    Key=file_path,
                    Body=file_data,
                    **extra_args
                )
            )
            
            # Generate public URL
            public_url = f"https://pub-{self.config.account_id}.r2.dev/{file_path}"
            
            return {
                "success": True,
                "file_path": file_path,
                "public_url": public_url,
                "size": len(file_data)
            }
            
        except ClientError as e:
            logger.error(f"R2 upload failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def download_file(self, file_path: str) -> Dict[str, Any]:
        """Download file from Cloudflare R2"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.get_object(
                    Bucket=self.config.bucket_name,
                    Key=file_path
                )
            )
            
            file_data = response['Body'].read()
            
            return {
                "success": True,
                "file_data": file_data,
                "content_type": response.get('ContentType'),
                "size": response.get('ContentLength')
            }
            
        except ClientError as e:
            logger.error(f"R2 download failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete file from Cloudflare R2"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.delete_object(
                    Bucket=self.config.bucket_name,
                    Key=file_path
                )
            )
            
            return {"success": True}
            
        except ClientError as e:
            logger.error(f"R2 delete failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Cloudflare R2 connection"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.head_bucket(Bucket=self.config.bucket_name)
            )
            
            return {
                "success": True,
                "message": "Cloudflare R2 connection successful"
            }
            
        except Exception as e:
            logger.error(f"R2 connection test failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }