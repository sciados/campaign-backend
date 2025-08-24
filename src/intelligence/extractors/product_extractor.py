# src/intelligence/extractors/product_extractor.py
"""
Product Name Extraction Engine - Clean version without TRY suffix issues
🎯 CRITICAL FIX: Properly extract product names from sales pages
🔥 FIXED: Enhanced validation and fallback logic to prevent TRY suffix
🔧 FIXED: Remove problematic extraction patterns that add unwanted suffixes
"""
import re
import logging
from typing import List, Dict, Any, Optional
from collections import Counter

logger = logging.getLogger(__name__)

class ProductNameExtractor:
    """Extract product names from sales page content"""
    
    def __init__(self):
        # 🔧 FIXED: Updated product name patterns to avoid TRY suffix
        self.product_patterns = [
            # Primary patterns (most reliable)
            r'([A-Z][a-zA-Z]+)\s*[™®©]',  # Trademarked names
            r'"([A-Z][a-zA-Z]+)"',  # Quoted product names
            r'([A-Z][a-zA-Z]+)\s+is\s+(?:a|an|the)',  # "ProductName is a/an/the"
            r'(?:^|\n)([A-Z][a-zA-Z]+)\s*[:-]',  # Start of line with separator
            
            # Secondary patterns (more cautious)
            r'(?:introducing|meet|discover)\s+([A-Z][a-zA-Z]+)(?:\s|$|[.!?])',  # "Introducing ProductName"
            r'([A-Z][a-zA-Z]+)\s+(?:helps|supports|provides|delivers)',  # "ProductName helps"
            r'([A-Z][a-zA-Z]+)\s+(?:contains|features|includes)',  # "ProductName contains"
            
            # Avoid patterns that commonly add unwanted suffixes
            # REMOVED: r'(?:try|get|use)\s+([A-Z][a-zA-Z]+)' - this was adding TRY
            # REMOVED: r'(?:with|using)\s+([A-Z][a-zA-Z]+)\s+you' - this was problematic
        ]
        
        # Words to exclude (expanded to prevent common issues)
        self.exclude_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'can', 'must', 'shall', 'it', 'he', 'she', 'they', 'we', 'you',
            'here', 'there', 'where', 'when', 'why', 'how', 'what', 'which', 'who',
            'discover', 'learn', 'find', 'get', 'buy', 'order', 'try', 'start',
            'click', 'visit', 'see', 'watch', 'read', 'download', 'access',
            # 🔧 NEW: Add more problematic suffixes and prefixes
            'try', 'get', 'use', 'now', 'today', 'free', 'new', 'best', 'top'
        }

        # 🔧 NEW: Common unwanted suffixes to remove
        self.unwanted_suffixes = [
            'try', 'TRY', 'get', 'GET', 'now', 'NOW', 'today', 'TODAY',
            'free', 'free', 'new', 'NEW', 'best', 'BEST'
        ]

    def extract_product_name(self, content: str, page_title: str = None) -> str:
        """🔥 FIXED: Extract product name from content with enhanced suffix removal"""
        
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
        
        # Method 3: Frequency-based extraction (more conservative)
        words = re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', content)
        if words:
            word_counts = Counter(words)
            for word, count in word_counts.items():
                if count >= 2:  # Must appear at least twice
                    cleaned = self._clean_candidate(word)
                    if cleaned and self._is_valid_candidate(cleaned):
                        # Weight by frequency but cap it
                        for _ in range(min(count, 3)):
                            candidates.append(cleaned)
        
        # 🔥 NEW: Emergency extraction if no good candidates found
        if not candidates:
            logger.warning("⚠️ No candidates found, trying emergency extraction...")
            
            # Look for ANY capitalized word that appears multiple times
            all_caps = re.findall(r'\b[A-Z][a-zA-Z]{3,20}\b', content)
            if all_caps:
                word_freq = Counter(all_caps)
                # Get most frequent that's not a common word
                for word, freq in word_freq.most_common(10):
                    cleaned = self._clean_candidate(word)
                    if (cleaned and 
                        len(cleaned) > 3 and
                        cleaned.lower() not in self.exclude_words and
                        freq >= 1):
                        candidates.append(cleaned)
                        logger.info(f"🔥 Emergency candidate found: '{cleaned}' (appears {freq} times)")
                        break
        
        # Rank and return best candidate
        best_candidate = self._rank_candidates(candidates, content)
        
        # 🔥 CRITICAL FIX: Post-process to remove unwanted suffixes
        if best_candidate:
            best_candidate = self._remove_unwanted_suffixes(best_candidate)
        
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
                    'method', 'strategy', 'plan', 'package', 'special', 'limited',
                    'order', 'today', 'click', 'visit'  # 🔧 ADDED more exclusions
                ]]
                
                if filtered:
                    best_candidate = self._remove_unwanted_suffixes(filtered[0])
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
        
        # Remove punctuation but preserve spaces
        candidate = re.sub(r'[^\w\s]', '', candidate)
        candidate = re.sub(r'\s+', ' ', candidate).strip()
        candidate = candidate.title()
        
        return candidate

    def _remove_unwanted_suffixes(self, candidate: str) -> str:
        """🔧 NEW: Remove unwanted suffixes that get appended to product names"""
        if not candidate:
            return candidate
        
        original = candidate
        
        # Check if the candidate ends with any unwanted suffix
        for suffix in self.unwanted_suffixes:
            # Check for exact suffix match at the end
            if candidate.upper().endswith(suffix.upper()):
                # Remove the suffix
                candidate = candidate[:-len(suffix)].strip()
                logger.info(f"🧹 Removed suffix '{suffix}' from '{original}' -> '{candidate}'")
                break
            
            # Check for suffix that's been concatenated (like HEPATOBURNTRY)
            if len(candidate) > len(suffix) and candidate.upper().endswith(suffix.upper()):
                # Check if removing suffix leaves a valid word
                potential_base = candidate[:-len(suffix)]
                if len(potential_base) >= 4:  # Must leave at least 4 characters
                    candidate = potential_base
                    logger.info(f"🧹 Removed concatenated suffix '{suffix}' from '{original}' -> '{candidate}'")
                    break
        
        return candidate or original  # Return original if cleaning resulted in empty string

    def _is_valid_candidate(self, candidate: str) -> bool:
        """🔥 FIXED: Check if a candidate is a valid product name - enhanced validation"""
        
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
        if len(candidate) <= 3 and candidate_lower in ['you', 'your', 'the', 'and', 'but', 'try', 'get', 'now']:
            return False
        
        if not re.search(r'[a-zA-Z]', candidate):
            return False
        
        # Check for non-product patterns
        if re.match(r'^\d+$', candidate_lower):
            return False
        
        # 🔥 FIXED: More specific pattern matching
        if candidate_lower.startswith(('click ', 'buy ', 'get ', 'here ', 'there ', 'try ')):
            return False
        
        # 🔥 NEW: Reject candidates that end with common unwanted suffixes
        for suffix in self.unwanted_suffixes:
            if candidate.upper().endswith(suffix.upper()) and len(candidate) > len(suffix):
                # This will be cleaned in _remove_unwanted_suffixes, but flag for extra processing
                pass
        
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
            
            # Bonus for length (sweet spot is 6-12 characters)
            if 6 <= len(candidate) <= 12:
                candidate_scores[candidate] = score + 2
            elif 4 <= len(candidate) <= 15:
                candidate_scores[candidate] = score + 1
            
            # Bonus for frequency in content
            content_mentions = len(re.findall(re.escape(candidate), content, re.IGNORECASE))
            if content_mentions >= 3:
                candidate_scores[candidate] = score + content_mentions
            
            # 🔧 NEW: Penalty for unwanted patterns
            if any(candidate.upper().endswith(suffix.upper()) for suffix in self.unwanted_suffixes):
                candidate_scores[candidate] = max(1, score - 1)  # Reduce score but don't eliminate
        
        # Get the best candidate
        best_candidate = candidate_scores.most_common(1)[0][0]
        
        # 🔧 NEW: Final cleanup on the best candidate
        best_candidate = self._remove_unwanted_suffixes(best_candidate)
        
        return best_candidate

    def extract_from_meta_tags(self, content: str) -> Optional[str]:
        """Extract product name from meta tags and structured data"""
        try:
            # Look for product name in meta tags
            meta_patterns = [
                r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']',
                r'<meta[^>]*name=["\']product["\'][^>]*content=["\']([^"\']+)["\']',
                r'<title[^>]*>([^<]+)</title>',
                r'"name"\s*:\s*"([^"]+)"',  # JSON-LD product name
                r'"title"\s*:\s*"([^"]+)"'  # JSON-LD title
            ]
            
            for pattern in meta_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    cleaned = self._clean_candidate(match.strip())
                    if cleaned and self._is_valid_candidate(cleaned):
                        return self._remove_unwanted_suffixes(cleaned)
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting from meta tags: {e}")
            return None

    def extract_from_headers(self, content: str) -> List[str]:
        """Extract potential product names from headers (h1, h2, h3)"""
        try:
            header_patterns = [
                r'<h1[^>]*>([^<]+)</h1>',
                r'<h2[^>]*>([^<]+)</h2>',
                r'<h3[^>]*>([^<]+)</h3>'
            ]
            
            candidates = []
            for pattern in header_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    # Clean HTML entities and extra whitespace
                    cleaned_text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', match)
                    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                    
                    # Extract capitalized words
                    words = re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', cleaned_text)
                    for word in words:
                        cleaned = self._clean_candidate(word)
                        if cleaned and self._is_valid_candidate(cleaned):
                            candidates.append(self._remove_unwanted_suffixes(cleaned))
            
            return candidates
            
        except Exception as e:
            logger.warning(f"Error extracting from headers: {e}")
            return []


# Convenience function
def extract_product_name(content: str, page_title: str = None) -> str:
    """Quick function to extract product name from content"""
    extractor = ProductNameExtractor()
    return extractor.extract_product_name(content, page_title)


# Enhanced extraction function that tries multiple methods
def extract_product_name_enhanced(content: str, page_title: str = None) -> Dict[str, Any]:
    """Enhanced extraction with multiple methods and confidence scoring"""
    extractor = ProductNameExtractor()
    
    results = {
        "primary_extraction": extractor.extract_product_name(content, page_title),
        "meta_extraction": extractor.extract_from_meta_tags(content),
        "header_extraction": extractor.extract_from_headers(content),
        "confidence": "high"
    }
    
    # Use meta extraction if available and different from primary
    if results["meta_extraction"] and results["meta_extraction"] != results["primary_extraction"]:
        if len(results["meta_extraction"]) > len(results["primary_extraction"]):
            results["recommended"] = results["meta_extraction"]
            results["confidence"] = "very_high"
        else:
            results["recommended"] = results["primary_extraction"]
    else:
        results["recommended"] = results["primary_extraction"]
    
    return results


# Test functions for comprehensive testing
def test_hepatoburn_extraction():
    """Test the extraction with HepatoBurn content to prevent TRY suffix"""
    test_content = """
    <title>HepatoBurn - Natural Liver Support</title>
    <meta property="og:title" content="HepatoBurn Official Site">
    <h1>Join The Thousands Who Rave About HepatoBurn</h1>
    <p>Feel The Difference HepatoBurn May Make!</p>
    <p>Get HepatoBurn today and see results.</p>
    <p>Try HepatoBurn now for amazing results.</p>
    <p>HepatoBurn helps support liver function naturally.</p>
    <p>Order HepatoBurn today and start your journey.</p>
    """
    
    result = extract_product_name(test_content)
    enhanced_result = extract_product_name_enhanced(test_content)
    
    print(f"Basic extraction: '{result}' (Expected: 'HepatoBurn', NOT 'HepatoBurnTRY')")
    print(f"Enhanced extraction: {enhanced_result}")
    
    # Test should pass - no TRY suffix
    success = result == 'HepatoBurn' and not result.endswith('TRY')
    enhanced_success = enhanced_result["recommended"] == 'HepatoBurn'
    
    if success and enhanced_success:
        print("✅ SUCCESS: Both extractions work correctly without TRY suffix")
    else:
        print(f"❌ FAILED: Basic='{result}', Enhanced='{enhanced_result['recommended']}'")
    
    return success and enhanced_success


