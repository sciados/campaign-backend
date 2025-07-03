"""
File: src/intelligence/utils/analyzer_factory.py
Analyzer Factory - Manages different types of analyzers
Extracted from routes.py for better organization
FIXED: Circular import issue resolved with lazy loading
"""
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# ✅ FIXED: Remove direct imports to avoid circular dependency
# Instead, use lazy loading when needed
ANALYZERS_AVAILABLE = False
INTELLIGENCE_AVAILABLE = False

def _lazy_import_analyzers():
    """Lazy import analyzers to avoid circular dependencies"""
    global ANALYZERS_AVAILABLE, INTELLIGENCE_AVAILABLE
    
    try:
        # ✅ FIXED: Import inside function to avoid circular import
        from src.intelligence.analyzers import (
            SalesPageAnalyzer, 
            DocumentAnalyzer, 
            WebAnalyzer, 
            EnhancedSalesPageAnalyzer, 
            VSLAnalyzer
        )
        
        ANALYZERS_AVAILABLE = True
        INTELLIGENCE_AVAILABLE = True
        logger.info("✅ SUCCESS: All intelligence analyzers imported successfully via lazy loading")
        
        return {
            'SalesPageAnalyzer': SalesPageAnalyzer,
            'DocumentAnalyzer': DocumentAnalyzer,
            'WebAnalyzer': WebAnalyzer,
            'EnhancedSalesPageAnalyzer': EnhancedSalesPageAnalyzer,
            'VSLAnalyzer': VSLAnalyzer
        }
        
    except ImportError as e:
        logger.warning(f"⚠️ IMPORT WARNING: Analyzers not available: {str(e)}")
        ANALYZERS_AVAILABLE = False
        INTELLIGENCE_AVAILABLE = False
        return None

class FallbackAnalyzer:
    """Fallback analyzer when dependencies are missing"""
    
    async def analyze(self, url: str) -> Dict[str, Any]:
        return {
            "offer_intelligence": {
                "products": ["Analysis requires missing dependencies"],
                "pricing": [],
                "bonuses": [],
                "guarantees": [],
                "value_propositions": ["Install aiohttp, beautifulsoup4, lxml to enable analysis"]
            },
            "psychology_intelligence": {
                "emotional_triggers": [],
                "pain_points": ["Dependency error - cannot analyze"],
                "target_audience": "Unknown",
                "persuasion_techniques": []
            },
            "competitive_intelligence": {
                "opportunities": ["Fix import dependencies to enable analysis"],
                "gaps": [],
                "positioning": "Analysis disabled",
                "advantages": [],
                "weaknesses": []
            },
            "content_intelligence": {
                "key_messages": [f"URL: {url}"],
                "success_stories": [],
                "social_proof": [],
                "content_structure": "Cannot analyze without dependencies"
            },
            "brand_intelligence": {
                "tone_voice": "Unknown",
                "messaging_style": "Unknown",
                "brand_positioning": "Unknown"
            },
            "campaign_suggestions": [
                "Install missing dependencies: pip install aiohttp beautifulsoup4 lxml",
                "Check Railway deployment logs for import errors",
                "Verify requirements.txt contains all dependencies"
            ],
            "source_url": url,
            "page_title": "Analysis Failed - Missing Dependencies",
            "analysis_timestamp": "2025-01-01T00:00:00Z",
            "confidence_score": 0.0,
            "raw_content": "",
            "error_message": "Missing dependencies: aiohttp, beautifulsoup4, lxml",
            "analysis_note": "Install required dependencies to enable URL analysis"
        }

def get_analyzer(analysis_type: str = "sales_page"):
    """
    Get appropriate analyzer based on type
    Returns fallback analyzer if dependencies are missing
    Uses lazy loading to avoid circular imports
    """
    
    # ✅ FIXED: Use lazy loading instead of module-level imports
    analyzers = _lazy_import_analyzers()
    
    if not analyzers:
        logger.warning("⚠️ Using fallback analyzer - dependencies missing")
        return FallbackAnalyzer()
    
    analyzer_map = {
        "sales_page": analyzers['SalesPageAnalyzer'],
        "website": analyzers['WebAnalyzer'],
        "document": analyzers['DocumentAnalyzer'],
        "enhanced_sales_page": analyzers['EnhancedSalesPageAnalyzer'],
        "vsl": analyzers['VSLAnalyzer'],
        "video_sales_letter": analyzers['VSLAnalyzer']
    }
    
    analyzer_class = analyzer_map.get(analysis_type, analyzers['SalesPageAnalyzer'])
    
    try:
        return analyzer_class()
    except Exception as e:
        logger.error(f"❌ Failed to initialize {analyzer_class.__name__}: {str(e)}")
        return FallbackAnalyzer()

