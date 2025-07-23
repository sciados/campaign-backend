# src/storage/providers/backblaze_b2.py
"""
BACKBLAZE B2 STORAGE PROVIDER
✅ Backup storage provider for ultra-cheap costs
✅ Cheapest storage at $0.005/GB/month
✅ S3-compatible API for easy integration
✅ Reliable backup for primary storage
✅ Health monitoring and sync support
"""

import os
import boto3
import aiohttp
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass

# Handle botocore import gracefully
try:
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    # Fallback for missing botocore
    class ClientError(Exception):
        def __init__(self, error_response, operation_name):
            self.response = error_response
            super().__init__(f"AWS operation {operation_name} failed")
    
    class NoCredentialsError(Exception):
        pass

logger = logging.getLogger(__name__)

@dataclass
class B2Config:
    """Backblaze B2 configuration"""
    access_key_id: str
    secret_access_key: str
    bucket_name: str
    endpoint_url: str
    region: str
    
    def __post_init__(self):
        if not self.endpoint_url:
            # Default B2 endpoint for US West region
            self.endpoint_url = f"https://s3.{self.region}.backblazeb2.com"

class BackblazeB2Provider:
    """Backblaze B2 storage provider optimized for backup storage"""
    
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
            "sync_lag": 0.0,
            "backup_reliability": 100.0
        }
    
    def _load_config(self) -> B2Config:
        """Load B2 configuration from environment variables"""
        
        access_key_id = os.getenv('B2_ACCESS_KEY_ID')
        secret_access_key = os.getenv('B2_SECRET_ACCESS_KEY')
        bucket_name = os.getenv('B2_BUCKET_NAME')
        region = os.getenv('B2_REGION', 'us-west-004')  # Default region
        
        if not all([access_key_id, secret_access_key, bucket_name]):
            missing_vars = []
            if not access_key_id: missing_vars.append('B2_ACCESS_KEY_ID')
            if not secret_access_key: missing_vars.append('B2_SECRET_ACCESS_KEY')
            if not bucket_name: missing_vars.append('B2_BUCKET_NAME')
            
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return B2Config(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            bucket_name=bucket_name,
            endpoint_url=f"https://s3.{region}.backblazeb2.com",
            region=region
        )
    
    def _initialize_client(self) -> boto3.client:
        """Initialize boto3 client for B2"""
        
        try:
            client = boto3.client(
                's3',
                endpoint_url=self.config.endpoint_url,
                aws_access_key_id=self.config.access_key_id,
                aws_secret_access_key=self.config.secret_access_key,
                region_name=self.config.region
            )
            
            logger.info(f"✅ Backblaze B2 client initialized: {self.config.endpoint_url}")
            return client
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize B2 client: {str(e)}")
            raise
    
    async def upload_file(
        self,
        file_data: Union[bytes, str],
        filename: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
        storage_class: str = "STANDARD",
        sync_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload file to Backblaze B2"""
        
        start_time = datetime.now(timezone.utc).astimezone().isoformat()
        
        try:
            # Convert base64 to bytes if needed
            if isinstance(file_data, str):
                import base64
                file_data = base64.b64decode(file_data)
            
            # Prepare metadata with sync information
            enhanced_metadata = metadata or {}
            if sync_source:
                enhanced_metadata["sync_source"] = sync_source
                enhanced_metadata["sync_timestamp"] = datetime.now(timezone.utc).astimezone().isoformat()
            
            enhanced_metadata["backup_provider"] = "backblaze_b2"
            enhanced_metadata["backup_timestamp"] = datetime.now(timezone.utc).astimezone().isoformat()
            
            # Prepare upload parameters
            upload_params = {
                'Bucket': self.config.bucket_name,
                'Key': filename,
                'Body': file_data,
                'ContentType': content_type,
                'StorageClass': storage_class,
                'Metadata': {k: str(v) for k, v in enhanced_metadata.items()}
            }
            
            # Perform upload
            response = self.client.put_object(**upload_params)
            
            # Calculate upload time
            upload_time = (datetime.now(timezone.utc).astimezone().isoformat() - start_time).total_seconds()
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
                "storage_class": storage_class,
                "metadata": enhanced_metadata,
                "provider": "backblaze_b2",
                "backup_verified": True
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            self._update_performance_metrics("upload", 0, False)
            self.error_count += 1
            self.performance_metrics["last_error"] = f"{error_code}: {error_message}"
            
            logger.error(f"❌ B2 upload failed: {error_code} - {error_message}")
            
            return {
                "success": False,
                "error": f"B2 upload failed: {error_code} - {error_message}",
                "error_code": error_code,
                "filename": filename,
                "provider": "backblaze_b2"
            }
            
        except Exception as e:
            self._update_performance_metrics("upload", 0, False)
            self.error_count += 1
            self.performance_metrics["last_error"] = str(e)
            
            logger.error(f"❌ B2 upload exception: {str(e)}")
            
            return {
                "success": False,
                "error": f"B2 upload exception: {str(e)}",
                "filename": filename,
                "provider": "backblaze_b2"
            }
    
    async def download_file(
        self,
        filename: str,
        return_metadata: bool = False,
        verify_sync: bool = True
    ) -> Dict[str, Any]:
        """Download file from Backblaze B2"""
        
        start_time = datetime.now(timezone.utc).astimezone().isoformat()
        
        try:
            # Get object
            response = self.client.get_object(
                Bucket=self.config.bucket_name,
                Key=filename
            )
            
            # Read file data
            file_data = response['Body'].read()
            
            # Calculate download time
            download_time = (datetime.now(timezone.utc).astimezone().isoformat() - start_time).total_seconds()
            self._update_performance_metrics("download", download_time, True)
            
            result = {
                "success": True,
                "filename": filename,
                "file_data": file_data,
                "file_size": len(file_data),
                "content_type": response.get('ContentType', 'application/octet-stream'),
                "download_time": download_time,
                "provider": "backblaze_b2",
                "backup_source": True
            }
            
            # Add metadata if requested
            if return_metadata:
                metadata = response.get('Metadata', {})
                result["metadata"] = metadata
                result["etag"] = response.get('ETag', '').strip('"')
                result["last_modified"] = response.get('LastModified')
                result["storage_class"] = response.get('StorageClass', 'STANDARD')
                
                # Check sync information
                if verify_sync:
                    sync_info = self._verify_sync_metadata(metadata)
                    result["sync_info"] = sync_info
            
            self.request_count += 1
            return result
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            self._update_performance_metrics("download", 0, False)
            self.error_count += 1
            
            logger.error(f"❌ B2 download failed: {error_code} - {error_message}")
            
            return {
                "success": False,
                "error": f"B2 download failed: {error_code} - {error_message}",
                "error_code": error_code,
                "filename": filename,
                "provider": "backblaze_b2"
            }
            
        except Exception as e:
            self._update_performance_metrics("download", 0, False)
            self.error_count += 1
            
            logger.error(f"❌ B2 download exception: {str(e)}")
            
            return {
                "success": False,
                "error": f"B2 download exception: {str(e)}",
                "filename": filename,
                "provider": "backblaze_b2"
            }
    
    async def delete_file(
        self,
        filename: str,
        verify_deletion: bool = True
    ) -> Dict[str, Any]:
        """Delete file from Backblaze B2"""
        
        try:
            # Delete object
            response = self.client.delete_object(
                Bucket=self.config.bucket_name,
                Key=filename
            )
            
            # Verify deletion if requested
            if verify_deletion:
                try:
                    await asyncio.sleep(1)  # Brief delay for consistency
                    self.client.head_object(Bucket=self.config.bucket_name, Key=filename)
                    # If we get here, deletion failed
                    return {
                        "success": False,
                        "error": "File deletion verification failed - file still exists",
                        "filename": filename,
                        "provider": "backblaze_b2"
                    }
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        # File doesn't exist, deletion successful
                        pass
                    else:
                        raise
            
            self.request_count += 1
            
            return {
                "success": True,
                "filename": filename,
                "provider": "backblaze_b2",
                "deleted": True,
                "verified": verify_deletion
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            self.error_count += 1
            logger.error(f"❌ B2 delete failed: {error_code} - {error_message}")
            
            return {
                "success": False,
                "error": f"B2 delete failed: {error_code} - {error_message}",
                "error_code": error_code,
                "filename": filename,
                "provider": "backblaze_b2"
            }
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ B2 delete exception: {str(e)}")
            
            return {
                "success": False,
                "error": f"B2 delete exception: {str(e)}",
                "filename": filename,
                "provider": "backblaze_b2"
            }
    
    async def check_file_exists(
        self,
        filename: str,
        return_metadata: bool = False
    ) -> Dict[str, Any]:
        """Check if file exists in Backblaze B2"""
        
        try:
            response = self.client.head_object(
                Bucket=self.config.bucket_name,
                Key=filename
            )
            
            result = {
                "success": True,
                "exists": True,
                "filename": filename,
                "provider": "backblaze_b2",
                "file_size": response.get('ContentLength', 0),
                "content_type": response.get('ContentType', 'application/octet-stream'),
                "last_modified": response.get('LastModified'),
                "etag": response.get('ETag', '').strip('"')
            }
            
            if return_metadata:
                result["metadata"] = response.get('Metadata', {})
                result["storage_class"] = response.get('StorageClass', 'STANDARD')
            
            self.request_count += 1
            return result
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            if error_code == '404':
                return {
                    "success": True,
                    "exists": False,
                    "filename": filename,
                    "provider": "backblaze_b2"
                }
            else:
                error_message = e.response.get('Error', {}).get('Message', str(e))
                self.error_count += 1
                
                return {
                    "success": False,
                    "error": f"B2 check failed: {error_code} - {error_message}",
                    "error_code": error_code,
                    "filename": filename,
                    "provider": "backblaze_b2"
                }
                
        except Exception as e:
            self.error_count += 1
            
            return {
                "success": False,
                "error": f"B2 check exception: {str(e)}",
                "filename": filename,
                "provider": "backblaze_b2"
            }
    
    async def list_files(
        self,
        prefix: str = "",
        max_keys: int = 1000,
        continuation_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """List files in Backblaze B2 bucket"""
        
        try:
            params = {
                'Bucket': self.config.bucket_name,
                'MaxKeys': max_keys
            }
            
            if prefix:
                params['Prefix'] = prefix
            
            if continuation_token:
                params['ContinuationToken'] = continuation_token
            
            response = self.client.list_objects_v2(**params)
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    "filename": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'],
                    "etag": obj['ETag'].strip('"'),
                    "storage_class": obj.get('StorageClass', 'STANDARD')
                })
            
            self.request_count += 1
            
            return {
                "success": True,
                "files": files,
                "count": len(files),
                "is_truncated": response.get('IsTruncated', False),
                "next_continuation_token": response.get('NextContinuationToken'),
                "provider": "backblaze_b2"
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            self.error_count += 1
            logger.error(f"❌ B2 list failed: {error_code} - {error_message}")
            
            return {
                "success": False,
                "error": f"B2 list failed: {error_code} - {error_message}",
                "error_code": error_code,
                "provider": "backblaze_b2"
            }
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ B2 list exception: {str(e)}")
            
            return {
                "success": False,
                "error": f"B2 list exception: {str(e)}",
                "provider": "backblaze_b2"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Backblaze B2"""
        
        health_start = datetime.now(timezone.utc).astimezone().isoformat()
        
        try:
            # Test bucket access
            response = self.client.head_bucket(Bucket=self.config.bucket_name)
            
            # Test upload/download with small file
            test_filename = f"health-check-{datetime.now(timezone.utc).astimezone().isoformat().strftime('%Y%m%d-%H%M%S')}.txt"
            test_data = b"B2 health check test"
            
            # Upload test
            upload_result = await self.upload_file(
                file_data=test_data,
                filename=test_filename,
                content_type="text/plain",
                metadata={"test": "health_check"}
            )
            
            if not upload_result["success"]:
                raise Exception(f"Upload test failed: {upload_result['error']}")
            
            # Download test
            download_result = await self.download_file(test_filename)
            
            if not download_result["success"]:
                raise Exception(f"Download test failed: {download_result['error']}")
            
            # Verify data integrity
            if download_result["file_data"] != test_data:
                raise Exception("Data integrity check failed")
            
            # Cleanup test file
            await self.delete_file(test_filename)
            
            # Calculate health check time
            health_time = (datetime.now(timezone.utc).astimezone().isoformat() - health_start).total_seconds()
            
            self.health_status = True
            self.last_health_check = datetime.now(timezone.utc).astimezone().isoformat()
            
            return {
                "healthy": True,
                "provider": "backblaze_b2",
                "response_time": health_time,
                "bucket_accessible": True,
                "upload_test": "passed",
                "download_test": "passed",
                "data_integrity": "verified",
                "last_check": self.last_health_check.isoformat(),
                "performance_metrics": self.performance_metrics,
                "request_count": self.request_count,
                "error_count": self.error_count,
                "success_rate": self._calculate_success_rate()
            }
            
        except Exception as e:
            self.health_status = False
            self.last_health_check = datetime.now(timezone.utc).astimezone().isoformat()
            self.error_count += 1
            
            logger.error(f"❌ B2 health check failed: {str(e)}")
            
            return {
                "healthy": False,
                "provider": "backblaze_b2",
                "error": str(e),
                "last_check": self.last_health_check.isoformat(),
                "performance_metrics": self.performance_metrics,
                "request_count": self.request_count,
                "error_count": self.error_count,
                "success_rate": self._calculate_success_rate()
            }
    
    def _generate_public_url(self, filename: str) -> str:
        """Generate public URL for file"""
        return f"{self.config.endpoint_url}/{self.config.bucket_name}/{filename}"
    
    def _generate_presigned_url(
        self,
        filename: str,
        expiration: int = 3600,
        http_method: str = 'GET'
    ) -> str:
        """Generate presigned URL for secure file access"""
        
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.config.bucket_name, 'Key': filename},
                ExpiresIn=expiration,
                HttpMethod=http_method
            )
            return url
        except Exception as e:
            logger.error(f"❌ Failed to generate presigned URL: {str(e)}")
            return self._generate_public_url(filename)
    
    def _update_performance_metrics(self, operation: str, time_taken: float, success: bool):
        """Update performance metrics"""
        
        if operation == "upload":
            if success:
                current_avg = self.performance_metrics["avg_upload_time"]
                # Simple moving average
                self.performance_metrics["avg_upload_time"] = (current_avg + time_taken) / 2
        
        elif operation == "download":
            if success:
                current_avg = self.performance_metrics["avg_download_time"]
                self.performance_metrics["avg_download_time"] = (current_avg + time_taken) / 2
        
        # Update success rate
        self.performance_metrics["success_rate"] = self._calculate_success_rate()
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate based on request history"""
        if self.request_count == 0:
            return 100.0
        
        success_count = self.request_count - self.error_count
        return (success_count / self.request_count) * 100.0
    
    def _verify_sync_metadata(self, metadata: Dict[str, str]) -> Dict[str, Any]:
        """Verify sync metadata for backup consistency"""
        
        sync_info = {
            "is_synced": False,
            "sync_source": metadata.get("sync_source"),
            "sync_timestamp": metadata.get("sync_timestamp"),
            "backup_timestamp": metadata.get("backup_timestamp"),
            "sync_lag": None
        }
        
        if sync_info["sync_timestamp"] and sync_info["backup_timestamp"]:
            try:
                sync_time = datetime.fromisoformat(sync_info["sync_timestamp"].replace('Z', '+00:00'))
                backup_time = datetime.fromisoformat(sync_info["backup_timestamp"].replace('Z', '+00:00'))
                
                sync_lag = (backup_time - sync_time).total_seconds()
                sync_info["sync_lag"] = sync_lag
                sync_info["is_synced"] = sync_lag >= 0  # Backup should be after or at sync time
                
                # Update performance metrics
                self.performance_metrics["sync_lag"] = sync_lag
                
            except Exception as e:
                logger.warning(f"Failed to parse sync timestamps: {str(e)}")
        
        return sync_info
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information and capabilities"""
        
        return {
            "provider": "backblaze_b2",
            "display_name": "Backblaze B2",
            "type": "backup_storage",
            "capabilities": {
                "upload": True,
                "download": True,
                "delete": True,
                "list": True,
                "presigned_urls": True,
                "metadata": True,
                "health_check": True,
                "sync_verification": True
            },
            "pricing": {
                "storage_cost_per_gb_month": 0.005,
                "download_cost_per_gb": 0.01,
                "class_a_transactions_per_1000": 0.004,
                "class_b_transactions_per_1000": 0.004
            },
            "limits": {
                "max_file_size": "10TB",
                "max_bucket_size": "unlimited",
                "max_files_per_bucket": "unlimited"
            },
            "regions": ["us-west-004", "eu-central-003"],
            "configuration": {
                "endpoint_url": self.config.endpoint_url,
                "bucket_name": self.config.bucket_name,
                "region": self.config.region
            },
            "status": {
                "healthy": self.health_status,
                "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
                "request_count": self.request_count,
                "error_count": self.error_count,
                "success_rate": self._calculate_success_rate()
            }
        }
    
    def get_cost_estimate(self, file_size_bytes: int, operations: Dict[str, int]) -> Dict[str, Any]:
        """Estimate costs for B2 operations"""
        
        file_size_gb = file_size_bytes / (1024**3)
        
        # Storage cost (per month)
        storage_cost = file_size_gb * 0.005
        
        # Transaction costs
        uploads = operations.get("uploads", 0)
        downloads = operations.get("downloads", 0)
        
        # Class A transactions (uploads, lists, etc.)
        class_a_cost = (uploads / 1000) * 0.004
        
        # Class B transactions (downloads)
        class_b_cost = (downloads / 1000) * 0.004
        
        # Download bandwidth cost
        download_gb = (file_size_bytes * downloads) / (1024**3)
        download_cost = download_gb * 0.01
        
        total_cost = storage_cost + class_a_cost + class_b_cost + download_cost
        
        return {
            "provider": "backblaze_b2",
            "file_size_gb": file_size_gb,
            "storage_cost_monthly": storage_cost,
            "class_a_transaction_cost": class_a_cost,
            "class_b_transaction_cost": class_b_cost,
            "download_bandwidth_cost": download_cost,
            "total_monthly_cost": total_cost,
            "cost_breakdown": {
                "storage": f"${storage_cost:.4f}",
                "uploads": f"${class_a_cost:.4f}",
                "downloads": f"${class_b_cost:.4f}",
                "bandwidth": f"${download_cost:.4f}"
            }
        }


# Global instance for easy access
_b2_provider = None

def get_b2_provider() -> BackblazeB2Provider:
    """Get global B2 provider instance"""
    global _b2_provider
    if _b2_provider is None:
        _b2_provider = BackblazeB2Provider()
    return _b2_provider

# Convenience functions
async def upload_to_b2(
    file_data: Union[bytes, str],
    filename: str,
    content_type: str = "application/octet-stream",
    metadata: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Convenience function to upload file to B2"""
    provider = get_b2_provider()
    return await provider.upload_file(file_data, filename, content_type, metadata)

async def download_from_b2(filename: str) -> Dict[str, Any]:
    """Convenience function to download file from B2"""
    provider = get_b2_provider()
    return await provider.download_file(filename)

async def check_b2_health() -> Dict[str, Any]:
    """Convenience function to check B2 health"""
    provider = get_b2_provider()
    return await provider.health_check()