# routes_analytics.py
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from src.intelligence.services.analytics_service import analytics_service
from src.core.database.session import get_async_db
from src.users.services.auth_service import AuthService

router = APIRouter(prefix="/analytics", tags=["Analytics"])
security = HTTPBearer()

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
) -> str:
    """Get current user ID from token"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return str(user.id)

class RefreshAnalyticsRequest(BaseModel):
    platform: Optional[str] = None  # If None, refresh all platforms
    days: int = 30

@router.get("/dashboard")
async def get_user_analytics_dashboard(
    user_id: str = Depends(get_current_user_id)
):
    """Get comprehensive analytics dashboard data for the user"""
    try:
        dashboard_data = await analytics_service.get_user_dashboard_data(user_id)
        return {
            "success": True,
            "data": dashboard_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refresh")
async def refresh_user_analytics(
    body: RefreshAnalyticsRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Refresh analytics data from connected platforms"""
    try:
        if body.platform:
            # Refresh specific platform
            result = await analytics_service.fetch_and_store_user_analytics(
                user_id, body.platform, body.days
            )
            return {
                "success": True,
                "data": {body.platform: result},
                "message": f"Analytics refreshed for {body.platform}"
            }
        else:
            # Refresh all platforms
            results = await analytics_service.refresh_all_user_analytics(user_id)
            return {
                "success": True,
                "data": results,
                "message": "Analytics refreshed for all connected platforms"
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/platforms/{platform}")
async def get_platform_analytics(
    platform: str,
    user_id: str = Depends(get_current_user_id),
    days: int = Query(30, description="Number of days for analytics")
):
    """Get analytics for a specific platform"""
    try:
        # Fetch fresh data
        result = await analytics_service.fetch_and_store_user_analytics(
            user_id, platform, days
        )
        return {
            "success": True,
            "data": result,
            "platform": platform
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/products")
async def get_product_analytics(
    user_id: str = Depends(get_current_user_id),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    product_id: Optional[str] = Query(None, description="Filter by product ID")
):
    """Get product-level analytics"""
    try:
        from src.core.database.analytics_repo import get_product_performance

        products = await get_product_performance(
            user_id=user_id,
            platform=platform,
            product_id=product_id
        )

        return {
            "success": True,
            "data": products
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Admin/Creator endpoints
@router.get("/admin/summary")
async def get_admin_analytics_summary(
    user_id: str = Depends(get_current_user_id)
    # Add admin role check here
):
    """Get aggregated analytics summary for admins/creators"""
    try:
        summary = await analytics_service.get_creator_analytics_summary()
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/admin/products/{product_id}")
async def get_product_performance_summary(
    product_id: str,
    user_id: str = Depends(get_current_user_id)
    # Add creator role check here
):
    """Get performance summary for a specific product across all users"""
    try:
        from src.core.database.analytics_repo import get_product_performance

        performance = await get_product_performance(product_id=product_id)

        # Aggregate metrics across all users for this product
        total_sales = sum(p["metrics"].get("sales", 0) for p in performance)
        total_revenue = sum(p["metrics"].get("revenue", 0.0) for p in performance)
        active_promoters = len(performance)

        summary = {
            "product_id": product_id,
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "active_promoters": active_promoters,
            "promoter_details": performance
        }

        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))