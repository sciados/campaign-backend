"""
FastAPI dependencies for authentication and database - ASYNC FIXED VERSION
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import Optional
from uuid import UUID
import structlog

from src.core.database import get_async_db  # ✅ FIXED: Use get_async_db
from src.core.security import verify_token, SECRET_KEY
from src.models.user import User
from jose import jwt, JWTError

logger = structlog.get_logger()
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)  # ✅ FIXED: Use get_async_db
) -> User:
    """Get current authenticated user"""

    credentials_exception = HTTPException(
        status_code=http_status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id_str: str = payload.get("sub")
        user_email: str = payload.get("email")
        user_role: str = payload.get("role")
        company_id: str = payload.get("company_id")

        if user_id_str is None or user_email is None or user_role is None or company_id is None:
            raise credentials_exception
        
        # Convert string to UUID
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise credentials_exception
        
        # ✅ FIXED: Use async database operation
        result = await db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.company))
        )
        user = result.scalar_one_or_none()
        
        if user is None or not user.is_active:
            raise credentials_exception
        
        # Verify company_id in token matches user's actual company_id
        if str(user.company_id) != company_id:
            logger.warning(f"Token company_id mismatch for user {user_id}. Token: {company_id}, User DB: {user.company_id}")
            raise credentials_exception

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication processing error",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current admin user"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user