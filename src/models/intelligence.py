# src/models/intelligence.py
"""
Intelligence models - Extends existing campaign system with competitive intelligence
"""
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from src.models import BaseModel

class IntelligenceSourceType(str, enum.Enum):
    SALES_PAGE = "sales_page"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    WEBSITE = "website"
    COMPETITOR_ANALYSIS = "competitor_analysis"

class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class CampaignIntelligence(BaseModel):
    """Store extracted intelligence for campaigns"""
    __tablename__ = "campaign_intelligence"
    
    # Basic Information
    source_url = Column(Text)  # URL if from web source
    source_type = Column(Enum(IntelligenceSourceType), nullable=False)
    source_title = Column(String(500))
    analysis_status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING)
    
    # Core Intelligence Data (JSONB for flexibility)
    offer_intelligence = Column(JSONB, default={})
    psychology_intelligence = Column(JSONB, default={})
    content_intelligence = Column(JSONB, default={})
    competitive_intelligence = Column(JSONB, default={})
    brand_intelligence = Column(JSONB, default={})
    
    # Performance Tracking
    confidence_score = Column(Float, default=0.0)  # 0-1 confidence in analysis
    usage_count = Column(Integer, default=0)  # How many times used for content generation
    success_rate = Column(Float, default=0.0)  # Performance of content generated from this intelligence
    
    # Raw Data Storage
    raw_content = Column(Text)  # Original extracted content
    processing_metadata = Column(JSONB, default={})  # Processing logs and settings
    
    # Relationships
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    campaign = relationship("Campaign", back_populates="intelligence_sources")
    user = relationship("User")
    company = relationship("Company")
    generated_content = relationship("GeneratedContent", back_populates="intelligence_source")

class GeneratedContent(BaseModel):
    """Track content generated from intelligence"""
    __tablename__ = "generated_content"
    
    # Content Information
    content_type = Column(String(100), nullable=False)  # email, social_post, ad_copy, etc.
    content_title = Column(String(500))
    content_body = Column(Text, nullable=False)
    content_metadata = Column(JSONB, default={})  # Additional content data
    
    # Generation Settings
    generation_prompt = Column(Text)  # AI prompt used
    generation_settings = Column(JSONB, default={})  # Tone, style, preferences
    intelligence_used = Column(JSONB, default={})  # Which intelligence data was used
    
    # Performance Tracking
    performance_data = Column(JSONB, default={})  # CTR, conversions, etc.
    user_rating = Column(Integer)  # 1-5 user rating
    is_published = Column(Boolean, default=False)
    published_at = Column(String(100))  # Where it was published
    
    # Relationships
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    intelligence_source_id = Column(UUID(as_uuid=True), ForeignKey("campaign_intelligence.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    campaign = relationship("Campaign")
    intelligence_source = relationship("CampaignIntelligence", back_populates="generated_content")
    user = relationship("User")
    company = relationship("Company")

class SmartURL(BaseModel):
    """Smart URL tracking for attribution"""
    __tablename__ = "smart_urls"
    
    # URL Information
    short_code = Column(String(50), unique=True, nullable=False)  # The unique short code
    original_url = Column(Text, nullable=False)
    tracking_url = Column(Text, nullable=False)  # Full tracking URL
    
    # Tracking Configuration
    tracking_parameters = Column(JSONB, default={})  # UTM and custom parameters
    expiration_date = Column(String(100))  # Optional expiration
    is_active = Column(Boolean, default=True)
    
    # Analytics Data
    click_count = Column(Integer, default=0)
    unique_clicks = Column(Integer, default=0)
    conversion_count = Column(Integer, default=0)
    revenue_attributed = Column(Float, default=0.0)
    
    # Detailed Analytics (JSONB for flexibility)
    click_analytics = Column(JSONB, default={})  # Geographic, device, referrer data
    conversion_analytics = Column(JSONB, default={})  # Conversion tracking data
    
    # Relationships
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    generated_content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    campaign = relationship("Campaign")
    generated_content = relationship("GeneratedContent")
    user = relationship("User")
    company = relationship("Company")

# Update existing Campaign model to include intelligence relationships
# Add this to your existing campaign.py file:

# In src/models/campaign.py, add these relationships to the Campaign class:
"""
# Add these relationships to your existing Campaign class:
intelligence_sources = relationship("CampaignIntelligence", back_populates="campaign", cascade="all, delete-orphan")
generated_content = relationship("GeneratedContent", back_populates="campaign", cascade="all, delete-orphan") 
smart_urls = relationship("SmartURL", back_populates="campaign", cascade="all, delete-orphan")

# Also add intelligence tracking to existing JSONB fields:
# In your existing content JSONB field, you can store:
# {
#   "intelligence_summary": {},  # Summary of all intelligence used
#   "generated_assets": [],      # List of generated content IDs
#   "performance_tracking": {},  # Overall campaign performance
#   "competitive_insights": {}   # Key insights driving strategy
# }
"""