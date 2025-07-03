# src/intelligence/amplifier/enhancements/scientific_enhancer.py
"""
Generates comprehensive scientific backing for health claims using ULTRA-CHEAP AI providers
UPDATED: Integrated with tiered AI provider system for 95-99% cost savings
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)

class ScientificIntelligenceEnhancer:
    """Generate scientific intelligence for health and wellness products using ultra-cheap AI"""
    
    def __init__(self, ai_providers: List[Dict]):
        self.ai_providers = ai_providers
        self.available_provider = self._get_ultra_cheap_provider()
        
        # Log the ultra-cheap optimization status
        if self.available_provider:
            provider_name = self.available_provider.get("name", "unknown")
            cost_per_1k = self.available_provider.get("cost_per_1k_tokens", 0)
            quality_score = self.available_provider.get("quality_score", 0)
            
            logger.info(f"🚀 Scientific Enhancer using ULTRA-CHEAP provider: {provider_name}")
            logger.info(f"💰 Cost: ${cost_per_1k:.5f}/1K tokens (vs $0.030 OpenAI)")
            logger.info(f"🎯 Quality: {quality_score}/100")
            
            # Calculate savings
            openai_cost = 0.030
            if cost_per_1k > 0:
                savings_pct = ((openai_cost - cost_per_1k) / openai_cost) * 100
                logger.info(f"💎 SAVINGS: {savings_pct:.1f}% cost reduction!")
        else:
            logger.warning("⚠️ No ultra-cheap AI providers available for Scientific Enhancement")
        
    def _get_ultra_cheap_provider(self) -> Optional[Dict]:
        """Get the best ultra-cheap AI provider using tiered system priority"""
        
        if not self.ai_providers:
            logger.warning("⚠️ No AI providers available for scientific enhancement")
            return None
        
        # Sort by priority (lowest first = cheapest/fastest)
        sorted_providers = sorted(
            [p for p in self.ai_providers if p.get("available", False)],
            key=lambda x: x.get("priority", 999)
        )
        
        if not sorted_providers:
            logger.warning("⚠️ No available AI providers for scientific enhancement")
            return None
        
        # Use the highest priority (cheapest) provider
        selected_provider = sorted_providers[0]
        
        provider_name = selected_provider.get("name", "unknown")
        cost = selected_provider.get("cost_per_1k_tokens", 0)
        quality = selected_provider.get("quality_score", 0)
        
        logger.info(f"✅ Selected ultra-cheap provider for scientific enhancement:")
        logger.info(f"   Provider: {provider_name}")
        logger.info(f"   Cost: ${cost:.5f}/1K tokens")
        logger.info(f"   Quality: {quality}/100")
        logger.info(f"   Priority: {selected_provider.get('priority', 'unknown')}")
        
        return selected_provider
    
    async def generate_scientific_intelligence(
        self, 
        product_data: Dict[str, Any], 
        base_intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive scientific intelligence using ultra-cheap AI"""
        
        if not self.available_provider:
            logger.warning("🚨 No ultra-cheap providers available, using fallback")
            return self._generate_fallback_scientific_intelligence(product_data)
        
        try:
            # Log cost optimization start
            provider_name = self.available_provider.get("name", "unknown")
            logger.info(f"🧬 Starting scientific intelligence generation with {provider_name}")
            
            # Extract product information
            product_name = product_data.get("product_name", "Product")
            offer_intel = base_intelligence.get("offer_intelligence", {})
            
            # Generate scientific backing using ultra-cheap AI
            scientific_backing = await self._generate_scientific_backing(product_name, offer_intel)
            
            # Generate ingredient research using ultra-cheap AI
            ingredient_research = await self._generate_ingredient_research(product_name, offer_intel)
            
            # Generate mechanism of action using ultra-cheap AI
            mechanism_research = await self._generate_mechanism_research(product_name, offer_intel)
            
            # Generate clinical evidence using ultra-cheap AI
            clinical_evidence = await self._generate_clinical_evidence(product_name, offer_intel)
            
            # Generate safety profile using ultra-cheap AI
            safety_profile = await self._generate_safety_profile(product_name, offer_intel)
            
            # Calculate research quality score
            research_quality = self._calculate_research_quality_score(
                scientific_backing, ingredient_research, clinical_evidence
            )
            
            # Compile comprehensive scientific intelligence with ultra-cheap metadata
            scientific_intelligence = {
                "scientific_backing": scientific_backing,
                "ingredient_research": ingredient_research,
                "mechanism_of_action": mechanism_research,
                "clinical_evidence": clinical_evidence,
                "safety_profile": safety_profile,
                "research_quality_score": research_quality,
                "generated_at": datetime.utcnow().isoformat(),
                "ai_provider": provider_name,
                "enhancement_confidence": 0.85,
                "ultra_cheap_optimization": {
                    "provider_used": provider_name,
                    "cost_per_1k_tokens": self.available_provider.get("cost_per_1k_tokens", 0),
                    "quality_score": self.available_provider.get("quality_score", 0),
                    "provider_tier": self.available_provider.get("provider_tier", "unknown"),
                    "estimated_cost_savings_vs_openai": self._calculate_cost_savings(),
                    "speed_rating": self.available_provider.get("speed_rating", 0)
                }
            }
            
            # Log successful generation with cost data
            total_items = (
                len(scientific_backing) + 
                len(ingredient_research) + 
                len(clinical_evidence) +
                len(safety_profile)
            )
            
            logger.info(f"✅ Scientific intelligence generated using {provider_name}")
            logger.info(f"📊 Generated {total_items} intelligence items")
            logger.info(f"💰 Cost optimization: {self._calculate_cost_savings():.1f}% savings")
            
            return scientific_intelligence
            
        except Exception as e:
            logger.error(f"❌ Ultra-cheap scientific intelligence generation failed: {str(e)}")
            logger.info("🔄 Falling back to static scientific intelligence")
            return self._generate_fallback_scientific_intelligence(product_data)
    
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
    
    async def _generate_scientific_backing(
        self, 
        product_name: str, 
        offer_intel: Dict[str, Any]
    ) -> List[str]:
        """Generate scientific backing statements using ultra-cheap AI"""
        
        # Extract health claims from offer intelligence
        value_props = offer_intel.get("value_propositions", [])
        benefits = offer_intel.get("insights", [])
        
        prompt = f"""
        As a scientific researcher, provide evidence-based backing for a health product called "{product_name}".
        
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
            logger.info(f"🧬 Generating scientific backing with {self.available_provider.get('name')}")
            scientific_backing = await self._call_ultra_cheap_ai(prompt)
            
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
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate ingredient research information using ultra-cheap AI"""
        
        prompt = f"""
        As a nutritional scientist, provide research-based information about potential ingredients for a product called "{product_name}".
        
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
            logger.info(f"🧪 Generating ingredient research with {self.available_provider.get('name')}")
            ingredient_research = await self._call_ultra_cheap_ai(prompt)
            
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
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate mechanism of action research using ultra-cheap AI"""
        
        # Determine product category for targeted research
        product_category = self._determine_product_category(product_name, offer_intel)
        
        prompt = f"""
        As a biochemist, explain the potential mechanisms of action for a {product_category} product called "{product_name}".
        
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
            logger.info(f"⚙️ Generating mechanism research with {self.available_provider.get('name')}")
            mechanism_research = await self._call_ultra_cheap_ai(prompt)
            
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
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate clinical evidence information using ultra-cheap AI"""
        
        prompt = f"""
        As a clinical researcher, provide information about the types of clinical evidence typically relevant for products like "{product_name}".
        
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
            logger.info(f"🔬 Generating clinical evidence with {self.available_provider.get('name')}")
            clinical_evidence = await self._call_ultra_cheap_ai(prompt)
            
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
        offer_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate safety profile information using ultra-cheap AI"""
        
        prompt = f"""
        As a safety researcher, provide general safety considerations for a product like "{product_name}".
        
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
            logger.info(f"🛡️ Generating safety profile with {self.available_provider.get('name')}")
            safety_profile = await self._call_ultra_cheap_ai(prompt)
            
            if isinstance(safety_profile, str):
                safety_profile = json.loads(safety_profile)
            
            result = safety_profile if isinstance(safety_profile, dict) else {}
            logger.info(f"✅ Generated safety profile with {len(result)} categories")
            return result
            
        except Exception as e:
            logger.error(f"❌ Safety profile generation failed: {str(e)}")
            return self._fallback_safety_profile()
    
    async def _call_ultra_cheap_ai(self, prompt: str) -> Any:
        """Call the ultra-cheap AI provider with optimized settings"""
        
        provider_name = self.available_provider["name"]
        client = self.available_provider["client"]
        
        # Log the call for cost tracking
        estimated_tokens = len(prompt.split()) * 1.3  # Rough estimate
        cost_per_1k = self.available_provider.get("cost_per_1k_tokens", 0)
        estimated_cost = (estimated_tokens / 1000) * cost_per_1k
        
        logger.info(f"💰 AI Call: {provider_name} | ~{estimated_tokens:.0f} tokens | ~${estimated_cost:.6f}")
        
        try:
            if provider_name == "groq":
                response = await client.chat.completions.create(
                    model="llama-3.3-70b-versatile",  # Best Groq model for scientific content
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a scientific researcher providing evidence-based information. Always respond with valid JSON when requested. Be concise but comprehensive."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                return response.choices[0].message.content
                
            elif provider_name == "together":
                response = await client.chat.completions.create(
                    model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",  # Best Together AI model
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a scientific researcher providing evidence-based information. Always respond with valid JSON when requested. Be concise but comprehensive."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                return response.choices[0].message.content
                
            elif provider_name == "deepseek":
                response = await client.chat.completions.create(
                    model="deepseek-chat",  # Deepseek's main model
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a scientific researcher providing evidence-based information. Always respond with valid JSON when requested. Be concise but comprehensive."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                return response.choices[0].message.content
                
            elif provider_name == "anthropic":
                response = await client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    temperature=0.3,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                return response.content[0].text
            
            elif provider_name == "cohere":
                response = await client.chat(
                    model="command-r-plus",
                    message=prompt,
                    temperature=0.3,
                    max_tokens=2000
                )
                return response.text
                
            elif provider_name == "openai":
                response = await client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a scientific researcher providing evidence-based information. Always respond with valid JSON when requested."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            
            else:
                raise Exception(f"Unsupported ultra-cheap provider: {provider_name}")
                
        except Exception as e:
            logger.error(f"❌ Ultra-cheap AI call failed for {provider_name}: {str(e)}")
            raise
    
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
        if scientific_backing:
            score += min(len(scientific_backing) * 0.08, 0.25)
        
        # Ingredient research score
        if ingredient_research:
            score += min(len(ingredient_research) * 0.05, 0.20)
        
        # Clinical evidence score
        if clinical_evidence:
            score += min(len(clinical_evidence) * 0.05, 0.25)
        
        return min(score, 1.0)
    
    # Fallback methods (unchanged but with ultra-cheap metadata)
    def _generate_fallback_scientific_intelligence(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback scientific intelligence with ultra-cheap metadata"""
        
        product_name = product_data.get("product_name", "Product")
        
        return {
            "scientific_backing": self._fallback_scientific_backing(product_name),
            "ingredient_research": self._fallback_ingredient_research(product_name),
            "mechanism_of_action": self._fallback_mechanism_research("supplement"),
            "clinical_evidence": self._fallback_clinical_evidence(),
            "safety_profile": self._fallback_safety_profile(),
            "research_quality_score": 0.6,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "fallback",
            "enhancement_confidence": 0.6,
            "ultra_cheap_optimization": {
                "provider_used": "fallback_static",
                "cost_per_1k_tokens": 0.0,
                "quality_score": 60,
                "provider_tier": "fallback",
                "estimated_cost_savings_vs_openai": 100.0,
                "fallback_reason": "No ultra-cheap providers available"
            }
        }
    
    def _fallback_scientific_backing(self, product_name: str) -> List[str]:
        """Fallback scientific backing"""
        
        return [
            "Research indicates that natural compounds may support overall health and wellness",
            "Clinical studies suggest that dietary supplements can complement a healthy lifestyle",
            "Scientific literature supports the role of nutrition in maintaining optimal health",
            "Evidence-based research validates the importance of quality ingredients",
            "Studies demonstrate that proper supplementation may support natural body processes",
            "Research confirms the value of comprehensive approaches to health and wellness"
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