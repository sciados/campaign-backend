# src/routes/__init__.py

"""
Routes package for CampaignForge Backend
Contains all API route definitions
"""

from .waitlist import router as waitlist_router

__all__ = ["waitlist_router"]