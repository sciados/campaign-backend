# src/intelligence/routers/clickbank_routes.py - FIXED VERSION
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Dict, Any
import httpx
import os
import json
from datetime import datetime, timedelta

# ✅ Keep your existing API setup
router = APIRouter()
CLICKBANK_API_KEY = os.getenv("CLICKBANK_API_KEY")
CLICKBANK_BASE_URL = "https://api.clickbank.com/rest/1.3/products/list"

# ✅ Keep your existing category mapping
CATEGORY_LABELS = {
    "top": {"category": None, "sortField": "gravity"},
    "new": {"category": None, "sortField": "dateCreated"},
    "health": {"category": "Health & Fitness", "sortField": "gravity"},
    "ebusiness": {"category": "E-business & E-marketing", "sortField": "gravity"},
    "selfhelp": {"category": "Self-Help", "sortField": "gravity"},
    "green": {"category": "Green Products", "sortField": "gravity"},
    "business": {"category": "Business / Investing", "sortField": "gravity"},
}

# ✅ Your existing endpoint - keep this working
@router.get("/top-products", tags=["clickbank"])
async def get_clickbank_products(
    type: str = Query(..., description="Category or type: top, new, health, ebusiness, selfhelp, green, business")
) -> List[Dict[str, Any]]:
    if type not in CATEGORY_LABELS:
        return [{"error": f"Invalid type '{type}'. Allowed: {', '.join(CATEGORY_LABELS.keys())}"}]

    config = CATEGORY_LABELS[type]
    headers = {"Authorization": CLICKBANK_API_KEY}
    params = {"results": 10, "sortField": config["sortField"]}

    if config["category"]:
        params["category"] = config["category"]

    async with httpx.AsyncClient() as client:
        resp = await client.get(CLICKBANK_BASE_URL, headers=headers, params=params)
        if resp.status_code != 200:
            return [{"error": f"ClickBank API error: {resp.text}"}]

        data = resp.json()
        products = data.get("products", [])

    return [
        {
            "title": p.get("title"),
            "vendor": p.get("vendor"),
            "description": p.get("description"),
            "salespage_url": p.get("pitchPageUrl"),
            "gravity": p.get("gravity", 0),
            "commission_rate": p.get("commissionRate", 0),
            "product_id": p.get("sku"),
            "vendor_id": p.get("vendor"),
            "category": type,
            "analysis_status": "pending",  # Default status
            "is_analyzed": False,
            "key_insights": [],
            "recommended_angles": [],
            "created_at": datetime.utcnow().isoformat()
        }
        for p in products
    ]

# ✅ NEW: Enhanced endpoint that works without database models
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

