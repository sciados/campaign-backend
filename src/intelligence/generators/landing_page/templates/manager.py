"""
Template Manager
Handles template selection and customization based on niche and page type.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ..core.types import PageType
from ..intelligence.niche_detector import NicheType
from .defaults import TEMPLATE_REGISTRY

logger = logging.getLogger(__name__)

@dataclass
class TemplateConfig:
    """Template configuration"""
    name: str
    sections: list
    conversion_elements: list
    config: dict

class TemplateManager:
    """Manages template selection and customization"""
    
    def __init__(self):
        self.templates = TEMPLATE_REGISTRY
    
    def get_template(
        self, 
        page_type: PageType, 
        niche: NicheType
    ) -> TemplateConfig:
        """Get appropriate template based on page type and niche"""
        
        # Build template key
        template_key = f"{niche.value}_{page_type.value}"
        
        # Try to find specific template
        if template_key in self.templates:
            template_data = self.templates[template_key]
        else:
            # Fall back to generic template for this page type
            generic_key = f"generic_{page_type.value}"
            template_data = self.templates.get(generic_key, self.templates["generic_lead_generation"])
        
        return TemplateConfig(
            name=template_data['name'],
            sections=template_data['sections'],
            conversion_elements=template_data['conversion_elements'],
            config=template_data['config']
        )
    
    def get_fallback_template(self) -> str:
        """Get fallback HTML template"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Landing Page</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; text-align: center; }
                .btn { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Get Started Today</h1>
                <p>Transform your results with our proven solution.</p>
                <button class="btn">Learn More</button>
            </div>
        </body>
        </html>
        """