# =====================================
# File: src/intelligence/analysis/handler.py
# =====================================

"""
Analysis handler for coordinating AI-powered content analysis.

Manages the analysis pipeline including AI provider routing,
content processing, and result extraction.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
import openai
import anthropic

from src.core.config import ai_provider_config, settings
from src.core.shared.decorators import retry_on_failure
from src.core.shared.exceptions import AIProviderError, ServiceUnavailableError

logger = logging.getLogger(__name__)


class AnalysisHandler:
    """Handler for AI-powered content analysis operations."""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    @retry_on_failure(max_retries=2)
    async def extract_product_info(self, content: str, provider_name: str = "openai") -> Dict[str, Any]:
        """Extract basic product information using AI."""
        
        prompt = f"""
        Analyze the following content and extract product information. Return a JSON object with:
        - name: Product name
        - features: List of key features (max 10)
        - benefits: List of key benefits (max 10)
        - ingredients: List of ingredients if mentioned
        - conditions: List of health conditions it addresses
        - usage_instructions: List of usage instructions if mentioned
        
        Content: {content[:4000]}
        
        Return only valid JSON.
        """
        
        try:
            if provider_name == "openai":
                response = await self._query_openai(prompt)
            elif provider_name == "anthropic":
                response = await self._query_anthropic(prompt)
            else:
                # Fallback to cheapest provider
                response = await self._query_openai(prompt)
            
            # Parse JSON response
            product_info = json.loads(response)
            
            # Ensure required fields
            return {
                "name": product_info.get("name", "Unknown Product"),
                "features": product_info.get("features", [])[:10],
                "benefits": product_info.get("benefits", [])[:10],
                "ingredients": product_info.get("ingredients", []),
                "conditions": product_info.get("conditions", []),
                "usage_instructions": product_info.get("usage_instructions", [])
            }
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}")
            return self._extract_fallback_product_info(content)
        except Exception as e:
            logger.error(f"Product info extraction failed: {e}")
            raise AIProviderError(f"Failed to extract product info: {str(e)}", provider=provider_name)
    
    async def extract_market_info(self, content: str, provider_name: str = "openai") -> Dict[str, Any]:
        """Extract basic market information using AI."""
        
        prompt = f"""
        Analyze the following content and extract market information. Return a JSON object with:
        - category: Product category (e.g., "Health Supplement", "Beauty Product")
        - positioning: How the product is positioned in the market
        - competitive_advantages: List of competitive advantages mentioned
        - target_audience: Description of the target audience
        
        Content: {content[:4000]}
        
        Return only valid JSON.
        """
        
        try:
            if provider_name == "openai":
                response = await self._query_openai(prompt)
            elif provider_name == "anthropic":
                response = await self._query_anthropic(prompt)
            else:
                response = await self._query_openai(prompt)
            
            market_info = json.loads(response)
            
            return {
                "category": market_info.get("category"),
                "positioning": market_info.get("positioning"),
                "competitive_advantages": market_info.get("competitive_advantages", []),
                "target_audience": market_info.get("target_audience")
            }
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse market info JSON: {e}")
            return self._extract_fallback_market_info(content)
        except Exception as e:
            logger.error(f"Market info extraction failed: {e}")
            return {"category": None, "positioning": None, "competitive_advantages": [], "target_audience": None}
    
    async def extract_detailed_product_info(self, content: str, provider_name: str) -> Dict[str, Any]:
        """Extract detailed product information for deep analysis."""
        # Enhanced version with more detailed prompts
        return await self.extract_product_info(content, provider_name)
    
    async def extract_detailed_market_info(self, content: str, provider_name: str) -> Dict[str, Any]:
        """Extract detailed market information for deep analysis."""
        # Enhanced version with more detailed prompts
        return await self.extract_market_info(content, provider_name)
    
    async def extract_comprehensive_product_info(self, content: str, provider_name: str) -> Dict[str, Any]:
        """Extract comprehensive product information for enhanced analysis."""
        # Most detailed version with multiple AI passes
        return await self.extract_product_info(content, provider_name)
    
    async def extract_comprehensive_market_info(self, content: str, provider_name: str) -> Dict[str, Any]:
        """Extract comprehensive market information for enhanced analysis."""
        # Most detailed version with multiple AI passes
        return await self.extract_market_info(content, provider_name)
    
    async def gather_basic_research(self, product_name: str, content: str) -> List[Dict[str, Any]]:
        """Gather basic research for deep analysis."""
        # Placeholder - implement research gathering logic
        return []
    
    async def gather_comprehensive_research(self, product_name: str, content: str, category: str) -> List[Dict[str, Any]]:
        """Gather comprehensive research for enhanced analysis."""
        # Placeholder - implement comprehensive research logic
        return []
    
    async def _query_openai(self, prompt: str) -> str:
        """Query OpenAI API."""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise AIProviderError(f"OpenAI query failed: {str(e)}", provider="openai")
    
    async def _query_anthropic(self, prompt: str) -> str:
        """Query Anthropic API."""
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise AIProviderError(f"Anthropic query failed: {str(e)}", provider="anthropic")
    
    def _extract_fallback_product_info(self, content: str) -> Dict[str, Any]:
        """Fallback product info extraction using simple text analysis."""
        return {
            "name": "Unknown Product",
            "features": [],
            "benefits": [],
            "ingredients": [],
            "conditions": [],
            "usage_instructions": []
        }
    
    def _extract_fallback_market_info(self, content: str) -> Dict[str, Any]:
        """Fallback market info extraction."""
        return {
            "category": None,
            "positioning": None,
            "competitive_advantages": [],
            "target_audience": None
        }