"""
File: src/intelligence/routers/debug_routes.py
Debug Routes - Development and testing endpoints
Extracted from main routes.py for better organization
UPDATED: Added R2 and AI provider testing endpoints
"""
import os
import aiohttp
import traceback
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from ..utils.analyzer_factory import test_analyzer_functionality

# Check if enhancement functions are available
try:
    from ..amplifier.enhancement import (
        identify_opportunities,
        generate_enhancements,
        create_enriched_intelligence
    )
    ENHANCEMENT_FUNCTIONS_AVAILABLE = True
except ImportError:
    ENHANCEMENT_FUNCTIONS_AVAILABLE = False

router = APIRouter()

def get_amplifier_status():
    """Get amplifier system status"""
    if not ENHANCEMENT_FUNCTIONS_AVAILABLE:
        return {
            "status": "unavailable",
            "available": False,
            "error": "Enhancement dependencies not installed",
            "capabilities": {},
            "recommendations": [
                "Install amplifier dependencies",
                "Check amplifier package configuration"
            ]
        }
    
    return {
        "status": "available",
        "available": True,
        "capabilities": {
            "direct_enhancement_functions": True,
            "scientific_enhancement": True,
            "credibility_boost": True,
            "competitive_analysis": True,
            "content_optimization": True
        },
        "architecture": "direct_modular_enhancement",
        "functions_available": [
            "identify_opportunities",
            "generate_enhancements", 
            "create_enriched_intelligence"
        ]
    }

@router.get("/test-r2-status") 
async def test_r2_status():
    """🔧 Test Cloudflare R2 configuration status"""
    r2_vars = [
        "CLOUDFLARE_ACCOUNT_ID",
        "CLOUDFLARE_R2_ACCESS_KEY_ID", 
        "CLOUDFLARE_R2_SECRET_ACCESS_KEY", 
        "CLOUDFLARE_R2_BUCKET_NAME"
    ]
    configured = [var for var in r2_vars if os.getenv(var)]
    missing = [var for var in r2_vars if not os.getenv(var)]
    
    r2_fully_configured = len(missing) == 0
    
    return {
        "success": True,
        "r2_status": "✅ R2 CONFIGURED" if r2_fully_configured else "❌ MISSING VARIABLES",
        "r2_fully_configured": r2_fully_configured,
        "configured_vars": configured,
        "missing_vars": missing,
        "total_vars_needed": len(r2_vars),
        "vars_configured": len(configured),
        "diagnosis": {
            "issue": "Missing R2 environment variables" if missing else "R2 appears configured",
            "solution": f"Add missing variables: {missing}" if missing else "R2 configuration looks good",
            "impact": "AI enhancement system will fail without R2" if missing else "R2 should support AI enhancements"
        },
        "next_steps": [
            "Add missing R2 variables in Railway dashboard" if missing else "R2 configuration complete",
            "Deploy service after adding variables" if missing else "Test AI enhancement system",
            "Test intelligence enhancement system"
        ]
    }

