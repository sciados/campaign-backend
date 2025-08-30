# API Endpoints for Manual Control
# File: src/intelligence/routers/proactive_analysis.py

from fastapi import APIRouter, Depends
from core.database import get_async_db
from intelligence.proactive.sales_page_monitor import ProactiveSalesPageMonitor
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/proactive", tags=["proactive-analysis"])

@router.post("/queue-url")
async def queue_url_for_analysis(
    url: str,
    priority: int = 3,
    db: AsyncSession = Depends(get_async_db)
):
    """Manually queue a URL for proactive analysis"""
    monitor = ProactiveSalesPageMonitor(db)
    success = await monitor.queue_url_for_proactive_analysis(url, priority, "manual")
    
    return {
        "success": success,
        "message": f"URL queued for analysis with priority {priority}" if success else "Failed to queue URL",
        "url": url
    }

@router.get("/stats")
async def get_proactive_stats(db: AsyncSession = Depends(get_async_db)):
    """Get proactive analysis statistics"""
    monitor = ProactiveSalesPageMonitor(db)
    stats = await monitor.get_proactive_analysis_stats()
    return stats

@router.post("/process-queue")
async def process_queue_manually(
    batch_size: int = 10,
    db: AsyncSession = Depends(get_async_db)
):
    """Manually trigger queue processing"""
    monitor = ProactiveSalesPageMonitor(db)
    result = await monitor.process_proactive_analysis_queue(batch_size)
    return result