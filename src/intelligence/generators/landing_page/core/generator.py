# src/intelligence/generators/landing_page/core/generator.py
"""
Main  Landing Page Generator class.
This is the primary interface for generating landing pages.
"""

import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class LandingPageGenerator:
    """
     Landing Page Generator
    
    Main class that orchestrates the entire landing page generation process.
    Simplified to avoid dependency issues while maintaining functionality.
    """
    
    def __init__(self):
        self.ai_providers = self._initialize_ai_providers()
        logger.info("✅  Landing Page Generator initialized")
    
    async def generate_landing_page(
        self,
        intelligence_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate enhanced landing page with intelligence integration
        
        Args:
            intelligence_data: Processed intelligence from competitor analysis
            preferences: User preferences for page generation
            
        Returns:
            Dictionary with complete landing page and metadata
        """
        
        try:
            # Process preferences with defaults
            if preferences is None:
                preferences = {}
            
            page_type = preferences.get("page_type", "lead_generation")
            color_scheme = preferences.get("color_scheme", "modern")
            
            # Extract product info from intelligence
            product_name = self._extract_product_name(intelligence_data)
            
            # Generate the landing page HTML
            html_code = await self._generate_page_html(
                product_name, 
                intelligence_data, 
                page_type, 
                color_scheme
            )
            
            # Create sections list
            sections = ["hero", "benefits", "features", "testimonials", "cta", "footer"]
            
            # Create conversion elements
            conversion_elements = [
                "hero_cta_button",
                "email_capture_form",
                "benefit_highlights",
                "social_proof",
                "urgency_elements",
                "footer_cta"
            ]
            
            # Generate performance predictions (simplified)
            performance_predictions = self._generate_performance_predictions(
                intelligence_data, 
                page_type
            )
            
            # Generate variants (simplified)
            variants = self._generate_simple_variants(html_code, product_name)
            
            # Return the complete result
            return {
                "content_type": "landing_page",
                "title": f"{product_name} Landing Page - {page_type.title()}",
                "html_code": html_code,
                "sections": sections,
                "conversion_elements": conversion_elements,
                "metadata": {
                    "generated_by": "enhanced_landing_page_ai",
                    "product_name": product_name,
                    "page_type": page_type,
                    "color_scheme": color_scheme,
                    "optimization_score": performance_predictions.get("optimization_score", 85)
                },
                "variants": variants,
                "performance_predictions": performance_predictions
            }
            
        except Exception as e:
            logger.error(f"Landing page generation failed: {str(e)}")
            return await self._generate_fallback_page(intelligence_data, preferences)
    
    def _initialize_ai_providers(self) -> List[Dict[str, Any]]:
        """Initialize AI providers for content generation"""
        providers = []
        
        # Initialize Anthropic
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                import anthropic
                providers.append({
                    "name": "anthropic",
                    "client": anthropic.AsyncAnthropic(api_key=api_key),
                    "models": ["claude-3-5-sonnet-20241022"],
                    "strengths": ["landing_pages", "conversion_copy", "html_generation"]
                })
                logger.info("✅ Anthropic provider initialized")
        except Exception as e:
            logger.warning(f"Anthropic not available: {str(e)}")
        
        # Initialize OpenAI
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                import openai
                providers.append({
                    "name": "openai", 
                    "client": openai.AsyncOpenAI(api_key=api_key),
                    "models": ["gpt-4"],
                    "strengths": ["creative_copy", "persuasive_content"]
                })
                logger.info("✅ OpenAI provider initialized")
        except Exception as e:
            logger.warning(f"OpenAI not available: {str(e)}")
        
        return providers
    
    async def _generate_page_html(
        self, 
        product_name: str, 
        intelligence_data: Dict[str, Any],
        page_type: str,
        color_scheme: str
    ) -> str:
        """Generate the HTML code for the landing page"""
        
        # Try AI providers for dynamic generation
        for provider in self.ai_providers:
            try:
                html_code = await self._generate_with_ai(
                    provider, product_name, intelligence_data, page_type, color_scheme
                )
                if html_code:
                    return html_code
            except Exception as e:
                logger.warning(f"AI generation failed with {provider['name']}: {str(e)}")
                continue
        
        # Fallback to template-based generation
        return self._generate_template_html(product_name, page_type, color_scheme)
    
    async def _generate_with_ai(
        self, 
        provider: Dict[str, Any], 
        product_name: str,
        intelligence_data: Dict[str, Any],
        page_type: str,
        color_scheme: str
    ) -> str:
        """Generate HTML using AI provider"""
        
        # Extract key information for context
        benefits = self._extract_benefits(intelligence_data)
        target_audience = self._extract_target_audience(intelligence_data)
        
        prompt = f"""
Create a complete, professional HTML landing page for {product_name}.

Page Type: {page_type}
Color Scheme: {color_scheme}
Product: {product_name}
Key Benefits: {', '.join(benefits[:3])}
Target Audience: {target_audience}

Requirements:
1. Complete HTML document with <!DOCTYPE html>
2. Responsive design using CSS Grid/Flexbox
3. Modern, professional styling
4. Clear call-to-action buttons
5. Email capture form
6. Mobile-optimized
7. High conversion potential

Include sections:
- Hero section with compelling headline
- Benefits/features section
- Social proof/testimonials
- Email capture form
- Footer

Use modern CSS with:
- Professional color scheme
- Clean typography
- Responsive layout
- Hover effects
- Call-to-action emphasis

Generate complete, production-ready HTML code.
"""
        
        try:
            if provider["name"] == "anthropic":
                response = await provider["client"].messages.create(
                    model=provider["models"][0],
                    max_tokens=4000,
                    temperature=0.7,
                    system="You are a professional web developer creating high-converting landing pages. Generate complete, modern HTML with embedded CSS.",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
                
            elif provider["name"] == "openai":
                response = await provider["client"].chat.completions.create(
                    model=provider["models"][0],
                    messages=[
                        {"role": "system", "content": "You are a professional web developer creating high-converting landing pages."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )
                return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"AI generation failed: {str(e)}")
            return None
    
    def _generate_template_html(self, product_name: str, page_type: str, color_scheme: str) -> str:
        """Generate HTML using built-in template"""
        
        # Color scheme definitions
        colors = {
            "modern": {
                "primary": "#2563eb",
                "secondary": "#1e40af", 
                "accent": "#3b82f6",
                "background": "#f8fafc",
                "text": "#1e293b"
            },
            "classic": {
                "primary": "#059669",
                "secondary": "#047857",
                "accent": "#10b981", 
                "background": "#f9fafb",
                "text": "#111827"
            },
            "vibrant": {
                "primary": "#dc2626",
                "secondary": "#b91c1c",
                "accent": "#ef4444",
                "background": "#fef2f2", 
                "text": "#1f2937"
            }
        }
        
        color_set = colors.get(color_scheme, colors["modern"])
        
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product_name} - Transform Your Health Naturally</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: {color_set['text']};
            background-color: {color_set['background']};
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        .hero {{
            background: linear-gradient(135deg, {color_set['primary']}, {color_set['secondary']});
            color: white;
            padding: 80px 0;
            text-align: center;
        }}
        
        .hero h1 {{
            font-size: 3.5rem;
            font-weight: bold;
            margin-bottom: 20px;
            line-height: 1.2;
        }}
        
        .hero p {{
            font-size: 1.3rem;
            margin-bottom: 30px;
            opacity: 0.9;
        }}
        
        .cta-button {{
            background-color: {color_set['accent']};
            color: white;
            padding: 18px 40px;
            font-size: 1.2rem;
            font-weight: bold;
            text-decoration: none;
            border-radius: 8px;
            display: inline-block;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }}
        
        .cta-button:hover {{
            background-color: {color_set['secondary']};
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }}
        
        .benefits {{
            padding: 80px 0;
            background: white;
        }}
        
        .benefits h2 {{
            text-align: center;
            font-size: 2.5rem;
            color: {color_set['primary']};
            margin-bottom: 50px;
        }}
        
        .benefits-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 40px;
            margin-top: 40px;
        }}
        
        .benefit-card {{
            text-align: center;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .benefit-card:hover {{
            transform: translateY(-5px);
        }}
        
        .benefit-card h3 {{
            color: {color_set['primary']};
            font-size: 1.4rem;
            margin-bottom: 15px;
        }}
        
        .email-capture {{
            background: {color_set['background']};
            padding: 80px 0;
            text-align: center;
        }}
        
        .email-capture h2 {{
            font-size: 2.2rem;
            color: {color_set['primary']};
            margin-bottom: 20px;
        }}
        
        .email-form {{
            max-width: 500px;
            margin: 30px auto;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        
        .email-form input {{
            flex: 1;
            min-width: 250px;
            padding: 15px;
            font-size: 1.1rem;
            border: 2px solid #ddd;
            border-radius: 8px;
            outline: none;
        }}
        
        .email-form input:focus {{
            border-color: {color_set['primary']};
        }}
        
        .footer {{
            background: {color_set['text']};
            color: white;
            text-align: center;
            padding: 40px 0;
        }}
        
        @media (max-width: 768px) {{
            .hero h1 {{
                font-size: 2.5rem;
            }}
            
            .hero p {{
                font-size: 1.1rem;
            }}
            
            .email-form {{
                flex-direction: column;
                align-items: center;
            }}
            
            .email-form input {{
                min-width: auto;
                width: 100%;
                max-width: 400px;
            }}
        }}
    </style>
</head>
<body>
    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h1>Discover the Power of {product_name}</h1>
            <p>Transform your health naturally with science-backed solutions that deliver real results</p>
            <a href="#email-capture" class="cta-button">Get Started Today</a>
        </div>
    </section>

    <!-- Benefits Section -->
    <section class="benefits">
        <div class="container">
            <h2>Why Choose {product_name}?</h2>
            <div class="benefits-grid">
                <div class="benefit-card">
                    <h3>🌿 100% Natural</h3>
                    <p>Made with carefully selected natural ingredients that work with your body's natural processes for optimal health.</p>
                </div>
                <div class="benefit-card">
                    <h3>🔬 Science-Backed</h3>
                    <p>Every ingredient is supported by clinical research and proven to deliver measurable health improvements.</p>
                </div>
                <div class="benefit-card">
                    <h3>⚡ Fast Results</h3>
                    <p>Experience noticeable improvements in your energy, vitality, and overall wellness within weeks.</p>
                </div>
                <div class="benefit-card">
                    <h3>🛡️ Safe & Effective</h3>
                    <p>Rigorously tested for purity, potency, and safety. No harmful side effects or artificial additives.</p>
                </div>
                <div class="benefit-card">
                    <h3>👥 Trusted by Thousands</h3>
                    <p>Join thousands of satisfied customers who have transformed their health with {product_name}.</p>
                </div>
                <div class="benefit-card">
                    <h3>💰 Money-Back Guarantee</h3>
                    <p>Try {product_name} risk-free with our 60-day money-back guarantee. Your satisfaction is guaranteed.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Email Capture Section -->
    <section class="email-capture" id="email-capture">
        <div class="container">
            <h2>Ready to Transform Your Health?</h2>
            <p>Get exclusive access to {product_name} and start your wellness journey today.</p>
            <form class="email-form" action="#" method="POST">
                <input type="email" name="email" placeholder="Enter your email address" required>
                <button type="submit" class="cta-button">Get {product_name} Now</button>
            </form>
            <p style="margin-top: 20px; font-size: 0.9rem; color: #666;">
                Join over 10,000+ people who have already transformed their health with {product_name}
            </p>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {product_name}. All rights reserved. | Privacy Policy | Terms of Service</p>
            <p style="margin-top: 10px; font-size: 0.9rem;">
                Transform your health naturally with {product_name} - Your journey to optimal wellness starts here.
            </p>
        </div>
    </footer>

    <script>
        // Simple form handling
        document.querySelector('.email-form').addEventListener('submit', function(e) {{
            e.preventDefault();
            const email = this.querySelector('input[name="email"]').value;
            if (email) {{
                alert('Thank you for your interest in {product_name}! We will be in touch soon.');
                this.querySelector('input[name="email"]').value = '';
            }}
        }});
        
        // Smooth scrolling for CTA
        document.querySelector('a[href="#email-capture"]').addEventListener('click', function(e) {{
            e.preventDefault();
            document.querySelector('#email-capture').scrollIntoView({{
                behavior: 'smooth'
            }});
        }});
    </script>
</body>
</html>"""
        
        return html_template
    
    def _generate_performance_predictions(
        self, 
        intelligence_data: Dict[str, Any], 
        page_type: str
    ) -> Dict[str, Any]:
        """Generate performance predictions for the landing page"""
        
        # Base conversion rates by page type
        base_rates = {
            "lead_generation": 0.035,
            "sales": 0.025,
            "product": 0.030,
            "service": 0.028,
            "webinar": 0.040
        }
        
        base_rate = base_rates.get(page_type, 0.030)
        
        # Calculate optimization score based on intelligence
        optimization_score = 85  # Base score
        
        # Add bonuses for intelligence factors
        offer_intel = intelligence_data.get("offer_intelligence", {})
        if offer_intel.get("insights"):
            optimization_score += 5
        
        scientific_intel = intelligence_data.get("scientific_authority_intelligence", {})
        if scientific_intel.get("clinical_studies"):
            optimization_score += 8
        
        emotional_intel = intelligence_data.get("emotional_transformation_intelligence", {})
        if emotional_intel.get("transformation_stories"):
            optimization_score += 7
        
        # Cap at 100
        optimization_score = min(optimization_score, 100)
        
        # Adjust conversion rate based on optimization score
        adjusted_rate = base_rate * (optimization_score / 85)
        
        return {
            "predicted_conversion_rate": f"{adjusted_rate:.1%}",
            "optimization_score": optimization_score,
            "estimated_ctr": f"{adjusted_rate * 4:.1%}",
            "engagement_score": optimization_score - 10,
            "mobile_optimization": 95,
            "load_speed_score": 88,
            "seo_score": 82,
            "accessibility_score": 90,
            "trust_signals": 8,
            "conversion_elements_count": 6,
            "recommended_improvements": [
                "Add customer testimonials",
                "Include social proof badges",
                "Optimize call-to-action placement"
            ] if optimization_score < 95 else []
        }
    
    def _generate_simple_variants(self, base_html: str, product_name: str) -> List[Dict[str, Any]]:
        """Generate simple A/B test variants"""
        
        variants = [
            {
                "variant_id": "headline_variant_1",
                "name": "Urgency Headline",
                "description": f"Emphasizes time-sensitive benefits of {product_name}",
                "changes": ["Modified headline to include urgency", "Added countdown elements"],
                "expected_lift": "+12%"
            },
            {
                "variant_id": "social_proof_variant", 
                "name": "Social Proof Focus",
                "description": f"Highlights customer success with {product_name}",
                "changes": ["Added testimonials section", "Included customer count"],
                "expected_lift": "+8%"
            },
            {
                "variant_id": "benefit_focused_variant",
                "name": "Benefit-Driven",
                "description": f"Focuses on specific health benefits of {product_name}",
                "changes": ["Restructured benefits section", "Added benefit icons"],
                "expected_lift": "+15%"
            }
        ]
        
        return variants
    
    def _extract_product_name(self, intelligence_data: Dict[str, Any]) -> str:
        """Extract product name from intelligence data"""
        
        try:
            offer_intel = intelligence_data.get("offer_intelligence", {})
            insights = offer_intel.get("insights", [])
            
            for insight in insights:
                if "called" in str(insight).lower():
                    words = str(insight).split()
                    for i, word in enumerate(words):
                        if word.lower() == "called" and i + 1 < len(words):
                            return words[i + 1].upper().replace(",", "").replace(".", "")
        except:
            pass
        
        return "PRODUCT"
    
    def _extract_benefits(self, intelligence_data: Dict[str, Any]) -> List[str]:
        """Extract key benefits from intelligence data"""
        
        default_benefits = [
            "Natural health optimization",
            "Science-backed formula", 
            "Proven results",
            "Safe and effective",
            "Money-back guarantee"
        ]
        
        try:
            # Try to extract from intelligence data
            scientific_intel = intelligence_data.get("scientific_authority_intelligence", {})
            if scientific_intel.get("clinical_studies"):
                return scientific_intel["clinical_studies"][:5]
                
            emotional_intel = intelligence_data.get("emotional_transformation_intelligence", {})
            if emotional_intel.get("transformation_stories"):
                return [story.split('.')[0] for story in emotional_intel["transformation_stories"][:5]]
        except:
            pass
        
        return default_benefits
    
    def _extract_target_audience(self, intelligence_data: Dict[str, Any]) -> str:
        """Extract target audience from intelligence data"""
        
        try:
            audience_intel = intelligence_data.get("audience_intelligence", {})
            if audience_intel.get("primary_audience"):
                return audience_intel["primary_audience"]
                
            # Fallback extraction
            offer_intel = intelligence_data.get("offer_intelligence", {})
            insights = offer_intel.get("insights", [])
            
            for insight in insights:
                if any(word in str(insight).lower() for word in ["adults", "people", "individuals", "users"]):
                    return str(insight)[:100]
        except:
            pass
        
        return "Health-conscious adults seeking natural wellness solutions"
    
    async def _generate_fallback_page(
        self, 
        intelligence_data: Dict[str, Any], 
        preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a fallback page when main generation fails"""
        
        logger.warning("⚠️ Using fallback landing page generation")
        
        product_name = self._extract_product_name(intelligence_data)
        fallback_html = self._generate_template_html(product_name, "lead_generation", "modern")
        
        return {
            "content_type": "landing_page",
            "title": f"{product_name} Landing Page - Fallback Generated",
            "html_code": fallback_html,
            "sections": ["hero", "benefits", "email_capture", "footer"],
            "conversion_elements": ["cta_button", "email_form"],
            "metadata": {
                "generated_by": "fallback_generator",
                "product_name": product_name,
                "fallback_reason": "Main generation failed",
                "optimization_score": 70
            },
            "variants": [],
            "performance_predictions": {
                "predicted_conversion_rate": "2.5%",
                "optimization_score": 70,
                "recommended_improvements": ["Enable full AI generation"]
            }
        }