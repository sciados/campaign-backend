# src/intelligence/test_routes.py - EMAIL SERIES ONLY Testing
"""
Web-based test endpoints for affiliate EMAIL SERIES testing only
Focus on getting email generation working first, then add other content types
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, Any
import json
import asyncio
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)

# Import your intelligence modules
try:
    from src.intelligence.analyzers import SalesPageAnalyzer
    from src.intelligence.generators import ContentGenerator
    MODULES_AVAILABLE = True
    logger.info("✅ Intelligence modules imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import intelligence modules: {str(e)}")
    MODULES_AVAILABLE = False

router = APIRouter(prefix="/test", tags=["testing"])

@router.get("/", response_class=HTMLResponse)
async def test_dashboard():
    """Test dashboard - EMAIL SERIES focused testing"""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CampaignForge Email Series Test Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; margin-bottom: 30px; }
            .test-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 6px; }
            .test-button { 
                background: #007bff; color: white; padding: 12px 24px; border: none; 
                border-radius: 6px; cursor: pointer; margin: 10px 5px; font-size: 16px;
                text-decoration: none; display: inline-block;
            }
            .test-button:hover { background: #0056b3; }
            .test-button.success { background: #28a745; }
            .test-button.secondary { background: #6c757d; }
            .description { color: #666; margin-bottom: 15px; }
            .focus-note { background: #fff3cd; color: #856404; padding: 15px; border-radius: 4px; margin-bottom: 20px; border: 1px solid #ffeaa7; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📧 CampaignForge Email Series Test Dashboard</h1>
            <p style="text-align: center; color: #666;">Test your affiliate email intelligence transformation</p>
            
            <div class="focus-note">
                <strong>🎯 Current Focus:</strong> Email series generation only. Once this is working perfectly, we'll add other content types one by one.
            </div>
            
            <div class="test-section">
                <h2>📊 System Status</h2>
                <div class="description">Check if email generation modules are properly imported and working</div>
                <a href="/test/status" class="test-button">Check System Status</a>
            </div>
            
            <div class="test-section">
                <h2>🚀 Quick Email Test (Recommended)</h2>
                <div class="description">Test affiliate email series with mock data - safe and fast</div>
                <a href="/test/email-quick" class="test-button success">Run Quick Email Test</a>
            </div>
            
            <div class="test-section">
                <h2>📧 Affiliate vs Generic Comparison</h2>
                <div class="description">Compare affiliate-specific email generation vs generic templates</div>
                <a href="/test/email-comparison" class="test-button">Compare Email Generation</a>
            </div>
            
            <div class="test-section">
                <h2>🔍 Intelligence Analysis Test</h2>
                <div class="description">Test URL analysis that feeds into email generation</div>
                <a href="/test/analysis" class="test-button secondary">Test Intelligence Analysis</a>
            </div>
            
            <div class="test-section">
                <h2>📈 Full Email Integration Test</h2>
                <div class="description">Complete test: Analysis → Intelligence → Email Generation</div>
                <a href="/test/full-email" class="test-button">Run Full Email Test</a>
            </div>
            
            <div class="test-section">
                <h2>🔧 Debug Information</h2>
                <div class="description">View detailed system information for email generation</div>
                <a href="/test/debug" class="test-button secondary">View Debug Info</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@router.get("/status")
async def system_status():
    """Check system status - EMAIL FOCUSED"""
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "modules_available": MODULES_AVAILABLE,
        "focus": "email_series_only",
        "tests": {}
    }
    
    if MODULES_AVAILABLE:
        try:
            analyzer = SalesPageAnalyzer()
            generator = ContentGenerator()
            
            status["tests"]["analyzer_instantiation"] = "✅ Success"
            status["tests"]["generator_instantiation"] = "✅ Success"
            status["tests"]["ai_available"] = "✅ Available" if generator.ai_available else "⚠️ Template mode"
            
            # Check if email_sequence generator exists
            if "email_sequence" in generator.generators:
                status["tests"]["email_generator_available"] = "✅ Available"
            else:
                status["tests"]["email_generator_available"] = "❌ Missing"
            
        except Exception as e:
            status["tests"]["instantiation_error"] = f"❌ {str(e)}"
    else:
        status["tests"]["import_error"] = "❌ Modules not available"
    
    return status

@router.get("/email-quick")
async def quick_email_test():
    """Quick email series test with mock data - MAIN TEST"""
    
    if not MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Intelligence modules not available")
    
    try:
        generator = ContentGenerator()
        
        # Mock affiliate intelligence data focused on email generation
        mock_intelligence = {
            "psychology_intelligence": {
                "emotional_triggers": ["proven", "exclusive", "breakthrough", "limited"],
                "pain_points": [
                    "low conversion rates from affiliate promotions",
                    "fierce competition from other affiliates", 
                    "lack of unique promotional angles",
                    "difficulty standing out in crowded market"
                ],
                "target_audience": "affiliate marketers",
                "persuasion_techniques": ["social proof", "urgency", "authority", "scarcity"]
            },
            "offer_intelligence": {
                "products": [
                    "weight loss supplement with clinical backing",
                    "90-day transformation program", 
                    "exclusive bonus package"
                ],
                "value_propositions": [
                    "scientifically proven rapid results",
                    "money-back guarantee", 
                    "personal coaching included",
                    "exclusive member community"
                ],
                "pricing": ["$97", "$197", "$297"],
                "bonuses": ["meal plans", "workout videos", "progress tracker"]
            },
            "competitive_intelligence": {
                "opportunities": [
                    "focus on long-term health vs quick fixes",
                    "emphasize safety and natural ingredients",
                    "target specific demographics (busy professionals)",
                    "provide ongoing support vs one-time purchase"
                ],
                "gaps": [
                    "lack of personalization in competitor offers",
                    "no ongoing support after purchase",
                    "generic testimonials without specifics",
                    "focus only on weight loss, not overall health"
                ],
                "positioning": "premium health transformation",
                "advantages": ["scientific backing", "personalized approach", "ongoing support"]
            },
            "content_intelligence": {
                "key_messages": [
                    "transform your health naturally",
                    "scientifically proven system",
                    "personalized approach for lasting results"
                ],
                "success_stories": [
                    "Lost 30 pounds in 90 days safely",
                    "Increased energy and confidence",
                    "Maintained results for 2+ years"
                ],
                "social_proof": ["10,000+ success stories", "featured in health magazines", "doctor recommended"]
            },
            "brand_intelligence": {
                "tone_voice": "professional yet approachable",
                "messaging_style": "educational with proof",
                "brand_positioning": "trusted health transformation expert"
            },
            "confidence_score": 0.85,
            "source_url": "mock://affiliate-product-test",
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Test affiliate email generation
        affiliate_preferences = {
            "tone": "conversational",
            "length": "5", 
            "audience": "health-conscious adults",
            "user_type": "affiliate"
        }
        
        logger.info("🧪 Starting affiliate email generation test...")
        
        email_result = await generator.generate_content(
            intelligence_data=mock_intelligence,
            content_type="email_sequence",
            preferences=affiliate_preferences
        )
        
        logger.info("✅ Email generation completed")
        
        # Detailed analysis of results
        analysis = {
            "test_type": "quick_email_test",
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "intelligence_data_quality": {
                "emotional_triggers_count": len(mock_intelligence["psychology_intelligence"]["emotional_triggers"]),
                "pain_points_count": len(mock_intelligence["psychology_intelligence"]["pain_points"]),
                "opportunities_count": len(mock_intelligence["competitive_intelligence"]["opportunities"]),
                "gaps_count": len(mock_intelligence["competitive_intelligence"]["gaps"]),
                "confidence_score": mock_intelligence["confidence_score"]
            },
            "email_generation_results": {
                "content_type": email_result.get("content_type"),
                "title": email_result.get("title"),
                "generated_by": email_result.get("metadata", {}).get("generated_by"),
                "emails_generated": len(email_result.get("content", {}).get("emails", [])),
                "has_affiliate_intelligence": bool(email_result.get("affiliate_intelligence")),
                "affiliate_intelligence_details": email_result.get("affiliate_intelligence", {})
            },
            "sample_emails": []
        }
        
        # Add sample emails with affiliate focus analysis
        emails = email_result.get("content", {}).get("emails", [])
        for i, email in enumerate(emails[:3], 1):  # Show first 3 emails
            sample = {
                "email_number": i,
                "subject": email.get("subject", "No subject"),
                "body_preview": email.get("body", "No body")[:150] + "...",
                "affiliate_focus": email.get("affiliate_focus", "No affiliate focus specified"),
                "send_delay": email.get("send_delay", "No delay specified"),
                "has_affiliate_elements": bool(email.get("affiliate_focus"))
            }
            analysis["sample_emails"].append(sample)
        
        # Calculate detailed score
        score = 0
        max_score = 10
        score_breakdown = {}
        
        # Check for affiliate intelligence integration (4 points)
        affiliate_intel = email_result.get("affiliate_intelligence", {})
        if affiliate_intel:
            score += 2
            score_breakdown["affiliate_intelligence_present"] = "✅ +2 points"
            
            unique_positioning = len(affiliate_intel.get("unique_positioning", []))
            if unique_positioning > 0:
                score += 1
                score_breakdown["unique_positioning"] = f"✅ +1 point ({unique_positioning} angles)"
            else:
                score_breakdown["unique_positioning"] = "❌ +0 points (no unique positioning)"
            
            avoided_cliches = len(affiliate_intel.get("avoided_cliches", []))
            if avoided_cliches > 0:
                score += 1
                score_breakdown["avoided_cliches"] = f"✅ +1 point ({avoided_cliches} cliches avoided)"
            else:
                score_breakdown["avoided_cliches"] = "❌ +0 points (no cliche avoidance)"
        else:
            score_breakdown["affiliate_intelligence_present"] = "❌ +0 points (no affiliate intelligence)"
            score_breakdown["unique_positioning"] = "❌ +0 points (no affiliate intelligence)"
            score_breakdown["avoided_cliches"] = "❌ +0 points (no affiliate intelligence)"
        
        # Check generation method (2 points)
        generated_by = email_result.get("metadata", {}).get("generated_by", "")
        if "affiliate" in generated_by.lower():
            score += 2
            score_breakdown["generation_method"] = f"✅ +2 points (using {generated_by})"
        else:
            score_breakdown["generation_method"] = f"❌ +0 points (using {generated_by})"
        
        # Check email quality (2 points)
        if emails and len(emails) >= 3:
            score += 1
            score_breakdown["email_count"] = f"✅ +1 point ({len(emails)} emails generated)"
        else:
            score_breakdown["email_count"] = f"❌ +0 points ({len(emails)} emails generated)"
        
        # Check for affiliate-specific focus (2 points)
        emails_with_focus = len([e for e in emails if e.get("affiliate_focus")])
        if emails_with_focus > 0:
            score += 1
            score_breakdown["affiliate_focus"] = f"✅ +1 point ({emails_with_focus}/{len(emails)} emails have affiliate focus)"
        else:
            score_breakdown["affiliate_focus"] = "❌ +0 points (no emails have affiliate focus)"
        
        # Performance predictions check (1 point)
        performance_predictions = email_result.get("performance_predictions", {})
        if performance_predictions:
            score += 1
            score_breakdown["performance_predictions"] = "✅ +1 point (performance predictions included)"
        else:
            score_breakdown["performance_predictions"] = "❌ +0 points (no performance predictions)"
        
        analysis["score_breakdown"] = score_breakdown
        analysis["final_score"] = f"{score}/{max_score}"
        
        # Overall assessment
        if score >= 8:
            analysis["assessment"] = "🎉 EXCELLENT - Ready for Step 3!"
            analysis["recommendation"] = "Affiliate email intelligence is working perfectly. Ready to implement usage tracking and tiered pricing."
        elif score >= 6:
            analysis["assessment"] = "✅ GOOD - Minor improvements needed"
            analysis["recommendation"] = "Most features working well. Fix remaining issues then proceed to Step 3."
        elif score >= 4:
            analysis["assessment"] = "⚠️ PARTIAL - Significant improvements needed"
            analysis["recommendation"] = "Some intelligence integration working. Need to fix generation method and affiliate focus."
        else:
            analysis["assessment"] = "❌ POOR - Major fixes required"
            analysis["recommendation"] = "Intelligence integration not working. Check generators.py implementation."
        
        return {
            "analysis": analysis,
            "full_email_result": email_result,
            "mock_intelligence_used": mock_intelligence
        }
        
    except Exception as e:
        logger.error(f"Quick email test failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/email-comparison")
async def email_comparison_test():
    """Compare affiliate vs generic email generation"""
    
    if not MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Intelligence modules not available")
    
    try:
        generator = ContentGenerator()
        
        # Simple mock data for comparison
        mock_data = {
            "psychology_intelligence": {
                "emotional_triggers": ["proven", "exclusive"],
                "pain_points": ["low conversions", "competition"]
            },
            "offer_intelligence": {
                "products": ["affiliate product"],
                "value_propositions": ["higher commissions"]
            },
            "competitive_intelligence": {
                "opportunities": ["unique angle", "honest approach"],
                "gaps": ["lack of authenticity"]
            }
        }
        
        # Test both affiliate and generic
        tests = [
            {
                "name": "Affiliate Email Sequence",
                "preferences": {
                    "tone": "conversational", 
                    "user_type": "affiliate", 
                    "length": "3",
                    "audience": "health enthusiasts"
                }
            },
            {
                "name": "Generic Email Sequence", 
                "preferences": {
                    "tone": "conversational", 
                    "length": "3",
                    "audience": "health enthusiasts"
                }
            }
        ]
        
        results = []
        
        for test in tests:
            logger.info(f"🧪 Testing {test['name']}...")
            
            result = await generator.generate_content(
                intelligence_data=mock_data,
                content_type="email_sequence",
                preferences=test["preferences"]
            )
            
            emails = result.get("content", {}).get("emails", [])
            
            test_result = {
                "test_name": test["name"],
                "generated_by": result.get("metadata", {}).get("generated_by"),
                "has_affiliate_intelligence": bool(result.get("affiliate_intelligence")),
                "emails_count": len(emails),
                "sample_subject": emails[0].get("subject", "N/A") if emails else "N/A",
                "sample_body_preview": emails[0].get("body", "N/A")[:100] + "..." if emails else "N/A",
                "affiliate_focus": emails[0].get("affiliate_focus", "N/A") if emails else "N/A",
                "full_result": result
            }
            
            results.append(test_result)
        
        # Comparison analysis
        comparison = {
            "different_generation_methods": results[0]["generated_by"] != results[1]["generated_by"],
            "affiliate_specific_features": results[0]["has_affiliate_intelligence"] and not results[1]["has_affiliate_intelligence"],
            "subject_line_differences": results[0]["sample_subject"] != results[1]["sample_subject"],
            "content_differences": results[0]["sample_body_preview"] != results[1]["sample_body_preview"]
        }
        
        return {
            "test_type": "email_comparison",
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "comparison": comparison,
            "analysis": {
                "differentiation_working": comparison["different_generation_methods"] and comparison["affiliate_specific_features"],
                "recommendation": "Good differentiation" if comparison["affiliate_specific_features"] else "Need to improve affiliate differentiation"
            }
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/analysis")
async def test_intelligence_analysis():
    """Test intelligence analysis that feeds email generation"""
    
    if not MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Intelligence modules not available")
    
    try:
        analyzer = SalesPageAnalyzer()
        
        # Test with a simple URL
        test_url = "https://example.com"
        
        logger.info(f"🧪 Testing intelligence analysis for {test_url}")
        
        analysis_result = await analyzer.analyze(test_url)
        
        # Analyze the quality of intelligence for email generation
        email_intelligence_quality = {
            "psychology_intelligence": {
                "has_emotional_triggers": bool(analysis_result.get("psychology_intelligence", {}).get("emotional_triggers")),
                "has_pain_points": bool(analysis_result.get("psychology_intelligence", {}).get("pain_points")),
                "triggers_count": len(analysis_result.get("psychology_intelligence", {}).get("emotional_triggers", [])),
                "pain_points_count": len(analysis_result.get("psychology_intelligence", {}).get("pain_points", []))
            },
            "competitive_intelligence": {
                "has_opportunities": bool(analysis_result.get("competitive_intelligence", {}).get("opportunities")),
                "has_gaps": bool(analysis_result.get("competitive_intelligence", {}).get("gaps")),
                "opportunities_count": len(analysis_result.get("competitive_intelligence", {}).get("opportunities", [])),
                "gaps_count": len(analysis_result.get("competitive_intelligence", {}).get("gaps", []))
            },
            "offer_intelligence": {
                "has_products": bool(analysis_result.get("offer_intelligence", {}).get("products")),
                "has_value_props": bool(analysis_result.get("offer_intelligence", {}).get("value_propositions")),
                "products_count": len(analysis_result.get("offer_intelligence", {}).get("products", [])),
                "value_props_count": len(analysis_result.get("offer_intelligence", {}).get("value_propositions", []))
            }
        }
        
        return {
            "test_type": "intelligence_analysis",
            "timestamp": datetime.now().isoformat(),
            "test_url": test_url,
            "analysis_result": analysis_result,
            "email_intelligence_quality": email_intelligence_quality,
            "overall_assessment": {
                "confidence_score": analysis_result.get("confidence_score", 0.0),
                "suitable_for_email_generation": analysis_result.get("confidence_score", 0.0) > 0.3,
                "intelligence_richness": "High" if analysis_result.get("confidence_score", 0.0) > 0.7 else "Medium" if analysis_result.get("confidence_score", 0.0) > 0.4 else "Low"
            }
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/full-email")
async def full_email_integration_test():
    """Complete email integration test: Analysis → Intelligence → Email Generation"""
    
    if not MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Intelligence modules not available")
    
    try:
        analyzer = SalesPageAnalyzer()
        generator = ContentGenerator()
        
        test_results = {
            "test_type": "full_email_integration",
            "timestamp": datetime.now().isoformat(),
            "stages": {}
        }
        
        # Stage 1: Intelligence Analysis
        logger.info("🧪 Stage 1: Intelligence Analysis")
        test_results["stages"]["1_intelligence_analysis"] = {
            "status": "running",
            "description": "Analyzing competitor URL for intelligence"
        }
        
        try:
            test_url = "https://example.com"
            intelligence_data = await analyzer.analyze(test_url)
            
            test_results["stages"]["1_intelligence_analysis"]["status"] = "completed"
            test_results["stages"]["1_intelligence_analysis"]["confidence"] = intelligence_data.get("confidence_score", 0.0)
            test_results["stages"]["1_intelligence_analysis"]["url"] = test_url
            
        except Exception as e:
            test_results["stages"]["1_intelligence_analysis"]["status"] = "failed"
            test_results["stages"]["1_intelligence_analysis"]["error"] = str(e)
            # Use mock data if analysis fails
            intelligence_data = {
                "psychology_intelligence": {"emotional_triggers": ["proven"], "pain_points": ["competition"]},
                "offer_intelligence": {"products": ["test product"], "value_propositions": ["results"]},
                "competitive_intelligence": {"opportunities": ["unique angle"], "gaps": ["authenticity"]},
                "confidence_score": 0.5
            }
        
        # Stage 2: Email Generation
        logger.info("🧪 Stage 2: Email Generation")
        test_results["stages"]["2_email_generation"] = {
            "status": "running",
            "description": "Generating affiliate email sequence from intelligence"
        }
        
        try:
            email_result = await generator.generate_content(
                intelligence_data=intelligence_data,
                content_type="email_sequence",
                preferences={"user_type": "affiliate", "tone": "conversational", "length": "3"}
            )
            
            test_results["stages"]["2_email_generation"]["status"] = "completed"
            test_results["stages"]["2_email_generation"]["emails_generated"] = len(email_result.get("content", {}).get("emails", []))
            test_results["stages"]["2_email_generation"]["has_affiliate_intelligence"] = bool(email_result.get("affiliate_intelligence"))
            test_results["stages"]["2_email_generation"]["generated_by"] = email_result.get("metadata", {}).get("generated_by")
            
        except Exception as e:
            test_results["stages"]["2_email_generation"]["status"] = "failed"
            test_results["stages"]["2_email_generation"]["error"] = str(e)
        
        # Overall Assessment
        completed_stages = len([s for s in test_results["stages"].values() if s["status"] == "completed"])
        total_stages = len(test_results["stages"])
        
        test_results["overall"] = {
            "completed_stages": f"{completed_stages}/{total_stages}",
            "success_rate": f"{(completed_stages/total_stages*100):.1f}%",
            "status": "success" if completed_stages == total_stages else "partial",
            "ready_for_step_3": completed_stages == total_stages and test_results["stages"]["2_email_generation"].get("has_affiliate_intelligence", False)
        }
        
        return test_results
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/debug")
async def debug_info():
    """Get debug information focused on email generation"""
    
    import sys
    import os
    
    debug_data = {
        "timestamp": datetime.now().isoformat(),
        "focus": "email_series_generation",
        "system_info": {
            "python_version": sys.version,
            "modules_available": MODULES_AVAILABLE
        },
        "environment": {
            "working_directory": os.getcwd(),
            "python_path": sys.path[:5]
        },
        "email_generation_status": {}
    }
    
    if MODULES_AVAILABLE:
        try:
            generator = ContentGenerator()
            debug_data["email_generation_status"]["generator_ai_available"] = generator.ai_available
            debug_data["email_generation_status"]["has_email_generator"] = "email_sequence" in generator.generators
            debug_data["email_generation_status"]["email_generator_method"] = str(generator.generators.get("email_sequence", "Not found"))
            
            # Try to instantiate the email generator method
            if "email_sequence" in generator.generators:
                debug_data["email_generation_status"]["email_method_callable"] = "Yes"
            else:
                debug_data["email_generation_status"]["email_method_callable"] = "No"
                
        except Exception as e:
            debug_data["email_generation_status"]["error"] = str(e)
    
    return debug_data