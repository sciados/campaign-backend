import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# ============================================================================
# UNIVERSAL PLACEHOLDER SUBSTITUTION FUNCTIONS
# ============================================================================

def substitute_product_placeholders(content: str, product_name: str, company_name: str = None) -> str:
    """
    🔥 UNIVERSAL: Replace all product placeholders with actual names
    Apply this to ALL generated content before returning to user
    """
    if not isinstance(content, str) or not product_name:
        return content
    
    # Define all possible placeholder variations
    placeholders = {
        # Product placeholders
        "PRODUCT": product_name,
        "Product": product_name,
        "product": product_name,
        "[PRODUCT]": product_name,
        "[Product]": product_name,
        "[Product Name]": product_name,
        "[PRODUCT_NAME]": product_name,
        "Your Product": product_name,
        "Your product": product_name,
        "your product": product_name,
        "this product": product_name,
        "This product": product_name,
        "the product": product_name,
        "The product": product_name,
        
        # Company placeholders (if company_name provided)
        "COMPANY": company_name or product_name,
        "Company": company_name or product_name,
        "[COMPANY]": company_name or product_name,
        "[Company]": company_name or product_name,
        "[Company Name]": company_name or product_name,
        "[COMPANY_NAME]": company_name or product_name,
        "Your Company": company_name or product_name,
        "Your company": company_name or product_name,
        "your company": company_name or product_name,
        
        # Generic "Your" replacements (context-sensitive)
        "Your ": f"{product_name} ",
        "your ": f"{product_name} ",
    }
    
    result = content
    
    # Apply exact replacements first (whole words only)
    for placeholder, replacement in placeholders.items():
        if replacement:  # Only replace if we have a replacement
            # Use word boundaries for exact matches
            if placeholder.endswith(" "):
                # For "Your " and "your " - replace at word boundaries
                pattern = r'\b' + re.escape(placeholder.strip()) + r'\b'
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            else:
                # For exact placeholder matches
                result = result.replace(placeholder, replacement)
    
    # Log the substitution for debugging
    if result != content:
        logger.info(f"🔄 Placeholder substitution: Applied {product_name} replacements")
        
        # Count substitutions made
        substitutions_made = sum(1 for p in placeholders.keys() if p in content)
        logger.info(f"📝 Total substitutions: {substitutions_made}")
    
    return result

def substitute_placeholders_in_data(data: Any, product_name: str, company_name: str = None) -> Any:
    """
    🔥 RECURSIVE: Apply placeholder substitution to nested data structures
    Use this for JSON responses, lists, and complex data structures
    """
    if isinstance(data, dict):
        return {k: substitute_placeholders_in_data(v, product_name, company_name) for k, v in data.items()}
    elif isinstance(data, list):
        return [substitute_placeholders_in_data(item, product_name, company_name) for item in data]
    elif isinstance(data, str):
        return substitute_product_placeholders(data, product_name, company_name)
    else:
        return data

def validate_no_placeholders(content: str, product_name: str) -> bool:
    """
    🔥 VALIDATION: Check if content still contains placeholders
    Returns True if content is clean, False if placeholders found
    """
    placeholder_indicators = [
        "PRODUCT", "[Product", "Your Product", "your product", 
        "the product", "COMPANY", "[Company", "Your Company"
    ]
    
    content_lower = content.lower()
    found_placeholders = []
    
    for indicator in placeholder_indicators:
        if indicator.lower() in content_lower:
            found_placeholders.append(indicator)
    
    if found_placeholders:
        logger.warning(f"🚨 PLACEHOLDERS STILL FOUND in content: {found_placeholders}")
        logger.warning(f"🎯 Expected product name: {product_name}")
        return False
    
    return True

# ============================================================================
# INTELLIGENCE DATA EXTRACTION HELPERS
# ============================================================================

def extract_product_name_from_intelligence(intelligence: Dict[str, Any]) -> str:
    """
    🔥 EXTRACT: Get actual product name from intelligence data
    Use this in ALL content generators to get the real product name
    """
    # Priority order for product name extraction
    sources = [
        intelligence.get("product_name"),
        intelligence.get("offer_intelligence", {}).get("products", [None])[0] if intelligence.get("offer_intelligence", {}).get("products") else None,
        intelligence.get("page_title", "").split()[0] if intelligence.get("page_title") else None,
        "Product"  # Last resort fallback
    ]
    
    for source in sources:
        if source and isinstance(source, str) and len(source) > 1:
            # Clean the product name
            product_name = source.strip()
            
            # Filter out obvious placeholders
            if product_name.lower() not in ['your', 'product', 'company', 'unknown']:
                logger.info(f"✅ Extracted product name: '{product_name}'")
                return product_name
    
    logger.warning("⚠️ Could not extract product name, using 'Product'")
    return "Product"

