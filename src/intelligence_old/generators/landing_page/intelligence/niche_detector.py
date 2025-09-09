"""
Niche Detection System
Automatically detects industry niche and optimizes content accordingly.
"""

import logging
from typing import Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)

class NicheType(Enum):
    HEALTH_SUPPLEMENTS = "health_supplements"
    SAAS_SOFTWARE = "saas_software"
    BUSINESS_COURSE = "business_course"
    ECOMMERCE_PRODUCT = "ecommerce_product"
    LIFE_COACHING = "life_coaching"
    FITNESS_PROGRAM = "fitness_program"
    FINANCIAL_SERVICE = "financial_service"
    TECHNOLOGY_TOOL = "technology_tool"
    EDUCATION_COURSE = "education_course"
    GENERIC = "generic"

class NicheDetector:
    """Detects product niche and provides niche-specific optimizations"""
    
    def __init__(self):
        self.niche_keywords = {
            NicheType.HEALTH_SUPPLEMENTS: [
                'supplement', 'vitamin', 'health', 'natural', 'organic', 'wellness',
                'liver', 'detox', 'cleanse', 'antioxidant', 'immunity', 'energy'
            ],
            NicheType.SAAS_SOFTWARE: [
                'software', 'saas', 'platform', 'app', 'tool', 'automation',
                'dashboard', 'analytics', 'api', 'integration', 'workflow'
            ],
            NicheType.BUSINESS_COURSE: [
                'business', 'entrepreneur', 'marketing', 'sales', 'strategy',
                'revenue', 'profit', 'growth', 'course', 'training', 'mastermind'
            ],
            NicheType.ECOMMERCE_PRODUCT: [
                'product', 'store', 'shop', 'buy', 'purchase', 'shipping',
                'quality', 'premium', 'exclusive', 'limited', 'bestseller'
            ],
            NicheType.LIFE_COACHING: [
                'coaching', 'life', 'personal', 'transformation', 'mindset',
                'success', 'goals', 'habits', 'lifestyle', 'fulfillment'
            ],
            NicheType.FITNESS_PROGRAM: [
                'fitness', 'workout', 'exercise', 'muscle', 'weight', 'strength',
                'cardio', 'nutrition', 'diet', 'body', 'athletic', 'performance'
            ],
            NicheType.FINANCIAL_SERVICE: [
                'financial', 'investment', 'money', 'wealth', 'portfolio',
                'trading', 'crypto', 'stocks', 'returns', 'profit', 'income'
            ],
            NicheType.TECHNOLOGY_TOOL: [
                'tech', 'digital', 'innovation', 'ai', 'machine learning',
                'automation', 'efficiency', 'productivity', 'system', 'solution'
            ],
            NicheType.EDUCATION_COURSE: [
                'education', 'learn', 'course', 'skill', 'certification',
                'knowledge', 'expertise', 'career', 'professional', 'development'
            ]
        }
        
        self.niche_contexts = {
            NicheType.HEALTH_SUPPLEMENTS: {
                'hero_headline': 'Transform Your Health with Science-Backed {product_name}',
                'hero_subheadline': 'Discover the natural approach that delivers {benefit} without harmful side effects',
                'benefit_icons': ['🧬', '🌿', '⚡'],
                'testimonial_template': 'This completely changed how I feel every day. The energy boost is incredible!',
                'testimonial_author': 'Sarah M., Health Enthusiast',
                'footer_tagline': 'Natural health optimization through science-backed solutions',
                'trust_elements': ['FDA Registered Facility', 'Third-Party Tested', 'Money-Back Guarantee'],
                'urgency_triggers': ['Limited Stock', 'Special Pricing', 'Exclusive Formula']
            },
            NicheType.SAAS_SOFTWARE: {
                'hero_headline': 'Automate Your Success with {product_name}',
                'hero_subheadline': 'The platform that {benefit} and saves you 10+ hours per week',
                'benefit_icons': ['⚡', '🚀', '📊'],
                'testimonial_template': 'This tool transformed our workflow. We increased productivity by 300%!',
                'testimonial_author': 'Mike Chen, Startup Founder',
                'footer_tagline': 'Powerful automation for modern businesses',
                'trust_elements': ['SOC 2 Compliant', '99.9% Uptime', 'Enterprise Security'],
                'urgency_triggers': ['Free Trial Ending', 'Limited Beta Access', 'Early Bird Pricing']
            },
            NicheType.BUSINESS_COURSE: {
                'hero_headline': 'Build a 7-Figure Business with {product_name}',
                'hero_subheadline': 'The proven system that helps entrepreneurs {benefit} in 90 days or less',
                'benefit_icons': ['💰', '📈', '🎯'],
                'testimonial_template': 'This course gave me the exact blueprint I needed. Revenue increased 400%!',
                'testimonial_author': 'Jessica L., Business Owner',
                'footer_tagline': 'Proven strategies for explosive business growth',
                'trust_elements': ['10,000+ Success Stories', 'Money-Back Guarantee', 'Lifetime Support'],
                'urgency_triggers': ['Course Closing Soon', 'Bonus Deadline', 'Limited Enrollment']
            },
            NicheType.LIFE_COACHING: {
                'hero_headline': 'Transform Your Life with {product_name}',
                'hero_subheadline': 'The breakthrough system that helps you {benefit} and live your best life',
                'benefit_icons': ['🌟', '💎', '🚀'],
                'testimonial_template': 'This program completely changed my perspective. I finally found my purpose!',
                'testimonial_author': 'David R., Life Transformation',
                'footer_tagline': 'Empowering transformation through proven coaching methods',
                'trust_elements': ['Certified Coaches', '5-Star Reviews', 'Success Guarantee'],
                'urgency_triggers': ['Limited Spots', 'Early Bird Access', 'Bonus Content']
            },
            NicheType.GENERIC: {
                'hero_headline': 'Achieve Amazing Results with {product_name}',
                'hero_subheadline': 'The solution that delivers {benefit} and transforms your success',
                'benefit_icons': ['⭐', '🚀', '💎'],
                'testimonial_template': 'This exceeded all my expectations. Exactly what I was looking for!',
                'testimonial_author': 'Alex M., Satisfied Customer',
                'footer_tagline': 'Quality solutions for better results',
                'trust_elements': ['Proven Results', 'Money-Back Guarantee', 'Expert Support'],
                'urgency_triggers': ['Limited Time', 'Special Offer', 'Exclusive Access']
            }
        }
    
    def detect_niche(
        self, 
        product_info: Dict[str, Any], 
        conversion_intelligence: Dict[str, Any]
    ) -> NicheType:
        """Detect the product niche based on product info and intelligence"""
        
        # Combine all text for analysis
        text_content = []
        text_content.append(product_info.get('name', ''))
        text_content.append(product_info.get('description', ''))
        text_content.extend(product_info.get('benefits', []))
        text_content.extend(conversion_intelligence.get('key_messages', []))
        
        combined_text = ' '.join(text_content).lower()
        
        # Score each niche
        niche_scores = {}
        for niche_type, keywords in self.niche_keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            niche_scores[niche_type] = score
        
        # Get the highest scoring niche
        best_niche = max(niche_scores, key=niche_scores.get)
        
        # Require minimum score threshold
        if niche_scores[best_niche] < 2:
            best_niche = NicheType.GENERIC
        
        logger.info(f"✅ Detected niche: {best_niche.value} (score: {niche_scores[best_niche]})")
        return best_niche
    
    def get_niche_context(self, niche_type: NicheType) -> Dict[str, Any]:
        """Get niche-specific context for content generation"""
        return self.niche_contexts.get(niche_type, self.niche_contexts[NicheType.GENERIC])