# src/intelligence/analyzers.py - FIXED VERSION WITH PRODUCT EXTRACTION
"""
Intelligence analysis engines - FIXED to properly extract product names like "AquaSculpt"
🎯 CRITICAL FIX: Added proper product name extraction and enhanced intelligence categories
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

# ✅ CRITICAL FIX: Import the product extractor
try:
    from src.intelligence.extractors.product_extractor import ProductNameExtractor, extract_product_name
    PRODUCT_EXTRACTOR_AVAILABLE = True
    logger.info("✅ Product extractor imported successfully")
except ImportError:
    PRODUCT_EXTRACTOR_AVAILABLE = False
    logger.warning("⚠️ Product extractor not found. Creating fallback extractor.")
    
            # ✅ FALLBACK: Simple product extractor built-in
    class ProductNameExtractor:
        """Fallback product name extractor"""
        
        def extract_product_name(self, content: str, page_title: str = None) -> str:
            """Simple fallback product name extraction"""
            
            # Simple patterns for product names
            simple_patterns = [
                r'Join\s+The\s+Thousands\s+Who\s+Rave\s+About\s+([A-Z][a-zA-Z]+)',
                r'Feel\s+The\s+Difference\s+([A-Z][a-zA-Z]+)\s+May\s+Make',
                r'Get\s+([A-Z][a-zA-Z]+)\s+(?:today|now|here)',
                r'Try\s+([A-Z][a-zA-Z]+)\s+(?:today|now|here)',
                r'([A-Z][a-zA-Z]+)\s+helps?\s+support',
                r'([A-Z][a-zA-Z]+)\s+is\s+a\s+(?:natural|powerful|effective)',
                r'(?:with|using)\s+([A-Z][a-zA-Z]+)\s+you',
                r'([A-Z][a-zA-Z]+)\s+(?:contains|features|provides)',
                r'discover\s+([A-Z][a-zA-Z]+)',
                r'introducing\s+([A-Z][a-zA-Z]+)'
            ]
            
            # Check title first
            if page_title:
                title_words = page_title.split()
                for word in title_words:
                    if len(word) > 3 and word[0].isupper() and word.lower() not in ['the', 'and', 'for', 'with']:
                        return word
            
            # Check patterns in content
            for pattern in simple_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    candidate = match.group(1).strip()
                    if len(candidate) > 3 and candidate.lower() not in ['the', 'this', 'that', 'many', 'some']:
                        return candidate
            
            # Frequency-based fallback
            words = re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', content)
            if words:
                from collections import Counter
                word_counts = Counter(words)
                # Get most frequent capitalized word that appears at least twice
                for word, count in word_counts.most_common(10):
                    if count >= 2 and word.lower() not in ['the', 'this', 'that', 'many', 'some', 'click', 'here']:
                        return word
            
            # Final fallback
            return "Product"

class SalesPageAnalyzer:
    """Analyze competitor sales pages for offers, psychology, and opportunities - FIXED VERSION"""
    
    def __init__(self):
        # Initialize OpenAI client if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=api_key)
        else:
            self.openai_client = None
            logger.warning("OpenAI API key not found. AI analysis will be limited.")
        
        # ✅ CRITICAL FIX: Initialize product extractor
        if PRODUCT_EXTRACTOR_AVAILABLE:
            self.product_extractor = ProductNameExtractor()
        else:
            self.product_extractor = None
    
    async def analyze(self, url: str) -> Dict[str, Any]:
        """Complete sales page analysis - FIXED to extract product names properly"""
        
        try:
            logger.info(f"🎯 Starting FIXED analysis for URL: {url}")
            
            # Step 1: Scrape the page content
            page_content = await self._scrape_page(url)
            logger.info("✅ Page scraping completed successfully")
            
            # Step 2: Extract structured content
            structured_content = await self._extract_content_structure(page_content)
            logger.info("✅ Content structure extraction completed")
            
            # ✅ CRITICAL FIX: Step 3: Extract product name FIRST
            product_name = await self._extract_product_name(page_content, structured_content)
            logger.info(f"🎯 FIXED: Product name extracted: '{product_name}'")
            
            # Step 4: Enhanced intelligence extraction with product name
            if self.openai_client:
                intelligence = await self._extract_enhanced_intelligence(
                    structured_content, url, product_name
                )
                logger.info("✅ Enhanced AI intelligence extraction completed")
            else:
                intelligence = self._fallback_analysis_enhanced(
                    structured_content, url, product_name
                )
                logger.info("✅ Enhanced fallback analysis completed")
            
            return intelligence
            
        except Exception as e:
            logger.error(f"❌ FIXED analysis failed for {url}: {str(e)}")
            # Return enhanced fallback response
            return self._error_fallback_analysis_enhanced(url, str(e))
    
    async def _extract_product_name(self, page_content: Dict[str, str], structured_content: Dict[str, Any]) -> str:
        """✅ CRITICAL FIX: Extract product name using dedicated extractor"""
        
        try:
            if PRODUCT_EXTRACTOR_AVAILABLE:
                # Use the full extractor
                extractor = ProductNameExtractor()
                product_name = extractor.extract_product_name(
                    content=page_content["content"],
                    page_title=page_content["title"]
                )
            else:
                # Use simple fallback function
                product_name = extract_product_name(
                    content=page_content["content"],
                    page_title=page_content["title"]
                )
            
            # Validate result
            if product_name and product_name != "Product":
                logger.info(f"✅ Product name successfully extracted: '{product_name}'")
                return product_name
            else:
                logger.warning("⚠️ Product extractor returned generic name, trying simple fallback")
                return self._simple_product_detection(page_content["content"])
                
        except Exception as e:
            logger.error(f"❌ Product extraction failed: {str(e)}")
            return self._simple_product_detection(page_content["content"])
    
    def _simple_product_detection(self, content: str) -> str:
        """Simplest possible product name detection"""
        
        # Just look for capitalized words that appear multiple times
        words = re.findall(r'\b[A-Z][a-zA-Z]{4,}\b', content)
        if words:
            from collections import Counter
            word_counts = Counter(words)
            for word, count in word_counts.most_common(5):
                if count >= 2 and word.lower() not in ['the', 'this', 'that', 'click', 'here', 'get', 'buy']:
                    logger.info(f"🔍 Simple detection found: '{word}'")
                    return word
        
        logger.warning("⚠️ No product name detected, using 'Product'")
        return "Product"
    
    def _fallback_product_detection(self, content: str) -> str:
        """Fallback product name detection when extractor is not available"""
        
        # Simple patterns to detect product names
        simple_patterns = [
            r'Join\s+The\s+Thousands\s+Who\s+Rave\s+About\s+([A-Z][a-zA-Z]+)',
            r'Feel\s+The\s+Difference\s+([A-Z][a-zA-Z]+)\s+May\s+Make',
            r'Get\s+([A-Z][a-zA-Z]+)\s+(?:today|now|here)',
            r'Try\s+([A-Z][a-zA-Z]+)\s+(?:today|now|here)',
            r'([A-Z][a-zA-Z]+)\s+helps?\s+support',
            r'([A-Z][a-zA-Z]+)\s+is\s+a\s+(?:natural|powerful|effective)',
            r'(?:with|using)\s+([A-Z][a-zA-Z]+)\s+(?:you|users|customers)',
            r'([A-Z][a-zA-Z]+)\s+(?:contains|features|provides)',
            r'discover\s+([A-Z][a-zA-Z]+)',
            r'introducing\s+([A-Z][a-zA-Z]+)'
        ]
        
        for pattern in simple_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                if candidate and len(candidate) > 3 and candidate not in ['The', 'This', 'That', 'Many', 'Some']:
                    logger.info(f"🔍 Fallback detection found: '{candidate}'")
                    return candidate
        
        # Frequency-based fallback
        words = re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', content)
        if words:
            from collections import Counter
            word_counts = Counter(words)
            for word, count in word_counts.most_common(5):
                if count >= 2 and word.lower() not in ['the', 'this', 'that', 'many', 'some', 'click', 'here']:
                    logger.info(f"🔍 Frequency fallback found: '{word}'")
                    return word
        
        # If nothing found, return generic
        logger.warning("⚠️ No product name detected, using 'Product'")
        return "Product"
    
    async def _scrape_page(self, url: str) -> Dict[str, str]:
        """Advanced web scraping with error handling - UNCHANGED"""
        
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
        """Extract and structure key page elements - FOCUSED on product/benefits/features"""
        
        content = page_content["content"]
        
        # Extract benefit claims (primary focus)
        benefit_patterns = [
            r'(?:helps?|supports?|improves?|enhances?|boosts?|increases?|reduces?|eliminates?)\s+([^.!?]+)',
            r'(?:you (?:will|can|get))\s+([^.!?]+)',
            r'(?:provides?|delivers?|gives? you)\s+([^.!?]+)',
            r'(?:transforms?|changes?|fixes?|solves?)\s+([^.!?]+)'
        ]
        
        benefits = []
        for pattern in benefit_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 5 and len(match.strip()) < 100:
                    benefits.append(match.strip())
        
        # Extract feature mentions (what the product contains/includes)
        feature_patterns = [
            r'(?:contains?|includes?|features?|made with|powered by)\s+([^.!?]+)',
            r'(?:ingredients?|components?|elements?)\s*:?\s*([^.!?]+)',
            r'(?:built with|designed with|created with)\s+([^.!?]+)'
        ]
        
        features = []
        for pattern in feature_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 3 and len(match.strip()) < 80:
                    features.append(match.strip())
        
        # Extract emotional triggers and power words
        emotional_triggers = [
            "breakthrough", "secret", "proven", "guaranteed", "exclusive",
            "revolutionary", "advanced", "powerful", "effective", "natural",
            "safe", "fast", "easy", "simple", "amazing", "incredible"
        ]
        
        found_triggers = []
        content_lower = content.lower()
        for trigger in emotional_triggers:
            if trigger in content_lower:
                found_triggers.append(trigger)
        
        # Extract social proof elements (focused on results, not pricing)
        social_proof_patterns = [
            r'(\d+(?:,\d+)*)\s*(?:customers?|users?|people|clients?)',
            r'(?:testimonials?|reviews?|success stories)',
            r'(?:results?|transformations?|improvements?)',
            r'(?:satisfied|happy|thrilled)\s+(?:customers?|users?|clients?)'
        ]
        
        social_proof = []
        for pattern in social_proof_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                social_proof.extend([str(match) if not isinstance(match, tuple) else match[0] for match in matches][:3])
        
        # Extract problem/pain points addressed
        pain_point_patterns = [
            r'(?:struggling with|tired of|frustrated by|sick of)\s+([^.!?]+)',
            r'(?:problems? with|issues? with|trouble with)\s+([^.!?]+)',
            r'(?:can\'t|cannot|unable to)\s+([^.!?]+)'
        ]
        
        pain_points = []
        for pattern in pain_point_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 5 and len(match.strip()) < 80:
                    pain_points.append(match.strip())
        
        return {
            "title": page_content["title"],
            "content": content,
            "url": page_content["url"],
            "benefits_claimed": benefits[:10],  # Top 10 benefits
            "features_mentioned": features[:8],  # Top 8 features
            "emotional_triggers": found_triggers,
            "social_proof_elements": social_proof,
            "pain_points_addressed": pain_points[:5],  # Top 5 pain points
            "word_count": len(content.split()),
            "content_sections": self._identify_content_sections(content)
        }
    
    # ✅ ENHANCED: Extract health claims
        health_claims = self._extract_health_claims(content)
        
        # ✅ ENHANCED: Extract ingredients mentions
        ingredients = self._extract_ingredients(content)
        
        return {
            "title": page_content["title"],
            "content": content,
            "url": page_content["url"],
            "pricing_mentions": prices,
            "emotional_triggers": found_triggers,
            "social_proof_elements": social_proof,
            "health_claims": health_claims,  # ✅ NEW
            "ingredients_mentioned": ingredients,  # ✅ NEW
            "word_count": len(content.split()),
            "content_sections": self._identify_content_sections(content)
        }
    
    def _extract_health_claims(self, content: str) -> List[str]:
        """✅ NEW: Extract benefit claims (works across all industries)"""
        
        # Generic benefit patterns that work across industries
        benefit_patterns = [
            r'helps?\s+(?:you\s+)?(\w+(?:\s+\w+){0,3})',
            r'supports?\s+(\w+(?:\s+\w+){0,3})',
            r'improves?\s+(?:your\s+)?(\w+(?:\s+\w+){0,3})',
            r'boosts?\s+(?:your\s+)?(\w+(?:\s+\w+){0,3})',
            r'enhances?\s+(?:your\s+)?(\w+(?:\s+\w+){0,3})',
            r'reduces?\s+(\w+(?:\s+\w+){0,3})',
            r'increases?\s+(?:your\s+)?(\w+(?:\s+\w+){0,3})',
            r'provides?\s+(\w+(?:\s+\w+){0,3})',
            r'delivers?\s+(\w+(?:\s+\w+){0,3})',
            r'guarantees?\s+(\w+(?:\s+\w+){0,3})'
        ]
        
        claims = []
        for pattern in benefit_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) > 3 and not match.lower().startswith(('the', 'you', 'your')):
                    claims.append(f"Claims to help with {match.lower()}")
        
        return list(set(claims[:10]))  # Remove duplicates, limit to 10
    
    def _extract_ingredients(self, content: str) -> List[str]:
        """✅ NEW: Extract ingredients/components (works across industries)"""
        
        # Generic patterns for components/ingredients/features
        component_patterns = [
            r'contains?\s+(\w+(?:\s+\w+){0,2})',
            r'made\s+with\s+(\w+(?:\s+\w+){0,2})',
            r'includes?\s+(\w+(?:\s+\w+){0,2})',
            r'features?\s+(\w+(?:\s+\w+){0,2})',
            r'powered\s+by\s+(\w+(?:\s+\w+){0,2})',
            r'built\s+with\s+(\w+(?:\s+\w+){0,2})'
        ]
        
        ingredients = []
        for pattern in component_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) > 2:
                    ingredients.append(match.title())
        
        return list(set(ingredients[:8]))  # Remove duplicates, limit to 8