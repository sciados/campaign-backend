# src/intelligence/amplifier/enhancements/emotional_enhancer.py
"""
Generates emotional journey mapping and psychological insights using ULTRA-CHEAP AI providers
FIXED: Removed duplicate AI calling methods, using centralized ai_throttle for consistency
UPDATED: Integrated with tiered AI provider system for 95-99% cost savings
🔥 FIXED: Added product name fix to prevent AI-generated placeholders
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json

# FIXED: Import centralized AI throttling system
from ...utils.ai_throttle import safe_ai_call
# 🔥 ADD THESE IMPORTS
from ...utils.product_name_fix import (
    extract_product_name_from_intelligence,
    extract_company_name_from_intelligence,
    substitute_placeholders_in_data,
    validate_no_placeholders
)

logger = logging.getLogger(__name__)

class EmotionalTransformationEnhancer:
    """Generate emotional transformation intelligence and customer journey mapping using ultra-cheap AI"""
    
    def __init__(self, ai_providers: List[Dict]):
        self.ai_providers = ai_providers
        self.available_provider = self._get_ultra_cheap_provider()
        
        # Log the ultra-cheap optimization status
        if self.available_provider:
            provider_name = self.available_provider.get("name", "unknown")
            cost_per_1k = self.available_provider.get("cost_per_1k_tokens", 0)
            quality_score = self.available_provider.get("quality_score", 0)
            
            logger.info(f"🚀 Emotional Enhancer using ULTRA-CHEAP provider: {provider_name}")
            logger.info(f"💰 Cost: ${cost_per_1k:.5f}/1K tokens (vs $0.030 OpenAI)")
            logger.info(f"🎯 Quality: {quality_score}/100")
            
            # Calculate savings
            openai_cost = 0.030
            if cost_per_1k > 0:
                savings_pct = ((openai_cost - cost_per_1k) / openai_cost) * 100
                logger.info(f"💎 SAVINGS: {savings_pct:.1f}% cost reduction!")
        else:
            logger.warning("⚠️ No ultra-cheap AI providers available for Emotional Enhancement")
        
    def _get_ultra_cheap_provider(self) -> Optional[Dict]:
        """Get the best ultra-cheap AI provider using tiered system priority"""
        
        if not self.ai_providers:
            logger.warning("⚠️ No AI providers available for emotional enhancement")
            return None
        
        # Sort by priority (lowest first = cheapest/fastest)
        sorted_providers = sorted(
            [p for p in self.ai_providers if p.get("available", False)],
            key=lambda x: x.get("priority", 999)
        )
        
        if not sorted_providers:
            logger.warning("⚠️ No available AI providers for emotional enhancement")
            return None
        
        # Use the highest priority (cheapest) provider
        selected_provider = sorted_providers[0]
        
        provider_name = selected_provider.get("name", "unknown")
        cost = selected_provider.get("cost_per_1k_tokens", 0)
        quality = selected_provider.get("quality_score", 0)
        
        logger.info(f"✅ Selected ultra-cheap provider for emotional enhancement:")
        logger.info(f"   Provider: {provider_name}")
        logger.info(f"   Cost: ${cost:.5f}/1K tokens")
        logger.info(f"   Quality: {quality}/100")
        logger.info(f"   Priority: {selected_provider.get('priority', 'unknown')}")
        
        return selected_provider
    
    async def _call_ultra_cheap_ai(self, prompt: str, intelligence: Dict[str, Any]) -> Any:
        """
        🔥 FIXED: Call AI provider with automatic product name fix
        This ensures all AI responses use actual product names instead of placeholders
        """
        
        if not self.available_provider:
            raise Exception("No AI provider available")
            
        # 🔥 Extract actual product name before AI call
        product_name = extract_product_name_from_intelligence(intelligence)
        company_name = extract_company_name_from_intelligence(intelligence)
        
        # 🔥 Enhance prompt to include actual product name
        enhanced_prompt = f"""
        IMPORTANT: You are analyzing a product called "{product_name}". 
        Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", or similar.
        
        {prompt}
        """
        
        provider_name = self.available_provider["name"]
        client = self.available_provider["client"]
        
        # Create messages for the AI call
        messages = [
            {
                "role": "system",
                "content": f"You are an expert analyst for '{product_name}'. Always use the actual product name '{product_name}' in responses. Never use placeholders. Always respond with valid JSON when requested."
            },
            {
                "role": "user", 
                "content": enhanced_prompt
            }
        ]
        
        # Get the model name for this provider
        model_map = {
            "groq": "llama-3.3-70b-versatile",
            "together": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "deepseek": "deepseek-chat",
            "anthropic": "claude-3-haiku-20240307",
            "cohere": "command-r-plus",
            "openai": "gpt-3.5-turbo"
        }
        
        model = model_map.get(provider_name, "gpt-3.5-turbo")
        
        # Make the safe AI call with automatic throttling and JSON validation
        raw_result = await safe_ai_call(
            client=client,
            provider_name=provider_name,
            model=model,
            messages=messages,
            temperature=0.4,
            max_tokens=2000
        )
        
        # Handle fallback responses
        if isinstance(raw_result, dict) and raw_result.get("fallback"):
            logger.warning(f"⚠️ AI call returned fallback for {provider_name}")
            # Extract any useful fallback data
            if "fallback_data" in raw_result:
                raw_result = raw_result["fallback_data"]
            else:
                raise Exception("AI call failed and no fallback data available")
        
        # 🔥 Apply product name fix to AI response
        if raw_result:
            fixed_result = substitute_placeholders_in_data(raw_result, product_name, company_name)
            
            # 🔥 Validate that placeholders were removed
            if isinstance(fixed_result, str):
                is_clean = validate_no_placeholders(fixed_result, product_name)
                if not is_clean:
                    logger.warning(f"⚠️ AI response still contains placeholders after fix")
            
            # 🔥 Log the fix application
            logger.info(f"🔧 Applied product name fix: {product_name}")
            return fixed_result
        
        return raw_result
    
    async def generate_emotional_transformation_intelligence(
        self, 
        product_data: Dict[str, Any], 
        base_intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive emotional transformation intelligence using ultra-cheap AI"""
        
        if not self.available_provider:
            logger.warning("🚨 No ultra-cheap providers available, using fallback")
            return self._generate_fallback_emotional_intelligence(product_data)
        
        try:
            # Log cost optimization start
            provider_name = self.available_provider.get("name", "unknown")
            logger.info(f"💭 Starting emotional transformation intelligence with {provider_name}")
            
            # Extract product information
            product_name = extract_product_name_from_intelligence(base_intelligence)
            
            # 🔥 Log product name extraction
            logger.info(f"🎯 Using product name: '{product_name}' for emotional generation")
            
            psych_intel = base_intelligence.get("psychology_intelligence", {})
            offer_intel = base_intelligence.get("offer_intelligence", {})
            
            # Generate emotional journey mapping using centralized AI system
            emotional_journey = await self._generate_emotional_journey_mapping(product_name, psych_intel, offer_intel, base_intelligence)
            
            # Generate psychological triggers using centralized AI system
            psychological_triggers = await self._generate_psychological_triggers(product_name, psych_intel, base_intelligence)
            
            # Generate emotional value propositions using centralized AI system
            emotional_value_props = await self._generate_emotional_value_propositions(product_name, offer_intel, base_intelligence)
            
            # Generate transformation narratives using centralized AI system
            transformation_narratives = await self._generate_transformation_narratives(product_name, base_intelligence, base_intelligence)
            
            # Generate emotional engagement strategies using centralized AI system
            engagement_strategies = await self._generate_emotional_engagement_strategies(product_name, psych_intel, base_intelligence)
            
            # Calculate emotional impact score
            emotional_impact = self._calculate_emotional_impact_score(
                emotional_journey, psychological_triggers, emotional_value_props
            )
            
            # Compile emotional transformation intelligence with ultra-cheap metadata
            emotional_intelligence = {
                "emotional_journey_mapping": emotional_journey,
                "psychological_triggers": psychological_triggers,
                "emotional_value_propositions": emotional_value_props,
                "transformation_narratives": transformation_narratives,
                "emotional_engagement_strategies": engagement_strategies,
                "emotional_impact_score": emotional_impact,
                "generated_at": datetime.datetime.now(),
                "ai_provider": provider_name,
                "enhancement_confidence": 0.86,
                "product_name_fix_applied": True,  # 🔥 Track that fix was applied
                "actual_product_name": product_name,  # 🔥 Track actual product name used
                "ultra_cheap_optimization": {
                    "provider_used": provider_name,
                    "cost_per_1k_tokens": self.available_provider.get("cost_per_1k_tokens", 0),
                    "quality_score": self.available_provider.get("quality_score", 0),
                    "provider_tier": self.available_provider.get("provider_tier", "unknown"),
                    "estimated_cost_savings_vs_openai": self._calculate_cost_savings(),
                    "speed_rating": self.available_provider.get("speed_rating", 0)
                }
            }
            
            # 🔥 Apply final product name fix to entire result
            company_name = extract_company_name_from_intelligence(base_intelligence)
            final_result = substitute_placeholders_in_data(emotional_intelligence, product_name, company_name)
            
            # Log successful generation with cost data
            total_items = (
                len(emotional_journey) if isinstance(emotional_journey, dict) else 0 +
                len(psychological_triggers) if isinstance(psychological_triggers, dict) else 0 +
                len(emotional_value_props) if isinstance(emotional_value_props, dict) else 0 +
                len(transformation_narratives) if isinstance(transformation_narratives, dict) else 0 +
                len(engagement_strategies) if isinstance(engagement_strategies, dict) else 0
            )
            
            logger.info(f"✅ Emotional intelligence generated using {provider_name}")
            logger.info(f"📊 Generated {total_items} emotional items")
            logger.info(f"💰 Cost optimization: {self._calculate_cost_savings():.1f}% savings")
            logger.info(f"🔧 Product name fix: Applied '{product_name}' throughout content")
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Ultra-cheap emotional intelligence generation failed: {str(e)}")
            logger.info("🔄 Falling back to static emotional intelligence")
            return self._generate_fallback_emotional_intelligence(product_data)
    
    def _calculate_cost_savings(self) -> float:
        """Calculate cost savings percentage vs OpenAI"""
        try:
            openai_cost = 0.030  # OpenAI GPT-4 cost per 1K tokens
            provider_cost = self.available_provider.get("cost_per_1k_tokens", openai_cost)
            
            if provider_cost >= openai_cost:
                return 0.0
            
            savings_pct = ((openai_cost - provider_cost) / openai_cost) * 100
            return min(savings_pct, 99.9)  # Cap at 99.9%
            
        except Exception:
            return 0.0
    
    async def _generate_emotional_journey_mapping(
        self, 
        product_name: str, 
        psych_intel: Dict[str, Any],
        offer_intel: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed emotional journey mapping using centralized AI system"""
        
        pain_points = psych_intel.get("pain_points", [])
        emotional_triggers = psych_intel.get("emotional_triggers", [])
        value_props = offer_intel.get("value_propositions", [])
        
        prompt = f"""
        As an emotional journey expert, map the customer emotional journey for "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
        Customer pain points: {json.dumps(pain_points, indent=2)}
        Emotional triggers: {json.dumps(emotional_triggers, indent=2)}
        Value propositions: {json.dumps(value_props, indent=2)}
        
        Create detailed emotional journey mapping. Format as JSON:
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
            logger.info(f"🗺️ Generating emotional journey with {self.available_provider.get('name')}")
            emotional_journey = await self._call_ultra_cheap_ai(prompt, intelligence)
            
            # Handle string responses
            if isinstance(emotional_journey, str):
                try:
                    emotional_journey = json.loads(emotional_journey)
                except:
                    logger.warning("⚠️ Could not parse emotional journey as JSON, using fallback")
                    return self._fallback_emotional_journey_mapping()
            
            result = emotional_journey if isinstance(emotional_journey, dict) else {}
            logger.info(f"✅ Generated emotional journey with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Emotional journey mapping failed: {str(e)}")
            return self._fallback_emotional_journey_mapping()
    
    async def _generate_psychological_triggers(
        self, 
        product_name: str, 
        psych_intel: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate psychological triggers analysis using centralized AI system"""
        
        existing_triggers = psych_intel.get("emotional_triggers", [])
        target_audience = psych_intel.get("target_audience", "General audience")
        
        prompt = f"""
        As a behavioral psychologist, analyze psychological triggers for "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
        Existing triggers: {json.dumps(existing_triggers, indent=2)}
        Target audience: {target_audience}
        
        Generate psychological triggers. Format as JSON:
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
            logger.info(f"🧠 Generating psychological triggers with {self.available_provider.get('name')}")
            psychological_triggers = await self._call_ultra_cheap_ai(prompt, intelligence)
            
            # Handle string responses
            if isinstance(psychological_triggers, str):
                try:
                    psychological_triggers = json.loads(psychological_triggers)
                except:
                    logger.warning("⚠️ Could not parse psychological triggers as JSON, using fallback")
                    return self._fallback_psychological_triggers()
            
            result = psychological_triggers if isinstance(psychological_triggers, dict) else {}
            logger.info(f"✅ Generated psychological triggers with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Psychological triggers generation failed: {str(e)}")
            return self._fallback_psychological_triggers()
    
    async def _generate_emotional_value_propositions(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate emotional value propositions using centralized AI system"""
        
        value_props = offer_intel.get("value_propositions", [])
        benefits = offer_intel.get("insights", [])
        
        prompt = f"""
        As an emotional messaging expert, create emotional value propositions for "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
        Functional value propositions: {json.dumps(value_props, indent=2)}
        Product benefits: {json.dumps(benefits, indent=2)}
        
        Generate emotional value propositions. Format as JSON:
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
            logger.info(f"💝 Generating emotional value propositions with {self.available_provider.get('name')}")
            emotional_value_props = await self._call_ultra_cheap_ai(prompt, intelligence)
            
            # Handle string responses
            if isinstance(emotional_value_props, str):
                try:
                    emotional_value_props = json.loads(emotional_value_props)
                except:
                    logger.warning("⚠️ Could not parse emotional value props as JSON, using fallback")
                    return self._fallback_emotional_value_propositions()
            
            result = emotional_value_props if isinstance(emotional_value_props, dict) else {}
            logger.info(f"✅ Generated emotional value propositions with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Emotional value propositions generation failed: {str(e)}")
            return self._fallback_emotional_value_propositions()
    
    async def _generate_transformation_narratives(
        self, 
        product_name: str, 
        base_intelligence: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate transformation narratives using centralized AI system"""
        
        prompt = f"""
        As a transformation storytelling expert, create narratives for "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
        Generate transformation narratives. Format as JSON:
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
            logger.info(f"📖 Generating transformation narratives with {self.available_provider.get('name')}")
            transformation_narratives = await self._call_ultra_cheap_ai(prompt, intelligence)
            
            # Handle string responses
            if isinstance(transformation_narratives, str):
                try:
                    transformation_narratives = json.loads(transformation_narratives)
                except:
                    logger.warning("⚠️ Could not parse transformation narratives as JSON, using fallback")
                    return self._fallback_transformation_narratives()
            
            result = transformation_narratives if isinstance(transformation_narratives, dict) else {}
            logger.info(f"✅ Generated transformation narratives with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Transformation narratives generation failed: {str(e)}")
            return self._fallback_transformation_narratives()
    
    async def _generate_emotional_engagement_strategies(
        self, 
        product_name: str, 
        psych_intel: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate emotional engagement strategies using centralized AI system"""
        
        prompt = f"""
        As an emotional engagement strategist, develop strategies for "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
        Generate emotional engagement strategies. Format as JSON:
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
            logger.info(f"🤝 Generating emotional engagement with {self.available_provider.get('name')}")
            engagement_strategies = await self._call_ultra_cheap_ai(prompt, intelligence)
            
            # Handle string responses
            if isinstance(engagement_strategies, str):
                try:
                    engagement_strategies = json.loads(engagement_strategies)
                except:
                    logger.warning("⚠️ Could not parse engagement strategies as JSON, using fallback")
                    return self._fallback_emotional_engagement_strategies()
            
            result = engagement_strategies if isinstance(engagement_strategies, dict) else {}
            logger.info(f"✅ Generated emotional engagement with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Emotional engagement strategies generation failed: {str(e)}")
            return self._fallback_emotional_engagement_strategies()
    
    def _calculate_emotional_impact_score(
        self, 
        emotional_journey: Dict[str, Any], 
        psychological_triggers: Dict[str, Any], 
        emotional_value_props: Dict[str, Any]
    ) -> float:
        """Calculate emotional impact score"""
        
        score = 0.4  # Base score
        
        # Emotional journey score
        if emotional_journey and isinstance(emotional_journey, dict):
            score += min(len(emotional_journey) * 0.06, 0.20)
        
        # Psychological triggers score
        if psychological_triggers and isinstance(psychological_triggers, dict):
            score += min(len(psychological_triggers) * 0.05, 0.20)
        
        # Emotional value propositions score
        if emotional_value_props and isinstance(emotional_value_props, dict):
            score += min(len(emotional_value_props) * 0.04, 0.20)
        
        return min(score, 1.0)
    
    # Fallback methods (updated with ultra-cheap metadata)
    def _generate_fallback_emotional_intelligence(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback emotional intelligence with ultra-cheap metadata"""
        
        # 🔥 Extract product name from product_data
        product_name = product_data.get("product_name", "Product")
        
        # Generate fallback data
        fallback_data = {
            "emotional_journey_mapping": self._fallback_emotional_journey_mapping(),
            "psychological_triggers": self._fallback_psychological_triggers(),
            "emotional_value_propositions": self._fallback_emotional_value_propositions(),
            "transformation_narratives": self._fallback_transformation_narratives(),
            "emotional_engagement_strategies": self._fallback_emotional_engagement_strategies(),
            "emotional_impact_score": 0.74,
            "generated_at": datetime.datetime.now(),
            "ai_provider": "fallback",
            "enhancement_confidence": 0.74,
            "product_name_fix_applied": True,
            "actual_product_name": product_name,
            "ultra_cheap_optimization": {
                "provider_used": "fallback_static",
                "cost_per_1k_tokens": 0.0,
                "quality_score": 74,
                "provider_tier": "fallback",
                "estimated_cost_savings_vs_openai": 100.0,
                "fallback_reason": "No ultra-cheap providers available"
            }
        }
        
        # 🔥 Apply product name fix to fallback data
        company_name = extract_company_name_from_intelligence(product_data)
        final_fallback = substitute_placeholders_in_data(fallback_data, product_name, company_name)
        
        logger.info(f"🔧 Applied product name fix to fallback data: '{product_name}'")
        return final_fallback
    
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