# src/mockups/mockup_module.py
from fastapi import APIRouter, FastAPI
from src.mockups.api.routes import router as mockup_router

class MockupModule:
    """
    Product Mockup Module
    Handles image compositing for product-on-template rendering.
    """

    def __init__(self, app: FastAPI):
        self.app = app
        self.version = "1.0.0"
        self.description = "Product image overlay and mockup generation module"

        # Attach routes directly to the main FastAPI app
        self.register_routes()

    def register_routes(self):
        """Register mockup API routes with the FastAPI app"""
        self.app.include_router(mockup_router, prefix="/api/mockups", tags=["Mockups"])
