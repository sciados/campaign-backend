# src/intelligence/routers/clickbank_routes.py - CORRECTED FOR ACTUAL CLICKBANK API
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Dict, Any
import httpx
import os
import json
from datetime import datetime, timedelta

router = APIRouter()

# ✅ CORRECTED: ClickBank API Configuration
CLICKBANK_API_KEY = os.getenv("CLICKBANK_API_KEY")
# The correct ClickBank API endpoint for marketplace data
CLICKBANK_BASE_URL = "https://api.clickbank.com/rest/1.3/products"

# ✅ Category mapping for ClickBank marketplace categories
CATEGORY_LABELS = {
    "top": {"category": None, "sortField": "gravity", "sortOrder": "DESC"},
    "new": {"category": None, "sortField": "dateCreated", "sortOrder": "DESC"},
    "health": {"category": "Health & Fitness", "sortField": "gravity", "sortOrder": "DESC"},
    "ebusiness": {"category": "E-business & E-marketing", "sortField": "gravity", "sortOrder": "DESC"},
    "selfhelp": {"category": "Self-Help", "sortField": "gravity", "sortOrder": "DESC"},
    "green": {"category": "Green Products", "sortField": "gravity", "sortOrder": "DESC"},
    "business": {"category": "Business / Investing", "sortField": "gravity", "sortOrder": "DESC"},
}

# ✅ Debug endpoint to test API connection
@router.get("/debug-connection", tags=["clickbank-debug"])
async def debug_clickbank_connection() -> Dict[str, Any]:
    """Debug ClickBank API connection with your actual API key"""
    
    if not CLICKBANK_API_KEY:
        return {
            "status": "error",
            "message": "CLICKBANK_API_KEY environment variable not set",
            "api_key_configured": False
        }
    
    # Test with your actual API key format
    try:
        headers = {
            "Authorization": CLICKBANK_API_KEY,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Test the simplest possible request
        test_url = f"{CLICKBANK_BASE_URL}?pageSize=1"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(test_url, headers=headers)
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "api_key_configured": True,
                "api_key_length": len(CLICKBANK_API_KEY),
                "api_key_preview": CLICKBANK_API_KEY[:10] + "...",
                "test_url": test_url,
                "response_headers": dict(response.headers),
                "response_preview": response.text[:1000],
                "permissions_check": "Products API should be enabled in your ClickBank account"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection test failed: {str(e)}",
            "api_key_configured": True
        }

# ✅ CORRECTED: Main products endpoint using proper ClickBank API
@router.get("/top-products", tags=["clickbank"])
async def get_clickbank_products(
    type: str = Query(..., description="Category or type: top, new, health, ebusiness, selfhelp, green, business")
) -> List[Dict[str, Any]]:
    """Get ClickBank products using correct API format"""
    
    if type not in CATEGORY_LABELS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type '{type}'. Allowed: {', '.join(CATEGORY_LABELS.keys())}"
        )
    
    if not CLICKBANK_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="ClickBank API key not configured"
        )
    
    config = CATEGORY_LABELS[type]
    
    # ✅ CORRECTED: Proper ClickBank API headers and parameters
    headers = {
        "Authorization": CLICKBANK_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # ✅ CORRECTED: ClickBank API parameters
    params = {
        "pageSize": 10,
        "sortField": config["sortField"],
        "sortOrder": config["sortOrder"]
    }
    
    # Add category filter if specified
    if config["category"]:
        params["category"] = config["category"]
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(CLICKBANK_BASE_URL, headers=headers, params=params)
            
            print(f"ClickBank API Request: {response.url}")
            print(f"Response Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 400:
                error_detail = response.text
                print(f"ClickBank 400 Error Details: {error_detail}")
                
                # Parse error response
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", error_detail)
                except:
                    error_message = error_detail
                
                raise HTTPException(
                    status_code=400, 
                    detail=f"ClickBank API error: {error_message}"
                )
            
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=401, 
                    detail="ClickBank API authentication failed. Check your API key permissions."
                )
            
            elif response.status_code == 403:
                raise HTTPException(
                    status_code=403, 
                    detail="ClickBank API access forbidden. Ensure Products API permission is enabled."
                )
            
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"ClickBank API returned {response.status_code}: {response.text}"
                )
            
            # Parse successful response
            try:
                data = response.json()
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Invalid JSON response from ClickBank")
            
            # ✅ Extract products from ClickBank response format
            products = []
            
            # Handle different possible response formats
            if isinstance(data, dict):
                if "products" in data:
                    products = data["products"]
                elif "items" in data:
                    products = data["items"]
                elif "data" in data:
                    products = data["data"]
                else:
                    # Data might be the products array directly
                    products = data if isinstance(data, list) else []
            elif isinstance(data, list):
                products = data
            
            # Transform to our format
            enhanced_products = []
            for i, product in enumerate(products):
                if isinstance(product, dict):
                    enhanced_product = {
                        "id": f"cb_{product.get('id', i)}",
                        "title": product.get("title", product.get("name", "Unknown Product")),
                        "vendor": product.get("vendor", product.get("vendorName", "Unknown Vendor")),
                        "description": product.get("description", product.get("summary", "")),
                        "salespage_url": product.get("salesPageUrl", product.get("url", "")),
                        "gravity": float(product.get("gravity", 0)),
                        "commission_rate": float(product.get("commissionRate", product.get("commission", 0))),
                        "product_id": product.get("id", product.get("sku")),
                        "vendor_id": product.get("vendorId", product.get("vendor")),
                        "category": type,
                        "analysis_status": "pending",
                        "is_analyzed": False,
                        "key_insights": [],
                        "recommended_angles": [],
                        "created_at": datetime.utcnow().isoformat()
                    }
                    enhanced_products.append(enhanced_product)
            
            return enhanced_products
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# ✅ Alternative endpoint with different API approach
@router.get("/test-api-format", tags=["clickbank-debug"])
async def test_api_format() -> Dict[str, Any]:
    """Test different ClickBank API endpoint formats"""
    
    if not CLICKBANK_API_KEY:
        return {"error": "No API key"}
    
    # Test different possible endpoints
    endpoints_to_test = [
        "https://api.clickbank.com/rest/1.3/products",
        "https://api.clickbank.com/rest/1.3/products/list",
        "https://api.clickbank.com/rest/1.3/marketplace/products",
        "https://accounts.clickbank.com/rest/1.3/products"
    ]
    
    results = {}
    
    headers = {
        "Authorization": CLICKBANK_API_KEY,
        "Accept": "application/json"
    }
    
    for endpoint in endpoints_to_test:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{endpoint}?pageSize=1", headers=headers)
                results[endpoint] = {
                    "status_code": response.status_code,
                    "response_preview": response.text[:200]
                }
        except Exception as e:
            results[endpoint] = {"error": str(e)}
    
    return results

