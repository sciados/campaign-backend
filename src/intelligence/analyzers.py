# src/intelligence/analyzers.py - ENHANCED VERSION WITH EXTRACTORS
"""
Intelligence analysis engines - The core AI that extracts competitive insights
Enhanced with product extractor integration
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

# ✅ ADD: Import product extractor with error handling
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
        # Initialize OpenAI client if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=api_key)
        else:
            self.openai_client = None
            logger.warning("OpenAI API key not found. AI analysis will be limited.")
        
        # ✅ ADD: Initialize product extractor
        if PRODUCT_EXTRACTOR_AVAILABLE:
            self.product_extractor = ProductNameExtractor()
            logger.info("✅ Product extractor initialized")
        else:
            self.product_extractor = None
            logger.warning("⚠️ Product extractor not available")
    
    async def analyze(self, url: str) -> Dict[str, Any]:
        """Complete sales page analysis"""
        
        try:
            logger.info(f"Starting analysis for URL: {url}")
            
            # Step 1: Scrape the page content
            page_content = await self._scrape_page(url)
            logger.info("Page scraping completed successfully")
            
            # Step 2: Extract structured content
            structured_content = await self._extract_content_structure(page_content)
            logger.info("Content structure extraction completed")
            
            # ✅ ADD: Step 2.5: Extract product name using advanced extractor
            product_name = await self._extract_product_name(page_content, structured_content)
            logger.info(f"🎯 Product name extracted: '{product_name}'")
            
            # Step 3: AI-powered intelligence extraction (if available)
            if self.openai_client:
                intelligence = await self._extract_intelligence(structured_content, url, product_name)
                logger.info("AI intelligence extraction completed")
            else:
                intelligence = self._fallback_analysis(structured_content, url, product_name)
                logger.info("Using fallback analysis (no OpenAI key)")
            
            return intelligence
            
        except Exception as e:
            logger.error(f"Sales page analysis failed for {url}: {str(e)}")
            # Return a fallback response instead of raising
            return self._error_fallback_analysis(url, str(e))
    
    # ✅ ADD: Advanced product name extraction method
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
        """Basic product name extraction fallback"""
        
        # Try title first
        if title:
            title_words = title.split()
            for word in title_words:
                if (len(word) > 4 and 
                    word[0].isupper() and 
                    word.lower() not in ['the', 'and', 'for', 'with', 'health', 'natural']):
                    return word
        
        # Basic pattern matching
        patterns = [
            r'(?:introducing|try|get)\s+([A-Z][a-zA-Z]{3,15})',
            r'([A-Z][a-zA-Z]{3,15})\s+(?:helps|supports|works)',
            r'([A-Z][a-zA-Z]{3,15})\s*[™®©]'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                return matches[0] if isinstance(matches[0], str) else matches[0][0]
        
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
        
        # ✅ COMPREHENSIVE PRODUCT EXTRACTION
        product_details = self._extract_comprehensive_product_details(content)
        
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
        emotional_triggers = self._extract_emotional_triggers(content)
        
        # Extract social proof elements (enhanced)
        social_proof = self._extract_social_proof_elements(content)
        
        # Extract guarantees and risk reversals
        guarantees = self._extract_guarantees(content)
        
        # Extract bonuses and incentives
        bonuses = self._extract_bonuses(content)
        
        # Extract call-to-actions
        ctas = self._extract_call_to_actions(content)
        
        # Extract testimonials and reviews
        testimonials = self._extract_testimonials(content)
        
        return {
            "title": page_content["title"],
            "content": content,
            "url": page_content["url"],
            # ✅ COMPREHENSIVE PRODUCT DATA
            "product_details": product_details,
            "benefits_claimed": product_details["benefits"],
            "features_mentioned": product_details["features"],
            "ingredients_components": product_details["ingredients"],
            "pricing_mentions": prices,
            "emotional_triggers": emotional_triggers,
            "social_proof_elements": social_proof,
            "guarantees_offered": guarantees,
            "bonuses_incentives": bonuses,
            "call_to_actions": ctas,
            "testimonials_reviews": testimonials,
            "word_count": len(content.split()),
            "content_sections": self._identify_content_sections(content)
        }
    
    def _extract_comprehensive_product_details(self, content: str) -> Dict[str, Any]:
        """Extract ALL product/service details from sales page"""
        
        # Extract benefits (what it does FOR you)
        benefits = self._extract_product_benefits(content)
        
        # Extract features (what it HAS/IS)
        features = self._extract_product_features(content)
        
        # Extract ingredients/components
        ingredients = self._extract_ingredients_components(content)
        
        # Extract product types/categories
        product_types = self._extract_product_types(content)
        
        # Extract target audience indicators
        target_audience = self._extract_target_audience(content)
        
        # Extract usage instructions/directions
        usage_instructions = self._extract_usage_instructions(content)
        
        return {
            "benefits": benefits,
            "features": features,
            "ingredients": ingredients,
            "product_types": product_types,
            "target_audience": target_audience,
            "usage_instructions": usage_instructions,
            "extraction_confidence": 0.5 # self._calculate_extraction_confidence(benefits, features, ingredients)
        }
    
    def _extract_product_benefits(self, content: str) -> List[str]:
        """Extract product benefits (what it does FOR the customer)"""
        
        benefit_patterns = [
            # Direct benefit statements
            r'(?:helps?|supports?|improves?|enhances?|boosts?|increases?|reduces?|eliminates?|provides?|delivers?|gives?)\s+(?:you\s+)?([^.!?]{15,100})',
            
            # Outcome-based benefits
            r'(?:you\s+(?:will|can|get|experience|enjoy|feel|achieve|obtain))\s+([^.!?]{15,100})',
            
            # Result statements
            r'(?:results?\s+in|leads\s+to|causes|creates|brings)\s+([^.!?]{15,100})',
            
            # Benefit listing patterns
            r'benefits?\s*(?:include|are|of):\s*([^.!?]{20,200})',
            
            # Problem solution benefits
            r'(?:fixes?|solves?|addresses?|tackles?|handles?|stops?|prevents?)\s+([^.!?]{15,100})',
            
            # Transformation benefits
            r'(?:transforms?|changes?|converts?|turns?)\s+([^.!?]{15,100})',
            
            # Health/wellness benefits
            r'(?:promotes?|supports?|maintains?|restores?|optimizes?)\s+(?:healthy|natural|optimal)\s+([^.!?]{10,80})',
        ]
        
        benefits = []
        for pattern in benefit_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                cleaned = self._clean_extraction(match)
                if cleaned and len(cleaned) > 10:
                    benefits.append(cleaned)
        
        return list(set(benefits[:20]))  # Remove duplicates, keep top 20
    
    def _extract_product_features(self, content: str) -> List[str]:
        """Extract product features (what the product HAS/IS)"""
        
        feature_patterns = [
            # Direct feature statements
            r'(?:contains?|includes?|features?|has|made\s+with|powered\s+by|built\s+with|composed\s+of)\s+([^.!?]{10,80})',
            
            # Ingredient/component features
            r'(?:ingredients?|components?|elements?)\s*(?:include|are|:)?\s*([^.!?]{15,150})',
            
            # Formula/blend features
            r'(?:formula|blend|mixture|combination|complex)\s+(?:of|with|containing|includes?)\s+([^.!?]{15,100})',
            
            # Active ingredient features
            r'(?:active|key|main|primary|essential|proprietary)\s+(?:ingredient|component|element|formula)\s*:?\s*([^.!?]{10,80})',
            
            # Specification features
            r'(?:size|weight|volume|concentration|strength|potency)\s*:?\s*([^.!?]{5,50})',
            
            # Technology/method features
            r'(?:technology|method|process|technique|system)\s*:?\s*([^.!?]{10,80})',
            
            # Format/delivery features
            r'(?:capsules?|tablets?|powder|liquid|cream|gel|spray)\s*([^.!?]{0,50})',
        ]
        
        features = []
        for pattern in feature_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                cleaned = self._clean_extraction(match)
                if cleaned and len(cleaned) > 5:
                    features.append(cleaned)
        
        return list(set(features[:15]))  # Remove duplicates, keep top 15
    
    def _extract_ingredients_components(self, content: str) -> List[str]:
        """Extract specific ingredients, components, or materials"""
        
        ingredient_patterns = [
            # Specific ingredient mentions
            r'(?:mg|mcg|grams?|g)\s+(?:of\s+)?([A-Z][a-zA-Z\s]{3,25})',
            
            # Natural ingredient patterns
            r'(?:natural|organic|pure|extract|oil)\s+([A-Z][a-zA-Z\s]{3,25})',
            
            # Scientific/chemical names
            r'([A-Z][a-z]+(?:\s+[a-z]+)*)\s+(?:extract|acid|compound|complex)',
            
            # Vitamin/mineral patterns
            r'(Vitamin\s+[A-Z](?:\d+)?|[A-Z][a-z]+\s+(?:B|C|D|E|K)\d*)',
            
            # Herb/plant patterns
            r'([A-Z][a-z]+(?:\s+[a-z]+)*)\s+(?:root|leaf|bark|seed|berry|flower)',
            
            # Proprietary blend patterns
            r'(?:proprietary|exclusive|patented)\s+([^.!?]{10,50})\s+(?:blend|formula|complex)',
        ]
        
        ingredients = []
        for pattern in ingredient_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                cleaned = self._clean_extraction(match)
                if cleaned and len(cleaned) > 2:
                    ingredients.append(cleaned.title())
        
        return list(set(ingredients[:12]))  # Remove duplicates, keep top 12
    
    def _extract_product_types(self, content: str) -> List[str]:
        """Extract product categories and types"""
        
        type_patterns = [
            r'(?:supplement|vitamin|mineral|herb|extract|formula|blend|complex|compound)',
            r'(?:capsule|tablet|powder|liquid|cream|gel|spray|drops)',
            r'(?:natural|organic|synthetic|clinically\s+tested|FDA\s+approved)',
            r'(?:dietary\s+supplement|nutritional\s+support|health\s+formula)',
            r'(?:weight\s+loss|fat\s+burner|metabolism\s+booster|energy\s+enhancer)',
            r'(?:liver\s+support|detox|cleanse|digestive\s+health)',
        ]
        
        types = []
        content_lower = content.lower()
        
        for pattern in type_patterns:
            matches = re.findall(pattern, content_lower)
            types.extend(matches)
        
        return list(set(types[:8]))  # Remove duplicates, keep top 8
    
    def _extract_target_audience(self, content: str) -> List[str]:
        """Extract target audience indicators"""
        
        audience_patterns = [
            r'(?:for|designed\s+for|perfect\s+for|ideal\s+for)\s+([^.!?]{10,60})',
            r'(?:men|women|adults|seniors|athletes|professionals)\s+(?:who|looking|wanting|needing)',
            r'(?:people|individuals|those)\s+(?:who|with|suffering\s+from|dealing\s+with)\s+([^.!?]{10,60})',
            r'(?:if\s+you|whether\s+you)\s+(?:are|have|want|need|struggle\s+with)\s+([^.!?]{10,60})',
        ]
        
        audience = []
        for pattern in audience_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                cleaned = self._clean_extraction(match)
                if cleaned and len(cleaned) > 5:
                    audience.append(cleaned)
        
        return list(set(audience[:6]))  # Remove duplicates, keep top 6
    
    def _extract_usage_instructions(self, content: str) -> List[str]:
        """Extract usage instructions and directions"""
        
        usage_patterns = [
            r'(?:take|use|apply|consume|drink)\s+([^.!?]{10,80})',
            r'(?:dosage|directions|instructions)\s*:?\s*([^.!?]{15,100})',
            r'(?:\d+\s+(?:times?|capsules?|tablets?|drops?)\s+(?:per\s+day|daily|morning|evening))',
            r'(?:before|after|with|without)\s+(?:meals?|food|eating|breakfast|dinner)',
        ]
        
        instructions = []
        for pattern in usage_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                cleaned = self._clean_extraction(match)
                if cleaned and len(cleaned) > 8:
                    instructions.append(cleaned)
        
        return list(set(instructions[:5]))  # Remove duplicates, keep top 5
    
    def _extract_emotional_triggers(self, content: str) -> List[Dict[str, str]]:
        """Extract emotional triggers with context"""
        
        trigger_words = [
            "limited time", "exclusive", "secret", "breakthrough", "guaranteed",
            "proven", "instant", "fast", "easy", "simple", "powerful",
            "revolutionary", "amazing", "incredible", "shocking", "urgent",
            "clinically tested", "doctor recommended", "scientifically proven",
            "natural", "safe", "effective", "trusted", "recommended"
        ]
        
        found_triggers = []
        for trigger in trigger_words:
            if trigger.lower() in content.lower():
                # Find context around the trigger
                pattern = rf'.{{0,50}}{re.escape(trigger)}.{{0,50}}'
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    found_triggers.append({
                        "trigger": trigger,
                        "context": matches[0].strip()
                    })
        
        return found_triggers[:15]  # Keep top 15 with context
    
    def _extract_social_proof_elements(self, content: str) -> List[str]:
        """Extract social proof elements"""
        
        social_proof_patterns = [
            r'(\d+(?:,\d+)*)\s*(?:customers?|users?|clients?|members?|people)',
            r'(?:over|more\s+than|above)\s+(\d+(?:,\d+)*)\s*(?:customers?|users?|people)',
            r'(\d+)\s*(?:star|★)\s*(?:rating|review)',
            r'(?:testimonials?|reviews?|success\s+stories?|case\s+studies?)',
            r'(?:as\s+seen\s+(?:on|in)|featured\s+(?:on|in)|mentioned\s+(?:on|in))\s+([^.!?]{5,40})',
            r'(?:trusted\s+by|used\s+by|recommended\s+by)\s+([^.!?]{5,40})',
            r'(?:doctor|physician|expert|professional)\s+(?:recommended|approved|endorsed)',
        ]
        
        social_proof = []
        for pattern in social_proof_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(str(m) for m in match if m)
                social_proof.append(str(match).strip())
        
        return list(set(social_proof[:10]))  # Remove duplicates, keep top 10
    
    def _extract_guarantees(self, content: str) -> List[str]:
        """Extract guarantee information"""
        
        guarantee_patterns = [
            r'(\d+)\s*day\s*(?:money\s*back\s*)?guarantee',
            r'(?:100%|full)\s*(?:money\s*back\s*)?guarantee',
            r'(?:satisfaction|results?)\s*guarantee',
            r'(?:risk\s*free|no\s*risk)',
            r'(?:refund|return)\s*policy',
            r'(?:lifetime|forever)\s*guarantee',
        ]
        
        guarantees = []
        for pattern in guarantee_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(str(m) for m in match if m)
                guarantees.append(str(match).strip())
        
        return list(set(guarantees[:5]))  # Remove duplicates, keep top 5
    
    def _extract_bonuses(self, content: str) -> List[str]:
        """Extract bonus offers and incentives"""
        
        bonus_patterns = [
            r'(?:free|bonus|complimentary)\s+([^.!?]{10,60})',
            r'(?:plus|also\s+get|you\s+also\s+receive)\s+([^.!?]{10,60})',
            r'(?:bonus\s+#?\d+)\s*:?\s*([^.!?]{10,60})',
            r'(?:special\s+offer|limited\s+time)\s*:?\s*([^.!?]{10,60})',
            r'(?:buy\s+\d+\s+get\s+\d+\s+free)',
        ]
        
        bonuses = []
        for pattern in bonus_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                cleaned = self._clean_extraction(match)
                if cleaned and len(cleaned) > 8:
                    bonuses.append(cleaned)
        
        return list(set(bonuses[:8]))  # Remove duplicates, keep top 8
    
    def _extract_call_to_actions(self, content: str) -> List[str]:
        """Extract call-to-action phrases"""
        
        cta_patterns = [
            r'(?:buy|order|get|try|start|download|claim|grab)\s+(?:now|today|here)',
            r'(?:click|tap)\s+(?:here|now|below)',
            r'(?:add\s+to\s+cart|order\s+now|buy\s+now)',
            r'(?:get\s+started|start\s+now|begin\s+today)',
            r'(?:claim\s+your|get\s+your)\s+[^.!?]{5,30}',
            r'(?:don\'t\s+wait|act\s+now|hurry)',
            r'(?:limited\s+time|while\s+supplies\s+last)',
        ]
        
        ctas = []
        for pattern in cta_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            ctas.extend(matches)
        
        return list(set(ctas[:10]))  # Remove duplicates, keep top 10
    
    def _extract_testimonials(self, content: str) -> List[str]:
        """Extract testimonial content"""
        
        testimonial_patterns = [
            r'"([^"]{25,200})"',  # Quoted testimonials
            r'\'([^\']{25,200})\'',  # Single-quoted testimonials
            r'(?:testimonial|review|says?|states?|reports?)\s*:?\s*"([^"]{25,200})"',
            r'(?:customer|user|client)\s+(?:says?|reports?|testimonial)\s*:?\s*([^.!?]{25,150})',
        ]
        
        testimonials = []
        for pattern in testimonial_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                cleaned = self._clean_extraction(match)
                if cleaned and len(cleaned) > 20:
                    testimonials.append(cleaned)
        
        return testimonials[:8]  # Keep top 8 testimonials
    
    def _clean_extraction(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
    
    # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove common artifacts
        text = re.sub(r'^(and|or|but|the|a|an)\s+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+(and|or|but)$', '', text, flags=re.IGNORECASE)
    
        return text
    
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
    
    # ✅ UPDATED: Include product name in AI analysis
    async def _extract_intelligence(self, structured_content: Dict[str, Any], url: str, product_name: str = "Product") -> Dict[str, Any]:
        """Use AI to extract competitive intelligence from structured content"""
        
        analysis_prompt = f"""
        Analyze this sales page content and extract competitive intelligence:

        URL: {url}
        Title: {structured_content['title']}
        Product Name: {product_name}
        Content Preview: {structured_content['content'][:2000]}
        Found Triggers: {structured_content['emotional_triggers']}
        Pricing Mentions: {structured_content['pricing_mentions']}
        
        Extract intelligence in these categories:

        1. OFFER INTELLIGENCE:
        - Main products/services offered (focus on {product_name})
        - Pricing strategy and structure
        - Bonuses and incentives
        - Guarantees and risk reversal
        - Value propositions

        2. PSYCHOLOGY INTELLIGENCE:
        - Emotional triggers used
        - Persuasion techniques
        - Target audience indicators
        - Pain points addressed
        - Social proof elements

        3. COMPETITIVE INTELLIGENCE:
        - Market positioning
        - Competitive advantages claimed
        - Potential weaknesses
        - Market gaps
        - Improvement opportunities

        4. CONTENT INTELLIGENCE:
        - Key messages
        - Content structure
        - Call-to-action strategy
        - Success stories mentioned

        5. CAMPAIGN SUGGESTIONS:
        - Alternative positioning ideas
        - Content opportunities
        - Marketing strategies

        Provide actionable insights that can be used for competitive campaigns.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert competitive intelligence analyst. Extract actionable insights for marketing campaigns."
                    },
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            ai_analysis = response.choices[0].message.content
            
            # Parse AI response into structured format
            intelligence = self._parse_ai_analysis(ai_analysis, structured_content)
            
            # Add metadata
            intelligence.update({
                "source_url": url,
                "page_title": structured_content["title"],
                "product_name": product_name,  # ✅ ADD: Include extracted product name
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "confidence_score": self._calculate_confidence_score(intelligence, structured_content),
                "raw_content": structured_content["content"][:1000]
            })
            
            return intelligence
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            # Return basic analysis if AI fails
            return self._fallback_analysis(structured_content, url, product_name)
    
    def _parse_ai_analysis(self, ai_response: str, structured_content: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured intelligence data"""
        
        # Simple parsing - extract insights from text
        lines = ai_response.split('\n')
        
        parsed_data = {
            "offer_intelligence": {
                "products": [],
                "pricing": structured_content.get("pricing_mentions", []),
                "bonuses": [],
                "guarantees": [],
                "value_propositions": []
            },
            "psychology_intelligence": {
                "emotional_triggers": structured_content.get("emotional_triggers", []),
                "pain_points": [],
                "target_audience": "General audience",
                "persuasion_techniques": []
            },
            "competitive_intelligence": {
                "opportunities": [],
                "gaps": [],
                "positioning": "Standard approach",
                "advantages": [],
                "weaknesses": []
            },
            "content_intelligence": {
                "key_messages": [structured_content.get("title", "")],
                "success_stories": [],
                "social_proof": structured_content.get("social_proof_elements", []),
                "content_structure": "Standard sales page"
            },
            "brand_intelligence": {
                "tone_voice": "Professional",
                "messaging_style": "Direct",
                "brand_positioning": "Market competitor"
            },
            "campaign_suggestions": []
        }
        
        # Extract insights from AI response
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify sections
            if "offer" in line.lower():
                current_section = "offer_intelligence"
            elif "psychology" in line.lower():
                current_section = "psychology_intelligence"
            elif "competitive" in line.lower():
                current_section = "competitive_intelligence"
            elif "content" in line.lower():
                current_section = "content_intelligence"
            elif "campaign" in line.lower() or "suggestion" in line.lower():
                current_section = "campaign_suggestions"
            
            # Extract bullet points
            if line.startswith(('-', '•', '*')) and current_section:
                insight = line[1:].strip()
                if insight:
                    if current_section == "campaign_suggestions":
                        parsed_data["campaign_suggestions"].append(insight)
                    elif "price" in insight.lower() or "$" in insight:
                        parsed_data["offer_intelligence"]["pricing"].append(insight)
                    elif "trigger" in insight.lower() or "emotion" in insight.lower():
                        parsed_data["psychology_intelligence"]["emotional_triggers"].append(insight)
                    elif "opportunity" in insight.lower() or "gap" in insight.lower():
                        parsed_data["competitive_intelligence"]["opportunities"].append(insight)
                    else:
                        # Add to appropriate section
                        if current_section in parsed_data:
                            if isinstance(parsed_data[current_section], dict):
                                # Add to a general list within the section
                                if "insights" not in parsed_data[current_section]:
                                    parsed_data[current_section]["insights"] = []
                                parsed_data[current_section]["insights"].append(insight)
        
        return parsed_data
    
    def _calculate_confidence_score(self, intelligence: Dict[str, Any], structured_content: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        
        score = 0.5  # Base score
        
        # Increase confidence based on data richness
        if intelligence.get("offer_intelligence", {}).get("pricing"):
            score += 0.1
        if intelligence.get("psychology_intelligence", {}).get("emotional_triggers"):
            score += 0.1
        if intelligence.get("competitive_intelligence", {}).get("opportunities"):
            score += 0.1
        if structured_content.get("pricing_mentions"):
            score += 0.1
        if structured_content.get("social_proof_elements"):
            score += 0.1
        if structured_content.get("word_count", 0) > 500:
            score += 0.1
        
        return min(score, 1.0)
    
    # ✅ UPDATED: Include product name in fallback analysis
    def _fallback_analysis(self, structured_content: Dict[str, Any], url: str, product_name: str = "Product") -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        
        return {
            "offer_intelligence": {
                "products": [product_name],  # ✅ Use extracted product name
                "pricing": structured_content.get("pricing_mentions", []),
                "bonuses": [],
                "guarantees": [],
                "value_propositions": ["Value proposition analysis available with AI"]
            },
            "psychology_intelligence": {
                "emotional_triggers": structured_content.get("emotional_triggers", []),
                "pain_points": ["Pain point analysis requires AI"],
                "target_audience": "General audience",
                "persuasion_techniques": ["Persuasion analysis requires AI"]
            },
            "competitive_intelligence": {
                "opportunities": ["Detailed competitive analysis requires AI"],
                "gaps": ["Gap analysis requires AI"],
                "positioning": "Standard market approach",
                "advantages": [],
                "weaknesses": []
            },
            "content_intelligence": {
                "key_messages": [structured_content["title"]],
                "success_stories": [],
                "social_proof": structured_content.get("social_proof_elements", []),
                "content_structure": f"Page with {structured_content.get('word_count', 0)} words"
            },
            "brand_intelligence": {
                "tone_voice": "Professional",
                "messaging_style": "Direct",
                "brand_positioning": "Market competitor"
            },
            "campaign_suggestions": [
                f"Create comparison content for {product_name}",
                "Address pricing strategy",
                "Develop unique positioning",
                "Build social proof campaigns"
            ],
            "source_url": url,
            "page_title": structured_content["title"],
            "product_name": product_name,  # ✅ ADD: Include extracted product name
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "confidence_score": 0.6,
            "raw_content": structured_content["content"][:1000],
            "analysis_note": "Basic analysis completed. Enhanced AI analysis requires OpenAI API key."
        }
    
    def _error_fallback_analysis(self, url: str, error_msg: str) -> Dict[str, Any]:
        """Fallback when analysis completely fails"""
        
        return {
            "offer_intelligence": {
                "products": [],
                "pricing": [],
                "bonuses": [],
                "guarantees": [],
                "value_propositions": []
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
            "analysis_note": f"Analysis failed: {error_msg}"
        }


# Enhanced analyzer class that extends the base
class EnhancedSalesPageAnalyzer(SalesPageAnalyzer):
    """Enhanced sales page analyzer with additional features"""
    
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
            
            # Add enhanced features
            enhanced_intelligence = {
                **base_analysis,
                "intelligence_id": f"intel_{uuid.uuid4().hex[:8]}",
                "analysis_depth": analysis_depth,
                "campaign_angles": self._generate_basic_campaign_angles(base_analysis),
                "actionable_insights": self._generate_actionable_insights(base_analysis),
                "technical_analysis": self._analyze_technical_aspects(url)
            }
            
            # Add VSL detection if requested (simplified for now)
            if include_vsl_detection:
                enhanced_intelligence["vsl_analysis"] = self._detect_video_content(base_analysis)
            
            return enhanced_intelligence
            
        except Exception as e:
            logger.error(f"Enhanced analysis failed: {str(e)}")
            # Return basic analysis on error
            return await self.analyze(url)
    
    def _generate_basic_campaign_angles(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic campaign angles without AI"""
        
        product_name = analysis.get("product_name", "Product")
        
        return {
            "primary_angle": f"Strategic competitive advantage through {product_name} intelligence",
            "alternative_angles": [
                f"Transform results with proven {product_name} insights",
                f"Competitive edge through {product_name} analysis", 
                f"Data-driven {product_name} strategies"
            ],
            "positioning_strategy": "Premium intelligence-driven solution",
            "target_audience_insights": ["Business owners", "Marketing professionals"],
            "messaging_framework": ["Problem identification", "Solution presentation", "Results proof"],
            "differentiation_strategy": "Intelligence-based competitive advantage"
        }
    
    def _generate_actionable_insights(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable insights"""
        
        product_name = analysis.get("product_name", "Product")
        
        return {
            "immediate_opportunities": [
                f"Create comparison content highlighting {product_name} advantages",
                "Develop content addressing market gaps",
                "Build authority through unique insights"
            ],
            "content_creation_ideas": [
                f"{product_name} competitive analysis blog posts",
                "Market insight newsletters",
                "Educational video content"
            ],
            "campaign_strategies": [
                "Multi-touch educational campaign",
                "Authority building content series",
                "Competitive positioning campaign"
            ],
            "testing_recommendations": [
                "A/B test different value propositions",
                "Test messaging variations",
                "Optimize conversion elements"
            ]
        }
    
    def _analyze_technical_aspects(self, url: str) -> Dict[str, Any]:
        """Analyze technical aspects"""
        
        return {
            "page_load_speed": "Analysis requires additional tools",
            "mobile_optimization": True,  # Assume modern sites are mobile-friendly
            "conversion_elements": [
                "Call-to-action buttons",
                "Trust signals",
                "Contact information"
            ],
            "trust_signals": [
                "Professional design",
                "Contact information",
                "Security indicators"
            ]
        }
    
    def _detect_video_content(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Basic video content detection"""
        
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
                "Video content detected" if has_video else "No video content found"
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
    }  # ✅ Clean syntax

        return text.strip()
    
    def _calculate_extraction_confidence(self, benefits: List, features: List, ingredients: List) -> float:
        """Calculate confidence in product extraction"""
    
        confidence = 0.3  # Base confidence
    
        if benefits:
            confidence += min(len(benefits) * 0.05, 0.3)
        if features:
            confidence += min(len(features) * 0.05, 0.25)
        if ingredients:
            confidence += min(len(ingredients) * 0.03, 0.15)
    
        return min(confidence, 1.0)
    
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
    
    # ✅ UPDATED: Include product name in AI analysis
    async def _extract_intelligence(self, structured_content: Dict[str, Any], url: str, product_name: str = "Product") -> Dict[str, Any]:
        """Use AI to extract competitive intelligence from structured content"""
        
        analysis_prompt = f"""
        Analyze this sales page content and extract competitive intelligence:

        URL: {url}
        Title: {structured_content['title']}
        Product Name: {product_name}
        Content Preview: {structured_content['content'][:2000]}
        Found Triggers: {structured_content['emotional_triggers']}
        Pricing Mentions: {structured_content['pricing_mentions']}
        
        Extract intelligence in these categories:

        1. OFFER INTELLIGENCE:
        - Main products/services offered (focus on {product_name})
        - Pricing strategy and structure
        - Bonuses and incentives
        - Guarantees and risk reversal
        - Value propositions

        2. PSYCHOLOGY INTELLIGENCE:
        - Emotional triggers used
        - Persuasion techniques
        - Target audience indicators
        - Pain points addressed
        - Social proof elements

        3. COMPETITIVE INTELLIGENCE:
        - Market positioning
        - Competitive advantages claimed
        - Potential weaknesses
        - Market gaps
        - Improvement opportunities

        4. CONTENT INTELLIGENCE:
        - Key messages
        - Content structure
        - Call-to-action strategy
        - Success stories mentioned

        5. CAMPAIGN SUGGESTIONS:
        - Alternative positioning ideas
        - Content opportunities
        - Marketing strategies

        Provide actionable insights that can be used for competitive campaigns.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert competitive intelligence analyst. Extract actionable insights for marketing campaigns."
                    },
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            ai_analysis = response.choices[0].message.content
            
            # Parse AI response into structured format
            intelligence = self._parse_ai_analysis(ai_analysis, structured_content)
            
            # Add metadata
            intelligence.update({
                "source_url": url,
                "page_title": structured_content["title"],
                "product_name": product_name,  # ✅ ADD: Include extracted product name
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "confidence_score": self._calculate_confidence_score(intelligence, structured_content),
                "raw_content": structured_content["content"][:1000]
            })
            
            return intelligence
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            # Return basic analysis if AI fails
            return self._fallback_analysis(structured_content, url, product_name)
    
    def _parse_ai_analysis(self, ai_response: str, structured_content: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured intelligence data"""
        
        # Simple parsing - extract insights from text
        lines = ai_response.split('\n')
        
        parsed_data = {
            "offer_intelligence": {
                "products": [],
                "pricing": structured_content.get("pricing_mentions", []),
                "bonuses": [],
                "guarantees": [],
                "value_propositions": []
            },
            "psychology_intelligence": {
                "emotional_triggers": structured_content.get("emotional_triggers", []),
                "pain_points": [],
                "target_audience": "General audience",
                "persuasion_techniques": []
            },
            "competitive_intelligence": {
                "opportunities": [],
                "gaps": [],
                "positioning": "Standard approach",
                "advantages": [],
                "weaknesses": []
            },
            "content_intelligence": {
                "key_messages": [structured_content.get("title", "")],
                "success_stories": [],
                "social_proof": structured_content.get("social_proof_elements", []),
                "content_structure": "Standard sales page"
            },
            "brand_intelligence": {
                "tone_voice": "Professional",
                "messaging_style": "Direct",
                "brand_positioning": "Market competitor"
            },
            "campaign_suggestions": []
        }
        
        # Extract insights from AI response
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify sections
            if "offer" in line.lower():
                current_section = "offer_intelligence"
            elif "psychology" in line.lower():
                current_section = "psychology_intelligence"
            elif "competitive" in line.lower():
                current_section = "competitive_intelligence"
            elif "content" in line.lower():
                current_section = "content_intelligence"
            elif "campaign" in line.lower() or "suggestion" in line.lower():
                current_section = "campaign_suggestions"
            
            # Extract bullet points
            if line.startswith(('-', '•', '*')) and current_section:
                insight = line[1:].strip()
                if insight:
                    if current_section == "campaign_suggestions":
                        parsed_data["campaign_suggestions"].append(insight)
                    elif "price" in insight.lower() or "$" in insight:
                        parsed_data["offer_intelligence"]["pricing"].append(insight)
                    elif "trigger" in insight.lower() or "emotion" in insight.lower():
                        parsed_data["psychology_intelligence"]["emotional_triggers"].append(insight)
                    elif "opportunity" in insight.lower() or "gap" in insight.lower():
                        parsed_data["competitive_intelligence"]["opportunities"].append(insight)
                    else:
                        # Add to appropriate section
                        if current_section in parsed_data:
                            if isinstance(parsed_data[current_section], dict):
                                # Add to a general list within the section
                                if "insights" not in parsed_data[current_section]:
                                    parsed_data[current_section]["insights"] = []
                                parsed_data[current_section]["insights"].append(insight)
        
        return parsed_data
    
    def _calculate_confidence_score(self, intelligence: Dict[str, Any], structured_content: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        
        score = 0.5  # Base score
        
        # Increase confidence based on data richness
        if intelligence.get("offer_intelligence", {}).get("pricing"):
            score += 0.1
        if intelligence.get("psychology_intelligence", {}).get("emotional_triggers"):
            score += 0.1
        if intelligence.get("competitive_intelligence", {}).get("opportunities"):
            score += 0.1
        if structured_content.get("pricing_mentions"):
            score += 0.1
        if structured_content.get("social_proof_elements"):
            score += 0.1
        if structured_content.get("word_count", 0) > 500:
            score += 0.1
        
        return min(score, 1.0)
    
    # ✅ UPDATED: Include product name in fallback analysis
    def _fallback_analysis(self, structured_content: Dict[str, Any], url: str, product_name: str = "Product") -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        
        return {
            "offer_intelligence": {
                "products": [product_name],  # ✅ Use extracted product name
                "pricing": structured_content.get("pricing_mentions", []),
                "bonuses": [],
                "guarantees": [],
                "value_propositions": ["Value proposition analysis available with AI"]
            },
            "psychology_intelligence": {
                "emotional_triggers": structured_content.get("emotional_triggers", []),
                "pain_points": ["Pain point analysis requires AI"],
                "target_audience": "General audience",
                "persuasion_techniques": ["Persuasion analysis requires AI"]
            },
            "competitive_intelligence": {
                "opportunities": ["Detailed competitive analysis requires AI"],
                "gaps": ["Gap analysis requires AI"],
                "positioning": "Standard market approach",
                "advantages": [],
                "weaknesses": []
            },
            "content_intelligence": {
                "key_messages": [structured_content["title"]],
                "success_stories": [],
                "social_proof": structured_content.get("social_proof_elements", []),
                "content_structure": f"Page with {structured_content.get('word_count', 0)} words"
            },
            "brand_intelligence": {
                "tone_voice": "Professional",
                "messaging_style": "Direct",
                "brand_positioning": "Market competitor"
            },
            "campaign_suggestions": [
                f"Create comparison content for {product_name}",
                "Address pricing strategy",
                "Develop unique positioning",
                "Build social proof campaigns"
            ],
            "source_url": url,
            "page_title": structured_content["title"],
            "product_name": product_name,  # ✅ ADD: Include extracted product name
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "confidence_score": 0.6,
            "raw_content": structured_content["content"][:1000],
            "analysis_note": "Basic analysis completed. Enhanced AI analysis requires OpenAI API key."
        }
    
    def _error_fallback_analysis(self, url: str, error_msg: str) -> Dict[str, Any]:
        """Fallback when analysis completely fails"""
        
        return {
            "offer_intelligence": {
                "products": [],
                "pricing": [],
                "bonuses": [],
                "guarantees": [],
                "value_propositions": []
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
            "analysis_note": f"Analysis failed: {error_msg}"
        }


# Enhanced analyzer class that extends the base
class EnhancedSalesPageAnalyzer(SalesPageAnalyzer):
    """Enhanced sales page analyzer with additional features"""
    
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
            
            # Add enhanced features
            enhanced_intelligence = {
                **base_analysis,
                "intelligence_id": f"intel_{uuid.uuid4().hex[:8]}",
                "analysis_depth": analysis_depth,
                "campaign_angles": self._generate_basic_campaign_angles(base_analysis),
                "actionable_insights": self._generate_actionable_insights(base_analysis),
                "technical_analysis": self._analyze_technical_aspects(url)
            }
            
            # Add VSL detection if requested (simplified for now)
            if include_vsl_detection:
                enhanced_intelligence["vsl_analysis"] = self._detect_video_content(base_analysis)
            
            return enhanced_intelligence
            
        except Exception as e:
            logger.error(f"Enhanced analysis failed: {str(e)}")
            # Return basic analysis on error
            return await self.analyze(url)
    
    def _generate_basic_campaign_angles(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic campaign angles without AI"""
        
        product_name = analysis.get("product_name", "Product")
        
        return {
            "primary_angle": f"Strategic competitive advantage through {product_name} intelligence",
            "alternative_angles": [
                f"Transform results with proven {product_name} insights",
                f"Competitive edge through {product_name} analysis", 
                f"Data-driven {product_name} strategies"
            ],
            "positioning_strategy": "Premium intelligence-driven solution",
            "target_audience_insights": ["Business owners", "Marketing professionals"],
            "messaging_framework": ["Problem identification", "Solution presentation", "Results proof"],
            "differentiation_strategy": "Intelligence-based competitive advantage"
        }
    
    def _generate_actionable_insights(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable insights"""
        
        product_name = analysis.get("product_name", "Product")
        
        return {
            "immediate_opportunities": [
                f"Create comparison content highlighting {product_name} advantages",
                "Develop content addressing market gaps",
                "Build authority through unique insights"
            ],
            "content_creation_ideas": [
                f"{product_name} competitive analysis blog posts",
                "Market insight newsletters",
                "Educational video content"
            ],
            "campaign_strategies": [
                "Multi-touch educational campaign",
                "Authority building content series",
                "Competitive positioning campaign"
            ],
            "testing_recommendations": [
                "A/B test different value propositions",
                "Test messaging variations",
                "Optimize conversion elements"
            ]
        }
    
    def _analyze_technical_aspects(self, url: str) -> Dict[str, Any]:
        """Analyze technical aspects"""
        
        return {
            "page_load_speed": "Analysis requires additional tools",
            "mobile_optimization": True,  # Assume modern sites are mobile-friendly
            "conversion_elements": [
                "Call-to-action buttons",
                "Trust signals",
                "Contact information"
            ],
            "trust_signals": [
                "Professional design",
                "Contact information",
                "Security indicators"
            ]
        }
    
    def _detect_video_content(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Basic video content detection"""
        
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
                "Video content detected" if has_video else "No video content found"
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