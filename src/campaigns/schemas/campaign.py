# src/campaigns/schemas/campaign.py

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

class CampaignStatusEnum(str, Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class CampaignTypeEnum(str, Enum):
    """Campaign type enumeration"""
    EMAIL_SEQUENCE = "email_sequence"
    SOCIAL_MEDIA = "social_media"
    CONTENT_MARKETING = "content_marketing"
    AFFILIATE_PROMOTION = "affiliate_promotion"
    PRODUCT_LAUNCH = "product_launch"

class CampaignWorkflowStateEnum(str, Enum):
    """Campaign workflow state enumeration"""
    INITIAL = "INITIAL"
    ANALYZING = "ANALYZING"
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"
    GENERATING_CONTENT = "GENERATING_CONTENT"
    CONTENT_READY = "CONTENT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    DEPLOYED = "DEPLOYED"
    MONITORING = "MONITORING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"

# ============================================================================
# BASE SCHEMAS
# ============================================================================

class CampaignBase(BaseModel):
    """Base campaign schema"""
    title: str = Field(..., min_length=1, max_length=255, description="Campaign title")
    description: Optional[str] = Field(None, max_length=2000, description="Campaign description")
    campaign_type: CampaignTypeEnum = Field(..., description="Type of campaign")
    target_audience: Optional[str] = Field(None, max_length=1000, description="Target audience description")
    goals: Optional[List[str]] = Field(default_factory=list, description="Campaign goals")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Campaign settings")

class CampaignCreate(CampaignBase):
    """Schema for creating a new campaign"""
    pass

class CampaignUpdate(BaseModel):
    """Schema for updating a campaign"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    target_audience: Optional[str] = Field(None, max_length=1000)
    goals: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class CampaignWorkflowProgress(BaseModel):
    """Campaign workflow progress schema"""
    current_step: int = Field(default=0, description="Current workflow step")
    current_state: str = Field(default="INITIAL", description="Current workflow state")
    completion_percentage: int = Field(default=0, ge=0, le=100, description="Completion percentage")
    is_complete: bool = Field(default=False, description="Whether workflow is complete")
    auto_analysis_status: str = Field(default="PENDING", description="Auto analysis status")

class CampaignCounters(BaseModel):
    """Campaign counters schema"""
    sources: int = Field(default=0, ge=0, description="Number of sources")
    intelligence: int = Field(default=0, ge=0, description="Intelligence count")
    content: int = Field(default=0, ge=0, description="Generated content count")

class CampaignPerformanceMetrics(BaseModel):
    """Campaign performance metrics schema"""
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    conversions: int = Field(default=0, ge=0)
    revenue: float = Field(default=0.0, ge=0.0, description="Revenue in dollars")
    ctr: float = Field(default=0.0, ge=0.0, le=100.0, description="Click-through rate percentage")
    conversion_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Conversion rate percentage")
    roas: float = Field(default=0.0, ge=0.0, description="Return on ad spend")

class CampaignResponse(BaseModel):
    """Complete campaign response schema"""
    id: str = Field(..., description="Campaign ID")
    title: str = Field(..., description="Campaign title")
    name: Optional[str] = Field(None, description="Campaign name (legacy)")
    display_name: str = Field(..., description="Display name")
    description: Optional[str] = Field(None, description="Campaign description")
    campaign_type: str = Field(..., description="Campaign type")
    status: str = Field(..., description="Campaign status")
    user_id: str = Field(..., description="User ID")
    company_id: str = Field(..., description="Company ID")
    target_audience: Optional[str] = Field(None, description="Target audience")
    goals: Optional[List[str]] = Field(default_factory=list, description="Campaign goals")
    workflow: CampaignWorkflowProgress = Field(..., description="Workflow progress")
    counters: CampaignCounters = Field(..., description="Campaign counters")
    intelligence_status: str = Field(default="pending", description="Intelligence status")
    performance: CampaignPerformanceMetrics = Field(..., description="Performance metrics")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    launched_at: Optional[str] = Field(None, description="Launch timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")

    class Config:
        from_attributes = True

# ============================================================================
# LIST AND PAGINATION SCHEMAS
# ============================================================================

class CampaignListResponse(BaseModel):
    """Campaign list response schema"""
    campaigns: List[CampaignResponse] = Field(..., description="List of campaigns")
    total: int = Field(..., ge=0, description="Total number of campaigns")
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, description="Items per page")
    has_next: bool = Field(default=False, description="Whether there are more pages")
    has_prev: bool = Field(default=False, description="Whether there are previous pages")

    @validator('has_next')
    def validate_has_next(cls, v, values):
        if 'total' in values and 'page' in values and 'per_page' in values:
            total_pages = (values['total'] + values['per_page'] - 1) // values['per_page']
            return values['page'] < total_pages
        return v

    @validator('has_prev')
    def validate_has_prev(cls, v, values):
        if 'page' in values:
            return values['page'] > 1
        return v

# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class CampaignStatusBreakdown(BaseModel):
    """Campaign status breakdown schema"""
    draft: int = Field(default=0, ge=0)
    active: int = Field(default=0, ge=0)
    paused: int = Field(default=0, ge=0)
    completed: int = Field(default=0, ge=0)
    archived: int = Field(default=0, ge=0)

class CampaignTypeBreakdown(BaseModel):
    """Campaign type breakdown schema"""
    email_sequence: int = Field(default=0, ge=0)
    social_media: int = Field(default=0, ge=0)
    content_marketing: int = Field(default=0, ge=0)
    affiliate_promotion: int = Field(default=0, ge=0)
    product_launch: int = Field(default=0, ge=0)

class CampaignStatsResponse(BaseModel):
    """Campaign statistics response schema"""
    total_campaigns: int = Field(..., ge=0, description="Total number of campaigns")
    active_campaigns: int = Field(..., ge=0, description="Number of active campaigns")
    completed_campaigns: int = Field(..., ge=0, description="Number of completed campaigns")
    draft_campaigns: int = Field(..., ge=0, description="Number of draft campaigns")
    recent_campaigns: int = Field(default=0, ge=0, description="Recent campaigns (last 30 days)")
    completion_rate: float = Field(..., ge=0.0, le=100.0, description="Campaign completion rate")
    status_breakdown: CampaignStatusBreakdown = Field(..., description="Breakdown by status")
    campaign_types: CampaignTypeBreakdown = Field(..., description="Breakdown by type")
    user_id: Optional[str] = Field(None, description="User ID (if user-specific)")
    company_id: Optional[str] = Field(None, description="Company ID")
    generated_at: str = Field(..., description="Timestamp when stats were generated")

# ============================================================================
# ACTION SCHEMAS
# ============================================================================

class CampaignStatusUpdate(BaseModel):
    """Schema for updating campaign status"""
    status: CampaignStatusEnum = Field(..., description="New campaign status")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")

class CampaignWorkflowUpdate(BaseModel):
    """Schema for updating campaign workflow"""
    workflow_state: CampaignWorkflowStateEnum = Field(..., description="New workflow state")
    completion_percentage: Optional[int] = Field(None, ge=0, le=100, description="Completion percentage")
    step_data: Optional[Dict[str, Any]] = Field(None, description="Additional step data")

class CampaignCounterUpdate(BaseModel):
    """Schema for updating campaign counters"""
    counter_type: str = Field(..., description="Type of counter to update")
    increment: int = Field(default=1, description="Amount to increment")

    @validator('counter_type')
    def validate_counter_type(cls, v):
        allowed_types = ['sources', 'intelligence', 'content']
        if v not in allowed_types:
            raise ValueError(f'counter_type must be one of: {allowed_types}')
        return v

# ============================================================================
# SEARCH SCHEMAS
# ============================================================================

class CampaignSearchRequest(BaseModel):
    """Schema for campaign search requests"""
    search_term: str = Field(..., min_length=1, max_length=100, description="Search term")
    status_filter: Optional[CampaignStatusEnum] = Field(None, description="Filter by status")
    type_filter: Optional[CampaignTypeEnum] = Field(None, description="Filter by type")
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum number of items to return")

class CampaignSearchResponse(BaseModel):
    """Schema for campaign search responses"""
    campaigns: List[CampaignResponse] = Field(..., description="Matching campaigns")
    total_matches: int = Field(..., ge=0, description="Total number of matches")
    search_term: str = Field(..., description="Search term used")
    page_info: Dict[str, Any] = Field(..., description="Pagination information")

# ============================================================================
# ERROR SCHEMAS
# ============================================================================

class CampaignError(BaseModel):
    """Campaign error response schema"""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def convert_campaign_to_response(campaign_dict: Dict[str, Any]) -> CampaignResponse:
    """Convert campaign dictionary to response schema"""
    return CampaignResponse(**campaign_dict)