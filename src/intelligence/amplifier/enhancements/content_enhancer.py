# src/intelligence/amplifier/enhancements/content_enhancer.py
"""
Generates enhanced content intelligence using ULTRA-CHEAP AI providers
UPDATED: Integrated with tiered AI provider system for 95-99% cost savings
FIXED: Added throttling and proper error handling
FIXED: Now uses centralized AI system with automatic provider failover
🔥 FIXED: Added product name fix to prevent AI-generated placeholders
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json

from ...utils.ai_throttle import safe_ai_call
# 🔥 ADD THESE IMPORTS
from ...utils.product_name_fix import (
    extract_product_name_from_intelligence,
    extract_company_name_from_intelligence,
    substitute_placeholders_in_data,
    validate_no_placeholders
)

logger = logging.getLogger(__name__)

class ContentIntelligenceEnhancer:
    """Generate enhanced content intelligence and messaging optimization using ultra-cheap AI"""
    
    def __init__(self, ai_providers: List[Dict]):
        self.ai_providers = ai_providers
        self.available_provider = self._get_ultra_cheap_provider()
        
        # Log the ultra-cheap optimization status
        if self.available_provider:
            provider_name = self.available_provider.get("name", "unknown")
            cost_per_1k = self.available_provider.get("cost_per_1k_tokens", 0)
            quality_score = self.available_provider.get("quality_score", 0)
            
            logger.info(f"🚀 Content Enhancer using ULTRA-CHEAP provider: {provider_name}")
            logger.info(f"💰 Cost: ${cost_per_1k:.5f}/1K tokens (vs $0.030 OpenAI)")
            logger.info(f"🎯 Quality: {quality_score}/100")
            
            # Calculate savings
            openai_cost = 0.030
            if cost_per_1k > 0:
                savings_pct = ((openai_cost - cost_per_1k) / openai_cost) * 100
                logger.info(f"💎 SAVINGS: {savings_pct:.1f}% cost reduction!")
        else:
            logger.warning("⚠️ No ultra-cheap AI providers available for Content Enhancement")
        
    def _get_ultra_cheap_provider(self) -> Optional[Dict]:
        """Get the best ultra-cheap AI provider using tiered system priority"""
        
        if not self.ai_providers:
            logger.warning("⚠️ No AI providers available for content enhancement")
            return None
        
        # Sort by priority (lowest first = cheapest/fastest)
        sorted_providers = sorted(
            [p for p in self.ai_providers if p.get("available", False)],
            key=lambda x: x.get("priority", 999)
        )
        
        if not sorted_providers:
            logger.warning("⚠️ No available AI providers for content enhancement")
            return None
        
        # Use the highest priority (cheapest) provider
        selected_provider = sorted_providers[0]
        
        provider_name = selected_provider.get("name", "unknown")
        cost = selected_provider.get("cost_per_1k_tokens", 0)
        quality = selected_provider.get("quality_score", 0)
        
        logger.info(f"✅ Selected ultra-cheap provider for content enhancement:")
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
    
    async def generate_content_intelligence(
        self, 
        product_data: Dict[str, Any], 
        base_intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate enhanced content intelligence using ultra-cheap AI"""
        
        if not self.available_provider:
            logger.warning("🚨 No ultra-cheap providers available, using fallback")
            return self._generate_fallback_content_intelligence(product_data)
        
        try:
            # Log cost optimization start
            provider_name = self.available_provider.get("name", "unknown")
            logger.info(f"📝 Starting content intelligence generation with {provider_name}")
            
            # Extract product information
            product_name = extract_product_name_from_intelligence(base_intelligence)
            
            # 🔥 Log product name extraction
            logger.info(f"🎯 Using product name: '{product_name}' for content generation")
            
            base_content = base_intelligence.get("content_intelligence", {})
            offer_intel = base_intelligence.get("offer_intelligence", {})
            
            # Generate enhanced key messages using ultra-cheap AI
            key_messages = await self._generate_enhanced_key_messages(product_name, base_content, offer_intel, base_intelligence)
            
            # Generate social proof amplification using ultra-cheap AI
            social_proof = await self._generate_social_proof_amplification(product_name, base_content, base_intelligence)
            
            # Generate success story frameworks using ultra-cheap AI
            success_stories = await self._generate_success_story_frameworks(product_name, base_content, base_intelligence)
            
            # Generate messaging hierarchy using ultra-cheap AI
            messaging_hierarchy = await self._generate_messaging_hierarchy(product_name, offer_intel, base_intelligence)
            
            # Generate engagement optimization using ultra-cheap AI
            engagement_optimization = await self._generate_engagement_optimization(product_name, base_intelligence, base_intelligence)
            
            # Calculate content performance score
            content_performance = self._calculate_content_performance_score(
                key_messages, social_proof, success_stories
            )
            
            # Compile enhanced content intelligence with ultra-cheap metadata
            content_intelligence = {
                "enhanced_key_messages": key_messages,
                "social_proof_amplification": social_proof,
                "success_story_frameworks": success_stories,
                "messaging_hierarchy": messaging_hierarchy,
                "engagement_optimization": engagement_optimization,
                "content_performance_score": content_performance,
                "generated_at": datetime.now(timezone.utc).astimezone().isoformat(),
                "ai_provider": provider_name,
                "enhancement_confidence": 0.83,
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
            final_result = substitute_placeholders_in_data(content_intelligence, product_name, company_name)
            
            # Log successful generation with cost data
            total_items = (
                len(key_messages) + 
                len(social_proof) + 
                len(success_stories) +
                len(messaging_hierarchy) +
                len(engagement_optimization)
            )
            
            logger.info(f"✅ Content intelligence generated using {provider_name}")
            logger.info(f"📊 Generated {total_items} content items")
            logger.info(f"💰 Cost optimization: {self._calculate_cost_savings():.1f}% savings")
            logger.info(f"🔧 Product name fix: Applied '{product_name}' throughout content")
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Ultra-cheap content intelligence generation failed: {str(e)}")
            logger.info("🔄 Falling back to static content intelligence")
            return self._generate_fallback_content_intelligence(product_data)
    
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
    
    async def _generate_enhanced_key_messages(
        self, 
        product_name: str, 
        base_content: Dict[str, Any],
        offer_intel: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate enhanced key messaging using ultra-cheap AI"""
        
        existing_messages = base_content.get("key_messages", [])
        value_props = offer_intel.get("value_propositions", [])
        
        prompt = f"""
        As a messaging strategist, enhance key messages for "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
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
            logger.info(f"💬 Generating key messages with {self.available_provider.get('name')}")
            key_messages = await self._call_ultra_cheap_ai(prompt, intelligence)
            
            if isinstance(key_messages, str):
                key_messages = json.loads(key_messages)
            
            result = key_messages if isinstance(key_messages, dict) else {}
            logger.info(f"✅ Generated key messages with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Key messages generation failed: {str(e)}")
            return self._fallback_key_messages(product_name)
    
    async def _generate_social_proof_amplification(
        self, 
        product_name: str, 
        base_content: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate social proof amplification strategies using ultra-cheap AI"""
        
        existing_social_proof = base_content.get("social_proof", [])
        
        prompt = f"""
        As a social proof expert, amplify social proof for "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
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
            logger.info(f"👥 Generating social proof amplification with {self.available_provider.get('name')}")
            social_proof = await self._call_ultra_cheap_ai(prompt, intelligence)
            
            if isinstance(social_proof, str):
                social_proof = json.loads(social_proof)
            
            result = social_proof if isinstance(social_proof, dict) else {}
            logger.info(f"✅ Generated social proof amplification with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Social proof amplification failed: {str(e)}")
            return self._fallback_social_proof_amplification()
    
    async def _generate_success_story_frameworks(
        self, 
        product_name: str, 
        base_content: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate success story frameworks using ultra-cheap AI"""
        
        existing_stories = base_content.get("success_stories", [])
        
        prompt = f"""
        As a storytelling expert, create success story frameworks for "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
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
            logger.info(f"📖 Generating success story frameworks with {self.available_provider.get('name')}")
            success_stories = await self._call_ultra_cheap_ai(prompt, intelligence)
            
            if isinstance(success_stories, str):
                success_stories = json.loads(success_stories)
            
            result = success_stories if isinstance(success_stories, dict) else {}
            logger.info(f"✅ Generated success story frameworks with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Success story frameworks generation failed: {str(e)}")
            return self._fallback_success_story_frameworks()
    
    async def _generate_messaging_hierarchy(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate messaging hierarchy optimization using ultra-cheap AI"""
        
        prompt = f"""
        As a messaging architect, create messaging hierarchy for "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
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
            logger.info(f"🏗️ Generating messaging hierarchy with {self.available_provider.get('name')}")
            messaging_hierarchy = await self._call_ultra_cheap_ai(prompt, intelligence)
            
            if isinstance(messaging_hierarchy, str):
                messaging_hierarchy = json.loads(messaging_hierarchy)
            
            result = messaging_hierarchy if isinstance(messaging_hierarchy, dict) else {}
            logger.info(f"✅ Generated messaging hierarchy with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Messaging hierarchy generation failed: {str(e)}")
            return self._fallback_messaging_hierarchy()
    
    async def _generate_engagement_optimization(
        self, 
        product_name: str, 
        base_intelligence: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate engagement optimization strategies using ultra-cheap AI"""
        
        prompt = f"""
        As an engagement expert, optimize content engagement for "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
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
            logger.info(f"🎯 Generating engagement optimization with {self.available_provider.get('name')}")
            engagement_optimization = await self._call_ultra_cheap_ai(prompt, intelligence)
            
            if isinstance(engagement_optimization, str):
                engagement_optimization = json.loads(engagement_optimization)
            
            result = engagement_optimization if isinstance(engagement_optimization, dict) else {}
            logger.info(f"✅ Generated engagement optimization with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Engagement optimization generation failed: {str(e)}")
            return self._fallback_engagement_optimization()
    
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
    
    # Fallback methods (updated with ultra-cheap metadata)
    def _generate_fallback_content_intelligence(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback content intelligence with ultra-cheap metadata"""
        
        # 🔥 Extract product name from product_data
        product_name = product_data.get("product_name", "Product")
        
        # Generate fallback data
        fallback_data = {
            "enhanced_key_messages": self._fallback_key_messages(product_name),
            "social_proof_amplification": self._fallback_social_proof_amplification(),
            "success_story_frameworks": self._fallback_success_story_frameworks(),
            "messaging_hierarchy": self._fallback_messaging_hierarchy(),
            "engagement_optimization": self._fallback_engagement_optimization(),
            "content_performance_score": 0.68,
            "generated_at": datetime.now(timezone.utc).astimezone().isoformat(),
            "ai_provider": "fallback",
            "enhancement_confidence": 0.68,
            "product_name_fix_applied": True,
            "actual_product_name": product_name,
            "ultra_cheap_optimization": {
                "provider_used": "fallback_static",
                "cost_per_1k_tokens": 0.0,
                "quality_score": 68,
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