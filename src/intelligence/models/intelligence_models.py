# =====================================
# File: src/intelligence/models/intelligence_models.py
# =====================================

"""
Data models for Intelligence Engine operations.

Provides Pydantic models for API requests, responses, and internal data structures
that work with the consolidated intelligence schema.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from src.core.shared.validators import validate_url


class AnalysisMethod(str, Enum):
    """Analysis method types."""
    FAST = "fast"
    DEEP = "deep"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


class IntelligenceRequest(BaseModel):
    """Request model for intelligence analysis."""

    salespage_url: str = Field(..., description="URL to analyze")
    analysis_method: AnalysisMethod = Field(
        default=AnalysisMethod.MAXIMUM,
        description="Analysis depth and method"
    )
    force_refresh: bool = Field(
        default=False,
        description="Force new analysis even if cached data exists"
    )
    campaign_id: Optional[str] = Field(
        default=None,
        description="Campaign ID to associate analysis with"
    )
    scrape_images: bool = Field(
        default=True,
        description="Automatically scrape product images from sales page"
    )

    @validator("salespage_url")
    def validate_source_url(cls, v):
        return validate_url(v, "salespage_url")


class ProductInfo(BaseModel):
    """Product information extracted from analysis."""
    
    features: List[str] = Field(default_factory=list, description="Product features")
    benefits: List[str] = Field(default_factory=list, description="Product benefits")
    ingredients: List[str] = Field(default_factory=list, description="Product ingredients")
    conditions: List[str] = Field(default_factory=list, description="Health conditions addressed")
    usage_instructions: List[str] = Field(default_factory=list, description="Usage instructions")


class MarketInfo(BaseModel):
    """Market and positioning information."""
    
    category: Optional[str] = Field(None, description="Product category")
    positioning: Optional[str] = Field(None, description="Market positioning")
    competitive_advantages: List[str] = Field(default_factory=list, description="Competitive advantages")
    target_audience: Optional[str] = Field(None, description="Target audience description")


class ResearchInfo(BaseModel):
    """Research and knowledge information."""
    
    research_id: str = Field(..., description="Knowledge base research ID")
    content: str = Field(..., description="Research content")
    research_type: str = Field(..., description="Type of research")
    relevance_score: float = Field(..., description="Relevance to intelligence")
    source_metadata: Dict[str, Any] = Field(default_factory=dict, description="Source information")


class AnalysisResult(BaseModel):
    """Complete analysis result."""
    
    intelligence_id: str = Field(..., description="Intelligence record ID")
    product_name: str = Field(..., description="Extracted product name")
    confidence_score: float = Field(..., description="Analysis confidence score")
    product_info: ProductInfo = Field(..., description="Product information")
    market_info: MarketInfo = Field(..., description="Market information") 
    research: List[ResearchInfo] = Field(default_factory=list, description="Related research")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")


class IntelligenceResponse(BaseModel):
    """Response model for intelligence operations."""

    success: bool = Field(True, description="Operation success status")
    response_type: str = Field("sync", description="Response type discriminator")
    intelligence_id: str = Field(..., description="Intelligence record ID")
    analysis_result: AnalysisResult = Field(..., description="Analysis results")
    cached: bool = Field(False, description="Whether result was from cache")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


class AsyncAnalysisResponse(BaseModel):
    """Response model for asynchronous analysis operations."""

    success: bool = Field(True, description="Operation success status")
    response_type: str = Field("async", description="Response type discriminator")
    analysis_id: str = Field(..., description="Analysis tracking ID")
    message: str = Field(..., description="Status message")