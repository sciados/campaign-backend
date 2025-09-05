# =====================================
# File: src/intelligence/repositories/__init__.py
# =====================================

"""
Intelligence Engine repositories for data access.

Provides data access layer implementations using the repository pattern
with the consolidated intelligence schema.
"""

from .intelligence_repository import IntelligenceRepository
from .research_repository import ResearchRepository

__all__ = [
    "IntelligenceRepository",
    "ResearchRepository",
]