# src/intelligence/generators/landing_page/components/sections.py
"""
Individual section builders for landing page components.
Each section type has its own dedicated builder class.
"""

from typing import Dict, List, Any
from abc import ABC, abstractmethod

class SectionBuilder(ABC):
    """Abstract base class for section builders"""
    
    @abstractmethod
    def build(self, **kwargs) -> str:
        """Build the HTML for this section"""
        pass
    
    @abstractmethod
    def get_conversion_elements(self) -> List[str]:
        """Get conversion elements for this section"""
        pass

class HeroSectionBuilder(SectionBuilder):
    """Builder for hero sections"""
    
    def build(
        self,
        product_info: Dict[str, Any],
        conversion_intelligence: Dict[str, Any],
        colors: Dict[str, Any],
        niche_context: Dict[str, Any],
        page_config: Dict[str, Any]
    ) -> str:
        """Build conversion-optimized hero section"""
        
        product_name = product_info['name']
        primary_benefit = product_info['benefits'][0] if product_info['benefits'] else niche_context.get('hero_subheadline', 'Transform your results')
        
        # Get trust signals for hero
        trust_signals = conversion_intelligence['trust_signals'][:3]
        
        return f"""
        <section class="hero" id="hero">
            <div class="hero-background"></div>
            <div class="container">
                <div class="hero-content" data-aos="fade-up">
                    <h1 class="hero-headline">{niche_context['hero_headline'].format(product_name=product_name)}</h1>
                    <p class="hero-subtext">{niche_context['hero_subheadline'].format(benefit=primary_benefit)}</p>
                    <div class="hero-cta-group">
                        <button class="btn btn-primary" onclick="scrollToForm()" data-track="hero-cta">
                            {page_config['primary_cta']}
                        </button>
                        <div class="trust-indicators">
                            {self._build_trust_indicators(trust_signals)}
                        </div>
                    </div>
                </div>
                <div class="hero-visual">
                    <div class="hero-image-placeholder">
                        <span class="hero-icon">{niche_context.get('benefit_icons', ['🚀'])[0]}</span>
                        <p>Product Visualization</p>
                    </div>
                </div>
            </div>
        </section>
        """
    
    def _build_trust_indicators(self, trust_signals: List[str]) -> str:
        """Build trust indicators HTML"""
        indicators_html = []
        for signal in trust_signals:
            indicators_html.append(f'<span class="trust-item">✅ {signal}</span>')
        return '\n                            '.join(indicators_html)
    
    def get_conversion_elements(self) -> List[str]:
        return ["headline", "value_proposition", "primary_cta", "trust_signals"]

class BenefitsSectionBuilder(SectionBuilder):
    """Builder for benefits sections"""
    
    def build(
        self,
        product_info: Dict[str, Any],
        conversion_intelligence: Dict[str, Any],
        niche_context: Dict[str, Any]
    ) -> str:
        """Build benefits section with conversion psychology"""
        
        benefits = product_info['benefits'][:3] if len(product_info['benefits']) >= 3 else product_info['benefits'] + [
            "Proven results", "Expert support", "Satisfaction guaranteed"
        ][:3]
        
        icons = niche_context.get('benefit_icons', ['⭐', '🚀', '💎'])
        
        benefits_html = ""
        for i, benefit in enumerate(benefits):
            benefits_html += f"""
            <div class="benefit-card" data-aos="fade-up" data-aos-delay="{i * 100}">
                <div class="benefit-icon">{icons[i % len(icons)]}</div>
                <h3>{benefit}</h3>
                <p>Experience the proven approach that delivers measurable results and transforms your success journey.</p>
                <div class="benefit-proof">
                    <span class="proof-indicator">✓ Verified Results</span>
                </div>
            </div>
            """
        
        return f"""
        <section class="benefits" id="benefits">
            <div class="container">
                <h2 class="section-title">Why Choose {product_info['name']}?</h2>
                <p class="section-subtitle">Join thousands who've transformed their results</p>
                <div class="benefits-grid">
                    {benefits_html}
                </div>
            </div>
        </section>
        """
    
    def get_conversion_elements(self) -> List[str]:
        return ["benefit_list", "value_props", "social_proof", "verification"]

