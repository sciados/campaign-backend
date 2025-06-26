"""
Default Templates
Predefined templates for different niches and page types.
"""

from typing import Dict, Any

# Template registry with all available templates
TEMPLATE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "health_supplements_lead_generation": {
        "name": "Health Supplement Lead Gen",
        "sections": ["hero", "benefits", "social_proof", "form", "footer"],
        "conversion_elements": ["scientific_backing", "testimonials", "guarantee", "urgency"],
        "config": {
            "primary_cta": "Get Your Free Health Guide",
            "focus": "email_capture",
            "style": "health_focused",
            "trust_emphasis": "high",
            "social_proof_weight": "high"
        }
    },
    
    "saas_software_free_trial": {
        "name": "SaaS Free Trial",
        "sections": ["hero", "benefits", "demo", "form", "testimonials", "footer"],
        "conversion_elements": ["feature_showcase", "social_proof", "free_trial", "demo"],
        "config": {
            "primary_cta": "Start Free Trial",
            "focus": "trial_signup",
            "style": "tech_modern",
            "demo_emphasis": "high",
            "feature_focus": "automation"
        }
    },
    
    "business_course_sales": {
        "name": "Business Course Sales",
        "sections": ["hero", "problem", "solution", "benefits", "testimonials", "pricing", "guarantee", "cta", "footer"],
        "conversion_elements": ["problem_agitation", "solution_reveal", "social_proof", "guarantee", "urgency"],
        "config": {
            "primary_cta": "Get Instant Access",
            "focus": "course_purchase",
            "style": "business_premium",
            "social_proof_weight": "high",
            "urgency_emphasis": "high"
        }
    },
    
    "life_coaching_lead_generation": {
        "name": "Life Coaching Lead Gen",
        "sections": ["hero", "transformation", "benefits", "social_proof", "form", "footer"],
        "conversion_elements": ["transformation_story", "emotional_triggers", "testimonials", "guarantee"],
        "config": {
            "primary_cta": "Start Your Transformation",
            "focus": "email_capture",
            "style": "inspirational",
            "emotional_emphasis": "high",
            "transformation_focus": "personal_growth"
        }
    },
    
    "ecommerce_product_sales": {
        "name": "E-commerce Product Sales",
        "sections": ["hero", "features", "benefits", "reviews", "pricing", "guarantee", "cta", "footer"],
        "conversion_elements": ["product_showcase", "reviews", "guarantee", "urgency", "security"],
        "config": {
            "primary_cta": "Buy Now",
            "focus": "purchase",
            "style": "ecommerce_clean",
            "product_focus": "features_benefits",
            "trust_emphasis": "high"
        }
    },
    
    "generic_lead_generation": {
        "name": "Generic Lead Generation",
        "sections": ["hero", "benefits", "social_proof", "form", "footer"],
        "conversion_elements": ["value_proposition", "social_proof", "form_optimization"],
        "config": {
            "primary_cta": "Get Started",
            "focus": "email_capture",
            "style": "professional",
            "conversion_focus": "general"
        }
    },
    
    "webinar_registration": {
        "name": "Webinar Registration",
        "sections": ["hero", "agenda", "benefits", "speaker", "registration", "social_proof", "footer"],
        "conversion_elements": ["agenda_preview", "speaker_authority", "urgency", "social_proof"],
        "config": {
            "primary_cta": "Reserve My Seat",
            "focus": "webinar_registration",
            "style": "educational",
            "urgency_emphasis": "high",
            "authority_focus": "speaker_credentials"
        }
    }
}

class DefaultTemplates:
    """Access to default template configurations"""
    
    @staticmethod
    def get_all_templates() -> Dict[str, Dict[str, Any]]:
        """Get all available templates"""
        return TEMPLATE_REGISTRY
    
    @staticmethod
    def get_template_by_name(name: str) -> Dict[str, Any]:
        """Get template by name"""
        for template_data in TEMPLATE_REGISTRY.values():
            if template_data['name'] == name:
                return template_data
        return TEMPLATE_REGISTRY['generic_lead_generation']
    
    @staticmethod
    def get_templates_by_type(page_type: str) -> Dict[str, Dict[str, Any]]:
        """Get all templates for a specific page type"""
        matching_templates = {}
        for key, template_data in TEMPLATE_REGISTRY.items():
            if page_type in key:
                matching_templates[key] = template_data
        return matching_templates