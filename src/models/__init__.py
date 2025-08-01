# src/models/__init__.py - FIXED VERSION with correct imports
"""
Central model imports and exports with proper dependency order
Fixed to match actual database structure and prevent import conflicts
"""

import logging
logger = logging.getLogger(__name__)

# ============================================================================
# ✅ PHASE 1: Import base classes first (always required)
# ============================================================================

try:
    from .base import BaseModel, EnumSerializerMixin, Base
    logger.debug("✅ Base models imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import base models: {e}")
    raise

# ============================================================================
# ✅ PHASE 2: Import storage models first (new - no dependencies)
# ============================================================================

try:
    from .user_storage import UserStorageUsage
    logger.debug("✅ User storage model imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ User storage model not available: {e}")
    UserStorageUsage = None

# ============================================================================
# ✅ PHASE 3: Import core models (Company, User - minimal dependencies)
# ============================================================================

try:
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
    logger.debug("✅ Company models imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Company models not available: {e}")
    # Create placeholder classes to prevent import errors
    Company = None
    CompanyMembership = None
    CompanyInvitation = None
    CompanySize = None
    CompanySubscriptionTier = None
    MembershipRole = None
    MembershipStatus = None
    InvitationStatus = None

try:
    from .user import User
    logger.debug("✅ User model imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ User model not available: {e}")
    User = None

# ============================================================================
# ✅ PHASE 4: Import campaign models (depends on User, Company)
# ============================================================================

try:
    from .campaign import (
        Campaign,
        CampaignStatus,
        WorkflowPreference, 
        CampaignWorkflowState,
        AutoAnalysisStatus
    )
    logger.debug("✅ Campaign models imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Campaign models not available: {e}")
    Campaign = None
    CampaignStatus = None
    WorkflowPreference = None
    CampaignWorkflowState = None
    AutoAnalysisStatus = None

# ============================================================================
# ✅ PHASE 5: Import asset models (depends on Campaign, User)
# ============================================================================

try:
    from .campaign_assets import (
        CampaignAsset,
        AssetType,
        AssetStatus,
        get_asset_type_from_extension,
        validate_file_size,
        generate_file_hash,
        get_allowed_extensions
    )
    logger.debug("✅ Campaign asset models imported successfully")
    
except Exception as e:
    logger.error(f"❌ Campaign asset models failed: {e}")
    # Attempt to resolve metadata conflicts
    try:
        from .base import Base
        if hasattr(Base, 'metadata'):
            Base.metadata.clear()
            logger.debug("🧹 SQLAlchemy metadata cleared (assets)")
        
        # Try importing again after clearing metadata
        from .campaign_assets import (
            CampaignAsset,
            AssetType,
            AssetStatus,
            get_asset_type_from_extension,
            validate_file_size,
            generate_file_hash,
            get_allowed_extensions
        )
        logger.info("✅ Campaign asset models imported successfully after metadata clear")
    except Exception as retry_error:
        logger.error(f"❌ Retry of campaign asset models failed: {retry_error}")
        CampaignAsset = None
        AssetType = None
        AssetStatus = None
        get_asset_type_from_extension = None
        validate_file_size = None
        generate_file_hash = None
        get_allowed_extensions = None

# ============================================================================
# ✅ PHASE 6: Import intelligence models (depends on Campaign, User)
# ============================================================================

try:
    from .intelligence import (
        CampaignIntelligence,
        GeneratedContent,
        SmartURL,
        IntelligenceSourceType,
        AnalysisStatus,
        AnalysisRequest
    )
    logger.debug("✅ Intelligence models imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Intelligence models not available: {e}")
    CampaignIntelligence = None
    GeneratedContent = None
    SmartURL = None
    IntelligenceSourceType = None
    AnalysisStatus = None
    AnalysisRequest = None

# ============================================================================
# ✅ PHASE 7: Import waitlist model (minimal dependencies)
# ============================================================================

try:
    from .waitlist import Waitlist
    logger.debug("✅ Waitlist model imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Waitlist model not available: {e}")
    Waitlist = None

# ============================================================================
# ✅ ENHANCED EXPORTS WITH AVAILABILITY CHECKING
# ============================================================================

# Create a function to check model availability
def get_available_models():
    """
    Returns a dictionary of available models for debugging
    """
    return {
        'base_models': BaseModel is not None,
        'storage_models': UserStorageUsage is not None,
        'company_models': Company is not None,
        'user_models': User is not None,
        'campaign_models': Campaign is not None,
        'asset_models': CampaignAsset is not None,
        'intelligence_models': CampaignIntelligence is not None,
        'waitlist_models': Waitlist is not None
    }

# __all__ export with conditional inclusion
_base_exports = [
    'BaseModel',
    'EnumSerializerMixin', 
    'Base',
]

_storage_exports = ['UserStorageUsage'] if UserStorageUsage is not None else []

_company_exports = [
    'Company',
    'CompanyMembership',
    'CompanyInvitation',
    'CompanySize',
    'CompanySubscriptionTier',
    'MembershipRole',
    'MembershipStatus',
    'InvitationStatus',
] if Company is not None else []

_user_exports = ['User'] if User is not None else []

_campaign_exports = [
    'Campaign',
    'CampaignStatus',
    'WorkflowPreference',
    'CampaignWorkflowState',
    'AutoAnalysisStatus',
] if Campaign is not None else []

_asset_exports = [
    'CampaignAsset',
    'AssetType',
    'AssetStatus',
    'get_asset_type_from_extension',
    'validate_file_size', 
    'generate_file_hash',
    'get_allowed_extensions',
] if CampaignAsset is not None else []

_intelligence_exports = [
    'CampaignIntelligence',
    'GeneratedContent', 
    'SmartURL',
    'IntelligenceSourceType',
    'AnalysisStatus',
    'AnalysisRequest',
] if CampaignIntelligence is not None else []

_waitlist_exports = ['Waitlist'] if Waitlist is not None else []

# Utility exports (always available)
_utility_exports = [
    'get_available_models',
]

# Combine all exports
__all__ = (
    _base_exports + 
    _storage_exports +
    _company_exports + 
    _user_exports + 
    _campaign_exports + 
    _asset_exports + 
    _intelligence_exports +
    _waitlist_exports +
    _utility_exports
)

# ============================================================================
# ✅ STARTUP LOGGING AND DIAGNOSTICS
# ============================================================================

def log_model_status():
    """
    Log the status of all models for debugging
    """
    available = get_available_models()
    
    logger.info("📊 Model Import Status:")
    logger.info(f"  ✅ Base models: {'Available' if available['base_models'] else 'Failed'}")
    logger.info(f"  ✅ Storage models: {'Available' if available['storage_models'] else 'Failed'}")
    logger.info(f"  ✅ Company models: {'Available' if available['company_models'] else 'Failed'}")
    logger.info(f"  ✅ User models: {'Available' if available['user_models'] else 'Failed'}")
    logger.info(f"  ✅ Campaign models: {'Available' if available['campaign_models'] else 'Failed'}")
    logger.info(f"  ✅ Asset models: {'Available' if available['asset_models'] else 'Failed'}")
    logger.info(f"  ✅ Intelligence models: {'Available' if available['intelligence_models'] else 'Failed'}")
    logger.info(f"  ✅ Waitlist models: {'Available' if available['waitlist_models'] else 'Failed'}")
    
    total_available = sum(1 for v in available.values() if v)
    total_models = len(available)
    logger.info(f"📈 Overall: {total_available}/{total_models} model groups available")

# Log status when module is imported
try:
    log_model_status()
except:
    # Suppress logging errors during import
    pass