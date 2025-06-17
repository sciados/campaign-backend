"""
Authentication routes - Clean best practice implementation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import selectinload  # Add this line
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
import re

from src.core.database import get_db
from src.core.security import verify_password, get_password_hash, create_access_token
from src.auth.schemas import UserRegister, UserLogin, UserResponse, AuthResponse, CompanyResponse
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.company import Company, CompanyMembership, CompanySubscriptionTier, MembershipRole

router = APIRouter(prefix="/api/auth", tags=["authentication"])

def create_company_slug(company_name: str) -> str:
    """Create URL-friendly slug from company name"""
    slug = re.sub(r'[^a-z0-9]+', '-', company_name.lower())
    return slug.strip('-')[:50]

async def ensure_unique_company_slug(base_slug: str, db: AsyncSession) -> str:
    """Ensure company slug is unique by adding numbers if needed"""
    slug = base_slug
    counter = 1
    
    while True:
        result = await db.execute(select(Company).where(Company.company_slug == slug))
        if not result.scalar_one_or_none():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1

@router.post("/register", response_model=AuthResponse)
async def register_user_with_company(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register new user and create their company"""
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create unique company slug
        base_slug = create_company_slug(user_data.company_name)
        unique_slug = await ensure_unique_company_slug(base_slug, db)
        
        # Create company
        company = Company(
            id=uuid4(),
            company_name=user_data.company_name,
            company_slug=unique_slug,
            industry=user_data.industry,
            company_size=user_data.company_size,
            website_url=user_data.website_url,
            subscription_tier=CompanySubscriptionTier.FREE.value,
            billing_email=user_data.email,
            monthly_credits_limit=1000,
            monthly_credits_used=0
        )
        
        db.add(company)
        await db.flush()
        
        # Create user
        user = User(
            id=uuid4(),
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            company_id=company.id,
            role=MembershipRole.OWNER.value,
            is_active=True,
            is_verified=False
        )
        
        db.add(user)
        await db.flush()
        
        # Create company membership
        membership = CompanyMembership(
            id=uuid4(),
            user_id=user.id,
            company_id=company.id,
            role=MembershipRole.OWNER.value,
            status="active"
        )
        
        db.add(membership)
        await db.commit()
        
        # Refresh to get complete data
        await db.refresh(user)
        await db.refresh(company)
        
        # Create access token
        access_token = create_access_token(data={
            "sub": str(user.id),
            "company_id": str(company.id),
            "role": user.role
        })
        
        # Build response
        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                company=CompanyResponse(
                    id=company.id,
                    company_name=company.company_name,
                    company_slug=company.company_slug,
                    subscription_tier=company.subscription_tier,
                    monthly_credits_limit=company.monthly_credits_limit,
                    monthly_credits_used=company.monthly_credits_used,
                    company_size=company.company_size
                )
            ),
            access_token=access_token
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=AuthResponse)
async def login_user(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return access token"""
    
    # Get user with company data
    result = await db.execute(
        select(User).options(selectinload(User.company))
        .where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    # Verify credentials
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(data={
        "sub": str(user.id),
        "company_id": str(user.company_id),
        "role": user.role
    })
    
    # Build response
    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            company=CompanyResponse(
                id=user.company.id,
                company_name=user.company.company_name,
                company_slug=user.company.company_slug,
                subscription_tier=user.company.subscription_tier,
                monthly_credits_limit=user.company.monthly_credits_limit,
                monthly_credits_used=user.company.monthly_credits_used,
                company_size=user.company.company_size
            )
        ),
        access_token=access_token
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information with company data"""
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        company=CompanyResponse(
            id=current_user.company.id,
            company_name=current_user.company.company_name,
            company_slug=current_user.company.company_slug,
            subscription_tier=current_user.company.subscription_tier,
            monthly_credits_limit=current_user.company.monthly_credits_limit,
            monthly_credits_used=current_user.company.monthly_credits_used,
            company_size=current_user.company.company_size
        )
    )

@router.post("/logout")
async def logout_user():
    """Logout user (client should remove token)"""
    return {"message": "Successfully logged out"}