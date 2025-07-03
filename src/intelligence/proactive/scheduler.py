# Proactive Analysis Scheduler
# File: src/intelligence/proactive/scheduler.py

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import logger

from intelligence.proactive.sales_page_monitor import ProactiveSalesPageMonitor


class ProactiveAnalysisScheduler:
    """Schedule and manage proactive analysis tasks"""
    
    def __init__(self, db: AsyncSession):
        self.monitor = ProactiveSalesPageMonitor(db)
        self.running = False
    
    async def start_monitoring(self):
        """Start the proactive monitoring process"""
        self.running = True
        logger.info("🚀 Starting proactive sales page monitoring...")
        
        while self.running:
            try:
                # Process discovery for each source
                for source in self.monitor.sources:
                    if source.monitoring_enabled:
                        new_urls = await self.monitor.discover_new_sales_pages(source, limit=20)
                        
                        # Queue discovered URLs for analysis
                        for url in new_urls:
                            await self.monitor.queue_url_for_proactive_analysis(
                                url=url,
                                priority=source.priority,
                                source=source.name
                            )
                
                # Process the analysis queue
                await self.monitor.process_proactive_analysis_queue(batch_size=5)
                
                # Wait before next cycle (adjust based on your needs)
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring cycle: {str(e)}")
                await asyncio.sleep(300)  # 5 minutes on error
    
    def stop_monitoring(self):
        """Stop the proactive monitoring process"""
        self.running = False
        logger.info("⏹️ Stopping proactive sales page monitoring...")