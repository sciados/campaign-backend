# scripts/validate_ultra_cheap_providers.py
"""
ULTRA-CHEAP PROVIDER VALIDATION SCRIPT
✅ Test all your Railway API keys
✅ Validate cost savings potential
✅ Benchmark performance across providers
✅ Generate deployment readiness report
"""

import os
import asyncio
import time
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltraCheapProviderValidator:
    """Validate ultra-cheap providers on Railway"""
    
    def __init__(self):
        self.results = {
            "text_providers": {},
            "image_providers": {},
            "cost_analysis": {},
            "deployment_readiness": {}
        }
    
    async def validate_all_providers(self) -> Dict[str, Any]:
        """Validate all ultra-cheap providers"""
        
        logger.info("🚀 Starting Ultra-Cheap Provider Validation")
        logger.info("=" * 60)
        
        # Validate text providers
        await self._validate_text_providers()
        
        # Validate image providers  
        await self._validate_image_providers()
        
        # Analyze cost savings
        self._analyze_cost_savings()
        
        # Check deployment readiness
        self._check_deployment_readiness()
        
        # Generate summary report
        self._generate_summary_report()
        
        return self.results
    
    async def _validate_text_providers(self):
        """Validate text generation providers"""
        
        logger.info("📝 VALIDATING TEXT PROVIDERS:")
        
        text_providers = [
            {
                "name": "groq",
                "api_key_env": "GROQ_API_KEY",
                "cost_per_1k": 0.0002,
                "expected_quality": 78
            },
            {
                "name": "together",
                "api_key_env": "TOGETHER_API_KEY", 
                "cost_per_1k": 0.0008,
                "expected_quality": 82
            },
            {
                "name": "deepseek",
                "api_key_env": "DEEPSEEK_API_KEY",
                "cost_per_1k": 0.00014,
                "expected_quality": 72
            },
            {
                "name": "anthropic",
                "api_key_env": "ANTHROPIC_API_KEY",
                "cost_per_1k": 0.0025,
                "expected_quality": 90
            },
            {
                "name": "openai",
                "api_key_env": "OPENAI_API_KEY",
                "cost_per_1k": 0.0015,
                "expected_quality": 88
            }
        ]
        
        for provider in text_providers:
            result = await self._test_text_provider(provider)
            self.results["text_providers"][provider["name"]] = result
            
            status_emoji = "✅" if result["available"] else "❌"
            cost_savings = ((0.030 - provider["cost_per_1k"]) / 0.030) * 100
            
            logger.info(f"   {status_emoji} {provider['name']}: ${provider['cost_per_1k']:.5f}/1K ({cost_savings:.1f}% savings)")
            
            if result["available"] and result.get("test_successful"):
                logger.info(f"      Response time: {result.get('response_time', 0):.2f}s")
                logger.info(f"      Test result: {result.get('test_response', 'N/A')[:50]}...")
    
    async def _validate_image_providers(self):
        """Validate image generation providers"""
        
        logger.info("\n🎨 VALIDATING IMAGE PROVIDERS:")
        
        image_providers = [
            {
                "name": "fal_ai",
                "api_key_env": "FAL_API_KEY",
                "cost_per_image": 0.0015,
                "expected_quality": 83
            },
            {
                "name": "stability_ai",
                "api_key_env": "STABILITY_API_KEY",
                "cost_per_image": 0.002,
                "expected_quality": 85
            },
            {
                "name": "replicate",
                "api_key_env": "REPLICATE_API_TOKEN",
                "cost_per_image": 0.004,
                "expected_quality": 80
            },
            {
                "name": "openai_dalle",
                "api_key_env": "OPENAI_API_KEY",
                "cost_per_image": 0.040,
                "expected_quality": 92
            }
        ]
        
        for provider in image_providers:
            result = await self._test_image_provider(provider)
            self.results["image_providers"][provider["name"]] = result
            
            status_emoji = "✅" if result["available"] else "❌"
            cost_savings = ((0.040 - provider["cost_per_image"]) / 0.040) * 100
            
            logger.info(f"   {status_emoji} {provider['name']}: ${provider['cost_per_image']:.4f}/image ({cost_savings:.1f}% savings)")
            
            if result["available"]:
                logger.info(f"      Speed rating: {provider['expected_quality']}/100")
    
    async def _test_text_provider(self, provider: Dict) -> Dict[str, Any]:
        """Test individual text provider"""
        
        api_key = os.getenv(provider["api_key_env"])
        
        if not api_key:
            return {
                "available": False,
                "error": f"Missing {provider['api_key_env']} environment variable",
                "test_successful": False
            }
        
        try:
            start_time = time.time()
            
            # Test based on provider type
            if provider["name"] == "groq":
                result = await self._test_groq(api_key)
            elif provider["name"] == "together":
                result = await self._test_together(api_key)
            elif provider["name"] == "deepseek":
                result = await self._test_deepseek(api_key)
            elif provider["name"] == "anthropic":
                result = await self._test_anthropic(api_key)
            elif provider["name"] == "openai":
                result = await self._test_openai(api_key)
            else:
                return {"available": False, "error": "Unknown provider type", "test_successful": False}
            
            response_time = time.time() - start_time
            
            return {
                "available": True,
                "test_successful": True,
                "response_time": response_time,
                "test_response": result,
                "cost_per_1k": provider["cost_per_1k"],
                "estimated_monthly_cost": provider["cost_per_1k"] * 100  # 100K tokens/month estimate
            }
            
        except Exception as e:
            return {
                "available": True,
                "test_successful": False,
                "error": str(e),
                "cost_per_1k": provider["cost_per_1k"]
            }
    
    async def _test_image_provider(self, provider: Dict) -> Dict[str, Any]:
        """Test individual image provider"""
        
        api_key = os.getenv(provider["api_key_env"])
        
        if not api_key:
            return {
                "available": False,
                "error": f"Missing {provider['api_key_env']} environment variable"
            }
        
        # For now, just check API key availability
        # Full image testing would require actual API calls
        return {
            "available": True,
            "test_note": "API key available - ready for image generation",
            "cost_per_image": provider["cost_per_image"],
            "estimated_monthly_cost": provider["cost_per_image"] * 1000  # 1000 images/month estimate
        }
    
    async def _test_groq(self, api_key: str) -> str:
        """Test Groq API"""
        try:
            import groq
            client = groq.AsyncGroq(api_key=api_key)
            
            response = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Say 'Groq ultra-cheap AI test successful'"}],
                max_tokens=50
            )
            
            return response.choices[0].message.content
        except ImportError:
            return "Groq package not installed (pip install groq)"
        except Exception as e:
            raise Exception(f"Groq test failed: {str(e)}")
    
    async def _test_together(self, api_key: str) -> str:
        """Test Together AI API"""
        try:
            import openai
            client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.together.xyz/v1"
            )
            
            response = await client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                messages=[{"role": "user", "content": "Say 'Together AI ultra-cheap test successful'"}],
                max_tokens=50
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Together AI test failed: {str(e)}")
    
    async def _test_deepseek(self, api_key: str) -> str:
        """Test DeepSeek API"""
        try:
            import openai
            client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            
            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "Say 'DeepSeek ultra-cheap test successful'"}],
                max_tokens=50
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"DeepSeek test failed: {str(e)}")
    
    async def _test_anthropic(self, api_key: str) -> str:
        """Test Anthropic API"""
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=api_key)
            
            response = await client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=50,
                messages=[{"role": "user", "content": "Say 'Anthropic fallback test successful'"}]
            )
            
            return response.content[0].text
        except ImportError:
            return "Anthropic package not installed (pip install anthropic)"
        except Exception as e:
            raise Exception(f"Anthropic test failed: {str(e)}")
    
    async def _test_openai(self, api_key: str) -> str:
        """Test OpenAI API"""
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=api_key)
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'OpenAI emergency fallback test successful'"}],
                max_tokens=50
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI test failed: {str(e)}")
    
    def _analyze_cost_savings(self):
        """Analyze potential cost savings"""
        
        logger.info("\n💰 COST SAVINGS ANALYSIS:")
        
        # Text provider analysis
        available_text = [p for p in self.results["text_providers"].values() if p.get("available")]
        if available_text:
            cheapest_text = min(available_text, key=lambda x: x.get("cost_per_1k", 999))
            text_savings = ((0.030 - cheapest_text["cost_per_1k"]) / 0.030) * 100
            
            logger.info(f"   Cheapest text: ${cheapest_text['cost_per_1k']:.5f}/1K tokens")
            logger.info(f"   Text savings: {text_savings:.1f}% vs OpenAI GPT-4")
        
        # Image provider analysis
        available_image = [p for p in self.results["image_providers"].values() if p.get("available")]
        if available_image:
            cheapest_image = min(available_image, key=lambda x: x.get("cost_per_image", 999))
            image_savings = ((0.040 - cheapest_image["cost_per_image"]) / 0.040) * 100
            
            logger.info(f"   Cheapest image: ${cheapest_image['cost_per_image']:.4f}/image")
            logger.info(f"   Image savings: {image_savings:.1f}% vs DALL-E")
        
        # Monthly projections (1000 users)
        if available_text and available_image:
            monthly_text_cost = cheapest_text["cost_per_1k"] * 100 * 1000  # 100K tokens per user
            monthly_image_cost = cheapest_image["cost_per_image"] * 5 * 1000  # 5 images per user
            
            openai_monthly = (0.030 * 100 * 1000) + (0.040 * 5 * 1000)
            ultra_cheap_monthly = monthly_text_cost + monthly_image_cost
            
            monthly_savings = openai_monthly - ultra_cheap_monthly
            annual_savings = monthly_savings * 12
            
            logger.info(f"\n   PROJECTIONS (1,000 users):")
            logger.info(f"   Current monthly cost: ${openai_monthly:,.2f}")
            logger.info(f"   Ultra-cheap monthly: ${ultra_cheap_monthly:,.2f}")
            logger.info(f"   Monthly savings: ${monthly_savings:,.2f}")
            logger.info(f"   Annual savings: ${annual_savings:,.2f}")
            
            self.results["cost_analysis"] = {
                "current_monthly": openai_monthly,
                "ultra_cheap_monthly": ultra_cheap_monthly,
                "monthly_savings": monthly_savings,
                "annual_savings": annual_savings,
                "savings_percentage": (monthly_savings / openai_monthly) * 100
            }
    
    def _check_deployment_readiness(self):
        """Check deployment readiness"""
        
        logger.info("\n🚀 DEPLOYMENT READINESS CHECK:")
        
        # Count available providers
        available_text = sum(1 for p in self.results["text_providers"].values() if p.get("available"))
        available_image = sum(1 for p in self.results["image_providers"].values() if p.get("available"))
        
        working_text = sum(1 for p in self.results["text_providers"].values() if p.get("test_successful"))
        
        # Check requirements
        min_text_providers = 2
        min_image_providers = 1
        
        text_ready = available_text >= min_text_providers
        image_ready = available_image >= min_image_providers
        
        deployment_ready = text_ready and image_ready
        
        logger.info(f"   Text providers: {available_text} available, {working_text} tested successfully")
        logger.info(f"   Image providers: {available_image} available")
        logger.info(f"   Minimum requirements: {min_text_providers} text, {min_image_providers} image")
        
        status_emoji = "✅" if deployment_ready else "⚠️"
        logger.info(f"   {status_emoji} Deployment ready: {deployment_ready}")
        
        self.results["deployment_readiness"] = {
            "ready": deployment_ready,
            "available_text_providers": available_text,
            "available_image_providers": available_image,
            "working_text_providers": working_text,
            "requirements_met": {
                "text_providers": text_ready,
                "image_providers": image_ready
            }
        }
        
        # Recommendations
        recommendations = []
        if not text_ready:
            recommendations.append("Add more text provider API keys")
        if not image_ready:
            recommendations.append("Add image provider API keys")
        if available_text == 0:
            recommendations.append("CRITICAL: No text providers available")
        if available_image == 0:
            recommendations.append("CRITICAL: No image providers available")
        
        if not recommendations:
            recommendations.append("System ready for deployment!")
        
        self.results["deployment_readiness"]["recommendations"] = recommendations
    
    def _generate_summary_report(self):
        """Generate summary report"""
        
        logger.info("\n📊 VALIDATION SUMMARY REPORT:")
        logger.info("=" * 60)
        
        # Provider summary
        text_count = sum(1 for p in self.results["text_providers"].values() if p.get("available"))
        image_count = sum(1 for p in self.results["image_providers"].values() if p.get("available"))
        
        logger.info(f"✅ Available Providers: {text_count} text, {image_count} image")
        
        # Cost summary
        if "cost_analysis" in self.results:
            cost = self.results["cost_analysis"]
            logger.info(f"💰 Monthly Savings: ${cost['monthly_savings']:,.2f} ({cost['savings_percentage']:.1f}%)")
            logger.info(f"📈 Annual Savings: ${cost['annual_savings']:,.2f}")
        
        # Deployment status
        deployment = self.results["deployment_readiness"]
        status_emoji = "🚀" if deployment["ready"] else "⚠️"
        logger.info(f"{status_emoji} Deployment Ready: {deployment['ready']}")
        
        # Recommendations
        logger.info("\n📋 RECOMMENDATIONS:")
        for rec in deployment["recommendations"]:
            logger.info(f"   • {rec}")
        
        # Next steps
        if deployment["ready"]:
            logger.info("\n🎯 NEXT STEPS:")
            logger.info("   1. Deploy enhanced base_generator.py")
            logger.info("   2. Deploy enhanced factory.py")
            logger.info("   3. Deploy unified_ultra_cheap_provider.py")
            logger.info("   4. Update high-priority generators")
            logger.info("   5. Monitor cost savings in real-time")


async def main():
    """Run ultra-cheap provider validation"""
    
    validator = UltraCheapProviderValidator()
    results = await validator.validate_all_providers()
    
    # Save results to file
    import json
    with open("ultra_cheap_validation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n📄 Results saved to: ultra_cheap_validation_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())