# src/intelligence/utils/ai_throttle.py
"""
AI Request Throttling and JSON Validation Utility
Simple importable module to prevent rate limits and handle JSON parsing
"""
import asyncio
import time
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Global rate limiting state
_last_request_time = {}
_request_counts = {}
_current_minute = 0

async def throttle_ai_request(provider_name: str) -> None:
    """
    Simple throttling to prevent rate limits
    Call this before every AI request
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
    
    # Provider-specific limits (conservative to avoid rate limits)
    limits = {
        "groq": {"max_per_minute": 25, "min_delay": 2.5},      # Groq: 25/min, 2.5s between
        "together": {"max_per_minute": 80, "min_delay": 0.8},   # Together: 80/min, 0.8s between  
        "deepseek": {"max_per_minute": 50, "min_delay": 1.2},   # Deepseek: 50/min, 1.2s between
        "anthropic": {"max_per_minute": 40, "min_delay": 1.5},  # Anthropic: 40/min, 1.5s between
        "openai": {"max_per_minute": 100, "min_delay": 0.6}     # OpenAI: 100/min, 0.6s between
    }
    
    provider_limit = limits.get(provider_name, {"max_per_minute": 20, "min_delay": 3.0})
    
    # Check if we're at the rate limit
    if _request_counts[provider_name] >= provider_limit["max_per_minute"]:
        wait_time = 60 - (current_time % 60)  # Wait until next minute
        logger.warning(f"⏳ {provider_name}: Rate limit reached, waiting {wait_time:.1f}s")
        await asyncio.sleep(wait_time)
        _request_counts[provider_name] = 0
    
    # Ensure minimum delay between requests
    time_since_last = current_time - _last_request_time[provider_name]
    min_delay = provider_limit["min_delay"]
    
    if time_since_last < min_delay:
        delay = min_delay - time_since_last
        logger.info(f"⏱️ {provider_name}: Throttling {delay:.1f}s")
        await asyncio.sleep(delay)
    
    # Update tracking
    _request_counts[provider_name] += 1
    _last_request_time[provider_name] = time.time()

def validate_and_parse_json(response_text: str, provider_name: str = "AI") -> Any:
    """
    Validate and parse JSON response from AI
    Handles common JSON parsing issues automatically
    """
    
    if not response_text or not response_text.strip():
        logger.error(f"❌ Empty response from {provider_name}")
        return {"error": "Empty AI response", "fallback": True}
    
    # First attempt: Direct JSON parsing
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.warning(f"⚠️ JSON parse error from {provider_name}: {str(e)}")
        
        # Second attempt: Fix common issues
        try:
            cleaned = response_text.strip()
            
            # Remove markdown code blocks
            if cleaned.startswith("```"):
                lines = cleaned.split('\n')
                if lines[0].strip().startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip().startswith("```"):
                    lines = lines[:-1]
                cleaned = '\n'.join(lines).strip()
            
            # Fix common JSON issues
            import re
            cleaned = re.sub(r',\s*}', '}', cleaned)  # Remove trailing commas before }
            cleaned = re.sub(r',\s*]', ']', cleaned)  # Remove trailing commas before ]
            
            # Try parsing the cleaned version
            parsed = json.loads(cleaned)
            logger.info(f"✅ Fixed JSON response from {provider_name}")
            return parsed
            
        except json.JSONDecodeError:
            logger.error(f"❌ Could not fix JSON from {provider_name}")
            
            # Third attempt: Extract JSON from mixed content
            try:
                # Look for JSON objects in the text
                json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if json_match:
                    json_text = json_match.group()
                    parsed = json.loads(json_text)
                    logger.info(f"✅ Extracted JSON from mixed content ({provider_name})")
                    return parsed
            except:
                pass
            
            # Final fallback: Return structured error
            return {
                "error": "Invalid JSON response",
                "raw_response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                "fallback": True,
                "provider": provider_name
            }

async def safe_ai_call(client, provider_name: str, model: str, messages: list, **kwargs) -> Any:
    """
    Make a safe AI call with throttling and JSON validation
    Universal function that works with any provider
    """
    
    # Apply throttling
    await throttle_ai_request(provider_name)
    
    # Log the call
    prompt_length = sum(len(msg.get("content", "")) for msg in messages)
    estimated_tokens = prompt_length * 0.3  # Rough estimate
    logger.info(f"💰 AI Call: {provider_name} | ~{estimated_tokens:.0f} tokens")
    
    try:
        # Make the API call based on provider type
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
        
        # Validate and parse JSON
        return validate_and_parse_json(response_text, provider_name)
        
    except Exception as e:
        logger.error(f"❌ AI call failed for {provider_name}: {str(e)}")
        
        # Return structured error
        return {
            "error": str(e),
            "provider": provider_name,
            "fallback": True,
            "timestamp": time.time()
        }

def get_throttle_stats() -> Dict[str, Any]:
    """Get current throttling statistics"""
    return {
        "request_counts": _request_counts.copy(),
        "last_request_times": _last_request_time.copy(),
        "current_minute": _current_minute
    }