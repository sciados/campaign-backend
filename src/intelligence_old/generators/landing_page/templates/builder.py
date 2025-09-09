"""
Template Builder
Constructs complete landing page templates from components.
"""

import logging
from typing import Dict, Any, List

from ..utils.css import CSSGenerator
from ..utils.html import HTMLStructureBuilder

logger = logging.getLogger(__name__)

class TemplateBuilder:
    """Builds complete landing page templates"""
    
    def __init__(self):
        self.css_generator = CSSGenerator()
        self.html_builder = HTMLStructureBuilder()
    
    def build_complete_template(
        self,
        sections_html: List[str],
        product_info: Dict[str, Any],
        colors: Dict[str, Any],
        page_config: Dict[str, Any]
    ) -> str:
        """Build complete HTML template with all sections"""
        
        # Generate CSS
        css_styles = self.css_generator.generate_complete_css(colors, page_config)
        
        # Generate JavaScript
        javascript_code = self._generate_javascript(page_config)
        
        # Build complete HTML structure
        return self.html_builder.build_complete_html(
            sections_html=sections_html,
            css_styles=css_styles,
            javascript_code=javascript_code,
            product_info=product_info,
            page_config=page_config
        )
    
    def _generate_javascript(self, page_config: Dict[str, Any]) -> str:
        """Generate JavaScript for interactivity and tracking"""
        
        return """
        // Form handling
        function handleFormSubmit(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            const email = formData.get('email');
            const firstName = formData.get('firstName');
            
            // Track conversion
            trackEvent('form_submit', { email: email, firstName: firstName });
            
            // Show success message
            showSuccessMessage();
        }
        
        // Scroll to form
        function scrollToForm() {
            const formSection = document.getElementById('form');
            if (formSection) {
                formSection.scrollIntoView({ behavior: 'smooth' });
                trackEvent('cta_click', { section: 'form' });
            }
        }
        
        // Event tracking
        function trackEvent(eventName, data = {}) {
            console.log('Event:', eventName, data);
            // Add your analytics tracking here
        }
        
        // Success message
        function showSuccessMessage() {
            alert('Thank you! Check your email for next steps.');
        }
        
        // Smooth scrolling for all anchor links
        document.addEventListener('DOMContentLoaded', function() {
            // Add click tracking to all tracked elements
            document.querySelectorAll('[data-track]').forEach(element => {
                element.addEventListener('click', function() {
                    trackEvent('element_click', { 
                        element: this.getAttribute('data-track'),
                        text: this.textContent.trim()
                    });
                });
            });
            
            // Track page load
            trackEvent('page_load', { 
                timestamp: Date.now(),
                userAgent: navigator.userAgent
            });
        });
        """