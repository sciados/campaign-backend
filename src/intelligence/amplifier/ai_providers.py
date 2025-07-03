# src/intelligence/amplifier/ai_providers.py - ULTRA-CHEAP INTEGRATION
"""
AI Provider initialization for Intelligence Amplifier and Content Generation
✅ UPDATED: Added ULTRA-CHEAP providers (Groq, Together, Deepseek) for 95-99% cost savings
✅ ENHANCED: Cost optimization with provider prioritization
"""
import os
import logging

logger = logging.getLogger(__name__)

def initialize_ai_providers():
    """Initialize multiple AI providers with ULTRA-CHEAP optimization for 95-99% cost savings"""
    
    providers = []
    
    logger.info("🚀 STARTING ULTRA-CHEAP AI PROVIDER INITIALIZATION...")
    logger.info("💰 Target: 95-99% cost reduction vs OpenAI")
    
    # ============================================================================
    # PRIORITY 1: ULTRA-CHEAP PROVIDERS (Primary focus for cost optimization)
    # ============================================================================
    
    # GROQ - Ultra-fast and ultra-cheap (Priority 1)
    logger.info("🔍 Checking Groq provider (ULTRA-CHEAP #1)...")
    try:
        import groq
        logger.info(f"✅ Groq library imported successfully")
        
        api_key = os.getenv("GROQ_API_KEY")
        logger.info(f"🔑 Groq API key present: {bool(api_key)}")
        
        if api_key:
            logger.info(f"🔑 Groq key length: {len(api_key)} characters")
            
            # Test client creation
            client = groq.AsyncGroq(api_key=api_key)
            logger.info("✅ Groq client created successfully")
            
            provider = {
                "name": "groq",
                "client": client,
                "models": [
                    "llama-3.1-70b-versatile",      # Best for complex tasks
                    "llama-3.1-8b-instant",        # Fastest
                    "mixtral-8x7b-32768"           # Good balance
                ],
                "available": True,
                "priority": 1,  # Highest priority (cheapest)
                "capabilities": [
                    "scientific_enhancement",
                    "market_analysis",
                    "credibility_boosting",
                    "content_optimization",
                    "emotional_intelligence"
                ],
                "cost_per_1k_tokens": 0.0002,  # 150x cheaper than OpenAI!
                "quality_score": 78,
                "speed_rating": 10,  # Fastest available
                "provider_tier": "ultra_cheap",
                "service_tier": "free",
                "max_tokens": 32768,
                "rate_limit_rpm": 30,
                "strengths": [
                    "Extremely fast processing (10x faster than OpenAI)",
                    "Ultra-low cost (150x cheaper than GPT-4)",
                    "Excellent for marketing analysis and content",
                    "High throughput capability"
                ]
            }
            providers.append(provider)
            
            # Calculate savings
            openai_cost = 0.030
            savings_pct = ((openai_cost - provider["cost_per_1k_tokens"]) / openai_cost) * 100
            logger.info(f"✅ Groq provider added - 💰 SAVINGS: {savings_pct:.1f}% vs OpenAI")
        else:
            logger.warning("⚠️ GROQ_API_KEY not found - Missing 150x cost savings!")
    except ImportError as e:
        logger.error(f"❌ Groq library not installed: {str(e)}")
        logger.error("💡 Run: pip install groq")
    except Exception as e:
        logger.error(f"❌ Groq initialization failed: {str(e)}")
    
    # TOGETHER AI - Excellent value (Priority 2)
    logger.info("🔍 Checking Together AI provider (ULTRA-CHEAP #2)...")
    try:
        import openai  # Together AI uses OpenAI SDK
        logger.info(f"✅ Together AI (OpenAI SDK) imported successfully")
        
        api_key = os.getenv("TOGETHER_API_KEY")
        logger.info(f"🔑 Together API key present: {bool(api_key)}")
        
        if api_key:
            logger.info(f"🔑 Together key length: {len(api_key)} characters")
            
            # Test client creation
            client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.together.xyz/v1"
            )
            logger.info("✅ Together AI client created successfully")
            
            provider = {
                "name": "together",
                "client": client,
                "models": [
                    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",  # Best quality
                    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",   # Faster
                    "mistralai/Mixtral-8x7B-Instruct-v0.1"           # Alternative
                ],
                "available": True,
                "priority": 2,  # Second priority
                "capabilities": [
                    "scientific_enhancement",
                    "market_analysis", 
                    "credibility_boosting",
                    "content_optimization",
                    "emotional_intelligence"
                ],
                "cost_per_1k_tokens": 0.0008,  # 37x cheaper than OpenAI!
                "quality_score": 82,
                "speed_rating": 8,
                "provider_tier": "ultra_cheap",
                "service_tier": "free",
                "max_tokens": 32768,
                "rate_limit_rpm": 60,
                "strengths": [
                    "Excellent quality for the price",
                    "37x cheaper than GPT-4",
                    "Good balance of speed and quality",
                    "Strong reasoning capabilities"
                ]
            }
            providers.append(provider)
            
            # Calculate savings
            openai_cost = 0.030
            savings_pct = ((openai_cost - provider["cost_per_1k_tokens"]) / openai_cost) * 100
            logger.info(f"✅ Together AI provider added - 💰 SAVINGS: {savings_pct:.1f}% vs OpenAI")
        else:
            logger.warning("⚠️ TOGETHER_API_KEY not found - Missing 37x cost savings!")
    except ImportError as e:
        logger.error(f"❌ OpenAI library not installed for Together AI: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Together AI initialization failed: {str(e)}")
    
    # DEEPSEEK - Cheapest overall (Priority 3)
    logger.info("🔍 Checking Deepseek provider (ULTRA-CHEAP #3)...")
    try:
        import openai  # Deepseek uses OpenAI SDK
        logger.info(f"✅ Deepseek (OpenAI SDK) imported successfully")
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        logger.info(f"🔑 Deepseek API key present: {bool(api_key)}")
        
        if api_key:
            logger.info(f"🔑 Deepseek key length: {len(api_key)} characters")
            
            # Test client creation
            client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            logger.info("✅ Deepseek client created successfully")
            
            provider = {
                "name": "deepseek",
                "client": client,
                "models": [
                    "deepseek-chat",           # Main model
                    "deepseek-coder"           # Code-focused (if needed)
                ],
                "available": True,
                "priority": 3,  # Third priority
                "capabilities": [
                    "scientific_enhancement",
                    "market_analysis",
                    "credibility_boosting", 
                    "content_optimization",
                    "emotional_intelligence"
                ],
                "cost_per_1k_tokens": 0.00014,  # 214x cheaper than OpenAI!
                "quality_score": 72,
                "speed_rating": 7,
                "provider_tier": "ultra_cheap",
                "service_tier": "free",
                "max_tokens": 32768,
                "rate_limit_rpm": 60,
                "strengths": [
                    "Cheapest overall provider",
                    "214x cheaper than GPT-4",
                    "Good for high-volume tasks",
                    "Decent quality for the price"
                ]
            }
            providers.append(provider)
            
            # Calculate savings
            openai_cost = 0.030
            savings_pct = ((openai_cost - provider["cost_per_1k_tokens"]) / openai_cost) * 100
            logger.info(f"✅ Deepseek provider added - 💰 SAVINGS: {savings_pct:.1f}% vs OpenAI")
        else:
            logger.warning("⚠️ DEEPSEEK_API_KEY not found - Missing 214x cost savings!")
    except ImportError as e:
        logger.error(f"❌ OpenAI library not installed for Deepseek: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Deepseek initialization failed: {str(e)}")
    
    # ============================================================================
    # PRIORITY 2: PREMIUM PROVIDERS (Fallback for quality when needed)
    # ============================================================================
    
    # ANTHROPIC CLAUDE - Premium quality (Priority 4)
    logger.info("🔍 Checking Anthropic provider (PREMIUM FALLBACK)...")
    try:
        import anthropic
        logger.info(f"✅ Anthropic library imported successfully")
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        logger.info(f"🔑 Anthropic API key present: {bool(api_key)}")
        
        if api_key:
            client = anthropic.AsyncAnthropic(api_key=api_key)
            logger.info("✅ Anthropic client created successfully")
            
            provider = {
                "name": "anthropic",
                "client": client,
                "models": [
                    "claude-3-5-sonnet-20241022",
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307"
                ],
                "available": True,
                "priority": 4,  # Lower priority (premium tier)
                "capabilities": [
                    "long_form_content",
                    "scientific_writing",
                    "detailed_analysis",
                    "complex_reasoning"
                ],
                "cost_per_1k_tokens": 0.006,  # Still 5x cheaper than OpenAI
                "quality_score": 92,
                "speed_rating": 6,
                "provider_tier": "premium",
                "service_tier": "premium",
                "max_tokens": 200000,
                "rate_limit_rpm": 50,
                "strengths": [
                    "Highest quality reasoning",
                    "200K context window",
                    "Superior long-form content",
                    "Scientific accuracy"
                ]
            }
            providers.append(provider)
            logger.info("✅ Anthropic provider added as premium fallback")
        else:
            logger.info("💡 ANTHROPIC_API_KEY not found - Premium quality not available")
    except ImportError as e:
        logger.info(f"💡 Anthropic library not installed: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Anthropic initialization failed: {str(e)}")
    
    # COHERE - Budget option (Priority 5)
    logger.info("🔍 Checking Cohere provider (BUDGET OPTION)...")
    try:
        import cohere
        logger.info("✅ Cohere library imported successfully")
        
        api_key = os.getenv("COHERE_API_KEY")
        logger.info(f"🔑 Cohere API key present: {bool(api_key)}")
        
        if api_key:
            client = cohere.AsyncClient(api_key=api_key)
            logger.info("✅ Cohere client created successfully")
            
            provider = {
                "name": "cohere",
                "client": client,
                "models": [
                    "command-r-plus",
                    "command-r",
                    "command"
                ],
                "available": True,
                "priority": 5,
                "capabilities": [
                    "content_generation",
                    "summarization",
                    "short_form_content"
                ],
                "cost_per_1k_tokens": 0.002,  # 15x cheaper than OpenAI
                "quality_score": 75,
                "speed_rating": 8,
                "provider_tier": "budget",
                "service_tier": "budget",
                "max_tokens": 4000,
                "rate_limit_rpm": 1000,
                "strengths": [
                    "Good for high-volume content",
                    "Fast generation",
                    "Cost-effective for basic tasks"
                ]
            }
            providers.append(provider)
            logger.info("✅ Cohere provider added as budget option")
        else:
            logger.info("💡 COHERE_API_KEY not found - Budget option not available")
    except ImportError as e:
        logger.info(f"💡 Cohere library not installed: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Cohere initialization failed: {str(e)}")
    
    # OPENAI - Emergency fallback only (Priority 6)
    logger.info("🔍 Checking OpenAI provider (EMERGENCY FALLBACK ONLY)...")
    try:
        import openai
        logger.info(f"✅ OpenAI library imported successfully")
        
        api_key = os.getenv("OPENAI_API_KEY")
        logger.info(f"🔑 OpenAI API key present: {bool(api_key)}")
        
        if api_key:
            client = openai.AsyncOpenAI(api_key=api_key)
            logger.info("✅ OpenAI client created successfully")
            
            provider = {
                "name": "openai",
                "client": client,
                "models": ["gpt-4", "gpt-3.5-turbo"],
                "available": True,
                "priority": 6,  # Lowest priority (most expensive)
                "capabilities": [
                    "emergency_fallback",
                    "complex_reasoning",
                    "creative_content"
                ],
                "cost_per_1k_tokens": 0.030,  # Most expensive
                "quality_score": 95,
                "speed_rating": 5,
                "provider_tier": "premium_expensive",
                "service_tier": "emergency",
                "max_tokens": 4000,
                "rate_limit_rpm": 500,
                "strengths": [
                    "Highest quality (but expensive)",
                    "Industry standard",
                    "Emergency fallback reliability"
                ]
            }
            providers.append(provider)
            logger.info("✅ OpenAI provider added as EMERGENCY FALLBACK ONLY")
        else:
            logger.info("💡 OPENAI_API_KEY not found - Emergency fallback not available")
    except ImportError as e:
        logger.error(f"❌ OpenAI library not installed: {str(e)}")
    except Exception as e:
        logger.error(f"❌ OpenAI initialization failed: {str(e)}")
    
    # ============================================================================
    # FINAL RESULTS AND ULTRA-CHEAP OPTIMIZATION SUMMARY
    # ============================================================================
    
    # Sort providers by priority (lowest number = highest priority = cheapest)
    providers.sort(key=lambda x: x.get("priority", 999))
    
    logger.info(f"📊 ULTRA-CHEAP PROVIDERS INITIALIZATION COMPLETE")
    logger.info(f"📊 Total providers initialized: {len(providers)}")
    
    if providers:
        logger.info(f"🚀 SUCCESS: Initialized {len(providers)} AI provider(s) with ultra-cheap optimization")
        
        # Calculate total cost savings
        ultra_cheap_providers = [p for p in providers if p.get("provider_tier") == "ultra_cheap"]
        
        if ultra_cheap_providers:
            primary_provider = providers[0]  # Cheapest available
            openai_cost = 0.030
            primary_cost = primary_provider.get("cost_per_1k_tokens", openai_cost)
            savings_pct = ((openai_cost - primary_cost) / openai_cost) * 100
            
            logger.info(f"💎 ULTRA-CHEAP OPTIMIZATION ACTIVE:")
            logger.info(f"   🥇 Primary Provider: {primary_provider['name']}")
            logger.info(f"   💰 Cost: ${primary_cost:.5f}/1K tokens")
            logger.info(f"   🎯 Quality: {primary_provider.get('quality_score', 0)}/100")
            logger.info(f"   ⚡ Speed: {primary_provider.get('speed_rating', 0)}/10")
            logger.info(f"   🔥 SAVINGS: {savings_pct:.1f}% vs OpenAI")
            
            # Calculate monthly savings at scale
            monthly_tokens = 1000000  # 1M tokens/month
            openai_monthly = (monthly_tokens / 1000) * openai_cost
            ultra_cheap_monthly = (monthly_tokens / 1000) * primary_cost
            monthly_savings = openai_monthly - ultra_cheap_monthly
            
            logger.info(f"   📈 Monthly savings (1M tokens): ${monthly_savings:.2f}")
            
            # Log all ultra-cheap providers
            logger.info(f"🔥 ULTRA-CHEAP PROVIDERS AVAILABLE:")
            for provider in ultra_cheap_providers:
                cost = provider.get("cost_per_1k_tokens", 0)
                quality = provider.get("quality_score", 0)
                savings = ((openai_cost - cost) / openai_cost) * 100
                logger.info(f"   ✅ {provider['name']}: ${cost:.5f}/1K ({savings:.0f}% savings, {quality}/100 quality)")
            
        else:
            logger.warning("⚠️ NO ULTRA-CHEAP PROVIDERS AVAILABLE!")
            logger.warning("💡 Add Groq, Together AI, or Deepseek for 95-99% cost savings")
        
        # Log provider order
        logger.info(f"🔄 PROVIDER PRIORITY ORDER (cheapest first):")
        for i, provider in enumerate(providers, 1):
            cost = provider.get("cost_per_1k_tokens", 0)
            tier = provider.get("provider_tier", "unknown")
            logger.info(f"   {i}. {provider['name']} (${cost:.5f}/1K, {tier})")
            
    else:
        logger.error("❌ CRITICAL: NO AI PROVIDERS AVAILABLE!")
        logger.error("🔧 ULTRA-CHEAP OPTIMIZATION FAILED - No cost savings possible")
        logger.error("🔧 Add at least one provider: Groq, Together AI, or Deepseek")
    
    return providers

