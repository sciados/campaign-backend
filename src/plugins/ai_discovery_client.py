import httpx
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class AiDiscoveryPlugin:
    """Client for integrating AI Discovery Service with main CampaignForge app"""
    
    def __init__(self, discovery_service_url: str = None):
        self.base_url = (discovery_service_url or 
                        os.getenv("AI_DISCOVERY_SERVICE_URL", "http://localhost:8001")).rstrip('/')
        self.client = httpx.AsyncClient(timeout=10)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"AI Discovery Service request failed: {e}")
            return {
                "error": "AI Discovery Service unavailable",
                "details": str(e),
                "service_status": "disconnected"
            }
    
    async def get_discoveries_widget_data(self, days: int = 7) -> Dict[str, Any]:
        """Get data for admin dashboard discoveries widget"""
        return await self._make_request("GET", f"/api/v1/discoveries/recent?days={days}")
    
    async def get_provider_recommendations(self) -> Dict[str, Any]:
        """Get current best providers for each AI category"""
        return await self._make_request("GET", "/api/v1/providers/recommendations")
    
    async def check_service_health(self) -> Dict[str, Any]:
        """Check if AI Discovery Service is running and healthy"""
        return await self._make_request("GET", "/health")
    
    async def get_aggregated_dashboard_data(self) -> Dict[str, Any]:
        """Get all data needed for admin dashboard in single call"""
        
        # Fetch all data concurrently
        results = await asyncio.gather(
            self.get_discoveries_widget_data(),
            self.get_provider_recommendations(),
            self.check_service_health(),
            return_exceptions=True
        )
        
        discoveries, recommendations, health = results
        
        # Handle any exceptions
        def safe_result(result, default=None):
            return result if not isinstance(result, Exception) else (default or {"error": str(result)})
        
        return {
            "discoveries": safe_result(discoveries, {"discoveries": [], "summary": {"total_found": 0}}),
            "recommendations": safe_result(recommendations, {}),
            "service_health": safe_result(health, {"status": "unknown"}),
            "last_updated": datetime.utcnow().isoformat(),
            "is_connected": not isinstance(health, Exception)
        }