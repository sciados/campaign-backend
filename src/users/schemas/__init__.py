# src/users/schemas/__init__.py

"""User Schemas"""

# Import only classes that actually exist in user.py
from src.users.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProfile,  # This exists in user.py
    UserPasswordUpdate,
    UserTypeUpdate,
    UserOnboardingUpdate,
    UserDashboardPreferences,
    UserNotificationPreferences,
    CompanyResponse,  # This exists
    UserUsageSummary,
    UserListResponse,
    UserStatsResponse,
    UserSearchRequest,
    UserFilterRequest,
    UserCreatedResponse,
    UserUpdatedResponse,
    UserDeletedResponse,
    PreferencesUpdatedResponse,
    UserErrorResponse,
    ValidationErrorResponse
)

# Import only classes that actually exist in auth.py (fix the path)
from src.users.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    CompanyInfo,
    UserProfile as AuthUserProfile,  # Alias to avoid conflict
    DashboardRouteResponse
)

__all__ = [
    # User schemas that actually exist
    "UserCreate",
    "UserUpdate",
    "UserResponse", 
    "UserProfile",
    "UserPasswordUpdate",
    "UserTypeUpdate",
    "UserOnboardingUpdate",
    "UserDashboardPreferences",
    "UserNotificationPreferences",
    "CompanyResponse",
    "UserUsageSummary",
    "UserListResponse",
    "UserStatsResponse",
    "UserSearchRequest",
    "UserFilterRequest",
    "UserCreatedResponse",
    "UserUpdatedResponse",
    "UserDeletedResponse",
    "PreferencesUpdatedResponse",
    "UserErrorResponse",
    "ValidationErrorResponse",
    # Auth schemas that actually exist
    "LoginRequest",
    "LoginResponse",
    "RegisterRequest",
    "CompanyInfo",
    "AuthUserProfile",
    "DashboardRouteResponse"
]