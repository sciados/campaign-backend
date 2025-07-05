# src/models/user.py - FIXED VERSION
"""
User model and related schemas - FIXED VERSION (no circular imports)
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# EMERGENCY FIX: Create BaseModel locally to avoid circular imports
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4

Base = declarative_base()

class BaseModel(Base):
    """Emergency base model to avoid circular imports"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class User(BaseModel):
    """User model - FIXED VERSION"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    avatar_url = Column(Text)
    
    # Company Relationship
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    role = Column(String(50), default="owner")  # owner, admin, member, viewer
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # User Preferences (personal, not company-wide)
    preferences = Column(JSONB, default={})
    
    # EMERGENCY FIX: Remove relationships to avoid circular imports
    # Relationships will be defined elsewhere if needed
    
    def get_preferences(self) -> dict:
        """Get user preferences with proper handling"""
        if isinstance(self.preferences, dict):
            return self.preferences
        elif isinstance(self.preferences, str):
            try:
                import json
                return json.loads(self.preferences)
            except (json.JSONDecodeError, ValueError):
                return {}
        return {}
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"