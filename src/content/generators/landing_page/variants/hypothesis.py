"""
Test Hypothesis Generator
Creates testing hypotheses for A/B variants.
"""

import logging
from typing import Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TestHypothesis:
    """Test hypothesis for A/B testing"""
    hypothesis_text: str
    change_description: str
    expected_improvement: str
    success_metric: str
    confidence_level: str

class HypothesisGenerator:
    """Generates test hypotheses for landing page variants"""
    
    def __init__(self):
        self.hypothesis_templates = {
            'headline_focused': {
                'hypothesis': "By changing the headline to focus more on {focus_area}, we will increase conversion rates",
                'change': "Headline optimization for better value communication",
                'improvement': "10-15% increase in conversion rate",
                'metric': "Email signups / page views",
                'confidence': "Medium"
            },
            'benefit_focused': {
                'hypothesis': "By enhancing the benefits section with stronger value propositions, we will increase user engagement",
                'change': " benefits with proof elements",
                'improvement': "8-12% increase in time on page and conversions",
                'metric': "Time on page, scroll depth, conversions",
                'confidence': "High"
            },
            'urgency_focused': {
                'hypothesis': "By adding urgency and scarcity elements, we will create FOMO and increase immediate action",
                'change': "Added urgency banners and countdown timers",
                'improvement': "15-20% increase in immediate conversions",
                'metric': "Same-session conversion rate",
                'confidence': "Medium-High"
            },
            'social_proof_focused': {
                'hypothesis': "By adding more testimonials and trust signals, we will reduce hesitation and increase trust",
                'change': " social proof and testimonials",
                'improvement': "12-18% increase in conversion rate",
                'metric': "Overall conversion rate",
                'confidence': "High"
            },
            'form_optimized': {
                'hypothesis': "By optimizing the form copy and reducing perceived friction, we will increase form completions",
                'change': "Simplified form with better copy and guarantees",
                'improvement': "20-25% increase in form completion rate",
                'metric': "Form starts to form completions ratio",
                'confidence': "High"
            }
        }
    
    def generate_hypothesis(
        self, 
        strategy_name: str, 
        product_info: Dict[str, Any]
    ) -> TestHypothesis:
        """Generate test hypothesis for a specific strategy"""
        
        template = self.hypothesis_templates.get(
            strategy_name, 
            self.hypothesis_templates['benefit_focused']
        )
        
        # Customize hypothesis based on product
        focus_area = self._determine_focus_area(product_info)
        
        return TestHypothesis(
            hypothesis_text=template['hypothesis'].format(focus_area=focus_area),
            change_description=template['change'],
            expected_improvement=template['improvement'],
            success_metric=template['metric'],
            confidence_level=template['confidence']
        )
    
    def _determine_focus_area(self, product_info: Dict[str, Any]) -> str:
        """Determine the main focus area for the product"""
        
        product_name = product_info.get('name', '').lower()
        benefits = ' '.join(product_info.get('benefits', [])).lower()
        
        if any(word in f"{product_name} {benefits}" for word in ['health', 'supplement', 'wellness']):
            return 'health benefits and scientific backing'
        elif any(word in f"{product_name} {benefits}" for word in ['software', 'saas', 'tool']):
            return 'automation and time-saving benefits'
        elif any(word in f"{product_name} {benefits}" for word in ['business', 'course', 'training']):
            return 'revenue growth and success outcomes'
        else:
            return 'core value proposition and unique benefits'