# ✅ NEW: Get products by category (enhanced version of your existing endpoint)
@router.get("/products/{category}", tags=["clickbank"])
async def get_category_products(
    category: str,
    analyzed_only: bool = Query(False, description="Only return analyzed products"),
    limit: int = Query(20, description="Number of products to return")
) -> List[Dict[str, Any]]:
    """Get products for a specific category with enhanced data"""
    
    if category not in CATEGORY_LABELS:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    
    config = CATEGORY_LABELS[category]
    headers = {"Authorization": CLICKBANK_API_KEY}
    params = {"results": limit, "sortField": config["sortField"]}

    if config["category"]:
        params["category"] = config["category"]

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(CLICKBANK_BASE_URL, headers=headers, params=params)
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail=f"ClickBank API error: {resp.text}")

            data = resp.json()
            products = data.get("products", [])

        enhanced_products = []
        for p in products:
            product_data = {
                "id": f"cb_{p.get('sku', '')}_temp",  # Temporary ID until we have database
                "title": p.get("title", ""),
                "vendor": p.get("vendor", ""),
                "description": p.get("description", ""),
                "gravity": float(p.get("gravity", 0)),
                "commission_rate": float(p.get("commissionRate", 0)),
                "salespage_url": p.get("pitchPageUrl", ""),
                "product_id": p.get("sku"),
                "vendor_id": p.get("vendor"),
                "category": category,
                "analysis_status": "pending",
                "analysis_score": None,
                "key_insights": [],
                "recommended_angles": [],
                "is_analyzed": False,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # If analyzed_only is requested, skip non-analyzed products
            if analyzed_only and not product_data["is_analyzed"]:
                continue
                
            enhanced_products.append(product_data)

        return enhanced_products
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# ✅ NEW: Simple product analysis endpoint (without database for now)
@router.post("/products/{product_id}/analyze", tags=["clickbank"])
async def analyze_product_simple(product_id: str) -> Dict[str, Any]:
    """Trigger analysis for a specific product (placeholder for now)"""
    
    # For now, return a mock response
    # Later this will integrate with your intelligence analysis system
    return {
        "product_id": product_id,
        "analysis_status": "processing",
        "message": "Analysis started. This will be implemented with your intelligence system.",
        "estimated_completion": "2-3 minutes"
    }

# ✅ NEW: Simple favorites endpoints (using in-memory storage for now)
# In production, these would use your database
_user_favorites = {}  # Temporary storage - replace with database later

@router.post("/favorites/{product_id}", tags=["clickbank"])
async def add_to_favorites_simple(product_id: str, notes: str = None) -> Dict[str, str]:
    """Add product to favorites (temporary implementation)"""
    
    # For now, use simple in-memory storage
    # Later this will use your User model and database
    user_id = "temp_user"  # Replace with actual user ID from auth
    
    if user_id not in _user_favorites:
        _user_favorites[user_id] = {}
    
    _user_favorites[user_id][product_id] = {
        "notes": notes,
        "added_at": datetime.utcnow().isoformat()
    }
    
    return {"message": "Product added to favorites"}

@router.delete("/favorites/{product_id}", tags=["clickbank"])
async def remove_from_favorites_simple(product_id: str) -> Dict[str, str]:
    """Remove product from favorites (temporary implementation)"""
    
    user_id = "temp_user"  # Replace with actual user ID from auth
    
    if user_id in _user_favorites and product_id in _user_favorites[user_id]:
        del _user_favorites[user_id][product_id]
        return {"message": "Product removed from favorites"}
    
    raise HTTPException(status_code=404, detail="Favorite not found")

@router.get("/favorites", tags=["clickbank"])
async def get_user_favorites_simple() -> List[Dict[str, Any]]:
    """Get user's favorite products (temporary implementation)"""
    
    user_id = "temp_user"  # Replace with actual user ID from auth
    
    if user_id not in _user_favorites:
        return []
    
    # Return list of favorited product IDs
    # In production, this would join with the products table
    favorites = []
    for product_id, data in _user_favorites[user_id].items():
        favorites.append({
            "product_id": product_id,
            "notes": data["notes"],
            "added_at": data["added_at"]
        })
    
    return favorites

# ✅ NEW: Test endpoint to verify API key
@router.get("/test-connection", tags=["clickbank"])
async def test_clickbank_connection() -> Dict[str, Any]:
    """Test ClickBank API connection"""
    
    if not CLICKBANK_API_KEY:
        return {
            "status": "error",
            "message": "CLICKBANK_API_KEY not configured"
        }
    
    try:
        headers = {"Authorization": CLICKBANK_API_KEY}
        params = {"results": 1, "sortField": "gravity"}
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(CLICKBANK_BASE_URL, headers=headers, params=params)
            
            return {
                "status": "success" if resp.status_code == 200 else "error",
                "status_code": resp.status_code,
                "api_key_configured": True,
                "api_key_length": len(CLICKBANK_API_KEY),
                "base_url": CLICKBANK_BASE_URL,
                "response_preview": resp.json() if resp.status_code == 200 else resp.text[:200]
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection test failed: {str(e)}",
            "api_key_configured": True,
            "api_key_length": len(CLICKBANK_API_KEY)
        }