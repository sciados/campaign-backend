# src/intelligence/adapters/__init__.py
"""
Intelligence Adapters - Clean Import System
No circular imports, lazy loading for optimal performance
"""

import logging

logger = logging.getLogger(__name__)

# Export main components with error handling
try:
    from .dynamic_router import DynamicAIRouter, get_dynamic_router, route_text_generation, route_image_generation
    DYNAMIC_ROUTER_AVAILABLE = True
    logger.info("✅ Dynamic router imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Dynamic router import failed: {e}")
    DYNAMIC_ROUTER_AVAILABLE = False

# Create fallback classes if imports fail
if not DYNAMIC_ROUTER_AVAILABLE:
    class DynamicAIRouter:
        def __init__(self):
            logger.warning("Using fallback DynamicAIRouter")
        
        async def get_optimal_provider(self, content_type: str, task_complexity: str = "standard"):
            return None
        
        async def execute_with_optimal_provider(self, content_type: str, generation_function: callable, **kwargs):
            raise Exception("Dynamic router not available")
    
    async def get_dynamic_router():
        return DynamicAIRouter()
    
    async def route_text_generation(generation_function: callable, content_type: str = "text", **kwargs):
        raise Exception("Text routing not available")
    
    async def route_image_generation(generation_function: callable, **kwargs):
        raise Exception("Image routing not available")

__all__ = [
    "DynamicAIRouter",
    "get_dynamic_router", 
    "route_text_generation",
    "route_image_generation",
    "DYNAMIC_ROUTER_AVAILABLE"
]

logger.info(f"🔧 Adapters module loaded - Dynamic router available: {DYNAMIC_ROUTER_AVAILABLE}")