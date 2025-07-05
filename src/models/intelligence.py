# src/models/intelligence.py - FINAL FIX for reserved 'metadata' column name
"""
Intelligence models - FINAL FIX to resolve SQLAlchemy reserved attribute error
"""
import json
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Integer, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from pydantic import BaseModel as PydanticBaseModel, Field
from typing import List, Optional, Dict, Any, Literal

# EMERGENCY FIX: Import BaseModel directly from the module to avoid circular imports
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4

# Create our own base to avoid circular imports
Base = declarative_base()

class BaseModel(Base):
    """Emergency base model to avoid circular imports"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# EMERGENCY FIX: Create a simple enum serializer here to avoid imports
class EnumSerializerMixin:
    """Simple enum serializer to avoid import issues"""
    
    def _serialize_enum_field(self, field_value):
        """Serialize enum field to proper format"""
        if field_value is None:
            return {}
        
        if isinstance(field_value, dict):
            return field_value
        
        if isinstance(field_value, str):
            try:
                return json.loads(field_value)
            except (json.JSONDecodeError, ValueError):
                return {}
        
        return {}

class IntelligenceSourceType(str, enum.Enum):
    SALES_PAGE = "SALES_PAGE"
    DOCUMENT = "DOCUMENT"
    VIDEO = "VIDEO"
    WEBSITE = "WEBSITE"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    COMPETITOR_AD = "COMPETITOR_AD"

class AnalysisStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class CampaignIntelligence(BaseModel, EnumSerializerMixin):
    """Store extracted intelligence for campaigns - EMERGENCY FIX VERSION"""
    __tablename__ = "campaign_intelligence"
    
    # Basic Information
    source_url = Column(Text)
    source_type = Column(Enum(IntelligenceSourceType, name='intelligence_source_type'), nullable=False)
    source_title = Column(String(500))
    analysis_status = Column(Enum(AnalysisStatus, name='analysis_status'), default=AnalysisStatus.PENDING)
    
    # Core Intelligence Data - JSONB columns
    offer_intelligence = Column(JSONB, default={})
    psychology_intelligence = Column(JSONB, default={})
    content_intelligence = Column(JSONB, default={})
    competitive_intelligence = Column(JSONB, default={})
    brand_intelligence = Column(JSONB, default={})
    
    # AI Enhancement Intelligence Columns - JSONB columns
    scientific_intelligence = Column(JSONB, default={})
    credibility_intelligence = Column(JSONB, default={})
    market_intelligence = Column(JSONB, default={})
    emotional_transformation_intelligence = Column(JSONB, default={})
    scientific_authority_intelligence = Column(JSONB, default={})
    
    # Performance Tracking
    confidence_score = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Raw Data Storage
    raw_content = Column(Text)
    processing_metadata = Column(JSONB, default={})
    
    # Foreign Keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # EMERGENCY FIX: Remove relationships to avoid circular imports
    # Relationships will be defined elsewhere if needed
    
    def get_core_intelligence(self) -> Dict[str, Any]:
        """Get all core intelligence data with proper enum serialization"""
        return {
            "offer_intelligence": self._serialize_enum_field(self.offer_intelligence),
            "psychology_intelligence": self._serialize_enum_field(self.psychology_intelligence),
            "content_intelligence": self._serialize_enum_field(self.content_intelligence),
            "competitive_intelligence": self._serialize_enum_field(self.competitive_intelligence),
            "brand_intelligence": self._serialize_enum_field(self.brand_intelligence),
        }
    
    def get_ai_intelligence(self) -> Dict[str, Any]:
        """Get all AI-enhanced intelligence data with proper enum serialization"""
        return {
            "scientific_intelligence": self._serialize_enum_field(self.scientific_intelligence),
            "credibility_intelligence": self._serialize_enum_field(self.credibility_intelligence),
            "market_intelligence": self._serialize_enum_field(self.market_intelligence),
            "emotional_transformation_intelligence": self._serialize_enum_field(self.emotional_transformation_intelligence),
            "scientific_authority_intelligence": self._serialize_enum_field(self.scientific_authority_intelligence),
        }
    
    def get_all_intelligence(self) -> Dict[str, Any]:
        """Get all intelligence data (core + AI) with proper enum serialization"""
        return {
            **self.get_core_intelligence(),
            **self.get_ai_intelligence(),
            "processing_metadata": self._serialize_enum_field(self.processing_metadata)
        }
    
    def is_amplified(self) -> bool:
        """Check if this intelligence source has been amplified with AI enhancements"""
        metadata = self._serialize_enum_field(self.processing_metadata)
        return metadata.get("amplification_applied", False)
    
    def get_amplification_summary(self) -> Dict[str, Any]:
        """Get summary of amplification status and quality"""
        metadata = self._serialize_enum_field(self.processing_metadata)
        
        if not self.is_amplified():
            return {
                "amplified": False,
                "amplification_available": True,
                "message": "Intelligence source ready for AI amplification"
            }
        
        return {
            "amplified": True,
            "amplified_at": metadata.get("amplification_timestamp", "Unknown"),
            "confidence_boost": metadata.get("confidence_boost", 0.0),
            "total_enhancements": metadata.get("total_enhancements", 0),
            "enhancement_quality": metadata.get("enhancement_quality", "unknown"),
            "ai_categories_populated": self._count_ai_categories(),
            "amplification_method": metadata.get("amplification_method", "unknown")
        }
    
    def _count_ai_categories(self) -> int:
        """Count how many AI intelligence categories have data"""
        ai_data = self.get_ai_intelligence()
        return sum(1 for category_data in ai_data.values() if category_data and len(category_data) > 0)

class GeneratedContent(BaseModel, EnumSerializerMixin):
    """Track content generated from intelligence - FINAL FIX VERSION"""
    __tablename__ = "generated_content"
    
    # Content Information
    content_type = Column(String(50), nullable=False)
    title = Column(String(500))
    content = Column(Text, nullable=False)
    content_metadata = Column(JSONB, default={})  # 🔥 FIXED: Renamed from 'metadata' to 'content_metadata'
    
    # Generation Settings
    generation_prompt = Column(Text)
    generation_settings = Column(JSONB, default={})
    intelligence_used = Column(JSONB, default={})
    
    # Performance Tracking
    performance_data = Column(JSONB, default={})
    user_rating = Column(Integer)
    is_published = Column(Boolean, default=False)
    
    # Publishing Information
    published_at = Column(DateTime(timezone=True), nullable=True)
    published_to = Column(String(200), nullable=True)
    
    # Analysis Status
    analysis_status = Column(String(20), default="pending")
    
    # Foreign Keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    intelligence_source_id = Column(UUID(as_uuid=True), ForeignKey("campaign_intelligence.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # EMERGENCY FIX: Remove relationships to avoid circular imports
    
    def get_generation_metadata(self) -> Dict[str, Any]:
        """Get generation metadata with proper serialization"""
        return {
            "generation_settings": self._serialize_enum_field(self.generation_settings),
            "intelligence_used": self._serialize_enum_field(self.intelligence_used),
            "content_metadata": self._serialize_enum_field(self.content_metadata),  # 🔥 FIXED: Updated reference
            "performance_data": self._serialize_enum_field(self.performance_data)
        }

class SmartURL(BaseModel, EnumSerializerMixin):
    """Smart URL tracking for attribution - EMERGENCY FIX VERSION"""
    __tablename__ = "smart_urls"
    
    # URL Information
    short_code = Column(String(50), unique=True, nullable=False)
    original_url = Column(Text, nullable=False)
    tracking_url = Column(Text, nullable=False)
    
    # Tracking Configuration
    tracking_parameters = Column(JSONB, default={})
    expiration_date = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Analytics Data
    click_count = Column(Integer, default=0)
    unique_clicks = Column(Integer, default=0)
    conversion_count = Column(Integer, default=0)
    revenue_attributed = Column(Float, default=0.0)
    
    # Detailed Analytics
    click_analytics = Column(JSONB, default={})
    conversion_analytics = Column(JSONB, default={})
    
    # Foreign Keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    generated_content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # EMERGENCY FIX: Remove relationships to avoid circular imports
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics data with proper serialization"""
        return {
            "tracking_parameters": self._serialize_enum_field(self.tracking_parameters),
            "click_analytics": self._serialize_enum_field(self.click_analytics),
            "conversion_analytics": self._serialize_enum_field(self.conversion_analytics),
            "performance_summary": {
                "click_count": self.click_count,
                "unique_clicks": self.unique_clicks,
                "conversion_count": self.conversion_count,
                "revenue_attributed": self.revenue_attributed,
                "conversion_rate": (self.conversion_count / self.click_count * 100) if self.click_count > 0 else 0
            }
        }

# Minimal Pydantic models for production compatibility
class EnhancedAnalysisRequest(PydanticBaseModel):
    url: str = Field(..., description="URL to analyze")
    campaign_id: str = Field(..., description="Campaign ID")
    analysis_depth: Literal["basic", "comprehensive", "competitive"] = Field(
        default="comprehensive", 
        description="Depth of analysis"
    )
    include_vsl_detection: bool = Field(
        default=True, 
        description="Whether to detect and analyze video sales letters"
    )
    custom_analysis_points: Optional[List[str]] = Field(
        default=None,
        description="Custom analysis focus points"
    )