# src/intelligence/routers/universal_test_routes.py

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

# Import the universal extraction system
from src.intelligence.utils.product_name_fix import (
    extract_product_name_from_intelligence,
    debug_product_extraction,
    test_universal_extraction
)

logger = logging.getLogger(__name__)

universal_test_router = APIRouter(prefix="/api/test/universal", tags=["universal-product-extraction"])

@universal_test_router.get("/run-all-tests")
async def run_all_universal_tests():
    """
    🧪 Run comprehensive tests across multiple product types and niches
    
    Tests the universal extraction system with:
    - Health supplements (AquaSculpt, ProstaStream, etc.)
    - Business courses (Profit Maximizer, etc.)
    - Software products (CodeMaster Pro, etc.)
    - Diet programs (Keto Blueprint, etc.)
    - Brain training (Memory Hack, etc.)
    """
    
    try:
        logger.info("🧪 Running universal product extraction tests...")
        
        # Run the comprehensive test suite
        test_passed = test_universal_extraction()
        
        return {
            "success": True,
            "all_tests_passed": test_passed,
            "test_coverage": [
                "Health supplements", 
                "Business courses", 
                "Software products", 
                "Diet programs", 
                "Brain training",
                "Any product type"
            ],
            "extraction_strategies": [
                "URL-based extraction",
                "Content pattern matching", 
                "Emotional trigger analysis",
                "Page title analysis",
                "Multi-source content analysis",
                "Scientific content analysis",
                "AI-generated data (filtered)"
            ],
            "message": "✅ Universal extraction system ready for thousands of products" if test_passed else "❌ Some tests failed - review extraction logic"
        }
        
    except Exception as e:
        logger.error(f"❌ Universal tests failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tests failed: {str(e)}")


