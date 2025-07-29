"""
Workflow Schemas - Following intelligence/schemas pattern
🎯 NEW: 2-step workflow state management
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class WorkflowStateResponse(BaseModel):
    """Response model for workflow state"""
    campaign_id: str
    workflow_state: str
    completion_percentage: float
    total_steps: int
    current_step: int
    
    # Progress metrics
    metrics: Dict[str, int]
    
    # Auto-analysis info
    auto_analysis: Dict[str, Any]
    
    # Next recommended actions
    next_steps: List[Dict[str, Any]]
    
    # Workflow capabilities
    can_analyze: bool
    can_generate_content: bool
    is_demo: bool
    
    # Step states
    step_states: Dict[str, Any]
    
    # Timestamps
    created_at: str
    updated_at: str

class AnalysisProgressResponse(BaseModel):
    """Response model for analysis progress"""
    campaign_id: str
    analysis_status: str
    completion_percentage: float
    analysis_started_at: Optional[str] = None
    analysis_completed_at: Optional[str] = None
    error_message: Optional[str] = None
    analysis_results: Dict[str, Any] = {}
    is_demo: bool
    continue_polling: bool
    next_poll_in_seconds: Optional[int] = None

class CampaignIntelligenceResponse(BaseModel):
    """Response model for campaign intelligence"""
    campaign_id: str
    intelligence_entries: List[Dict[str, Any]]
    pagination: Dict[str, Any]
    summary: Dict[str, Any]
    is_demo: bool

class WorkflowProgressData(BaseModel):
    """Data for saving workflow progress - ADDED MISSING SCHEMA"""
    workflow_state: Optional[str] = None
    completion_percentage: Optional[float] = None
    step_data: Optional[Dict[str, Any]] = None
    auto_analysis_enabled: Optional[bool] = None
    generate_content_after_analysis: Optional[bool] = None
    
    class Config:
        validate_by_name = True  # Updated for Pydantic V2