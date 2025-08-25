# src/auth/routes.py - FIXED VERSION with correct timezone import

import os
import logging
from datetime import datetime, timedelta, timezone  # ✅ FIXED: Import timezone from datetime, not time
from uuid import UUID, uuid4 # Import uuid4 to generate new UUIDs
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

# ✅ FIXED: Use synchronous Session instead of AsyncSession
from sqlalchemy.orm import Session, selectinload # Needed for eager loading of relationships
from sqlalchemy import select

# Import password hashing and JWT functions from your security module
from src.core.security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
# Import your database session, User model, and Company model
from src.core.database import get_db
from src.models.user import User # Assuming your User model is here
from src.models.company import Company # Assuming your Company model is here and required for User

# ✅ FIXED: Import get_current_user from dependencies instead of redefining it
from src.auth.dependencies import get_current_user

# JWT and security imports
from jose import jwt

# Set up logging for this module
logger = logging.getLogger(__name__)

# ✅ FIXED: Add auth prefix to router
router = APIRouter(
    prefix="/auth",  # ✅ ADDED: This makes routes /api/auth/login instead of /api/login
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

# HTTPBearer for extracting JWT tokens from Authorization header
security = HTTPBearer()

# --- Pydantic Models for Request Body Validation ---

class UserRegister(BaseModel):
    """Schema for user registration requests."""
    email: EmailStr
    password: str
    full_name: str
    company_name: str  # ✅ ADDED: Frontend sends this field

class Token(BaseModel):
    """Schema for returning JWT access tokens."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: UUID

class UserLogin(BaseModel):
    """Schema for user login requests."""
    email: EmailStr
    password: str

# --- API Endpoints ---

@router.post("/register", summary="Register a new user")
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Registers a new user with email and password, storing them directly in PostgreSQL.
    Automatically creates a new company for the first registered user.
    """
    # ✅ FIXED: Remove await from synchronous database operations
    existing_user = db.scalar(select(User).where(User.email == user_data.email))
    if existing_user:
        logger.warning(f"Registration attempt for existing email: {user_data.email}")
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    # Hash the password using the function from src/core/security.py
    hashed_password = get_password_hash(user_data.password)

    new_company = None
    # Business logic: For initial registration, create a new company and make the user its owner.
    # This is a simplified approach. In a more complex app, company creation might be a separate step
    # or handle inviting users to existing companies.
    try:
        # Generate a new UUID for the company
        new_company_id = uuid4()
        
        # ✅ FIXED: Use company_name from request instead of generating default
        company_name = user_data.company_name or f"{user_data.full_name}'s Company"
        
        # Create a new Company instance
        new_company = Company(
            id=new_company_id,
            company_name=company_name,  # Use provided company name
            company_slug=f"{company_name.lower().replace(' ', '-')}-{uuid4().hex[:4]}",
            subscription_tier="free", # Default tier for new companies
            subscription_status="active",
            monthly_credits_used=0,
            monthly_credits_limit=5000, # Example default limit
            total_campaigns_created=0,
            created_at=datetime.now(timezone.utc)  # ✅ FIXED: Now timezone.utc will work correctly
        )
        db.add(new_company)
        db.flush() # ✅ FIXED: Remove await - Flush to assign company_id before user creation if needed immediately

        # Create a new User object
        new_user = User(
            id=uuid4(), # Generate UUID for user
            email=user_data.email,
            password_hash=hashed_password, # Use password_hash as defined in user.py
            full_name=user_data.full_name,
            company_id=new_company.id, # Assign the newly created company's ID
            role="owner", # First user of a new company is the owner
            is_active=True,
            is_verified=False, # Set to False for email verification flow
            created_at=datetime.now(timezone.utc)  # ✅ FIXED: Now timezone.utc will work correctly
        )
        db.add(new_user)
        
        db.commit() # ✅ FIXED: Remove await
        db.refresh(new_user) # ✅ FIXED: Remove await - Refresh to get the generated ID and other defaults
        db.refresh(new_company) # ✅ FIXED: Remove await

        # ✅ ADDED: Create access token immediately after registration
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(new_user.id), "email": new_user.email, "role": new_user.role, "company_id": str(new_company.id)},
            expires_delta=access_token_expires
        )

        logger.info(f"User {new_user.email} registered and new company '{new_company.company_name}' created.")

        # ✅ FIXED: Return format expected by frontend
        return {
            "message": "User registered successfully! A new company was created for you.", 
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(new_user.id),
                "email": new_user.email,
                "full_name": new_user.full_name,
                "role": new_user.role,
                "company_id": str(new_company.id),
                "company_name": new_company.company_name
            }
        }

    except Exception as e:
        db.rollback() # ✅ FIXED: Remove await - Rollback in case of error
        logger.exception(f"Unexpected error during user registration for {user_data.email}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during registration: {str(e)}"
        )


@router.post("/token", response_model=Token, summary="Login and obtain access token (OAuth2 standard)")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)  # ✅ FIXED: Changed AsyncSession to Session
):
    """
    Authenticates a user and returns a JWT access token.
    Uses standard OAuth2 password flow.
    """
    # ✅ FIXED: Remove await
    user = db.scalar(select(User).where(User.email == form_data.username)) # form_data.username is the email

    # Use verify_password from src.core.security.py
    if not user or not verify_password(form_data.password, user.password_hash): # Use user.password_hash
        logger.warning(f"Login attempt failed for email: {form_data.username}")
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if the user is active (as per user.py model)
    if not user.is_active:
         raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive. Please contact support."
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role, "company_id": str(user.company_id)},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User {user.email} logged in successfully, issued token.")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60, # Convert minutes to seconds
        "user_id": user.id
    }

@router.post("/login", summary="Login an existing user (JSON body)")
async def login_user_json(user_login: UserLogin, db: Session = Depends(get_db)):  # ✅ FIXED: Changed AsyncSession to Session
    """
    Logs in an existing user and returns an access token, accepting JSON body.
    """

    # ✅ FIXED: Remove await
    user = db.scalar(select(User).where(User.email == user_login.email))

    # Use verify_password from src.core.security.py
    if not user or not verify_password(user_login.password, user.password_hash): # Use user.password_hash
        logger.warning(f"JSON login attempt failed for email: {user_login.email}")
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not user.is_active:
         raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive. Please contact support."
        )

    # ✅ ADDED: Get company information for response - FIXED: Remove await
    company = db.scalar(select(Company).where(Company.id == user.company_id))

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role, "company_id": str(user.company_id)},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User {user_login.email} logged in successfully via JSON, issued token.")
    
    # ✅ FIXED: Return format expected by frontend
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "company_id": str(user.company_id),
            "company_name": company.company_name if company else "Unknown"
        }
    }


@router.get("/profile", summary="Get current user profile")
async def get_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):  # ✅ FIXED: Changed AsyncSession to Session
    """
    Get current user profile with company information.
    This endpoint can be used to validate tokens and get user data.
    """
    try:
        # Get company data if not already loaded
        if hasattr(current_user, 'company') and current_user.company:
            company = current_user.company
        else:
            # ✅ FIXED: Remove await - Fetch company separately if not loaded
            company = db.scalar(select(Company).where(Company.id == current_user.company_id))
            if not company:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail="User company not found"
                )

        return {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "company": {
                "id": company.id,
                "company_name": company.company_name,
                "company_slug": company.company_slug,
                "subscription_tier": company.subscription_tier,
                "monthly_credits_used": company.monthly_credits_used,
                "monthly_credits_limit": company.monthly_credits_limit,
                "company_size": company.company_size
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching profile for user {current_user.id}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )