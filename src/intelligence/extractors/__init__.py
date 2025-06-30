# src/intelligence/extractors/__init__.py
"""
Intelligence Extraction Module
"""

try:
    from .product_extractor import ProductNameExtractor, extract_product_name
    __all__ = ['ProductNameExtractor', 'extract_product_name']
except ImportError:
    # Fallback if product_extractor.py is missing
    __all__ = []