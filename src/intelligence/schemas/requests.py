"""
File: src/intelligence/schemas/requests.py
Request Schemas - Pydantic models for request validation
Extracted from main routes.py for better organization
"""
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional


class AnalyzeURLRequest(BaseModel):
    """Request model for URL analysis"""
    url: HttpUrl
    campaign_id: str
    analysis_type: str = "sales_page"


class GenerateContentRequest(BaseModel):
    """Request model for content generation"""
    intelligence_id: str
    content_type: str
    preferences: Dict[str, Any] = {}
    campaign_id: str


class UpdateContentRequest(BaseModel):
    """Request model for updating content"""
    content_title: Optional[str] = None
    content_body: Optional[str] = None
    content_metadata: Optional[Dict[str, Any]] = None
    user_rating: Optional[int] = None
    is_published: Optional[bool] = None
    published_at: Optional[str] = None
    performance_data: Optional[Dict[str, Any]] = None


class AmplificationRequest(BaseModel):
    """Request model for intelligence amplification"""
    intelligence_id: str
    preferences: Dict[str, Any] = {
        "enhance_scientific_backing": True,
        "boost_credibility": True,
        "competitive_analysis": True
    }


class ExportRequest(BaseModel):
    """Request model for data export"""
    campaign_id: str
    export_format: str = "json"
    include_content: bool = True
    include_intelligence: bool = True
    include_metadata: bool = True


class BulkAnalysisRequest(BaseModel):
    """Request model for bulk URL analysis"""
    urls: list[HttpUrl]
    campaign_id: str
    analysis_type: str = "sales_page"
    batch_size: int = 5


class ContentPreferencesRequest(BaseModel):
    """Request model for content generation preferences"""
    tone: Optional[str] = "professional"
    style: Optional[str] = "direct"
    length: Optional[str] = "medium"
    target_audience: Optional[str] = None
    include_statistics: bool = False
    include_testimonials: bool = True
    include_urgency: bool = False
    focus_benefits: bool = True
    focus_features: bool = False
    call_to_action_style: Optional[str] = "medium"
    personalization_level: Optional[str] = "medium"
    industry_focus: Optional[str] = None
    brand_voice: Optional[str] = None