def get_available_analyzers() -> Dict[str, Dict[str, Any]]:
    """Get list of available analyzers and their capabilities"""
    
    # Check if analyzers are available via lazy loading
    analyzers = _lazy_import_analyzers()
    analyzers_available = analyzers is not None
    
    analyzer_info = {
        "sales_page": {
            "name": "Sales Page Analyzer",
            "description": "Analyze sales pages and landing pages",
            "supported_formats": ["HTML", "URL"],
            "available": analyzers_available
        },
        "website": {
            "name": "Website Analyzer", 
            "description": "Analyze general websites and web content",
            "supported_formats": ["HTML", "URL"],
            "available": analyzers_available
        },
        "document": {
            "name": "Document Analyzer",
            "description": "Analyze uploaded documents",
            "supported_formats": ["PDF", "DOC", "TXT"],
            "available": analyzers_available
        },
        "enhanced_sales_page": {
            "name": "Enhanced Sales Page Analyzer",
            "description": "Advanced sales page analysis with deeper insights",
            "supported_formats": ["HTML", "URL"],
            "available": analyzers_available
        },
        "vsl": {
            "name": "Video Sales Letter Analyzer",
            "description": "Analyze video sales letters and video content",
            "supported_formats": ["URL", "Video"],
            "available": analyzers_available
        }
    }
    
    return analyzer_info

def test_analyzer_functionality() -> Dict[str, Any]:
    """Test analyzer functionality and return status"""
    
    # Use lazy loading to test
    analyzers = _lazy_import_analyzers()
    analyzers_available = analyzers is not None
    
    test_results = {
        "analyzers_available": analyzers_available,
        "test_results": {},
        "overall_status": "unknown"
    }
    
    if not analyzers_available:
        test_results["overall_status"] = "failed"
        test_results["error"] = "Analyzer dependencies not available"
        return test_results
    
    # Test each analyzer type
    analyzer_types = ["sales_page", "website", "document", "enhanced_sales_page", "vsl"]
    
    for analyzer_type in analyzer_types:
        try:
            analyzer = get_analyzer(analyzer_type)
            test_results["test_results"][analyzer_type] = {
                "class_name": type(analyzer).__name__,
                "instantiation": "success",
                "is_fallback": isinstance(analyzer, FallbackAnalyzer)
            }
        except Exception as e:
            test_results["test_results"][analyzer_type] = {
                "class_name": "Unknown",
                "instantiation": "failed",
                "error": str(e),
                "is_fallback": True
            }
    
    # Determine overall status
    successful_analyzers = sum(
        1 for result in test_results["test_results"].values() 
        if result["instantiation"] == "success" and not result["is_fallback"]
    )
    
    if successful_analyzers == len(analyzer_types):
        test_results["overall_status"] = "excellent"
    elif successful_analyzers > 0:
        test_results["overall_status"] = "partial"
    else:
        test_results["overall_status"] = "failed"
    
    test_results["successful_analyzers"] = successful_analyzers
    test_results["total_analyzers"] = len(analyzer_types)
    
    return test_results

def get_analyzer_requirements() -> Dict[str, Any]:
    """Get analyzer system requirements and dependencies"""
    
    return {
        "required_packages": [
            "aiohttp>=3.8.0",
            "beautifulsoup4>=4.11.0", 
            "lxml>=4.9.0",
            "requests>=2.28.0",
            "asyncio"
        ],
        "optional_packages": [
            "selenium>=4.0.0",  # For JavaScript-heavy sites
            "playwright>=1.30.0",  # Alternative to selenium
            "pandas>=1.5.0",  # For data processing
            "numpy>=1.23.0"  # For numerical operations
        ],
        "ai_provider_packages": [
            "groq>=0.4.0",  # Ultra-cheap provider
            "openai>=1.0.0",  # For Together AI, Deepseek, etc.
            "anthropic>=0.25.0",  # For Claude
            "cohere>=4.40.0"  # For Cohere
        ],
        "system_requirements": {
            "python_version": ">=3.8",
            "memory": ">=512MB available",
            "network": "Internet access required for URL analysis"
        },
        "installation_commands": [
            "pip install aiohttp beautifulsoup4 lxml requests",
            "pip install groq openai anthropic cohere",
            "# Optional: pip install selenium playwright pandas numpy"
        ]
    }

class AnalyzerManager:
    """Manager class for handling multiple analyzers with lazy loading"""
    
    def __init__(self):
        self.analyzers = {}
        self._analyzers_loaded = False
        self._analyzer_classes = None
    
    def _ensure_analyzers_loaded(self):
        """Ensure analyzers are loaded using lazy loading"""
        if not self._analyzers_loaded:
            self._analyzer_classes = _lazy_import_analyzers()
            self._initialize_analyzers()
            self._analyzers_loaded = True
    
    def _initialize_analyzers(self):
        """Initialize all available analyzers"""
        if not self._analyzer_classes:
            # All analyzers will be fallback
            analyzer_types = ["sales_page", "website", "document", "enhanced_sales_page", "vsl"]
            for analyzer_type in analyzer_types:
                self.analyzers[analyzer_type] = FallbackAnalyzer()
                logger.warning(f"⚠️ Using fallback for {analyzer_type} analyzer")
            return
        
        analyzer_types = ["sales_page", "website", "document", "enhanced_sales_page", "vsl"]
        
        for analyzer_type in analyzer_types:
            try:
                analyzer = get_analyzer(analyzer_type)
                self.analyzers[analyzer_type] = analyzer
                logger.info(f"✅ Initialized {analyzer_type} analyzer: {type(analyzer).__name__}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {analyzer_type} analyzer: {str(e)}")
                self.analyzers[analyzer_type] = FallbackAnalyzer()
    
    def get_analyzer(self, analyzer_type: str):
        """Get analyzer by type"""
        self._ensure_analyzers_loaded()
        return self.analyzers.get(analyzer_type, self.analyzers.get("sales_page", FallbackAnalyzer()))
    
    def get_best_analyzer_for_url(self, url: str) -> str:
        """Determine best analyzer type based on URL analysis"""
        url_lower = url.lower()
        
        # Video sales letter detection
        if any(indicator in url_lower for indicator in ['video', 'vsl', 'watch', 'play']):
            return "vsl"
        
        # Enhanced sales page detection
        if any(indicator in url_lower for indicator in ['sales', 'buy', 'order', 'checkout', 'offer']):
            return "enhanced_sales_page"
        
        # General website
        return "website"
    
    async def analyze_with_best_fit(self, url: str) -> Dict[str, Any]:
        """Analyze URL with the most appropriate analyzer"""
        analyzer_type = self.get_best_analyzer_for_url(url)
        analyzer = self.get_analyzer(analyzer_type)
        
        logger.info(f"🎯 Using {analyzer_type} analyzer for {url}")
        
        result = await analyzer.analyze(url)
        result["analyzer_used"] = analyzer_type
        result["analyzer_class"] = type(analyzer).__name__
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all analyzers"""
        self._ensure_analyzers_loaded()
        
        status = {
            "total_analyzers": len(self.analyzers),
            "working_analyzers": 0,
            "fallback_analyzers": 0,
            "analyzer_details": {}
        }
        
        for analyzer_type, analyzer in self.analyzers.items():
            is_fallback = isinstance(analyzer, FallbackAnalyzer)
            
            status["analyzer_details"][analyzer_type] = {
                "class_name": type(analyzer).__name__,
                "is_fallback": is_fallback,
                "status": "fallback" if is_fallback else "working"
            }
            
            if is_fallback:
                status["fallback_analyzers"] += 1
            else:
                status["working_analyzers"] += 1
        
        return status

# ✅ FIXED: Update global flags after attempting lazy load
def update_global_flags():
    """Update global availability flags"""
    global ANALYZERS_AVAILABLE, INTELLIGENCE_AVAILABLE
    
    analyzers = _lazy_import_analyzers()
    ANALYZERS_AVAILABLE = analyzers is not None
    INTELLIGENCE_AVAILABLE = analyzers is not None

# Auto-update flags when module is imported
update_global_flags()