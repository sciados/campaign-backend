"""
HTML Generation Utilities
Provides HTML structure building and optimization tools.
"""

import logging
import re
from typing import Dict, List, Any, Optional
from html import escape

logger = logging.getLogger(__name__)

class HTMLStructureBuilder:
    """Builds complete HTML document structure"""
    
    def __init__(self):
        self.meta_tags = {
            'charset': '<meta charset="UTF-8">',
            'viewport': '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            'robots': '<meta name="robots" content="index, follow">',
            'description': '<meta name="description" content="{description}">',
            'keywords': '<meta name="keywords" content="{keywords}">',
            'og_title': '<meta property="og:title" content="{title}">',
            'og_description': '<meta property="og:description" content="{description}">',
            'og_type': '<meta property="og:type" content="website">',
            'twitter_card': '<meta name="twitter:card" content="summary_large_image">'
        }
    
    def build_complete_html(
        self,
        sections_html: List[str],
        css_styles: str,
        javascript_code: str,
        product_info: Dict[str, Any],
        page_config: Dict[str, Any]
    ) -> str:
        """Build complete HTML document"""
        
        # Generate meta tags
        meta_html = self._generate_meta_tags(product_info, page_config)
        
        # Build HTML structure
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    {meta_html}
    <title>{escape(product_info.get('name', 'Landing Page'))} - {escape(page_config.get('primary_cta', 'Get Started'))}</title>
    
    <!-- Preconnect to external domains -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- AOS Animation Library -->
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    
    <style>
        {css_styles}
    </style>
</head>
<body>
    <!-- Page Content -->
    {chr(10).join(sections_html)}
    
    <!-- Scripts -->
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <script>
        // Initialize AOS animations
        AOS.init({{
            duration: 800,
            easing: 'ease-in-out',
            once: true,
            offset: 100
        }});
        
        {javascript_code}
    </script>
    
    <!-- Analytics placeholder -->
    <script>
        // Add your analytics tracking code here
        // Google Analytics, Facebook Pixel, etc.
    </script>
