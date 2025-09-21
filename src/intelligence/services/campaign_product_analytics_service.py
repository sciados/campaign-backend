# campaign_product_analytics_service.py
"""
Enhanced analytics service that leverages the Campaign → Product → Creator relationship
for simplified filtering and analytics aggregation.
"""

import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
from sqlalchemy import text
from src.core.database.session import AsyncSessionManager

class CampaignProductAnalyticsService:
    """Service for campaign-product-creator analytics relationships"""

    async def link_campaign_to_product(
        self,
        campaign_id: str,
        platform: str,
        product_sku: str,
        product_name: str,
        creator_user_id: str
    ) -> dict:
        """Link a campaign to a specific product and creator"""

        # First ensure the product-creator mapping exists
        await self._ensure_product_creator_mapping(
            platform=platform,
            product_sku=product_sku,
            product_name=product_name,
            creator_user_id=creator_user_id
        )

        # Then link the campaign to this product
        query = text("""
        INSERT INTO campaign_product_links (
            campaign_id, platform, product_sku, linked_at
        ) VALUES (
            :campaign_id, :platform, :product_sku, NOW()
        ) ON CONFLICT (campaign_id) DO UPDATE
        SET platform = :platform,
            product_sku = :product_sku,
            linked_at = NOW()
        """)

        try:
            async with AsyncSessionManager.get_session() as session:
                await session.execute(query, {
                    "campaign_id": campaign_id,
                    "platform": platform,
                    "product_sku": product_sku
                })
                await session.commit()

            return {"status": "success", "message": "Campaign linked to product"}
        except Exception as e:
            # Create the table if it doesn't exist
            await self._create_campaign_product_links_table()

            # Retry the insert
            async with AsyncSessionManager.get_session() as session:
                await session.execute(query, {
                    "campaign_id": campaign_id,
                    "platform": platform,
                    "product_sku": product_sku
                })
                await session.commit()

            return {"status": "success", "message": "Campaign linked to product"}

    async def _create_campaign_product_links_table(self):
        """Create the campaign-product links table if it doesn't exist"""
        query = text("""
        CREATE TABLE IF NOT EXISTS campaign_product_links (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            campaign_id UUID NOT NULL,
            platform VARCHAR(50) NOT NULL,
            product_sku VARCHAR(255) NOT NULL,
            linked_at TIMESTAMP DEFAULT NOW(),

            -- Ensure one product per campaign
            UNIQUE (campaign_id),

            -- Foreign key to campaigns
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,

            -- Foreign key to product-creator mappings
            FOREIGN KEY (platform, product_sku) REFERENCES product_creator_mappings(platform, product_sku)
        );

        CREATE INDEX IF NOT EXISTS idx_campaign_product_links_campaign ON campaign_product_links(campaign_id);
        CREATE INDEX IF NOT EXISTS idx_campaign_product_links_product ON campaign_product_links(platform, product_sku);
        """)

        async with AsyncSessionManager.get_session() as session:
            await session.execute(query)
            await session.commit()

    async def _ensure_product_creator_mapping(
        self,
        platform: str,
        product_sku: str,
        product_name: str,
        creator_user_id: str
    ):
        """Ensure product-creator mapping exists"""
        query = text("""
        INSERT INTO product_creator_mappings (
            platform, product_sku, product_name, vendor_account, creator_user_id
        ) VALUES (
            :platform, :product_sku, :product_name, '', :creator_user_id
        ) ON CONFLICT (platform, product_sku) DO UPDATE
        SET product_name = :product_name,
            creator_user_id = :creator_user_id,
            updated_at = NOW()
        """)

        async with AsyncSessionManager.get_session() as session:
            await session.execute(query, {
                "platform": platform,
                "product_sku": product_sku,
                "product_name": product_name,
                "creator_user_id": creator_user_id
            })
            await session.commit()

    async def get_campaign_analytics_with_product_context(self, campaign_id: str) -> dict:
        """Get analytics for a specific campaign with its product and creator context"""
        query = text("""
        SELECT
            c.id as campaign_id,
            c.name as campaign_name,
            c.campaign_type,
            c.status as campaign_status,

            cpl.platform,
            cpl.product_sku,

            pcm.product_name,
            pcm.creator_user_id,

            -- Get analytics data for this specific product
            cpa.total_sales,
            cpa.total_revenue,
            cpa.total_quantity,
            cpa.total_affiliates,
            cpa.period_start,
            cpa.period_end

        FROM campaigns c
        LEFT JOIN campaign_product_links cpl ON c.id = cpl.campaign_id
        LEFT JOIN product_creator_mappings pcm ON (cpl.platform = pcm.platform AND cpl.product_sku = pcm.product_sku)
        LEFT JOIN creator_product_analytics cpa ON (
            pcm.creator_user_id = cpa.creator_user_id
            AND pcm.platform = cpa.platform
            AND pcm.product_sku = cpa.product_sku
        )
        WHERE c.id = :campaign_id
        """)

        async with AsyncSessionManager.get_session() as session:
            result = await session.execute(query, {"campaign_id": campaign_id})
            row = result.fetchone()

            if not row:
                return {"error": "Campaign not found"}

            return {
                "campaign": {
                    "id": row.campaign_id,
                    "name": row.campaign_name,
                    "type": row.campaign_type,
                    "status": row.campaign_status
                },
                "product": {
                    "platform": row.platform,
                    "sku": row.product_sku,
                    "name": row.product_name,
                    "creator_user_id": row.creator_user_id
                },
                "analytics": {
                    "total_sales": row.total_sales or 0,
                    "total_revenue": float(row.total_revenue or 0),
                    "total_quantity": row.total_quantity or 0,
                    "total_affiliates": row.total_affiliates or 0,
                    "period_start": row.period_start.isoformat() if row.period_start else None,
                    "period_end": row.period_end.isoformat() if row.period_end else None
                }
            }

    async def get_creator_campaigns_performance(self, creator_user_id: str) -> List[dict]:
        """Get all campaigns promoting this creator's products"""
        query = text("""
        SELECT
            c.id as campaign_id,
            c.name as campaign_name,
            c.campaign_type,
            c.status as campaign_status,
            c.user_id as affiliate_user_id,

            pcm.platform,
            pcm.product_sku,
            pcm.product_name,

            -- Get affiliate performance for this specific campaign's product
            app.sales as affiliate_sales,
            app.revenue as affiliate_revenue,
            app.quantity as affiliate_quantity,
            app.period_start,
            app.period_end

        FROM product_creator_mappings pcm
        JOIN campaign_product_links cpl ON (pcm.platform = cpl.platform AND pcm.product_sku = cpl.product_sku)
        JOIN campaigns c ON cpl.campaign_id = c.id
        LEFT JOIN affiliate_product_performance app ON (
            c.user_id = app.affiliate_user_id
            AND pcm.creator_user_id = app.creator_user_id
            AND pcm.platform = app.platform
            AND pcm.product_sku = app.product_sku
        )
        WHERE pcm.creator_user_id = :creator_user_id
        ORDER BY app.revenue DESC NULLS LAST, c.created_at DESC
        """)

        async with AsyncSessionManager.get_session() as session:
            result = await session.execute(query, {"creator_user_id": creator_user_id})
            rows = result.fetchall()

            campaigns = []
            for row in rows:
                campaigns.append({
                    "campaign": {
                        "id": row.campaign_id,
                        "name": row.campaign_name,
                        "type": row.campaign_type,
                        "status": row.campaign_status,
                        "affiliate_user_id": row.affiliate_user_id
                    },
                    "product": {
                        "platform": row.platform,
                        "sku": row.product_sku,
                        "name": row.product_name
                    },
                    "performance": {
                        "sales": row.affiliate_sales or 0,
                        "revenue": float(row.affiliate_revenue or 0),
                        "quantity": row.affiliate_quantity or 0,
                        "period_start": row.period_start.isoformat() if row.period_start else None,
                        "period_end": row.period_end.isoformat() if row.period_end else None
                    }
                })

            return campaigns

    async def get_affiliate_campaign_performance(self, affiliate_user_id: str) -> List[dict]:
        """Get performance for all campaigns by this affiliate"""
        query = text("""
        SELECT
            c.id as campaign_id,
            c.name as campaign_name,
            c.campaign_type,
            c.status as campaign_status,

            pcm.platform,
            pcm.product_sku,
            pcm.product_name,
            pcm.creator_user_id,

            -- Get performance data
            app.sales,
            app.revenue,
            app.quantity,
            app.conversion_rate,
            app.period_start,
            app.period_end

        FROM campaigns c
        JOIN campaign_product_links cpl ON c.id = cpl.campaign_id
        JOIN product_creator_mappings pcm ON (cpl.platform = pcm.platform AND cpl.product_sku = pcm.product_sku)
        LEFT JOIN affiliate_product_performance app ON (
            c.user_id = app.affiliate_user_id
            AND pcm.creator_user_id = app.creator_user_id
            AND pcm.platform = app.platform
            AND pcm.product_sku = app.product_sku
        )
        WHERE c.user_id = :affiliate_user_id
        ORDER BY app.revenue DESC NULLS LAST, c.created_at DESC
        """)

        async with AsyncSessionManager.get_session() as session:
            result = await session.execute(query, {"affiliate_user_id": affiliate_user_id})
            rows = result.fetchall()

            campaigns = []
            for row in rows:
                campaigns.append({
                    "campaign": {
                        "id": row.campaign_id,
                        "name": row.campaign_name,
                        "type": row.campaign_type,
                        "status": row.campaign_status
                    },
                    "product": {
                        "platform": row.platform,
                        "sku": row.product_sku,
                        "name": row.product_name,
                        "creator_user_id": row.creator_user_id
                    },
                    "performance": {
                        "sales": row.sales or 0,
                        "revenue": float(row.revenue or 0),
                        "quantity": row.quantity or 0,
                        "conversion_rate": float(row.conversion_rate or 0),
                        "period_start": row.period_start.isoformat() if row.period_start else None,
                        "period_end": row.period_end.isoformat() if row.period_end else None
                    }
                })

            return campaigns

    async def auto_link_campaign_to_product_from_url(self, campaign_id: str, analyzed_url: str) -> dict:
        """Auto-link campaign to product based on analyzed URL data"""
        # This would extract product information from the intelligence analysis
        # and automatically create the campaign-product link

        # For now, return a placeholder - this would integrate with your intelligence system
        return {
            "status": "pending",
            "message": "Auto-linking from URL analysis not yet implemented",
            "campaign_id": campaign_id,
            "analyzed_url": analyzed_url
        }

# Global service instance
campaign_product_analytics_service = CampaignProductAnalyticsService()