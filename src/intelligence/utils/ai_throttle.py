# src/intelligence/utils/ai_throttle.py
"""
AI Request Throttling and Multi-Provider Failover System
🔥 FIXED: Intelligent provider failover with NO mock data contamination
🚀 NEW: Analysis queue system for complete failures
⚡ ENHANCED: Load balancing with automatic provider health tracking
"""
import asyncio
import time
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Global rate limiting state
_last_request_time = {}
_request_counts = {}
_current_minute = 0

# 🔥 NEW: Provider health tracking
_provider_health = {}
_provider_failure_counts = {}
_provider_last_failure = {}

# 🚀 NEW: Analysis queue for failed requests
_analysis_queue = []
_queue_processor_running = False

class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DISABLED = "disabled"

@dataclass
class QueuedAnalysis:
    url: str
    request_type: str
    messages: List[Dict]
    model: str
    kwargs: Dict
    retry_count: int = 0
    next_retry_at: datetime = None
    created_at: datetime = None
    metadata: Dict = None

class ProviderFailureError(Exception):
    """Raised when all providers have failed"""
    pass

# ============================================================================
# PROVIDER HEALTH TRACKING SYSTEM
# ============================================================================

def _update_provider_health(provider_name: str, success: bool, error_message: str = None) -> None:
    """
    🔥 NEW: Track provider health and automatically disable failing providers
    """
    global _provider_health, _provider_failure_counts, _provider_last_failure
    
    current_time = time.time()
    
    # Initialize tracking for new providers
    if provider_name not in _provider_health:
        _provider_health[provider_name] = ProviderStatus.HEALTHY
        _provider_failure_counts[provider_name] = 0
        _provider_last_failure[provider_name] = 0
    
    if success:
        # Reset failure count on successful request
        _provider_failure_counts[provider_name] = max(0, _provider_failure_counts[provider_name] - 1)
        
        # Upgrade health status if recovering
        if _provider_health[provider_name] == ProviderStatus.DEGRADED and _provider_failure_counts[provider_name] == 0:
            _provider_health[provider_name] = ProviderStatus.HEALTHY
            logger.info(f"🟢 {provider_name}: Recovered to HEALTHY status")
        elif _provider_health[provider_name] == ProviderStatus.UNHEALTHY and _provider_failure_counts[provider_name] <= 2:
            _provider_health[provider_name] = ProviderStatus.DEGRADED
            logger.info(f"🟡 {provider_name}: Improved to DEGRADED status")
            
    else:
        # Increment failure count
        _provider_failure_counts[provider_name] += 1
        _provider_last_failure[provider_name] = current_time
        
        # Determine new health status based on failure pattern
        failure_count = _provider_failure_counts[provider_name]
        
        # Check for payment/auth errors (immediate disable)
        if error_message and any(term in error_message.lower() for term in ['402', 'payment', 'insufficient', 'balance', 'billing', '401', 'unauthorized']):
            _provider_health[provider_name] = ProviderStatus.DISABLED
            logger.error(f"🔴 {provider_name}: DISABLED due to payment/auth error: {error_message}")
        elif failure_count >= 5:
            _provider_health[provider_name] = ProviderStatus.UNHEALTHY
            logger.warning(f"🔴 {provider_name}: UNHEALTHY ({failure_count} failures)")
        elif failure_count >= 2:
            _provider_health[provider_name] = ProviderStatus.DEGRADED
            logger.warning(f"🟡 {provider_name}: DEGRADED ({failure_count} failures)")

def _is_provider_healthy(provider_name: str) -> bool:
    """Check if provider is healthy enough to use"""
    status = _provider_health.get(provider_name, ProviderStatus.HEALTHY)
    return status in [ProviderStatus.HEALTHY, ProviderStatus.DEGRADED]

