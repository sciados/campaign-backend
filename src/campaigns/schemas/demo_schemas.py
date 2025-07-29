"""
Demo Campaign Schemas - Following intelligence/schemas pattern
🎯 NEW: User preference system for demo campaign visibility control
"""
from pydantic import BaseModel
from typing import Dict, Any, Optional

class DemoPreferenceUpdate(BaseModel):
    """Request model for updating demo preferences"""
    show_demo_campaigns: bool

class DemoPreferenceResponse(BaseModel):
    """Response model for demo preferences"""
    show_demo_campaigns: bool
    demo_available: bool
    real_campaigns_count: int
    demo_campaigns_count: int

class DemoCreationRequest(BaseModel):
    """Request model for demo creation"""
    demo_type: str = "instant"  # "instant" or "live_analysis"
    competitor_url: Optional[str] = "https://mailchimp.com"

class DemoCreationResponse(BaseModel):
    """Response model for demo creation"""
    success: bool
    message: str
    demo_campaign: Dict[str, Any]
    frontend_instructions: Dict[str, Any]
    meta: Optional[Dict[str, Any]] = {}