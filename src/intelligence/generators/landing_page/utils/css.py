"""
CSS Generation Utilities
Generates responsive CSS stylesheets for landing pages.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class CSSGenerator:
    """Generates CSS styles for landing pages"""
    
    def __init__(self):
        self.base_styles = self._get_base_styles()
        self.responsive_breakpoints = {
            'mobile': '(max-width: 768px)',
            'tablet': '(min-width: 769px) and (max-width: 1024px)',
            'desktop': '(min-width: 1025px)'
        }
    
    def generate_complete_css(
        self, 
        colors: Dict[str, str], 
        page_config: Dict[str, Any]
    ) -> str:
        """Generate complete CSS stylesheet"""
        
        try:
            css_parts = [
                self._get_css_reset(),
                self._get_base_styles(),
                self._generate_color_variables(colors),
                self._generate_layout_styles(),
                self._generate_component_styles(),
                self._generate_responsive_styles(),
                self._generate_animation_styles(),
                self._generate_utility_classes()
            ]
            
            complete_css = '\n\n'.join(css_parts)
            
            logger.info("✅ Generated complete CSS stylesheet")
            return complete_css
            
        except Exception as e:
            logger.error(f"CSS generation failed: {str(e)}")
            return self._get_fallback_css()
    
    def _get_css_reset(self) -> str:
        """CSS reset and normalize"""
        
        return """
/* CSS Reset */
*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html {
    line-height: 1.15;
    -webkit-text-size-adjust: 100%;
    scroll-behavior: smooth;
}

body {
    margin: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--background-color);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
}

button, input, select, textarea {
    font-family: inherit;
    font-size: 100%;
    line-height: 1.15;
    margin: 0;
    border: none;
    outline: none;
}

a {
    text-decoration: none;
    color: inherit;
}

ul, ol {
    list-style: none;
}"""
    
    def _generate_color_variables(self, colors: Dict[str, str]) -> str:
        """Generate CSS custom properties for colors"""
        
        return f"""
/* Color Variables */
:root {{
    --primary-color: {colors.get('primary', '#2563eb')};
    --secondary-color: {colors.get('secondary', '#1e40af')};
    --accent-color: {colors.get('accent', '#f59e0b')};
    --background-color: {colors.get('background', '#ffffff')};
    --text-color: {colors.get('text', '#1f2937')};
    --text-light: #6b7280;
    --border-color: #e5e7eb;
    --success-color: #10b981;
    --error-color: #ef4444;
    --warning-color: #f59e0b;
    
    /* Gradients */
    --primary-gradient: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    --accent-gradient: linear-gradient(135deg, var(--accent-color) 0%, #d97706 100%);
    
    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}}"""
    
    def _get_base_styles(self) -> str:
        """Base typography and layout styles"""
        
        return """
/* Base Typography */
h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    line-height: 1.2;
    margin-bottom: 0.5em;
    color: var(--text-color);
}

h1 { font-size: 2.5rem; }
h2 { font-size: 2rem; }
h3 { font-size: 1.5rem; }
h4 { font-size: 1.25rem; }
h5 { font-size: 1.125rem; }
h6 { font-size: 1rem; }

p {
    margin-bottom: 1rem;
    color: var(--text-color);
}

.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

/* Base Layout */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.section {
    padding: 5rem 0;
}

.section-title {
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 1rem;
    color: var(--text-color);
}

.section-subtitle {
    font-size: 1.25rem;
    text-align: center;
    color: var(--text-light);
    margin-bottom: 3rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}"""
    
    def _generate_layout_styles(self) -> str:
        """Layout and grid styles"""
        
        return """
/* Layout Styles */
.hero {
    background: var(--primary-gradient);
    color: white;
    padding: 6rem 0;
    position: relative;
    overflow: hidden;
}

.hero-background {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    opacity: 0.1;
    background-image: radial-gradient(circle at 25% 25%, white 2px, transparent 2px),
                      radial-gradient(circle at 75% 75%, white 2px, transparent 2px);
    background-size: 50px 50px;
}

.hero-content {
    position: relative;
    z-index: 2;
    text-align: center;
    max-width: 800px;
    margin: 0 auto;
}

.hero-headline {
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: 1.5rem;
    line-height: 1.1;
}

.hero-subtext {
    font-size: 1.25rem;
    margin-bottom: 2.5rem;
    opacity: 0.9;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.hero-cta-group {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
}

.hero-visual {
    margin-top: 3rem;
    text-align: center;
}

.hero-image-placeholder {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 3rem 2rem;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.hero-icon {
    font-size: 4rem;
    display: block;
    margin-bottom: 1rem;
}

/* Grid Layouts */
.benefits-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 3rem;
}

.testimonials-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
    margin-top: 3rem;
}

