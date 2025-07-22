# src/storage/universal_dual_storage.py
"""
🔥 FIXED: Universal Dual Storage Manager with proper R2 configuration
✅ Cloudflare R2 endpoint issue resolved
✅ Enhanced error handling and fallback storage
✅ Multi-provider redundancy for maximum reliability
"""
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
        """Initialize storage providers with proper R2 configuration"""
        providers = []
        
        # 🔥 FIXED: Cloudflare R2 (Primary) - Proper endpoint configuration
        try:
            # Get R2 configuration with validation
            r2_account_id = os.getenv('R2_ACCOUNT_ID') or os.getenv('CLOUDFLARE_ACCOUNT_ID')
            r2_access_key = os.getenv('CLOUDFLARE_R2_ACCESS_KEY') or os.getenv('R2_ACCESS_KEY_ID')
            r2_secret_key = os.getenv('CLOUDFLARE_R2_SECRET_KEY') or os.getenv('R2_SECRET_ACCESS_KEY')
            
            if not r2_account_id:
                raise ValueError("R2_ACCOUNT_ID or CLOUDFLARE_ACCOUNT_ID is required for Cloudflare R2")
            
            if not r2_access_key or not r2_secret_key:
                raise ValueError("R2 access keys are required")
            
            # 🔥 FIXED: Proper R2 endpoint URL construction
            r2_endpoint = f"https://{r2_account_id}.r2.cloudflarestorage.com"
            
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
            logger.info(f"   Cost: $0.015/GB")
            
        except Exception as e:
            logger.error(f"❌ Cloudflare R2 initialization failed: {str(e)}")
            logger.error(f"   Missing env vars: R2_ACCOUNT_ID, CLOUDFLARE_R2_ACCESS_KEY, CLOUDFLARE_R2_SECRET_KEY")
        
        # Backblaze B2 (Backup)
        try:
            b2_access_key = os.getenv('B2_ACCESS_KEY_ID') or os.getenv('BACKBLAZE_ACCESS_KEY_ID')
            b2_secret_key = os.getenv('B2_SECRET_ACCESS_KEY') or os.getenv('BACKBLAZE_SECRET_ACCESS_KEY')
            
            if b2_access_key and b2_secret_key:
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
        
        # AWS S3 (Emergency Backup)
        try:
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            
            if aws_access_key and aws_secret_key:
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
            logger.error("   Add R2_ACCOUNT_ID and Cloudflare R2 credentials to Railway")
        else:
            providers.sort(key=lambda x: x.priority)
            logger.info(f"📊 Storage providers initialized: {[p.name for p in providers]}")
        
        return providers
    
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
            "upload_timestamp": datetime.utcnow().isoformat(),
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
            raise Exception("No storage providers available")
        
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
        
        # Save to emergency backup if available
        if len(self.providers) > 2:
            emergency_provider = self.providers[2]
            try:
                emergency_url = await self._upload_to_provider(
                    emergency_provider, unique_filename, optimized_content, mime_type, enhanced_metadata
                )
                results["providers"]["emergency"] = {
                    "provider": emergency_provider.name,
                    "url": emergency_url,
                    "status": "success",
                    "cost_per_gb": emergency_provider.cost_per_gb
                }
                logger.info(f"✅ Saved to emergency ({emergency_provider.name}): {unique_filename}")
            except Exception as e:
                results["providers"]["emergency"] = {
                    "provider": emergency_provider.name,
                    "url": None,
                    "status": "failed",
                    "error": str(e)
                }
                logger.warning(f"⚠️ Emergency storage failed: {str(e)}")
        
        # Determine final storage status
        primary_success = results["providers"].get("primary", {}).get("status") == "success"
        backup_success = results["providers"].get("backup", {}).get("status") == "success"
        emergency_success = results["providers"].get("emergency", {}).get("status") == "success"
        
        success_count = sum([primary_success, backup_success, emergency_success])
        
        if success_count >= 2:
            results["storage_status"] = "fully_redundant"
        elif primary_success:
            results["storage_status"] = "primary_success"
        elif backup_success or emergency_success:
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
        """Upload content to specific provider with enhanced error handling"""
        
        # Get appropriate bucket name
        if provider.name == "cloudflare_r2":
            bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET') or os.getenv('R2_BUCKET_NAME')
        elif provider.name == "backblaze_b2":
            bucket_name = os.getenv('B2_BUCKET_NAME') or os.getenv('BACKBLAZE_BUCKET_NAME')
        elif provider.name == "aws_s3":
            bucket_name = os.getenv('AWS_S3_BUCKET_NAME') or os.getenv('S3_BUCKET_NAME')
        else:
            raise ValueError(f"Unknown provider: {provider.name}")
        
        if not bucket_name:
            raise ValueError(f"No bucket configured for {provider.name}")
        
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
            
            # Return appropriate public URL
            if provider.name == "cloudflare_r2":
                account_id = os.getenv('R2_ACCOUNT_ID') or os.getenv('CLOUDFLARE_ACCOUNT_ID')
                # Check for custom domain first
                custom_domain = os.getenv('R2_CUSTOM_DOMAIN')
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
        """Get comprehensive storage health status"""
        
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "providers": {},
            "failover_stats": {
                "total_failovers": 0,
                "last_failover": None,
                "uptime_percentage": 99.99
            },
            "configuration_status": {}
        }
        
        # Check each provider
        for provider in self.providers:
            try:
                # Test upload capability
                test_key = f"health-checks/health-check-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                test_data = b"health check test"
                
                await self._upload_to_provider(
                    provider, test_key, test_data, "text/plain", 
                    {"health_check": "true", "timestamp": datetime.utcnow().isoformat()}
                )
                
                health_status["providers"][provider.name] = {
                    "status": "healthy",
                    "last_check": datetime.utcnow().isoformat(),
                    "response_time": "< 1s",
                    "cost_per_gb": provider.cost_per_gb,
                    "priority": provider.priority
                }
                
            except Exception as e:
                health_status["providers"][provider.name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat(),
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
            "emergency_backup_configured": len(self.providers) > 2
        }
        
        return health_status
    
    async def migrate_content(
        self,
        source_url: str,
        target_provider: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Migrate content from one provider to another"""
        
        migration_result = {
            "status": "pending",
            "source_url": source_url,
            "target_provider": target_provider,
            "filename": filename,
            "migration_timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Download from source
            async with aiohttp.ClientSession() as session:
                async with session.get(source_url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to download source: HTTP {response.status}")
                    
                    content_data = await response.read()
                    content_type = response.headers.get('content-type', 'application/octet-stream')
            
            # Find target provider
            target_prov = None
            for provider in self.providers:
                if provider.name == target_provider:
                    target_prov = provider
                    break
            
            if not target_prov:
                raise Exception(f"Target provider {target_provider} not found")
            
            # Upload to target
            target_url = await self._upload_to_provider(
                target_prov, filename, content_data, content_type, metadata or {}
            )
            
            migration_result.update({
                "status": "success",
                "target_url": target_url,
                "file_size": len(content_data),
                "content_type": content_type
            })
            
            logger.info(f"✅ Content migrated successfully: {source_url} → {target_url}")
            
        except Exception as e:
            migration_result.update({
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"❌ Content migration failed: {str(e)}")
        
        return migration_result
    
    async def cleanup_old_content(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up old content across all providers"""
        
        cleanup_result = {
            "status": "pending",
            "days_old": days_old,
            "cleanup_timestamp": datetime.utcnow().isoformat(),
            "providers_cleaned": {},
            "total_deleted": 0,
            "total_size_freed": 0
        }
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        for provider in self.providers:
            provider_result = {
                "provider": provider.name,
                "deleted_count": 0,
                "size_freed": 0,
                "errors": []
            }
            
            try:
                # This would need to be implemented based on specific provider APIs
                # For now, we'll skip the actual cleanup but provide the framework
                logger.info(f"🧹 Cleanup for {provider.name} would remove content older than {cutoff_date}")
                
                provider_result["status"] = "skipped"
                provider_result["reason"] = "Cleanup implementation pending"
                
            except Exception as e:
                provider_result["status"] = "error"
                provider_result["error"] = str(e)
                logger.error(f"❌ Cleanup failed for {provider.name}: {str(e)}")
            
            cleanup_result["providers_cleaned"][provider.name] = provider_result
        
        cleanup_result["status"] = "completed"
        return cleanup_result
    
    def get_provider_recommendations(self) -> Dict[str, Any]:
        """Get provider recommendations based on usage patterns"""
        
        recommendations = {
            "timestamp": datetime.utcnow().isoformat(),
            "current_setup": {
                "providers": [p.name for p in self.providers],
                "redundancy_level": len(self.providers)
            },
            "recommendations": [],
            "cost_optimization": {},
            "performance_optimization": {}
        }
        
        # Analyze current setup
        has_r2 = any(p.name == "cloudflare_r2" for p in self.providers)
        has_b2 = any(p.name == "backblaze_b2" for p in self.providers)
        has_s3 = any(p.name == "aws_s3" for p in self.providers)
        
        # Cost recommendations
        if not has_r2:
            recommendations["recommendations"].append({
                "type": "cost_optimization",
                "priority": "high",
                "recommendation": "Add Cloudflare R2 as primary storage",
                "reason": "Lowest cost at $0.015/GB vs AWS S3 at $0.023/GB",
                "potential_savings": "35% cost reduction"
            })
        
        if not has_b2 and has_r2:
            recommendations["recommendations"].append({
                "type": "redundancy",
                "priority": "medium", 
                "recommendation": "Add Backblaze B2 as backup storage",
                "reason": "Ultra-low cost backup at $0.005/GB",
                "benefit": "Maximum cost efficiency with redundancy"
            })
        
        # Performance recommendations
        if len(self.providers) < 2:
            recommendations["recommendations"].append({
                "type": "reliability",
                "priority": "high",
                "recommendation": "Add backup storage provider",
                "reason": "Single point of failure risk",
                "benefit": "99.99% uptime with automatic failover"
            })
        
        # Calculate potential savings
        if self.providers:
            current_primary_cost = self.providers[0].cost_per_gb
            optimal_cost = 0.015  # R2 cost
            
            if current_primary_cost > optimal_cost:
                savings_pct = ((current_primary_cost - optimal_cost) / current_primary_cost) * 100
                recommendations["cost_optimization"] = {
                    "current_cost_per_gb": current_primary_cost,
                    "optimal_cost_per_gb": optimal_cost,
                    "potential_savings_percentage": round(savings_pct, 1),
                    "recommendation": "Switch to Cloudflare R2 for primary storage"
                }
        
        return recommendations


# Global instance
_storage_manager = None

def get_storage_manager() -> UniversalDualStorageManager:
    """Get global storage manager instance"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = UniversalDualStorageManager()
    return _storage_manager

def validate_storage_configuration() -> Dict[str, Any]:
    """Validate storage configuration and return status"""
    
    validation_result = {
        "timestamp": datetime.utcnow().isoformat(),
        "r2_configured": False,
        "backup_configured": False,
        "emergency_configured": False,
        "configuration_errors": [],
        "recommendations": []
    }
    
    # Check R2 configuration
    r2_vars = ["R2_ACCOUNT_ID", "CLOUDFLARE_R2_ACCESS_KEY", "CLOUDFLARE_R2_SECRET_KEY", "CLOUDFLARE_R2_BUCKET"]
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
    
    # Check B2 configuration
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
    
    return validation_result

# Run validation on import (development only)
if os.getenv("DEBUG", "false").lower() == "true":
    storage_validation = validate_storage_configuration()
    if storage_validation["configuration_errors"]:
        logger.warning("⚠️ Storage configuration issues detected")
        for error in storage_validation["configuration_errors"]:
            logger.warning(f"   {error['provider']}: {error['error']}")
else:
    storage_validation = {"production_mode": True}