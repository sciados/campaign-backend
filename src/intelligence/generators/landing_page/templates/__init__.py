"""
Templates module for landing page generation.
Handles template selection, building, and management.
"""

from .manager import TemplateManager
from .builder import TemplateBuilder
from .defaults import DefaultTemplates, TEMPLATE_REGISTRY

__all__ = [
    'TemplateManager',
    'TemplateBuilder',
    'DefaultTemplates',
    'TEMPLATE_REGISTRY'
]