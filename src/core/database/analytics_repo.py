# analytics_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from src.core.database.session import AsyncSessionManager

async def save_analytics_data(
    user_id: str,
    platform: str,
    raw_data: dict,
    processed_metrics: dict
):
    """Save analytics data for any platform"""
    query = text("""
    INSERT INTO platform_analytics (
        user_id, platform, raw_data, processed_metrics,
        created_at, updated_at
    ) VALUES (
        :user_id, :platform, :raw_data, :processed_metrics,
        NOW(), NOW()
    ) ON CONFLICT (user_id, platform) DO UPDATE
    SET raw_data = :raw_data,
        processed_metrics = :processed_metrics,
        updated_at = NOW()
    """)

    async with AsyncSessionManager.get_session() as session:
        await session.execute(query, {
            "user_id": user_id,
            "platform": platform,
            "raw_data": json.dumps(raw_data),
            "processed_metrics": json.dumps(processed_metrics)
        })
        await session.commit()

async def get_user_analytics(user_id: str, platform: Optional[str] = None) -> List[Dict]:
    """Get analytics for user across all platforms or specific platform"""
    if platform:
        query = text("""
        SELECT platform, processed_metrics, raw_data, updated_at
        FROM platform_analytics
        WHERE user_id = :user_id AND platform = :platform
        ORDER BY updated_at DESC
        """)
        params = {"user_id": user_id, "platform": platform}
    else:
        query = text("""
        SELECT platform, processed_metrics, raw_data, updated_at
        FROM platform_analytics
        WHERE user_id = :user_id
        ORDER BY platform, updated_at DESC
        """)
        params = {"user_id": user_id}

    async with AsyncSessionManager.get_session() as session:
        result = await session.execute(query, params)
        rows = result.fetchall()
        return [
            {
                "platform": row.platform,
                "metrics": json.loads(row.processed_metrics) if isinstance(row.processed_metrics, str) else row.processed_metrics,
                "raw_data": json.loads(row.raw_data) if isinstance(row.raw_data, str) else row.raw_data,
                "last_updated": row.updated_at
            }
            for row in rows
        ]

async def get_aggregated_platform_stats() -> Dict:
    """Get aggregated stats across all platforms for admin/creator view"""
    query = text("""
    SELECT
        platform,
        COUNT(DISTINCT user_id) as connected_users,
        AVG(CAST(processed_metrics->>'total_sales' AS NUMERIC)) as avg_sales,
        SUM(CAST(processed_metrics->>'total_revenue' AS NUMERIC)) as total_revenue
    FROM platform_analytics
    WHERE updated_at > NOW() - INTERVAL '30 days'
    GROUP BY platform
    """)

    async with AsyncSessionManager.get_session() as session:
        result = await session.execute(query)
        rows = result.fetchall()
        return {
            row.platform: {
                "connected_users": row.connected_users,
                "avg_sales": float(row.avg_sales or 0),
                "total_revenue": float(row.total_revenue or 0)
            }
            for row in rows
        }

async def save_product_performance(
    user_id: str,
    platform: str,
    product_id: str,
    product_name: str,
    metrics: dict
):
    """Save individual product performance data"""
    query = text("""
    INSERT INTO product_analytics (
        user_id, platform, product_id, product_name,
        metrics, created_at, updated_at
    ) VALUES (
        :user_id, :platform, :product_id, :product_name,
        :metrics, NOW(), NOW()
    ) ON CONFLICT (user_id, platform, product_id) DO UPDATE
    SET metrics = :metrics,
        product_name = :product_name,
        updated_at = NOW()
    """)

    async with AsyncSessionManager.get_session() as session:
        await session.execute(query, {
            "user_id": user_id,
            "platform": platform,
            "product_id": product_id,
            "product_name": product_name,
            "metrics": json.dumps(metrics)
        })
        await session.commit()

async def get_product_performance(
    user_id: Optional[str] = None,
    platform: Optional[str] = None,
    product_id: Optional[str] = None
) -> List[Dict]:
    """Get product performance data with flexible filtering"""
    conditions = []
    params = {}

    if user_id:
        conditions.append("user_id = :user_id")
        params["user_id"] = user_id
    if platform:
        conditions.append("platform = :platform")
        params["platform"] = platform
    if product_id:
        conditions.append("product_id = :product_id")
        params["product_id"] = product_id

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    query = text(f"""
    SELECT user_id, platform, product_id, product_name,
           metrics, updated_at
    FROM product_analytics
    WHERE {where_clause}
    ORDER BY updated_at DESC
    """)

    async with AsyncSessionManager.get_session() as session:
        result = await session.execute(query, params)
        rows = result.fetchall()
        return [
            {
                "user_id": row.user_id,
                "platform": row.platform,
                "product_id": row.product_id,
                "product_name": row.product_name,
                "metrics": json.loads(row.metrics) if isinstance(row.metrics, str) else row.metrics,
                "last_updated": row.updated_at
            }
            for row in rows
        ]