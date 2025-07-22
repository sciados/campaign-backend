# src/intelligence/utils/product_name_fix.py
"""
UNIVERSAL Product Name Extraction System
🎯 Designed to extract product names from thousands of different sales pages
✅ Works with any niche: health, finance, software, courses, etc.
✅ Handles multiple product name formats and patterns
✅ Robust against AI hallucinations and fallback content
"""

import re
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from urllib.parse import urlparse
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

class UniversalProductExtractor:
    """Universal product name extractor for any sales page"""
    
    def __init__(self):
        # Universal product name patterns (works for any niche)
        self.universal_patterns = [
            # Direct mentions with action words
            r'(?:try|get|use|discover|introducing|meet|welcome\s+to|buy|order|download)\s+([A-Z][a-zA-Z]{3,20}(?:\s+[A-Z][a-zA-Z]{2,15}){0,2})',
            
            # Product helps/supports patterns
            r'([A-Z][a-zA-Z]{3,20}(?:\s+[A-Z][a-zA-Z]{2,15}){0,2})\s+(?:helps?|supports?|provides?|delivers?|works?|offers?|gives?)',
            
            # Possessive and descriptive patterns
            r'(?:with|using|from|about)\s+([A-Z][a-zA-Z]{3,20}(?:\s+[A-Z][a-zA-Z]{2,15}){0,2})',
            
            # Trademark and quoted patterns
            r'([A-Z][a-zA-Z]{3,20}(?:\s+[A-Z][a-zA-Z]{2,15}){0,2})\s*[™®©]',
            r'"([A-Z][a-zA-Z]{3,20}(?:\s+[A-Z][a-zA-Z]{2,15}){0,2})"',
            r"'([A-Z][a-zA-Z]{3,20}(?:\s+[A-Z][a-zA-Z]{2,15}){0,2})'",
            
            # Emotional/impact patterns
            r'(?:difference|benefits?|power\s+of|magic\s+of|secret\s+of)\s+([A-Z][a-zA-Z]{3,20}(?:\s+[A-Z][a-zA-Z]{2,15}){0,2})',
            
            # Business/program patterns
            r'([A-Z][a-zA-Z]{3,20}(?:\s+[A-Z][a-zA-Z]{2,15}){0,2})\s+(?:program|system|method|course|training|formula|solution|protocol)',
            
            # Results/testimonial patterns
            r'(?:thanks\s+to|because\s+of|after\s+using)\s+([A-Z][a-zA-Z]{3,20}(?:\s+[A-Z][a-zA-Z]{2,15}){0,2})',
            
            # Call-to-action patterns
            r'(?:click|tap)\s+(?:here\s+)?(?:to\s+)?(?:get|try|order|access|download)\s+([A-Z][a-zA-Z]{3,20}(?:\s+[A-Z][a-zA-Z]{2,15}){0,2})'
        ]
        
        # Common product suffixes across all niches
        self.product_suffixes = [
            # Health/supplement suffixes
            'Pure', 'Max', 'Plus', 'Pro', 'Ultra', 'Advanced', 'Complete', 'Elite', 'Premium',
            'Sculpt', 'Burn', 'Boost', 'Guard', 'Shield', 'Force', 'Power', 'Flow',
            'Cleanse', 'Detox', 'Restore', 'Repair', 'Renew', 'Revive',
            
            # Business/software suffixes  
            'Pro', 'Suite', 'Master', 'Academy', 'University', 'Blueprint', 'Secrets',
            'Method', 'System', 'Formula', 'Protocol', 'Strategy', 'Mastery',
            
            # Course/training suffixes
            'Course', 'Training', 'Bootcamp', 'Workshop', 'Masterclass', 'Program',
            
            # Generic premium suffixes
            'Gold', 'Platinum', 'Diamond', 'VIP', 'Executive', 'Deluxe'
        ]
        
        # Universal false positive filters
        self.false_positives = {
            # Generic words that appear in many contexts
            'your', 'this', 'that', 'here', 'there', 'what', 'when', 'where', 'how',
            'the', 'and', 'or', 'but', 'with', 'for', 'from', 'about', 'into',
            'product', 'company', 'business', 'service', 'solution', 'system',
            'page', 'site', 'website', 'home', 'main', 'click', 'buy', 'order',
            'get', 'try', 'start', 'join', 'sign', 'login', 'register',
            'free', 'now', 'today', 'here', 'more', 'best', 'new', 'top',
            'health', 'natural', 'effective', 'powerful', 'amazing', 'incredible',
            'guaranteed', 'proven', 'tested', 'safe', 'organic', 'premium',
            'exclusive', 'limited', 'special', 'bonus', 'discount', 'offer',
            'mobile', 'email', 'phone', 'number', 'name', 'address', 'city',
            'state', 'country', 'zip', 'code', 'submit', 'send', 'contact',
            'privacy', 'terms', 'policy', 'legal', 'copyright', 'rights',
            'island', 'difference', 'benefits', 'results', 'success', 'power',
            'magic', 'secret', 'formula', 'method', 'way', 'steps', 'guide'
        }
        
        # Temporal and location words to filter
        self.temporal_location_words = {
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'january', 'february', 'march', 'april', 'may', 'june', 'july',
            'august', 'september', 'october', 'november', 'december',
            'morning', 'afternoon', 'evening', 'night', 'today', 'tomorrow',
            'yesterday', 'week', 'month', 'year', 'time', 'date',
            'america', 'europe', 'asia', 'africa', 'australia', 'canada',
            'united', 'states', 'kingdom', 'france', 'germany', 'italy'
        }

    def extract_product_name(self, intelligence: Dict[str, Any]) -> str:
        """
        Universal product name extraction from any sales page
        
        Priority order (designed for maximum accuracy across all niches):
        1. URL-based extraction (domain names often contain product names)
        2. Raw content pattern matching (highest accuracy)
        3. Emotional trigger contexts (catches testimonial mentions)
        4. Page title analysis (often contains product name)
        5. Multiple content source analysis
        6. AI-generated data (lowest priority due to hallucination risk)
        """
        
        logger.info("🔍 Starting universal product name extraction...")
        
        all_candidates = []
        extraction_sources = {}
        
        # Strategy 1: URL-based extraction (HIGH CONFIDENCE)
        source_url = intelligence.get("source_url") or intelligence.get("url")
        if source_url:
            url_candidates = self._extract_from_url(source_url)
            if url_candidates:
                all_candidates.extend(url_candidates)
                extraction_sources["url"] = url_candidates
                logger.debug(f"URL candidates: {url_candidates}")
        
        # Strategy 2: Raw content pattern analysis (HIGHEST CONFIDENCE)
        raw_content = intelligence.get("raw_content") or intelligence.get("content")
        if raw_content:
            content_candidates = self._extract_from_content(raw_content)
            if content_candidates:
                all_candidates.extend(content_candidates)
                extraction_sources["content"] = content_candidates
                logger.debug(f"Content candidates: {content_candidates[:5]}")
        
        # Strategy 3: Emotional trigger contexts (HIGH CONFIDENCE)
        context_candidates = self._extract_from_emotional_contexts(intelligence)
        if context_candidates:
            all_candidates.extend(context_candidates)
            extraction_sources["emotional_context"] = context_candidates
            logger.debug(f"Emotional context candidates: {context_candidates}")
        
        # Strategy 4: Page title analysis (MEDIUM CONFIDENCE)
        title_candidates = self._extract_from_titles(intelligence)
        if title_candidates:
            all_candidates.extend(title_candidates)
            extraction_sources["title"] = title_candidates
            logger.debug(f"Title candidates: {title_candidates}")
        
        # Strategy 5: Multi-source content analysis (MEDIUM CONFIDENCE)
        multi_candidates = self._extract_from_multiple_sources(intelligence)
        if multi_candidates:
            all_candidates.extend(multi_candidates)
            extraction_sources["multi_source"] = multi_candidates
            logger.debug(f"Multi-source candidates: {multi_candidates}")
        
        # Strategy 6: Scientific/credibility content (MEDIUM CONFIDENCE)
        scientific_candidates = self._extract_from_scientific_content(intelligence)
        if scientific_candidates:
            all_candidates.extend(scientific_candidates)
            extraction_sources["scientific"] = scientific_candidates
            logger.debug(f"Scientific candidates: {scientific_candidates}")
        
        # Strategy 7: AI-generated data (LOWEST CONFIDENCE - check last)
        ai_candidates = self._extract_from_ai_data(intelligence)
        if ai_candidates:
            all_candidates.extend(ai_candidates)
            extraction_sources["ai_generated"] = ai_candidates
            logger.debug(f"AI-generated candidates: {ai_candidates}")
        
        # Filter and rank all candidates
        filtered_candidates = self._filter_candidates(all_candidates)
        best_candidate = self._rank_and_select_best(filtered_candidates, extraction_sources, intelligence)
        
        logger.info(f"🎯 Universal extraction result: '{best_candidate}'")
        logger.info(f"📊 Total candidates: {len(all_candidates)}, filtered: {len(filtered_candidates)}")
        logger.info(f"📋 Sources used: {list(extraction_sources.keys())}")
        
        return best_candidate

    def _extract_from_url(self, url: str) -> List[str]:
        """Extract product names from URL structure"""
        candidates = []
        
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '')
            
            # Extract from domain parts
            domain_parts = domain.split('.')
            for part in domain_parts:
                if len(part) > 4 and part not in ['com', 'net', 'org', 'co', 'uk', 'io', 'app']:
                    # Handle compound words in domains
                    if 'get' in part and len(part) > 6:
                        # getproductnamenow.com pattern
                        remainder = part.replace('get', '').replace('now', '')
                        if len(remainder) > 4:
                            candidates.append(self._clean_product_name(remainder))
                    elif len(part) > 6:
                        candidates.append(self._clean_product_name(part))
            
            # Extract from path
            path_parts = [p for p in parsed.path.split('/') if p and len(p) > 3]
            for part in path_parts:
                clean_part = re.sub(r'[^a-zA-Z]', '', part)
                if len(clean_part) > 4:
                    candidates.append(self._clean_product_name(clean_part))
        
        except Exception as e:
            logger.debug(f"URL extraction error: {e}")
        
        return [c for c in candidates if self._is_valid_product_name(c)]

    def _extract_from_content(self, content: str) -> List[str]:
        """Extract product names using universal patterns"""
        if not content or len(content) < 20:
            return []
        
        candidates = []
        
        # Apply all universal patterns
        for pattern in self.universal_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                
                cleaned = self._clean_product_name(match.strip())
                if cleaned and self._is_valid_product_name(cleaned):
                    candidates.append(cleaned)
        
        # Look for branded product patterns with suffixes
        for suffix in self.product_suffixes:
            pattern = rf'\b([A-Z][a-zA-Z]{{2,15}}{re.escape(suffix)})\b'
            matches = re.findall(pattern, content)
            for match in matches:
                cleaned = self._clean_product_name(match)
                if cleaned and self._is_valid_product_name(cleaned):
                    candidates.append(cleaned)
        
        # Look for CamelCase product names
        camelcase_pattern = r'\b([A-Z][a-z]+[A-Z][a-z]+(?:[A-Z][a-z]+)?)\b'
        camelcase_matches = re.findall(camelcase_pattern, content)
        for match in camelcase_matches:
            cleaned = self._clean_product_name(match)
            if cleaned and self._is_valid_product_name(cleaned):
                candidates.append(cleaned)
        
        return candidates

    def _extract_from_emotional_contexts(self, intelligence: Dict[str, Any]) -> List[str]:
        """Extract from emotional trigger contexts and testimonials"""
        candidates = []
        
        # Psychology intelligence emotional triggers
        psych_intel = intelligence.get("psychology_intelligence", {})
        if isinstance(psych_intel, dict):
            triggers = psych_intel.get("emotional_triggers", [])
            if isinstance(triggers, list):
                for trigger in triggers:
                    if isinstance(trigger, dict) and "context" in trigger:
                        context = trigger.get("context", "")
                        if isinstance(context, str) and len(context) > 10:
                            context_candidates = self._extract_from_content(context)
                            candidates.extend(context_candidates)
        
        # Content intelligence key messages
        content_intel = intelligence.get("content_intelligence", {})
        if isinstance(content_intel, dict):
            key_messages = content_intel.get("key_messages", [])
            if isinstance(key_messages, list):
                for message in key_messages:
                    if isinstance(message, str) and len(message) > 10:
                        message_candidates = self._extract_from_content(message)
                        candidates.extend(message_candidates)
            
            # Success stories
            success_stories = content_intel.get("success_stories", [])
            if isinstance(success_stories, list):
                for story in success_stories:
                    if isinstance(story, str) and len(story) > 10:
                        story_candidates = self._extract_from_content(story)
                        candidates.extend(story_candidates)
        
        return candidates

    def _extract_from_titles(self, intelligence: Dict[str, Any]) -> List[str]:
        """Extract from various title fields"""
        candidates = []
        
        title_sources = [
            intelligence.get("page_title"),
            intelligence.get("source_title"), 
            intelligence.get("title")
        ]
        
        for title in title_sources:
            if title and isinstance(title, str) and len(title.strip()) > 3:
                title = title.strip()
                
                # Skip obviously generic titles
                generic_titles = [
                    'stock up - exclusive offer', 'exclusive offer', 'special offer',
                    'limited time offer', 'get yours now', 'order now', 'buy now',
                    'official website', 'home page', 'welcome'
                ]
                
                if title.lower() not in generic_titles:
                    title_candidates = self._extract_from_content(title)
                    candidates.extend(title_candidates)
        
        return candidates

    def _extract_from_multiple_sources(self, intelligence: Dict[str, Any]) -> List[str]:
        """Extract from multiple content sources and cross-reference"""
        all_text_sources = []
        
        # Collect all text from various intelligence sections
        text_sources = [
            intelligence.get("raw_content", ""),
            intelligence.get("content", ""),
        ]
        
        # Add brand intelligence text
        brand_intel = intelligence.get("brand_intelligence", {})
        if isinstance(brand_intel, dict):
            brand_positioning = brand_intel.get("brand_positioning", "")
            if isinstance(brand_positioning, str):
                text_sources.append(brand_positioning)
        
        # Combine and analyze
        combined_text = " ".join(text_sources)
        if len(combined_text) > 50:
            return self._extract_from_content(combined_text)
        
        return []

    def _extract_from_scientific_content(self, intelligence: Dict[str, Any]) -> List[str]:
        """Extract from scientific and credibility content"""
        candidates = []
        
        scientific_intel = intelligence.get("scientific_intelligence", {})
        if isinstance(scientific_intel, dict):
            scientific_backing = scientific_intel.get("scientific_backing", [])
            if isinstance(scientific_backing, list):
                for backing in scientific_backing[:3]:  # Limit to first 3 to avoid noise
                    if isinstance(backing, str) and len(backing) > 20:
                        science_candidates = self._extract_from_content(backing)
                        candidates.extend(science_candidates)
        
        return candidates

    def _extract_from_ai_data(self, intelligence: Dict[str, Any]) -> List[str]:
        """Extract from AI-generated data (lowest priority due to hallucination risk)"""
        candidates = []
        
        # Direct product name fields
        direct_sources = [
            intelligence.get("product_name"),
            intelligence.get("extracted_product_name"),
            intelligence.get("brand_name")
        ]
        
        for source in direct_sources:
            if source and isinstance(source, str) and len(source.strip()) > 1:
                cleaned = self._clean_product_name(source.strip())
                if cleaned and self._is_valid_product_name(cleaned):
                    candidates.append(cleaned)
        
        # Offer intelligence products (with heavy filtering)
        offer_intel = intelligence.get("offer_intelligence", {})
        if isinstance(offer_intel, dict):
            products = offer_intel.get("products", [])
            if isinstance(products, list):
                for product in products[:2]:  # Only check first 2 to avoid AI spam
                    if product and isinstance(product, str):
                        cleaned = self._clean_product_name(product.strip())
                        # Extra strict filtering for AI data
                        if (cleaned and 
                            self._is_valid_product_name(cleaned) and 
                            len(cleaned) > 4 and
                            cleaned.lower() not in self.false_positives):
                            candidates.append(cleaned)
        
        return candidates

    def _clean_product_name(self, name: str) -> str:
        """Clean and normalize product names universally"""
        if not name:
            return ""
        
        # Remove extra whitespace and special characters
        name = re.sub(r'[^\w\s\-]', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Handle known compound products
        known_compounds = {
            'aquasculpt': 'AquaSculpt',
            'liverpure': 'LiverPure', 
            'metabolflex': 'MetaboFlex',
            'prostastream': 'ProstaStream',
            'bloodpressure': 'BloodPressure'
        }
        
        name_lower = name.lower().replace(' ', '')
        if name_lower in known_compounds:
            return known_compounds[name_lower]
        
        # General proper case
        words = name.split()
        cleaned_words = []
        for word in words:
            if word:
                cleaned_words.append(word[0].upper() + word[1:].lower())
        
        return ' '.join(cleaned_words)

    def _is_valid_product_name(self, name: str) -> bool:
        """Universal validation for product names across all niches"""
        if not name or len(name) < 3:
            return False
        
        # Must start with capital letter
        if not name[0].isupper():
            return False
        
        # Check against false positives
        name_lower = name.lower()
        if name_lower in self.false_positives:
            return False
        
        # Check against temporal/location words
        if name_lower in self.temporal_location_words:
            return False
        
        # Must contain letters
        if not re.search(r'[a-zA-Z]', name):
            return False
        
        # Length constraints
        if len(name) > 50 or len(name) < 3:
            return False
        
        # Check for too many common words
        words = name.lower().split()
        common_word_count = sum(1 for word in words if word in self.false_positives)
        if len(words) > 1 and common_word_count >= len(words) / 2:
            return False
        
        # Positive indicators for any niche
        positive_score = 0
        
        # Reasonable length
        if 4 <= len(name) <= 20:
            positive_score += 1
        
        # Contains known product suffixes
        if any(suffix in name for suffix in self.product_suffixes):
            positive_score += 2
        
        # CamelCase or compound structure
        if re.search(r'[a-z][A-Z]', name) or ' ' in name:
            positive_score += 1
        
        # Numeric elements (common in product names)
        if re.search(r'\d', name):
            positive_score += 1
        
        return positive_score >= 1

    def _filter_candidates(self, candidates: List[str]) -> List[str]:
        """Filter and deduplicate candidates"""
        filtered = []
        seen = set()
        
        for candidate in candidates:
            if not candidate:
                continue
            
            cleaned = self._clean_product_name(candidate)
            if not cleaned or cleaned in seen:
                continue
            
            if self._is_valid_product_name(cleaned):
                filtered.append(cleaned)
                seen.add(cleaned)
        
        return filtered

    def _rank_and_select_best(self, candidates: List[str], sources: Dict[str, List[str]], intelligence: Dict[str, Any]) -> str:
        """Rank candidates using universal scoring system"""
        if not candidates:
            return "Product"
        
        candidate_scores = defaultdict(float)
        
        # Base frequency scoring
        frequency_scores = Counter(candidates)
        for candidate, freq in frequency_scores.items():
            candidate_scores[candidate] += freq
        
        # Source-based scoring (prioritize reliable sources)
        source_weights = {
            "url": 3.0,           # URLs often contain actual product names
            "content": 2.5,       # Raw content is most reliable
            "emotional_context": 2.0,  # Testimonials often mention real names
            "title": 1.5,         # Titles may be generic
            "multi_source": 1.2,  # Cross-referenced content
            "scientific": 1.0,    # May contain generic terms
            "ai_generated": 0.5   # Lowest priority due to hallucination risk
        }
        
        for source, source_candidates in sources.items():
            weight = source_weights.get(source, 1.0)
            for candidate in source_candidates:
                if candidate in candidate_scores:
                    candidate_scores[candidate] += weight
        
        # Content-based scoring enhancements
        raw_content = intelligence.get("raw_content", "")
        for candidate in candidate_scores:
            
            # Frequency in raw content bonus
            if raw_content:
                content_mentions = len(re.findall(re.escape(candidate), raw_content, re.IGNORECASE))
                candidate_scores[candidate] += min(content_mentions * 0.5, 3.0)
            
            # Length bonus (optimal product name length)
            if 6 <= len(candidate) <= 15:
                candidate_scores[candidate] += 1.0
            elif 4 <= len(candidate) <= 20:
                candidate_scores[candidate] += 0.5
            
            # Product suffix bonus
            if any(suffix in candidate for suffix in self.product_suffixes):
                candidate_scores[candidate] += 2.0
            
            # CamelCase bonus (common in modern product names)
            if re.search(r'[a-z][A-Z]', candidate):
                candidate_scores[candidate] += 1.5
            
            # Avoid obvious AI hallucinations
            if candidate.lower() in ['island', 'solution', 'system', 'formula', 'method']:
                candidate_scores[candidate] *= 0.3  # Heavy penalty
        
        # Select best candidate
        if candidate_scores:
            best_candidate = max(candidate_scores.items(), key=lambda x: x[1])
            best_name, best_score = best_candidate
            
            logger.info(f"🏆 Best candidate: '{best_name}' (score: {best_score:.2f})")
            logger.debug(f"📊 All scores: {dict(sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)[:5])}")
            
            return best_name
        
        return "Product"


# Global instance for easy access
_universal_extractor = UniversalProductExtractor()

def extract_company_name_from_intelligence(intelligence: Dict[str, Any]) -> str:
    """
    Extract company name from intelligence data
    Often the company name is the same as the product name, but sometimes different
    """
    
    # Try to find company-specific mentions first
    company_patterns = [
        r'(?:from|by|created by|made by|developed by)\s+([A-Z][a-zA-Z]{3,20}(?:\s+[A-Z][a-zA-Z]{2,15}){0,2})',
        r'([A-Z][a-zA-Z]{3,20}(?:\s+[A-Z][a-zA-Z]{2,15}){0,2})\s+(?:Inc|LLC|Corp|Limited|Company)',
        r'©\s*(?:\d{4}\s+)?([A-Z][a-zA-Z]{3,20}(?:\s+[A-Z][a-zA-Z]{2,15}){0,2})',
        r'(?:contact|about)\s+([A-Z][a-zA-Z]{3,20}(?:\s+[A-Z][a-zA-Z]{2,15}){0,2})'
    ]
    
    # Check raw content for company mentions
    raw_content = intelligence.get("raw_content", "")
    if raw_content:
        for pattern in company_patterns:
            matches = re.findall(pattern, raw_content, re.IGNORECASE)
            if matches:
                company_name = matches[0] if isinstance(matches[0], str) else matches[0][0]
                cleaned = _universal_extractor._clean_product_name(company_name)
                if cleaned and _universal_extractor._is_valid_product_name(cleaned):
                    logger.info(f"🏢 Company name extracted: '{cleaned}'")
                    return cleaned
    
    # Check brand intelligence
    brand_intel = intelligence.get("brand_intelligence", {})
    if isinstance(brand_intel, dict):
        brand_positioning = brand_intel.get("brand_positioning", "")
        if isinstance(brand_positioning, str) and len(brand_positioning) > 10:
            for pattern in company_patterns:
                matches = re.findall(pattern, brand_positioning, re.IGNORECASE)
                if matches:
                    company_name = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    cleaned = _universal_extractor._clean_product_name(company_name)
                    if cleaned and _universal_extractor._is_valid_product_name(cleaned):
                        logger.info(f"🏢 Company name from brand intel: '{cleaned}'")
                        return cleaned
    
    # Check URL for company indicators
    source_url = intelligence.get("source_url", "")
    if source_url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(source_url.lower())
            domain = parsed.netloc.replace('www.', '')
            
            # If domain looks like a company name (not generic)
            domain_parts = domain.split('.')
            main_domain = domain_parts[0] if domain_parts else ""
            
            if (len(main_domain) > 6 and 
                main_domain not in ['get', 'buy', 'order', 'official', 'secure', 'click'] and
                not main_domain.startswith('get') and
                not main_domain.endswith('now')):
                
                cleaned = _universal_extractor._clean_product_name(main_domain)
                if cleaned and _universal_extractor._is_valid_product_name(cleaned):
                    logger.info(f"🏢 Company name from domain: '{cleaned}'")
                    return cleaned
        
        except Exception as e:
            logger.debug(f"Company URL extraction error: {e}")
    
    # Fallback: often company name = product name for direct-to-consumer products
    product_name = extract_product_name_from_intelligence(intelligence)
    if product_name and product_name != "Product":
        logger.info(f"🏢 Company name fallback to product name: '{product_name}'")
        return product_name
    
    # Final fallback
    logger.warning("⚠️ Could not extract company name, using 'Company'")
    return "Company"

def extract_product_name_from_intelligence(intelligence: Dict[str, Any]) -> str:
    """
    Universal product name extraction for any sales page
    
    This function works with thousands of different products across all niches:
    - Health supplements (AquaSculpt, LiverPure, etc.)
    - Software products (ProductName Pro, etc.)
    - Courses and training (MasterClass, Academy, etc.)
    - Business tools and services
    - Any other product type
    """
    return _universal_extractor.extract_product_name(intelligence)


# Keep all existing placeholder substitution functions (unchanged)
def substitute_product_placeholders(content: str, product_name: str, company_name: str = None) -> str:
    """Universal placeholder substitution system"""
    if not isinstance(content, str) or not product_name:
        return content
    
    placeholders = {
        "PRODUCT": product_name, "Product": product_name, "product": product_name,
        "[PRODUCT]": product_name, "[Product]": product_name, "[Product Name]": product_name,
        "[PRODUCT_NAME]": product_name, "Your Product": product_name, "Your product": product_name,
        "your product": product_name, "this product": product_name, "This product": product_name,
        "the product": product_name, "The product": product_name,
        "COMPANY": company_name or product_name, "Company": company_name or product_name,
        "[COMPANY]": company_name or product_name, "[Company]": company_name or product_name,
        "[Company Name]": company_name or product_name, "[COMPANY_NAME]": company_name or product_name,
        "Your Company": company_name or product_name, "Your company": company_name or product_name,
        "your company": company_name or product_name, "Your ": f"{product_name} ", "your ": f"{product_name} ",
    }
    
    result = content
    for placeholder, replacement in placeholders.items():
        if replacement:
            if placeholder.endswith(" "):
                pattern = r'\b' + re.escape(placeholder.strip()) + r'\b'
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            else:
                result = result.replace(placeholder, replacement)
    
    if result != content:
        logger.info(f"🔄 Placeholder substitution: Applied {product_name} replacements")
    
    return result

def substitute_placeholders_in_data(data: Any, product_name: str, company_name: str = None) -> Any:
    """Recursive placeholder substitution for complex data structures"""
    if isinstance(data, dict):
        return {k: substitute_placeholders_in_data(v, product_name, company_name) for k, v in data.items()}
    elif isinstance(data, list):
        return [substitute_placeholders_in_data(item, product_name, company_name) for item in data]
    elif isinstance(data, str):
        return substitute_product_placeholders(data, product_name, company_name)
    else:
        return data

def validate_no_placeholders(content: str, product_name: str) -> bool:
    """Validate that no placeholders remain in content"""
    placeholder_indicators = [
        "PRODUCT", "[Product", "Your Product", "your product", 
        "the product", "COMPANY", "[Company", "Your Company"
    ]
    
    content_lower = content.lower()
    found_placeholders = [ind for ind in placeholder_indicators if ind.lower() in content_lower]
    
    if found_placeholders:
        logger.warning(f"🚨 PLACEHOLDERS STILL FOUND: {found_placeholders}")
        return False
    
    return True


# Universal test function for any product
def test_universal_extraction():
    """Test the universal extraction with multiple product types"""
    
    test_cases = [
        {
            "name": "AquaSculpt (Health Supplement)",
            "intelligence": {
                "source_url": "https://getaquasculptnow.net/extraBottle",
                "raw_content": "The Difference AquaSculpt May Make! Powerful Ingredients AquaSculpt supports healthy weight loss",
                "psychology_intelligence": {
                    "emotional_triggers": [{"context": "AquaSculpt May Make! Claim Discount Powerful"}]
                }
            },
            "expected": "AquaSculpt"
        },
        {
            "name": "ProstaStream (Health Supplement)",
            "intelligence": {
                "source_url": "https://prostastreamofficial.com",
                "raw_content": "Discover ProstaStream today! ProstaStream helps support prostate health naturally.",
                "page_title": "ProstaStream - Official Website"
            },
            "expected": "ProstaStream"
        },
        {
            "name": "Profit Maximizer (Business Course)",
            "intelligence": {
                "source_url": "https://profitmaximizer.io/signup",
                "raw_content": "Join Profit Maximizer today! Learn the Profit Maximizer system that successful entrepreneurs use.",
                "page_title": "Profit Maximizer - Business Training Course"
            },
            "expected": "Profit Maximizer"
        },
        {
            "name": "CodeMaster Pro (Software)",
            "intelligence": {
                "source_url": "https://codemasterpro.com",
                "raw_content": "CodeMaster Pro helps developers write better code. Get CodeMaster Pro now!",
                "offer_intelligence": {
                    "products": ["Software Solution"]  # AI hallucination
                }
            },
            "expected": "CodeMaster Pro"
        },
        {
            "name": "Keto Blueprint (Diet Program)",
            "intelligence": {
                "source_url": "https://ketoblueprint.net",
                "raw_content": "The Keto Blueprint program shows you how to lose weight fast. Keto Blueprint contains everything you need.",
                "page_title": "Keto Blueprint - Weight Loss System"
            },
            "expected": "Keto Blueprint"
        },
        {
            "name": "Memory Hack (Brain Training)",
            "intelligence": {
                "source_url": "https://memoryhack.co",
                "raw_content": "Memory Hack improves your memory naturally. Try Memory Hack risk-free today!",
                "psychology_intelligence": {
                    "emotional_triggers": [{"context": "Memory Hack changed my life completely"}]
                }
            },
            "expected": "Memory Hack"
        }
    ]
    
    print("🧪 Testing Universal Product Name Extraction")
    print("=" * 60)
    
    passed = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        result = extract_product_name_from_intelligence(test_case["intelligence"])
        expected = test_case["expected"]
        success = result == expected
        
        if success:
            passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        print(f"{status} {test_case['name']}")
        print(f"  Expected: '{expected}'")
        print(f"  Got:      '{result}'")
        print()
    
    print(f"📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    return passed == total


# Advanced debugging function
def debug_product_extraction(intelligence: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive debugging for product extraction
    Shows results from all strategies for any product type
    """
    
    extractor = _universal_extractor
    
    debug_results = {
        "extraction_strategies": {},
        "final_result": None,
        "intelligence_analysis": {},
        "recommendations": []
    }
    
    # Test each strategy individually
    source_url = intelligence.get("source_url")
    if source_url:
        url_candidates = extractor._extract_from_url(source_url)
        debug_results["extraction_strategies"]["url"] = {
            "candidates": url_candidates,
            "source": source_url
        }
    
    raw_content = intelligence.get("raw_content")
    if raw_content:
        content_candidates = extractor._extract_from_content(raw_content)
        debug_results["extraction_strategies"]["content"] = {
            "candidates": content_candidates[:10],  # Limit for readability
            "content_length": len(raw_content),
            "content_preview": raw_content[:200]
        }
    
    emotional_candidates = extractor._extract_from_emotional_contexts(intelligence)
    debug_results["extraction_strategies"]["emotional_context"] = {
        "candidates": emotional_candidates,
        "sources_found": len(intelligence.get("psychology_intelligence", {}).get("emotional_triggers", []))
    }
    
    title_candidates = extractor._extract_from_titles(intelligence)
    debug_results["extraction_strategies"]["titles"] = {
        "candidates": title_candidates,
        "page_title": intelligence.get("page_title"),
        "source_title": intelligence.get("source_title")
    }
    
    ai_candidates = extractor._extract_from_ai_data(intelligence)
    debug_results["extraction_strategies"]["ai_generated"] = {
        "candidates": ai_candidates,
        "offer_products": intelligence.get("offer_intelligence", {}).get("products", [])
    }
    
    # Final extraction
    final_result = extract_product_name_from_intelligence(intelligence)
    debug_results["final_result"] = final_result
    
    # Intelligence analysis
    debug_results["intelligence_analysis"] = {
        "total_sections": len(intelligence.keys()),
        "has_raw_content": bool(intelligence.get("raw_content")),
        "has_url": bool(intelligence.get("source_url")),
        "has_emotional_triggers": bool(intelligence.get("psychology_intelligence", {}).get("emotional_triggers")),
        "content_length": len(intelligence.get("raw_content", "")),
        "main_sections": list(intelligence.keys())
    }
    
    # Recommendations
    if final_result == "Product":
        debug_results["recommendations"].extend([
            "❌ Product name extraction failed",
            "💡 Check if raw_content contains actual product name",
            "💡 Verify source_url contains product identifier",
            "💡 Ensure emotional triggers contain real product mentions",
            "🔍 Manual review recommended"
        ])
    else:
        debug_results["recommendations"].extend([
            f"✅ Successfully extracted: {final_result}",
            "🎯 Extraction working correctly"
        ])
    
    # Strategy effectiveness
    strategy_counts = {}
    for strategy, data in debug_results["extraction_strategies"].items():
        strategy_counts[strategy] = len(data.get("candidates", []))
    
    if strategy_counts:
        best_strategy = max(strategy_counts.items(), key=lambda x: x[1])
        debug_results["recommendations"].append(f"🏆 Most effective strategy: {best_strategy[0]} ({best_strategy[1]} candidates)")
    
    return debug_results


if __name__ == "__main__":
    test_universal_extraction()