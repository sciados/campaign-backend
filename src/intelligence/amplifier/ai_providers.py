# src/intelligence/amplifier/ai_providers.py - ENHANCED WITH CLAUDE SUPPORT
"""
AI Provider initialization for Intelligence Amplifier and Content Generation
✅ ENHANCED: Added Anthropic Claude support alongside OpenAI
"""
import os
import logging

logger = logging.getLogger(__name__)

def initialize_ai_providers():
    """Initialize multiple AI providers for redundancy and enhanced capabilities"""
    
    providers = []
    
    # ============================================================================
    # OPENAI GPT PROVIDER
    # ============================================================================
    try:
        import openai
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            providers.append({
                "name": "openai",
                "client": openai.AsyncOpenAI(api_key=api_key),
                "models": ["gpt-4", "gpt-3.5-turbo"],
                "available": True,
                "capabilities": [
                    "email_sequences",
                    "blog_posts", 
                    "ad_copy",
                    "sales_pages",
                    "social_posts"
                ],
                "cost_per_1k_tokens": 0.03,  # GPT-4 pricing
                "strengths": [
                    "High-quality content generation",
                    "Complex reasoning and analysis",
                    "Creative writing capabilities"
                ]
            })
            logger.info("✅ OpenAI provider initialized successfully")
        else:
            logger.warning("⚠️ OPENAI_API_KEY not found in environment variables")
    except ImportError:
        logger.error("❌ OpenAI library not installed. Run: pip install openai")
    except Exception as e:
        logger.error(f"❌ OpenAI initialization failed: {str(e)}")
    
    # ============================================================================
    # ANTHROPIC CLAUDE PROVIDER  
    # ============================================================================
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            providers.append({
                "name": "anthropic",
                "client": anthropic.AsyncAnthropic(api_key=api_key),
                "models": [
                    "claude-3-5-sonnet-20241022",  # Latest and best
                    "claude-3-sonnet-20240229",    # Fallback
                    "claude-3-haiku-20240307"      # Fast and cheap
                ],
                "available": True,
                "capabilities": [
                    "long_form_content",
                    "blog_posts",
                    "scientific_writing",
                    "detailed_analysis",
                    "webinar_content",
                    "sales_pages"
                ],
                "cost_per_1k_tokens": 0.015,  # Claude 3.5 Sonnet pricing (50% cheaper than GPT-4)
                "strengths": [
                    "Excellent long-form content",
                    "Scientific and technical writing", 
                    "200K context window",
                    "Superior reasoning capabilities",
                    "Cost-effective for long content"
                ]
            })
            logger.info("✅ Anthropic Claude provider initialized successfully")
        else:
            logger.warning("⚠️ ANTHROPIC_API_KEY not found in environment variables")
    except ImportError:
        logger.warning("⚠️ Anthropic library not installed. Run: pip install anthropic")
        logger.info("💡 Claude would provide excellent long-form content and scientific writing")
    except Exception as e:
        logger.error(f"❌ Anthropic initialization failed: {str(e)}")
    
    # ============================================================================
    # COHERE PROVIDER (OPTIONAL - HIGH VOLUME, LOW COST)
    # ============================================================================
    try:
        import cohere
        api_key = os.getenv("COHERE_API_KEY")
        if api_key:
            providers.append({
                "name": "cohere",
                "client": cohere.AsyncClient(api_key=api_key),
                "models": [
                    "command",         # Best quality
                    "command-light",   # Faster and cheaper
                    "command-nightly"  # Latest experimental
                ],
                "available": True,
                "capabilities": [
                    "social_posts",
                    "product_descriptions", 
                    "short_form_content",
                    "high_volume_generation",
                    "summarization"
                ],
                "cost_per_1k_tokens": 0.002,  # Very cost-effective
                "strengths": [
                    "Extremely cost-effective",
                    "Fast generation",
                    "Good for high-volume content",
                    "Excellent for social media"
                ]
            })
            logger.info("✅ Cohere provider initialized successfully")
        else:
            logger.info("💡 COHERE_API_KEY not found - Cohere provides very cost-effective content generation")
    except ImportError:
        logger.info("💡 Cohere library not installed. Run: pip install cohere")
        logger.info("💡 Cohere would provide cost-effective social media and product descriptions")
    except Exception as e:
        logger.warning(f"⚠️ Cohere initialization failed: {str(e)}")
    
    # ============================================================================
    # PROVIDER SUMMARY AND RECOMMENDATIONS
    # ============================================================================
    
    if providers:
        logger.info(f"🚀 Initialized {len(providers)} AI provider(s): {[p['name'] for p in providers]}")
        
        # Log provider recommendations
        provider_names = [p['name'] for p in providers]
        
        if 'openai' in provider_names and 'anthropic' in provider_names:
            logger.info("🎯 OPTIMAL SETUP: OpenAI + Claude provides excellent redundancy and capabilities")
        elif 'openai' in provider_names:
            logger.info("✅ GOOD SETUP: OpenAI available. Consider adding Claude for 50% cost savings on long content")
        elif 'anthropic' in provider_names:
            logger.info("✅ GOOD SETUP: Claude available. Consider adding OpenAI for content variety")
        
        if 'cohere' not in provider_names:
            logger.info("💡 OPTIMIZATION: Consider adding Cohere for 90% cost savings on social media content")
    else:
        logger.error("❌ NO AI PROVIDERS AVAILABLE - Content generation will use emergency fallback")
        logger.error("🔧 Add at least OPENAI_API_KEY or ANTHROPIC_API_KEY to environment variables")
    
    return providers

