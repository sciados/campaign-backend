# src/campaigns/schemas/__init__.py

"""Campaign Schemas"""

from .campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignListResponse,
    CampaignStatsResponse,
    CampaignStatusUpdate,
    CampaignSearchRequest,
    CampaignSearchResponse,
    CampaignCounterUpdate,
    convert_campaign_to_response
)

from .workflow import (
    WorkflowProgress,
    WorkflowAction,
    WorkflowStepResult,
    WorkflowAnalytics,
    WorkflowNotification,
    WorkflowResponse,
    WorkflowListResponse,
    WorkflowStartRequest,
    WorkflowTemplate,
    WorkflowTemplateCreate,
    WorkflowTemplateUpdate
)

__all__ = [
    # Campaign schemas
    "CampaignCreate",
    "CampaignUpdate", 
    "CampaignResponse",
    "CampaignListResponse",
    "CampaignStatsResponse",
    "CampaignStatusUpdate",
    "CampaignSearchRequest",
    "CampaignSearchResponse",
    "CampaignCounterUpdate",
    "convert_campaign_to_response",
    # Workflow schemas
    "WorkflowProgress",
    "WorkflowAction",
    "WorkflowStepResult",
    "WorkflowAnalytics", 
    "WorkflowNotification",
    "WorkflowResponse",
    "WorkflowListResponse",
    "WorkflowStartRequest",
    "WorkflowTemplate",
    "WorkflowTemplateCreate",
    "WorkflowTemplateUpdate"
]