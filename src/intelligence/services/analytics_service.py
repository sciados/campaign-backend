# analytics_service.py
import asyncio
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from src.core.database.analytics_repo import (
    save_analytics_data,
    get_user_analytics,
    get_aggregated_platform_stats,
    save_product_performance,
    get_product_performance
)
from src.intelligence.services.clickbank_service import fetch_sales_async as fetch_clickbank_sales_async
from src.core.database.clickbank_repo import get_clickbank_creds

class PlatformAnalyticsProcessor:
    """Base class for processing platform-specific analytics data"""

    def __init__(self, platform: str):
        self.platform = platform

    def normalize_metrics(self, raw_data: dict) -> dict:
        """Convert platform-specific data to standardized metrics"""
        raise NotImplementedError("Subclasses must implement normalize_metrics")

    def extract_product_data(self, raw_data: dict) -> List[dict]:
        """Extract individual product performance from raw data"""
        raise NotImplementedError("Subclasses must implement extract_product_data")

class ClickBankAnalyticsProcessor(PlatformAnalyticsProcessor):
    """ClickBank-specific analytics processor"""

    def __init__(self):
        super().__init__("clickbank")

    def normalize_metrics(self, raw_data: dict) -> dict:
        """Convert ClickBank API response to standardized metrics"""
        # ClickBank API structure may vary - adapt based on actual response
        if not raw_data:
            return self._empty_metrics()

        # Extract key metrics from ClickBank response
        try:
            return {
                "total_sales": raw_data.get("totalTransactions", 0),
                "total_revenue": raw_data.get("totalRevenue", 0.0),
                "conversion_rate": raw_data.get("conversionRate", 0.0),
                "refund_rate": raw_data.get("refundRate", 0.0),
                "avg_order_value": raw_data.get("averageOrderValue", 0.0),
                "platform": self.platform,
                "period_days": raw_data.get("periodDays", 30),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error normalizing ClickBank metrics: {e}")
            return self._empty_metrics()

    def extract_product_data(self, raw_data: dict) -> List[dict]:
        """Extract individual product performance from ClickBank data"""
        products = []

        try:
            # Adapt based on actual ClickBank API response structure
            product_data = raw_data.get("productBreakdown", [])

            for product in product_data:
                products.append({
                    "product_id": product.get("productId", "unknown"),
                    "product_name": product.get("productName", "Unknown Product"),
                    "sales": product.get("sales", 0),
                    "revenue": product.get("revenue", 0.0),
                    "conversion_rate": product.get("conversionRate", 0.0),
                    "refunds": product.get("refunds", 0)
                })
        except Exception as e:
            print(f"Error extracting ClickBank product data: {e}")

        return products

    def _empty_metrics(self) -> dict:
        """Return empty metrics structure"""
        return {
            "total_sales": 0,
            "total_revenue": 0.0,
            "conversion_rate": 0.0,
            "refund_rate": 0.0,
            "avg_order_value": 0.0,
            "platform": self.platform,
            "period_days": 30,
            "last_updated": datetime.now().isoformat()
        }

# Future platform processors can be added here:
# class JVZooAnalyticsProcessor(PlatformAnalyticsProcessor): ...
# class WarriorPlusAnalyticsProcessor(PlatformAnalyticsProcessor): ...

class UnifiedAnalyticsService:
    """Main service for handling analytics across all platforms"""

    def __init__(self):
        self.processors = {
            "clickbank": ClickBankAnalyticsProcessor(),
            # "jvzoo": JVZooAnalyticsProcessor(),
            # "warriorplus": WarriorPlusAnalyticsProcessor(),
        }

    async def fetch_and_store_user_analytics(self, user_id: str, platform: str, days: int = 30) -> dict:
        """Fetch analytics from platform and store in database"""
        if platform not in self.processors:
            raise ValueError(f"Platform {platform} not supported")

        processor = self.processors[platform]

        try:
            # Platform-specific data fetching
            if platform == "clickbank":
                raw_data = await self._fetch_clickbank_data(user_id, days)
            # elif platform == "jvzoo":
            #     raw_data = await self._fetch_jvzoo_data(user_id, days)
            else:
                raise ValueError(f"Data fetching not implemented for {platform}")

            # Process and normalize the data
            processed_metrics = processor.normalize_metrics(raw_data)

            # Store in database
            await save_analytics_data(user_id, platform, raw_data, processed_metrics)

            # Extract and store individual product performance
            product_data = processor.extract_product_data(raw_data)
            for product in product_data:
                await save_product_performance(
                    user_id=user_id,
                    platform=platform,
                    product_id=product["product_id"],
                    product_name=product["product_name"],
                    metrics=product
                )

            return processed_metrics

        except Exception as e:
            print(f"Error fetching analytics for {platform}: {e}")
            # Store empty metrics on error
            empty_metrics = processor._empty_metrics() if hasattr(processor, '_empty_metrics') else {}
            await save_analytics_data(user_id, platform, {}, empty_metrics)
            return empty_metrics

    async def _fetch_clickbank_data(self, user_id: str, days: int) -> dict:
        """Fetch ClickBank data using existing service"""
        try:
            # Use the async version to avoid event loop conflicts
            return await fetch_clickbank_sales_async(user_id, days)
        except Exception as e:
            print(f"Error fetching ClickBank data: {e}")
            raise e

    async def get_user_dashboard_data(self, user_id: str) -> dict:
        """Get comprehensive analytics data for user dashboard"""
        analytics = await get_user_analytics(user_id)

        dashboard_data = {
            "platforms": {},
            "total_metrics": {
                "total_sales": 0,
                "total_revenue": 0.0,
                "avg_conversion_rate": 0.0,
                "connected_platforms": 0
            }
        }

        total_revenue = 0.0
        total_sales = 0
        conversion_rates = []

        for platform_data in analytics:
            platform = platform_data["platform"]
            metrics = platform_data["metrics"]

            dashboard_data["platforms"][platform] = {
                "metrics": metrics,
                "last_updated": platform_data["last_updated"],
                "status": "connected" if metrics.get("total_sales", 0) > 0 else "no_data"
            }

            # Aggregate totals
            total_revenue += metrics.get("total_revenue", 0.0)
            total_sales += metrics.get("total_sales", 0)
            if metrics.get("conversion_rate", 0) > 0:
                conversion_rates.append(metrics["conversion_rate"])

        dashboard_data["total_metrics"] = {
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "avg_conversion_rate": sum(conversion_rates) / len(conversion_rates) if conversion_rates else 0.0,
            "connected_platforms": len(analytics)
        }

        return dashboard_data

    async def get_creator_analytics_summary(self) -> dict:
        """Get aggregated analytics for product creators"""
        return await get_aggregated_platform_stats()

    async def refresh_all_user_analytics(self, user_id: str) -> dict:
        """Refresh analytics for all connected platforms for a user"""
        results = {}

        # Check which platforms the user has connected
        connected_platforms = []

        # Check ClickBank
        try:
            clickbank_creds = await get_clickbank_creds(user_id)
        except Exception as e:
            print(f"Error checking ClickBank credentials: {e}")
            clickbank_creds = None

        if clickbank_creds:
            connected_platforms.append("clickbank")

        # Fetch fresh data for all connected platforms
        for platform in connected_platforms:
            try:
                results[platform] = await self.fetch_and_store_user_analytics(user_id, platform)
            except Exception as e:
                results[platform] = {"error": str(e)}

        return results

# Global service instance
analytics_service = UnifiedAnalyticsService()