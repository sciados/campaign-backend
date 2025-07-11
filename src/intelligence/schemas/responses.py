"""
File: src/intelligence/schemas/responses.py
Response Schemas - Pydantic models for API responses
✅ ENHANCED: Complete ultra-cheap AI support with all missing classes
"""
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime


# ✅ NEW: Missing classes that other routers need
class UltraCheapMetadata(BaseModel):
    """Metadata for ultra-cheap AI operations"""
    provider: str
    model_used: str
    cost_per_token: float
    total_tokens: int
    generation_cost: float
    estimated_openai_cost: float
    savings_amount: float
    cost_savings_percentage: str
    generation_time: float
    tokens_per_second: float
    provider_status: str = "active"


class GenerationMetadata(BaseModel):
    """Enhanced generation metadata for content creation"""
    generation_id: str
    content_type: str
    user_id: Optional[str] = None
    campaign_id: Optional[str] = None
    generation_method: str = "standard"
    ultra_cheap_ai_used: bool = False
    provider: Optional[str] = None
    model_used: Optional[str] = None
    generation_cost: float = 0.0
    estimated_openai_cost: float = 0.0
    savings_amount: float = 0.0
    cost_savings_percentage: str = "0%"
    generation_time: float = 0.0
    tokens_used: int = 0
    quality_score: Optional[float] = None
    generation_settings: Dict[str, Any] = {}
    timestamp: Optional[datetime] = None


class AnalysisResponse(BaseModel):
    """Response model for URL analysis"""
    intelligence_id: str
    analysis_status: str
    confidence_score: float
    offer_intelligence: Dict[str, Any]
    psychology_intelligence: Dict[str, Any]
    competitive_opportunities: List[Dict[str, Any]]
    campaign_suggestions: List[str]


class ContentGenerationResponse(BaseModel):
    """
    Response model for content generation
    ✅ ENHANCED: Complete ultra-cheap AI support with schema alignment
    """
    # ✅ EXISTING FIELDS (unchanged for backward compatibility)
    content_id: str
    content_type: str
    generated_content: Dict[str, Any]
    smart_url: Optional[str] = None
    performance_predictions: Dict[str, Any] = {}
    
    # ✅ ENHANCED: Ultra-cheap AI fields (optional for backward compatibility)
    ultra_cheap_ai_used: Optional[bool] = False
    cost_savings: Optional[str] = "0%"
    provider: Optional[str] = "unknown"
    generation_method: Optional[str] = "standard"
    generation_cost: Optional[float] = 0.0
    estimated_openai_cost: Optional[float] = 0.0
    savings_amount: Optional[float] = 0.0
    
    # ✅ ENHANCED: Detailed metadata
    intelligence_sources_used: Optional[int] = 0
    generation_metadata: Optional[Dict[str, Any]] = {}
    ultra_cheap_metadata: Optional[UltraCheapMetadata] = None
    
    # ✅ NEW: Performance tracking
    generation_time: Optional[float] = 0.0
    tokens_used: Optional[int] = 0
    quality_metrics: Optional[Dict[str, Any]] = {}


class IntelligenceSourceResponse(BaseModel):
    """Response model for intelligence source data"""
    id: str
    source_title: str
    source_url: str
    source_type: str
    confidence_score: float
    usage_count: int
    analysis_status: str
    created_at: Optional[str]
    updated_at: Optional[str]
    offer_intelligence: Dict[str, Any]
    psychology_intelligence: Dict[str, Any]
    content_intelligence: Dict[str, Any]
    competitive_intelligence: Dict[str, Any]
    brand_intelligence: Dict[str, Any]
    amplification_status: Dict[str, Any]


class ContentItemResponse(BaseModel):
    """
    Response model for content items
    ✅ ENHANCED: Complete ultra-cheap AI tracking
    """
    id: str
    content_type: str
    content_title: str
    created_at: Optional[str]
    updated_at: Optional[str]
    user_rating: Optional[int]
    is_published: bool
    published_at: Optional[str]
    performance_data: Dict[str, Any]
    content_metadata: Dict[str, Any]
    generation_settings: Dict[str, Any]
    intelligence_used: Dict[str, Any]
    amplification_context: Dict[str, Any]
    
    # ✅ ENHANCED: Ultra-cheap AI tracking
    ultra_cheap_ai_used: Optional[bool] = False
    generation_metadata: Optional[GenerationMetadata] = None


