"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4

from src.core.database import get_db
from src.core.security import verify_password, get_password_hash, create_access_token
from src.auth.schemas import UserRegister, UserLogin, UserResponse, AuthResponse
from src.auth.dependencies import get_current_user
from src.models.user import User, SubscriptionTier

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=AuthResponse)
async def register_user(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create full_name from first_name and last_name if provided
    full_name = user_data.full_name
    if not full_name and user_data.first_name:
        full_name = user_data.first_name
        if user_data.last_name:
            full_name += f" {user_data.last_name}"
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        id=uuid4(),
        email=user_data.email,
        password_hash=hashed_password,
        full_name=full_name or "User",
        subscription_tier=SubscriptionTier.FREE,
        is_active=True,
        is_verified=False,
        credits_remaining=1000,  # Free tier credits
        preferences={"company": user_data.company} if user_data.company else {}
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    # Return user and token
    user_response = UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        subscription_tier=new_user.subscription_tier.value,
        is_active=new_user.is_active,
        is_verified=new_user.is_verified,
        credits_remaining=new_user.credits_remaining
    )
    
    return AuthResponse(
        user=user_response,
        access_token=access_token
    )

@router.post("/login", response_model=AuthResponse)
async def login_user(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login user"""
    
    # Get user by email
    result = await db.execute(select(User).where(User.email == user_credentials.email))
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
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Return user and token
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        subscription_tier=user.subscription_tier.value,
        is_active=user.is_active,
        is_verified=user.is_verified,
        credits_remaining=user.credits_remaining
    )
    
    return AuthResponse(
        user=user_response,
        access_token=access_token
    )

@router.get("/validate", response_model=UserResponse)
async def validate_token(current_user: User = Depends(get_current_user)):
    """Validate token and return user data"""
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        subscription_tier=current_user.subscription_tier.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        credits_remaining=current_user.credits_remaining
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        subscription_tier=current_user.subscription_tier.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        credits_remaining=current_user.credits_remaining
    )