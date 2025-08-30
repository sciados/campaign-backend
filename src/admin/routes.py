# /app/src/admin/routes.py - COMPLETE CRUD MIGRATED VERSION WITH RAILWAY INTEGRATION
"""
Admin routes for user and company management - CRUD MIGRATED VERSION
🎯 All database operations now use CRUD patterns
✅ Eliminates direct SQLAlchemy queries and raw SQL
✅ Consistent with successful high-priority file migrations
🛤️ NEW: Railway Environment Variable Management for AI Providers
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os
import logging

from src.core.database import get_async_db
from src.auth.dependencies import get_current_user
from src.admin.schemas import (
    UserListResponse, CompanyListResponse, AdminStatsResponse,
    UserUpdateRequest, CompanyUpdateRequest, UserCreateRequest,
    SubscriptionUpdateRequest, AdminUserResponse, AdminCompanyResponse
)
from src.models.user import User
from src.models.company import Company, CompanyMembership, CompanySubscriptionTier
from src.models.campaign import Campaign

# 🔧 CRUD IMPORTS - Using proven CRUD patterns
from src.core.crud.campaign_crud import CampaignCRUD
from src.core.crud.base_crud import BaseCRUD

# ✅ Initialize CRUD instances
campaign_crud = CampaignCRUD()
user_crud = BaseCRUD(User)
company_crud = BaseCRUD(Company)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["admin"])

async def require_admin(current_user: User = Depends(get_current_user)):
    """Require admin role for admin endpoints"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Admin access required. Only platform administrators can access this area."
        )
    return current_user

# ============================================================================
# 🛤️ RAILWAY ENVIRONMENT VARIABLE MANAGEMENT SERVICE
# ============================================================================

