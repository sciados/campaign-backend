# =====================================
# File: src/core/auth/dependencies.py
# =====================================

"""
Authentication dependencies for FastAPI routes.

Provides reusable authentication and authorization functions
for protecting API endpoints.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_db
from src.users.services.auth_service import AuthService
from src.users.models.user import UserRoleEnum

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_db)
) -> dict:
    """
    Get current authenticated user.

    Args:
        credentials: HTTP authorization credentials
        session: Database session

    Returns:
        dict: User information

    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_service = AuthService(session)
    user = await auth_service.get_current_user(credentials.credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "user_type": user.user_type,
        "company_id": str(user.company_id) if user.company_id else None
    }


async def require_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Require admin role for access.

    Args:
        current_user: Current authenticated user

    Returns:
        dict: Admin user information

    Raises:
        HTTPException: If user is not an admin
    """
    if current_user["role"] != UserRoleEnum.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user


async def require_admin_or_product_creator(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Require admin role OR content creator with special permissions.

    This enables product creators to submit URLs through special accounts
    while maintaining admin oversight.

    Args:
        current_user: Current authenticated user

    Returns:
        dict: Authorized user information

    Raises:
        HTTPException: If user doesn't have required permissions
    """
    # Admin always has access
    if current_user["role"] == UserRoleEnum.ADMIN.value:
        return current_user

    # Content creators can submit URLs for pre-analysis
    if current_user["user_type"] == "CONTENT_CREATOR":
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin or product creator access required"
    )