def extract_company_name_from_intelligence(intelligence: Dict[str, Any]) -> Optional[str]:
    """
    🔥 EXTRACT: Get company name from intelligence data if available
    """
    # Try to extract company name from various sources
    sources = [
        intelligence.get("company_name"),
        intelligence.get("brand_intelligence", {}).get("brand_name"),
        intelligence.get("page_title", "").split()[-1] if intelligence.get("page_title") else None,
    ]
    
    for source in sources:
        if source and isinstance(source, str) and len(source) > 1:
            company_name = source.strip()
            if company_name.lower() not in ['your', 'company', 'unknown']:
                logger.info(f"✅ Extracted company name: '{company_name}'")
                return company_name
    
    return None

# ============================================================================
# CONTENT GENERATOR WRAPPER FUNCTIONS
# ============================================================================

def apply_product_name_fix(generator_function):
    """
    🔥 DECORATOR: Apply product name fix to any content generator
    Use this decorator on all content generation functions
    """
    def wrapper(*args, **kwargs):
        # Get the result from the original function
        result = generator_function(*args, **kwargs)
        
        # Extract intelligence data (usually first argument)
        intelligence = args[0] if args else {}
        
        # Extract product name
        product_name = extract_product_name_from_intelligence(intelligence)
        company_name = extract_company_name_from_intelligence(intelligence)
        
        # Apply substitutions
        if isinstance(result, str):
            # Single string result
            fixed_result = substitute_product_placeholders(result, product_name, company_name)
        elif isinstance(result, (dict, list)):
            # Complex data structure
            fixed_result = substitute_placeholders_in_data(result, product_name, company_name)
        else:
            # Unknown type, return as-is
            fixed_result = result
        
        # Validate result
        if isinstance(fixed_result, str):
            is_clean = validate_no_placeholders(fixed_result, product_name)
            if not is_clean:
                logger.error(f"❌ Content still contains placeholders after fix!")
        
        return fixed_result
    
    return wrapper

# ============================================================================
# SPECIFIC CONTENT TYPE FIXES
# ============================================================================

def fix_email_sequence_placeholders(emails: List[Dict], intelligence: Dict[str, Any]) -> List[Dict]:
    """
    🔥 EMAIL FIX: Apply product name fix to email sequences
    """
    product_name = extract_product_name_from_intelligence(intelligence)
    company_name = extract_company_name_from_intelligence(intelligence)
    
    fixed_emails = []
    
    for email in emails:
        fixed_email = {
            "subject": substitute_product_placeholders(email.get("subject", ""), product_name, company_name),
            "body": substitute_product_placeholders(email.get("body", ""), product_name, company_name),
            "day": email.get("day", 1),
            "email_type": email.get("email_type", "promotional")
        }
        
        # Additional email-specific fixes
        if "preview_text" in email:
            fixed_email["preview_text"] = substitute_product_placeholders(email["preview_text"], product_name, company_name)
        
        # Copy all other fields
        for key, value in email.items():
            if key not in fixed_email:
                if isinstance(value, str):
                    fixed_email[key] = substitute_product_placeholders(value, product_name, company_name)
                else:
                    fixed_email[key] = value
        
        fixed_emails.append(fixed_email)
    
    logger.info(f"📧 Fixed {len(fixed_emails)} emails with product name: {product_name}")
    return fixed_emails

def fix_social_media_placeholders(posts: List[Dict], intelligence: Dict[str, Any]) -> List[Dict]:
    """
    🔥 SOCIAL FIX: Apply product name fix to social media posts
    """
    product_name = extract_product_name_from_intelligence(intelligence)
    company_name = extract_company_name_from_intelligence(intelligence)
    
    fixed_posts = []
    
    for post in posts:
        fixed_post = {
            "content": substitute_product_placeholders(post.get("content", ""), product_name, company_name),
            "platform": post.get("platform", "facebook"),
            "hashtags": [substitute_product_placeholders(tag, product_name, company_name) for tag in post.get("hashtags", [])]
        }
        
        # Additional social-specific fixes
        if "caption" in post:
            fixed_post["caption"] = substitute_product_placeholders(post["caption"], product_name, company_name)
        
        # Copy all other fields
        for key, value in post.items():
            if key not in fixed_post:
                if isinstance(value, str):
                    fixed_post[key] = substitute_product_placeholders(value, product_name, company_name)
                else:
                    fixed_post[key] = value
        
        fixed_posts.append(fixed_post)
    
    logger.info(f"📱 Fixed {len(fixed_posts)} social posts with product name: {product_name}")
    return fixed_posts

