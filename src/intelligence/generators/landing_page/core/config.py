"""
Configuration constants and default settings for the landing page system.
"""

from typing import Dict, Any
from .types import PageType, ColorScheme, PageConfig, ColorConfig

# Default page configurations
PAGE_CONFIGS: Dict[PageType, PageConfig] = {
    PageType.LEAD_GENERATION: PageConfig(
        sections=["hero", "benefits", "social_proof", "form", "guarantee", "footer"],
        primary_cta="Get Free Guide",
        focus="email capture",
        conversion_elements=["lead_magnet", "email_form", "trust_signals"]
    ),
    PageType.SALES: PageConfig(
        sections=["hero", "problem", "solution", "benefits", "pricing", "testimonials", "guarantee", "cta", "footer"],
        primary_cta="Buy Now",
        focus="purchase conversion", 
        conversion_elements=["social_proof", "urgency", "guarantee", "pricing"]
    ),
    PageType.WEBINAR: PageConfig(
        sections=["hero", "speaker_bio", "agenda", "benefits", "registration", "countdown", "social_proof", "footer"],
        primary_cta="Register Now",
        focus="webinar registration",
        conversion_elements=["countdown_timer", "speaker_authority", "limited_seats"]
    ),
    PageType.PRODUCT_DEMO: PageConfig(
        sections=["hero", "features", "demo_video", "benefits", "trial_form", "testimonials", "footer"],
        primary_cta="Watch Demo",
        focus="demo engagement",
        conversion_elements=["demo_video", "feature_highlights", "trial_offer"]
    ),
    PageType.free_TRIAL: PageConfig(
        sections=["hero", "features", "benefits", "trial_form", "testimonials", "guarantee", "footer"],
        primary_cta="Start Free Trial",
        focus="trial signup",
        conversion_elements=["trial_form", "no_credit_card", "instant_access"]
    )
}

# Color scheme configurations
COLOR_SCHEMES: Dict[ColorScheme, ColorConfig] = {
    ColorScheme.PROFESSIONAL: ColorConfig(
        primary="#2563eb",
        secondary="#1e40af",
        accent="#f59e0b",
        background="#ffffff",
        text="#1f2937",
        gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    ),
    ColorScheme.HEALTH: ColorConfig(
        primary="#059669", 
        secondary="#047857",
        accent="#f59e0b",
        background="#f9fafb",
        text="#1f2937",
        gradient="linear-gradient(135deg, #34d399 0%, #059669 100%)"
    ),
    ColorScheme.PREMIUM: ColorConfig(
        primary="#7c3aed",
        secondary="#5b21b6", 
        accent="#f59e0b",
        background="#ffffff",
        text="#1f2937",
        gradient="linear-gradient(135deg, #a855f7 0%, #7c3aed 100%)"
    ),
    ColorScheme.ENERGY: ColorConfig(
        primary="#dc2626",
        secondary="#b91c1c",
        accent="#f59e0b", 
        background="#ffffff",
        text="#1f2937",
        gradient="linear-gradient(135deg, #f87171 0%, #dc2626 100%)"
    )
}

# Default generation settings
DEFAULT_PREFERENCES = {
    "page_type": PageType.LEAD_GENERATION,
    "color_scheme": ColorScheme.HEALTH,
    "include_animations": True,
    "mobile_first": True,
    "seo_optimized": True,
    "generate_variants": False
}

# AI Provider configurations
AI_PROVIDER_CONFIG = {
    "anthropic": {
        "models": ["claude-3-5-sonnet-20241022"],
        "strengths": ["long_form", "structured_content", "html_generation"],
        "max_tokens": 4000,
        "temperature": 0.7
    },
    "openai": {
        "models": ["gpt-4"],
        "strengths": ["creativity", "conversion_copy"],
        "max_tokens": 4000, 
        "temperature": 0.7
    }
}

# Performance and optimization settings
PERFORMANCE_CONFIG = {
    "max_html_size": 2 * 1024 * 1024,  # 2MB
    "target_load_time": 2000,  # 2 seconds
    "min_lighthouse_score": 90,
    "cache_templates": True,
    "optimize_images": True
}

# Analytics configuration
ANALYTICS_CONFIG = {
    "track_scroll_depth": True,
    "track_form_interactions": True,
    "track_cta_clicks": True,
    "track_time_milestones": [30, 60, 120, 300],
    "session_timeout": 30 * 60,  # 30 minutes
    "enable_heatmaps": False  # Requires additional setup
}