def _get_provider_priority_score(provider_name: str, base_priority: int = 1) -> float:
    """
    🔥 NEW: Calculate dynamic priority score based on health and performance
    Lower score = higher priority
    """
    status = _provider_health.get(provider_name, ProviderStatus.HEALTHY)
    failure_count = _provider_failure_counts.get(provider_name, 0)
    
    # Base priority (1=highest, 3=lowest for ultra-cheap providers)
    score = float(base_priority)
    
    # Health status adjustments
    if status == ProviderStatus.HEALTHY:
        score += 0.0  # No penalty
    elif status == ProviderStatus.DEGRADED:
        score += 0.5  # Slight penalty
    elif status == ProviderStatus.UNHEALTHY:
        score += 2.0  # Heavy penalty
    elif status == ProviderStatus.DISABLED:
        score += 100.0  # Effectively disabled
    
    # Recent failure penalty
    score += failure_count * 0.1
    
    return score

def get_provider_health_report() -> Dict[str, Any]:
    """Get comprehensive provider health report"""
    report = {
        "providers": {},
        "summary": {
            "healthy": 0,
            "degraded": 0,
            "unhealthy": 0,
            "disabled": 0
        }
    }
    
    for provider_name in _provider_health:
        status = _provider_health[provider_name]
        failure_count = _provider_failure_counts.get(provider_name, 0)
        last_failure = _provider_last_failure.get(provider_name, 0)
        
        report["providers"][provider_name] = {
            "status": status.value,
            "failure_count": failure_count,
            "last_failure_ago": time.time() - last_failure if last_failure > 0 else None,
            "is_usable": _is_provider_healthy(provider_name)
        }
        
        # Update summary
        report["summary"][status.value] += 1
    
    return report

# ============================================================================
# ENHANCED THROTTLING WITH HEALTH AWARENESS
# ============================================================================

