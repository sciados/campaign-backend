"""
Type definitions, enums, and data structures for the landing page system.
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import uuid

class PageType(Enum):
    """Supported landing page types"""
    LEAD_GENERATION = "lead_generation"
    SALES = "sales"
    WEBINAR = "webinar"
    PRODUCT_DEMO = "product_demo"
    free_TRIAL = "free_trial"

class ColorScheme(Enum):
    """Available color schemes"""
    PROFESSIONAL = "professional"
    HEALTH = "health"
    PREMIUM = "premium"
    ENERGY = "energy"

class IndustryNiche(Enum):
    """Supported industry niches"""
    HEALTH = "health"
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    EDUCATION = "education"
    FINANCE = "finance"
    LIFESTYLE = "lifestyle"

class ContentType(Enum):
    """Content generation types"""
    EMAIL_SEQUENCE = "EMAIL_SEQUENCE"
    LANDING_PAGE = "LANDING_PAGE"
    AD_COPY = "AD_COPY"
    BLOG_POST = "BLOG_POST"
    SOCIAL_POSTS = "SOCIAL_POSTS"
    VIDEO_SCRIPT = "VIDEO_SCRIPT"

@dataclass
class PageConfig:
    """Configuration for a landing page type"""
    sections: List[str]
    primary_cta: str
    focus: str
    conversion_elements: List[str]

@dataclass
class ColorConfig:
    """Color configuration for a theme"""
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    gradient: str

@dataclass
class ProductInfo:
    """Product information extracted from intelligence"""
    name: str
    category: str
    benefits: List[str]
    value_propositions: List[str]
    positioning: str

@dataclass
class ConversionIntelligence:
    """Conversion-focused intelligence data"""
    emotional_triggers: List[str]
    pain_points: List[str]
    trust_signals: List[str]
    competitive_advantages: List[str]
    urgency_elements: List[str]
    social_proof: List[str]
    amplified_intelligence: bool
    confidence_boost: float
    scientific_enhancements: int

@dataclass
class GenerationPreferences:
    """User preferences for page generation"""
    page_type: PageType
    color_scheme: ColorScheme
    include_animations: bool = True
    mobile_first: bool = True
    seo_optimized: bool = True
    generate_variants: bool = False
    custom_sections: Optional[List[str]] = None

@dataclass
class GenerationResult:
    """Result of landing page generation"""
    content_type: str
    title: str
    html_code: str
    sections: List[str]
    conversion_elements: List[str]
    metadata: Dict[str, Any]
    variants: List[Dict[str, Any]]
    performance_predictions: Dict[str, Any]