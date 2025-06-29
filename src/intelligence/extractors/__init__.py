# src/intelligence/extractors/__init__.py
"""
Intelligence Extraction Module
Handles extraction of specific intelligence elements from sales pages and content
"""

from .product_extractor import ProductNameExtractor, extract_product_name

__all__ = [
    'ProductNameExtractor',
    'extract_product_name'
]