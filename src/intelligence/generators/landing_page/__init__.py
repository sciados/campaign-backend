"""
Landing Page Generator Package
Main entry point for the enhanced landing page generation system.
"""

# Package metadata
__version__ = "2.0.0"
__author__ = "CampaignForge Team"
__description__ = "Enhanced Landing Page Generator with Intelligence Integration"

# Import with error handling - only import what actually exists
try:
    from .core.generator import EnhancedLandingPageGenerator
except ImportError as e:
    print(f"Warning: Could not import EnhancedLandingPageGenerator: {e}")
    EnhancedLandingPageGenerator = None

try:
    from .database.storage import LandingPageStorage
    # Create alias for the expected name
    LandingPageDatabase = LandingPageStorage
except ImportError as e:
    print(f"Warning: Could not import LandingPageStorage: {e}")
    LandingPageStorage = None
    LandingPageDatabase = None

try:
    from .components.sections import LandingPageSectionBuilders
except ImportError as e:
    print(f"Warning: Could not import LandingPageSectionBuilders: {e}")
    LandingPageSectionBuilders = None

try:
    from .components.modular import ModularLandingPageBuilder
except ImportError as e:
    print(f"Warning: Could not import ModularLandingPageBuilder: {e}")
    ModularLandingPageBuilder = None

try:
    from .templates.manager import TemplateManager
except ImportError as e:
    print(f"Warning: Could not import TemplateManager: {e}")
    TemplateManager = None

try:
    from .variants.generator import VariantGenerator
except ImportError as e:
    print(f"Warning: Could not import VariantGenerator: {e}")
    VariantGenerator = None

try:
    from .analytics.tracker import AnalyticsTracker
except ImportError as e:
    print(f"Warning: Could not import AnalyticsTracker: {e}")
    AnalyticsTracker = None

# Import types and enums
try:
    from .core.types import PageType, ColorScheme, ContentType
except ImportError as e:
    print(f"Warning: Could not import types: {e}")
    # Create fallback enums
    from enum import Enum
    
    class PageType(str, Enum):
        SALES = "sales"
        LEAD_GEN = "lead_gen"
        PRODUCT = "product"
        SERVICE = "service"
        LEAD_GENERATION = "lead_generation"
    
    class ColorScheme(str, Enum):
        MODERN = "modern"
        CLASSIC = "classic"
        VIBRANT = "vibrant"
        PROFESSIONAL = "professional"
    
    class ContentType(str, Enum):
        LANDING_PAGE = "landing_page"

try:
    from .database.models import (
        LandingPageComponent,
        LandingPageTemplate, 
        LandingPageVariant,
        LandingPageAnalytics
    )
except ImportError as e:
    print(f"Warning: Could not import database models: {e}")
    LandingPageComponent = None
    LandingPageTemplate = None
    LandingPageVariant = None
    LandingPageAnalytics = None

# Build __all__ with only successfully imported items
__all__ = ['PageType', 'ColorScheme', 'ContentType']

if EnhancedLandingPageGenerator is not None:
    __all__.append('EnhancedLandingPageGenerator')

if LandingPageStorage is not None:
    __all__.extend(['LandingPageStorage', 'LandingPageDatabase'])

if LandingPageSectionBuilders is not None:
    __all__.append('LandingPageSectionBuilders')

if ModularLandingPageBuilder is not None:
    __all__.append('ModularLandingPageBuilder')

if TemplateManager is not None:
    __all__.append('TemplateManager')

if VariantGenerator is not None:
    __all__.append('VariantGenerator')

if AnalyticsTracker is not None:
    __all__.append('AnalyticsTracker')

if LandingPageComponent is not None:
    __all__.extend([
        'LandingPageComponent',
        'LandingPageTemplate',
        'LandingPageVariant',
        'LandingPageAnalytics'
    ])

def get_available_features():
    """Get list of available features"""
    return {
        'generator': EnhancedLandingPageGenerator is not None,
        'storage': LandingPageStorage is not None,
        'sections': LandingPageSectionBuilders is not None,
        'modular': ModularLandingPageBuilder is not None,
        'templates': TemplateManager is not None,
        'variants': VariantGenerator is not None,
        'analytics': AnalyticsTracker is not None,
        'models': LandingPageComponent is not None
    }