"""
File: src/intelligence/schemas/responses.py
Response Schemas - Pydantic models for API responses
Extracted from main routes.py for better organization
"""
from pydantic import BaseModel
from typing import Dict, Any, List, Optional


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
    """Response model for content generation"""
    content_id: str
    content_type: str
    generated_content: Dict[str, Any]
    smart_url: Optional[str] = None
    performance_predictions: Dict[str, Any]


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
    """Response model for content items"""
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
    """Response model for system status"""
    system_health: Dict[str, str]
    detailed_status: Dict[str, Any]
    recommendations: List[str]


class ContentTypesResponse(BaseModel):
    """Response model for available content types"""
    available_content_types: List[str]
    total_available: int
    capabilities: Dict[str, Any]
    factory_available: bool
    status: str


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