# src/intelligence/routers/content_routes.py
"""
ULTRA MINIMAL Content Routes - ZERO dependencies to isolate import issues
"""

# NO IMPORTS - just basic FastAPI
from fastapi import APIRouter

# Create router
router = APIRouter()

print("🔧 ULTRA MINIMAL: Content routes starting...")

@router.get("/test-route")
def test_content_routes():
    """Test endpoint to verify content routes are working"""
    return {"message": "Ultra minimal content routes working!"}

@router.post("/generate")
def generate_content_ultra_minimal():
    """Ultra minimal content generation endpoint"""
    return {
        "content_id": "ultra-minimal-test",
        "success": True,
        "message": "Ultra minimal content generation works"
    }

@router.get("/{campaign_id}")
def get_generated_content_ultra_minimal(campaign_id: str):
    """Ultra minimal get content endpoint"""
    return [
        {
            "content_id": "ultra-minimal-content-1",
            "campaign_id": campaign_id,
            "message": "Ultra minimal content retrieval works"
        }
    ]

print(f"🔧 ULTRA MINIMAL: Router created with {len(router.routes)} routes")
print("🔧 ULTRA MINIMAL: Content routes module loaded successfully")