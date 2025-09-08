"""
Variants module for A/B testing landing page variations.
Generates and manages landing page variants for testing.
"""

from .generator import VariantGenerator
from .hypothesis import HypothesisGenerator, TestHypothesis

__all__ = [
    'VariantGenerator',
    'HypothesisGenerator',
    'TestHypothesis'
]