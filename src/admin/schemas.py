"""
Admin-specific Pydantic schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

# Admin Dashboard Stats
class AdminStatsResponse(BaseModel):
    total_users: int
    total_companies: int
    total_campaigns_created: int
    active_users: int
    new_users_month: int
    new_users_week: int
    subscription_breakdown: Dict[str, int]
    monthly_recurring_revenue: float

# User Management
class AdminUserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    company_id: UUID
    company_name: str
    subscription_tier: str
    monthly_credits_used: int
    monthly_credits_limit: int

class UserListResponse(BaseModel):
    users: List[AdminUserResponse]
    total: int
    page: int
    limit: int
    pages: int

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class UserCreateRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "member"
    company_id: UUID
    is_active: bool = True
    is_verified: bool = False

# Company Management
class AdminCompanyResponse(BaseModel):
    id: UUID
    company_name: str
    company_slug: str
    industry: Optional[str]
    company_size: str
    subscription_tier: str
    subscription_status: str
    monthly_credits_used: int
    monthly_credits_limit: int
    total_campaigns_created: int
    created_at: datetime
    user_count: int
    campaign_count: int

class CompanyListResponse(BaseModel):
    companies: List[AdminCompanyResponse]
    total: int
    page: int
    limit: int
    pages: int

class CompanyUpdateRequest(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website_url: Optional[str] = None

# Subscription Management
class SubscriptionUpdateRequest(BaseModel):
    subscription_tier: Optional[str] = None
    subscription_status: Optional[str] = None
    monthly_credits_limit: Optional[int] = None
    reset_monthly_credits: bool = False

# Analytics & Reporting
class UserActivityResponse(BaseModel):
    user_id: UUID
    user_email: str
    company_name: str
    last_login: Optional[datetime]
    total_campaigns_created: int
    credits_used_month: int
    subscription_tier: str

class CompanyAnalyticsResponse(BaseModel):
    company_id: UUID
    company_name: str
    subscription_tier: str
    total_users: int
    total_campaigns_created: int
    monthly_credits_used: int
    monthly_credits_limit: int
    utilization_rate: float
    created_at: datetime

# Bulk Operations
class BulkUserUpdateRequest(BaseModel):
    user_ids: List[UUID]
    updates: UserUpdateRequest

class BulkSubscriptionUpdateRequest(BaseModel):
    company_ids: List[UUID]
    subscription_updates: SubscriptionUpdateRequest

# System Monitoring
class SystemHealthResponse(BaseModel):
    database_status: str
    api_response_time: float
    active_users_24h: int
    failed_requests_24h: int
    storage_usage_gb: float
    credit_usage_24h: int