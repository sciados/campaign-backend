"""
Landing Page Generator Package
Main entry point for the enhanced landing page generation system.
"""

# Import main classes for easy access
from .core.generator import EnhancedLandingPageGenerator
from .database.storage import LandingPageDatabase
from .components.sections import LandingPageSectionBuilders
from .components.modular import ModularLandingPageBuilder
from .templates.manager import TemplateManager
from .variants.generator import VariantGenerator
from .analytics.tracker import AnalyticsTracker

# Import types and enums
from .core.types import PageType, ColorScheme, ContentType
from .database.models import (
    LandingPageComponent,
    LandingPageTemplate, 
    LandingPageVariant,
    LandingPageAnalytics
)

# Package metadata
__version__ = "2.0.0"
__author__ = "CampaignForge Team"
__description__ = "Enhanced Landing Page Generator with Intelligence Integration"

# Main export for external use
__all__ = [
    # Core classes
    'EnhancedLandingPageGenerator',
    'LandingPageDatabase',
    'LandingPageSectionBuilders',
    'ModularLandingPageBuilder',
    'TemplateManager',
    'VariantGenerator',
    'AnalyticsTracker',
    
    # Types and models
    'PageType',
    'ColorScheme', 
    'ContentType',
    'LandingPageComponent',
    'LandingPageTemplate',
    'LandingPageVariant',
    'LandingPageAnalytics'
]