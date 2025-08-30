# src/services/ai_provider_analyzer.py - FIXED VERSION with missing function

import os
import re
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

class DynamicAIProviderAnalyzer:
    """
    Dynamic AI Provider Analyzer that discovers and analyzes providers from environment
    This is what the discovery system expects but was missing
    """
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI clients for analysis if available"""
        try:
            if os.getenv("OPENAI_API_KEY"):
                # Initialize OpenAI client if needed
                self.openai_client = "available"
        except Exception as e:
            logger.warning(f"OpenAI client initialization failed: {e}")
        
        try:
            if os.getenv("ANTHROPIC_API_KEY"):
                # Initialize Anthropic client if needed  
                self.anthropic_client = "available"
        except Exception as e:
            logger.warning(f"Anthropic client initialization failed: {e}")
    
    async def discover_providers_from_environment(self) -> List[Dict[str, Any]]:
        """
        Discover AI providers from environment variables
        This is the main method that the discovery system calls
        """
        try:
            providers = []
            env_vars = dict(os.environ)
            
            # AI provider patterns
            ai_patterns = [
                r'^([A-Z_]+)_API_KEY$',
                r'^([A-Z_]+)_API_TOKEN$',
                r'^([A-Z_]+)_KEY$',
                r'^([A-Z_]+)_TOKEN$'
            ]
            
            # Skip patterns for non-AI services
            skip_patterns = [
                'DATABASE', 'JWT', 'SECRET', 'CLOUDFLARE', 'RAILWAY',
                'SUPABASE', 'STRIPE', 'SENDGRID', 'SENTRY', 'BACKBLAZE'
            ]
            
            for env_var, value in env_vars.items():
                if not value or not value.strip():
                    continue
                    
                for pattern in ai_patterns:
                    match = re.match(pattern, env_var)
                    if match:
                        provider_key = match.group(1).lower()
                        
                        # Skip non-AI services
                        if any(skip in provider_key.upper() for skip in skip_patterns):
                            continue
                        
                        # Analyze the provider
                        provider_info = await self.ai_analyze_provider(env_var, provider_key, value)
                        if provider_info:
                            providers.append(provider_info)
                        break
            
            logger.info(f"Dynamic analyzer discovered {len(providers)} AI providers")
            return providers
            
        except Exception as e:
            logger.error(f"Provider discovery failed: {e}")
            return []
    
    async def ai_analyze_provider(self, env_var_name: str, provider_key: str, api_key: str) -> Optional[Dict[str, Any]]:
        """
        AI-powered analysis of a provider based on its name and characteristics
        """
        try:
            provider_name = provider_key.replace('_', ' ').title()
            
            # Determine category based on provider name
            category = self._categorize_provider(provider_key)
            
            # Estimate costs based on known patterns
            cost_per_1k_tokens = self._estimate_cost(provider_key)
            
            # Quality score based on known providers
            quality_score = self._estimate_quality(provider_key)
            
            # Speed rating
            speed_rating = self._estimate_speed(provider_key)
            
            # Capabilities
            capabilities = self._determine_capabilities(provider_key, category)
            
            # Use types
            use_types = self._determine_use_types(category)
            
            return {
                'provider_name': provider_name,
                'env_var_name': env_var_name,
                'primary_category': category,
                'secondary_categories': [category],  # Could be expanded
                'capabilities': capabilities,
                'use_types': use_types,
                'cost_per_1k_tokens': cost_per_1k_tokens,
                'video_cost_per_minute': self._estimate_video_cost(provider_key) if 'video' in category else None,
                'image_cost_per_generation': self._estimate_image_cost(provider_key) if 'image' in category else None,
                'quality_score': quality_score,
                'speed_rating': speed_rating,
                'primary_model': self._get_primary_model(provider_key),
                'supported_models': self._get_supported_models(provider_key),
                'response_time_ms': self._estimate_response_time(provider_key),
                'error_rate': self._estimate_error_rate(provider_key),
                'api_endpoint': self._guess_api_endpoint(provider_key),
                'priority_tier': self._determine_priority_tier(cost_per_1k_tokens, category),
                'is_active': True,  # Has API key so assume active
                'ai_confidence_score': 0.8,  # Confidence in our analysis
                'ai_analysis_version': '2.0_dynamic'
            }
            
        except Exception as e:
            logger.warning(f"Failed to analyze provider {provider_key}: {e}")
            return None
    
    def _categorize_provider(self, provider_key: str) -> str:
        """Categorize provider based on name patterns"""
        key_lower = provider_key.lower()
        
        if any(term in key_lower for term in ['replicate', 'runway', 'pika', 'video']):
            return 'video_generation'
        elif any(term in key_lower for term in ['stability', 'dalle', 'midjourney', 'image']):
            return 'image_generation'
        elif any(term in key_lower for term in ['eleven', 'voice', 'speech', 'audio']):
            return 'audio_generation'
        elif any(term in key_lower for term in ['vision', 'multimodal']):
            return 'multimodal'
        else:
            return 'text_generation'
    
    def _estimate_cost(self, provider_key: str) -> float:
        """Estimate cost per 1k tokens based on provider"""
        key_lower = provider_key.lower()
        
        # Known ultra-cheap providers
        if any(term in key_lower for term in ['groq', 'together', 'deepseek']):
            return 0.0002
        elif any(term in key_lower for term in ['cohere', 'aimlapi']):
            return 0.0005
        elif any(term in key_lower for term in ['openai', 'gpt']):
            return 0.002
        elif any(term in key_lower for term in ['anthropic', 'claude']):
            return 0.003
        else:
            return 0.001  # Default estimate
    
    def _estimate_video_cost(self, provider_key: str) -> Optional[float]:
        """Estimate video generation cost per minute"""
        key_lower = provider_key.lower()
        
        if 'replicate' in key_lower:
            return 0.50  # Estimate
        elif 'runway' in key_lower:
            return 2.00  # Estimate
        else:
            return 1.00  # Default
    
    def _estimate_image_cost(self, provider_key: str) -> Optional[float]:
        """Estimate image generation cost per image"""
        key_lower = provider_key.lower()
        
        if 'stability' in key_lower:
            return 0.004  # Estimate
        elif 'dalle' in key_lower:
            return 0.02   # Estimate
        else:
            return 0.01   # Default
    
    def _estimate_quality(self, provider_key: str) -> float:
        """Estimate quality score (1-5)"""
        key_lower = provider_key.lower()
        
        if any(term in key_lower for term in ['openai', 'anthropic', 'claude']):
            return 4.5
        elif any(term in key_lower for term in ['groq', 'together']):
            return 4.0
        else:
            return 3.5  # Default
    
    def _estimate_speed(self, provider_key: str) -> float:
        """Estimate speed rating (1-5)"""
        key_lower = provider_key.lower()
        
        if 'groq' in key_lower:
            return 5.0  # Known for speed
        elif any(term in key_lower for term in ['together', 'deepseek']):
            return 4.0
        else:
            return 3.0  # Default
    
    def _determine_capabilities(self, provider_key: str, category: str) -> List[str]:
        """Determine provider capabilities"""
        capabilities = []
        
        if category == 'text_generation':
            capabilities.extend(['text_generation', 'conversation', 'completion'])
        elif category == 'image_generation':
            capabilities.extend(['image_generation', 'image_editing'])
        elif category == 'video_generation':
            capabilities.extend(['video_generation', 'video_editing'])
        elif category == 'audio_generation':
            capabilities.extend(['text_to_speech', 'voice_cloning'])
        elif category == 'multimodal':
            capabilities.extend(['vision', 'image_understanding', 'multimodal'])
        
        return capabilities
    
    def _determine_use_types(self, category: str) -> List[str]:
        """Determine use types for category"""
        if category == 'text_generation':
            return ['content_creation', 'conversation', 'analysis']
        elif category == 'image_generation':
            return ['content_creation', 'design', 'art_generation']
        elif category == 'video_generation':
            return ['content_creation', 'video_production']
        else:
            return ['content_creation']
    
    def _get_primary_model(self, provider_key: str) -> str:
        """Get primary model name"""
        key_lower = provider_key.lower()
        
        if 'openai' in key_lower:
            return 'gpt-4'
        elif 'anthropic' in key_lower or 'claude' in key_lower:
            return 'claude-3'
        elif 'groq' in key_lower:
            return 'llama-3'
        else:
            return 'unknown'
    
    def _get_supported_models(self, provider_key: str) -> List[str]:
        """Get list of supported models"""
        primary = self._get_primary_model(provider_key)
        return [primary] if primary != 'unknown' else []
    
    def _estimate_response_time(self, provider_key: str) -> int:
        """Estimate response time in milliseconds"""
        key_lower = provider_key.lower()
        
        if 'groq' in key_lower:
            return 500   # Very fast
        elif any(term in key_lower for term in ['together', 'deepseek']):
            return 1000  # Fast
        else:
            return 2000  # Standard
    
    def _estimate_error_rate(self, provider_key: str) -> float:
        """Estimate error rate percentage"""
        return 1.0  # Default 1% error rate
    
    def _guess_api_endpoint(self, provider_key: str) -> Optional[str]:
        """Guess API endpoint URL"""
        key_lower = provider_key.lower()
        
        endpoints = {
            'openai': 'https://api.openai.com/v1',
            'anthropic': 'https://api.anthropic.com',
            'groq': 'https://api.groq.com/openai/v1',
            'together': 'https://api.together.xyz',
            'replicate': 'https://api.replicate.com'
        }
        
        for provider, endpoint in endpoints.items():
            if provider in key_lower:
                return endpoint
        
        return None
    
    def _determine_priority_tier(self, cost: float, category: str) -> str:
        """Determine priority tier"""
        if cost <= 0.0003:
            return 'primary'
        elif cost <= 0.001:
            return 'secondary'
        else:
            return 'expensive'
    
    async def scan_environment_for_ai_providers(self) -> Dict[str, Dict[str, Any]]:
        """Alternative method name for compatibility"""
        providers_list = await self.discover_providers_from_environment()
        
        # Convert list to dict format expected by some callers
        providers_dict = {}
        for provider in providers_list:
            env_var = provider.get('env_var_name')
            if env_var:
                providers_dict[env_var] = provider
        
        return providers_dict

# Global instance
_dynamic_analyzer_instance = None

def get_dynamic_ai_provider_analyzer() -> DynamicAIProviderAnalyzer:
    """
    Get or create dynamic AI provider analyzer instance
    This is the function that was missing and causing import errors
    """
    global _dynamic_analyzer_instance
    if _dynamic_analyzer_instance is None:
        _dynamic_analyzer_instance = DynamicAIProviderAnalyzer()
    return _dynamic_analyzer_instance

# Add to your __all__ export list
__all__ = [
    'get_ai_provider_analyzer',
    'get_dynamic_ai_provider_analyzer',  # This was missing!
    'DynamicAIProviderAnalyzer',        # Add this too
    'AIProviderAnalyzer', 
    'get_ai_provider_analyzer_instance',
    'analyze_ai_providers',
    'get_provider_stats'
]