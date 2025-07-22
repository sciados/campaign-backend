# src/intelligence/utils/product_name_fix.py
"""
🔥 PRODUCT NAME FIX UTILITY
Handles extraction and substitution of actual product names from intelligence data
Eliminates placeholders like "HEPATOBURNTRY", "PRODUCT", "[Product]", etc.
"""

import re
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Common product name placeholders that need to be replaced
PLACEHOLDER_PATTERNS = [
    # Generic placeholders
    r'\[Product\]', r'\[PRODUCT\]', r'\[product\]',
    r'\{Product\}', r'\{PRODUCT\}', r'\{product\}',
    r'PRODUCT', r'Product', r'product',
    r'Your Product', r'YOUR PRODUCT', r'your product',
    r'Your Company', r'YOUR COMPANY', r'your company',
    r'This Product', r'THIS PRODUCT', r'this product',
    
    # Corrupted variations (like HEPATOBURNTRY)
    r'[A-Z]+TRY$',  # Words ending in TRY that look corrupted
    r'[A-Z]{10,}',  # Very long uppercase strings that might be corrupted
    
    # Common corruption patterns
    r'HEPATOBURNTRY', r'PRODUCTNAME', r'BRANDNAME',
    r'SUPPLEMENTNAME', r'ITEMNAME', r'SERVICENAME'
]

def extract_product_name_from_intelligence(intelligence_data: Dict[str, Any]) -> str:
    """
    Extract the actual product name from intelligence data with fallback logic
    
    Priority order:
    1. content_intelligence.actual_product_name (if exists and clean)
    2. offer_intelligence products array (first clean product)  
    3. scientific_intelligence compound names (if health product)
    4. Page title cleanup
    5. Fallback to generic name based on detected category
    """
    
    if not intelligence_data:
        return "Premium Product"
    
    # Try content intelligence first (most reliable)
    content_intel = _safe_get_dict(intelligence_data, "content_intelligence")
    if content_intel:
        actual_name = content_intel.get("actual_product_name")
        if actual_name and _is_valid_product_name(actual_name):
            logger.info(f"✅ Found actual product name: {actual_name}")
            return actual_name
    
    # Try offer intelligence products
    offer_intel = _safe_get_dict(intelligence_data, "offer_intelligence") 
    if offer_intel:
        products = offer_intel.get("products", [])
        if isinstance(products, list):
            for product in products:
                if isinstance(product, str) and _is_valid_product_name(product):
                    cleaned_name = _clean_product_name(product)
                    if cleaned_name:
                        logger.info(f"✅ Extracted from offer products: {cleaned_name}")
                        return cleaned_name
    
    # Try scientific intelligence for health products
    scientific_intel = _safe_get_dict(intelligence_data, "scientific_intelligence")
    if scientific_intel:
        compounds = scientific_intel.get("primary_compounds", [])
        if isinstance(compounds, list) and compounds:
            # Look for obvious product names in compounds
            for compound in compounds:
                if isinstance(compound, str):
                    # Check if compound looks like a product name rather than a chemical
                    if _looks_like_product_name(compound):
                        cleaned_name = _clean_product_name(compound)
                        if cleaned_name:
                            logger.info(f"✅ Extracted from scientific compounds: {cleaned_name}")
                            return cleaned_name
    
    # Try page title cleanup
    page_title = intelligence_data.get("page_title", "")
    if page_title:
        extracted_name = _extract_name_from_title(page_title)
        if extracted_name and _is_valid_product_name(extracted_name):
            logger.info(f"✅ Extracted from page title: {extracted_name}")
            return extracted_name
    
    # Try URL-based extraction
    source_url = intelligence_data.get("source_url", "")
    if source_url:
        url_name = _extract_name_from_url(source_url)
        if url_name and _is_valid_product_name(url_name):
            logger.info(f"✅ Extracted from URL: {url_name}")
            return url_name
    
    # Fallback based on detected category
    category = _detect_product_category(intelligence_data)
    fallback_name = _get_category_fallback_name(category)
    
    logger.warning(f"⚠️ No clean product name found, using fallback: {fallback_name}")
    return fallback_name

