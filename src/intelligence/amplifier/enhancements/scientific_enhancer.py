# src/intelligence/amplifier/enhancements/scientific_enhancer.py
"""
Generates comprehensive scientific backing for health claims using ULTRA-CHEAP AI providers
🔥 FIXED: Multi-provider failover - automatically switches between Groq, DeepSeek, Together
UPDATED: Integrated with tiered AI provider system for 95-99% cost savings
🔥 FIXED: Added product name fix to prevent AI-generated placeholders
"""
import logging
import asyncio
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

class ScientificIntelligenceEnhancer:
    """Generate scientific intelligence for health and wellness products using ultra-cheap AI with multi-provider failover"""
    
    def __init__(self, ai_providers: List[Dict]):
        self.ai_providers = ai_providers
        self.available_providers = self._get_all_ultra_cheap_providers()
        
        # Log the ultra-cheap optimization status
        if self.available_providers:
            logger.info(f"🚀 Scientific Enhancer initialized with {len(self.available_providers)} ultra-cheap providers:")
            for i, provider in enumerate(self.available_providers, 1):
                provider_name = provider.get("name", "unknown")
                cost_per_1k = provider.get("cost_per_1k_tokens", 0)
                quality_score = provider.get("quality_score", 0)
                logger.info(f"   {i}. {provider_name}: ${cost_per_1k:.5f}/1K tokens, quality: {quality_score}/100")
                
            # Calculate total cost savings
            cheapest_cost = min(p.get("cost_per_1k_tokens", 0.030) for p in self.available_providers)
            openai_cost = 0.030
            if cheapest_cost > 0:
                savings_pct = ((openai_cost - cheapest_cost) / openai_cost) * 100
                logger.info(f"💎 MAXIMUM SAVINGS: {savings_pct:.1f}% cost reduction vs OpenAI!")
        else:
            logger.warning("⚠️ No ultra-cheap AI providers available for Scientific Enhancement")
        
    def _get_all_ultra_cheap_providers(self) -> List[Dict]:
        """Get ALL available ultra-cheap AI providers sorted by cost"""
        
        if not self.ai_providers:
            logger.warning("⚠️ No AI providers available for scientific enhancement")
            return []
        
        # Get all available providers and sort by cost (cheapest first)
        available_providers = [p for p in self.ai_providers if p.get("available", False)]
        
        if not available_providers:
            logger.warning("⚠️ No available AI providers for scientific enhancement")
            return []
        
        # Sort by cost (cheapest first)
        sorted_providers = sorted(available_providers, key=lambda x: x.get("cost_per_1k_tokens", 999))
        
        logger.info(f"✅ Found {len(sorted_providers)} ultra-cheap providers for scientific enhancement")
        return sorted_providers
    
    async def _call_ultra_cheap_ai_with_failover(self, prompt: str, intelligence: Dict[str, Any]) -> Any:
        """
        🔥 FIXED: Call ultra-cheap AI with automatic failover across ALL providers and product name fix
        Tries Groq → DeepSeek → Together automatically when one fails
        """
        
        if not self.available_providers:
            raise Exception("No ultra-cheap AI providers available")
            
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
            
        last_error = None
        
        # Try each provider in cost order (cheapest first)
        for i, provider in enumerate(self.available_providers):
            provider_name = provider.get("name", "unknown")
            client = provider.get("client")
            cost_per_1k = provider.get("cost_per_1k_tokens", 0)
            
            if not client:
                logger.warning(f"⚠️ {provider_name}: No client available, skipping")
                continue
                
            try:
                logger.info(f"🔄 Scientific AI attempt {i+1}/{len(self.available_providers)}: {provider_name} (${cost_per_1k:.5f}/1K)")
                
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
                    temperature=0.3,
                    max_tokens=2000
                )
                
                # Check if result indicates fallback/error
                if isinstance(raw_result, dict) and raw_result.get("fallback"):
                    logger.warning(f"⚠️ {provider_name}: Returned fallback response, trying next provider")
                    last_error = Exception(f"{provider_name} returned fallback response")
                    
                    if i < len(self.available_providers) - 1:
                        await asyncio.sleep(1)  # Brief delay before trying next provider
                        continue
                    else:
                        raw_result = raw_result  # Return fallback on final attempt
                
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
                    logger.info(f"✅ Scientific AI success: {provider_name} (${cost_per_1k:.5f}/1K)")
                    return fixed_result
                
                return raw_result
                
            except Exception as e:
                error_msg = str(e)
                last_error = e
                
                logger.error(f"❌ {provider_name}: Failed - {error_msg}")
                
                # Check if it's a rate limit or server error
                if "rate limit" in error_msg.lower() or "429" in error_msg or "500" in error_msg:
                    logger.info(f"🔄 {provider_name}: Server issue detected, trying next provider immediately...")
                elif "timeout" in error_msg.lower():
                    logger.info(f"🔄 {provider_name}: Timeout detected, trying next provider...")
                else:
                    logger.info(f"🔄 {provider_name}: Error detected, trying next provider...")
                
                # If not the last provider, try the next one
                if i < len(self.available_providers) - 1:
                    await asyncio.sleep(1)  # Brief delay before trying next provider
                    continue
        
        # All providers failed
        logger.error(f"❌ All {len(self.available_providers)} ultra-cheap providers failed for scientific enhancement")
        raise Exception(f"All ultra-cheap AI providers failed. Last error: {str(last_error)}")
    
    async def generate_scientific_intelligence(
        self, 
        product_data: Dict[str, Any], 
        base_intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive scientific intelligence using ultra-cheap AI with failover"""
        
        if not self.available_providers:
            logger.warning("🚨 No ultra-cheap providers available, using fallback")
            return self._generate_fallback_scientific_intelligence(product_data)
        
        try:
            # Log cost optimization start
            primary_provider = self.available_providers[0].get("name", "unknown")
            logger.info(f"🧬 Starting scientific intelligence generation with {len(self.available_providers)} providers")
            logger.info(f"🎯 Primary provider: {primary_provider}, {len(self.available_providers)-1} backups available")
            
            # Extract product information
            product_name = extract_product_name_from_intelligence(base_intelligence)
            
            # 🔥 Log product name extraction
            logger.info(f"🎯 Using product name: '{product_name}' for scientific generation")
            
            offer_intel = base_intelligence.get("offer_intelligence", {})
            
            # Generate scientific backing using ultra-cheap AI with failover
            scientific_backing = await self._generate_scientific_backing(product_name, offer_intel, base_intelligence)
            
            # Generate ingredient research using ultra-cheap AI with failover
            ingredient_research = await self._generate_ingredient_research(product_name, offer_intel, base_intelligence)
            
            # Generate mechanism of action using ultra-cheap AI with failover
            mechanism_research = await self._generate_mechanism_research(product_name, offer_intel, base_intelligence)
            
            # Generate clinical evidence using ultra-cheap AI with failover
            clinical_evidence = await self._generate_clinical_evidence(product_name, offer_intel, base_intelligence)
            
            # Generate safety profile using ultra-cheap AI with failover
            safety_profile = await self._generate_safety_profile(product_name, offer_intel, base_intelligence)
            
            # Calculate research quality score
            research_quality = self._calculate_research_quality_score(
                scientific_backing, ingredient_research, clinical_evidence
            )
            
            # Determine which provider was actually used (for cost tracking)
            provider_used = primary_provider  # This could be enhanced to track actual provider used
            
            # Compile comprehensive scientific intelligence with ultra-cheap metadata
            scientific_intelligence = {
                "scientific_backing": scientific_backing,
                "ingredient_research": ingredient_research,
                "mechanism_of_action": mechanism_research,
                "clinical_evidence": clinical_evidence,
                "safety_profile": safety_profile,
                "research_quality_score": research_quality,
                "generated_at": datetime.now(timezone.utc).astimezone().isoformat(),
                "ai_provider": provider_used,
                "enhancement_confidence": 0.85,
                "product_name_fix_applied": True,  # 🔥 Track that fix was applied
                "actual_product_name": product_name,  # 🔥 Track actual product name used
                "ultra_cheap_optimization": {
                    "primary_provider": primary_provider,
                    "backup_providers": [p.get("name") for p in self.available_providers[1:]],
                    "total_providers_available": len(self.available_providers),
                    "cost_per_1k_tokens": self.available_providers[0].get("cost_per_1k_tokens", 0),
                    "quality_score": self.available_providers[0].get("quality_score", 0),
                    "provider_tier": "ultra_cheap_with_failover",
                    "estimated_cost_savings_vs_openai": self._calculate_cost_savings(),
                    "failover_enabled": True
                }
            }
            
            # 🔥 Apply final product name fix to entire result
            company_name = extract_company_name_from_intelligence(base_intelligence)
            final_result = substitute_placeholders_in_data(scientific_intelligence, product_name, company_name)
            
            # Log successful generation with cost data
            total_items = (
                len(scientific_backing) if isinstance(scientific_backing, list) else 0 +
                len(ingredient_research) if isinstance(ingredient_research, dict) else 0 +
                len(clinical_evidence) if isinstance(clinical_evidence, dict) else 0 +
                len(safety_profile) if isinstance(safety_profile, dict) else 0
            )
            
            logger.info(f"✅ Scientific intelligence generated with failover system")
            logger.info(f"📊 Generated {total_items} intelligence items")
            logger.info(f"💰 Cost optimization: {self._calculate_cost_savings():.1f}% savings")
            logger.info(f"🛡️ Failover protection: {len(self.available_providers)} providers available")
            logger.info(f"🔧 Product name fix: Applied '{product_name}' throughout content")
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Ultra-cheap scientific intelligence generation failed: {str(e)}")
            logger.info("🔄 Falling back to static scientific intelligence")
            return self._generate_fallback_scientific_intelligence(product_data)
    
    def _calculate_cost_savings(self) -> float:
        """Calculate cost savings percentage vs OpenAI using cheapest provider"""
        try:
            openai_cost = 0.030  # OpenAI GPT-4 cost per 1K tokens
            cheapest_cost = min(p.get("cost_per_1k_tokens", openai_cost) for p in self.available_providers)
            
            if cheapest_cost >= openai_cost:
                return 0.0
            
            savings_pct = ((openai_cost - cheapest_cost) / openai_cost) * 100
            return min(savings_pct, 99.9)  # Cap at 99.9%
            
        except Exception:
            return 0.0
    
    async def _generate_scientific_backing(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> List[str]:
        """Generate scientific backing statements using ultra-cheap AI with failover"""
        
        # Extract health claims from offer intelligence
        value_props = offer_intel.get("value_propositions", [])
        benefits = offer_intel.get("insights", [])
        
        prompt = f"""
        As a scientific researcher, provide evidence-based backing for a health product called "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
        Product claims and benefits:
        {json.dumps(value_props + benefits, indent=2)}
        
        Generate 6-8 scientific backing statements that:
        1. Reference general research categories (not specific studies)
        2. Use proper scientific terminology
        3. Focus on mechanisms and pathways
        4. Are factual but not overreaching
        5. Support the health claims appropriately
        
        Format as a JSON array of strings. Example:
        [
            "Clinical research demonstrates that natural compounds can support liver detoxification pathways",
            "Studies indicate that certain botanical extracts may enhance metabolic function",
            "Research validates the role of antioxidants in supporting cellular health"
        ]
        
        Generate evidence-based scientific backing:
        """
        
        try:
            logger.info(f"🧬 Generating scientific backing with multi-provider failover")
            scientific_backing = await self._call_ultra_cheap_ai_with_failover(prompt, intelligence)
            
            # Parse JSON response
            if isinstance(scientific_backing, str):
                scientific_backing = json.loads(scientific_backing)
            
            result = scientific_backing if isinstance(scientific_backing, list) else []
            logger.info(f"✅ Generated {len(result)} scientific backing statements")
            return result
            
        except Exception as e:
            logger.error(f"❌ Scientific backing generation failed: {str(e)}")
            return self._fallback_scientific_backing(product_name)
    
    async def _generate_ingredient_research(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate ingredient research information using ultra-cheap AI with failover"""
        
        prompt = f"""
        As a nutritional scientist, provide research-based information about potential ingredients for a product called "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
        Based on the product name and common health supplement categories, generate ingredient research that includes:
        
        1. Primary active compounds typically found in such products
        2. Research on bioavailability and absorption
        3. Synergistic effects between ingredients
        4. Quality and purity considerations
        
        Provide factual, research-based information without making specific medical claims.
        
        Format as JSON:
        {{
            "primary_compounds": ["compound1", "compound2"],
            "bioavailability_research": ["research point 1", "research point 2"],
            "synergistic_effects": ["effect 1", "effect 2"],
            "quality_factors": ["factor 1", "factor 2"]
        }}
        """
        
        try:
            logger.info(f"🧪 Generating ingredient research with multi-provider failover")
            ingredient_research = await self._call_ultra_cheap_ai_with_failover(prompt, intelligence)
            
            if isinstance(ingredient_research, str):
                ingredient_research = json.loads(ingredient_research)
            
            result = ingredient_research if isinstance(ingredient_research, dict) else {}
            logger.info(f"✅ Generated ingredient research with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ingredient research generation failed: {str(e)}")
            return self._fallback_ingredient_research(product_name)
    
    async def _generate_mechanism_research(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate mechanism of action research using ultra-cheap AI with failover"""
        
        # Determine product category for targeted research
        product_category = self._determine_product_category(product_name, offer_intel)
        
        prompt = f"""
        As a biochemist, explain the potential mechanisms of action for a {product_category} product called "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
        Provide research-based explanations of:
        1. Primary biological pathways involved
        2. Cellular mechanisms
        3. Physiological processes
        4. Metabolic interactions
        
        Use scientific terminology and focus on established biological processes.
        
        Format as JSON:
        {{
            "primary_pathways": ["pathway 1", "pathway 2"],
            "cellular_mechanisms": ["mechanism 1", "mechanism 2"],
            "physiological_processes": ["process 1", "process 2"],
            "metabolic_interactions": ["interaction 1", "interaction 2"]
        }}
        """
        
        try:
            logger.info(f"⚙️ Generating mechanism research with multi-provider failover")
            mechanism_research = await self._call_ultra_cheap_ai_with_failover(prompt, intelligence)
            
            if isinstance(mechanism_research, str):
                mechanism_research = json.loads(mechanism_research)
            
            result = mechanism_research if isinstance(mechanism_research, dict) else {}
            logger.info(f"✅ Generated mechanism research with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Mechanism research generation failed: {str(e)}")
            return self._fallback_mechanism_research(product_category)
    
    async def _generate_clinical_evidence(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate clinical evidence information using ultra-cheap AI with failover"""
        
        prompt = f"""
        As a clinical researcher, provide information about the types of clinical evidence typically relevant for products like "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
        Include:
        1. Types of clinical studies relevant to this product category
        2. Outcome measures commonly used
        3. Study design considerations
        4. Research limitations and considerations
        
        Focus on general clinical research approaches rather than specific studies.
        
        Format as JSON:
        {{
            "relevant_study_types": ["study type 1", "study type 2"],
            "outcome_measures": ["measure 1", "measure 2"],
            "design_considerations": ["consideration 1", "consideration 2"],
            "research_limitations": ["limitation 1", "limitation 2"]
        }}
        """
        
        try:
            logger.info(f"🔬 Generating clinical evidence with multi-provider failover")
            clinical_evidence = await self._call_ultra_cheap_ai_with_failover(prompt, intelligence)
            
            if isinstance(clinical_evidence, str):
                clinical_evidence = json.loads(clinical_evidence)
            
            result = clinical_evidence if isinstance(clinical_evidence, dict) else {}
            logger.info(f"✅ Generated clinical evidence with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Clinical evidence generation failed: {str(e)}")
            return self._fallback_clinical_evidence()
    
    async def _generate_safety_profile(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate safety profile information using ultra-cheap AI with failover"""
        
        prompt = f"""
        As a safety researcher, provide general safety considerations for a product like "{product_name}".
        
        IMPORTANT: Always use the actual product name "{product_name}" in your response.
        Never use placeholders like "Your Product", "Product", "[Product]", etc.
        
        Include:
        1. General safety considerations for this product category
        2. Potential interactions to be aware of
        3. Contraindications and precautions
        4. Recommended usage guidelines
        
        Focus on general safety principles and standard precautions.
        
        Format as JSON:
        {{
            "general_safety": ["safety point 1", "safety point 2"],
            "potential_interactions": ["interaction 1", "interaction 2"],
            "contraindications": ["contraindication 1", "contraindication 2"],
            "usage_guidelines": ["guideline 1", "guideline 2"]
        }}
        """
        
        try:
            logger.info(f"🛡️ Generating safety profile with multi-provider failover")
            safety_profile = await self._call_ultra_cheap_ai_with_failover(prompt, intelligence)
            
            if isinstance(safety_profile, str):
                safety_profile = json.loads(safety_profile)
            
            result = safety_profile if isinstance(safety_profile, dict) else {}
            logger.info(f"✅ Generated safety profile with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Safety profile generation failed: {str(e)}")
            return self._fallback_safety_profile()
    
    def _determine_product_category(self, product_name: str, offer_intel: Dict[str, Any]) -> str:
        """Determine product category for targeted research"""
        
        product_name_lower = product_name.lower()
        content = str(offer_intel).lower()
        
        if "liver" in product_name_lower or "hepato" in product_name_lower:
            return "liver health supplement"
        elif "weight" in content or "fat" in content or "burn" in content:
            return "weight management supplement"
        elif "energy" in content or "metabolism" in content:
            return "metabolic support supplement"
        elif "detox" in content or "cleanse" in content:
            return "detoxification supplement"
        else:
            return "dietary supplement"
    
    def _calculate_research_quality_score(
        self, 
        scientific_backing: List[str], 
        ingredient_research: Dict[str, Any], 
        clinical_evidence: Dict[str, Any]
    ) -> float:
        """Calculate research quality score"""
        
        score = 0.3  # Base score
        
        # Scientific backing score
        if scientific_backing and isinstance(scientific_backing, list):
            score += min(len(scientific_backing) * 0.08, 0.25)
        
        # Ingredient research score
        if ingredient_research and isinstance(ingredient_research, dict):
            score += min(len(ingredient_research) * 0.05, 0.20)
        
        # Clinical evidence score
        if clinical_evidence and isinstance(clinical_evidence, dict):
            score += min(len(clinical_evidence) * 0.05, 0.25)
        
        return min(score, 1.0)
    
    # Fallback methods (unchanged but with updated metadata)
    def _generate_fallback_scientific_intelligence(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback scientific intelligence with multi-provider metadata"""
        
        # 🔥 Extract product name from product_data
        product_name = product_data.get("product_name", "Product")
        
        # Generate fallback data
        fallback_data = {
            "scientific_backing": self._fallback_scientific_backing(product_name),
            "ingredient_research": self._fallback_ingredient_research(product_name),
            "mechanism_of_action": self._fallback_mechanism_research("supplement"),
            "clinical_evidence": self._fallback_clinical_evidence(),
            "safety_profile": self._fallback_safety_profile(),
            "research_quality_score": 0.6,
            "generated_at": datetime.now(timezone.utc).astimezone().isoformat(),
            "ai_provider": "fallback",
            "enhancement_confidence": 0.6,
            "product_name_fix_applied": True,
            "actual_product_name": product_name,
            "ultra_cheap_optimization": {
                "provider_used": "fallback_static",
                "total_providers_available": len(self.available_providers),
                "cost_per_1k_tokens": 0.0,
                "quality_score": 60,
                "provider_tier": "fallback",
                "estimated_cost_savings_vs_openai": 100.0,
                "fallback_reason": "All ultra-cheap providers failed"
            }
        }
        
        # 🔥 Apply product name fix to fallback data
        company_name = extract_company_name_from_intelligence(product_data)
        final_fallback = substitute_placeholders_in_data(fallback_data, product_name, company_name)
        
        logger.info(f"🔧 Applied product name fix to fallback data: '{product_name}'")
        return final_fallback
    
    def _fallback_scientific_backing(self, product_name: str) -> List[str]:
        """Fallback scientific backing"""
        
        return [
            "Research indicates that natural compounds may support overall health and wellness",
            "Clinical studies suggest that dietary supplements can complement a healthy lifestyle",
            "Scientific literature supports the role of nutrition in maintaining optimal health",
            "Evidence-based research validates the importance of quality ingredients",
            "Studies demonstrate that proper supplementation may support natural body processes",
            "Research confirms the value of comprehensive approaches to health and wellness",
            "Scientific methodology validates the importance of standardized formulations",
            "Clinical research supports the role of natural compounds in wellness"
        ]
    
    def _fallback_ingredient_research(self, product_name: str) -> Dict[str, Any]:
        """Fallback ingredient research"""
        
        return {
            "primary_compounds": ["natural extracts", "botanical ingredients", "nutritional compounds"],
            "bioavailability_research": [
                "Absorption rates vary based on formulation quality",
                "Bioavailability is enhanced through proper extraction methods"
            ],
            "synergistic_effects": [
                "Ingredient combinations may provide enhanced benefits",
                "Synergistic formulations support comprehensive wellness"
            ],
            "quality_factors": [
                "Source quality affects ingredient potency",
                "Standardized extracts ensure consistent quality"
            ]
        }
    
    def _fallback_mechanism_research(self, product_category: str) -> Dict[str, Any]:
        """Fallback mechanism research"""
        
        return {
            "primary_pathways": ["metabolic pathways", "cellular processes", "physiological systems"],
            "cellular_mechanisms": ["cellular uptake", "metabolic processing", "cellular signaling"],
            "physiological_processes": ["natural detoxification", "metabolic function", "cellular health"],
            "metabolic_interactions": ["nutrient absorption", "metabolic conversion", "elimination processes"]
        }
    
    def _fallback_clinical_evidence(self) -> Dict[str, Any]:
        """Fallback clinical evidence"""
        
        return {
            "relevant_study_types": ["randomized controlled trials", "observational studies", "meta-analyses"],
            "outcome_measures": ["biomarker analysis", "functional assessments", "safety parameters"],
            "design_considerations": ["study duration", "sample size", "control groups"],
            "research_limitations": ["individual variation", "lifestyle factors", "study duration constraints"]
        }
    
    def _fallback_safety_profile(self) -> Dict[str, Any]:
        """Fallback safety profile"""
        
        return {
            "general_safety": [
                "Generally well-tolerated in healthy adults",
                "Follow recommended dosage guidelines"
            ],
            "potential_interactions": [
                "Consult healthcare provider if taking medications",
                "Consider timing with other supplements"
            ],
            "contraindications": [
                "Not recommended during pregnancy or nursing",
                "Consult physician if you have medical conditions"
            ],
            "usage_guidelines": [
                "Take as directed on product label",
                "Use as part of a healthy lifestyle"
            ]
        }