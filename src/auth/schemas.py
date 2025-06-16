"""
Authentication Pydantic schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    first_name: Optional[str] = None  # For frontend compatibility
    last_name: Optional[str] = None   # For frontend compatibility
    company: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    subscription_tier: str
    is_active: bool
    is_verified: bool
    credits_remaining: int
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str