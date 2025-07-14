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
    
    logger.info(f"📝 Fixed blog post with product name: {product_name}")
    return fixed_blog_post

# ============================================================================
# SPECIFIC CONTENT TYPE FIXES
# ============================================================================

def fix_video_script_placeholders(script_data: Dict, intelligence: Dict[str, Any]) -> Dict:
    """
    🔥 VIDEO SCRIPT FIX: Apply product name fix to video scripts
    """
    product_name = extract_product_name_from_intelligence(intelligence)
    company_name = extract_company_name_from_intelligence(intelligence)
    
    fixed_script = {}
    
    # Fix main script content
    if isinstance(script_data, dict):
        for key, value in script_data.items():
            if key == "segments" and isinstance(value, list):
                # Fix video segments
                fixed_segments = []
                for segment in value:
                    fixed_segment = {
                        "segment_type": segment.get("segment_type", ""),
                        "time_range": segment.get("time_range", ""),
                        "narration": substitute_product_placeholders(segment.get("narration", ""), product_name, company_name),
                        "visual_cues": [substitute_product_placeholders(cue, product_name, company_name) for cue in segment.get("visual_cues", [])],
                        "text_overlays": [substitute_product_placeholders(overlay, product_name, company_name) for overlay in segment.get("text_overlays", [])]
                    }
                    fixed_segments.append(fixed_segment)
                fixed_script[key] = fixed_segments
            elif isinstance(value, str):
                fixed_script[key] = substitute_product_placeholders(value, product_name, company_name)
            else:
                fixed_script[key] = value
    else:
        # If script_data is a string, fix it directly
        fixed_script = substitute_product_placeholders(str(script_data), product_name, company_name)
    
    logger.info(f"🎬 Fixed video script with product name: {product_name}")
    return fixed_script

def fix_slideshow_video_placeholders(video_data: Dict, intelligence: Dict[str, Any]) -> Dict:
    """
    🔥 SLIDESHOW VIDEO FIX: Apply product name fix to slideshow video data
    """
    product_name = extract_product_name_from_intelligence(intelligence)
    company_name = extract_company_name_from_intelligence(intelligence)
    
    fixed_video_data = {}
    
    for key, value in video_data.items():
        if key == "storyboard" and isinstance(value, dict):
            # Fix storyboard content
            fixed_storyboard = {}
            for sb_key, sb_value in value.items():
                if sb_key == "title":
                    fixed_storyboard[sb_key] = substitute_product_placeholders(sb_value, product_name, company_name)
                elif sb_key == "scenes" and isinstance(sb_value, list):
                    # Fix individual scenes
                    fixed_scenes = []
                    for scene in sb_value:
                        fixed_scene = {}
                        for scene_key, scene_value in scene.items():
                            if scene_key in ["text_overlay"] and isinstance(scene_value, str):
                                fixed_scene[scene_key] = substitute_product_placeholders(scene_value, product_name, company_name)
                            else:
                                fixed_scene[scene_key] = scene_value
                        fixed_scenes.append(fixed_scene)
                    fixed_storyboard[sb_key] = fixed_scenes
                else:
                    fixed_storyboard[sb_key] = sb_value
            fixed_video_data[key] = fixed_storyboard
        elif isinstance(value, str):
            fixed_video_data[key] = substitute_product_placeholders(value, product_name, company_name)
        else:
            fixed_video_data[key] = value
    
    logger.info(f"📹 Fixed slideshow video data with product name: {product_name}")
    return fixed_video_data

def fix_image_generation_placeholders(image_data: Dict, intelligence: Dict[str, Any]) -> Dict:
    """
    🔥 IMAGE GENERATION FIX: Apply product name fix to image generation data
    """
    product_name = extract_product_name_from_intelligence(intelligence)
    company_name = extract_company_name_from_intelligence(intelligence)
    
    fixed_image_data = {}
    
    for key, value in image_data.items():
        if key == "generated_images" and isinstance(value, list):
            # Fix image prompts and metadata
            fixed_images = []
            for image in value:
                fixed_image = {}
                for img_key, img_value in image.items():
                    if img_key == "prompt" and isinstance(img_value, str):
                        fixed_image[img_key] = substitute_product_placeholders(img_value, product_name, company_name)
                    else:
                        fixed_image[img_key] = img_value
                fixed_images.append(fixed_image)
            fixed_image_data[key] = fixed_images
        elif isinstance(value, str):
            fixed_image_data[key] = substitute_product_placeholders(value, product_name, company_name)
        else:
            fixed_image_data[key] = value
    
    logger.info(f"🖼️ Fixed image generation data with product name: {product_name}")
    return fixed_image_data