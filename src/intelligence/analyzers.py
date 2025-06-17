# src/intelligence/analyzers.py
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

logger = logging.getLogger(__name__)

class SalesPageAnalyzer:
    """Analyze competitor sales pages for offers, psychology, and opportunities"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
    
    async def analyze(self, url: str) -> Dict[str, Any]:
        """Complete sales page analysis"""
        
        try:
            # Step 1: Scrape the page content
            page_content = await self._scrape_page(url)
            
            # Step 2: Extract structured content
            structured_content = await self._extract_content_structure(page_content)
            
            # Step 3: AI-powered intelligence extraction
            intelligence = await self._extract_intelligence(structured_content, url)
            
            return intelligence
            
        except Exception as e:
            logger.error(f"Sales page analysis failed for {url}: {str(e)}")
            raise e
    
    async def _scrape_page(self, url: str) -> Dict[str, str]:
        """Advanced web scraping with JavaScript rendering support"""
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to fetch page: HTTP {response.status}")
                    
                    html_content = await response.text()
                    
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Extract key elements
                    title = soup.find('title')
                    title_text = title.get_text().strip() if title else "No title"
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Extract text content
                    body_text = soup.get_text()
                    
                    # Clean up text
                    lines = (line.strip() for line in body_text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    clean_text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    return {
                        "title": title_text,
                        "content": clean_text,
                        "html": html_content,
                        "url": url
                    }
                    
            except Exception as e:
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
            prices.extend(matches)
        
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
                social_proof.extend(matches)
        
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
        Analyze this sales page content and extract competitive intelligence. Focus on actionable insights for creating competing campaigns.

        URL: {url}
        Title: {structured_content['title']}
        Content: {structured_content['content'][:4000]}  # Limit for token efficiency
        
        Extract and structure the following intelligence:

        1. OFFER INTELLIGENCE:
        - Main products/services and pricing
        - Bonuses and incentives offered
        - Guarantees and risk reversal
        - Payment options and plans
        - Value propositions and unique selling points

        2. PSYCHOLOGY INTELLIGENCE:
        - Primary emotional triggers used
        - Persuasion techniques identified
        - Target audience characteristics
        - Pain points addressed
        - Desires and aspirations appealed to
        - Objections handled

        3. COMPETITIVE INTELLIGENCE:
        - Market positioning approach
        - Competitive advantages claimed
        - Weaknesses or gaps identified
        - Opportunities for differentiation
        - Unaddressed pain points
        - Missing value propositions

        4. CONTENT INTELLIGENCE:
        - Key messages and talking points
        - Success stories or case studies
        - Statistics and social proof
        - Content structure and flow
        - Call-to-action strategies

        5. CAMPAIGN OPPORTUNITIES:
        - Alternative positioning angles
        - Content creation opportunities
        - Marketing channel suggestions
        - Improvement opportunities

        Return as structured JSON with high confidence insights only.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert competitive intelligence analyst specializing in affiliate marketing and sales psychology. Extract actionable insights that can be used to create competing campaigns."
                    },
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            ai_analysis = response.choices[0].message.content
            
            # Parse AI response into structured format
            intelligence = self._parse_ai_analysis(ai_analysis, structured_content)
            
            # Add metadata
            intelligence.update({
                "source_url": url,
                "page_title": structured_content["title"],
                "analysis_timestamp": asyncio.get_event_loop().time(),
                "confidence_score": self._calculate_confidence_score(intelligence, structured_content),
                "raw_content": structured_content["content"][:1000]  # Store sample
            })
            
            return intelligence
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            # Return basic analysis if AI fails
            return self._fallback_analysis(structured_content, url)
    
    def _parse_ai_analysis(self, ai_response: str, structured_content: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured intelligence data"""
        
        try:
            # Try to extract JSON from AI response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                # Fallback: Parse text response into structure
                parsed_data = self._parse_text_analysis(ai_response)
            
            return {
                "offer_intelligence": parsed_data.get("offer_intelligence", {}),
                "psychology_intelligence": parsed_data.get("psychology_intelligence", {}),
                "competitive_intelligence": parsed_data.get("competitive_intelligence", {}),
                "content_intelligence": parsed_data.get("content_intelligence", {}),
                "brand_intelligence": parsed_data.get("brand_intelligence", {}),
                "campaign_suggestions": parsed_data.get("campaign_opportunities", [])
            }
            
        except json.JSONDecodeError:
            # Fallback to text parsing
            return self._parse_text_analysis(ai_response)
    
    def _parse_text_analysis(self, text_response: str) -> Dict[str, Any]:
        """Fallback text parsing when JSON parsing fails"""
        
        # Extract key sections from text response
        sections = {
            "offer_intelligence": {"products": [], "pricing": [], "bonuses": []},
            "psychology_intelligence": {"emotional_triggers": [], "pain_points": []},
            "competitive_intelligence": {"opportunities": [], "gaps": []},
            "content_intelligence": {"key_messages": [], "success_stories": []},
            "campaign_suggestions": []
        }
        
        # Simple pattern matching for key insights
        lines = text_response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Identify section headers
            if "offer" in line.lower():
                current_section = "offer_intelligence"
            elif "psychology" in line.lower():
                current_section = "psychology_intelligence"
            elif "competitive" in line.lower():
                current_section = "competitive_intelligence"
            elif "content" in line.lower():
                current_section = "content_intelligence"
            elif "campaign" in line.lower() or "opportunity" in line.lower():
                current_section = "campaign_suggestions"
            
            # Extract bullet points and insights
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                insight = line[1:].strip()
                if current_section == "campaign_suggestions":
                    sections["campaign_suggestions"].append(insight)
                elif current_section and insight:
                    # Add to appropriate subsection
                    if "price" in insight.lower() or "$" in insight:
                        sections["offer_intelligence"].setdefault("pricing", []).append(insight)
                    elif "emotion" in insight.lower() or "feel" in insight.lower():
                        sections["psychology_intelligence"].setdefault("emotional_triggers", []).append(insight)
                    elif "gap" in insight.lower() or "opportunity" in insight.lower():
                        sections["competitive_intelligence"].setdefault("opportunities", []).append(insight)
                    else:
                        sections["content_intelligence"].setdefault("key_messages", []).append(insight)
        
        return sections
    
    def _calculate_confidence_score(self, intelligence: Dict[str, Any], structured_content: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        
        score = 0.5  # Base score
        
        # Increase confidence based on data richness
        if intelligence.get("offer_intelligence", {}).get("products"):
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
        """Fallback analysis when AI fails"""
        
        return {
            "offer_intelligence": {
                "products": ["Product identified from: " + structured_content["title"]],
                "pricing": structured_content.get("pricing_mentions", []),
                "bonuses": []
            },
            "psychology_intelligence": {
                "emotional_triggers": structured_content.get("emotional_triggers", []),
                "pain_points": [],
                "target_audience": "General audience"
            },
            "competitive_intelligence": {
                "opportunities": ["Analyze competitor positioning"],
                "gaps": ["Identify improvement areas"],
                "positioning": "Standard market approach"
            },
            "content_intelligence": {
                "key_messages": [structured_content["title"]],
                "success_stories": [],
                "social_proof": structured_content.get("social_proof_elements", [])
            },
            "brand_intelligence": {
                "tone_voice": "Professional",
                "messaging_style": "Direct"
            },
            "campaign_suggestions": [
                "Create comparison content",
                "Address identified gaps",
                "Develop unique positioning"
            ],
            "source_url": url,
            "page_title": structured_content["title"],
            "confidence_score": 0.4,
            "raw_content": structured_content["content"][:1000]
        }


class DocumentAnalyzer:
    """Analyze uploaded documents for intelligence extraction"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
    
    async def analyze_document(self, file_content: bytes, file_extension: str) -> Dict[str, Any]:
        """Analyze uploaded document and extract intelligence"""
        
        try:
            # Extract text based on file type
            if file_extension == 'pdf':
                text_content = await self._extract_pdf_text(file_content)
            elif file_extension in ['docx', 'doc']:
                text_content = await self._extract_word_text(file_content)
            elif file_extension in ['pptx', 'ppt']:
                text_content = await self._extract_powerpoint_text(file_content)
            elif file_extension == 'txt':
                text_content = file_content.decode('utf-8', errors='ignore')
            else:
                raise Exception(f"Unsupported file type: {file_extension}")
            
            # Analyze extracted text
            intelligence = await self._analyze_document_content(text_content)
            
            return intelligence
            
        except Exception as e:
            logger.error(f"Document analysis failed: {str(e)}")
            raise e
    
    async def _extract_pdf_text(self, pdf_content: bytes) -> str:
        """Extract text from PDF files"""
        try:
            import PyPDF2
            from io import BytesIO
            
            pdf_file = BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
            
        except ImportError:
            raise Exception("PyPDF2 not installed. Please install: pip install PyPDF2")
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    async def _extract_word_text(self, word_content: bytes) -> str:
        """Extract text from Word documents"""
        try:
            import docx
            from io import BytesIO
            
            doc_file = BytesIO(word_content)
            doc = docx.Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text
            
        except ImportError:
            raise Exception("python-docx not installed. Please install: pip install python-docx")
        except Exception as e:
            raise Exception(f"Word extraction failed: {str(e)}")
    
    async def _extract_powerpoint_text(self, ppt_content: bytes) -> str:
        """Extract text from PowerPoint presentations"""
        try:
            from pptx import Presentation
            from io import BytesIO
            
            ppt_file = BytesIO(ppt_content)
            prs = Presentation(ppt_file)
            
            text = ""
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + "\n"
            
            return text
            
        except ImportError:
            raise Exception("python-pptx not installed. Please install: pip install python-pptx")
        except Exception as e:
            raise Exception(f"PowerPoint extraction failed: {str(e)}")
    
    async def _analyze_document_content(self, content: str) -> Dict[str, Any]:
        """Analyze extracted document content"""
        
        analysis_prompt = f"""
        Analyze this document content and extract marketing intelligence:

        Content: {content[:3000]}  # Limit for efficiency
        
        Extract:
        1. Key insights and strategies
        2. Market opportunities mentioned
        3. Competitive advantages discussed
        4. Target audience characteristics
        5. Success metrics and data points
        6. Content creation opportunities
        
        Focus on actionable intelligence for campaign creation.
        Return as structured data.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting marketing intelligence from business documents. Focus on actionable insights for campaign creation."
                    },
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            ai_analysis = response.choices[0].message.content
            
            return {
                "content_intelligence": {
                    "key_insights": self._extract_key_insights(ai_analysis),
                    "strategies_mentioned": self._extract_strategies(ai_analysis),
                    "data_points": self._extract_data_points(content)
                },
                "competitive_intelligence": {
                    "opportunities": self._extract_opportunities(ai_analysis),
                    "market_gaps": []
                },
                "content_opportunities": self._generate_content_opportunities(ai_analysis),
                "extracted_text": content[:1000],
                "confidence_score": 0.7
            }
            
        except Exception as e:
            logger.error(f"Document AI analysis failed: {str(e)}")
            return self._fallback_document_analysis(content)
    
    def _extract_key_insights(self, ai_response: str) -> List[str]:
        """Extract key insights from AI response"""
        insights = []
        lines = ai_response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                insight = line[1:].strip()
                if len(insight) > 10:  # Filter out very short items
                    insights.append(insight)
        
        return insights[:10]  # Limit to top 10 insights
    
    def _extract_strategies(self, ai_response: str) -> List[str]:
        """Extract strategies from AI response"""
        strategies = []
        
        # Look for strategy-related keywords
        strategy_keywords = ['strategy', 'approach', 'method', 'technique', 'tactic']
        lines = ai_response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in strategy_keywords):
                if line.strip() and len(line.strip()) > 20:
                    strategies.append(line.strip())
        
        return strategies[:5]
    
    def _extract_data_points(self, content: str) -> List[str]:
        """Extract numerical data points from content"""
        data_points = []
        
        # Pattern for percentages and numbers
        patterns = [
            r'\d+%',  # Percentages
            r'\$[\d,]+(?:\.\d{2})?',  # Money amounts
            r'\d+(?:,\d+)*\s+(?:users|customers|clients|sales)',  # User counts
            r'increased?\s+by\s+\d+%',  # Growth percentages
            r'ROI\s+of\s+\d+%'  # ROI figures
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            data_points.extend(matches)
        
        return list(set(data_points))[:10]  # Unique data points, limited
    
    def _extract_opportunities(self, ai_response: str) -> List[str]:
        """Extract opportunities from AI response"""
        opportunities = []
        
        opportunity_keywords = ['opportunity', 'potential', 'gap', 'untapped', 'underserved']
        lines = ai_response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in opportunity_keywords):
                if line.strip() and len(line.strip()) > 15:
                    opportunities.append(line.strip())
        
        return opportunities[:5]
    
    def _generate_content_opportunities(self, ai_response: str) -> List[str]:
        """Generate content creation opportunities"""
        return [
            "Blog post series based on key insights",
            "Social media content from data points",
            "Email sequence using document strategies",
            "Infographic from statistics mentioned",
            "Video content explaining methodologies"
        ]
    
    def _fallback_document_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback analysis when AI fails"""
        
        return {
            "content_intelligence": {
                "key_insights": ["Document contains valuable market insights"],
                "strategies_mentioned": ["Strategic approaches identified"],
                "data_points": self._extract_data_points(content)
            },
            "competitive_intelligence": {
                "opportunities": ["Analyze document for competitive advantages"],
                "market_gaps": []
            },
            "content_opportunities": [
                "Create content based on document insights",
                "Develop case studies from examples",
                "Extract quotes for social media"
            ],
            "extracted_text": content[:1000],
            "confidence_score": 0.5
        }


class WebAnalyzer:
    """Analyze general websites and web content"""
    
    def __init__(self):
        self.sales_page_analyzer = SalesPageAnalyzer()
    
    async def analyze(self, url: str) -> Dict[str, Any]:
        """Analyze general website content"""
        
        # For now, delegate to sales page analyzer
        # Can be extended with specific web analysis logic
        return await self.sales_page_analyzer.analyze(url)