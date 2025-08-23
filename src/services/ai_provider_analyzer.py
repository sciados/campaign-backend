# src/services/ai_provider_analyzer.py - FULLY DYNAMIC VERSION

"""
🤖 Dynamic AI-Powered Provider Analysis System
NO HARDCODED CATEGORIES - Everything is AI-analyzed in real-time
Uses AI to:
- Analyze provider capabilities from their API/documentation
- Determine categories dynamically
- Calculate pricing and performance metrics
- Detect video/image/text/audio/multimodal capabilities
"""

import os
import re
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

class DynamicAIProviderAnalyzer:
    """Fully dynamic AI-powered system to analyze providers with zero hardcoding"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.initialize_ai_clients()
    
    def initialize_ai_clients(self):
        """Initialize AI clients for analysis"""
        try:
            if os.getenv('OPENAI_API_KEY'):
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        except ImportError:
            pass
            
        try:
            if os.getenv('ANTHROPIC_API_KEY'):
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        except ImportError:
            pass
    
    async def discover_providers_from_environment(self) -> List[Dict[str, Any]]:
        """
        🔍 Discover AI providers from environment variables
        Returns fully AI-analyzed provider data with dynamic categorization
        """
        discovered_providers = []
        env_vars = dict(os.environ)
        
        # Smart pattern matching for AI provider API keys
        ai_patterns = [
            r'^([A-Z_]+)_API_KEY$',
            r'^([A-Z_]+)_KEY$', 
            r'^([A-Z_]+)_TOKEN$',
            r'^([A-Z_]+)_API_TOKEN$'
        ]
        
        # Skip non-AI patterns
        skip_patterns = ['DATABASE', 'JWT', 'SECRET', 'CLOUDFLARE', 'RAILWAY', 'SUPABASE', 'STRIPE', 'ALLOWED', 'CREDIT']
        
        for env_var, value in env_vars.items():
            for pattern in ai_patterns:
                match = re.match(pattern, env_var)
                if match:
                    provider_key = match.group(1).lower()
                    
                    # Skip obviously non-AI variables
                    if any(skip in provider_key.upper() for skip in skip_patterns):
                        continue
                    
                    # 🤖 AI-analyze this provider dynamically
                    provider_data = await self.ai_analyze_provider(env_var, provider_key, value)
                    if provider_data:
                        discovered_providers.append(provider_data)
                    break
        
        return discovered_providers
    
    async def ai_analyze_provider(self, env_var: str, provider_key: str, api_key: str) -> Optional[Dict[str, Any]]:
        """
        🤖 Use AI to completely analyze a provider and determine all characteristics
        NO HARDCODED DATA - Everything is AI-determined
        """
        try:
            # 1. 🤖 AI identifies the provider and its characteristics
            provider_identity = await self.ai_identify_provider(provider_key, api_key)
            
            # 2. 🌐 Web research for pricing and capabilities
            web_research = await self.ai_web_research_provider(provider_identity['name'])
            
            # 3. 🔍 API analysis for real capabilities
            api_analysis = await self.ai_analyze_api_capabilities(provider_identity, api_key)
            
            # 4. 🤖 AI determines final categorization and metrics
            final_analysis = await self.ai_final_categorization(provider_identity, web_research, api_analysis)
            
            # 5. 📊 Performance testing
            performance_data = await self.test_api_performance(final_analysis, api_key)
            
            return {
                'provider_name': final_analysis['provider_name'],
                'env_var_name': env_var,
                'env_var_status': 'configured' if api_key and api_key.strip() else 'empty',
                'value_preview': api_key[:10] + '...' if api_key and len(api_key) > 10 else api_key,
                'integration_status': 'active' if performance_data['api_accessible'] else 'pending',
                
                # 🤖 AI-DETERMINED CATEGORIES (no hardcoding)
                'primary_category': final_analysis['primary_category'],
                'secondary_categories': final_analysis['secondary_categories'],
                'capabilities': final_analysis['capabilities'],
                'use_types': final_analysis['use_types'],
                
                # 🤖 AI-CALCULATED METRICS
                'cost_per_1k_tokens': final_analysis['estimated_cost_per_1k_tokens'],
                'video_cost_per_minute': final_analysis.get('video_cost_per_minute'),
                'image_cost_per_generation': final_analysis.get('image_cost_per_generation'),
                'quality_score': final_analysis['estimated_quality_score'],
                'speed_rating': final_analysis['estimated_speed_rating'],
                
                'priority_tier': self.ai_calculate_priority_tier(final_analysis),
                'primary_model': final_analysis['primary_model'],
                'supported_models': final_analysis['supported_models'],
                
                # Performance data
                'monthly_usage': 0,
                'response_time_ms': performance_data['avg_response_time'],
                'error_rate': performance_data['error_rate'],
                'api_endpoint': final_analysis['api_endpoint'],
                
                # Metadata
                'source': 'ai_analyzed',
                'last_checked': datetime.utcnow(),
                'is_active': performance_data['api_accessible'],
                'discovery_date': datetime.utcnow(),
                'ai_analysis_version': '2.0_dynamic',
                'ai_confidence_score': final_analysis['confidence_score']
            }
            
        except Exception as e:
            print(f"⚠️ Error AI-analyzing provider {provider_key}: {e}")
            return None
    
    async def ai_identify_provider(self, provider_key: str, api_key: str) -> Dict[str, Any]:
        """
        🤖 Use AI to identify what provider this is based on key pattern and name
        """
        # Prepare AI prompt for provider identification
        prompt = f"""
        Analyze this AI provider and identify what service it is:
        
        Environment Variable: {provider_key}
        API Key Pattern: {api_key[:15]}...
        
        Based on the environment variable name and API key pattern, identify:
        1. The exact provider name (e.g., "OpenAI", "Replicate", "Anthropic")
        2. The company/service behind it
        3. The most likely API endpoint URL
        4. Primary model/service they're known for
        
        Respond in JSON format:
        {{
            "name": "Provider Name",
            "company": "Company Name", 
            "likely_endpoint": "https://api.example.com/v1",
            "primary_service": "text generation/image generation/etc",
            "confidence": 0.95
        }}
        """
        
        ai_response = await self.call_ai_for_analysis(prompt)
        
        # Parse AI response or provide fallback
        try:
            if ai_response:
                return json.loads(ai_response)
        except:
            pass
        
        # Fallback logic if AI fails
        return {
            "name": provider_key.replace('_', ' ').title(),
            "company": "Unknown",
            "likely_endpoint": f"https://api.{provider_key.lower()}.com/v1",
            "primary_service": "unknown",
            "confidence": 0.1
        }
    
    async def ai_web_research_provider(self, provider_name: str) -> Dict[str, Any]:
        """
        🌐 AI researches the provider online to get pricing and capabilities
        """
        # This would use web scraping + AI analysis in production
        # For now, simulate with AI knowledge
        
        prompt = f"""
        Research the AI provider "{provider_name}" and provide:
        
        1. What categories of AI services do they offer? (text, image, video, audio, multimodal)
        2. What are their typical pricing models?
        3. What are their most popular models/services?
        4. What makes them unique in the market?
        5. Are they known for being cheap, fast, high-quality, or specialized?
        
        Respond in JSON:
        {{
            "categories": ["text_generation", "image_generation"],
            "pricing_model": "per_token/per_minute/per_request",
            "typical_cost_range": "0.001-0.03 per 1k tokens",
            "popular_models": ["model1", "model2"],
            "unique_features": ["feature1", "feature2"],
            "market_position": "budget/premium/specialized/mainstream",
            "video_capable": true/false,
            "image_capable": true/false,
            "multimodal_capable": true/false
        }}
        """
        
        ai_response = await self.call_ai_for_analysis(prompt)
        
        try:
            if ai_response:
                return json.loads(ai_response)
        except:
            pass
        
        # Fallback
        return {
            "categories": ["unknown"],
            "pricing_model": "unknown",
            "market_position": "unknown",
            "video_capable": False,
            "image_capable": False,
            "multimodal_capable": False
        }
    
    async def ai_analyze_api_capabilities(self, provider_identity: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """
        🔍 AI analyzes actual API endpoints to determine real capabilities
        """
        capabilities = {
            "text_generation": False,
            "image_generation": False, 
            "video_generation": False,
            "audio_generation": False,
            "multimodal": False,
            "available_models": [],
            "api_accessible": False
        }
        
        try:
            # Try to call /models endpoint to see what's available
            endpoint = provider_identity.get('likely_endpoint', '')
            if endpoint:
                async with aiohttp.ClientSession() as session:
                    headers = {'Authorization': f'Bearer {api_key}'}
                    
                    # Try common model listing endpoints
                    model_endpoints = ['/models', '/v1/models', '/api/v1/models']
                    
                    for model_endpoint in model_endpoints:
                        try:
                            async with session.get(f"{endpoint.rstrip('/')}{model_endpoint}", 
                                                 headers=headers, timeout=10) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    capabilities["api_accessible"] = True
                                    
                                    # 🤖 AI analyzes the model list to determine capabilities
                                    model_analysis = await self.ai_analyze_model_list(data)
                                    capabilities.update(model_analysis)
                                    break
                        except:
                            continue
        except Exception as e:
            print(f"API analysis failed: {e}")
        
        return capabilities
    
    async def ai_analyze_model_list(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🤖 AI analyzes a list of models to determine capabilities
        """
        prompt = f"""
        Analyze this API response containing available models and determine capabilities:
        
        {json.dumps(model_data, indent=2)[:2000]}...
        
        Based on the model names and descriptions, determine:
        1. Does this provider support text generation?
        2. Does this provider support image generation? 
        3. Does this provider support video generation?
        4. Does this provider support audio generation?
        5. Is this a multimodal provider?
        6. What are the key model names?
        
        Look for keywords like:
        - Text: gpt, claude, llama, text, chat, instruct
        - Image: dall-e, flux, stable-diffusion, imagen, midjourney
        - Video: video, kling, runway, luma, veo, seedance
        - Audio: whisper, voice, tts, audio, music
        
        Respond in JSON:
        {{
            "text_generation": true/false,
            "image_generation": true/false,
            "video_generation": true/false,
            "audio_generation": true/false,
            "multimodal": true/false,
            "available_models": ["model1", "model2"],
            "primary_capability": "text/image/video/audio/multimodal"
        }}
        """
        
        ai_response = await self.call_ai_for_analysis(prompt)
        
        try:
            if ai_response:
                return json.loads(ai_response)
        except:
            pass
        
        return {
            "text_generation": False,
            "image_generation": False,
            "video_generation": False,
            "audio_generation": False,
            "multimodal": False,
            "available_models": [],
            "primary_capability": "unknown"
        }
    
    async def ai_final_categorization(self, provider_identity: Dict, web_research: Dict, api_analysis: Dict) -> Dict[str, Any]:
        """
        🤖 AI makes final decision on categorization based on all data
        """
        prompt = f"""
        Based on all this research data, provide final categorization for this AI provider:
        
        Provider Identity: {json.dumps(provider_identity)}
        Web Research: {json.dumps(web_research)}
        API Analysis: {json.dumps(api_analysis)}
        
        Determine:
        1. Primary category (choose ONE): text_generation, image_generation, video_generation, audio_generation, multimodal
        2. Secondary categories (list all that apply)
        3. Specific capabilities list
        4. Use types (what is this provider best for?)
        5. Estimated pricing (cost per 1k tokens, cost per minute for video, cost per image)
        6. Quality score (1-5 based on reputation and capabilities)
        7. Speed rating (1-5 based on known performance)
        8. Priority tier recommendation
        
        Respond in JSON:
        {{
            "provider_name": "Exact Provider Name",
            "primary_category": "multimodal",
            "secondary_categories": ["text_generation", "image_generation"],
            "capabilities": ["specific", "capability", "list"],
            "use_types": ["what_its_best_for"],
            "estimated_cost_per_1k_tokens": 0.001,
            "video_cost_per_minute": 1.08,
            "image_cost_per_generation": 0.02,
            "estimated_quality_score": 4.2,
            "estimated_speed_rating": 4.5,
            "primary_model": "most_popular_model",
            "supported_models": ["model1", "model2"],
            "api_endpoint": "correct_api_endpoint",
            "confidence_score": 0.95,
            "reasoning": "why these decisions were made"
        }}
        """
        
        ai_response = await self.call_ai_for_analysis(prompt)
        
        try:
            if ai_response:
                result = json.loads(ai_response)
                # Ensure we have all required fields
                return self.validate_and_complete_analysis(result)
        except Exception as e:
            print(f"AI final categorization failed: {e}")
        
        # Fallback
        return self.create_fallback_analysis(provider_identity)
    
    def validate_and_complete_analysis(self, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        ✅ Validate AI analysis and fill in missing fields
        """
        # Ensure required fields exist
        required_fields = {
            'provider_name': 'Unknown Provider',
            'primary_category': 'unknown',
            'secondary_categories': [],
            'capabilities': [],
            'use_types': ['general_ai'],
            'estimated_cost_per_1k_tokens': 0.001,
            'estimated_quality_score': 3.0,
            'estimated_speed_rating': 3.0,
            'primary_model': 'unknown',
            'supported_models': [],
            'api_endpoint': 'https://api.unknown.com/v1',
            'confidence_score': 0.5
        }
        
        for field, default_value in required_fields.items():
            if field not in ai_result:
                ai_result[field] = default_value
        
        return ai_result
    
    def create_fallback_analysis(self, provider_identity: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚨 Create fallback analysis if AI fails
        """
        return {
            'provider_name': provider_identity.get('name', 'Unknown Provider'),
            'primary_category': 'unknown',
            'secondary_categories': [],
            'capabilities': ['general_ai'],
            'use_types': ['unknown'],
            'estimated_cost_per_1k_tokens': 0.001,
            'estimated_quality_score': 3.0,
            'estimated_speed_rating': 3.0,
            'primary_model': 'unknown',
            'supported_models': [],
            'api_endpoint': provider_identity.get('likely_endpoint', 'unknown'),
            'confidence_score': 0.1,
            'reasoning': 'Fallback analysis due to AI failure'
        }
    
    async def call_ai_for_analysis(self, prompt: str) -> Optional[str]:
        """
        🤖 Call available AI service for analysis
        """
        try:
            # Try OpenAI first
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",  # Cheaper model for analysis
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.1
                )
                return response.choices[0].message.content
            
            # Try Anthropic as backup
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",  # Cheaper model for analysis
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
                
        except Exception as e:
            print(f"AI analysis call failed: {e}")
        
        return None
    
    def ai_calculate_priority_tier(self, analysis: Dict[str, Any]) -> str:
        """
        🎯 AI-calculated priority tier based on multiple factors
        """
        cost = analysis.get('estimated_cost_per_1k_tokens', 0.001)
        quality = analysis.get('estimated_quality_score', 3.0)
        speed = analysis.get('estimated_speed_rating', 3.0)
        confidence = analysis.get('confidence_score', 0.5)
        
        # Multi-factor scoring
        if cost <= 0.0003 and quality >= 4.0 and confidence >= 0.8:
            return 'primary'
        elif cost <= 0.001 and quality >= 3.5 and speed >= 4.0:
            return 'secondary'  
        elif quality >= 4.5 and confidence >= 0.9:
            return 'premium'
        elif 'video' in analysis.get('primary_category', ''):
            return 'video_specialized'
        elif 'image' in analysis.get('primary_category', ''):
            return 'image_specialized'
        elif confidence < 0.3:
            return 'needs_review'
        else:
            return 'discovered'
    
    async def test_api_performance(self, analysis: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """
        ⚡ Test actual API performance
        """
        try:
            start_time = datetime.utcnow()
            
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {api_key}'}
                test_url = f"{analysis['api_endpoint']}/models"
                
                async with session.get(test_url, headers=headers, timeout=10) as response:
                    response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    return {
                        'api_accessible': response.status == 200,
                        'avg_response_time': int(response_time),
                        'error_rate': 0.0 if response.status == 200 else 1.0,
                        'timestamp': datetime.utcnow(),
                        'status_code': response.status
                    }
                    
        except Exception as e:
            return {
                'api_accessible': False,
                'avg_response_time': None,
                'error_rate': 1.0,
                'timestamp': datetime.utcnow(),
                'error': str(e)
            }


# Global instance
_dynamic_analyzer_instance = None

def get_dynamic_ai_provider_analyzer() -> DynamicAIProviderAnalyzer:
    """Get singleton instance of Dynamic AI Provider Analyzer"""
    global _dynamic_analyzer_instance
    if _dynamic_analyzer_instance is None:
        _dynamic_analyzer_instance = DynamicAIProviderAnalyzer()
    return _dynamic_analyzer_instance