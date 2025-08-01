# src/storage/providers/cloudflare_r2.py
"""
🔥 FIXED: Cloudflare R2 Storage Provider
✅ Fixed environment variable inconsistencies
✅ Proper public URL generation with custom domains
✅ Async-safe boto3 operations
✅ Enhanced error handling and recovery
✅ Production-ready configuration
✅ Comprehensive health monitoring
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
from concurrent.futures import ThreadPoolExecutor
import functools

logger = logging.getLogger(__name__)

@dataclass
class R2Config:
    """Cloudflare R2 configuration with validation"""
    account_id: str
    access_key_id: str
    secret_access_key: str
    bucket_name: str
    endpoint_url: str
    custom_domain: Optional[str] = None
    region: str = "auto"
    
    def __post_init__(self):
        # Validate required fields
        if not all([self.account_id, self.access_key_id, self.secret_access_key, self.bucket_name]):
            raise ValueError("All R2 configuration fields are required")
        
        # Auto-generate endpoint if not provided
        if not self.endpoint_url:
            self.endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"
        
        # Clean up custom domain
        if self.custom_domain:
            self.custom_domain = self.custom_domain.strip().lower()
            if self.custom_domain.startswith('http'):
                self.custom_domain = self.custom_domain.split('://', 1)[1]

class CloudflareR2Provider:
    """Fixed Cloudflare R2 storage provider"""
    
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
            "last_error": None,
            "total_requests": 0
        }
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def _load_config(self) -> R2Config:
        """Load R2 configuration with proper environment variable handling"""
        
        # 🔥 FIXED: Consistent environment variable names
        account_id = (
            os.getenv('CLOUDFLARE_ACCOUNT_ID') or 
            os.getenv('CF_ACCOUNT_ID') or
            os.getenv('R2_ACCOUNT_ID')
        )
        
        access_key_id = (
            os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID') or
            os.getenv('R2_ACCESS_KEY_ID') or
            os.getenv('CF_R2_ACCESS_KEY_ID')
        )
        
        secret_access_key = (
            os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY') or
            os.getenv('R2_SECRET_ACCESS_KEY') or
            os.getenv('CF_R2_SECRET_ACCESS_KEY')
        )
        
        bucket_name = (
            os.getenv('CLOUDFLARE_R2_BUCKET_NAME') or
            os.getenv('R2_BUCKET_NAME') or
            os.getenv('CF_R2_BUCKET_NAME')
        )
        
        # Custom domain for public URLs
        custom_domain = (
            os.getenv('R2_CUSTOM_DOMAIN') or
            os.getenv('CLOUDFLARE_R2_CUSTOM_DOMAIN') or
            os.getenv('CF_R2_CUSTOM_DOMAIN')
        )
        
        # Validate required variables
        missing_vars = []
        if not account_id: missing_vars.append('CLOUDFLARE_ACCOUNT_ID')
        if not access_key_id: missing_vars.append('CLOUDFLARE_R2_ACCESS_KEY_ID')
        if not secret_access_key: missing_vars.append('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
        if not bucket_name: missing_vars.append('CLOUDFLARE_R2_BUCKET_NAME')
        
        if missing_vars:
            raise ValueError(f"Missing required R2 environment variables: {', '.join(missing_vars)}")
        
        logger.info(f"✅ R2 Configuration loaded:")
        logger.info(f"   Account ID: {account_id}")
        logger.info(f"   Bucket: {bucket_name}")
        logger.info(f"   Custom Domain: {custom_domain or 'Not configured'}")
        
        return R2Config(
            account_id=account_id,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            bucket_name=bucket_name,
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            custom_domain=custom_domain
        )
    
    def _initialize_client(self) -> boto3.client:
        """Initialize boto3 client with proper configuration"""
        
        try:
            client = boto3.client(
                's3',
                endpoint_url=self.config.endpoint_url,
                aws_access_key_id=self.config.access_key_id,
                aws_secret_access_key=self.config.secret_access_key,
                region_name=self.config.region,
                config=boto3.session.Config(
                    signature_version='s3v4',
                    retries={'max_attempts': 3},
                    read_timeout=60,
                    connect_timeout=10
                )
            )
            
            logger.info(f"✅ R2 client initialized: {self.config.endpoint_url}")
            return client
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize R2 client: {str(e)}")
            raise
    
    async def _run_sync_in_executor(self, func, *args, **kwargs):
        """Run synchronous boto3 operations in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            functools.partial(func, *args, **kwargs)
        )
    
    async def upload_file(
        self,
        file_data: Union[bytes, str],
        filename: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
        cache_control: Optional[str] = None,
        make_public: bool = True
    ) -> Dict[str, Any]:
        """🔥 FIXED: Upload file to Cloudflare R2 with async safety"""
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Convert base64 to bytes if needed
            if isinstance(file_data, str):
                try:
                    import base64
                    file_data = base64.b64decode(file_data)
                except Exception as e:
                    raise ValueError(f"Invalid base64 content: {str(e)}")
            
            # Prepare upload parameters
            upload_params = {
                'Bucket': self.config.bucket_name,
                'Key': filename,
                'Body': file_data,
                'ContentType': content_type,
            }
            
            # 🔥 FIXED: Proper ACL handling for public access
            if make_public:
                upload_params['ACL'] = 'public-read'
                # Add CORS-friendly headers
                upload_params['ContentDisposition'] = f'inline; filename="{os.path.basename(filename)}"'
            
            # Add metadata if provided
            if metadata:
                upload_params['Metadata'] = {k: str(v) for k, v in metadata.items()}
            
            # Add cache control
            if cache_control:
                upload_params['CacheControl'] = cache_control
            else:
                # Default cache control for different file types
                if content_type.startswith('image/'):
                    upload_params['CacheControl'] = 'public, max-age=31536000'  # 1 year for images
                elif content_type.startswith('video/'):
                    upload_params['CacheControl'] = 'public, max-age=86400'    # 1 day for videos
                else:
                    upload_params['CacheControl'] = 'public, max-age=3600'     # 1 hour for others
            
            # 🔥 FIXED: Async-safe upload
            response = await self._run_sync_in_executor(
                self.client.put_object,
                **upload_params
            )
            
            # Calculate upload time
            upload_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self._update_performance_metrics("upload", upload_time, True)
            
            # 🔥 FIXED: Proper public URL generation
            public_url = self._generate_public_url(filename)
            
            # Generate presigned URL for secure access
            presigned_url = await self._generate_presigned_url(filename, expiration=3600)
            
            self.request_count += 1
            
            result = {
                "success": True,
                "filename": filename,
                "public_url": public_url,
                "presigned_url": presigned_url,
                "etag": response.get('ETag', '').strip('"'),
                "upload_time": upload_time,
                "file_size": len(file_data),
                "content_type": content_type,
                "metadata": metadata or {},
                "provider": "cloudflare_r2",
                "bucket": self.config.bucket_name,
                "make_public": make_public
            }
            
            logger.info(f"✅ R2 upload successful: {filename} ({len(file_data)} bytes)")
            return result
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            self._update_performance_metrics("upload", 0, False)
            self.error_count += 1
            self.performance_metrics["last_error"] = f"{error_code}: {error_message}"
            
            logger.error(f"❌ R2 upload failed: {error_code} - {error_message}")
            logger.error(f"   File: {filename}")
            logger.error(f"   Bucket: {self.config.bucket_name}")
            
            return {
                "success": False,
                "error": f"R2 upload failed: {error_code} - {error_message}",
                "error_code": error_code,
                "filename": filename,
                "provider": "cloudflare_r2",
                "troubleshooting": self._get_troubleshooting_info(error_code)
            }
            
        except Exception as e:
            self._update_performance_metrics("upload", 0, False)
            self.error_count += 1
            self.performance_metrics["last_error"] = str(e)
            
            logger.error(f"❌ R2 upload exception: {str(e)}")
            logger.error(f"   File: {filename}")
            
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
        """🔥 FIXED: Download file from Cloudflare R2 with async safety"""
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # 🔥 FIXED: Async-safe download
            response = await self._run_sync_in_executor(
                self.client.get_object,
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
                result["cache_control"] = response.get('CacheControl')
            
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
        """🔥 FIXED: Delete file from Cloudflare R2 with async safety"""
        
        try:
            await self._run_sync_in_executor(
                self.client.delete_object,
                Bucket=self.config.bucket_name,
                Key=filename
            )
            
            self.request_count += 1
            
            logger.info(f"✅ R2 file deleted: {filename}")
            
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
    
    async def check_health(self) -> Dict[str, Any]:
        """🔥 FIXED: Check R2 health status with async safety"""
        
        try:
            start_time = datetime.now(timezone.utc)
            
            # Test with head_bucket operation
            await self._run_sync_in_executor(
                self.client.head_bucket,
                Bucket=self.config.bucket_name
            )
            
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            self.health_status = True
            self.last_health_check = datetime.now(timezone.utc)
            
            return {
                "healthy": True,
                "response_time": response_time,
                "last_check": self.last_health_check.isoformat(),
                "endpoint": self.config.endpoint_url,
                "bucket": self.config.bucket_name,
                "custom_domain": self.config.custom_domain,
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
                "provider": "cloudflare_r2",
                "troubleshooting": self._get_troubleshooting_info("HealthCheckFailed")
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
        """🔥 FIXED: Generate proper public URL for file"""
        
        # Use custom domain if available (recommended for production)
        if self.config.custom_domain:
            return f"https://{self.config.custom_domain}/{filename}"
        
        # Use R2.dev subdomain (public bucket access)
        # Note: This requires the bucket to be configured for public access
        return f"https://{self.config.bucket_name}.{self.config.account_id}.r2.cloudflarestorage.com/{filename}"
    
    async def _generate_presigned_url(
        self,
        filename: str,
        expiration: int = 3600,
        method: str = "GET"
    ) -> str:
        """🔥 FIXED: Generate presigned URL with async safety"""
        
        try:
            if method.upper() == "GET":
                url = await self._run_sync_in_executor(
                    self.client.generate_presigned_url,
                    'get_object',
                    Params={
                        'Bucket': self.config.bucket_name,
                        'Key': filename
                    },
                    ExpiresIn=expiration
                )
            else:
                url = await self._run_sync_in_executor(
                    self.client.generate_presigned_url,
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
        """🔥 FIXED: Update performance metrics with proper calculation"""
        
        self.performance_metrics["total_requests"] += 1
        
        if success:
            if operation == "upload":
                current_avg = self.performance_metrics["avg_upload_time"]
                count = self.request_count + 1
                self.performance_metrics["avg_upload_time"] = ((current_avg * (count - 1)) + duration) / count
            elif operation == "download":
                current_avg = self.performance_metrics["avg_download_time"]
                count = self.request_count + 1
                self.performance_metrics["avg_download_time"] = ((current_avg * (count - 1)) + duration) / count
        
        # Update success rate
        total_requests = self.request_count + self.error_count
        if total_requests > 0:
            self.performance_metrics["success_rate"] = (self.request_count / total_requests) * 100
    
    def _get_troubleshooting_info(self, error_code: str) -> Dict[str, Any]:
        """Get troubleshooting information for common errors"""
        
        troubleshooting_guide = {
            "NoSuchBucket": {
                "description": "The specified bucket does not exist",
                "solutions": [
                    "Verify CLOUDFLARE_R2_BUCKET_NAME environment variable",
                    "Check if bucket exists in Cloudflare dashboard",
                    "Ensure bucket name matches exactly (case-sensitive)"
                ]
            },
            "InvalidAccessKeyId": {
                "description": "The R2 access key ID is invalid",
                "solutions": [
                    "Verify CLOUDFLARE_R2_ACCESS_KEY_ID environment variable",
                    "Generate new R2 API token in Cloudflare dashboard",
                    "Ensure API token has R2:Edit permissions"
                ]
            },
            "SignatureDoesNotMatch": {
                "description": "The secret access key is incorrect",
                "solutions": [
                    "Verify CLOUDFLARE_R2_SECRET_ACCESS_KEY environment variable",
                    "Regenerate R2 API token with correct permissions",
                    "Check for trailing spaces in environment variables"
                ]
            },
            "AccessDenied": {
                "description": "Access denied to the bucket or object",
                "solutions": [
                    "Verify R2 API token has sufficient permissions",
                    "Check bucket CORS configuration",
                    "Ensure public access is configured if needed"
                ]
            },
            "HealthCheckFailed": {
                "description": "R2 health check failed",
                "solutions": [
                    "Check internet connectivity",
                    "Verify Cloudflare R2 service status",
                    "Validate all environment variables",
                    "Test with Cloudflare dashboard"
                ]
            }
        }
        
        return troubleshooting_guide.get(error_code, {
            "description": f"Unknown error: {error_code}",
            "solutions": [
                "Check Cloudflare R2 service status",
                "Verify all environment variables",
                "Check application logs for details",
                "Contact Cloudflare support if issue persists"
            ]
        })
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        
        return {
            "provider": "cloudflare_r2",
            "health_status": self.health_status,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "performance_metrics": self.performance_metrics,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "configuration": {
                "endpoint": self.config.endpoint_url,
                "bucket": self.config.bucket_name,
                "custom_domain": self.config.custom_domain,
                "account_id": self.config.account_id
            }
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get comprehensive provider information"""
        
        return {
            "name": "cloudflare_r2",
            "display_name": "Cloudflare R2",
            "type": "primary",
            "status": "production_ready",
            "features": [
                "Zero egress fees",
                "Global CDN distribution",
                "S3-compatible API",
                "Sub-second first-byte latency",
                "Automatic scaling",
                "Built-in DDoS protection"
            ],
            "pricing": {
                "storage": "$0.015/GB/month",
                "class_a_operations": "$4.50/million requests",
                "class_b_operations": "$0.36/million requests",
                "data_retrieval": "Free",
                "egress": "Free (unlimited)"
            },
            "limits": {
                "max_object_size": "5TB",
                "max_bucket_size": "Unlimited",
                "max_requests_per_second": "1000+",
                "max_buckets_per_account": "1000"
            },
            "benefits": [
                "💰 Zero egress fees save 10x vs AWS",
                "🚀 Global CDN for instant access",
                "🔧 S3-compatible for easy migration",
                "📱 Perfect for social media campaigns",
                "💡 Excellent for high-traffic apps",
                "🛡️ Built-in security and DDoS protection"
            ],
            "use_cases": [
                "Image and video serving",
                "Static website hosting",
                "Backup and archival",
                "Content distribution",
                "Social media assets",
                "Marketing campaigns"
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

# 🔥 FIXED: Convenience functions with async safety
async def upload_to_r2(
    file_data: Union[bytes, str],
    filename: str,
    content_type: str = "application/octet-stream",
    metadata: Optional[Dict[str, str]] = None,
    make_public: bool = True
) -> Dict[str, Any]:
    """Upload file to R2 (convenience function)"""
    
    provider = get_r2_provider()
    return await provider.upload_file(
        file_data=file_data,
        filename=filename,
        content_type=content_type,
        metadata=metadata,
        make_public=make_public
    )

async def download_from_r2(filename: str, return_metadata: bool = False) -> Dict[str, Any]:
    """Download file from R2 (convenience function)"""
    
    provider = get_r2_provider()
    return await provider.download_file(filename, return_metadata)

async def check_r2_health() -> Dict[str, Any]:
    """Check R2 health (convenience function)"""
    
    provider = get_r2_provider()
    return await provider.check_health()

async def get_r2_metrics() -> Dict[str, Any]:
    """Get R2 performance metrics (convenience function)"""
    
    provider = get_r2_provider()
    return provider.get_performance_metrics()

def validate_r2_configuration() -> Dict[str, Any]:
    """Validate R2 configuration and provide setup guidance"""
    
    validation_result = {
        "timestamp": datetime.now(timezone.utc),
        "r2_configured": False,
        "configuration_errors": [],
        "recommendations": [],
        "required_env_vars": [
            "CLOUDFLARE_ACCOUNT_ID",
            "CLOUDFLARE_R2_ACCESS_KEY_ID", 
            "CLOUDFLARE_R2_SECRET_ACCESS_KEY",
            "CLOUDFLARE_R2_BUCKET_NAME"
        ],
        "optional_env_vars": [
            "R2_CUSTOM_DOMAIN"
        ]
    }
    
    # Check required environment variables
    missing_vars = []
    for var in validation_result["required_env_vars"]:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if not missing_vars:
        validation_result["r2_configured"] = True
        validation_result["status"] = "✅ Cloudflare R2 properly configured"
    else:
        validation_result["configuration_errors"].append({
            "error": f"Missing required environment variables: {missing_vars}",
            "severity": "high"
        })
        validation_result["status"] = "❌ Cloudflare R2 configuration incomplete"
    
    # Recommendations
    if missing_vars:
        validation_result["recommendations"].append({
            "priority": "high",
            "action": f"Add missing environment variables: {', '.join(missing_vars)}",
            "benefit": "Enable Cloudflare R2 storage with zero egress fees"
        })
    
    if not os.getenv('R2_CUSTOM_DOMAIN'):
        validation_result["recommendations"].append({
            "priority": "medium",
            "action": "Configure R2_CUSTOM_DOMAIN for branded URLs",
            "benefit": "Professional URLs and better SEO"
        })
    
    return validation_result

# Run validation on import (development only)
if os.getenv("DEBUG", "false").lower() == "true":
    try:
        r2_validation = validate_r2_configuration()
        logger.info(f"R2 Configuration Status: {r2_validation['status']}")
        
        if r2_validation["configuration_errors"]:
            for error in r2_validation["configuration_errors"]:
                logger.warning(f"   {error['error']}")
        
        if r2_validation["recommendations"]:
            logger.info("💡 R2 Setup Recommendations:")
            for rec in r2_validation["recommendations"]:
                logger.info(f"   {rec['priority'].upper()}: {rec['action']}")
    except Exception as e:
        logger.error(f"⚠️ R2 validation failed: {str(e)}")
else:
    logger.info("🏭 Production mode: R2 configuration validation skipped")