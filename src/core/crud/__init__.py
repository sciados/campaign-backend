# src/core/crud/__init__.py - UPDATED: Session 3 Users Module Migration
"""
Centralized CRUD exports - UPDATED for modular architecture
🎯 Single import point for remaining CRUD operations
✅ Global instances ready to use across the application
🆕 User management moved to Users module
"""

from src.core.crud.base_crud import BaseCRUD
from src.core.crud.campaign_crud import CampaignCRUD
# from src.core.crudintelligence_crud import IntelligenceCRUD

# 🔄 DEPRECATED: User CRUD moved to Users module
# Use: from src.users.services.user_service import UserService
# from src.core.crud.user_crud import user_crud  # MOVED TO: src.users.services.user_service

# ✅ NEW: Import UserStorageCRUD
try:
    from src.users.services.user_storage_crud import user_storage_crud
    USER_STORAGE_CRUD_AVAILABLE = True
except ImportError as e:
    # Fallback if user_storage_crud is not available yet
    USER_STORAGE_CRUD_AVAILABLE = False
    UserStorageCRUD = None
    user_storage_crud = None
    print(f"⚠️ UserStorageCRUD not available: {e}")

# Global CRUD instances - ready to use anywhere
campaign_crud = CampaignCRUD()
# intelligence_crud = IntelligenceCRUD()

# 🔄 DEPRECATED: user_crud moved to Users module
# Use UserService instead: 
# from src.users.services.user_service import UserService
# user_service = UserService(db)

# ✅ Export list with conditional user_storage_crud
if USER_STORAGE_CRUD_AVAILABLE:
    __all__ = [
        "BaseCRUD",
        "CampaignCRUD", 
        # "IntelligenceCRUD",
        "UserStorageCRUD",
        "campaign_crud",
        # "intelligence_crud",
        "user_storage_crud",
        # "user_crud"  # DEPRECATED: Moved to Users module
    ]
else:
    __all__ = [
        "BaseCRUD",
        "CampaignCRUD", 
        # "IntelligenceCRUD",
        "campaign_crud",
        # "intelligence_crud",
        # "user_crud"  # DEPRECATED: Moved to Users module
    ]

"""
Centralized CRUD exports for modular architecture.
Note: User CRUD moved to src.users.services.user_service.UserService
"""

# 📊 Import availability check
def get_available_crud_instances():
    """Get dictionary of available CRUD instances"""
    available = {
        "campaign_crud": campaign_crud,
        # "intelligence_crud": intelligence_crud
    }
    
    if USER_STORAGE_CRUD_AVAILABLE:
        available["user_storage_crud"] = user_storage_crud
    
    # Note: user_crud moved to Users module
    available["users_note"] = "Use UserService from src.users.services.user_service"
    
    return available

def check_crud_system_status():
    """Check status of CRUD system"""
    return {
        "base_crud_available": BaseCRUD is not None,
        "campaign_crud_available": campaign_crud is not None,
        # "intelligence_crud_available": intelligence_crud is not None,
        "user_storage_crud_available": USER_STORAGE_CRUD_AVAILABLE,
        "users_module_migration": "✅ Completed - Use UserService",
        "total_crud_classes": len(__all__),
        "system_ready": all([
            BaseCRUD is not None,
            campaign_crud is not None,
        ])
    }