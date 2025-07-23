# src/intelligence/utils/ai_throttle.py
"""
AI Request Throttling and Provider Failover - FIXED VERSION
🔥 FIXED: Empty response handling for Groq
🔥 FIXED: JSON parsing errors completely resolved
⚡ ENHANCED: Provider health tracking
🎯 CRITICAL: Always returns structured data for analyzers
"""
import asyncio
import time
import json
import logging
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

# Global rate limiting state
_last_request_time = {}
_request_counts = {}
_current_minute = 0

# 🔥 NEW: Provider health tracking
_provider_health = {}
_provider_failure_counts = {}

class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DISABLED = "disabled"

# ============================================================================
# PROVIDER HEALTH TRACKING
# ============================================================================

def _update_provider_health(provider_name: str, success: bool, error_message: str = None) -> None:
    """Track provider health and automatically disable failing providers"""
    global _provider_health, _provider_failure_counts
    
    # Initialize tracking for new providers
    if provider_name not in _provider_health:
        _provider_health[provider_name] = ProviderStatus.HEALTHY
        _provider_failure_counts[provider_name] = 0
    
    if success:
        # Reset failure count on successful request
        _provider_failure_counts[provider_name] = max(0, _provider_failure_counts[provider_name] - 1)
        
        # Upgrade health status if recovering
        if _provider_health[provider_name] == ProviderStatus.DEGRADED and _provider_failure_counts[provider_name] == 0:
            _provider_health[provider_name] = ProviderStatus.HEALTHY
            logger.info(f"🟢 {provider_name}: Recovered to HEALTHY status")
            
    else:
        # Increment failure count
        _provider_failure_counts[provider_name] += 1
        
        # Check for payment/auth errors (immediate disable)
        if error_message and any(term in error_message.lower() for term in ['402', 'payment', 'insufficient', 'balance', 'billing', '401', 'unauthorized']):
            _provider_health[provider_name] = ProviderStatus.DISABLED
            logger.error(f"🔴 {provider_name}: DISABLED due to payment/auth error: {error_message}")
        elif _provider_failure_counts[provider_name] >= 3:
            _provider_health[provider_name] = ProviderStatus.UNHEALTHY
            logger.warning(f"🔴 {provider_name}: UNHEALTHY ({_provider_failure_counts[provider_name]} failures)")
        elif _provider_failure_counts[provider_name] >= 2:
            _provider_health[provider_name] = ProviderStatus.DEGRADED
            logger.warning(f"🟡 {provider_name}: DEGRADED ({_provider_failure_counts[provider_name]} failures)")

def _is_provider_healthy(provider_name: str) -> bool:
    """Check if provider is healthy enough to use"""
    status = _provider_health.get(provider_name, ProviderStatus.HEALTHY)
    return status in [ProviderStatus.HEALTHY, ProviderStatus.DEGRADED]

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
        
        report["providers"][provider_name] = {
            "status": status.value,
            "failure_count": failure_count,
            "is_usable": _is_provider_healthy(provider_name)
        }
        
        # Update summary
        report["summary"][status.value] += 1
    
    return report

# ============================================================================
# ENHANCED THROTTLING
# ============================================================================

async def throttle_ai_request(provider_name: str) -> None:
    """Enhanced throttling with provider health awareness"""
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
    
    # Rate limits based on provider health
    base_limits = {
        "groq": {"max_per_minute": 15, "min_delay": 4.0},
        "together": {"max_per_minute": 60, "min_delay": 1.0},
        "deepseek": {"max_per_minute": 40, "min_delay": 1.5},
        "anthropic": {"max_per_minute": 30, "min_delay": 2.0},
        "openai": {"max_per_minute": 80, "min_delay": 0.8}
    }
    
    provider_limit = base_limits.get(provider_name, {"max_per_minute": 10, "min_delay": 6.0})
    
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
# 🔥 FIXED JSON VALIDATION - Handles empty Groq responses properly
# ============================================================================

