# src/auth/routes.py

import os
import logging
from datetime import datetime, timedelta
from uuid import UUID, uuid4 # Import uuid4 to generate new UUIDs

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload # Needed for eager loading of relationships

# Import password hashing and JWT functions from your security module
from src.core.security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
# Import your database session, User model, and Company model
from src.core.database import get_db
from src.models.user import User # Assuming your User model is here
from src.models.company import Company # Assuming your Company model is here and required for User

# JWT and security imports
from jose import jwt

# Set up logging for this module
logger = logging.getLogger(__name__)

# --- FastAPI Router Definition - FIXED: Remove duplicate prefix ---

router = APIRouter(
    # prefix="/auth",  # ❌ REMOVED: This was causing double prefix /api/auth/auth
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

# HTTPBearer for extracting JWT tokens from Authorization header
security = HTTPBearer()

# --- Authentication Dependency ---
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Extract and validate JWT token, return authenticated user with company data
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify and decode the token
        print(f"🔍 Decoding token...")
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        print(f"🔍 Token payload: {payload}")
        
        user_id_str: str = payload.get("sub")
        user_email: str = payload.get("email")
        user_role: str = payload.get("role")
        company_id: str = payload.get("company_id")

        print(f"🔍 Extracted from token:")
        print(f"   user_id: {user_id_str}")
        print(f"   email: {user_email}")
        print(f"   role: {user_role}")
        print(f"   company_id: {company_id}")

        if user_id_str is None or user_email is None or user_role is None or company_id is None:
            print(f"❌ Missing required fields in token")
            raise credentials_exception
        
        # Convert string to UUID
        try:
            user_id = UUID(user_id_str)
            print(f"✅ User ID converted to UUID: {user_id}")
        except ValueError:
            print(f"❌ Invalid UUID format: {user_id_str}")
            raise credentials_exception
        
        # Fetch the user from the DB to ensure they exist, are active, and load their company relationship
        print(f"🔍 Fetching user from database...")
        user = await db.scalar(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.company)) # Eagerly load the company
        )
        
        if user is None:
            print(f"❌ User not found in database")
            raise credentials_exception
            
        if not user.is_active:
            print(f"❌ User is not active")
            raise credentials_exception
        
        print(f"✅ User found: {user.email}")
        print(f"✅ User company_id: {user.company_id}")
        
        # Verify company_id in token matches user's actual company_id
        if str(user.company_id) != company_id:
             print(f"❌ Token company_id mismatch!")
             print(f"   Token company_id: {company_id}")
             print(f"   User DB company_id: {user.company_id}")
             raise credentials_exception

        print(f"✅ Authentication successful!")
        return user # Return the full User ORM object with company loaded

    except jwt.ExpiredSignatureError:
        print(f"❌ Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError as e:
        print(f"❌ JWT Error: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"❌ Unexpected error in get_current_user dependency: {str(e)}")
        logger.exception(f"Unexpected error in get_current_user dependency: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication processing error.",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
async def register_user(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user with email and password, storing them directly in PostgreSQL.
    Automatically creates a new company for the first registered user.
    """
    # Check if a user with this email already exists
    existing_user = await db.scalar(select(User).where(User.email == user_data.email))
    if existing_user:
        logger.warning(f"Registration attempt for existing email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
            total_campaigns=0,
            created_at=datetime.utcnow()
        )
        db.add(new_company)
        await db.flush() # Flush to assign company_id before user creation if needed immediately

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
            created_at=datetime.utcnow()
        )
        db.add(new_user)
        
        await db.commit()
        await db.refresh(new_user) # Refresh to get the generated ID and other defaults
        await db.refresh(new_company)

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
        await db.rollback() # Rollback in case of error
        logger.exception(f"Unexpected error during user registration for {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during registration: {str(e)}"
        )


@router.post("/token", response_model=Token, summary="Login and obtain access token (OAuth2 standard)")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates a user and returns a JWT access token.
    Uses standard OAuth2 password flow.
    """
    user = await db.scalar(select(User).where(User.email == form_data.username)) # form_data.username is the email

    # Use verify_password from src.core.security.py
    if not user or not verify_password(form_data.password, user.password_hash): # Use user.password_hash
        logger.warning(f"Login attempt failed for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if the user is active (as per user.py model)
    if not user.is_active:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
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
async def login_user_json(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Logs in an existing user and returns an access token, accepting JSON body.
    """
    user = await db.scalar(select(User).where(User.email == user_login.email))

    # Use verify_password from src.core.security.py
    if not user or not verify_password(user_login.password, user.password_hash): # Use user.password_hash
        logger.warning(f"JSON login attempt failed for email: {user_login.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not user.is_active:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive. Please contact support."
        )

    # ✅ ADDED: Get company information for response
    company = await db.scalar(select(Company).where(Company.id == user.company_id))

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
async def get_user_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Get current user profile with company information.
    This endpoint can be used to validate tokens and get user data.
    """
    try:
        # Get company data if not already loaded
        if hasattr(current_user, 'company') and current_user.company:
            company = current_user.company
        else:
            # Fetch company separately if not loaded
            company = await db.scalar(select(Company).where(Company.id == current_user.company_id))
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )