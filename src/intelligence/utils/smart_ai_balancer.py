# src/intelligence/utils/smart_ai_balancer.py
"""
Smart Load Balancer for Ultra-Cheap AI Providers
Automatically switches between Groq, Together, DeepSeek when rate limits hit
SOLVES: Rate limit issues by distributing load across multiple cheap providers
"""
import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SmartAILoadBalancer:
    """
    Intelligent load balancer that switches between ultra-cheap AI providers
    when rate limits are hit, ensuring continuous operation at minimum cost
    """
    
    def __init__(self, ai_providers: List[Dict[str, Any]]):
        self.providers = sorted(ai_providers, key=lambda x: x.get('cost_per_1k_tokens', 999))
        self.provider_status = {}
        self.request_counts = {}
        self.last_requests = {}
        
        # Initialize provider tracking
        for provider in self.providers:
            name = provider.get('name', 'unknown')
            self.provider_status[name] = {
                'available': True,
                'rate_limited_until': None,
                'consecutive_failures': 0,
                'requests_this_minute': 0,
                'last_success': datetime.now(),
                'total_requests': 0,
                'total_failures': 0
            }
            
        logger.info(f"🔄 Smart Load Balancer initialized with {len(self.providers)} ultra-cheap providers")
        self._log_provider_summary()
    
    def _log_provider_summary(self):
        """Log summary of available providers and their costs"""
        logger.info("💰 ULTRA-CHEAP PROVIDER LINEUP:")
        for i, provider in enumerate(self.providers, 1):
            name = provider.get('name', 'unknown')
            cost = provider.get('cost_per_1k_tokens', 0)
            quality = provider.get('quality_score', 0)
            logger.info(f"   {i}. {name}: ${cost:.5f}/1K tokens, quality: {quality}/100")
    
    def get_best_available_provider(self) -> Optional[Dict[str, Any]]:
        """
        Get the best available provider based on:
        1. Not rate limited
        2. Lowest cost
        3. Recent success rate
        """
        
        current_time = datetime.now()
        
        # Remove expired rate limits
        for name, status in self.provider_status.items():
            if status['rate_limited_until'] and current_time >= status['rate_limited_until']:
                status['rate_limited_until'] = None
                status['available'] = True
                logger.info(f"✅ {name}: Rate limit expired, back online")
        
        # Find best available provider
        available_providers = []
        for provider in self.providers:
            name = provider.get('name', 'unknown')
            status = self.provider_status.get(name, {})
            
            if status.get('available', True) and not status.get('rate_limited_until'):
                # Calculate success rate
                total_requests = status.get('total_requests', 0)
                total_failures = status.get('total_failures', 0)
                success_rate = 1.0 if total_requests == 0 else (total_requests - total_failures) / total_requests
                
                # Don't use providers with >50% failure rate and >5 requests
                if total_requests > 5 and success_rate < 0.5:
                    logger.warning(f"⚠️ {name}: Low success rate ({success_rate:.1%}), skipping")
                    continue
                
                available_providers.append({
                    'provider': provider,
                    'name': name,
                    'cost': provider.get('cost_per_1k_tokens', 999),
                    'success_rate': success_rate,
                    'consecutive_failures': status.get('consecutive_failures', 0)
                })
        
        if not available_providers:
            logger.error("❌ NO PROVIDERS AVAILABLE - all are rate limited or failed")
            return None
        
        # Sort by: fewest consecutive failures, then lowest cost, then highest success rate
        available_providers.sort(key=lambda x: (
            x['consecutive_failures'],
            x['cost'],
            -x['success_rate']
        ))
        
        best = available_providers[0]
        provider = best['provider']
        name = best['name']
        
        logger.info(f"🎯 Selected provider: {name} (${best['cost']:.5f}/1K, {best['success_rate']:.1%} success)")
        return provider
    
    def mark_rate_limited(self, provider_name: str, retry_after_seconds: int = 60):
        """Mark a provider as rate limited"""
        
        if provider_name in self.provider_status:
            retry_time = datetime.now() + timedelta(seconds=retry_after_seconds)
            self.provider_status[provider_name]['rate_limited_until'] = retry_time
            self.provider_status[provider_name]['available'] = False
            
            logger.warning(f"🚨 {provider_name}: Rate limited until {retry_time.strftime('%H:%M:%S')}")
            
            # Log next best option
            next_best = self.get_best_available_provider()
            if next_best:
                next_name = next_best.get('name', 'unknown')
                next_cost = next_best.get('cost_per_1k_tokens', 0)
                logger.info(f"🔄 Switching to: {next_name} (${next_cost:.5f}/1K tokens)")
            else:
                logger.error("🚨 ALL PROVIDERS RATE LIMITED!")
    
    def mark_request_success(self, provider_name: str):
        """Mark a successful request"""
        if provider_name in self.provider_status:
            status = self.provider_status[provider_name]
            status['consecutive_failures'] = 0
            status['last_success'] = datetime.now()
            status['total_requests'] += 1
            
            # Reset availability if it was marked as failed
            if not status['available'] and not status['rate_limited_until']:
                status['available'] = True
                logger.info(f"✅ {provider_name}: Back online after success")
    
    def mark_request_failure(self, provider_name: str, error_message: str = ""):
        """Mark a failed request"""
        if provider_name in self.provider_status:
            status = self.provider_status[provider_name]
            status['consecutive_failures'] += 1
            status['total_requests'] += 1
            status['total_failures'] += 1
            
            # Check if this is a rate limit error
            if "rate limit" in error_message.lower() or "429" in error_message:
                # Extract retry time if available
                retry_seconds = 60  # Default
                if "try again in" in error_message:
                    try:
                        # Extract seconds from message like "try again in 5.973s"
                        import re
                        match = re.search(r'try again in (\d+\.?\d*)s', error_message)
                        if match:
                            retry_seconds = int(float(match.group(1))) + 5  # Add buffer
                    except:
                        pass
                
                self.mark_rate_limited(provider_name, retry_seconds)
            
            # Temporarily disable if too many consecutive failures
            elif status['consecutive_failures'] >= 3:
                status['available'] = False
                retry_time = datetime.now() + timedelta(minutes=2)
                status['rate_limited_until'] = retry_time
                logger.warning(f"⚠️ {provider_name}: Disabled due to {status['consecutive_failures']} consecutive failures")
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get current statistics for all providers"""
        stats = {
            'providers': {},
            'total_available': 0,
            'cheapest_available': None,
            'total_requests': 0
        }
        
        current_time = datetime.now()
        cheapest_cost = float('inf')
        
        for provider in self.providers:
            name = provider.get('name', 'unknown')
            status = self.provider_status.get(name, {})
            cost = provider.get('cost_per_1k_tokens', 999)
            
            is_available = (
                status.get('available', True) and 
                (not status.get('rate_limited_until') or current_time >= status['rate_limited_until'])
            )
            
            if is_available:
                stats['total_available'] += 1
                if cost < cheapest_cost:
                    cheapest_cost = cost
                    stats['cheapest_available'] = name
            
            stats['providers'][name] = {
                'available': is_available,
                'cost_per_1k': cost,
                'consecutive_failures': status.get('consecutive_failures', 0),
                'total_requests': status.get('total_requests', 0),
                'total_failures': status.get('total_failures', 0),
                'success_rate': self._calculate_success_rate(status),
                'rate_limited_until': status.get('rate_limited_until')
            }
            
            stats['total_requests'] += status.get('total_requests', 0)
        
        return stats
    
    def _calculate_success_rate(self, status: Dict[str, Any]) -> float:
        """Calculate success rate for a provider"""
        total = status.get('total_requests', 0)
        failures = status.get('total_failures', 0)
        return 1.0 if total == 0 else (total - failures) / total
    
    def log_status_summary(self):
        """Log a summary of current provider status"""
        stats = self.get_provider_stats()
        
        logger.info("📊 LOAD BALANCER STATUS:")
        logger.info(f"   Available providers: {stats['total_available']}/{len(self.providers)}")
        logger.info(f"   Cheapest available: {stats['cheapest_available']}")
        logger.info(f"   Total requests: {stats['total_requests']}")
        
        for name, provider_stats in stats['providers'].items():
            status_emoji = "✅" if provider_stats['available'] else "❌"
            success_rate = provider_stats['success_rate']
            cost = provider_stats['cost_per_1k']
            requests = provider_stats['total_requests']
            
            logger.info(f"   {status_emoji} {name}: ${cost:.5f}/1K, {success_rate:.1%} success, {requests} requests")


#  AI throttle with smart load balancing
async def smart_ai_call_with_balancing(
    load_balancer: SmartAILoadBalancer,
    prompt: str,
    system_message: str = "You are a helpful AI assistant. Always respond with valid JSON when requested.",
    max_retries: int = 3
) -> Any:
    """
    Make AI call with smart load balancing across ultra-cheap providers
    Automatically switches providers when rate limits are hit
    """
    
    from src.intelligence.utils.ai_throttle import safe_ai_call
    
    for attempt in range(max_retries):
        # Get best available provider
        provider = load_balancer.get_best_available_provider()
        
        if not provider:
            logger.error(f"❌ No providers available for attempt {attempt + 1}")
            if attempt == max_retries - 1:
                raise Exception("All ultra-cheap AI providers are unavailable")
            
            # Wait before trying again
            await asyncio.sleep(30)
            continue
        
        provider_name = provider.get('name', 'unknown')
        client = provider.get('client')
        
        # Model mapping
        model_map = {
            "groq": "llama-3.3-70b-versatile",
            "together": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", 
            "deepseek": "deepseek-chat",
            "anthropic": "claude-3-haiku-20240307",
            "cohere": "command-r-plus"
        }
        
        model = model_map.get(provider_name, "llama-3.3-70b-versatile")
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        
        try:
            logger.info(f"🔄 Attempt {attempt + 1}: Using {provider_name} (${provider.get('cost_per_1k_tokens', 0):.5f}/1K)")
            
            # Make the call with centralized throttling
            result = await safe_ai_call(
                client=client,
                provider_name=provider_name,
                model=model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            # Mark success
            load_balancer.mark_request_success(provider_name)
            
            # Check if result indicates fallback/error
            if isinstance(result, dict) and result.get("fallback"):
                logger.warning(f"⚠️ {provider_name} returned fallback response")
                load_balancer.mark_request_failure(provider_name, "Fallback response received")
                
                if attempt < max_retries - 1:
                    continue  # Try next provider
                else:
                    return result  # Return fallback on final attempt
            
            logger.info(f"✅ {provider_name}: Success on attempt {attempt + 1}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ {provider_name}: Failed on attempt {attempt + 1} - {error_msg}")
            
            # Mark failure and handle rate limiting
            load_balancer.mark_request_failure(provider_name, error_msg)
            
            if attempt == max_retries - 1:
                logger.error(f"❌ All {max_retries} attempts failed")
                raise Exception(f"All ultra-cheap AI providers failed: {error_msg}")
            
            # Small delay before retry
            await asyncio.sleep(2)
    
    raise Exception("Smart AI call failed after all attempts")


# Global load balancer instance (will be initialized by the enhancement modules)
_global_load_balancer: Optional[SmartAILoadBalancer] = None

def get_global_load_balancer() -> Optional[SmartAILoadBalancer]:
    """Get the global load balancer instance"""
    return _global_load_balancer

def set_global_load_balancer(providers: List[Dict[str, Any]]):
    """Set the global load balancer with providers"""
    global _global_load_balancer
    _global_load_balancer = SmartAILoadBalancer(providers)
    return _global_load_balancer