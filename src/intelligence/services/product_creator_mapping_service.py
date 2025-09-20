# product_creator_mapping_service.py
import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from sqlalchemy import text
from src.core.database.session import AsyncSessionManager

class ProductCreatorMappingService:
    """Service for managing product-creator mappings and analytics aggregation"""

    async def register_product_mapping(
        self,
        platform: str,
        product_sku: str,
        product_name: str,
        vendor_account: str,
        creator_user_id: str
    ) -> dict:
        """Register a product with its creator"""
        query = text("""
        INSERT INTO product_creator_mappings (
            platform, product_sku, product_name, vendor_account, creator_user_id
        ) VALUES (
            :platform, :product_sku, :product_name, :vendor_account, :creator_user_id
        ) ON CONFLICT (platform, product_sku) DO UPDATE
        SET product_name = :product_name,
            vendor_account = :vendor_account,
            creator_user_id = :creator_user_id,
            updated_at = NOW()
        """)

        async with AsyncSessionManager.get_session() as session:
            await session.execute(query, {
                "platform": platform,
                "product_sku": product_sku,
                "product_name": product_name,
                "vendor_account": vendor_account,
                "creator_user_id": creator_user_id
            })
            await session.commit()

        return {"status": "success", "message": "Product mapping registered"}

    async def get_creator_for_product(self, platform: str, product_sku: str) -> Optional[str]:
        """Get the creator user ID for a given product"""
        query = text("""
        SELECT creator_user_id FROM product_creator_mappings
        WHERE platform = :platform AND product_sku = :product_sku
        """)

        async with AsyncSessionManager.get_session() as session:
            result = await session.execute(query, {
                "platform": platform,
                "product_sku": product_sku
            })
            row = result.fetchone()
            return row.creator_user_id if row else None

    async def funnel_analytics_to_creators(self, affiliate_user_id: str, product_performance: List[dict]) -> dict:
        """Process affiliate analytics and funnel to appropriate creators"""
        funneled_count = 0
        errors = []

        for product in product_performance:
            try:
                platform = product.get("platform", "unknown")
                product_sku = product.get("sku")

                if not product_sku:
                    continue

                # Find the creator for this product
                creator_user_id = await self.get_creator_for_product(platform, product_sku)

                if not creator_user_id:
                    # No creator mapping found - skip this product
                    continue

                # Store affiliate performance for creator insights
                await self._store_affiliate_performance(
                    affiliate_user_id=affiliate_user_id,
                    creator_user_id=creator_user_id,
                    platform=platform,
                    product_sku=product_sku,
                    performance_data=product
                )

                # Update aggregated creator analytics
                await self._update_creator_analytics(
                    creator_user_id=creator_user_id,
                    platform=platform,
                    product_sku=product_sku,
                    affiliate_data=product
                )

                funneled_count += 1

            except Exception as e:
                errors.append(f"Error processing product {product.get('sku', 'unknown')}: {str(e)}")

        return {
            "funneled_count": funneled_count,
            "total_products": len(product_performance),
            "errors": errors
        }

    async def _store_affiliate_performance(
        self,
        affiliate_user_id: str,
        creator_user_id: str,
        platform: str,
        product_sku: str,
        performance_data: dict
    ):
        """Store individual affiliate performance data"""
        period_start = date.today() - timedelta(days=30)
        period_end = date.today()

        query = text("""
        INSERT INTO affiliate_product_performance (
            affiliate_user_id, creator_user_id, platform, product_sku,
            sales, revenue, quantity, conversion_rate,
            period_start, period_end, performance_data
        ) VALUES (
            :affiliate_user_id, :creator_user_id, :platform, :product_sku,
            :sales, :revenue, :quantity, :conversion_rate,
            :period_start, :period_end, :performance_data
        ) ON CONFLICT (affiliate_user_id, creator_user_id, platform, product_sku, period_start, period_end)
        DO UPDATE SET
            sales = :sales,
            revenue = :revenue,
            quantity = :quantity,
            conversion_rate = :conversion_rate,
            performance_data = :performance_data,
            updated_at = NOW()
        """)

        async with AsyncSessionManager.get_session() as session:
            await session.execute(query, {
                "affiliate_user_id": affiliate_user_id,
                "creator_user_id": creator_user_id,
                "platform": platform,
                "product_sku": product_sku,
                "sales": performance_data.get("total_sales", 0),
                "revenue": float(performance_data.get("total_revenue", 0.0)),
                "quantity": performance_data.get("total_quantity", 0),
                "conversion_rate": 0.0,  # Will be calculated later
                "period_start": period_start,
                "period_end": period_end,
                "performance_data": json.dumps(performance_data)
            })
            await session.commit()

    async def _update_creator_analytics(
        self,
        creator_user_id: str,
        platform: str,
        product_sku: str,
        affiliate_data: dict
    ):
        """Update aggregated analytics for product creator"""
        period_start = date.today() - timedelta(days=30)
        period_end = date.today()

        # Get current aggregated data
        query = text("""
        SELECT total_affiliates, total_sales, total_revenue, total_quantity, affiliate_data
        FROM creator_product_analytics
        WHERE creator_user_id = :creator_user_id
        AND platform = :platform
        AND product_sku = :product_sku
        AND period_start = :period_start
        AND period_end = :period_end
        """)

        async with AsyncSessionManager.get_session() as session:
            result = await session.execute(query, {
                "creator_user_id": creator_user_id,
                "platform": platform,
                "product_sku": product_sku,
                "period_start": period_start,
                "period_end": period_end
            })
            row = result.fetchone()

            if row:
                # Update existing record
                existing_data = json.loads(row.affiliate_data) if row.affiliate_data else []
                existing_data.append(affiliate_data)

                update_query = text("""
                UPDATE creator_product_analytics SET
                    total_affiliates = total_affiliates + 1,
                    total_sales = total_sales + :sales,
                    total_revenue = total_revenue + :revenue,
                    total_quantity = total_quantity + :quantity,
                    affiliate_data = :affiliate_data,
                    updated_at = NOW()
                WHERE creator_user_id = :creator_user_id
                AND platform = :platform
                AND product_sku = :product_sku
                AND period_start = :period_start
                AND period_end = :period_end
                """)

                await session.execute(update_query, {
                    "creator_user_id": creator_user_id,
                    "platform": platform,
                    "product_sku": product_sku,
                    "period_start": period_start,
                    "period_end": period_end,
                    "sales": affiliate_data.get("total_sales", 0),
                    "revenue": float(affiliate_data.get("total_revenue", 0.0)),
                    "quantity": affiliate_data.get("total_quantity", 0),
                    "affiliate_data": json.dumps(existing_data)
                })
            else:
                # Create new record
                insert_query = text("""
                INSERT INTO creator_product_analytics (
                    creator_user_id, platform, product_sku,
                    total_affiliates, total_sales, total_revenue, total_quantity,
                    period_start, period_end, affiliate_data
                ) VALUES (
                    :creator_user_id, :platform, :product_sku,
                    1, :sales, :revenue, :quantity,
                    :period_start, :period_end, :affiliate_data
                )
                """)

                await session.execute(insert_query, {
                    "creator_user_id": creator_user_id,
                    "platform": platform,
                    "product_sku": product_sku,
                    "sales": affiliate_data.get("total_sales", 0),
                    "revenue": float(affiliate_data.get("total_revenue", 0.0)),
                    "quantity": affiliate_data.get("total_quantity", 0),
                    "period_start": period_start,
                    "period_end": period_end,
                    "affiliate_data": json.dumps([affiliate_data])
                })

            await session.commit()

    async def get_creator_analytics(self, creator_user_id: str, platform: Optional[str] = None) -> List[dict]:
        """Get aggregated analytics for a product creator"""
        if platform:
            query = text("""
            SELECT ca.*, pcm.product_name, pcm.vendor_account
            FROM creator_product_analytics ca
            JOIN product_creator_mappings pcm ON (
                ca.creator_user_id = pcm.creator_user_id
                AND ca.platform = pcm.platform
                AND ca.product_sku = pcm.product_sku
            )
            WHERE ca.creator_user_id = :creator_user_id AND ca.platform = :platform
            ORDER BY ca.total_revenue DESC
            """)
            params = {"creator_user_id": creator_user_id, "platform": platform}
        else:
            query = text("""
            SELECT ca.*, pcm.product_name, pcm.vendor_account
            FROM creator_product_analytics ca
            JOIN product_creator_mappings pcm ON (
                ca.creator_user_id = pcm.creator_user_id
                AND ca.platform = pcm.platform
                AND ca.product_sku = pcm.product_sku
            )
            WHERE ca.creator_user_id = :creator_user_id
            ORDER BY ca.total_revenue DESC
            """)
            params = {"creator_user_id": creator_user_id}

        async with AsyncSessionManager.get_session() as session:
            result = await session.execute(query, params)
            rows = result.fetchall()

            return [
                {
                    "platform": row.platform,
                    "product_sku": row.product_sku,
                    "product_name": row.product_name,
                    "vendor_account": row.vendor_account,
                    "total_affiliates": row.total_affiliates,
                    "total_sales": row.total_sales,
                    "total_revenue": float(row.total_revenue),
                    "total_quantity": row.total_quantity,
                    "avg_conversion_rate": float(row.avg_conversion_rate),
                    "period_start": row.period_start.isoformat(),
                    "period_end": row.period_end.isoformat(),
                    "affiliate_data": json.loads(row.affiliate_data) if row.affiliate_data else []
                }
                for row in rows
            ]

# Global service instance
product_creator_mapping_service = ProductCreatorMappingService()