class SocialProofSectionBuilder(SectionBuilder):
    """Builder for social proof sections"""
    
    def build(
        self,
        conversion_intelligence: Dict[str, Any],
        niche_context: Dict[str, Any]
    ) -> str:
        """Build social proof section with testimonials and stats"""
        
        return f"""
        <section class="social-proof" id="social-proof">
            <div class="container">
                <h2 class="section-title">Real Results from Real People</h2>
                
                <div class="stats-row">
                    <div class="stat-item">
                        <div class="stat-number">10,000+</div>
                        <div class="stat-label">Success Stories</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">98%</div>
                        <div class="stat-label">Satisfaction Rate</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">5★</div>
                        <div class="stat-label">Average Rating</div>
                    </div>
                </div>
                
                <div class="testimonials-grid">
                    <div class="testimonial-card">
                        <div class="testimonial-content">
                            <div class="testimonial-stars">★★★★★</div>
                            <blockquote>"{niche_context['testimonial_template']}"</blockquote>
                            <cite>— {niche_context['testimonial_author']}</cite>
                        </div>
                    </div>
                    
                    <div class="testimonial-card">
                        <div class="testimonial-content">
                            <div class="testimonial-stars">★★★★★</div>
                            <blockquote>"The results exceeded my expectations. This is exactly what I was looking for."</blockquote>
                            <cite>— Alex M., Verified User</cite>
                        </div>
                    </div>
                </div>
                
                <div class="trust-badges">
                    {self._build_trust_badges(conversion_intelligence['trust_signals'][:4])}
                </div>
            </div>
        </section>
        """
    
    def _build_trust_badges(self, trust_signals: List[str]) -> str:
        """Build trust badges HTML"""
        badges_html = []
        for signal in trust_signals:
            badges_html.append(f'<div class="trust-badge">{signal}</div>')
        return '\n                    '.join(badges_html)
    
    def get_conversion_elements(self) -> List[str]:
        return ["testimonials", "statistics", "trust_badges", "ratings"]

class FormSectionBuilder(SectionBuilder):
    """Builder for form sections"""
    
    def build(
        self,
        product_info: Dict[str, Any],
        page_config: Dict[str, Any]
    ) -> str:
        """Build lead capture form section"""
        
        form_title_map = {
            "lead_generation": "Get Your Free Guide",
            "sales": "Complete Your Order",
            "webinar": "Reserve Your Seat",
            "free_trial": "Start Your Free Trial"
        }
        
        form_title = form_title_map.get(page_config.get('focus', 'lead_generation'), "Get Started")
        
        return f"""
        <section class="form-section" id="form">
            <div class="container">
                <div class="form-container">
                    <div class="form-header">
                        <h2 class="form-title">{form_title}</h2>
                        <p class="form-subtitle">Join thousands who've transformed their results</p>
                    </div>
                    
                    <form class="lead-form" id="leadForm" onsubmit="handleFormSubmit(event)">
                        <div class="form-group">
                            <label for="email" class="sr-only">Email Address</label>
                            <input 
                                type="email" 
                                id="email" 
                                name="email" 
                                placeholder="Enter your email address" 
                                required
                                class="form-input"
                                aria-describedby="email-help"
                                data-track="email-input"
                            >
                            <div id="email-help" class="form-help">We respect your privacy. Unsubscribe at any time.</div>
                        </div>
                        
                        <div class="form-group">
                            <label for="firstName" class="sr-only">First Name</label>
                            <input 
                                type="text" 
                                id="firstName" 
                                name="firstName" 
                                placeholder="First name (optional)" 
                                class="form-input"
                                data-track="name-input"
                            >
                        </div>
                        
                        <button type="submit" class="btn btn-primary btn-form" data-track="form-submit">
                            <span class="btn-text">{page_config['primary_cta']}</span>
                            <span class="btn-arrow">→</span>
                        </button>
                        
                        <div class="form-footer">
                            <div class="privacy-note">
                                <span class="privacy-icon">🔒</span>
                                Your information is secure and will never be shared
                            </div>
                            <div class="spam-note">
                                No spam, ever. Easy unsubscribe with one click.
                            </div>
                        </div>
                    </form>
                    
                    <div class="form-benefits">
                        <h3>What you'll get:</h3>
                        <ul class="benefit-list">
                            <li>✅ Instant access to proven strategies</li>
                            <li>✅ Step-by-step implementation guide</li>
                            <li>✅ Exclusive tips and insights</li>
                            <li>✅ Regular updates and improvements</li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>
        """
    
    def get_conversion_elements(self) -> List[str]:
        return ["email_capture", "form_optimization", "privacy_assurance", "value_preview"]

