# =====================================
# File: src/api/routes/auth.py  
# =====================================

"""
Authentication routes that integrate with existing CampaignForge backend architecture
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import jwt
import logging

# Import existing infrastructure - FIXED IMPORTS
from src.core.database.connection import AsyncSessionLocal  # Direct import from connection
from src.core.crud.user_crud import user_crud
from src.core.middleware.auth_middleware import AuthMiddleware, security
from src.core.shared.responses import StandardResponse
from src.core.config.settings import settings
from src.core.database.connection import get_async_db

# Import schemas and models
from src.schemas.auth import (
    LoginRequest, 
    RegisterRequest, 
    LoginResponse, 
    DashboardRouteResponse,
    UserProfile,
    CompanyInfo
)
from src.models.user import User, Company

logger = logging.getLogger(__name__)

# Create router following your modular pattern
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# ============================================================================
# DATABASE DEPENDENCY - Compatible with your session manager
# ============================================================================

# async def get_async_db():
#    """FastAPI dependency to get async database session."""
#    async with AsyncSessionLocal() as session:
#        yield session

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/login", response_model=StandardResponse[LoginResponse])
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    User login endpoint - integrates with existing UserCRUD and models
    """
    try:
        logger.info(f"Login attempt for email: {request.email}")
        
        # Use existing user_crud to authenticate user
        user = await user_crud.authenticate_user(
            db=db, 
            email=request.email, 
            password=request.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create JWT token
        token_data = {"sub": str(user.id)}
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires
        token_data.update({"exp": expire})
        
        access_token = jwt.encode(
            token_data, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        # Prepare company data if available
        company_data = None
        if user.company:
            company_data = CompanyInfo(
                id=str(user.company.id),
                company_name=user.company.company_name,
                company_slug=user.company.company_slug,
                subscription_tier=user.company.subscription_tier,
                monthly_credits_used=user.company.monthly_credits_used or 0,
                monthly_credits_limit=user.company.monthly_credits_limit or 1000,
                company_size=user.company.company_size
            )
        
        # Prepare user profile data
        user_profile = UserProfile(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            user_type=user.user_type,
            is_active=user.is_active,
            is_verified=user.is_verified,
            company=company_data
        )
        
        response_data = LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=str(user.id),
            user=user_profile
        )
        
        logger.info(f"Login successful for user: {user.id}")
        
        return StandardResponse(
            success=True,
            data=response_data,
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/register", response_model=StandardResponse[dict])
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    User registration endpoint - integrates with existing UserCRUD and models
    """
    try:
        logger.info(f"Registration attempt for email: {request.email}")
        
        # Check if user already exists using existing CRUD
        existing_user = await user_crud.get_by_email(db=db, email=request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user using existing user_crud
        new_user = await user_crud.create_user(
            db=db,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            company_name=request.company_name
        )
        
        # Create access token for immediate login
        token_data = {"sub": str(new_user.id)}
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires
        token_data.update({"exp": expire})
        
        access_token = jwt.encode(
            token_data, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        logger.info(f"Registration successful for user: {new_user.id}")
        
        return StandardResponse(
            success=True,
            data={
                "message": "User registered successfully",
                "user_id": str(new_user.id),
                "company_id": str(new_user.company_id),
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            },
            message="Registration successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.get("/profile", response_model=StandardResponse[UserProfile])
async def get_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get current user profile - uses existing auth middleware
    """
    try:
        # Use existing auth middleware to get user ID
        user_id = AuthMiddleware.require_authentication(credentials)
        
        # Use existing user_crud to get user
        user = await user_crud.get_by_id(db=db, user_id=user_id, include_company=True)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prepare company data if available
        company_data = None
        if user.company:
            company_data = CompanyInfo(
                id=str(user.company.id),
                company_name=user.company.company_name,
                company_slug=user.company.company_slug,
                subscription_tier=user.company.subscription_tier,
                monthly_credits_used=user.company.monthly_credits_used or 0,
                monthly_credits_limit=user.company.monthly_credits_limit or 1000,
                company_size=user.company.company_size
            )
        
        # Prepare user profile data using Pydantic schema
        profile_data = UserProfile(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            user_type=user.user_type,
            is_active=user.is_active,
            is_verified=user.is_verified,
            company=company_data
        )
        
        return StandardResponse(
            success=True,
            data=profile_data,
            message="Profile retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving profile"
        )

@router.get("/dashboard-route", response_model=StandardResponse[DashboardRouteResponse])
async def get_dashboard_route(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get appropriate dashboard route for user - integrates with user types
    """
    try:
        # Use existing auth middleware
        user_id = AuthMiddleware.require_authentication(credentials)
        
        # Get user using existing CRUD
        user = await user_crud.get_by_id(db=db, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Determine dashboard route based on user role and type
        if user.role == "admin":
            route = "/admin/dashboard"
        elif not user.onboarding_completed:
            route = "/onboarding"
        elif not user.user_type:
            route = "/user-selection"
        elif user.user_type == "affiliate_marketer":
            route = "/dashboard/affiliate"
        elif user.user_type == "content_creator":
            route = "/dashboard/creator"
        elif user.user_type == "business_owner":
            route = "/dashboard/business"
        else:
            route = "/dashboard"  # Default dashboard
        
        response_data = DashboardRouteResponse(route=route)
        
        return StandardResponse(
            success=True,
            data=response_data,
            message="Dashboard route determined"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard route error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error determining dashboard route"
        )

@router.post("/logout", response_model=StandardResponse[dict])
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    User logout endpoint - JWT tokens are stateless, so this is mainly for logging
    """
    try:
        # Use existing auth middleware to validate token
        user_id = AuthMiddleware.require_authentication(credentials)
        
        logger.info(f"User {user_id} logged out")
        
        return StandardResponse(
            success=True,
            data={"message": "Successfully logged out"},
            message="Logout successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )

@router.get("/me", response_model=StandardResponse[dict])
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get current user information including usage stats
    """
    try:
        user_id = AuthMiddleware.require_authentication(credentials)
        
        user = await user_crud.get_by_id(db=db, user_id=user_id, include_company=True)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get usage summary from user model
        usage_summary = user.get_usage_summary()
        
        # Prepare detailed user info
        user_info = {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "user_type": user.user_type,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "onboarding_completed": user.onboarding_completed,
            "onboarding_step": user.onboarding_step,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "company": {
                "id": str(user.company.id),
                "company_name": user.company.company_name,
                "subscription_tier": user.company.subscription_tier,
                "monthly_credits_used": user.company.monthly_credits_used or 0,
                "monthly_credits_limit": user.company.monthly_credits_limit or 1000
            } if user.company else None,
            "usage": usage_summary
        }
        
        return StandardResponse(
            success=True,
            data=user_info,
            message="User information retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving user information"
        )

# ============================================================================
# EXPORT ROUTER FOR MODULAR INTEGRATION
# ============================================================================

def get_auth_router() -> APIRouter:
    """Get the authentication router for integration with main app"""
    return router

__all__ = ["router", "get_auth_router"]