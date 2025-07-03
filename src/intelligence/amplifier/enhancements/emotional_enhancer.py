# src/intelligence/amplifier/enhancements/emotional_enhancer.py
"""
Generates emotional journey mapping and psychological insights using AI
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EmotionalTransformationEnhancer:
    """Generate emotional transformation intelligence and customer journey mapping"""
    
    def __init__(self, ai_providers: List[Dict]):
        self.ai_providers = ai_providers
        self.available_provider = self._get_best_provider()
        
    def _get_best_provider(self) -> Optional[Dict]:
        """Get the best available AI provider - prefer Claude for stability"""
        
        # Prefer Claude first (has API issues currently)
        for provider in self.ai_providers:
            if provider.get("name") == "anthropic" and provider.get("available"):
                logger.info("🤖 Using Claude for authority enhancement")
                return provider
                
        # Fallback to Cohere second
        for provider in self.ai_providers:
            if provider.get("name") == "cohere" and provider.get("available"):
                logger.info("💫 Using Cohere for authority enhancement") 
                return provider
        
        # Fallback to OpenAI last (working perfectly)
        for provider in self.ai_providers:
            if provider.get("name") == "openai" and provider.get("available"):
                logger.info("🚀 Using OpenAI for authority enhancement")
                return provider        
        
        logger.warning("⚠️ No AI providers available for authority enhancement")
        return None
    
    async def generate_emotional_transformation_intelligence(
        self, 
        product_data: Dict[str, Any], 
        base_intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive emotional transformation intelligence"""
        
        if not self.available_provider:
            return self._generate_fallback_emotional_intelligence(product_data)
        
        try:
            # Extract product information
            product_name = product_data.get("product_name", "Product")
            psych_intel = base_intelligence.get("psychology_intelligence", {})
            offer_intel = base_intelligence.get("offer_intelligence", {})
            
            # Generate emotional journey mapping
            emotional_journey = await self._generate_emotional_journey_mapping(product_name, psych_intel, offer_intel)
            
            # Generate psychological triggers
            psychological_triggers = await self._generate_psychological_triggers(product_name, psych_intel)
            
            # Generate emotional value propositions
            emotional_value_props = await self._generate_emotional_value_propositions(product_name, offer_intel)
            
            # Generate transformation narratives
            transformation_narratives = await self._generate_transformation_narratives(product_name, base_intelligence)
            
            # Generate emotional engagement strategies
            engagement_strategies = await self._generate_emotional_engagement_strategies(product_name, psych_intel)
            
            # Compile emotional transformation intelligence
            emotional_intelligence = {
                "emotional_journey_mapping": emotional_journey,
                "psychological_triggers": psychological_triggers,
                "emotional_value_propositions": emotional_value_props,
                "transformation_narratives": transformation_narratives,
                "emotional_engagement_strategies": engagement_strategies,
                "emotional_impact_score": self._calculate_emotional_impact_score(
                    emotional_journey, psychological_triggers, emotional_value_props
                ),
                "generated_at": datetime.utcnow().isoformat(),
                "ai_provider": self.available_provider.get("name"),
                "enhancement_confidence": 0.86
            }
            
            logger.info(f"✅ Generated emotional transformation intelligence for {product_name}")
            return emotional_intelligence
            
        except Exception as e:
            logger.error(f"❌ Emotional transformation intelligence generation failed: {str(e)}")
            return self._generate_fallback_emotional_intelligence(product_data)
    
    async def _generate_emotional_journey_mapping(
        self, 
        product_name: str, 
        psych_intel: Dict[str, Any],
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed emotional journey mapping"""
        
        pain_points = psych_intel.get("pain_points", [])
        emotional_triggers = psych_intel.get("emotional_triggers", [])
        value_props = offer_intel.get("value_propositions", [])
        
        prompt = f"""
        As an emotional journey expert, map the customer emotional journey for "{product_name}".
        
        Customer pain points: {json.dumps(pain_points, indent=2)}
        Emotional triggers: {json.dumps(emotional_triggers, indent=2)}
        Value propositions: {json.dumps(value_props, indent=2)}
        
        Create detailed emotional journey mapping including:
        1. Current emotional state (before product)
        2. Transformation process stages
        3. Desired emotional outcome
        4. Emotional milestones along the way
        5. Potential emotional barriers
        
        Format as JSON:
        {{
            "current_emotional_state": ["emotion1", "emotion2", "emotion3"],
            "transformation_stages": [
                {{"stage": "stage1", "emotions": ["emotion1", "emotion2"], "triggers": ["trigger1"]}},
                {{"stage": "stage2", "emotions": ["emotion3", "emotion4"], "triggers": ["trigger2"]}}
            ],
            "desired_outcome": ["outcome1", "outcome2"],
            "emotional_milestones": ["milestone1", "milestone2"],
            "emotional_barriers": ["barrier1", "barrier2"],
            "breakthrough_moments": ["moment1", "moment2"]
        }}
        """
        
        try:
            emotional_journey = await self._call_ai_provider(prompt)
            
            if isinstance(emotional_journey, str):
                emotional_journey = json.loads(emotional_journey)
            
            return emotional_journey if isinstance(emotional_journey, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Emotional journey mapping failed: {str(e)}")
            return self._fallback_emotional_journey_mapping()
    
    async def _generate_psychological_triggers(
        self, 
        product_name: str, 
        psych_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate psychological triggers analysis"""
        
        existing_triggers = psych_intel.get("emotional_triggers", [])
        target_audience = psych_intel.get("target_audience", "General audience")
        
        prompt = f"""
        As a behavioral psychologist, analyze psychological triggers for "{product_name}".
        
        Existing triggers: {json.dumps(existing_triggers, indent=2)}
        Target audience: {target_audience}
        
        Generate psychological triggers including:
        1. Trust-building triggers
        2. Urgency and scarcity triggers
        3. Social proof triggers
        4. Authority and credibility triggers
        5. Emotional comfort triggers
        6. Decision facilitation triggers
        
        Format as JSON:
        {{
            "trust_building": ["trigger1", "trigger2"],
            "urgency_scarcity": ["trigger1", "trigger2"],
            "social_proof": ["trigger1", "trigger2"],
            "authority_credibility": ["trigger1", "trigger2"],
            "emotional_comfort": ["trigger1", "trigger2"],
            "decision_facilitation": ["trigger1", "trigger2"],
            "psychological_safety": ["safety1", "safety2"]
        }}
        """
        
        try:
            psychological_triggers = await self._call_ai_provider(prompt)
            
            if isinstance(psychological_triggers, str):
                psychological_triggers = json.loads(psychological_triggers)
            
            return psychological_triggers if isinstance(psychological_triggers, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Psychological triggers generation failed: {str(e)}")
            return self._fallback_psychological_triggers()
    
    async def _generate_emotional_value_propositions(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate emotional value propositions"""
        
        value_props = offer_intel.get("value_propositions", [])
        benefits = offer_intel.get("insights", [])
        
        prompt = f"""
        As an emotional messaging expert, create emotional value propositions for "{product_name}".
        
        Functional value propositions: {json.dumps(value_props, indent=2)}
        Product benefits: {json.dumps(benefits, indent=2)}
        
        Generate emotional value propositions including:
        1. Emotional benefits and outcomes
        2. Feeling-focused messaging
        3. Aspirational positioning
        4. Peace of mind propositions
        5. Confidence-building messages
        
        Format as JSON:
        {{
            "emotional_benefits": ["benefit1", "benefit2", "benefit3"],
            "feeling_focused": ["feeling1", "feeling2"],
            "aspirational": ["aspiration1", "aspiration2"],
            "peace_of_mind": ["peace1", "peace2"],
            "confidence_building": ["confidence1", "confidence2"],
            "empowerment_messages": ["empowerment1", "empowerment2"]
        }}
        """
        
        try:
            emotional_value_props = await self._call_ai_provider(prompt)
            
            if isinstance(emotional_value_props, str):
                emotional_value_props = json.loads(emotional_value_props)
            
            return emotional_value_props if isinstance(emotional_value_props, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Emotional value propositions generation failed: {str(e)}")
            return self._fallback_emotional_value_propositions()
    
    async def _generate_transformation_narratives(
        self, 
        product_name: str, 
        base_intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate transformation narratives"""
        
        prompt = f"""
        As a transformation storytelling expert, create narratives for "{product_name}".
        
        Generate transformation narratives including:
        1. Hero's journey adaptation for customers
        2. Problem to solution story arcs
        3. Transformation milestone stories
        4. Success achievement narratives
        5. Empowerment and growth stories
        
        Format as JSON:
        {{
            "heros_journey": ["journey1", "journey2"],
            "problem_solution_arcs": ["arc1", "arc2"],
            "milestone_stories": ["story1", "story2"],
            "success_narratives": ["narrative1", "narrative2"],
            "empowerment_stories": ["story1", "story2"],
            "growth_frameworks": ["framework1", "framework2"]
        }}
        """
        
        try:
            transformation_narratives = await self._call_ai_provider(prompt)
            
            if isinstance(transformation_narratives, str):
                transformation_narratives = json.loads(transformation_narratives)
            
            return transformation_narratives if isinstance(transformation_narratives, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Transformation narratives generation failed: {str(e)}")
            return self._fallback_transformation_narratives()
    
    async def _generate_emotional_engagement_strategies(
        self, 
        product_name: str, 
        psych_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate emotional engagement strategies"""
        
        prompt = f"""
        As an emotional engagement strategist, develop strategies for "{product_name}".
        
        Generate emotional engagement strategies including:
        1. Emotional connection building
        2. Empathy and understanding demonstration
        3. Community and belonging creation
        4. Support and guidance provision
        5. Celebration and achievement recognition
        
        Format as JSON:
        {{
            "connection_building": ["strategy1", "strategy2"],
            "empathy_demonstration": ["demo1", "demo2"],
            "community_belonging": ["community1", "community2"],
            "support_guidance": ["support1", "support2"],
            "celebration_recognition": ["celebration1", "celebration2"],
            "emotional_touchpoints": ["touchpoint1", "touchpoint2"]
        }}
        """
        
        try:
            engagement_strategies = await self._call_ai_provider(prompt)
            
            if isinstance(engagement_strategies, str):
                engagement_strategies = json.loads(engagement_strategies)
            
            return engagement_strategies if isinstance(engagement_strategies, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Emotional engagement strategies generation failed: {str(e)}")
            return self._fallback_emotional_engagement_strategies()
    
    async def _call_ai_provider(self, prompt: str) -> Any:
        """Call the available AI provider"""
        
        if self.available_provider["name"] == "anthropic":
            response = await self.available_provider["client"].messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.4,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text
            
        elif self.available_provider["name"] == "openai":
            response = await self.available_provider["client"].chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an emotional psychology expert providing strategic insights. Always respond with valid JSON when requested."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=2000
            )
            return response.choices[0].message.content
        
        else:
            raise Exception("No supported AI provider available")
    
    def _calculate_emotional_impact_score(
        self, 
        emotional_journey: Dict[str, Any], 
        psychological_triggers: Dict[str, Any], 
        emotional_value_props: Dict[str, Any]
    ) -> float:
        """Calculate emotional impact score"""
        
        score = 0.4  # Base score
        
        # Emotional journey score
        if emotional_journey:
            score += min(len(emotional_journey) * 0.06, 0.20)
        
        # Psychological triggers score
        if psychological_triggers:
            score += min(len(psychological_triggers) * 0.05, 0.20)
        
        # Emotional value propositions score
        if emotional_value_props:
            score += min(len(emotional_value_props) * 0.04, 0.20)
        
        return min(score, 1.0)
    
    # Fallback methods
    def _generate_fallback_emotional_intelligence(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback emotional intelligence"""
        
        product_name = product_data.get("product_name", "Product")
        
        return {
            "emotional_journey_mapping": self._fallback_emotional_journey_mapping(),
            "psychological_triggers": self._fallback_psychological_triggers(),
            "emotional_value_propositions": self._fallback_emotional_value_propositions(),
            "transformation_narratives": self._fallback_transformation_narratives(),
            "emotional_engagement_strategies": self._fallback_emotional_engagement_strategies(),
            "emotional_impact_score": 0.74,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "fallback",
            "enhancement_confidence": 0.74
        }
    
    def _fallback_emotional_journey_mapping(self) -> Dict[str, Any]:
        """Fallback emotional journey mapping"""
        
        return {
            "current_emotional_state": [
                "Frustrated with current health situation",
                "Skeptical about new solutions",
                "Hopeful but cautious about changes"
            ],
            "transformation_stages": [
                {
                    "stage": "Discovery and Interest",
                    "emotions": ["curiosity", "cautious optimism"],
                    "triggers": ["compelling benefits", "social proof"]
                },
                {
                    "stage": "Evaluation and Trust Building",
                    "emotions": ["growing confidence", "reduced skepticism"],
                    "triggers": ["scientific backing", "guarantees"]
                },
                {
                    "stage": "Decision and Commitment",
                    "emotions": ["excitement", "determination"],
                    "triggers": ["trust established", "clear benefits"]
                }
            ],
            "desired_outcome": [
                "Confident in health choices",
                "Satisfied with results achieved",
                "Grateful for positive changes"
            ],
            "emotional_milestones": [
                "First moment of genuine interest",
                "Decision to trust and try",
                "First positive experience",
                "Sustained satisfaction"
            ],
            "emotional_barriers": [
                "Past disappointment with similar products",
                "Skepticism about health claims",
                "Fear of wasting money"
            ],
            "breakthrough_moments": [
                "Realizing this solution is different from others",
                "Experiencing first positive health changes",
                "Feeling confident about long-term benefits"
            ]
        }
    
    def _fallback_psychological_triggers(self) -> Dict[str, Any]:
        """Fallback psychological triggers"""
        
        return {
            "trust_building": [
                "Scientific research validation",
                "Money-back guarantee assurance",
                "Transparent ingredient disclosure"
            ],
            "urgency_scarcity": [
                "Limited-time introductory pricing",
                "Exclusive availability for health-conscious individuals"
            ],
            "social_proof": [
                "Customer success testimonials",
                "Healthcare professional endorsements",
                "Growing community of satisfied users"
            ],
            "authority_credibility": [
                "Expert formulation team",
                "Clinical research backing",
                "Professional-grade quality standards"
            ],
            "emotional_comfort": [
                "Risk-free trial period",
                "Supportive customer service",
                "Clear usage guidance"
            ],
            "decision_facilitation": [
                "Simple ordering process",
                "Clear benefit explanations",
                "No-pressure approach"
            ],
            "psychological_safety": [
                "Privacy protection assurance",
                "Secure transaction processing",
                "Professional discretion"
            ]
        }
    
    def _fallback_emotional_value_propositions(self) -> Dict[str, Any]:
        """Fallback emotional value propositions"""
        
        return {
            "emotional_benefits": [
                "Feel confident about your health choices",
                "Experience peace of mind with quality ingredients",
                "Enjoy the satisfaction of taking control of your wellness"
            ],
            "feeling_focused": [
                "Feel energized and vitalized",
                "Experience renewed confidence in your health"
            ],
            "aspirational": [
                "Achieve the health and vitality you deserve",
                "Become the healthiest version of yourself"
            ],
            "peace_of_mind": [
                "Trust in scientifically-backed solutions",
                "Feel secure with money-back guarantee protection"
            ],
            "confidence_building": [
                "Make health decisions with confidence",
                "Trust in proven, quality ingredients"
            ],
            "empowerment_messages": [
                "Take control of your health journey",
                "Empower yourself with evidence-based wellness"
            ]
        }
    
    def _fallback_transformation_narratives(self) -> Dict[str, Any]:
        """Fallback transformation narratives"""
        
        return {
            "heros_journey": [
                "From health concerns to wellness discovery",
                "Overcoming skepticism to achieve health goals"
            ],
            "problem_solution_arcs": [
                "Struggling with health challenges, finding the right solution",
                "Disappointed by past attempts, discovering what actually works"
            ],
            "milestone_stories": [
                "First week of positive changes",
                "One month of consistent improvement",
                "Three months of sustained health benefits"
            ],
            "success_narratives": [
                "Customer achieves health goals with sustained commitment",
                "Individual transforms health outlook through quality solution"
            ],
            "empowerment_stories": [
                "Taking charge of personal health with informed choices",
                "Building confidence through evidence-based wellness decisions"
            ],
            "growth_frameworks": [
                "Progressive health improvement over time",
                "Building healthy habits with support and guidance"
            ]
        }
    
    def _fallback_emotional_engagement_strategies(self) -> Dict[str, Any]:
        """Fallback emotional engagement strategies"""
        
        return {
            "connection_building": [
                "Share authentic customer stories and experiences",
                "Create content that resonates with health concerns"
            ],
            "empathy_demonstration": [
                "Acknowledge common health struggles and frustrations",
                "Show understanding of customer health journey challenges"
            ],
            "community_belonging": [
                "Foster community of health-conscious individuals",
                "Create sense of belonging among quality-focused customers"
            ],
            "support_guidance": [
                "Provide helpful health and wellness education",
                "Offer ongoing support throughout customer journey"
            ],
            "celebration_recognition": [
                "Celebrate customer health achievements and milestones",
                "Recognize commitment to quality health choices"
            ],
            "emotional_touchpoints": [
                "Welcome new customers with warmth and support",
                "Follow up with care and genuine interest in progress"
            ]
        }