.stats-row {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin: 3rem 0;
    flex-wrap: wrap;
}"""
    
    def _generate_component_styles(self) -> str:
        """Component-specific styles"""
        
        return """
/* Button Styles */
.btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 2rem;
    font-size: 1.125rem;
    font-weight: 600;
    border-radius: 8px;
    transition: all 0.2s ease;
    cursor: pointer;
    text-decoration: none;
    border: none;
    line-height: 1;
}

.btn-primary {
    background: var(--accent-color);
    color: white;
    box-shadow: var(--shadow-md);
}

.btn-primary:hover {
    background: #d97706;
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.btn-large {
    padding: 1.25rem 2.5rem;
    font-size: 1.25rem;
}

.btn-form {
    width: 100%;
    justify-content: center;
}

/* Card Styles */
.benefit-card, .testimonial-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: var(--shadow-md);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.benefit-card:hover, .testimonial-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}

.benefit-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    display: block;
}

.benefit-card h3 {
    color: var(--primary-color);
    margin-bottom: 1rem;
}

.benefit-proof {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);
}

.proof-indicator {
    color: var(--success-color);
    font-weight: 500;
    font-size: 0.875rem;
}

/* Testimonial Styles */
.testimonial-stars {
    color: #fbbf24;
    font-size: 1.25rem;
    margin-bottom: 1rem;
}

.testimonial-content blockquote {
    font-style: italic;
    font-size: 1.125rem;
    margin-bottom: 1rem;
    color: var(--text-color);
}

.testimonial-content cite {
    font-weight: 600;
    color: var(--text-light);
}

/* Stats Styles */
.stat-item {
    text-align: center;
}

.stat-number {
    font-size: 3rem;
    font-weight: 800;
    color: var(--primary-color);
    line-height: 1;
}

.stat-label {
    font-size: 1rem;
    color: var(--text-light);
    margin-top: 0.5rem;
}

/* Trust Elements */
.trust-indicators {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    align-items: center;
}

.trust-item {
    font-size: 0.875rem;
    opacity: 0.9;
}

.trust-badges {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 2rem;
}

.trust-badge {
    background: white;
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-color);
    box-shadow: var(--shadow-sm);
}

/* Form Styles */
.form-section {
    background: #f9fafb;
    padding: 5rem 0;
}

.form-container {
    max-width: 600px;
    margin: 0 auto;
    background: white;
    padding: 3rem;
    border-radius: 12px;
    box-shadow: var(--shadow-lg);
}

.form-title {
    font-size: 2rem;
    text-align: center;
    margin-bottom: 0.5rem;
    color: var(--text-color);
}

