# src/intelligence/utils/product_name_extractor.py
"""
Universal Product Name Extractor
🎯 Centralized product name extraction for all content generators
✅ Direct source_title extraction with AI corruption prevention
✅ Universal fallbacks for thousands of product types
✅ Consistent product name handling across entire platform
"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def extract_product_name_from_intelligence(intelligence_data: Dict[str, Any]) -> str:
    """
    🔥 UNIVERSAL: Extract product name from intelligence data with corruption prevention
    
    Priority order:
    1. Direct source_title (database field - most reliable)
    2. Offer intelligence products array
    3. Generic fallback for universal support
    
    Args:
        intelligence_data: Intelligence data dictionary containing source_title and other fields
        
    Returns:
        str: The extracted product name or generic fallback
    """
    
    # 🔧 PRIORITY 1: Use direct source_title field (most reliable)
    # This comes directly from the database, not from AI-processed content
    direct_source_title = intelligence_data.get("source_title")
    
    if direct_source_title and isinstance(direct_source_title, str) and len(direct_source_title.strip()) > 2:
        product_name = direct_source_title.strip()
        
        # Only remove analysis-specific suffixes, not the product name
        analysis_suffixes = [
            " - Sales Page Analysis",
            " - Analysis", 
            " - Page Analysis",
            " Sales Page",
            " Analysis",
            " - Product Analysis",
            " Product Analysis"
        ]
        
        for suffix in analysis_suffixes:
            if product_name.endswith(suffix):
                product_name = product_name[:-len(suffix)].strip()
        
        # Validate it's a real product name (not a placeholder or AI corruption)
        invalid_names = [
            "Unknown Product", 
            "Analyzed Page", 
            "Stock Up - Exclusive Offer",
            "Burning",  # Common AI corruption
            "PRODUCT",
            "Your Product",
            "this product",
            "the product",
            "[PRODUCT]",
            "COMPANY",
            "Your Company",
            "[COMPANY]",
            "Product Name",
            "Brand Name"
        ]
        
        if product_name and len(product_name) > 2 and product_name not in invalid_names:
            logger.info(f"✅ Extracted product name from source_title: '{product_name}'")
            return product_name
    
    # 🔧 PRIORITY 2: Try to extract from offer_intelligence if direct source fails
    logger.warning("⚠️ Direct source_title not available, checking offer_intelligence")
    
    try:
        offer_intel = intelligence_data.get("offer_intelligence", {})
        if isinstance(offer_intel, str):
            offer_intel = json.loads(offer_intel)
        
        # Look for products array
        products = offer_intel.get("products", [])
        if products and isinstance(products, list) and len(products) > 0:
            first_product = products[0]
            if first_product and first_product not in ["BURNING", "Burning", "PRODUCT", "COMPANY"]:
                logger.info(f"✅ Extracted product name from offer_intelligence: '{first_product}'")
                return first_product
                
    except Exception as e:
        logger.warning(f"Error parsing offer_intelligence: {e}")
    
    # 🔧 PRIORITY 3: Check value_propositions for product mentions
    try:
        offer_intel = intelligence_data.get("offer_intelligence", {})
        if isinstance(offer_intel, str):
            offer_intel = json.loads(offer_intel)
        
        value_props = offer_intel.get("value_propositions", [])
        if value_props and isinstance(value_props, list):
            for prop in value_props:
                if isinstance(prop, str) and "Main" in prop and ":" in prop:
                    # Extract from format like "Main HEPATOBURN: HEPATOBURN"
                    parts = prop.split(":")
                    if len(parts) >= 2:
                        potential_name = parts[1].strip()
                        if potential_name and potential_name not in ["BURNING", "Burning", "PRODUCT"]:
                            logger.info(f"✅ Extracted product name from value_propositions: '{potential_name}'")
                            return potential_name
                            
    except Exception as e:
        logger.warning(f"Error parsing value_propositions: {e}")
    
    # 🔧 PRIORITY 4: Generic fallback for universal product support
    logger.info("🔄 Using generic product fallback for universal support")
    return "this product"  # Universal fallback for any product type

def extract_company_name_from_intelligence(intelligence_data: Dict[str, Any]) -> str:
    """
    Extract company/brand name from intelligence data
    Often the same as product name for direct-to-consumer products
    
    Args:
        intelligence_data: Intelligence data dictionary
        
    Returns:
        str: The extracted company name or product name fallback
    """
    
    # For most direct-to-consumer products, company name = product name
    product_name = extract_product_name_from_intelligence(intelligence_data)
    
    # Try to extract specific company info from brand intelligence
    try:
        brand_intel = intelligence_data.get("brand_intelligence", {})
        if isinstance(brand_intel, str):
            brand_intel = json.loads(brand_intel)
        
        brand_positioning = brand_intel.get("brand_positioning", "")
        if brand_positioning and "company" in brand_positioning.lower():
            # Extract company name from brand positioning if available
            pass  # Could add more sophisticated extraction here
            
    except Exception as e:
        logger.warning(f"Error parsing brand_intelligence: {e}")
    
    return product_name  # Default to product name

def validate_product_name(product_name: str) -> bool:
    """
    Validate that a product name is legitimate (not a placeholder or corruption)
    
    Args:
        product_name: The product name to validate
        
    Returns:
        bool: True if valid, False if placeholder/corruption
    """
    
    if not product_name or not isinstance(product_name, str):
        return False
    
    product_name = product_name.strip()
    
    if len(product_name) < 2:
        return False
    
    # Check against known invalid patterns
    invalid_patterns = [
        "unknown", "product", "company", "brand", "burning", 
        "[", "]", "your", "this", "the", "placeholder"
    ]
    
    product_lower = product_name.lower()
    for pattern in invalid_patterns:
        if pattern in product_lower:
            return False
    
    return True

def get_product_details_summary(intelligence_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract comprehensive product details for content generation
    
    Args:
        intelligence_data: Intelligence data dictionary
        
    Returns:
        Dict containing product name, benefits, audience, etc.
    """
    
    product_name = extract_product_name_from_intelligence(intelligence_data)
    company_name = extract_company_name_from_intelligence(intelligence_data)
    
    # Extract benefits from offer intelligence
    benefits = "optimization, enhancement, improvement"  # Default
    try:
        offer_intel = intelligence_data.get("offer_intelligence", {})
        if isinstance(offer_intel, str):
            offer_intel = json.loads(offer_intel)
        
        extracted_benefits = offer_intel.get("benefits", [])
        if extracted_benefits and isinstance(extracted_benefits, list):
            benefits = ", ".join(extracted_benefits[:3])
            
    except Exception as e:
        logger.warning(f"Error extracting benefits: {e}")
    
    # Extract target audience from psychology intelligence
    audience = "individuals seeking effective solutions"  # Default
    try:
        psych_intel = intelligence_data.get("psychology_intelligence", {})
        if isinstance(psych_intel, str):
            psych_intel = json.loads(psych_intel)
        
        target_audience = psych_intel.get("target_audience", "")
        if target_audience and isinstance(target_audience, str):
            audience = target_audience
            
    except Exception as e:
        logger.warning(f"Error extracting audience: {e}")
    
    return {
        "name": product_name,
        "company": company_name,
        "benefits": benefits,
        "audience": audience,
        "transformation": "improvement and lifestyle enhancement"
    }

# Convenience functions for backward compatibility
def get_product_name_from_intelligence(intelligence_data: Dict[str, Any]) -> str:
    """Alias for extract_product_name_from_intelligence for backward compatibility"""
    return extract_product_name_from_intelligence(intelligence_data)

def get_product_name_for_content(intelligence_data: Dict[str, Any]) -> str:
    """Alias for content generators"""
    return extract_product_name_from_intelligence(intelligence_data)