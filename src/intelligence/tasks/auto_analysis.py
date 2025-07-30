# src/intelligence/tasks/auto_analysis.py
"""
Auto Analysis Tasks for Campaign Intelligence
Production-ready implementation integrating with existing CompetitiveAnalyzer
"""

import logging
from typing import Optional, Dict, Any, Union
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class AutoAnalysisTask:
    """
    Auto Analysis Task Handler
    Integrates with your existing CompetitiveAnalyzer for real intelligence extraction
    """
    
    def __init__(self):
        self.task_id_counter = 0
    
    def _generate_task_id(self, campaign_id: str) -> str:
        """Generate unique task ID"""
        self.task_id_counter += 1
        return f"analysis_{campaign_id}_{self.task_id_counter}_{int(datetime.now().timestamp())}"
    
    async def trigger_analysis(
        self,
        campaign_id: str,
        salespage_url: str,
        user_id: str,
        company_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Trigger comprehensive campaign analysis using CompetitiveAnalyzer
        
        Args:
            campaign_id: Campaign to analyze
            salespage_url: URL to analyze
            user_id: User requesting analysis
            company_id: Company context
            **kwargs: Additional parameters
            
        Returns:
            Analysis results with metadata
        """
        
        task_id = self._generate_task_id(campaign_id)
        
        try:
            logger.info(f"🔍 Starting analysis task {task_id} for campaign {campaign_id}")
            logger.info(f"📄 Analyzing URL: {salespage_url}")
            
            # Validate inputs
            if not salespage_url or not salespage_url.strip():
                raise ValueError("Sales page URL is required")
            
            if not campaign_id:
                raise ValueError("Campaign ID is required")
            
            # Perform analysis using your existing CompetitiveAnalyzer
            analysis_result = await self._run_competitive_analysis(
                salespage_url, campaign_id, user_id, company_id, **kwargs
            )
            
            logger.info(f"✅ Analysis task {task_id} completed successfully")
            
            return {
                "success": True,
                "task_id": task_id,
                "campaign_id": campaign_id,
                "user_id": user_id,
                "company_id": company_id,
                "result": analysis_result,
                "metadata": {
                    "started_at": datetime.now().isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "analyzer_used": "CompetitiveAnalyzer",
                    "version": "2.0.0-production"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Analysis task {task_id} failed: {e}")
            
            return {
                "success": False,
                "task_id": task_id,
                "campaign_id": campaign_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "metadata": {
                    "started_at": datetime.now().isoformat(),
                    "failed_at": datetime.now().isoformat(),
                    "version": "2.0.0-production"
                }
            }
    
    async def _run_competitive_analysis(
        self,
        salespage_url: str,
        campaign_id: str,
        user_id: str,
        company_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run your existing CompetitiveAnalyzer
        """
        
        try:
            # Import your existing analyzer
            from src.intelligence.analyzers import CompetitiveAnalyzer
            
            logger.info(f"🤖 Initializing CompetitiveAnalyzer for URL: {salespage_url}")
            
            # Initialize your existing competitive analyzer
            competitive_analyzer = CompetitiveAnalyzer()
            
            # Call your existing analyze_competitor method
            analysis_result = await competitive_analyzer.analyze_competitor(
                url=salespage_url,
                campaign_id=campaign_id
            )
            
            logger.info(f"✅ CompetitiveAnalyzer completed successfully")
            
            # Return the analysis result with task metadata
            return {
                "success": True,
                "analysis_result": analysis_result,
                "metadata": {
                    "campaign_id": campaign_id,
                    "user_id": user_id,
                    "company_id": company_id,
                    "salespage_url": salespage_url,
                    "analyzer_used": "CompetitiveAnalyzer",
                    "analysis_method": "analyze_competitor",
                    "started_at": datetime.now().isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "version": "2.0.0-production"
                }
            }
            
        except ImportError as e:
            logger.error(f"❌ CompetitiveAnalyzer import failed: {e}")
            raise RuntimeError(f"CompetitiveAnalyzer not available: {e}")
        
        except Exception as e:
            logger.error(f"❌ CompetitiveAnalyzer execution failed: {e}")
            raise RuntimeError(f"Competitive analysis failed: {e}")

# Create singleton instance
_analysis_task = AutoAnalysisTask()

# ============================================================================
# ✅ PUBLIC API FUNCTIONS
# ============================================================================

async def trigger_auto_analysis_task_fixed(
    campaign_id: str,
    salespage_url: str,
    user_id: str = None,
    company_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main entry point for auto analysis tasks
    Integrates with your existing CompetitiveAnalyzer system
    """
    
    # Provide defaults for optional parameters
    user_id = user_id or "unknown"
    company_id = company_id or "unknown"
    
    return await _analysis_task.trigger_analysis(
        campaign_id=campaign_id,
        salespage_url=salespage_url,
        user_id=user_id,
        company_id=company_id,
        **kwargs
    )

def _check_dependencies() -> Dict[str, bool]:
    """Check production dependencies and intelligence systems"""
    dependencies = {}
    
    # Check your custom intelligence analyzer (primary dependency)
    try:
        from src.intelligence.analyzers import CompetitiveAnalyzer
        dependencies["competitive_analyzer"] = True
        dependencies["intelligence_system"] = True
    except ImportError:
        dependencies["competitive_analyzer"] = False
        dependencies["intelligence_system"] = False
    
    # Check AI provider infrastructure
    intelligence_packages = [
        "openai",        # Primary AI provider
        "aiohttp",       # Web scraping
        "beautifulsoup4", # HTML parsing
    ]
    
    for package in intelligence_packages:
        try:
            __import__(package)
            dependencies[package] = True
        except ImportError:
            dependencies[package] = False
    
    # Check OpenAI configuration (used by CompetitiveAnalyzer)
    if dependencies.get("openai", False):
        try:
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            dependencies["openai_configured"] = bool(api_key and len(api_key) > 10)
        except Exception:
            dependencies["openai_configured"] = False
    else:
        dependencies["openai_configured"] = False
    
    # Check ultra-cheap AI providers (used by CompetitiveAnalyzer)
    ultra_cheap_providers = ["groq", "together", "deepseek"]
    ultra_cheap_available = 0
    
    for provider in ultra_cheap_providers:
        key_name = f"{provider.upper()}_API_KEY"
        try:
            import os
            api_key = os.getenv(key_name)
            if api_key and len(api_key) > 10:
                dependencies[f"{provider}_configured"] = True
                ultra_cheap_available += 1
            else:
                dependencies[f"{provider}_configured"] = False
        except Exception:
            dependencies[f"{provider}_configured"] = False
    
    dependencies["ultra_cheap_providers_available"] = ultra_cheap_available
    dependencies["cost_optimization_enabled"] = ultra_cheap_available > 0
    
    # Core Python packages (should always be available)
    core_packages = ["asyncio", "datetime", "logging", "typing"]
    for package in core_packages:
        try:
            __import__(package)
            dependencies[package] = True
        except ImportError:
            dependencies[package] = False
    
    return dependencies

def get_analysis_task_status() -> Dict[str, Any]:
    """Get status information about the analysis task system"""
    dependencies = _check_dependencies()
    
    return {
        "status": "operational" if dependencies.get("competitive_analyzer", False) else "degraded",
        "version": "2.0.0-production",
        "primary_analyzer": "CompetitiveAnalyzer",
        "intelligence_system_available": dependencies.get("intelligence_system", False),
        "ultra_cheap_providers": dependencies.get("ultra_cheap_providers_available", 0),
        "cost_optimization": {
            "enabled": dependencies.get("cost_optimization_enabled", False),
            "groq_available": dependencies.get("groq_configured", False),
            "together_available": dependencies.get("together_configured", False),
            "deepseek_available": dependencies.get("deepseek_configured", False),
            "estimated_savings": "95%+ vs OpenAI" if dependencies.get("cost_optimization_enabled", False) else "0%"
        },
        "features": [
            "URL competitive analysis",
            "Product name extraction", 
            "Load-balanced AI providers",
            "Ultra-cheap AI integration",
            "Real-time intelligence extraction"
        ],
        "dependencies": dependencies
    }

# ============================================================================
# ✅ MODULE EXPORTS
# ============================================================================

__all__ = [
    "trigger_auto_analysis_task_fixed",
    "AutoAnalysisTask",
    "get_analysis_task_status"
]

logger.info("✅ Auto analysis tasks module loaded successfully")