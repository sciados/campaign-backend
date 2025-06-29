# src/intelligence/extractors/product_extractor.py

import re
import logging
from typing import List, Dict, Any
from collections import Counter

logger = logging.getLogger(__name__)

class ProductNameExtractor:
    """Extract product names from sales page content"""

    def __init__(self):
        # Example initializations (replace with actual patterns/words as needed)
        self.product_patterns = [r'\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)\b']
        self.exclude_words = set(['the', 'and', 'with', 'for', 'from', 'this', 'that', 'your', 'our', 'best', 'new', 'sale', 'offer'])
        self.niche_indicators = {'fitness': ['fit', 'gym', 'muscle'], 'beauty': ['skin', 'glow', 'cream']}
        self.benefit_keywords = ['boost', 'improve', 'enhance', 'support', 'increase']

        # Precompile patterns/lists if desired for performance

    def extract_product_name(self, content: str, page_title: str = None) -> str:
        logger.info("🔍 Starting product name extraction...")
        cleaned = self._clean_content(content)

        candidates: List[str] = []
        candidates.extend(self._extract_by_patterns(cleaned))
        if page_title:
            candidates.extend(self._extract_from_title(page_title))
        candidates.extend(self._extract_by_context(cleaned))
        candidates.extend(self._extract_by_frequency(cleaned))

        best = self._rank_candidates(candidates, cleaned)
        logger.info(f"🎯 Product name extraction result: '{best}' "
                    f"(from {len(candidates)} candidates)")
        return best

    def _clean_content(self, content: str) -> str:
        txt = re.sub(r'\s+', ' ', content)
        noise = [
            r'click\s+here\s+to\s+\w+',
            r'order\s+now\s+for\s+\$\d+',
            r'buy\s+\d+\s+get\s+\d+\s+free',
            r'limited\s+time\s+offer',
            r'\$\d+(?:\.\d{2})?\s+(?:value|price|cost)'
        ]
        for p in noise:
            txt = re.sub(p, '', txt, flags=re.IGNORECASE)
        return txt.strip()

    def _extract_by_patterns(self, content: str) -> List[str]:
        candidates = []
        for pat in self.product_patterns:
            for m in re.findall(pat, content, re.IGNORECASE | re.MULTILINE):
                match = m[0] if isinstance(m, tuple) else m
                c = self._clean_candidate(match)
                if c and self._is_valid_candidate(c):
                    def _extract_from_title(self, title: str) -> List[str]:
        # Dummy implementation for now
                        candidates = []
        # Example: extract capitalized words from title
        for m in re.findall(r'\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)\b', title):
            def _extract_by_context(self, content: str) -> List[str]:
        # Dummy implementation for now
                candidates = []
        logger.info(f"🎯 Context extraction found {len(candidates)} candidates")
        return candidates
    def _extract_by_frequency(self, content: str) -> List[str]:
        # Dummy implementation for now
        candidates = []
        logger.info(f"📊 Frequency extraction found {len(candidates)} candidates")
        return candidates
        logger.info(f"📰 Title extraction found {len(candidates)} candidates")
        return candidates

    def _extract_by_context(self, content: str) -> List[str]:
        # benefit_context_patterns + niche-specific patterns
        logger.info(f"🎯 Context extraction found {len(candidates)} candidates")
        return candidates

    def _extract_by_frequency(self, content: str) -> List[str]:
        logger.info(f"📊 Frequency extraction found {len(candidates)} candidates")
        return candidates

    def _clean_candidate(self, candidate: str) -> str:
        candidate = re.sub(r'[^\w\s]', '', candidate).strip().title()
        return candidate

    def _is_valid_candidate(self, candidate: str) -> bool:
        if len(candidate) < 3 or not candidate[0].isupper():
            return False
        if any(w in self.exclude_words for w in candidate.lower().split()):
            return False

        candidate_lower = candidate.lower()
        positive = 0
        if re.search(r'[a-z][A-Z]', candidate):
            positive += 2
        if any(kw in candidate_lower for kws in self.niche_indicators.values() for kw in kws):
            positive += 1
        if 6 <= len(candidate) <= 15:
            positive += 1
        if any(candidate_lower.endswith(suf) for suf in ['max','pro','plus','elite','ultra','prime','boost','force','x','fx']):
            # score = scores[cand]  # Not used, so commented out

            return positive >= 1

    def _rank_candidates(self, candidates: List[str], content: str) -> str:
        if not candidates:
            logger.warning("⚠️ No product name candidates found, using fallback")
            return "Product"

        scores = Counter(candidates)
        niche = self._detect_niche(content)

        for cand in list(scores):
            score = scores[cand]
            if niche and any(kw in cand.lower() for kw in self.niche_indicators.get(niche, [])):
                scores[cand] += 3
            if re.search(r'[a-z][A-Z]', cand):
                def extract_product_details(self, content: str, product_name: str) -> Dict[str, Any]:
        # Stub implementation to avoid unused parameter errors
                    return {}
    
    # Static method and test function should be outside the class
    @staticmethod
    def extract_product_name(content: str, page_title: str = None) -> str:
        return ProductNameExtractor().extract_product_name(content, page_title)
    
    def test_aquasculpt_extraction() -> bool:
        test_content = """AquaSculpt is the revolutionary new way to tone your body. AquaSculpt uses water resistance to help you sculpt muscles fast. Order AquaSculpt today!"""
        result = ProductNameExtractor().extract_product_name(test_content)
        print(result)
        return result == 'AquaSculpt'
    
    if __name__ == "__main__":
        success = test_aquasculpt_extraction()
        print(f"Success: {success}")
        def extract_product_name(content: str, page_title: str = None) -> str:
            return ProductNameExtractor().extract_product_name(content, page_title)
    
    # Test function and script entry point should be outside the class
    def test_aquasculpt_extraction() -> bool:
        test_content = """..."""  # same
        result = ProductNameExtractor.extract_product_name(test_content)
        print(result)
        return result == 'AquaSculpt'
    
    if __name__ == "__main__":
        success = test_aquasculpt_extraction()
        print(f"Success: {success}")
