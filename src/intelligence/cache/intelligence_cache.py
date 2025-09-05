# =====================================
# File: src/intelligence/cache/intelligence_cache.py
# =====================================

"""
Intelligent caching system for analysis results and research data.

Provides multi-tier caching with automatic cache invalidation,
deduplication, and cost optimization for AI operations.
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from src.core.shared.decorators import log_execution_time
from src.core.health.metrics import record_cache_hit, record_cache_miss

logger = logging.getLogger(__name__)


class IntelligenceCache:
    """Multi-tier cache for intelligence operations."""
    
    def __init__(self):
        # In-memory caches with different TTLs
        self.analysis_cache = {}     # Analysis results (longer TTL)
        self.research_cache = {}     # Research data (medium TTL)
        self.provider_cache = {}     # AI provider responses (shorter TTL)
        
        # Cache configuration
        self.cache_ttls = {
            "analysis": 3600,      # 1 hour
            "research": 1800,      # 30 minutes
            "provider": 300,       # 5 minutes
        }
    
    @log_execution_time()
    def get_analysis_cache(self, url: str, user_id: str, analysis_method: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result."""
        cache_key = self._generate_analysis_key(url, user_id, analysis_method)
        
        cached_data = self._get_from_cache("analysis", cache_key)
        if cached_data:
            record_cache_hit()
            logger.debug(f"Analysis cache hit for {url}")
            return cached_data
        
        record_cache_miss()
        logger.debug(f"Analysis cache miss for {url}")
        return None
    
    def set_analysis_cache(
        self, 
        url: str, 
        user_id: str, 
        analysis_method: str, 
        data: Dict[str, Any]
    ):
        """Cache analysis result."""
        cache_key = self._generate_analysis_key(url, user_id, analysis_method)
        self._set_to_cache("analysis", cache_key, data)
        logger.debug(f"Cached analysis result for {url}")
    
    def get_research_cache(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached research data."""
        cached_data = self._get_from_cache("research", content_hash)
        if cached_data:
            record_cache_hit()
            return cached_data
        
        record_cache_miss()
        return None
    
    def set_research_cache(self, content_hash: str, data: Dict[str, Any]):
        """Cache research data."""
        self._set_to_cache("research", content_hash, data)
    
    def get_provider_cache(self, provider: str, content_hash: str) -> Optional[str]:
        """Get cached AI provider response."""
        cache_key = f"{provider}:{content_hash}"
        cached_data = self._get_from_cache("provider", cache_key)
        if cached_data:
            record_cache_hit()
            return cached_data.get("response")
        
        record_cache_miss()
        return None
    
    def set_provider_cache(self, provider: str, content_hash: str, response: str):
        """Cache AI provider response."""
        cache_key = f"{provider}:{content_hash}"
        self._set_to_cache("provider", cache_key, {"response": response})
    
    def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for a user."""
        # Remove analysis cache entries for user
        keys_to_remove = [
            key for key in self.analysis_cache.keys() 
            if user_id in key
        ]
        
        for key in keys_to_remove:
            del self.analysis_cache[key]
        
        logger.info(f"Invalidated {len(keys_to_remove)} cache entries for user {user_id}")
    
    def cleanup_expired(self):
        """Remove expired cache entries."""
        current_time = time.time()
        
        # Clean each cache type
        for cache_type in ["analysis", "research", "provider"]:
            cache = getattr(self, f"{cache_type}_cache")
            expired_keys = [
                key for key, value in cache.items()
                if current_time > value.get("expires_at", 0)
            ]
            
            for key in expired_keys:
                del cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned {len(expired_keys)} expired {cache_type} cache entries")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache performance statistics."""
        return {
            "analysis_cache": {
                "size": len(self.analysis_cache),
                "ttl_seconds": self.cache_ttls["analysis"]
            },
            "research_cache": {
                "size": len(self.research_cache),
                "ttl_seconds": self.cache_ttls["research"]
            },
            "provider_cache": {
                "size": len(self.provider_cache),
                "ttl_seconds": self.cache_ttls["provider"]
            },
            "total_entries": len(self.analysis_cache) + len(self.research_cache) + len(self.provider_cache)
        }
    
    def _generate_analysis_key(self, url: str, user_id: str, analysis_method: str) -> str:
        """Generate cache key for analysis results."""
        key_data = f"{url}:{user_id}:{analysis_method}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_from_cache(self, cache_type: str, key: str) -> Optional[Dict[str, Any]]:
        """Get data from specified cache."""
        cache = getattr(self, f"{cache_type}_cache")
        
        if key not in cache:
            return None
        
        cached_data = cache[key]
        
        # Check expiration
        if time.time() > cached_data.get("expires_at", 0):
            del cache[key]
            return None
        
        return cached_data.get("data")
    
    def _set_to_cache(self, cache_type: str, key: str, data: Dict[str, Any]):
        """Set data to specified cache."""
        cache = getattr(self, f"{cache_type}_cache")
        ttl = self.cache_ttls[cache_type]
        
        cache[key] = {
            "data": data,
            "cached_at": time.time(),
            "expires_at": time.time() + ttl
        }


# Global cache instance
intelligence_cache = IntelligenceCache()