def fix_ad_copy_placeholders(ads: List[Dict], intelligence: Dict[str, Any]) -> List[Dict]:
    """
    🔥 AD FIX: Apply product name fix to ad copy
    """
    product_name = extract_product_name_from_intelligence(intelligence)
    company_name = extract_company_name_from_intelligence(intelligence)
    
    fixed_ads = []
    
    for ad in ads:
        fixed_ad = {
            "headline": substitute_product_placeholders(ad.get("headline", ""), product_name, company_name),
            "description": substitute_product_placeholders(ad.get("description", ""), product_name, company_name),
            "call_to_action": substitute_product_placeholders(ad.get("call_to_action", ""), product_name, company_name),
            "platform": ad.get("platform", "facebook")
        }
        
        # Additional ad-specific fixes
        if "primary_text" in ad:
            fixed_ad["primary_text"] = substitute_product_placeholders(ad["primary_text"], product_name, company_name)
        
        # Copy all other fields
        for key, value in ad.items():
            if key not in fixed_ad:
                if isinstance(value, str):
                    fixed_ad[key] = substitute_product_placeholders(value, product_name, company_name)
                else:
                    fixed_ad[key] = value
        
        fixed_ads.append(fixed_ad)
    
    logger.info(f"📢 Fixed {len(fixed_ads)} ads with product name: {product_name}")
    return fixed_ads

def fix_blog_post_placeholders(blog_post: Dict, intelligence: Dict[str, Any]) -> Dict:
    """
    🔥 BLOG FIX: Apply product name fix to blog posts
    """
    product_name = extract_product_name_from_intelligence(intelligence)
    company_name = extract_company_name_from_intelligence(intelligence)
    
    fixed_blog_post = {
        "title": substitute_product_placeholders(blog_post.get("title", ""), product_name, company_name),
        "content": substitute_product_placeholders(blog_post.get("content", ""), product_name, company_name),
        "meta_description": substitute_product_placeholders(blog_post.get("meta_description", ""), product_name, company_name),
        "tags": [substitute_product_placeholders(tag, product_name, company_name) for tag in blog_post.get("tags", [])]
    }
    
    # Additional blog-specific fixes
    if "excerpt" in blog_post:
        fixed_blog_post["excerpt"] = substitute_product_placeholders(blog_post["excerpt"], product_name, company_name)
    
    if "sections" in blog_post:
        fixed_blog_post["sections"] = [
            substitute_product_placeholders(section, product_name, company_name) 
            for section in blog_post["sections"]
        ]
    
    # Copy all other fields
    for key, value in blog_post.items():
        if key not in fixed_blog_post:
            if isinstance(value, str):
                fixed_blog_post[key] = substitute_product_placeholders(value, product_name, company_name)
            else:
                fixed_blog_post[key] = value
    
    logger.info(f"📝 Fixed blog post with product name: {product_name}")
    return fixed_blog_post

# ============================================================================
# ADDITIONAL CONTENT TYPE FIXES
# ============================================================================

def fix_video_script_placeholders(script_data: Dict, intelligence: Dict[str, Any]) -> Dict:
    """
    🔥 VIDEO SCRIPT FIX: Apply product name fix to video scripts
    """
    product_name = extract_product_name_from_intelligence(intelligence)
    company_name = extract_company_name_from_intelligence(intelligence)
    
    if isinstance(script_data, str):
        return substitute_product_placeholders(script_data, product_name, company_name)
    
    fixed_script = {}
    
    for key, value in script_data.items():
        if key == "segments" and isinstance(value, list):
            # Fix video segments
            fixed_segments = []
            for segment in value:
                fixed_segment = {}
                for seg_key, seg_value in segment.items():
                    if isinstance(seg_value, str):
                        fixed_segment[seg_key] = substitute_product_placeholders(seg_value, product_name, company_name)
                    elif isinstance(seg_value, list):
                        fixed_segment[seg_key] = [substitute_product_placeholders(item, product_name, company_name) if isinstance(item, str) else item for item in seg_value]
                    else:
                        fixed_segment[seg_key] = seg_value
                fixed_segments.append(fixed_segment)
            fixed_script[key] = fixed_segments
        elif isinstance(value, str):
            fixed_script[key] = substitute_product_placeholders(value, product_name, company_name)
        else:
            fixed_script[key] = value
    
    logger.info(f"🎬 Fixed video script with product name: {product_name}")
    return fixed_script

def fix_slideshow_video_placeholders(video_data: Dict, intelligence: Dict[str, Any]) -> Dict:
    """
    🔥 SLIDESHOW VIDEO FIX: Apply product name fix to slideshow video data
    """
    product_name = extract_product_name_from_intelligence(intelligence)
    company_name = extract_company_name_from_intelligence(intelligence)
    
    # Apply recursive substitution to the entire video data structure
    fixed_video_data = substitute_placeholders_in_data(video_data, product_name, company_name)
    
    logger.info(f"📹 Fixed slideshow video data with product name: {product_name}")
    return fixed_video_data

def fix_landing_page_placeholders(page_data: Dict, intelligence: Dict[str, Any]) -> Dict:
    """
    🔥 LANDING PAGE FIX: Apply product name fix to landing page data
    """
    product_name = extract_product_name_from_intelligence(intelligence)
    company_name = extract_company_name_from_intelligence(intelligence)
    
    # Apply recursive substitution to the entire page data structure
    fixed_page_data = substitute_placeholders_in_data(page_data, product_name, company_name)
    
    logger.info(f"🏗️ Fixed landing page data with product name: {product_name}")
    return fixed_page_data