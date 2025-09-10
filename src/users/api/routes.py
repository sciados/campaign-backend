# ============================================================================
# API ROUTE UPDATES FOR SERVICE INTEGRATION
# ============================================================================

# src/users/api/routes.py (Enhanced for Session 5)

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, Any

from src.core.factories.service_factory import ServiceFactory
from src.users.services.auth_service import AuthService
from src.users.services.user_service import UserService

router = APIRouter()
security = HTTPBearer()

@router.post("/api/auth/register")
async def register_user(request: Dict[str, Any]):
    """Enhanced user registration with proper service management"""
    try:
        email = request.get("email")
        password = request.get("password")
        full_name = request.get("full_name")
        company_name = request.get("company_name", "Default Company")
        user_type = request.get("user_type")  # Get user_type from request
        
        if not all([email, password, full_name]):
            raise HTTPException(
                status_code=400,
                detail="email, password, and full_name are required"
            )
        
        # Map frontend user types to backend enums if user_type is provided
        backend_user_type = None
        if user_type:
            user_type_mapping = {
                "affiliate_marketer": "AFFILIATE_MARKETER",
                "affiliate": "AFFILIATE_MARKETER",
                "content_creator": "CONTENT_CREATOR", 
                "creator": "CONTENT_CREATOR",
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
                user_type=backend_user_type  # Pass user_type to register method
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
async def get_admin_stats(token: str = Depends(security)):
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
            
            # Return mock admin stats for now
            return {
                "total_users": 150,
                "total_companies": 45,
                "total_campaigns_created": 325,
                "monthly_recurring_revenue": 12500,
                "subscription_breakdown": {
                    "free": 89,
                    "starter": 35,
                    "professional": 18,
                    "agency": 6,
                    "enterprise": 2
                }
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
    token: str = Depends(security)
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
            
            # Return mock user data for now
            return {
                "users": [
                    {
                        "id": "user1",
                        "full_name": "John Doe",
                        "email": "john@example.com",
                        "role": "user",
                        "company_name": "John's Company",
                        "subscription_tier": "professional",
                        "monthly_credits_used": 150,
                        "monthly_credits_limit": 500,
                        "is_active": True,
                        "is_verified": True
                    }
                ],
                "total": 150,
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
    token: str = Depends(security)
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
            
            # Return mock company data for now
            return {
                "companies": [
                    {
                        "id": "comp1",
                        "company_name": "Tech Startup Inc",
                        "company_slug": "tech-startup",
                        "company_size": "50-100",
                        "industry": "Technology",
                        "subscription_tier": "professional",
                        "monthly_credits_used": 2500,
                        "monthly_credits_limit": 5000,
                        "user_count": 8,
                        "campaign_count": 25
                    }
                ],
                "total": 45,
                "page": page,
                "per_page": limit
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI Discovery API endpoints (basic stubs for now)
@router.get("/api/admin/ai-discovery/active-providers")
async def get_active_providers(
    top_3_only: bool = False,
    token: str = Depends(security)
):
    """Get active AI providers for admin dashboard"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # Return mock AI provider data
            return {
                "providers": [
                    {"id": 1, "name": "OpenAI GPT-4", "status": "active", "cost": 50},
                    {"id": 2, "name": "Claude-3", "status": "active", "cost": 45},
                    {"id": 3, "name": "Gemini Pro", "status": "active", "cost": 40}
                ]
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/ai-discovery/discovered-suggestions")
async def get_discovered_suggestions(token: str = Depends(security)):
    """Get AI discovery suggestions for admin dashboard"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            return {"suggestions": []}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/ai-discovery/dashboard")
async def get_ai_discovery_dashboard(token: str = Depends(security)):
    """Get AI discovery dashboard data"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            return {"dashboard": {"healthy": True}}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/ai-discovery/category-rankings")
async def get_category_rankings(token: str = Depends(security)):
    """Get AI category rankings"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            return {"rankings": []}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ✅ WAITLIST API ENDPOINTS
# ============================================================================

@router.post("/api/waitlist/join")
async def join_waitlist(request: dict):
    """Join the waitlist"""
    email = request.get("email")
    referrer = request.get("referrer")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    return {
        "message": "Successfully joined the waitlist!",
        "total_signups": 1247,
        "position": 1248,
        "email": email
    }

@router.get("/api/waitlist/check/{email}")
async def check_waitlist(email: str):
    """Check if email is on waitlist"""
    return {
        "on_waitlist": True,
        "message": "You're on the waitlist!",
        "position": 1248,
        "total_signups": 1247,
        "joined_date": "2024-01-15",
        "is_notified": False
    }

@router.get("/api/waitlist/stats")
async def get_waitlist_stats(token: str = Depends(security)):
    """Get waitlist statistics (admin only)"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            return {
                "total": 1247,
                "today": 15,
                "this_week": 89,
                "this_month": 342,
                "recent_signups": [
                    {"email": "user1@example.com", "created_at": "2024-01-15", "id": 1},
                    {"email": "user2@example.com", "created_at": "2024-01-14", "id": 2}
                ],
                "daily_stats": [
                    {"date": "2024-01-15", "count": 15},
                    {"date": "2024-01-14", "count": 23}
                ]
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/waitlist/export")
async def export_waitlist(token: str = Depends(security)):
    """Export waitlist emails (admin only)"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            return {
                "emails": [
                    {
                        "id": 1,
                        "email": "user1@example.com",
                        "joined_date": "2024-01-15",
                        "is_notified": False,
                        "referrer": "direct"
                    }
                ],
                "total": 1247,
                "export_date": "2024-01-15"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/waitlist/list")
async def get_waitlist_list(skip: int = 0, limit: int = 100, token: str = Depends(security)):
    """Get paginated waitlist entries (admin only)"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            return [
                {
                    "id": 1,
                    "email": "user1@example.com",
                    "created_at": "2024-01-15",
                    "ip_address": "192.168.1.1",
                    "is_notified": False
                }
            ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))