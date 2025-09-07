# src/campaigns/api/__init__.py

"""Campaign API Routes"""

# Import router when routes.py is implemented
try:
    from src.campaigns.dashboard import router
    __all__ = ["router"]
except ImportError:
    # Routes not implemented yet
    __all__ = []