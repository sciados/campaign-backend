"""
Authentication routes with company support
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
import re
import secrets

from src.core.database import get_db
from src.core.security import verify_password, get_password_hash, create_access_token
from src.auth.schemas import UserRegister, UserLogin, UserResponse, AuthResponse, CompanyResponse
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.company import Company, CompanyMembership, CompanySize, CompanySubscriptionTier, MembershipRole

router = APIRouter(prefix="/api/auth", tags=["authentication"])

def create_company_slug(company_name: str) -> str:
    """Create URL-friendly slug from company name"""
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', company_name.lower())
    # Remove leading/trailing hyphens and limit length
    slug = slug.strip('-')[:50]
    return slug

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
    """Register user and create company with smart defaults"""
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create company slug and ensure uniqueness
        base_slug = create_company_slug(user_data.company_name)
        unique_slug = await ensure_unique_company_slug(base_slug, db)
        
        # Create new company
        new_company = Company(
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
        
        db.add(new_company)
        await db.flush()  # Get company ID
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            id=uuid4(),
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name,
            company_id=new_company.id,
            role=MembershipRole.OWNER.value,  # First user is always owner
            is_active=True,
            is_verified=False
        )
        
        db.add(new_user)
        await db.flush()  # Get user ID
        
        # Create company membership
        membership = CompanyMembership(
            id=uuid4(),
            user_id=new_user.id,
            company_id=new_company.id,
            role=MembershipRole.OWNER.value,
            status="active"
        )
        
        db.add(membership)
        await db.commit()
        
        # Refresh objects to get all data
        await db.refresh(new_user)
        await db.refresh(new_company)
        
        # Create access token with company context
        access_token = create_access_token(data={
            "sub": str(new_user.id),
            "company_id": str(new_company.id),
            "role": new_user.role
        })
        
        # Return response with company data
        company_response = CompanyResponse(
            id=new_company.id,
            company_name=new_company.company_name,
            company_slug=new_company.company_slug,
            subscription_tier=new_company.subscription_tier,
            monthly_credits_limit=new_company.monthly_credits_limit,
            monthly_credits_used=new_company.monthly_credits_used,
            company_size=new_company.company_size
        )
        
        user_response = UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            is_active=new_user.is_active,
            is_verified=new_user.is_verified,
            company=company_response
        )
        
        return AuthResponse(
            user=user_response,
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
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login user with company data"""
    
    # Get user with company data
    result = await db.execute(
        select(User).options(selectinload(User.company))
        .where(User.email == user_credentials.email)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    # Create access token with company context
    access_token = create_access_token(data={
        "sub": str(user.id),
        "company_id": str(user.company_id),
        "role": user.role
    })
    
    # Build response with company data
    company_response = CompanyResponse(
        id=user.company.id,
        company_name=user.company.company_name,
        company_slug=user.company.company_slug,
        subscription_tier=user.company.subscription_tier,
        monthly_credits_limit=user.company.monthly_credits_limit,
        monthly_credits_used=user.company.monthly_credits_used,
        company_size=user.company.company_size
    )
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        company=company_response
    )
    
    return AuthResponse(
        user=user_response,
        access_token=access_token
    )

@router.get("/validate", response_model=UserResponse)
async def validate_token(current_user: User = Depends(get_current_user)):
    """Validate token and return user data with company"""
    
    # Load company data
    company_response = CompanyResponse(
        id=current_user.company.id,
        company_name=current_user.company.company_name,
        company_slug=current_user.company.company_slug,
        subscription_tier=current_user.company.subscription_tier,
        monthly_credits_limit=current_user.company.monthly_credits_limit,
        monthly_credits_used=current_user.company.monthly_credits_used,
        company_size=current_user.company.company_size
    )
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        company=company_response
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information with company data"""
    
    # Same as validate_token
    company_response = CompanyResponse(
        id=current_user.company.id,
        company_name=current_user.company.company_name,
        company_slug=current_user.company.company_slug,
        subscription_tier=current_user.company.subscription_tier,
        monthly_credits_limit=current_user.company.monthly_credits_limit,
        monthly_credits_used=current_user.company.monthly_credits_used,
        company_size=current_user.company.company_size
    )
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        company=company_response
    )