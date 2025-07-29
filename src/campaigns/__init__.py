"""
Campaign Schemas Package - Following intelligence/schemas pattern
"""

from .campaign_schemas import (
    CampaignCreate,
    CampaignUpdate, 
    CampaignResponse,
    WorkflowProgressData
)
from .demo_schemas import (
    DemoPreferenceUpdate,
    DemoPreferenceResponse,
    DemoCreationRequest,
    DemoCreationResponse
)
from .workflow_schemas import (
    WorkflowStateResponse,
    AnalysisProgressResponse,
    CampaignIntelligenceResponse
)

__all__ = [
    "CampaignCreate",
    "CampaignUpdate", 
    "CampaignResponse",
    "WorkflowProgressData",
    "DemoPreferenceUpdate",
    "DemoPreferenceResponse",
    "DemoCreationRequest",
    "DemoCreationResponse",
    "WorkflowStateResponse",
    "AnalysisProgressResponse",
    "CampaignIntelligenceResponse"
]