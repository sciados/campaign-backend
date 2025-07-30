"""
Core configuration settings for CampaignForge AI
🔥 FIXED: Enhanced with ultra-cheap AI providers and R2 configuration
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""

    # Basic settings
    APP_NAME: str = "CampaignForge AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str

    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["https://campaignforge-frontend.vercel.app", "https://rodgersdigital.com", "https://www.rodgersdigital.com"]
    ALLOWED_HOSTS: List[str] = ["*"]

    # 🔥 ULTRA-CHEAP AI PROVIDERS (Primary - 95-99% cost savings)
    GROQ_API_KEY: Optional[str] = None              # $0.0002/1K tokens - 99.3% savings
    TOGETHER_API_KEY: Optional[str] = None          # $0.0008/1K tokens - 97.3% savings  
    DEEPSEEK_API_KEY: Optional[str] = None          # $0.00014/1K tokens - 99.5% savings
    
    # 🔥 ULTRA-CHEAP IMAGE GENERATION
    FAL_API_KEY: Optional[str] = None               # $0.0015/image - 96.3% savings vs DALL-E
    REPLICATE_API_TOKEN: Optional[str] = None       # $0.004/image - 90% savings vs DALL-E
    STABILITY_AI_API_KEY: Optional[str] = None      # $0.002/image - 95% savings vs DALL-E

    # AI Services (Fallback/Premium)
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str

    # 🔥 ENHANCED: Cloudflare R2 Configuration (FIXED)
    R2_ACCOUNT_ID: Optional[str] = None                    # ADDED: Critical for R2 endpoint
    CLOUDFLARE_R2_ENDPOINT: str
    CLOUDFLARE_R2_ACCESS_KEY: str
    CLOUDFLARE_R2_SECRET_KEY: str
    CLOUDFLARE_R2_BUCKET: str

    # File Upload
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES: List[str] = [
        "video/mp4", "video/avi", "video/mov",
        "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg", "image/png", "image/gif",
        "text/csv", "application/vnd.ms-excel"
    ]

    # External APIs
    YOUTUBE_API_KEY: Optional[str] = None
    VIMEO_ACCESS_TOKEN: Optional[str] = None

    # Monitoring
    SENTRY_DSN: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# 🔥 ULTRA-CHEAP AI VALIDATION AND COST OPTIMIZATION
def validate_ultra_cheap_ai_config():
    """Validate ultra-cheap AI configuration and display cost savings"""
    
    ultra_cheap_providers = []
    total_estimated_savings = 0.0
    
    print("\n" + "="*60)
    print("🚀 ULTRA-CHEAP AI CONFIGURATION VALIDATION")
    print("="*60)
    
    # Text Generation Providers
    print("\n📝 TEXT GENERATION PROVIDERS:")
    
    if os.getenv("GROQ_API_KEY"):
        ultra_cheap_providers.append("groq")
        savings = ((0.030 - 0.0002) / 0.030) * 100
        total_estimated_savings += 0.030 - 0.0002
        print(f"   ✅ GROQ: ${0.0002:.5f}/1K tokens ({savings:.1f}% savings)")
        
    if os.getenv("TOGETHER_API_KEY"):
        ultra_cheap_providers.append("together") 
        savings = ((0.030 - 0.0008) / 0.030) * 100
        total_estimated_savings += 0.030 - 0.0008
        print(f"   ✅ TOGETHER: ${0.0008:.5f}/1K tokens ({savings:.1f}% savings)")
        
    if os.getenv("DEEPSEEK_API_KEY"):
        ultra_cheap_providers.append("deepseek")
        savings = ((0.030 - 0.00014) / 0.030) * 100
        total_estimated_savings += 0.030 - 0.00014
        print(f"   ✅ DEEPSEEK: ${0.00014:.5f}/1K tokens ({savings:.1f}% savings)")
    
    if not ultra_cheap_providers:
        print("   ❌ NO ULTRA-CHEAP TEXT PROVIDERS CONFIGURED!")
        print("   💡 Add GROQ_API_KEY, TOGETHER_API_KEY, or DEEPSEEK_API_KEY")
    else:
        print(f"   🎯 PRIMARY PROVIDER: {ultra_cheap_providers[0].upper()}")
    
    # Image Generation Providers
    print("\n🎨 IMAGE GENERATION PROVIDERS:")
    
    image_providers = []
    if os.getenv("FAL_API_KEY"):
        image_providers.append("fal")
        savings = ((0.040 - 0.0015) / 0.040) * 100
        print(f"   ✅ FAL AI: ${0.0015:.4f}/image ({savings:.1f}% savings) - ULTRA-FAST")
        
    if os.getenv("STABILITY_AI_API_KEY"):
        image_providers.append("stability")
        savings = ((0.040 - 0.002) / 0.040) * 100  
        print(f"   ✅ STABILITY AI: ${0.002:.4f}/image ({savings:.1f}% savings)")
        
    if os.getenv("REPLICATE_API_TOKEN"):
        image_providers.append("replicate")
        savings = ((0.040 - 0.004) / 0.040) * 100
        print(f"   ✅ REPLICATE: ${0.004:.4f}/image ({savings:.1f}% savings)")
    
    if not image_providers:
        print("   ⚠️  No ultra-cheap image providers configured")
        print("   💡 Add FAL_API_KEY for fastest/cheapest image generation")
    else:
        print(f"   🎯 PRIMARY IMAGE PROVIDER: {image_providers[0].upper()}")
    
    # Cost Projections
    print(f"\n💰 COST OPTIMIZATION SUMMARY:")
    if ultra_cheap_providers:
        print(f"   📊 Ultra-cheap providers configured: {len(ultra_cheap_providers)}")
        print(f"   📊 Image providers configured: {len(image_providers)}")
        
        # Monthly savings projection (example usage)
        monthly_text_requests = 10000  # 10K text generations
        monthly_image_requests = 1000   # 1K image generations
        
        # Text savings calculation (using cheapest provider)
        if "deepseek" in ultra_cheap_providers:
            text_cost_ultra_cheap = (monthly_text_requests / 1000) * 0.00014
        elif "groq" in ultra_cheap_providers:
            text_cost_ultra_cheap = (monthly_text_requests / 1000) * 0.0002
        elif "together" in ultra_cheap_providers:
            text_cost_ultra_cheap = (monthly_text_requests / 1000) * 0.0008
        else:
            text_cost_ultra_cheap = (monthly_text_requests / 1000) * 0.030  # OpenAI fallback
            
        text_cost_openai = (monthly_text_requests / 1000) * 0.030
        text_savings_monthly = text_cost_openai - text_cost_ultra_cheap
        
        # Image savings calculation
        if "fal" in image_providers:
            image_cost_ultra_cheap = monthly_image_requests * 0.0015
        elif "stability" in image_providers:
            image_cost_ultra_cheap = monthly_image_requests * 0.002
        elif "replicate" in image_providers:
            image_cost_ultra_cheap = monthly_image_requests * 0.004
        else:
            image_cost_ultra_cheap = monthly_image_requests * 0.040  # DALL-E fallback
            
        image_cost_dalle = monthly_image_requests * 0.040
        image_savings_monthly = image_cost_dalle - image_cost_ultra_cheap
        
        total_monthly_savings = text_savings_monthly + image_savings_monthly
        total_annual_savings = total_monthly_savings * 12
        
        print(f"   💵 Est. monthly text cost: ${text_cost_ultra_cheap:.2f} (vs ${text_cost_openai:.2f} OpenAI)")
        print(f"   💵 Est. monthly image cost: ${image_cost_ultra_cheap:.2f} (vs ${image_cost_dalle:.2f} DALL-E)")
        print(f"   💎 TOTAL MONTHLY SAVINGS: ${total_monthly_savings:.2f}")
        print(f"   🏆 TOTAL ANNUAL SAVINGS: ${total_annual_savings:.2f}")
        
        # Savings percentage
        total_expensive_cost = text_cost_openai + image_cost_dalle
        if total_expensive_cost > 0:
            total_savings_pct = (total_monthly_savings / total_expensive_cost) * 100
            print(f"   📈 OVERALL COST REDUCTION: {total_savings_pct:.1f}%")
    else:
        print("   ❌ NO ULTRA-CHEAP PROVIDERS - USING EXPENSIVE APIS!")
        print("   💸 Missing out on 95-99% potential cost savings")
    
    # Configuration recommendations
    print(f"\n🔧 CONFIGURATION RECOMMENDATIONS:")
    if not os.getenv("GROQ_API_KEY"):
        print("   💡 Add GROQ_API_KEY for fastest ultra-cheap text generation")
    if not os.getenv("FAL_API_KEY"):
        print("   💡 Add FAL_API_KEY for fastest ultra-cheap image generation")
    if not os.getenv("R2_ACCOUNT_ID"):
        print("   ⚠️  Add R2_ACCOUNT_ID to fix Cloudflare R2 storage")
    
    print("="*60)
    
    return {
        "ultra_cheap_providers": ultra_cheap_providers,
        "image_providers": image_providers, 
        "estimated_monthly_savings": total_monthly_savings if ultra_cheap_providers else 0,
        "configuration_complete": len(ultra_cheap_providers) > 0 and len(image_providers) > 0,
        "primary_text_provider": ultra_cheap_providers[0] if ultra_cheap_providers else None,
        "primary_image_provider": image_providers[0] if image_providers else None
    }

def get_r2_endpoint_url():
    """Get properly formatted Cloudflare R2 endpoint URL"""
    account_id = os.getenv("R2_ACCOUNT_ID")
    if not account_id:
        raise ValueError("R2_ACCOUNT_ID environment variable is required for Cloudflare R2")
    
    return f"https://{account_id}.r2.cloudflarestorage.com"

def validate_r2_configuration():
    """Validate Cloudflare R2 configuration"""
    
    print("\n🗄️  CLOUDFLARE R2 STORAGE VALIDATION:")
    
    required_r2_vars = [
        ("R2_ACCOUNT_ID", "Cloudflare Account ID"),
        ("CLOUDFLARE_R2_ACCESS_KEY", "R2 Access Key"),
        ("CLOUDFLARE_R2_SECRET_KEY", "R2 Secret Key"), 
        ("CLOUDFLARE_R2_BUCKET", "R2 Bucket Name")
    ]
    
    r2_configured = True
    for var_name, description in required_r2_vars:
        if os.getenv(var_name):
            print(f"   ✅ {description}: Configured")
        else:
            print(f"   ❌ {description}: MISSING ({var_name})")
            r2_configured = False
    
    if r2_configured:
        try:
            endpoint_url = get_r2_endpoint_url()
            print(f"   ✅ R2 Endpoint: {endpoint_url}")
            print(f"   🎯 R2 Configuration: COMPLETE")
        except Exception as e:
            print(f"   ❌ R2 Endpoint Error: {str(e)}")
            r2_configured = False
    else:
        print(f"   💡 Add missing R2 environment variables to Railway")
    
    return r2_configured

def get_ai_provider_priority():
    """Get AI provider priority order for cost optimization"""
    
    text_providers = []
    if os.getenv("DEEPSEEK_API_KEY"):
        text_providers.append(("deepseek", 0.00014, "99.5%"))
    if os.getenv("GROQ_API_KEY"):
        text_providers.append(("groq", 0.0002, "99.3%"))
    if os.getenv("TOGETHER_API_KEY"):
        text_providers.append(("together", 0.0008, "97.3%"))
    if os.getenv("ANTHROPIC_API_KEY"):
        text_providers.append(("anthropic", 0.006, "80.0%"))
    if os.getenv("OPENAI_API_KEY"):
        text_providers.append(("openai", 0.030, "0.0%"))
    
    # Sort by cost (cheapest first)
    text_providers.sort(key=lambda x: x[1])
    
    image_providers = []
    if os.getenv("FAL_API_KEY"):
        image_providers.append(("fal", 0.0015, "96.3%"))
    if os.getenv("STABILITY_AI_API_KEY"):
        image_providers.append(("stability", 0.002, "95.0%"))
    if os.getenv("REPLICATE_API_TOKEN"):
        image_providers.append(("replicate", 0.004, "90.0%"))
    
    # Sort by cost (cheapest first)
    image_providers.sort(key=lambda x: x[1])
    
    return {
        "text_providers": text_providers,
        "image_providers": image_providers,
        "primary_text": text_providers[0] if text_providers else None,
        "primary_image": image_providers[0] if image_providers else None
    }

def display_deployment_status():
    """Display complete deployment status"""
    
    print("\n" + "🚀" + "="*58 + "🚀")
    print("   CAMPAIGNFORGE AI - DEPLOYMENT STATUS")
    print("🚀" + "="*58 + "🚀")
    
    # Ultra-cheap AI validation
    ai_config = validate_ultra_cheap_ai_config()
    
    # R2 storage validation  
    r2_config = validate_r2_configuration()
    
    # Provider priority
    provider_priority = get_ai_provider_priority()
    
    # Overall status
    print(f"\n📊 DEPLOYMENT READINESS:")
    
    ai_ready = len(ai_config["ultra_cheap_providers"]) > 0
    storage_ready = r2_config
    
    if ai_ready and storage_ready:
        print(f"   🎉 STATUS: FULLY OPTIMIZED & READY")
        print(f"   💰 Cost optimization: MAXIMUM (95-99% savings)")
        print(f"   🗄️  Storage: CONFIGURED")
    elif ai_ready:
        print(f"   ⚠️  STATUS: AI OPTIMIZED, STORAGE NEEDS SETUP")  
        print(f"   💰 Cost optimization: ACTIVE ({ai_config['estimated_monthly_savings']:.2f}+ monthly savings)")
        print(f"   🗄️  Storage: NEEDS R2_ACCOUNT_ID")
    elif storage_ready:
        print(f"   ⚠️  STATUS: STORAGE READY, AI NEEDS OPTIMIZATION")
        print(f"   💰 Cost optimization: MISSING (Add ultra-cheap providers)")
        print(f"   🗄️  Storage: CONFIGURED")
    else:
        print(f"   ❌ STATUS: NEEDS SETUP")
        print(f"   💰 Cost optimization: NOT CONFIGURED")
        print(f"   🗄️  Storage: NOT CONFIGURED")
    
    print("\n" + "🚀" + "="*58 + "🚀")
    
    return {
        "ai_ready": ai_ready,
        "storage_ready": storage_ready,
        "fully_optimized": ai_ready and storage_ready,
        "ai_config": ai_config,
        "provider_priority": provider_priority
    }

# 🔥 ENHANCED: Run validation on import (only in development)
if os.getenv("DEBUG", "false").lower() == "true" or os.getenv("RAILWAY_ENVIRONMENT_NAME", "production") == "production":
    deployment_status = display_deployment_status()
else:
    # Production: Silent validation  
    deployment_status = {
        "ai_ready": bool(os.getenv("GROQ_API_KEY") or os.getenv("TOGETHER_API_KEY") or os.getenv("DEEPSEEK_API_KEY")),
        "storage_ready": bool(os.getenv("R2_ACCOUNT_ID") and os.getenv("CLOUDFLARE_R2_ACCESS_KEY")),
        "production_mode": True
    }

# Export for use in application
ultra_cheap_ai_config = deployment_status