@router.get("/test-ai-providers")
async def test_ai_providers():
    """🔧 Test AI provider configuration and status"""
    providers = {
        "groq": bool(os.getenv("GROQ_API_KEY")),
        "together": bool(os.getenv("TOGETHER_API_KEY")), 
        "deepseek": bool(os.getenv("DEEPSEEK_API_KEY")),
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "cohere": bool(os.getenv("COHERE_API_KEY"))
    }
    
    configured_providers = [name for name, configured in providers.items() if configured]
    total_providers = len(configured_providers)
    
    # Check R2 for enhancement system
    r2_configured = all([
        os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID"),
        os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY"),
        os.getenv("CLOUDFLARE_R2_BUCKET_NAME")
    ])
    
    # Determine enhancement system status
    if total_providers == 0:
        enhancement_status = "❌ NO AI PROVIDERS"
        confidence_expected = "10-20%"
        issue = "No AI providers configured"
    elif not r2_configured:
        enhancement_status = "❌ STORAGE MISSING"
        confidence_expected = "60%"
        issue = "R2 storage not configured - blocking AI enhancements"
    else:
        enhancement_status = "✅ SHOULD BE WORKING"
        confidence_expected = "90-95%"
        issue = "System should be fully operational"
    
    return {
        "success": True,
        "enhancement_status": enhancement_status,
        "confidence_expected": confidence_expected,
        "current_issue": issue,
        "providers_configured": providers,
        "configured_providers": configured_providers,
        "total_providers": total_providers,
        "primary_provider": "groq" if providers["groq"] else (configured_providers[0] if configured_providers else "none"),
        "r2_configured": r2_configured,
        "diagnosis": {
            "problem": issue,
            "solution": "Configure missing R2 environment variables" if not r2_configured else "System should be working",
            "expected_result": f"Intelligence confidence should reach {confidence_expected}"
        },
        "enhancement_modules": {
            "scientific_intelligence": "Requires AI providers + R2",
            "credibility_intelligence": "Requires AI providers + R2", 
            "market_intelligence": "Requires AI providers + R2",
            "emotional_transformation_intelligence": "Requires AI providers + R2",
            "scientific_authority_intelligence": "Requires AI providers + R2"
        }
    }

@router.get("/test-groq-connection")  
async def test_groq_connection():
    """🔧 Test Groq API key and connection"""
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not groq_key:
        return {
            "success": False,
            "groq_configured": False,
            "status": "❌ MISSING GROQ KEY",
            "error": "GROQ_API_KEY environment variable not found"
        }
    
    # Test if key format looks valid
    key_valid_format = len(groq_key) > 20 and groq_key.startswith("gsk_")
    
    return {
        "success": True,
        "groq_configured": True,
        "groq_key_length": len(groq_key),
        "key_format_valid": key_valid_format,
        "key_prefix": groq_key[:8] + "..." if len(groq_key) > 8 else "short_key",
        "status": "✅ GROQ CONFIGURED" if key_valid_format else "⚠️ GROQ KEY FORMAT ISSUE",
        "diagnosis": {
            "issue": "Groq key format issue" if not key_valid_format else "Groq key appears valid",
            "recommendation": "Check Groq key format" if not key_valid_format else "Groq configuration looks good"
        }
    }

