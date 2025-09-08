# src/users/dashboard/__init__.py

"""User Dashboard"""

from src.users.dashboard.dashboard_service import DashboardService

# Import dashboard routes if they exist
try:
    from src.users.dashboard.dashboard_routes import router as dashboard_router
    __all__ = [
        "DashboardService",
        "dashboard_router"
    ]
except ImportError:
    # Routes not available
    __all__ = [
        "DashboardService"
    ]