def get_ultra_cheap_provider_recommendations():
    """Get recommendations for ultra-cheap AI provider setup"""
    
    return {
        "ultra_cheap_providers": {
            "groq": {
                "priority": "🔥 CRITICAL",
                "setup_time": "2 minutes",
                "signup_url": "https://console.groq.com",
                "api_key_env": "GROQ_API_KEY",
                "cost_per_1k": "$0.0002",
                "savings_vs_openai": "99.3%",
                "quality_score": "78/100",
                "speed": "10x faster than OpenAI",
                "why": "Fastest and cheapest - massive cost savings"
            },
            "together": {
                "priority": "🔥 CRITICAL", 
                "setup_time": "3 minutes",
                "signup_url": "https://api.together.xyz",
                "api_key_env": "TOGETHER_API_KEY",
                "cost_per_1k": "$0.0008",
                "savings_vs_openai": "97.3%",
                "quality_score": "82/100",
                "speed": "Very fast",
                "why": "Best quality for ultra-cheap tier"
            },
            "deepseek": {
                "priority": "🔥 CRITICAL",
                "setup_time": "3 minutes", 
                "signup_url": "https://platform.deepseek.com",
                "api_key_env": "DEEPSEEK_API_KEY",
                "cost_per_1k": "$0.00014",
                "savings_vs_openai": "99.5%",
                "quality_score": "72/100",
                "speed": "Good",
                "why": "Absolute cheapest option available"
            }
        },
        "setup_priority": [
            "1. 🥇 Groq (biggest impact, 2 min setup)",
            "2. 🥈 Together AI (best quality ultra-cheap, 3 min)",
            "3. 🥉 Deepseek (cheapest overall, 3 min)"
        ],
        "expected_savings": {
            "monthly_1m_tokens": "$2,900+ saved vs OpenAI",
            "yearly_1m_tokens": "$35,000+ saved vs OpenAI",
            "break_even": "Immediate - first API call saves money"
        }
    }

