# src/intelligence/amplifier/ai_providers.py - ENHANCED WITH DEBUG LOGGING
"""
AI Provider initialization for Intelligence Amplifier and Content Generation
✅ ENHANCED: Added Anthropic Claude support alongside OpenAI + Debug Logging
"""
import os
import logging

logger = logging.getLogger(__name__)

def initialize_ai_providers():
    """Initialize multiple AI providers for redundancy and enhanced capabilities"""
    
    providers = []
    
    logger.info("🚀 STARTING AI PROVIDER INITIALIZATION...")
    
    # ============================================================================
    # OPENAI GPT PROVIDER
    # ============================================================================
    logger.info("🔍 Checking OpenAI provider...")
    try:
        import openai
        logger.info(f"✅ OpenAI library imported successfully (version: {openai.__version__})")
        
        api_key = os.getenv("OPENAI_API_KEY")
        logger.info(f"🔑 OpenAI API key present: {bool(api_key)}")
        
        if api_key:
            logger.info(f"🔑 OpenAI key length: {len(api_key)} characters")
            logger.info(f"🔑 OpenAI key format: {api_key[:10]}...")
            
            if not api_key.startswith("sk-"):
                logger.warning(f"⚠️ OpenAI key doesn't start with 'sk-' (starts with: {api_key[:10]})")
            
            # Test client creation
            client = openai.AsyncOpenAI(api_key=api_key)
            logger.info("✅ OpenAI client created successfully")
            
            provider = {
                "name": "openai",
                "client": client,
                "models": ["gpt-4", "gpt-3.5-turbo"],
                "available": True,
                "capabilities": [
                    "email_sequences",
                    "blog_posts", 
                    "ad_copy",
                    "sales_pages",
                    "SOCIAL_POSTS"
                ],
                "cost_per_1k_tokens": 0.03,
                "strengths": [
                    "High-quality content generation",
                    "Complex reasoning and analysis",
                    "Creative writing capabilities"
                ]
            }
            providers.append(provider)
            logger.info("✅ OpenAI provider successfully added to providers list")
        else:
            logger.warning("⚠️ OPENAI_API_KEY not found in environment variables")
    except ImportError as e:
        logger.error(f"❌ OpenAI library not installed: {str(e)}")
    except Exception as e:
        logger.error(f"❌ OpenAI initialization failed: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    # ============================================================================
    # ANTHROPIC CLAUDE PROVIDER  
    # ============================================================================
    logger.info("🔍 Checking Anthropic provider...")
    try:
        import anthropic
        logger.info(f"✅ Anthropic library imported successfully (version: {anthropic.__version__})")
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        logger.info(f"🔑 Anthropic API key present: {bool(api_key)}")
        
        if api_key:
            logger.info(f"🔑 Anthropic key length: {len(api_key)} characters")
            logger.info(f"🔑 Anthropic key format: {api_key[:15]}...")
            
            if not api_key.startswith("sk-ant-"):
                logger.warning(f"⚠️ Anthropic key doesn't start with 'sk-ant-' (starts with: {api_key[:15]})")
            
            # Test client creation
            client = anthropic.AsyncAnthropic(api_key=api_key)
            logger.info("✅ Anthropic client created successfully")
            
            provider = {
                "name": "anthropic",
                "client": client,
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
                "cost_per_1k_tokens": 0.015,
                "strengths": [
                    "Excellent long-form content",
                    "Scientific and technical writing", 
                    "200K context window",
                    "Superior reasoning capabilities",
                    "Cost-effective for long content"
                ]
            }
            providers.append(provider)
            logger.info("✅ Anthropic provider successfully added to providers list")
        else:
            logger.warning("⚠️ ANTHROPIC_API_KEY not found in environment variables")
    except ImportError as e:
        logger.warning(f"⚠️ Anthropic library not installed: {str(e)}")
        logger.info("💡 Run: pip install anthropic")
    except Exception as e:
        logger.error(f"❌ Anthropic initialization failed: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    # ============================================================================
    # COHERE PROVIDER (OPTIONAL - HIGH VOLUME, LOW COST)
    # ============================================================================
    logger.info("🔍 Checking Cohere provider...")
    try:
        import cohere
        logger.info("✅ Cohere library imported successfully")
        
        api_key = os.getenv("COHERE_API_KEY")
        logger.info(f"🔑 Cohere API key present: {bool(api_key)}")
        
        if api_key:
            logger.info(f"🔑 Cohere key length: {len(api_key)} characters")
            
            # Test client creation
            client = cohere.AsyncClient(api_key=api_key)
            logger.info("✅ Cohere client created successfully")
            
            provider = {
                "name": "cohere",
                "client": client,
                "models": [
                    "command",         # Best quality
                    "command-light",   # Faster and cheaper
                    "command-nightly"  # Latest experimental
                ],
                "available": True,
                "capabilities": [
                    "SOCIAL_POSTS",
                    "product_descriptions", 
                    "short_form_content",
                    "high_volume_generation",
                    "summarization"
                ],
                "cost_per_1k_tokens": 0.002,
                "strengths": [
                    "Extremely cost-effective",
                    "Fast generation",
                    "Good for high-volume content",
                    "Excellent for social media"
                ]
            }
            providers.append(provider)
            logger.info("✅ Cohere provider successfully added to providers list")
        else:
            logger.info("💡 COHERE_API_KEY not found - Cohere provides very cost-effective content generation")
    except ImportError as e:
        logger.info(f"💡 Cohere library not installed: {str(e)}")
        logger.info("💡 Run: pip install cohere")
    except Exception as e:
        logger.error(f"❌ Cohere initialization failed: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    # ============================================================================
    # FINAL RESULTS AND SUMMARY
    # ============================================================================
    
    logger.info(f"📊 PROVIDERS INITIALIZATION COMPLETE")
    logger.info(f"📊 Total providers initialized: {len(providers)}")
    logger.info(f"📋 Provider names: {[p['name'] for p in providers]}")
    
    if providers:
        logger.info(f"🚀 SUCCESS: Initialized {len(providers)} AI provider(s)")
        
        # Log provider recommendations
        provider_names = [p['name'] for p in providers]
        
        for provider in providers:
            logger.info(f"   ✅ {provider['name']}: {len(provider['models'])} models available")
        
        if 'openai' in provider_names and 'anthropic' in provider_names:
            logger.info("🎯 OPTIMAL SETUP: OpenAI + Claude provides excellent redundancy and capabilities")
        elif 'openai' in provider_names:
            logger.info("✅ GOOD SETUP: OpenAI available. Consider adding Claude for 50% cost savings on long content")
        elif 'anthropic' in provider_names:
            logger.info("✅ GOOD SETUP: Claude available. Consider adding OpenAI for content variety")
        
        if 'cohere' not in provider_names:
            logger.info("💡 OPTIMIZATION: Consider adding Cohere for 90% cost savings on social media content")
            
        # Log what enhancement modules will receive
        logger.info(f"🔗 Enhancement modules will receive {len(providers)} providers:")
        for provider in providers:
            logger.info(f"   🔗 {provider['name']}: Available with {len(provider.get('capabilities', []))} capabilities")
            
    else:
        logger.error("❌ CRITICAL: NO AI PROVIDERS AVAILABLE!")
        logger.error("🔧 Enhancement modules will receive empty providers list")
        logger.error("🔧 This will cause fallback to mock data with unrealistic confidence scores")
        logger.error("🔧 Check environment variables and API key formats above")
        
        # Debug environment variables
        logger.error("🔍 Environment variable debug:")
        for var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "COHERE_API_KEY"]:
            value = os.getenv(var)
            if value:
                logger.error(f"   🔍 {var}: Present (length: {len(value)}, starts: {value[:8]})")
            else:
                logger.error(f"   🔍 {var}: Missing")
    
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
                "use_cases": ["SOCIAL_POSTS", "product_descriptions", "high_volume"],
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


# Add direct test capability
if __name__ == "__main__":
    print("🔍 TESTING AI PROVIDER INITIALIZATION DIRECTLY...")
    providers = initialize_ai_providers()
    print(f"\n📊 FINAL RESULT: {len(providers)} providers")
    for provider in providers:
        print(f"   ✅ {provider['name']}: {provider.get('available', False)}")