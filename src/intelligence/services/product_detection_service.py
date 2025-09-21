# product_detection_service.py
"""
Service for detecting and linking products during campaign creation.
Integrates with URL analysis and content library selection to establish Campaign → Product relationships.
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from src.intelligence.services.campaign_product_analytics_service import campaign_product_analytics_service

class ProductDetectionService:
    """Service for detecting products from URLs and content library selections"""

    async def detect_and_link_product_from_url(
        self,
        source_url: str,
        campaign_id: str,
        user_id: str,
        intelligence_result: dict = None
    ) -> dict:
        """
        Smart product detection: Check library first, analyze URL only if needed
        """
        try:
            # Step 1: Check if product already exists in library by URL
            existing_product = await self._find_product_in_library_by_url(source_url)

            if existing_product:
                # Product exists - direct link to creator (no analysis needed)
                link_result = await campaign_product_analytics_service.link_campaign_to_product(
                    campaign_id=campaign_id,
                    platform=existing_product["platform"],
                    product_sku=existing_product["sku"],
                    product_name=existing_product["name"],
                    creator_user_id=existing_product["creator_user_id"]
                )

                return {
                    "status": "product_linked_from_library",
                    "message": f"Campaign linked to existing product: {existing_product['name']}",
                    "product": existing_product,
                    "analysis_performed": False,
                    "link_result": link_result
                }

            # Step 2: Product doesn't exist - perform URL analysis
            if not intelligence_result:
                return {
                    "status": "analysis_required",
                    "message": "Product not in library - URL analysis required",
                    "analysis_performed": False
                }

            # Step 3: Extract product from analysis
            product_info = self._extract_product_from_intelligence(intelligence_result)
            if not product_info:
                return {
                    "status": "no_product_detected",
                    "message": "No product information found in URL analysis"
                }

            # Step 4: Identify platform and creator
            platform_info = self._identify_platform_from_url(source_url)
            creator_info = await self._identify_product_creator(product_info, platform_info)

            if not creator_info:
                # Add to library without creator link for manual assignment later
                await self._add_product_to_library(product_info, platform_info, source_url)

                return {
                    "status": "product_added_pending_creator",
                    "message": f"Product '{product_info['name']}' added to library - creator assignment needed",
                    "product": product_info,
                    "platform": platform_info,
                    "analysis_performed": True
                }

            # Step 5: Add to library and link campaign
            await self._add_product_to_library(product_info, platform_info, source_url, creator_info["creator_user_id"])

            link_result = await campaign_product_analytics_service.link_campaign_to_product(
                campaign_id=campaign_id,
                platform=platform_info["platform"],
                product_sku=product_info["sku"],
                product_name=product_info["name"],
                creator_user_id=creator_info["creator_user_id"]
            )

            return {
                "status": "product_analyzed_and_linked",
                "message": f"New product analyzed, added to library, and linked: {product_info['name']}",
                "product": product_info,
                "platform": platform_info,
                "creator": creator_info,
                "analysis_performed": True,
                "link_result": link_result
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error in smart product detection: {str(e)}"
            }

    def _extract_product_from_intelligence(self, intelligence_result: dict) -> Optional[dict]:
        """Extract product information from intelligence analysis result"""
        try:
            # Look for product information in various places in the intelligence result
            analysis_result = intelligence_result.get("analysis_result", {})

            # Method 1: Direct product information
            if "product_name" in analysis_result:
                return {
                    "name": analysis_result["product_name"],
                    "sku": analysis_result.get("product_sku", self._generate_sku_from_name(analysis_result["product_name"])),
                    "description": analysis_result.get("product_description", ""),
                    "price": analysis_result.get("price", 0.0)
                }

            # Method 2: Extract from content analysis
            content_analysis = analysis_result.get("content_analysis", {})
            if "product_details" in content_analysis:
                product_details = content_analysis["product_details"]
                return {
                    "name": product_details.get("name", ""),
                    "sku": product_details.get("sku", self._generate_sku_from_name(product_details.get("name", ""))),
                    "description": product_details.get("description", ""),
                    "price": product_details.get("price", 0.0)
                }

            # Method 3: Extract from page title/content
            page_title = analysis_result.get("page_title", "")
            if page_title:
                # Use page title as product name and generate SKU
                return {
                    "name": page_title,
                    "sku": self._generate_sku_from_name(page_title),
                    "description": analysis_result.get("meta_description", ""),
                    "price": 0.0
                }

            return None

        except Exception as e:
            print(f"Error extracting product from intelligence: {e}")
            return None

    def _identify_platform_from_url(self, url: str) -> dict:
        """Identify the platform from the URL"""
        url_lower = url.lower()

        # ClickBank patterns
        if any(pattern in url_lower for pattern in [
            "clickbank.com", "hop.clickbank.net", "cbpbtrack.com",
            "cbproads.com", "cb-analytics.com"
        ]):
            return {
                "platform": "clickbank",
                "detected_from": "url_pattern"
            }

        # JVZoo patterns
        if any(pattern in url_lower for pattern in [
            "jvzoo.com", "warriorplus.com", "jvz1.com", "jvzoogateways.com"
        ]):
            return {
                "platform": "jvzoo",
                "detected_from": "url_pattern"
            }

        # WarriorPlus patterns
        if any(pattern in url_lower for pattern in [
            "warriorplus.com", "w-plus.com", "wplusmember.com"
        ]):
            return {
                "platform": "warriorplus",
                "detected_from": "url_pattern"
            }

        # Default to ClickBank for unknown patterns
        return {
            "platform": "clickbank",
            "detected_from": "default_assumption"
        }

    async def _identify_product_creator(self, product_info: dict, platform_info: dict) -> Optional[dict]:
        """Try to identify the product creator from existing mappings"""
        try:
            # Check if this product already exists in our mappings
            from src.intelligence.services.product_creator_mapping_service import product_creator_mapping_service

            creator_user_id = await product_creator_mapping_service.get_creator_for_product(
                platform=platform_info["platform"],
                product_sku=product_info["sku"]
            )

            if creator_user_id:
                return {
                    "creator_user_id": creator_user_id,
                    "source": "existing_mapping"
                }

            # If no existing mapping, this would be where you'd integrate with
            # your user system to identify creators by various methods:
            # - Domain ownership verification
            # - Manual creator registration
            # - AI-powered creator identification
            # For now, return None to indicate creator needs to be manually set

            return None

        except Exception as e:
            print(f"Error identifying product creator: {e}")
            return None

    def _generate_sku_from_name(self, product_name: str) -> str:
        """Generate a SKU from product name"""
        if not product_name:
            return "UNKNOWN_PRODUCT"

        # Clean the name and create a SKU
        cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', '', product_name)
        words = cleaned_name.split()[:3]  # Take first 3 words
        sku = "_".join(word.upper() for word in words if word)

        return sku if sku else "UNNAMED_PRODUCT"

    async def _find_product_in_library_by_url(self, url: str) -> Optional[dict]:
        """Check if product already exists in library by URL"""
        try:
            # This would query your content library system to find products by URL
            # For now, simulate the lookup - in production this would be a real database query

            from sqlalchemy import text
            from src.core.database.session import AsyncSessionManager

            # Look for products with matching URLs in the library
            query = text("""
            SELECT
                pcm.platform,
                pcm.product_sku as sku,
                pcm.product_name as name,
                pcm.creator_user_id,
                pl.source_url,
                pl.description
            FROM product_creator_mappings pcm
            JOIN product_library pl ON (pcm.platform = pl.platform AND pcm.product_sku = pl.product_sku)
            WHERE pl.source_url = :url
            LIMIT 1
            """)

            try:
                async with AsyncSessionManager.get_session() as session:
                    result = await session.execute(query, {"url": url})
                    row = result.fetchone()

                    if row:
                        return {
                            "platform": row.platform,
                            "sku": row.sku,
                            "name": row.name,
                            "creator_user_id": row.creator_user_id,
                            "source_url": row.source_url,
                            "description": row.description,
                            "source": "library"
                        }
            except Exception as db_error:
                print(f"Database error checking product library: {db_error}")
                # If table doesn't exist yet, create it
                await self._create_product_library_table()

            return None

        except Exception as e:
            print(f"Error finding product in library: {e}")
            return None

    async def _add_product_to_library(
        self,
        product_info: dict,
        platform_info: dict,
        source_url: str,
        creator_user_id: str = None
    ):
        """Add product to the content library"""
        try:
            from sqlalchemy import text
            from src.core.database.session import AsyncSessionManager

            # Add to product library table
            query = text("""
            INSERT INTO product_library (
                platform, product_sku, product_name, source_url, description,
                price, added_at, creator_user_id
            ) VALUES (
                :platform, :product_sku, :product_name, :source_url, :description,
                :price, NOW(), :creator_user_id
            ) ON CONFLICT (platform, product_sku) DO UPDATE
            SET product_name = :product_name,
                source_url = :source_url,
                description = :description,
                price = :price,
                creator_user_id = :creator_user_id,
                updated_at = NOW()
            """)

            async with AsyncSessionManager.get_session() as session:
                await session.execute(query, {
                    "platform": platform_info["platform"],
                    "product_sku": product_info["sku"],
                    "product_name": product_info["name"],
                    "source_url": source_url,
                    "description": product_info.get("description", ""),
                    "price": product_info.get("price", 0.0),
                    "creator_user_id": creator_user_id
                })
                await session.commit()

        except Exception as e:
            print(f"Error adding product to library: {e}")
            # Create table if it doesn't exist
            await self._create_product_library_table()
            # Retry the insert
            await self._add_product_to_library(product_info, platform_info, source_url, creator_user_id)

    async def _create_product_library_table(self):
        """Create the product library table if it doesn't exist"""
        query = text("""
        CREATE TABLE IF NOT EXISTS product_library (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            platform VARCHAR(50) NOT NULL,
            product_sku VARCHAR(255) NOT NULL,
            product_name VARCHAR(500) NOT NULL,
            source_url TEXT NOT NULL,
            description TEXT,
            price DECIMAL(10,2) DEFAULT 0.00,
            creator_user_id UUID,
            added_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),

            -- Ensure unique products
            UNIQUE (platform, product_sku),

            -- Index for URL lookups
            UNIQUE (source_url)
        );

        CREATE INDEX IF NOT EXISTS idx_product_library_url ON product_library(source_url);
        CREATE INDEX IF NOT EXISTS idx_product_library_creator ON product_library(creator_user_id);
        CREATE INDEX IF NOT EXISTS idx_product_library_platform ON product_library(platform, product_sku);

        COMMENT ON TABLE product_library IS 'Content library of analyzed products with creator relationships';
        """)

        from src.core.database.session import AsyncSessionManager
        async with AsyncSessionManager.get_session() as session:
            await session.execute(query)
            await session.commit()

    async def link_campaign_to_content_library_product(
        self,
        campaign_id: str,
        content_library_product_id: str,
        user_id: str
    ) -> dict:
        """
        Link campaign to a product selected from content library
        """
        try:
            # Get product information from content library
            product_info = await self._get_content_library_product(content_library_product_id)

            if not product_info:
                return {
                    "status": "product_not_found",
                    "message": "Product not found in content library"
                }

            # Link campaign to this product
            link_result = await campaign_product_analytics_service.link_campaign_to_product(
                campaign_id=campaign_id,
                platform=product_info["platform"],
                product_sku=product_info["sku"],
                product_name=product_info["name"],
                creator_user_id=product_info["creator_user_id"]
            )

            return {
                "status": "product_linked",
                "message": f"Campaign linked to {product_info['name']} from content library",
                "product": product_info,
                "link_result": link_result
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error linking to content library product: {str(e)}"
            }

    async def _get_content_library_product(self, product_id: str) -> Optional[dict]:
        """Get product information from content library"""
        # This would integrate with your content library system
        # For now, return a placeholder structure
        # In production, this would query your content library database

        return {
            "id": product_id,
            "name": "Content Library Product",
            "sku": f"CL_{product_id}",
            "platform": "clickbank",
            "creator_user_id": "placeholder_creator_id",
            "description": "Product selected from content library",
            "source": "content_library"
        }

    async def get_campaign_product_info(self, campaign_id: str) -> Optional[dict]:
        """Get the product information linked to a campaign"""
        try:
            result = await campaign_product_analytics_service.get_campaign_analytics_with_product_context(campaign_id)

            if "error" in result:
                return None

            return {
                "campaign": result["campaign"],
                "product": result["product"],
                "analytics": result["analytics"]
            }

        except Exception as e:
            print(f"Error getting campaign product info: {e}")
            return None

# Global service instance
product_detection_service = ProductDetectionService()