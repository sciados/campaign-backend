# src/intelligence/analyzers.py - FIXED VERSION
"""
Intelligence analysis engines - The core AI that extracts competitive insights
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
            
            # Step 3: AI-powered intelligence extraction (if available)
            if self.openai_client:
                intelligence = await self._extract_intelligence(structured_content, url)
                logger.info("AI intelligence extraction completed")
            else:
                intelligence = self._fallback_analysis(structured_content, url)
                logger.info("Using fallback analysis (no OpenAI key)")
            
            return intelligence
            
        except Exception as e:
            logger.error(f"Sales page analysis failed for {url}: {str(e)}")
            # Return a fallback response instead of raising
            return self._error_fallback_analysis(url, str(e))
    
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
        """Extract and structure key page elements"""
        
        content = page_content["content"]
        
        # Extract pricing patterns
        price_patterns = [
            r'\$[\d,]+(?:\.\d{2})?',  # $99.99, $1,299
            r'£[\d,]+(?:\.\d{2})?',  # £99.99
            r'€[\d,]+(?:\.\d{2})?',  # €99.99
            r'[\d,]+\s*dollars?',     # 99 dollars
            r'free(?:\s+trial)?',     # free, free trial
            r'money\s*back\s*guarantee',  # money back guarantee
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            prices.extend(matches[:5])  # Limit to prevent too many matches
        
        # Extract emotional triggers and power words
        emotional_triggers = [
            "limited time", "exclusive", "secret", "breakthrough", "guaranteed",
            "proven", "instant", "fast", "easy", "simple", "powerful",
            "revolutionary", "amazing", "incredible", "shocking", "urgent"
        ]
        
        found_triggers = []
        for trigger in emotional_triggers:
            if trigger.lower() in content.lower():
                found_triggers.append(trigger)
        
        # Extract social proof elements
        social_proof_patterns = [
            r'(\d+(?:,\d+)*)\s*(?:customers?|users?|clients?|members?)',
            r'testimonials?',
            r'reviews?',
            r'ratings?',
            r'(\d+)\s*stars?',
            r'trusted\s+by',
            r'as\s+seen\s+(?:on|in)'
        ]
        
        social_proof = []
        for pattern in social_proof_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                social_proof.extend([str(match) for match in matches][:3])
        
        return {
            "title": page_content["title"],
            "content": content,
            "url": page_content["url"],
            "pricing_mentions": prices,
            "emotional_triggers": found_triggers,
            "social_proof_elements": social_proof,
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
    
    async def _extract_intelligence(self, structured_content: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Use AI to extract competitive intelligence from structured content"""
        
        analysis_prompt = f"""
        Analyze this sales page content and extract competitive intelligence:

        URL: {url}
        Title: {structured_content['title']}
        Content Preview: {structured_content['content'][:2000]}
        Found Triggers: {structured_content['emotional_triggers']}
        Pricing Mentions: {structured_content['pricing_mentions']}
        
        Extract intelligence in these categories:

        1. OFFER INTELLIGENCE:
        - Main products/services offered
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
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "confidence_score": self._calculate_confidence_score(intelligence, structured_content),
                "raw_content": structured_content["content"][:1000]
            })
            
            return intelligence
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            # Return basic analysis if AI fails
            return self._fallback_analysis(structured_content, url)
    
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
    
    def _fallback_analysis(self, structured_content: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        
        return {
            "offer_intelligence": {
                "products": [f"Product from: {structured_content['title']}"],
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
                "Create comparison content",
                "Address pricing strategy",
                "Develop unique positioning",
                "Build social proof campaigns"
            ],
            "source_url": url,
            "page_title": structured_content["title"],
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
        
        return {
            "primary_angle": "Strategic competitive advantage through intelligence",
            "alternative_angles": [
                "Transform results with proven insights",
                "Competitive edge through market analysis", 
                "Data-driven growth strategies"
            ],
            "positioning_strategy": "Premium intelligence-driven solution",
            "target_audience_insights": ["Business owners", "Marketing professionals"],
            "messaging_framework": ["Problem identification", "Solution presentation", "Results proof"],
            "differentiation_strategy": "Intelligence-based competitive advantage"
        }
    
    def _generate_actionable_insights(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable insights"""
        
        return {
            "immediate_opportunities": [
                "Create comparison content highlighting advantages",
                "Develop content addressing market gaps",
                "Build authority through unique insights"
            ],
            "content_creation_ideas": [
                "Competitive analysis blog posts",
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