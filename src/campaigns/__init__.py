# src/campaigns/__init__.py

"""
Campaign Management Module

This module provides complete campaign lifecycle management including:
- Campaign CRUD operations
- Workflow automation
- Dashboard analytics
- Performance tracking
"""

# from src.campaigns.campaigns_module import CampaignModule
from src.campaigns.services.campaign_service import CampaignService
from src.campaigns.models.campaign import Campaign
from src.campaigns.campaigns_module import CampaignModule

__all__ = [
    "CampaignModule",
    "CampaignService",
    "Campaign"
]