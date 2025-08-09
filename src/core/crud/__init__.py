# src/core/crud/__init__.py
"""
Centralized CRUD exports
🎯 Single import point for all CRUD operations
✅ Global instances ready to use across the application
"""

from .base_crud import BaseCRUD
from .campaign_crud import CampaignCRUD
from .intelligence_crud import IntelligenceCRUD

# Global CRUD instances - ready to use anywhere
campaign_crud = CampaignCRUD()
intelligence_crud = IntelligenceCRUD()

__all__ = [
    "BaseCRUD",
    "CampaignCRUD", 
    "IntelligenceCRUD",
    "campaign_crud",
    "intelligence_crud"
]

# Usage examples:
"""
# In any service file:
from src.core.crud import campaign_crud, intelligence_crud

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
    query = select(CampaignIntelligence)
    query = query.where(CampaignIntelligence.campaign_id == campaign_id)
    query = query.order_by(desc(CampaignIntelligence.confidence_score))
    result = await db.execute(query)
    intelligence = result.scalars().all()

AFTER (simplified method call):
    intelligence = await intelligence_crud.get_campaign_intelligence(
        db=db,
        campaign_id=campaign_id
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
    "src/campaigns/routes/dashboard_stats.py"
]

# 🚀 Next Steps:
"""
1. Replace direct database queries with CRUD methods
2. Remove ChunkedIteratorResult issues by using proven async patterns
3. Simplify service layer code with consistent database access
4. Add proper error handling and logging through CRUD layer
5. Maintain existing API contracts while improving reliability
"""