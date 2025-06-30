"""
File: src/intelligence/routers/debug_routes.py
Debug Routes - Development and testing endpoints
Extracted from main routes.py for better organization
"""
import aiohttp
import traceback
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from ..utils.analyzer_factory import test_analyzer_functionality
from ..utils.amplifier_service import get_amplifier_status

router = APIRouter()

@router.get("/test-scraping")
async def debug_test_scraping():
    """Debug the actual scraping process"""
    
    test_urls = [
        "https://httpbin.org/html",           # Simple test page
        "https://example.com",                # Basic page
        "https://www.hepatoburn.com/",        # Target site
    ]
    
    results = {}
    
    for url in test_urls:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    content = await response.text()
                    results[url] = {
                        "status": response.status,
                        "content_length": len(content),
                        "success": response.status == 200,
                        "title_found": "<title>" in content.lower(),
                        "error": None
                    }
        except Exception as e:
            results[url] = {
                "status": None,
                "content_length": 0,
                "success": False,
                "title_found": False,
                "error": str(e)
            }
    
    return {
        "scraping_test_results": results,
        "summary": {
            "basic_http_working": results.get("https://httpbin.org/html", {}).get("success", False),
            "target_site_accessible": results.get("https://www.hepatoburn.com/", {}).get("success", False),
            "network_available": any(r.get("success", False) for r in results.values())
        }
    }

@router.get("/test-database-storage")
async def debug_database_storage():
    """Test what gets stored in the database vs what the analyzer returns"""
    
    try:
        from src.intelligence.analyzers import SalesPageAnalyzer
        
        # Run analyzer
        analyzer = SalesPageAnalyzer()
        test_url = "https://www.hepatoburn.com/"
        analysis_result = await analyzer.analyze(test_url)
        
        # Extract the intelligence data (like routes.py does)
        offer_intel = analysis_result.get("offer_intelligence", {})
        psychology_intel = analysis_result.get("psychology_intelligence", {})
        content_intel = analysis_result.get("content_intelligence", {})
        competitive_intel = analysis_result.get("competitive_intelligence", {})
        brand_intel = analysis_result.get("brand_intelligence", {})
        
        # Test the validation function (if it exists)
        try:
            from ..utils.intelligence_validation import validate_intelligence_section
            
            validated_content = validate_intelligence_section(content_intel)
            validated_brand = validate_intelligence_section(brand_intel)
            
            validation_results = {
                "validation_function_available": True,
                "content_intel_before_validation": content_intel,
                "content_intel_after_validation": validated_content,
                "brand_intel_before_validation": brand_intel,
                "brand_intel_after_validation": validated_brand,
                "content_validation_changed": content_intel != validated_content,
                "brand_validation_changed": brand_intel != validated_brand
            }
        except ImportError:
            validation_results = {
                "validation_function_available": False,
                "note": "validate_intelligence_section function not found - this might be the issue"
            }
        
        return {
            "test_url": test_url,
            "analyzer_extraction": {
                "offer_intelligence_keys": list(offer_intel.keys()),
                "psychology_intelligence_keys": list(psychology_intel.keys()),
                "content_intelligence_keys": list(content_intel.keys()),
                "competitive_intelligence_keys": list(competitive_intel.keys()),
                "brand_intelligence_keys": list(brand_intel.keys()),
                "content_intelligence_empty": not bool(content_intel),
                "brand_intelligence_empty": not bool(brand_intel)
            },
            "raw_extraction_data": {
                "content_intelligence": content_intel,
                "brand_intelligence": brand_intel
            },
            "validation_test": validation_results,
            "database_storage_ready": {
                "offer_intel_size": len(str(offer_intel)),
                "psychology_intel_size": len(str(psychology_intel)), 
                "content_intel_size": len(str(content_intel)),
                "competitive_intel_size": len(str(competitive_intel)),
                "brand_intel_size": len(str(brand_intel)),
                "all_categories_have_data": all([offer_intel, psychology_intel, content_intel, competitive_intel, brand_intel])
            }
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "test_failed": True
        }

