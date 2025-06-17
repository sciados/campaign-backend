"""
Authentication Pydantic schemas with company support
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from uuid import UUID
import re

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Company fields with smart defaults
    company_name: Optional[str] = None  # Will auto-generate if not provided
    industry: Optional[str] = "Marketing"
    company_size: str = "startup"
    website_url: Optional[str] = None

    @validator('company_name', always=True)
    def generate_company_name(cls, v, values):
        """Auto-generate company name if not provided"""
        if v:
            return v
        
        # Try to generate from full_name or first_name
        if 'full_name' in values and values['full_name']:
            name_parts = values['full_name'].split()
            if len(name_parts) >= 2:
                return f"{name_parts[-1]} Marketing"  # "Smith Marketing"
            else:
                return f"{values['full_name']}'s Business"  # "John's Business"
        elif 'first_name' in values and values['first_name']:
            return f"{values['first_name']}'s Marketing"  # "John's Marketing"
        else:
            return "My Marketing Business"  # Fallback

    @validator('company_name')
    def validate_company_name(cls, v):
        """Clean up company name"""
        if v:
            # Remove extra spaces and capitalize properly
            return ' '.join(word.capitalize() for word in v.split())
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class CompanyResponse(BaseModel):
    id: UUID
    company_name: str
    company_slug: str
    subscription_tier: str
    monthly_credits_limit: int
    monthly_credits_used: int
    company_size: str
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    company: Optional[CompanyResponse] = None
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str