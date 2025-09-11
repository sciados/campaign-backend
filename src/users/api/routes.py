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

from src.core.factories.service_factory import ServiceFactory
from src.users.services.auth_service import AuthService
from src.users.services.user_service import UserService
from src.core.database.connection import get_db
from src.users.models.user import User, Company
from src.campaigns.models.campaign import Campaign
from src.core.database.models import IntelligenceCore, Waitlist

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
    """Get active AI providers for admin dashboard"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # Get analysis method statistics from intelligence data
            method_stats = db.query(
                IntelligenceCore.analysis_method,
                func.count(IntelligenceCore.id).label('count'),
                func.avg(IntelligenceCore.confidence_score).label('avg_confidence')
            ).group_by(IntelligenceCore.analysis_method).all()
            
            # Map analysis methods to providers
            provider_map = {
                "fast": {"name": "OpenAI GPT-3.5", "cost": 30},
                "deep": {"name": "OpenAI GPT-4", "cost": 50}, 
                "enhanced": {"name": "Claude-3", "cost": 45}
            }
            
            providers = []
            for method, count, avg_conf in method_stats:
                provider_info = provider_map.get(method, {"name": method.title(), "cost": 35})
                providers.append({
                    "id": method,
                    "name": provider_info["name"],
                    "status": "active",
                    "cost": provider_info["cost"],
                    "usage_count": count,
                    "avg_confidence": round(float(avg_conf or 0), 2)
                })
            
            # Sort by usage count and limit if requested
            providers.sort(key=lambda x: x['usage_count'], reverse=True)
            if top_3_only:
                providers = providers[:3]
            
            return {"providers": providers}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/ai-discovery/discovered-suggestions")
async def get_discovered_suggestions(token: str = Depends(security), db: Session = Depends(get_db)):
    """Get AI discovery suggestions for admin dashboard"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # Get recent intelligence with low confidence scores as suggestions for improvement
            low_confidence_intel = db.query(IntelligenceCore).filter(
                IntelligenceCore.confidence_score < 0.7
            ).order_by(desc(IntelligenceCore.created_at)).limit(10).all()
            
            suggestions = []
            for intel in low_confidence_intel:
                suggestions.append({
                    "id": intel.id,
                    "product_name": intel.product_name,
                    "confidence_score": intel.confidence_score,
                    "analysis_method": intel.analysis_method,
                    "suggestion": f"Consider re-analyzing {intel.product_name} with enhanced method for better confidence",
                    "created_at": intel.created_at.isoformat() if intel.created_at else None
                })
            
            return {"suggestions": suggestions}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/ai-discovery/dashboard")
async def get_ai_discovery_dashboard(token: str = Depends(security), db: Session = Depends(get_db)):
    """Get AI discovery dashboard data"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # Get intelligence statistics
            total_intelligence = db.query(IntelligenceCore).count()
            avg_confidence = db.query(func.avg(IntelligenceCore.confidence_score)).scalar() or 0
            
            # Get recent activity (last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            recent_intelligence = db.query(IntelligenceCore).filter(
                IntelligenceCore.created_at >= week_ago
            ).count()
            
            # Calculate health score based on various metrics
            health_score = min(100, (avg_confidence * 100) + (recent_intelligence * 2))
            
            return {
                "dashboard": {
                    "healthy": health_score > 70,
                    "health_score": round(health_score, 1),
                    "total_intelligence": total_intelligence,
                    "avg_confidence": round(avg_confidence, 2),
                    "recent_activity": recent_intelligence
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/ai-discovery/category-rankings")
async def get_category_rankings(token: str = Depends(security), db: Session = Depends(get_db)):
    """Get AI category rankings"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # Get top products by confidence score
            top_products = db.query(
                IntelligenceCore.product_name,
                func.avg(IntelligenceCore.confidence_score).label('avg_confidence'),
                func.count(IntelligenceCore.id).label('analysis_count')
            ).group_by(IntelligenceCore.product_name)\
             .order_by(desc('avg_confidence'))\
             .limit(10).all()
            
            rankings = []
            for rank, (product, avg_conf, count) in enumerate(top_products, 1):
                rankings.append({
                    "rank": rank,
                    "product_name": product,
                    "avg_confidence": round(float(avg_conf), 2),
                    "analysis_count": count,
                    "category": "Intelligence Analysis"  # Could be enhanced with real categories
                })
            
            return {"rankings": rankings}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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