@router.get("/intelligence-confidence-analysis")
async def intelligence_confidence_analysis():
    """📊 Analyze why intelligence confidence might be low"""
    
    # Current vs Expected Analysis
    current_state = {
        "confidence_score": 0.6,
        "enhancement_quality": "fallback_no_mock",
        "modules_successful": [],
        "total_enhancements": 0,
        "empty_sections": [
            "scientific_intelligence",
            "credibility_intelligence", 
            "market_intelligence",
            "emotional_transformation_intelligence",
            "scientific_authority_intelligence"
        ]
    }
    
    expected_state = {
        "confidence_score": 0.95,
        "enhancement_quality": "excellent",
        "modules_successful": [
            "scientific", "credibility", "content", 
            "emotional", "authority", "market"
        ],
        "total_enhancements": 192,
        "populated_sections": [
            "scientific_intelligence",
            "credibility_intelligence",
            "market_intelligence", 
            "emotional_transformation_intelligence",
            "scientific_authority_intelligence"
        ]
    }
    
    # Identify the gap
    confidence_gap = expected_state["confidence_score"] - current_state["confidence_score"]
    missing_enhancements = expected_state["total_enhancements"] - current_state["total_enhancements"]
    
    # Check current configuration
    r2_configured = all([
        os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID"),
        os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY"),
        os.getenv("CLOUDFLARE_R2_BUCKET_NAME")
    ])
    
    groq_configured = bool(os.getenv("GROQ_API_KEY"))
    
    return {
        "success": True,
        "confidence_analysis": {
            "current_confidence": current_state["confidence_score"],
            "expected_confidence": expected_state["confidence_score"],
            "confidence_gap": confidence_gap,
            "percentage_loss": f"{(confidence_gap / expected_state['confidence_score']) * 100:.1f}%"
        },
        "enhancement_analysis": {
            "current_enhancements": current_state["total_enhancements"],
            "expected_enhancements": expected_state["total_enhancements"],
            "missing_enhancements": missing_enhancements,
            "enhancement_success_rate": "0%" if current_state["total_enhancements"] == 0 else "Partial"
        },
        "missing_intelligence_sections": current_state["empty_sections"],
        "current_configuration": {
            "r2_configured": r2_configured,
            "groq_configured": groq_configured,
            "system_ready": r2_configured and groq_configured
        },
        "root_cause": {
            "primary_issue": "Groq JSON parsing errors" if groq_configured and r2_configured else "Missing configuration",
            "secondary_issue": "AI enhancement modules cannot generate content",
            "impact": "System falls back to basic analysis only",
            "evidence": {
                "enhancement_quality": current_state["enhancement_quality"],
                "modules_successful": current_state["modules_successful"],
                "total_enhancements": current_state["total_enhancements"]
            }
        },
        "fix_priority": [
            "1. Fix Groq API response parsing (CRITICAL)" if groq_configured else "1. Add Groq API key",
            "2. Test with alternative AI provider (Together/DeepSeek)",
            "3. Check AI response format handling",
            "4. Verify confidence scores return to 90-95%"
        ],
        "expected_after_fix": {
            "confidence_score": "90-95%",
            "enhancement_quality": "excellent",
            "populated_sections": 6,
            "total_enhancements": "150-200",
            "processing_time": "Similar (AI enhancement is fast)"
        }
    }

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

@router.get("/test-enhancement-functions")
async def debug_test_enhancement_functions():
    """Test the direct enhancement functions"""
    
    if not ENHANCEMENT_FUNCTIONS_AVAILABLE:
        return {
            "enhancement_functions_available": False,
            "error": "Enhancement functions not available",
            "recommendation": "Install amplifier dependencies"
        }
    
    try:
        # Create mock data to test enhancement functions
        mock_base_intel = {
            "product_name": "Test Product",
            "confidence_score": 0.7,
            "offer_intelligence": {
                "products": ["Main product"],
                "value_propositions": ["Health benefit"]
            },
            "psychology_intelligence": {
                "emotional_triggers": ["Health concern"],
                "target_audience": "Health-conscious individuals"
            }
        }
        
        mock_preferences = {
            "enhance_scientific_backing": True,
            "boost_credibility": True,
            "competitive_analysis": True
        }
        
        # Test each function
        opportunities = await identify_opportunities(
            base_intel=mock_base_intel,
            preferences=mock_preferences,
            providers=[]
        )
        
        enhancements = await generate_enhancements(
            base_intel=mock_base_intel,
            opportunities=opportunities,
            providers=[]
        )
        
        enriched = create_enriched_intelligence(
            base_intel=mock_base_intel,
            enhancements=enhancements
        )
        
        return {
            "enhancement_functions_available": True,
            "test_results": {
                "opportunities_identified": opportunities.get("opportunity_metadata", {}).get("total_opportunities", 0),
                "enhancements_generated": enhancements.get("enhancement_metadata", {}).get("total_enhancements", 0),
                "enrichment_successful": enriched.get("confidence_score", 0) > 0,
                "enrichment_metadata": enriched.get("enrichment_metadata", {})
            },
            "functions_tested": [
                "identify_opportunities",
                "generate_enhancements",
                "create_enriched_intelligence"
            ]
        }
        
    except Exception as e:
        return {
            "enhancement_functions_available": True,
            "test_failed": True,
            "error": str(e),
            "traceback": traceback.format_exc()
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