def substitute_product_placeholders(text: str, actual_product_name: str) -> str:
    """
    Replace product name placeholders in text with actual product name
    """
    
    if not text or not actual_product_name:
        return text
    
    result_text = text
    
    # Apply all placeholder patterns
    for pattern in PLACEHOLDER_PATTERNS:
        result_text = re.sub(pattern, actual_product_name, result_text, flags=re.IGNORECASE)
    
    # Clean up any remaining generic references
    generic_replacements = [
        (r'\bthis supplement\b', actual_product_name, re.IGNORECASE),
        (r'\bthe product\b', actual_product_name, re.IGNORECASE),
        (r'\bour product\b', actual_product_name, re.IGNORECASE),
        (r'\bthis formula\b', actual_product_name, re.IGNORECASE),
        (r'\bthe supplement\b', actual_product_name, re.IGNORECASE),
    ]
    
    for pattern, replacement, flags in generic_replacements:
        result_text = re.sub(pattern, replacement, result_text, flags=flags)
    
    return result_text

def substitute_placeholders_in_data(data: Dict[str, Any], actual_product_name: str) -> Dict[str, Any]:
    """
    Recursively substitute placeholders in dictionary data structure
    """
    
    if not isinstance(data, dict):
        return data
    
    result = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = substitute_product_placeholders(value, actual_product_name)
        elif isinstance(value, dict):
            result[key] = substitute_placeholders_in_data(value, actual_product_name)
        elif isinstance(value, list):
            result[key] = [
                substitute_product_placeholders(item, actual_product_name) if isinstance(item, str) 
                else substitute_placeholders_in_data(item, actual_product_name) if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            result[key] = value
    
    return result

def validate_no_placeholders(text: str, expected_product_name: str) -> bool:
    """
    Validate that text contains no remaining placeholders
    Returns True if clean, False if placeholders remain
    """
    
    if not text:
        return True
    
    # Check for remaining placeholder patterns
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"⚠️ Placeholder found: {pattern} in text: {text[:100]}...")
            return False
    
    # Check that expected product name is actually used
    if expected_product_name and expected_product_name.lower() not in text.lower():
        logger.warning(f"⚠️ Expected product name '{expected_product_name}' not found in: {text[:100]}...")
        return False
    
    return True

# Helper functions

def _safe_get_dict(data: Dict[str, Any], key: str) -> Dict[str, Any]:
    """Safely get dictionary from data, handling JSON strings"""
    
    value = data.get(key, {})
    
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            return {}
    elif isinstance(value, dict):
        return value
    else:
        return {}

def _is_valid_product_name(name: str) -> bool:
    """Check if name looks like a valid product name"""
    
    if not name or len(name.strip()) < 2:
        return False
    
    name = name.strip()
    
    # Skip obvious placeholders
    placeholder_indicators = [
        'product', 'supplement', 'formula', 'brand', 'company', 'service',
        'item', 'solution', 'system', 'method', 'program', '[', ']', '{', '}'
    ]
    
    name_lower = name.lower()
    if any(indicator in name_lower for indicator in placeholder_indicators):
        # Unless it's clearly a real product name
        if not _looks_like_real_product_name(name):
            return False
    
    # Skip corrupted names (like HEPATOBURNTRY)
    if re.match(r'^[A-Z]+TRY$', name) or len(name) > 15 and name.isupper():
        return False
    
    return True

def _looks_like_product_name(text: str) -> bool:
    """Check if text looks like a product name rather than a chemical compound"""
    
    if not text:
        return False
    
    # Product name indicators
    product_indicators = [
        # Common product name patterns
        r'\b\w+burn\b',  # Like "Hepatoburn", "Fatburn"
        r'\b\w+max\b',   # Like "TestoMax", "CardioMax"
        r'\b\w+plus\b',  # Like "MetaboPlus"
        r'\b\w+pro\b',   # Like "LeanPro"
        r'\b\w+elite\b', # Like "Elite formula"
    ]
    
    text_lower = text.lower()
    if any(re.search(pattern, text_lower) for pattern in product_indicators):
        return True
    
    # Check capitalization pattern (product names often have specific capitalization)
    if re.match(r'^[A-Z][a-z]+[A-Z][a-z]+', text):  # Like "HepatoBurn"
        return True
    
    return False

