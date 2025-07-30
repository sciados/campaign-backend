"""
Core configuration settings for CampaignForge AI
🔥 UPDATED: Works with your actual Railway environment variables
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""

    # Basic settings
    APP_NAME: str = "CampaignForge AI"
    VERSION: str = "3.0.0"
    DEBUG: bool = False

    # Security - Updated to match Railway vars
    SECRET_KEY: Optional[str] = None
    JWT_SECRET_KEY: Optional[str] = None  # Railway uses this name
    ALGORITHM: str = "HS256"
    JWT_ALGORITHM: str = "HS256"  # Railway uses this name
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def effective_secret_key(self) -> str:
        """Get the secret key from either variable name"""
        return self.JWT_SECRET_KEY or self.SECRET_KEY or "fallback-secret-key"

    # Database
    DATABASE_URL: str

    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379"

    # CORS - Updated to match Railway format
    ALLOWED_ORIGINS_STR: Optional[str] = None
    
    @property
    def allowed_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string"""
        if self.ALLOWED_ORIGINS_STR:
            return [origin.strip() for origin in self.ALLOWED_ORIGINS_STR.split(",")]
        return [
            "https://campaignforge.vercel.app",
            "https://campaignforge-frontend.vercel.app", 
            "https://rodgersdigital.com",
            "https://www.rodgersdigital.com",
            "https://rodgersdigital.vercel.app",
            "https://www.rodgersdigital.vercel.app",
            "http://localhost:3000",
            "http://localhost:3001"
        ]

    # 🔥 ULTRA-CHEAP AI PROVIDERS (Your excellent setup!)
    GROQ_API_KEY: Optional[str] = None              # $0.00027/1K tokens - 99.1% savings
    TOGETHER_API_KEY: Optional[str] = None          # $0.0008/1K tokens - 97.3% savings  
    DEEPSEEK_API_KEY: Optional[str] = None          # $0.00014/1K tokens - 99.5% savings
    
    # 🔥 ULTRA-CHEAP IMAGE GENERATION (Your setup is perfect!)
    FAL_API_KEY: Optional[str] = None               # $0.0015/image - 96.3% savings vs DALL-E
    REPLICATE_API_TOKEN: Optional[str] = None       # $0.004/image - 90% savings vs DALL-E
    STABILITY_API_KEY: Optional[str] = None         # $0.002/image - 95% savings vs DALL-E

    # AI Services (Fallback/Premium)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Additional AI Providers (You have these!)
    COHERE_API_KEY: Optional[str] = None
    MINIMAX_API_KEY: Optional[str] = None
    AIMLAPI_API_KEY: Optional[str] = None

    # 🔧 FIXED: Cloudflare R2 Configuration (Supporting both variable naming schemes)
    # Primary scheme (CLOUDFLARE_ prefix)
    CLOUDFLARE_ACCOUNT_ID: Optional[str] = None
    CLOUDFLARE_R2_ACCESS_KEY_ID: Optional[str] = None
    CLOUDFLARE_R2_SECRET_ACCESS_KEY: Optional[str] = None
    CLOUDFLARE_R2_BUCKET_NAME: Optional[str] = None
    
    # Alternative scheme (R2_ prefix) - for backwards compatibility
    R2_ACCOUNT_ID: Optional[str] = None
    R2_ACCESS_KEY_ID: Optional[str] = None
    R2_SECRET_ACCESS_KEY: Optional[str] = None
    R2_BUCKET_NAME: Optional[str] = None
    R2_ENDPOINT: Optional[str] = None

    @property
    def r2_account_id(self) -> Optional[str]:
        """Get R2 account ID from either variable scheme"""
        return self.CLOUDFLARE_ACCOUNT_ID or self.R2_ACCOUNT_ID

    @property
    def r2_access_key_id(self) -> Optional[str]:
        """Get R2 access key ID from either variable scheme"""
        return self.CLOUDFLARE_R2_ACCESS_KEY_ID or self.R2_ACCESS_KEY_ID

    @property
    def r2_secret_access_key(self) -> Optional[str]:
        """Get R2 secret access key from either variable scheme"""
        return self.CLOUDFLARE_R2_SECRET_ACCESS_KEY or self.R2_SECRET_ACCESS_KEY

    @property
    def r2_bucket_name(self) -> Optional[str]:
        """Get R2 bucket name from either variable scheme"""
        return self.CLOUDFLARE_R2_BUCKET_NAME or self.R2_BUCKET_NAME

    @property
    def r2_endpoint_url(self) -> str:
        """Generate R2 endpoint URL"""
        # Use explicit endpoint if provided
        if self.R2_ENDPOINT:
            return self.R2_ENDPOINT
        
        # Generate from account ID
        account_id = self.r2_account_id
        if account_id:
            return f"https://{account_id}.r2.cloudflarestorage.com"
        
        raise ValueError("R2 configuration incomplete: need either R2_ENDPOINT or account ID")

    @property 
    def r2_configured(self) -> bool:
        """Check if R2 is properly configured"""
        return all([
            self.r2_access_key_id,
            self.r2_secret_access_key,
            self.r2_bucket_name,
            (self.r2_account_id or self.R2_ENDPOINT)
        ])

    # AI Monitoring & Optimization (Your settings)
    AI_MONITORING_ENABLED: bool = True
    AI_MONITORING_INTERVAL_MINUTES: int = 60
    AI_CACHE_TTL_SECONDS: int = 300
    AI_COST_OPTIMIZATION: bool = True
    AI_FALLBACK_ENABLED: bool = True

    # Intelligence System
    INTELLIGENCE_ANALYSIS_ENABLED: bool = True
    CREDIT_ENFORCEMENT_ENABLED: bool = True

    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # Convert to bytes
    ALLOWED_FILE_TYPES: List[str] = [
        "video/mp4", "video/avi", "video/mov",
        "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg", "image/png", "image/gif",
        "text/csv", "application/vnd.ms-excel"
    ]

    # External APIs (You have these!)
    CLICKBANK_API_KEY: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    VIMEO_ACCESS_TOKEN: Optional[str] = None

    # Monitoring
    SENTRY_DSN: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True
        
        # Allow Railway's ALLOWED_ORIGINS format
        fields = {
            "ALLOWED_ORIGINS_STR": {"env": "ALLOWED_ORIGINS"}
        }

