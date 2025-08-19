# src/models/ai_provider_registry.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, DECIMAL
from sqlalchemy.sql import func
from src.models.base import Base  # Import your existing base
from datetime import datetime
import json

class AIProviderRegistry(Base):
    """Database model for discovered AI providers"""
    __tablename__ = "ai_provider_registry"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(255), nullable=False, index=True)
    env_var_name = Column(String(255), unique=True, nullable=False, index=True)
    env_var_status = Column(String(50), nullable=False, default='missing')
    value_preview = Column(String(255), nullable=True)
    integration_status = Column(String(50), default='discovered', index=True)
    category = Column(String(100), nullable=False, index=True)
    priority_tier = Column(String(50), nullable=False, default='discovered', index=True)
    cost_per_1k_tokens = Column(DECIMAL(10, 6), nullable=True)
    quality_score = Column(DECIMAL(3, 2), default=4.0)
    model = Column(String(255), nullable=True)
    capabilities = Column(Text, nullable=True)
    monthly_usage = Column(Integer, default=0)
    response_time_ms = Column(Integer, nullable=True)
    error_rate = Column(DECIMAL(5, 4), nullable=True)
    source = Column(String(50), default='environment', index=True)
    last_checked = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=False, index=True)
    api_endpoint = Column(String(255), nullable=True)
    discovery_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AIProviderRegistry(provider_name='{self.provider_name}', env_var_name='{self.env_var_name}')>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'provider_name': self.provider_name,
            'env_var_name': self.env_var_name,
            'env_var_status': self.env_var_status,
            'value_preview': self.value_preview,
            'integration_status': self.integration_status,
            'category': self.category,
            'priority_tier': self.priority_tier,
            'cost_per_1k_tokens': float(self.cost_per_1k_tokens) if self.cost_per_1k_tokens else None,
            'quality_score': float(self.quality_score) if self.quality_score else None,
            'model': self.model,
            'capabilities': self.capabilities.split(',') if self.capabilities else [],
            'monthly_usage': self.monthly_usage,
            'response_time_ms': self.response_time_ms,
            'error_rate': float(self.error_rate) if self.error_rate else None,
            'source': self.source,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'is_active': self.is_active,
            'api_endpoint': self.api_endpoint,
            'discovery_date': self.discovery_date.isoformat() if self.discovery_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }