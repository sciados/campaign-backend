from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional
import re

class WaitlistCreate(BaseModel):
    email: EmailStr
    referrer: Optional[str] = None
    
    @validator('email')
    def validate_email(cls, v):
        # Additional email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower().strip()

class WaitlistResponse(BaseModel):
    message: str
    total_signups: int
    position: int
    email: str
    
    class Config:
        from_attributes = True

class WaitlistStatsResponse(BaseModel):
    total: int
    today: int
    this_week: int
    this_month: int
    recent_signups: list
    daily_stats: list
    
    class Config:
        from_attributes = True

class WaitlistEntry(BaseModel):
    id: int
    email: str
    created_at: datetime
    ip_address: Optional[str]
    is_notified: bool
    
    class Config:
        from_attributes = True