"""
File: src/intelligence/utils/amplifier_service.py
Amplifier Service - Intelligence amplification utilities
Extracted from main routes.py for better organization
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try to import amplifier with fallback handling
try:
    from src.intelligence.amplifier import (
        IntelligenceAmplificationService, 
        is_amplifier_available, 
        get_amplifier_status
    )
    AMPLIFIER_AVAILABLE = is_amplifier_available()
    logger.info(f"✅ SUCCESS: Intelligence Amplifier imported - Status: {get_amplifier_status()['status']}")
except ImportError as e:
    logger.warning(f"⚠️ AMPLIFIER WARNING: Intelligence Amplifier package not available: {str(e)}")
    AMPLIFIER_AVAILABLE = False


class FallbackAmplificationService:
    """Fallback amplification service when dependencies are missing"""
    
    async def process_sources(self, sources, preferences=None):
        return {
            "intelligence_data": sources[0] if sources else {},
            "summary": {
                "total": len(sources) if sources else 0,
                "successful": 0,
                "note": "Amplifier package not available"
            }
        }


def get_amplifier_service() -> Optional[object]:
    """Get amplifier service instance or None if not available"""
    if not AMPLIFIER_AVAILABLE:
        logger.warning("⚠️ Amplifier service not available - using fallback")
        return None
    
    try:
        return IntelligenceAmplificationService()
    except Exception as e:
        logger.error(f"❌ Failed to initialize amplifier service: {str(e)}")
        return None


def get_amplifier_status() -> Dict[str, Any]:
    """Get amplifier system status"""
    if not AMPLIFIER_AVAILABLE:
        return {
            "status": "unavailable",
            "available": False,
            "error": "Amplifier dependencies not installed",
            "capabilities": {},
            "recommendations": [
                "Install amplifier dependencies",
                "Check amplifier package configuration"
            ]
        }
    
    try:
        # Try to import the actual status function
        from src.intelligence.amplifier import get_amplifier_status as get_status
        return get_status()
    except ImportError:
        return {
            "status": "partial",
            "available": True,
            "error": "Status function not available",
            "capabilities": {
                "basic_amplification": True,
                "scientific_enhancement": False,
                "credibility_boost": False
            },
            "recommendations": ["Update amplifier package to latest version"]
        }
    except Exception as e:
        return {
            "status": "error",
            "available": False,
            "error": str(e),
            "capabilities": {},
            "recommendations": ["Check amplifier service configuration"]
        }


def test_amplifier_functionality() -> Dict[str, Any]:
    """Test amplifier functionality"""
    test_results = {
        "amplifier_available": AMPLIFIER_AVAILABLE,
        "test_results": {},
        "overall_status": "unknown"
    }
    
    if not AMPLIFIER_AVAILABLE:
        test_results["overall_status"] = "unavailable"
        test_results["error"] = "Amplifier dependencies not available"
        return test_results
    
    try:
        # Test amplifier initialization
        amplifier = get_amplifier_service()
        test_results["test_results"]["initialization"] = {
            "success": amplifier is not None,
            "class_name": type(amplifier).__name__ if amplifier else "None"
        }
        
        # Test basic capabilities
        if amplifier:
            test_results["test_results"]["capabilities"] = {
                "has_process_sources": hasattr(amplifier, 'process_sources'),
                "methods_available": [method for method in dir(amplifier) if not method.startswith('_')]
            }
            test_results["overall_status"] = "available"
        else:
            test_results["overall_status"] = "failed"
        
    except Exception as e:
        test_results["test_results"]["error"] = str(e)
        test_results["overall_status"] = "error"
    
    return test_results


async def amplify_intelligence_data(
    intelligence_data: Dict[str, Any], 
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Amplify intelligence data with enhanced insights"""
    
    amplifier = get_amplifier_service()
    
    if not amplifier:
        logger.warning("⚠️ Amplifier not available, returning original data")
        intelligence_data["amplification_metadata"] = {
            "amplification_applied": False,
            "amplification_available": False,
            "note": "Amplifier service not available"
        }
        return intelligence_data
    
    try:
        # Prepare sources for amplification
        sources = [{
            "type": "intelligence_data",
            "data": intelligence_data
        }]
        
        # Set default preferences if not provided
        if not preferences:
            preferences = {
                "enhance_scientific_backing": True,
                "boost_credibility": True,
                "competitive_analysis": True
            }
        
        # Run amplification
        amplification_result = await amplifier.process_sources(
            sources=sources,
            preferences=preferences
        )
        
        # Get enriched intelligence
        enriched_intelligence = amplification_result.get("intelligence_data", intelligence_data)
        amplification_summary = amplification_result.get("summary", {})
        
        # Add amplification metadata
        enriched_intelligence["amplification_metadata"] = {
            "amplification_applied": True,
            "amplification_summary": amplification_summary,
            "preferences_used": preferences,
            "amplification_timestamp": "2025-01-01T00:00:00Z"  # You'd use actual timestamp
        }
        
        logger.info("✅ Intelligence data amplified successfully")
        return enriched_intelligence
        
    except Exception as e:
        logger.error(f"❌ Amplification failed: {str(e)}")
        intelligence_data["amplification_metadata"] = {
            "amplification_applied": False,
            "amplification_error": str(e),
            "fallback_to_original": True
        }
        return intelligence_data


