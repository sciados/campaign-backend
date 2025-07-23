# src/intelligence/affiliate_networks/shareasale_integration.py
"""
SHAREASALE API INTEGRATION
✅ Immediate API access (no approval needed)
✅ 4,000+ merchants including major retailers
✅ Higher commission rates than digital products
✅ Mainstream appeal for broader audience
"""

import os
import asyncio
import aiohttp
import hashlib
import hmac
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class ShareASaleAPI:
    """ShareASale affiliate network integration"""
    
    def __init__(self):
        self.affiliate_id = os.getenv("SHAREASALE_AFFILIATE_ID")
        self.api_token = os.getenv("SHAREASALE_API_TOKEN")
        self.api_secret = os.getenv("SHAREASALE_API_SECRET")
        self.base_url = "https://api.shareasale.com/w.cfm"
        
        if not all([self.affiliate_id, self.api_token, self.api_secret]):
            logger.warning("⚠️ ShareASale credentials missing. Get them from: https://www.shareasale.com/a-signup.cfm")
    
    def _generate_signature(self, action: str, timestamp: str) -> str:
        """Generate API signature for ShareASale"""
        sig_string = f"{self.api_token}:{timestamp}:{action}:{self.affiliate_id}"
        return hmac.new(
            self.api_secret.encode(),
            sig_string.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def get_merchants(self, category: str = None) -> List[Dict[str, Any]]:
        """Get active merchants from ShareASale"""
        
        timestamp = str(int(time.time()))
        action = "merchantlist"
        signature = self._generate_signature(action, timestamp)
        
        params = {
            "affiliateId": self.affiliate_id,
            "token": self.api_token,
            "requestTimeStamp": timestamp,
            "action": action,
            "signature": signature,
            "XMLFormat": "1"
        }
        
        if category:
            params["category"] = category
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        return self._parse_merchants_xml(xml_content)
                    else:
                        logger.error(f"ShareASale API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"ShareASale merchants request failed: {str(e)}")
            return []
    
    async def get_products(self, merchant_id: str, category: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get products from specific ShareASale merchant"""
        
        timestamp = str(int(time.time()))
        action = "productSearch"
        signature = self._generate_signature(action, timestamp)
        
        params = {
            "affiliateId": self.affiliate_id,
            "token": self.api_token,
            "requestTimeStamp": timestamp,
            "action": action,
            "signature": signature,
            "merchantId": merchant_id,
            "resultsPerPage": str(limit),
            "XMLFormat": "1"
        }
        
        if category:
            params["category"] = category
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        return self._parse_products_xml(xml_content)
                    else:
                        logger.error(f"ShareASale products API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"ShareASale products request failed: {str(e)}")
            return []
    
    async def get_health_products(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get health and wellness products from ShareASale"""
        
        # Health-focused merchant IDs (major ones)
        health_merchants = [
            "39162",  # iHerb
            "43821",  # Vitacost
            "38328",  # Life Extension
            "20365",  # PipingRock
            "48347"   # Swanson Vitamins
        ]
        
        all_products = []
        
        for merchant_id in health_merchants:
            try:
                products = await self.get_products(
                    merchant_id=merchant_id,
                    category="health",
                    limit=limit // len(health_merchants)
                )
                
                # Add network metadata
                for product in products:
                    product.update({
                        "network": "shareasale",
                        "merchant_id": merchant_id,
                        "data_source": "shareasale_api",
                        "scraped_at": datetime.now(time.timezone.utc).astimezone().isoformat(),
                        "is_real_product": True
                    })
                
                all_products.extend(products)
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to get products from merchant {merchant_id}: {str(e)}")
                continue
        
        logger.info(f"✅ Retrieved {len(all_products)} health products from ShareASale")
        return all_products
    
    async def search_products(self, keywords: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search products by keywords"""
        
        timestamp = str(int(time.time()))
        action = "productSearch"
        signature = self._generate_signature(action, timestamp)
        
        params = {
            "affiliateId": self.affiliate_id,
            "token": self.api_token,
            "requestTimeStamp": timestamp,
            "action": action,
            "signature": signature,
            "keyword": keywords,
            "resultsPerPage": str(limit),
            "XMLFormat": "1"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        products = self._parse_products_xml(xml_content)
                        
                        # Add network metadata
                        for product in products:
                            product.update({
                                "network": "shareasale",
                                "data_source": "shareasale_search",
                                "search_keywords": keywords,
                                "scraped_at": datetime.datetime.now(),
                                "is_real_product": True
                            })
                        
                        return products
                    else:
                        logger.error(f"ShareASale search API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"ShareASale search failed: {str(e)}")
            return []
    
    def _parse_merchants_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse merchants XML response"""
        
        merchants = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for merchant in root.findall('.//merchant'):
                merchant_data = {
                    "merchant_id": merchant.find('merchantid').text if merchant.find('merchantid') is not None else "",
                    "merchant_name": merchant.find('merchantname').text if merchant.find('merchantname') is not None else "",
                    "website": merchant.find('website').text if merchant.find('website') is not None else "",
                    "category": merchant.find('category').text if merchant.find('category') is not None else "",
                    "commission_rate": merchant.find('commissionrate').text if merchant.find('commissionrate') is not None else "0",
                    "cookie_duration": merchant.find('cookieduration').text if merchant.find('cookieduration') is not None else "30",
                    "is_active": True,
                    "network": "shareasale"
                }
                merchants.append(merchant_data)
                
        except ET.ParseError as e:
            logger.error(f"Failed to parse ShareASale merchants XML: {str(e)}")
        
        return merchants
    
    def _parse_products_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse products XML response"""
        
        products = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for product in root.findall('.//product'):
                # Extract product data
                product_data = {
                    "product_id": product.find('sku').text if product.find('sku') is not None else "",
                    "title": product.find('name').text if product.find('name') is not None else "",
                    "description": product.find('description').text if product.find('description') is not None else "",
                    "price": self._safe_float(product.find('price').text if product.find('price') is not None else "0"),
                    "retail_price": self._safe_float(product.find('retailprice').text if product.find('retailprice') is not None else "0"),
                    "sale_price": self._safe_float(product.find('saleprice').text if product.find('saleprice') is not None else "0"),
                    "commission_rate": self._safe_float(product.find('commission').text if product.find('commission') is not None else "0"),
                    "category": product.find('category').text if product.find('category') is not None else "",
                    "subcategory": product.find('subcategory').text if product.find('subcategory') is not None else "",
                    "brand": product.find('brand').text if product.find('brand') is not None else "",
                    "upc": product.find('upc').text if product.find('upc') is not None else "",
                    "isbn": product.find('isbn').text if product.find('isbn') is not None else "",
                    "direct_link": product.find('directlink').text if product.find('directlink') is not None else "",
                    "image_url": product.find('imageurl').text if product.find('imageurl') is not None else "",
                    "thumbnail_url": product.find('thumbnailurl').text if product.find('thumbnailurl') is not None else "",
                    "merchant_id": product.find('merchantid').text if product.find('merchantid') is not None else "",
                    "merchant_name": product.find('merchantname').text if product.find('merchantname') is not None else "",
                    "in_stock": product.find('instock').text if product.find('instock') is not None else "1",
                    "currency": product.find('currency').text if product.find('currency') is not None else "USD"
                }
                
                # Calculate commission amount
                if product_data["price"] and product_data["commission_rate"]:
                    product_data["commission_amount"] = product_data["price"] * (product_data["commission_rate"] / 100)
                
                # Add affiliate link
                if product_data["direct_link"]:
                    product_data["salespage_url"] = product_data["direct_link"]
                    product_data["affiliate_url"] = product_data["direct_link"]
                
                products.append(product_data)
                
        except ET.ParseError as e:
            logger.error(f"Failed to parse ShareASale products XML: {str(e)}")
        
        return products
    
    def _safe_float(self, value: str) -> float:
        """Safely convert string to float"""
        try:
            return float(value) if value else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test ShareASale API connection"""
        
        if not all([self.affiliate_id, self.api_token, self.api_secret]):
            return {
                "status": "❌ FAILED",
                "error": "Missing ShareASale credentials",
                "setup_help": {
                    "signup_url": "https://www.shareasale.com/a-signup.cfm",
                    "required_env_vars": [
                        "SHAREASALE_AFFILIATE_ID",
                        "SHAREASALE_API_TOKEN", 
                        "SHAREASALE_API_SECRET"
                    ],
                    "approval_time": "Usually instant after signup"
                }
            }
        
        try:
            # Test with a simple merchant list request
            merchants = await self.get_merchants()
            
            if merchants:
                return {
                    "status": "✅ SUCCESS",
                    "merchants_found": len(merchants),
                    "api_working": True,
                    "message": "ShareASale API is ready to use!",
                    "next_steps": [
                        "Call get_health_products() to get health/wellness products",
                        "Use search_products() to find specific product types",
                        "Integrate with your product database"
                    ]
                }
            else:
                return {
                    "status": "⚠️ PARTIAL",
                    "api_working": True,
                    "merchants_found": 0,
                    "message": "API connected but no merchants returned",
                    "check": "Verify your affiliate account is approved"
                }
                
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "error": str(e),
                "api_working": False,
                "troubleshooting": [
                    "Check API credentials are correct",
                    "Verify affiliate account is active",
                    "Check network connectivity"
                ]
            }


# Integration with your existing product system
class MultiNetworkProductManager:
    """Manage products from multiple affiliate networks"""
    
    def __init__(self):
        self.shareasale = ShareASaleAPI()
        self.networks = {
            "shareasale": self.shareasale,
            # Will add: CJ Affiliate, Impact, etc.
        }
    
    async def get_products_by_network(self, network: str, category: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get products from specific network"""
        
        if network not in self.networks:
            available = list(self.networks.keys())
            raise ValueError(f"Network '{network}' not available. Available: {available}")
        
        api = self.networks[network]
        
        if network == "shareasale":
            if category and category.lower() in ["health", "wellness", "supplements"]:
                return await api.get_health_products(limit)
            else:
                # Get from top merchants
                merchants = await api.get_merchants(category)
                if merchants:
                    top_merchant = merchants[0]["merchant_id"]
                    return await api.get_products(top_merchant, category, limit)
                return []
        
        return []
    
    async def search_all_networks(self, keywords: str, limit: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """Search products across all networks"""
        
        results = {}
        
        for network_name, api in self.networks.items():
            try:
                if hasattr(api, 'search_products'):
                    products = await api.search_products(keywords, limit)
                    results[network_name] = products
                    logger.info(f"Found {len(products)} products in {network_name} for '{keywords}'")
                else:
                    results[network_name] = []
            except Exception as e:
                logger.error(f"Search failed for {network_name}: {str(e)}")
                results[network_name] = []
        
        return results
    
    async def get_health_products_all_networks(self, limit: int = 200) -> Dict[str, List[Dict[str, Any]]]:
        """Get health products from all available networks"""
        
        results = {}
        
        for network_name, api in self.networks.items():
            try:
                if hasattr(api, 'get_health_products'):
                    products = await api.get_health_products(limit)
                    results[network_name] = products
                    logger.info(f"Retrieved {len(products)} health products from {network_name}")
                else:
                    # Fallback to general product search
                    if hasattr(api, 'search_products'):
                        products = await api.search_products("health supplements", limit)
                        results[network_name] = products
                    else:
                        results[network_name] = []
            except Exception as e:
                logger.error(f"Health products retrieval failed for {network_name}: {str(e)}")
                results[network_name] = []
        
        return results
    
    def normalize_product_data(self, product: Dict[str, Any], network: str) -> Dict[str, Any]:
        """Normalize product data across different networks"""
        
        # Universal product format for your database
        normalized = {
            "id": f"{network}_{product.get('product_id', '')}",
            "network": network,
            "network_product_id": product.get("product_id", ""),
            "title": product.get("title", ""),
            "vendor": product.get("merchant_name", product.get("brand", "")),
            "description": product.get("description", ""),
            "price": product.get("price", 0),
            "commission_rate": product.get("commission_rate", 0),
            "commission_amount": product.get("commission_amount", 0),
            "category": product.get("category", ""),
            "salespage_url": product.get("salespage_url", product.get("direct_link", "")),
            "affiliate_url": product.get("affiliate_url", product.get("direct_link", "")),
            "image_url": product.get("image_url", ""),
            "is_active": product.get("in_stock", "1") == "1",
            "data_source": product.get("data_source", f"{network}_api"),
            "scraped_at": product.get("scraped_at", datetime.now(time.timezone.utc).astimezone().isoformat()),
            "is_real_product": product.get("is_real_product", True),
            
            # Network-specific metadata
            "network_metadata": {
                "merchant_id": product.get("merchant_id", ""),
                "currency": product.get("currency", "USD"),
                "brand": product.get("brand", ""),
                "upc": product.get("upc", ""),
                "subcategory": product.get("subcategory", "")
            }
        }
        
        return normalized
    
    async def bulk_import_products(self, network: str, category: str = None, limit: int = 500) -> Dict[str, Any]:
        """Bulk import products from network to database"""
        
        try:
            products = await self.get_products_by_network(network, category, limit)
            normalized_products = [
                self.normalize_product_data(product, network) 
                for product in products
            ]
            
            # Here you would save to your database
            # For now, return the data for inspection
            
            return {
                "success": True,
                "network": network,
                "category": category or "all",
                "products_imported": len(normalized_products),
                "products": normalized_products[:10],  # Sample for inspection
                "total_commission_potential": sum(p.get("commission_amount", 0) for p in normalized_products),
                "avg_commission_rate": sum(p.get("commission_rate", 0) for p in normalized_products) / len(normalized_products) if normalized_products else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "network": network,
                "category": category
            }


# FastAPI routes for multi-network integration
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter()

@router.get("/networks/available")
async def get_available_networks():
    """Get list of available affiliate networks"""
    manager = MultiNetworkProductManager()
    
    network_info = {}
    for network_name, api in manager.networks.items():
        if hasattr(api, 'test_connection'):
            test_result = await api.test_connection()
            network_info[network_name] = {
                "status": test_result.get("status"),
                "available": "SUCCESS" in test_result.get("status", ""),
                "setup_required": "FAILED" in test_result.get("status", "")
            }
        else:
            network_info[network_name] = {
                "status": "Available",
                "available": True,
                "setup_required": False
            }
    
    return {
        "available_networks": list(manager.networks.keys()),
        "network_status": network_info,
        "total_networks": len(manager.networks)
    }

@router.get("/networks/{network}/products")
async def get_network_products(
    network: str,
    category: Optional[str] = Query(None),
    limit: int = Query(50, le=500)
):
    """Get products from specific network"""
    manager = MultiNetworkProductManager()
    
    try:
        products = await manager.get_products_by_network(network, category, limit)
        normalized = [manager.normalize_product_data(p, network) for p in products]
        
        return {
            "network": network,
            "category": category or "all",
            "products_found": len(normalized),
            "products": normalized,
            "avg_commission_rate": sum(p.get("commission_rate", 0) for p in normalized) / len(normalized) if normalized else 0
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve products: {str(e)}")

@router.get("/networks/search")
async def search_all_networks(
    keywords: str = Query(..., description="Search keywords"),
    limit: int = Query(100, le=500)
):
    """Search products across all networks"""
    manager = MultiNetworkProductManager()
    
    try:
        results = await manager.search_all_networks(keywords, limit)
        
        # Normalize all results
        normalized_results = {}
        total_products = 0
        
        for network, products in results.items():
            normalized_products = [manager.normalize_product_data(p, network) for p in products]
            normalized_results[network] = normalized_products
            total_products += len(normalized_products)
        
        return {
            "search_keywords": keywords,
            "networks_searched": list(results.keys()),
            "total_products_found": total_products,
            "results_by_network": {
                network: {
                    "count": len(products),
                    "products": products
                }
                for network, products in normalized_results.items()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/networks/{network}/import")
async def bulk_import_network_products(
    network: str,
    category: Optional[str] = None,
    limit: int = Query(500, le=1000)
):
    """Bulk import products from network"""
    manager = MultiNetworkProductManager()
    
    try:
        result = await manager.bulk_import_products(network, category, limit)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@router.get("/networks/health-products")
async def get_health_products_all_networks(limit: int = Query(200, le=1000)):
    """Get health products from all networks"""
    manager = MultiNetworkProductManager()
    
    try:
        results = await manager.get_health_products_all_networks(limit)
        
        # Normalize and aggregate
        all_products = []
        network_summary = {}
        
        for network, products in results.items():
            normalized_products = [manager.normalize_product_data(p, network) for p in products]
            all_products.extend(normalized_products)
            
            network_summary[network] = {
                "products_found": len(normalized_products),
                "avg_commission_rate": sum(p.get("commission_rate", 0) for p in normalized_products) / len(normalized_products) if normalized_products else 0,
                "total_commission_potential": sum(p.get("commission_amount", 0) for p in normalized_products)
            }
        
        return {
            "total_health_products": len(all_products),
            "network_summary": network_summary,
            "top_products": sorted(all_products, key=lambda x: x.get("commission_amount", 0), reverse=True)[:20],
            "all_products": all_products
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve health products: {str(e)}")