"""
Campaign Routes Package
Following intelligence/routers pattern for modular organization
"""

from . import campaign_crud
from . import demo_management  
from . import workflow_operations
from . import dashboard_stats
from . import admin_endpoints

__all__ = [
    "campaign_crud",
    "demo_management",
    "workflow_operations", 
    "dashboard_stats",
    "admin_endpoints"
]