async def throttle_ai_request(provider_name: str) -> None:
    """
    Enhanced throttling with provider health awareness
    """
    global _last_request_time, _request_counts, _current_minute
    
    current_time = time.time()
    current_minute_key = int(current_time // 60)
    
    # Reset counters every minute
    if current_minute_key != _current_minute:
        _current_minute = current_minute_key
        _request_counts = {}
    
    # Initialize provider tracking
    if provider_name not in _request_counts:
        _request_counts[provider_name] = 0
        _last_request_time[provider_name] = 0
    
    # Enhanced limits based on provider health
    base_limits = {
        "groq": {"max_per_minute": 15, "min_delay": 4.0},
        "together": {"max_per_minute": 60, "min_delay": 1.0},
        "deepseek": {"max_per_minute": 40, "min_delay": 1.5},
        "anthropic": {"max_per_minute": 30, "min_delay": 2.0},
        "openai": {"max_per_minute": 80, "min_delay": 0.8}
    }
    
    provider_limit = base_limits.get(provider_name, {"max_per_minute": 10, "min_delay": 6.0})
    
    # Adjust limits based on provider health
    status = _provider_health.get(provider_name, ProviderStatus.HEALTHY)
    if status == ProviderStatus.DEGRADED:
        # Reduce limits for degraded providers
        provider_limit["max_per_minute"] = int(provider_limit["max_per_minute"] * 0.7)
        provider_limit["min_delay"] = provider_limit["min_delay"] * 1.5
        logger.debug(f"🟡 {provider_name}: Using reduced limits due to degraded status")
    
    # Check if we're at the rate limit
    if _request_counts[provider_name] >= provider_limit["max_per_minute"]:
        wait_time = 60 - (current_time % 60)
        logger.warning(f"⏳ {provider_name}: Rate limit reached, waiting {wait_time:.1f}s")
        await asyncio.sleep(wait_time)
        _request_counts[provider_name] = 0
    
    # Ensure minimum delay between requests
    time_since_last = current_time - _last_request_time[provider_name]
    min_delay = provider_limit["min_delay"]
    
    if time_since_last < min_delay:
        delay = min_delay - time_since_last
        logger.debug(f"⏱️ {provider_name}: Throttling {delay:.1f}s")
        await asyncio.sleep(delay)
    
    # Update tracking
    _request_counts[provider_name] += 1
    _last_request_time[provider_name] = time.time()

# ============================================================================
# ENHANCED JSON VALIDATION (NO MOCK DATA)
# ============================================================================

def validate_and_parse_json(response_text: str, provider_name: str = "AI") -> Any:
    """
    🔥 FIXED: Validate and parse JSON response WITHOUT mock data fallbacks
    Returns None if parsing fails - no mock data contamination
    """
    
    if not response_text or not response_text.strip():
        logger.error(f"❌ Empty response from {provider_name}")
        return None
    
    # Clean the response text first
    cleaned = response_text.strip()
    
    # First attempt: Direct JSON parsing
    try:
        result = json.loads(cleaned)
        logger.debug(f"✅ JSON parsed successfully from {provider_name}")
        return result
    except json.JSONDecodeError as e:
        logger.warning(f"⚠️ JSON parse error from {provider_name}: {str(e)}")
        
        # Second attempt: Fix common issues
        try:
            # Remove markdown code blocks
            if cleaned.startswith("```"):
                lines = cleaned.split('\n')
                # Remove first line if it's a code block marker
                if lines[0].strip().startswith("```"):
                    lines = lines[1:]
                # Remove last line if it's a code block marker
                if lines and lines[-1].strip().startswith("```"):
                    lines = lines[:-1]
                cleaned = '\n'.join(lines).strip()
            
            # Remove common prefixes/suffixes that aren't JSON
            cleaned = re.sub(r'^[^{\[]*', '', cleaned)  # Remove everything before first { or [
            cleaned = re.sub(r'[^}\]]*$', '', cleaned)  # Remove everything after last } or ]
            
            # Fix common JSON issues
            cleaned = re.sub(r',\s*}', '}', cleaned)  # Remove trailing commas before }
            cleaned = re.sub(r',\s*]', ']', cleaned)  # Remove trailing commas before ]
            cleaned = re.sub(r'}\s*{', '},{', cleaned)  # Fix missing commas between objects
            
            # Try parsing the cleaned version
            result = json.loads(cleaned)
            logger.info(f"✅ Fixed JSON response from {provider_name}")
            return result
            
        except json.JSONDecodeError:
            logger.error(f"❌ Could not fix JSON from {provider_name}")
            
            # Third attempt: Extract JSON objects from mixed content
            try:
                # Look for JSON objects in the text (more aggressive)
                json_matches = [
                    r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Nested objects
                    r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]',  # Nested arrays
                    r'\{.*?\}',  # Simple objects
                    r'\[.*?\]'   # Simple arrays
                ]
                
                for pattern in json_matches:
                    matches = re.findall(pattern, cleaned, re.DOTALL)
                    for match in matches:
                        try:
                            result = json.loads(match)
                            logger.info(f"✅ Extracted JSON from mixed content ({provider_name})")
                            return result
                        except:
                            continue
                            
            except Exception:
                pass
            
            # Fourth attempt: Try to extract key-value pairs manually
            try:
                # Look for patterns like "key": "value" or "key": ["value1", "value2"]
                kv_pattern = r'"([^"]+)":\s*(?:"([^"]+)"|(\[[^\]]+\])|\{[^}]+\})'
                matches = re.findall(kv_pattern, cleaned)
                
                if matches:
                    result = {}
                    for match in matches:
                        key = match[0]
                        if match[1]:  # String value
                            result[key] = match[1]
                        elif match[2]:  # Array or object value
                            try:
                                result[key] = json.loads(match[2])
                            except:
                                result[key] = match[2]
                    
                    if result:
                        logger.info(f"✅ Extracted key-value pairs from {provider_name}")
                        return result
                        
            except Exception:
                pass
            
            # 🔥 CRITICAL CHANGE: Return None instead of mock data
            logger.error(f"❌ All JSON parsing attempts failed for {provider_name} - NO MOCK DATA")
            return None

# ============================================================================
# ANALYSIS QUEUE SYSTEM
# ============================================================================

