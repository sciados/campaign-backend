# src/models/intelligence.py - COMPLETE FIXED VERSION
"""
Intelligence models - Extends existing campaign system with competitive intelligence - FIXED RELATIONSHIPS
"""
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from pydantic import BaseModel as PydanticBaseModel, Field
from typing import List, Optional, Dict, Any, Literal

from src.models import BaseModel

class IntelligenceSourceType(str, enum.Enum):
    SALES_PAGE = "SALES_PAGE"
    DOCUMENT = "DOCUMENT"
    VIDEO = "VIDEO"
    WEBSITE = "WEBSITE"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"           # ← New
    COMPETITOR_AD = "COMPETITOR_AD" 

class AnalysisStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class CampaignIntelligence(BaseModel):
    """Store extracted intelligence for campaigns"""
    __tablename__ = "campaign_intelligence"
    
    # Basic Information
    source_url = Column(Text)  # URL if from web source
    source_type = Column(Enum(IntelligenceSourceType, name='intelligence_source_type'), nullable=False)
    source_title = Column(String(500))
    analysis_status = Column(Enum(AnalysisStatus, name='analysis_status'), default=AnalysisStatus.PENDING)
    
    
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
    
    # Foreign Keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Relationships - Use string references to avoid circular imports
    campaign = relationship("Campaign", back_populates="intelligence_sources")
    user = relationship("User", back_populates="intelligence_sources")
    company = relationship("Company", back_populates="intelligence_sources")
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
    
    # Foreign Keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    intelligence_source_id = Column(UUID(as_uuid=True), ForeignKey("campaign_intelligence.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Relationships - Use string references to avoid circular imports
    campaign = relationship("Campaign", back_populates="generated_content")
    intelligence_source = relationship("CampaignIntelligence", back_populates="generated_content")
    user = relationship("User", back_populates="generated_content")
    company = relationship("Company", back_populates="generated_content")

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
    
    # Foreign Keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    generated_content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Relationships - Use string references to avoid circular imports
    campaign = relationship("Campaign", back_populates="smart_urls")
    generated_content = relationship("GeneratedContent")
    user = relationship("User", back_populates="smart_urls")
    company = relationship("Company", back_populates="smart_urls")

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

# Enhanced Response Models
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

class VSLKeyMoment(PydanticBaseModel):
    timestamp: str
    description: str
    importance_score: float

class VSLOfferMention(PydanticBaseModel):
    timestamp: str
    offer_details: str

class VSLCallToAction(PydanticBaseModel):
    timestamp: str
    cta_text: str
    urgency_level: Literal['low', 'medium', 'high']

class VSLTranscriptionResult(PydanticBaseModel):
    transcript_id: str
    video_url: str
    transcript_text: str
    key_moments: List[VSLKeyMoment]
    psychological_hooks: List[str]
    offer_mentions: List[VSLOfferMention]
    call_to_actions: List[VSLCallToAction]

class PrimaryAngle(PydanticBaseModel):
    angle: str
    reasoning: str
    target_audience: str
    key_messages: List[str]
    differentiation_points: List[str]

class AlternativeAngle(PydanticBaseModel):
    angle: str
    reasoning: str
    strength_score: float
    use_case: str

class PositioningStrategy(PydanticBaseModel):
    market_position: str
    competitive_advantage: str
    value_proposition: str
    messaging_framework: List[str]

class ImplementationGuide(PydanticBaseModel):
    content_priorities: List[str]
    channel_recommendations: List[str]
    testing_suggestions: List[str]

class CampaignAngleResponse(PydanticBaseModel):
    primary_angle: PrimaryAngle
    alternative_angles: List[AlternativeAngle]
    positioning_strategy: PositioningStrategy
    implementation_guide: ImplementationGuide

class ConsolidatedIntelligence(PydanticBaseModel):
    top_opportunities: List[str]
    consistent_patterns: List[str]
    conflicting_insights: List[str]
    confidence_weighted_insights: Dict[str, Any]

class SourceComparison(PydanticBaseModel):
    intelligence_id: str
    source_url: str
    key_insights: List[str]
    confidence_score: float

class RecommendedStrategy(PydanticBaseModel):
    primary_positioning: str
    messaging_pillars: List[str]
    content_recommendations: List[str]
    testing_priorities: List[str]

class MultiSourceIntelligence(PydanticBaseModel):
    campaign_id: str
    consolidated_intelligence: ConsolidatedIntelligence
    source_comparison: List[SourceComparison]
    recommended_campaign_strategy: RecommendedStrategy

class UniqueApproach(PydanticBaseModel):
    url: str
    unique_elements: List[str]

class OpportunityMatrix(PydanticBaseModel):
    opportunity: str
    difficulty: Literal['low', 'medium', 'high']
    impact: Literal['low', 'medium', 'high']

class ComparativeAnalysis(PydanticBaseModel):
    common_strategies: List[str]
    unique_approaches: List[UniqueApproach]
    market_gaps: List[str]
    opportunity_matrix: List[OpportunityMatrix]

class BatchAnalysisResponse(PydanticBaseModel):
    analyses: List[EnhancedSalesPageIntelligence]
    comparative_analysis: ComparativeAnalysis

class AnalysisReadiness(PydanticBaseModel):
    content_extractable: bool
    video_detected: bool
    estimated_analysis_time: str
    confidence_prediction: float

class AnalysisRecommendations(PydanticBaseModel):
    recommended_analysis_type: str
    expected_insights: List[str]
    potential_limitations: List[str]

class URLValidationResponse(PydanticBaseModel):
    is_valid: bool
    is_accessible: bool
    page_type: Literal['sales_page', 'landing_page', 'website', 'blog', 'social', 'unknown']
    analysis_readiness: AnalysisReadiness
    optimization_suggestions: List[str]
    analysis_recommendations: AnalysisRecommendations

class ConsolidateIntelligenceRequest(PydanticBaseModel):
    campaign_id: str = Field(..., description="Campaign ID to consolidate intelligence for")
    weight_by_confidence: bool = Field(
        default=True,
        description="Whether to weight insights by confidence scores"
    )
    include_conflicting_insights: bool = Field(
        default=True,
        description="Whether to include conflicting insights in analysis"
    )
    generate_unified_strategy: bool = Field(
        default=True,
        description="Whether to generate unified campaign strategy"
    )

class IntelligenceConsolidationResponse(PydanticBaseModel):
    campaign_id: str
    total_sources: int
    confidence_weighted_score: float
    top_insights: List[str]
    common_patterns: List[str]
    conflicting_insights: List[str]
    recommended_actions: List[str]
    unified_strategy: Optional[Dict[str, Any]] = None

class ExportReportRequest(PydanticBaseModel):
    campaign_id: str = Field(..., description="Campaign ID to export")
    format: Literal['pdf', 'excel', 'json', 'presentation'] = Field(
        default='pdf',
        description="Export format"
    )
    sections: Optional[List[str]] = Field(
        default=None,
        description="Specific sections to include in export"
    )
    include_recommendations: bool = Field(
        default=True,
        description="Whether to include actionable recommendations"
    )
    include_visuals: bool = Field(
        default=True,
        description="Whether to include charts and visualizations"
    )

class ExportReportResponse(PydanticBaseModel):
    download_url: str
    expires_at: str
    file_size: int
    format: str
    sections_included: List[str]