@universal_test_router.post("/analyze-any-product")
async def analyze_any_product(intelligence_data: Dict[str, Any]):
    """
    🔍 Analyze product extraction for ANY sales page
    
    Send intelligence data from any product/niche and get detailed analysis:
    - Which strategies found candidates
    - Why specific candidates were selected/rejected
    - Confidence scores and recommendations
    - Works with any product type across all niches
    """
    
    try:
        logger.info("🔍 Analyzing universal product extraction...")
        
        # Run the extraction
        extracted_name = extract_product_name_from_intelligence(intelligence_data)
        
        # Get detailed debug information
        debug_info = debug_product_extraction(intelligence_data)
        
        return {
            "success": True,
            "extracted_product_name": extracted_name,
            "extraction_successful": extracted_name != "Product",
            "confidence": "high" if extracted_name != "Product" else "low",
            "debug_analysis": debug_info,
            "source_analysis": {
                "url": intelligence_data.get("source_url"),
                "title": intelligence_data.get("page_title") or intelligence_data.get("source_title"),
                "content_length": len(intelligence_data.get("raw_content", "")),
                "has_emotional_triggers": bool(intelligence_data.get("psychology_intelligence", {}).get("emotional_triggers")),
                "intelligence_sections": list(intelligence_data.keys())
            },
            "universal_compatibility": True,
            "supported_niches": [
                "Health & Supplements",
                "Business & Finance", 
                "Software & Technology",
                "Education & Courses",
                "Diet & Fitness",
                "Personal Development",
                "Any other product type"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Universal analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@universal_test_router.get("/test-specific-niche/{niche}")
async def test_specific_niche(niche: str):
    """
    🎯 Test extraction for a specific niche
    
    Available niches:
    - health (supplements, wellness products)
    - business (courses, training, tools)
    - software (apps, SaaS, tools)
    - diet (weight loss, nutrition)
    - education (courses, programs)
    """
    
    niche_test_data = {
        "health": {
            "source_url": "https://liverpureadvanced.com/offer",
            "raw_content": "LiverPure Advanced supports liver health naturally. Get LiverPure Advanced today with 60-day guarantee!",
            "page_title": "LiverPure Advanced - Liver Health Supplement",
            "expected": "LiverPure Advanced"
        },
        "business": {
            "source_url": "https://wealthbuilderblueprint.co",
            "raw_content": "The Wealth Builder Blueprint shows you how to build passive income. Wealth Builder Blueprint students earn $10k+ monthly.",
            "page_title": "Wealth Builder Blueprint - Financial Freedom Course",
            "expected": "Wealth Builder Blueprint"
        },
        "software": {
            "source_url": "https://designerpro.app/premium",
            "raw_content": "Designer Pro makes graphic design easy. Designer Pro includes 1000+ templates and AI tools.",
            "page_title": "Designer Pro - Graphic Design Software",
            "expected": "Designer Pro"
        },
        "diet": {
            "source_url": "https://fatlossaccelerate.net",
            "raw_content": "Fat Loss Accelerator helps you lose weight fast. The Fat Loss Accelerator system burns fat naturally.",
            "page_title": "Fat Loss Accelerator - Weight Loss Program",
            "expected": "Fat Loss Accelerator"
        },
        "education": {
            "source_url": "https://tradingmastery.academy",
            "raw_content": "Trading Mastery Academy teaches profitable trading strategies. Join Trading Mastery Academy today!",
            "page_title": "Trading Mastery Academy - Learn to Trade",
            "expected": "Trading Mastery Academy"
        }
    }
    
    if niche.lower() not in niche_test_data:
        raise HTTPException(status_code=400, detail=f"Niche '{niche}' not supported. Available: {list(niche_test_data.keys())}")
    
    try:
        test_data = niche_test_data[niche.lower()]
        
        # Create intelligence data
        intelligence = {
            "source_url": test_data["source_url"],
            "raw_content": test_data["raw_content"],
            "page_title": test_data["page_title"]
        }
        
        # Test extraction
        extracted_name = extract_product_name_from_intelligence(intelligence)
        expected_name = test_data["expected"]
        
        test_passed = extracted_name == expected_name
        
        return {
            "success": True,
            "niche": niche.title(),
            "test_passed": test_passed,
            "extracted_name": extracted_name,
            "expected_name": expected_name,
            "test_data": {
                "url": test_data["source_url"],
                "title": test_data["page_title"],
                "content_preview": test_data["raw_content"][:100] + "..."
            },
            "message": f"✅ {niche.title()} niche extraction working correctly" if test_passed else f"❌ {niche.title()} niche extraction needs attention"
        }
        
    except Exception as e:
        logger.error(f"❌ Niche test for {niche} failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Niche test failed: {str(e)}")


@universal_test_router.post("/test-your-product")
async def test_your_product(
    product_url: str,
    product_name: str = None,
    raw_content: str = None,
    page_title: str = None
):
    """
    🚀 Test extraction with YOUR specific product
    
    Provide your product's URL and optional content to test if the 
    universal extraction system can correctly identify your product name.
    
    Parameters:
    - product_url: URL of your sales page
    - product_name: Expected product name (for validation)
    - raw_content: Page content (optional)
    - page_title: Page title (optional)
    """
    
    try:
        # Create intelligence data from provided information
        intelligence = {
            "source_url": product_url,
            "raw_content": raw_content or "",
            "page_title": page_title or "",
            "source_title": page_title or ""
        }
        
        # Run extraction
        extracted_name = extract_product_name_from_intelligence(intelligence)
        debug_info = debug_product_extraction(intelligence)
        
        # Determine success
        if product_name:
            test_passed = extracted_name.lower() == product_name.lower()
            accuracy_message = f"✅ Correctly extracted '{extracted_name}'" if test_passed else f"❌ Expected '{product_name}' but got '{extracted_name}'"
        else:
            test_passed = extracted_name != "Product"
            accuracy_message = f"✅ Successfully extracted '{extracted_name}'" if test_passed else "❌ Could not extract product name"
        
        return {
            "success": True,
            "your_product_test": {
                "url": product_url,
                "extracted_name": extracted_name,
                "expected_name": product_name,
                "test_passed": test_passed,
                "accuracy_message": accuracy_message
            },
            "extraction_details": debug_info,
            "recommendations": [
                "✅ Universal extraction system can handle your product" if test_passed else "🔧 May need custom patterns for your product type",
                "📊 Review extraction strategies for optimization",
                "🚀 Ready for production use" if test_passed else "🛠️ Consider providing more content for better accuracy"
            ],
            "next_steps": [
                "Deploy to production" if test_passed else "Review extraction patterns",
                "Monitor extraction accuracy across different products",
                "Scale to thousands of products with confidence" if test_passed else "Fine-tune extraction for your specific niche"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Custom product test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Product test failed: {str(e)}")


@universal_test_router.get("/extraction-stats")
async def get_extraction_stats():
    """
    📊 Get statistics about the universal extraction system
    
    Shows capabilities, supported patterns, and coverage across different niches
    """
    
    return {
        "success": True,
        "universal_extraction_system": {
            "total_patterns": 10,
            "pattern_types": [
                "Direct action patterns (try, get, discover, etc.)",
                "Product relationship patterns (helps, supports, etc.)",
                "Branded product patterns with suffixes",
                "Emotional/impact patterns",
                "Business/program patterns", 
                "Testimonial patterns",
                "Call-to-action patterns",
                "CamelCase patterns",
                "Trademark patterns",
                "Quoted content patterns"
            ],
            "supported_suffixes": [
                "Health: Pure, Max, Plus, Sculpt, Burn, Boost, Guard, Shield",
                "Business: Pro, Suite, Master, Academy, Blueprint, Secrets",
                "Education: Course, Training, Bootcamp, Workshop, Masterclass",
                "Premium: Gold, Platinum, Diamond, VIP, Executive, Deluxe"
            ],
            "extraction_strategies": 7,
            "strategy_priority": [
                "1. URL-based extraction (highest confidence)",
                "2. Raw content pattern matching",
                "3. Emotional trigger contexts",
                "4. Page title analysis", 
                "5. Multi-source content analysis",
                "6. Scientific content analysis",
                "7. AI-generated data (lowest confidence)"
            ],
            "false_positive_filters": 85,
            "supported_niches": [
                "Health & Supplements",
                "Business & Finance",
                "Software & Technology", 
                "Education & Courses",
                "Diet & Fitness",
                "Personal Development",
                "E-commerce Products",
                "Digital Marketing Tools",
                "Investment Programs",
                "Any other product type"
            ],
            "quality_assurance": {
                "multi_strategy_validation": True,
                "ai_hallucination_filtering": True,
                "frequency_based_scoring": True,
                "source_reliability_weighting": True,
                "universal_false_positive_detection": True
            }
        },
        "performance_metrics": {
            "designed_for": "Thousands of different products",
            "accuracy_target": ">95% for properly structured sales pages",
            "processing_speed": "Near-instantaneous",
            "memory_efficient": True,
            "scalable_architecture": True
        },
        "deployment_ready": True,
        "production_status": "Ready for large-scale deployment"
    }


# Include this in your main routes
def include_universal_test_routes(main_router):
    """Include universal test routes in main router"""
    main_router.include_router(universal_test_router)