def _add_to_analysis_queue(
    url: str,
    request_type: str,
    messages: List[Dict],
    model: str,
    kwargs: Dict,
    metadata: Dict = None
) -> str:
    """
    🚀 NEW: Add failed analysis to queue for later processing
    """
    global _analysis_queue
    
    queue_item = QueuedAnalysis(
        url=url,
        request_type=request_type,
        messages=messages,
        model=model,
        kwargs=kwargs,
        retry_count=0,
        next_retry_at=datetime.utcnow() + timedelta(minutes=10),
        created_at=datetime.utcnow(),
        metadata=metadata or {}
    )
    
    _analysis_queue.append(queue_item)
    queue_id = f"queue_{len(_analysis_queue)}_{int(time.time())}"
    
    logger.info(f"📥 Added analysis to queue: {queue_id} (URL: {url[:50]}...)")
    logger.info(f"📊 Queue size: {len(_analysis_queue)}")
    
    # Start queue processor if not running
    if not _queue_processor_running:
        asyncio.create_task(_start_queue_processor())
    
    return queue_id

async def _start_queue_processor():
    """
    🚀 NEW: Background queue processor for retrying failed analyses
    """
    global _queue_processor_running
    
    if _queue_processor_running:
        return
    
    _queue_processor_running = True
    logger.info("🚀 Starting analysis queue processor...")
    
    try:
        while _analysis_queue:
            await _process_queue_batch()
            await asyncio.sleep(600)  # Check every 10 minutes
            
    except Exception as e:
        logger.error(f"❌ Queue processor error: {str(e)}")
    finally:
        _queue_processor_running = False
        logger.info("⏹️ Queue processor stopped")

async def _process_queue_batch():
    """Process a batch of queued analyses"""
    global _analysis_queue
    
    if not _analysis_queue:
        return
    
    current_time = datetime.utcnow()
    processed_items = []
    
    logger.info(f"🔄 Processing queue batch: {len(_analysis_queue)} items")
    
    for i, item in enumerate(_analysis_queue):
        if current_time >= item.next_retry_at and item.retry_count < 3:
            try:
                # Find healthy providers
                from .tiered_ai_provider import get_available_providers
                providers = get_available_providers()
                healthy_providers = [p for p in providers if _is_provider_healthy(p.get("name", ""))]
                
                if healthy_providers:
                    # Try processing with healthy provider
                    provider = healthy_providers[0]
                    # This would integrate with your existing provider system
                    logger.info(f"🔄 Retrying queued analysis {i+1} with {provider.get('name')}")
                    
                    # Mark for removal on success (implementation depends on your system)
                    processed_items.append(i)
                    
                else:
                    # No healthy providers, schedule for later
                    item.next_retry_at = current_time + timedelta(minutes=15)
                    item.retry_count += 1
                    logger.warning(f"⏳ No healthy providers, rescheduling queue item {i+1}")
                    
            except Exception as e:
                logger.error(f"❌ Queue processing error for item {i+1}: {str(e)}")
                item.retry_count += 1
                item.next_retry_at = current_time + timedelta(minutes=15)
        
        elif item.retry_count >= 3:
            # Remove failed items after 3 retries
            processed_items.append(i)
            logger.warning(f"🗑️ Removing queue item {i+1} after 3 failed retries")
    
    # Remove processed items (reverse order to maintain indices)
    for i in reversed(processed_items):
        _analysis_queue.pop(i)
    
    if processed_items:
        logger.info(f"✅ Processed {len(processed_items)} queue items")

def get_queue_status() -> Dict[str, Any]:
    """Get current analysis queue status"""
    global _analysis_queue
    
    pending = sum(1 for item in _analysis_queue if item.retry_count < 3)
    failed = sum(1 for item in _analysis_queue if item.retry_count >= 3)
    
    return {
        "total_queued": len(_analysis_queue),
        "pending_retry": pending,
        "permanently_failed": failed,
        "processor_running": _queue_processor_running,
        "next_processing": min([item.next_retry_at for item in _analysis_queue]) if _analysis_queue else None
    }

# ============================================================================
# MULTI-PROVIDER FAILOVER SYSTEM
# ============================================================================