class RailwayEnvironmentService:
    """Service to manage Railway environment variables for AI providers"""
    
    def __init__(self):
        # AI Providers Configuration - Your existing Railway environment variables
        self.existing_providers = [
            {
                "id": "groq",
                "provider_name": "Groq",
                "env_var_name": "GROQ_API_KEY",
                "category": "content_generation",
                "priority_tier": "primary",
                "cost_per_1k_tokens": 0.0002,
                "api_endpoint": "https://api.groq.com/openai/v1",
                "model": "llama-3.3-70b-versatile",
                "capabilities": ["text_generation", "code_generation", "analysis"]
            },
            {
                "id": "deepseek",
                "provider_name": "DeepSeek",
                "env_var_name": "DEEPSEEK_API_KEY",
                "category": "analysis",
                "priority_tier": "primary",
                "cost_per_1k_tokens": 0.0002,
                "api_endpoint": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "capabilities": ["analysis", "reasoning", "math"]
            },
            {
                "id": "together",
                "provider_name": "Together AI",
                "env_var_name": "TOGETHER_API_KEY",
                "category": "content_generation",
                "priority_tier": "primary",
                "cost_per_1k_tokens": 0.0003,
                "api_endpoint": "https://api.together.xyz/v1",
                "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                "capabilities": ["text_generation", "reasoning", "code_generation"]
            },
            {
                "id": "aimlapi",
                "provider_name": "AIML API",
                "env_var_name": "AIMLAPI_API_KEY",
                "category": "content_generation",
                "priority_tier": "secondary",
                "cost_per_1k_tokens": 0.0004,
                "api_endpoint": "https://api.aimlapi.com/v1",
                "model": "various",
                "capabilities": ["text_generation", "analysis"]
            },
            {
                "id": "minimax",
                "provider_name": "MiniMax",
                "env_var_name": "MINIMAX_API_KEY",
                "category": "content_generation",
                "priority_tier": "secondary",
                "cost_per_1k_tokens": 0.0005,
                "api_endpoint": "https://api.minimax.chat/v1",
                "model": "various",
                "capabilities": ["text_generation", "chat"]
            },
            {
                "id": "openai",
                "provider_name": "OpenAI GPT-4",
                "env_var_name": "OPENAI_API_KEY",
                "category": "premium_generation",
                "priority_tier": "expensive",
                "cost_per_1k_tokens": 0.03,
                "api_endpoint": "https://api.openai.com/v1",
                "model": "gpt-4",
                "capabilities": ["text_generation", "code_generation", "analysis", "reasoning"]
            },
            {
                "id": "anthropic",
                "provider_name": "Claude 3 Sonnet",
                "env_var_name": "ANTHROPIC_API_KEY",
                "category": "premium_analysis",
                "priority_tier": "expensive",
                "cost_per_1k_tokens": 0.015,
                "api_endpoint": "https://api.anthropic.com/v1",
                "model": "claude-3-sonnet-20240229",
                "capabilities": ["analysis", "reasoning", "code_review", "writing"]
            },
            {
                "id": "cohere",
                "provider_name": "Cohere",
                "env_var_name": "COHERE_API_KEY",
                "category": "analysis",
                "priority_tier": "expensive",
                "cost_per_1k_tokens": 0.002,
                "api_endpoint": "https://api.cohere.ai/v1",
                "model": "command-r-plus",
                "capabilities": ["text_generation", "embeddings", "classification"]
            },
            {
                "id": "stability",
                "provider_name": "Stability AI",
                "env_var_name": "STABILITY_API_KEY",
                "category": "image_generation",
                "priority_tier": "specialized",
                "cost_per_1k_tokens": 0.02,
                "api_endpoint": "https://api.stability.ai/v1",
                "model": "stable-diffusion",
                "capabilities": ["image_generation", "image_editing"]
            },
            {
                "id": "replicate",
                "provider_name": "Replicate",
                "env_var_name": "REPLICATE_API_TOKEN",
                "category": "image_generation",
                "priority_tier": "specialized",
                "cost_per_1k_tokens": 0.025,
                "api_endpoint": "https://api.replicate.com/v1",
                "model": "various",
                "capabilities": ["image_generation", "video_generation", "audio"]
            },
            {
                "id": "fal",
                "provider_name": "FAL AI",
                "env_var_name": "FAL_API_KEY",
                "category": "image_generation",
                "priority_tier": "specialized",
                "cost_per_1k_tokens": 0.015,
                "api_endpoint": "https://fal.ai/api",
                "model": "various",
                "capabilities": ["image_generation", "real_time_inference"]
            }
        ]
        
        # Discovered providers (simulation for now, will be real AI discovery later)
        self.discovered_providers = [
            {
                "id": "fireworks",
                "provider_name": "Fireworks AI",
                "env_var_name": "FIREWORKS_API_KEY",
                "category": "content_generation",
                "priority_tier": "discovered",
                "cost_per_1k_tokens": 0.0001,
                "api_endpoint": "https://api.fireworks.ai/v1",
                "model": "llama-v3p1-405b-instruct",
                "capabilities": ["text_generation", "code_generation", "reasoning"],
                "discovery_source": "artificialanalysis.ai",
                "cost_savings_vs_baseline": 50,
                "recommended_for": ["Replace Groq for even cheaper costs"],
                "integration_difficulty": "easy",
                "railway_setup_instructions": [
                    "Go to Railway Dashboard → Your Project",
                    "Click 'Variables' tab",
                    "Add FIREWORKS_API_KEY with your API key from fireworks.ai",
                    "Add FIREWORKS_BASE_URL=https://api.fireworks.ai/v1 (optional)",
                    "Deploy changes"
                ]
            },
            {
                "id": "perplexity",
                "provider_name": "Perplexity API",
                "env_var_name": "PERPLEXITY_API_KEY",
                "category": "analysis",
                "priority_tier": "discovered",
                "cost_per_1k_tokens": 0.0001,
                "api_endpoint": "https://api.perplexity.ai/chat/completions",
                "model": "llama-3.1-sonar-large-128k-online",
                "capabilities": ["analysis", "search", "real_time_data"],
                "discovery_source": "perplexity.ai/pricing",
                "cost_savings_vs_baseline": 50,
                "recommended_for": ["Replace DeepSeek for real-time analysis"],
                "integration_difficulty": "easy",
                "railway_setup_instructions": [
                    "Go to Railway Dashboard → Your Project",
                    "Click 'Variables' tab",
                    "Add PERPLEXITY_API_KEY with your API key from perplexity.ai",
                    "Add PERPLEXITY_BASE_URL=https://api.perplexity.ai (optional)",
                    "Deploy changes"
                ]
            }
        ]
    
    async def check_railway_env_vars(self) -> Dict[str, Any]:
        """Check which environment variables are actually configured in Railway"""
        try:
            all_providers = self.existing_providers + self.discovered_providers
            
            results = {
                "total_providers": len(all_providers),
                "configured_count": 0,
                "missing_count": 0,
                "configured_providers": [],
                "missing_providers": [],
                "by_tier": {
                    "primary": {"total": 0, "configured": 0},
                    "secondary": {"total": 0, "configured": 0},
                    "expensive": {"total": 0, "configured": 0},
                    "specialized": {"total": 0, "configured": 0},
                    "discovered": {"total": 0, "configured": 0}
                }
            }
            
            for provider in all_providers:
                env_var_exists = os.getenv(provider['env_var_name']) is not None
                tier = provider['priority_tier']
                
                # Count by tier
                results["by_tier"][tier]["total"] += 1
                if env_var_exists:
                    results["by_tier"][tier]["configured"] += 1
                
                # Overall counts
                if env_var_exists:
                    results["configured_count"] += 1
                    results["configured_providers"].append({
                        "name": provider['provider_name'],
                        "env_var": provider['env_var_name'],
                        "tier": tier,
                        "category": provider['category']
                    })
                else:
                    results["missing_count"] += 1
                    results["missing_providers"].append({
                        "name": provider['provider_name'],
                        "env_var": provider['env_var_name'],
                        "tier": tier,
                        "category": provider['category'],
                        "setup_instructions": provider.get('railway_setup_instructions', [
                            f"Go to Railway Dashboard → Your Project",
                            f"Click 'Variables' tab",
                            f"Add {provider['env_var_name']} with your API key",
                            f"Deploy changes"
                        ])
                    })
                
                logger.info(f"Provider {provider['provider_name']}: {provider['env_var_name']} = {'✅' if env_var_exists else '❌'}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error checking Railway environment variables: {e}")
            raise
    
    async def get_provider_summary(self) -> Dict[str, Any]:
        """Get summary of all AI providers with Railway integration status"""
        try:
            all_providers = self.existing_providers + self.discovered_providers
            
            # Check environment variables
            env_check = await self.check_railway_env_vars()
            
            provider_summary = []
            for provider in all_providers:
                env_var_exists = os.getenv(provider['env_var_name']) is not None
                
                summary_item = {
                    "id": provider['id'],
                    "provider_name": provider['provider_name'],
                    "env_var_name": provider['env_var_name'],
                    "env_var_configured": env_var_exists,
                    "category": provider['category'],
                    "priority_tier": provider['priority_tier'],
                    "cost_per_1k_tokens": provider['cost_per_1k_tokens'],
                    "api_endpoint": provider.get('api_endpoint'),
                    "model": provider.get('model'),
                    "capabilities": provider.get('capabilities', []),
                    "integration_status": "active" if env_var_exists else "pending",
                    "source": "discovered" if provider['priority_tier'] == "discovered" else "existing"
                }
                
                # Add discovery-specific fields
                if provider['priority_tier'] == "discovered":
                    summary_item.update({
                        "discovery_source": provider.get('discovery_source'),
                        "cost_savings_vs_baseline": provider.get('cost_savings_vs_baseline'),
                        "recommended_for": provider.get('recommended_for'),
                        "integration_difficulty": provider.get('integration_difficulty'),
                        "railway_setup_instructions": provider.get('railway_setup_instructions')
                    })
                
                provider_summary.append(summary_item)
            
            # Sort by priority: primary -> discovered -> secondary -> specialized -> expensive
            tier_order = {"primary": 1, "discovered": 2, "secondary": 3, "specialized": 4, "expensive": 5}
            provider_summary.sort(key=lambda x: (tier_order.get(x['priority_tier'], 6), x['cost_per_1k_tokens']))
            
            return {
                "providers": provider_summary,
                "summary": env_check,
                "cost_analysis": {
                    "cheapest_configured": min([p['cost_per_1k_tokens'] for p in provider_summary if p['env_var_configured']], default=0),
                    "cheapest_available": min([p['cost_per_1k_tokens'] for p in provider_summary], default=0),
                    "primary_tier_configured": env_check["by_tier"]["primary"]["configured"],
                    "discovered_ready_to_integrate": env_check["by_tier"]["discovered"]["total"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting provider summary: {e}")
            raise
    
    async def generate_railway_setup_instructions(self, provider_id: str) -> Dict[str, Any]:
        """Generate step-by-step Railway setup instructions for a provider"""
        try:
            all_providers = self.existing_providers + self.discovered_providers
            provider = next((p for p in all_providers if p['id'] == provider_id), None)
            
            if not provider:
                raise ValueError("Provider not found")
            
            instructions = {
                "provider_name": provider['provider_name'],
                "env_var_name": provider['env_var_name'],
                "railway_steps": provider.get('railway_setup_instructions', [
                    "1. Go to Railway Dashboard (railway.app)",
                    "2. Select your CampaignForge project",
                    "3. Click on 'Variables' tab",
                    f"4. Click 'Add Variable'",
                    f"5. Name: {provider['env_var_name']}",
                    f"6. Value: Your API key from {provider['provider_name']}",
                    "7. Click 'Add' to save",
                    "8. Redeploy your service"
                ]),
                "api_endpoint": provider.get('api_endpoint'),
                "estimated_time": "3-5 minutes",
                "verification": f"System will auto-detect when {provider['env_var_name']} is available",
                "optional_variables": [
                    f"{provider['env_var_name'].replace('_API_KEY', '_BASE_URL')}",
                    f"{provider['env_var_name'].replace('_API_KEY', '_MODEL_NAME')}"
                ],
                "cost_savings": provider.get('cost_savings_vs_baseline'),
                "integration_difficulty": provider.get('integration_difficulty', 'medium')
            }
            
            return instructions
            
        except Exception as e:
            logger.error(f"Error generating setup instructions: {e}")
            raise

# Create service instance
railway_env_service = RailwayEnvironmentService()

# ============================================================================
# 🛤️ RAILWAY ENVIRONMENT VARIABLE MANAGEMENT ROUTES
# ============================================================================

@router.get("/railway/env-status")
async def check_railway_environment_status(
    admin_user: User = Depends(require_admin)
):
    """Check status of all Railway environment variables for AI providers"""
    try:
        results = await railway_env_service.check_railway_env_vars()
        return {
            "success": True,
            "data": results,
            "message": f"Checked {results['total_providers']} AI providers",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Railway env status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/railway/providers-summary")
async def get_ai_providers_summary(
    admin_user: User = Depends(require_admin)
):
    """Get comprehensive summary of all AI providers with Railway integration status"""
    try:
        summary = await railway_env_service.get_provider_summary()
        return {
            "success": True,
            "data": summary,
            "message": f"Retrieved {len(summary['providers'])} AI providers",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"AI providers summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/railway/setup-instructions/{provider_id}")
async def get_railway_setup_instructions(
    provider_id: str,
    admin_user: User = Depends(require_admin)
):
    """Get Railway setup instructions for a specific AI provider"""
    try:
        instructions = await railway_env_service.generate_railway_setup_instructions(provider_id)
        return {
            "success": True,
            "data": instructions,
            "message": f"Generated Railway setup instructions for {instructions['provider_name']}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Setup instructions generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 🎯 EXISTING CRUD MIGRATED ROUTES (COMPLETE)
# ============================================================================

@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Get admin dashboard statistics - CRUD VERSION"""
    try:
        # ✅ CRUD MIGRATION: Use CRUD count methods instead of raw SQL
        total_users = await user_crud.count(db=db)
        total_companies = await company_crud.count(db=db)
        total_campaigns = await campaign_crud.count(db=db)
        
        # Active users using CRUD
        active_users = await user_crud.count(
            db=db, 
            filters={"is_active": True}
        )
        
        # Get new users in last month (simplified using CRUD)
        all_users = await user_crud.get_multi(
            db=db,
            limit=10000,  # Get all users for date filtering
            order_by="created_at",
            order_desc=True
        )
        
        # Calculate date-based metrics
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        one_month_ago = now - timedelta(days=30)
        one_week_ago = now - timedelta(days=7)
        
        new_users_month = len([
            user for user in all_users 
            if user.created_at and user.created_at >= one_month_ago
        ])
        
        new_users_week = len([
            user for user in all_users 
            if user.created_at and user.created_at >= one_week_ago
        ])
        
        # Get subscription breakdown using CRUD
        all_companies = await company_crud.get_multi(
            db=db,
            limit=10000  # Get all companies for subscription analysis
        )
        
        subscription_breakdown = {}
        all_tiers = ["free", "starter", "professional", "agency", "enterprise"]
        
        # Initialize all tiers to 0
        for tier in all_tiers:
            subscription_breakdown[tier] = 0
        
        # Count by subscription tier
        for company in all_companies:
            tier = company.subscription_tier
            if tier in subscription_breakdown:
                subscription_breakdown[tier] += 1
            else:
                subscription_breakdown[tier] = 1
        
        # Calculate MRR (simplified for now)
        monthly_recurring_revenue = 0.0
        
        print(f"✅ CRUD ADMIN STATS: Users={total_users}, Companies={total_companies}, Campaigns={total_campaigns}")
        
        return AdminStatsResponse(
            total_users=total_users,
            total_companies=total_companies,
            total_campaigns_created=total_campaigns,
            active_users=active_users,
            new_users_month=new_users_month,
            new_users_week=new_users_week,
            subscription_breakdown=subscription_breakdown,
            monthly_recurring_revenue=monthly_recurring_revenue
        )
        
    except Exception as e:
        print(f"❌ Error in CRUD admin stats: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting admin statistics: {str(e)}"
        )

@router.get("/users", response_model=UserListResponse)
async def get_all_users(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    subscription_tier: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None)
):
    """Get paginated list of all users with filtering - CRUD VERSION"""
    try:
        # ✅ CRUD MIGRATION: Build filters for CRUD operations
        filters = {}
        
        # Apply basic filters through CRUD
        if is_active is not None:
            filters["is_active"] = is_active
        
        # Get users using CRUD
        skip = (page - 1) * limit
        users = await user_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit * 2,  # Get more for filtering
            filters=filters,
            order_by="created_at",
            order_desc=True
        )
        
        # Get companies for lookup
        all_companies = await company_crud.get_multi(
            db=db,
            limit=10000  # Get all companies for user enrichment
        )
        company_lookup = {str(company.id): company for company in all_companies}
        
        # Apply additional filters that require company data
        filtered_users = []
        for user in users:
            company = company_lookup.get(str(user.company_id))
            if not company:
                continue
            
            # Apply search filter
            if search:
                search_lower = search.lower()
                name_match = user.full_name and search_lower in user.full_name.lower()
                email_match = user.email and search_lower in user.email.lower()
                company_match = company.company_name and search_lower in company.company_name.lower()
                
                if not (name_match or email_match or company_match):
                    continue
            
            # Apply subscription tier filter
            if subscription_tier and company.subscription_tier != subscription_tier:
                continue
            
            filtered_users.append((user, company))
        
        # Apply pagination to filtered results
        paginated_users = filtered_users[skip:skip + limit]
        
        # Get total count for pagination (simplified)
        total = len(filtered_users)
        
        # Convert to response format
        user_list = []
        for user, company in paginated_users:
            user_list.append(AdminUserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                company_id=user.company_id,
                company_name=company.company_name,
                subscription_tier=company.subscription_tier,
                monthly_credits_used=company.monthly_credits_used or 0,
                monthly_credits_limit=company.monthly_credits_limit or 0
            ))
        
        print(f"✅ CRUD USER MANAGEMENT: Found {total} users, returning {len(user_list)} for page {page}")
        
        return UserListResponse(
            users=user_list,
            total=total,
            page=page,
            limit=limit,
            pages=((total - 1) // limit + 1) if total > 0 else 0
        )
        
    except Exception as e:
        print(f"❌ Error in CRUD get_all_users: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting users: {str(e)}"
        )

@router.get("/companies", response_model=CompanyListResponse)
async def get_all_companies(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    subscription_tier: Optional[str] = Query(None)
):
    """Get paginated list of all companies - CRUD VERSION"""
    try:
        # ✅ CRUD MIGRATION: Use CRUD operations instead of raw SQL
        filters = {}
        
        # Apply subscription tier filter through CRUD
        if subscription_tier:
            filters["subscription_tier"] = subscription_tier
        
        # Get companies using CRUD
        skip = (page - 1) * limit
        companies = await company_crud.get_multi(
            db=db,
            skip=0,  # Get all for filtering
            limit=10000,
            filters=filters,
            order_by="created_at",
            order_desc=True
        )
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            filtered_companies = []
            for company in companies:
                name_match = company.company_name and search_lower in company.company_name.lower()
                industry_match = company.industry and search_lower in company.industry.lower()
                
                if name_match or industry_match:
                    filtered_companies.append(company)
            companies = filtered_companies
        
        # Apply pagination
        total = len(companies)
        paginated_companies = companies[skip:skip + limit]
        
        # Convert to response format with enriched data
        company_list = []
        for company in paginated_companies:
            # Get user count for this company using CRUD
            user_count = await user_crud.count(
                db=db,
                filters={"company_id": company.id}
            )
            
            # Get campaign count for this company using CRUD
            campaign_count = await campaign_crud.count(
                db=db,
                filters={"company_id": company.id}
            )
            
            company_list.append(AdminCompanyResponse(
                id=company.id,
                company_name=company.company_name,
                company_slug=company.company_slug,
                industry=company.industry or "",
                company_size=company.company_size,
                subscription_tier=company.subscription_tier,
                subscription_status=company.subscription_status,
                monthly_credits_used=company.monthly_credits_used or 0,
                monthly_credits_limit=company.monthly_credits_limit or 0,
                total_campaigns_created=company.total_campaigns_created or 0,
                created_at=company.created_at,
                user_count=user_count,
                campaign_count=campaign_count
            ))
        
        print(f"✅ CRUD COMPANY MANAGEMENT: Found {total} companies, returning {len(company_list)} for page {page}")
        
        return CompanyListResponse(
            companies=company_list,
            total=total,
            page=page,
            limit=limit,
            pages=((total - 1) // limit + 1) if total > 0 else 0
        )
        
    except Exception as e:
        print(f"❌ Error in CRUD get_all_companies: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting companies: {str(e)}"
        )

@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user_details(
    user_id: str,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Get detailed user information - CRUD VERSION"""
    try:
        # ✅ CRUD MIGRATION: Use CRUD get method
        user = await user_crud.get(db=db, id=user_id)
        
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get company using CRUD
        company = await company_crud.get(db=db, id=user.company_id)
        
        if not company:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User's company not found"
            )
        
        return AdminUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            company_id=user.company_id,
            company_name=company.company_name,
            subscription_tier=company.subscription_tier,
            monthly_credits_used=company.monthly_credits_used,
            monthly_credits_limit=company.monthly_credits_limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in CRUD get_user_details: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user details: {str(e)}"
        )

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_update: UserUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Update user details - CRUD VERSION"""
    try:
        # ✅ CRUD MIGRATION: Use CRUD get and update methods
        user = await user_crud.get(db=db, id=user_id)
        
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Build update data
        update_data = {}
        if user_update.full_name is not None:
            update_data["full_name"] = user_update.full_name
        if user_update.role is not None:
            update_data["role"] = user_update.role
        if user_update.is_active is not None:
            update_data["is_active"] = user_update.is_active
        if user_update.is_verified is not None:
            update_data["is_verified"] = user_update.is_verified
        
        # Update using CRUD
        updated_user = await user_crud.update(
            db=db,
            db_obj=user,
            obj_in=update_data
        )
        
        print(f"✅ CRUD USER UPDATE: Updated user {user_id}")
        
        return {"message": "User updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in CRUD update_user: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )

@router.put("/companies/{company_id}/subscription")
async def update_company_subscription(
    company_id: str,
    subscription_update: SubscriptionUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Update company subscription tier and limits - CRUD VERSION"""
    try:
        # ✅ CRUD MIGRATION: Use CRUD get and update methods
        company = await company_crud.get(db=db, id=company_id)
        
        if not company:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Build update data
        update_data = {}
        if subscription_update.subscription_tier is not None:
            update_data["subscription_tier"] = subscription_update.subscription_tier
        if subscription_update.monthly_credits_limit is not None:
            update_data["monthly_credits_limit"] = subscription_update.monthly_credits_limit
        if subscription_update.subscription_status is not None:
            if hasattr(company, 'subscription_status'):
                update_data["subscription_status"] = subscription_update.subscription_status
        
        # Reset monthly credits if requested
        if subscription_update.reset_monthly_credits:
            update_data["monthly_credits_used"] = 0
        
        # Update using CRUD
        updated_company = await company_crud.update(
            db=db,
            db_obj=company,
            obj_in=update_data
        )
        
        print(f"✅ CRUD SUBSCRIPTION UPDATE: Updated company {company_id}")
        
        return {"message": "Company subscription updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in CRUD update_company_subscription: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating company subscription: {str(e)}"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete user account - CRUD VERSION"""
    try:
        # ✅ CRUD MIGRATION: Use CRUD get method
        user = await user_crud.get(db=db, id=user_id)
        
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Don't allow deleting the last owner of a company
        if user.role == "owner":
            # Count owners in the same company using CRUD
            owner_count = await user_crud.count(
                db=db,
                filters={
                    "company_id": user.company_id,
                    "role": "owner"
                }
            )
            
            if owner_count <= 1:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete the last owner of a company"
                )
        
        # Delete using CRUD
        success = await user_crud.delete(db=db, id=user_id)
        
        if not success:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
        
        print(f"✅ CRUD USER DELETE: Deleted user {user_id}")
        
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in CRUD delete_user: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )

@router.post("/users/{user_id}/impersonate")
async def impersonate_user(
    user_id: str,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Generate impersonation token for user (admin feature) - CRUD VERSION"""
    try:
        # ✅ CRUD MIGRATION: Use CRUD get method
        user = await user_crud.get(db=db, id=user_id)
        
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get company using CRUD
        company = await company_crud.get(db=db, id=user.company_id)
        
        if not company:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User's company not found"
            )
        
        # Create impersonation token
        from src.auth.dependencies import create_access_token
        
        impersonation_token = create_access_token(data={
            "sub": str(user.id),
            "company_id": str(user.company_id),
            "role": user.role,
            "impersonated_by": str(admin_user.id)
        })
        
        print(f"✅ CRUD IMPERSONATION: Created token for {user.email}")
        
        return {
            "message": f"Impersonation token created for {user.email}",
            "access_token": impersonation_token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "company_name": company.company_name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in CRUD impersonate_user: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating impersonation token: {str(e)}"
        )

@router.get("/companies/{company_id}", response_model=AdminCompanyResponse)
async def get_company_details(
    company_id: str,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Get detailed company information - CRUD VERSION"""
    try:
        # ✅ CRUD MIGRATION: Use CRUD get method
        company = await company_crud.get(db=db, id=company_id)
        
        if not company:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Get user count using CRUD
        user_count = await user_crud.count(
            db=db,
            filters={"company_id": company.id}
        )
        
        # Get campaign count using CRUD
        campaign_count = await campaign_crud.count(
            db=db,
            filters={"company_id": company.id}
        )
        
        return AdminCompanyResponse(
            id=company.id,
            company_name=company.company_name,
            company_slug=company.company_slug,
            industry=company.industry or "",
            company_size=company.company_size,
            subscription_tier=company.subscription_tier,
            subscription_status=company.subscription_status,
            monthly_credits_used=company.monthly_credits_used,
            monthly_credits_limit=company.monthly_credits_limit,
            total_campaigns_created=company.total_campaigns_created,
            created_at=company.created_at,
            user_count=user_count,
            campaign_count=campaign_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in CRUD get_company_details: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting company details: {str(e)}"
        )

@router.put("/companies/{company_id}")
async def update_company_details(
    company_id: str,
    company_update: CompanyUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Update company details - CRUD VERSION"""
    try:
        # ✅ CRUD MIGRATION: Use CRUD get and update methods
        company = await company_crud.get(db=db, id=company_id)
        
        if not company:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Build update data
        update_data = {}
        if company_update.company_name is not None:
            update_data["company_name"] = company_update.company_name
        if company_update.industry is not None:
            update_data["industry"] = company_update.industry
        if company_update.company_size is not None:
            update_data["company_size"] = company_update.company_size
        if company_update.website_url is not None:
            if hasattr(company, 'website_url'):
                update_data["website_url"] = company_update.website_url
        
        # Update using CRUD
        updated_company = await company_crud.update(
            db=db,
            db_obj=company,
            obj_in=update_data
        )
        
        print(f"✅ CRUD COMPANY UPDATE: Updated company {company_id}")
        
        return {"message": "Company details updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in CRUD update_company_details: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating company details: {str(e)}"
        )

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_data: dict,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Update user role (only main admin can do this) - CRUD VERSION"""
    try:
        new_role = role_data.get("new_role")
        
        # Only allow main admin to change roles
        if admin_user.role != "admin":
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Only main admin can change user roles"
            )
        
        # Validate role
        valid_roles = ["admin", "owner", "member", "viewer"]
        if new_role not in valid_roles:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {valid_roles}"
            )
        
        # ✅ CRUD MIGRATION: Use CRUD get method
        user = await user_crud.get(db=db, id=user_id)
        
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent removing admin role from last admin
        if user.role == "admin" and new_role != "admin":
            # Count total admins using CRUD
            admin_count = await user_crud.count(
                db=db,
                filters={"role": "admin"}
            )
            
            if admin_count <= 1:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove admin role from the last admin user"
                )
        
        # Update role using CRUD
        old_role = user.role
        updated_user = await user_crud.update(
            db=db,
            db_obj=user,
            obj_in={"role": new_role}
        )
        
        print(f"✅ CRUD ROLE UPDATE: Changed {user.email} from {old_role} to {new_role}")
        
        return {
            "message": f"User role updated from {old_role} to {new_role}",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "old_role": old_role,
                "new_role": new_role
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in CRUD update_user_role: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user role: {str(e)}"
        )

@router.get("/roles")
async def get_available_roles(
    admin_user: User = Depends(require_admin)
):
    """Get list of available user roles"""
    roles = [
        {
            "value": "admin",
            "label": "Admin",
            "description": "Full platform access, can manage all users and companies"
        },
        {
            "value": "owner", 
            "label": "Company Owner",
            "description": "Company owner with full access to their company"
        },
        {
            "value": "member",
            "label": "Member", 
            "description": "Regular user with standard access"
        },
        {
            "value": "viewer",
            "label": "Viewer",
            "description": "Read-only access to company resources"
        }
    ]
    
    return {"roles": roles}

@router.get("/system-status-complete")
async def get_complete_system_status(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Get complete system status including CRUD operations and Railway integration"""
    try:
        status = {
            "system_status": "operational",
            "timestamp": datetime.now().isoformat(),
            "checked_by": admin_user.email,
            "components": {}
        }
        
        # Test database/CRUD operations
        try:
            user_count = await user_crud.count(db=db)
            company_count = await company_crud.count(db=db)
            campaign_count = await campaign_crud.count(db=db)
            
            status["components"]["database"] = {
                "status": "operational",
                "user_count": user_count,
                "company_count": company_count,
                "campaign_count": campaign_count,
                "crud_operations": "working"
            }
        except Exception as e:
            status["components"]["database"] = {
                "status": "error",
                "error": str(e)
            }
            status["system_status"] = "degraded"
        
        # Test Railway environment service
        try:
            railway_status = await railway_env_service.check_railway_env_vars()
            
            status["components"]["railway_integration"] = {
                "status": "operational",
                "total_providers": railway_status["total_providers"],
                "configured_providers": railway_status["configured_count"],
                "configuration_health": "excellent" if railway_status["configured_count"] >= railway_status["total_providers"] * 0.8 else "needs_attention"
            }
        except Exception as e:
            status["components"]["railway_integration"] = {
                "status": "error", 
                "error": str(e)
            }
            status["system_status"] = "degraded"
        
        # Overall system health
        all_components_ok = all(
            comp.get("status") == "operational" 
            for comp in status["components"].values()
        )
        
        if not all_components_ok:
            status["system_status"] = "degraded"
        
        status["summary"] = {
            "overall_health": status["system_status"],
            "components_operational": len([c for c in status["components"].values() if c.get("status") == "operational"]),
            "total_components": len(status["components"]),
            "admin_routes_status": "fully_migrated_with_railway_integration",
            "production_ready": all_components_ok
        }
        
        return {
            "success": True,
            "data": status,
            "message": f"Complete system status: {status['system_status']}"
        }
        
    except Exception as e:
        logger.error(f"Complete system status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))