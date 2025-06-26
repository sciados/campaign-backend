# src/intelligence/generators/landing_page/database/models.py
"""
SQLAlchemy models for the enhanced landing page system.
These models correspond to the database tables created in the migration.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, DECIMAL, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()

# Enum definitions
class IntelligenceSourceType(enum.Enum):
    SALES_PAGE = "SALES_PAGE"
    DOCUMENT = "DOCUMENT"
    VIDEO = "VIDEO"
    WEBSITE = "WEBSITE"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    COMPETITOR_AD = "COMPETITOR_AD"

class AnalysisStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class ContentType(enum.Enum):
    EMAIL_SEQUENCE = "EMAIL_SEQUENCE"
    LANDING_PAGE = "LANDING_PAGE"
    AD_COPY = "AD_COPY"
    BLOG_POST = "BLOG_POST"
    SOCIAL_POSTS = "SOCIAL_POSTS"
    VIDEO_SCRIPT = "VIDEO_SCRIPT"
    SALES_PAGE = "SALES_PAGE"
    WEBINAR_CONTENT = "WEBINAR_CONTENT"

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False)
    company_slug = Column(String(255), unique=True)
    industry = Column(String(100))
    company_size = Column(String(50))
    website_url = Column(Text)
    logo_url = Column(Text)
    brand_colors = Column(JSONB, default={})
    brand_guidelines = Column(JSONB, default={})
    subscription_tier = Column(String(50), default='free')
    subscription_status = Column(String(50), default='active')
    billing_email = Column(String(255))
    monthly_credits_used = Column(Integer, default=0)
    monthly_credits_limit = Column(Integer, default=100)
    total_campaigns_created = Column(Integer, default=0)
    settings = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="company")
    campaigns = relationship("Campaign", back_populates="company")

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255))
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(Text)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    role = Column(String(50), default='user')
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    preferences = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="users")
    campaigns = relationship("Campaign", back_populates="user")

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    keywords = Column(JSONB, default={})
    target_audience = Column(JSONB, default={})
    status = Column(String(50), default='active')
    tone = Column(String(50), default='professional')
    style = Column(String(50), default='modern')
    settings = Column(JSONB, default={})
    
    # Workflow management
    workflow_state = Column(String(50), default='setup')
    workflow_preference = Column(String(50), default='guided')
    active_steps = Column(JSONB, default=[])
    completed_steps = Column(JSONB, default=[])
    current_step = Column(Integer, default=1)
    step_states = Column(JSONB, default={})
    current_session = Column(String(100))
    session_history = Column(JSONB, default=[])
    
    # Mode and preferences
    quick_mode_enabled = Column(Boolean, default=False)
    auto_advance_steps = Column(Boolean, default=True)
    skip_confirmations = Column(Boolean, default=False)
    show_detailed_guidance = Column(Boolean, default=True)
    require_step_completion = Column(Boolean, default=False)
    save_frequently = Column(Boolean, default=True)
    
    # Enhanced counters
    sources_count = Column(Integer, default=0)
    sources_processed = Column(Integer, default=0)
    intelligence_extracted = Column(Integer, default=0)
    intelligence_count = Column(Integer, default=0)
    content_generated = Column(Integer, default=0)
    generated_content_count = Column(Integer, default=0)
    
    # Step progress tracking
    step_2_data = Column(JSONB, default={})
    step_3_data = Column(JSONB, default={})
    step_4_data = Column(JSONB, default={})
    step_2_progress = Column(JSONB, default={})
    step_3_progress = Column(JSONB, default={})
    step_1_progress = Column(JSONB, default={})
    last_active_step = Column(Integer, default=1)
    
    # Enhanced metadata
    resume_data = Column(JSONB, default={})
    confidence_score = Column(DECIMAL(3,2), default=0.0)
    performance_metrics = Column(JSONB, default={})
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="campaigns")
    user = relationship("User", back_populates="campaigns")
    intelligence_sources = relationship("CampaignIntelligence", back_populates="campaign")
    generated_content = relationship("GeneratedContent", back_populates="campaign")

class CampaignIntelligence(Base):
    __tablename__ = "campaign_intelligence"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    
    # Source information
    source_url = Column(Text)
    source_type = Column(SQLEnum(IntelligenceSourceType))
    source_title = Column(String(500))
    analysis_status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    
    # Intelligence data
    offer_intelligence = Column(JSONB, default={})
    psychology_intelligence = Column(JSONB, default={})
    content_intelligence = Column(JSONB, default={})
    competitive_intelligence = Column(JSONB, default={})
    brand_intelligence = Column(JSONB, default={})
    
    # Enhanced intelligence fields
    scientific_intelligence = Column(JSONB, default={})
    credibility_intelligence = Column(JSONB, default={})
    market_intelligence = Column(JSONB, default={})
    emotional_transformation_intelligence = Column(JSONB, default={})
    scientific_authority_intelligence = Column(JSONB, default={})
    
    # Quality metrics
    usage_count = Column(Integer, default=0)
    success_rate = Column(DECIMAL(3,2), default=0.0)
    raw_content = Column(Text)
    processing_metadata = Column(JSONB, default={})
    confidence_score = Column(DECIMAL(3,2), default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="intelligence_sources")

class GeneratedContent(Base):
    __tablename__ = "generated_content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    intelligence_source_id = Column(UUID(as_uuid=True), ForeignKey("campaign_intelligence.id", ondelete="SET NULL"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    
    # Content basics
    content_type = Column(SQLEnum(ContentType), nullable=False)
    content_title = Column(String(500), nullable=False)
    content_body = Column(Text, nullable=False)
    content_metadata = Column(JSONB, default={})
    generation_prompt = Column(Text)
    generation_settings = Column(JSONB, default={})
    intelligence_used = Column(JSONB, default={})
    
    # Enhanced landing page fields
    landing_page_metadata = Column(JSONB, default={})
    seo_data = Column(JSONB, default={})
    performance_predictions = Column(JSONB, default={})
    page_components = Column(JSONB, default={})
    conversion_elements = Column(JSONB, default={})
    
    # Performance tracking
    performance_data = Column(JSONB, default={})
    user_rating = Column(Integer)
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True))
    
    # A/B testing
    variant_group_id = Column(UUID(as_uuid=True))
    is_control_variant = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="generated_content")
    landing_page_components = relationship("LandingPageComponent", back_populates="generated_content")
    variants = relationship("LandingPageVariant", back_populates="parent_content")

class LandingPageComponent(Base):
    __tablename__ = "landing_page_components"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generated_content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id", ondelete="CASCADE"), nullable=False)
    
    # Component details
    component_type = Column(String(50), nullable=False)
    component_order = Column(Integer, nullable=False)
    component_data = Column(JSONB, nullable=False)
    styling_data = Column(JSONB, default={})
    
    # Component metadata
    conversion_elements = Column(JSONB, default={})
    analytics_data = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    generated_content = relationship("GeneratedContent", back_populates="landing_page_components")

class LandingPageTemplate(Base):
    __tablename__ = "landing_page_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_name = Column(String(100), nullable=False)
    template_type = Column(String(50), nullable=False)
    industry_niche = Column(String(50))
    
    # Template configuration
    template_structure = Column(JSONB, nullable=False)
    default_styling = Column(JSONB, default={})
    conversion_elements = Column(JSONB, default={})
    
    # Template metadata
    performance_data = Column(JSONB, default={})
    usage_count = Column(Integer, default=0)
    is_premium = Column(Boolean, default=False)
    created_by = Column(String(100), default='system')
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class LandingPageVariant(Base):
    __tablename__ = "landing_page_variants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id", ondelete="CASCADE"), nullable=False)
    variant_group_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Variant details
    variant_name = Column(String(100), nullable=False)
    variant_type = Column(String(50), nullable=False)
    html_content = Column(Text, nullable=False)
    
    # Testing metadata
    test_hypothesis = Column(Text)
    expected_improvement = Column(String(100))
    test_configuration = Column(JSONB, default={})
    
    # Performance tracking
    performance_data = Column(JSONB, default={})
    is_winning_variant = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    parent_content = relationship("GeneratedContent", back_populates="variants")

class LandingPageAnalytics(Base):
    __tablename__ = "landing_page_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("landing_page_variants.id", ondelete="SET NULL"))
    
    # Traffic metrics
    page_views = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    returning_visitors = Column(Integer, default=0)
    
    # Engagement metrics
    avg_time_on_page = Column(Integer)  # seconds
    bounce_rate = Column(DECIMAL(5,4))
    scroll_depth_avg = Column(DECIMAL(5,2))
    exit_rate = Column(DECIMAL(5,4))
    
    # Conversion metrics
    conversions = Column(Integer, default=0)
    conversion_rate = Column(DECIMAL(5,4))
    cta_clicks = Column(Integer, default=0)
    form_starts = Column(Integer, default=0)
    form_completions = Column(Integer, default=0)
    
    # Detailed tracking data
    device_breakdown = Column(JSONB, default={})
    traffic_sources = Column(JSONB, default={})
    geographic_data = Column(JSONB, default={})
    conversion_events = Column(JSONB, default={})
    user_behavior_data = Column(JSONB, default={})
    
    # Time tracking
    date_recorded = Column(Date, server_default=func.current_date())
    hour_of_day = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ConversionEvent(Base):
    __tablename__ = "conversion_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("landing_page_variants.id", ondelete="SET NULL"))
    
    # Event details
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSONB, default={})
    
    # Session information
    session_id = Column(String(100))
    user_fingerprint = Column(String(100))
    ip_address = Column(INET)
    user_agent = Column(Text)
    
    # Context
    referrer = Column(Text)
    landing_url = Column(Text)
    device_info = Column(JSONB, default={})
    
    # Performance
    page_load_time = Column(Integer)  # milliseconds
    timestamp_ms = Column(Integer)  # Unix timestamp with milliseconds
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Export all models for easy imports
__all__ = [
    'Base',
    'Company',
    'User', 
    'Campaign',
    'CampaignIntelligence',
    'GeneratedContent',
    'LandingPageComponent',
    'LandingPageTemplate',
    'LandingPageVariant', 
    'LandingPageAnalytics',
    'ConversionEvent',
    'IntelligenceSourceType',
    'AnalysisStatus',
    'ContentType'
]