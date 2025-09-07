# src/users/schemas/user.py
"""
User-related Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class UserTypeSchema(str, Enum):
    """User type enumeration for schemas"""
    AFFILIATE_MARKETER = "affiliate_marketer"
    CONTENT_CREATOR = "content_creator"
    BUSINESS_OWNER = "business_owner"

class UserRoleSchema(str, Enum):
    """User role enumeration for schemas"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

# Request schemas
class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=1, max_length=255)
    company_name: str = Field(..., min_length=1, max_length=255)
    user_type: Optional[UserTypeSchema] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=1000)
    phone_number: Optional[str] = Field(None, max_length=50)
    timezone: Optional[str] = Field(None, max_length=100)
    language: Optional[str] = Field(None, max_length=10)
    theme: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    user_type: Optional[UserTypeSchema] = None

class UserPasswordUpdate(BaseModel):
    """Schema for password updates"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v

class UserTypeUpdate(BaseModel):
    """Schema for updating user type"""
    user_type: UserTypeSchema
    type_data: Optional[Dict[str, Any]] = None

class UserOnboardingUpdate(BaseModel):
    """Schema for onboarding updates"""
    step: int = Field(..., ge=0, le=100)
    step_data: Optional[Dict[str, Any]] = None
    goals: Optional[List[str]] = None
    experience_level: Optional[str] = Field(None, regex="^(beginner|intermediate|advanced)$")

class UserDashboardPreferences(BaseModel):
    """Schema for dashboard preferences"""
    theme: Optional[str] = Field(None, regex="^(light|dark|system)$")
    layout: Optional[str] = Field(None, regex="^(grid|list|cards)$")
    sidebar_collapsed: Optional[bool] = None
    show_welcome: Optional[bool] = None
    default_view: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    auto_refresh: Optional[bool] = None
    items_per_page: Optional[int] = Field(None, ge=10, le=100)

class UserNotificationPreferences(BaseModel):
    """Schema for notification preferences"""
    email_notifications: bool = True
    marketing_emails: bool = True
    product_updates: bool = True
    security_alerts: bool = True
    campaign_updates: bool = True
    intelligence_ready: bool = True

# Response schemas
class CompanyResponse(BaseModel):
    """Company information in responses"""
    id: str
    company_name: str
    company_slug: str
    subscription_tier: str
    monthly_credits_used: int
    monthly_credits_limit: int
    company_size: Optional[str] = None
    industry: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserUsageSummary(BaseModel):
    """User usage statistics"""
    monthly_usage: Dict[str, int]
    lifetime_totals: Dict[str, int]
    subscription_info: Dict[str, Any]
    account_info: Dict[str, Any]

class UserResponse(BaseModel):
    """Complete user response schema"""
    id: str
    email: str
    full_name: str
    display_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    user_type: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_admin: bool
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: str
    language: str
    theme: str
    experience_level: str
    onboarding_completed: bool
    onboarding_step: int
    created_at: Optional[str] = None
    last_login_at: Optional[str] = None
    last_activity_at: Optional[str] = None
    company: Optional[CompanyResponse] = None
    
    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    """Detailed user profile response"""
    id: str
    email: str
    full_name: str
    display_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    user_type: Optional[str] = None
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: str
    language: str
    theme: str
    experience_level: str
    onboarding_completed: bool
    created_at: Optional[str] = None
    last_login_at: Optional[str] = None
    company: Optional[CompanyResponse] = None
    dashboard_preferences: Dict[str, Any]
    notification_preferences: Dict[str, Any]
    usage_summary: UserUsageSummary
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    """Response for user lists (admin)"""
    users: List[UserResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class UserStatsResponse(BaseModel):
    """User statistics response"""
    total_users: int
    active_users: int
    inactive_users: int
    admin_users: int
    user_types: Dict[str, int]
    recent_signups: int
    onboarded_users: int

# Search and filter schemas
class UserSearchRequest(BaseModel):
    """Schema for user search requests"""
    query: str = Field(..., min_length=1, max_length=100)
    user_type: Optional[UserTypeSchema] = None
    is_active: Optional[bool] = None
    company_id: Optional[str] = None
    limit: int = Field(50, ge=1, le=100)

class UserFilterRequest(BaseModel):
    """Schema for user filtering"""
    user_type: Optional[UserTypeSchema] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    role: Optional[UserRoleSchema] = None
    company_id: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    order_by: Optional[str] = Field(None, regex="^(created_at|last_login_at|full_name|email)$")
    order_direction: Optional[str] = Field("desc", regex="^(asc|desc)$")

# Success response schemas
class UserCreatedResponse(BaseModel):
    """Response for successful user creation"""
    success: bool = True
    message: str = "User created successfully"
    user: UserResponse
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None

class UserUpdatedResponse(BaseModel):
    """Response for successful user updates"""
    success: bool = True
    message: str = "User updated successfully"
    user: UserResponse

class UserDeletedResponse(BaseModel):
    """Response for successful user deletion"""
    success: bool = True
    message: str = "User deactivated successfully"
    user_id: str

class PreferencesUpdatedResponse(BaseModel):
    """Response for successful preferences update"""
    success: bool = True
    message: str = "Preferences updated successfully"
    preferences: Dict[str, Any]

# Error response schemas
class UserErrorResponse(BaseModel):
    """User-related error response"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    success: bool = False
    error: str = "Validation error"
    validation_errors: List[Dict[str, Any]]