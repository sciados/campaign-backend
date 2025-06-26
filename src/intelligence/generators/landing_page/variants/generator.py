"""
A/B Test Variant Generator
Creates landing page variants for testing different approaches.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .hypothesis import HypothesisGenerator, TestHypothesis

logger = logging.getLogger(__name__)

@dataclass
class VariantResult:
    """Result of variant generation"""
    variant_id: str
    variant_name: str
    variant_type: str
    html_content: str
    test_hypothesis: TestHypothesis
    expected_improvement: str
    changes_made: List[str]

class VariantGenerator:
    """Generates A/B test variants for landing pages"""
    
    def __init__(self):
        self.hypothesis_generator = HypothesisGenerator()
        self.variant_strategies = {
            'headline_focused': self._generate_headline_variant,
            'benefit_focused': self._generate_benefit_variant,
            'urgency_focused': self._generate_urgency_variant,
            'social_proof_focused': self._generate_social_proof_variant,
            'form_optimized': self._generate_form_variant
        }
    
    async def generate_variants(
        self,
        base_html: str,
        product_info: Dict[str, Any],
        template: Any,
        max_variants: int = 3
    ) -> List[VariantResult]:
        """Generate multiple A/B test variants"""
        
        variants = []
        variant_group_id = str(uuid.uuid4())
        
        # Select variant strategies
        selected_strategies = list(self.variant_strategies.keys())[:max_variants]
        
        for i, strategy_name in enumerate(selected_strategies):
            try:
                variant = await self._generate_single_variant(
                    base_html=base_html,
                    product_info=product_info,
                    strategy_name=strategy_name,
                    variant_index=i + 1,
                    variant_group_id=variant_group_id
                )
                
                if variant:
                    variants.append(variant)
                    
            except Exception as e:
                logger.error(f"Variant generation failed for {strategy_name}: {str(e)}")
                continue
        
        logger.info(f"✅ Generated {len(variants)} variants for testing")
        return variants
    
    async def _generate_single_variant(
        self,
        base_html: str,
        product_info: Dict[str, Any],
        strategy_name: str,
        variant_index: int,
        variant_group_id: str
    ) -> Optional[VariantResult]:
        """Generate a single variant using specified strategy"""
        
        try:
            # Get strategy function
            strategy_func = self.variant_strategies[strategy_name]
            
            # Generate hypothesis
            hypothesis = self.hypothesis_generator.generate_hypothesis(
                strategy_name, product_info
            )
            
            # Apply variant strategy
            variant_html, changes_made = strategy_func(
                base_html, product_info, hypothesis
            )
            
            # Create variant result
            return VariantResult(
                variant_id=str(uuid.uuid4()),
                variant_name=f"Variant {variant_index}: {strategy_name.replace('_', ' ').title()}",
                variant_type=strategy_name,
                html_content=variant_html,
                test_hypothesis=hypothesis,
                expected_improvement=hypothesis.expected_improvement,
                changes_made=changes_made
            )
            
        except Exception as e:
            logger.error(f"Single variant generation failed: {str(e)}")
            return None
    
    def _generate_headline_variant(
        self, 
        base_html: str, 
        product_info: Dict[str, Any], 
        hypothesis: TestHypothesis
    ) -> tuple[str, List[str]]:
        """Generate variant with different headline approach"""
        
        original_headline = self._extract_headline(base_html)
        new_headline = self._create_alternate_headline(product_info, "benefit_focused")
        
        variant_html = base_html.replace(original_headline, new_headline)
        changes_made = [f"Changed headline from '{original_headline}' to '{new_headline}'"]
        
        return variant_html, changes_made
    
    def _generate_benefit_variant(
        self, 
        base_html: str, 
        product_info: Dict[str, Any], 
        hypothesis: TestHypothesis
    ) -> tuple[str, List[str]]:
        """Generate variant with enhanced benefit presentation"""
        
        # Add benefit amplifiers
        benefit_section = self._find_benefits_section(base_html)
        if benefit_section:
            enhanced_benefits = self._enhance_benefits_section(benefit_section, product_info)
            variant_html = base_html.replace(benefit_section, enhanced_benefits)
            changes_made = ["Enhanced benefits section with stronger value propositions"]
        else:
            variant_html = base_html
            changes_made = ["No benefits section found to enhance"]
        
        return variant_html, changes_made
    
    def _generate_urgency_variant(
        self, 
        base_html: str, 
        product_info: Dict[str, Any], 
        hypothesis: TestHypothesis
    ) -> tuple[str, List[str]]:
        """Generate variant with added urgency elements"""
        
        urgency_elements = [
            '<div class="urgency-banner">⏰ Limited Time: Special Launch Pricing Ends Soon!</div>',
            '<div class="scarcity-indicator">🔥 Only 47 spots remaining today</div>',
            '<div class="timer-element">⌛ Offer expires in: <span class="countdown">23:59:45</span></div>'
        ]
        
        # Insert urgency elements after hero section
        hero_end = base_html.find('</section>', base_html.find('class="hero"'))
        if hero_end != -1:
            insert_point = hero_end + len('</section>')
            urgency_html = '\n'.join(urgency_elements)
            variant_html = base_html[:insert_point] + '\n' + urgency_html + base_html[insert_point:]
            changes_made = ["Added urgency and scarcity elements after hero section"]
        else:
            variant_html = base_html
            changes_made = ["Could not find hero section to add urgency elements"]
        
        return variant_html, changes_made
    
    def _generate_social_proof_variant(
        self, 
        base_html: str, 
        product_info: Dict[str, Any], 
        hypothesis: TestHypothesis
    ) -> tuple[str, List[str]]:
        """Generate variant with enhanced social proof"""
        
        additional_testimonials = '''
        <div class="extra-testimonials">
            <div class="testimonial-highlight">
                <div class="testimonial-content">
                    <div class="stars">★★★★★</div>
                    <blockquote>"Best investment I've made this year. Results were immediate and exactly what was promised."</blockquote>
                    <cite>— Jennifer K., Verified Customer</cite>
                </div>
            </div>
            <div class="trust-stats">
                <div class="stat">📊 15,000+ Happy Customers</div>
                <div class="stat">⭐ 4.9/5 Average Rating</div>
                <div class="stat">🏆 Industry Award Winner</div>
            </div>
        </div>
        '''
        
        # Find social proof section and enhance it
        social_section_start = base_html.find('class="social-proof"')
        if social_section_start != -1:
            section_end = base_html.find('</section>', social_section_start)
            if section_end != -1:
                variant_html = base_html[:section_end] + additional_testimonials + base_html[section_end:]
                changes_made = ["Added additional testimonials and trust statistics"]
            else:
                variant_html = base_html
                changes_made = ["Could not find end of social proof section"]
        else:
            variant_html = base_html
            changes_made = ["No social proof section found to enhance"]
        
        return variant_html, changes_made
    
    def _generate_form_variant(
        self, 
        base_html: str, 
        product_info: Dict[str, Any], 
        hypothesis: TestHypothesis
    ) -> tuple[str, List[str]]:
        """Generate variant with optimized form"""
        
        # Find form and optimize
        form_start = base_html.find('<form')
        if form_start != -1:
            form_end = base_html.find('</form>', form_start) + 7
            original_form = base_html[form_start:form_end]
            
            optimized_form = self._create_optimized_form(product_info)
            variant_html = base_html[:form_start] + optimized_form + base_html[form_end:]
            changes_made = ["Optimized form with better copy and reduced friction"]
        else:
            variant_html = base_html
            changes_made = ["No form found to optimize"]
        
        return variant_html, changes_made
    
    def _extract_headline(self, html: str) -> str:
        """Extract main headline from HTML"""
        import re
        headline_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
        return headline_match.group(1) if headline_match else "Default Headline"
    
    def _create_alternate_headline(self, product_info: Dict[str, Any], style: str) -> str:
        """Create alternate headline based on style"""
        product_name = product_info.get('name', 'Our Product')
        
        headlines = {
            'benefit_focused': f"Finally! The {product_name} That Actually Works",
            'problem_focused': f"Stop Struggling - {product_name} Has the Answer",
            'curiosity_focused': f"The Secret Behind {product_name}'s Amazing Results",
            'urgency_focused': f"Last Chance: Get {product_name} Before It's Gone"
        }
        
        return headlines.get(style, headlines['benefit_focused'])
    
    def _find_benefits_section(self, html: str) -> Optional[str]:
        """Find benefits section in HTML"""
        benefits_start = html.find('class="benefits"')
        if benefits_start != -1:
            section_start = html.rfind('<section', 0, benefits_start)
            section_end = html.find('</section>', benefits_start) + 10
            return html[section_start:section_end]
        return None
    
    def _enhance_benefits_section(self, section: str, product_info: Dict[str, Any]) -> str:
        """Enhance benefits section with stronger copy"""
        # This is a simplified version - in practice, you'd have more sophisticated enhancement
        enhanced = section.replace(
            "Experience the proven approach", 
            "Get GUARANTEED results with our breakthrough approach"
        )
        enhanced = enhanced.replace(
            "✓ Verified Results", 
            "✓ PROVEN Results (see testimonials below)"
        )
        return enhanced
    
    def _create_optimized_form(self, product_info: Dict[str, Any]) -> str:
        """Create optimized form with better conversion copy"""
        return '''
        <form class="lead-form optimized-form" id="leadForm" onsubmit="handleFormSubmit(event)">
            <div class="form-header-optimized">
                <h3>Get Instant Access - 100% Free</h3>
                <p>Join 10,000+ people already transforming their results</p>
            </div>
            
            <div class="form-group">
                <input 
                    type="email" 
                    id="email" 
                    name="email" 
                    placeholder="Enter your best email address" 
                    required
                    class="form-input-optimized"
                >
            </div>
            
            <button type="submit" class="btn btn-primary btn-optimized">
                YES! Give Me Instant Access →
            </button>
            
            <div class="form-guarantees">
                <div class="guarantee-item">🔒 Your email is 100% secure</div>
                <div class="guarantee-item">📧 No spam, unsubscribe anytime</div>
                <div class="guarantee-item">⚡ Instant access, no waiting</div>
            </div>
        </form>
        '''