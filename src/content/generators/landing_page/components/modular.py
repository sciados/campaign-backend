"""
Modular Landing Page Builder
Constructs complete landing pages from individual components.
"""

import logging
from typing import Dict, Any, List

from ..core.types import GenerationPreferences, ProductInfo, ConversionIntelligence
from ..templates.manager import TemplateConfig
from ..templates.builder import TemplateBuilder
from .sections import get_section_builder

logger = logging.getLogger(__name__)

class ModularLandingPageBuilder:
    """Builds landing pages using modular components"""
    
    def __init__(self):
        self.template_builder = TemplateBuilder()
        self.section_cache = {}
    
    async def build_complete_landing_page(
        self,
        product_info: ProductInfo,
        conversion_intelligence: ConversionIntelligence,
        template: TemplateConfig,
        preferences: GenerationPreferences
    ) -> Dict[str, Any]:
        """Build complete landing page from modular components"""
        
        try:
            # Get niche context for section building
            niche_context = self._get_niche_context(conversion_intelligence)
            
            # Get color scheme
            colors = self._get_color_scheme(preferences.color_scheme)
            
            # Build all sections
            sections_html = []
            built_sections = []
            
            for section_type in template.sections:
                try:
                    section_html = await self._build_section(
                        section_type=section_type,
                        product_info=product_info.dict(),
                        conversion_intelligence=conversion_intelligence.dict(),
                        niche_context=niche_context,
                        colors=colors,
                        page_config=template.config
                    )
                    
                    sections_html.append(section_html)
                    built_sections.append(section_type)
                    
                except Exception as e:
                    logger.warning(f"Failed to build section {section_type}: {str(e)}")
                    continue
            
            # Build complete HTML template
            complete_html = self.template_builder.build_complete_template(
                sections_html=sections_html,
                product_info=product_info.dict(),
                colors=colors,
                page_config=template.config
            )
            
            return {
                "complete_html": complete_html,
                "sections": built_sections,
                "template_used": template.name,
                "total_sections": len(built_sections),
                "conversion_elements": template.conversion_elements,
                "build_metadata": {
                    "niche_detected": niche_context.get('niche_type', 'generic'),
                    "color_scheme": preferences.color_scheme.value,
                    "page_type": preferences.page_type.value,
                    "sections_built": len(built_sections),
                    "sections_failed": len(template.sections) - len(built_sections)
                }
            }
            
        except Exception as e:
            logger.error(f"Complete landing page build failed: {str(e)}")
            raise
    
    async def _build_section(
        self,
        section_type: str,
        product_info: Dict[str, Any],
        conversion_intelligence: Dict[str, Any],
        niche_context: Dict[str, Any],
        colors: Dict[str, Any],
        page_config: Dict[str, Any]
    ) -> str:
        """Build individual section using appropriate builder"""
        
        # Check cache first
        cache_key = f"{section_type}_{hash(str(product_info))}"
        if cache_key in self.section_cache:
            return self.section_cache[cache_key]
        
        # Get section builder
        section_builder = get_section_builder(section_type)
        
        # Build section HTML
        section_html = section_builder.build(
            product_info=product_info,
            conversion_intelligence=conversion_intelligence,
            colors=colors,
            niche_context=niche_context,
            page_config=page_config
        )
        
        # Cache result
        self.section_cache[cache_key] = section_html
        
        return section_html
    
    def _get_niche_context(self, conversion_intelligence: ConversionIntelligence) -> Dict[str, Any]:
        """Extract niche context from conversion intelligence"""
        return {
            'hero_headline': 'Transform Your Results with {product_name}',
            'hero_subheadline': 'Discover the solution that delivers {benefit}',
            'benefit_icons': ['⭐', '🚀', '💎'],
            'testimonial_template': 'This exceeded my expectations. Exactly what I needed!',
            'testimonial_author': 'Alex M., Happy Customer',
            'footer_tagline': 'Quality solutions for better results'
        }
    
    def _get_color_scheme(self, color_scheme_name: str) -> Dict[str, Any]:
        """Get color scheme configuration"""
        color_schemes = {
            "professional": {
                "primary": "#2563eb",
                "secondary": "#1e40af",
                "accent": "#f59e0b",
                "background": "#ffffff",
                "text": "#1f2937"
            },
            "health": {
                "primary": "#059669",
                "secondary": "#047857",
                "accent": "#f59e0b",
                "background": "#f9fafb",
                "text": "#1f2937"
            },
            "premium": {
                "primary": "#7c3aed",
                "secondary": "#5b21b6",
                "accent": "#f59e0b",
                "background": "#ffffff",
                "text": "#1f2937"
            }
        }
        
        return color_schemes.get(color_scheme_name, color_schemes["professional"])