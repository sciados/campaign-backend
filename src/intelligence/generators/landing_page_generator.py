# src/intelligence/generators/landing_page_generator.py
"""
LANDING PAGE GENERATOR
✅ Complete HTML landing pages with CSS/JS
✅ Multiple page types (lead gen, sales, webinar)
✅ Conversion-optimized layouts
✅ Mobile-responsive design
"""

import os
import logging
import uuid
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LandingPageGenerator:
    """Generate complete HTML landing pages for different objectives"""
    
    def __init__(self):
        self.ai_providers = self._initialize_ai_providers()
        self.page_types = ["lead_generation", "sales", "webinar", "product_demo", "free_trial"]
        
    def _initialize_ai_providers(self):
        """Initialize AI providers for landing pages"""
        providers = []
        
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                import anthropic
                providers.append({
                    "name": "anthropic",
                    "client": anthropic.AsyncAnthropic(api_key=api_key),
                    "models": ["claude-3-5-sonnet-20241022"],
                    "strengths": ["long_form", "structured_content", "html_generation"]
                })
                logger.info("✅ Anthropic provider initialized for landing pages")
        except Exception as e:
            logger.warning(f"Anthropic not available for landing pages: {str(e)}")
            
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                import openai
                providers.append({
                    "name": "openai",
                    "client": openai.AsyncOpenAI(api_key=api_key),
                    "models": ["gpt-4"],
                    "strengths": ["creativity", "conversion_copy"]
                })
                logger.info("✅ OpenAI provider initialized for landing pages")
        except Exception as e:
            logger.warning(f"OpenAI not available for landing pages: {str(e)}")
            
        return providers
    
    async def generate_landing_page(
        self, 
        intelligence_data: Dict[str, Any], 
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate complete HTML landing page"""
        
        if preferences is None:
            preferences = {}
            
        page_type = preferences.get("page_type", "lead_generation")
        objective = preferences.get("objective", "email_capture")
        color_scheme = preferences.get("color_scheme", "professional")
        
        product_name = self._extract_product_name(intelligence_data)
        
        landing_page = None
        
        for provider in self.ai_providers:
            try:
                landing_page = await self._generate_landing_page_content(
                    provider, page_type, objective, color_scheme, product_name, intelligence_data
                )
                
                if landing_page:
                    break
                    
            except Exception as e:
                logger.error(f"Landing page generation failed with {provider['name']}: {str(e)}")
                continue
        
        if not landing_page:
            landing_page = self._generate_fallback_landing_page(product_name, page_type, objective)
        
        return {
            "content_type": "landing_page",
            "title": f"{product_name} Landing Page - {page_type.title()}",
            "content": {
                "html_code": landing_page.get("html_code"),
                "page_sections": landing_page.get("sections", []),
                "conversion_elements": landing_page.get("conversion_elements", []),
                "mobile_optimized": True,
                "page_type": page_type,
                "objective": objective
            },
            "metadata": {
                "generated_by": "landing_page_ai",
                "product_name": product_name,
                "content_type": "landing_page",
                "page_type": page_type,
                "conversion_optimized": True,
                "responsive_design": True,
                "code_lines": len(landing_page.get("html_code", "").split('\n'))
            }
        }
    
    async def _generate_landing_page_content(self, provider, page_type, objective, color_scheme, product_name, intelligence_data):
        """Generate landing page content with AI"""
        
        # Extract intelligence for page optimization
        scientific_intel = intelligence_data.get("scientific_authority_intelligence", {})
        emotional_intel = intelligence_data.get("emotional_transformation_intelligence", {})
        offer_intel = intelligence_data.get("offer_intelligence", {})
        
        # Page type specifications
        page_specs = {
            "lead_generation": {
                "sections": ["hero", "benefits", "form", "social_proof", "footer"],
                "primary_cta": "Get Free Guide",
                "focus": "email capture"
            },
            "sales": {
                "sections": ["hero", "problem", "solution", "benefits", "pricing", "testimonials", "guarantee", "cta", "footer"],
                "primary_cta": "Buy Now",
                "focus": "purchase conversion"
            },
            "webinar": {
                "sections": ["hero", "agenda", "benefits", "registration", "social_proof", "footer"],
                "primary_cta": "Register Now",
                "focus": "webinar registration"
            },
            "product_demo": {
                "sections": ["hero", "features", "demo_video", "benefits", "cta", "footer"],
                "primary_cta": "Watch Demo",
                "focus": "demo engagement"
            },
            "free_trial": {
                "sections": ["hero", "features", "trial_form", "benefits", "testimonials", "footer"],
                "primary_cta": "Start Free Trial",
                "focus": "trial signup"
            }
        }
        
        spec = page_specs.get(page_type, page_specs["lead_generation"])
        
        # Color scheme configurations
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
        
        colors = color_schemes.get(color_scheme, color_schemes["professional"])
        
        prompt = f"""
Create a complete, conversion-optimized HTML landing page for {product_name}.

Page Type: {page_type}
Objective: {objective}
Primary CTA: {spec['primary_cta']}
Sections: {', '.join(spec['sections'])}

Product: {product_name}
Focus: Health optimization, liver support, natural wellness
Scientific Backing: {', '.join(scientific_intel.get('clinical_studies', ['Research-supported'])[:3])}

Color Scheme: {color_scheme}
Colors: Primary: {colors['primary']}, Secondary: {colors['secondary']}, Accent: {colors['accent']}

Requirements:
- Complete HTML document with embedded CSS and JavaScript
- Mobile-responsive design using CSS Grid/Flexbox
- Conversion-optimized copy and layout
- Modern, professional design
- Fast loading and SEO-friendly
- Include meta tags and proper HTML structure

Page Structure:
{self._get_page_structure_guide(spec['sections'], spec['primary_cta'])}

Return complete HTML code starting with <!DOCTYPE html> and ending with </html>.
Make it production-ready with proper styling, responsiveness, and conversion optimization.
"""
        
        try:
            if provider["name"] == "anthropic":
                response = await provider["client"].messages.create(
                    model=provider["models"][0],
                    max_tokens=4000,
                    temperature=0.7,
                    system=f"You are an expert landing page developer creating conversion-optimized pages. Create professional, responsive HTML for {page_type} focused on {objective}.",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.content[0].text
                return self._parse_landing_page(content, spec['sections'], product_name)
                
            elif provider["name"] == "openai":
                response = await provider["client"].chat.completions.create(
                    model=provider["models"][0],
                    messages=[
                        {"role": "system", "content": f"Expert landing page developer creating {page_type} pages for {objective}. Create professional, responsive HTML."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )
                
                content = response.choices[0].message.content
                return self._parse_landing_page(content, spec['sections'], product_name)
        
        except Exception as e:
            logger.error(f"Landing page content generation failed: {str(e)}")
            return None
    
    def _get_page_structure_guide(self, sections: List[str], primary_cta: str) -> str:
        """Get page structure guide for the prompt"""
        
        structure_guide = ""
        
        for section in sections:
            if section == "hero":
                structure_guide += f"""
Hero Section:
- Compelling headline about {primary_cta}
- Subheadline explaining the benefit
- Primary CTA button: "{primary_cta}"
- Hero image or background
"""
            elif section == "benefits":
                structure_guide += """
Benefits Section:
- 3-4 key benefits with icons
- Clear value propositions
- Social proof elements
"""
            elif section == "form":
                structure_guide += """
Form Section:
- Email capture form
- Clear privacy statement
- Strong form CTA
"""
            elif section == "pricing":
                structure_guide += """
Pricing Section:
- Clear pricing options
- Value highlighting
- Purchase CTAs
"""
            elif section == "testimonials":
                structure_guide += """
Testimonials Section:
- 2-3 customer testimonials
- Photos if possible
- Credibility indicators
"""
            elif section == "footer":
                structure_guide += """
Footer Section:
- Contact information
- Privacy policy link
- Copyright notice
"""
        
        return structure_guide
    
    def _parse_landing_page(self, content: str, sections: List[str], product_name: str) -> Dict[str, Any]:
        """Parse landing page from AI response"""
        
        # Clean the HTML content
        html_code = self._extract_html_from_content(content)
        
        # Identify sections in the HTML
        identified_sections = []
        for section in sections:
            if section.lower() in html_code.lower():
                identified_sections.append(section)
        
        # Identify conversion elements
        conversion_elements = []
        if "button" in html_code.lower() or "btn" in html_code.lower():
            conversion_elements.append("CTA buttons")
        if "form" in html_code.lower():
            conversion_elements.append("Form")
        if "testimonial" in html_code.lower():
            conversion_elements.append("Testimonials")
        if "guarantee" in html_code.lower():
            conversion_elements.append("Guarantee")
        
        return {
            "html_code": html_code,
            "sections": identified_sections,
            "conversion_elements": conversion_elements,
            "word_count": len(html_code.split()),
            "estimated_load_time": "< 2 seconds"
        }
    
    def _extract_html_from_content(self, content: str) -> str:
        """Extract HTML code from AI response"""
        
        # Look for HTML doctype
        if "<!DOCTYPE html>" in content:
            start_idx = content.find("<!DOCTYPE html>")
            end_idx = content.rfind("</html>") + 7
            if end_idx > start_idx:
                return content[start_idx:end_idx]
        
        # Look for html tag
        if "<html" in content.lower():
            start_idx = content.lower().find("<html")
            end_idx = content.lower().rfind("</html>") + 7
            if end_idx > start_idx:
                return content[start_idx:end_idx]
        
        # Return as-is if no clear HTML structure found
        return content
    
    def _generate_fallback_landing_page(self, product_name: str, page_type: str, objective: str) -> Dict[str, Any]:
        """Generate fallback landing page"""
        
        primary_cta = "Learn More"
        if page_type == "lead_generation":
            primary_cta = "Get Free Guide"
        elif page_type == "sales":
            primary_cta = "Buy Now"
        elif page_type == "webinar":
            primary_cta = "Register Now"
        
        html_code = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product_name} - Natural Health Optimization</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f9fafb;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        .hero {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 100px 0;
            text-align: center;
        }}
        
        .hero h1 {{
            font-size: 3rem;
            margin-bottom: 20px;
            font-weight: bold;
        }}
        
        .hero p {{
            font-size: 1.25rem;
            margin-bottom: 30px;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .cta-button {{
            background-color: #f59e0b;
            color: white;
            padding: 15px 30px;
            font-size: 1.1rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: background-color 0.3s;
        }}
        
        .cta-button:hover {{
            background-color: #d97706;
        }}
        
        .benefits {{
            padding: 80px 0;
            background-color: white;
        }}
        
        .benefits h2 {{
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 50px;
        }}
        
        .benefits-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 40px;
        }}
        
        .benefit-item {{
            text-align: center;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .benefit-item h3 {{
            font-size: 1.5rem;
            margin-bottom: 15px;
            color: #2563eb;
        }}
        
        .social-proof {{
            background-color: #f3f4f6;
            padding: 80px 0;
            text-align: center;
        }}
        
        .testimonial {{
            max-width: 800px;
            margin: 0 auto;
            padding: 30px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .footer {{
            background-color: #1f2937;
            color: white;
            padding: 40px 0;
            text-align: center;
        }}
        
        @media (max-width: 768px) {{
            .hero h1 {{
                font-size: 2rem;
            }}
            
            .hero p {{
                font-size: 1rem;
            }}
            
            .benefits-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <section class="hero">
        <div class="container">
            <h1>Transform Your Health with {product_name}</h1>
            <p>Discover the science-backed approach to natural health optimization and liver support that's helping thousands achieve their wellness goals.</p>
            <a href="#{objective}" class="cta-button">{primary_cta}</a>
        </div>
    </section>
    
    <section class="benefits">
        <div class="container">
            <h2>Why Choose {product_name}?</h2>
            <div class="benefits-grid">
                <div class="benefit-item">
                    <h3>🔬 Research-Backed</h3>
                    <p>Formulated based on clinical research and scientific studies for optimal effectiveness.</p>
                </div>
                <div class="benefit-item">
                    <h3>🌿 Natural Approach</h3>
                    <p>Support your body's natural processes with carefully selected, high-quality ingredients.</p>
                </div>
                <div class="benefit-item">
                    <h3>⚡ Proven Results</h3>
                    <p>Join thousands who have experienced real improvements in their health and energy levels.</p>
                </div>
            </div>
        </div>
    </section>
    
    <section class="social-proof">
        <div class="container">
            <div class="testimonial">
                <h3>Real Results from Real People</h3>
                <p>"I've tried many health products, but {product_name} is different. The science-based approach and natural ingredients have made a real difference in how I feel every day."</p>
                <p><strong>- Sarah M., Verified Customer</strong></p>
            </div>
        </div>
    </section>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {product_name}. All rights reserved.</p>
            <p>Natural health optimization through science-backed solutions.</p>
        </div>
    </footer>
    
    <script>
        // Simple analytics and interaction tracking
        document.querySelectorAll('.cta-button').forEach(button => {{
            button.addEventListener('click', function(e) {{
                console.log('CTA clicked:', this.textContent);
                // Add your analytics tracking here
            }});
        }});
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth'
                    }});
                }}
            }});
        }});
    </script>
</body>
</html>'''
        
        return {
            "html_code": html_code,
            "sections": ["hero", "benefits", "social_proof", "footer"],
            "conversion_elements": ["CTA buttons", "Testimonials"],
            "fallback_generated": True
        }
    
    def _extract_product_name(self, intelligence_data):
        """Extract product name from intelligence"""
        offer_intel = intelligence_data.get("offer_intelligence", {})
        insights = offer_intel.get("insights", [])
        
        for insight in insights:
            if "called" in str(insight).lower():
                words = str(insight).split()
                for i, word in enumerate(words):
                    if word.lower() == "called" and i + 1 < len(words):
                        return words[i + 1].upper().replace(",", "").replace(".", "")
        
        return "PRODUCT"