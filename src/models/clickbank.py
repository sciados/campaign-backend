# src/models/clickbank.py - FIXED VERSION with correct database schema
from sqlalchemy import Column, String, Integer, Boolean, DECIMAL, DateTime, Text, JSON, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from src.core.database import Base

class ClickBankProduct(Base):
    __tablename__ = "clickbank_products"
    __table_args__ = (
        Index('idx_clickbank_products_category', 'category'),
        Index('idx_clickbank_products_gravity', 'gravity'),
        Index('idx_clickbank_products_active', 'is_active'),
        Index('idx_clickbank_products_last_seen', 'last_seen_at'),
        {'extend_existing': True}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    vendor = Column(String(200))
    description = Column(Text)
    category = Column(String(50), nullable=False)
    gravity = Column(DECIMAL(10,2))
    commission_rate = Column(DECIMAL(5,2))
    initial_dollar_amount = Column(DECIMAL(10,2))
    avg_dollar_per_conversion = Column(DECIMAL(10,2))
    salespage_url = Column(String(1000))
    product_page_url = Column(String(1000))
    vendor_id = Column(String(100))
    product_type = Column(String(50), default='digital')
    rebill_percentage = Column(DECIMAL(5,2))
    refund_rate = Column(DECIMAL(5,2))
    activation_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    last_seen_at = Column(DateTime, server_default=func.now())
    performance_score = Column(Integer)
    affiliate_tools_available = Column(Boolean, default=False)
    target_keywords = Column(ARRAY(String))
    
    # Analysis fields
    analysis_status = Column(String(20), default='pending')
    analysis_score = Column(DECIMAL(3,2))
    key_insights = Column(JSONB, default=lambda: [])
    recommended_angles = Column(JSONB, default=lambda: [])
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class ClickBankCategoryURL(Base):
    __tablename__ = "clickbank_category_urls"
    __table_args__ = {'extend_existing': True}
    
    # ✅ FIXED: Model now matches your actual database schema
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(50), nullable=False)  # Note: Not unique in your DB
    category_name = Column(String(100), nullable=False)
    primary_url = Column(String(1000), nullable=False)
    backup_urls = Column(JSONB, default=lambda: [])
    is_active = Column(Boolean, default=True)
    
    # ✅ FIXED: Use actual column name from your database
    last_validated_at = Column(DateTime)  # Your DB has this, not 'last_tested'
    
    priority_level = Column(Integer, default=5)
    commission_range = Column(String(20))
    target_audience = Column(Text)
    validation_status = Column(String(20), default='pending')
    url_type = Column(String(20), default='marketplace')
    scraping_notes = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class ScrapingSchedule(Base):
    __tablename__ = "scraping_schedule"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(50), unique=True, nullable=False)
    scrape_time = Column(DateTime, nullable=False)
    is_enabled = Column(Boolean, default=True)
    last_scraped_at = Column(DateTime)
    next_scrape_at = Column(DateTime)
    scrape_frequency_hours = Column(Integer, default=24)
    max_products_per_scrape = Column(Integer, default=50)
    priority_level = Column(Integer, default=5)
    success_rate = Column(DECIMAL(5,2), default=0)
    avg_scraping_time_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class ScrapingLog(Base):
    __tablename__ = "scraping_logs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(50), nullable=False)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    status = Column(String(20), nullable=False, default='running')
    products_found = Column(Integer, default=0)
    products_added = Column(Integer, default=0)
    products_updated = Column(Integer, default=0)
    products_marked_inactive = Column(Integer, default=0)
    error_message = Column(Text)
    scraping_duration_seconds = Column(Integer)
    success_rate = Column(DECIMAL(5,2))
    data_quality_score = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

class ProductPerformance(Base):
    __tablename__ = "product_performance"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    date_tracked = Column(DateTime, server_default=func.current_date())
    gravity_score = Column(DECIMAL(10,2))
    commission_rate = Column(DECIMAL(5,2))
    estimated_earnings = Column(DECIMAL(10,2))
    rank_in_category = Column(Integer)
    trending_direction = Column(String(10))
    created_at = Column(DateTime, server_default=func.now())

class UserAffiliatePreferences(Base):
    __tablename__ = "user_affiliate_preferences"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    
    # ClickBank Settings
    clickbank_affiliate_id = Column(String(50))
    clickbank_nickname = Column(String(100))
    
    # Link Customization
    link_cloaking_enabled = Column(Boolean, default=False)
    custom_domain = Column(String(100))
    tracking_parameters = Column(JSONB, default=lambda: {})
    
    # Commission Tracking
    commission_goal_monthly = Column(DECIMAL(10,2), default=0)
    preferred_commission_threshold = Column(DECIMAL(5,2), default=50.0)
    
    # Notification Settings
    notify_new_products = Column(Boolean, default=True)
    notify_high_gravity_products = Column(Boolean, default=True)
    email_weekly_reports = Column(Boolean, default=True)
    
    # Campaign Integration
    auto_create_campaigns = Column(Boolean, default=False)
    default_campaign_tone = Column(String(50), default='professional')
    default_campaign_style = Column(String(50), default='persuasive')
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class AffiliateLinkClick(Base):
    __tablename__ = "affiliate_link_clicks"
    __table_args__ = (
        Index('idx_affiliate_clicks_user_id', 'user_id'),
        Index('idx_affiliate_clicks_product_id', 'product_id'),
        Index('idx_affiliate_clicks_timestamp', 'click_timestamp'),
        Index('idx_affiliate_clicks_category', 'category'),
        {'extend_existing': True}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    product_id = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    original_url = Column(String(1000), nullable=False)
    affiliate_url = Column(String(1000), nullable=False)
    click_ip = Column(String(45))
    click_user_agent = Column(Text)
    click_referrer = Column(String(1000))
    click_timestamp = Column(DateTime, server_default=func.now())
    conversion_tracked = Column(Boolean, default=False)
    estimated_commission = Column(DECIMAL(10,2))

# Export all models
__all__ = [
    'ClickBankProduct',
    'ClickBankCategoryURL', 
    'ScrapingSchedule',
    'ScrapingLog',
    'ProductPerformance',
    'UserAffiliatePreferences',
    'AffiliateLinkClick'
]