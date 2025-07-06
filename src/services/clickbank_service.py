# src/services/clickbank_service.py - NEW FILE
"""
Enhanced ClickBank service for marketplace functionality
"""
import asyncio
from uuid import uuid4
import httpx
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from datetime import datetime, timedelta

from ..models.clickbank import ClickBankProduct, ClickBankCategory, ProductAnalysisStatus
from ..models.intelligence import CampaignIntelligence
from ..core.database import get_db
from ..intelligence.handlers.analysis_handler import analyze_sales_page

class ClickBankService:
    def __init__(self):
        self.api_key = os.getenv("CLICKBANK_API_KEY")
        self.base_url = "https://api.clickbank.com/rest/1.3/products/list"
    
    async def fetch_and_store_products(
        self, 
        category: ClickBankCategory, 
        limit: int = 10,
        force_refresh: bool = False
    ) -> List[ClickBankProduct]:
        """Fetch products from ClickBank API and store in database"""
        
        async with AsyncSession(engine) as session:
            # Check if we have recent data (unless force refresh)
            if not force_refresh:
                recent_cutoff = datetime.utcnow() - timedelta(hours=6)
                existing = await session.execute(
                    select(ClickBankProduct)
                    .where(
                        and_(
                            ClickBankProduct.category == category,
                            ClickBankProduct.last_updated > recent_cutoff
                        )
                    )
                    .limit(limit)
                )
                if existing.scalars().all():
                    return existing.scalars().all()
            
            # Fetch from ClickBank API
            products_data = await self._fetch_from_api(category, limit)
            
            # Store/update in database
            stored_products = []
            for product_data in products_data:
                product = await self._store_product(session, product_data, category)
                stored_products.append(product)
            
            await session.commit()
            return stored_products
    
    async def _fetch_from_api(self, category: ClickBankCategory, limit: int) -> List[Dict]:
        """Fetch products from ClickBank API"""
        config = {
            "top": {"category": None, "sortField": "gravity"},
            "new": {"category": None, "sortField": "dateCreated"},
            "health": {"category": "Health & Fitness", "sortField": "gravity"},
            "ebusiness": {"category": "E-business & E-marketing", "sortField": "gravity"},
            "selfhelp": {"category": "Self-Help", "sortField": "gravity"},
            "green": {"category": "Green Products", "sortField": "gravity"},
            "business": {"category": "Business / Investing", "sortField": "gravity"},
        }
        
        category_config = config.get(category.value, config["top"])
        headers = {"Authorization": self.api_key}
        params = {"results": limit, "sortField": category_config["sortField"]}
        
        if category_config["category"]:
            params["category"] = category_config["category"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("products", [])
    
    async def _store_product(
        self, 
        session: AsyncSession, 
        product_data: Dict, 
        category: ClickBankCategory
    ) -> ClickBankProduct:
        """Store or update a product in the database"""
        
        # Check if product exists
        existing = await session.execute(
            select(ClickBankProduct).where(
                ClickBankProduct.salespage_url == product_data.get("pitchPageUrl")
            )
        )
        product = existing.scalar_one_or_none()
        
        if product:
            # Update existing product
            product.title = product_data.get("title", "")
            product.description = product_data.get("description", "")
            product.gravity = product_data.get("gravity", 0)
            product.commission_rate = product_data.get("commissionRate", 0)
            product.last_updated = datetime.utcnow()
        else:
            # Create new product
            product = ClickBankProduct(
                vendor=product_data.get("vendor", ""),
                title=product_data.get("title", ""),
                description=product_data.get("description", ""),
                category=category,
                gravity=product_data.get("gravity", 0),
                commission_rate=product_data.get("commissionRate", 0),
                salespage_url=product_data.get("pitchPageUrl", ""),
                product_id=product_data.get("sku"),
                vendor_id=product_data.get("vendor"),
                date_created=datetime.utcnow()
            )
            session.add(product)
        
        return product
    
    async def analyze_product(self, product_id: str, user_id: str, company_id: str) -> Dict[str, Any]:
        """Analyze a ClickBank product and extract intelligence"""
        
        async with AsyncSession(engine) as session:
            # Get product
            product = await session.get(ClickBankProduct, product_id)
            if not product:
                raise ValueError("Product not found")
            
            # Mark as processing
            product.analysis_status = ProductAnalysisStatus.PROCESSING
            await session.commit()
            
            try:
                # Create temporary campaign for analysis
                temp_campaign_id = str(uuid4())
                
                # Analyze the sales page
                analysis_result = await analyze_sales_page(
                    url=product.salespage_url,
                    campaign_id=temp_campaign_id,
                    user_id=user_id,
                    company_id=company_id
                )
                
                # Extract key insights
                insights = self._extract_key_insights(analysis_result)
                
                # Update product with analysis
                product.analysis_status = ProductAnalysisStatus.COMPLETED
                product.analysis_data = analysis_result
                product.key_insights = insights.get("key_insights", [])
                product.recommended_angles = insights.get("recommended_angles", [])
                product.target_audience_data = insights.get("target_audience", {})
                product.analysis_score = insights.get("confidence_score", 0.0)
                product.last_analyzed = datetime.utcnow()
                
                await session.commit()
                
                return {
                    "product_id": product_id,
                    "analysis_status": "completed",
                    "confidence_score": product.analysis_score,
                    "key_insights": product.key_insights,
                    "recommended_angles": product.recommended_angles,
                    "target_audience": product.target_audience_data
                }
                
            except Exception as e:
                # Mark as failed
                product.analysis_status = ProductAnalysisStatus.FAILED
                product.metadata = {"error": str(e), "failed_at": datetime.utcnow().isoformat()}
                await session.commit()
                raise
    
    def _extract_key_insights(self, analysis_result: Dict) -> Dict[str, Any]:
        """Extract key insights from analysis result"""
        # Extract from offer intelligence
        offer_intel = analysis_result.get("offer_intelligence", {})
        psych_intel = analysis_result.get("psychology_intelligence", {})
        content_intel = analysis_result.get("content_intelligence", {})
        
        insights = []
        angles = []
        
        # Extract key selling points
        if offer_intel.get("key_selling_points"):
            insights.extend(offer_intel["key_selling_points"][:3])
        
        # Extract psychological triggers
        if psych_intel.get("psychological_triggers"):
            triggers = psych_intel["psychological_triggers"]
            insights.append(f"Uses {len(triggers)} psychological triggers")
        
        # Extract recommended angles
        if psych_intel.get("emotional_journey"):
            journey = psych_intel["emotional_journey"]
            angles.extend([f"Target {emotion} emotion" for emotion in journey.get("emotions", [])[:3]])
        
        # Extract target audience
        target_audience = {}
        if offer_intel.get("target_audience"):
            target_audience = offer_intel["target_audience"]
        
        return {
            "key_insights": insights[:5],  # Top 5 insights
            "recommended_angles": angles[:5],  # Top 5 angles
            "target_audience": target_audience,
            "confidence_score": analysis_result.get("confidence_score", 0.0)
        }
    
    async def get_products_by_category(
        self, 
        category: ClickBankCategory,
        analyzed_only: bool = False,
        limit: int = 20
    ) -> List[ClickBankProduct]:
        """Get products by category"""
        
        async with AsyncSession(engine) as session:
            query = select(ClickBankProduct).where(ClickBankProduct.category == category)
            
            if analyzed_only:
                query = query.where(ClickBankProduct.analysis_status == ProductAnalysisStatus.COMPLETED)
            
            query = query.order_by(ClickBankProduct.gravity.desc()).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()

# Initialize service
clickbank_service = ClickBankService()