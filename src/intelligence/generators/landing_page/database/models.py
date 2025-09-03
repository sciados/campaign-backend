# src/models/database_models.py - Updated for NEW OPTIMIZED SCHEMA
"""
SQLAlchemy models for the NEW optimized database schema.
Replaces the old flat campaign intelligence table with normalized structure.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, DECIMAL, Date, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()

# Keep existing Company, User, Campaign models (they're fine)
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
    
    # Performance counters
    sources_count = Column(Integer, default=0)
    sources_processed = Column(Integer, default=0)
    intelligence_extracted = Column(Integer, default=0)
    intelligence_count = Column(Integer, default=0)
    content_generated = Column(Integer, default=0)
    generated_content_count = Column(Integer, default=0)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="campaigns")
    user = relationship("User", back_populates="campaigns")
    generated_content = relationship("GeneratedContent", back_populates="campaign")

# NEW OPTIMIZED SCHEMA MODELS - Replace campaign intelligence table
class IntelligenceCore(Base):
    """Core intelligence table - replaces campaign intelligence"""
    __tablename__ = "intelligence_core"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_name = Column(Text, nullable=False)
    source_url = Column(Text, nullable=False)
    confidence_score = Column(Float)
    analysis_method = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product_data = relationship("ProductData", back_populates="intelligence_core", uselist=False)
    market_data = relationship("MarketData", back_populates="intelligence_core", uselist=False)
    research_links = relationship("IntelligenceResearch", back_populates="intelligence")

class ProductData(Base):
    """Product-specific data"""
    __tablename__ = "product_data"
    
    intelligence_id = Column(UUID(as_uuid=True), ForeignKey("intelligence_core.id"), primary_key=True)
    features = Column(ARRAY(Text))
    benefits = Column(ARRAY(Text))
    ingredients = Column(ARRAY(Text))
    conditions = Column(ARRAY(Text))
    usage_instructions = Column(ARRAY(Text))
    
    # Relationships
    intelligence_core = relationship("IntelligenceCore", back_populates="product_data")

class MarketData(Base):
    """Market insights"""
    __tablename__ = "market_data"
    
    intelligence_id = Column(UUID(as_uuid=True), ForeignKey("intelligence_core.id"), primary_key=True)
    category = Column(Text)
    positioning = Column(Text)
    competitive_advantages = Column(ARRAY(Text))
    target_audience = Column(Text)
    
    # Relationships
    intelligence_core = relationship("IntelligenceCore", back_populates="market_data")

class KnowledgeBase(Base):
    """Centralized research knowledge"""
    __tablename__ = "knowledge_base"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_hash = Column(Text, unique=True, nullable=False)  # Added missing field
    content = Column(Text, nullable=False)
    research_type = Column(Text)  # 'clinical', 'market', 'ingredient'
    source_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    intelligence_links = relationship("IntelligenceResearch", back_populates="research")

class IntelligenceResearch(Base):
    """Link intelligence to research"""
    __tablename__ = "intelligence_research"
    
    intelligence_id = Column(UUID(as_uuid=True), ForeignKey("intelligence_core.id"), primary_key=True)
    research_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_base.id"), primary_key=True)
    relevance_score = Column(Float)
    
    # Relationships
    intelligence = relationship("IntelligenceCore", back_populates="research_links")
    research = relationship("KnowledgeBase", back_populates="intelligence_links")

class ScrapedContent(Base):
    """Content cache (deduplicated)"""
    __tablename__ = "scraped_content"
    
    url_hash = Column(Text, primary_key=True)
    url = Column(Text)
    content = Column(Text)
    title = Column(Text)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

# Updated GeneratedContent to work with new schema
class GeneratedContent(Base):
    """Generated content - updated to work with new intelligence schema"""
    __tablename__ = "generated_content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    
    # UPDATED: Link to new intelligence schema
    intelligence_id = Column(UUID(as_uuid=True), ForeignKey("intelligence_core.id", ondelete="SET NULL"))
    
    # Content basics
    content_type = Column(String(50), nullable=False)
    content_title = Column(String(500), nullable=False)
    content_body = Column(Text, nullable=False)
    content_metadata = Column(JSONB, default={})
    generation_settings = Column(JSONB, default={})
    intelligence_used = Column(JSONB, default={})
    
    # Performance tracking
    performance_data = Column(JSONB, default={})
    user_rating = Column(Integer)
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True))
    performance_score = Column(Float)
    view_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="generated_content")
    # UPDATED: Link to new intelligence schema
    intelligence_source = relationship("IntelligenceCore")

# Keep existing proactive analysis table (it's separate from intelligence)
class ProactiveAnalysisQueue(Base):
    """Queue for proactive analysis (separate from main intelligence)"""
    __tablename__ = "proactive_analysis_queue"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, unique=True, nullable=False)
    priority = Column(Integer, nullable=False)
    source = Column(String(50), nullable=False)
    metadata = Column(JSONB, default={})
    status = Column(String(20), default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Export models
__all__ = [
    'Base',
    'Company',
    'User', 
    'Campaign',
    'IntelligenceCore',        # NEW - replaces IntelligenceSourceType
    'ProductData',             # NEW - normalized product data
    'MarketData',              # NEW - normalized market data  
    'KnowledgeBase',           # NEW - centralized research
    'IntelligenceResearch',    # NEW - research links
    'ScrapedContent',          # NEW - content cache
    'GeneratedContent',        # UPDATED - links to new schema
    'ProactiveAnalysisQueue'   # EXISTING - separate table
]