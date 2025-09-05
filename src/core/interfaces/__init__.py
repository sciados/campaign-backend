# =====================================
# File: src/core/interfaces/__init__.py
# =====================================

"""
Module interfaces and contracts for CampaignForge architecture.

Defines the standard interfaces that all modules must implement
for consistent interaction and dependency management.
"""

from .module_interfaces import ModuleInterface
from .service_interfaces import ServiceInterface
from .repository_interfaces import RepositoryInterface

__all__ = [
    "ModuleInterface",
    "ServiceInterface", 
    "RepositoryInterface",
]