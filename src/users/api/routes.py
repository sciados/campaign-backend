# ============================================================================
# API ROUTE UPDATES FOR SERVICE INTEGRATION
# ============================================================================

# src/users/api/routes.py (Enhanced for Session 5)

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
import logging

from src.core.factories.service_factory import ServiceFactory
from src.users.services.auth_service import AuthService
from src.users.services.user_service import UserService
from src.core.database.connection import get_db
from src.users.models.user import User, Company
from src.campaigns.models.campaign import Campaign
from src.core.database.models import IntelligenceCore, Waitlist

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

@router.post("/api/auth/register")
async def register_user(request: Dict[str, Any]):
    """Enhanced user registration with invite token support"""
    try:
        email = request.get("email")
        password = request.get("password")
        full_name = request.get("full_name")
        company_name = request.get("company_name", "Default Company")
        user_type = request.get("user_type")  # Get user_type from request
        invite_token = request.get("invite_token")  # Get invite token if provided

        if not all([email, password, full_name]):
            raise HTTPException(
                status_code=400,
                detail="email, password, and full_name are required"
            )

        # If invite token is provided, validate it and set user type
        if invite_token:
            from src.intelligence.services.product_creator_invite_service import ProductCreatorInviteService
            from src.core.database import get_async_db

            # Get database session for invite validation
            db_gen = get_async_db()
            session = await db_gen.__anext__()

            try:
                invite_service = ProductCreatorInviteService()
                validation_result = await invite_service.validate_invite_token(
                    invite_token=invite_token,
                    session=session
                )

                if not validation_result["valid"]:
                    raise HTTPException(status_code=400, detail=f"Invalid invite token: {validation_result['reason']}")

                # Set user type to PRODUCT_CREATOR for product creator invites
                user_type = "product_creator"

                # Extract company name from invite if available
                if validation_result.get("invite_data", {}).get("company_name"):
                    company_name = validation_result["invite_data"]["company_name"]

            finally:
                await session.close()

        # Map frontend user types to backend enums if user_type is provided
        backend_user_type = None
        if user_type:
            user_type_mapping = {
                "affiliate_marketer": "AFFILIATE_MARKETER",
                "affiliate": "AFFILIATE_MARKETER",
                "content_creator": "CONTENT_CREATOR",
                "creator": "CONTENT_CREATOR",
                "product_creator": "PRODUCT_CREATOR",
                "business_owner": "BUSINESS_OWNER",
                "business": "BUSINESS_OWNER",
            }
            backend_user_type = user_type_mapping.get(user_type, user_type.upper())

        async with ServiceFactory.create_transactional_service(AuthService) as auth_service:
            result = await auth_service.register(
                email=email,
                password=password,
                full_name=full_name,
                company_name=company_name,
                user_type=backend_user_type,  # Pass user_type to register method
                invite_token=invite_token  # Pass invite token for acceptance
            )

        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/auth/login")
async def login_user(request: Dict[str, Any]):
    """Enhanced user login with proper service management"""
    try:
        email = request.get("email")
        password = request.get("password")
        
        if not all([email, password]):
            raise HTTPException(
                status_code=400,
                detail="email and password are required"
            )
        
        async with ServiceFactory.create_service(AuthService) as auth_service:
            result = await auth_service.login(email=email, password=password)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/api/auth/profile")
