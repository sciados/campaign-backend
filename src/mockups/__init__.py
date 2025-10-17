"""
Product Mockups Module
Handles image compositing for product-on-template rendering.
Provides clean package-level access to MockupModule and submodules.
"""

__version__ = "1.0.0"
__all__ = ["MockupModule", "api", "schemas", "services"]

# Expose top-level MockupModule
try:
    from src.mockups.mockup_module import MockupModule
except ImportError:
    MockupModule = None

# Subpackage references for convenience
from src.mockups import api, schemas, services
