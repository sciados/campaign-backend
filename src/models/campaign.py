"""
Campaign model - Clean best practice implementation
"""
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from src.models import BaseModel

class CampaignType(str, enum.Enum):
    SOCIAL_MEDIA = "social_media"
    EMAIL_MARKETING = "email_marketing"
    VIDEO_CONTENT = "video_content"
    BLOG_POST = "blog_post"
    ADVERTISEMENT = "advertisement"
    PRODUCT_LAUNCH = "product_launch"
    BRAND_AWARENESS = "brand_awareness"
    MULTIMEDIA = "multimedia"

class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class AssetType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    LOGO = "logo"
    SOCIAL_POST = "social_post"
    EMAIL_TEMPLATE = "email_template"
    BLOG_POST = "blog_post"
    AD_COPY = "ad_copy"

class Campaign(BaseModel):
    """Main campaign model"""
    __tablename__ = "campaigns"
    
    # Basic Information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    target_audience = Column(Text)
    campaign_type = Column(Enum(CampaignType), nullable=False)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # AI Generation Settings
    tone = Column(String(100))  # professional, casual, friendly, etc.
    style = Column(String(100))  # modern, classic, minimalist, etc.
    brand_voice = Column(Text)
    
    # Generated Content Storage
    content = Column(JSONB, default={})  # All generated text content
    settings = Column(JSONB, default={})  # Campaign configuration
    campaign_metadata = Column(JSONB, default={})  # Analytics and tracking data
    
    # Ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="campaigns")
    company = relationship("Company", back_populates="campaigns")
    assets = relationship("CampaignAsset", back_populates="campaign", cascade="all, delete-orphan")

class CampaignAsset(BaseModel):
    """Campaign asset model for storing generated files"""
    __tablename__ = "campaign_assets"
    
    # Asset Information
    asset_type = Column(Enum(AssetType), nullable=False)
    filename = Column(String(255))
    file_url = Column(Text)
    file_size = Column(Integer)  # in bytes
    
    # AI Generation Data
    prompt_used = Column(Text)
    generation_settings = Column(JSONB, default={})
    asset_metadata = Column(JSONB, default={})  # dimensions, duration, etc.
    
    # Relationships
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    campaign = relationship("Campaign", back_populates="assets")
    user = relationship("User")
    company = relationship("Company")