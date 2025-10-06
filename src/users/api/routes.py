# ============================================================================
# API ROUTE UPDATES FOR SERVICE INTEGRATION - COMPLETE VERSION
# ============================================================================
# src/users/api/routes.py (Enhanced for Session 5 + Registration Fixes)

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
import logging

from src.core.factories.service_factory import ServiceFactory
from src.users.services.auth_service import AuthService
from src.users.services.user_service import UserService
from src.core.database.session import get_db
from src.users.models.user import User, Company
from src.campaigns.models.campaign import Campaign
from src.core.database.models import IntelligenceCore, Waitlist

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# ============================================================================
# FIXED: Enhanced Registration with Proper User Type Mapping
# ============================================================================

@router.post("/api/auth/register")
async def register_user(request: Dict[str, Any]):
    """Enhanced user registration with invite token support and proper user type mapping"""
    try:
        email = request.get("email")
        password = request.get("password")
        full_name = request.get("full_name")
        company_name = request.get("company_name", "Default Company")
        user_type = request.get("user_type")
        invite_token = request.get("invite_token")

        if not all([email, password, full_name]):
            raise HTTPException(
                status_code=400,
                detail="email, password, and full_name are required"
            )

        # Enhanced user type mapping - handles both frontend formats and case variations
        backend_user_type = None
        if user_type:
            user_type_mapping = {
                # Lowercase frontend formats
                "affiliate_marketer": "AFFILIATE_MARKETER",
                "affiliate": "AFFILIATE_MARKETER",
                "content_creator": "CONTENT_CREATOR",
                "creator": "CONTENT_CREATOR",
                "product_creator": "PRODUCT_CREATOR",
                "business_owner": "BUSINESS_OWNER",
                "business": "BUSINESS_OWNER",
                # Uppercase formats (defensive programming)
                "AFFILIATE_MARKETER": "AFFILIATE_MARKETER",
                "CONTENT_CREATOR": "CONTENT_CREATOR",
                "PRODUCT_CREATOR": "PRODUCT_CREATOR",
                "BUSINESS_OWNER": "BUSINESS_OWNER",
            }
            # Try exact match first, then lowercase match, then uppercase fallback
            backend_user_type = user_type_mapping.get(
                user_type, 
                user_type_mapping.get(user_type.lower(), user_type.upper())
            )
            logger.info(f"Mapped user_type '{user_type}' to backend format: '{backend_user_type}'")

        # Handle invite token validation for product creators
        if invite_token:
            from src.intelligence.services.product_creator_invite_service import ProductCreatorInviteService
            from src.core.database import get_async_db

            db_gen = get_async_db()
            session = await db_gen.__anext__()

            try:
                invite_service = ProductCreatorInviteService()
                validation_result = await invite_service.validate_invite_token(
                    invite_token=invite_token,
                    session=session
                )

                if not validation_result["valid"]:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Invalid invite token: {validation_result.get('reason', 'Unknown error')}"
                    )

                # Override user type for product creator invites
                backend_user_type = "PRODUCT_CREATOR"
                logger.info(f"Invite token validated - user_type set to PRODUCT_CREATOR")

                # Use company name from invite if available
                invite_data = validation_result.get("invite_data", {})
                if invite_data.get("company_name"):
                    company_name = invite_data["company_name"]
                    logger.info(f"Using company name from invite: {company_name}")

            finally:
                await session.close()

        # Register user with proper user type
        async with ServiceFactory.create_transactional_service(AuthService) as auth_service:
            result = await auth_service.register(
                email=email,
                password=password,
                full_name=full_name,
                company_name=company_name,
                user_type=backend_user_type,
                invite_token=invite_token
            )

        logger.info(f"User registered successfully: {email} with user_type: {backend_user_type}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FIXED: Enhanced Profile Endpoint with Clean User Type Mapping
# ============================================================================

@router.get("/api/auth/profile")
async def get_user_profile(token: str = Depends(security)):
    """Get user profile with enhanced service management and clean user type mapping"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
            # Map backend user_type to frontend format consistently
            frontend_user_type = None
            if user.user_type:
                backend_to_frontend = {
                    "AFFILIATE_MARKETER": "affiliate_marketer",
                    "CONTENT_CREATOR": "content_creator",
                    "PRODUCT_CREATOR": "product_creator",
                    "BUSINESS_OWNER": "business_owner",
                }
                frontend_user_type = backend_to_frontend.get(
                    user.user_type, 
                    user.user_type.lower()
                )
                logger.info(f"Mapped user_type '{user.user_type}' to frontend format: '{frontend_user_type}'")

            return {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role or "user",
                "user_type": frontend_user_type,
                "is_active": user.is_active,
                "onboarding_completed": user.onboarding_completed,
                "company": {
                    "id": str(user.company.id),
                    "name": user.company.company_name,
                    "subscription_tier": user.company.subscription_tier
                } if user.company else None
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}")
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

# ============================================================================
# User Type Selection & Onboarding
# ============================================================================

@router.post("/api/user-types/select")
async def select_user_type(request: Dict[str, Any], token: str = Depends(security)):
    """Set user type during onboarding"""
    try:
        user_type = request.get("user_type")
        goals = request.get("goals", [])
        experience_level = request.get("experience_level", "beginner")
        
        if not user_type:
            raise HTTPException(status_code=400, detail="user_type is required")
        
        # Map frontend user types to backend enums
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
        
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
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
                        "user_type": user_type,
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
        user_type = request.get("user_type")
        goals = request.get("goals", [])
        experience_level = request.get("experience_level", "beginner")
        
        if not user_type:
            raise HTTPException(status_code=400, detail="user_type is required")
        
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
        
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
            async with ServiceFactory.create_service(UserService) as user_service:
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

# ============================================================================
# NEW: Dashboard-Specific Endpoints (Previously Missing)
# ============================================================================

@router.get("/api/users/company/stats")
async def get_company_stats(token: str = Depends(security)):
    """Get company statistics for business dashboard"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
            if not user.company:
                raise HTTPException(status_code=404, detail="No company associated with user")
            
            # Return company metrics (can be enhanced with real data later)
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
            
            if not user or not user.company:
                raise HTTPException(status_code=404, detail="Company not found")
            
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
                raise HTTPException(status_code=401, detail="User not found")
            
            # Return social profile data (can integrate real platforms later)
            return {
                "social_profiles": [
                    {
                        "platform": "Instagram",
                        "username": "@creator",
                        "followers": 12450,
                        "engagement_rate": 4.2,
                        "last_updated": "2024-01-15T10:30:00Z",
                        "status": "connected"
                    },
                    {
                        "platform": "YouTube",
                        "username": "Creator Channel",
                        "followers": 8960,
                        "engagement_rate": 7.1,
                        "last_updated": "2024-01-15T09:15:00Z",
                        "status": "connected"
                    }
                ],
                "total_platforms": 2,
                "connected_platforms": 2,
                "total_followers": 21410,
                "avg_engagement_rate": 5.65
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ADMIN API ENDPOINTS (Existing - Keep These)
# ============================================================================

@router.get("/api/admin/stats")
async def get_admin_stats(token: str = Depends(security), db: Session = Depends(get_db)):
    """Get admin dashboard statistics"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user or user.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            total_users = db.query(User).count()
            total_companies = db.query(Company).count()
            total_campaigns = db.query(Campaign).count()
            
            subscription_stats = db.query(
                Company.subscription_tier,
                func.count(Company.id).label('count')
            ).group_by(Company.subscription_tier).all()
            
            subscription_breakdown = {}
            total_mrr = 0
            
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

# ... (Keep all your existing admin endpoints: get_admin_users, get_admin_companies, etc.)
# ... (Keep all your waitlist endpoints)
# ... (Keep all your demo campaign endpoints)

# NOTE: The rest of your routes.py file remains unchanged. 
# Only the sections above were modified for the fixes.