# ✅ Keep existing endpoints
@router.get("/categories", tags=["clickbank"])
async def get_available_categories() -> List[Dict[str, str]]:
    """Get available ClickBank categories"""
    return [
        {"id": "new", "name": "New Products", "description": "Latest ClickBank products"},
        {"id": "top", "name": "Top Performers", "description": "Highest gravity products"},
        {"id": "health", "name": "Health & Fitness", "description": "Health and wellness products"},
        {"id": "ebusiness", "name": "E-Business & Marketing", "description": "Online business and marketing"},
        {"id": "selfhelp", "name": "Self-Help", "description": "Personal development and self-improvement"},
        {"id": "business", "name": "Business & Investing", "description": "Business and investment products"},
        {"id": "green", "name": "Green Products", "description": "Environmental and sustainability products"}
    ]

# ✅ Mock data for testing while API is being fixed
@router.get("/mock-products", tags=["clickbank-debug"])
async def get_mock_products(
    type: str = Query("new", description="Category type")
) -> List[Dict[str, Any]]:
    """Return mock ClickBank products for testing"""
    
    base_products = [
        {
            "title": "Ultimate Weight Loss System 2025",
            "vendor": "HealthMaster",
            "description": "Revolutionary approach to sustainable weight loss with proven results",
            "gravity": 127.5,
            "commission_rate": 75.0,
            "salespage_url": "https://example.com/weight-loss-system"
        },
        {
            "title": "Digital Marketing Mastery Course",
            "vendor": "MarketingPro",
            "description": "Complete course on building profitable online businesses",
            "gravity": 98.2,
            "commission_rate": 50.0,
            "salespage_url": "https://example.com/marketing-course"
        },
        {
            "title": "Millionaire Mindset Blueprint",
            "vendor": "WealthGuru",
            "description": "Transform your mindset to attract wealth and success",
            "gravity": 85.7,
            "commission_rate": 60.0,
            "salespage_url": "https://example.com/mindset-blueprint"
        },
        {
            "title": "Solar Power Installation Guide",
            "vendor": "GreenEnergy",
            "description": "DIY solar power system installation for homeowners",
            "gravity": 73.4,
            "commission_rate": 40.0,
            "salespage_url": "https://example.com/solar-guide"
        },
        {
            "title": "Cryptocurrency Trading Secrets",
            "vendor": "CryptoExpert",
            "description": "Advanced strategies for profitable crypto trading",
            "gravity": 156.8,
            "commission_rate": 65.0,
            "salespage_url": "https://example.com/crypto-trading"
        }
    ]
    
    # Generate mock products for the category
    mock_products = []
    for i, base in enumerate(base_products):
        mock_product = {
            "id": f"mock_{type}_{i+1}",
            "title": base["title"],
            "vendor": base["vendor"],
            "description": base["description"],
            "salespage_url": base["salespage_url"],
            "gravity": base["gravity"],
            "commission_rate": base["commission_rate"],
            "product_id": f"MOCK{i+1:03d}",
            "vendor_id": base["vendor"].lower(),
            "category": type,
            "analysis_status": "completed" if i % 2 == 0 else "pending",
            "is_analyzed": i % 2 == 0,
            "key_insights": [
                "High-converting sales page with strong testimonials",
                "Clear value proposition and benefits",
                "Professional presentation and credibility markers"
            ] if i % 2 == 0 else [],
            "recommended_angles": [
                "Results-focused messaging",
                "Problem-solution narrative",
                "Authority positioning"
            ] if i % 2 == 0 else [],
            "created_at": datetime.utcnow().isoformat()
        }
        mock_products.append(mock_product)
    
    return mock_products