def get_amplification_capabilities() -> Dict[str, Any]:
    """Get available amplification capabilities"""
    
    if not AMPLIFIER_AVAILABLE:
        return {
            "available": False,
            "capabilities": {},
            "requirements": [
                "Install amplifier package",
                "Configure amplifier dependencies"
            ]
        }
    
    return {
        "available": True,
        "capabilities": {
            "scientific_enhancement": {
                "description": "Add scientific backing to claims",
                "available": True
            },
            "credibility_boost": {
                "description": "Enhance credibility with authority sources",
                "available": True
            },
            "competitive_analysis": {
                "description": "Advanced competitive intelligence",
                "available": True
            },
            "psychological_profiling": {
                "description": "Enhanced psychological insights",
                "available": True
            },
            "content_optimization": {
                "description": "Optimize content for better performance",
                "available": True
            }
        },
        "preferences": {
            "enhance_scientific_backing": "bool - Add scientific support",
            "boost_credibility": "bool - Enhance credibility",
            "competitive_analysis": "bool - Deep competitive insights",
            "psychological_depth": "str - low/medium/high",
            "content_optimization": "bool - Optimize for conversion"
        }
    }


class AmplificationManager:
    """Manager for handling amplification operations"""
    
    def __init__(self):
        self.amplifier = get_amplifier_service()
        self.available = self.amplifier is not None
    
    async def amplify_source(
        self, 
        source_data: Dict[str, Any], 
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Amplify a single intelligence source"""
        
        if not self.available:
            return self._add_unavailable_metadata(source_data)
        
        try:
            return await amplify_intelligence_data(source_data, preferences)
        except Exception as e:
            logger.error(f"❌ Source amplification failed: {str(e)}")
            return self._add_error_metadata(source_data, e)
    
    async def batch_amplify(
        self, 
        sources: list, 
        preferences: Dict[str, Any] = None
    ) -> list:
        """Amplify multiple sources in batch"""
        
        results = []
        
        for source in sources:
            try:
                amplified = await self.amplify_source(source, preferences)
                results.append(amplified)
            except Exception as e:
                logger.error(f"❌ Batch amplification failed for source: {str(e)}")
                results.append(self._add_error_metadata(source, e))
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get amplification manager status"""
        return {
            "available": self.available,
            "amplifier_class": type(self.amplifier).__name__ if self.amplifier else None,
            "capabilities": get_amplification_capabilities(),
            "test_results": test_amplifier_functionality()
        }
    
    def _add_unavailable_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata indicating amplification is unavailable"""
        data["amplification_metadata"] = {
            "amplification_applied": False,
            "amplification_available": False,
            "note": "Amplification service not available"
        }
        return data
    
    def _add_error_metadata(self, data: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Add metadata indicating amplification failed"""
        data["amplification_metadata"] = {
            "amplification_applied": False,
            "amplification_error": str(error),
            "fallback_to_original": True
        }
        return data