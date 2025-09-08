# src/users/middleware/__init__.py

"""
Users Middleware Module

Provides authentication and authorization middleware for the Users module.
Exports commonly used middleware functions and classes.
"""

from src.users.middleware.auth_middleware import AuthMiddleware

# Import from services where the function actually exists
from src.users.services.auth_service import AuthService

# If you need get_current_user as a module-level function, create a wrapper
async def get_current_user_wrapper(token: str, db_session):
    """
    Wrapper function to get current user from token
    Note: This requires a database session
    """
    auth_service = AuthService(db_session)
    return await auth_service.get_current_user(token)

__all__ = [
    "AuthMiddleware",
    "get_current_user_wrapper",
]