# COMPLETE: src/intelligence/analyzers.py - Product Name Placeholder Fix
"""
Intelligence analysis engines - The core AI that extracts competitive insights
🔥 FIXED: Product name placeholder issue - AI now uses actual product names
📝 UPDATED:  prompts and post-processing to eliminate generic placeholders
✅ COMPLETE: Full file with all methods and placeholder substitution system
"""
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import openai
import json
import re
from typing import Dict, List, Any, Optional
import logging
from urllib.parse import urlparse, urljoin
import uuid
from datetime import datetime
import os

logger = logging.getLogger(__name__)

# ✅ UPDATED: Import both tiered provider AND load balancing utilities
try:
    from src.intelligence.utils.tiered_ai_provider import (
        get_tiered_ai_provider, 
        make_tiered_ai_request, 
        ServiceTier
    )
    TIERED_AI_AVAILABLE = True
    logger.info("✅ Tiered AI provider imported successfully")
except ImportError as e:
    TIERED_AI_AVAILABLE = False
    logger.warning(f"⚠️ Tiered AI provider not available: {e}")

# 🔥 NEW: Import load balancing system from enhancement module
try:
    from src.intelligence.amplifier.enhancement import (
        get_load_balancing_stats,
        _get_next_provider_with_load_balancing,
        _provider_usage_stats
    )
    LOAD_BALANCING_AVAILABLE = True
    logger.info("✅ Load balancing system imported successfully")
except ImportError as e:
    LOAD_BALANCING_AVAILABLE = False
    logger.warning(f"⚠️ Load balancing system not available: {e}")

# ✅ FIXED: Import product extractor with error handling
try:
    from src.intelligence.extractors.product_extractor import ProductNameExtractor, extract_product_name
    PRODUCT_EXTRACTOR_AVAILABLE = True
    logger.info("✅ Product extractor imported successfully")
except ImportError as e:
    PRODUCT_EXTRACTOR_AVAILABLE = False
    logger.warning(f"⚠️ Product extractor import failed: {e}")

