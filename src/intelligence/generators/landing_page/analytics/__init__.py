"""
Analytics module for landing page performance tracking.
Handles tracking, events, and performance predictions.
"""

# Import what actually exists in the files
try:
    from .tracker import AnalyticsTracker
except ImportError as e:
    print(f"Warning: Could not import AnalyticsTracker: {e}")
    AnalyticsTracker = None

try:
    from .events import (
        EventType, ConversionType, DeviceType,
        EventDataFactory, EventValidator, EventAggregator,
        ConversionEventData, AnalyticsEventData
    )
except ImportError as e:
    print(f"Warning: Could not import events: {e}")
    EventType = None
    ConversionType = None
    DeviceType = None
    EventDataFactory = None
    EventValidator = None
    EventAggregator = None
    ConversionEventData = None
    AnalyticsEventData = None

try:
    from .performance import PerformancePrediction, PerformanceCalculator
except ImportError as e:
    print(f"Warning: Could not import performance: {e}")
    PerformancePrediction = None
    PerformanceCalculator = None

# Build __all__ with only successfully imported items
__all__ = []

if AnalyticsTracker is not None:
    __all__.append('AnalyticsTracker')

if EventType is not None:
    __all__.extend([
        'EventType', 'ConversionType', 'DeviceType',
        'EventDataFactory', 'EventValidator', 'EventAggregator',
        'ConversionEventData', 'AnalyticsEventData'
    ])

if PerformancePrediction is not None:
    __all__.extend(['PerformancePrediction', 'PerformanceCalculator'])

# Legacy aliases for backward compatibility
EventDefinitions = EventDataFactory  # Alias for the old name
ConversionEventTracker = AnalyticsTracker  # Alias for the old name

if EventDefinitions is not None:
    __all__.append('EventDefinitions')
if ConversionEventTracker is not None:
    __all__.append('ConversionEventTracker')