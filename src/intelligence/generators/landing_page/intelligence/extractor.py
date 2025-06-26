# src/intelligence/generators/landing_page/intelligence/extractor.py
"""
Intelligence data extraction and processing for landing page generation.
Processes raw intelligence data and extracts relevant information for page creation.
"""

from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class IntelligenceExtractor:
    """Extracts and processes intelligence data for landing page generation"""
    
    def extract_product_info(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract product information from intelligence data"""
        
        try:
            offer_intel = intelligence_data.get("offer_intelligence", {})
            
            # Extract product name
            product_name = self._extract_product_name(offer_intel)
            
            # Extract benefits with scientific backing
            benefits = self._extract_enhanced_benefits(intelligence_data)
            
            # Extract value propositions
            value_props = self._extract_value_propositions(offer_intel)
            
            # Determine product category
            category = self._determine_category(intelligence_data)
            
            return {
                "name": product_name,
                "category": category,
                "benefits": benefits,
                "value_propositions": value_props,
                "positioning": self._determine_positioning(intelligence_data)
            }
            
        except Exception as e:
            logger.error(f"Error extracting product info: {str(e)}")
            return self._fallback_product_info()
    
    def extract_conversion_intelligence(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract conversion-focused intelligence"""
        
        try:
            psychology_intel = intelligence_data.get("psychology_intelligence", {})
            competitive_intel = intelligence_data.get("competitive_intelligence", {})
            credibility_intel = intelligence_data.get("credibility_intelligence", {})
            
            # Check if intelligence was amplified
            amplification_metadata = intelligence_data.get("amplification_metadata", {})
            is_amplified = amplification_metadata.get("amplification_applied", False)
            
            return {
                "emotional_triggers": self._extract_emotional_triggers(psychology_intel),
                "pain_points": self._extract_pain_points(psychology_intel),
                "trust_signals": self._extract_trust_signals(credibility_intel, intelligence_data),
                "competitive_advantages": self._extract_competitive_advantages(competitive_intel),
                "urgency_elements": self._extract_urgency_elements(psychology_intel),
                "social_proof": self._extract_social_proof(intelligence_data),
                "amplified_intelligence": is_amplified,
                "confidence_boost": amplification_metadata.get("confidence_boost", 0.0),
                "scientific_enhancements": amplification_metadata.get("scientific_enhancements", 0)
            }
            
        except Exception as e:
            logger.error(f"Error extracting conversion intelligence: {str(e)}")
            return self._fallback_conversion_intelligence()
    
    def _extract_product_name(self, offer_intel: Dict[str, Any]) -> str:
        """Extract product name from offer intelligence"""
        
        # Method 1: Look for product name in insights
        insights = offer_intel.get("insights", [])
        for insight in insights:
            insight_str = str(insight).lower()
            if "called" in insight_str:
                words = str(insight).split()
                for i, word in enumerate(words):
                    if word.lower() == "called" and i + 1 < len(words):
                        potential_name = words[i + 1].upper().replace(",", "").replace(".", "")
                        if len(potential_name) > 2:
                            return potential_name
        
        # Method 2: Look for product mentions in products list
        products = offer_intel.get("products", [])
        if products:
            first_product = str(products[0]).strip()
            if len(first_product) > 2:
                return first_product.upper()
        
        # Method 3: Extract from value propositions
        value_props = offer_intel.get("value_propositions", [])
        for prop in value_props:
            prop_str = str(prop)
            # Look for brand names (capitalized words)
            words = prop_str.split()
            for word in words:
                if word[0].isupper() and len(word) > 3 and word.isalpha():
                    return word.upper()
        
        # Fallback
        return "PRODUCT"
    
    def _extract_enhanced_benefits(self, intelligence_data: Dict[str, Any]) -> List[str]:
        """Extract benefits with scientific backing priority"""
        
        benefits = []
        offer_intel = intelligence_data.get("offer_intelligence", {})
        
        # Priority 1: Scientific support (from amplification)
        scientific_support = offer_intel.get("scientific_support", [])
        if scientific_support:
            benefits.extend(scientific_support[:3])
            return benefits
        
        # Priority 2: Validated claims (from amplification)
        validated_claims = offer_intel.get("validated_claims", [])
        if validated_claims:
            for claim in validated_claims[:3]:
                if isinstance(claim, dict):
                    benefits.append(claim.get("original_claim", str(claim)))
                else:
                    benefits.append(str(claim))
            return benefits
        
        # Priority 3: Regular value propositions
        value_props = offer_intel.get("value_propositions", [])
        if value_props:
            benefits.extend([str(prop) for prop in value_props[:3]])
            return benefits
        
        # Priority 4: Extract from insights
        insights = offer_intel.get("insights", [])
        for insight in insights:
            insight_str = str(insight).lower()
            if any(word in insight_str for word in ["benefit", "help", "improve", "support"]):
                benefits.append(str(insight))
                if len(benefits) >= 3:
                    break
        
        # Fallback benefits
        if not benefits:
            benefits = [
                "Research-backed formula",
                "Natural wellness support",
                "Proven effectiveness"
            ]
        
        return benefits
    
    def _extract_value_propositions(self, offer_intel: Dict[str, Any]) -> List[str]:
        """Extract value propositions"""
        
        value_props = offer_intel.get("value_propositions", [])
        
        if value_props:
            return [str(prop) for prop in value_props]
        
        # Extract from other sources
        products = offer_intel.get("products", [])
        if products:
            return [f"Premium {product}" for product in products[:3]]
        
        # Fallback
        return [
            "Science-backed natural formula",
            "Clinically researched ingredients", 
            "Premium wellness optimization"
        ]
    
    def _extract_emotional_triggers(self, psychology_intel: Dict[str, Any]) -> List[str]:
        """Extract emotional triggers"""
        
        triggers = psychology_intel.get("emotional_triggers", [])
        
        if triggers:
            return [str(trigger) for trigger in triggers]
        
        # Extract from persuasion techniques
        techniques = psychology_intel.get("persuasion_techniques", [])
        emotional_techniques = []
        for technique in techniques:
            technique_str = str(technique).lower()
            if any(word in technique_str for word in ["emotion", "feel", "fear", "desire", "hope"]):
                emotional_techniques.append(str(technique))
        
        if emotional_techniques:
            return emotional_techniques
        
        # Fallback triggers
        return ["transformation", "results", "confidence", "success"]
    
    def _extract_pain_points(self, psychology_intel: Dict[str, Any]) -> List[str]:
        """Extract pain points"""
        
        pain_points = psychology_intel.get("pain_points", [])
        
        if pain_points:
            return [str(point) for point in pain_points]
        
        # Fallback pain points
        return [
            "Struggling with current solutions",
            "Looking for better results",
            "Want proven approach"
        ]
    
    def _extract_trust_signals(self, credibility_intel: Dict[str, Any], intelligence_data: Dict[str, Any]) -> List[str]:
        """Extract trust signals from multiple sources"""
        
        trust_signals = []
        
        # From credibility intelligence (amplified)
        if credibility_intel:
            trust_indicators = credibility_intel.get("trust_indicators", [])
            authority_signals = credibility_intel.get("authority_signals", [])
            trust_signals.extend([str(signal) for signal in trust_indicators[:2]])
            trust_signals.extend([str(signal) for signal in authority_signals[:2]])
        
        # From offer intelligence
        offer_intel = intelligence_data.get("offer_intelligence", {})
        guarantees = offer_intel.get("guarantees", [])
        trust_signals.extend([str(guarantee) for guarantee in guarantees[:2]])
        
        # From scientific backing
        scientific_support = offer_intel.get("scientific_support", [])
        if scientific_support:
            trust_signals.append("Scientific research backing")
        
        # Remove duplicates and limit
        unique_signals = list(dict.fromkeys(trust_signals))[:4]
        
        # Fallback if empty
        if not unique_signals:
            unique_signals = [
                "Expert recommended",
                "Proven results", 
                "Satisfaction guaranteed",
                "Secure and safe"
            ]
        
        return unique_signals
    
    def _extract_competitive_advantages(self, competitive_intel: Dict[str, Any]) -> List[str]:
        """Extract competitive advantages"""
        
        advantages = []
        
        # From competitive intelligence
        if competitive_intel:
            existing_advantages = competitive_intel.get("advantages", [])
            advantages.extend([str(adv) for adv in existing_advantages])
            
            # From scientific advantages (amplified)
            scientific_advantages = competitive_intel.get("scientific_advantages", [])
            advantages.extend([str(adv) for adv in scientific_advantages])
            
            # From opportunities
            opportunities = competitive_intel.get("opportunities", [])
            for opp in opportunities[:2]:
                advantages.append(f"Competitive advantage: {str(opp)}")
        
        # Fallback advantages
        if not advantages:
            advantages = [
                "Research-validated approach",
                "Premium scientific credibility",
                "Evidence-based formulation"
            ]
        
        return advantages[:3]
    
    def _extract_urgency_elements(self, psychology_intel: Dict[str, Any]) -> List[str]:
        """Extract urgency elements"""
        
        # Look for urgency in persuasion techniques
        techniques = psychology_intel.get("persuasion_techniques", [])
        urgency_elements = []
        
        for technique in techniques:
            technique_str = str(technique).lower()
            if any(word in technique_str for word in ["urgency", "limited", "scarcity", "deadline"]):
                urgency_elements.append(str(technique))
        
        # Default urgency elements
        if not urgency_elements:
            urgency_elements = [
                "Limited time offer",
                "Exclusive access", 
                "Act now"
            ]
        
        return urgency_elements
    
    def _extract_social_proof(self, intelligence_data: Dict[str, Any]) -> List[str]:
        """Extract social proof elements"""
        
        social_proof = []
        
        # From content intelligence
        content_intel = intelligence_data.get("content_intelligence", {})
        if content_intel:
            success_stories = content_intel.get("success_stories", [])
            social_proof.extend([str(story) for story in success_stories[:2]])
            
            existing_social_proof = content_intel.get("social_proof", [])
            social_proof.extend([str(proof) for proof in existing_social_proof[:2]])
        
        # From psychology intelligence
        psychology_intel = intelligence_data.get("psychology_intelligence", {})
        techniques = psychology_intel.get("persuasion_techniques", [])
        for technique in techniques:
            technique_str = str(technique).lower()
            if "social proof" in technique_str or "testimonial" in technique_str:
                social_proof.append("Customer testimonials")
                break
        
        # Fallback social proof
        if not social_proof:
            social_proof = [
                "Thousands of satisfied customers",
                "Clinically researched formula",
                "Science-backed results"
            ]
        
        return social_proof
    
    def _determine_category(self, intelligence_data: Dict[str, Any]) -> str:
        """Determine product category from intelligence data"""
        
        # Analyze all content for category indicators
        all_content = str(intelligence_data).lower()
        
        # Health category
        health_indicators = ["health", "supplement", "wellness", "liver", "weight", "medical", "clinical"]
        if any(indicator in all_content for indicator in health_indicators):
            return "Health & Wellness"
        
        # Technology category
        tech_indicators = ["software", "saas", "app", "platform", "technology", "digital", "automation"]
        if any(indicator in all_content for indicator in tech_indicators):
            return "Technology"
        
        # Business category
        business_indicators = ["business", "marketing", "sales", "course", "training", "strategy", "growth"]
        if any(indicator in all_content for indicator in business_indicators):
            return "Business"
        
        # Education category
        education_indicators = ["learn", "education", "course", "training", "skill", "knowledge"]
        if any(indicator in all_content for indicator in education_indicators):
            return "Education"
        
        # Finance category
        finance_indicators = ["money", "investment", "financial", "wealth", "trading", "profit"]
        if any(indicator in all_content for indicator in finance_indicators):
            return "Finance"
        
        # Default
        return "Solution"
    
    def _determine_positioning(self, intelligence_data: Dict[str, Any]) -> str:
        """Determine positioning strategy"""
        
        # Check for scientific backing
        offer_intel = intelligence_data.get("offer_intelligence", {})
        scientific_support = offer_intel.get("scientific_support", [])
        
        if scientific_support:
            return "Premium scientific solution"
        
        # Check for competitive advantages
        competitive_intel = intelligence_data.get("competitive_intelligence", {})
        if competitive_intel and competitive_intel.get("advantages"):
            return "Competitive market leader"
        
        # Default positioning
        return "Premium solution for optimal results"
    
    def _fallback_product_info(self) -> Dict[str, Any]:
        """Fallback product information when extraction fails"""
        
        return {
            "name": "PRODUCT",
            "category": "Solution",
            "benefits": [
                "Proven results",
                "Expert solution", 
                "Satisfaction guaranteed"
            ],
            "value_propositions": [
                "Premium quality",
                "Expert developed",
                "Results guaranteed"
            ],
            "positioning": "Premium solution"
        }
    
    def _fallback_conversion_intelligence(self) -> Dict[str, Any]:
        """Fallback conversion intelligence when extraction fails"""
        
        return {
            "emotional_triggers": ["success", "results", "transformation"],
            "pain_points": ["current challenges", "seeking solutions"],
            "trust_signals": ["expert recommended", "proven results", "satisfaction guaranteed"],
            "competitive_advantages": ["proven approach", "expert solution"],
            "urgency_elements": ["limited time", "exclusive access", "act now"],
            "social_proof": ["thousands of customers", "proven results"],
            "amplified_intelligence": False,
            "confidence_boost": 0.0,
            "scientific_enhancements": 0
        }

# Export for external use
__all__ = ['IntelligenceExtractor']