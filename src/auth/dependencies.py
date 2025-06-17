"""
Authentication dependencies - Clean best practice implementation
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import Optional

from src.core.database import get_db
from src.core.security import verify_token
from src.models.user import User

# HTTPBearer for extracting JWT tokens from Authorization header
security = HTTPBearer()

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
        payload = verify_token(credentials.credentials)
        user_id_str: str = payload.get("sub")
        
        if user_id_str is None:
            raise credentials_exception
        
        # Convert string to UUID
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise credentials_exception
        
        # Get user from database with company data pre-loaded
        result = await db.execute(
            select(User)
            .options(selectinload(User.company))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise credentials_exception
        
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception:
        # Convert any other exception to authentication error
        raise credentials_exception

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify user is active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Verify user has admin permissions (owner or admin role)
    """
    if current_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required"
        )
    return current_user

# Optional dependency for endpoints that can work with or without auth
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication - returns User if valid token provided, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        user_id_str: str = payload.get("sub")
        
        if user_id_str is None:
            return None
        
        user_id = UUID(user_id_str)
        result = await db.execute(
            select(User)
            .options(selectinload(User.company))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        return user if user and user.is_active else None
        
    except Exception:
        return None