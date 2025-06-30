"""
File: src/intelligence/utils/analyzer_factory.py
Analyzer Factory - Manages different types of analyzers
Extracted from routes.py for better organization
"""
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Try to import analyzers with fallback handling
try:
    from src.intelligence import (
        SalesPageAnalyzer, 
        DocumentAnalyzer, 
        WebAnalyzer, 
        EnhancedSalesPageAnalyzer, 
        VSLAnalyzer,
        INTELLIGENCE_AVAILABLE
    )
    ANALYZERS_AVAILABLE = INTELLIGENCE_AVAILABLE
    logger.info("✅ SUCCESS: All intelligence analyzers imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ IMPORT WARNING: Analyzers not available: {str(e)}")
    ANALYZERS_AVAILABLE = False


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
    """
    if not ANALYZERS_AVAILABLE:
        logger.warning("⚠️ Using fallback analyzer - dependencies missing")
        return FallbackAnalyzer()
    
    analyzer_map = {
        "sales_page": SalesPageAnalyzer,
        "website": WebAnalyzer,
        "document": DocumentAnalyzer,
        "enhanced_sales_page": EnhancedSalesPageAnalyzer,
        "vsl": VSLAnalyzer,
        "video_sales_letter": VSLAnalyzer
    }
    
    analyzer_class = analyzer_map.get(analysis_type, SalesPageAnalyzer)
    
    try:
        return analyzer_class()
    except Exception as e:
        logger.error(f"❌ Failed to initialize {analyzer_class.__name__}: {str(e)}")
        return FallbackAnalyzer()


def get_available_analyzers() -> Dict[str, Dict[str, Any]]:
    """Get list of available analyzers and their capabilities"""
    
    analyzers = {
        "sales_page": {
            "name": "Sales Page Analyzer",
            "description": "Analyze sales pages and landing pages",
            "supported_formats": ["HTML", "URL"],
            "available": ANALYZERS_AVAILABLE
        },
        "website": {
            "name": "Website Analyzer", 
            "description": "Analyze general websites and web content",
            "supported_formats": ["HTML", "URL"],
            "available": ANALYZERS_AVAILABLE
        },
        "document": {
            "name": "Document Analyzer",
            "description": "Analyze uploaded documents",
            "supported_formats": ["PDF", "DOC", "TXT"],
            "available": ANALYZERS_AVAILABLE
        },
        "enhanced_sales_page": {
            "name": "Enhanced Sales Page Analyzer",
            "description": "Advanced sales page analysis with deeper insights",
            "supported_formats": ["HTML", "URL"],
            "available": ANALYZERS_AVAILABLE
        },
        "vsl": {
            "name": "Video Sales Letter Analyzer",
            "description": "Analyze video sales letters and video content",
            "supported_formats": ["URL", "Video"],
            "available": ANALYZERS_AVAILABLE
        }
    }
    
    return analyzers


def test_analyzer_functionality() -> Dict[str, Any]:
    """Test analyzer functionality and return status"""
    
    test_results = {
        "analyzers_available": ANALYZERS_AVAILABLE,
        "test_results": {},
        "overall_status": "unknown"
    }
    
    if not ANALYZERS_AVAILABLE:
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
        "system_requirements": {
            "python_version": ">=3.8",
            "memory": ">=512MB available",
            "network": "Internet access required for URL analysis"
        },
        "installation_commands": [
            "pip install aiohttp beautifulsoup4 lxml requests",
            "# Optional: pip install selenium playwright pandas numpy"
        ]
    }


class AnalyzerManager:
    """Manager class for handling multiple analyzers"""
    
    def __init__(self):
        self.analyzers = {}
        self._initialize_analyzers()
    
    def _initialize_analyzers(self):
        """Initialize all available analyzers"""
        analyzer_types = ["sales_page", "website", "document", "enhanced_sales_page", "vsl"]
        
        for analyzer_type in analyzer_types:
            try:
                self.analyzers[analyzer_type] = get_analyzer(analyzer_type)
                logger.info(f"✅ Initialized {analyzer_type} analyzer")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {analyzer_type} analyzer: {str(e)}")
                self.analyzers[analyzer_type] = FallbackAnalyzer()
    
    def get_analyzer(self, analyzer_type: str):
        """Get analyzer by type"""
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