class CTASectionBuilder(SectionBuilder):
    """Builder for call-to-action sections"""
    
    def build(
        self,
        product_info: Dict[str, Any],
        page_config: Dict[str, Any],
        conversion_intelligence: Dict[str, Any]
    ) -> str:
        """Build call-to-action section with urgency and guarantee"""
        
        return f"""
        <section class="cta-section" id="cta">
            <div class="container">
                <div class="cta-content">
                    <h2 class="cta-headline">Ready to Transform Your Results?</h2>
                    <p class="cta-subtext">Join thousands who've already started their success journey</p>
                    
                    <div class="urgency-elements">
                        <div class="urgency-item">⏰ Limited Time Offer</div>
                        <div class="urgency-item">🎯 Exclusive Access</div>
                        <div class="urgency-item">🚀 Instant Results</div>
                    </div>
                    
                    <div class="cta-button-group">
                        <button class="btn btn-primary btn-large" onclick="scrollToForm()" data-track="final-cta">
                            {page_config['primary_cta']}
                        </button>
                        <div class="guarantee-text">
                            <span class="guarantee-icon">🛡️</span>
                            30-Day Money-Back Guarantee
                        </div>
                    </div>
                    
                    <div class="risk-reversal">
                        <p>No risk, no commitment. If you're not completely satisfied, get your money back.</p>
                    </div>
                </div>
            </div>
        </section>
        """
    
    def get_conversion_elements(self) -> List[str]:
        return ["urgency_elements", "guarantee", "risk_reversal", "final_cta"]

class FooterSectionBuilder(SectionBuilder):
    """Builder for footer sections"""
    
    def build(
        self,
        product_info: Dict[str, Any],
        niche_context: Dict[str, Any]
    ) -> str:
        """Build footer section with contact and legal info"""
        
        return f"""
        <footer class="footer" id="footer">
            <div class="container">
                <div class="footer-content">
                    <div class="footer-main">
                        <div class="footer-brand">
                            <h3>{product_info['name']}</h3>
                            <p>{niche_context['footer_tagline']}</p>
                        </div>
                        
                        <div class="footer-links">
                            <div class="footer-column">
                                <h4>Product</h4>
                                <ul>
                                    <li><a href="#benefits">Features</a></li>
                                    <li><a href="#social-proof">Testimonials</a></li>
                                    <li><a href="#cta">Pricing</a></li>
                                    <li><a href="#form">Get Started</a></li>
                                </ul>
                            </div>
                            
                            <div class="footer-column">
                                <h4>Support</h4>
                                <ul>
                                    <li><a href="#" onclick="openChat()" data-track="contact-click">Contact Us</a></li>
                                    <li><a href="#" onclick="openFAQ()" data-track="faq-click">FAQ</a></li>
                                    <li><a href="#" onclick="openSupport()" data-track="support-click">Help Center</a></li>
                                    <li><a href="#" onclick="openGuarantee()" data-track="guarantee-click">Guarantee</a></li>
                                </ul>
                            </div>
                            
                            <div class="footer-column">
                                <h4>Legal</h4>
                                <ul>
                                    <li><a href="#" onclick="openPrivacy()" data-track="privacy-click">Privacy Policy</a></li>
                                    <li><a href="#" onclick="openTerms()" data-track="terms-click">Terms of Service</a></li>
                                    <li><a href="#" onclick="openRefund()" data-track="refund-click">Refund Policy</a></li>
                                    <li><a href="#" onclick="openDisclaimer()" data-track="disclaimer-click">Disclaimer</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    
                    <div class="footer-bottom">
                        <div class="footer-copyright">
                            <p>&copy; 2024 {product_info['name']}. All rights reserved.</p>
                        </div>
                        
                        <div class="footer-social">
                            <a href="#" class="social-link" aria-label="Facebook" data-track="social-facebook">📘</a>
                            <a href="#" class="social-link" aria-label="Twitter" data-track="social-twitter">🐦</a>
                            <a href="#" class="social-link" aria-label="LinkedIn" data-track="social-linkedin">💼</a>
                            <a href="#" class="social-link" aria-label="Instagram" data-track="social-instagram">📷</a>
                        </div>
                    </div>
                </div>
            </div>
        </footer>
        """
    
    def get_conversion_elements(self) -> List[str]:
        return ["contact_links", "social_proof", "trust_links", "brand_reinforcement"]

# Section builder registry for easy access
SECTION_BUILDERS = {
    'hero': HeroSectionBuilder(),
    'benefits': BenefitsSectionBuilder(),
    'social_proof': SocialProofSectionBuilder(),
    'form': FormSectionBuilder(),
    'cta': CTASectionBuilder(),
    'footer': FooterSectionBuilder()
}

def get_section_builder(section_type: str) -> SectionBuilder:
    """Get the appropriate section builder"""
    return SECTION_BUILDERS.get(section_type, HeroSectionBuilder())

# Export for external use
__all__ = [
    'SectionBuilder',
    'HeroSectionBuilder',
    'BenefitsSectionBuilder', 
    'SocialProofSectionBuilder',
    'FormSectionBuilder',
    'CTASectionBuilder',
    'FooterSectionBuilder',
    'SECTION_BUILDERS',
    'get_section_builder'
]