.form-subtitle {
    text-align: center;
    color: var(--text-light);
    margin-bottom: 2rem;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-input {
    width: 100%;
    padding: 1rem;
    border: 2px solid var(--border-color);
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s ease;
}

.form-input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-help {
    font-size: 0.875rem;
    color: var(--text-light);
    margin-top: 0.5rem;
}

.form-footer {
    text-align: center;
    margin-top: 1.5rem;
    font-size: 0.875rem;
    color: var(--text-light);
}

.privacy-note, .spam-note {
    margin: 0.5rem 0;
}

.privacy-icon {
    margin-right: 0.25rem;
}

.form-benefits {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid var(--border-color);
}

.form-benefits h3 {
    margin-bottom: 1rem;
    color: var(--text-color);
}

.benefit-list {
    list-style: none;
}

.benefit-list li {
    padding: 0.5rem 0;
    color: var(--text-color);
}

/* CTA Section */
.cta-section {
    background: var(--primary-gradient);
    color: white;
    padding: 5rem 0;
    text-align: center;
}

.cta-content {
    max-width: 800px;
    margin: 0 auto;
}

.cta-headline {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.cta-subtext {
    font-size: 1.25rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

.urgency-elements {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin: 2rem 0;
    flex-wrap: wrap;
}

.urgency-item {
    background: rgba(255, 255, 255, 0.1);
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.cta-button-group {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
}

.guarantee-text {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    opacity: 0.9;
}

.guarantee-icon {
    font-size: 1rem;
}

.risk-reversal {
    margin-top: 1.5rem;
    font-size: 0.875rem;
    opacity: 0.8;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
}

/* Footer Styles */
.footer {
    background: #1f2937;
    color: white;
    padding: 3rem 0 1rem;
}

.footer-content {
    display: grid;
    gap: 2rem;
}

.footer-main {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 3rem;
    margin-bottom: 2rem;
}

.footer-brand h3 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.footer-brand p {
    color: #9ca3af;
}

.footer-links {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
}

.footer-column h4 {
    font-size: 1.125rem;
    margin-bottom: 1rem;
    color: white;
}

.footer-column ul li {
    margin-bottom: 0.5rem;
}

.footer-column a {
    color: #9ca3af;
    transition: color 0.2s ease;
}

.footer-column a:hover {
    color: white;
}

.footer-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 2rem;
    border-top: 1px solid #374151;
    font-size: 0.875rem;
    color: #9ca3af;
}"""
    
    def _generate_responsive_styles(self) -> str:
        """Generate responsive CSS for different screen sizes"""
        
        return """
/* Responsive Styles */
@media (max-width: 768px) {
    .hero-headline {
        font-size: 2.5rem;
    }
    
    .hero-subtext {
        font-size: 1.125rem;
    }
    
    .hero-cta-group {
        flex-direction: column;
        width: 100%;
    }
    
    .btn {
        width: 100%;
        justify-content: center;
    }
    
    .section-title {
        font-size: 2rem;
    }
    
    .benefits-grid {
        grid-template-columns: 1fr;
    }
    
    .testimonials-grid {
        grid-template-columns: 1fr;
    }
    
    .stats-row {
        flex-direction: column;
        gap: 2rem;
    }
    
    .footer-main {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
    
    .footer-links {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
    
    .footer-bottom {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
    }
    
    .urgency-elements {
        flex-direction: column;
        gap: 1rem;
    }
}

@media (min-width: 769px) and (max-width: 1024px) {
    .hero-headline {
        font-size: 3rem;
    }
    
    .benefits-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .testimonials-grid {
        grid-template-columns: 1fr;
    }
}

@media (min-width: 1025px) {
    .hero-cta-group {
        flex-direction: row;
        justify-content: center;
    }
    
    .btn {
        width: auto;
    }
}"""
    
    def _generate_animation_styles(self) -> str:
        """Generate CSS animations and transitions"""
        
        return """
/* Animation Styles */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes pulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.05);
    }
}

@keyframes bounce {
    0%, 20%, 53%, 80%, 100% {
        transform: translate3d(0, 0, 0);
    }
    40%, 43% {
        transform: translate3d(0, -10px, 0);
    }
    70% {
        transform: translate3d(0, -5px, 0);
    }
    90% {
        transform: translate3d(0, -2px, 0);
    }
}

/* Animation Classes */
.animate-fade-in-up {
    animation: fadeInUp 0.8s ease-out;
}

.animate-fade-in-down {
    animation: fadeInDown 0.8s ease-out;
}

.animate-slide-in-left {
    animation: slideInLeft 0.8s ease-out;
}

.animate-slide-in-right {
    animation: slideInRight 0.8s ease-out;
}

.animate-pulse {
    animation: pulse 2s infinite;
}

.animate-bounce {
    animation: bounce 1s infinite;
}

/* Hover Animations */
.hover-lift {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hover-lift:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-xl);
}

.hover-scale {
    transition: transform 0.3s ease;
}

.hover-scale:hover {
    transform: scale(1.05);
}

/* Loading Animations */
.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}"""
    
    def _generate_utility_classes(self) -> str:
        """Generate utility CSS classes"""
        
        return """
/* Utility Classes */
.visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

.clearfix::after {
    content: "";
    display: table;
    clear: both;
}