@router.get("/test-routes-validation")
async def debug_routes_validation():
    """Test the routes.py validation functions specifically"""
    
    try:
        # Test data similar to what analyzer would return
        test_content_intelligence = {
            "key_messages": ["Test message 1", "Test message 2"],
            "success_stories": ["Customer success story"],
            "social_proof": ["5-star reviews", "1000+ customers"],
            "content_structure": "Long-form sales page with 3 sections",
            "content_length": 1500,
            "messaging_hierarchy": ["Primary benefit", "Social proof", "Call to action"]
        }
        
        test_brand_intelligence = {
            "tone_voice": "Scientific and authoritative",
            "messaging_style": "Educational and informative", 
            "brand_positioning": "Premium health solution provider"
        }
        
        # Test if validation functions exist and work
        try:
            from ..utils.intelligence_validation import ensure_intelligence_structure
            structure_function_available = True
        except ImportError:
            structure_function_available = False
        
        try:
            from ..utils.intelligence_validation import validate_intelligence_section
            validation_function_available = True
            
            # Test validation
            validated_content = validate_intelligence_section(test_content_intelligence)
            validated_brand = validate_intelligence_section(test_brand_intelligence)
            
        except ImportError:
            validation_function_available = False
            validated_content = test_content_intelligence
            validated_brand = test_brand_intelligence
        
        return {
            "routes_functions": {
                "ensure_intelligence_structure_available": structure_function_available,
                "validate_intelligence_section_available": validation_function_available
            },
            "test_data": {
                "content_intelligence_test": test_content_intelligence,
                "brand_intelligence_test": test_brand_intelligence
            },
            "validation_results": {
                "content_intelligence_validated": validated_content,
                "brand_intelligence_validated": validated_brand,
                "content_data_preserved": bool(validated_content),
                "brand_data_preserved": bool(validated_brand)
            },
            "issue_diagnosis": {
                "functions_missing": not (structure_function_available and validation_function_available),
                "data_getting_lost": not (bool(validated_content) and bool(validated_brand)),
                "likely_issue": "validation_functions_missing" if not validation_function_available else "unknown"
            }
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "test_failed": True
        }

@router.get("/test-full-analyzer")
async def debug_test_full_analyzer():
    """Test the complete analyzer chain"""
    try:
        from src.intelligence.analyzers import SalesPageAnalyzer
        
        analyzer = SalesPageAnalyzer()
        url = "https://www.hepatoburn.com/"
        
        # Test the full analysis
        result = await analyzer.analyze(url)
        
        return {
            "analyzer_class": type(analyzer).__name__,
            "test_url": url,
            "analysis_results": {
                "confidence_score": result.get('confidence_score', 0),
                "page_title": result.get('page_title', 'None'),
                "product_name": result.get('product_name', 'None'),
                "raw_content_length": len(result.get('raw_content', '')),
                "raw_content_preview": result.get('raw_content', '')[:500] + "..." if result.get('raw_content') else "EMPTY",
                "has_products": len(result.get('offer_intelligence', {}).get('products', [])),
                "has_pricing": len(result.get('offer_intelligence', {}).get('pricing', [])),
                "has_error": 'error' in result,
                "error_message": result.get('error', None),
                "analysis_note": result.get('analysis_note', None)
            },
            "full_result_keys": list(result.keys()),
            "success": result.get('confidence_score', 0) > 0
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "success": False
        }

@router.get("/system-status")
async def get_system_status(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive system status"""
    
    # Test analyzers
    analyzer_status = test_analyzer_functionality()
    
    # Test amplifier
    amplifier_status = get_amplifier_status()
    
    # Test database connection
    try:
        # Simple database test would go here
        database_status = "connected"
    except Exception as e:
        database_status = f"error: {str(e)}"
    
    return {
        "system_health": {
            "analyzers": analyzer_status["overall_status"],
            "amplifier": amplifier_status["status"],
            "database": database_status,
            "overall": "healthy" if all([
                analyzer_status["overall_status"] in ["excellent", "partial"],
                amplifier_status["status"] != "error",
                database_status == "connected"
            ]) else "degraded"
        },
        "detailed_status": {
            "analyzers": analyzer_status,
            "amplifier": amplifier_status,
            "database": {"status": database_status}
        },
        "recommendations": []
    }

@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "service": "intelligence-module",
        "version": "2.0.0-refactored"
    }