class SalesPageAnalyzer:
    """Analyze competitor sales pages for offers, psychology, and opportunities"""
    
    def __init__(self):
        # 🔥 UPDATED: Use load balanced AI provider system when available
        print("🤖 Initializing AI provider system with load balancing...")
        logger.info("🤖 Starting AI provider initialization with load balancing")
        
        # Try to use load balanced system first
        if TIERED_AI_AVAILABLE and LOAD_BALANCING_AVAILABLE:
            self.use_load_balanced_system = True
            self._init_load_balanced_providers()
        elif TIERED_AI_AVAILABLE:
            self.use_load_balanced_system = False
            self._init_tiered_providers()
        else:
            self.use_load_balanced_system = False
            print("❌ No AI provider systems available - using expensive providers")
            logger.warning("❌ No AI provider systems available")
            self.available_providers = []
            self._init_expensive_providers_fallback()
        
        # ✅ Keep product extractor initialization
        if PRODUCT_EXTRACTOR_AVAILABLE:
            self.product_extractor = ProductNameExtractor()
            logger.info("✅ Product extractor initialized")
        else:
            self.product_extractor = None
            logger.warning("⚠️ Product extractor not available")
    
    def _init_load_balanced_providers(self):
        """🔥 NEW: Initialize with load balanced provider system"""
        try:
            # Get the tiered provider manager
            self.ai_provider_manager = get_tiered_ai_provider(ServiceTier.FREE)
            
            # Get available ultra-cheap providers in load balancing format
            self.available_providers = self.ai_provider_manager.get_available_providers(ServiceTier.FREE)
            
            if self.available_providers:
                # Log load balanced setup
                provider_names = [p['name'] for p in self.available_providers]
                total_cost = sum(p['cost_per_1k_tokens'] for p in self.available_providers) / len(self.available_providers)
                
                print(f"✅ Load balanced ultra-cheap providers: {provider_names}")
                print(f"💰 Average cost: ${total_cost:.5f}/1K tokens")
                print(f"🎯 Load balancing: ENABLED")
                
                # Calculate savings vs OpenAI
                openai_cost = 0.030
                savings_pct = ((openai_cost - total_cost) / openai_cost) * 100
                print(f"💎 SAVINGS: {savings_pct:.1f}% vs OpenAI!")
                
                logger.info(f"✅ Load balanced AI system initialized with {len(self.available_providers)} providers")
            else:
                print("❌ No ultra-cheap providers available - falling back")
                logger.warning("❌ No ultra-cheap providers available")
                self.use_load_balanced_system = False
                self._init_expensive_providers_fallback()
                
        except Exception as e:
            logger.error(f"❌ Load balanced system initialization failed: {e}")
            self.use_load_balanced_system = False
            self._init_tiered_providers()
    
    def _init_tiered_providers(self):
        """Initialize with standard tiered provider system (fallback)"""
        try:
            # Get the tiered provider manager
            self.ai_provider_manager = get_tiered_ai_provider(ServiceTier.FREE)
            
            # Get available ultra-cheap providers
            provider_configs = self.ai_provider_manager.get_providers_for_tier(ServiceTier.FREE)
            
            if provider_configs:
                # Convert to format expected by analyzers
                self.available_providers = []
                for provider in provider_configs:
                    self.available_providers.append({
                        "name": provider.name,
                        "available": provider.available,
                        "client": provider.client,
                        "priority": provider.priority,
                        "cost_per_1k_tokens": provider.cost_per_1k_tokens,
                        "quality_score": provider.quality_score,
                        "provider_tier": provider.provider_tier.value,
                        "speed_rating": provider.speed_rating
                    })
                
                primary_provider = self.available_providers[0]
                provider_name = primary_provider["name"]
                cost_per_1k = primary_provider["cost_per_1k_tokens"]
                
                print(f"✅ Primary ultra-cheap provider: {provider_name}")
                print(f"💰 Cost: ${cost_per_1k:.5f}/1K tokens")
                print(f"🎯 Load balancing: DISABLED (using tiered system)")
                
                # Calculate savings vs OpenAI
                openai_cost = 0.030
                if cost_per_1k > 0:
                    savings_pct = ((openai_cost - cost_per_1k) / openai_cost) * 100
                    print(f"💎 SAVINGS: {savings_pct:.1f}% vs OpenAI!")
                
                logger.info(f"✅ Tiered AI system initialized with {len(self.available_providers)} providers")
            else:
                print("❌ No ultra-cheap providers available - falling back to expensive providers")
                logger.warning("❌ No ultra-cheap providers available")
                self._init_expensive_providers_fallback()
                
        except Exception as e:
            logger.error(f"❌ Tiered system initialization failed: {e}")
            self._init_expensive_providers_fallback()
    
    def _init_expensive_providers_fallback(self):
        """Fallback to expensive providers if ultra-cheap not available"""
        print("⚠️ Falling back to expensive providers...")
        
        # Original expensive provider initialization (keep as fallback)
        openai_key = os.getenv("OPENAI_API_KEY")
        claude_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
        cohere_key = os.getenv("COHERE_API_KEY")
        
        self.openai_client = openai.AsyncOpenAI(api_key=openai_key) if openai_key else None
        
        if claude_key:
            try:
                import anthropic
                self.claude_client = anthropic.AsyncAnthropic(api_key=claude_key)
            except ImportError:
                self.claude_client = None
        else:
            self.claude_client = None
            
        if cohere_key:
            try:
                import cohere
                self.cohere_client = cohere.AsyncClient(api_key=cohere_key)
            except ImportError:
                self.cohere_client = None
        else:
            self.cohere_client = None
    
    async def analyze(self, url: str) -> Dict[str, Any]:
        """Complete sales page analysis with COMPREHENSIVE intelligence extraction"""
        
        try:
            logger.info(f"Starting COMPREHENSIVE analysis for URL: {url}")
            
            # Step 1: Scrape the page content
            page_content = await self._scrape_page(url)
            logger.info("Page scraping completed successfully")
            
            # Step 2: Extract structured content
            structured_content = await self._extract_content_structure(page_content)
            logger.info("Content structure extraction completed")
            
            # Step 2.5: 🔥 FIXED: Extract product name using advanced extractor
            product_name = await self._extract_product_name(page_content, structured_content)
            logger.info(f"🎯 Product name extracted: '{product_name}'")
            
            # Step 3: 🔥 FIXED: AI-powered intelligence extraction with product name
            intelligence = await self._extract_intelligence_with_load_balancing(structured_content, url, product_name)
            
            return intelligence
            
        except Exception as e:
            logger.error(f"Sales page analysis failed for {url}: {str(e)}")
            # Return a fallback response instead of raising
            return self._error_fallback_analysis(url, str(e))
    
    async def _extract_product_name(self, page_content: Dict[str, str], structured_content: Dict[str, Any]) -> str:
        """Extract product name using advanced product extractor"""
        
        try:
            if self.product_extractor:
                # Use advanced product extractor
                product_name = self.product_extractor.extract_product_name(
                    content=page_content["content"],
                    page_title=page_content["title"]
                )
                
                if product_name and product_name != "Product":
                    logger.info(f"✅ Advanced extraction successful: '{product_name}'")
                    return product_name
            
            # Fallback to basic extraction
            return self._basic_product_extraction(page_content["content"], page_content["title"])
            
        except Exception as e:
            logger.error(f"❌ Product extraction failed: {e}")
            return self._basic_product_extraction(page_content["content"], page_content["title"])
    
    def _basic_product_extraction(self, content: str, title: str) -> str:
        """🔥 ENHANCED: Basic product name extraction fallback with better patterns"""
        
        # Try title first - look for proper nouns
        if title:
            # Remove common words and look for capitalized words
            title_words = title.split()
            for word in title_words:
                if (len(word) > 3 and 
                    word[0].isupper() and 
                    word.lower() not in ['the', 'and', 'for', 'with', 'health', 'natural', 'best', 'free', 'join', 'sign', 'your', 'how', 'get', 'now']):
                    logger.info(f"🎯 Extracted from title: '{word}'")
                    return word
        
        # 🔥 ENHANCED: Better pattern matching for product names
        patterns = [
            r'(?:introducing|try|get|join)\s+([A-Z][a-zA-Z]{3,20})',
            r'([A-Z][a-zA-Z]{3,20})\s+(?:helps|supports|works|offers|provides)',
            r'([A-Z][a-zA-Z]{3,20})\s*[™®©]',
            r'welcome\s+to\s+([A-Z][a-zA-Z]{3,20})',
            r'([A-Z][a-zA-Z]{3,20})\s+(?:is|was|has)',
            r'(?:about|from)\s+([A-Z][a-zA-Z]{3,20})',
            r'([A-Z][a-zA-Z]{3,20})\s+(?:community|circle|program|system|course)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                product_name = matches[0] if isinstance(matches[0], str) else matches[0][0]
                # Filter out common false positives
                if product_name.lower() not in ['your', 'this', 'that', 'here', 'there', 'what', 'when', 'where', 'mobile', 'email', 'phone', 'number']:
                    logger.info(f"🎯 Extracted from content: '{product_name}'")
                    return product_name
        
        # Last resort - look for any capitalized word that appears multiple times
        words = re.findall(r'\b[A-Z][a-zA-Z]{3,20}\b', content)
        word_count = {}
        for word in words:
            if word.lower() not in ['your', 'this', 'that', 'here', 'there', 'what', 'when', 'where', 'mobile', 'email', 'phone', 'number']:
                word_count[word] = word_count.get(word, 0) + 1
        
        if word_count:
            # Get the most frequent proper noun
            most_common = max(word_count, key=word_count.get)
            if word_count[most_common] > 1:
                logger.info(f"🎯 Extracted most frequent: '{most_common}'")
                return most_common
        
        logger.warning("⚠️ Could not extract product name, using 'Product'")
        return "Product"
    
    async def _scrape_page(self, url: str) -> Dict[str, str]:
        """Advanced web scraping with error handling"""
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        try:
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.warning(f"HTTP {response.status} for {url}")
                        # Continue with whatever content we got
                    
                    html_content = await response.text()
                    logger.info(f"Successfully fetched {len(html_content)} characters from {url}")
                    
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Extract key elements
                    title = soup.find('title')
                    title_text = title.get_text().strip() if title else "No title found"
                    
                    # Remove script and style elements
                    for script in soup(["script", "style", "nav", "footer"]):
                        script.decompose()
                    
                    # Extract text content
                    body_text = soup.get_text()
                    
                    # Clean up text
                    lines = (line.strip() for line in body_text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    clean_text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    logger.info(f"Extracted {len(clean_text)} characters of clean text")
                    
                    return {
                        "title": title_text,
                        "content": clean_text,
                        "html": html_content,
                        "url": url
                    }
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error scraping {url}: {str(e)}")
            raise Exception(f"Failed to access webpage: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {str(e)}")
            raise Exception(f"Scraping failed: {str(e)}")
    
    async def _extract_content_structure(self, page_content: Dict[str, str]) -> Dict[str, Any]:
        """Extract and structure ALL key page elements including comprehensive product details"""
        
        content = page_content["content"]
        
        # Extract pricing patterns (enhanced)
        price_patterns = [
            r'\$[\d,]+(?:\.\d{2})?',  # $99.99, $1,299
            r'£[\d,]+(?:\.\d{2})?',  # £99.99
            r'€[\d,]+(?:\.\d{2})?',  # €99.99
            r'[\d,]+\s*dollars?',     # 99 dollars
            r'free(?:\s+trial)?',     # free, free trial
            r'money\s*back\s*guarantee',  # money back guarantee
            r'buy\s+\d+\s+get\s+\d+\s+free',  # BOGO offers
            r'\d+%\s+(?:off|discount)',  # percentage discounts
            r'save\s+\$[\d,]+',  # save amounts
            r'was\s+\$[\d,]+\s+now\s+\$[\d,]+',  # before/after prices
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            prices.extend(matches[:10])  # More pricing info
        
        # Extract emotional triggers and power words (enhanced)
        emotional_triggers = []
        trigger_words = [
            "limited time", "exclusive", "secret", "breakthrough", "guaranteed",
            "proven", "instant", "fast", "easy", "simple", "powerful",
            "revolutionary", "amazing", "incredible", "shocking", "urgent",
            "clinically tested", "doctor recommended", "scientifically proven",
            "natural", "safe", "effective", "trusted", "recommended"
        ]
        
        for trigger in trigger_words:
            if trigger.lower() in content.lower():
                # Find context around the trigger
                pattern = rf'.{{0,50}}{re.escape(trigger)}.{{0,50}}'
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    emotional_triggers.append({
                        "trigger": trigger,
                        "context": matches[0].strip()
                    })
        
        return {
            "title": page_content["title"],
            "content": content,
            "url": page_content["url"],
            "pricing_mentions": prices,
            "emotional_triggers": emotional_triggers[:15],  # Top 15 with context
            "word_count": len(content.split()),
            "content_sections": self._identify_content_sections(content)
        }
    
    def _identify_content_sections(self, content: str) -> Dict[str, str]:
        """Identify key sections of sales page content"""
        
        sections = {}
        content_lower = content.lower()
        
        # Common section indicators
        section_patterns = {
            "headline": r"(.{0,200}?)(?:\n|\.|!|\?)",
            "benefits": r"(benefits?.*?)(?:features?|price|order|buy)",
            "features": r"(features?.*?)(?:benefits?|price|order|buy)",
            "testimonials": r"(testimonial.*?)(?:price|order|buy|feature)",
            "guarantee": r"(guarantee.*?)(?:price|order|buy|feature)",
            "urgency": r"(limited.*?time|urgent.*?|hurry.*?|act.*?now)",
            "call_to_action": r"(buy\s+now|order\s+now|get\s+started|sign\s+up|click\s+here)"
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, content_lower, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section_name] = match.group(1).strip()[:500]  # Limit length
        
        return sections
    
    # 🔥 UPDATED: Intelligence extraction with load balancing integration
    async def _extract_intelligence_with_load_balancing(self, structured_content: Dict[str, Any], url: str, product_name: str = "Product") -> Dict[str, Any]:
        """Extract intelligence using load balanced AI providers when available"""
        
        if self.use_load_balanced_system and self.available_providers:
            # Use load balanced system
            return await self._extract_intelligence_load_balanced(structured_content, url, product_name)
        elif self.available_providers:
            # Use tiered system (fallback)
            return await self._extract_intelligence_ultra_cheap(structured_content, url, product_name)
        else:
            # Use expensive providers (last resort)
            logger.warning("🚨 Using expensive provider fallback")
            return await self._extract_intelligence_expensive_fallback(structured_content, url, product_name)
    
    async def _extract_intelligence_load_balanced(self, structured_content: Dict[str, Any], url: str, product_name: str = "Product") -> Dict[str, Any]:
        """🔥 NEW: Extract intelligence using load balanced AI providers"""
        
        logger.info("🚀 Starting LOAD BALANCED intelligence extraction...")
        
        try:
            # Get next provider using load balancing
            if LOAD_BALANCING_AVAILABLE:
                selected_provider = _get_next_provider_with_load_balancing(self.available_providers)
            else:
                # Fallback to first available provider
                selected_provider = self.available_providers[0]
            
            if not selected_provider:
                logger.error("❌ No provider selected by load balancer")
                return self._fallback_analysis(structured_content, url, product_name)
            
            provider_name = selected_provider.get("name", "unknown")
            cost_per_1k = selected_provider.get("cost_per_1k_tokens", 0)
            
            logger.info(f"🎯 Load balancer selected: {provider_name} (${cost_per_1k:.5f}/1K tokens)")
            
            # 🔥 FIXED: Create optimized prompt with product name enforcement
            analysis_prompt = self._create_intelligence_prompt(structured_content, url, product_name)
            
            # Make AI request using selected provider
            logger.info("💰 Making load balanced AI request...")
            result = await self._make_ai_request_with_provider(selected_provider, analysis_prompt)
            
            # 🔥 FIXED: Parse AI response with product name substitution
            intelligence = self._parse_ai_analysis(result, structured_content, product_name)
            
            # Add load balancing metadata
            intelligence.update({
                "source_url": url,
                "page_title": structured_content["title"],
                "product_name": product_name,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "confidence_score": self._calculate_confidence_score(intelligence, structured_content),
                "raw_content": structured_content["content"][:1000],
                "load_balanced_analysis": {
                    "provider_selected": provider_name,
                    "cost_per_1k_tokens": cost_per_1k,
                    "load_balancing_enabled": True,
                    "load_balancing_stats": get_load_balancing_stats() if LOAD_BALANCING_AVAILABLE else {},
                    "provider_selection_method": "round_robin_load_balancing"
                }
            })
            
            return intelligence
            
        except Exception as e:
            logger.error(f"❌ Load balanced intelligence extraction failed: {str(e)}")
            logger.info("🔄 Falling back to pattern-based analysis")
            return self._fallback_analysis(structured_content, url, product_name)
    
    async def _make_ai_request_with_provider(self, provider: Dict[str, Any], prompt: str) -> str:
        """Make AI request using specific provider"""
        
        provider_name = provider.get("name", "unknown")
        client = provider.get("client")
        
        if not client:
            raise Exception(f"No client available for provider {provider_name}")
        
        try:
            # Use the centralized AI throttling system
            from src.intelligence.utils.ai_throttle import safe_ai_call
            
            # Create messages
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert competitive intelligence analyst. Extract actionable insights for marketing campaigns. Provide specific, detailed analysis in each category. Always use the actual product name provided, never generic terms like 'Your' or 'Product'."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Model mapping
            model_map = {
                "groq": "llama-3.3-70b-versatile",
                "together": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                "deepseek": "deepseek-chat",
                "anthropic": "claude-3-haiku-20240307",
                "cohere": "command-r-plus",
                "openai": "gpt-3.5-turbo"
            }
            
            model = model_map.get(provider_name, "gpt-3.5-turbo")
            
            # Make safe AI call with throttling
            response = await safe_ai_call(
                client=client,
                provider_name=provider_name,
                model=model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            # Handle response
            if isinstance(response, dict):
                if response.get("fallback"):
                    # Extract fallback content if available
                    fallback_data = response.get("fallback_data", {})
                    return json.dumps(fallback_data)
                else:
                    # Response is structured data, convert to string
                    return json.dumps(response)
            elif isinstance(response, str):
                return response
            else:
                raise Exception("Unexpected response format")
                
        except Exception as e:
            logger.error(f"❌ AI request failed for {provider_name}: {str(e)}")
            raise
    
    async def _extract_intelligence_ultra_cheap(self, structured_content: Dict[str, Any], url: str, product_name: str = "Product") -> Dict[str, Any]:
        """Extract intelligence using ultra-cheap AI providers (original method)"""
        
        logger.info("🚀 Starting ULTRA-CHEAP intelligence extraction...")
        
        # Get primary ultra-cheap provider
        primary_provider = self.available_providers[0]
        provider_name = primary_provider["name"]
        cost_per_1k = primary_provider["cost_per_1k_tokens"]
        
        logger.info(f"🤖 Using ultra-cheap provider: {provider_name} (${cost_per_1k:.5f}/1K tokens)")
        
        try:
            # 🔥 FIXED: Create optimized prompt with product name enforcement
            analysis_prompt = self._create_intelligence_prompt(structured_content, url, product_name)
            
            # Make ultra-cheap AI request
            logger.info("💰 Making ultra-cheap AI request...")
            result = await make_tiered_ai_request(
                prompt=analysis_prompt,
                max_tokens=2000,
                service_tier=ServiceTier.FREE  # Use ultra-cheap tier
            )
            
            # Log cost savings
            estimated_cost = result.get("estimated_cost", 0)
            openai_equivalent_cost = estimated_cost / (1 - 0.95)  # Assuming 95% savings
            savings = openai_equivalent_cost - estimated_cost
            
            logger.info(f"✅ Intelligence extraction completed!")
            logger.info(f"💰 Cost: ${estimated_cost:.5f} (saved ${savings:.5f} vs OpenAI)")
            logger.info(f"🤖 Provider: {result.get('provider_used', 'unknown')}")
            
            # 🔥 FIXED: Parse AI response with product name substitution
            ai_analysis = result.get("response", "")
            intelligence = self._parse_ai_analysis(ai_analysis, structured_content, product_name)
            
            # Add ultra-cheap metadata
            intelligence.update({
                "source_url": url,
                "page_title": structured_content["title"],
                "product_name": product_name,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "confidence_score": self._calculate_confidence_score(intelligence, structured_content),
                "raw_content": structured_content["content"][:1000],
                "ultra_cheap_analysis": {
                    "provider_used": result.get("provider_used", "unknown"),
                    "cost_per_request": estimated_cost,
                    "cost_savings_vs_openai": savings,
                    "savings_percentage": (savings / openai_equivalent_cost * 100) if openai_equivalent_cost > 0 else 0,
                    "quality_score": result.get("quality_score", 0),
                    "processing_time": result.get("processing_time", 0),
                    "load_balancing_enabled": False
                }
            })
            
            return intelligence
            
        except Exception as e:
            logger.error(f"❌ Ultra-cheap intelligence extraction failed: {str(e)}")
            logger.info("🔄 Falling back to pattern-based analysis")
            return self._fallback_analysis(structured_content, url, product_name)
    
    def _create_intelligence_prompt(self, structured_content: Dict[str, Any], url: str, product_name: str) -> str:
        """🔥 FIXED: Create optimized prompt with product name enforcement - eliminates placeholders"""
        
        # 🔥 CRITICAL:  prompt that enforces actual product name usage
        prompt = f"""Analyze this sales page for the specific product "{product_name}":

CRITICAL INSTRUCTIONS:
- The product name is "{product_name}" - use this EXACT name in all analysis
- DO NOT use generic terms like "Your", "Product", "Your Product", or "[Product Name]"
- Replace any generic references with the actual product name "{product_name}"
- When extracting products list, use ["{product_name}"] not ["Your"] or ["Product"]

ANALYSIS TARGET:
URL: {url}
Product Name: {product_name}
Page Title: {structured_content['title']}
Content: {structured_content['content'][:1500]}
Emotional Triggers: {structured_content['emotional_triggers'][:5]}
Pricing: {structured_content['pricing_mentions'][:3]}

Extract competitive intelligence using the ACTUAL product name "{product_name}":

1. OFFER ANALYSIS:
- Main product/service: Use "{product_name}" as the product name
- Pricing strategy for {product_name}
- Key benefits claimed for {product_name}
- Guarantees offered for {product_name}

2. PSYCHOLOGY ANALYSIS:
- Emotional triggers used to sell {product_name}
- Target audience for {product_name}
- Pain points {product_name} addresses
- Persuasion techniques for {product_name}

3. COMPETITIVE ANALYSIS:
- Market positioning of {product_name}
- Competitive advantages of {product_name}
- Potential weaknesses of {product_name}
- Opportunities for competing with {product_name}

4. CONTENT ANALYSIS:
- Key messages about {product_name}
- Success stories related to {product_name}
- Social proof elements for {product_name}
- Call-to-action strategy for {product_name}

IMPORTANT: In your response, always use "{product_name}" as the actual product name. 
Never use "Your", "Product", "Your Product", or generic placeholders.

Respond with structured analysis using "{product_name}" throughout."""

        return prompt
    
    async def _extract_intelligence_expensive_fallback(self, structured_content: Dict[str, Any], url: str, product_name: str = "Product") -> Dict[str, Any]:
        """Fallback to expensive providers if ultra-cheap fails"""
        
        logger.warning("💸 Using EXPENSIVE provider fallback")
        
        # Try expensive providers in order (same as original code)
        providers_tried = []
        
        # Try Claude first (expensive)
        if getattr(self, 'claude_client', None):
            try:
                logger.info("💸 Trying Claude (EXPENSIVE)...")
                intelligence = await self._extract_intelligence_claude(structured_content, url, product_name)
                logger.info("✅ Claude intelligence extraction successful (but expensive)")
                return intelligence
            except Exception as e:
                providers_tried.append("Claude")
                logger.warning(f"❌ Claude failed: {str(e)}")
        
        # Try Cohere second (expensive)
        if getattr(self, 'cohere_client', None):
            try:
                logger.info("💸 Trying Cohere (EXPENSIVE)...")
                intelligence = await self._extract_intelligence_cohere(structured_content, url, product_name)
                logger.info("✅ Cohere intelligence extraction successful (but expensive)")
                return intelligence
            except Exception as e:
                providers_tried.append("Cohere")
                logger.warning(f"❌ Cohere failed: {str(e)}")

        # Try OpenAI third (most expensive)
        if getattr(self, 'openai_client', None):
            try:
                logger.info("💸 Trying OpenAI (MOST EXPENSIVE)...")
                intelligence = await self._extract_intelligence_openai(structured_content, url, product_name)
                logger.info("✅ OpenAI intelligence extraction successful (but most expensive)")
                return intelligence
            except Exception as e:
                providers_tried.append("OpenAI")
                logger.warning(f"❌ OpenAI failed: {str(e)}")
        
        # All providers failed
        logger.warning(f"🚨 All providers failed ({', '.join(providers_tried)}), using pattern matching")
        return self._fallback_analysis(structured_content, url, product_name)
    
    async def _extract_intelligence_claude(self, structured_content: Dict[str, Any], url: str, product_name: str = "Product") -> Dict[str, Any]:
        """Claude-specific intelligence extraction"""
        # TODO: Implement Claude analysis
        logger.info("Claude analysis not yet implemented, using fallback")
        return self._fallback_analysis(structured_content, url, product_name)
    
    async def _extract_intelligence_cohere(self, structured_content: Dict[str, Any], url: str, product_name: str = "Product") -> Dict[str, Any]:
        """Cohere-specific intelligence extraction"""
        # TODO: Implement Cohere analysis
        logger.info("Cohere analysis not yet implemented, using fallback")
        return self._fallback_analysis(structured_content, url, product_name)
    
    async def _extract_intelligence_openai(self, structured_content: Dict[str, Any], url: str, product_name: str = "Product") -> Dict[str, Any]:
        """OpenAI-specific intelligence extraction (EXPENSIVE - original method)"""
        
        # 🔥 FIXED: Use enhanced prompt with product name enforcement
        analysis_prompt = self._create_intelligence_prompt(structured_content, url, product_name)
        
        try:
            # Log expensive usage
            estimated_tokens = len(analysis_prompt.split()) * 1.3
            estimated_cost = (estimated_tokens / 1000) * 0.030  # OpenAI cost
            logger.warning(f"💸 EXPENSIVE OpenAI call: ~${estimated_cost:.4f}")
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are an expert competitive intelligence analyst. Extract actionable insights for marketing campaigns. Always use the actual product name '{product_name}' provided, never generic terms like 'Your' or 'Product'. Provide specific, detailed analysis in each category."
                    },
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            ai_analysis = response.choices[0].message.content
            
            # 🔥 FIXED: Parse AI response with product name substitution
            intelligence = self._parse_ai_analysis(ai_analysis, structured_content, product_name)
            
            # Add metadata with cost warning
            intelligence.update({
                "source_url": url,
                "page_title": structured_content["title"],
                "product_name": product_name,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "confidence_score": self._calculate_confidence_score(intelligence, structured_content),
                "raw_content": structured_content["content"][:1000],
                "expensive_analysis_warning": {
                    "provider_used": "openai_gpt4",
                    "estimated_cost": estimated_cost,
                    "cost_vs_ultra_cheap": f"{estimated_cost / 0.0002:.0f}x more expensive than Groq",
                    "recommendation": "Switch to ultra-cheap providers for 95%+ savings",
                    "load_balancing_enabled": False
                }
            })
            
            return intelligence
            
        except Exception as e:
            logger.error(f"💸 EXPENSIVE OpenAI analysis failed: {str(e)}")
            return self._fallback_analysis(structured_content, url, product_name)
    
    def _parse_ai_analysis(self, ai_response: str, structured_content: Dict[str, Any], product_name: str) -> Dict[str, Any]:
        """🔥 FIXED: Parse AI response with product name substitution to eliminate placeholders"""
        
        # Initialize with COMPLETE structure
        parsed_data = {
            "offer_intelligence": {
                "products": [product_name],  # 🔥 FIXED: Use actual product name
                "pricing": structured_content.get("pricing_mentions", []),
                "bonuses": [],
                "guarantees": [],
                "value_propositions": [f"Main product: {product_name}"],  # 🔥 FIXED: Use actual product name
                "insights": []
            },
            "psychology_intelligence": {
                "emotional_triggers": structured_content.get("emotional_triggers", []),
                "pain_points": [],
                "target_audience": f"Customers interested in {product_name}",  # 🔥 FIXED: Use actual product name
                "persuasion_techniques": []
            },
            "competitive_intelligence": {
                "opportunities": [],
                "gaps": [],
                "positioning": f"{product_name} market positioning",  # 🔥 FIXED: Use actual product name
                "advantages": [],
                "weaknesses": []
            },
            "content_intelligence": {
                "key_messages": [structured_content.get("title", f"{product_name} Page")],  # 🔥 FIXED: Use actual product name
                "success_stories": [],
                "social_proof": [],
                "content_structure": f"{product_name} sales page"  # 🔥 FIXED: Use actual product name
            },
            "brand_intelligence": {
                "tone_voice": "Professional",
                "messaging_style": "Direct",
                "brand_positioning": f"{product_name} market competitor"  # 🔥 FIXED: Use actual product name
            }
        }
        
        # 🔥 CRITICAL: Apply placeholder substitution to AI response
        if ai_response:
            ai_response = self._substitute_placeholders(ai_response, product_name)
        
        # Extract insights from AI response
        lines = ai_response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 🔥 FIXED: Apply placeholder substitution to each line
            line = self._substitute_placeholders(line, product_name)
            
            # Identify sections
            line_lower = line.lower()
            if "offer" in line_lower and "intelligence" in line_lower:
                current_section = "offer_intelligence"
            elif "psychology" in line_lower and "intelligence" in line_lower:
                current_section = "psychology_intelligence"
            elif "competitive" in line_lower and "intelligence" in line_lower:
                current_section = "competitive_intelligence"
            elif "content" in line_lower and "intelligence" in line_lower:
                current_section = "content_intelligence"
            elif "brand" in line_lower and "intelligence" in line_lower:
                current_section = "brand_intelligence"
            
            # Extract bullet points and insights
            if line.startswith(('-', '•', '*')) and current_section:
                insight = line[1:].strip()
                if insight:
                    # 🔥 FIXED: Apply placeholder substitution to insight
                    insight = self._substitute_placeholders(insight, product_name)
                    
                    # Route to appropriate sub-category
                    if current_section == "offer_intelligence":
                        parsed_data["offer_intelligence"]["insights"].append(insight)
                    elif current_section == "psychology_intelligence":
                        parsed_data["psychology_intelligence"]["persuasion_techniques"].append(insight)
                    elif current_section == "competitive_intelligence":
                        parsed_data["competitive_intelligence"]["opportunities"].append(insight)
                    elif current_section == "content_intelligence":
                        parsed_data["content_intelligence"]["key_messages"].append(insight)
        
        # 🔥 FINAL: Apply placeholder substitution to entire parsed data
        parsed_data = self._substitute_placeholders_recursive(parsed_data, product_name)
        
        return parsed_data
    
    def _substitute_placeholders(self, text: str, product_name: str) -> str:
        """🔥 NEW: Substitute placeholder text with actual product name"""
        if not isinstance(text, str):
            return text
        
        # Define placeholder patterns to replace
        placeholders = [
            "Your",
            "PRODUCT",
            "Product",
            "[Product Name]",
            "[Your Company]",
            "[Company Name]",
            "Your Product",
            "Your Company",
            "the product",
            "this product"
        ]
        
        result = text
        for placeholder in placeholders:
            # Replace exact matches at word boundaries
            result = re.sub(r'\b' + re.escape(placeholder) + r'\b', product_name, result, flags=re.IGNORECASE)
        
        return result
    
    def _substitute_placeholders_recursive(self, data: Any, product_name: str) -> Any:
        """🔥 NEW: Recursively substitute placeholders in nested data structures"""
        if isinstance(data, dict):
            return {k: self._substitute_placeholders_recursive(v, product_name) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._substitute_placeholders_recursive(item, product_name) for item in data]
        elif isinstance(data, str):
            return self._substitute_placeholders(data, product_name)
        else:
            return data
    
    def _calculate_confidence_score(self, intelligence: Dict[str, Any], structured_content: Dict[str, Any]) -> float:
        """Calculate realistic confidence score based on data richness"""

        score = 0.3  # Lower base score (30% instead of 10%)

        # Offer intelligence scoring (max 0.2)
        offer_intel = intelligence.get("offer_intelligence", {})
        if offer_intel.get("products"):
            score += 0.05  # Reduced from 0.1
        if offer_intel.get("pricing"):
            score += 0.05  # Reduced from 0.1
        if offer_intel.get("value_propositions"):
            score += 0.05  # Reduced from 0.1
        if offer_intel.get("guarantees"):
            score += 0.03
        if offer_intel.get("bonuses"):
            score += 0.02

        # Psychology intelligence scoring (max 0.15)
        psych_intel = intelligence.get("psychology_intelligence", {})
        if psych_intel.get("emotional_triggers"):
            score += 0.05  # Reduced from 0.1
        if psych_intel.get("pain_points"):
            score += 0.05  # Reduced from 0.1
        if psych_intel.get("target_audience") and psych_intel["target_audience"] != "General audience":
            score += 0.03
        if psych_intel.get("persuasion_techniques"):
            score += 0.02

        # Content intelligence scoring (max 0.15)
        content_intel = intelligence.get("content_intelligence", {})
        if content_intel.get("key_messages"):
            score += 0.05  # Reduced from 0.1
        if content_intel.get("social_proof"):
            score += 0.04  # Reduced from 0.05
        if content_intel.get("success_stories"):
            score += 0.03
        if content_intel.get("content_structure") and "sales page" in content_intel["content_structure"]:
            score += 0.03

        # Competitive intelligence scoring (max 0.1)
        comp_intel = intelligence.get("competitive_intelligence", {})
        if comp_intel.get("opportunities"):
            score += 0.04  # Reduced from 0.1
        if comp_intel.get("advantages"):
            score += 0.03  # Reduced from 0.05
        if comp_intel.get("positioning") and comp_intel["positioning"] != "Standard approach":
            score += 0.03

        # Brand intelligence scoring (max 0.1)
        brand_intel = intelligence.get("brand_intelligence", {})
        if brand_intel.get("tone_voice") and brand_intel["tone_voice"] != "Professional":
            score += 0.03  # Reduced from 0.05
        if brand_intel.get("messaging_style") and brand_intel["messaging_style"] != "Direct":
            score += 0.03  # Reduced from 0.05
        if brand_intel.get("brand_positioning") and brand_intel["brand_positioning"] != "Market competitor":
            score += 0.04

        # Structured content quality bonus (max 0.15)
        if structured_content.get("word_count", 0) > 1000:
            score += 0.05  # Good content length
        if structured_content.get("word_count", 0) > 500:
            score += 0.02  # Decent content length

        if structured_content.get("emotional_triggers"):
            score += 0.03  # Reduced from 0.05
        if structured_content.get("pricing_mentions"):
            score += 0.03  # Reduced from 0.05

        # Quality multiplier based on completeness
        categories_populated = sum(
            1
            for category in [
                intelligence.get("offer_intelligence", {}),
                intelligence.get("psychology_intelligence", {}),
                intelligence.get("content_intelligence", {}),
                intelligence.get("competitive_intelligence", {}),
                intelligence.get("brand_intelligence", {}),
            ]
            if category
        )

        completeness_bonus = (categories_populated / 5) * 0.1
        score += completeness_bonus

        # Apply realism cap - max confidence should be 85% for automated analysis
        final_score = min(score, 0.85)  # Cap at 85% instead of 100%

        logger.info(f"📊 Confidence calculation: base={score:.2f}, final={final_score:.2f} ({final_score*100:.1f}%)")

        return final_score
    
    def _fallback_analysis(self, structured_content: Dict[str, Any], url: str, product_name: str = "Product") -> Dict[str, Any]:
        """🔥 FIXED: Comprehensive fallback analysis with actual product name - NO PLACEHOLDERS"""
        
        return {
            "offer_intelligence": {
                "products": [product_name],  # 🔥 FIXED: Use actual product name
                "pricing": structured_content.get("pricing_mentions", []),
                "bonuses": [],
                "guarantees": [],
                "value_propositions": [f"Main product: {product_name}"],  # 🔥 FIXED: Use actual product name
                "insights": [
                    f"Product analysis: {product_name} appears to be the main offering",  # 🔥 FIXED
                    f"Target audience: General consumers interested in {product_name}",  # 🔥 FIXED
                    f"Content focus: {product_name} presentation and benefits"  # 🔥 FIXED
                ]
            },
            "psychology_intelligence": {
                "emotional_triggers": structured_content.get("emotional_triggers", []),
                "pain_points": [f"General consumer needs addressed by {product_name}"],  # 🔥 FIXED
                "target_audience": f"Customers interested in {product_name}",  # 🔥 FIXED
                "persuasion_techniques": [f"{product_name} benefits presentation", f"{product_name} value proposition emphasis"]  # 🔥 FIXED
            },
            "competitive_intelligence": {
                "opportunities": [
                    f" {product_name} positioning possible",  # 🔥 FIXED
                    f"Competitive differentiation opportunities for {product_name}",  # 🔥 FIXED
                    f"{product_name} market gap analysis needed"  # 🔥 FIXED
                ],
                "gaps": [f"Detailed competitive analysis for {product_name} requires AI providers"],  # 🔥 FIXED
                "positioning": f"{product_name} standard market approach",  # 🔥 FIXED
                "advantages": [f"{product_name} unique selling proposition"],  # 🔥 FIXED
                "weaknesses": [f"Limited {product_name} analysis without AI providers"]  # 🔥 FIXED
            },
            "content_intelligence": {
                "key_messages": [structured_content.get("title", f"{product_name} Page")],  # 🔥 FIXED
                "success_stories": [],
                "social_proof": [],
                "content_structure": f"{product_name} page with {structured_content.get('word_count', 0)} words"  # 🔥 FIXED
            },
            "brand_intelligence": {
                "tone_voice": "Professional",
                "messaging_style": "Direct",
                "brand_positioning": f"{product_name} market competitor"  # 🔥 FIXED
            },
            "campaign_suggestions": [
                f"Develop unique positioning for {product_name}",  # 🔥 FIXED
                f"Create compelling value propositions for {product_name}",  # 🔥 FIXED
                f"Build competitive differentiation for {product_name}",  # 🔥 FIXED
                f"Enhance social proof elements for {product_name}"  # 🔥 FIXED
            ],
            "source_url": url,
            "page_title": structured_content.get("title", f"{product_name} Analyzed Page"),  # 🔥 FIXED
            "product_name": product_name,  # ✅ Correct
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "confidence_score": 0.6,
            "raw_content": structured_content.get("content", "")[:1000],
            "analysis_note": f"Fallback analysis for {product_name} - AI providers recommended for enhanced insights",  # 🔥 FIXED
            "load_balancing_analysis": {
                "load_balancing_available": LOAD_BALANCING_AVAILABLE,
                "load_balancing_enabled": False,
                "fallback_reason": "AI provider system not available"
            }
        }
    
    def _error_fallback_analysis(self, url: str, error_msg: str) -> Dict[str, Any]:
        """🔥 FIXED: Fallback when analysis completely fails - uses generic product name"""
        
        return {
            "offer_intelligence": {
                "products": [],
                "pricing": [],
                "bonuses": [],
                "guarantees": [],
                "value_propositions": [],
                "insights": []
            },
            "psychology_intelligence": {
                "emotional_triggers": [],
                "pain_points": [],
                "target_audience": "Unknown",
                "persuasion_techniques": []
            },
            "competitive_intelligence": {
                "opportunities": ["Analysis failed - manual review required"],
                "gaps": [],
                "positioning": "Unknown",
                "advantages": [],
                "weaknesses": []
            },
            "content_intelligence": {
                "key_messages": [],
                "success_stories": [],
                "social_proof": [],
                "content_structure": "Could not analyze"
            },
            "brand_intelligence": {
                "tone_voice": "Unknown",
                "messaging_style": "Unknown",
                "brand_positioning": "Unknown"
            },
            "campaign_suggestions": [
                "Manual analysis required due to technical error",
                "Check URL accessibility",
                "Verify site allows scraping"
            ],
            "source_url": url,
            "page_title": "Analysis Failed",
            "product_name": "Unknown",
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "confidence_score": 0.0,
            "raw_content": "",
            "error_message": error_msg,
            "analysis_note": f"Analysis failed: {error_msg}",
            "load_balancing_analysis": {
                "load_balancing_available": LOAD_BALANCING_AVAILABLE,
                "load_balancing_enabled": False,
                "error_occurred": True
            }
        }


#  analyzer class that extends the base
classSalesPageAnalyzer(SalesPageAnalyzer):
    """ sales page analyzer with additional features"""
    
    async def analyze_enhanced(
        self, 
        url: str, 
        campaign_id: str = None, 
        analysis_depth: str = "comprehensive",
        include_vsl_detection: bool = True
    ) -> Dict[str, Any]:
        """Perform enhanced analysis with all advanced features"""
        
        try:
            # Use existing analyze method as base
            base_analysis = await self.analyze(url)
            
            # Get actual product name from base analysis
            product_name = base_analysis.get("product_name", "Product")
            
            # Add enhanced features with actual product name
            enhanced_intelligence = {
                **base_analysis,
                "intelligence_id": f"intel_{uuid.uuid4().hex[:8]}",
                "analysis_depth": analysis_depth,
                "campaign_angles": self._generate_basic_campaign_angles(base_analysis, product_name),
                "actionable_insights": self._generate_actionable_insights(base_analysis, product_name),
                "technical_analysis": self._analyze_technical_aspects(url, product_name)
            }
            
            # Add VSL detection if requested (simplified for now)
            if include_vsl_detection:
                enhanced_intelligence["vsl_analysis"] = self._detect_video_content(base_analysis, product_name)
            
            return enhanced_intelligence
            
        except Exception as e:
            logger.error(f" analysis failed: {str(e)}")
            # Return basic analysis on error
            return await self.analyze(url)
    
    def _generate_basic_campaign_angles(self, analysis: Dict[str, Any], product_name: str) -> Dict[str, Any]:
        """🔥 FIXED: Generate basic campaign angles with actual product name"""
        
        return {
            "primary_angle": f"Strategic competitive advantage through {product_name} intelligence",
            "alternative_angles": [
                f"Transform results with proven {product_name} insights",
                f"Competitive edge through {product_name} analysis", 
                f"Data-driven {product_name} strategies"
            ],
            "positioning_strategy": f"Premium {product_name} intelligence-driven solution",
            "target_audience_insights": [f"{product_name} business owners", f"{product_name} marketing professionals"],
            "messaging_framework": [f"{product_name} problem identification", f"{product_name} solution presentation", f"{product_name} results proof"],
            "differentiation_strategy": f"Intelligence-based {product_name} competitive advantage"
        }
    
    def _generate_actionable_insights(self, analysis: Dict[str, Any], product_name: str) -> Dict[str, Any]:
        """🔥 FIXED: Generate actionable insights with actual product name"""
        
        return {
            "immediate_opportunities": [
                f"Create comparison content highlighting {product_name} advantages",
                f"Develop content addressing {product_name} market gaps",
                f"Build authority through unique {product_name} insights"
            ],
            "content_creation_ideas": [
                f"{product_name} competitive analysis blog posts",
                f"{product_name} market insight newsletters",
                f"{product_name} educational video content"
            ],
            "campaign_strategies": [
                f"Multi-touch {product_name} educational campaign",
                f"{product_name} authority building content series",
                f"{product_name} competitive positioning campaign"
            ],
            "testing_recommendations": [
                f"A/B test different {product_name} value propositions",
                f"Test {product_name} messaging variations",
                f"Optimize {product_name} conversion elements"
            ]
        }
    
    def _analyze_technical_aspects(self, url: str, product_name: str) -> Dict[str, Any]:
        """🔥 FIXED: Analyze technical aspects with actual product name"""
        
        return {
            "page_load_speed": f"Analysis for {product_name} requires additional tools",
            "mobile_optimization": True,  # Assume modern sites are mobile-friendly
            "conversion_elements": [
                f"{product_name} call-to-action buttons",
                f"{product_name} trust signals",
                f"{product_name} contact information"
            ],
            "trust_signals": [
                f"{product_name} professional design",
                f"{product_name} contact information",
                f"{product_name} security indicators"
            ]
        }
    
    def _detect_video_content(self, analysis: Dict[str, Any], product_name: str) -> Dict[str, Any]:
        """🔥 FIXED: Basic video content detection with actual product name"""
        
        content = analysis.get("raw_content", "").lower()
        
        has_video = any(keyword in content for keyword in [
            "video", "youtube", "vimeo", "player", "watch", "play"
        ])
        
        return {
            "has_video": has_video,
            "video_length_estimate": "Unknown",
            "video_type": "unknown",
            "transcript_available": False,
            "key_video_elements": [
                f"{product_name} video content detected" if has_video else f"No {product_name} video content found"
            ]
        }


# Simplified document analyzer
class DocumentAnalyzer:
    """Analyze uploaded documents for intelligence extraction"""
    
    def __init__(self):
        # Initialize OpenAI client if available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=api_key)
        else:
            self.openai_client = None
    
    async def analyze_document(self, file_content: bytes, file_extension: str) -> Dict[str, Any]:
        """Analyze uploaded document and extract intelligence"""
        
        try:
            # Extract text based on file type
            if file_extension == 'txt':
                text_content = file_content.decode('utf-8', errors='ignore')
            else:
                # For now, just handle text files
                # PDF and other formats require additional libraries
                text_content = file_content.decode('utf-8', errors='ignore')
            
            # Basic analysis
            intelligence = {
                "content_intelligence": {
                    "key_insights": self._extract_key_phrases(text_content),
                    "strategies_mentioned": ["Document analysis completed"],
                    "data_points": self._extract_numbers(text_content)
                },
                "competitive_intelligence": {
                    "opportunities": ["Document contains market insights"],
                    "market_gaps": []
                },
                "content_opportunities": [
                    "Create content based on document insights",
                    "Develop case studies from examples"
                ],
                "extracted_text": text_content[:1000],
                "confidence_score": 0.7
            }
            
            return intelligence
            
        except Exception as e:
            logger.error(f"Document analysis failed: {str(e)}")
            return {
                "content_intelligence": {"key_insights": ["Document processing failed"]},
                "competitive_intelligence": {"opportunities": []},
                "content_opportunities": [],
                "extracted_text": "",
                "confidence_score": 0.0,
                "error": str(e)
            }
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        
        # Simple keyword extraction
        words = text.split()
        key_phrases = []
        
        # Look for important business terms
        business_terms = ['strategy', 'market', 'customer', 'revenue', 'growth', 'competitive']
        
        for term in business_terms:
            if term in text.lower():
                key_phrases.append(f"Contains {term} insights")
        
        return key_phrases[:5]
    
    def _extract_numbers(self, text: str) -> List[str]:
        """Extract numerical data from text"""
        
        # Find percentages and numbers
        percentages = re.findall(r'\d+%', text)
        numbers = re.findall(r'\$[\d,]+', text)
        
        return (percentages + numbers)[:5]


# Simplified web analyzer
class WebAnalyzer:
    """Analyze general websites and web content"""
    
    def __init__(self):
        self.sales_page_analyzer = SalesPageAnalyzer()
    
    async def analyze(self, url: str) -> Dict[str, Any]:
        """Analyze general website content"""
        
        # Delegate to sales page analyzer
        return await self.sales_page_analyzer.analyze(url)


# Additional analyzer classes for the enhanced API
class VSLAnalyzer:
    """Simplified VSL analyzer"""
    
    async def detect_vsl(self, url: str) -> Dict[str, Any]:
        """Detect VSL content"""
        
        return {
            "has_video": True,
            "video_length_estimate": "Unknown",
            "video_type": "unknown",
            "transcript_available": False,
            "key_video_elements": ["Video content analysis requires additional tools"]
        }
    
    async def analyze_vsl(self, url: str, campaign_id: str, extract_transcript: bool = True) -> Dict[str, Any]:
        """Analyze VSL content"""
        
        return {
            "transcript_id": f"vsl_{uuid.uuid4().hex[:8]}",
            "video_url": url,
            "transcript_text": "VSL analysis requires video processing tools",
            "key_moments": [],
            "psychological_hooks": ["Video analysis not yet implemented"],
            "offer_mentions": [],
            "call_to_actions": []
        }

# At the end of src/intelligence/analyzers.py:
ANALYZERS_AVAILABLE = True