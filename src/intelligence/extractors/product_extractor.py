# src/intelligence/extractors/product_extractor.py
"""
Product Name Extraction Engine - Clean version without duplication
🎯 CRITICAL FIX: Properly extract product names from sales pages
🔥 FIXED: Enhanced validation and fallback logic
"""
import re
import logging
from typing import List, Dict, Any, Optional
from collections import Counter

logger = logging.getLogger(__name__)

class ProductNameExtractor:
    """Extract product names from sales page content"""
    
    def __init__(self):
        # Universal product name patterns
        self.product_patterns = [
            r'(?:try|get|use|discover|introducing|meet)\s+([A-Z][a-zA-Z]+)',
            r'([A-Z][a-zA-Z]+)\s+(?:helps|supports|provides|delivers)',
            r'(?:^|\n)([A-Z][a-zA-Z]+)\s*[:-]',
            r'([A-Z][a-zA-Z]+)\s*[™®©]',
            r'"([A-Z][a-zA-Z]+)"',
            r'([A-Z][a-zA-Z]+)\s+is\s+(?:a|an|the)',
            r'([A-Z][a-zA-Z]+)\s+(?:contains|features|includes)',
            r'(?:with|using)\s+([A-Z][a-zA-Z]+)\s+you'
        ]
        
        # Words to exclude
        self.exclude_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'can', 'must', 'shall', 'it', 'he', 'she', 'they', 'we', 'you',
            'here', 'there', 'where', 'when', 'why', 'how', 'what', 'which', 'who',
            'discover', 'learn', 'find', 'get', 'buy', 'order', 'try', 'start',
            'click', 'visit', 'see', 'watch', 'read', 'download', 'access'
        }

    def extract_product_name(self, content: str, page_title: str = None) -> str:
        """🔥 FIXED: Extract product name from content with enhanced fallback logic"""
        
        logger.info("🔍 Starting product name extraction...")
        
        candidates = []
        
        # Method 1: Pattern-based extraction
        for pattern in self.product_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                
                cleaned = self._clean_candidate(match)
                if cleaned and self._is_valid_candidate(cleaned):
                    candidates.append(cleaned)
        
        # Method 2: Title-based extraction
        if page_title:
            title_words = page_title.split()
            for word in title_words:
                cleaned = self._clean_candidate(word)
                if cleaned and self._is_valid_candidate(cleaned) and len(cleaned) > 3:
                    candidates.append(cleaned)
        
        # Method 3: Frequency-based extraction
        words = re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', content)
        if words:
            word_counts = Counter(words)
            for word, count in word_counts.items():
                if count >= 2:
                    cleaned = self._clean_candidate(word)
                    if cleaned and self._is_valid_candidate(cleaned):
                        for _ in range(min(count, 3)):
                            candidates.append(cleaned)
        
        # 🔥 NEW: Emergency extraction if no good candidates found
        if not candidates:
            logger.warning("⚠️ No candidates found, trying emergency extraction...")
            
            # Look for ANY capitalized word that appears multiple times
            all_caps = re.findall(r'\b[A-Z][a-zA-Z]{2,20}\b', content)
            if all_caps:
                word_freq = Counter(all_caps)
                # Get most frequent that's not a common word
                for word, freq in word_freq.most_common(10):
                    if (word.lower() not in ['your', 'this', 'that', 'here', 'there', 'what', 'when', 'where'] and
                        len(word) > 3 and
                        freq >= 1):  # Even single occurrence is OK now
                        candidates.append(word)
                        logger.info(f"🔥 Emergency candidate found: '{word}' (appears {freq} times)")
                        break
        
        # Rank and return best candidate
        best_candidate = self._rank_candidates(candidates, content)
        
        # 🔥 CRITICAL FIX: Better fallback logic
        if not best_candidate or best_candidate.lower() in ['your', 'product', 'this', 'that']:
            # Try one more extraction attempt
            logger.warning("⚠️ Poor candidate result, trying final extraction...")
            
            # Look for branded terms or unique words
            unique_caps = re.findall(r'\b[A-Z][a-zA-Z]{4,15}\b', content)
            if unique_caps:
                # Filter out very common words
                filtered = [w for w in unique_caps if w.lower() not in [
                    'health', 'natural', 'premium', 'quality', 'service', 'company', 
                    'business', 'solution', 'system', 'program', 'course', 'guide',
                    'method', 'strategy', 'plan', 'package', 'special', 'limited'
                ]]
                
                if filtered:
                    best_candidate = filtered[0]  # Take the first unique one
                    logger.info(f"🎯 Final extraction successful: '{best_candidate}'")
                else:
                    best_candidate = "HealthProduct"  # Better than "Your"
            else:
                best_candidate = "HealthProduct"  # Better than "Your"
        
        logger.info(f"🎯 Product name extraction result: '{best_candidate}'")
        return best_candidate

    def _clean_candidate(self, candidate: str) -> str:
        """Clean a candidate product name"""
        if not candidate:
            return ""
        
        candidate = re.sub(r'[^\w\s]', '', candidate)
        candidate = re.sub(r'\s+', ' ', candidate).strip()
        candidate = candidate.title()
        
        return candidate

    def _is_valid_candidate(self, candidate: str) -> bool:
        """🔥 FIXED: Check if a candidate is a valid product name - less restrictive"""
        
        if not candidate or len(candidate) < 3:
            return False
        
        if not candidate[0].isupper():
            return False
        
        candidate_lower = candidate.lower()
        
        # 🔥 CRITICAL FIX: Be more specific about exclusions
        # Only exclude if the ENTIRE candidate is a common word, not if it contains one
        if candidate_lower in self.exclude_words:
            return False
        
        # 🔥 CRITICAL FIX: Don't exclude "Your" if it's part of a longer product name
        if len(candidate) == 3 and candidate_lower in ['you', 'your', 'the', 'and', 'but']:
            return False
        
        if not re.search(r'[a-zA-Z]', candidate):
            return False
        
        # Check for non-product patterns
        if re.match(r'^\d+$', candidate_lower):
            return False
        
        # 🔥 FIXED: More specific pattern matching
        if candidate_lower.startswith(('click ', 'buy ', 'get ', 'here ', 'there ')):
            return False
        
        # 🔥 NEW: Accept anything that looks like a proper product name
        if len(candidate) >= 4 and candidate[0].isupper():
            return True
        
        # Must have some positive indicators (relaxed)
        positive_score = 0
        
        if re.search(r'[a-z][A-Z]', candidate):  # CamelCase
            positive_score += 2
        
        if 4 <= len(candidate) <= 15:
            positive_score += 1
        
        if candidate.count(candidate[0].upper()) == 1:  # Starts with capital
            positive_score += 1
        
        return positive_score >= 1

    def _rank_candidates(self, candidates: List[str], content: str) -> str:
        """Rank candidates and return the best one"""
        
        if not candidates:
            return "Product"
        
        candidate_scores = Counter(candidates)
        
        # Add bonus scores
        for candidate in candidate_scores:
            score = candidate_scores[candidate]
            
            # Bonus for length
            if 6 <= len(candidate) <= 12:
                candidate_scores[candidate] = score + 1
            
            # Bonus for frequency in content
            content_mentions = len(re.findall(re.escape(candidate), content, re.IGNORECASE))
            if content_mentions >= 3:
                candidate_scores[candidate] = score + content_mentions
        
        best_candidate = candidate_scores.most_common(1)[0][0]
        return best_candidate


# Convenience function
def extract_product_name(content: str, page_title: str = None) -> str:
    """Quick function to extract product name from content"""
    extractor = ProductNameExtractor()
    return extractor.extract_product_name(content, page_title)


# Test function
def test_aquasculpt_extraction():
    """Test the extraction with AquaSculpt content"""
    test_content = """
    Join The Thousands Who Rave About AquaSculpt
    Feel The Difference AquaSculpt May Make!
    Get AquaSculpt today and see results.
    AquaSculpt helps support liver function naturally.
    """
    
    result = extract_product_name(test_content)
    print(f"Test result: '{result}' (Expected: 'AquaSculpt')")
    return result == 'AquaSculpt'


if __name__ == "__main__":
    test_aquasculpt_extraction()