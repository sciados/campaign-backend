# src/routes/health.py
"""
🔥 R2 Storage Health Check Endpoints
Add these to your FastAPI app to test R2 storage in Railway production
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import logging
import os

logger = logging.getLogger(__name__)

# Create health router
health_router = APIRouter(prefix="/health", tags=["health"])

@health_router.get("/storage")
async def check_storage_health():
    """Check overall storage system health"""
    try:
        from src.storage.universal_dual_storage import get_storage_manager
        
        storage_manager = get_storage_manager()
        health_status = await storage_manager.get_storage_health()
        
        return {
            "success": True,
            "status": "healthy" if health_status.get("overall_status") == "healthy" else "unhealthy",
            "timestamp": health_status.get("timestamp"),
            "providers": health_status.get("providers", {}),
            "configuration": health_status.get("configuration_status", {}),
            "recommendations": health_status.get("recommendations", [])
        }
    except Exception as e:
        logger.error(f"Storage health check failed: {str(e)}")
        return {
            "success": False,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc)
        }

@health_router.get("/r2")
async def check_r2_health():
    """Check Cloudflare R2 specific health"""
    try:
        from src.storage.providers.cloudflare_r2 import get_r2_provider
        
        r2_provider = get_r2_provider()
        health_status = await r2_provider.check_health()
        
        return {
            "success": True,
            "status": "healthy" if health_status.get("healthy") else "unhealthy",
            "provider": "cloudflare_r2",
            "response_time": health_status.get("response_time"),
            "endpoint": health_status.get("endpoint"),
            "bucket": health_status.get("bucket"),
            "custom_domain": health_status.get("custom_domain"),
            "error": health_status.get("error"),
            "last_check": health_status.get("last_check")
        }
    except Exception as e:
        logger.error(f"R2 health check failed: {str(e)}")
        return {
            "success": False,
            "status": "error",
            "provider": "cloudflare_r2",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@health_router.get("/r2/test-upload")
async def test_r2_upload():
    """Test R2 upload functionality with a small test file"""
    try:
        from src.storage.universal_dual_storage import get_storage_manager
        
        storage_manager = get_storage_manager()
        
        # Create test content
        test_content = f"R2 health check test - {datetime.now().isoformat()}\nThis is a test file to verify R2 upload functionality."
        test_filename = f"health-check-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
        
        # Test upload
        result = await storage_manager.save_content_dual_storage(
            content_data=test_content.encode(),
            content_type="document", 
            filename=test_filename,
            user_id="health-check",
            campaign_id="system-test",
            metadata={
                "test": "true", 
                "type": "health_check",
                "created_by": "health_endpoint"
            }
        )
        
        return {
            "success": True,
            "status": "upload_successful" if result.get("storage_status") == "success" else "upload_failed",
            "filename": result.get("filename"),
            "public_url": result.get("primary_url"),
            "presigned_url": result.get("presigned_url"),
            "file_size": result.get("file_size"),
            "original_size": result.get("original_size"),
            "storage_status": result.get("storage_status"),
            "providers": result.get("providers", {}),
            "cost_analysis": result.get("cost_analysis", {}),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"R2 upload test failed: {str(e)}")
        return {
            "success": False,
            "status": "upload_failed",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@health_router.get("/r2/config")
async def check_r2_configuration():
    """Check R2 configuration status and environment variables"""
    try:
        from src.storage.universal_dual_storage import validate_storage_configuration
        
        config_status = validate_storage_configuration()
        
        return {
            "success": True,
            "r2_configured": config_status.get("r2_configured"),
            "status": config_status.get("status"),
            "configuration_errors": config_status.get("configuration_errors", []),
            "recommendations": config_status.get("recommendations", []),
            "timestamp": config_status.get("timestamp"),
            "benefits": config_status.get("benefits", [])
        }
        
    except Exception as e:
        logger.error(f"R2 config check failed: {str(e)}")
        return {
            "success": False,
            "status": "configuration_check_failed",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@health_router.get("/r2/metrics")
async def get_r2_metrics():
    """Get R2 performance metrics and provider information"""
    try:
        from src.storage.providers.cloudflare_r2 import get_r2_provider
        
        r2_provider = get_r2_provider()
        
        # Get performance metrics
        metrics = r2_provider.get_performance_metrics()
        
        # Get provider info
        provider_info = r2_provider.get_provider_info()
        
        return {
            "success": True,
            "metrics": metrics,
            "provider_info": provider_info,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"R2 metrics check failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@health_router.get("/r2/debug/env")
async def debug_r2_environment():
    """Debug R2 environment variables (use only for troubleshooting)"""
    
    # Only enable in debug mode
    if not os.getenv("DEBUG", "false").lower() == "true":
        raise HTTPException(status_code=404, detail="Debug endpoint not available in production")
    
    try:
        vars_to_check = [
            "CLOUDFLARE_ACCOUNT_ID",
            "CLOUDFLARE_R2_ACCESS_KEY_ID", 
            "CLOUDFLARE_R2_SECRET_ACCESS_KEY",
            "CLOUDFLARE_R2_BUCKET_NAME",
            "R2_CUSTOM_DOMAIN",
            "DEBUG"
        ]
        
        env_status = {}
        for var in vars_to_check:
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                if "SECRET" in var or "ACCESS_KEY" in var:
                    env_status[var] = f"✅ {value[:4]}...{value[-4:]}" if len(value) > 8 else "✅ ***"
                else:
                    env_status[var] = f"✅ {value}"
            else:
                env_status[var] = "❌ NOT SET"
        
        return {
            "success": True,
            "environment_variables": env_status,
            "warning": "This is a debug endpoint - disable DEBUG=true in production",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Environment debug failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@health_router.get("/r2/recommendations") 
async def get_r2_recommendations():
    """Get R2 setup and optimization recommendations"""
    try:
        from src.storage.universal_dual_storage import get_storage_manager
        
        storage_manager = get_storage_manager()
        recommendations = storage_manager.get_provider_recommendations()
        
        return {
            "success": True,
            "recommendations": recommendations,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"R2 recommendations failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Health check summary endpoint
@health_router.get("/r2/summary")
async def r2_health_summary():
    """Complete R2 health summary - all checks in one endpoint"""
    
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": "checking",
        "checks": {}
    }
    
    # Configuration check
    try:
        config_result = await check_r2_configuration()
        summary["checks"]["configuration"] = {
            "status": "pass" if config_result.get("success") and config_result.get("r2_configured") else "fail",
            "details": config_result
        }
    except Exception as e:
        summary["checks"]["configuration"] = {"status": "error", "error": str(e)}
    
    # Health check
    try:
        health_result = await check_r2_health()
        summary["checks"]["health"] = {
            "status": "pass" if health_result.get("success") and health_result.get("status") == "healthy" else "fail",
            "details": health_result
        }
    except Exception as e:
        summary["checks"]["health"] = {"status": "error", "error": str(e)}
    
    # Upload test
    try:
        upload_result = await test_r2_upload()
        summary["checks"]["upload"] = {
            "status": "pass" if upload_result.get("success") and upload_result.get("status") == "upload_successful" else "fail",
            "details": upload_result
        }
    except Exception as e:
        summary["checks"]["upload"] = {"status": "error", "error": str(e)}
    
    # Determine overall status
    check_results = [check["status"] for check in summary["checks"].values()]
    
    if all(status == "pass" for status in check_results):
        summary["overall_status"] = "✅ All R2 systems operational"
    elif any(status == "pass" for status in check_results):
        summary["overall_status"] = "⚠️ Some R2 systems have issues"
    else:
        summary["overall_status"] = "❌ R2 systems not operational"
    
    return summary

# Export the router so it can be included in main.py
__all__ = ["health_router"]