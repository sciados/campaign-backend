# src/models/clickbank.py - NEW FILE
"""
ClickBank models for marketplace integration
"""
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Integer, Float, Boolean, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from .base import BaseModel

class ClickBankCategory(str, enum.Enum):
    TOP = "top"
    NEW = "new"
    HEALTH = "health"
    EBUSINESS = "ebusiness"
    SELFHELP = "selfhelp"
    GREEN = "green"
    BUSINESS = "business"

class ProductAnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ClickBankProduct(BaseModel):
    """ClickBank products for marketplace"""
    __tablename__ = "clickbank_products"
    
    # ClickBank Data
    vendor = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(Enum(ClickBankCategory, name='clickbank_category'), nullable=False)
    
    # Performance Metrics
    gravity = Column(DECIMAL(8,2))
    commission_rate = Column(DECIMAL(5,2))
    initial_per_sale = Column(DECIMAL(8,2))
    average_per_sale = Column(DECIMAL(8,2))
    
    # URLs
    salespage_url = Column(Text, nullable=False)
    pitch_page_url = Column(Text)
    affiliate_page_url = Column(Text)
    
    # ClickBank IDs
    product_id = Column(String(50), unique=True)
    vendor_id = Column(String(50))
    
    # Analysis Data
    analysis_status = Column(Enum(ProductAnalysisStatus, name='product_analysis_status'), default=ProductAnalysisStatus.PENDING)
    analysis_score = Column(DECIMAL(3,2))
    analysis_data = Column(JSONB, default={})
    
    # Intelligence Insights
    key_insights = Column(ARRAY(Text), default=[])
    recommended_angles = Column(ARRAY(Text), default=[])
    target_audience_data = Column(JSONB, default={})
    competitive_advantages = Column(ARRAY(Text), default=[])
    
    # Marketplace Features
    is_featured = Column(Boolean, default=False)
    is_trending = Column(Boolean, default=False)
    quality_score = Column(DECIMAL(3,2))
    
    # Timestamps
    date_created = Column(DateTime(timezone=True))
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    last_analyzed = Column(DateTime(timezone=True))
    
    # Metadata
    metadata = Column(JSONB, default={})
    
    def __repr__(self):
        return f"<ClickBankProduct(id={self.id}, title='{self.title}', vendor='{self.vendor}')>"

class UserClickBankFavorite(BaseModel):
    """User favorites for ClickBank products"""
    __tablename__ = "user_clickbank_favorites"
    
    # References
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("clickbank_products.id"), nullable=False)
    
    # User Notes
    notes = Column(Text)
    tags = Column(ARRAY(String), default=[])
    
    # Tracking
    campaigns_created = Column(Integer, default=0)
    last_viewed = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    product = relationship("ClickBankProduct")
    
    def __repr__(self):
        return f"<UserClickBankFavorite(user_id={self.user_id}, product_id={self.product_id})>"

class ClickBankCampaign(BaseModel):
    """Track campaigns created from ClickBank products"""
    __tablename__ = "clickbank_campaigns"
    
    # References
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("clickbank_products.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Campaign Creation Context
    selected_angles = Column(ARRAY(Text), default=[])
    customization_notes = Column(Text)
    
    # Performance Tracking
    content_generated = Column(Integer, default=0)
    campaign_status = Column(String(50))
    
    # Relationships
    campaign = relationship("Campaign")
    product = relationship("ClickBankProduct")
    user = relationship("User")