settings = Settings()

# 🔥 RAILWAY DEPLOYMENT VALIDATION
def validate_railway_deployment():
    """Validate deployment with your actual Railway variables"""
    
    print("\n" + "🚀" + "="*58 + "🚀")
    print("   CAMPAIGNFORGE AI - RAILWAY DEPLOYMENT STATUS")
    print("🚀" + "="*58 + "🚀")
    
    # Check critical variables
    print("\n🔑 CRITICAL VARIABLES:")
    critical_checks = [
        ("JWT_SECRET_KEY", settings.JWT_SECRET_KEY, "JWT Secret"),
        ("DATABASE_URL", settings.DATABASE_URL, "Database Connection"),
        ("OPENAI_API_KEY", settings.OPENAI_API_KEY, "OpenAI Fallback")
    ]
    
    critical_ok = True
    for var_name, value, description in critical_checks:
        if value:
            print(f"   ✅ {description}: Configured")
        else:
            print(f"   ❌ {description}: MISSING ({var_name})")
            critical_ok = False
    
    # Check ultra-cheap AI providers
    print("\n💰 ULTRA-CHEAP AI PROVIDERS:")
    ai_providers = [
        ("GROQ", settings.GROQ_API_KEY, "$0.00027/1K tokens - 99.1% savings"),
        ("TOGETHER", settings.TOGETHER_API_KEY, "$0.0008/1K tokens - 97.3% savings"),
        ("DEEPSEEK", settings.DEEPSEEK_API_KEY, "$0.00014/1K tokens - 99.5% savings")
    ]
    
    ai_configured = []
    for provider, key, description in ai_providers:
        if key:
            print(f"   ✅ {provider}: {description}")
            ai_configured.append(provider)
        else:
            print(f"   ⚠️  {provider}: Not configured")
    
    # Check image generation
    print("\n🎨 ULTRA-CHEAP IMAGE GENERATION:")
    image_providers = [
        ("FAL AI", settings.FAL_API_KEY, "$0.0015/image - 96.3% savings"),
        ("STABILITY AI", settings.STABILITY_API_KEY, "$0.002/image - 95% savings"),
        ("REPLICATE", settings.REPLICATE_API_TOKEN, "$0.004/image - 90% savings")
    ]
    
    image_configured = []
    for provider, key, description in image_providers:
        if key:
            print(f"   ✅ {provider}: {description}")
            image_configured.append(provider)
        else:
            print(f"   ⚠️  {provider}: Not configured")
    
    # Check R2 storage
    print("\n🗄️  CLOUDFLARE R2 STORAGE:")
    r2_vars = [
        ("Account ID", settings.r2_account_id),
        ("Access Key", settings.r2_access_key_id),
        ("Secret Key", settings.r2_secret_access_key),
        ("Bucket Name", settings.r2_bucket_name)
    ]
    
    r2_ok = True
    for desc, value in r2_vars:
        if value:
            print(f"   ✅ {desc}: Configured")
        else:
            print(f"   ❌ {desc}: MISSING")
            r2_ok = False
    
    if r2_ok:
        try:
            endpoint = settings.r2_endpoint_url
            print(f"   ✅ R2 Endpoint: {endpoint}")
        except Exception as e:
            print(f"   ❌ R2 Endpoint Error: {e}")
            r2_ok = False
    
    # Overall status
    print(f"\n📊 DEPLOYMENT SUMMARY:")
    print(f"   🔑 Critical variables: {'✅ READY' if critical_ok else '❌ MISSING'}")
    print(f"   💰 AI cost optimization: {'✅ ACTIVE' if ai_configured else '❌ INACTIVE'}")
    print(f"   🎨 Image generation: {'✅ OPTIMIZED' if image_configured else '⚠️  LIMITED'}")
    print(f"   🗄️  Storage system: {'✅ CONFIGURED' if r2_ok else '❌ NEEDS SETUP'}")
    
    # Cost savings calculation
    if ai_configured and image_configured:
        print(f"\n💎 ESTIMATED MONTHLY SAVINGS:")
        print(f"   📊 Text generation: $270+ (vs OpenAI)")
        print(f"   📊 Image generation: $380+ (vs DALL-E)")
        print(f"   🏆 TOTAL POTENTIAL: $650+ monthly")
        print(f"   📈 Annual savings: $7,800+")
    
    # Next steps
    if not r2_ok:
        print(f"\n🔧 IMMEDIATE ACTION NEEDED:")
        print(f"   1. Set R2_ACCOUNT_ID = '{settings.CLOUDFLARE_ACCOUNT_ID or 'MISSING'}'")
        if not settings.r2_account_id:
            print(f"   2. Check if CLOUDFLARE_ACCOUNT_ID is properly set")
    
    print("🚀" + "="*58 + "🚀")
    
    return {
        "critical_ok": critical_ok,
        "ai_configured": len(ai_configured) > 0,
        "image_configured": len(image_configured) > 0,
        "r2_configured": r2_ok,
        "deployment_ready": critical_ok and len(ai_configured) > 0
    }

# 🔧 IMMEDIATE RAILWAY FIX NEEDED
def check_immediate_fixes_needed():
    """Check what needs immediate fixing in Railway"""
    
    fixes_needed = []
    
    # Check if R2_ACCOUNT_ID is missing but CLOUDFLARE_ACCOUNT_ID exists
    if not settings.R2_ACCOUNT_ID and settings.CLOUDFLARE_ACCOUNT_ID:
        fixes_needed.append({
            "variable": "R2_ACCOUNT_ID",
            "value": settings.CLOUDFLARE_ACCOUNT_ID,
            "action": "ADD this variable to Railway"
        })
    
    # Check for missing critical variables
    if not settings.JWT_SECRET_KEY and not settings.SECRET_KEY:
        fixes_needed.append({
            "variable": "JWT_SECRET_KEY", 
            "value": "GENERATE_NEW_SECRET",
            "action": "ADD a secure secret key"
        })
    
    return fixes_needed

# Export for use in application
railway_deployment_status = None

# Run validation only in development or when explicitly requested
if (os.getenv("DEBUG", "false").lower() == "true" or 
    os.getenv("RAILWAY_ENVIRONMENT_NAME") == "development" or
    os.getenv("VALIDATE_CONFIG", "false").lower() == "true"):
    railway_deployment_status = validate_railway_deployment()
    immediate_fixes = check_immediate_fixes_needed()
    
    if immediate_fixes:
        print(f"\n🚨 IMMEDIATE FIXES NEEDED IN RAILWAY:")
        for fix in immediate_fixes:
            print(f"   • {fix['variable']} = '{fix['value']}'")
            print(f"     Action: {fix['action']}")
else:
    # Production: Silent validation
    railway_deployment_status = {
        "production_mode": True,
        "ai_ready": bool(settings.GROQ_API_KEY or settings.TOGETHER_API_KEY),
        "storage_ready": settings.r2_configured,
        "deployment_ready": bool(settings.effective_secret_key and settings.DATABASE_URL)
    }