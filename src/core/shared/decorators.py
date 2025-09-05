# =====================================
# File: src/core/shared/decorators.py
# =====================================

"""
Common decorators for CampaignForge application.

Provides reusable decorators for retry logic, rate limiting,
caching, and performance monitoring.
"""

import functools
import time
import asyncio
import logging
from typing import Any, Callable, Dict, Optional, Union
import hashlib
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Simple in-memory cache for demonstration
_cache: Dict[str, Dict[str, Any]] = {}


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Retry decorator for handling transient failures.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry on
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries + 1} attempts: {e}")
                        raise
                    
                    logger.warning(f"Function {func.__name__} failed on attempt {attempt + 1}: {e}. Retrying in {current_delay}s...")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor
            
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries + 1} attempts: {e}")
                        raise
                    
                    logger.warning(f"Function {func.__name__} failed on attempt {attempt + 1}: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
            
            raise last_exception
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def rate_limit(calls: int = 100, period: int = 60):
    """
    Simple rate limiting decorator.
    
    Args:
        calls: Number of calls allowed
        period: Time period in seconds
    """
    call_times = []
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove old calls outside the period
            cutoff = now - period
            call_times[:] = [t for t in call_times if t > cutoff]
            
            # Check if rate limit exceeded
            if len(call_times) >= calls:
                raise Exception(f"Rate limit exceeded: {calls} calls per {period} seconds")
            
            # Record this call
            call_times.append(now)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def cache_result(ttl: int = 300, key_func: Optional[Callable] = None):
    """
    Simple caching decorator with TTL.
    
    Args:
        ttl: Time to live in seconds
        key_func: Function to generate cache key, defaults to using args/kwargs
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                key_data = {
                    "func": func.__name__,
                    "args": str(args),
                    "kwargs": str(sorted(kwargs.items()))
                }
                cache_key = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
            
            # Check cache
            if cache_key in _cache:
                entry = _cache[cache_key]
                if datetime.now() < entry["expires"]:
                    logger.debug(f"Cache miss for {func.__name__}, result cached")
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def log_execution_time(logger_name: Optional[str] = None):
    """
    Decorator to log function execution time.
    
    Args:
        logger_name: Name of logger to use, defaults to function module
    """
    def decorator(func: Callable) -> Callable:
        func_logger = logging.getLogger(logger_name or func.__module__)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                func_logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                func_logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                func_logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                func_logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator