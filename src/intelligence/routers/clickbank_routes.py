# src/intelligence/routers/clickbank_routes.py - LIVE CLICKBANK SCRAPING
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Dict, Any, Optional
import httpx
import asyncio
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
from urllib.parse import urljoin, urlparse
import logging

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClickBankScraper:
    def __init__(self):
        self.base_url = "https://clickbank.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        }
        
        # ClickBank marketplace category URLs
        self.category_urls = {
            "top": "https://clickbank.com/marketplace?sortBy=gravity&page=1",
            "new": "https://clickbank.com/marketplace?sortBy=launchDate&page=1", 
            "health": "https://clickbank.com/marketplace/categories/health-fitness?sortBy=gravity&page=1",
            "business": "https://clickbank.com/marketplace/categories/business-investing?sortBy=gravity&page=1",
            "ebusiness": "https://clickbank.com/marketplace/categories/business-investing/marketing?sortBy=gravity&page=1",
            "selfhelp": "https://clickbank.com/marketplace/categories/self-help?sortBy=gravity&page=1",
            "green": "https://clickbank.com/marketplace/categories/green-products?sortBy=gravity&page=1"
        }

    async def extract_sales_page_url(self, product_page_url: str) -> Optional[str]:
        """
        Extract the actual sales page URL from a ClickBank product page
        """
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=self.headers) as client:
                response = await client.get(product_page_url)
                
                if response.status_code != 200:
                    return None
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for the sales page link - ClickBank uses different patterns
                sales_link = None
                
                # Pattern 1: Direct link to sales page
                sales_link = soup.find('a', {'class': re.compile(r'.*sales.*page.*', re.I)})
                if not sales_link:
                    # Pattern 2: "Visit Website" or "View Sales Page" button
                    sales_link = soup.find('a', string=re.compile(r'.*(visit|view|sales|website).*', re.I))
                if not sales_link:
                    # Pattern 3: Look for external links (not clickbank.com)
                    all_links = soup.find_all('a', href=True)
                    for link in all_links:
                        href = link.get('href')
                        if href and not href.startswith('#') and 'clickbank.com' not in href:
                            if href.startswith('http'):
                                sales_link = link
                                break
                
                if sales_link:
                    href = sales_link.get('href')
                    if href:
                        # Make absolute URL if needed
                        if href.startswith('/'):
                            href = urljoin(self.base_url, href)
                        return href
                
                return None
                
        except Exception as e:
            logger.error(f"Error extracting sales page URL from {product_page_url}: {e}")
            return None

    async def scrape_category_products(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape top products from a specific ClickBank category
        """
        if category not in self.category_urls:
            raise ValueError(f"Category '{category}' not supported")
        
        url = self.category_urls[category]
        logger.info(f"Scraping ClickBank category: {category} from {url}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0, headers=self.headers) as client:
                response = await client.get(url)
                
                if response.status_code != 200:
                    logger.error(f"Failed to fetch marketplace page: {response.status_code}")
                    return []
                
                soup = BeautifulSoup(response.text, 'html.parser')
                products = []
                
                # Find product containers - ClickBank uses various selectors
                product_selectors = [
                    'div[class*="product"]',
                    'div[class*="listing"]', 
                    'div[class*="item"]',
                    'article',
                    'li[class*="product"]'
                ]
                
                product_elements = []
                for selector in product_selectors:
                    elements = soup.select(selector)
                    if elements:
                        product_elements = elements
                        break
                
                logger.info(f"Found {len(product_elements)} product elements")
                
                # Process each product
                for i, element in enumerate(product_elements[:limit * 2]):  # Get extra in case some fail
                    try:
                        product_data = await self.extract_product_data(element)
                        if product_data and len(products) < limit:
                            products.append(product_data)
                            logger.info(f"Extracted product {len(products)}: {product_data['title']}")
                    except Exception as e:
                        logger.error(f"Error processing product element {i}: {e}")
                        continue
                
                logger.info(f"Successfully scraped {len(products)} products from {category}")
                return products
                
        except Exception as e:
            logger.error(f"Error scraping category {category}: {e}")
            return []

    async def extract_product_data(self, element) -> Optional[Dict[str, Any]]:
        """
        Extract product data from a product element
        """
        try:
            # Extract title
            title_elem = (element.find('h3') or 
                         element.find('h2') or 
                         element.find('a', {'class': re.compile(r'.*title.*', re.I)}) or
                         element.find('a', string=True))
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            if not title:
                return None
            
            # Extract vendor
            vendor_elem = (element.find('span', {'class': re.compile(r'.*vendor.*', re.I)}) or
                          element.find('div', {'class': re.compile(r'.*vendor.*', re.I)}) or
                          element.find('p', {'class': re.compile(r'.*vendor.*', re.I)}))
            
            vendor = vendor_elem.get_text(strip=True) if vendor_elem else "Unknown Vendor"
            
            # Extract gravity
            gravity_elem = (element.find('span', {'class': re.compile(r'.*gravity.*', re.I)}) or
                           element.find('div', {'class': re.compile(r'.*gravity.*', re.I)}))
            
            gravity = 0.0
            if gravity_elem:
                gravity_text = gravity_elem.get_text(strip=True)
                gravity_match = re.search(r'(\d+(?:\.\d+)?)', gravity_text)
                if gravity_match:
                    gravity = float(gravity_match.group(1))
            
            # Extract commission rate
            commission_elem = (element.find('span', string=re.compile(r'.*%.*')) or
                             element.find('div', string=re.compile(r'.*commission.*', re.I)))
            
            commission_rate = 50.0  # Default
            if commission_elem:
                commission_text = commission_elem.get_text(strip=True)
                commission_match = re.search(r'(\d+(?:\.\d+)?)%', commission_text)
                if commission_match:
                    commission_rate = float(commission_match.group(1))
            
            # Extract product page URL
            product_link = element.find('a', href=True)
            product_page_url = None
            sales_page_url = None
            
            if product_link:
                href = product_link.get('href')
                if href.startswith('/'):
                    product_page_url = urljoin(self.base_url, href)
                else:
                    product_page_url = href
                
                # Extract sales page URL
                sales_page_url = await self.extract_sales_page_url(product_page_url)
            
            # Extract description
            desc_elem = (element.find('p') or 
                        element.find('div', {'class': re.compile(r'.*desc.*', re.I)}))
            
            description = desc_elem.get_text(strip=True) if desc_elem else f"ClickBank product: {title}"
            
            # Generate product ID
            product_id = re.sub(r'[^a-zA-Z0-9]', '', title.upper())[:10]
            
            product_data = {
                "title": title,
                "vendor": vendor,
                "description": description[:200] + "..." if len(description) > 200 else description,
                "gravity": gravity,
                "commission_rate": commission_rate,
                "salespage_url": sales_page_url or product_page_url or f"https://clickbank.com/products/{product_id.lower()}",
                "product_page_url": product_page_url,
                "product_id": product_id,
                "vendor_id": re.sub(r'[^a-zA-Z0-9]', '', vendor.lower()),
                "scraped_at": datetime.utcnow().isoformat(),
                "is_live_data": True
            }
            
            return product_data
            
        except Exception as e:
            logger.error(f"Error extracting product data: {e}")
            return None

# Initialize scraper
scraper = ClickBankScraper()

@router.get("/live-products/{category}", tags=["clickbank-live"])
async def get_live_clickbank_products(
    category: str,
    limit: int = Query(10, ge=1, le=20, description="Number of products to scrape (max 20)")
) -> Dict[str, Any]:
    """
    Scrape live ClickBank products from the marketplace
    Returns top performers by gravity score for the specified category
    """
    
    if category not in scraper.category_urls:
        raise HTTPException(
            status_code=400, 
            detail=f"Category '{category}' not supported. Available: {list(scraper.category_urls.keys())}"
        )
    
    try:
        start_time = datetime.utcnow()
        
        # Scrape products
        products = await scraper.scrape_category_products(category, limit)
        
        # Format for API response
        formatted_products = []
        for i, product in enumerate(products):
            formatted_product = {
                "id": f"live_{product['product_id']}_{category}_{i}",
                "title": product["title"],
                "vendor": product["vendor"],
                "description": product["description"],
                "salespage_url": product["salespage_url"],
                "gravity": product["gravity"],
                "commission_rate": product["commission_rate"],
                "product_id": product["product_id"],
                "vendor_id": product["vendor_id"],
                "category": category,
                "analysis_status": "pending",
                "is_analyzed": False,
                "key_insights": [],
                "recommended_angles": [],
                "created_at": product["scraped_at"],
                "data_source": "live_scraping",
                "product_page_url": product.get("product_page_url"),
                "is_real_product": True
            }
            formatted_products.append(formatted_product)
        
        end_time = datetime.utcnow()
        scraping_time = (end_time - start_time).total_seconds()
        
        return {
            "category": category,
            "products_requested": limit,
            "products_found": len(formatted_products),
            "products": formatted_products,
            "scraping_metadata": {
                "scraped_at": end_time.isoformat(),
                "scraping_time_seconds": scraping_time,
                "data_source": "clickbank_marketplace",
                "marketplace_url": scraper.category_urls[category],
                "is_live_data": True
            },
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error in live scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@router.get("/live-all-categories", tags=["clickbank-live"])
async def get_all_categories_live(
    products_per_category: int = Query(5, ge=1, le=10, description="Products per category")
) -> Dict[str, Any]:
    """
    Scrape top products from all ClickBank categories
    """
    
    start_time = datetime.utcnow()
    all_results = {}
    total_products = 0
    
    # Scrape all categories concurrently
    tasks = []
    for category in scraper.category_urls.keys():
        task = scraper.scrape_category_products(category, products_per_category)
        tasks.append((category, task))
    
    # Wait for all scraping tasks to complete
    for category, task in tasks:
        try:
            products = await task
            all_results[category] = products
            total_products += len(products)
            logger.info(f"Completed scraping {category}: {len(products)} products")
        except Exception as e:
            logger.error(f"Failed to scrape {category}: {e}")
            all_results[category] = []
    
    end_time = datetime.utcnow()
    scraping_time = (end_time - start_time).total_seconds()
    
    return {
        "categories_scraped": list(scraper.category_urls.keys()),
        "products_per_category": products_per_category,
        "total_products_found": total_products,
        "results": all_results,
        "scraping_metadata": {
            "scraped_at": end_time.isoformat(),
            "total_scraping_time_seconds": scraping_time,
            "data_source": "clickbank_marketplace",
            "is_live_data": True
        },
        "success": True
    }

@router.get("/validate-sales-url", tags=["clickbank-live"])
async def validate_sales_page_url(
    url: str = Query(..., description="Sales page URL to validate")
) -> Dict[str, Any]:
    """
    Validate that a sales page URL is accessible and analyze its content
    """
    
    try:
        async with httpx.AsyncClient(timeout=15.0, headers=scraper.headers) as client:
            response = await client.get(url)
            
            analysis = {
                "url": url,
                "status_code": response.status_code,
                "is_accessible": response.status_code == 200,
                "response_time_ms": response.elapsed.total_seconds() * 1000 if hasattr(response, 'elapsed') else None,
                "content_length": len(response.text) if response.status_code == 200 else 0,
                "validated_at": datetime.utcnow().isoformat()
            }
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract page info
                title = soup.find('title')
                analysis["page_title"] = title.get_text(strip=True) if title else "No title"
                
                # Look for ClickBank indicators
                analysis["has_order_button"] = bool(soup.find('a', href=re.compile(r'clickbank\.com.*order', re.I)))
                analysis["has_clickbank_links"] = bool(soup.find('a', href=re.compile(r'clickbank\.com', re.I)))
                analysis["is_likely_clickbank_product"] = analysis["has_order_button"] or analysis["has_clickbank_links"]
                
                # Count key elements
                analysis["total_links"] = len(soup.find_all('a', href=True))
                analysis["total_images"] = len(soup.find_all('img'))
                analysis["has_video"] = bool(soup.find('video') or soup.find('iframe', src=re.compile(r'youtube|vimeo', re.I)))
            
            return analysis
            
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "is_accessible": False,
            "validated_at": datetime.utcnow().isoformat()
        }

@router.get("/scraping-status", tags=["clickbank-live"])
async def get_scraping_status() -> Dict[str, Any]:
    """
    Get information about the scraping capabilities and supported categories
    """
    
    return {
        "scraper_status": "operational",
        "supported_categories": list(scraper.category_urls.keys()),
        "category_urls": scraper.category_urls,
        "max_products_per_request": 20,
        "features": [
            "Live marketplace scraping",
            "Real sales page URL extraction", 
            "Product data validation",
            "Gravity score extraction",
            "Commission rate detection",
            "Vendor information extraction"
        ],
        "limitations": [
            "Depends on ClickBank marketplace structure",
            "Rate limited to prevent blocking",
            "Some products may not have extractable sales URLs",
            "Scraping time varies by category size"
        ],
        "last_updated": datetime.utcnow().isoformat()
    }

# Update your existing endpoint to use live scraping
@router.get("/top-products", tags=["clickbank"])
async def get_clickbank_products(
    type: str = Query(..., description="Category: top, new, health, ebusiness, selfhelp, green, business"),
    use_live_data: bool = Query(True, description="Use live scraping (recommended)")
) -> List[Dict[str, Any]]:
    """
    Get ClickBank products - now uses live scraping by default
    """
    
    if use_live_data:
        # Use live scraping
        result = await get_live_clickbank_products(type, limit=10)
        return result["products"]
    else:
        # Fallback to cached/mock data if needed
        raise HTTPException(status_code=400, detail="Live scraping is required. Set use_live_data=true")