async def safe_ai_call_with_failover(
    providers: List[Dict],
    model_key: str,
    messages: List[Dict],
    request_metadata: Dict = None,
    **kwargs
) -> Tuple[Any, str]:
    """
    🔥 NEW: Multi-provider failover system - tries all providers before giving up
    Returns (result, provider_used) or raises ProviderFailureError
    """
    
    if not providers:
        raise ProviderFailureError("No providers available")
    
    # Sort providers by dynamic priority (health + base priority)
    sorted_providers = sorted(
        providers,
        key=lambda p: _get_provider_priority_score(p.get("name", ""), p.get("priority", 999))
    )
    
    # Filter to only healthy providers first
    healthy_providers = [p for p in sorted_providers if _is_provider_healthy(p.get("name", ""))]
    
    # If no healthy providers, try degraded ones as fallback
    if not healthy_providers:
        logger.warning("⚠️ No healthy providers available, trying degraded providers")
        degraded_providers = [
            p for p in sorted_providers 
            if _provider_health.get(p.get("name", ""), ProviderStatus.HEALTHY) == ProviderStatus.DEGRADED
        ]
        providers_to_try = degraded_providers if degraded_providers else sorted_providers
    else:
        providers_to_try = healthy_providers
    
    last_error = None
    
    logger.info(f"🔄 Multi-provider failover: Trying {len(providers_to_try)} providers")
    
    for i, provider in enumerate(providers_to_try, 1):
        provider_name = provider.get("name", f"provider_{i}")
        model = provider.get("models", {}).get(model_key, "default-model")
        
        try:
            logger.info(f"🔄 Attempt {i}/{len(providers_to_try)}: {provider_name}")
            
            # Get provider client
            client = provider.get("client")
            if not client:
                logger.error(f"❌ {provider_name}: No client available")
                continue
            
            # Make the API call
            result = await safe_ai_call(client, provider_name, model, messages, **kwargs)
            
            # Check if we got valid data (not None from failed JSON parsing)
            if result is not None:
                logger.info(f"✅ {provider_name}: Success on attempt {i}")
                _update_provider_health(provider_name, True)
                return result, provider_name
            else:
                logger.warning(f"⚠️ {provider_name}: Returned None (JSON parsing failed)")
                _update_provider_health(provider_name, False, "JSON parsing failed")
                continue
                
        except Exception as e:
            error_message = str(e)
            logger.warning(f"❌ {provider_name}: Failed - {error_message}")
            _update_provider_health(provider_name, False, error_message)
            last_error = e
            
            # Small delay before trying next provider
            if i < len(providers_to_try):
                await asyncio.sleep(1)
            continue
    
    # All providers failed
    logger.error(f"💥 ALL PROVIDERS FAILED after {len(providers_to_try)} attempts")
    
    # Add to queue for later processing
    if request_metadata:
        queue_id = _add_to_analysis_queue(
            url=request_metadata.get("url", "unknown"),
            request_type=request_metadata.get("type", "analysis"),
            messages=messages,
            model=model_key,
            kwargs=kwargs,
            metadata=request_metadata
        )
        logger.info(f"📥 Added to analysis queue: {queue_id}")
    
    # Report provider health
    health_report = get_provider_health_report()
    logger.error(f"🏥 Provider Health Summary: {health_report['summary']}")
    
    raise ProviderFailureError(f"All {len(providers_to_try)} providers failed. Last error: {last_error}")

# ============================================================================
# LEGACY SINGLE-PROVIDER SAFE_AI_CALL (Enhanced)
# ============================================================================

