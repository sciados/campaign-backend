"""
Core Campaign Schemas - Following intelligence/schemas pattern
🔧 FIXED: Extracted from routes.py for better organization
"""
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class CampaignCreate(BaseModel):
    """Request model for campaign creation"""
    title: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = []
    target_audience: Optional[str] = None
    tone: Optional[str] = "conversational"
    style: Optional[str] = "modern"
    
    # Auto-Analysis Fields
    salespage_url: Optional[str] = None
    auto_analysis_enabled: Optional[bool] = True
    content_types: Optional[List[str]] = ["email", "social_post", "ad_copy"]
    content_tone: Optional[str] = "conversational"
    content_style: Optional[str] = "modern"
    generate_content_after_analysis: Optional[bool] = False
    
    settings: Optional[Dict[str, Any]] = {}

class CampaignUpdate(BaseModel):
    """Request model for campaign updates"""
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    target_audience: Optional[str] = None
    status: Optional[str] = None
    tone: Optional[str] = None
    style: Optional[str] = None
    salespage_url: Optional[str] = None
    auto_analysis_enabled: Optional[bool] = None
    content_types: Optional[List[str]] = None

class CampaignResponse(BaseModel):
    """Response model for campaigns"""
    id: str
    title: str
    description: Optional[str] = ""
    keywords: List[str] = []
    target_audience: Optional[str] = None
    campaign_type: str = "universal"
    status: str = "draft"
    tone: Optional[str] = "conversational"
    style: Optional[str] = "modern"
    created_at: datetime
    updated_at: datetime
    
    # Auto-Analysis Response Fields
    salespage_url: Optional[str] = None
    auto_analysis_enabled: bool = True
    auto_analysis_status: str = "pending"
    analysis_confidence_score: float = 0.0
    
    # Workflow fields
    workflow_state: str = "basic_setup"
    completion_percentage: float = 0.0
    sources_count: int = 0
    intelligence_count: int = 0
    content_count: int = 0
    total_steps: int = 2
    
    # Demo campaign indicator
    is_demo: bool = False

    class Config:
        from_attributes = True
        use_enum_values = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class WorkflowProgressData(BaseModel):
    """Request model for workflow progress updates"""
    workflow_state: Optional[str] = None
    completion_percentage: Optional[float] = None
    step_data: Optional[Dict[str, Any]] = {}
    auto_analysis_enabled: Optional[bool] = None
    generate_content_after_analysis: Optional[bool] = None