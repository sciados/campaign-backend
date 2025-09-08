# =====================================
# File: src/core/interfaces/__init__.py
# =====================================

"""
Module interfaces and contracts for CampaignForge architecture.

Defines the standard interfaces that all modules must implement
for consistent interaction and dependency management.
"""

from src.core.interfaces.module_interfaces import ModuleInterface
from src.core.interfaces.service_interfaces import ServiceInterface
from src.core.interfaces.repository_interfaces import RepositoryInterface

__all__ = [
    "ModuleInterface",
    "ServiceInterface", 
    "RepositoryInterface",
]