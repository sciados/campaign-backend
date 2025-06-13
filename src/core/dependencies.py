"""
FastAPI dependencies for authentication and database
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import structlog

from src.core.database import get_db
from src.core.security import verify_token
from src.models.user import User

logger = structlog.get_logger()
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
ECHO is off.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
ECHO is off.
    token = credentials.credentials
    payload = verify_token(token)
ECHO is off.
    if payload is None:
        raise credentials_exception
ECHO is off.
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
ECHO is off.
    # Get user from database
    user = await User.get_by_id(db, user_id)
    if user is None:
        raise credentials_exception
ECHO is off.
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
