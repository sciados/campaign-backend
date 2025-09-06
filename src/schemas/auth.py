# File: backend/src/schemas/auth.py
# Pydantic schemas for authentication endpoints

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    """Registration request schema"""
    email: EmailStr
    password: str
    full_name: str
    company_name: str

class CompanyInfo(BaseModel):
    """Company information schema"""
    id: str
    company_name: str
    company_slug: str
    subscription_tier: str
    monthly_credits_used: int
    monthly_credits_limit: int
    company_size: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    """User profile schema"""
    id: str
    email: str
    full_name: str
    role: str
    user_type: Optional[str] = None
    is_active: bool
    is_verified: bool
    company: Optional[CompanyInfo] = None
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    token_type: str
    expires_in: int
    user_id: str
    user: UserProfile

class DashboardRouteResponse(BaseModel):
    """Dashboard route response schema"""
    route: str