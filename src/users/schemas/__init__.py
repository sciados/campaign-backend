# src/users/schemas/__init__.py

"""User Schemas"""

from src.users.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProfile,
    UserPreferences,
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse
)

from src.users.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    TokenData,
    PasswordResetRequest,
    PasswordResetResponse
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse", 
    "UserProfile",
    "UserPreferences",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    # Auth schemas
    "LoginRequest",
    "LoginResponse",
    "RegisterRequest",
    "RegisterResponse",
    "TokenData",
    "PasswordResetRequest",
    "PasswordResetResponse"
]