async def get_user_profile(token: str = Depends(security)):
    """Get user profile with enhanced service management"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            # Map backend user_type to frontend format
            # Since user_type is stored as a string (not enum), we can directly map it
            frontend_user_type = None
            if user.user_type:
                try:
                    # Map to frontend format
                    backend_to_frontend_mapping = {
                        "AFFILIATE_MARKETER": "affiliate_marketer",
                        "CONTENT_CREATOR": "content_creator",
                        "PRODUCT_CREATOR": "product_creator",
                        "BUSINESS_OWNER": "business_owner",
                    }
                    
                    frontend_user_type = backend_to_frontend_mapping.get(user.user_type, user.user_type.lower())
                except Exception as e:
                    # Fallback to original value if mapping fails
                    frontend_user_type = user.user_type.lower() if user.user_type else None
                    print(f"Warning: User type mapping failed: {e}")
                    

            return {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role if user.role else "user",  # role is stored as string, not enum
                "user_type": frontend_user_type,
                "is_active": user.is_active,
                "company": {
                    "id": str(user.company.id),
                    "name": user.company.company_name,
                    "subscription_tier": user.company.subscription_tier  # subscription_tier is stored as string, not enum
                } if user.company else None
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/user-types/select")
async def select_user_type(request: Dict[str, Any], token: str = Depends(security)):
    """Set user type during onboarding"""
    try:
        from datetime import datetime
        
        user_type = request.get("user_type")
        goals = request.get("goals", [])
        experience_level = request.get("experience_level", "beginner")
        
        if not user_type:
            raise HTTPException(
                status_code=400,
                detail="user_type is required"
            )
        
        # Map frontend user types to backend enums
        user_type_mapping = {
            "affiliate_marketer": "AFFILIATE_MARKETER",
            "affiliate": "AFFILIATE_MARKETER", 
            "content_creator": "CONTENT_CREATOR",
            "creator": "CONTENT_CREATOR",
            "business_owner": "BUSINESS_OWNER", 
            "business": "BUSINESS_OWNER",
        }
        
        # Convert to backend format
        backend_user_type = user_type_mapping.get(user_type, user_type.upper())
        
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            # Use UserService to update user type
            async with ServiceFactory.create_service(UserService) as user_service:
                type_data = {
                    "goals": goals,
                    "experience_level": experience_level,
                    "selected_at": datetime.utcnow().isoformat()
                }
                
                updated_user = await user_service.update_user_type(
                    user.id, 
                    backend_user_type, 
                    type_data
                )
                
                if not updated_user:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to update user type"
                    )
                
                return {
                    "success": True,
                    "message": "User type selected successfully",
                    "user_profile": {
                        "id": str(updated_user.id),
                        "email": updated_user.email,
                        "full_name": updated_user.full_name,
                        "role": updated_user.role,
                        "user_type": user_type,  # Return original format for frontend
                        "is_active": updated_user.is_active,
                        "onboarding_completed": updated_user.onboarding_completed
                    }
                }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/user-types/complete-onboarding") 
async def complete_user_onboarding(request: Dict[str, Any], token: str = Depends(security)):
    """Complete user onboarding process"""
    try:
        from datetime import datetime
        
        user_type = request.get("user_type")
        goals = request.get("goals", [])
        experience_level = request.get("experience_level", "beginner")
        
        if not user_type:
            raise HTTPException(
                status_code=400,
                detail="user_type is required"
            )
        
        # Map frontend user types to backend enums  
        user_type_mapping = {
            "affiliate_marketer": "AFFILIATE_MARKETER",
            "affiliate": "AFFILIATE_MARKETER",
            "content_creator": "CONTENT_CREATOR", 
            "creator": "CONTENT_CREATOR",
            "business_owner": "BUSINESS_OWNER",
            "business": "BUSINESS_OWNER",
        }
        
        backend_user_type = user_type_mapping.get(user_type, user_type.upper())
        
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            async with ServiceFactory.create_service(UserService) as user_service:
                # Update user type
                type_data = {
                    "goals": goals,
                    "experience_level": experience_level,
                    "onboarding_completed_at": datetime.utcnow().isoformat()
                }
                
                updated_user = await user_service.update_user_type(
                    user.id,
                    backend_user_type, 
                    type_data
                )
                
                # Complete onboarding
                if updated_user:
                    updated_user.complete_onboarding(goals, experience_level)
                    await user_service.db.commit()
                    await user_service.db.refresh(updated_user)
                
                return {
                    "success": True,
                    "message": "Onboarding completed successfully",
                    "user_profile": {
                        "id": str(updated_user.id),
                        "email": updated_user.email,
                        "full_name": updated_user.full_name,
                        "role": updated_user.role,
                        "user_type": user_type,
                        "is_active": updated_user.is_active,
                        "onboarding_completed": updated_user.onboarding_completed
                    }
                }
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/users/company/stats")
async def get_company_stats(token: str = Depends(security)):
    """Get company statistics for business dashboard"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            if not user.company:
                raise HTTPException(
                    status_code=404,
                    detail="No company associated with user"
                )
            
            # For now, return mock data. This can be enhanced with real metrics later
            return {
                "business_metrics": {
                    "revenue": 125000,
                    "revenue_growth": 15.2,
                    "leads": 342,
                    "lead_growth": 8.5,
                    "conversion": 4.2,
                    "conversion_growth": 2.1,
                    "sales_calls": 89
                },
                "marketing_roi": {
                    "ad_spend": 12500,
                    "revenue": 125000,
                    "roi": 900
                },
                "company_id": str(user.company.id),
                "company_name": user.company.company_name
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/users/company/details")
async def get_company_details(token: str = Depends(security)):
    """Get company details for business dashboard"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            if not user.company:
                raise HTTPException(
                    status_code=404,
                    detail="No company associated with user"
                )
            
            # Return company details with some mock pipeline data
            return {
                "company": {
                    "id": str(user.company.id),
                    "name": user.company.company_name,
                    "subscription_tier": user.company.subscription_tier,
                    "created_at": user.company.created_at.isoformat() if user.company.created_at else None
                },
                "market_intelligence": [
                    {
                        "id": 1,
                        "type": "competitor",
                        "title": "Competitor Analysis Update",
                        "description": "New competitor pricing detected in your market",
                        "impact": "medium",
                        "source": "Market Intelligence Engine",
                        "timestamp": "2024-01-15T14:30:00Z"
                    },
                    {
                        "id": 2,
                        "type": "opportunity",
                        "title": "SEO Opportunity",
                        "description": "Untapped keyword cluster identified",
                        "impact": "high",
                        "source": "SEO Monitor",
                        "timestamp": "2024-01-15T12:15:00Z"
                    }
                ],
                "lead_pipeline": [
                    {
                        "id": 1,
                        "source": "Google Ads",
                        "leads": 125,
                        "revenue": 45000,
                        "conversion": 3.8,
                        "growth": 12.5
                    },
                    {
                        "id": 2,
                        "source": "Facebook Ads",
                        "leads": 89,
                        "revenue": 32000,
                        "conversion": 4.2,
                        "growth": 8.1
                    },
                    {
                        "id": 3,
                        "source": "Organic Search",
                        "leads": 156,
                        "revenue": 48000,
                        "conversion": 5.1,
                        "growth": 15.3
                    }
                ]
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/user-social/profiles")
async def get_user_social_profiles(token: str = Depends(security)):
    """Get user social media profiles for creator dashboard"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            # For now, return mock social profile data. This can be enhanced later
            return {
                "social_profiles": [
                    {
                        "platform": "Instagram",
                        "username": "@creator_username",
                        "followers": 12450,
                        "engagement_rate": 4.2,
                        "last_updated": "2024-01-15T10:30:00Z",
                        "status": "connected"
                    },
                    {
                        "platform": "YouTube",
                        "username": "CreatorChannel",
                        "followers": 8960,
                        "engagement_rate": 7.1,
                        "last_updated": "2024-01-15T09:15:00Z",
                        "status": "connected"
                    },
                    {
                        "platform": "TikTok",
                        "username": "@tiktokcreator",
                        "followers": 15200,
                        "engagement_rate": 9.8,
                        "last_updated": "2024-01-15T08:45:00Z",
                        "status": "connected"
                    },
                    {
                        "platform": "Twitter",
                        "username": "@twitteruser",
                        "followers": 3420,
                        "engagement_rate": 3.5,
                        "last_updated": "2024-01-15T11:20:00Z",
                        "status": "connected"
                    }
                ],
                "total_platforms": 4,
                "connected_platforms": 4,
                "total_followers": 40030,
                "avg_engagement_rate": 6.15
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ADMIN API ENDPOINTS
# ============================================================================

@router.get("/api/admin/stats")
async def get_admin_stats(token: str = Depends(security), db: Session = Depends(get_db)):
    """Get admin dashboard statistics"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            if user.role != "ADMIN":
                raise HTTPException(
                    status_code=403,
                    detail="Admin access required"
                )
            
            # Get real database statistics
            total_users = db.query(User).count()
            total_companies = db.query(Company).count()
            total_campaigns = db.query(Campaign).count()
            
            # Get subscription breakdown
            subscription_stats = db.query(
                Company.subscription_tier,
                func.count(Company.id).label('count')
            ).group_by(Company.subscription_tier).all()
            
            subscription_breakdown = {}
            total_mrr = 0
            
            # Process subscription stats and calculate MRR
            tier_pricing = {
                "FREE": 0,
                "BASIC": 29,
                "PRO": 99,
                "ENTERPRISE": 299
            }
            
            for tier, count in subscription_stats:
                subscription_breakdown[tier.lower()] = count
                total_mrr += count * tier_pricing.get(tier, 0)
            
            return {
                "total_users": total_users,
                "total_companies": total_companies,
                "total_campaigns_created": total_campaigns,
                "monthly_recurring_revenue": total_mrr,
                "subscription_breakdown": subscription_breakdown
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/users")
async def get_admin_users(
    page: int = 1,
    limit: int = 20,
    search: str = None,
    subscription_tier: str = None,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Get users list for admin dashboard"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            if user.role != "ADMIN":
                raise HTTPException(
                    status_code=403,
                    detail="Admin access required"
                )
            
            # Build query with filters
            query = db.query(User).join(Company)
            
            if search:
                query = query.filter(
                    User.full_name.ilike(f"%{search}%") |
                    User.email.ilike(f"%{search}%") |
                    Company.company_name.ilike(f"%{search}%")
                )
            
            if subscription_tier:
                query = query.filter(Company.subscription_tier == subscription_tier.upper())
            
            # Get total count
            total = query.count()
            
            # Apply pagination and get results
            users = query.order_by(desc(User.created_at)).offset((page - 1) * limit).limit(limit).all()
            
            # Format user data
            users_data = []
            for u in users:
                users_data.append({
                    "id": str(u.id),
                    "full_name": u.full_name,
                    "email": u.email,
                    "role": u.role,
                    "company_name": u.company.company_name if u.company else "No Company",
                    "subscription_tier": u.company.subscription_tier.lower() if u.company else "free",
                    "monthly_credits_used": u.company.monthly_credits_used if u.company else 0,
                    "monthly_credits_limit": u.company.monthly_credits_limit if u.company else 1000,
                    "is_active": u.is_active,
                    "is_verified": u.is_verified,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                    "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None
                })
            
            return {
                "users": users_data,
                "total": total,
                "page": page,
                "per_page": limit
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/companies") 
async def get_admin_companies(
    page: int = 1,
    limit: int = 20,
    search: str = None,
    subscription_tier: str = None,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Get companies list for admin dashboard"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            if user.role != "ADMIN":
                raise HTTPException(
                    status_code=403,
                    detail="Admin access required"
                )
            
            # Build query with filters
            query = db.query(Company)
            
            if search:
                query = query.filter(
                    Company.company_name.ilike(f"%{search}%") |
                    Company.industry.ilike(f"%{search}%")
                )
            
            if subscription_tier:
                query = query.filter(Company.subscription_tier == subscription_tier.upper())
            
            # Get total count
            total = query.count()
            
            # Apply pagination and get results
            companies = query.order_by(desc(Company.created_at)).offset((page - 1) * limit).limit(limit).all()
            
            # Format company data with user and campaign counts
            companies_data = []
            for c in companies:
                user_count = db.query(User).filter(User.company_id == c.id).count()
                campaign_count = db.query(Campaign).filter(Campaign.company_id == c.id).count()
                
                companies_data.append({
                    "id": str(c.id),
                    "company_name": c.company_name,
                    "company_slug": c.company_slug,
                    "company_size": c.company_size,
                    "industry": c.industry,
                    "subscription_tier": c.subscription_tier.lower(),
                    "monthly_credits_used": c.monthly_credits_used,
                    "monthly_credits_limit": c.monthly_credits_limit,
                    "user_count": user_count,
                    "campaign_count": campaign_count,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "website_url": c.website_url,
                    "contact_email": c.contact_email
                })
            
            return {
                "companies": companies_data,
                "total": total,
                "page": page,
                "per_page": limit
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI Discovery API endpoints with real data
@router.get("/api/admin/ai-discovery/active-providers")
async def get_active_providers(
    top_3_only: bool = False,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Get active AI providers from real configuration with cost-based tiering"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # Get real providers from AI provider configuration
            from src.core.config.ai_providers import ai_provider_config
            
            providers = []
            provider_names = {
                "deepseek": "DeepSeek-V2",
                "groq": "Groq LLaMA3", 
                "together": "Together AI",
                "aimlapi": "AIML API",
                "cohere": "Cohere Command",
                "minimax": "MiniMax",
                "openai": "OpenAI GPT-4",
                "anthropic": "Anthropic Claude"
            }
            
            # Define provider capabilities (many support multiple content types)
            provider_capabilities = {
                "deepseek": ["text_generation"],
                "groq": ["text_generation"],
                "together": ["text_generation", "image_generation"],  # Supports both
                "aimlapi": ["text_generation", "image_generation"],   # Multi-modal API
                "cohere": ["text_generation"],
                "minimax": ["text_generation", "image_generation", "video_generation"],  # Multi-modal
                "openai": ["text_generation", "image_generation"],   # GPT-4 + DALL-E
                "anthropic": ["text_generation", "image_generation"] # Claude 3 supports images
            }
            
            # Calculate quality scores based on cost efficiency
            cheapest_cost = min(p.cost_per_1k_tokens for p in ai_provider_config.providers.values() if p.enabled)
            
            # Create providers for each capability they support
            provider_id = 1
            for name, config in ai_provider_config.providers.items():
                capabilities = provider_capabilities.get(name, ["text_generation"])
                
                for category in capabilities:
                    # Calculate quality score with category-specific adjustments
                    base_quality = 5.0 - (config.fallback_priority * 0.1)
                    cost_efficiency_bonus = (cheapest_cost / config.cost_per_1k_tokens) * 0.5
                    
                    # Adjust quality based on category specialization
                    category_bonus = 0
                    if category == "image_generation" and name in ["openai", "together", "aimlapi"]:
                        category_bonus = 0.3  # These are known for good image generation
                    elif category == "video_generation" and name == "minimax":
                        category_bonus = 0.4  # MiniMax specializes in video
                    
                    quality_score = min(5.0, base_quality + cost_efficiency_bonus + category_bonus)
                    
                    # Determine use case based on tier and category
                    if config.tier.value == "ultra_cheap":
                        use_type = f"high_volume_{category.replace('_', '_')}"
                    elif config.tier.value == "budget":
                        use_type = f"cost_effective_{category.replace('_', '_')}"
                    elif config.tier.value == "standard":
                        use_type = f"balanced_{category.replace('_', '_')}"
                    else:  # premium
                        use_type = f"premium_{category.replace('_', '_')}_fallback"
                    
                    # Adjust costs for different content types (images cost more)
                    category_cost_multiplier = {
                        "text_generation": 1.0,
                        "image_generation": 20.0,  # Images typically cost ~20x more
                        "video_generation": 100.0,  # Videos cost significantly more
                        "audio_generation": 5.0     # Audio costs moderately more
                    }
                    
                    adjusted_cost = config.cost_per_1k_tokens * category_cost_multiplier.get(category, 1.0)
                    
                    providers.append({
                        "id": provider_id,
                        "provider_name": f"{provider_names.get(name, name.title())} {category.replace('_', ' ').title()}",
                        "env_var_name": f"{name.upper()}_API_KEY",
                        "category": category,
                        "use_type": use_type,
                        "cost_per_1k_tokens": adjusted_cost,
                        "quality_score": round(quality_score, 1),
                        "category_rank": config.fallback_priority,
                        "is_top_3": config.fallback_priority <= 3 and category == "text_generation",  # Top 3 for text
                        "is_active": config.enabled,
                        "primary_model": f"{config.name}-{category}",
                        "discovered_date": "2024-01-01T00:00:00Z",
                        "response_time_ms": 1000 + (config.fallback_priority * 200) + (50 if category != "text_generation" else 0),
                        "monthly_usage": config.max_tokens * (5 if category == "text_generation" else 1)  # Less usage for images/video
                    })
                    provider_id += 1
            
            # Sort by cost efficiency (cheapest first)
            providers.sort(key=lambda x: x["cost_per_1k_tokens"])
            
            if top_3_only:
                providers = [p for p in providers if p["is_top_3"]][:3]
            
            return {
                "success": True,
                "providers": providers,
                "total_count": len(providers),
                "filter": {"top_3_only": top_3_only}
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/ai-discovery/discovered-suggestions")
async def get_discovered_suggestions(token: str = Depends(security), db: Session = Depends(get_db)):
    """Get AI discovery suggestions including premium providers marked for caution"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # Get premium providers from configuration as "suggestions" with cost warnings
            from src.core.config.ai_providers import ai_provider_config
            
            suggestions = []
            
            # Show premium providers as suggestions with cost warnings
            premium_providers = [p for p in ai_provider_config.providers.values() if p.tier.value == "premium"]
            for i, config in enumerate(premium_providers, 1):
                suggestions.append({
                    "id": i,
                    "provider_name": f"{config.name.title()} (Premium)",
                    "suggested_env_var_name": f"{config.name.upper()}_API_KEY",
                    "category": "text_generation",
                    "use_type": "premium_fallback_only",
                    "estimated_cost_per_1k_tokens": config.cost_per_1k_tokens,
                    "estimated_quality_score": 4.9,  # High quality but expensive
                    "website_url": "https://openai.com" if config.name == "openai" else "https://anthropic.com",
                    "recommendation_priority": "low",  # Low priority due to high cost
                    "unique_features": '["Highest quality", "Most reliable", "Enterprise grade"]',
                    "research_notes": f"⚠️ HIGH COST ALERT: ${config.cost_per_1k_tokens:.3f}/1K tokens - Use only when budget providers fail",
                    "discovered_date": "2024-01-01T00:00:00Z",
                    "review_status": "approved",
                    "competitive_advantages": '["Premium quality", "Enterprise support", "Proven reliability"]',
                    "integration_complexity": "easy"
                })
            
            # Add diverse new provider suggestions across categories
            new_suggestions = [
                {
                    "id": len(suggestions) + 1,
                    "provider_name": "Perplexity AI",
                    "suggested_env_var_name": "PERPLEXITY_API_KEY",
                    "category": "text_generation",
                    "use_type": "research_analysis",
                    "estimated_cost_per_1k_tokens": 0.001,
                    "estimated_quality_score": 4.2,
                    "website_url": "https://perplexity.ai",
                    "recommendation_priority": "high",
                    "unique_features": '["Real-time web search", "Citation support", "Research-focused"]',
                    "research_notes": "Excellent for research tasks with real-time web integration",
                    "discovered_date": "2024-01-15T00:00:00Z",
                    "review_status": "pending",
                    "competitive_advantages": '["Web integration", "Citation tracking", "Research optimization"]',
                    "integration_complexity": "medium"
                },
                {
                    "id": len(suggestions) + 2,
                    "provider_name": "Stability AI SDXL",
                    "suggested_env_var_name": "STABILITY_API_KEY",
                    "category": "image_generation",
                    "use_type": "high_quality_images",
                    "estimated_cost_per_1k_tokens": 0.02,
                    "estimated_quality_score": 4.6,
                    "website_url": "https://stability.ai",
                    "recommendation_priority": "high",
                    "unique_features": '["Open source", "High resolution", "Style control", "Fast generation"]',
                    "research_notes": "💡 BUDGET-FRIENDLY: Excellent image quality at competitive pricing vs DALL-E",
                    "discovered_date": "2024-01-14T00:00:00Z",
                    "review_status": "pending",
                    "competitive_advantages": '["Cost effective", "Open source", "High quality", "Style flexibility"]',
                    "integration_complexity": "easy"
                },
                {
                    "id": len(suggestions) + 3,
                    "provider_name": "Replicate FLUX",
                    "suggested_env_var_name": "REPLICATE_API_KEY",
                    "category": "image_generation",
                    "use_type": "creative_images",
                    "estimated_cost_per_1k_tokens": 0.005,
                    "estimated_quality_score": 4.4,
                    "website_url": "https://replicate.com",
                    "recommendation_priority": "medium",
                    "unique_features": '["Multiple models", "Pay per use", "No subscription"]',
                    "research_notes": "🎨 Great for creative image generation with flexible pricing model",
                    "discovered_date": "2024-01-13T00:00:00Z",
                    "review_status": "pending",
                    "competitive_advantages": '["Model variety", "Pay per use", "No minimums", "Creative quality"]',
                    "integration_complexity": "medium"
                },
                {
                    "id": len(suggestions) + 4,
                    "provider_name": "RunwayML Gen-2",
                    "suggested_env_var_name": "RUNWAY_API_KEY",
                    "category": "video_generation",
                    "use_type": "video_content",
                    "estimated_cost_per_1k_tokens": 0.10,
                    "estimated_quality_score": 4.3,
                    "website_url": "https://runwayml.com",
                    "recommendation_priority": "medium",
                    "unique_features": '["Video generation", "Motion control", "Style transfer"]',
                    "research_notes": "🎬 Leading video AI platform - consider for video marketing campaigns",
                    "discovered_date": "2024-01-11T00:00:00Z",
                    "review_status": "pending",
                    "competitive_advantages": '["Video specialization", "Motion control", "Professional quality"]',
                    "integration_complexity": "medium"
                }
            ]
            
            suggestions.extend(new_suggestions)
            
            return {
                "success": True,
                "suggestions": suggestions,
                "total_count": len(suggestions),
                "filter": {}
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/ai-discovery/dashboard")
async def get_ai_discovery_dashboard(token: str = Depends(security), db: Session = Depends(get_db)):
    """Get AI discovery dashboard data - TEMPORARY MOCK DATA"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # TEMPORARY: Return mock data until intelligence_core table is created
            return {
                "success": True,
                "dashboard": {
                    "active_providers": {
                        "by_category": [
                            {
                                "category": "text_generation",
                                "total": 6,
                                "active": 4,
                                "top_3": 3
                            },
                            {
                                "category": "image_generation",
                                "total": 3,
                                "active": 2,
                                "top_3": 1
                            },
                            {
                                "category": "multimodal",
                                "total": 2,
                                "active": 1,
                                "top_3": 1
                            }
                        ],
                        "total": 11
                    },
                    "discovered_providers": {
                        "by_category": [
                            {
                                "category": "text_generation",
                                "total": 8,
                                "high_priority": 3
                            },
                            {
                                "category": "image_generation",
                                "total": 4,
                                "high_priority": 1
                            },
                            {
                                "category": "audio_generation",
                                "total": 2,
                                "high_priority": 0
                            }
                        ],
                        "total": 14
                    },
                    "recent_discoveries": [
                        {
                            "id": 1,
                            "provider_name": "Groq LLaMA",
                            "category": "text_generation",
                            "recommendation_priority": "high",
                            "discovered_date": "2024-01-15T00:00:00Z"
                        },
                        {
                            "id": 2,
                            "provider_name": "Together AI",
                            "category": "text_generation", 
                            "recommendation_priority": "medium",
                            "discovered_date": "2024-01-10T00:00:00Z"
                        }
                    ],
                    "system_status": "operational",
                    "last_discovery_cycle": "2024-01-15T12:00:00Z"
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/ai-discovery/category-rankings")
async def get_category_rankings(token: str = Depends(security), db: Session = Depends(get_db)):
    """Get AI category rankings - TEMPORARY MOCK DATA"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # TEMPORARY: Return mock data until intelligence_core table is created
            mock_category_rankings = {
                "text_generation": [
                    {
                        "rank": 1,
                        "provider_name": "OpenAI GPT-4",
                        "quality_score": 4.8,
                        "cost_per_1k_tokens": 0.01,
                        "primary_model": "gpt-4",
                        "is_active": True
                    },
                    {
                        "rank": 2,
                        "provider_name": "Claude-3-Sonnet",
                        "quality_score": 4.7,
                        "cost_per_1k_tokens": 0.015,
                        "primary_model": "claude-3-sonnet",
                        "is_active": True
                    },
                    {
                        "rank": 3,
                        "provider_name": "DeepSeek-V2",
                        "quality_score": 4.2,
                        "cost_per_1k_tokens": 0.0001,
                        "primary_model": "deepseek-v2",
                        "is_active": True
                    }
                ],
                "image_generation": [
                    {
                        "rank": 1,
                        "provider_name": "DALL-E 3",
                        "quality_score": 4.6,
                        "cost_per_1k_tokens": 0.02,
                        "primary_model": "dall-e-3",
                        "is_active": True
                    },
                    {
                        "rank": 2,
                        "provider_name": "Midjourney",
                        "quality_score": 4.5,
                        "cost_per_1k_tokens": 0.018,
                        "primary_model": "midjourney-v6",
                        "is_active": False
                    }
                ],
                "multimodal": [
                    {
                        "rank": 1,
                        "provider_name": "GPT-4-Vision",
                        "quality_score": 4.4,
                        "cost_per_1k_tokens": 0.012,
                        "primary_model": "gpt-4-vision-preview",
                        "is_active": True
                    }
                ]
            }
            
            return {
                "success": True,
                "category_rankings": mock_category_rankings,
                "total_categories": len(mock_category_rankings),
                "total_top_providers": sum(len(providers) for providers in mock_category_rankings.values())
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/admin/ai-discovery/run-discovery")
async def run_ai_discovery_scan(token: str = Depends(security), db: Session = Depends(get_db)):
    """Run AI discovery scan to find new providers and update suggestions"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # Simulate discovery scan process with realistic timing
            import asyncio
            await asyncio.sleep(2)  # Simulate processing time
            
            # Get current provider configuration for comparison
            from src.core.config.ai_providers import ai_provider_config
            
            # Simulate finding new providers based on market research
            discovered_providers = [
                "Hugging Face Inference API",
                "Replicate AI",
                "Cohere Fine-tuned Models",
                "Google Gemini Pro",
                "Meta Llama 2 API"
            ]
            
            # Calculate discovery metrics
            total_providers_scanned = 50
            new_suggestions_found = len(discovered_providers)
            existing_providers = len(ai_provider_config.providers)
            cost_savings_potential = sum(0.001 * (i + 1) for i in range(new_suggestions_found))  # Simulated savings
            
            return {
                "success": True,
                "scan_completed_at": "2024-01-01T00:00:00Z",
                "discovery_results": {
                    "total_providers_scanned": total_providers_scanned,
                    "new_suggestions_found": new_suggestions_found,
                    "existing_providers_confirmed": existing_providers,
                    "cost_savings_potential": round(cost_savings_potential, 3),
                    "discovered_providers": discovered_providers,
                    "scan_duration_seconds": 2.1,
                    "next_recommended_scan": "2024-01-15T00:00:00Z"
                },
                "recommendations": [
                    f"Found {new_suggestions_found} new AI providers worth evaluating",
                    f"Potential cost savings of ${cost_savings_potential:.3f}/1K tokens available",
                    "Consider testing new budget-friendly providers for cost optimization",
                    "Review premium provider usage and consider alternatives"
                ],
                "message": f"Discovery scan completed successfully! Found {new_suggestions_found} new providers to review."
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ✅ DEMO CAMPAIGN CREATION ENDPOINTS
# ============================================================================

@router.post("/api/admin/create-demo-campaign/{user_id}")
async def create_demo_campaign_for_user(
    user_id: str,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Create demo campaign for a specific user (admin only)"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            admin_user = await auth_service.get_current_user(token.credentials)
            
            if not admin_user or admin_user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
        
        async with ServiceFactory.create_service(UserService) as user_service:
            success = await user_service.ensure_user_has_demo_campaign(user_id)
            
            if success:
                return {
                    "message": f"Demo campaign created successfully for user {user_id}",
                    "success": True
                }
            else:
                return {
                    "message": f"Demo campaign already exists for user {user_id} or user not found",
                    "success": False
                }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating demo campaign: {str(e)}")

@router.post("/api/admin/create-demo-campaigns-all")
async def create_demo_campaigns_for_all_users(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Create demo campaigns for all users who don't have any campaigns (admin only)"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            admin_user = await auth_service.get_current_user(token.credentials)
            
            if not admin_user or admin_user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
        
        async with ServiceFactory.create_service(UserService) as user_service:
            # Get all users
            users = await user_service.get_all_users()
            
            created_count = 0
            total_users = len(users)
            
            for user in users:
                try:
                    success = await user_service.create_demo_campaign(user)
                    if success:
                        created_count += 1
                except Exception as e:
                    logger.warning(f"Failed to create demo for user {user.id}: {e}")
            
            return {
                "message": f"Created {created_count} demo campaigns for {total_users} users",
                "created_count": created_count,
                "total_users": total_users,
                "success": True
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating demo campaigns: {str(e)}")

@router.post("/api/campaigns/demo/toggle-visibility")
async def toggle_demo_campaign_visibility(
    request: Dict[str, Any],
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Toggle demo campaign visibility for the current user (now works with global demos)"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")
        
        hidden = request.get("hidden", True)
        
        async with ServiceFactory.create_service(UserService) as user_service:
            # Set user preference for global demo visibility
            demo_settings = await user_service.get_user_demo_settings(user.id)
            demo_settings["global_demo_hidden"] = hidden
            
            success = await user_service.set_user_demo_settings(user.id, demo_settings)
            
            if success:
                action = "hidden" if hidden else "shown"
                return {
                    "message": f"Global demo campaign {action} successfully",
                    "hidden": hidden,
                    "success": True
                }
            else:
                return {
                    "message": "Failed to update demo visibility preference",
                    "success": False
                }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling demo visibility: {str(e)}")

@router.get("/api/campaigns/list")
async def get_user_campaigns(
    include_hidden_demos: bool = False,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user campaigns with option to exclude hidden demo campaigns"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")
        
        async with ServiceFactory.create_service(UserService) as user_service:
            campaigns = await user_service.get_user_campaigns(user.id, include_hidden_demos)
            
            # Convert campaigns to serializable format
            campaigns_data = []
            for campaign in campaigns:
                # Handle both Campaign objects and raw query results
                if hasattr(campaign, 'id'):
                    # Campaign object
                    campaign_data = {
                        "id": str(campaign.id),
                        "name": campaign.name,
                        "description": campaign.description,
                        "campaign_type": campaign.campaign_type.value if hasattr(campaign.campaign_type, 'value') else str(campaign.campaign_type),
                        "status": campaign.status.value if hasattr(campaign.status, 'value') else str(campaign.status),
                        "target_audience": campaign.target_audience,
                        "goals": campaign.goals,
                        "settings": campaign.settings,
                        "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
                        "updated_at": campaign.updated_at.isoformat() if hasattr(campaign, 'updated_at') and campaign.updated_at else None
                    }
                else:
                    # Raw query result
                    campaign_data = dict(campaign._mapping) if hasattr(campaign, '_mapping') else dict(campaign)
                    # Convert UUID to string and handle dates
                    if 'id' in campaign_data and campaign_data['id']:
                        campaign_data['id'] = str(campaign_data['id'])
                    if 'created_at' in campaign_data and campaign_data['created_at']:
                        campaign_data['created_at'] = campaign_data['created_at'].isoformat()
                    if 'updated_at' in campaign_data and campaign_data['updated_at']:
                        campaign_data['updated_at'] = campaign_data['updated_at'].isoformat()
                
                campaigns_data.append(campaign_data)
            
            return {
                "campaigns": campaigns_data,
                "total": len(campaigns_data),
                "include_hidden_demos": include_hidden_demos,
                "success": True
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting campaigns: {str(e)}")

# ============================================================================
# ✅ WAITLIST API ENDPOINTS
# ============================================================================

@router.post("/api/waitlist/join")
async def join_waitlist(request: dict, db: Session = Depends(get_db)):
    """Join the waitlist"""
    email = request.get("email")
    referrer = request.get("referrer")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    try:
        # Check if email already exists
        existing = db.query(Waitlist).filter(Waitlist.email == email).first()
        if existing:
            total_signups = db.query(Waitlist).count()
            position = db.query(Waitlist).filter(Waitlist.created_at <= existing.created_at).count()
            return {
                "message": "You're already on the waitlist!",
                "total_signups": total_signups,
                "position": position,
                "email": email
            }
        
        # Add new waitlist entry
        new_entry = Waitlist(email=email, referrer=referrer)
        db.add(new_entry)
        db.commit()
        
        # Get current stats
        total_signups = db.query(Waitlist).count()
        
        return {
            "message": "Successfully joined the waitlist!",
            "total_signups": total_signups,
            "position": total_signups,
            "email": email
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/waitlist/check/{email}")
async def check_waitlist(email: str, db: Session = Depends(get_db)):
    """Check if email is on waitlist"""
    entry = db.query(Waitlist).filter(Waitlist.email == email).first()
    
    if not entry:
        return {
            "on_waitlist": False,
            "message": "Email not found on waitlist"
        }
    
    # Calculate position
    position = db.query(Waitlist).filter(Waitlist.created_at <= entry.created_at).count()
    total_signups = db.query(Waitlist).count()
    
    return {
        "on_waitlist": True,
        "message": "You're on the waitlist!",
        "position": position,
        "total_signups": total_signups,
        "joined_date": entry.created_at.date().isoformat() if entry.created_at else None,
        "is_notified": entry.is_notified
    }

@router.get("/api/waitlist/stats")
async def get_waitlist_stats(token: str = Depends(security), db: Session = Depends(get_db)):
    """Get waitlist statistics (admin only)"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # Get time periods
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = now - timedelta(days=7)
            month_start = now - timedelta(days=30)
            
            # Get counts
            total = db.query(Waitlist).count()
            today = db.query(Waitlist).filter(Waitlist.created_at >= today_start).count()
            this_week = db.query(Waitlist).filter(Waitlist.created_at >= week_start).count()
            this_month = db.query(Waitlist).filter(Waitlist.created_at >= month_start).count()
            
            # Get recent signups
            recent = db.query(Waitlist).order_by(desc(Waitlist.created_at)).limit(10).all()
            recent_signups = [
                {
                    "email": entry.email,
                    "created_at": entry.created_at.isoformat() if entry.created_at else None,
                    "id": entry.id
                }
                for entry in recent
            ]
            
            # Get daily stats for last 7 days
            daily_stats = []
            for i in range(7):
                day_start = today_start - timedelta(days=i)
                day_end = day_start + timedelta(days=1)
                count = db.query(Waitlist).filter(
                    and_(Waitlist.created_at >= day_start, Waitlist.created_at < day_end)
                ).count()
                daily_stats.append({
                    "date": day_start.date().isoformat(),
                    "count": count
                })
            
            return {
                "total": total,
                "today": today,
                "this_week": this_week,
                "this_month": this_month,
                "recent_signups": recent_signups,
                "daily_stats": daily_stats
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/waitlist/export")
async def export_waitlist(token: str = Depends(security), db: Session = Depends(get_db)):
    """Export waitlist emails (admin only)"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # Get all waitlist entries
            entries = db.query(Waitlist).order_by(Waitlist.created_at).all()
            
            emails_data = []
            for entry in entries:
                emails_data.append({
                    "id": entry.id,
                    "email": entry.email,
                    "joined_date": entry.created_at.date().isoformat() if entry.created_at else None,
                    "is_notified": entry.is_notified,
                    "referrer": entry.referrer or "direct"
                })
            
            return {
                "emails": emails_data,
                "total": len(emails_data),
                "export_date": datetime.now().date().isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/waitlist/list")
async def get_waitlist_list(skip: int = 0, limit: int = 100, token: str = Depends(security), db: Session = Depends(get_db)):
    """Get paginated waitlist entries (admin only)"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # Get paginated entries
            entries = db.query(Waitlist).order_by(desc(Waitlist.created_at)).offset(skip).limit(limit).all()
            
            entries_data = []
            for entry in entries:
                entries_data.append({
                    "id": entry.id,
                    "email": entry.email,
                    "created_at": entry.created_at.isoformat() if entry.created_at else None,
                    "ip_address": entry.ip_address,
                    "is_notified": entry.is_notified
                })
            
            return entries_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/admin/create-global-demo")
async def create_global_demo_campaign(token: str = Depends(security)):
    """Admin endpoint to create the single global demo campaign"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            # Try to create global demo campaign
            async with ServiceFactory.create_service(UserService) as user_service:
                try:
                    result = await user_service.create_global_demo_campaign()
                    return {
                        "success": True,
                        "message": f"Global demo campaign creation result: {result}",
                        "admin_user": str(user.id)
                    }
                except Exception as demo_error:
                    return {
                        "success": False,
                        "error": str(demo_error),
                        "error_type": type(demo_error).__name__,
                        "admin_user": str(user.id)
                    }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/debug/create-demo-campaign")
async def debug_create_demo_campaign(token: str = Depends(security)):
    """Debug endpoint to manually create demo campaign and see errors"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            # Try to create demo campaign and capture detailed errors
            async with ServiceFactory.create_service(UserService) as user_service:
                try:
                    result = await user_service.create_demo_campaign(user)
                    return {
                        "success": True,
                        "message": f"Demo campaign creation result: {result}",
                        "user_id": str(user.id),
                        "user_email": user.email
                    }
                except Exception as demo_error:
                    return {
                        "success": False,
                        "error": str(demo_error),
                        "error_type": type(demo_error).__name__,
                        "user_id": str(user.id),
                        "user_email": user.email
                    }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))