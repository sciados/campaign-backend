# src/services/ai_provider_analyzer.py - FIXED VERSION with missing function

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from intelligence.utils.tiered_ai_provider import ServiceTier

logger = logging.getLogger(__name__)

def get_ai_provider_analyzer() -> Dict[str, Any]:
    """Get AI provider analyzer instance and status"""
    
    try:
        # Check if tiered AI system is available
        tiered_available = False
        load_balancing_available = False
        
        try:
            from src.intelligence.utils.tiered_ai_provider import (
                get_tiered_ai_provider, 
                ServiceTier
            )
            tiered_available = True
            logger.info("Tiered AI provider system available")
        except ImportError:
            logger.warning("Tiered AI provider system not available")
        
        try:
            from src.intelligence.amplifier.enhancement import (
                get_load_balancing_stats,
                _get_next_provider_with_load_balancing
            )
            load_balancing_available = True
            logger.info("Load balancing system available")
        except ImportError:
            logger.warning("Load balancing system not available")
        
        # Get provider statistics if available
        provider_stats = {}
        if tiered_available:
            try:
                provider_manager = get_tiered_ai_provider(ServiceTier.free)
                free_providers = provider_manager.get_available_providers(ServiceTier.free)
                
                provider_stats = {
                    "total_providers": len(free_providers),
                    "available_providers": [p['name'] for p in free_providers if p.get('available', True)],
                    "average_cost_per_1k": sum(p.get('cost_per_1k_tokens', 0) for p in free_providers) / len(free_providers) if free_providers else 0,
                    "provider_details": free_providers
                }
            except Exception as e:
                logger.error(f"Error getting provider stats: {e}")
                provider_stats = {"error": str(e)}
        
        return {
            "analyzer_available": True,
            "tiered_system_available": tiered_available,
            "load_balancing_available": load_balancing_available,
            "provider_stats": provider_stats,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analyzer_version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"AI Provider analyzer error: {e}")
        return {
            "analyzer_available": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

class AIProviderAnalyzer:
    """AI Provider performance and cost analyzer"""
    
    def __init__(self):
        self.tiered_available = False
        self.load_balancing_available = False
        self._initialize_systems()
    
    def _initialize_systems(self):
        """Initialize available AI systems"""
        try:
            from src.intelligence.utils.tiered_ai_provider import get_tiered_ai_provider, ServiceTier
            self.tiered_available = True
            self.provider_manager = get_tiered_ai_provider(ServiceTier.free)
            logger.info("AI Provider Analyzer: Tiered system initialized")
        except ImportError:
            logger.warning("AI Provider Analyzer: Tiered system not available")
        
        try:
            from src.intelligence.amplifier.enhancement import get_load_balancing_stats
            self.load_balancing_available = True
            logger.info("AI Provider Analyzer: Load balancing system initialized")
        except ImportError:
            logger.warning("AI Provider Analyzer: Load balancing system not available")
    
    def get_provider_analysis(self) -> Dict[str, Any]:
        """Get comprehensive provider analysis"""
        
        analysis = {
            "system_status": {
                "tiered_system": self.tiered_available,
                "load_balancing": self.load_balancing_available,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            },
            "provider_performance": self._analyze_provider_performance(),
            "cost_analysis": self._analyze_costs(),
            "recommendations": self._generate_recommendations()
        }
        
        return analysis
    
    def _analyze_provider_performance(self) -> Dict[str, Any]:
        """Analyze provider performance metrics"""
        
        if not self.tiered_available:
            return {"error": "Tiered system not available for performance analysis"}
        
        try:
            free_providers = self.provider_manager.get_available_providers(ServiceTier.free)
            
            performance_data = {
                "total_providers": len(free_providers),
                "active_providers": sum(1 for p in free_providers if p.get('available', True)),
                "provider_breakdown": []
            }
            
            for provider in free_providers:
                provider_info = {
                    "name": provider.get('name', 'unknown'),
                    "available": provider.get('available', False),
                    "cost_per_1k_tokens": provider.get('cost_per_1k_tokens', 0),
                    "quality_score": provider.get('quality_score', 0),
                    "speed_rating": provider.get('speed_rating', 0),
                    "provider_tier": provider.get('provider_tier', 'unknown')
                }
                performance_data["provider_breakdown"].append(provider_info)
            
            return performance_data
            
        except Exception as e:
            return {"error": f"Performance analysis failed: {str(e)}"}
    
    def _analyze_costs(self) -> Dict[str, Any]:
        """Analyze cost efficiency across providers"""
        
        if not self.tiered_available:
            return {"error": "Tiered system not available for cost analysis"}
        
        try:
            free_providers = self.provider_manager.get_available_providers(ServiceTier.free)
            
            costs = [p.get('cost_per_1k_tokens', 0) for p in free_providers if p.get('available', True)]
            
            if not costs:
                return {"error": "No cost data available"}
            
            openai_cost = 0.030  # OpenAI GPT-4 cost per 1K tokens
            average_cost = sum(costs) / len(costs)
            min_cost = min(costs)
            max_cost = max(costs)
            
            savings_vs_openai = ((openai_cost - average_cost) / openai_cost) * 100 if average_cost > 0 else 0
            
            return {
                "average_cost_per_1k": average_cost,
                "min_cost_per_1k": min_cost,
                "max_cost_per_1k": max_cost,
                "openai_comparison": openai_cost,
                "savings_percentage": savings_vs_openai,
                "total_providers_analyzed": len(costs)
            }
            
        except Exception as e:
            return {"error": f"Cost analysis failed: {str(e)}"}
    
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        
        recommendations = []
        
        if not self.tiered_available:
            recommendations.append("Install tiered AI provider system for cost optimization")
        
        if not self.load_balancing_available:
            recommendations.append("Enable load balancing for better provider distribution")
        
        if self.tiered_available and self.load_balancing_available:
            recommendations.extend([
                "Ultra-cheap AI providers are active and optimized",
                "Load balancing is distributing requests efficiently",
                "Continue monitoring for cost optimization opportunities"
            ])
        
        recommendations.append("Regular monitoring of provider performance recommended")
        
        return recommendations

# Create global instance
_analyzer_instance = None

def get_ai_provider_analyzer_instance() -> AIProviderAnalyzer:
    """Get or create AI provider analyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = AIProviderAnalyzer()
    return _analyzer_instance

# Compatibility functions
def analyze_ai_providers() -> Dict[str, Any]:
    """Analyze AI providers - compatibility function"""
    analyzer = get_ai_provider_analyzer_instance()
    return analyzer.get_provider_analysis()

def get_provider_stats() -> Dict[str, Any]:
    """Get provider statistics - compatibility function"""
    return get_ai_provider_analyzer()

# Export the main function that was missing
__all__ = [
    'get_ai_provider_analyzer',
    'AIProviderAnalyzer', 
    'get_ai_provider_analyzer_instance',
    'analyze_ai_providers',
    'get_provider_stats'
]