class CampaignIntelligenceResponse(BaseModel):
    """Response model for campaign intelligence overview"""
    campaign_id: str
    intelligence_sources: List[IntelligenceSourceResponse]
    generated_content: List[ContentItemResponse]
    summary: Dict[str, Any]


class AmplificationResponse(BaseModel):
    """Response model for intelligence amplification"""
    intelligence_id: str
    amplification_applied: bool
    confidence_boost: float
    scientific_enhancements: int
    credibility_score: float
    total_enhancements: int
    amplification_metadata: Dict[str, Any]


class SystemStatusResponse(BaseModel):
    """
    Response model for system status
    ✅ ENHANCED: Complete ultra-cheap AI monitoring
    """
    system_health: Dict[str, str]
    detailed_status: Dict[str, Any]
    recommendations: List[str]
    
    # ✅ ENHANCED: Ultra-cheap AI system status
    ultra_cheap_ai_status: Optional[str] = "unknown"
    generators: Optional[Dict[str, Dict[str, Any]]] = {}
    cost_analysis: Optional[Dict[str, Any]] = {}
    monthly_projections: Optional[Dict[str, Any]] = {}


class ContentTypesResponse(BaseModel):
    """
    Response model for available content types
    ✅ ENHANCED: Complete ultra-cheap AI capabilities info
    """
    available_content_types: List[str]
    total_available: int
    capabilities: Dict[str, Any]
    factory_available: bool
    status: str
    
    # ✅ ENHANCED: Ultra-cheap AI info
    ultra_cheap_ai: Optional[bool] = False
    cost_savings: Optional[str] = "0%"
    ultra_cheap_providers: Optional[List[str]] = []


class ExportResponse(BaseModel):
    """Response model for data export"""
    export_id: str
    export_format: str
    file_size: int
    download_url: Optional[str]
    exported_at: str
    includes: Dict[str, bool]


class BulkAnalysisResponse(BaseModel):
    """Response model for bulk analysis"""
    batch_id: str
    total_urls: int
    processed_urls: int
    successful_analyses: int
    failed_analyses: int
    results: List[AnalysisResponse]
    batch_status: str


class StatisticsResponse(BaseModel):
    """Response model for campaign statistics"""
    campaign_id: str
    intelligence_statistics: Dict[str, Any]
    content_statistics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    trends: Dict[str, Any]


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    service: str
    version: str
    timestamp: Optional[str] = None


class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str
    detail: str
    error_code: Optional[str] = None
    timestamp: Optional[str] = None
    request_id: Optional[str] = None


# ✅ ENHANCED: Ultra-cheap AI specific responses
class UltraCheapStatusResponse(BaseModel):
    """Response model for ultra-cheap AI status"""
    ultra_cheap_ai_status: str
    generators: Dict[str, Dict[str, Any]]
    cost_analysis: Dict[str, Any]
    monthly_projections: Dict[str, Any]
    provider_health: Dict[str, str]
    cost_savings_today: float
    total_tokens_saved: int


class ContentListResponse(BaseModel):
    """Response model for content list with ultra-cheap AI stats"""
    campaign_id: str
    total_content: int
    content_items: List[Dict[str, Any]]
    ultra_cheap_stats: Optional[Dict[str, Any]] = {}
    cost_summary: Optional[Dict[str, Any]] = {}


class ContentDetailResponse(BaseModel):
    """Response model for detailed content view with ultra-cheap AI info"""
    id: str
    campaign_id: str
    content_type: str
    content_title: str
    content_body: str
    parsed_content: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    ultra_cheap_info: Optional[Dict[str, Any]] = {}
    generation_metadata: Optional[GenerationMetadata] = None


# ✅ NEW: Additional helper responses for better organization
class CostAnalysisResponse(BaseModel):
    """Response model for cost analysis"""
    total_savings: float
    cost_breakdown: Dict[str, float]
    provider_comparison: Dict[str, Dict[str, Any]]
    monthly_projection: Dict[str, float]
    efficiency_metrics: Dict[str, Any]


class ProviderStatusResponse(BaseModel):
    """Response model for provider status"""
    provider_name: str
    status: str
    response_time: float
    cost_per_token: float
    rate_limit_status: Dict[str, Any]
    quality_score: float
    last_used: Optional[str] = None