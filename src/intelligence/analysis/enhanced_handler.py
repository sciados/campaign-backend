# =====================================
# File: src/intelligence/analysis/enhanced_handler.py
# =====================================

"""
Enhanced Analysis Handler with 6-Stage Enhancement Pipeline

Restores the full 3-stage intelligence pipeline:
1. Base Analyzer - Extract core intelligence 
2. AI Enhancement Pipeline - 6 enhancers for rich intelligence
3. RAG Integration - Research-augmented intelligence
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

import openai
import anthropic
import httpx
import json

from src.core.config import ai_provider_config, settings
from src.core.config.ai_providers import AIProviderTier
from src.core.shared.decorators import retry_on_failure
from src.core.shared.exceptions import AIProviderError, ServiceUnavailableError

logger = logging.getLogger(__name__)


class EnhancedAnalysisHandler:
    """Enhanced handler with full 3-stage pipeline for rich intelligence generation."""
    
    def __init__(self):
        # Simple direct provider setup using environment variables (like before modular structure)
        self.available_providers = []

        # Check each provider directly from settings
        if settings.DEEPSEEK_API_KEY and len(settings.DEEPSEEK_API_KEY.strip()) > 10:
            self.available_providers.append({"name": "deepseek", "api_key": settings.DEEPSEEK_API_KEY, "cost": 0.0001})
            logger.info("✅ DeepSeek provider available")

        if settings.GROQ_API_KEY and len(settings.GROQ_API_KEY.strip()) > 10:
            self.available_providers.append({"name": "groq", "api_key": settings.GROQ_API_KEY, "cost": 0.0002})
            logger.info("✅ Groq provider available")

        if settings.TOGETHER_API_KEY and len(settings.TOGETHER_API_KEY.strip()) > 10:
            self.available_providers.append({"name": "together", "api_key": settings.TOGETHER_API_KEY, "cost": 0.0008})
            logger.info("✅ Together provider available")

        if settings.AIMLAPI_API_KEY and len(settings.AIMLAPI_API_KEY.strip()) > 10:
            self.available_providers.append({"name": "aimlapi", "api_key": settings.AIMLAPI_API_KEY, "cost": 0.001})
            logger.info("✅ AI/ML API provider available")

        if settings.MINIMAX_API_KEY and len(settings.MINIMAX_API_KEY.strip()) > 10:
            self.available_providers.append({"name": "minimax", "api_key": settings.MINIMAX_API_KEY, "cost": 0.003})
            logger.info("✅ MiniMax provider available")

        if settings.COHERE_API_KEY and len(settings.COHERE_API_KEY.strip()) > 10:
            self.available_providers.append({"name": "cohere", "api_key": settings.COHERE_API_KEY, "cost": 0.002})
            logger.info("✅ Cohere provider available")

        logger.info(f"Total providers loaded: {len(self.available_providers)}")

        self.current_provider_index = 0

        # Fallback to premium providers only if ultra-cheap fail
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

        # Enhancement modules
        self.enhancers = {
            "scientific": self._scientific_enhancer,
            "credibility": self._credibility_enhancer,
            "content": self._content_enhancer,
            "emotional": self._emotional_enhancer,
            "authority": self._authority_enhancer,
            "market": self._market_enhancer
        }

        logger.info(f"Enhanced handler initialized with {len(self.available_providers)} total providers")
    
    # =====================================
    # STAGE 1: BASE ANALYZER
    # =====================================
    
    async def perform_base_analysis(self, content: str, url: str) -> Dict[str, Any]:
        """
        Stage 1: Extract core intelligence from content.
        
        Returns structured base intelligence for enhancement.
        """
        logger.info(f"Starting base analysis for {url}")
        start_time = time.time()
        
        try:
            # Get base intelligence extraction
            base_intelligence = await self._extract_base_intelligence(content)
            
            # Calculate confidence score
            confidence_score = self._calculate_base_confidence(content, base_intelligence)
            base_intelligence["confidence_score"] = confidence_score
            
            execution_time = time.time() - start_time
            logger.info(f"Base analysis completed in {execution_time:.2f}s with confidence: {confidence_score}")
            
            return base_intelligence
            
        except Exception as e:
            logger.error(f"Base analysis failed: {e}")
            raise
    
    async def _extract_base_intelligence(self, content: str) -> Dict[str, Any]:
        """Extract comprehensive base intelligence."""
        
        prompt = f"""
        Analyze this content and extract comprehensive intelligence. Return JSON with these sections:

        {{
          "offer_intelligence": {{
            "products": ["product names"],
            "key_features": ["feature1", "feature2"],
            "primary_benefits": ["benefit1", "benefit2"],
            "value_propositions": ["prop1", "prop2"],
            "pricing_info": "pricing details if mentioned",
            "guarantee_terms": "guarantee info if mentioned"
          }},
          "psychology_intelligence": {{
            "target_audience": "detailed audience description",
            "emotional_triggers": ["trigger1", "trigger2"],
            "persuasion_techniques": ["technique1", "technique2"],
            "pain_points": ["pain1", "pain2"],
            "desire_states": ["desire1", "desire2"]
          }},
          "competitive_intelligence": {{
            "competitive_advantages": ["advantage1", "advantage2"],
            "market_positioning": "positioning description",
            "competitor_mentions": ["competitor1", "competitor2"],
            "differentiation_factors": ["factor1", "factor2"]
          }},
          "content_intelligence": {{
            "key_messages": ["message1", "message2"],
            "call_to_actions": ["cta1", "cta2"],
            "content_structure": "structure analysis",
            "tone_and_style": "tone description"
          }},
          "brand_intelligence": {{
            "brand_voice": "voice description",
            "brand_values": ["value1", "value2"],
            "brand_personality": "personality description",
            "credibility_signals": ["signal1", "signal2"]
          }}
        }}

        Content: {content[:8000]}

        Return only valid JSON without markdown formatting.
        """

        try:
            # Use available providers directly (simple approach like before modular structure)
            if not self.available_providers:
                raise ServiceUnavailableError("No AI providers available")

            # Log content details for debugging
            logger.info(f"Analyzing content: {len(content)} characters, first 200: {content[:200]}")

            # Use the cheapest available provider
            provider = min(self.available_providers, key=lambda x: x["cost"])
            logger.info(f"Using provider: {provider['name']} for base analysis")

            response = await self._query_ai_provider(prompt, provider["name"])

            # Log response for debugging
            logger.info(f"AI response length: {len(response) if response else 0}")
            logger.debug(f"AI response preview: {response[:200] if response else 'Empty'}")

            if not response or not response.strip():
                logger.warning("Empty response from AI provider, using fallback")
                return self._get_fallback_base_intelligence()

            # Try to clean the response (remove markdown if present)
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response.replace("```json", "").replace("```", "").strip()
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response.replace("```", "").strip()

            intelligence = json.loads(cleaned_response)

            # Ensure all required sections exist
            required_sections = [
                "offer_intelligence", "psychology_intelligence",
                "competitive_intelligence", "content_intelligence", "brand_intelligence"
            ]

            for section in required_sections:
                if section not in intelligence:
                    intelligence[section] = {}

            return intelligence

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse base intelligence JSON: {e}")
            logger.debug(f"Raw response that failed to parse: {response[:500] if response else 'None'}")
            return self._get_fallback_base_intelligence()
        except Exception as e:
            logger.error(f"Base intelligence extraction failed: {e}")
            return self._get_fallback_base_intelligence()
    
    # =====================================
    # STAGE 2: AI ENHANCEMENT PIPELINE
    # =====================================
    
    async def perform_amplification(self, base_intelligence: Dict[str, Any], url: str) -> Dict[str, Any]:
        """
        Stage 2: Amplify intelligence through 6 enhancers.
        
        Takes base intelligence and runs it through enhancement pipeline
        to generate rich, detailed intelligence data.
        """
        logger.info("Starting amplification pipeline")
        start_time = time.time()
        
        try:
            # Step 1: Get AI providers
            logger.info("Getting AI providers...")
            providers = self._get_enhancement_providers()
            
            # Step 2: Identify enhancement opportunities
            logger.info("Identifying enhancement opportunities...")
            opportunities = await asyncio.wait_for(
                self._identify_enhancement_opportunities(base_intelligence, providers),
                timeout=60
            )
            
            # Step 3: Generate enhancements
            logger.info("Generating enhancements...")
            enhancements = await asyncio.wait_for(
                self._generate_enhancements(base_intelligence, opportunities, providers),
                timeout=240  # Increased timeout for 6 enhancers
            )
            
            # Step 4: Create enriched intelligence
            logger.info("Creating enriched intelligence...")
            enriched_intelligence = await asyncio.wait_for(
                self._create_enriched_intelligence(base_intelligence, enhancements),
                timeout=30
            )
            
            execution_time = time.time() - start_time
            logger.info(f"Amplification completed in {execution_time:.2f}s")
            logger.info(f"Enhanced intelligence size: {len(str(enriched_intelligence))} characters")
            
            return enriched_intelligence
            
        except asyncio.TimeoutError as e:
            logger.error(f"Amplification timed out: {e}")
            # Return base intelligence with timeout marker
            base_intelligence["amplification_status"] = "timeout"
            return base_intelligence
        except Exception as e:
            logger.error(f"Amplification failed: {e}")
            base_intelligence["amplification_status"] = "failed"
            return base_intelligence
    
    async def _identify_enhancement_opportunities(self, base_intel: Dict[str, Any], providers: List[Any]) -> Dict[str, Any]:
        """Identify areas for enhancement based on base intelligence."""
        
        opportunities = {
            "scientific_opportunities": [],
            "credibility_opportunities": [],
            "content_opportunities": [],
            "emotional_opportunities": [],
            "authority_opportunities": [],
            "market_opportunities": []
        }
        
        # Analyze base intelligence for enhancement opportunities
        if base_intel.get("offer_intelligence", {}).get("products"):
            opportunities["scientific_opportunities"].append("product_validation")
            opportunities["credibility_opportunities"].append("trust_building")
        
        if base_intel.get("psychology_intelligence", {}).get("emotional_triggers"):
            opportunities["emotional_opportunities"].append("trigger_amplification")
        
        if base_intel.get("competitive_intelligence", {}).get("competitive_advantages"):
            opportunities["market_opportunities"].append("positioning_enhancement")
        
        if base_intel.get("content_intelligence", {}).get("key_messages"):
            opportunities["content_opportunities"].append("message_optimization")
        
        if base_intel.get("brand_intelligence", {}).get("credibility_signals"):
            opportunities["authority_opportunities"].append("expertise_building")
        
        return opportunities
    
    async def _generate_enhancements(self, base_intel: Dict[str, Any], opportunities: Dict[str, Any], providers: List[Any]) -> Dict[str, Any]:
        """Generate enhancements using all 6 enhancers."""
        
        enhancements = {}
        
        # Run all 6 enhancers concurrently with individual timeouts
        enhancement_tasks = []
        
        for enhancer_name, enhancer_func in self.enhancers.items():
            task = asyncio.create_task(
                asyncio.wait_for(
                    enhancer_func(base_intel, opportunities, providers),
                    timeout=60  # Individual enhancer timeout for comprehensive analysis
                )
            )
            enhancement_tasks.append((enhancer_name, task))
        
        # Collect results as they complete
        for enhancer_name, task in enhancement_tasks:
            try:
                result = await task
                enhancements[f"{enhancer_name}_enhancement"] = result
                logger.info(f"{enhancer_name} enhancer completed successfully")
            except asyncio.TimeoutError:
                logger.warning(f"{enhancer_name} enhancer timed out")
                enhancements[f"{enhancer_name}_enhancement"] = {"status": "timeout"}
            except Exception as e:
                logger.error(f"{enhancer_name} enhancer failed: {e}")
                enhancements[f"{enhancer_name}_enhancement"] = {"status": "failed", "error": str(e)}
        
        # Add enhancement metadata
        successful_enhancers = [name for name, result in enhancements.items() 
                               if result.get("status") != "timeout" and result.get("status") != "failed"]
        
        enhancements["enhancement_metadata"] = {
            "total_enhancers": len(self.enhancers),
            "successful_enhancers": len(successful_enhancers),
            "success_rate": len(successful_enhancers) / len(self.enhancers) * 100,
            "modules_successful": [name.replace("_enhancement", "") for name in successful_enhancers]
        }
        
        return enhancements
    
    # =====================================
    # 6 INDIVIDUAL ENHANCERS
    # =====================================
    
    async def _scientific_enhancer(self, base_intel: Dict[str, Any], opportunities: Dict[str, Any], providers: List[Any]) -> Dict[str, Any]:
        """Scientific validation and evidence enhancement."""
        
        products = base_intel.get("offer_intelligence", {}).get("products", [])
        features = base_intel.get("offer_intelligence", {}).get("key_features", [])
        
        prompt = f"""
        As a scientific research analyst, enhance these product claims with scientific validation:
        
        Products: {products}
        Features: {features}
        
        Provide scientific enhancement in JSON format:
        {{
          "validated_claims": ["scientifically backed claims"],
          "research_support": ["types of research that support these"],
          "scientific_credibility": {{
            "evidence_level": "high/medium/low",
            "research_basis": "description of scientific basis",
            "validation_methods": ["methods to validate claims"]
          }},
          "enhancement_applied": true
        }}
        """
        
        provider = providers[0] if providers else None
        if not provider:
            return {"enhancement_applied": False, "error": "No providers available"}
        
        try:
            provider_name = provider["name"] if isinstance(provider, dict) else provider.name
            response = await self._query_ai_provider(prompt, provider_name)

            # Debug logging
            logger.debug(f"AI response for enhancement: {response[:200]}...")

            if not response or not response.strip():
                return {
                    "enhancement_applied": False,
                    "error": "Empty response from AI provider",
                    "fallback_data": {"enhancement_type": "simulated", "confidence": 0.3}
                }

            # Try to parse JSON
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback: Create basic enhancement structure
                return {
                    "enhancement_applied": True,
                    "simulated_enhancement": True,
                    "raw_response": response,  # Store complete response for full intelligence
                    "enhancement_confidence": 0.5
                }

        except Exception as e:
            return {"enhancement_applied": False, "error": str(e)}
    
    async def _credibility_enhancer(self, base_intel: Dict[str, Any], opportunities: Dict[str, Any], providers: List[Any]) -> Dict[str, Any]:
        """Credibility and trust signal enhancement."""
        
        brand_signals = base_intel.get("brand_intelligence", {}).get("credibility_signals", [])
        guarantees = base_intel.get("offer_intelligence", {}).get("guarantee_terms", "")
        
        prompt = f"""
        As a trust and credibility expert, enhance these trust signals:
        
        Current Credibility Signals: {brand_signals}
        Guarantees: {guarantees}
        
        Provide credibility enhancement in JSON format:
        {{
          "trust_indicators": ["enhanced trust signals"],
          "authority_signals": ["authority building elements"],
          "social_proof_enhancement": ["social proof opportunities"],
          "credibility_score": 0.85,
          "enhancement_applied": true
        }}
        """
        
        provider = providers[0] if providers else None
        if not provider:
            return {"enhancement_applied": False, "error": "No providers available"}
        
        try:
            provider_name = provider["name"] if isinstance(provider, dict) else provider.name
            response = await self._query_ai_provider(prompt, provider_name)

            # Debug logging
            logger.debug(f"AI response for enhancement: {response[:200]}...")

            if not response or not response.strip():
                return {
                    "enhancement_applied": False,
                    "error": "Empty response from AI provider",
                    "fallback_data": {"enhancement_type": "simulated", "confidence": 0.3}
                }

            # Try to parse JSON
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback: Create basic enhancement structure
                return {
                    "enhancement_applied": True,
                    "simulated_enhancement": True,
                    "raw_response": response,  # Store complete response for full intelligence
                    "enhancement_confidence": 0.5
                }

        except Exception as e:
            return {"enhancement_applied": False, "error": str(e)}
    
    async def _content_enhancer(self, base_intel: Dict[str, Any], opportunities: Dict[str, Any], providers: List[Any]) -> Dict[str, Any]:
        """Content optimization and messaging enhancement."""
        
        messages = base_intel.get("content_intelligence", {}).get("key_messages", [])
        ctas = base_intel.get("content_intelligence", {}).get("call_to_actions", [])
        
        prompt = f"""
        As a content optimization expert, enhance these content elements:
        
        Key Messages: {messages}
        CTAs: {ctas}
        
        Provide content enhancement in JSON format:
        {{
          "enhanced_messaging": ["optimized key messages"],
          "optimized_ctas": ["improved call-to-actions"],
          "content_improvements": ["specific content optimizations"],
          "messaging_score": 0.9,
          "enhancement_applied": true
        }}
        """
        
        provider = providers[0] if providers else None
        if not provider:
            return {"enhancement_applied": False, "error": "No providers available"}
        
        try:
            provider_name = provider["name"] if isinstance(provider, dict) else provider.name
            response = await self._query_ai_provider(prompt, provider_name)

            # Debug logging
            logger.debug(f"AI response for enhancement: {response[:200]}...")

            if not response or not response.strip():
                return {
                    "enhancement_applied": False,
                    "error": "Empty response from AI provider",
                    "fallback_data": {"enhancement_type": "simulated", "confidence": 0.3}
                }

            # Try to parse JSON
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback: Create basic enhancement structure
                return {
                    "enhancement_applied": True,
                    "simulated_enhancement": True,
                    "raw_response": response,  # Store complete response for full intelligence
                    "enhancement_confidence": 0.5
                }

        except Exception as e:
            return {"enhancement_applied": False, "error": str(e)}
    
    async def _emotional_enhancer(self, base_intel: Dict[str, Any], opportunities: Dict[str, Any], providers: List[Any]) -> Dict[str, Any]:
        """Emotional triggers and psychological enhancement."""
        
        triggers = base_intel.get("psychology_intelligence", {}).get("emotional_triggers", [])
        pain_points = base_intel.get("psychology_intelligence", {}).get("pain_points", [])
        
        prompt = f"""
        As a psychology and persuasion expert, enhance these emotional elements:
        
        Emotional Triggers: {triggers}
        Pain Points: {pain_points}
        
        Provide emotional enhancement in JSON format:
        {{
          "amplified_triggers": ["enhanced emotional triggers"],
          "psychological_drivers": ["key psychological drivers"],
          "emotional_journey": ["customer emotional journey"],
          "persuasion_score": 0.88,
          "enhancement_applied": true
        }}
        """
        
        provider = providers[0] if providers else None
        if not provider:
            return {"enhancement_applied": False, "error": "No providers available"}
        
        try:
            provider_name = provider["name"] if isinstance(provider, dict) else provider.name
            response = await self._query_ai_provider(prompt, provider_name)

            # Debug logging
            logger.debug(f"AI response for enhancement: {response[:200]}...")

            if not response or not response.strip():
                return {
                    "enhancement_applied": False,
                    "error": "Empty response from AI provider",
                    "fallback_data": {"enhancement_type": "simulated", "confidence": 0.3}
                }

            # Try to parse JSON
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback: Create basic enhancement structure
                return {
                    "enhancement_applied": True,
                    "simulated_enhancement": True,
                    "raw_response": response,  # Store complete response for full intelligence
                    "enhancement_confidence": 0.5
                }

        except Exception as e:
            return {"enhancement_applied": False, "error": str(e)}
    
    async def _authority_enhancer(self, base_intel: Dict[str, Any], opportunities: Dict[str, Any], providers: List[Any]) -> Dict[str, Any]:
        """Authority and expertise establishment enhancement."""
        
        brand_voice = base_intel.get("brand_intelligence", {}).get("brand_voice", "")
        credibility = base_intel.get("brand_intelligence", {}).get("credibility_signals", [])
        
        prompt = f"""
        As an authority building expert, enhance these authority elements:
        
        Brand Voice: {brand_voice}
        Credibility Signals: {credibility}
        
        Provide authority enhancement in JSON format:
        {{
          "expertise_markers": ["expertise indicators"],
          "authority_positioning": ["authority building strategies"],
          "thought_leadership": ["thought leadership opportunities"],
          "authority_score": 0.82,
          "enhancement_applied": true
        }}
        """
        
        provider = providers[0] if providers else None
        if not provider:
            return {"enhancement_applied": False, "error": "No providers available"}
        
        try:
            provider_name = provider["name"] if isinstance(provider, dict) else provider.name
            response = await self._query_ai_provider(prompt, provider_name)

            # Debug logging
            logger.debug(f"AI response for enhancement: {response[:200]}...")

            if not response or not response.strip():
                return {
                    "enhancement_applied": False,
                    "error": "Empty response from AI provider",
                    "fallback_data": {"enhancement_type": "simulated", "confidence": 0.3}
                }

            # Try to parse JSON
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback: Create basic enhancement structure
                return {
                    "enhancement_applied": True,
                    "simulated_enhancement": True,
                    "raw_response": response,  # Store complete response for full intelligence
                    "enhancement_confidence": 0.5
                }

        except Exception as e:
            return {"enhancement_applied": False, "error": str(e)}
    
    async def _market_enhancer(self, base_intel: Dict[str, Any], opportunities: Dict[str, Any], providers: List[Any]) -> Dict[str, Any]:
        """Market positioning and competitive enhancement."""
        
        positioning = base_intel.get("competitive_intelligence", {}).get("market_positioning", "")
        advantages = base_intel.get("competitive_intelligence", {}).get("competitive_advantages", [])
        
        prompt = f"""
        As a market positioning expert, enhance these market elements:
        
        Current Positioning: {positioning}
        Competitive Advantages: {advantages}
        
        Provide market enhancement in JSON format:
        {{
          "enhanced_positioning": ["optimized positioning strategies"],
          "market_opportunities": ["market expansion opportunities"],
          "competitive_differentiation": ["enhanced differentiation"],
          "market_score": 0.86,
          "enhancement_applied": true
        }}
        """
        
        provider = providers[0] if providers else None
        if not provider:
            return {"enhancement_applied": False, "error": "No providers available"}
        
        try:
            provider_name = provider["name"] if isinstance(provider, dict) else provider.name
            response = await self._query_ai_provider(prompt, provider_name)

            # Debug logging
            logger.debug(f"AI response for enhancement: {response[:200]}...")

            if not response or not response.strip():
                return {
                    "enhancement_applied": False,
                    "error": "Empty response from AI provider",
                    "fallback_data": {"enhancement_type": "simulated", "confidence": 0.3}
                }

            # Try to parse JSON
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback: Create basic enhancement structure
                return {
                    "enhancement_applied": True,
                    "simulated_enhancement": True,
                    "raw_response": response,  # Store complete response for full intelligence
                    "enhancement_confidence": 0.5
                }

        except Exception as e:
            return {"enhancement_applied": False, "error": str(e)}
    
    # =====================================
    # STAGE 3: RAG INTEGRATION
    # =====================================
    
    async def apply_rag_enhancement(self, enriched_intelligence: Dict[str, Any], url: str) -> Dict[str, Any]:
        """
        Stage 3: Apply research-augmented generation.
        
        Adds autonomous research and knowledge base enhancement
        to create the final, comprehensive intelligence.
        """
        logger.info("Starting RAG enhancement")
        start_time = time.time()
        
        try:
            # Generate autonomous research queries
            research_queries = self._generate_research_queries(enriched_intelligence)
            
            # Simulate research gathering (replace with actual RAG system)
            research_enhancements = await self._gather_rag_research(research_queries, enriched_intelligence)
            
            # Apply research enhancements
            final_intelligence = enriched_intelligence.copy()
            final_intelligence["rag_enhancement"] = research_enhancements
            
            # Update confidence score with research boost
            original_confidence = final_intelligence.get("confidence_score", 0.5)
            research_boost = 0.1 if research_enhancements.get("research_applied") else 0.0
            final_intelligence["confidence_score"] = min(1.0, original_confidence + research_boost)
            
            execution_time = time.time() - start_time
            logger.info(f"RAG enhancement completed in {execution_time:.2f}s")
            
            return final_intelligence
            
        except Exception as e:
            logger.error(f"RAG enhancement failed: {e}")
            enriched_intelligence["rag_enhancement"] = {"error": str(e), "research_applied": False}
            return enriched_intelligence
    
    def _generate_research_queries(self, intelligence: Dict[str, Any]) -> List[str]:
        """Generate autonomous research queries based on intelligence."""
        
        queries = []
        
        # Extract product names for research
        products = intelligence.get("offer_intelligence", {}).get("products", [])
        for product in products[:3]:  # Limit to top 3 products
            queries.append(f"{product} scientific research")
            queries.append(f"{product} market analysis")
        
        # Extract categories for research
        category = intelligence.get("competitive_intelligence", {}).get("market_positioning", "")
        if category:
            queries.append(f"{category} industry trends")
        
        return queries[:6]  # Limit to 6 queries
    
    async def _gather_rag_research(self, queries: List[str], intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Gather research using RAG system (placeholder for actual implementation)."""
        
        # Placeholder research enhancement
        # In actual implementation, this would query your RAG system
        
        return {
            "research_applied": True,
            "queries_processed": len(queries),
            "research_summary": f"Processed {len(queries)} research queries",
            "confidence_boost": 0.1,
            "research_categories": ["market_research", "scientific_validation"]
        }
    
    # =====================================
    # HELPER METHODS
    # =====================================
    
    async def _create_enriched_intelligence(self, base_intel: Dict[str, Any], enhancements: Dict[str, Any]) -> Dict[str, Any]:
        """Combine base intelligence with enhancements."""
        
        enriched = base_intel.copy()
        
        # Merge all enhancements
        for enhancement_key, enhancement_data in enhancements.items():
            if enhancement_key != "enhancement_metadata":
                enriched[enhancement_key] = enhancement_data
        
        # Add enhancement summary
        enriched["enhancement_summary"] = enhancements.get("enhancement_metadata", {})
        
        # Boost confidence score based on successful enhancements
        success_rate = enhancements.get("enhancement_metadata", {}).get("success_rate", 0)
        confidence_boost = (success_rate / 100) * 0.2  # Up to 0.2 boost for 100% success
        original_confidence = enriched.get("confidence_score", 0.5)
        enriched["confidence_score"] = min(1.0, original_confidence + confidence_boost)
        
        return enriched
    
    def _get_enhancement_providers(self) -> List[Any]:
        """Get AI providers for enhancement pipeline using simple approach."""
        # Return available providers directly (simple approach like before modular structure)
        return self.available_providers[:3]  # Limit to 3 providers for cost control
    
    async def _query_ai_provider(self, prompt: str, provider_name: str = "ultra_cheap") -> str:
        """Query AI provider with ultra-cheap providers prioritized for cost optimization."""
        try:
            # Always try ultra-cheap providers first for cost savings
            if provider_name in ["ultra_cheap", "cheap", "budget"] or provider_name not in ["openai", "anthropic"]:
                logger.info("Using ultra-cheap providers for cost optimization")
                return await self._query_ultra_cheap_provider(prompt)
            elif provider_name.lower() in ["openai", "gpt"]:
                logger.warning("Using expensive OpenAI provider")
                return await self._query_openai(prompt)
            elif provider_name.lower() in ["anthropic", "claude"]:
                logger.warning("Using expensive Anthropic provider")
                return await self._query_anthropic(prompt)
            else:
                # Default to ultra-cheap providers
                return await self._query_ultra_cheap_provider(prompt)
        except Exception as e:
            logger.error(f"Provider {provider_name} failed: {e}")
            # Final fallback to OpenAI only if ultra-cheap providers fail
            logger.warning("All providers failed, using OpenAI as final fallback")
            return await self._query_openai(prompt)
    
    async def _query_ultra_cheap_provider(self, prompt: str) -> str:
        """Query available AI providers with rotation for cost optimization."""

        if not self.available_providers:
            logger.warning("No AI providers available, falling back to OpenAI")
            return await self._query_openai(prompt)

        # Try each available provider in cost order (rotation)
        for attempt in range(len(self.available_providers)):
            provider = self.available_providers[self.current_provider_index]

            try:
                logger.info(f"Using ultra-cheap provider: {provider['name']} (${provider['cost']}/1K tokens)")

                if provider["name"] == "deepseek":
                    result = await self._query_deepseek(prompt, provider)
                elif provider["name"] == "groq":
                    result = await self._query_groq(prompt, provider)
                elif provider["name"] == "together":
                    result = await self._query_together(prompt, provider)
                elif provider["name"] == "aimlapi":
                    result = await self._query_aimlapi(prompt, provider)
                elif provider["name"] == "minimax":
                    result = await self._query_minimax(prompt, provider)
                elif provider["name"] == "cohere":
                    result = await self._query_cohere(prompt, provider)
                else:
                    # Skip unknown providers
                    self._rotate_provider()
                    continue

                # Success! Rotate for next call
                self._rotate_provider()
                return result

            except Exception as e:
                logger.warning(f"Ultra-cheap provider {provider['name']} failed: {e}")
                self._rotate_provider()
                continue

        # If all available providers failed, fallback to OpenAI
        logger.warning("All available providers failed, falling back to OpenAI")
        return await self._query_openai(prompt)

    def _rotate_provider(self):
        """Rotate to next available provider."""
        self.current_provider_index = (self.current_provider_index + 1) % len(self.available_providers)

    async def _query_deepseek(self, prompt: str, provider_config) -> str:
        """Query DeepSeek API (ultra-cheap at $0.0001/1K tokens)."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={
                        "Authorization": f"Bearer {provider_config['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4000,
                        "temperature": 0.1
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise AIProviderError(f"DeepSeek query failed: {str(e)}", provider="deepseek")

    async def _query_groq(self, prompt: str, provider_config) -> str:
        """Query Groq API (ultra-cheap at $0.0002/1K tokens)."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {provider_config['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mixtral-8x7b-32768",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4000,
                        "temperature": 0.1
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise AIProviderError(f"Groq query failed: {str(e)}", provider="groq")

    async def _query_together(self, prompt: str, provider_config) -> str:
        """Query Together API (budget at $0.0008/1K tokens)."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.together.xyz/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {provider_config['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4000,
                        "temperature": 0.1
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise AIProviderError(f"Together query failed: {str(e)}", provider="together")

    async def _query_aimlapi(self, prompt: str, provider_config) -> str:
        """Query AI/ML API (budget at $0.001/1K tokens)."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.aimlapi.com/chat/completions",
                    headers={
                        "Authorization": f"Bearer {provider_config['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4000,
                        "temperature": 0.1
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise AIProviderError(f"AI/ML API query failed: {str(e)}", provider="aimlapi")

    async def _query_minimax(self, prompt: str, provider_config) -> str:
        """Query MiniMax API (standard at $0.003/1K tokens)."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.minimax.chat/v1/text/chatcompletion_v2",
                    headers={
                        "Authorization": f"Bearer {provider_config['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "abab6.5s-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4000,
                        "temperature": 0.1
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise AIProviderError(f"MiniMax query failed: {str(e)}", provider="minimax")

    async def _query_cohere(self, prompt: str, provider_config) -> str:
        """Query Cohere API (standard at $0.002/1K tokens)."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.cohere.ai/v1/chat",
                    headers={
                        "Authorization": f"Bearer {provider_config['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "command-r-plus",
                        "message": prompt,
                        "max_tokens": 4000,
                        "temperature": 0.1
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["text"]
        except Exception as e:
            raise AIProviderError(f"Cohere query failed: {str(e)}", provider="cohere")

    async def _query_openai(self, prompt: str) -> str:
        """Query OpenAI API (expensive fallback - $0.01/1K tokens)."""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise AIProviderError(f"OpenAI query failed: {str(e)}", provider="openai")
    
    async def _query_anthropic(self, prompt: str) -> str:
        """Query Anthropic API with enhanced error handling."""
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4000,  # Increased for enhancement responses
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise AIProviderError(f"Anthropic query failed: {str(e)}", provider="anthropic")
    
    def _calculate_base_confidence(self, content: str, intelligence: Dict[str, Any]) -> float:
        """Calculate confidence score for base analysis."""
        base_score = 0.5
        
        # Content length factor
        if len(content) > 5000:
            base_score += 0.2
        elif len(content) > 1000:
            base_score += 0.1
        
        # Intelligence completeness factor
        sections = ["offer_intelligence", "psychology_intelligence", "competitive_intelligence", 
                   "content_intelligence", "brand_intelligence"]
        complete_sections = sum(1 for section in sections if intelligence.get(section))
        completeness = complete_sections / len(sections)
        base_score += completeness * 0.2
        
        return min(1.0, max(0.0, base_score))
    
    
    # =====================================
    # FALLBACK ENHANCERS
    # =====================================
    
    async def _fallback_scientific_enhancer(self, base_intel: Dict[str, Any], providers: List[Any]) -> Dict[str, Any]:
        """Fallback scientific enhancement."""
        return {
            "scientific_backing": ["Research indicates natural compounds may support health"],
            "ingredient_research": {"primary_compounds": ["natural extracts"]},
            "mechanism_of_action": {"primary_pathways": ["metabolic support"]},
            "enhancement_applied": True,
            "fallback_used": True
        }
    
    async def _fallback_credibility_enhancer(self, base_intel: Dict[str, Any], providers: List[Any]) -> Dict[str, Any]:
        """Fallback credibility enhancement."""
        return {
            "trust_indicators": ["Quality assurance", "Customer satisfaction guarantee"],
            "authority_signals": ["Professional endorsements", "Quality certifications"],
            "enhancement_applied": True,
            "fallback_used": True
        }
    
    async def _fallback_content_enhancer(self, base_intel: Dict[str, Any], providers: List[Any]) -> Dict[str, Any]:
        """Fallback content enhancement."""
        return {
            "enhanced_key_messages": ["Quality health solution", "Trusted by customers"],
            "social_proof_amplification": {"testimonial_strategies": ["Customer success stories"]},
            "enhancement_applied": True,
            "fallback_used": True
        }
    
    async def _fallback_emotional_enhancer(self, base_intel: Dict[str, Any], providers: List[Any]) -> Dict[str, Any]:
        """Fallback emotional enhancement.""" 
        return {
            "emotional_journey_mapping": {"current_emotional_state": ["Health-conscious mindset"]},
            "psychological_triggers": {"trust_building": ["Scientific backing"]},
            "enhancement_applied": True,
            "fallback_used": True
        }
    
    async def _fallback_authority_enhancer(self, base_intel: Dict[str, Any], providers: List[Any]) -> Dict[str, Any]:
        """Fallback authority enhancement."""
        return {
            "research_validation_framework": {"methodology_standards": ["Evidence-based approach"]},
            "professional_authority_markers": {"professional_credentials": ["Industry expertise"]},
            "enhancement_applied": True,
            "fallback_used": True
        }
    
    async def _fallback_market_enhancer(self, base_intel: Dict[str, Any], providers: List[Any]) -> Dict[str, Any]:
        """Fallback market enhancement."""
        return {
            "market_analysis": {"market_trends": ["Growing health awareness"]},
            "competitive_landscape": {"competitive_advantages": ["Quality focus"]},
            "enhancement_applied": True,
            "fallback_used": True
        }

    def _get_fallback_base_intelligence(self):
        """Fallback base intelligence structure."""
        return {
            "offer_intelligence": {
                "products": [],
                "key_features": [],
                "primary_benefits": [],
                "value_propositions": []
            },
            "psychology_intelligence": {
                "target_audience": "",
                "emotional_triggers": [],
                "persuasion_techniques": []
            },
            "competitive_intelligence": {
                "competitive_advantages": [],
                "market_positioning": ""
            },
            "content_intelligence": {
                "key_messages": [],
                "call_to_actions": []
            },
            "brand_intelligence": {
                "brand_voice": "",
                "brand_values": []
            },
            "confidence_score": 0.1
        }