/* Spacing */
.mb-1 { margin-bottom: 0.25rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-3 { margin-bottom: 0.75rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-5 { margin-bottom: 1.25rem; }
.mb-6 { margin-bottom: 1.5rem; }

.mt-1 { margin-top: 0.25rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 0.75rem; }
.mt-4 { margin-top: 1rem; }
.mt-5 { margin-top: 1.25rem; }
.mt-6 { margin-top: 1.5rem; }

.p-1 { padding: 0.25rem; }
.p-2 { padding: 0.5rem; }
.p-3 { padding: 0.75rem; }
.p-4 { padding: 1rem; }
.p-5 { padding: 1.25rem; }
.p-6 { padding: 1.5rem; }

/* Display */
.d-none { display: none; }
.d-block { display: block; }
.d-inline { display: inline; }
.d-inline-block { display: inline-block; }
.d-flex { display: flex; }
.d-grid { display: grid; }

/* Flexbox */
.flex-row { flex-direction: row; }
.flex-col { flex-direction: column; }
.flex-wrap { flex-wrap: wrap; }
.flex-nowrap { flex-wrap: nowrap; }
.justify-start { justify-content: flex-start; }
.justify-center { justify-content: center; }
.justify-end { justify-content: flex-end; }
.justify-between { justify-content: space-between; }
.justify-around { justify-content: space-around; }
.items-start { align-items: flex-start; }
.items-center { align-items: center; }
.items-end { align-items: flex-end; }
.items-stretch { align-items: stretch; }

/* Positioning */
.relative { position: relative; }
.absolute { position: absolute; }
.fixed { position: fixed; }
.sticky { position: sticky; }

/* Width & Height */
.w-full { width: 100%; }
.w-auto { width: auto; }
.h-full { height: 100%; }
.h-auto { height: auto; }

/* Colors */
.text-primary { color: var(--primary-color); }
.text-secondary { color: var(--secondary-color); }
.text-accent { color: var(--accent-color); }
.text-light { color: var(--text-light); }
.text-white { color: white; }
.text-black { color: black; }

.bg-primary { background-color: var(--primary-color); }
.bg-secondary { background-color: var(--secondary-color); }
.bg-accent { background-color: var(--accent-color); }
.bg-white { background-color: white; }
.bg-light { background-color: #f8f9fa; }

/* Borders */
.border { border: 1px solid var(--border-color); }
.border-top { border-top: 1px solid var(--border-color); }
.border-bottom { border-bottom: 1px solid var(--border-color); }
.border-left { border-left: 1px solid var(--border-color); }
.border-right { border-right: 1px solid var(--border-color); }

.rounded { border-radius: 0.375rem; }
.rounded-lg { border-radius: 0.75rem; }
.rounded-xl { border-radius: 1rem; }
.rounded-full { border-radius: 9999px; }

/* Shadows */
.shadow-sm { box-shadow: var(--shadow-sm); }
.shadow-md { box-shadow: var(--shadow-md); }
.shadow-lg { box-shadow: var(--shadow-lg); }
.shadow-xl { box-shadow: var(--shadow-xl); }
.shadow-none { box-shadow: none; }

/* Typography */
.font-light { font-weight: 300; }
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }
.font-extrabold { font-weight: 800; }

.text-xs { font-size: 0.75rem; }
.text-sm { font-size: 0.875rem; }
.text-base { font-size: 1rem; }
.text-lg { font-size: 1.125rem; }
.text-xl { font-size: 1.25rem; }
.text-2xl { font-size: 1.5rem; }
.text-3xl { font-size: 1.875rem; }
.text-4xl { font-size: 2.25rem; }
.text-5xl { font-size: 3rem; }

.uppercase { text-transform: uppercase; }
.lowercase { text-transform: lowercase; }
.capitalize { text-transform: capitalize; }

.italic { font-style: italic; }
.not-italic { font-style: normal; }

/* Opacity */
.opacity-0 { opacity: 0; }
.opacity-25 { opacity: 0.25; }
.opacity-50 { opacity: 0.5; }
.opacity-75 { opacity: 0.75; }
.opacity-100 { opacity: 1; }

/* Overflow */
.overflow-hidden { overflow: hidden; }
.overflow-visible { overflow: visible; }
.overflow-auto { overflow: auto; }
.overflow-scroll { overflow: scroll; }"""
    
    def _get_fallback_css(self) -> str:
        """Generate fallback CSS when generation fails"""
        
        return """
/* Fallback CSS */
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    margin: 0;
    padding: 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.hero {
    background: #2563eb;
    color: white;
    padding: 4rem 0;
    text-align: center;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.hero p {
    font-size: 1.25rem;
    margin-bottom: 2rem;
}

.btn {
    display: inline-block;
    padding: 1rem 2rem;
    background: #f59e0b;
    color: white;
    text-decoration: none;
    border-radius: 8px;
    font-weight: 600;
}

.btn:hover {
    background: #d97706;
}

.section {
    padding: 4rem 0;
}

.text-center {
    text-align: center;
}"""

    def generate_responsive_css(self, breakpoint: str) -> str:
        """Generate CSS for specific breakpoint"""
        
        if breakpoint not in self.responsive_breakpoints:
            return ""
        
        media_query = self.responsive_breakpoints[breakpoint]
        
        if breakpoint == 'mobile':
            return f"""
@media {media_query} {{
    .hero-headline {{ font-size: 2rem; }}
    .section-title {{ font-size: 1.75rem; }}
    .benefits-grid {{ grid-template-columns: 1fr; }}
    .testimonials-grid {{ grid-template-columns: 1fr; }}
    .btn {{ width: 100%; }}
    .stats-row {{ flex-direction: column; }}
}}"""
        
        elif breakpoint == 'tablet':
            return f"""
@media {media_query} {{
    .hero-headline {{ font-size: 2.75rem; }}
    .benefits-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .testimonials-grid {{ grid-template-columns: 1fr; }}
}}"""
        
        elif breakpoint == 'desktop':
            return f"""
@media {media_query} {{
    .hero-cta-group {{ flex-direction: row; }}
    .btn {{ width: auto; }}
}}"""
        
        return ""
    
    def generate_component_css(self, component_type: str, config: Dict[str, Any]) -> str:
        """Generate CSS for specific component"""
        
        if component_type == 'hero':
            return self._generate_hero_css(config)
        elif component_type == 'benefits':
            return self._generate_benefits_css(config)
        elif component_type == 'testimonials':
            return self._generate_testimonials_css(config)
        elif component_type == 'form':
            return self._generate_form_css(config)
        elif component_type == 'cta':
            return self._generate_cta_css(config)
        else:
            return ""
    
    def _generate_hero_css(self, config: Dict[str, Any]) -> str:
        """Generate hero section specific CSS"""
        
        background_color = config.get('background_color', 'var(--primary-color)')
        text_color = config.get('text_color', 'white')
        
        return f"""
.hero-custom {{
    background: {background_color};
    color: {text_color};
    min-height: {config.get('min_height', '600px')};
    display: flex;
    align-items: center;
    justify-content: center;
}}"""
    
    def _generate_benefits_css(self, config: Dict[str, Any]) -> str:
        """Generate benefits section specific CSS"""
        
        columns = config.get('columns', 3)
        
        return f"""
.benefits-grid-custom {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    max-width: {300 * columns + 32 * (columns - 1)}px;
    margin: 0 auto;
}}"""
    
    def _generate_testimonials_css(self, config: Dict[str, Any]) -> str:
        """Generate testimonials section specific CSS"""
        
        layout = config.get('layout', 'grid')
        
        if layout == 'carousel':
            return """
.testimonials-carousel {
    display: flex;
    overflow-x: auto;
    gap: 2rem;
    scroll-snap-type: x mandatory;
    padding-bottom: 1rem;
}

.testimonials-carousel .testimonial-card {
    flex: 0 0 400px;
    scroll-snap-align: start;
}"""
        else:
            return """
.testimonials-grid-custom {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
}"""
    
    def _generate_form_css(self, config: Dict[str, Any]) -> str:
        """Generate form specific CSS"""
        
        style = config.get('style', 'default')
        
        if style == 'inline':
            return """
.form-inline {
    display: flex;
    gap: 1rem;
    align-items: end;
}

.form-inline .form-group {
    flex: 1;
    margin-bottom: 0;
}

.form-inline .btn {
    flex-shrink: 0;
}"""
        else:
            return """
.form-stacked .form-group {
    margin-bottom: 1.5rem;
}"""
    
    def _generate_cta_css(self, config: Dict[str, Any]) -> str:
        """Generate CTA section specific CSS"""
        
        urgency = config.get('urgency', False)
        
        if urgency:
            return """
.cta-urgent {
    animation: pulse 2s infinite;
}

.cta-urgent .urgency-timer {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 600;
    margin-bottom: 1rem;
}"""
        else:
            return ""
    
    def optimize_css(self, css: str) -> str:
        """Optimize CSS by removing unnecessary whitespace and comments"""
        
        import re
        
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        
        # Remove extra whitespace
        css = re.sub(r'\s+', ' ', css)
        
        # Remove whitespace around specific characters
        css = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css)
        
        # Remove trailing semicolons before closing braces
        css = re.sub(r';\s*}', '}', css)
        
        return css.strip()
    
    def generate_critical_css(self, above_fold_selectors: List[str]) -> str:
        """Generate critical CSS for above-the-fold content"""
        
        critical_selectors = [
            'body', 'html', '.container', '.hero', '.hero-content',
            '.hero-headline', '.hero-subtext', '.btn', '.btn-primary'
        ]
        
        # Add user-specified selectors
        critical_selectors.extend(above_fold_selectors)
        
        # This would extract only the CSS rules for critical selectors
        # For simplicity, returning base critical CSS
        return f"""
{self._get_css_reset()}
{self._get_base_styles()}
.hero {{
    background: var(--primary-gradient);
    color: white;
    padding: 6rem 0;
    text-align: center;
}}
.btn {{
    display: inline-flex;
    padding: 1rem 2rem;
    background: var(--accent-color);
    color: white;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
}}"""

# Export the CSS generator
__all__ = ['CSSGenerator']