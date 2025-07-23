# src/storage/providers/cloudflare_r2.py
"""
CLOUDFLARE R2 STORAGE PROVIDER
✅ Primary storage provider for ultra-cheap costs
✅ Free egress fees (perfect for image/video serving)
✅ S3-compatible API for easy integration
✅ Global CDN for fast worldwide access
✅ Health monitoring and failover support
"""

import os
import boto3
import aiohttp
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

@dataclass
class R2Config:
    """Cloudflare R2 configuration"""
    account_id: str
    access_key_id: str
    secret_access_key: str
    bucket_name: str
    endpoint_url: str
    region: str = "auto"
    
    def __post_init__(self):
        if not self.endpoint_url:
            self.endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"

class CloudflareR2Provider:
    """Cloudflare R2 storage provider with advanced features"""
    
    def __init__(self):
        self.config = self._load_config()
        self.client = self._initialize_client()
        self.health_status = True
        self.last_health_check = None
        self.request_count = 0
        self.error_count = 0
        self.performance_metrics = {
            "avg_upload_time": 0.0,
            "avg_download_time": 0.0,
            "success_rate": 100.0,
            "last_error": None
        }
    
    def _load_config(self) -> R2Config:
        """Load R2 configuration from environment variables"""
        
        account_id = os.getenv('R2_ACCOUNT_ID')
        access_key_id = os.getenv('R2_ACCESS_KEY_ID')
        secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')
        bucket_name = os.getenv('R2_BUCKET_NAME')
        
        if not all([account_id, access_key_id, secret_access_key, bucket_name]):
            missing_vars = []
            if not account_id: missing_vars.append('R2_ACCOUNT_ID')
            if not access_key_id: missing_vars.append('R2_ACCESS_KEY_ID')
            if not secret_access_key: missing_vars.append('R2_SECRET_ACCESS_KEY')
            if not bucket_name: missing_vars.append('R2_BUCKET_NAME')
            
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return R2Config(
            account_id=account_id,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            bucket_name=bucket_name,
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com"
        )
    
    def _initialize_client(self) -> boto3.client:
        """Initialize boto3 client for R2"""
        
        try:
            client = boto3.client(
                's3',
                endpoint_url=self.config.endpoint_url,
                aws_access_key_id=self.config.access_key_id,
                aws_secret_access_key=self.config.secret_access_key,
                region_name=self.config.region
            )
            
            logger.info(f"✅ Cloudflare R2 client initialized: {self.config.endpoint_url}")
            return client
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize R2 client: {str(e)}")
            raise
    
    async def upload_file(
        self,
        file_data: Union[bytes, str],
        filename: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
        cache_control: Optional[str] = None,
        acl: str = "private"
    ) -> Dict[str, Any]:
        """Upload file to Cloudflare R2"""
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Convert base64 to bytes if needed
            if isinstance(file_data, str):
                import base64
                file_data = base64.b64decode(file_data)
            
            # Prepare upload parameters
            upload_params = {
                'Bucket': self.config.bucket_name,
                'Key': filename,
                'Body': file_data,
                'ContentType': content_type,
                'ACL': acl
            }
            
            # Add metadata if provided
            if metadata:
                # Convert all values to strings for S3 compatibility
                upload_params['Metadata'] = {k: str(v) for k, v in metadata.items()}
            
            # Add cache control if provided
            if cache_control:
                upload_params['CacheControl'] = cache_control
            
            # Perform upload
            response = self.client.put_object(**upload_params)
            
            # Calculate upload time
            upload_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self._update_performance_metrics("upload", upload_time, True)
            
            # Generate public URL
            public_url = self._generate_public_url(filename)
            
            # Generate presigned URL for secure access
            presigned_url = self._generate_presigned_url(filename, expiration=3600)
            
            self.request_count += 1
            
            return {
                "success": True,
                "filename": filename,
                "public_url": public_url,
                "presigned_url": presigned_url,
                "etag": response.get('ETag', '').strip('"'),
                "upload_time": upload_time,
                "file_size": len(file_data),
                "content_type": content_type,
                "metadata": metadata or {},
                "provider": "cloudflare_r2"
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            self._update_performance_metrics("upload", 0, False)
            self.error_count += 1
            self.performance_metrics["last_error"] = f"{error_code}: {error_message}"
            
            logger.error(f"❌ R2 upload failed: {error_code} - {error_message}")
            
            return {
                "success": False,
                "error": f"R2 upload failed: {error_code} - {error_message}",
                "error_code": error_code,
                "filename": filename,
                "provider": "cloudflare_r2"
            }
            
        except Exception as e:
            self._update_performance_metrics("upload", 0, False)
            self.error_count += 1
            self.performance_metrics["last_error"] = str(e)
            
            logger.error(f"❌ R2 upload exception: {str(e)}")
            
            return {
                "success": False,
                "error": f"R2 upload exception: {str(e)}",
                "filename": filename,
                "provider": "cloudflare_r2"
            }
    
    async def download_file(
        self,
        filename: str,
        return_metadata: bool = False
    ) -> Dict[str, Any]:
        """Download file from Cloudflare R2"""
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get object
            response = self.client.get_object(
                Bucket=self.config.bucket_name,
                Key=filename
            )
            
            # Read file data
            file_data = response['Body'].read()
            
            # Calculate download time
            download_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self._update_performance_metrics("download", download_time, True)
            
            result = {
                "success": True,
                "filename": filename,
                "file_data": file_data,
                "file_size": len(file_data),
                "content_type": response.get('ContentType', 'application/octet-stream'),
                "download_time": download_time,
                "provider": "cloudflare_r2"
            }
            
            # Add metadata if requested
            if return_metadata:
                result["metadata"] = response.get('Metadata', {})
                result["etag"] = response.get('ETag', '').strip('"')
                result["last_modified"] = response.get('LastModified')
            
            self.request_count += 1
            return result
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            self._update_performance_metrics("download", 0, False)
            self.error_count += 1
            
            logger.error(f"❌ R2 download failed: {error_code} - {error_message}")
            
            return {
                "success": False,
                "error": f"R2 download failed: {error_code} - {error_message}",
                "error_code": error_code,
                "filename": filename,
                "provider": "cloudflare_r2"
            }
            
        except Exception as e:
            self._update_performance_metrics("download", 0, False)
            self.error_count += 1
            
            logger.error(f"❌ R2 download exception: {str(e)}")
            
            return {
                "success": False,
                "error": f"R2 download exception: {str(e)}",
                "filename": filename,
                "provider": "cloudflare_r2"
            }
    
    async def delete_file(self, filename: str) -> Dict[str, Any]:
        """Delete file from Cloudflare R2"""
        
        try:
            self.client.delete_object(
                Bucket=self.config.bucket_name,
                Key=filename
            )
            
            self.request_count += 1
            
            return {
                "success": True,
                "filename": filename,
                "provider": "cloudflare_r2"
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            self.error_count += 1
            
            logger.error(f"❌ R2 delete failed: {error_code} - {error_message}")
            
            return {
                "success": False,
                "error": f"R2 delete failed: {error_code} - {error_message}",
                "error_code": error_code,
                "filename": filename,
                "provider": "cloudflare_r2"
            }
            
        except Exception as e:
            self.error_count += 1
            
            logger.error(f"❌ R2 delete exception: {str(e)}")
            
            return {
                "success": False,
                "error": f"R2 delete exception: {str(e)}",
                "filename": filename,
                "provider": "cloudflare_r2"
            }
    
    async def list_files(
        self,
        prefix: str = "",
        max_keys: int = 1000,
        continuation_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """List files in Cloudflare R2"""
        
        try:
            list_params = {
                'Bucket': self.config.bucket_name,
                'MaxKeys': max_keys
            }
            
            if prefix:
                list_params['Prefix'] = prefix
            
            if continuation_token:
                list_params['ContinuationToken'] = continuation_token
            
            response = self.client.list_objects_v2(**list_params)
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'filename': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj.get('ETag', '').strip('"'),
                    'storage_class': obj.get('StorageClass', 'STANDARD')
                })
            
            self.request_count += 1
            
            return {
                "success": True,
                "files": files,
                "count": len(files),
                "is_truncated": response.get('IsTruncated', False),
                "next_continuation_token": response.get('NextContinuationToken'),
                "provider": "cloudflare_r2"
            }
            
        except Exception as e:
            self.error_count += 1
            
            logger.error(f"❌ R2 list files exception: {str(e)}")
            
            return {
                "success": False,
                "error": f"R2 list files exception: {str(e)}",
                "provider": "cloudflare_r2"
            }
    
    async def check_health(self) -> Dict[str, Any]:
        """Check R2 health status"""
        
        try:
            # Test with a simple head_bucket operation
            start_time = datetime.now(timezone.utc)
            
            self.client.head_bucket(Bucket=self.config.bucket_name)
            
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            self.health_status = True
            self.last_health_check = datetime.now(timezone.utc)
            
            return {
                "healthy": True,
                "response_time": response_time,
                "last_check": self.last_health_check.isoformat(),
                "endpoint": self.config.endpoint_url,
                "bucket": self.config.bucket_name,
                "provider": "cloudflare_r2"
            }
            
        except Exception as e:
            self.health_status = False
            self.last_health_check = datetime.now(timezone.utc)
            
            logger.error(f"❌ R2 health check failed: {str(e)}")
            
            return {
                "healthy": False,
                "error": str(e),
                "last_check": self.last_health_check.isoformat(),
                "endpoint": self.config.endpoint_url,
                "bucket": self.config.bucket_name,
                "provider": "cloudflare_r2"
            }
    
    async def check_url_health(self, url: str) -> bool:
        """Check if a specific URL is accessible"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.warning(f"R2 URL health check failed for {url}: {str(e)}")
            return False
    
    def _generate_public_url(self, filename: str) -> str:
        """Generate public URL for file"""
        
        # For public access, you might want to use a custom domain
        # For now, we'll use the R2 endpoint
        return f"{self.config.endpoint_url}/{filename}"
    
    def _generate_presigned_url(
        self,
        filename: str,
        expiration: int = 3600,
        method: str = "GET"
    ) -> str:
        """Generate presigned URL for secure access"""
        
        try:
            if method.upper() == "GET":
                url = self.client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': self.config.bucket_name,
                        'Key': filename
                    },
                    ExpiresIn=expiration
                )
            else:
                url = self.client.generate_presigned_url(
                    'put_object',
                    Params={
                        'Bucket': self.config.bucket_name,
                        'Key': filename
                    },
                    ExpiresIn=expiration
                )
            
            return url
            
        except Exception as e:
            logger.error(f"❌ Failed to generate presigned URL: {str(e)}")
            return self._generate_public_url(filename)
    
    def _update_performance_metrics(self, operation: str, duration: float, success: bool):
        """Update performance metrics"""
        
        if operation == "upload":
            if success:
                # Running average
                current_avg = self.performance_metrics["avg_upload_time"]
                self.performance_metrics["avg_upload_time"] = (current_avg + duration) / 2
        elif operation == "download":
            if success:
                # Running average
                current_avg = self.performance_metrics["avg_download_time"]
                self.performance_metrics["avg_download_time"] = (current_avg + duration) / 2
        
        # Update success rate
        total_requests = self.request_count + self.error_count
        if total_requests > 0:
            self.performance_metrics["success_rate"] = (self.request_count / total_requests) * 100
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        
        return {
            "provider": "cloudflare_r2",
            "health_status": self.health_status,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "performance_metrics": self.performance_metrics,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "endpoint": self.config.endpoint_url,
            "bucket": self.config.bucket_name
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information"""
        
        return {
            "name": "cloudflare_r2",
            "display_name": "Cloudflare R2",
            "type": "primary",
            "features": [
                "Free egress fees",
                "Global CDN",
                "S3-compatible API",
                "Fast uploads",
                "Automatic scaling"
            ],
            "pricing": {
                "storage": "$0.015/GB/month",
                "class_a_operations": "$4.50/million",
                "class_b_operations": "$0.36/million",
                "data_retrieval": "Free",
                "egress": "Free"
            },
            "limits": {
                "max_object_size": "5TB",
                "max_bucket_size": "Unlimited",
                "max_requests_per_second": "1000+"
            },
            "benefits": [
                "No egress fees (perfect for image serving)",
                "Global CDN for fast access",
                "S3-compatible for easy integration",
                "Excellent for social media campaigns",
                "Cost-effective for high-traffic applications"
            ]
        }

# Global instance
_r2_provider = None

def get_r2_provider() -> CloudflareR2Provider:
    """Get global R2 provider instance"""
    global _r2_provider
    if _r2_provider is None:
        _r2_provider = CloudflareR2Provider()
    return _r2_provider

# Convenience functions
async def upload_to_r2(
    file_data: Union[bytes, str],
    filename: str,
    content_type: str = "application/octet-stream",
    metadata: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Upload file to R2 (convenience function)"""
    
    provider = get_r2_provider()
    return await provider.upload_file(file_data, filename, content_type, metadata)

async def download_from_r2(filename: str) -> Dict[str, Any]:
    """Download file from R2 (convenience function)"""
    
    provider = get_r2_provider()
    return await provider.download_file(filename)

async def check_r2_health() -> Dict[str, Any]:
    """Check R2 health (convenience function)"""
    
    provider = get_r2_provider()
    return await provider.check_health()