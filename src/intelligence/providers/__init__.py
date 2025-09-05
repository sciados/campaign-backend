# =====================================
# File: src/intelligence/providers/__init__.py
# =====================================

"""
AI provider management for Intelligence Engine.

Integrates with the core AI provider configuration system
and provides intelligence-specific provider routing.
"""

from .ai_provider_router import AIProviderRouter

__all__ = ["AIProviderRouter"]