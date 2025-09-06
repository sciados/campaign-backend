# src/core/crud/__init__.py - UPDATED: Added UserStorageCRUD exports
"""
Centralized CRUD exports - UPDATED with Storage CRUD
🎯 Single import point for all CRUD operations
✅ Global instances ready to use across the application
🆕 Added UserStorageCRUD for storage management
"""

from .base_crud import BaseCRUD
from .campaign_crud import CampaignCRUD
# from .intelligence_crud import IntelligenceCRUD
from .user_crud import user_crud

# ✅ NEW: Import UserStorageCRUD
try:
    from .user_storage_crud import user_storage_crud
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

# ✅ Export list with conditional user_storage_crud
if USER_STORAGE_CRUD_AVAILABLE:
    __all__ = [
        "BaseCRUD",
        "CampaignCRUD", 
        "IntelligenceCRUD",
        "UserStorageCRUD",
        "campaign_crud",
#        "intelligence_crud",
        "user_storage_crud",
        "user_crud"
    ]
else:
    __all__ = [
        "BaseCRUD",
        "CampaignCRUD", 
#        "IntelligenceCRUD",
        "campaign_crud",
        "intelligence_crud",
        "user_crud"
    ]

# Usage examples:
"""
# In any service file:
from src.core.crud import campaign_crud, intelligence_crud, user_storage_crud

# In campaign service:
async def get_user_campaigns(db: AsyncSession, user_id: UUID, company_id: UUID):
    return await campaign_crud.get_user_campaigns(
        db=db, 
        user_id=user_id, 
        company_id=company_id
    )

# In intelligence service:
async def get_campaign_intelligence(db: AsyncSession, campaign_id: UUID):
    return await intelligence_crud.get_campaign_intelligence(
        db=db, 
        campaign_id=campaign_id
    )

# ✅ NEW: In storage service:
async def get_user_storage_analytics(db: AsyncSession, user_id: str):
    return await user_storage_crud.get_storage_analytics(
        db=db,
        user_id=user_id,
        days=30
    )

async def create_storage_record(db: AsyncSession, user_id: str, file_data: dict):
    return await user_storage_crud.create_storage_record(
        db=db,
        user_id=user_id,
        **file_data
    )

# Generic CRUD operations:
async def get_campaign_by_id(db: AsyncSession, campaign_id: UUID):
    return await campaign_crud.get(db=db, id=campaign_id)

# Search and filtering:
async def search_campaigns(db: AsyncSession, user_id: UUID, search_term: str):
    return await campaign_crud.search_campaigns(
        db=db,
        user_id=user_id,
        search_term=search_term
    )

# Statistics and analytics:
async def get_campaign_stats(db: AsyncSession, user_id: UUID):
    return await campaign_crud.get_campaign_stats(
        db=db,
        user_id=user_id
    )

# ✅ NEW: Storage management:
async def calculate_user_quota(db: AsyncSession, user_id: str):
    return await user_storage_crud.calculate_user_storage_usage(
        db=db,
        user_id=user_id
    )
"""

# 🔧 Migration Guide for Services:
"""
BEFORE (problematic async patterns):
    result = await db.execute(select(Campaign).where(...))
    campaigns = result.scalars().all()  # ChunkedIteratorResult issue

AFTER (centralized CRUD):
    campaigns = await campaign_crud.get_multi(
        db=db, 
        filters={"user_id": user_id}
    )

BEFORE (complex query building):
    query = select(IntelligenceSourceType)
    query = query.where(IntelligenceSourceType.campaign_id == campaign_id)
    query = query.order_by(desc(IntelligenceSourceType.confidence_score))
    result = await db.execute(query)
    intelligence = result.scalars().all()

AFTER (simplified method call):
    intelligence = await intelligence_crud.get_campaign_intelligence(
        db=db,
        campaign_id=campaign_id
    )

✅ NEW: BEFORE (direct user storage queries):
    result = await db.execute(
        select(UserStorageUsage).where(UserStorageUsage.user_id == user_id)
    )
    files = result.scalars().all()

✅ NEW: AFTER (CRUD storage operations):
    files_data = await user_storage_crud.get_user_files(
        db=db,
        user_id=user_id,
        limit=50
    )
"""

# 🎯 Files that need immediate updating:
FILES_TO_UPDATE = [
    "src/campaigns/services/campaign_service.py",
    "src/campaigns/services/workflow_service.py", 
    "src/intelligence/handlers/intelligence_handler.py",
    "src/intelligence/handlers/analysis_handler.py",
    "src/campaigns/routes/campaign_crud.py",
    "src/campaigns/routes/workflow_operations.py",
    "src/campaigns/routes/dashboard_stats.py",
    # ✅ NEW: Storage-related files
    "src/storage/universal_dual_storage.py",
    "src/routes/user_storage.py",
    "src/routes/admin_storage.py"
]

# 🚀 Next Steps:
"""
1. Replace direct database queries with CRUD methods
2. Remove ChunkedIteratorResult issues by using proven async patterns
3. Simplify service layer code with consistent database access
4. Add proper error handling and logging through CRUD layer
5. Maintain existing API contracts while improving reliability
6. ✅ NEW: Integrate storage management with CRUD operations
7. ✅ NEW: Enable quota management and analytics through CRUD
"""

# 🔍 Import availability check
def get_available_crud_instances():
    """Get dictionary of available CRUD instances"""
    available = {
        "campaign_crud": campaign_crud,
        # "intelligence_crud": intelligence_crud
    }
    
    if USER_STORAGE_CRUD_AVAILABLE:
        available["user_storage_crud"] = user_storage_crud
    
    return available

def check_crud_system_status():
    """Check status of CRUD system"""
    return {
        "base_crud_available": BaseCRUD is not None,
        "campaign_crud_available": campaign_crud is not None,
        # "intelligence_crud_available": intelligence_crud is not None,
        "user_storage_crud_available": USER_STORAGE_CRUD_AVAILABLE,
        "total_crud_classes": len(__all__),
        "system_ready": all([
            BaseCRUD is not None,
            campaign_crud is not None,
        #    intelligence_crud is not None
        ])
    }