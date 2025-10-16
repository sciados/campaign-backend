from fastapi import APIRouter
from src.mockups.api.routes import router as mockup_router

class MockupModule:
    """
    Product Mockup Module
    Handles image compositing for product-on-template rendering.
    """

    def __init__(self):
        self.router = APIRouter()
        self.version = "1.0.0"
        self.description = "Product image overlay and mockup generation module"

    async def initialize(self):
        """Include mockup API routes"""
        self.router.include_router(mockup_router, prefix="/api/mockups", tags=["Mockups"])
        return True

    def get_router(self):
        return self.router