def validate_and_parse_json(response_text: str, provider_name: str = "AI") -> Any:
    """
    🔥 COMPLETELY FIXED: Handle empty responses from Groq and other providers
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
            if "```json" in cleaned:
                match = re.search(r'```json\s*(.*?)\s*```', cleaned, re.DOTALL)
                if match:
                    cleaned = match.group(1).strip()
            elif "```" in cleaned:
                match = re.search(r'```\s*(.*?)\s*```', cleaned, re.DOTALL)
                if match:
                    cleaned = match.group(1).strip()
            
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
# 🔥 NEW: STRUCTURED FALLBACK RESPONSES
# ============================================================================

def create_structured_fallback(provider_name: str, error_reason: str) -> Dict[str, Any]:
    """🔥 NEW: Create structured fallback when AI fails"""
    
    return {
        "success": False,
        "provider_used": provider_name,
        "error": error_reason,
        "fallback": True,
        "fallback_data": {
            "offer_intelligence": {
                "products": ["Product"],
                "pricing": [],
                "value_propositions": [f"{provider_name} analysis unavailable - using pattern analysis"],
                "insights": ["AI provider failed - manual review recommended"],
                "bonuses": [],
                "guarantees": []
            },
            "psychology_intelligence": {
                "emotional_triggers": [],
                "pain_points": ["AI analysis temporarily unavailable"],
                "target_audience": "General audience",
                "persuasion_techniques": []
            },
            "competitive_intelligence": {
                "opportunities": ["Manual competitive analysis recommended"],
                "gaps": [],
                "positioning": "Standard market approach",
                "advantages": [],
                "weaknesses": []
            },
            "content_intelligence": {
                "key_messages": ["Pattern-based analysis used"],
                "success_stories": [],
                "social_proof": [],
                "content_structure": f"{provider_name} analysis failed"
            },
            "brand_intelligence": {
                "tone_voice": "Professional",
                "messaging_style": "Direct",
                "brand_positioning": "Market competitor"
            }
        }
    }

def _get_provider_cost(provider_name: str) -> float:
    """Get cost per 1K tokens for provider"""
    costs = {
        "groq": 0.00027,
        "together": 0.00018,
        "deepseek": 0.00014,
        "openai": 0.030,
        "anthropic": 0.015,
        "cohere": 0.015
    }
    return costs.get(provider_name, 0.002)

def _extract_insights_from_text(text: str) -> Optional[Dict[str, Any]]:
    """🔥 NEW: Extract structured insights from raw text response"""
    
    if not text or len(text) < 50:
        return None
    
    try:
        # Look for key insights in the text
        lines = text.split('\n')
        insights = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for bullet points or structured content
            if any(line.startswith(marker) for marker in ['-', '•', '*', '1.', '2.', '3.']):
                insight = re.sub(r'^[-•*0-9.\s]+', '', line).strip()
                if len(insight) > 10:
                    insights.append(insight)
        
        if insights:
            return {
                "offer_intelligence": {
                    "products": ["Product"],
                    "pricing": [],
                    "value_propositions": insights[:3],
                    "insights": insights,
                    "bonuses": [],
                    "guarantees": []
                },
                "psychology_intelligence": {
                    "emotional_triggers": [],
                    "pain_points": ["Extracted from text analysis"],
                    "target_audience": "General audience",
                    "persuasion_techniques": insights[3:6] if len(insights) > 3 else []
                },
                "competitive_intelligence": {
                    "opportunities": insights[6:9] if len(insights) > 6 else ["Text-based analysis completed"],
                    "gaps": [],
                    "positioning": "Text-extracted insights",
                    "advantages": [],
                    "weaknesses": []
                },
                "content_intelligence": {
                    "key_messages": insights[:2] if insights else ["Text analysis completed"],
                    "success_stories": [],
                    "social_proof": [],
                    "content_structure": f"Extracted {len(insights)} insights from text"
                },
                "brand_intelligence": {
                    "tone_voice": "Professional",
                    "messaging_style": "Direct", 
                    "brand_positioning": "Text-based analysis"
                }
            }
    
    except Exception as e:
        logger.error(f"❌ Text insight extraction failed: {str(e)}")
    
    return None

# ============================================================================
# 🔥 FIXED SAFE_AI_CALL - Always returns structured data
# ============================================================================

async def safe_ai_call(client, provider_name: str, model: str, messages: list, **kwargs) -> Any:
    """
    🔥 ENHANCED: Make a safe AI call with structured fallback responses
    Always returns structured data (never None)
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
            # 🔥 CRITICAL FIX: Disable streaming and add timeout for Groq
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,  # CRITICAL: Disable streaming for Groq
                timeout=30,    # Add timeout
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
        
        # 🔥 CRITICAL: Check for empty response (common with Groq)
        if not response_text or not response_text.strip():
            logger.error(f"❌ {provider_name}: Empty response returned")
            _update_provider_health(provider_name, False, "Empty response")
            return create_structured_fallback(provider_name, "empty_response")
        
        # Validate and parse JSON
        result = validate_and_parse_json(response_text, provider_name)
        if result is not None:
            logger.debug(f"✅ {provider_name}: Successful API call")
            _update_provider_health(provider_name, True)
            
            # Return structured success response
            return {
                "success": True,
                "provider_used": provider_name,
                "response": result,
                "estimated_cost": _get_provider_cost(provider_name),
                "processing_time": 0  # Could add actual timing
            }
        else:
            logger.error(f"❌ {provider_name}: JSON parsing failed")
            _update_provider_health(provider_name, False, "JSON parsing failed")
            
            # 🔥 NEW: Try to extract insights from raw text
            text_insights = _extract_insights_from_text(response_text)
            if text_insights:
                logger.info(f"✅ {provider_name}: Extracted insights from text response")
                return {
                    "success": True,
                    "provider_used": provider_name,
                    "response": text_insights,
                    "estimated_cost": _get_provider_cost(provider_name),
                    "note": "Extracted from text due to JSON parsing failure"
                }
            else:
                return create_structured_fallback(provider_name, "json_parsing_failed")
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"❌ {provider_name}: API call failed - {error_message}")
        _update_provider_health(provider_name, False, error_message)
        
        # Check if it's a rate limit error
        if "429" in error_message or "rate limit" in error_message.lower():
            logger.warning(f"🚨 Rate limit hit for {provider_name}")
            await asyncio.sleep(10)
            return create_structured_fallback(provider_name, "rate_limit")
        
        # 🔥 CRITICAL CHANGE: Return structured fallback instead of None
        return create_structured_fallback(provider_name, error_message)

# ============================================================================
# MONITORING AND STATISTICS
# ============================================================================

def get_throttle_stats() -> Dict[str, Any]:
    """Get current throttling statistics with health info"""
    return {
        "request_counts": _request_counts.copy(),
        "last_request_times": _last_request_time.copy(),
        "current_minute": _current_minute,
        "provider_health": get_provider_health_report()
    }

def reset_provider_health():
    """Reset all provider health tracking (useful for testing)"""
    global _provider_health, _provider_failure_counts
    
    _provider_health.clear()
    _provider_failure_counts.clear()
    
    logger.info("🔄 Provider health tracking reset")

def log_system_status():
    """Log comprehensive system status"""
    health_report = get_provider_health_report()
    
    logger.info("📊 AI THROTTLE SYSTEM STATUS")
    logger.info("=" * 50)
    logger.info(f"Provider Health: {health_report['summary']}")
    
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