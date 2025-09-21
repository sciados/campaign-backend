# campaignforge_value_attribution_service.py
"""
CampaignForge Value Attribution System

Tracks and reports how CampaignForge SAAS is benefiting Product Creators.
Focuses on platform effectiveness rather than raw sales data.
"""

import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from sqlalchemy import text
from src.core.database.session import AsyncSessionManager

class CampaignForgeValueAttributionService:
    """Service for tracking CampaignForge's value to Product Creators"""

    async def track_campaign_usage(
        self,
        campaign_id: str,
        affiliate_user_id: str,
        product_sku: str,
        platform: str,
        content_types_used: List[str],
        ai_features_used: List[str]
    ) -> dict:
        """Track when affiliates use CampaignForge for a product"""

        try:
            query = text("""
            INSERT INTO campaignforge_usage_tracking (
                campaign_id, affiliate_user_id, product_sku, platform,
                content_types_used, ai_features_used, usage_date, created_at
            ) VALUES (
                :campaign_id, :affiliate_user_id, :product_sku, :platform,
                :content_types_used, :ai_features_used, CURRENT_DATE, NOW()
            ) ON CONFLICT (campaign_id) DO UPDATE
            SET content_types_used = :content_types_used,
                ai_features_used = :ai_features_used,
                updated_at = NOW()
            """)

            async with AsyncSessionManager.get_session() as session:
                await session.execute(query, {
                    "campaign_id": campaign_id,
                    "affiliate_user_id": affiliate_user_id,
                    "product_sku": product_sku,
                    "platform": platform,
                    "content_types_used": json.dumps(content_types_used),
                    "ai_features_used": json.dumps(ai_features_used)
                })
                await session.commit()

            return {"status": "success", "message": "CampaignForge usage tracked"}

        except Exception as e:
            # Create table if it doesn't exist
            await self._create_usage_tracking_table()
            # Retry
            return await self.track_campaign_usage(
                campaign_id, affiliate_user_id, product_sku, platform,
                content_types_used, ai_features_used
            )

    async def track_performance_attribution(
        self,
        campaign_id: str,
        performance_metrics: dict,
        attribution_markers: dict
    ) -> dict:
        """Track performance that can be attributed to CampaignForge"""

        try:
            query = text("""
            INSERT INTO campaignforge_performance_attribution (
                campaign_id, performance_date,
                clicks, conversions, revenue_attributed,
                content_performance, ai_enhancement_impact,
                attribution_confidence, created_at
            ) VALUES (
                :campaign_id, CURRENT_DATE,
                :clicks, :conversions, :revenue_attributed,
                :content_performance, :ai_enhancement_impact,
                :attribution_confidence, NOW()
            ) ON CONFLICT (campaign_id, performance_date) DO UPDATE
            SET clicks = clicks + :clicks,
                conversions = conversions + :conversions,
                revenue_attributed = revenue_attributed + :revenue_attributed,
                content_performance = :content_performance,
                ai_enhancement_impact = :ai_enhancement_impact,
                attribution_confidence = :attribution_confidence,
                updated_at = NOW()
            """)

            async with AsyncSessionManager.get_session() as session:
                await session.execute(query, {
                    "campaign_id": campaign_id,
                    "clicks": performance_metrics.get("clicks", 0),
                    "conversions": performance_metrics.get("conversions", 0),
                    "revenue_attributed": performance_metrics.get("revenue_attributed", 0.0),
                    "content_performance": json.dumps(performance_metrics.get("content_performance", {})),
                    "ai_enhancement_impact": json.dumps(attribution_markers.get("ai_enhancement_impact", {})),
                    "attribution_confidence": attribution_markers.get("confidence_score", 0.7)
                })
                await session.commit()

            return {"status": "success", "message": "Performance attribution tracked"}

        except Exception as e:
            await self._create_performance_attribution_table()
            return await self.track_performance_attribution(campaign_id, performance_metrics, attribution_markers)

    async def generate_creator_value_report(self, creator_user_id: str, days: int = 30) -> dict:
        """Generate a value report showing how CampaignForge benefits the creator"""

        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            # Get usage metrics
            usage_query = text("""
            SELECT
                COUNT(DISTINCT cut.affiliate_user_id) as active_affiliates,
                COUNT(DISTINCT cut.campaign_id) as active_campaigns,
                COUNT(*) as total_usage_instances,
                ARRAY_AGG(DISTINCT content_type) as content_types_used,
                ARRAY_AGG(DISTINCT ai_feature) as ai_features_used,
                cut.product_sku,
                pcm.product_name
            FROM campaignforge_usage_tracking cut
            JOIN product_creator_mappings pcm ON (
                cut.platform = pcm.platform AND cut.product_sku = pcm.product_sku
            )
            CROSS JOIN LATERAL jsonb_array_elements_text(cut.content_types_used) content_type
            CROSS JOIN LATERAL jsonb_array_elements_text(cut.ai_features_used) ai_feature
            WHERE pcm.creator_user_id = :creator_user_id
            AND cut.usage_date >= :start_date
            AND cut.usage_date <= :end_date
            GROUP BY cut.product_sku, pcm.product_name
            """)

            # Get performance attribution
            performance_query = text("""
            SELECT
                SUM(cpa.clicks) as total_attributed_clicks,
                SUM(cpa.conversions) as total_attributed_conversions,
                SUM(cpa.revenue_attributed) as total_attributed_revenue,
                AVG(cpa.attribution_confidence) as avg_confidence,
                COUNT(DISTINCT cpa.campaign_id) as performing_campaigns,
                cut.product_sku
            FROM campaignforge_performance_attribution cpa
            JOIN campaignforge_usage_tracking cut ON cpa.campaign_id = cut.campaign_id
            JOIN product_creator_mappings pcm ON (
                cut.platform = pcm.platform AND cut.product_sku = pcm.product_sku
            )
            WHERE pcm.creator_user_id = :creator_user_id
            AND cpa.performance_date >= :start_date
            AND cpa.performance_date <= :end_date
            GROUP BY cut.product_sku
            """)

            async with AsyncSessionManager.get_session() as session:
                # Execute usage query
                usage_result = await session.execute(usage_query, {
                    "creator_user_id": creator_user_id,
                    "start_date": start_date,
                    "end_date": end_date
                })
                usage_data = usage_result.fetchall()

                # Execute performance query
                performance_result = await session.execute(performance_query, {
                    "creator_user_id": creator_user_id,
                    "start_date": start_date,
                    "end_date": end_date
                })
                performance_data = performance_result.fetchall()

            # Combine data into value report
            products = {}

            # Add usage data
            for row in usage_data:
                products[row.product_sku] = {
                    "product_name": row.product_name,
                    "product_sku": row.product_sku,
                    "campaignforge_adoption": {
                        "active_affiliates": row.active_affiliates,
                        "active_campaigns": row.active_campaigns,
                        "usage_instances": row.total_usage_instances,
                        "content_types_used": list(row.content_types_used) if row.content_types_used else [],
                        "ai_features_used": list(row.ai_features_used) if row.ai_features_used else []
                    },
                    "attributed_performance": {}
                }

            # Add performance data
            for row in performance_data:
                if row.product_sku in products:
                    products[row.product_sku]["attributed_performance"] = {
                        "clicks": int(row.total_attributed_clicks or 0),
                        "conversions": int(row.total_attributed_conversions or 0),
                        "revenue": float(row.total_attributed_revenue or 0),
                        "confidence_score": float(row.avg_confidence or 0),
                        "performing_campaigns": int(row.performing_campaigns or 0)
                    }

            # Calculate summary metrics
            total_affiliates = sum(p["campaignforge_adoption"]["active_affiliates"] for p in products.values())
            total_campaigns = sum(p["campaignforge_adoption"]["active_campaigns"] for p in products.values())
            total_attributed_revenue = sum(p["attributed_performance"].get("revenue", 0) for p in products.values())

            return {
                "creator_user_id": creator_user_id,
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "campaignforge_value_summary": {
                    "total_affiliates_using_platform": total_affiliates,
                    "total_campaigns_created": total_campaigns,
                    "total_attributed_revenue": total_attributed_revenue,
                    "products_benefiting": len(products)
                },
                "product_breakdown": list(products.values()),
                "value_indicators": {
                    "platform_adoption_rate": f"{total_affiliates}/{total_campaigns}" if total_campaigns > 0 else "0",
                    "revenue_attribution_confidence": sum(p["attributed_performance"].get("confidence_score", 0) for p in products.values()) / len(products) if products else 0,
                    "ai_feature_utilization": len(set().union(*[p["campaignforge_adoption"]["ai_features_used"] for p in products.values()])) if products else 0
                }
            }

        except Exception as e:
            return {
                "error": f"Failed to generate value report: {str(e)}",
                "creator_user_id": creator_user_id
            }

    async def get_platform_effectiveness_metrics(self, creator_user_id: str) -> dict:
        """Get metrics showing CampaignForge platform effectiveness"""

        try:
            query = text("""
            SELECT
                -- Campaign creation metrics
                COUNT(DISTINCT cut.campaign_id) as total_cf_campaigns,
                COUNT(DISTINCT cut.affiliate_user_id) as unique_affiliates,

                -- Content generation metrics
                COUNT(*) FILTER (WHERE 'email_sequence' = ANY(
                    SELECT jsonb_array_elements_text(content_types_used)
                )) as email_campaigns,
                COUNT(*) FILTER (WHERE 'social_media' = ANY(
                    SELECT jsonb_array_elements_text(content_types_used)
                )) as social_campaigns,

                -- AI feature adoption
                COUNT(*) FILTER (WHERE 'ai_analysis' = ANY(
                    SELECT jsonb_array_elements_text(ai_features_used)
                )) as ai_analysis_usage,
                COUNT(*) FILTER (WHERE 'content_generation' = ANY(
                    SELECT jsonb_array_elements_text(ai_features_used)
                )) as ai_content_usage,

                -- Time-based adoption
                DATE_TRUNC('month', usage_date) as usage_month,
                COUNT(*) as monthly_usage

            FROM campaignforge_usage_tracking cut
            JOIN product_creator_mappings pcm ON (
                cut.platform = pcm.platform AND cut.product_sku = pcm.product_sku
            )
            WHERE pcm.creator_user_id = :creator_user_id
            AND cut.usage_date >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY DATE_TRUNC('month', usage_date)
            ORDER BY usage_month DESC
            """)

            async with AsyncSessionManager.get_session() as session:
                result = await session.execute(query, {"creator_user_id": creator_user_id})
                rows = result.fetchall()

                if not rows:
                    return {"message": "No CampaignForge usage data found for this creator"}

                return {
                    "platform_effectiveness": {
                        "total_campaigns_created": sum(row.total_cf_campaigns for row in rows),
                        "unique_affiliates_engaged": max(row.unique_affiliates for row in rows),
                        "content_type_adoption": {
                            "email_campaigns": sum(row.email_campaigns for row in rows),
                            "social_campaigns": sum(row.social_campaigns for row in rows)
                        },
                        "ai_feature_adoption": {
                            "ai_analysis_usage": sum(row.ai_analysis_usage for row in rows),
                            "ai_content_generation": sum(row.ai_content_usage for row in rows)
                        },
                        "monthly_trends": [
                            {
                                "month": row.usage_month.isoformat(),
                                "campaigns": row.total_cf_campaigns,
                                "usage_instances": row.monthly_usage
                            } for row in rows
                        ]
                    }
                }

        except Exception as e:
            return {"error": f"Failed to get effectiveness metrics: {str(e)}"}

    async def _create_usage_tracking_table(self):
        """Create the CampaignForge usage tracking table"""
        query = text("""
        CREATE TABLE IF NOT EXISTS campaignforge_usage_tracking (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            campaign_id UUID NOT NULL,
            affiliate_user_id UUID NOT NULL,
            product_sku VARCHAR(255) NOT NULL,
            platform VARCHAR(50) NOT NULL,
            content_types_used JSONB DEFAULT '[]',
            ai_features_used JSONB DEFAULT '[]',
            usage_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),

            UNIQUE (campaign_id),

            FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_cf_usage_product ON campaignforge_usage_tracking(platform, product_sku);
        CREATE INDEX IF NOT EXISTS idx_cf_usage_affiliate ON campaignforge_usage_tracking(affiliate_user_id);
        CREATE INDEX IF NOT EXISTS idx_cf_usage_date ON campaignforge_usage_tracking(usage_date);

        COMMENT ON TABLE campaignforge_usage_tracking IS 'Tracks CampaignForge platform usage for value attribution';
        """)

        async with AsyncSessionManager.get_session() as session:
            await session.execute(query)
            await session.commit()

    async def _create_performance_attribution_table(self):
        """Create the performance attribution table"""
        query = text("""
        CREATE TABLE IF NOT EXISTS campaignforge_performance_attribution (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            campaign_id UUID NOT NULL,
            performance_date DATE NOT NULL,
            clicks INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0,
            revenue_attributed DECIMAL(12,2) DEFAULT 0.00,
            content_performance JSONB DEFAULT '{}',
            ai_enhancement_impact JSONB DEFAULT '{}',
            attribution_confidence DECIMAL(3,2) DEFAULT 0.70,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),

            UNIQUE (campaign_id, performance_date),

            FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_cf_performance_date ON campaignforge_performance_attribution(performance_date);
        CREATE INDEX IF NOT EXISTS idx_cf_performance_campaign ON campaignforge_performance_attribution(campaign_id);

        COMMENT ON TABLE campaignforge_performance_attribution IS 'Tracks performance attributed to CampaignForge platform';
        """)

        async with AsyncSessionManager.get_session() as session:
            await session.execute(query)
            await session.commit()

# Global service instance
campaignforge_value_attribution_service = CampaignForgeValueAttributionService()