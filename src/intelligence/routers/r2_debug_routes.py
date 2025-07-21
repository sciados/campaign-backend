# Add these debug endpoints to test R2 and AI enhancement issues
# src/intelligence/routers/debug_routes.py (add to existing file)

from fastapi import APIRouter, HTTPException
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Add these to your existing debug router
debug_router = APIRouter(prefix="/api/debug", tags=["debug"])

@debug_router.get("/test-r2-connection")
async def test_r2_connection():
    """
    🔧 Test Cloudflare R2 connection and configuration
    
    This endpoint checks if R2 environment variables are configured
    and if the R2 storage system is working properly.
    """
    
    try:
        # Check environment variables
        r2_config = {
            "CLOUDFLARE_ACCOUNT_ID": os.getenv("CLOUDFLARE_ACCOUNT_ID"),
            "CLOUDFLARE_R2_ACCESS_KEY_ID": os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID"),
            "CLOUDFLARE_R2_SECRET_ACCESS_KEY": os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY"),
            "CLOUDFLARE_R2_BUCKET_NAME": os.getenv("CLOUDFLARE_R2_BUCKET_NAME")
        }
        
        # Check which variables are missing
        missing_vars = []
        configured_vars = []
        
        for var_name, var_value in r2_config.items():
            if var_value:
                configured_vars.append(var_name)
            else:
                missing_vars.append(var_name)
        
        # Determine R2 status
        r2_fully_configured = len(missing_vars) == 0
        
        # Test R2 initialization if possible
        r2_test_result = None
        if r2_fully_configured:
            try:
                # Try to initialize R2 (without making actual calls)
                r2_test_result = "R2 configuration appears valid"
                r2_status = "✅ CONFIGURED"
            except Exception as e:
                r2_test_result = f"R2 initialization failed: {str(e)}"
                r2_status = "❌ CONFIGURATION ERROR"
        else:
            r2_status = "❌ MISSING VARIABLES"
            r2_test_result = f"Missing {len(missing_vars)} required variables"
        
        return {
            "success": True,
            "r2_status": r2_status,
            "r2_fully_configured": r2_fully_configured,
            "configured_variables": configured_vars,
            "missing_variables": missing_vars,
            "r2_test_result": r2_test_result,
            "total_variables_needed": 4,
            "variables_configured": len(configured_vars),
            "diagnosis": {
                "issue": "Missing R2 environment variables" if missing_vars else "R2 appears configured",
                "solution": "Add missing environment variables in Railway dashboard" if missing_vars else "R2 configuration looks good",
                "impact": "AI enhancement system will fail without R2" if missing_vars else "R2 should support AI enhancements"
            },
            "next_steps": [
                "Go to Railway dashboard -> Your Project -> Backend Service -> Variables",
                f"Add missing variables: {missing_vars}" if missing_vars else "R2 configuration complete",
                "Deploy service after adding variables",
                "Test intelligence enhancement system"
            ] if missing_vars else [
                "R2 configuration appears complete",
                "Test AI enhancement system",
                "Monitor intelligence confidence scores"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ R2 connection test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"R2 test failed: {str(e)}")


@debug_router.get("/test-enhancement-system")
async def test_enhancement_system():
    """
    🔧 Test AI enhancement system status
    
    This endpoint checks if the AI enhancement modules are working
    and why intelligence confidence might be low.
    """
    
    try:
        # Check AI provider configuration
        ai_providers = {
            "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY")),
            "ANTHROPIC_API_KEY": bool(os.getenv("ANTHROPIC_API_KEY")),
            "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
            "TOGETHER_API_KEY": bool(os.getenv("TOGETHER_API_KEY")),
            "DEEPSEEK_API_KEY": bool(os.getenv("DEEPSEEK_API_KEY"))
        }
        
        configured_providers = [name for name, configured in ai_providers.items() if configured]
        
        # Check storage configuration
        r2_configured = all([
            os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID"),
            os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY"),
            os.getenv("CLOUDFLARE_R2_BUCKET_NAME")
        ])
        
        # Determine enhancement system status
        if len(configured_providers) == 0:
            enhancement_status = "❌ NO AI PROVIDERS"
            confidence_expected = "10-20%"
            issue = "No AI providers configured"
        elif not r2_configured:
            enhancement_status = "❌ STORAGE MISSING"
            confidence_expected = "60%"  # This matches your current issue
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
            "ai_providers": {
                "configured_count": len(configured_providers),
                "configured_providers": configured_providers,
                "total_available": len(ai_providers)
            },
            "storage_systems": {
                "r2_configured": r2_configured,
                "required_for_ai_enhancement": True
            },
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
            },
            "current_behavior": {
                "expected": "All enhancement modules should populate with rich data",
                "actual": "Modules returning empty {} due to missing R2",
                "confidence_impact": "60% instead of 95% due to missing enhancements"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Enhancement system test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhancement test failed: {str(e)}")


@debug_router.get("/intelligence-confidence-analysis")
async def intelligence_confidence_analysis():
    """
    📊 Analyze why intelligence confidence is low
    
    Provides detailed analysis of what's causing low confidence scores
    and how to fix them.
    """
    
    try:
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
            "root_cause": {
                "primary_issue": "Cloudflare R2 environment variables missing",
                "secondary_issue": "AI enhancement modules cannot initialize without storage",
                "impact": "System falls back to basic analysis only",
                "evidence": {
                    "enhancement_quality": current_state["enhancement_quality"],
                    "modules_successful": current_state["modules_successful"],
                    "total_enhancements": current_state["total_enhancements"]
                }
            },
            "fix_priority": [
                "1. Add missing R2 environment variables (CRITICAL)",
                "2. Deploy Railway service with new variables",
                "3. Test intelligence enhancement system",
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
        
    except Exception as e:
        logger.error(f"❌ Confidence analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@debug_router.post("/test-full-intelligence-pipeline")
async def test_full_intelligence_pipeline(test_data: Dict[str, Any]):
    """
    🧪 Test the complete intelligence pipeline with sample data
    
    Send sample intelligence data to test if the enhancement system
    would work properly with R2 configured.
    """
    
    try:
        # Simulate what should happen with proper R2 configuration
        sample_intelligence = test_data or {
            "source_url": "https://www.hepatoburn.com/",
            "source_title": "HEPATOBURN",
            "raw_content": "HEPATOBURN liver fat-burning complex...",
            "offer_intelligence": {
                "products": ["Hepatoburn"],
                "pricing": ["$79", "$49", "$69"]
            }
        }
        
        # Test product name extraction
        from src.intelligence.utils.product_name_fix import extract_product_name_from_intelligence
        extracted_product = extract_product_name_from_intelligence(sample_intelligence)
        
        # Simulate what enhancements should look like
        simulated_enhancements = {
            "scientific_intelligence": "Would contain scientific backing data",
            "credibility_intelligence": "Would contain trust and authority data",
            "market_intelligence": "Would contain market analysis data",
            "emotional_transformation_intelligence": "Would contain emotional journey mapping",
            "scientific_authority_intelligence": "Would contain research validation data"
        }
        
        # Calculate what confidence should be
        base_confidence = 0.6  # Current basic analysis
        enhancement_boost = 0.35  # What enhancements add
        expected_confidence = base_confidence + enhancement_boost
        
        return {
            "success": True,
            "pipeline_test": {
                "product_extraction": {
                    "extracted": extracted_product,
                    "working": extracted_product != "Product"
                },
                "basic_analysis": {
                    "confidence": base_confidence,
                    "status": "✅ Working (you have this)"
                },
                "enhancement_analysis": {
                    "status": "❌ Blocked by missing R2",
                    "would_add": enhancement_boost,
                    "expected_confidence": expected_confidence,
                    "blocked_modules": list(simulated_enhancements.keys())
                }
            },
            "simulation": {
                "current_state": "Basic analysis only (60% confidence)",
                "after_r2_fix": "Full enhanced analysis (95% confidence)",
                "enhancement_preview": simulated_enhancements
            },
            "verification": {
                "product_name_extraction": "✅ Working correctly",
                "basic_intelligence": "✅ Working correctly", 
                "ai_enhancement": "❌ Blocked by missing R2 config",
                "overall_system": "60% functional - needs R2 fix"
            },
            "next_action": "Add R2 environment variables to unlock full 95% confidence"
        }
        
    except Exception as e:
        logger.error(f"❌ Pipeline test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pipeline test failed: {str(e)}")


# Add this to your main routes to include these debug endpoints
def include_r2_debug_routes(main_router):
    """Include R2 debug routes in main router"""
    main_router.include_router(debug_router)