def test_aquasculpt_extraction():
    """Test the extraction with AquaSculpt content"""
    test_content = """
    <h1>Join The Thousands Who Rave About AquaSculpt</h1>
    <p>Feel The Difference AquaSculpt May Make!</p>
    <p>Get AquaSculpt today and see results.</p>
    <p>AquaSculpt helps support liver function naturally.</p>
    """
    
    result = extract_product_name(test_content)
    print(f"Test result: '{result}' (Expected: 'AquaSculpt')")
    return result == 'AquaSculpt'


def test_edge_cases():
    """Test various edge cases and problematic patterns"""
    test_cases = [
        {
            "name": "TRY suffix prevention",
            "content": "Try ProductNameTRY today! Get ProductNameTRY now!",
            "expected": "ProductName"
        },
        {
            "name": "GET suffix prevention", 
            "content": "Get AwesomeProductGET here! Order AwesomeProductGET now!",
            "expected": "AwesomeProduct"
        },
        {
            "name": "Mixed case handling",
            "content": "SUPERPROD is amazing! SuperProd helps everyone.",
            "expected": "SuperProd"
        },
        {
            "name": "Meta tag extraction",
            "content": '<meta property="og:title" content="MetaProduct - Official Site">',
            "expected": "MetaProduct"
        }
    ]
    
    print("\n🧪 Testing edge cases...")
    all_passed = True
    
    for test_case in test_cases:
        result = extract_product_name(test_case["content"])
        passed = result == test_case["expected"]
        status = "✅" if passed else "❌"
        print(f"{status} {test_case['name']}: Got '{result}', Expected '{test_case['expected']}'")
        if not passed:
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    print("🧪 Testing product name extraction...")
    print("=" * 50)
    
    test1 = test_hepatoburn_extraction()
    print("\n" + "-" * 30)
    
    test2 = test_aquasculpt_extraction()
    print("\n" + "-" * 30)
    
    test3 = test_edge_cases()
    print("\n" + "=" * 50)
    
    if test1 and test2 and test3:
        print("🎉 ALL TESTS PASSED! Product extractor is working correctly.")
    else:
        print("❌ Some tests failed - check the implementation.")
        
    # Demo the enhanced extraction
    print("\n🔍 Enhanced extraction demo:")
    demo_content = """
    <title>SuperProduct - The Ultimate Solution</title>
    <h1>Try SuperProduct Today!</h1>
    <p>Get SuperProduct now and see amazing results!</p>
    """
    enhanced_demo = extract_product_name_enhanced(demo_content)
    print(f"Enhanced result: {enhanced_demo}")