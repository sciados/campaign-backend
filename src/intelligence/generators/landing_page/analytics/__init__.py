"""
Analytics module for landing page performance tracking.
Handles tracking, events, and performance predictions.
"""

from .tracker import AnalyticsTracker
from .events import EventDefinitions, ConversionEventTracker
from .performance import PerformancePrediction, OptimizationRecommendations

__all__ = [
    'AnalyticsTracker',
    'EventDefinitions',
    'ConversionEventTracker',
    'PerformancePrediction',
    'OptimizationRecommendations'
]