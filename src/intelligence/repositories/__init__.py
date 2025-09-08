# =====================================
# File: src/intelligence/repositories/__init__.py
# =====================================

"""
Intelligence Engine repositories for data access.

Provides data access layer implementations using the repository pattern
with the consolidated intelligence schema.
"""

from src.intelligence.repositories.intelligence_repository import IntelligenceRepository
from src.intelligence.repositories.research_repository import ResearchRepository

__all__ = [
    "IntelligenceRepository",
    "ResearchRepository",
]