def get_provider_recommendations():
    """Get recommendations for AI provider setup"""
    
    return {
        "essential_providers": {
            "openai": {
                "priority": "high",
                "use_cases": ["email_sequences", "ad_copy", "sales_pages"],
                "setup_url": "https://platform.openai.com/api-keys",
                "cost": "$0.03 per 1K tokens (GPT-4)",
                "why": "Industry standard, excellent quality, versatile"
            },
            "anthropic": {
                "priority": "high", 
                "use_cases": ["blog_posts", "long_content", "scientific_writing"],
                "setup_url": "https://console.anthropic.com",
                "cost": "$0.015 per 1K tokens (50% cheaper than GPT-4)",
                "why": "Superior long-form content, scientific writing, cost-effective"
            }
        },
        "optional_providers": {
            "cohere": {
                "priority": "medium",
                "use_cases": ["social_posts", "product_descriptions", "high_volume"],
                "setup_url": "https://dashboard.cohere.ai",
                "cost": "$0.002 per 1K tokens (90% cheaper)",
                "why": "Extremely cost-effective for high-volume content"
            }
        },
        "recommended_setup": {
            "minimal": ["openai"],
            "optimal": ["openai", "anthropic"], 
            "enterprise": ["openai", "anthropic", "cohere"]
        }
    }

def check_provider_availability():
    """Check which providers are available and provide setup guidance"""
    
    providers = initialize_ai_providers()
    available_providers = [p['name'] for p in providers]
    
    status = {
        "providers_available": len(providers),
        "providers_list": available_providers,
        "openai_available": "openai" in available_providers,
        "anthropic_available": "anthropic" in available_providers,
        "cohere_available": "cohere" in available_providers,
        "setup_complete": len(providers) >= 2,
        "recommendations": []
    }
    
    # Generate setup recommendations
    if not status["openai_available"] and not status["anthropic_available"]:
        status["recommendations"].append("🚨 URGENT: Add at least one AI provider (OpenAI or Anthropic)")
    
    if status["openai_available"] and not status["anthropic_available"]:
        status["recommendations"].append("💡 OPTIMIZE: Add Anthropic for 50% cost savings on long content")
    
    if status["anthropic_available"] and not status["openai_available"]:
        status["recommendations"].append("💡 ENHANCE: Add OpenAI for content variety and redundancy")
    
    if not status["cohere_available"]:
        status["recommendations"].append("💰 COST SAVING: Add Cohere for 90% savings on social content")
    
    if len(providers) >= 2:
        status["recommendations"].append("✅ EXCELLENT: Multiple providers ensure reliability and optimization")
    
    return status