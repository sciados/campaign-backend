"""
Utilities module for landing page generation.
Provides HTML, CSS, and validation utilities.
"""

# Import what actually exists
try:
    from .html import HTMLStructureBuilder, HTMLOptimizer
except ImportError as e:
    print(f"Warning: Could not import HTML utilities: {e}")
    HTMLStructureBuilder = None
    HTMLOptimizer = None

try:
    from .css import CSSGenerator, ResponsiveStylesheet
except ImportError as e:
    print(f"Warning: Could not import CSS utilities: {e}")
    CSSGenerator = None
    ResponsiveStylesheet = None

try:
    from .validation import (
        ValidationError, ValidationResult,
        validate_preferences, validate_intelligence_data,
        validate_analytics_event_data, sanitize_string, sanitize_text
    )
except ImportError as e:
    print(f"Warning: Could not import validation utilities: {e}")
    ValidationError = None
    ValidationResult = None
    validate_preferences = None
    validate_intelligence_data = None
    validate_analytics_event_data = None
    sanitize_string = None
    sanitize_text = None

# Build __all__ with only successfully imported items
__all__ = []

if HTMLStructureBuilder is not None:
    __all__.extend(['HTMLStructureBuilder', 'HTMLOptimizer'])

if CSSGenerator is not None:
    __all__.extend(['CSSGenerator', 'ResponsiveStylesheet'])

if ValidationError is not None:
    __all__.extend([
        'ValidationError', 'ValidationResult',
        'validate_preferences', 'validate_intelligence_data', 
        'validate_analytics_event_data', 'sanitize_string', 'sanitize_text'
    ])

# Create aliases for backward compatibility (if anyone was expecting these names)
InputValidator = ValidationResult if ValidationResult else None
ContentValidator = ValidationError if ValidationError else None

if InputValidator is not None:
    __all__.append('InputValidator')
if ContentValidator is not None:
    __all__.append('ContentValidator')