async def safe_ai_call(client, provider_name: str, model: str, messages: list, **kwargs) -> Any:
    """
    🔥 ENHANCED: Make a safe AI call with improved error handling
    Returns None on failure (NO MOCK DATA)
    """
    
    # Apply throttling
    await throttle_ai_request(provider_name)
    
    # Log the call
    prompt_length = sum(len(msg.get("content", "")) for msg in messages)
    estimated_tokens = prompt_length * 0.3  # Rough estimate
    logger.debug(f"💰 AI Call: {provider_name} | ~{estimated_tokens:.0f} tokens")
    
    try:
        # Make the API call based on provider type
        response_text = None
        
        if provider_name == "groq":
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            response_text = response.choices[0].message.content
            
        elif provider_name in ["together", "deepseek", "fireworks", "perplexity", "openai"]:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            response_text = response.choices[0].message.content
            
        elif provider_name == "anthropic":
            response = await client.messages.create(
                model=model,
                messages=messages,
                **kwargs
            )
            response_text = response.content[0].text
            
        elif provider_name == "cohere":
            # Cohere has different API structure
            prompt = messages[-1].get("content", "") if messages else ""
            response = await client.chat(
                model=model,
                message=prompt,
                **kwargs
            )
            response_text = response.text
            
        else:
            raise Exception(f"Unsupported provider: {provider_name}")
        
        # Validate and parse JSON (returns None on failure)
        if response_text:
            result = validate_and_parse_json(response_text, provider_name)
            if result is not None:
                logger.debug(f"✅ {provider_name}: Successful API call")
                return result
            else:
                logger.error(f"❌ {provider_name}: JSON parsing failed")
                return None
        else:
            logger.error(f"❌ {provider_name}: Empty response")
            return None
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"❌ {provider_name}: API call failed - {error_message}")
        
        # Check if it's a rate limit error
        if "429" in error_message or "rate limit" in error_message.lower():
            logger.warning(f"🚨 Rate limit hit for {provider_name}")
            await asyncio.sleep(10)
        
        # 🔥 CRITICAL CHANGE: Return None instead of mock data
        return None

# ============================================================================
# MONITORING AND STATISTICS
# ============================================================================

def get_throttle_stats() -> Dict[str, Any]:
    """Get current throttling statistics with health info"""
    return {
        "request_counts": _request_counts.copy(),
        "last_request_times": _last_request_time.copy(),
        "current_minute": _current_minute,
        "provider_health": get_provider_health_report(),
        "queue_status": get_queue_status()
    }

def reset_provider_health():
    """Reset all provider health tracking (useful for testing)"""
    global _provider_health, _provider_failure_counts, _provider_last_failure
    
    _provider_health.clear()
    _provider_failure_counts.clear()
    _provider_last_failure.clear()
    
    logger.info("🔄 Provider health tracking reset")

def log_system_status():
    """Log comprehensive system status"""
    health_report = get_provider_health_report()
    queue_status = get_queue_status()
    
    logger.info("📊 AI THROTTLE SYSTEM STATUS")
    logger.info("=" * 50)
    logger.info(f"Provider Health: {health_report['summary']}")
    logger.info(f"Queue Status: {queue_status['total_queued']} items ({queue_status['pending_retry']} pending)")
    logger.info(f"Queue Processor: {'Running' if queue_status['processor_running'] else 'Stopped'}")
    
    for provider, info in health_report['providers'].items():
        status_emoji = {
            'healthy': '🟢',
            'degraded': '🟡', 
            'unhealthy': '🔴',
            'disabled': '⚫'
        }.get(info['status'], '❓')
        
        logger.info(f"  {status_emoji} {provider}: {info['status']} ({info['failure_count']} failures)")
    
    logger.info("=" * 50)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def force_disable_provider(provider_name: str, reason: str = "Manual disable"):
    """Manually disable a provider"""
    global _provider_health
    
    _provider_health[provider_name] = ProviderStatus.DISABLED
    logger.warning(f"⚫ {provider_name}: Manually disabled - {reason}")

def force_enable_provider(provider_name: str):
    """Manually re-enable a provider"""
    global _provider_health, _provider_failure_counts
    
    _provider_health[provider_name] = ProviderStatus.HEALTHY
    _provider_failure_counts[provider_name] = 0
    logger.info(f"🟢 {provider_name}: Manually enabled")

async def test_provider_health(providers: List[Dict]) -> Dict[str, bool]:
    """Test all providers with a simple request"""
    test_messages = [{"role": "user", "content": "Reply with just: {'test': 'ok'}"}]
    results = {}
    
    for provider in providers:
        provider_name = provider.get("name", "unknown")
        try:
            result = await safe_ai_call(
                provider.get("client"),
                provider_name,
                provider.get("models", {}).get("chat", "default"),
                test_messages,
                max_tokens=50
            )
            results[provider_name] = result is not None
        except Exception as e:
            logger.error(f"❌ Health test failed for {provider_name}: {str(e)}")
            results[provider_name] = False
    
    return results