def _looks_like_real_product_name(name: str) -> bool:
    """Check if name looks like a real product despite containing generic words"""
    
    # Real product name patterns
    real_patterns = [
        r'\w+burn\b',    # Hepatoburn, Fatburn
        r'\w+max\b',     # TestoMax
        r'\w+pro\b',     # LeanPro  
        r'\w+plus\b',    # MetaboPlus
        r'\w+elite\b',   # Elite
        r'\w+force\b',   # Force
        r'\w+power\b',   # Power
    ]
    
    name_lower = name.lower()
    return any(re.search(pattern, name_lower) for pattern in real_patterns)

def _clean_product_name(raw_name: str) -> str:
    """Clean and format product name"""
    
    if not raw_name:
        return ""
    
    # Remove common prefixes/suffixes
    name = raw_name.strip()
    
    # Remove trademark symbols
    name = re.sub(r'[™®©]', '', name)
    
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Capitalize properly (first letter and after spaces)
    name = ' '.join(word.capitalize() for word in name.split())
    
    return name

def _extract_name_from_title(title: str) -> Optional[str]:
    """Extract product name from page title"""
    
    if not title:
        return None
    
    # Common title patterns
    patterns = [
        r'(\w+)\s*[-–|]\s*Official',  # "Hepatoburn - Official Site"
        r'(\w+)\s*Official',          # "Hepatoburn Official"
        r'Buy\s+(\w+)',               # "Buy Hepatoburn"
        r'(\w+)\s*Reviews?',          # "Hepatoburn Review"
        r'^(\w+)\b',                  # First word if it looks like a product name
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            candidate = match.group(1)
            if _is_valid_product_name(candidate):
                return _clean_product_name(candidate)
    
    return None

def _extract_name_from_url(url: str) -> Optional[str]:
    """Extract product name from URL"""
    
    if not url:
        return None
    
    # Extract domain name
    domain_match = re.search(r'https?://(?:www\.)?([^./]+)', url)
    if domain_match:
        domain = domain_match.group(1)
        
        # Remove common suffixes
        domain = re.sub(r'\.(com|net|org|io|co)$', '', domain, flags=re.IGNORECASE)
        
        if _is_valid_product_name(domain):
            return _clean_product_name(domain)
    
    return None

def _detect_product_category(intelligence_data: Dict[str, Any]) -> str:
    """Detect product category from intelligence data"""
    
    # Check for health/supplement indicators
    scientific_intel = _safe_get_dict(intelligence_data, "scientific_intelligence")
    if scientific_intel and scientific_intel.get("primary_compounds"):
        return "health_supplement"
    
    # Check offer intelligence for category clues
    offer_intel = _safe_get_dict(intelligence_data, "offer_intelligence")
    if offer_intel:
        value_props = offer_intel.get("value_propositions", [])
        if isinstance(value_props, list):
            text = " ".join(str(prop) for prop in value_props).lower()
            
            if any(keyword in text for keyword in ["health", "supplement", "vitamin", "nutrition"]):
                return "health_supplement"
            elif any(keyword in text for keyword in ["software", "app", "tool", "system"]):
                return "software"
            elif any(keyword in text for keyword in ["course", "training", "education", "learn"]):
                return "education"
    
    return "product"

def _get_category_fallback_name(category: str) -> str:
    """Get fallback product name based on category"""
    
    fallback_names = {
        "health_supplement": "Premium Health Formula",
        "software": "Professional Software",
        "education": "Expert Training Program", 
        "product": "Premium Solution"
    }
    
    return fallback_names.get(category, "Premium Product")

# Convenience functions for common use cases

def fix_ad_copy_placeholders(ads: List[Dict[str, Any]], intelligence_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Fix product name placeholders in ad copy"""
    
    actual_product_name = extract_product_name_from_intelligence(intelligence_data)
    
    fixed_ads = []
    for ad in ads:
        fixed_ad = ad.copy()
        
        # Fix placeholders in key fields
        for field in ["headline", "description", "cta", "target_audience"]:
            if fixed_ad.get(field):
                fixed_ad[field] = substitute_product_placeholders(fixed_ad[field], actual_product_name)
        
        # Ensure product name is set correctly
        fixed_ad["product_name"] = actual_product_name
        fixed_ad["placeholders_fixed"] = True
        
        fixed_ads.append(fixed_ad)
    
    return fixed_ads

def fix_email_placeholders(emails: List[Dict[str, Any]], intelligence_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Fix product name placeholders in email sequences"""
    
    actual_product_name = extract_product_name_from_intelligence(intelligence_data)
    
    fixed_emails = []
    for email in emails:
        fixed_email = email.copy()
        
        # Fix placeholders in email fields
        for field in ["subject", "preview_text", "content", "headline"]:
            if fixed_email.get(field):
                fixed_email[field] = substitute_product_placeholders(fixed_email[field], actual_product_name)
        
        # Fix in email body if present
        if fixed_email.get("email_body"):
            fixed_email["email_body"] = substitute_product_placeholders(fixed_email["email_body"], actual_product_name)
        
        fixed_email["product_name"] = actual_product_name
        fixed_email["placeholders_fixed"] = True
        
        fixed_emails.append(fixed_email)
    
    return fixed_emails

def fix_content_placeholders(content: Dict[str, Any], intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fix product name placeholders in generic content"""
    
    actual_product_name = extract_product_name_from_intelligence(intelligence_data)
    
    # Recursively fix placeholders in the entire content structure
    fixed_content = substitute_placeholders_in_data(content, actual_product_name)
    fixed_content["product_name_used"] = actual_product_name
    fixed_content["placeholders_fixed"] = True
    
    return fixed_content

def validate_content_clean(content: Dict[str, Any], expected_product_name: str) -> Dict[str, Any]:
    """Validate that content is free of placeholders"""
    
    validation_result = {
        "is_clean": True,
        "placeholder_issues": [],
        "expected_product_name": expected_product_name,
        "validation_timestamp": "2025-07-22T17:15:00Z"
    }
    
    def check_text(text: str, field_path: str):
        if isinstance(text, str) and text:
            if not validate_no_placeholders(text, expected_product_name):
                validation_result["is_clean"] = False
                validation_result["placeholder_issues"].append({
                    "field": field_path,
                    "text_preview": text[:100] + "..." if len(text) > 100 else text,
                    "issue": "Contains placeholders or missing product name"
                })
    
    def recursive_check(obj: Any, path: str = ""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                recursive_check(value, current_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                recursive_check(item, current_path)
        elif isinstance(obj, str):
            check_text(obj, path)
    
    recursive_check(content)
    
    return validation_result

# Advanced product name extraction for difficult cases

def extract_product_name_advanced(intelligence_data: Dict[str, Any], backup_sources: List[str] = None) -> str:
    """
    Advanced product name extraction with multiple backup sources
    
    Args:
        intelligence_data: Standard intelligence data
        backup_sources: Additional text sources to search (page content, etc.)
    """
    
    # Try standard extraction first
    standard_name = extract_product_name_from_intelligence(intelligence_data)
    
    if _is_high_confidence_name(standard_name):
        return standard_name
    
    # Try backup sources if provided
    if backup_sources:
        for source_text in backup_sources:
            if isinstance(source_text, str):
                extracted_name = _extract_from_text_content(source_text)
                if extracted_name and _is_valid_product_name(extracted_name):
                    logger.info(f"✅ Advanced extraction from backup source: {extracted_name}")
                    return extracted_name
    
    # Try pattern matching on raw content
    raw_content = intelligence_data.get("raw_content", "")
    if raw_content:
        pattern_name = _extract_with_patterns(raw_content)
        if pattern_name and _is_valid_product_name(pattern_name):
            logger.info(f"✅ Advanced pattern extraction: {pattern_name}")
            return pattern_name
    
    # Return standard name as fallback
    logger.warning(f"⚠️ Advanced extraction couldn't improve on: {standard_name}")
    return standard_name

def _is_high_confidence_name(name: str) -> bool:
    """Check if name is high confidence (not a fallback)"""
    
    fallback_names = [
        "Premium Product", "Premium Health Formula", "Professional Software", 
        "Expert Training Program", "Premium Solution"
    ]
    
    return name not in fallback_names and len(name) > 5

def _extract_from_text_content(text: str) -> Optional[str]:
    """Extract product name from raw text content"""
    
    if not text or len(text) < 10:
        return None
    
    # Look for product name patterns in text
    patterns = [
        r'introducing\s+([A-Z][a-zA-Z0-9]+)',  # "Introducing Hepatoburn"
        r'try\s+([A-Z][a-zA-Z0-9]+)\s+today',  # "Try Hepatoburn today"
        r'([A-Z][a-zA-Z0-9]+)\s+is\s+the\s+(?:best|only|top)',  # "Hepatoburn is the best"
        r'order\s+([A-Z][a-zA-Z0-9]+)\s+now',  # "Order Hepatoburn now"
        r'get\s+([A-Z][a-zA-Z0-9]+)\s+(?:today|now)',  # "Get Hepatoburn today"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if _is_valid_product_name(match):
                return _clean_product_name(match)
    
    return None

def _extract_with_patterns(content: str) -> Optional[str]:
    """Extract using advanced regex patterns"""
    
    if not content:
        return None
    
    # Advanced patterns for product names
    advanced_patterns = [
        # Branded product patterns
        r'\b([A-Z][a-z]+(?:[A-Z][a-z]*)*)\s*(?:™|®|©)',  # Trademarked names
        r'\b([A-Z][a-z]+(?:[A-Z][a-z]*)*)\s+formula\b',   # "Hepatoburn formula"
        r'\b([A-Z][a-z]+(?:[A-Z][a-z]*)*)\s+supplement\b', # "Hepatoburn supplement"
        
        # URL-based patterns
        r'(?:www\.)?([a-zA-Z0-9-]+)\.com(?:/|\s|$)',      # Domain names
        
        # Title patterns
        r'^([A-Z][a-zA-Z0-9]+)\s*[-:|]',                  # Title prefixes
    ]
    
    for pattern in advanced_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            candidate = match.strip() if isinstance(match, str) else str(match).strip()
            if candidate and _is_valid_product_name(candidate):
                return _clean_product_name(candidate)
    
    return None

# Validation and testing utilities

def test_product_name_extraction(intelligence_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Test product name extraction on multiple samples"""
    
    test_results = {
        "total_samples": len(intelligence_samples),
        "successful_extractions": 0,
        "fallback_used": 0,
        "high_confidence": 0,
        "results": []
    }
    
    for i, sample in enumerate(intelligence_samples):
        try:
            extracted_name = extract_product_name_from_intelligence(sample)
            is_fallback = not _is_high_confidence_name(extracted_name)
            is_valid = _is_valid_product_name(extracted_name)
            
            result = {
                "sample_id": i,
                "extracted_name": extracted_name,
                "is_fallback": is_fallback,
                "is_valid": is_valid,
                "confidence": "high" if not is_fallback and is_valid else "low"
            }
            
            test_results["results"].append(result)
            
            if is_valid:
                test_results["successful_extractions"] += 1
            if is_fallback:
                test_results["fallback_used"] += 1
            if not is_fallback and is_valid:
                test_results["high_confidence"] += 1
                
        except Exception as e:
            test_results["results"].append({
                "sample_id": i,
                "error": str(e),
                "confidence": "error"
            })
    
    # Calculate success rate
    if test_results["total_samples"] > 0:
        test_results["success_rate"] = test_results["successful_extractions"] / test_results["total_samples"]
        test_results["high_confidence_rate"] = test_results["high_confidence"] / test_results["total_samples"]
    
    return test_results

def generate_test_report(test_results: Dict[str, Any]) -> str:
    """Generate human-readable test report"""
    
    report = f"""
🧪 PRODUCT NAME EXTRACTION TEST REPORT
=====================================

📊 SUMMARY:
- Total samples tested: {test_results['total_samples']}
- Successful extractions: {test_results['successful_extractions']}
- High confidence results: {test_results['high_confidence']}
- Fallback names used: {test_results['fallback_used']}

📈 PERFORMANCE:
- Success rate: {test_results.get('success_rate', 0):.1%}
- High confidence rate: {test_results.get('high_confidence_rate', 0):.1%}

🎯 TOP EXTRACTED NAMES:
"""
    
    # Show top extracted names
    name_counts = {}
    for result in test_results.get("results", []):
        name = result.get("extracted_name")
        if name and not result.get("is_fallback", True):
            name_counts[name] = name_counts.get(name, 0) + 1
    
    for name, count in sorted(name_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        report += f"- {name}: {count} times\n"
    
    return report

# Export all main functions
__all__ = [
    'extract_product_name_from_intelligence',
    'substitute_product_placeholders', 
    'substitute_placeholders_in_data',
    'validate_no_placeholders',
    'fix_ad_copy_placeholders',
    'fix_email_placeholders',
    'fix_content_placeholders',
    'validate_content_clean',
    'extract_product_name_advanced',
    'test_product_name_extraction',
    'generate_test_report'
]