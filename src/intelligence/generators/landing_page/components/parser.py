"""
HTML Parser and Component Extractor
Parses HTML content and extracts components for analysis.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from html.parser import HTMLParser as BaseHTMLParser

logger = logging.getLogger(__name__)

class HTMLParser:
    """Parses HTML content and extracts structure information"""
    
    def __init__(self):
        self.component_patterns = {
            'headlines': r'<h[1-6][^>]*>(.*?)</h[1-6]>',
            'buttons': r'<button[^>]*>(.*?)</button>',
            'forms': r'<form[^>]*>.*?</form>',
            'images': r'<img[^>]*>',
            'links': r'<a[^>]*>(.*?)</a>',
            'sections': r'<section[^>]*>.*?</section>',
            'divs': r'<div[^>]*class="([^"]*)"[^>]*>',
        }
    
    def parse_html_structure(self, html_content: str) -> Dict[str, Any]:
        """Parse HTML and extract structural information"""
        
        structure = {
            'sections': [],
            'headlines': [],
            'buttons': [],
            'forms': [],
            'images': [],
            'links': [],
            'classes': [],
            'conversion_elements': []
        }
        
        try:
            # Extract each component type
            for component_type, pattern in self.component_patterns.items():
                matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
                if component_type == 'divs':
                    structure['classes'].extend(matches)
                else:
                    structure[component_type] = matches
            
            # Identify conversion elements
            structure['conversion_elements'] = self._identify_conversion_elements(html_content)
            
            # Calculate structure metrics
            structure['metrics'] = self._calculate_structure_metrics(structure)
            
        except Exception as e:
            logger.error(f"HTML parsing failed: {str(e)}")
        
        return structure
    
    def _identify_conversion_elements(self, html_content: str) -> List[str]:
        """Identify conversion-focused elements in HTML"""
        
        conversion_elements = []
        
        # Check for common conversion patterns
        conversion_patterns = {
            'cta_buttons': r'<button[^>]*(?:class="[^"]*(?:cta|btn-primary)[^"]*"|data-track="[^"]*cta[^"]*")[^>]*>',
            'forms': r'<form[^>]*>',
            'testimonials': r'(?:testimonial|review|quote)',
            'guarantees': r'(?:guarantee|money.?back|risk.?free)',
            'urgency': r'(?:limited.?time|act.?now|expires|hurry)',
            'social_proof': r'(?:customers|users|members|success|rating)',
            'trust_signals': r'(?:secure|verified|certified|award)'
        }
        
        for element_type, pattern in conversion_patterns.items():
            if re.search(pattern, html_content, re.IGNORECASE):
                conversion_elements.append(element_type)
        
        return conversion_elements
    
    def _calculate_structure_metrics(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate structural metrics for the HTML"""
        
        return {
            'total_sections': len(structure['sections']),
            'total_headlines': len(structure['headlines']),
            'total_buttons': len(structure['buttons']),
            'total_forms': len(structure['forms']),
            'total_images': len(structure['images']),
            'conversion_element_count': len(structure['conversion_elements']),
            'has_form': len(structure['forms']) > 0,
            'has_testimonials': 'testimonials' in structure['conversion_elements'],
            'has_guarantee': 'guarantees' in structure['conversion_elements']
        }

class ComponentExtractor:
    """Extracts specific components from HTML for analysis"""
    
    def __init__(self):
        self.parser = HTMLParser()
    
    def extract_sections(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract individual sections with their content"""
        
        sections = []
        
        # Find all section tags
        section_pattern = r'<section[^>]*id="([^"]*)"[^>]*>(.*?)</section>'
        matches = re.findall(section_pattern, html_content, re.DOTALL | re.IGNORECASE)
        
        for section_id, section_content in matches:
            section_data = {
                'id': section_id,
                'content': section_content.strip(),
                'type': self._identify_section_type(section_id, section_content),
                'conversion_elements': self.parser._identify_conversion_elements(section_content),
                'word_count': len(section_content.split()),
                'has_form': '<form' in section_content.lower(),
                'has_button': '<button' in section_content.lower()
            }
            sections.append(section_data)
        
        return sections
    
    def _identify_section_type(self, section_id: str, content: str) -> str:
        """Identify the type of section based on ID and content"""
        
        section_types = {
            'hero': ['hero', 'banner', 'header'],
            'benefits': ['benefits', 'features', 'advantages'],
            'testimonials': ['testimonials', 'reviews', 'social'],
            'form': ['form', 'signup', 'registration'],
            'cta': ['cta', 'action', 'call'],
            'footer': ['footer', 'bottom']
        }
        
        section_id_lower = section_id.lower()
        content_lower = content.lower()
        
        for section_type, keywords in section_types.items():
            if any(keyword in section_id_lower for keyword in keywords):
                return section_type
            if any(keyword in content_lower for keyword in keywords):
                return section_type
        
        return 'generic'