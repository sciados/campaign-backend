# src/intelligence/amplifier/enhancements/content_enhancer.py
"""
Generates enhanced content intelligence using AI
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ContentIntelligenceEnhancer:
    """Generate enhanced content intelligence and messaging optimization"""
    
    def __init__(self, ai_providers: List[Dict]):
        self.ai_providers = ai_providers
        self.available_provider = self._get_best_provider()
        
    def __init__(self, ai_providers: List[Dict]):
        self.ai_providers = ai_providers
        self.available_provider = self._get_best_provider()
        
    def _get_best_provider(self) -> Optional[Dict]:
        """Get the best available AI provider - prefer OpenAI for stability"""
        
        # Prefer OpenAI first (working perfectly)
        for provider in self.ai_providers:
            if provider.get("name") == "openai" and provider.get("available"):
                logger.info("🚀 Using OpenAI for content enhancement")
                return provider
        
        # Fallback to Cohere second
        for provider in self.ai_providers:
            if provider.get("name") == "cohere" and provider.get("available"):
                logger.info("💫 Using Cohere for content enhancement") 
                return provider
        
        # Fallback to Claude third (has API issues currently)
        for provider in self.ai_providers:
            if provider.get("name") == "anthropic" and provider.get("available"):
                logger.info("🤖 Using Claude for content enhancement")
                return provider
        
        logger.warning("⚠️ No AI providers available for content enhancement")
        return None
        
        # Prefer OpenAI for content and messaging
        for provider in self.ai_providers:
            if provider.get("name") == "openai" and provider.get("available"):
                logger.info("📝 Using OpenAI for content enhancement")
                return provider
        
        # Fallback to Anthropic Claude
        for provider in self.ai_providers:
            if provider.get("name") == "anthropic" and provider.get("available"):
                logger.info("📝 Using Anthropic Claude for content enhancement")
                return provider
        
        logger.warning("⚠️ No AI providers available for content enhancement")
        return None
    
    async def generate_content_intelligence(
        self, 
        product_data: Dict[str, Any], 
        base_intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate enhanced content intelligence"""
        
        if not self.available_provider:
            return self._generate_fallback_content_intelligence(product_data)
        
        try:
            # Extract product information
            product_name = product_data.get("product_name", "Product")
            base_content = base_intelligence.get("content_intelligence", {})
            offer_intel = base_intelligence.get("offer_intelligence", {})
            
            # Generate enhanced key messages
            key_messages = await self._generate_enhanced_key_messages(product_name, base_content, offer_intel)
            
            # Generate social proof amplification
            social_proof = await self._generate_social_proof_amplification(product_name, base_content)
            
            # Generate success story frameworks
            success_stories = await self._generate_success_story_frameworks(product_name, base_content)
            
            # Generate messaging hierarchy
            messaging_hierarchy = await self._generate_messaging_hierarchy(product_name, offer_intel)
            
            # Generate engagement optimization
            engagement_optimization = await self._generate_engagement_optimization(product_name, base_intelligence)
            
            # Compile enhanced content intelligence
            content_intelligence = {
                "enhanced_key_messages": key_messages,
                "social_proof_amplification": social_proof,
                "success_story_frameworks": success_stories,
                "messaging_hierarchy": messaging_hierarchy,
                "engagement_optimization": engagement_optimization,
                "content_performance_score": self._calculate_content_performance_score(
                    key_messages, social_proof, success_stories
                ),
                "generated_at": datetime.utcnow().isoformat(),
                "ai_provider": self.available_provider.get("name"),
                "enhancement_confidence": 0.83
            }
            
            logger.info(f"✅ Generated content intelligence for {product_name}")
            return content_intelligence
            
        except Exception as e:
            logger.error(f"❌ Content intelligence generation failed: {str(e)}")
            return self._generate_fallback_content_intelligence(product_data)
    
    async def _generate_enhanced_key_messages(
        self, 
        product_name: str, 
        base_content: Dict[str, Any],
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate enhanced key messaging"""
        
        existing_messages = base_content.get("key_messages", [])
        value_props = offer_intel.get("value_propositions", [])
        
        prompt = f"""
        As a messaging strategist, enhance key messages for "{product_name}".
        
        Existing messages: {json.dumps(existing_messages, indent=2)}
        Value propositions: {json.dumps(value_props, indent=2)}
        
        Generate enhanced messaging including:
        1. Primary headline variations
        2. Supporting message points
        3. Benefit-focused messaging
        4. Problem-solution messaging
        5. Emotional connection messages
        
        Format as JSON:
        {{
            "primary_headlines": ["headline1", "headline2", "headline3"],
            "supporting_messages": ["message1", "message2"],
            "benefit_focused": ["benefit1", "benefit2", "benefit3"],
            "problem_solution": ["solution1", "solution2"],
            "emotional_connection": ["emotional1", "emotional2"],
            "call_to_action_variations": ["cta1", "cta2", "cta3"]
        }}
        """
        
        try:
            key_messages = await self._call_ai_provider(prompt)
            
            if isinstance(key_messages, str):
                key_messages = json.loads(key_messages)
            
            return key_messages if isinstance(key_messages, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Key messages generation failed: {str(e)}")
            return self._fallback_key_messages(product_name)
    
    async def _generate_social_proof_amplification(
        self, 
        product_name: str, 
        base_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate social proof amplification strategies"""
        
        existing_social_proof = base_content.get("social_proof", [])
        
        prompt = f"""
        As a social proof expert, amplify social proof for "{product_name}".
        
        Existing social proof: {json.dumps(existing_social_proof, indent=2)}
        
        Generate social proof amplification including:
        1. Testimonial enhancement strategies
        2. User-generated content frameworks
        3. Community building approaches
        4. Influence and authority signals
        5. Trust-building social elements
        
        Format as JSON:
        {{
            "testimonial_strategies": ["strategy1", "strategy2"],
            "user_content_frameworks": ["framework1", "framework2"],
            "community_building": ["approach1", "approach2"],
            "authority_signals": ["signal1", "signal2"],
            "trust_elements": ["element1", "element2", "element3"],
            "social_validation": ["validation1", "validation2"]
        }}
        """
        
        try:
            social_proof = await self._call_ai_provider(prompt)
            
            if isinstance(social_proof, str):
                social_proof = json.loads(social_proof)
            
            return social_proof if isinstance(social_proof, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Social proof amplification failed: {str(e)}")
            return self._fallback_social_proof_amplification()
    
    async def _generate_success_story_frameworks(
        self, 
        product_name: str, 
        base_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate success story frameworks"""
        
        existing_stories = base_content.get("success_stories", [])
        
        prompt = f"""
        As a storytelling expert, create success story frameworks for "{product_name}".
        
        Existing stories: {json.dumps(existing_stories, indent=2)}
        
        Generate success story frameworks including:
        1. Story structure templates
        2. Customer journey narratives
        3. Transformation story formats
        4. Before/after frameworks
        5. Case study templates
        
        Format as JSON:
        {{
            "story_templates": ["template1", "template2"],
            "journey_narratives": ["narrative1", "narrative2"],
            "transformation_formats": ["format1", "format2"],
            "before_after_frameworks": ["framework1", "framework2"],
            "case_study_templates": ["template1", "template2"],
            "emotional_arcs": ["arc1", "arc2"]
        }}
        """
        
        try:
            success_stories = await self._call_ai_provider(prompt)
            
            if isinstance(success_stories, str):
                success_stories = json.loads(success_stories)
            
            return success_stories if isinstance(success_stories, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Success story frameworks generation failed: {str(e)}")
            return self._fallback_success_story_frameworks()
    
    async def _generate_messaging_hierarchy(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate messaging hierarchy optimization"""
        
        prompt = f"""
        As a messaging architect, create messaging hierarchy for "{product_name}".
        
        Product context: {json.dumps(offer_intel, indent=2)}
        
        Generate messaging hierarchy including:
        1. Primary message priority
        2. Supporting message layers
        3. Proof point sequences
        4. Emotional to logical flow
        5. Objection handling sequence
        
        Format as JSON:
        {{
            "primary_messages": ["message1", "message2"],
            "supporting_layers": ["layer1", "layer2", "layer3"],
            "proof_sequences": ["proof1", "proof2"],
            "emotional_logical_flow": ["flow1", "flow2"],
            "objection_handling": ["objection1", "objection2"],
            "hierarchy_structure": ["structure1", "structure2"]
        }}
        """
        
        try:
            messaging_hierarchy = await self._call_ai_provider(prompt)
            
            if isinstance(messaging_hierarchy, str):
                messaging_hierarchy = json.loads(messaging_hierarchy)
            
            return messaging_hierarchy if isinstance(messaging_hierarchy, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Messaging hierarchy generation failed: {str(e)}")
            return self._fallback_messaging_hierarchy()
    
    async def _generate_engagement_optimization(
        self, 
        product_name: str, 
        base_intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate engagement optimization strategies"""
        
        prompt = f"""
        As an engagement expert, optimize content engagement for "{product_name}".
        
        Generate engagement optimization including:
        1. Attention-grabbing techniques
        2. Interactive content ideas
        3. Personalization strategies
        4. Multi-format content approaches
        5. Engagement tracking methods
        
        Format as JSON:
        {{
            "attention_techniques": ["technique1", "technique2"],
            "interactive_content": ["idea1", "idea2"],
            "personalization": ["strategy1", "strategy2"],
            "multi_format_approaches": ["approach1", "approach2"],
            "engagement_tracking": ["method1", "method2"],
            "optimization_tactics": ["tactic1", "tactic2"]
        }}
        """
        
        try:
            engagement_optimization = await self._call_ai_provider(prompt)
            
            if isinstance(engagement_optimization, str):
                engagement_optimization = json.loads(engagement_optimization)
            
            return engagement_optimization if isinstance(engagement_optimization, dict) else {}
            
        except Exception as e:
            logger.error(f"❌ Engagement optimization generation failed: {str(e)}")
            return self._fallback_engagement_optimization()
    
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
                        "content": "You are a content and messaging expert. Always respond with valid JSON when requested."
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
    
    def _calculate_content_performance_score(
        self, 
        key_messages: Dict[str, Any], 
        social_proof: Dict[str, Any], 
        success_stories: Dict[str, Any]
    ) -> float:
        """Calculate content performance score"""
        
        score = 0.4  # Base score
        
        # Key messages score
        if key_messages:
            score += min(len(key_messages) * 0.06, 0.20)
        
        # Social proof score
        if social_proof:
            score += min(len(social_proof) * 0.05, 0.20)
        
        # Success stories score
        if success_stories:
            score += min(len(success_stories) * 0.04, 0.20)
        
        return min(score, 1.0)
    
    # Fallback methods
    def _generate_fallback_content_intelligence(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback content intelligence"""
        
        product_name = product_data.get("product_name", "Product")
        
        return {
            "enhanced_key_messages": self._fallback_key_messages(product_name),
            "social_proof_amplification": self._fallback_social_proof_amplification(),
            "success_story_frameworks": self._fallback_success_story_frameworks(),
            "messaging_hierarchy": self._fallback_messaging_hierarchy(),
            "engagement_optimization": self._fallback_engagement_optimization(),
            "content_performance_score": 0.68,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "fallback",
            "enhancement_confidence": 0.68
        }
    
    def _fallback_key_messages(self, product_name: str) -> Dict[str, Any]:
        """Fallback key messages"""
        
        return {
            "primary_headlines": [
                f"Discover the Power of {product_name}",
                f"Transform Your Health with {product_name}",
                f"Experience {product_name} - Your Health Solution"
            ],
            "supporting_messages": [
                "Quality ingredients for optimal results",
                "Trusted by health-conscious individuals"
            ],
            "benefit_focused": [
                "Supports your health and wellness goals",
                "Natural approach to better health",
                "Quality you can trust"
            ],
            "problem_solution": [
                "Addresses your health concerns naturally",
                "Provides the solution you've been seeking"
            ],
            "emotional_connection": [
                "Feel confident in your health choices",
                "Experience the peace of mind you deserve"
            ],
            "call_to_action_variations": [
                "Start your health journey today",
                "Experience the difference now",
                "Take action for your health"
            ]
        }
    
    def _fallback_social_proof_amplification(self) -> Dict[str, Any]:
        """Fallback social proof amplification"""
        
        return {
            "testimonial_strategies": [
                "Feature authentic customer experiences",
                "Highlight transformation stories",
                "Showcase diverse user demographics"
            ],
            "user_content_frameworks": [
                "Before and after success stories",
                "Customer video testimonials",
                "Written review highlights"
            ],
            "community_building": [
                "Create customer success community",
                "Encourage user-generated content sharing",
                "Build brand ambassador programs"
            ],
            "authority_signals": [
                "Professional endorsements",
                "Expert recommendations",
                "Industry recognition"
            ],
            "trust_elements": [
                "Customer satisfaction guarantees",
                "Quality certifications display",
                "Transparent business practices"
            ],
            "social_validation": [
                "Customer count and growth metrics",
                "Positive review percentages",
                "Social media engagement rates"
            ]
        }
    
    def _fallback_success_story_frameworks(self) -> Dict[str, Any]:
        """Fallback success story frameworks"""
        
        return {
            "story_templates": [
                "Challenge - Solution - Result framework",
                "Before - During - After narrative structure"
            ],
            "journey_narratives": [
                "Discovery to transformation journey",
                "Problem identification to solution success"
            ],
            "transformation_formats": [
                "Quantified improvement metrics",
                "Qualitative life enhancement stories"
            ],
            "before_after_frameworks": [
                "Baseline measurement to current results",
                "Initial concerns to achieved outcomes"
            ],
            "case_study_templates": [
                "Detailed customer journey documentation",
                "Professional use case examples"
            ],
            "emotional_arcs": [
                "Frustration to relief and satisfaction",
                "Skepticism to confidence and trust"
            ]
        }
    
    def _fallback_messaging_hierarchy(self) -> Dict[str, Any]:
        """Fallback messaging hierarchy"""
        
        return {
            "primary_messages": [
                "Quality health solution for discerning customers",
                "Trusted choice for health-conscious individuals"
            ],
            "supporting_layers": [
                "Premium ingredient quality",
                "Customer satisfaction focus",
                "Professional-grade standards"
            ],
            "proof_sequences": [
                "Quality certifications first, then customer results",
                "Professional endorsements followed by user testimonials"
            ],
            "emotional_logical_flow": [
                "Emotional connection through health benefits",
                "Logical validation through quality and proof"
            ],
            "objection_handling": [
                "Address quality concerns with certifications",
                "Counter price objections with value demonstration"
            ],
            "hierarchy_structure": [
                "Primary benefit headline",
                "Supporting proof points",
                "Risk mitigation elements",
                "Call to action"
            ]
        }
    
    def _fallback_engagement_optimization(self) -> Dict[str, Any]:
        """Fallback engagement optimization"""
        
        return {
            "attention_techniques": [
                "Strong benefit-focused headlines",
                "Visual interest through formatting"
            ],
            "interactive_content": [
                "Customer quiz or assessment",
                "Interactive product comparison"
            ],
            "personalization": [
                "Targeted messaging by customer segment",
                "Customized content based on interests"
            ],
            "multi_format_approaches": [
                "Video testimonials and demonstrations",
                "Infographic benefit summaries"
            ],
            "engagement_tracking": [
                "Click-through rate monitoring",
                "Content interaction analytics"
            ],
            "optimization_tactics": [
                "A/B testing of key messages",
                "Progressive information disclosure"
            ]
        }