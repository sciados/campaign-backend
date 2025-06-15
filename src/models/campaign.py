"""
Campaign model and related schemas
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

class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Campaign(BaseModel):
    """Campaign model"""
    __tablename__ = "campaigns"
    
    # Basic Info
    title = Column(String(255), nullable=False)
    description = Column(Text)
    target_audience = Column(String(255))
    campaign_type = Column(Enum(CampaignType), nullable=False)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # AI Generation Settings
    tone = Column(String(100))  # professional, casual, friendly, etc.
    style = Column(String(100))  # modern, classic, minimalist, etc.
    brand_voice = Column(String(255))
    
    # Generated Content
    content = Column(JSONB)  # Store all generated content
    assets = Column(JSONB)   # Store asset metadata and URLs
    
    # Relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="campaigns")
    
    # Campaign Assets (separate table for better organization)
    campaign_assets = relationship("CampaignAsset", back_populates="campaign", cascade="all, delete-orphan")

class AssetType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    LOGO = "logo"
    SOCIAL_POST = "social_post"
    EMAIL_TEMPLATE = "email_template"

class CampaignAsset(BaseModel):
    """Campaign asset model"""
    __tablename__ = "campaign_assets"
    
    # Asset Info
    asset_type = Column(Enum(AssetType), nullable=False)
    filename = Column(String(255))
    file_url = Column(Text)
    file_size = Column(Integer)  # in bytes
    
    # AI Generation Metadata
    prompt_used = Column(Text)
    generation_settings = Column(JSONB)
    
    # Asset Data
    metadata = Column(JSONB)  # dimensions, duration, etc.
    
    # Relationships
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    campaign = relationship("Campaign", back_populates="campaign_assets")