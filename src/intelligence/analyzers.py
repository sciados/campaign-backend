# src/intelligence/analyzers.py - PRODUCTION VERSION
"""
Production Intelligence Analysis - Best Possible Implementation
🚀 OPTIMAL: Full web scraping, comprehensive extraction, enterprise-grade reliability
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
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Initialize logger
logger = logging.getLogger(__name__)

# Import product extractor with proper error handling
try:
    from src.intelligence.extractors.product_extractor import ProductNameExtractor, extract_product_name
    PRODUCT_EXTRACTOR_AVAILABLE = True
    logger.info("✅ Product extractor imported successfully")
except ImportError as e:
    PRODUCT_EXTRACTOR_AVAILABLE = False
    logger.warning(f"⚠️ Product extractor import failed: {e}")

class ProductionSalesPageAnalyzer:
    """Production-grade sales page analyzer with enterprise capabilities"""
    
    def __init__(self):
        # Initialize AI client
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=api_key)
        else:
            self.openai_client = None
            logger.warning("OpenAI API key not found")
        
        # Initialize product extractor
        if PRODUCT_EXTRACTOR_AVAILABLE:
            self.product_extractor = ProductNameExtractor()
        else:
            self.product_extractor = None
        
        # Configure session with retry strategy
        self.session = self._create_robust_session()
    
    def _create_robust_session(self) -> requests.Session:
        """Create a robust HTTP session with retry logic"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return session
    
    async def analyze(self, url: str) -> Dict[str, Any]:
        """Production analysis with comprehensive extraction"""
        
        try:
            logger.info(f"🎯 Starting PRODUCTION analysis for: {url}")
            
            # Step 1: Advanced web scraping
            page_content = await self._advanced_scrape_page(url)
            logger.info("✅ Advanced page scraping completed")
            
            # Step 2: Comprehensive content extraction
            structured_content = await self._comprehensive_content_extraction(page_content)
            logger.info("✅ Comprehensive content extraction completed")
            
            # Step 3: Advanced product name extraction
            product_name = await self._advanced_product_extraction(page_content, structured_content)
            logger.info(f"🎯 PRODUCTION: Product name extracted: '{product_name}'")
            
            # Step 4: Multi-layered intelligence extraction
            if self.openai_client:
                intelligence = await self._ai_powered_intelligence_extraction(
                    structured_content, url, product_name
                )
                logger.info("✅ AI-powered intelligence extraction completed")
            else:
                intelligence = self._comprehensive_fallback_analysis(
                    structured_content, url, product_name
                )
                logger.info("✅ Comprehensive fallback analysis completed")
            
            # Step 5: Quality validation and scoring
            intelligence = self._validate_and_score_intelligence(intelligence, structured_content)
            
            return intelligence
            
        except Exception as e:
            logger.error(f"❌ Production analysis failed for {url}: {str(e)}")
            return self._enterprise_error_fallback(url, str(e))
    
    async def _advanced_scrape_page(self, url: str) -> Dict[str, str]:
        """Advanced web scraping with multiple fallback strategies"""
        
        # Strategy 1: Async aiohttp (fastest)
        try:
            return await self._aiohttp_scrape(url)
        except Exception as e:
            logger.warning(f"aiohttp scraping failed: {e}, trying requests")
        
        # Strategy 2: Synchronous requests with retry
        try:
            return await self._requests_scrape(url)
        except Exception as e:
            logger.warning(f"requests scraping failed: {e}, trying basic urllib")
        
        # Strategy 3: Basic urllib fallback
        try:
            return await self._urllib_scrape(url)
        except Exception as e:
            logger.error(f"All scraping strategies failed: {e}")
            raise Exception(f"Could not access {url}: {e}")
    
    async def _aiohttp_scrape(self, url: str) -> Dict[str, str]:
        """High-performance async scraping with aiohttp"""
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(url, allow_redirects=True) as response:
                if response.status not in [200, 201]:
                    logger.warning(f"HTTP {response.status} for {url}")
                
                html_content = await response.text(encoding='utf-8', errors='ignore')
                logger.info(f"aiohttp: Fetched {len(html_content)} characters")
                
                return self._parse_html_content(html_content, url)
    
    async def _requests_scrape(self, url: str) -> Dict[str, str]:
        """Robust scraping with requests library"""
        
        response = self.session.get(url, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        # Handle encoding properly
        if response.encoding is None:
            response.encoding = 'utf-8'
        
        html_content = response.text
        logger.info(f"requests: Fetched {len(html_content)} characters")
        
        return self._parse_html_content(html_content, url)
    
    async def _urllib_scrape(self, url: str) -> Dict[str, str]:
        """Basic fallback scraping with urllib"""
        
        import urllib.request
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; AnalyzerBot/1.0)'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            logger.info(f"urllib: Fetched {len(html_content)} characters")
            
            return self._parse_html_content(html_content, url)
    
    def _parse_html_content(self, html_content: str, url: str) -> Dict[str, str]:
        """Advanced HTML parsing with multiple parser strategies"""
        
        # Strategy 1: BeautifulSoup with lxml (fastest, most accurate)
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            return self._extract_with_beautifulsoup(soup, html_content, url)
        except Exception as e:
            logger.warning(f"lxml parsing failed: {e}, trying html.parser")
        
        # Strategy 2: BeautifulSoup with html.parser (built-in, reliable)
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return self._extract_with_beautifulsoup(soup, html_content, url)
        except Exception as e:
            logger.warning(f"html.parser failed: {e}, trying html5lib")
        
        # Strategy 3: BeautifulSoup with html5lib (most forgiving)
        try:
            soup = BeautifulSoup(html_content, 'html5lib')
            return self._extract_with_beautifulsoup(soup, html_content, url)
        except Exception as e:
            logger.warning(f"html5lib failed: {e}, using regex fallback")
        
        # Strategy 4: Regex-based extraction (last resort)
        return self._extract_with_regex(html_content, url)
    
    def _extract_with_beautifulsoup(self, soup: BeautifulSoup, html_content: str, url: str) -> Dict[str, str]:
        """Professional content extraction with BeautifulSoup"""
        
        # Extract title with multiple fallbacks
        title = None
        for selector in ['title', 'h1', '.title', '#title', '[data-title]']:
            try:
                element = soup.select_one(selector)
                if element and element.get_text().strip():
                    title = element.get_text().strip()
                    break
            except:
                continue
        
        if not title:
            title = "Page Title"
        
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", 
                           "aside", ".sidebar", ".menu", ".navigation", 
                           ".advertisement", ".ad", ".popup"]):
            element.decompose()
        
        # Extract main content areas
        main_content = ""
        for selector in ['main', '.main', '.content', '.post-content', 
                        '.article-content', '.page-content', 'article', '.entry']:
            try:
                content_element = soup.select_one(selector)
                if content_element:
                    main_content = content_element.get_text()
                    break
            except:
                continue
        
        # Fallback to body if no main content found
        if not main_content:
            main_content = soup.get_text()
        
        # Advanced text cleaning
        lines = (line.strip() for line in main_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = ' '.join(chunk for chunk in chunks if chunk and len(chunk) > 2)
        
        # Remove excessive whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        logger.info(f"BeautifulSoup: Extracted {len(clean_text)} characters of clean text")
        
        return {
            "title": title,
            "content": clean_text,
            "html": html_content,
            "url": url,
            "extraction_method": "beautifulsoup",
            "parser_used": soup.builder.name if hasattr(soup, 'builder') else "unknown"
        }
    
    def _extract_with_regex(self, html_content: str, url: str) -> Dict[str, str]:
        """Regex-based content extraction as last resort"""
        
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "Page Title"
        
        # Remove script and style content
        content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', ' ', content)
        
        # Clean up whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        logger.info(f"Regex: Extracted {len(content)} characters of text")
        
        return {
            "title": title,
            "content": content,
            "html": html_content,
            "url": url,
            "extraction_method": "regex",
            "parser_used": "regex"
        }
    
    async def _comprehensive_content_extraction(self, page_content: Dict[str, str]) -> Dict[str, Any]:
        """Comprehensive extraction of all sales page elements"""
        
        content = page_content["content"]
        
        # Advanced benefit extraction
        benefits = self._extract_comprehensive_benefits(content)
        
        # Advanced feature extraction  
        features = self._extract_comprehensive_features(content)
        
        # Emotional trigger extraction
        emotional_triggers = self._extract_emotional_triggers(content)
        
        # Social proof extraction
        social_proof = self._extract_social_proof(content)
        
        # Pain point extraction
        pain_points = self._extract_pain_points(content)
        
        # Pricing and offer extraction
        pricing_offers = self._extract_pricing_offers(content)
        
        # Guarantee extraction
        guarantees = self._extract_guarantees(content)
        
        # CTA extraction
        call_to_actions = self._extract_call_to_actions(content)
        
        # Testimonial extraction
        testimonials = self._extract_testimonials(content)
        
        return {
            "title": page_content["title"],
            "content": content,
            "url": page_content["url"],
            "extraction_method": page_content.get("extraction_method", "unknown"),
            "benefits_claimed": benefits,
            "features_mentioned": features,
            "emotional_triggers": emotional_triggers,
            "social_proof_elements": social_proof,
            "pain_points_addressed": pain_points,
            "pricing_offers": pricing_offers,
            "guarantees_mentioned": guarantees,
            "call_to_actions": call_to_actions,
            "testimonials_found": testimonials,
            "word_count": len(content.split()),
            "content_sections": self._identify_advanced_content_sections(content)
        }
    
    def _extract_comprehensive_benefits(self, content: str) -> List[str]:
        """Extract all types of benefits with advanced patterns"""
        
        benefit_patterns = [
            # Direct benefit statements
            r'(?:helps?|supports?|improves?|enhances?|boosts?|increases?|reduces?|eliminates?|provides?|delivers?|gives?)\s+(?:you\s+)?([^.!?]{10,80})',
            
            # Outcome-based benefits
            r'(?:you (?:will|can|get|experience|enjoy|feel))\s+([^.!?]{10,80})',
            
            # Result statements
            r'(?:results? in|leads to|causes|creates)\s+([^.!?]{10,80})',
            
            # Transformation statements
            r'(?:transforms?|changes?|converts?|turns?)\s+([^.!?]{10,80})',
            
            # Problem solution statements
            r'(?:fixes?|solves?|addresses?|tackles?|handles?)\s+([^.!?]{10,80})'
        ]
        
        benefits = []
        for pattern in benefit_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                cleaned = match.strip().lower()
                if len(cleaned) > 10 and len(cleaned) < 100:
                    benefits.append(cleaned.capitalize())
        
        return list(set(benefits[:15]))  # Remove duplicates, limit to top 15
    
    def _extract_comprehensive_features(self, content: str) -> List[str]:
        """Extract product features with advanced detection"""
        
        feature_patterns = [
            r'(?:contains?|includes?|features?|made with|powered by|built with|composed of)\s+([^.!?]{5,60})',
            r'(?:ingredients?|components?|elements?)\s*:?\s*([^.!?]{10,100})',
            r'(?:formula|blend|mixture|combination)\s+(?:of|with|containing)\s+([^.!?]{10,80})',
            r'(?:active|key|main|primary|essential)\s+(?:ingredient|component|element)\s*:?\s*([^.!?]{5,60})'
        ]
        
        features = []
        for pattern in feature_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                cleaned = match.strip()
                if len(cleaned) > 5 and len(cleaned) < 80:
                    features.append(cleaned.title())
        
        return list(set(features[:12]))
    
    def _extract_emotional_triggers(self, content: str) -> List[str]:
        """Extract emotional triggers and power words"""
        
        trigger_words = [
            "revolutionary", "breakthrough", "secret", "proven", "guaranteed", "exclusive",
            "limited", "urgent", "fast", "instant", "easy", "simple", "powerful",
            "amazing", "incredible", "shocking", "surprising", "natural", "safe",
            "effective", "clinically", "scientifically", "doctor", "expert",
            "thousands", "millions", "trusted", "recommended", "endorsed"
        ]
        
        found_triggers = []
        content_lower = content.lower()
        
        for trigger in trigger_words:
            if trigger in content_lower:
                # Find context around the trigger
                pattern = rf'.{{0,30}}{re.escape(trigger)}.{{0,30}}'
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    found_triggers.append({
                        "trigger": trigger,
                        "context": matches[0].strip()
                    })
        
        return found_triggers[:10]
    
    def _extract_social_proof(self, content: str) -> List[str]:
        """Extract social proof elements"""
        
        social_proof_patterns = [
            r'(\d+(?:,\d+)*)\s*(?:customers?|users?|people|clients?|members?)',
            r'(?:over|more than|above)\s+(\d+(?:,\d+)*)\s*(?:customers?|users?|people)',
            r'(\d+)\s*(?:star|★)\s*(?:rating|review)',
            r'(?:testimonials?|reviews?|success stories?|case studies?)',
            r'(?:as seen (?:on|in)|featured (?:on|in)|mentioned (?:on|in))\s+([^.!?]{5,40})',
            r'(?:trusted by|used by|recommended by)\s+([^.!?]{5,40})'
        ]
        
        social_proof = []
        for pattern in social_proof_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(str(m) for m in match if m)
                social_proof.append(str(match).strip())
        
        return list(set(social_proof[:8]))
    
    def _extract_pain_points(self, content: str) -> List[str]:
        """Extract pain points and problems addressed"""
        
        pain_patterns = [
            r'(?:struggling with|tired of|frustrated by|sick of|fed up with)\s+([^.!?]{10,60})',
            r'(?:problems? with|issues? with|trouble with|difficulty with)\s+([^.!?]{10,60})',
            r'(?:can\'t|cannot|unable to|failed to)\s+([^.!?]{10,60})',
            r'(?:worried about|concerned about|afraid of)\s+([^.!?]{10,60})',
            r'(?:embarrassed by|ashamed of|self-conscious about)\s+([^.!?]{10,60})'
        ]
        
        pain_points = []
        for pattern in pain_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                cleaned = match.strip().lower()
                if len(cleaned) > 8 and len(cleaned) < 80:
                    pain_points.append(cleaned.capitalize())
        
        return list(set(pain_points[:8]))
    
    def _extract_pricing_offers(self, content: str) -> List[str]:
        """Extract pricing and special offers"""
        
        pricing_patterns = [
            r'\$[\d,]+(?:\.\d{2})?',
            r'£[\d,]+(?:\.\d{2})?',
            r'€[\d,]+(?:\.\d{2})?',
            r'(?:buy\s+\d+\s+get\s+\d+\s+free)',
            r'(?:\d+%\s+off|save\s+\d+%)',
            r'(?:free\s+(?:shipping|trial|bonus|gift))',
            r'(?:money\s*back\s*guarantee)',
            r'(?:limited\s+time\s+offer)',
            r'(?:today\s+only|for\s+today)',
            r'(?:special\s+(?:offer|deal|price))'
        ]
        
        offers = []
        for pattern in pricing_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            offers.extend(matches)
        
        return list(set(offers[:10]))
    
    def _extract_guarantees(self, content: str) -> List[str]:
        """Extract guarantee information"""
        
        guarantee_patterns = [
            r'(\d+)\s*day\s*(?:money\s*back\s*)?guarantee',
            r'(?:100%|full)\s*(?:money\s*back\s*)?guarantee',
            r'(?:satisfaction|results?)\s*guarantee',
            r'(?:risk\s*free|no\s*risk)',
            r'(?:refund|return)\s*policy'
        ]
        
        guarantees = []
        for pattern in guarantee_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(str(m) for m in match if m)
                guarantees.append(str(match).strip())
        
        return list(set(guarantees[:5]))
    
    def _extract_call_to_actions(self, content: str) -> List[str]:
        """Extract call-to-action phrases"""
        
        cta_patterns = [
            r'(?:buy|order|get|try|start|download|claim|grab)\s+(?:now|today|here)',
            r'(?:click|tap)\s+(?:here|now|below)',
            r'(?:add\s+to\s+cart|order\s+now|buy\s+now)',
            r'(?:get\s+started|start\s+now|begin\s+today)',
            r'(?:claim\s+your|get\s+your)\s+[^.!?]{5,30}',
            r'(?:don\'t\s+wait|act\s+now|hurry)'
        ]
        
        ctas = []
        for pattern in cta_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            ctas.extend(matches)
        
        return list(set(ctas[:8]))
    
    def _extract_testimonials(self, content: str) -> List[str]:
        """Extract testimonial content"""
        
        # Look for quoted text that might be testimonials
        testimonial_patterns = [
            r'"([^"]{20,200})"',
            r'\'([^\']{20,200})\'',
            r'(?:testimonial|review|says?|states?|reports?)\s*:?\s*"([^"]{20,200})"',
            r'(?:customer|user|client)\s+(?:says?|reports?|testimonial)\s*:?\s*([^.!?]{20,100})'
        ]
        
        testimonials = []
        for pattern in testimonial_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                cleaned = match.strip()
                if len(cleaned) > 20 and len(cleaned) < 250:
                    testimonials.append(cleaned)
        
        return testimonials[:5]
    
    def _identify_advanced_content_sections(self, content: str) -> Dict[str, str]:
        """Identify and extract key content sections"""
        
        sections = {}
        content_lower = content.lower()
        
        section_patterns = {
            "headline": r'(.{0,300}?)(?:\n|\.)',
            "benefits": r'(benefits?[^.!?]*(?:[.!?][^.!?]*){0,3})',
            "features": r'(features?[^.!?]*(?:[.!?][^.!?]*){0,3})',
            "testimonials": r'(testimonial[^.!?]*(?:[.!?][^.!?]*){0,2})',
            "guarantee": r'(guarantee[^.!?]*(?:[.!?][^.!?]*){0,2})',
            "pricing": r'((?:price|cost|\$\d+)[^.!?]*(?:[.!?][^.!?]*){0,2})',
            "urgency": r'((?:limited|urgent|hurry|act now)[^.!?]*(?:[.!?][^.!?]*){0,1})',
            "social_proof": r'((?:customers?|users?|people)[^.!?]*(?:[.!?][^.!?]*){0,2})'
        }
        
        for section_name, pattern in section_patterns.items():
            matches = re.findall(pattern, content_lower, re.DOTALL | re.IGNORECASE)
            if matches:
                # Take the first match and clean it
                section_text = matches[0].strip()[:500]
                sections[section_name] = section_text
        
        return sections
    
    async def _advanced_product_extraction(self, page_content: Dict[str, str], structured_content: Dict[str, Any]) -> str:
        """Advanced product name extraction with multiple strategies"""
        
        try:
            if self.product_extractor:
                # Use full product extractor
                product_name = self.product_extractor.extract_product_name(
                    content=page_content["content"],
                    page_title=page_content["title"]
                )
            else:
                # Use advanced fallback
                product_name = self._advanced_product_fallback(
                    page_content["content"], 
                    page_content["title"]
                )
            
            # Validate and enhance result
            if product_name and product_name != "Product":
                logger.info(f"✅ Product name extracted: '{product_name}'")
                return product_name
            else:
                # Try additional extraction methods
                return self._multi_strategy_product_extraction(page_content["content"])
                
        except Exception as e:
            logger.error(f"❌ Product extraction failed: {e}")
            return self._emergency_product_extraction(page_content["content"])
    
    def _advanced_product_fallback(self, content: str, title: str) -> str:
        """Advanced fallback product extraction"""
        
        # Strategy 1: Title-based extraction
        if title:
            title_words = title.split()
            for word in title_words:
                if (len(word) > 4 and 
                    word[0].isupper() and 
                    word.lower() not in ['the', 'and', 'for', 'with', 'natural', 'health']):
                    return word
        
        # Strategy 2: Advanced pattern matching
        advanced_patterns = [
            r'(?:introducing|meet|discover|try|get|experience)\s+([A-Z][a-zA-Z]{3,15})',
            r'([A-Z][a-zA-Z]{3,15})\s+(?:is|helps|supports|provides|delivers)',
            r'(?:with|using|taking)\s+([A-Z][a-zA-Z]{3,15})\s+you',
            r'([A-Z][a-zA-Z]{3,15})\s+(?:formula|supplement|solution|system)',
            r'(?:love|rave about|recommend)\s+([A-Z][a-zA-Z]{3,15})',
            r'([A-Z][a-zA-Z]{3,15})\s+(?:works|contains|features)'
        ]