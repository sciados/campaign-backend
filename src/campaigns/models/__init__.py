# src/campaigns/models/__init__.py

"""Campaign Models"""

from src.campaigns.models.campaign import (
    Campaign,
    CampaignStatusEnum,
    CampaignTypeEnum,
    CampaignWorkflowStateEnum,
    AutoAnalysisStatusEnum,
    # Legacy compatibility aliases
    CampaignStatus,
    CampaignWorkflowState,
    AutoAnalysisStatus
)

__all__ = [
    "Campaign",
    "CampaignStatusEnum",
    "CampaignTypeEnum", 
    "CampaignWorkflowStateEnum",
    "AutoAnalysisStatusEnum",
    # Legacy aliases
    "CampaignStatus",
    "CampaignWorkflowState",
    "AutoAnalysisStatus"
]