def check_ultra_cheap_optimization():
    """Check ultra-cheap optimization status"""
    
    providers = initialize_ai_providers()
    ultra_cheap_available = [p for p in providers if p.get("provider_tier") == "ultra_cheap"]
    
    status = {
        "ultra_cheap_optimization_active": len(ultra_cheap_available) > 0,
        "ultra_cheap_providers_count": len(ultra_cheap_available),
        "total_providers": len(providers),
        "primary_provider": providers[0]["name"] if providers else None,
        "estimated_cost_savings": 0.0,
        "setup_recommendations": []
    }
    
    if ultra_cheap_available:
        primary = providers[0]
        openai_cost = 0.030
        primary_cost = primary.get("cost_per_1k_tokens", openai_cost)
        savings_pct = ((openai_cost - primary_cost) / openai_cost) * 100
        
        status["estimated_cost_savings"] = savings_pct
        status["setup_recommendations"].append(f"✅ EXCELLENT: Using {primary['name']} with {savings_pct:.1f}% cost savings")
        
        # Check for missing ultra-cheap providers
        available_names = [p["name"] for p in ultra_cheap_available]
        if "groq" not in available_names:
            status["setup_recommendations"].append("💡 ADD GROQ: 150x cost savings and 10x speed boost")
        if "together" not in available_names:
            status["setup_recommendations"].append("💡 ADD TOGETHER AI: Best quality ultra-cheap option")
        if "deepseek" not in available_names:
            status["setup_recommendations"].append("💡 ADD DEEPSEEK: Cheapest overall option available")
    else:
        status["setup_recommendations"].extend([
            "🚨 URGENT: No ultra-cheap providers available",
            "💰 MISSING: 95-99% potential cost savings",
            "🔧 ACTION: Add Groq, Together AI, or Deepseek immediately"
        ])
    
    return status

# Add test capability for ultra-cheap providers
if __name__ == "__main__":
    print("🔍 TESTING ULTRA-CHEAP AI PROVIDER INITIALIZATION...")
    providers = initialize_ai_providers()
    
    if providers:
        primary = providers[0]
        openai_cost = 0.030
        primary_cost = primary.get("cost_per_1k_tokens", openai_cost)
        savings = ((openai_cost - primary_cost) / openai_cost) * 100
        
        print(f"\n🎯 ULTRA-CHEAP OPTIMIZATION RESULT:")
        print(f"   Primary Provider: {primary['name']}")
        print(f"   Cost Savings: {savings:.1f}% vs OpenAI")
        print(f"   Quality Score: {primary.get('quality_score', 0)}/100")
        print(f"   Monthly Savings (1M tokens): ${((1000 * openai_cost) - (1000 * primary_cost)):.2f}")
    else:
        print("❌ NO PROVIDERS AVAILABLE - Setup required")