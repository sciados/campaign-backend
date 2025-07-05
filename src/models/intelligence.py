# src/models/intelligence.py - COMPLETE FIXED VERSION WITH PROPER COLUMNS
"""
Intelligence models - Extends existing campaign system with competitive intelligence
FIXED: Proper SQLAlchemy column definitions and enum serialization integration
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

# Import enum serializer mixin
from src.intelligence.utils.enum_serializer import EnumSerializerMixin
from src.models import BaseModel

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
    """
    Store extracted intelligence for campaigns
    
    FIXED: Proper SQLAlchemy column definitions with JSONB types
    ENHANCED: Includes enum serialization mixin for safe data access
    """
    __tablename__ = "campaign_intelligence"
    
    # Basic Information
    source_url = Column(Text)  # URL if from web source
    source_type = Column(Enum(IntelligenceSourceType, name='intelligence_source_type'), nullable=False)
    source_title = Column(String(500))
    analysis_status = Column(Enum(AnalysisStatus, name='analysis_status'), default=AnalysisStatus.PENDING)
    
    # 🔥 FIXED: Core Intelligence Data - Proper JSONB column definitions
    offer_intelligence = Column(JSONB, default={})
    psychology_intelligence = Column(JSONB, default={})
    content_intelligence = Column(JSONB, default={})
    competitive_intelligence = Column(JSONB, default={})
    brand_intelligence = Column(JSONB, default={})
    
    # 🔥 FIXED: AI Enhancement Intelligence Columns - Proper JSONB column definitions
    scientific_intelligence = Column(JSONB, default={})
    credibility_intelligence = Column(JSONB, default={})
    market_intelligence = Column(JSONB, default={})
    emotional_transformation_intelligence = Column(JSONB, default={})
    scientific_authority_intelligence = Column(JSONB, default={})
    
    # Performance Tracking
    confidence_score = Column(Float, default=0.0)  # 0-1 confidence in analysis
    usage_count = Column(Integer, default=0)  # How many times used for content generation
    success_rate = Column(Float, default=0.0)  # Performance of content generated from this intelligence
    
    # Raw Data Storage
    raw_content = Column(Text)  # Original extracted content
    processing_metadata = Column(JSONB, default={})  # Processing logs and settings
    
    # Foreign Keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Relationships - Use string references to avoid circular imports
    campaign = relationship("Campaign", back_populates="intelligence_sources")
    user = relationship("User", back_populates="intelligence_sources")
    company = relationship("Company", back_populates="intelligence_sources")
    generated_content = relationship("GeneratedContent", back_populates="intelligence_source")
    
    def get_core_intelligence(self) -> Dict[str, Any]:
        """
        Get all core intelligence data with proper enum serialization
        
        Returns:
            Dict containing all core intelligence categories as Python dicts
        """
        return {
            "offer_intelligence": self._serialize_enum_field(self.offer_intelligence),
            "psychology_intelligence": self._serialize_enum_field(self.psychology_intelligence),
            "content_intelligence": self._serialize_enum_field(self.content_intelligence),
            "competitive_intelligence": self._serialize_enum_field(self.competitive_intelligence),
            "brand_intelligence": self._serialize_enum_field(self.brand_intelligence),
        }
    
    def get_ai_intelligence(self) -> Dict[str, Any]:
        """
        Get all AI-enhanced intelligence data with proper enum serialization
        
        Returns:
            Dict containing all AI intelligence categories as Python dicts
        """
        return {
            "scientific_intelligence": self._serialize_enum_field(self.scientific_intelligence),
            "credibility_intelligence": self._serialize_enum_field(self.credibility_intelligence),
            "market_intelligence": self._serialize_enum_field(self.market_intelligence),
            "emotional_transformation_intelligence": self._serialize_enum_field(self.emotional_transformation_intelligence),
            "scientific_authority_intelligence": self._serialize_enum_field(self.scientific_authority_intelligence),
        }
    
    def get_all_intelligence(self) -> Dict[str, Any]:
        """
        Get all intelligence data (core + AI) with proper enum serialization
        
        Returns:
            Dict containing all intelligence categories as Python dicts
        """
        return {
            **self.get_core_intelligence(),
            **self.get_ai_intelligence(),
            "processing_metadata": self._serialize_enum_field(self.processing_metadata)
        }
    
    def is_amplified(self) -> bool:
        """
        Check if this intelligence source has been amplified with AI enhancements
        
        Returns:
            True if amplification has been applied
        """
        metadata = self._serialize_enum_field(self.processing_metadata)
        return metadata.get("amplification_applied", False)
    
    def get_amplification_summary(self) -> Dict[str, Any]:
        """
        Get summary of amplification status and quality
        
        Returns:
            Dict containing amplification metadata
        """
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
    """Track content generated from intelligence"""
    __tablename__ = "generated_content"
    
    # Content Information
    content_type = Column(String(50), nullable=False)
    title = Column(String(500))  # Fixed: was content_title
    content = Column(Text, nullable=False)  # Fixed: was content_body
    metadata = Column(JSONB, default={})  # Fixed: was content_metadata
    
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
    
    # Analysis Status (for content that gets analyzed)
    analysis_status = Column(String(20), default="pending")  # pending, completed, failed
    
    # Foreign Keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    intelligence_source_id = Column(UUID(as_uuid=True), ForeignKey("campaign_intelligence.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="generated_content")
    intelligence_source = relationship("CampaignIntelligence", back_populates="generated_content")
    user = relationship("User", back_populates="generated_content")
    company = relationship("Company", back_populates="generated_content")
    
    def get_generation_metadata(self) -> Dict[str, Any]:
        """Get generation metadata with proper serialization"""
        return {
            "generation_settings": self._serialize_enum_field(self.generation_settings),
            "intelligence_used": self._serialize_enum_field(self.intelligence_used),
            "metadata": self._serialize_enum_field(self.metadata),
            "performance_data": self._serialize_enum_field(self.performance_data)
        }

class SmartURL(BaseModel, EnumSerializerMixin):
    """Smart URL tracking for attribution"""
    __tablename__ = "smart_urls"
    
    # URL Information
    short_code = Column(String(50), unique=True, nullable=False)  # The unique short code
    original_url = Column(Text, nullable=False)
    tracking_url = Column(Text, nullable=False)  # Full tracking URL
    
    # Tracking Configuration
    tracking_parameters = Column(JSONB, default={})  # UTM and custom parameters
    expiration_date = Column(DateTime(timezone=True))  # Optional expiration
    is_active = Column(Boolean, default=True)
    
    # Analytics Data
    click_count = Column(Integer, default=0)
    unique_clicks = Column(Integer, default=0)
    conversion_count = Column(Integer, default=0)
    revenue_attributed = Column(Float, default=0.0)
    
    # Detailed Analytics (JSONB for flexibility)
    click_analytics = Column(JSONB, default={})  # Geographic, device, referrer data
    conversion_analytics = Column(JSONB, default={})  # Conversion tracking data
    
    # Foreign Keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    generated_content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="smart_urls")
    generated_content = relationship("GeneratedContent")
    user = relationship("User", back_populates="smart_urls")
    company = relationship("Company", back_populates="smart_urls")
    
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

# ============================================================================
# PYDANTIC MODELS FOR API REQUESTS/RESPONSES
# ============================================================================

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

class VSLAnalysisRequest(PydanticBaseModel):
    url: str = Field(..., description="URL containing video content")
    campaign_id: str = Field(..., description="Campaign ID")
    extract_transcript: bool = Field(
        default=True,
        description="Whether to extract video transcript"
    )
    analyze_psychological_hooks: bool = Field(
        default=True,
        description="Whether to analyze psychological hooks in the video"
    )

class CampaignAngleRequest(PydanticBaseModel):
    campaign_id: str = Field(..., description="Campaign ID")
    intelligence_sources: List[str] = Field(
        ..., 
        description="Array of intelligence IDs to base angles on"
    )
    target_audience: Optional[str] = Field(
        default=None,
        description="Specific target audience"
    )
    industry: Optional[str] = Field(
        default=None,
        description="Industry context"
    )
    tone_preferences: Optional[List[str]] = Field(
        default=None,
        description="Preferred tone and style"
    )
    unique_value_props: Optional[List[str]] = Field(
        default=None,
        description="Unique value propositions to emphasize"
    )
    avoid_angles: Optional[List[str]] = Field(
        default=None,
        description="Angles or approaches to avoid"
    )

class BatchAnalysisRequest(PydanticBaseModel):
    urls: List[str] = Field(..., description="List of URLs to analyze")
    campaign_id: str = Field(..., description="Campaign ID")
    analysis_type: Literal["quick", "detailed"] = Field(
        default="detailed",
        description="Type of analysis for each URL"
    )
    compare_results: bool = Field(
        default=True,
        description="Whether to generate comparative analysis"
    )

class URLValidationRequest(PydanticBaseModel):
    url: str = Field(..., description="URL to validate and pre-analyze")

# Enhanced Response Models with proper structure
class OfferAnalysis(PydanticBaseModel):
    primary_offer: str
    pricing_strategy: List[str]
    value_propositions: List[str]
    guarantees: List[str]
    bonuses: List[str]
    urgency_tactics: List[str]
    pricing_details: Optional[Dict[str, List[str]]] = None

class PsychologyAnalysis(PydanticBaseModel):
    emotional_triggers: List[str]
    persuasion_techniques: List[str]
    social_proof_elements: List[str]
    authority_indicators: List[str]
    scarcity_elements: List[str]
    cognitive_biases_used: List[str]

class ContentStrategy(PydanticBaseModel):
    headline_patterns: List[str]
    story_elements: List[str]
    objection_handling: List[str]
    call_to_action_analysis: List[str]
    content_flow: List[str]
    messaging_hierarchy: List[str]

class CompetitiveIntelligence(PydanticBaseModel):
    unique_differentiators: List[str]
    market_gaps: List[str]
    improvement_opportunities: List[str]
    competitive_advantages: List[str]
    weakness_analysis: List[str]

class VSLAnalysis(PydanticBaseModel):
    has_video: bool
    video_length_estimate: str
    video_type: Literal['vsl', 'demo', 'testimonial', 'other']
    transcript_available: bool
    key_video_elements: List[str]
    video_url: Optional[str] = None
    thumbnail_analysis: Optional[List[str]] = None

class CampaignAngles(PydanticBaseModel):
    primary_angle: str
    alternative_angles: List[str]
    positioning_strategy: str
    target_audience_insights: List[str]
    messaging_framework: List[str]
    differentiation_strategy: str

class ActionableInsights(PydanticBaseModel):
    immediate_opportunities: List[str]
    content_creation_ideas: List[str]
    campaign_strategies: List[str]
    testing_recommendations: List[str]
    implementation_priorities: List[str]

class TechnicalAnalysis(PydanticBaseModel):
    page_load_speed: str
    mobile_optimization: bool
    conversion_elements: List[str]
    trust_signals: List[str]
    checkout_analysis: Optional[List[str]] = None

class EnhancedSalesPageIntelligence(PydanticBaseModel):
    intelligence_id: str
    confidence_score: float
    source_url: str
    source_title: str
    analysis_timestamp: str
    offer_analysis: OfferAnalysis
    psychology_analysis: PsychologyAnalysis
    content_strategy: ContentStrategy
    competitive_intelligence: CompetitiveIntelligence
    vsl_analysis: Optional[VSLAnalysis] = None
    campaign_angles: CampaignAngles
    actionable_insights: ActionableInsights
    technical_analysis: Optional[TechnicalAnalysis] = None

# Additional response models for various endpoints
class IntelligenceSourceSummary(PydanticBaseModel):
    id: str
    source_url: str
    source_title: str
    confidence_score: float
    analysis_status: str
    amplified: bool
    created_at: str
    intelligence_categories: Dict[str, bool]
    ai_categories: Dict[str, bool]

class CampaignIntelligenceSummary(PydanticBaseModel):
    campaign_id: str
    total_sources: int
    amplified_sources: int
    average_confidence: float
    intelligence_sources: List[IntelligenceSourceSummary]
    amplification_status: Dict[str, Any]

class AmplificationRequest(PydanticBaseModel):
    intelligence_id: str
    preferences: Optional[Dict[str, Any]] = Field(
        default={},
        description="Amplification preferences and settings"
    )

class AmplificationResponse(PydanticBaseModel):
    intelligence_id: str
    amplification_applied: bool
    confidence_boost: float
    enhancements_applied: int
    ai_categories_populated: int
    message: str
    amplification_summary: Optional[Dict[str, Any]] = None