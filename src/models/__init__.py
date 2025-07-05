# src/models/__init__.py - Central model exports
"""
Central model imports and exports
"""

# Import base classes first
from .base import BaseModel, EnumSerializerMixin, Base

# Import all models (order matters to avoid circular imports)
from .company import (
    Company, 
    CompanyMembership, 
    CompanyInvitation,
    CompanySize,
    CompanySubscriptionTier,
    MembershipRole,
    MembershipStatus,
    InvitationStatus
)

from .user import User

from .campaign import (
    Campaign,
    CampaignStatus,
    WorkflowPreference, 
    CampaignWorkflowState
)

from .campaign_assets import (
    CampaignAsset,
    AssetType,
    AssetStatus,
    get_asset_type_from_extension,
    validate_file_size,
    generate_file_hash,
    get_allowed_extensions
)

from .intelligence import (
    CampaignIntelligence,
    GeneratedContent,
    SmartURL,
    IntelligenceSourceType,
    AnalysisStatus,
    EnhancedAnalysisRequest
)

# Export all models and utilities
__all__ = [
    # Base classes
    'BaseModel',
    'EnumSerializerMixin', 
    'Base',
    
    # Company models
    'Company',
    'CompanyMembership',
    'CompanyInvitation',
    'CompanySize',
    'CompanySubscriptionTier',
    'MembershipRole',
    'MembershipStatus',
    'InvitationStatus',
    
    # User models
    'User',
    
    # Campaign models
    'Campaign',
    'CampaignStatus',
    'WorkflowPreference',
    'CampaignWorkflowState',
    
    # Asset models
    'CampaignAsset',
    'AssetType',
    'AssetStatus',
    'get_asset_type_from_extension',
    'validate_file_size', 
    'generate_file_hash',
    'get_allowed_extensions',
    
    # Intelligence models
    'CampaignIntelligence',
    'GeneratedContent', 
    'SmartURL',
    'IntelligenceSourceType',
    'AnalysisStatus',
    'EnhancedAnalysisRequest',
]