</body>
</html>"""
        
        return html_template
    
    def _generate_meta_tags(
        self, 
        product_info: Dict[str, Any], 
        page_config: Dict[str, Any]
    ) -> str:
        """Generate meta tags for SEO and social sharing"""
        
        product_name = product_info.get('name', 'Product')
        primary_benefit = product_info.get('benefits', ['Better results'])[0] if product_info.get('benefits') else 'Better results'
        
        description = f"Discover {product_name} - the solution that delivers {primary_benefit}. {page_config.get('primary_cta', 'Get started')} today!"
        keywords = f"{product_name}, {primary_benefit}, {page_config.get('focus', 'solution')}"
        
        meta_html_parts = [
            self.meta_tags['charset'],
            self.meta_tags['viewport'],
            self.meta_tags['robots'],
            self.meta_tags['description'].format(description=escape(description)),
            self.meta_tags['keywords'].format(keywords=escape(keywords)),
            self.meta_tags['og_title'].format(title=escape(f"{product_name} - {primary_benefit}")),
            self.meta_tags['og_description'].format(description=escape(description)),
            self.meta_tags['og_type'],
            self.meta_tags['twitter_card']
        ]
        
        return '\n    '.join(meta_html_parts)
    
    def build_section_wrapper(
        self, 
        section_id: str, 
        section_content: str, 
        section_classes: List[str] = None
    ) -> str:
        """Build section wrapper with proper structure"""
        
        classes = ['section'] + (section_classes or [])
        class_attr = ' '.join(classes)
        
        return f'''
<section id="{section_id}" class="{class_attr}">
    <div class="container">
        {section_content}
    </div>
</section>'''
    
    def build_responsive_image(
        self, 
        src: str, 
        alt: str, 
        classes: List[str] = None,
        lazy_load: bool = True
    ) -> str:
        """Build responsive image with optimization"""
        
        img_classes = ' '.join(classes or ['responsive-image'])
        loading_attr = 'loading="lazy"' if lazy_load else ''
        
        return f'<img src="{escape(src)}" alt="{escape(alt)}" class="{img_classes}" {loading_attr}>'
    
    def build_cta_button(
        self, 
        text: str, 
        action: str = "button",
        classes: List[str] = None,
        data_track: str = None
    ) -> str:
        """Build CTA button with proper attributes"""
        
        btn_classes = ['btn', 'btn-primary'] + (classes or [])
        class_attr = ' '.join(btn_classes)
        
        if action == "link":
            track_attr = f'data-track="{data_track}"' if data_track else ''
            return f'<a href="#form" class="{class_attr}" {track_attr}>{escape(text)}</a>'
        else:
            track_attr = f'data-track="{data_track}"' if data_track else ''
            return f'<button type="button" class="{class_attr}" onclick="scrollToForm()" {track_attr}>{escape(text)}</button>'

class HTMLOptimizer:
    """Optimizes HTML for performance and SEO"""
    
    def __init__(self):
        self.optimization_rules = {
            'minify_whitespace': True,
            'optimize_images': True,
            'inline_critical_css': False,
            'defer_non_critical_js': True,
            'add_schema_markup': True
        }
    
    def optimize_html(self, html_content: str, optimizations: Dict[str, bool] = None) -> str:
        """Apply HTML optimizations"""
        
        if optimizations:
            self.optimization_rules.update(optimizations)
        
        optimized_html = html_content
        
        try:
            if self.optimization_rules.get('minify_whitespace'):
                optimized_html = self._minify_whitespace(optimized_html)
            
            if self.optimization_rules.get('optimize_images'):
                optimized_html = self._optimize_images(optimized_html)
            
            if self.optimization_rules.get('add_schema_markup'):
                optimized_html = self._add_schema_markup(optimized_html)
            
            logger.info("✅ HTML optimization completed")
            return optimized_html
            
        except Exception as e:
            logger.error(f"HTML optimization failed: {str(e)}")
            return html_content
    
    def _minify_whitespace(self, html: str) -> str:
        """Minify HTML whitespace while preserving structure"""
        
        # Remove extra whitespace between tags
        html = re.sub(r'>\s+<', '><', html)
        
        # Remove leading/trailing whitespace on lines
        lines = [line.strip() for line in html.split('\n') if line.strip()]
        
        return '\n'.join(lines)
    
    def _optimize_images(self, html: str) -> str:
        """Add image optimization attributes"""
        
        # Add loading="lazy" to images that don't have it
        html = re.sub(
            r'<img(?![^>]*loading=)([^>]*)>',
            r'<img\1 loading="lazy">',
            html
        )
        
        # Add width and height attributes for CLS prevention
        # This is a simplified version - in practice, you'd analyze actual images
        html = re.sub(
            r'<img(?![^>]*(?:width=|height=))([^>]*class="[^"]*hero[^"]*"[^>]*)>',
            r'<img\1 width="800" height="600">',
            html
        )
        
        return html
    
    def _add_schema_markup(self, html: str) -> str:
        """Add JSON-LD schema markup for SEO"""
        
        schema_markup = '''
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "Landing Page",
        "description": "Product landing page with conversion optimization",
        "url": "https://example.com",
        "mainEntity": {
            "@type": "Product",
            "name": "Product Name",
            "description": "Product description",
            "offers": {
                "@type": "Offer",
                "availability": "https://schema.org/InStock",
                "price": "0",
                "priceCurrency": "USD"
            }
        }
    }
    </script>'''
        
        # Insert before closing </head> tag
        html = html.replace('</head>', f'{schema_markup}\n</head>')
        
        return html
    
    def validate_html(self, html_content: str) -> Dict[str, Any]:
        """Validate HTML structure and accessibility"""
        
        validation_results = {
            'valid_structure': True,
            'accessibility_score': 85,
            'performance_score': 90,
            'seo_score': 88,
            'issues': [],
            'recommendations': []
        }
        
        # Check for basic structure
        if '<html' not in html_content:
            validation_results['issues'].append('Missing HTML tag')
            validation_results['valid_structure'] = False
        
        if '<head>' not in html_content:
            validation_results['issues'].append('Missing head section')
        
        if '<title>' not in html_content:
            validation_results['issues'].append('Missing title tag')
            validation_results['seo_score'] -= 10
        
        # Check for accessibility
        if 'alt=' not in html_content and '<img' in html_content:
            validation_results['issues'].append('Images missing alt attributes')
            validation_results['accessibility_score'] -= 15
        
        # Check for performance
        if 'loading="lazy"' not in html_content and '<img' in html_content:
            validation_results['recommendations'].append('Add lazy loading to images')
            validation_results['performance_score'] -= 5
        
        return validation_results