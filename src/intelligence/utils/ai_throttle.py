# src/intelligence/utils/ai_throttle.py
"""
AI Request Throttling and JSON Validation Utility
Simple importable module to prevent rate limits and handle JSON parsing
FIXED: Better JSON parsing, more aggressive rate limiting, robust error handling
"""
import asyncio
import time
import json
import logging
import re
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
    FIXED: More aggressive rate limiting to prevent 429 errors
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
    
    # FIXED: More aggressive limits to prevent rate limit errors
    limits = {
        "groq": {"max_per_minute": 15, "min_delay": 4.0},      # REDUCED: 15/min, 4s between (was 25/2.5s)
        "together": {"max_per_minute": 60, "min_delay": 1.0},   # REDUCED: 60/min, 1s between
        "deepseek": {"max_per_minute": 40, "min_delay": 1.5},   # REDUCED: 40/min, 1.5s between
        "anthropic": {"max_per_minute": 30, "min_delay": 2.0},  # REDUCED: 30/min, 2s between
        "openai": {"max_per_minute": 80, "min_delay": 0.8}      # REDUCED: 80/min, 0.8s between
    }
    
    provider_limit = limits.get(provider_name, {"max_per_minute": 10, "min_delay": 6.0})
    
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
    FIXED: More robust JSON parsing with better fallbacks
    """
    
    if not response_text or not response_text.strip():
        logger.error(f"❌ Empty response from {provider_name}")
        return _create_fallback_response("Empty AI response", provider_name)
    
    # Clean the response text first
    cleaned = response_text.strip()
    
    # First attempt: Direct JSON parsing
    try:
        return json.loads(cleaned)
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
            parsed = json.loads(cleaned)
            logger.info(f"✅ Fixed JSON response from {provider_name}")
            return parsed
            
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
                            parsed = json.loads(match)
                            logger.info(f"✅ Extracted JSON from mixed content ({provider_name})")
                            return parsed
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
            
            # Final fallback: Return structured error with raw content
            logger.error(f"❌ All JSON parsing attempts failed for {provider_name}")
            return _create_fallback_response("Invalid JSON response", provider_name, response_text)

def _create_fallback_response(error_message: str, provider_name: str, raw_response: str = "") -> Dict[str, Any]:
    """Create a structured fallback response when JSON parsing fails"""
    
    # Try to extract any useful information from the raw response
    fallback_data = {}
    
    if raw_response:
        # Look for any list-like content
        lines = raw_response.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('{') and not line.startswith('['):
                # Try to extract useful content from plain text responses
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip().lower().replace(' ', '_')
                        value = parts[1].strip()
                        if key and value:
                            fallback_data[key] = [value]
    
    # If we couldn't extract anything useful, provide generic fallback
    if not fallback_data:
        fallback_data = {
            "generated_content": ["AI response generated but could not be parsed as JSON"],
            "fallback_data": ["Generic marketing intelligence placeholder"],
            "processing_note": ["Response required manual processing"]
        }
    
    return {
        "error": error_message,
        "raw_response": raw_response[:200] + "..." if len(raw_response) > 200 else raw_response,
        "fallback": True,
        "provider": provider_name,
        "fallback_data": fallback_data,
        "timestamp": time.time()
    }

async def safe_ai_call(client, provider_name: str, model: str, messages: list, **kwargs) -> Any:
    """
    Make a safe AI call with throttling and JSON validation
    FIXED: Better error handling and more robust response processing
    """
    
    # Apply throttling
    await throttle_ai_request(provider_name)
    
    # Log the call
    prompt_length = sum(len(msg.get("content", "")) for msg in messages)
    estimated_tokens = prompt_length * 0.3  # Rough estimate
    logger.info(f"💰 AI Call: {provider_name} | ~{estimated_tokens:.0f} tokens")
    
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
        
        # Validate and parse JSON
        if response_text:
            return validate_and_parse_json(response_text, provider_name)
        else:
            logger.error(f"❌ Empty response from {provider_name}")
            return _create_fallback_response("Empty response from AI provider", provider_name)
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"❌ AI call failed for {provider_name}: {error_message}")
        
        # Check if it's a rate limit error
        if "429" in error_message or "rate limit" in error_message.lower():
            logger.warning(f"🚨 Rate limit hit for {provider_name}, will retry with longer delay")
            # Add extra delay for rate limited providers
            await asyncio.sleep(10)
        
        # Return structured error with fallback content
        return _create_fallback_response(f"AI call failed: {error_message}", provider_name)

def get_throttle_stats() -> Dict[str, Any]:
    """Get current throttling statistics"""
    return {
        "request_counts": _request_counts.copy(),
        "last_request_times": _last_request_time.copy(),
        "current_minute": _current_minute
    }